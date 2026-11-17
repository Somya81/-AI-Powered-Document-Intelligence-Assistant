
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Locate .env in the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_answer(question, context):

    # Read environment variables when the function is called
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/free")

    if not api_key:
        return "API key missing. Please check the .env file."

    prompt = f"""
You are an engineering document assistant.

Answer the user's question using ONLY the document context below.

Rules:
1. Give a direct and clear answer.
2. Use simple language.
3. Do not add information outside the document.
4. If the answer is not available, say so.
5. Use bullet points when useful.

Document Context:
{context}

User Question:
{question}

Answer:
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 700
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=90
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except requests.RequestException as error:
        return f"OpenRouter API error: {error}"

    except (KeyError, IndexError, ValueError):
        return "Could not read the response from the AI model."
