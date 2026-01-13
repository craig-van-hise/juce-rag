# test_agent_direct.py
import sys
import os
import uuid
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

# Minimal wrapper classes to satisfy ADK type strictness
class SimplePart:
    def __init__(self, text):
        self.text = text

class SimpleContent:
    def __init__(self, text):
        self.role = "user"
        self.parts = [SimplePart(text)]

print(f"--- DIAGNOSTICS ---")
print(f"Python Executable: {sys.executable}")

try:
    print("\n[1/4] Importing Agent...")
    sys.path.append(os.path.abspath("src"))
    from src.adk_agent import JuceExpertAgent
    print("✅ Agent imported.")

    print("\n[2/4] Setting up Runner & Session...")
    # The ADK needs a session service to store chat history
    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())
    user_id = "test_user"
    app_name = "JuceTestApp"

    # Create the session first
    session_service.create_session_sync(
        app_name=app_name, 
        user_id=user_id, 
        session_id=session_id
    )

    # Initialize the Runner
    runner = Runner(
        agent=JuceExpertAgent,
        app_name=app_name,
        session_service=session_service
    )
    print("✅ Runner initialized.")

    print("\n[3/4] Running Query: 'How do I create a Slider?'...")
    query_object = SimpleContent("How do I create a Slider?")
    
    # We must iterate over the events the runner yields
    full_response = ""
    print("   (Waiting for stream...)")
    
    for event in runner.run(user_id=user_id, session_id=session_id, new_message=query_object):
        # We capture text from specific event types
        if hasattr(event, 'text') and event.text:
            full_response += event.text
            print(f"   -> Chunk received: {len(event.text)} chars")
        elif hasattr(event, 'model_response'):
             resp = event.model_response
             if hasattr(resp, 'parts'):
                 for p in resp.parts:
                     if hasattr(p, 'text'):
                         full_response += p.text
                         print("   -> Model chunk received")

    print("\n" + "="*40)
    print("FINAL RESPONSE FROM GEMINI 3:")
    print("="*40)
    if not full_response:
        print("⚠️  No text returned. (This might happen if Auth failed silently inside the stream)")
    else:
        print(full_response)
    print("="*40)

except Exception as e:
    print(f"\n❌ RUNTIME ERROR: {e}")
    import traceback
    traceback.print_exc()