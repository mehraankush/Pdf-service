import argparse
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests

from src.main import process_pdf
from src.llm.parser import parse_with_llm


DEFAULT_BASE_URL = "http://localhost:3000"
DEFAULT_CUTOFF = datetime(2026, 1, 1)


def _log(msg: str):
    print(f"[events] {msg}")


def _parse_date(value):
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip()
    fmts = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d %b %Y",
        "%d %B %Y",
    )
    for fmt in fmts:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def _has_brochure(event):
    brochure = event.get("brochure")
    return isinstance(brochure, str) and brochure.strip() != ""


def _event_key(event):
    for k in ("event_id", "eventId", "id", "_id"):
        if event.get(k):
            return str(event[k])
    for k in ("name", "eventName", "title"):
        if event.get(k):
            return _slugify(str(event[k]))
    return f"event_{int(datetime.utcnow().timestamp())}"


def _slugify(text: str):
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", text).strip("_").lower() or "event"


def fetch_all_events(base_url: str):
    _log("Fetching all events with full data...")
    url = f"{base_url.rstrip('/')}/api/events/all"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("success") is False:
        raise RuntimeError(f"API returned error: {payload.get('error', 'Unknown error')}")
    events = payload.get("data", [])
    if not isinstance(events, list):
        raise RuntimeError("Unexpected API payload: data is not a list")
    return events


def fetch_single_event(base_url: str, event_id: str):
    _log(f"Fetching single event {event_id}...")
    url = f"{base_url.rstrip('/')}/api/event/{event_id}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("success") is False:
        raise RuntimeError(f"API returned error: {payload.get('error', 'Unknown error')}")
    event = payload.get("data")
    if not isinstance(event, dict):
        raise RuntimeError("Unexpected API payload: data is not an object")
    return event


def filter_events(events):
    _log("Filtering events with brochure + startDate >= 2026-01-01 + no Analysis...")
    filtered = []
    for event in events:
        if not _has_brochure(event):
            continue
        start_date = _parse_date(event.get("startDate"))
        if not start_date or start_date < DEFAULT_CUTOFF:
            continue
        if event.get("Analysis", None) is not None:
            continue
        filtered.append(event)
    _log(f"Selected {len(filtered)} / {len(events)} events")
    return filtered


def _download_brochure(url: str, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, timeout=120, stream=True) as resp:
        resp.raise_for_status()
        with target.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)


def _write_extracted(chunks: list[str], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, start=1):
            f.write(f"\n--- Chunk {i} ---\n\n")
            f.write(chunk)


def process_event(event, input_dir: Path, extracted_dir: Path, llm_dir: Path, base_url: str):
    key = _event_key(event)
    event_id = event.get("event_id") or event.get("eventId") or event.get("id") or event.get("_id") or key
    brochure_url = event["brochure"].strip()
    brochure_ext = Path(urlparse(brochure_url).path).suffix or ".pdf"
    pdf_path = input_dir / f"{key}{brochure_ext}"
    extracted_path = extracted_dir / f"{key}_extracted.txt"
    llm_output_path = llm_dir / key / "analysis.json"

    _log(f"Processing event {key}")
    _download_brochure(brochure_url, pdf_path)
    chunks = process_pdf(str(pdf_path))
    _write_extracted(chunks, extracted_path)
    content = "\n\n".join(chunks)
    analysis = parse_with_llm(content, output_path=llm_output_path)
    response = requests.post(
        f"{base_url.rstrip('/')}/api/analysis",
        json={"eventId": event_id, "Analysis": analysis},
        timeout=60,
    )
    response.raise_for_status()
    _log(f"Saved LLM output to {llm_output_path}")


def main():
    parser = argparse.ArgumentParser(description="Fetch events and process brochure PDFs")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL")
    parser.add_argument("--event-id", help="Process a single event by ID")
    args = parser.parse_args()

    input_dir = Path("data/input/events")
    extracted_dir = Path("data/output/events")
    llm_dir = Path("data/llm")

    if args.event_id:
        selected = [fetch_single_event(args.base_url, args.event_id)]
    else:
        events = fetch_all_events(args.base_url)
        if not events:
            _log("No events returned by API")
            return

        selected = filter_events(events)
        if not selected:
            _log("No events matched filters")
            return

    failures = 0
    for event in selected:
        try:
            process_event(event, input_dir, extracted_dir, llm_dir, args.base_url)
        except Exception as exc:
            failures += 1
            _log(f"Failed event {_event_key(event)}: {exc}")

    _log(f"Done. processed={len(selected) - failures} failed={failures}")


if __name__ == "__main__":
    main()
