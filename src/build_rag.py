import os
from dotenv import load_dotenv
load_dotenv()

import sys
import socket

# Add root to path for Turbo WoL
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    import TURBO_WoL
except ImportError:
    TURBO_WoL = None
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib
from typing import List, Dict, Iterator
import time
import pickle
from dataclasses import dataclass
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Imports that will be available after installation
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from rank_bm25 import BM25Okapi

@dataclass
class ScrapedItem:
    text: str
    metadata: Dict

@dataclass
class ScrapedDocument:
    url: str
    title: str
    items: List[ScrapedItem] # Changed from raw_text

class JuceScraper:
    def __init__(self, base_url="https://docs.juce.com/master/"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_class_list(self) -> List[str]:
        """Fetches the list of class URLs."""
        print(f"Fetching class list from {self.base_url}classes.html...")
        try:
            response = self.session.get(urljoin(self.base_url, "classes.html"))
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'class' in href or 'struct' in href:
                     if href.endswith('.html') and ('juce_' in href or 'classjuce' in href or 'structjuce' in href):
                         links.append(urljoin(self.base_url, href))
            
            if len(links) < 100:
                print("Refining link search...")
                content = soup.find('div', class_='contents') or soup.find('div', id='content')
                if content:
                    for a in content.find_all('a', href=True):
                         href = a['href']
                         if href.endswith('.html') and 'index' not in href:
                             links.append(urljoin(self.base_url, href))
            
            unique_links = sorted(list(set(links)))
            print(f"Found {len(unique_links)} potential class links.")
            return unique_links
        except Exception as e:
            print(f"Error fetching class list: {e}")
            return []

    def scrape_content(self, url: str) -> ScrapedDocument:
        """Fetches and parses a single documentation page using semantic blocking."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else url.split('/')[-1]
            
            items = []
            
            # 1. Try to find semantic Member Items (functions, variables)
            memitems = soup.find_all('div', class_='memitem')
            
            if memitems:
                for item in memitems:
                    proto = item.find('div', class_='memproto')
                    doc = item.find('div', class_='memdoc')
                    
                    text_parts = []
                    if proto:
                        text_parts.append(proto.get_text(" ", strip=True))
                    if doc:
                        text_parts.append(doc.get_text(" ", strip=True))
                        
                    full_text = "\n".join(text_parts)
                    
                    # Try to extract a specific name/ID
                    # Often the memitem has an ID anchor just before it or inside.
                    # <a id="a123..."></a><div class="memitem">...
                    # But text extraction is primary here.
                    
                    if full_text.strip():
                        items.append(ScrapedItem(text=full_text, metadata={"type": "method"}))
            
            # 2. Also capture the Detailed Description (usually at top)
            textblock = soup.find('div', class_='textblock')
            if textblock:
                description_parts = []
                for element in textblock.children:
                    # Stop if we hit a header indicating members
                    if element.name in ['h2', 'h3'] and ('Documentation' in element.get_text() or 'Member' in element.get_text()):
                        break
                    # Skip div.memitem etc if they are direct children (rare but possible)
                    if element.name == 'div' and 'memitem' in element.get('class', []):
                         continue
                    
                    text = element.get_text(" ", strip=True)
                    if text:
                        description_parts.append(text)
                
                full_desc = "\n".join(description_parts).strip()
                if full_desc:
                    # Add as the FIRST item
                    items.insert(0, ScrapedItem(text=full_desc, metadata={"type": "class_description"}))
            
            # If no items found (e.g. simple page or main index), fallback to full text
            if not items:
                content_div = soup.find('div', class_='contents') or soup.find('div', id='content')
                text = content_div.get_text(separator='\n', strip=True) if content_div else soup.get_text(separator='\n', strip=True)
                items.append(ScrapedItem(text=text, metadata={"type": "overview"}))
            
            return ScrapedDocument(url=url, title=title, items=items)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return ScrapedDocument(url=url, title="Error", items=[])

    def crawl(self) -> Iterator[ScrapedDocument]:
        links = self.get_class_list()
        for i, link in enumerate(links):
            if i % 10 == 0:
                print(f"Scraping {i}/{len(links)}: {link}")
            doc = self.scrape_content(link)
            if doc.items:
                yield doc
            time.sleep(0.05)

class JuceProcessor:
    def __init__(self):
        # We might still use a splitter for REALLY large descriptions, 
        # but primarily we pass through the semantic chunks.
        self.fallback_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=0 # No overlap for clean splits if we must split
        )

    def chunk_document(self, doc: ScrapedDocument) -> List[Dict]:
        result_chunks = []
        
        for i, item in enumerate(doc.items):
            # If item text is huge > 4000 chars, split it.
            if len(item.text) > 4000:
                sub_chunks = self.fallback_splitter.create_documents([item.text])
                for j, sub in enumerate(sub_chunks):
                    chunk_id = hashlib.md5(f"{doc.url}_{i}_{j}".encode()).hexdigest()
                    result_chunks.append({
                        "id": chunk_id,
                        "text": sub.page_content,
                        "metadata": {
                            "url": doc.url,
                            "title": doc.title,
                            "type": item.metadata.get("type", "unknown"),
                            "chunk_index": f"{i}_{j}"
                        }
                    })
            else:
                chunk_id = hashlib.md5(f"{doc.url}_{i}".encode()).hexdigest()
                result_chunks.append({
                    "id": chunk_id,
                    "text": item.text,
                    "metadata": {
                        "url": doc.url,
                        "title": doc.title,
                        "type": item.metadata.get("type", "unknown"),
                        "chunk_index": i
                    }
                })
                
        return result_chunks

class OllamaEmbeddingFunction:
    def __init__(self, base_url: str, model_name: str):
        self.api_url = f"{base_url}/api/embeddings"
        self.model_name = model_name
        self.session = requests.Session()
    
    def name(self) -> str:
        return "ollama_embedding_function"

    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings = []
        # Ollama API typically takes one prompt at a time for embeddings or supports batch depending on version.
        # We'll stick to serial for safety unless batch is confirmed.
        for text in input:
            try:
                response = self.session.post(self.api_url, json={"model": self.model_name, "prompt": text})
                response.raise_for_status()
                embeddings.append(response.json()["embedding"])
            except Exception as e:
                print(f"Error getting embedding from Ollama: {e}")
                # Fallback or empty? Better to crash in dev than produce garbage.
                # But for robustness, we might retry.
                # Returning empty list will crash Chroma.
                raise e
        return embeddings

    def embed_query(self, input: List[str]) -> List[List[float]]:
        return self(input)

    def embed_documents(self, input: List[str]) -> List[List[float]]:
        return self(input)

class VectorStore:
    def __init__(self, db_path=None, collection_name="juce_docs"):
        print("Initializing ChromaDB with Ollama Embeddings...")
        
        # Configuration
        default_url = "http://100.102.102.102:11434"
        self.ollama_url = os.getenv("OLLAMA_URL", default_url)

        # --- Lazy Wake-on-LAN ---
        if TURBO_WoL:
            # Parse host/port from URL for robustness
            from urllib.parse import urlparse
            try:
                parsed = urlparse(self.ollama_url)
                host = parsed.hostname
                port = parsed.port or 11434
            except:
                host = "100.102.102.102"
                port = 11434
            is_up = False
            try:
                # Fast check (500ms)
                with socket.create_connection((host, port), timeout=0.5):
                    is_up = True
            except OSError:
                pass
            
            if not is_up:
                print("[RAG] Ollama unreachable. Triggering Wake-on-LAN...")
                TURBO_WoL.wake_device()
                TURBO_WoL.wait_for_ollama(host, port)
        # ------------------------
        self.ollama_model = "embeddinggemma:latest"
        
        self.embedding_fn = OllamaEmbeddingFunction(
            base_url=self.ollama_url, 
            model_name=self.ollama_model
        )
        
        # Resolve absolute path for database
        if db_path is None:
            # Use data/juce_chroma_db relative to PROJECT ROOT
            # __file__ is src/build_rag.py -> dirname is src/ -> dirname is root
            src_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(src_dir)
            self.db_path = os.path.join(project_root, "data", "juce_chroma_db")
        else:
            self.db_path = db_path
            
        print(f"Using database at: {self.db_path}")

        self.client = chromadb.PersistentClient(path=self.db_path)
        # Register the embedding function with the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name, 
            embedding_function=self.embedding_fn
        )
        
        # BM25 State
        self.bm25 = None
        self.bm25_mapping = [] # List of chunk IDs corresponding to BM25 indices
        self.bm25_index_path = os.path.join(self.db_path, "bm25_index.pkl")
        self.bm25_mapping_path = os.path.join(self.db_path, "bm25_mapping.pkl")
        
        # Accumulator for building phase
        self.build_corpus_tokens = []
        self.build_corpus_ids = []
        
        self.load_bm25()

    def simple_tokenize(self, text: str) -> List[str]:
        import re
        # Split on any non-word character (like ::, ., etc)
        # This allows "juce::Slider" to be tokenized as ["juce", "slider"]
        return re.findall(r'\w+', text.lower())

    def load_bm25(self):
        """Loads BM25 index and mapping from disk if available."""
        if os.path.exists(self.bm25_index_path) and os.path.exists(self.bm25_mapping_path):
            try:
                print("Loading BM25 index from disk...")
                with open(self.bm25_index_path, 'rb') as f:
                    self.bm25 = pickle.load(f)
                with open(self.bm25_mapping_path, 'rb') as f:
                    self.bm25_mapping = pickle.load(f)
                print(f"BM25 loaded with {len(self.bm25_mapping)} documents.")
            except Exception as e:
                print(f"Failed to load BM25 index: {e}")
        else:
            print("No BM25 index found on disk.")

    def add_documents(self, chunks: List[Dict]):
        if not chunks:
            return
        
        ids = [c['id'] for c in chunks]
        documents = [c['text'] for c in chunks]
        metadatas = [c['metadata'] for c in chunks]
        
        # Add to Chroma
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        # Accumulate for BM25
        for c in chunks:
            tokens = self.simple_tokenize(c['text'])
            self.build_corpus_tokens.append(tokens)
            self.build_corpus_ids.append(c['id'])

    def build_and_save_bm25(self):
        """Builds the BM25 index from accumulated documents and saves to disk."""
        if not self.build_corpus_tokens:
            print("No documents accumulated for BM25 build.")
            return

        print(f"Building BM25 index for {len(self.build_corpus_tokens)} chunks...")
        self.bm25 = BM25Okapi(self.build_corpus_tokens)
        self.bm25_mapping = self.build_corpus_ids
        
        # Ensure db directory exists
        os.makedirs(self.db_path, exist_ok=True)
        
        print("Saving BM25 index to disk...")
        with open(self.bm25_index_path, 'wb') as f:
            pickle.dump(self.bm25, f)
        with open(self.bm25_mapping_path, 'wb') as f:
            pickle.dump(self.bm25_mapping, f)
        print("BM25 index saved.")
        
        # Clear memory
        self.build_corpus_tokens = []
        self.build_corpus_ids = []

    def reciprocal_rank_fusion(self, results: Dict[str, Dict[str, float]], k=60):
        """
        Combines ranked results using Reciprocal Rank Fusion.
        results: Dict mapping doc_id to {'bm25_rank': int, 'chroma_rank': int}
        """
        fused_scores = {}
        for doc_id, ranks in results.items():
            bm25_score = 0
            chroma_score = 0
            
            if 'bm25_rank' in ranks:
                bm25_score = 1 / (k + ranks['bm25_rank'])
            if 'chroma_rank' in ranks:
                chroma_score = 1 / (k + ranks['chroma_rank'])
                
            fused_scores[doc_id] = bm25_score + chroma_score
            
        # Sort by score descending
        sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results

    def hybrid_query(self, query_text: str, top_k=5):
        """
        Performs Hybrid Search (BM25 + Chroma) with RRF.
        """
        if not self.bm25:
            print("Warning: BM25 not initialized, falling back to vector search.")
            return self.query(query_text, n_results=top_k)

        # 1. BM25 Search
        tokenized_query = self.simple_tokenize(query_text)
        # rank_bm25 doesn't give indices directly easily with scores, using get_scores
        bm25_scores = self.bm25.get_scores(tokenized_query)
        # Get top N indices
        top_n_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
        
        bm25_results = {}
        for rank, idx in enumerate(top_n_bm25_indices):
            doc_id = self.bm25_mapping[idx]
            bm25_results[doc_id] = rank + 1 # 1-based rank

        # 2. Chroma Search
        chroma_res = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        chroma_results = {}
        if chroma_res['ids'] and chroma_res['ids'][0]:
            for rank, doc_id in enumerate(chroma_res['ids'][0]):
                chroma_results[doc_id] = rank + 1

        # 3. Fusion
        all_ids = set(bm25_results.keys()) | set(chroma_results.keys())
        fusion_input = {}
        for doc_id in all_ids:
            fusion_input[doc_id] = {}
            if doc_id in bm25_results:
                fusion_input[doc_id]['bm25_rank'] = bm25_results[doc_id]
            if doc_id in chroma_results:
                fusion_input[doc_id]['chroma_rank'] = chroma_results[doc_id]
        
        fused_ranked = self.reciprocal_rank_fusion(fusion_input)
        
        # 4. Fetch Documents for Final Output
        # We need to get details for the top k fused results
        top_fused_ids = [doc_id for doc_id, score in fused_ranked[:top_k]]
        
        if not top_fused_ids:
            return {'ids': [[]], 'metadatas': [[]], 'documents': [[]]}

        # Fetch from Chroma by ID
        final_docs = self.collection.get(ids=top_fused_ids)
        
        # Chroma .get() returns lists not necessarily in order of request ids? 
        # We should align them to the fused order.
        
        # Map ID to its data
        id_to_data = {
            id_: {'metadata': meta, 'document': doc} 
            for id_, meta, doc in zip(final_docs['ids'], final_docs['metadatas'], final_docs['documents'])
        }
        
        ordered_ids = []
        ordered_metas = []
        ordered_docs = []
        
        for id_ in top_fused_ids:
            if id_ in id_to_data:
                ordered_ids.append(id_)
                ordered_metas.append(id_to_data[id_]['metadata'])
                ordered_docs.append(id_to_data[id_]['document'])
                
        return {
            'ids': [ordered_ids],
            'metadatas': [ordered_metas],
            'documents': [ordered_docs]
        }

    def query(self, query_text: str, n_results=3):
        # Let Chroma handle query embedding
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

def main():
    print("Starting JUCE RAG System Builder...")
    
    scraper = JuceScraper()
    processor = JuceProcessor()
    vector_store = VectorStore()
    
    # 1. Scrape and Process
    links = scraper.get_class_list()
    if not links:
        print("No links found. Exiting.")
        return

    # For demonstration/testing purposes, limit to first 50 or verify if we should run all
    # The PRP implies running widely ("Iterate through the Class List"). 
    # I'll implement batching.
    
    batch_size = 100
    current_batch = []
    
    total_processed = 0
    
    for i, link in enumerate(links):
        doc = scraper.scrape_content(link)
        if not doc.items:
            continue
            
        chunks = processor.chunk_document(doc)
        current_batch.extend(chunks)
        
        if len(current_batch) >= batch_size:
            print(f"Upserting batch of {len(current_batch)} chunks...")
            vector_store.add_documents(current_batch)
            total_processed += len(current_batch)
            current_batch = []
            
    # Final batch
    if current_batch:
        print(f"Upserting final batch of {len(current_batch)} chunks...")
        vector_store.add_documents(current_batch)
        total_processed += len(current_batch)
        
    print("Building BM25 Index...")
    vector_store.build_and_save_bm25()
        
    print(f"Finished. Total chunks stored: {total_processed}")

if __name__ == "__main__":
    main()
