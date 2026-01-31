from paddleocr import PaddleOCR
import numpy as np
import cv2

# Initialize PaddleOCR once (reuse across calls)
ocr = PaddleOCR(use_angle_cls=True, lang='en')

def ocr_pixmap(pixmap):
    """
    Extract text from a fitz.Pixmap using PaddleOCR.
    
    Args:
        pixmap: fitz.Pixmap object
        
    Returns:
        Extracted text as string
    """
    # Convert pixmap to numpy array
    img = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
        pixmap.height, pixmap.width, pixmap.n
    )
    
    # Convert to BGR format for OpenCV (PaddleOCR expects BGR)
    if pixmap.n == 4:  # RGBA
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif pixmap.n == 3:  # RGB
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif pixmap.n == 1:  # Grayscale
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    # Run OCR (angle classifier already enabled in PaddleOCR init)
    result = ocr.ocr(img)
    
    # Extract text from result
    # PaddleOCR returns: [[[bbox], (text, confidence)], ...]
    if not result or not result[0]:
        return ""
    
    text_lines = []
    for line in result[0]:
        if line:
            # line[1] is a tuple: (text, confidence)
            text = line[1][0]
            text_lines.append(text)
    
    return "\n".join(text_lines)
