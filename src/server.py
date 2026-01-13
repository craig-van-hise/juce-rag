from mcp.server.fastmcp import FastMCP
import sys
import os

# Import your existing VectorStore logic
# We assume build_rag.py is in the same directory or properly referenced
sys.path.append(os.path.dirname(__file__))
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
    # Return a clean string representation for the AI to read
    return str(results)

if __name__ == "__main__":
    mcp.run()