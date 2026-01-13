
import sys
import os

# Ensure we can import from src
sys.path.append(os.path.join(os.getcwd(), 'src'))

from adk_tools import _search_juce_docs_impl

def main():
    query = "how to manage a juce::AudioProcessorValueTreeState with a juce::Slider"
    print(f"Querying: {query}")
    result = _search_juce_docs_impl(query)
    print("\n--- Result ---\n")
    print(result)

if __name__ == "__main__":
    main()
