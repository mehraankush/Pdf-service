import fitz

MIN_TEXT_CHARS = 50
MIN_TEXT_RATIO = 0.3


def detect_pdf_type(pdf_path: str) -> str:
    """
    Detect PDF type: 'digital', 'scanned', or 'hybrid'.

    Args:
        pdf_path: Path to PDF file

    Returns:
        PDF type as string
    """
    doc = fitz.open(pdf_path)

    text_pages = 0
    image_pages = 0
    total_pages = len(doc)

    for page in doc:
        # Consider a page "text" if it has meaningful content.
        text = page.get_text().strip()
        if text and len(text) > MIN_TEXT_CHARS:
            text_pages += 1

        if page.get_images(full=True):
            image_pages += 1

    doc.close()

    text_ratio = text_pages / total_pages if total_pages > 0 else 0

    if text_pages == 0:
        return "scanned"
    if text_ratio < MIN_TEXT_RATIO and image_pages > 0:
        return "scanned"
    if image_pages > 0:
        return "hybrid"
    return "digital"
