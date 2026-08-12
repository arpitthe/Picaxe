# API Contract: Backend Gateway ↔ Face Engine

This document defines the HTTP API contract between the NestJS Backend (`apps/backend`) and the Python Face Engine (`apps/face-engine`).

## Base URL
- **Local Development**: `http://localhost:8000`

---

## Endpoints

### 1. `POST /face/embed`
Generates a 512-dimensional vector embedding from a base64-encoded face image.

- **Request Body**:
  ```json
  {
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }
  ```

- **Response Body (`200 OK`)**:
  ```json
  {
    "embedding": [0.012, -0.045, 0.891, "...(512 floats total)"]
  }
  ```

---

### 2. `POST /face/search`
Searches Qdrant for matching student face embeddings.

- **Request Body**:
  ```json
  {
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "limit": 10,
    "score_threshold": 0.65
  }
  ```

- **Response Body (`200 OK`)**:
  ```json
  {
    "matches": [
      {
        "student_id": "stu_8849102",
        "score": 0.94
      }
    ]
  }
  ```

---

### Legacy Compatibility Routes
- `POST /ai/face/embed`
- `POST /ai/face/search`
