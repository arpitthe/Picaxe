"""
InsightFace ArcFace Embedder Implementation.

Wraps the ArcFaceONNX model (w600k_r50.onnx — ResNet50 backbone)
from InsightFace's buffalo_l model pack.
"""

import logging
from typing import Any
import numpy as np

from app.embedding.base import BaseFaceEmbedder
from app.core.config import settings
from app.exceptions.custom import ModelInferenceException

logger = logging.getLogger(__name__)

def l2_normalize(vec: np.ndarray) -> np.ndarray:
    """Performs L2 vector normalization."""
    norm = np.linalg.norm(vec)
    if norm == 0.0 or np.isnan(norm):
        return vec
    return (vec / norm).astype(np.float32)

class InsightFaceEmbedder(BaseFaceEmbedder):

    def __init__(self, dimension: int = settings.EMBEDDING_DIMENSION):
        self.dimension = dimension

    def get_embedding_dimension(self) -> int:
        return self.dimension

    def embed_face(self, face_obj: Any) -> np.ndarray:
        """
        Extracts and verifies the 512-D ArcFace vector embedding from a detected face.
        """
        if face_obj is None or not hasattr(face_obj, "embedding") or face_obj.embedding is None:
            raise ModelInferenceException("Face object does not contain an embedding attribute.")

        raw_vec = face_obj.embedding
        if not isinstance(raw_vec, np.ndarray):
            raw_vec = np.array(raw_vec, dtype=np.float32)

        # Flatten vector to 1D
        vec_1d = raw_vec.flatten().astype(np.float32)

        # Dimensionality assertion
        if vec_1d.shape[0] != self.dimension:
            raise ModelInferenceException(
                f"Embedding dimension mismatch: expected {self.dimension}, got {vec_1d.shape[0]}"
            )

        # Perform L2 normalization
        norm_vec = l2_normalize(vec_1d)
        return norm_vec
