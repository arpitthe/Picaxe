"""
Custom Application Exceptions and FastAPI Exception Handlers.

Ensures machine-readable error responses and prevents raw Python stack traces
from being exposed to API clients.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ErrorCode(str, Enum):
    INVALID_IMAGE = "INVALID_IMAGE"
    IMAGE_CORRUPTED = "IMAGE_CORRUPTED"
    IMAGE_TOO_LARGE = "IMAGE_TOO_LARGE"
    NO_FACE_DETECTED = "NO_FACE_DETECTED"
    TOO_MANY_FACES = "TOO_MANY_FACES"
    FACE_TOO_SMALL = "FACE_TOO_SMALL"
    IMAGE_TOO_BLURRY = "IMAGE_TOO_BLURRY"
    IMAGE_TOO_DARK = "IMAGE_TOO_DARK"
    IMAGE_TOO_BRIGHT = "IMAGE_TOO_BRIGHT"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    QDRANT_UNAVAILABLE = "QDRANT_UNAVAILABLE"
    EMBEDDING_GENERATION_FAILED = "EMBEDDING_GENERATION_FAILED"
    SEARCH_FAILED = "SEARCH_FAILED"
    REGISTRATION_FAILED = "REGISTRATION_FAILED"

class FaceEngineException(Exception):
    def __init__(self, error_code: ErrorCode, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class InvalidImageException(FaceEngineException):
    def __init__(self, message: str = "Invalid image format or payload"):
        super().__init__(ErrorCode.INVALID_IMAGE, message, status.HTTP_400_BAD_REQUEST)

class CorruptedImageException(FaceEngineException):
    def __init__(self, message: str = "Image is corrupted and cannot be decoded"):
        super().__init__(ErrorCode.IMAGE_CORRUPTED, message, status.HTTP_400_BAD_REQUEST)

class QualityValidationException(FaceEngineException):
    def __init__(self, error_code: ErrorCode, message: str):
        super().__init__(error_code, message, status.HTTP_422_UNPROCESSABLE_ENTITY)

class ModelInferenceException(FaceEngineException):
    def __init__(self, message: str = "Failed to run face model inference"):
        super().__init__(ErrorCode.EMBEDDING_GENERATION_FAILED, message, status.HTTP_500_INTERNAL_SERVER_ERROR)

class QdrantRepositoryException(FaceEngineException):
    def __init__(self, message: str = "Vector database error"):
        super().__init__(ErrorCode.QDRANT_UNAVAILABLE, message, status.HTTP_503_SERVICE_UNAVAILABLE)

async def face_engine_exception_handler(request: Request, exc: FaceEngineException):
    """Global handler for FaceEngineException returning clean JSON responses."""
    logger.error(f"FaceEngineException [{exc.error_code.value}]: {exc.message} (Path: {request.url.path})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code.value,
            "detail": exc.message,
            "path": request.url.path
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    """Fallback handler for unhandled exceptions to prevent stack trace exposure."""
    logger.exception(f"Unhandled Exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "detail": "An internal server error occurred in the Face Engine.",
            "path": request.url.path
        }
    )
