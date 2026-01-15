
import sys
import os

# Ensure we can import from src
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.adk_tools import search_juce_docs

def main():
    query = "how to manage a juce::AudioProcessorValueTreeState with a juce::Slider"
    print(f"Querying: {query}")
    result = search_juce_docs(query)
    print("\n--- Result ---\n")
    print(result)

if __name__ == "__main__":
    main()
