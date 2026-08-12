from fastapi import APIRouter
from app.schemas.requests import CertificateOcrRequest, ExtractNameRequest, CertificateAnalyzeRequest
from app.schemas.responses import OcrResponse, NameExtractionResponse, CertificateAnalyzeResponse

router = APIRouter(prefix="/certificate", tags=["Certificate NLP"])

@router.post("/ocr", response_model=OcrResponse)
def ocr_certificate(req: CertificateOcrRequest):
    # Stub implementation for OCR
    return OcrResponse(raw_text="Sample Certificate of Completion awarded to John Doe", confidence=0.98)

@router.post("/extract-name", response_model=NameExtractionResponse)
def extract_name(req: ExtractNameRequest):
    # Stub implementation for Name Extraction
    return NameExtractionResponse(extracted_name="John Doe", confidence=0.95)

@router.post("/analyze", response_model=CertificateAnalyzeResponse)
def analyze_certificate(req: CertificateAnalyzeRequest):
    # Stub implementation for overall analysis
    return CertificateAnalyzeResponse(
        raw_text="Sample Certificate of Completion awarded to John Doe",
        extracted_name="John Doe",
        match_score=0.96
    )
