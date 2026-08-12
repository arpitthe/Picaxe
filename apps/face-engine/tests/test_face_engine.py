"""
Picaxe Face Engine Unit & Integration Test Suite.

Contains mock repository setups for running tests independently of a live Qdrant server.
"""

import base64
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import cv2
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.exceptions.custom import ErrorCode
from app.preprocessing.image import decode_image, resize_if_needed, to_rgb, preprocess
from app.detection.quality import evaluate_quality
from app.embedding.model import cosine_similarity, l2_normalize
from app.matching.matcher import rank_and_tier_matches, ConfidenceTier
from app.qdrant.client import QdrantRepository

def create_dummy_image(width=100, height=100, color=(128, 128, 128)) -> str:
    """Helper to generate a base64 encoded dummy image."""
    img = np.full((height, width, 3), color, dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    return "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')


class TestFaceEnginePipeline(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.dummy_image = create_dummy_image()

    def test_01_preprocessing_valid(self):
        """Test robust decoding and color space conversion of valid input."""
        bgr = decode_image(self.dummy_image)
        self.assertIsNotNone(bgr)
        self.assertEqual(bgr.shape[2], 3)
        
        # Color conversion BGR to RGB
        rgb = to_rgb(bgr)
        self.assertEqual(rgb.shape, bgr.shape)

    def test_02_preprocessing_invalid(self):
        """Test validation of malformed and corrupted base64 payloads."""
        # Invalid Base64 format
        with self.assertRaises(Exception):
            decode_image("invalid-base64-string!!!")
            
        # Large payload size check
        original_limit = settings.MAX_IMAGE_SIZE_BYTES
        settings.MAX_IMAGE_SIZE_BYTES = 100  # set a very small limit
        try:
            with self.assertRaises(Exception):
                decode_image(self.dummy_image)
        finally:
            settings.MAX_IMAGE_SIZE_BYTES = original_limit

    def test_03_resizing_aspect_ratio(self):
        """Test proportional resizing constraints."""
        large_img = np.zeros((3000, 1500, 3), dtype=np.uint8)
        resized = resize_if_needed(large_img, max_dim=1000)
        self.assertEqual(resized.shape[0], 1000)
        self.assertEqual(resized.shape[1], 500) # Check aspect ratio preservation

    def test_04_quality_validation(self):
        """Test quality validation gates (blur, brightness, size)."""
        bgr = decode_image(self.dummy_image)
        bbox = [10, 10, 90, 90]
        report = evaluate_quality(bgr, bbox)
        
        # In a plain flat color synthetic image, blur score (Laplacian var) will be 0.0 (very blurry)
        self.assertFalse(report.valid)
        self.assertEqual(report.reason, ErrorCode.IMAGE_TOO_BLURRY)

    def test_05_cosine_similarity(self):
        """Test ArcFace cosine similarity calculations."""
        vec1 = np.zeros(512, dtype=np.float32)
        vec1[0] = 1.0
        
        vec2 = np.zeros(512, dtype=np.float32)
        vec2[0] = 1.0
        
        vec3 = np.zeros(512, dtype=np.float32)
        vec3[1] = 1.0 # orthogonal vector
        
        sim_same = cosine_similarity(vec1, vec2)
        sim_ortho = cosine_similarity(vec1, vec3)
        
        self.assertAlmostEqual(sim_same, 1.0, places=4)
        self.assertAlmostEqual(sim_ortho, 0.0, places=4)

    def test_06_matching_tiers(self):
        """Test multi-tier confidence classification."""
        candidates = [
            {"student_id": "stu_1", "score": 0.85},
            {"student_id": "stu_2", "score": 0.62},
            {"student_id": "stu_3", "score": 0.45},
        ]
        
        results = rank_and_tier_matches(candidates, threshold=0.50)
        
        self.assertEqual(len(results), 2) # stu_3 is below similarity threshold
        self.assertEqual(results[0]["confidence_tier"], ConfidenceTier.HIGH_CONFIDENCE.value)
        self.assertEqual(results[1]["confidence_tier"], ConfidenceTier.REVIEW.value)

    def test_07_api_health(self):
        """Test health check returns expected status keys."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("service", data)
        self.assertIn("model_loaded", data)
        self.assertIn("qdrant_connected", data)

    @patch('app.services.face_service.get_qdrant_repository')
    @patch('app.services.face_service.detect_faces')
    def test_08_registration_no_face(self, mock_detect, mock_get_repo):
        """Test registration endpoint returns NO_FACE_DETECTED error code on empty faces."""
        mock_detect.return_value = []
        
        response = self.client.post("/face/register", json={
            "student_id": "stu_123",
            "image_base64": self.dummy_image
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error_code"], ErrorCode.NO_FACE_DETECTED.value)

    @patch('app.services.face_service.get_qdrant_repository')
    @patch('app.services.face_service.detect_faces')
    def test_09_registration_multiple_faces(self, mock_detect, mock_get_repo):
        """Test registration endpoint returns TOO_MANY_FACES error code on multiple faces."""
        face1 = MagicMock()
        face2 = MagicMock()
        mock_detect.return_value = [face1, face2]
        
        response = self.client.post("/face/register", json={
            "student_id": "stu_123",
            "image_base64": self.dummy_image
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error_code"], ErrorCode.TOO_MANY_FACES.value)

    def test_10_error_response_format(self):
        """Test FastAPI error response matches our custom structure with no raw stack trace."""
        # Pass a completely empty body to trigger validator error handler
        response = self.client.post("/face/register", json={})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error_code"], ErrorCode.INVALID_IMAGE.value)
        self.assertIn("detail", data)


if __name__ == "__main__":
    unittest.main()
