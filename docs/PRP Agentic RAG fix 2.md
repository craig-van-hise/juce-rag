The error message is the "smoking gun." It tells us exactly why "Native Auth" is failing.

**The Diagnosis:**
"Native Auth" (Anti-Gravity) provides the **Identity** (the keys), but the SDK still needs the **Destination** (Project ID and Region).
The error `ValueError: ... To use the Google Cloud API, provide (vertexai, project & location)` means the code is defaulting to the public API (which needs an API key) because it doesn't know *which* Google Cloud Project to bill against.

**The Solution:**
We need to update `src/adk_agent.py` to grab the Project ID and Region from the Anti-Gravity environment variables.


# Code Fix: Initialize Vertex AI for Anti-Gravity

**Error Analysis:**
The previous test failed with `ValueError: Missing key inputs...`.
This confirms that while we have credentials (ADC), we are missing the **Project Configuration**.

**Task: Update `src/adk_agent.py**`
Rewrite `src/adk_agent.py` to explicitly initialize Vertex AI using environment variables.

**Requirements:**

1. Import `os` and `vertexai`.
2. Retrieve `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_REGION` from the environment.
3. Pass these into the `Agent` or `vertexai.init` configuration.

**Reference Code (Use this logic):**

```python
import os
import vertexai
from google_adk import Agent
from .adk_tools import search_juce_docs

# 1. GET CONFIG FROM ENV (Anti-Gravity provides these)
# Fallback to a default if missing, or raise error
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

if not project_id:
    # Try to determine from default credentials if env var is missing
    import google.auth
    _, project_id = google.auth.default()

print(f"DEBUG: Initializing Agent with Project: {project_id}, Location: {location}")

# 2. INIT VERTEX AI
vertexai.init(project=project_id, location=location)

# 3. DEFINE AGENT
# We pass the vertexai-compatible model name
JuceExpertAgent = Agent(
    name="JuceExpert",
    model="gemini-3-pro", # Ensure this model ID is valid in your region
    tools=[search_juce_docs],
    instructions="""
        You are a JUCE C++ Expert. 
        1. Query the search tool to get documentation.
        2. Analyze the retrieved context.
        3. Answer the user's question with code examples.
    """
)

```

**Task: Run Validation**
After updating the file, run the test script again:

```bash
python3 tests/evaluate_10_queries.py

```

