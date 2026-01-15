# How to Query the JUCE RAG System

This guide explains how to query the Hybrid RAG system using three methods:
1.  **Agent-Based Query**: Using the reasoning agent to synthesize an answer.
2.  **Direct Retrieval**: Gets raw, reranked documentation snippets via script.
3.  **MCP Server**: Exposes the RAG as a tool to any MCP-compliant client (Cursor, Claude Desktop, Antigravity IDE).

## Prerequisites

Ensure your environment is set up and the virtual environment is valid.
```bash
source .venv/bin/activate
export GOOGLE_API_KEY="your_api_key_here"
```

---

## Method 1: Agent-Based Query (Synthesized Answer)

This method uses the `JuceReasoningAgent` to retrieve documentation and generate a natural language answer using Gemini.

### Usage
Create a python script (e.g., `ask_agent.py`):

```python
import sys
import os

# Ensure src module is in path
sys.path.append(os.getcwd())

from src.agent import JuceReasoningAgent

def main():
    # Initialize the agent (loads RAG + Gemini)
    # Ensure GOOGLE_API_KEY is set in your environment
    agent = JuceReasoningAgent()
    
    query = "How do I create a custom LookAndFeel?"
    print(f"Asking: {query}...\n")
    
    # Get the synthesized answer
    response = agent.ask(query)
    
    print("--- Answer ---")
    print(response)

if __name__ == "__main__":
    main()
```

---

## Method 2: Direct Retrieval (Raw Results)

This method bypasses the LLM and directly queries the ChromaDB vector store, returning the top relevant documentation snippets. This is useful for debugging or if you only need the raw source material.

### Usage
Run the utility script directly:

```bash
python3 query_rag.py
```

---

## Method 3: MCP Server (Universal Access)

You can run the RAG as a Model Context Protocol (MCP) server. This allows you to give *any* MCP-compliant AI agent access to your JUCE documentation, even if they are working in a different project folder.

### 1. Server Script
The server is located at `src/server.py`. It uses `fastmcp` to expose the `search_juce_docs` tool.

### 2. Configuration
Add the following to your MCP Client configuration (e.g., `claude_desktop_config.json`, `cursor.json`, or Antigravity Settings).

**Important**: Replace `/absolute/path/to/...` with your actual full paths.

```json
{
  "mcpServers": {
    "juce-rag": {
      "command": "/absolute/path/to/project/.venv/bin/python",
      "args": [
        "/absolute/path/to/project/src/server.py"
      ],
      "env": {
        "OLLAMA_URL": "http://localhost:11434"
      }
    }
  }
}
```

### 3. Usage
Once configured, your AI assistant will have a tool named `search_juce_docs`. You can simply ask it:
> "Check the JUCE RAG for how to use an AudioBuffer."

The AI will call the tool and see the documentation snippets.
