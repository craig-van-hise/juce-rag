from google.adk.models import Gemini
try:
    g = Gemini(model="gemini-3-pro", project_id="test-project", location="us-central1")
    print("SUCCESS: Gemini accepted project_id/location")
    print(g.__dict__)
except Exception as e:
    print(f"FAILED: {e}")
