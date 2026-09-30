import base64
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.requests import (
    CertificateOcrRequest,
    ExtractNameRequest,
    CertificateAnalyzeRequest,
)
from app.schemas.responses import (
    OcrResponse,
    NameExtractionResponse,
    CertificateAnalyzeResponse,
)

from app.ocr.ocr_engine import CertificateOCR
from app.nlp.candidate_pipeline import CandidatePipeline
from app.matching.name_matcher import NameMatcher


router = APIRouter(
    prefix="/certificate",
    tags=["Certificate NLP"],
)


# Initialize models once when the service starts.
ocr_engine = CertificateOCR()
candidate_pipeline = CandidatePipeline()
name_matcher = NameMatcher()


def decode_base64_image(image_base64: str) -> bytes:
    """
    Decode a normal base64 string or a data-URL base64 string.
    """

    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]

        return base64.b64decode(
            image_base64,
            validate=True,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid base64 image.",
        ) from exc


def get_image_suffix(filename: str | None) -> str:
    """
    Determine a supported image suffix from the supplied filename.

    Falls back to .png when the filename is missing or unsupported.
    """

    suffix = Path(filename or "").suffix.lower()

    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        suffix = ".png"

    return suffix


def run_ocr(
    image_base64: str,
    filename: str | None = None,
):
    """
    Decode the supplied image, save it temporarily,
    and run PaddleOCR.
    """

    image_bytes = decode_base64_image(image_base64)
    suffix = get_image_suffix(filename)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(image_bytes)
            temp_path = temp_file.name

        detections = ocr_engine.extract_text(temp_path)

        return detections

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def build_raw_text(detections):
    return " ".join(
        detection["text"]
        for detection in detections
    )


def calculate_ocr_confidence(detections):
    if not detections:
        return 0.0

    return sum(
        detection["confidence"]
        for detection in detections
    ) / len(detections)


@router.post(
    "/ocr",
    response_model=OcrResponse,
)
def ocr_certificate(req: CertificateOcrRequest):
    """
    Run OCR on a certificate image.
    """

    detections = run_ocr(
        req.image_base64,
        req.filename,
    )

    raw_text = build_raw_text(detections)

    confidence = calculate_ocr_confidence(
        detections
    )

    return OcrResponse(
        raw_text=raw_text,
        confidence=round(confidence, 4),
    )


@router.post(
    "/extract-name",
    response_model=NameExtractionResponse,
)
def extract_name(req: ExtractNameRequest):
    """
    Extract the certificate recipient from plain OCR text.

    Recipient-context extraction is preferred. spaCy PERSON
    detection is used only as a fallback when no recipient
    anchor can be identified.
    """

    candidates = (
        candidate_pipeline.name_extractor
        .extract_candidates_from_text(req.raw_text)
    )

    if candidates:
        candidate = candidates[0]

        scored = candidate_pipeline.scorer.score_candidate(
            candidate=candidate["name"],
            ocr_confidence=0.0,
            recipient_context=True,
            is_person=False,
        )

        return NameExtractionResponse(
            extracted_name=candidate["name"],
            confidence=scored["score"],
        )

    # Fallback when the OCR text does not contain recognizable
    # recipient context.
    persons = candidate_pipeline.ner.extract_persons(
        req.raw_text
    )

    if not persons:
        return NameExtractionResponse(
            extracted_name=None,
            confidence=0.0,
        )

    extracted_name = persons[0]["name"]

    return NameExtractionResponse(
        extracted_name=extracted_name,
        confidence=0.2,
    )


@router.post(
    "/analyze",
    response_model=CertificateAnalyzeResponse,
)
def analyze_certificate(
    req: CertificateAnalyzeRequest,
):
    """
    Full certificate pipeline:

    OCR → recipient extraction → candidate scoring
    → fuzzy matching against target_name.
    """

    detections = run_ocr(
        req.image_base64,
        req.filename,
    )

    raw_text = build_raw_text(detections)

    candidate_result = candidate_pipeline.process(
        detections
    )

    extracted_name = candidate_result["name"]

    match_score = None

    if extracted_name and req.target_name:
        participant = {
            "id": "target",
            "name": req.target_name,
        }

        match_result = name_matcher.match(
            extracted_name,
            [participant],
        )

        # Contract uses a 0.0 - 1.0 score.
        match_score = round(
            match_result["score"] / 100,
            4,
        )

    return CertificateAnalyzeResponse(
        raw_text=raw_text,
        extracted_name=extracted_name,
        match_score=match_score,
    )