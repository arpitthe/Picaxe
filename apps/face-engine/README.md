# 👤 Picaxe Face Engine

The **Picaxe Face Engine** is an independent Python/FastAPI computer vision microservice designed to perform robust face localization, quality check validation, ArcFace embedding generation, and Qdrant similarity searches.

---

## 🏗️ Architecture & Pipeline

```text
Request Payload (Base64)
           │
           ▼
[Preprocessing] ──► Decode Base64 ──► Aspect Ratio / Dimensions ──► Resize ──► RGB
           │
           ▼
[Detector] ──────► Localization (det_10g.onnx) ──► 5 Landmarks (Keypoints)
           │
           ├──► [Quality Validation] ──► Blur, Brightness, Fraction gates
           │
           ▼
[Alignment] ─────► Internal Similarity Transform Warping (112x112 px crop)
           │
           ▼
[Embedder] ──────► ResNet-50 ArcFace (w600k_r50.onnx) ──► L2-norm 512-D vector
           │
           ▼
[Vector DB] ─────► Qdrant ANN Cosine Search & Idempotent Upsert
```

---

## 📊 Verified Model Information

These metrics were empirically verified directly from the loaded `buffalo_l` ONNX models:

1. **Face Detection Model**: `SCRFD` (ONNX model: `det_10g.onnx`, input tensor: `[1, 3, 640, 640]`).
2. **Recognition/Embedding Model**: `ArcFaceONNX` (ONNX model: `w600k_r50.onnx` trained on WebFace600K).
3. **Backbone Architecture**: ResNet-50.
4. **Landmark Detection**: 3D 68-points (`1k3d68.onnx`) & 2D 106-points (`2d106det.onnx`).
5. **Embedding Dimensionality**: 512 float32 parameters.
6. **Distance Metric**: Cosine Distance ($\text{Similarity} = \vec{u} \cdot \vec{v}$ for unit L2-norm vectors).
7. **Normalization**: Unit L2-normalized ($\|\vec{v}\| = 1.0$) automatically before storage/search.
8. **Alignment Strategy**: InsightFace `FaceAnalysis` handles similarity transformation alignment using the 5 keypoints (`kps`) internally to align faces to $112 \times 112$ pixels before embedding extraction.

---

## ⚙️ Configuration & Environment Variables

Create `apps/face-engine/.env` to customize settings:

```env
# Service Settings
PORT=8000
HOST=0.0.0.0
ENV=development

# Quality Validation Thresholds
MIN_FACE_FRACTION=0.05
BLUR_THRESHOLD=80.0
MIN_BRIGHTNESS=30.0
MAX_BRIGHTNESS=230.0

# Matching Thresholds
SIMILARITY_THRESHOLD=0.50
HIGH_CONFIDENCE_THRESHOLD=0.70
REVIEW_THRESHOLD=0.50

# Qdrant Database Connections
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=face_embeddings
QDRANT_API_KEY=
```

---

## 🔌 API Endpoints

### 1. `GET /health`
Returns system, loaded model, and database status.

**Example Response**:
```json
{
  "status": "ok",
  "service": "Picaxe Face Engine",
  "version": "1.0.0",
  "model_loaded": true,
  "qdrant_connected": true,
  "insightface_model": "buffalo_l",
  "detector": "SCRFD (det_10g.onnx)",
  "recognition_model": "ArcFace (w600k_r50.onnx - ResNet50)",
  "embedding_dimension": 512,
  "distance_metric": "Cosine"
}
```

---

### 2. `POST /face/register`
Student Registration Endpoint.

- **Request**:
  ```json
  {
    "student_id": "student_012",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "student_id": "student_012",
    "qdrant_point_id": "d748f3b9-11ba-449e-b5c6-c95843b0ea2d",
    "model_version": "buffalo_l-w600k_r50",
    "embedding_dimension": 512,
    "quality": {
      "valid": true,
      "score": 0.842,
      "blur_score": 145.2,
      "brightness": 112.5,
      "face_fraction": 0.124,
      "reason": null
    }
  }
  ```

---

### 3. `POST /face/search-event`
Event Multi-face Matching Endpoint.

- **Request**:
  ```json
  {
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "limit_per_face": 5,
    "score_threshold": 0.50
  }
  ```
- **Response**:
  ```json
  {
    "total_faces_detected": 1,
    "faces": [
      {
        "face_index": 0,
        "bbox": [120, 80, 240, 220],
        "detection_confidence": 0.9842,
        "quality": {
          "valid": true,
          "score": 0.812,
          "blur_score": 132.4,
          "brightness": 98.2,
          "face_fraction": 0.082,
          "reason": null
        },
        "matches": [
          {
            "student_id": "student_012",
            "similarity": 0.8241,
            "confidence_tier": "HIGH_CONFIDENCE",
            "qdrant_point_id": "d748f3b9-11ba-449e-b5c6-c95843b0ea2d"
          }
        ]
      }
    ]
  }
  ```

---

## 🚀 Setup & Execution

### Local Development
1. Activate virtual environment and install dependencies:
   ```bash
   cd apps/face-engine
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Running Tests
Execute unit and mock integration tests:
```bash
python -m unittest discover -s tests
```

### Running Threshold Evaluation Experiment
```bash
python -m scripts.experiment_similarity
```
Outputs report to console and generates `scripts/evaluation_results.json`.

### Running CALFW Benchmark Evaluation
Run the dedicated CALFW evaluation pipeline to benchmark Face Engine verification accuracy. This requires the dataset to be locally downloaded.
```bash
python -m scripts.evaluate_calfw --dataset-root "C:\Users\Acer\Downloads\calfw\calfw" --max-pairs 100
```
Optional arguments:
- `--max-pairs N`: Evaluate only the first N verification pairs.
- `--cache-dir`: Path to store/load embedding cache (e.g., `scripts/evaluation/cache`).
- `--force-recompute`: Ignore existing cache and recompute embeddings.

Outputs will be generated in `scripts/evaluation/`, including a JSON summary, a CSV of metrics per threshold, a score distribution plot, and a markdown report.
