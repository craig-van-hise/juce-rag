import os
try:
    from src.build_rag import VectorStore
except ImportError:
    from build_rag import VectorStore

def search_juce_docs(query: str) -> str:
    """
    Search the JUCE C++ Framework documentation for classes, methods, and concepts.
    Returns snippets of relevant documentation.
    
    Args:
        query: The search query (e.g. "AudioBuffer", "how to use Slider").
    """
    # Create a fresh VectorStore instance for every call as requested
    try:
        # User requested explicit absolute path handling here as well
        # __file__ is src/adk_tools.py -> dirname is src/ -> dirname is root
        src_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(src_dir)
        db_path = os.path.join(project_root, "data", "juce_chroma_db")
        store = VectorStore(db_path=db_path)
    except Exception as e:
        return f"Error initializing VectorStore: {e}"

    print(f"[Tool] Searching for: {query}")
    try:
        results = store.hybrid_query(query, top_k=5)
    except Exception as e:
        return f"Error executing search: {e}"
        
    if not results or not results.get('documents') or not results['documents'][0]:
        return "No relevant documentation found in the local database."
        
    output = []
    for i, doc_text in enumerate(results['documents'][0]):
        meta = results['metadatas'][0][i]
        title = meta.get('title', 'Unknown')
        url = meta.get('url', '#')
        
        snippet = (
            f"--- Document {i+1} ---\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Content:\n{doc_text}\n"
        )
        output.append(snippet)
        
    return "\n".join(output)

