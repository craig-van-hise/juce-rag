from mcp.server.fastmcp import FastMCP
import sys
import os

# Import your existing VectorStore logic
# We assume build_rag.py is in the same directory or properly referenced
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from build_rag import VectorStore 

# Initialize Store once
store = VectorStore()
mcp = FastMCP("juce-data-library")

@mcp.tool()
def search_juce_docs(query: str) -> str:
    """
    Retrieves raw text chunks from the local JUCE documentation database.
    Does NOT interpret. Just returns data.
    """
    results = store.hybrid_query(query)
    
    if not results or not results.get('documents') or not results['documents'][0]:
        return "No relevant documentation found."
        
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

if __name__ == "__main__":
    mcp.run()