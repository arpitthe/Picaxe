from pydantic import BaseModel
from typing import Optional

class OcrResponse(BaseModel):
    raw_text: str
    confidence: float

class NameExtractionResponse(BaseModel):
    extracted_name: str
    confidence: float

class CertificateAnalyzeResponse(BaseModel):
    raw_text: str
    extracted_name: Optional[str] = None
    match_score: Optional[float] = None
