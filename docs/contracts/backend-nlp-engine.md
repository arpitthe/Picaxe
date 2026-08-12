# API Contract: Backend Gateway ↔ NLP Engine

This document defines the HTTP API contract between the NestJS Backend (`apps/backend`) and the Python NLP Engine (`apps/nlp-engine`).

## Base URL
- **Local Development**: `http://localhost:8001`

---

## Endpoints

### 1. `POST /certificate/ocr`
Performs OCR extraction on an uploaded certificate image or document.

- **Request Body**:
  ```json
  {
    "image_base64": "data:image/png;base64,iVBORw0KGgo...",
    "filename": "certificate_john_doe.png"
  }
  ```

- **Response Body (`200 OK`)**:
  ```json
  {
    "raw_text": "Certificate of Merit awarded to Johnathan Doe for 1st place in Hackathon.",
    "confidence": 0.97
  }
  ```

---

### 2. `POST /certificate/extract-name`
Extracts student candidate names from raw OCR text using Named Entity Recognition (NER).

- **Request Body**:
  ```json
  {
    "raw_text": "Certificate of Merit awarded to Johnathan Doe for 1st place in Hackathon."
  }
  ```

- **Response Body (`200 OK`)**:
  ```json
  {
    "extracted_name": "Johnathan Doe",
    "confidence": 0.94
  }
  ```

---

### 3. `POST /certificate/analyze`
Full pipeline processing combining OCR, name extraction, and fuzzy score matching.

- **Request Body**:
  ```json
  {
    "image_base64": "data:image/png;base64,iVBORw0KGgo...",
    "target_name": "John Doe"
  }
  ```

- **Response Body (`200 OK`)**:
  ```json
  {
    "raw_text": "Certificate of Merit awarded to Johnathan Doe for 1st place in Hackathon.",
    "extracted_name": "Johnathan Doe",
    "match_score": 0.92
  }
  ```
