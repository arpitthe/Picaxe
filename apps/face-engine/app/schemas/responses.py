from pydantic import BaseModel
from typing import List, Optional

class QualityDetails(BaseModel):
    valid: bool
    score: float
    blur_score: float
    brightness: float
    face_fraction: float
    reason: Optional[str] = None

class FaceRegisterResponse(BaseModel):
    success: bool
    student_id: str
    qdrant_point_id: Optional[str] = None
    model_version: str
    embedding_dimension: int
    quality: QualityDetails
    error_code: Optional[str] = None
    detail: Optional[str] = None

class StudentMatch(BaseModel):
    student_id: str
    similarity: float
    confidence_tier: str
    qdrant_point_id: Optional[str] = None

class DetectedFaceResult(BaseModel):
    face_index: int
    bbox: List[int]
    detection_confidence: float
    quality: QualityDetails
    matches: List[StudentMatch]

class EventPhotoSearchResponse(BaseModel):
    total_faces_detected: int
    faces: List[DetectedFaceResult]

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model_loaded: bool
    qdrant_connected: bool
    insightface_model: str
    detector: str
    recognition_model: str
    embedding_dimension: int
    distance_metric: str

# Legacy response schemas kept for backward compat
class FaceEmbedResponse(BaseModel):
    embedding: List[float]

class MatchItem(BaseModel):
    student_id: str
    score: float

class FaceSearchResponse(BaseModel):
    matches: List[MatchItem]
