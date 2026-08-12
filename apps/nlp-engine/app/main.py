from fastapi import FastAPI
from app.api.certificate import router as certificate_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(certificate_router)

@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
