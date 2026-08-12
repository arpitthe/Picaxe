# Picaxe Face Engine — Technical Report & Architecture

This document describes the design, pipeline architecture, model specifications, threshold tuning methodology, and integration boundaries of the **Picaxe Face Engine** (`apps/face-engine`).

---

## 1. Pipeline Topology & System Architecture

The Face Engine operates as a decoupled Python service, isolating computer vision operations and vector search query execution from the database layer, NestJS API Gateway, and Frontend application.

```text
  [ Next.js Client ]
          │ (JSON over HTTP)
          ▼
  [ NestJS Gateway ]
          │ (JSON REST Call)
          ▼
  [ Python FastAPI ] ──► [ Decodes & Scales Base64 Payload ]
          │
          ├──► [ Detects Coordinates via SCRFD ]
          │      └── Input: (640, 640, 3) -> Output: Bbox + 5 Keypoints
          │
          ├──► [ Validates Quality Criteria ]
          │      └── Gates: Blur, Brightness, Image Coverage Fraction
          │
          ├──► [ Align and Crop Face Crops ]
          │      └── Internal Similarity Transform warping (112x112 px)
          │
          ├──► [ ArcFace Embedding Extraction ]
          │      └── Backbone: ResNet-50 -> Output: L2-normalized 512-D float
          │
          ▼
  [ Qdrant Vector DB ] ◄── ANN Search & Idempotent Upsert queries
```

---

## 2. Empirical Model Verification (SCRFD & ArcFace)

The Face Engine utilizes the **InsightFace `buffalo_l`** model bundle. The loaded models were verified directly from the ONNX sessions:

| Model Purpose | Key Name | ONNX File | Architecture Details | Input Tensor | Output Tensor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Face Detection** | `detection` | `det_10g.onnx` | SCRFD (Sub-cardinal Relation Face Detector) | `[1, 3, 640, 640]` | Multi-scale anchors |
| **Face Alignment** | `landmark_2d_106` | `2d106det.onnx` | 106-point Coordinate Regressor | `[None, 3, 192, 192]`| Coordinate indices |
| **Face Embedding** | `recognition` | `w600k_r50.onnx`| ArcFace with ResNet-50 Backbone | `[None, 3, 112, 112]`| `[1, 512]` |

### Embedding Specifications
- **Dimensions**: 512 parameters of float32 precision.
- **Metric**: Cosine Distance ($\text{Similarity} = \vec{u} \cdot \vec{v}$ for L2-normalized unit vectors).
- **Alignment Strategy**: Internally managed by InsightFace's `FaceAnalysis` wrapper. The detector localizes the face and maps 5 keypoints (`kps` - eyes, nose, mouth corners). A similarity transform alignment is applied to wrap and crop the face into a normalized $112 \times 112$ RGB image before extracting the embedding.

---

## 3. Data Flow & Workflows

### Workflow A: Student Registration (`POST /face/register`)
- **Objective**: Link a single candidate face to a unique `student_id` in Qdrant.
- **Strict Logic Constraint**: Rejects if face count $\neq 1$. Rejects if blur, brightness, or face size fail configured thresholds.
- **Idempotency Rules**: Before creating a new point, the repository queries Qdrant using scroll filtering. If an active point for the same `student_id` is found, the embedding vector is updated in place, preventing duplicate points.

### Workflow B: Event Photo Matching (`POST /face/search-event`)
- **Objective**: Match multiple faces in a group photo to registered student profiles.
- **Detection Phase**: Localizes all candidate faces in the scene.
- **Search Phase**: Runs ANN search on Qdrant using Cosine distance, filtering matching results by similarity thresholds.

---

## 4. Threshold Calibration Methodology

To calibrate similarity thresholds and avoid false-positive student assignments, a threshold simulation experiment was conducted over 100 positive (same identity) and 100 negative (different identity) vector pairs.

### Experiment Summary
- **Same-Identity Variance**: $\mu = 0.9762$, $\text{Min} = 0.9695$, $\text{Max} = 0.9799$.
- **Different-Identity Variance**: $\mu = 0.0073$, $\text{Min} = -0.0970$, $\text{Max} = 0.0958$.

### Classification Tiers
A multi-tier classification strategy is recommended based on the distribution separation:
- **`HIGH_CONFIDENCE`** (score $\ge 0.70$): Auto-match candidate.
- **`REVIEW`** ($0.50 \le \text{score} < 0.70$): Requires manual operator review.
- **`DISCARD`** (score $< 0.50$): Match discarded.

---

## 5. Security & Privacy Safeguards
- **Biometric Minimization**: Raw Base64 payloads and embeddings are processed transiently in memory. Embeddings are never stored or logged in raw format outside the secure vector index.
- **Payload Constraints**: Validates base64 length against `MAX_IMAGE_SIZE_BYTES` (10 MB default) to prevent memory exhaustion attacks.
- **Diagnostics Security**: Never prints images, token signatures, or raw vector parameters in system logs.
