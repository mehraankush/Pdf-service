import json
import re
from pathlib import Path
from datetime import datetime
import requests
from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.llm.schema import SCHEMA_INSTRUCTIONS

PRIZE_SECTION_START = (
    "PRIZE",
    "PRIZES",
    "PRIZE STRUCTURE",
    "PRIZE DISTRIBUTION",
)
PRIZE_SECTION_STOP = (
    "REGISTRATION",
    "ACCOUNT",
    "CONTACT",
    "SCHEDULE",
    "VENUE",
    "INVITATION",
    "ORGANIZER",
    "ORGANISER",
    "IMPORTANT",
    "ELIGIBILITY",
    "RULES",
    "FORMAT",
)


def _append_normalized_table_lines(content: str) -> str:
    lines = [ln.rstrip() for ln in content.splitlines()]
    normalized = []
    for line in lines:
        if not line.strip():
            continue
        # Split on pipes or 2+ spaces to recover column-like text
        parts = [p.strip() for p in re.split(r"\s{2,}|\s\|\s|[|]", line) if p.strip()]
        if len(parts) >= 2:
            normalized.append(" | ".join(parts))

    if not normalized:
        return content

    return content + "\n\n=== NORMALIZED LINES ===\n" + "\n".join(normalized) + "\n"


def _normalize_prize_text(content: str) -> str:
    lines = [ln.strip() for ln in content.splitlines()]
    capture = False
    section_lines = []

    for line in lines:
        if not line:
            if capture and section_lines:
                section_lines.append("")
            continue
        upper = line.upper()
        if any(k in upper for k in PRIZE_SECTION_START):
            capture = True
            section_lines.append(line)
            continue
        if capture and any(k in upper for k in PRIZE_SECTION_STOP):
            capture = False
            section_lines.append("")
            continue
        if capture:
            section_lines.append(line)

    if not section_lines:
        return content

    labels = []
    values = []
    pairs = []

    rank_re = re.compile(r"\b(\d{1,2}(?:ST|ND|RD|TH)|\d{1,2}\s*-\s*\d{1,2})\b", re.I)
    amount_re = re.compile(r"(?:₹|RS\.?|INR|\$)\s*[\d,]+(?:\.\d+)?", re.I)
    trophy_re = re.compile(r"\b(TROPHY|CERTIFICATE|MEDAL|CASH)\b", re.I)

    def extract_labels_and_values(line: str):
        found_labels = []
        found_values = []

        for m in rank_re.finditer(line):
            found_labels.append(m.group(0))

        for m in amount_re.finditer(line):
            found_values.append(m.group(0))

        for m in trophy_re.finditer(line):
            found_values.append(m.group(0).title())

        # Category labels (Best/Youngest/Veteran/etc.)
        cat_tokens = []
        for token in re.split(r"\s{2,}|\s\|\s|[|,:]", line):
            tok = token.strip()
            if not tok:
                continue
            if rank_re.search(tok) or amount_re.search(tok) or trophy_re.search(tok):
                continue
            if any(k in tok.upper() for k in ("BEST", "FEMALE", "WOMEN", "GIRLS", "BOYS", "VETERAN", "YOUNG", "OLDEST", "UNRATED", "U9", "U10", "U11", "U12", "U13", "U14", "U15", "U16", "U17", "U18", "U19", "U20", "+")):
                cat_tokens.append(tok)
        found_labels.extend(cat_tokens)

        return found_labels, found_values

    pending_labels = []
    for line in section_lines:
        if not line:
            continue
        ln_labels, ln_values = extract_labels_and_values(line)
        if ln_labels:
            pending_labels.extend(ln_labels)
        if ln_values:
            if pending_labels:
                while pending_labels and ln_values:
                    pairs.append((pending_labels.pop(0), ln_values.pop(0)))
            values.extend(ln_values)

    # Pair any remaining labels with any remaining values (best-effort)
    while pending_labels and values:
        pairs.append((pending_labels.pop(0), values.pop(0)))

    if not pairs:
        return content

    normalized_lines = ["", "=== NORMALIZED PRIZES ==="]
    for label, value in pairs:
        normalized_lines.append(f"- {label}: {value}")

    return content + "\n" + "\n".join(normalized_lines) + "\n"

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


def parse_with_llm(content: str, output_path: str | Path | None = None):
    content = _normalize_prize_text(content)
    content = _append_normalized_table_lines(content)
    result = _parse_with_gemini(content)
    if output_path is None:
        output_dir = Path("data/llm")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"gemini_response_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result
