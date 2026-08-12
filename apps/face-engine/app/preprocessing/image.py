"""
Robust Image Preprocessing Module.

Handles Base64 decoding, format validation, corrupted image checks,
proportional resizing, and BGR->RGB color space conversion.
"""

import base64
import logging
from typing import Tuple
import cv2
import numpy as np

from app.core.config import settings
from app.exceptions.custom import InvalidImageException, CorruptedImageException, ErrorCode

logger = logging.getLogger(__name__)

def decode_image(image_base64: str) -> np.ndarray:
    """
    Decodes a base64 string or Data URL into an OpenCV BGR numpy array.

    Raises InvalidImageException or CorruptedImageException on invalid input.
    """
    if not image_base64 or not isinstance(image_base64, str):
        raise InvalidImageException("Image payload is empty or not a string.")

    # Strip data-URL prefix if present
    payload = image_base64
    if "," in image_base64:
        header, payload = image_base64.split(",", 1)
        if "base64" not in header.lower():
            raise InvalidImageException("Invalid Data URL header (must specify base64 encoding).")

    # Validate Base64 payload length (rough check against max allowed size)
    estimated_size = (len(payload) * 3) // 4
    if estimated_size > settings.MAX_IMAGE_SIZE_BYTES:
        raise InvalidImageException(
            f"Image payload size ({estimated_size / (1024*1024):.2f} MB) exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE_BYTES / (1024*1024):.2f} MB."
        )

    try:
        raw_bytes = base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise InvalidImageException(f"Failed to decode base64 payload: {str(exc)}") from exc

    if not raw_bytes:
        raise CorruptedImageException("Decoded image bytes are empty.")

    img = cv2.imdecode(np.frombuffer(raw_bytes, np.uint8), cv2.IMREAD_COLOR)

    if img is None or img.size == 0:
        raise CorruptedImageException("OpenCV failed to decode image bytes. Unsupported format or corrupted file.")

    return img


def resize_if_needed(img: np.ndarray, max_dim: int = settings.MAX_IMAGE_DIMENSION) -> np.ndarray:
    """
    Proportionally resizes img so its longest edge does not exceed max_dim.
    Preserves aspect ratio and avoids unnecessary array allocations if within limit.
    """
    h, w = img.shape[:2]
    if h == 0 or w == 0:
        raise CorruptedImageException("Image has zero width or height.")

    longest = max(h, w)
    if longest <= max_dim:
        return img

    scale = max_dim / float(longest)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def to_rgb(img_bgr: np.ndarray) -> np.ndarray:
    """Converts an OpenCV BGR image array to RGB format."""
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


def preprocess(image_base64: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Full deterministic preprocessing pipeline.

    Returns:
        (img_bgr, img_rgb)
    """
    bgr = decode_image(image_base64)
    bgr = resize_if_needed(bgr)
    rgb = to_rgb(bgr)
    return bgr, rgb
