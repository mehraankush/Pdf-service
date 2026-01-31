import fitz

from src.pipeline.detector import detect_pdf_type
from src.pipeline.extractor import extract_text, extract_images
from src.pipeline.ocr import ocr_pixmap
from src.pipeline.cleaner import clean_text
from src.pipeline.chunker import chunk_text

MIN_TEXT_CHARS = 50
RENDER_DPI = 300


def _collect_text_pages(pdf_path: str):
    """Extract and clean text for all pages, including empty pages."""
    text_pages = extract_text(pdf_path, include_empty=True)
    full_text_parts = []
    page_text_len = {}

    for page in text_pages:
        cleaned = clean_text(page["content"])
        page_text_len[page["page"]] = len(cleaned.strip())
        full_text_parts.append(cleaned)

    full_text = "\n\n".join(full_text_parts) + ("\n\n" if full_text_parts else "")
    return text_pages, page_text_len, full_text


def _ocr_rendered_pages(pdf_path: str, pdf_type: str, page_text_len: dict):
    """OCR full rendered pages for scanned or low-text pages."""
    ocr_results = []
    pages_ocr_full = set()

    if pdf_type not in ("scanned", "hybrid"):
        return ocr_results, pages_ocr_full

    print("Running OCR on rendered pages...")
    doc = fitz.open(pdf_path)
    for page_index, page in enumerate(doc):
        page_number = page_index + 1
        text_len = page_text_len.get(page_number, 0)
        should_ocr = pdf_type == "scanned" or text_len < MIN_TEXT_CHARS

        if not should_ocr:
            continue

        try:
            zoom = RENDER_DPI / 72  # render at target DPI
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            ocr_text = ocr_pixmap(pix)
            if ocr_text and len(ocr_text.strip()) > 0:
                ocr_results.append(ocr_text)
                pages_ocr_full.add(page_number)
                print(f"OCR completed for page {page_number}: {len(ocr_text)} chars")
        except Exception as e:
            print(f"OCR failed for page {page_number}: {e}")

    doc.close()
    return ocr_results, pages_ocr_full


def _ocr_embedded_images(pdf_path: str, pdf_type: str, pages_ocr_full: set):
    """OCR embedded images to capture text in figures/screenshots."""
    ocr_results = []

    if pdf_type not in ("digital", "hybrid"):
        return ocr_results

    print("Running OCR on embedded images...")
    images = extract_images(pdf_path)
    print(f"Found {len(images)} images to process")

    for i, img in enumerate(images):
        if img["page"] in pages_ocr_full:
            continue
        try:
            ocr_text = ocr_pixmap(img["pixmap"])
            if ocr_text and len(ocr_text.strip()) > 0:
                ocr_results.append(ocr_text)
                print(f"OCR completed for image {i+1}/{len(images)}: {len(ocr_text)} chars")
        except Exception as e:
            print(f"OCR failed for image {i+1}: {e}")

    return ocr_results


def _append_ocr_text(full_text: str, ocr_results: list[str]):
    """Append OCR text to the full text with a separator."""
    if not ocr_results:
        return full_text

    full_text += "\n\n=== OCR EXTRACTED TEXT ===\n\n"
    full_text += "\n\n".join(ocr_results)
    print(f"Total OCR text added: {sum(len(t) for t in ocr_results)} chars")
    return full_text

def process_pdf(pdf_path: str):
    """
    Process PDF and extract all text content.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of text chunks
    """
    # Detect PDF type to choose the OCR strategy.
    pdf_type = detect_pdf_type(pdf_path)
    print(f"PDF type: {pdf_type}")

    # Extract text layer first; OCR fills gaps.
    text_pages, page_text_len, full_text = _collect_text_pages(pdf_path)
    print(f"Extracted text from {len(text_pages)} pages")

    # OCR full pages when needed, then OCR embedded images for digital/hybrid PDFs.
    rendered_ocr, pages_ocr_full = _ocr_rendered_pages(pdf_path, pdf_type, page_text_len)
    image_ocr = _ocr_embedded_images(pdf_path, pdf_type, pages_ocr_full)
    full_text = _append_ocr_text(full_text, rendered_ocr + image_ocr)

    print(f"Total text length: {len(full_text)} characters")
    
    # Chunk the final text for downstream processing.
    chunks = chunk_text(full_text)
    print(f"Created {len(chunks)} chunks")
    
    return chunks
