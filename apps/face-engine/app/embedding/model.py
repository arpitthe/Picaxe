"""
Embedding Utilities and Helper Functions.

Contains L2-normalization, cosine similarity scoring, and array conversion helpers.
"""

from typing import List
import numpy as np

def l2_normalize(vec: np.ndarray) -> np.ndarray:
    """Returns L2 unit-norm version of a vector."""
    vec = vec.astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm == 0.0 or np.isnan(norm):
        return vec
    return vec / norm

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Computes cosine similarity between two vector embeddings.

    For L2-normalized unit vectors, cosine similarity is equivalent to the dot product.
    Returns float score in range [-1.0, 1.0].
    """
    a_norm = l2_normalize(a.flatten())
    b_norm = l2_normalize(b.flatten())
    dot_product = float(np.dot(a_norm, b_norm))
    return float(np.clip(dot_product, -1.0, 1.0))

def embedding_to_list(embedding: np.ndarray) -> List[float]:
    """Converts a numpy embedding array to a Python float list."""
    return l2_normalize(embedding.flatten()).tolist()
