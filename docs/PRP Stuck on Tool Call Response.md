

**"You are now the Lead Engineer for this session. We are stuck in a broken loop and I need you to fix the MCP Server connection autonomously.**

**PHASE 1: CONTEXT & DIAGNOSIS**

1. Read `PROJECT_STATE.md` to understand the architecture.
2. Read `src/server.py` and `src/adk_agent.py`.
3. **The Problem:** The current implementation in `server.py` tries to initialize a `google.adk.Agent` class. This fails with 'Check Auth' errors because the script lacks the IDE's internal credentials.
4. **The Solution:** We must strip out the 'Agent' wrapper entirely. We need `server.py` to be a "dumb" pipe that simply runs the local `search_juce_docs` function and returns the raw string to the IDE.

**PHASE 2: IMPLEMENTATION (Iterative Loop)**
Your goal is to edit `src/server.py` to satisfy `FastMCP` requirements without using `google.adk`.

**Execute this loop until success:**

1. **Refactor `src/server.py`:**
* Import `FastMCP` from `mcp.server.fastmcp`.
* Import `search_juce_docs` from `adk_tools`.
* Initialize `mcp = FastMCP("juce-expert")`.
* Create a tool `@mcp.tool()` named `ask_juce_expert`.
* Inside the tool, call `search_juce_docs(query)` and return `str(results)`.
* Ensure `if __name__ == "__main__": mcp.run()` is present.


2. **Verify Imports:** Ensure you are NOT importing `JuceExpertAgent` anymore. That file (`adk_agent.py`) is dead code for now.
3. **Wait & Test:** After saving the file, wait 5 seconds for the `FastMCP` server to hot-reload.
4. **VALIDATE:** Attempt to call the tool yourself with the prompt: `How do I create a juce::Slider?`
* **IF** you get "No response" or an error: Analyze the failure, re-read `server.py`, and fix syntax/imports.
* **IF** you get raw text/JSON back: You have succeeded. Inform the user we are ready."**



