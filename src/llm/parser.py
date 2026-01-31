import requests
from src.config import LM_STUDIO_URL, MODEL_NAME

def parse_with_llm(content: str):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Extract structured data from text and return JSON."},
            {"role": "user", "content": content}
        ]
    }

    r = requests.post(LM_STUDIO_URL, json=payload)
    r.raise_for_status()
    return r.json()
