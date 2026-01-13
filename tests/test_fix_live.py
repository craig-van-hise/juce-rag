
import pytest
from src.adk_agent import JuceExpertAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

# Mock Content for Runner input
class SimplePart:
    def __init__(self, text): self.text = text
class SimpleContent:
    def __init__(self, text): 
        self.role = "user"
        self.parts = [SimplePart(text)]

@pytest.mark.live
def test_live_agent_connection():
    # This will only work if Native Auth is correct
    print("\n--- Starting Live Connection Test (Native Gemini 3) ---")
    
    session_service = InMemorySessionService()
    app_name = "JuceLiveTest"
    try:
        session_service.create_session_sync(app_name=app_name, user_id="tester", session_id="live_test")
    except Exception as e: 
        # Session might exist or other non-critical
        print(f"Session init note: {e}")

    runner = Runner(agent=JuceExpertAgent, app_name=app_name, session_service=session_service)
    
    response_text = ""
    try:
        # Running the Agent natively via ADK Runner
        for event in runner.run(user_id="tester", session_id="live_test", new_message=SimpleContent("How do I create a Slider?")):
            if hasattr(event, 'text') and event.text:
                response_text += event.text
            elif hasattr(event, 'model_response'):
                 resp = event.model_response
                 if hasattr(resp, 'parts'):
                     for p in resp.parts:
                         if hasattr(p, 'text'):
                             response_text += p.text
                             
    except Exception as e:
        print(f"\nCONNECTION FAILURE: {e}")
        pytest.fail(f"Agent execution failed (likely Auth/Network): {e}")

    print(f"\nREAL RESPONSE: {response_text}")

    # Validation
    if not response_text:
        pytest.fail("Agent returned empty response. Check Authentication.")
        
    assert "Slider" in response_text or "slider" in response_text.lower()
    assert len(response_text) > 50
