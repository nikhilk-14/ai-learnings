import openai
import requests
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env file
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:1234/v1/chat/completions")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "lm-studio")
MODEL = os.getenv("LLM_MODEL", "local-model")
TIMEOUT = float(os.getenv("LLM_TIMEOUT", "300"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# Initialize OpenAI client with configuration from .env
client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
    timeout=TIMEOUT
)

def ask_llm(prompt):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE
    }
    try:
        response = requests.post(LLM_ENDPOINT, json=payload, timeout=TIMEOUT)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return f"⚠️ LLM request timed out after {TIMEOUT} seconds. The model might be processing a complex query."
    except Exception as e:
        return f"⚠️ Error talking to LLM: {e}"

def test_llm_connection(prompt="Say hello"):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Connection test failed: {e}"
