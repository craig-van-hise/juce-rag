
# Refactor Request: Fix Agent Auth & Architecture

**Context:** We have an existing RAG setup. We attempted to build an Agent layer, but it is currently broken because it tries to use API keys or mocks the connection.
**Goal:** Rewrite the Agent layer to correctly use **Google Anti-Gravity Native Auth** and the **Google ADK**.

## 1. The Core Fix

We are **not** starting over, but we are replacing the logic in `src/adk_agent.py` and `src/server.py`.

**Stop doing this:**

* ❌ `genai.configure(api_key=...)` (We are in Anti-Gravity; use ADC).
* ❌ `unittest.mock` (Do not fake the test results).
* ❌ "Simulating" the search.

**Start doing this:**

* ✅ Use `google_adk.Agent` with `model="gemini-3-pro"`.
* ✅ Use the existing `VectorStore` class as a real tool.

## 2. File-by-File Refactor Instructions

### A. Refactor `src/adk_tools.py`

* **Action:** Open this file.
* **Logic:** Ensure the `search_juce_docs` function creates a *fresh instance* of `VectorStore` every time it runs.
* **Decorator:** Ensure it is decorated with `@tool` (from `google_adk`) so the agent can see it.

### B. Refactor `src/adk_agent.py`

* **Action:** Completely rewrite this file.
* **Code Spec:**
```python
from google_adk import Agent
from .adk_tools import search_juce_docs

# Initialize the Agent using Native Auth (no API key param needed)
JuceExpertAgent = Agent(
    name="JuceExpert",
    model="gemini-3-pro",  # NATIVE MODEL ID
    tools=[search_juce_docs],
    instructions="""
        You are a JUCE C++ Expert. 
        1. Always use the search tool to find information. 
        2. Analyze the returned hybrid search results. 
        3. Synthesize the answer.
    """
)

```



### C. Refactor `src/server.py`

* **Action:** Update the MCP server to use the new `JuceExpertAgent`.
* **Logic:**
```python
@mcp.tool()
def ask_juce_expert(query: str) -> str:
    # Call the ADK agent directly
    response = JuceExpertAgent.run(query)
    return response.text

```



## 3. The "Truth" Test (`tests/test_fix_live.py`)

Create a new test file to verify the fix.

* **Requirement:** This test must **FAIL** if the network is down. It must **NOT** pass using mocks.
* **Code:**
```python
import pytest
from src.adk_agent import JuceExpertAgent

@pytest.mark.live
def test_live_agent_connection():
    # This will only work if Native Auth is correct
    response = JuceExpertAgent.run("How do I create a Slider?")
    print(f"\nREAL RESPONSE: {response.text}")

    # Validation
    assert "Slider" in response.text
    assert len(response.text) > 50

```



## 4. Execution

1. Apply these refactors to the code.
2. Run `pytest tests/test_fix_live.py -s` immediately to prove the connection works.