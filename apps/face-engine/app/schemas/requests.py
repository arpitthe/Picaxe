from pydantic import BaseModel, Field
from typing import Optional

class FaceRegisterRequest(BaseModel):
    student_id: str = Field(..., description="Unique student ID from backend Gateway", example="stu_98412")
    image_base64: str = Field(..., description="Base64 encoded student registration photo (Raw or Data URL)")

class EventPhotoSearchRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded event photo (single or multi-face)")
    limit_per_face: Optional[int] = Field(default=5, description="Max candidate matches per detected face", ge=1, le=20)
    score_threshold: Optional[float] = Field(default=None, description="Similarity cutoff score threshold", ge=0.0, le=1.0)

class FaceQualityCheckRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded photo to validate quality")

class FaceEmbedRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded photo")

class FaceSearchRequest(BaseModel):
    image_base64: str
    limit: Optional[int] = 10
    score_threshold: Optional[float] = 0.5
