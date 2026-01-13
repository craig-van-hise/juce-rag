
import os
import sys
# Add src to path
sys.path.append(os.path.abspath("src"))

from src.agent import JuceReasoningAgent
from dotenv import load_dotenv

# Load env variables (looking for GOOGLE_API_KEY)
load_dotenv()

def run_demo():
    print("Initializing Smart Agent...")
    try:
        agent = JuceReasoningAgent() 
    except ValueError as e:
        print(f"\nCRITICAL ERROR: {e}")
        print("Please ensure GOOGLE_API_KEY is set in your environment or a .env file.")
        return

    queries = [
        "How do I create a Slider and listen to its value changes?",
        "What is the best way to iterate over MidiMessages in processBlock?",
        "Explain how to use the AudioBuffer class to manage samples."
    ]
    
    print(f"\nRunning {len(queries)} test queries...\n")
    
    for q in queries:
        print(f"QUERY: {q}")
        print("-" * 60)
        try:
            answer = agent.ask(q)
            print(f"AGENT RESPONSE:\n{answer}\n")
        except Exception as e:
            print(f"ERROR: {e}\n")
        print("=" * 60 + "\n")

if __name__ == "__main__":
    run_demo()
