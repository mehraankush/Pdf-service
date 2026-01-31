# Pdf-service

PDF text extraction pipeline with OCR fallback for scanned and hybrid documents.

## What it does
- Detects PDF type (digital / scanned / hybrid)
- Extracts text from the PDF text layer
- Runs OCR on rendered pages for scanned/low-text pages
- Runs OCR on embedded images for digital/hybrid PDFs
- Outputs chunked text for downstream LLM processing

## Project structure
- `src/main.py`: Orchestrates detection, extraction, OCR, and chunking
- `src/pipeline/`: Detector, extractor, OCR, cleaner, chunker
- `scripts/run.py`: Example runner
- `data/input/`: Sample input PDFs
- `data/output/`: Extracted output (generated)

## Setup
Create and activate a virtual environment, then install deps (project uses PyMuPDF + PaddleOCR):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pymupdf paddleocr opencv-python numpy
```

## Run
```bash
PYTHONPATH=. python3 scripts/run.py
```

The full extracted text is saved to:
- `data/output/sample2.txt`

## Notes
- OCR quality depends on source PDF resolution and image quality.
- Rendered-page OCR uses 300 DPI by default; adjust in `src/main.py` if needed.
- Embedded image OCR skips very small images by default; adjust in `src/pipeline/extractor.py`.
