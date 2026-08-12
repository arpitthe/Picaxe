"""
Picaxe Face Engine Configuration Module.

All thresholds, model names, and infrastructure parameters are loaded
from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Picaxe Face Engine"
    VERSION: str = "1.0.0"
    ENV: str = os.getenv("ENV", "development")
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # InsightFace Model Configuration
    INSIGHTFACE_MODEL: str = os.getenv("INSIGHTFACE_MODEL", "buffalo_l")
    INSIGHTFACE_CTX_ID: int = int(os.getenv("INSIGHTFACE_CTX_ID", "-1"))  # -1 = CPU, 0+ = CUDA GPU
    
    # Model Metadata (Verified empirically from InsightFace buffalo_l pack)
    DETECTOR_MODEL_NAME: str = "SCRFD (det_10g.onnx)"
    RECOGNITION_MODEL_NAME: str = "ArcFace (w600k_r50.onnx - ResNet50)"
    EMBEDDING_DIMENSION: int = 512
    DISTANCE_METRIC: str = "Cosine"

    # Preprocessing Limits
    MAX_IMAGE_SIZE_BYTES: int = int(os.getenv("MAX_IMAGE_SIZE_BYTES", str(10 * 1024 * 1024))) # 10 MB limit
    MAX_IMAGE_DIMENSION: int = int(os.getenv("MAX_IMAGE_DIMENSION", "1920"))

    # Configurable Quality Validation Thresholds
    MIN_FACE_FRACTION: float = float(os.getenv("MIN_FACE_FRACTION", "0.05")) # 5% minimum image area
    BLUR_THRESHOLD: float = float(os.getenv("BLUR_THRESHOLD", "80.0"))       # Laplacian variance threshold
    MIN_BRIGHTNESS: float = float(os.getenv("MIN_BRIGHTNESS", "30.0"))       # 0–255 scale
    MAX_BRIGHTNESS: float = float(os.getenv("MAX_BRIGHTNESS", "230.0"))      # 0–255 scale

    # Configurable Matching Thresholds
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.50"))
    HIGH_CONFIDENCE_THRESHOLD: float = float(os.getenv("HIGH_CONFIDENCE_THRESHOLD", "0.70"))
    REVIEW_THRESHOLD: float = float(os.getenv("REVIEW_THRESHOLD", "0.50"))

    # Qdrant Vector Database
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "face_embeddings")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_VECTOR_SIZE: int = 512

settings = Settings()
