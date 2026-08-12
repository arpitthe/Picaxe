"""
Face Quality Validation Module.

Evaluates detected face crops against configurable quality criteria:
  1. Blur (Laplacian variance of face crop)
  2. Brightness (Mean grayscale intensity)
  3. Face Fraction (Face bounding box area / Total image area)
  4. Face Count (Enforced per workflow requirement)

All thresholds are configurable via app.core.config.settings.
"""

from dataclasses import dataclass
from typing import Optional, List
import cv2
import numpy as np

from app.core.config import settings
from app.exceptions.custom import ErrorCode

@dataclass
class QualityReport:
    valid: bool
    score: float                         # Composite score 0.0 - 1.0
    blur_score: float                    # Laplacian variance (higher = sharper)
    brightness: float                    # Mean intensity 0 - 255
    face_fraction: float                 # Face area / Total image area
    reason: Optional[ErrorCode] = None   # Enum ErrorCode when valid=False


def _laplacian_variance(gray_crop: np.ndarray) -> float:
    """Computes variance of the Laplacian operator as a blur metric."""
    if gray_crop.size == 0:
        return 0.0
    return float(cv2.Laplacian(gray_crop, cv2.CV_64F).var())


def _mean_brightness(gray_crop: np.ndarray) -> float:
    """Computes mean pixel intensity of a grayscale image crop."""
    if gray_crop.size == 0:
        return 0.0
    return float(np.mean(gray_crop))


def _face_fraction(img_h: int, img_w: int, bbox: List[int]) -> float:
    """Computes the fraction of total image area occupied by the face bounding box."""
    if img_h == 0 or img_w == 0:
        return 0.0
    x1, y1, x2, y2 = bbox
    face_w = max(0, x2 - x1)
    face_h = max(0, y2 - y1)
    face_area = face_w * face_h
    total_area = img_h * img_w
    return float(face_area / total_area)


def _composite_score(blur: float, brightness: float, fraction: float) -> float:
    """Computes a normalized composite quality score in [0.0, 1.0]."""
    blur_norm = min(blur / 300.0, 1.0)
    brightness_norm = max(0.0, 1.0 - abs(brightness - 128.0) / 128.0)
    fraction_norm = min(fraction / 0.20, 1.0)
    
    score = (0.5 * blur_norm) + (0.3 * brightness_norm) + (0.2 * fraction_norm)
    return round(float(np.clip(score, 0.0, 1.0)), 4)


def evaluate_quality(img_bgr: np.ndarray, bbox: List[int]) -> QualityReport:
    """
    Evaluates quality metrics for a detected face crop within img_bgr.
    """
    h, w = img_bgr.shape[:2]
    x1, y1, x2, y2 = [int(v) for v in bbox]
    
    # Clamp bounding box coordinates to image boundaries
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    crop = img_bgr[y1:y2, x1:x2]
    if crop.size == 0:
        return QualityReport(
            valid=False, score=0.0, blur_score=0.0, brightness=0.0, face_fraction=0.0,
            reason=ErrorCode.FACE_TOO_SMALL
        )

    gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    
    blur = _laplacian_variance(gray_crop)
    brightness = _mean_brightness(gray_crop)
    fraction = _face_fraction(h, w, [x1, y1, x2, y2])
    score = _composite_score(blur, brightness, fraction)

    # --- Quality Gates against Settings ---
    if fraction < settings.MIN_FACE_FRACTION:
        return QualityReport(
            valid=False, score=score, blur_score=blur, brightness=brightness, face_fraction=fraction,
            reason=ErrorCode.FACE_TOO_SMALL
        )

    if blur < settings.BLUR_THRESHOLD:
        return QualityReport(
            valid=False, score=score, blur_score=blur, brightness=brightness, face_fraction=fraction,
            reason=ErrorCode.IMAGE_TOO_BLURRY
        )

    if brightness < settings.MIN_BRIGHTNESS:
        return QualityReport(
            valid=False, score=score, blur_score=blur, brightness=brightness, face_fraction=fraction,
            reason=ErrorCode.IMAGE_TOO_DARK
        )

    if brightness > settings.MAX_BRIGHTNESS:
        return QualityReport(
            valid=False, score=score, blur_score=blur, brightness=brightness, face_fraction=fraction,
            reason=ErrorCode.IMAGE_TOO_BRIGHT
        )

    return QualityReport(
        valid=True, score=score, blur_score=blur, brightness=brightness, face_fraction=fraction,
        reason=None
    )
