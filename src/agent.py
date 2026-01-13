
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

from .build_rag import VectorStore

class JuceReasoningAgent:
    def __init__(self, api_key=None):
        # 1. Setup API Key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        genai.configure(api_key=self.api_key)
        
        # 2. Initialize Model
        # Using flash for speed/cost effectiveness for the internal reasoning layer
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=(
                "You are an expert C++ JUCE Framework Developer. "
                "Your goal is to answer the user's question based on the provided documentation context. "
                "Synthesize the information into a clear, concise guide. "
                "Always cite the relevant class names and URLs found in the context. "
                "If the context is irrelevant, state that you cannot find the answer in the local docs."
            )
        )
        
        # 3. Initialize RAG Store
        try:
             self.store = VectorStore()
        except Exception as e:
            print(f"Error initializing VectorStore: {e}")
            self.store = None

    def ask(self, query: str) -> str:
        """
        Orchestrates the RAG flow: Retrieve -> Augment -> Generate
        """
        if not self.store:
            return "Error: Database not initialized."

        print(f"[Agent] Searching docs for: '{query}'")
        try:
            results = self.store.hybrid_query(query, top_k=5)
        except Exception as e:
            return f"Error during query: {e}"
        
        # Step 2: Context Construction
        context_parts = []
        
        if not results or not results.get('documents') or not results['documents'][0]:
            print("[Agent] No documents found.")
            return "I couldn't find any relevant documentation in the local database for that query."

        for i, doc_text in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i]
            title = meta.get('title', 'Unknown Title')
            url = meta.get('url', 'No URL')
            
            context_part = (
                f"--- DOCUMENT {i+1} ---\n"
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Content:\n{doc_text}\n"
            )
            context_parts.append(context_part)
            
        full_context = "\n".join(context_parts)
        
        # Step 3: Prompting
        user_prompt = (
            f"User Query: {query}\n\n"
            f"Here is the retrieved documentation context:\n"
            f"{full_context}\n\n"
            f"Please synthesize an answer."
        )
        
        print("[Agent] Generating answer with Gemini...")
        try:
            response = self.model.generate_content(user_prompt)
            return response.text
        except Exception as e:
            return f"Error using Gemini API: {e}"
