import fitz

MIN_IMAGE_SIZE_PX = 50

def extract_text(pdf_path: str, include_empty: bool = False):
    """Extract text from all pages of PDF.

    Args:
        pdf_path: Path to PDF file
        include_empty: Include pages with no text content
    """
    doc = fitz.open(pdf_path)
    pages = []

    for i, page in enumerate(doc):
        text = page.get_text("text")
        if include_empty or text.strip():
            pages.append({
                "page": i + 1,
                "content": text
            })
    
    doc.close()
    return pages


def extract_images(pdf_path: str):
    """Extract images from all pages of PDF."""
    doc = fitz.open(pdf_path)
    images = []

    for page_index, page in enumerate(doc):
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            
            try:
                # Extract the image
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Create pixmap from bytes
                pix = fitz.Pixmap(image_bytes)
                
                # Convert CMYK to RGB if needed.
                if pix.colorspace and pix.colorspace.name not in ("DeviceRGB", "DeviceGray"):
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                # Skip very small images (likely icons or decorations).
                if pix.width > MIN_IMAGE_SIZE_PX and pix.height > MIN_IMAGE_SIZE_PX:
                    images.append({
                        "page": page_index + 1,
                        "pixmap": pix
                    })
            except Exception as e:
                print(f"Warning: Could not extract image {img_index} from page {page_index + 1}: {e}")
                continue
    
    doc.close()
    return images
