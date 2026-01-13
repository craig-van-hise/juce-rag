
import sys
import os
import json
import logging

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

try:
    from src.adk_agent import JuceExpertAgent
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

def run_demo():
    """
    Official Native Gemini 3 Demo Script.
    """
    print("=====================================================")
    print("       NATIVE GEMINI 3 AGENT DEMO (JUCE RAG)         ")
    print("=====================================================")
    
    session_service = InMemorySessionService()
    APP_NAME = "JuceNativeDemo"
    USER_ID = "tester"
    SESSION_ID = "native_test_session"
    
    # Init Session
    try:
        session_service.create_session_sync(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    except Exception:
        pass # Session might exist
    
    runner = Runner(
        agent=JuceExpertAgent,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    queries = [
        "How do I create a simple audio distortion effect in processBlock?",
        "Show me how to iterate over MIDI messages in a MidiBuffer.",
        "How do I correctly use AudioBuffer::getWritePointer?",
        "How do I load an audio file into an AudioSampleBuffer using AudioFormatReader?",
        "Explain how to use the ValueTree class for state management.",
        "How do I implement a Slider::Listener?",
        "What is the AbstractFifo class used for?",
        "How do I draw a rectangle in the paint() method?",
        "How to use lookAndFeelChanged()?",
        "How do I create a plugin editor window?"
    ]
    
    print(f"Executing {len(queries)} queries via Native Gemini 3...\n")
    
    for i, q in enumerate(queries):
        print(f"\n[Query {i+1}] {q}")
        print("-" * 60)
        
        response_text = ""
        # Native Run
        try:
            for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=q):
                text = None
                if hasattr(event, 'text'):
                     text = event.text
                elif hasattr(event, 'model_response'):
                     if hasattr(event.model_response, 'parts'):
                         parts = event.model_response.parts
                         if parts:
                             text = "".join([p.text for p in parts if hasattr(p, 'text')])
                
                if text:
                    print(text, end="", flush=True)
                    response_text += text
            
            if not response_text:
                print("  [No response. Ensure Auth is active.]")
                
        except Exception as e:
            print(f"  [Execution Error: {e}]")
            
        print("\n" + "="*60)

if __name__ == "__main__":
    run_demo()
