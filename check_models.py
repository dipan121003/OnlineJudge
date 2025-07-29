# check_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the API key from your .env file
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env file.")
else:
    genai.configure(api_key=api_key)
    print("Available models that support 'generateContent':")

    # List all available models and check their supported methods
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)