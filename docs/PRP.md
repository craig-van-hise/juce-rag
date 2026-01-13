
# Product Requirements Prompt (PRP)
**Project:** JUCE Documentation RAG System
**Target Agent:** Gemini 3 Pro (Google Antigravity IDE)
**Role:** Senior Data Engineer / Python Developer

## 1. Project Overview
We are building a local RAG (Retrieval-Augmented Generation) system for the [JUCE C++ Framework Documentation](https://docs.juce.com/master/index.html). The system must scrape the documentation, intelligently chunk the data to preserve code context, embed it using `EmbeddingGemma`, and store it in a local `ChromaDB` instance.

## 2. Technical Stack
* **Language:** Python 3.12+
* **Scraping:** `requests`, `BeautifulSoup4`
* **Vector Database:** `chromadb` (Persistent Local Storage)
* **Embedding Model:** `google/embedding-gemma-300m` (via `sentence-transformers`)
* **Processing:** `langchain-text-splitters`

## 3. Implementation Requirements

### A. Scraper (Data Acquisition)
* **Target:** Iterate through the Class List at `https://docs.juce.com/master/classes.html`.
* **Filtering:** Ignore standard headers/footers. Focus on the main content block (`#content` or `.contents`).
* **Output:** List of dictionaries containing `source_url`, `title`, and `raw_text`.

### B. Chunking Strategy (Critical)
Do not embed entire HTML pages. The context window is limited, and C++ documentation requires precise retrieval of specific methods or class descriptions.

**Use `RecursiveCharacterTextSplitter` with these specific parameters:**
1.  **Chunk Size:** 1000 tokens (approx. 4000 characters).
2.  **Overlap:** 200 tokens (approx. 800 characters).
3.  **Separators:** Prioritize splitting on double newlines and C++ structural elements:
    * `["\nclass ", "\nstruct ", "\n\n", "\n", " ", ""]`

### C. Embedding & Storage
* Initialize `SentenceTransformer` with `google/embedding-gemma-300m`.
* Initialize `chromadb.PersistentClient`.
* **Upsert Logic:**
    * Generate ID: Hash of the URL + Chunk Index.
    * Metadata: `{"url": "...", "title": "...", "chunk_index": int}`.
    * Document: The chunked text.

## 4. Required Code Structure
Generate a single Python script `build_rag.py` that implements the following classes:

1.  `JuceScraper`: Handles the crawling and text extraction.
2.  `JuceProcessor`: Handles the **chunking logic**.
3.  `VectorStore`: Handles the embedding generation and ChromaDB interfacing.

## 5. Validation & Testing Protocols
You must include a `test_rag.py` suite or a `__main__` verification block that performs the following validation checks before marking the task complete:

### A. Scraper Logic Validation
1.  **Connectivity Check:** Assert HTTP 200 response from `https://docs.juce.com/master/classes.html`.
2.  **Selector Accuracy:** Assert that `JuceScraper` finds > 500 class links (JUCE has significantly more, this filters out parsing errors).
3.  **Content Extraction:** Scrape `juce::AudioBuffer`. Assert `raw_text` contains "Manage a buffer of audio samples".

### B. Chunking Validation
1.  **Token Limit:** Feed a 5000-token string. Assert the output list has > 1 chunk.
2.  **Overlap Check:** Assert the last 50 chars of Chunk N match the first 50 chars of Chunk N+1 (approximately, depending on separator).
3.  **Context Preservation:** Assert that class definitions (lines starting with `class MyClass`) remain at the start of a chunk where possible.

### C. Embedding & Retrieval Sanity Check
1.  **Model Load:** Assert `SentenceTransformer` loads `google/embedding-gemma-300m` without error.
2.  **Vector Dimension:** Encode the string "test". Assert embedding dimension matches model spec (typically 768 or 256 for small variants).
3.  **Integration Test (The "Needle in Haystack"):**
    * Query: "How do I create a slider?"
    * Assert: Top 3 results in ChromaDB include `juce_Slider.html`.

## 6. Execution Steps
1.  Verify environment contains `sentence-transformers` and `chromadb`.
2.  Run scraper against `docs.juce.com`.
3.  Process and Chunk text immediately after scraping.
4.  Batch upsert chunks into ChromaDB (Batch size: 100).
5.  **Run Validation Suite.**
6.  Print total chunks stored and validation results.