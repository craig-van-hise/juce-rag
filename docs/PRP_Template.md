
# Product Requirements Prompt (PRP) Template
**Project:** [PROJECT_NAME] (e.g., General API RAG System)
**Target Agent:** Agentic AI Assistant
**Role:** Senior Machine Learning Engineer / Python Developer

## 1. Project Overview
We are building a robust, local **Hybrid RAG (Retrieval-Augmented Generation)** system for the [TARGET_API_NAME] Documentation located at [DOCS_BASE_URL]. 

The system must:
1.  **Scrape** the documentation (handling both list-pages and individual class/method pages).
2.  **Chunk** the data intelligently to preserve semantic context (e.g., keeping method signatures with their descriptions).
3.  **Embed** the data using a local embedding model.
4.  **Index** the data lexically (BM25) to support exact matching of class/method names.
5.  **Retrieve** information using **Hybrid Search** (Vector + BM25) fused via Reciprocal Rank Fusion (RRF).

## 2. Technical Stack
*   **Language:** Python 3.12+
*   **Scraping:** `requests`, `BeautifulSoup4`
*   **Vector Database:** `chromadb` (Persistent Local Storage)
*   **Embedding Model:** Local Ollama instance (e.g., `embeddinggemma:latest` or similar) OR `sentence-transformers`.
*   **Lexical Search:** `rank_bm25` (BM25Okapi)
*   **Processing:** `langchain-text-splitters` (for fallback chunking)

## 3. Implementation Requirements

### A. Scraper (Data Acquisition)
*   **Target:** Iterate through the main index or class list at [DOCS_INDEX_URL].
*   **Semantic Blocking (Crucial):** 
    *   Do NOT just dump the `<body>`.
    *   Identify individual API members (e.g., `div.memitem`, `dl.function`, or equivalent HTML containers for methods/properties).
    *   Extract the **Signature** (prototype) and **Description** together as a single semantic unit.
    *   Capture specific metadata for each item: `type` (class, method, property), `url`, `title`.

### B. Chunking Strategy
*   **Primary Strategy [Semantic Chunking]:** Use the natural boundaries of the documentation (e.g., one chunk per method/function).
*   **Fallback Strategy:** If a description is massive (> 2000 tokens) or unstructured, fall back to `RecursiveCharacterTextSplitter`.
    *   Chunk Size: 1000 tokens.
    *   Overlap: 200 tokens.

### C. Hybrid Search Architecture (Critical)
The system must support **Hybrid Search** to solve the "Exact Match" problem (where "slider" might not semantically match "juce::Slider" well enough).

1.  **Vector Store**:
    *   Store chunks in ChromaDB.
    *   Use `OllamaEmbeddingFunction` (or equivalent) to generate embeddings.
2.  **Lexical Index (BM25)**:
    *   Maintain a parallel BM25 index using `rank_bm25`.
    *   **Tokenization Rule:** You **MUST** use a regex-based tokenizer (e.g., `re.findall(r'\w+', text.lower())`) to split punctuation.
        *   *Why?* To ensure Namespaced classes like `namespace::Class` are split into `['namespace', 'class']`, allowing queries for `Class` to match exactly.
    *   Save/Load the BM25 index to disk (pickle) to persist along with ChromaDB.
3.  **Reciprocal Rank Fusion (RRF)**:
    *   Implement a `hybrid_query(text, top_k)` method.
    *   Get top $N$ results from Vector Search.
    *   Get top $N$ results from BM25.
    *   Fuse scores: $Score = \frac{1}{k + rank_{vec}} + \frac{1}{k + rank_{bm25}}$.
    *   Return re-ranked unique results.

## 4. Required Code Structure
Generate the following files:

1.  `build_rag.py`: Main orchestration script.
    *   `[ApiName]Scraper`: Handles crawling and semantic parsing.
    *   `[ApiName]Processor`: Logic for chunking (Semantic + Fallback).
    *   `VectorStore`: Manages ChromaDB + BM25 persistence and Hybrid Query logic.
2.  `evaluate_rag_quality.py`: A benchmark script.
    *   Must define a list of "Golden Queries" with expected results.
    *   Test Categories:
        *   **Exact Match**: (e.g., "[ClassName]" -> Matches `[Namespace::ClassName]`)
        *   **Fuzzy/Typo**: (e.g., "[MisspelledName]" -> Matches `[CorrectName]`)
        *   **Conceptual**: (e.g., "How do I [action]?" -> Matches `[RelevantClass]`)
3.  `test_rag.py`: Unit tests for connectivity, chunking limits, and regression tests.

## 5. Validation Protocols
You must verify the system before marking completion:

1.  **Connectivity & Parsing**: Ensure the scraper finds the expected number of pages (approx [EXPECTED_PAGE_COUNT]).
2.  **Tokenization check**: Verify `simple_tokenize` correctly splits `namespace::Class` into `['namespace', 'class']`.
3.  **Exact Match Regression**: Create a test case where a document with a namespaced title is retrieved at Rank 1 by a query for the simple name.
4.  **Benchmark**: Run `evaluate_rag_quality.py` and ensure > 90% "Rank 1" or "Rank 2" success rate for key terms.

## 6. Execution Steps
1.  Setup environment (venv, dependencies).
2.  Implement `build_rag.py`.
3.  Run `build_rag.py` to ingest data (support batching to avoid OOM).
4.  Implement and run `test_rag.py` to pass unit tests.
5.  Implement and run `evaluate_rag_quality.py` to prove search relevance.
6.  Generate a `benchmark_report.md` summarizing the results.
