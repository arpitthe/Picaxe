# Picaxe Face Engine — AI Specifications

The **Picaxe Face Engine** (`apps/face-engine`) is an isolated computer vision service. This document details its AI specifications.

Refer to [Technical Report](file:///c:/Coding/picaxe/docs/face-engine.md) for full architecture.

---

## Model Specifications

1. **SCRFD (det_10g.onnx)**: Sub-cardinal Relation Face Detector, optimized for accuracy and inference runtime.
2. **ArcFace (w600k_r50.onnx)**: ResNet-50 ArcFace deep recognition model, maps face crops to 512-dimensional vector embedding.
3. **Distance Metric**: Cosine similarity.
4. **Target Dimension**: 512 parameters of float32 precision.
