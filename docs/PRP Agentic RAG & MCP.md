

# Product Requirements Prompt: Agentic RAG & MCP Implementation

**Role:** Senior Python Systems Architect & AI Engineer
**Project:** JUCE Documentation RAG System (Existing)
**Goal:** Upgrade the existing passive RAG system into an **Agentic RAG** (using Google Gemini) and expose it via a **Model Context Protocol (MCP)** server.

## 1. Context & Environment

We have a working RAG system in `src/` that uses ChromaDB and BM25.

* **Existing Entry Point:** `src.build_rag.VectorStore` class.
* **Method to Call:** `store.hybrid_query(query_text)` returns a dictionary of documents and metadata.
* **Target SDKs:**
* `google-generativeai` (for the reasoning layer).
* `mcp` (for the server interface).



## 2. Implementation Tasks

### Task A: Dependency Management

Update the environment to support the new agentic layers.

* **Action:** Create/Update `requirements.txt` or install instructions to include:
* `google-generativeai`
* `mcp[cli]` (or `mcp` standard library)
* `python-dotenv` (for API key management)



### Task B: Create the Reasoning Agent (`src/agent.py`)

Create a class `JuceReasoningAgent` that acts as the "brain" between the user and the database.

**Requirements:**

1. **Initialization:**
* Accept a `google_api_key`.
* Initialize the `VectorStore` (existing class).
* Initialize a Google Gemini model (recommend `gemini-1.5-flash` for speed/cost or `gemini-1.5-pro` for complex reasoning).


2. **Core Method:** `ask(query: str) -> str`
* **Step 1:** Perform a `hybrid_query` using `VectorStore`. Fetch top 5-10 results.
* **Step 2 (The Thinking Layer):** Construct a prompt for Gemini.
* *Input:* User Query + Raw Search Results (Chunk text + Source URL).
* *System Instruction:* "You are an expert C++ JUCE Developer. Review the provided documentation chunks. Ignore irrelevant chunks. Synthesize a concise, technically accurate answer to the user's question based *only* on the provided context. If the context is insufficient, state that. Always cite the relevant class names and URLs."


* **Step 3:** Return the synthesized text.


3. **Error Handling:** Gracefully handle missing API keys or empty search results.

### Task C: Create the MCP Server (`src/server.py`)

Create a standardized server file to expose this agent to other tools (Claude, Cursor, IDEs).

**Requirements:**

1. Use `FastMCP` (from the `mcp` library).
2. Name the server "JUCE Documentation Expert".
3. Define a tool named `consult_juce_docs`.
* **Description:** "Queries the local JUCE C++ framework documentation. Use this for questions about JUCE classes, modules, or implementation details."
* **Arguments:** `query` (string).
* **Implementation:** Instantiates `JuceReasoningAgent` and calls `.ask(query)`.


4. Ensure it loads the `GOOGLE_API_KEY` from environment variables.

### Task D: Validation Suite (`tests/test_agentic_layer.py`)

We need to verify this works without burning API credits on every run (mocking) and a way to test it for real.

**Requirements:**

1. **Test 1: Mocked Integration:**
* Mock `google.generativeai.GenerativeModel.generate_content`.
* Mock `VectorStore.hybrid_query`.
* *Assert:* The agent correctly formats the prompt from the "search results" and returns the "model response".


2. **Test 2: Live Smoke Test (Marked `@pytest.mark.live`):**
* Requires a real API key.
* Runs a real query ("How do I use a Slider?") and asserts the response is non-empty and contains keywords like "Slider" or "Listener".



## 3. Execution Instructions for the Agent

Please execute the following steps:

1. Install the required libraries.
2. Write `src/agent.py` adhering to the logic defined in Task B.
3. Write `src/server.py` adhering to the MCP standards in Task C.
4. Write `tests/test_agentic_layer.py` using `unittest` or `pytest`.
5. **Run the tests** and output the results to confirm the system is operational.

---

### 4. Verification

Once you have generated the files, run the validation command:

```bash
python -m pytest tests/test_agentic_layer.py -v

```