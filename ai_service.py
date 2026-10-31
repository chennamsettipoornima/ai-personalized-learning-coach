
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def generate_json(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    if not api_key:
        raise ValueError("Gemini API key not found. Check your .env file.")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as error:
        raise ValueError("Gemini returned invalid JSON.") from error
