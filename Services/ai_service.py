import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GEMINI_API_KEY"))
    return _client

def ask_gemini(prompt):
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_str = str(e)
        print(f"AI Error: {e}")
        if "429" in error_str:
            return "⚠️ API quota exceeded. Please try again later."
        else:
            return "Sorry, AI service is currently unavailable."
