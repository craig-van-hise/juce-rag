

# Product Requirements Prompt: ADK-Based Agentic RAG

**Role:** Google Ecosystem Specialist & Python Architect
**Project:** JUCE Documentation RAG System
**Environment:** **Google Anti-Gravity IDE** (Native Agent Support)
**Frameworks:** * **Google ADK** (Agent Development Kit)

* **MCP** (Model Context Protocol)

## 1. The Objective

We need to upgrade our passive RAG system into a "Smart RAG" using the **Google ADK**.
Instead of just returning search results, we will create an **ADK Agent** that:

1. Has our existing `VectorStore` as a **Tool**.
2. Uses **Gemini 3** (native access) to reason about the user's query.
3. Critiques the search results and synthesizes a final answer.
4. Is exposed as an **MCP Server** so other agents in the Anti-Gravity ecosystem can call it.

**Constraint:** Do NOT use `genai.configure(api_key=...)`. Rely on the native environment authentication provided by Anti-Gravity and the ADK.

## 2. Implementation Specs

### Step A: Dependencies

Update `requirements.txt` to include:

* `google-adk` (The Agent Development Kit)
* `mcp`
* `pytest`

### Step B: The Tool Wrapper (`src/adk_tools.py`)

Wrap our existing `VectorStore` so the ADK agent can understand it.

* Create a function `search_juce_docs(query: str) -> str`.
* This function instantiates `VectorStore`, runs `hybrid_query`, and formats the output as a string (Document Title + URL + Content Snippet).
* **Crucial:** Decorate this function or wrap it as an `adk.Tool` (or `FunctionTool` depending on ADK syntax) so the agent can invoke it.

### Step C: The ADK Agent (`src/adk_agent.py`)

Create the "Smart Layer" using the ADK.

* **Model:** Use `"gemini-3-pro"` (or the appropriate internal model ID supported by Anti-Gravity).
* **Definition:** Create an agent (e.g., `JuceExpertAgent`).
* **Tools:** specificy `tools=[search_juce_docs]`.
* **Instructions:** > "You are an expert JUCE C++ Framework developer. When asked a question, use the `search_juce_docs` tool to find information. Read the results carefully. Discard irrelevant C++ results. Synthesize a clear, step-by-step answer citing the documentation URLs."
* **Auth:** Ensure the agent initializes using the environment's default credentials (ADC).

### Step D: The MCP Interface (`src/server.py`)

Expose the ADK Agent as an MCP Server.

* Initialize `FastMCP("JUCE Smart Search")`.
* Create a tool `ask_juce(query: str)`.
* **Logic:** This tool should invoke the `JuceExpertAgent.run(query)` (or equivalent ADK execution method) and return the text result.

## 3. Validation Strategy

We need to verify this works without breaking the native environment.

### Create `tests/test_adk_integration.py`

1. **Test 1: Tool Availability (Unit)**
* Verify that `search_juce_docs` can be called directly and returns a string from your local ChromaDB.


2. **Test 2: Agent Definition (Configuration)**
* Verify the ADK Agent is initialized with the correct model name (`gemini-3...`) and has the tool attached.


3. **Test 3: Smoke Test (Live)**
* *Note to Agent:* Mark this with `@pytest.mark.live`.
* Attempt to run the agent with a simple query ("Hello").
* **Goal:** This confirms the Native Auth is working. If it fails due to auth, print a friendly message about checking Anti-Gravity environment login.



---

## 4. Execution Command

Please implement the files in this order:

1. `src/adk_tools.py`
2. `src/adk_agent.py`
3. `src/server.py`
4. `tests/test_adk_integration.py`

Then run the validation:

```bash
python -m pytest tests/test_adk_integration.py

```