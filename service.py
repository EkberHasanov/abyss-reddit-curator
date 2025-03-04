from google import genai
from google.genai import types

from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_content(text: str) -> str:
    response = client.models.generate_content(
        contents=text,
        model="gemini-2.0-flash-001",
    )

    return response.text if response.text else "No text generated"
