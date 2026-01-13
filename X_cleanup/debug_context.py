
import sys
import os
sys.path.append(os.path.abspath("src"))
from src.adk_tools import _search_juce_docs_impl

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

print("GATHERING CONTEXT...")
for q in queries:
    print(f"QUERY_START: {q}")
    try:
        ctx = _search_juce_docs_impl(q)
        # Limit context to save space, just need enough to answer
        print(ctx[:1000].replace('\n', ' ')) 
    except Exception as e:
        print(f"Error: {e}")
    print("QUERY_END")
