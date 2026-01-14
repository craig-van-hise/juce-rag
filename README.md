# JUCE Expert RAG System

A local Retrieval-Augmented Generation (RAG) system designed to answer technical questions about the [JUCE C++ Framework](https://juce.com/) with high precision.

## 🚀 Overview

This project implements a complete RAG pipeline that:
1.  **Scrapes** the official JUCE documentation.
2.  **Chunks** content semantically (by class, method, and concept).
3.  **Embeds** text using a local **Ollama** model (`embeddinggemma`).
4.  **Stores** vectors in **ChromaDB** for semantic retrieval.
5.  **Indexes** keywords using **BM25** for exact match precision (Hybrid Search).
6.  **Synthesizes** answers using a Smart Agent (Google Gemini) that reasons over the retrieved context.

## 🌟 Features

*   **Hybrid Search Engine**: Combines Vector Search (semantic understanding) with BM25 (keyword precision) using Reciprocal Rank Fusion (RRF). This ensures exact class names like `juce::AudioBuffer` are found alongside conceptual queries like "how to handle midi".
*   **Semantic Chunking**: Custom scraper parses HTML to respect API boundaries, keeping method signatures and descriptions together.
*   **Smart Agent**: A `JuceReasoningAgent` that doesn't just find links but writes code examples and explanations.
*   **ADK & Native Support**: designed to run within the Google Agent Development Kit (ADK) ecosystem or as a standalone Python script.

## 🛠️ Prerequisites

*   **Python 3.10+**
*   **Ollama**: Running locally with the `embeddinggemma` model pulled.
    ```bash
    ollama pull embeddinggemma
    ```
*   **Google Cloud Project**: With Vertex AI/Gemini API enabled application default credentials (ADC) or a `GOOGLE_API_KEY`.

## 📦 Installation
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you encounter `opentelemetry` conflicts, ensure versions match those in `requirements.txt` (specifically `1.37.0` for SDK/API).*

2.  **Verify Ollama**:
    Ensure your local Ollama instance is running at `http://<YOUR_OLLAMA_IP>:11434` (or update `src/build_rag.py` with your local IP).

## 🏃 Usage

### 1. Build the Knowledge Base
Run the ingestion script to scrape docs and build the ChromaDB/BM25 indexes.
```bash
python3 src/build_rag.py
```
*   **Output**: Database stored in `data/juce_chroma_db`.
*   **Note**: This process may take 5-10 minutes depending on network and CPU.

### 2. Verify the System
Run the included test suite to check connectivity, retrieval quality, and ranking logic.
```bash
python3 tests/test_rag.py
```

### 3. Run the Smart Agent (Standalone)
To interact with the agent directly in terminal:
```python
from src.agent import JuceReasoningAgent

agent = JuceReasoningAgent()
response = agent.ask("How do I create a basic AudioProcessor?")
print(response)
```

### 4. Run as MCP Server (IDE Integration)
Expose the RAG tool to your IDE via the Model Context Protocol:
```bash
fastmcp run src/server.py
```

## 📂 Project Structure

```text
/
├── data/                  # Stored ChromaDB & BM25 Indexes
├── src/
│   ├── build_rag.py       # Scraper, Chunker, & Database Builder
│   ├── agent.py           # "Smart" Reasoning Agent (Gemini + RAG)
│   ├── adk_agent.py       # ADK-specific Agent wrapper
│   ├── adk_tools.py       # ADK Tool definitions
│   └── server.py          # MCP Server for IDE tools
├── tests/                 # Integration & Unit Tests
├── WoL.py                 # Utility: Wake-on-LAN script
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

*   **Model Settings**: 
    *   Embedding Model: Defined in `src/build_rag.py` (`OllamaEmbeddingFunction`).
    *   Reasoning Model: Defined in `src/agent.py` (`gemini-1.5-flash`).
*   **Database Path**: Default is `data/juce_chroma_db` relative to project root.

## 🤝 Contributing
1.  Run `tests/test_rag.py` before submitting changes to ensure retrieval regression tests pass.
2.  If modifying the scraper, verify `Section A.3` of the test suite (Content Extraction).
