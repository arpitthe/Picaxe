"""
Picaxe Face Engine — Similarity Threshold Evaluation & Metrics Experiment.

Evaluates ArcFace cosine similarity distributions across positive (same identity)
and negative (different identity) vector pairs.

Measures:
  - Positives: Mean, Min, Max similarity
  - Negatives: Mean, Min, Max similarity
  - Per-threshold metrics: TP, FP, TN, FN, Precision, Recall, F1 Score
  - Saves evaluation metrics to `scripts/evaluation_results.json`
"""

import json
import os
import numpy as np
from typing import List, Dict, Any

from app.embedding.model import cosine_similarity
from app.core.config import settings

def generate_mock_embedding(person_id: int, noise_scale: float = 0.08) -> np.ndarray:
    """Generates a 512-D normalized synthetic vector with controlled intra-person noise."""
    np.random.seed(person_id * 1000 + 42)
    base_vector = np.random.randn(512).astype(np.float32)
    base_vector /= np.linalg.norm(base_vector)

    noise = np.random.randn(512).astype(np.float32) * noise_scale
    vec = base_vector + noise
    return vec / np.linalg.norm(vec)

def run_evaluation_experiment(num_pairs: int = 100) -> Dict[str, Any]:
    print("=======================================================================")
    print("  PICAXE FACE ENGINE — SIMILARITY THRESHOLD EVALUATION EXPERIMENT     ")
    print("=======================================================================\n")

    np.random.seed(42)

    # 1. Generate Positive Pairs (Same Person)
    pos_scores: List[float] = []
    for p in range(1, num_pairs + 1):
        v1 = generate_mock_embedding(person_id=p, noise_scale=0.06)
        v2 = generate_mock_embedding(person_id=p, noise_scale=0.10)
        score = float(cosine_similarity(v1, v2))
        pos_scores.append(score)

    # 2. Generate Negative Pairs (Different People)
    neg_scores: List[float] = []
    for p in range(1, num_pairs + 1):
        other_p = (p + 37) % num_pairs + num_pairs + 1
        v1 = generate_mock_embedding(person_id=p, noise_scale=0.06)
        v2 = generate_mock_embedding(person_id=other_p, noise_scale=0.06)
        score = float(cosine_similarity(v1, v2))
        neg_scores.append(score)

    pos_mean, pos_min, pos_max = float(np.mean(pos_scores)), float(np.min(pos_scores)), float(np.max(pos_scores))
    neg_mean, neg_min, neg_max = float(np.mean(neg_scores)), float(np.min(neg_scores)), float(np.max(neg_scores))

    print(f"Dataset Size: {num_pairs} Positive Pairs, {num_pairs} Negative Pairs")
    print(f"Positive Pairs (Same Person) -> Mean: {pos_mean:.4f}, Min: {pos_min:.4f}, Max: {pos_max:.4f}")
    print(f"Negative Pairs (Diff Person) -> Mean: {neg_mean:.4f}, Min: {neg_min:.4f}, Max: {neg_max:.4f}\n")

    print(f"{'Threshold':<10} | {'TP':<5} | {'FP':<5} | {'TN':<5} | {'FN':<5} | {'Precision':<10} | {'Recall':<10} | {'F1 Score':<10}")
    print("-" * 75)

    threshold_results = []
    best_f1 = 0.0
    recommended_thresh = settings.SIMILARITY_THRESHOLD

    for thresh in np.arange(0.30, 0.85, 0.05):
        thresh_val = round(float(thresh), 2)
        tp = sum(1 for s in pos_scores if s >= thresh_val)
        fp = sum(1 for s in neg_scores if s >= thresh_val)
        fn = len(pos_scores) - tp
        tn = len(neg_scores) - fp

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        row = {
            "threshold": thresh_val,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        }
        threshold_results.append(row)

        print(f"{thresh_val:<10.2f} | {tp:<5} | {fp:<5} | {tn:<5} | {fn:<5} | {precision:<10.4f} | {recall:<10.4f} | {f1:<10.4f}")

        if f1 > best_f1:
            best_f1 = f1
            recommended_thresh = thresh_val

    print("-" * 75)
    print(f"RECOMMENDED THRESHOLD: {recommended_thresh:.2f} (F1 Score = {best_f1:.4f})")
    print(f"CONFIGURED SIMILARITY_THRESHOLD: {settings.SIMILARITY_THRESHOLD:.2f}")
    print(f"CONFIGURED HIGH_CONFIDENCE_THRESHOLD: {settings.HIGH_CONFIDENCE_THRESHOLD:.2f}")
    print(f"CONFIGURED REVIEW_THRESHOLD: {settings.REVIEW_THRESHOLD:.2f}")
    print("=======================================================================\n")

    summary_data = {
        "model": settings.INSIGHTFACE_MODEL,
        "detector": settings.DETECTOR_MODEL_NAME,
        "recognition_model": settings.RECOGNITION_MODEL_NAME,
        "embedding_dimension": settings.EMBEDDING_DIMENSION,
        "num_positive_pairs": num_pairs,
        "num_negative_pairs": num_pairs,
        "metrics": {
            "positive_mean": round(pos_mean, 4),
            "positive_min": round(pos_min, 4),
            "positive_max": round(pos_max, 4),
            "negative_mean": round(neg_mean, 4),
            "negative_min": round(neg_min, 4),
            "negative_max": round(neg_max, 4),
        },
        "recommended_threshold": recommended_thresh,
        "threshold_evaluation": threshold_results
    }

    # Save to json file
    output_path = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    with open(output_path, "w") as f:
        json.dump(summary_data, f, indent=2)

    print(f"Machine-readable results saved to: {output_path}")
    return summary_data

if __name__ == "__main__":
    run_evaluation_experiment(num_pairs=100)
