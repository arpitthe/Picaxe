"""
Face Detection Module — Wraps InsightFace's SCRFD Detector (det_10g.onnx).

Handles face localization, 5-point landmark detection, alignment, and ordering.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Any
import numpy as np

from app.core.config import settings
from app.exceptions.custom import ModelInferenceException

logger = logging.getLogger(__name__)

_app_instance: Optional[Any] = None

@dataclass
class DetectedFace:
    bbox: List[int]                     # [x1, y1, x2, y2]
    confidence: float                  # Detection confidence score (0.0 - 1.0)
    kps: Optional[List] = field(default=None) # 5-point facial keypoints
    raw_face_obj: Optional[Any] = field(default=None, repr=False)
    embedding: Optional[np.ndarray] = field(default=None, repr=False)

def _get_insightface_app() -> Any:
    """
    Singleton initializer for InsightFace's FaceAnalysis pipeline.
    Loads models once at application startup.
    """
    global _app_instance
    if _app_instance is None:
        # --- ONNX Runtime CUDA/cuDNN DLL preload ---
        # Must happen before any ONNX session (including InsightFace) is created,
        # otherwise the CUDAExecutionProvider may silently fall back to CPU.
        try:
            import onnxruntime as _ort
            logger.info("Attempting ONNX Runtime CUDA/cuDNN DLL preload (onnxruntime.preload_dlls)...")
            _ort.preload_dlls(directory="")
            logger.info("ONNX Runtime CUDA/cuDNN DLL preload succeeded.")
        except Exception as _ort_exc:
            logger.warning(
                f"ONNX Runtime CUDA/cuDNN DLL preload failed — CUDA provider may be unavailable, "
                f"falling back to CPU. Reason: {_ort_exc}"
            )

        import insightface

        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if settings.INSIGHTFACE_CTX_ID >= 0 else ["CPUExecutionProvider"]
        logger.info(f"Initializing InsightFace model pack '{settings.INSIGHTFACE_MODEL}' with providers={providers}...")
        
        try:
            fa = insightface.app.FaceAnalysis(
                name=settings.INSIGHTFACE_MODEL,
                providers=providers
            )
            fa.prepare(ctx_id=settings.INSIGHTFACE_CTX_ID, det_size=(640, 640))
            _app_instance = fa
            logger.info("InsightFace FaceAnalysis pipeline initialized successfully.")
        except Exception as exc:
            logger.error(f"Failed to load InsightFace model pack: {exc}")
            raise ModelInferenceException(f"Failed to load InsightFace model: {str(exc)}") from exc
            
    return _app_instance

def is_model_loaded() -> bool:
    """Check if InsightFace model singleton is initialized."""
    return _app_instance is not None

def detect_faces(img_rgb: np.ndarray) -> List[DetectedFace]:
    """
    Detects all faces in an RGB image.

    InsightFace automatically detects 5 facial landmarks (kps) and performs
    similarity transformation face alignment (norm_crop to 112x112 px) internally
    before generating ArcFace embeddings.

    Returns:
        List[DetectedFace]: Sorted by detection confidence descending.
    """
    fa = _get_insightface_app()
    
    try:
        raw_faces = fa.get(img_rgb)
    except Exception as exc:
        raise ModelInferenceException(f"InsightFace detection execution failed: {str(exc)}") from exc

    results: List[DetectedFace] = []
    for face in raw_faces:
        bbox = [int(v) for v in face.bbox.tolist()]
        confidence = float(face.det_score)
        kps = face.kps.tolist() if hasattr(face, "kps") and face.kps is not None else None
        embedding = face.embedding if hasattr(face, "embedding") else None
        
        results.append(DetectedFace(
            bbox=bbox,
            confidence=confidence,
            kps=kps,
            raw_face_obj=face,
            embedding=embedding
        ))

    # Sort faces by detection confidence descending
    results.sort(key=lambda f: f.confidence, reverse=True)
    return results
