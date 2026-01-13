
import sys
import os
import time

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

try:
    from src.adk_tools import _search_juce_docs_impl
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

def verify_retrieval():
    print("=============================================================")
    print("       VERIFYING REAL RAG DOCUMENT RETRIEVAL (NO AGENT)      ")
    print("=============================================================")
    print("Using Local ChromaDB + Ollama Embeddings (No Google Auth Req)")
    print("-" * 60)
    
    queries = [
        "How do I create a simple audio distortion effect in processBlock?",
        "Show me how to iterate over MIDI messages in a MidiBuffer.",
        "How do I correctly use AudioBuffer::getWritePointer?",
        "How do I load an audio file into an AudioSampleBuffer using AudioFormatReader?",
        "Explain how to use the ValueTree class for state management.",
        "How do I implement a Slider::Listener?",
        "What is the AbstractFifo class used for?",
        "How do I draw a rectangle in the paint() method?",
        "How to use lookAndFeelChanged()?",
        "How do I create a plugin editor window?"
    ]
    
    for i, q in enumerate(queries):
        print(f"\n[QUERY {i+1}] {q}")
        start_t = time.time()
        
        # ACTUALLY CALLING THE SEARCH FUNCTION
        # This accesses the Real ChromaDB on disk
        result = _search_juce_docs_impl(q)
        
        duration = time.time() - start_t
        print(f"Time: {duration:.4f}s")
        
        # Verify valid return
        if "Error:" in result:
             print(f"FAILURE: {result}")
        elif "No relevant documentation" in result:
             print("FAILURE: No docs found.")
        elif "--- Document" in result:
             print("SUCCESS: Retrieved Real Documents.")
             # Print titles of found docs to prove it
             lines = result.split('\n')
             for line in lines:
                 if line.startswith("Title:"):
                     print(f"  > Found: {line[7:]}")
        else:
             print(f"UNKNOWN RESPONSE: {result[:100]}...")
             
        print("-" * 60)

if __name__ == "__main__":
    verify_retrieval()
