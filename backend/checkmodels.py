# backend/check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Checking available models for your API key...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")