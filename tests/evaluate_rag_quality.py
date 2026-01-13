import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import shutil
import time
# from tabulate import tabulate
from src.build_rag import JuceScraper, JuceProcessor, VectorStore, ScrapedDocument
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def setup_test_db(db_path="data/eval_juce_chroma_db"):
    if os.path.exists(db_path):
        print(f"Cleaning previous test DB at {db_path}...")
        shutil.rmtree(db_path)
    
    # Initialize with specific DB path
    store = VectorStore(db_path=db_path, collection_name="eval_collection")
    scraper = JuceScraper()
    processor = JuceProcessor()
    
    return store, scraper, processor

def run_benchmark():
    print_header("STARTING HYBRID RAG BENCHMARK")
    
    db_path = "data/eval_juce_chroma_db"
    store, scraper, processor = setup_test_db(db_path)
    
    # 1. Define Seed URLs (Representative Classes)
    # These cover: Audio (Processor, Buffer), UI (Slider, Component, Graphics), MIDI (MidiMessage), DSP
    target_classes = [
        "AudioProcessor", 
        "AudioBuffer", 
        "MidiMessage", 
        "Slider", 
        "Component", 
        "Graphics",
        "AudioProcessorValueTreeState", # Specific complex class name
    ]
    
    print("\n[PHASE 1] Ingesting seeded documents...")
    all_links = scraper.get_class_list()
    
    seeded_docs = []
    
    for cls_name in target_classes:
        # Simple fuzzy match to find the link
        match = next((l for l in all_links if f"classjuce_1_1{cls_name}.html" in l or f"classjuce_1_1{cls_name.lower()}.html" in l), None)
        # Fallback for simpler names if standard doxygen naming differs
        if not match:
            match = next((l for l in all_links if cls_name in l), None)
            
        if match:
            print(f"  - Scraping {cls_name}...", end="", flush=True)
            doc = scraper.scrape_content(match)
            if doc.items:
                chunks = processor.chunk_document(doc)
                store.add_documents(chunks)
                seeded_docs.append(cls_name)
                print(f" Done ({len(chunks)} chunks)")
            else:
                print(" Failed (No content)")
        else:
            print(f"  - Could not find link for {cls_name}")
            
    print(f"\nbuilding BM25 index for {len(seeded_docs)} documents...")
    store.build_and_save_bm25()
    
    # 2. Define Test Queries
    # Format: (Query Text, Expected Keyword/Concept in Title, Type)
    test_cases = [
        ("AudioProcessor", "AudioProcessor", "Exact Class Name"),
        ("AudioProcesser", "AudioProcessor", "Fuzzy Typo"), # Typo: 'er' vs 'or'
        ("How do I process audio blocks?", "AudioProcessor", "Conceptual"),
        ("processBlock", "AudioProcessor", "Exact Method Name"),
        ("MidiMessage", "MidiMessage", "Exact Class Name"),
        ("MidiMasage", "MidiMessage", "Fuzzy Typo"), # Typo
        ("Handling midi events", "MidiMessage", "Conceptual"),
        ("Slider", "Slider", "Exact Class Name"),
        ("AudioProcessorValueTreeState", "AudioProcessorValueTreeState", "Long Exact Keyword"),
        ("drawing rectangles", "Graphics", "Conceptual"),
        ("paint", "Component", "Method/Concept"),
        ("getMagnitude", "AudioBuffer", "Specific Method"),
        ("clear", "AudioBuffer", "Ambiguous Method") # clear() exists in many, let's see which ranks high
    ]
    
    results_table = []
    
    print("\n[PHASE 2] Running Evaluation Queries...")
    
    for query, expected, q_type in test_cases:
        # Run Vector Only
        vec_res = store.query(query, n_results=5)
        vec_titles = [m['title'] for m in vec_res['metadatas'][0]]
        
        # Run Hybrid
        hyb_res = store.hybrid_query(query, top_k=5)
        hyb_titles = [m['title'] for m in hyb_res['metadatas'][0]]
        
        # Check Ranks (1-based index of first match)
        vec_rank = "Not Found"
        for i, t in enumerate(vec_titles):
            if expected in t:
                vec_rank = i + 1
                break
                
        hyb_rank = "Not Found"
        for i, t in enumerate(hyb_titles):
            if expected in t:
                hyb_rank = i + 1
                break
        
        # Determine Status
        if hyb_rank == vec_rank:
            outcome = "Tie"
        elif hyb_rank != "Not Found" and (vec_rank == "Not Found" or hyb_rank < vec_rank):
            outcome = "Hybrid Win"
        else:
            outcome = "Vector Win" # Rare, but possible if BM25 adds noise
            
        results_table.append([query, q_type, vec_rank, hyb_rank, outcome])

    # 3. Print Results
    print_header("BENCHMARK RESULTS")
    
    # Simple formatting since tabulate might not be installed
    # Columns: Query | Type | Vector Rank | Hybrid Rank | Outcome
    header = f"{'Query':<35} | {'Type':<20} | {'Vector':<8} | {'Hybrid':<8} | {'Outcome'}"
    print(header)
    print("-" * len(header))
    
    hybrid_wins = 0
    total = len(test_cases)
    
    for row in results_table:
        # Truncate query if too long
        q = (row[0][:32] + '..') if len(row[0]) > 32 else row[0]
        line = f"{q:<35} | {row[1]:<20} | {str(row[2]):<8} | {str(row[3]):<8} | {row[4]}"
        print(line)
        
        if row[4] == "Hybrid Win":
            hybrid_wins += 1
            
    print(f"\nSummary: Hybrid improved ranking in {hybrid_wins}/{total} cases.")
    print(f"Test Database saved at: {db_path}")

if __name__ == "__main__":
    run_benchmark()
