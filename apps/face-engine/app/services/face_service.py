"""
Face Engine Business Logic Service.

Orchestrates the full registration and event-photo search pipelines.
Routes call this service layer only — no model inference in route handlers.

Architecture:
  API (face.py)
    → FaceService
        → preprocessing.image
        → detection.detector
        → detection.quality
        → embedding.insightface
        → matching.matcher
        → qdrant.client
"""

import logging
import time
from typing import Dict, Any, List, Optional

from app.preprocessing.image import preprocess
from app.detection.detector import detect_faces
from app.detection.quality import evaluate_quality, QualityReport
from app.embedding.insightface import InsightFaceEmbedder
from app.embedding.model import embedding_to_list
from app.matching.matcher import rank_and_tier_matches
from app.qdrant.client import get_qdrant_repository
from app.core.config import settings
from app.exceptions.custom import (
    ErrorCode, FaceEngineException, QdrantRepositoryException, ModelInferenceException
)

logger = logging.getLogger(__name__)

_embedder = InsightFaceEmbedder()

def _quality_to_dict(q: QualityReport) -> Dict[str, Any]:
    return {
        "valid": q.valid,
        "score": q.score,
        "blur_score": round(q.blur_score, 2),
        "brightness": round(q.brightness, 2),
        "face_fraction": round(q.face_fraction, 4),
        "reason": q.reason.value if q.reason else None
    }

def register_student_face(image_base64: str, student_id: str) -> Dict[str, Any]:
    """
    Workflow A — Student Registration Pipeline:
      1. Decode and preprocess image
      2. Detect faces (require exactly 1)
      3. Run quality validation
      4. Extract 512-D ArcFace embedding
      5. Upsert vector into Qdrant (idempotent)
    """
    t_start = time.monotonic()
    model_version = f"{settings.INSIGHTFACE_MODEL}-w600k_r50"
    base_response = {
        "success": False,
        "student_id": student_id,
        "qdrant_point_id": None,
        "model_version": model_version,
        "embedding_dimension": settings.EMBEDDING_DIMENSION,
    }

    # --- 1. Decode & preprocess ---
    t0 = time.monotonic()
    bgr, rgb = preprocess(image_base64)   # Raises on invalid/corrupt input
    logger.info(f"[register] Preprocessing took {(time.monotonic()-t0)*1000:.1f}ms")

    # --- 2. Detect faces ---
    t0 = time.monotonic()
    detected = detect_faces(rgb)
    logger.info(f"[register] Detection took {(time.monotonic()-t0)*1000:.1f}ms — {len(detected)} face(s) found")

    if len(detected) == 0:
        q = {"valid": False, "score": 0.0, "blur_score": 0.0, "brightness": 0.0, "face_fraction": 0.0, "reason": ErrorCode.NO_FACE_DETECTED.value}
        return {**base_response, "quality": q, "error_code": ErrorCode.NO_FACE_DETECTED.value, "detail": "No face detected in registration photo."}

    if len(detected) > 1:
        q = {"valid": False, "score": 0.0, "blur_score": 0.0, "brightness": 0.0, "face_fraction": 0.0, "reason": ErrorCode.TOO_MANY_FACES.value}
        return {**base_response, "quality": q, "error_code": ErrorCode.TOO_MANY_FACES.value, "detail": f"Registration photo must contain exactly 1 face, found {len(detected)}."}

    face = detected[0]

    # --- 3. Quality validation ---
    t0 = time.monotonic()
    quality = evaluate_quality(bgr, face.bbox)
    logger.info(f"[register] Quality evaluation took {(time.monotonic()-t0)*1000:.1f}ms — valid={quality.valid}")

    if not quality.valid:
        return {**base_response, "quality": _quality_to_dict(quality), "error_code": quality.reason.value if quality.reason else "QUALITY_FAILED", "detail": f"Face quality check failed: {quality.reason.value if quality.reason else 'unknown'}"}

    # --- 4. Generate embedding ---
    t0 = time.monotonic()
    try:
        embedding_vec = _embedder.embed_face(face.raw_face_obj)
    except ModelInferenceException as exc:
        q = {**_quality_to_dict(quality), "valid": False, "reason": ErrorCode.EMBEDDING_GENERATION_FAILED.value}
        return {**base_response, "quality": q, "error_code": ErrorCode.EMBEDDING_GENERATION_FAILED.value, "detail": str(exc)}
    logger.info(f"[register] Embedding took {(time.monotonic()-t0)*1000:.1f}ms — dim={len(embedding_vec)}")

    embedding_list = embedding_to_list(embedding_vec)

    # --- 5. Qdrant upsert ---
    t0 = time.monotonic()
    try:
        repo = get_qdrant_repository()
        point_id = repo.upsert_student_vector(
            student_id=student_id,
            embedding=embedding_list,
            metadata={"source": "registration"}
        )
        logger.info(f"[register] Qdrant upsert took {(time.monotonic()-t0)*1000:.1f}ms — point_id={point_id}")
    except QdrantRepositoryException as exc:
        logger.error(f"Qdrant upsert failed for student {student_id}: {exc}")
        return {**base_response, "quality": _quality_to_dict(quality), "error_code": ErrorCode.QDRANT_UNAVAILABLE.value, "detail": "Vector storage unavailable. Registration stored locally but not persisted to vector DB."}

    total_ms = (time.monotonic() - t_start) * 1000
    logger.info(f"[register] Total time: {total_ms:.1f}ms for student {student_id}")

    return {
        "success": True,
        "student_id": student_id,
        "qdrant_point_id": point_id,
        "model_version": model_version,
        "embedding_dimension": settings.EMBEDDING_DIMENSION,
        "quality": _quality_to_dict(quality),
        "error_code": None,
        "detail": None
    }


def search_event_photo(image_base64: str, limit_per_face: int = 5, score_threshold: Optional[float] = None) -> Dict[str, Any]:
    """
    Workflow B — Event Photo Search Pipeline:
      1. Decode and preprocess
      2. Detect ALL faces
      3. Per face: quality check + embedding + Qdrant ANN search
      4. Rank and tier matches
    """
    t_start = time.monotonic()
    threshold = score_threshold if score_threshold is not None else settings.SIMILARITY_THRESHOLD

    bgr, rgb = preprocess(image_base64)

    t0 = time.monotonic()
    detected = detect_faces(rgb)
    logger.info(f"[search-event] Detection took {(time.monotonic()-t0)*1000:.1f}ms — {len(detected)} face(s)")

    face_results = []
    for idx, face in enumerate(detected):
        quality = evaluate_quality(bgr, face.bbox)
        quality_dict = _quality_to_dict(quality)

        matches = []
        if face.raw_face_obj is not None:
            try:
                embedding_vec = _embedder.embed_face(face.raw_face_obj)
                embedding_list = embedding_to_list(embedding_vec)

                t0 = time.monotonic()
                try:
                    repo = get_qdrant_repository()
                    raw_matches = repo.search_similar_vectors(
                        query_embedding=embedding_list,
                        limit=limit_per_face,
                        score_threshold=threshold
                    )
                    logger.info(f"[search-event] Qdrant search face#{idx} took {(time.monotonic()-t0)*1000:.1f}ms — {len(raw_matches)} candidate(s)")

                    tiered = rank_and_tier_matches(raw_matches, threshold=threshold)
                    for m in tiered:
                        if m.get("student_id"):
                            matches.append({
                                "student_id": m["student_id"],
                                "similarity": m["score"],
                                "confidence_tier": m["confidence_tier"],
                                "qdrant_point_id": m.get("point_id")
                            })
                except QdrantRepositoryException as exc:
                    logger.warning(f"Qdrant search failed for face#{idx}: {exc}")

            except ModelInferenceException as exc:
                logger.warning(f"Embedding failed for face#{idx}: {exc}")

        face_results.append({
            "face_index": idx,
            "bbox": face.bbox,
            "detection_confidence": round(face.confidence, 4),
            "quality": quality_dict,
            "matches": matches
        })

    total_ms = (time.monotonic() - t_start) * 1000
    logger.info(f"[search-event] Total time: {total_ms:.1f}ms — {len(detected)} face(s) processed")

    return {
        "total_faces_detected": len(detected),
        "faces": face_results
    }
