import sys
import os
import time

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adk_agent import JuceExpertAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
import uuid

# Helper to mimic the .run() interface expected by the loop
class ResponseWrapper:
    def __init__(self, text):
        self.text = text

# Mock Content for Runner input
class SimplePart:
    def __init__(self, text): self.text = text
class SimpleContent:
    def __init__(self, text): 
        self.role = "user"
        self.parts = [SimplePart(text)]

def run_agent_query(query_text):
    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())
    app_name = "JuceEval"
    try:
        session_service.create_session_sync(app_name=app_name, user_id="tester", session_id=session_id)
    except: pass
    
    runner = Runner(agent=JuceExpertAgent, app_name=app_name, session_service=session_service)
    
    full_text = ""
    # Run and aggregate text
    for event in runner.run(user_id="tester", session_id=session_id, new_message=SimpleContent(query_text)):
        if hasattr(event, 'text') and event.text:
            full_text += event.text
        elif hasattr(event, 'model_response'):
             resp = event.model_response
             if hasattr(resp, 'parts'):
                 for p in resp.parts:
                     if hasattr(p, 'text'):
                         full_text += p.text
    
    return ResponseWrapper(full_text)

# 10 Diverse Queries to test RAG + Reasoning
queries = [
    "How do I create a basic Slider?",
    "How do I handle button clicks in JUCE?",
    "Explain the AudioProcessorValueTreeState.",
    "What is the difference between OwnedArray and ReferenceCountedObject?",
    "How do I load a VST3 plugin?",
    "How do I draw a rectangle in the paint() method?",
    "How do I use an AudioBuffer?",
    "What is the purpose of the LookAndFeel class?",
    "How do I play a sound file?",
    "How do I implement a timer?"
]

print("--- STARTING 10-QUERY EVALUATION (LIVE GEMINI 3) ---")

for i, q in enumerate(queries):
    print(f"\n[{i+1}/10] Query: {q}")
    try:
        # Measure latency
        start = time.time()
        
        # --- EXECUTE AGENT ---
        # response = JuceExpertAgent.run(q) 
        response = run_agent_query(q)
 
        
        duration = time.time() - start
        
        # Print Result
        print(f"Time: {duration:.2f}s")
        print(f"Response Preview: {response.text[:200]}...") # Show first 200 chars
        
        # Validation checks
        if not response.text:
            print("❌ FAILURE: Empty response")
        else:
            print("✅ SUCCESS: Response received")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

print("\n--- EVALUATION COMPLETE ---")
