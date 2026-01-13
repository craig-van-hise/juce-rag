import sys
from dataclasses import dataclass
try:
    from src.adk_tools import search_juce_docs
except ImportError:
    from adk_tools import search_juce_docs


@dataclass
class ModelConfig:
    model_name: str

class JuceExpertAgent:
    model = ModelConfig(model_name="gemini-3-pro")
    tools = [search_juce_docs]

    def __init__(self):
        self.name = "JUCE Expert"
        
    async def consult(self, query, context_session):
        """
        Directly queries the RAG system and returns the raw documentation results.
        The 'Conductor' (Antigravity IDE) will interpret these results.
        """
        # 1. RAG LOOKUP
        # We query the vector DB using the existing tool function
        rag_docs = search_juce_docs(query)

        # 2. RETURN CONTEXT
        # Since the client doesn't support sampling, we return the raw docs
        # for the Conductor to interpret.
        return f"""[JUCE EXPERT RAG RESULTS]
Query: {query}

{rag_docs}
"""

# Export the Single Agent instance
juce_expert = JuceExpertAgent()