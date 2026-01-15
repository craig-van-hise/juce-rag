
import sys
import os

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.agent import JuceReasoningAgent

def main():
    print("Initializing Agent...")
    try:
        agent = JuceReasoningAgent()
    except ValueError as e:
        print(f"Error initializing agent: {e}")
        return

    query = "How do I use a juce::Slider?"
    print(f"\nAsking Agent: '{query}'\n")
    
    answer = agent.ask(query)
    
    print("\n--- Agent Answer ---\n")
    print(answer)
    print("\n--------------------\n")

if __name__ == "__main__":
    main()
