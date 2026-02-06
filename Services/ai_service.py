import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(prompt):
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        if response.text:
            return response.text.strip()
        else:
            return "Model couldn't generate a response."
    except Exception as e:
        error_str = str(e)
        print(f"AI Error: {e}")
        
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            return "⚠️ API quota exceeded. Please try again later."
        else:
            return "Sorry, AI service is currently unavailable."
