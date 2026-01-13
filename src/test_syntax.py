import asyncio
from unittest.mock import MagicMock
from adk_agent import juce_expert

async def test_logic():
    print("--- Testing JUCE Expert Logic (Dry Run) ---")
    
    # 1. Mock the MCP Context Session (Faking the IDE)
    mock_session = MagicMock()
    
    # Define what the "IDE" returns when asked to sample
    async def mock_sample(*args, **kwargs):
        return type('obj', (object,), {'content': type('obj', (object,), {'text': "MOCK_IDE_RESPONSE: Use juce::Slider."})})
    
    # Apply the mock
    mock_session.sample = mock_sample

    # 2. Run the Agent
    print("Sending Query: 'test slider'...")
    try:
        result = await juce_expert.consult("test slider", mock_session)
        print(f"\nSUCCESS. Agent returned:\n{result}")
    except Exception as e:
        print(f"\nFAILED with error:\n{e}")

if __name__ == "__main__":
    asyncio.run(test_logic())