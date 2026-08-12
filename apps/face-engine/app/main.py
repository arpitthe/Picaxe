from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.api.face import router as face_router
from app.core.config import settings
from app.detection.detector import _get_insightface_app, is_model_loaded
from app.qdrant.client import get_qdrant_repository
from app.exceptions.custom import (
    FaceEngineException, face_engine_exception_handler, global_exception_handler, ErrorCode
)
from app.schemas.responses import HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    logger.info("Initializing models on startup...")
    try:
        _get_insightface_app()
    except Exception as exc:
        logger.error(f"Startup model initialization failed: {exc}")
    
    # Initialize Qdrant collection on startup if connected
    try:
        repo = get_qdrant_repository()
        repo.get_client()
    except Exception as exc:
        logger.warning(f"Startup Qdrant connection skipped (will retry on demand): {exc}")
        
    yield
    logger.info("Shutting down Face Engine...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Picaxe Face Engine — ArcFace 512-D Face Detection, Quality Validation, Embedding & Qdrant Search",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
app.add_exception_handler(FaceEngineException, face_engine_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom Pydantic request validation error handler."""
    logger.error(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error_code": ErrorCode.INVALID_IMAGE.value,
            "detail": "Request validation failed: " + "; ".join([f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()]),
            "path": request.url.path
        }
    )

app.include_router(face_router)

@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
def health_check():
    """
    Robust health check returning configuration & connectivity details.
    Does not throw HTTP 500 if Qdrant is down, but returns status='degraded'.
    """
    qdrant_connected = False
    try:
        repo = get_qdrant_repository()
        qdrant_connected = repo.is_connected()
    except Exception:
        pass
        
    model_loaded = is_model_loaded()
    
    status_str = "ok"
    if not model_loaded:
        status_str = "unhealthy"
    elif not qdrant_connected:
        status_str = "degraded"
        
    import platform
    execution_provider = "CPUExecutionProvider"
    if settings.INSIGHTFACE_CTX_ID >= 0:
        execution_provider = "CUDAExecutionProvider"

    return {
        "status": status_str,
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model_loaded": model_loaded,
        "qdrant_connected": qdrant_connected,
        "insightface_model": settings.INSIGHTFACE_MODEL,
        "detector": settings.DETECTOR_MODEL_NAME,
        "recognition_model": settings.RECOGNITION_MODEL_NAME,
        "embedding_dimension": settings.EMBEDDING_DIMENSION,
        "distance_metric": settings.DISTANCE_METRIC
    }
