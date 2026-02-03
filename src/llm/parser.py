import json
from pathlib import Path
from datetime import datetime
import requests
from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.llm.schema import SCHEMA_INSTRUCTIONS

def _parse_with_gemini(content: str):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")

    prompt = (
        "Extract structured data from the brochure text and return ONLY JSON.\n\n"
        + SCHEMA_INSTRUCTIONS.strip()
        + "\n\nBrochure text:\n"
        + content
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "response_mime_type": "application/json",
        },
    }

    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Unexpected Gemini response format: {data}") from e

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: return raw text if model didn't emit valid JSON
        return {"_raw": text}


def parse_with_llm(content: str):
    sample_path = Path("data/output/sample3_extracted.txt")
    if sample_path.exists():
        content = sample_path.read_text(encoding="utf-8")
    result = _parse_with_gemini(content)
    output_dir = Path("data/llm")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"gemini_response_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result
