"""
Abstract Base Class for Face Embedders.

Provides an isolated interface for embedding extraction models.
"""

from abc import ABC, abstractmethod
from typing import Any
import numpy as np

class BaseFaceEmbedder(ABC):

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Returns the output vector dimensionality (e.g. 512)."""
        pass

    @abstractmethod
    def embed_face(self, face_obj: Any) -> np.ndarray:
        """
        Extracts an L2-normalized 512-dimensional vector embedding for a detected face.

        Args:
            face_obj: InsightFace face object or detected face region.

        Returns:
            np.ndarray: float32 L2-normalized 1D array of shape (dimension,).
        """
        pass
