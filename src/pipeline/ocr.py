import cv2
import numpy as np
import os
from paddleocr import PaddleOCR

_OCR_INSTANCES = {}
_USE_GPU = os.getenv("OCR_USE_GPU", "false").lower() == "true"


def _get_ocr(use_angle_cls: bool):
    key = "angle" if use_angle_cls else "no_angle"
    if key not in _OCR_INSTANCES:
        _OCR_INSTANCES[key] = PaddleOCR(
            use_angle_cls=use_angle_cls,
            lang="en",
            use_gpu=_USE_GPU,
            show_log=False,
        )
    return _OCR_INSTANCES[key]


def _to_bgr(pixmap):
    img = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
        pixmap.height, pixmap.width, pixmap.n
    )
    if pixmap.n == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    if pixmap.n == 3:
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    if pixmap.n == 1:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    # Handle uncommon channel formats (e.g., CMYK) by taking first 3 channels.
    if img.ndim == 3 and img.shape[2] >= 3:
        return img[:, :, :3]
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def _resize_for_ocr(img, source_type: str, embedded_max_dimension: int = 3000):
    h, w = img.shape[:2]
    if source_type == "rendered":
        return img
    if max(h, w) <= embedded_max_dimension:
        return img
    scale = embedded_max_dimension / max(h, w)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def ocr_pixmap(pixmap, source_type: str = "embedded", use_angle_cls: bool = True):
    """Extract text from a fitz.Pixmap with safer speed optimizations."""
    if pixmap.width < 20 or pixmap.height < 20:
        return ""

    img = _to_bgr(pixmap)
    img = _resize_for_ocr(img, source_type=source_type)
    ocr = _get_ocr(use_angle_cls=use_angle_cls)
    result = ocr.ocr(img, cls=use_angle_cls)
    if not result or not result[0]:
        return ""
    text_lines = [line[1][0] for line in result[0] if line and line[1]]
    return "\n".join(text_lines)
