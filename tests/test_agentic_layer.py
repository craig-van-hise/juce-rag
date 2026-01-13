
import pytest
import unittest.mock as mock
import os
import sys

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent import JuceReasoningAgent

class TestAgenticLayer:
    
    @pytest.fixture
    def mock_agent(self):
        """Creates an agent with mocked Gemini and VectorStore."""
        with mock.patch("src.agent.genai.GenerativeModel") as MockModel, \
             mock.patch("src.agent.VectorStore") as MockStore, \
             mock.patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"}):
            
            agent = JuceReasoningAgent(api_key="fake_key")
            
            # Setup Mock Model
            mock_response = mock.Mock()
            mock_response.text = "This is a synthesized answer about Sliders."
            agent.model.generate_content.return_value = mock_response
            
            # Setup Mock Store
            agent.store.hybrid_query.return_value = {
                'documents': [['Chunk 1 text about Slider', 'Chunk 2 text about Listener']],
                'metadatas': [[{'title': 'Slider Class', 'url': 'http://juce.com/slider'}, 
                               {'title': 'Listener Class', 'url': 'http://juce.com/listener'}]]
            }
            
            yield agent

    def test_mocked_ask_flow(self, mock_agent):
        """
        Verifies that asking a question:
        1. Queries the VectorStore
        2. Formats the prompt
        3. Calls Gemini
        4. Returns the result
        """
        response = mock_agent.ask("How do I use a Slider?")
        
        # Verify Store Call
        mock_agent.store.hybrid_query.assert_called_once()
        args, _ = mock_agent.store.hybrid_query.call_args
        assert "Slider" in args[0]
        
        # Verify Model Call (Prompt Construction)
        mock_agent.model.generate_content.assert_called_once()
        prompt_arg = mock_agent.model.generate_content.call_args[0][0]
        
        # Check prompt contains context
        assert "Chunk 1 text about Slider" in prompt_arg
        assert "Slider Class" in prompt_arg
        
        # Check Final Response
        assert response == "This is a synthesized answer about Sliders."

    @pytest.mark.live
    def test_live_agent_smoke(self):
        """
        Actual Integration Test. Requires GOOGLE_API_KEY in env.
        Skipped if no key found.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("Skipping live test: GOOGLE_API_KEY not found.")
            
        try:
            agent = JuceReasoningAgent(api_key=api_key)
            response = agent.ask("How do I create a slider?")
            
            print(f"\n[Live Response]: {response}")
            
            assert response is not None
            assert len(response) > 20
            # Expecting a synthesized answer, likely checking for "Slider" keyword
            assert "Slider" in response or "slider" in response
            
        except Exception as e:
            pytest.fail(f"Live agent failed: {e}")
