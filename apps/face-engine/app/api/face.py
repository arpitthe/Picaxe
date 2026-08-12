"""
Face Engine FastAPI Routes.

Routes are thin wrappers — all logic lives in FaceService.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.requests import (
    FaceRegisterRequest, EventPhotoSearchRequest,
    FaceQualityCheckRequest, FaceEmbedRequest, FaceSearchRequest
)
from app.schemas.responses import (
    FaceRegisterResponse, EventPhotoSearchResponse,
    FaceEmbedResponse, FaceSearchResponse, MatchItem
)
from app.services.face_service import register_student_face, search_event_photo
from app.preprocessing.image import preprocess
from app.detection.detector import detect_faces
from app.detection.quality import evaluate_quality
from app.embedding.model import embedding_to_list
from app.embedding.insightface import InsightFaceEmbedder
from app.exceptions.custom import FaceEngineException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/face", tags=["Face Engine"])
_embedder = InsightFaceEmbedder()


@router.post("/register", response_model=FaceRegisterResponse, status_code=200,
             summary="Register a student's face embedding into Qdrant")
def register_face(req: FaceRegisterRequest):
    """
    Student Registration Endpoint.

    - Requires exactly **1 face** in the photo.
    - Validates blur, brightness, and face size.
    - Extracts a 512-D ArcFace (w600k_r50) embedding.
    - Upserts the vector into Qdrant (idempotent per student_id).
    - Does **not** return the raw embedding vector.
    """
    result = register_student_face(
        image_base64=req.image_base64,
        student_id=req.student_id
    )
    return result


@router.post("/search-event", response_model=EventPhotoSearchResponse, status_code=200,
             summary="Detect all faces in an event photo and search for student matches")
def search_event(req: EventPhotoSearchRequest):
    """
    Event Photo Matching Endpoint.

    - Detects **all faces** present in the image.
    - Generates a 512-D ArcFace embedding per face.
    - Performs ANN cosine similarity search in Qdrant.
    - Returns ranked candidate matches with confidence tiers.
    """
    result = search_event_photo(
        image_base64=req.image_base64,
        limit_per_face=req.limit_per_face,
        score_threshold=req.score_threshold
    )
    return result


@router.post("/quality-check", status_code=200,
             summary="Validate face quality without embedding generation")
def quality_check(req: FaceQualityCheckRequest):
    """
    Standalone quality validation. Useful for client-side pre-checks.
    Returns blur, brightness, face count, and fraction metrics.
    """
    bgr, rgb = preprocess(req.image_base64)
    detected = detect_faces(rgb)

    if len(detected) == 0:
        return {"valid": False, "face_count": 0, "reason": "NO_FACE_DETECTED"}

    target_face = detected[0]
    quality = evaluate_quality(bgr, target_face.bbox)

    return {
        "valid": quality.valid and len(detected) == 1,
        "face_count": len(detected),
        "score": quality.score,
        "blur_score": round(quality.blur_score, 2),
        "brightness": round(quality.brightness, 2),
        "face_fraction": round(quality.face_fraction, 4),
        "reason": quality.reason.value if quality.reason else (
            "TOO_MANY_FACES" if len(detected) > 1 else None
        )
    }


@router.post("/embed", response_model=FaceEmbedResponse, status_code=200,
             summary="[Debug] Extract raw 512-D embedding from first detected face")
def face_embed(req: FaceEmbedRequest):
    """
    Debug embedding extraction endpoint.
    Returns the 512-D L2-normalized ArcFace vector of the first detected face.
    """
    bgr, rgb = preprocess(req.image_base64)
    detected = detect_faces(rgb)

    if not detected or detected[0].raw_face_obj is None:
        return FaceEmbedResponse(embedding=[0.0] * 512)

    try:
        vec = _embedder.embed_face(detected[0].raw_face_obj)
        return FaceEmbedResponse(embedding=embedding_to_list(vec))
    except Exception:
        return FaceEmbedResponse(embedding=[0.0] * 512)


@router.post("/search", response_model=FaceSearchResponse, status_code=200,
             summary="[Legacy] Flat face search for backward compatibility")
def face_search_legacy(req: FaceSearchRequest):
    """Legacy endpoint maintaining backward compatibility with old API Gateway calls."""
    res = search_event_photo(
        image_base64=req.image_base64,
        limit_per_face=req.limit,
        score_threshold=req.score_threshold
    )
    matches = []
    for face in res.get("faces", []):
        for m in face.get("matches", []):
            matches.append(MatchItem(student_id=m["student_id"], score=m["similarity"]))
    return FaceSearchResponse(matches=matches)
