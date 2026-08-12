from pydantic import BaseModel
from typing import Optional

class CertificateOcrRequest(BaseModel):
    image_base64: str
    filename: Optional[str] = None

class ExtractNameRequest(BaseModel):
    raw_text: str

class CertificateAnalyzeRequest(BaseModel):
    image_base64: str
    target_name: Optional[str] = None
