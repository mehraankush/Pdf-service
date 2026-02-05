import cv2
import numpy as np


def _decode_qr_from_bgr(image_bgr):
    """Decode QR codes from a BGR image.

    Returns:
        List of decoded strings (may be empty).
    """
    detector = cv2.QRCodeDetector()

    try:
        # Prefer multi-QR decode when available.
        if hasattr(detector, "detectAndDecodeMulti"):
            ok, decoded_info, _, _ = detector.detectAndDecodeMulti(image_bgr)
            if ok and decoded_info:
                return [s for s in decoded_info if s]

        decoded, _, _ = detector.detectAndDecode(image_bgr)
        return [decoded] if decoded else []
    except cv2.error:
        # Some embedded images trigger OpenCV internals (kmeans assertion); skip them.
        return []


def decode_qr_from_pixmap(pixmap):
    """Decode QR codes from a fitz.Pixmap."""
    if pixmap.width < 24 or pixmap.height < 24:
        return []

    img = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
        pixmap.height, pixmap.width, pixmap.n
    )

    if pixmap.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif pixmap.n == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif pixmap.n == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    else:
        # Fallback for uncommon channel formats (e.g., CMYK); keep first 3 channels.
        img = img[:, :, :3]

    return _decode_qr_from_bgr(img)
