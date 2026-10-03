from typing import Optional

from pydantic import BaseModel


class CertificateOcrRequest(BaseModel):
    image_base64: str
    filename: Optional[str] = None


class ExtractNameRequest(BaseModel):
    raw_text: str


class CertificateAnalyzeRequest(BaseModel):
    image_base64: str
    filename: Optional[str] = None
    target_name: Optional[str] = None