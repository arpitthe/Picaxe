"""
Similarity Scoring and Multi-Tier Confidence Matching Module.

Classifies matches into confidence tiers:
  - HIGH_CONFIDENCE (score >= HIGH_CONFIDENCE_THRESHOLD)
  - REVIEW          (REVIEW_THRESHOLD <= score < HIGH_CONFIDENCE_THRESHOLD)
  - DISCARD         (score < REVIEW_THRESHOLD)
"""

from typing import List, Dict, Any, Optional
from enum import Enum

from app.embedding.model import cosine_similarity
from app.core.config import settings

class ConfidenceTier(str, Enum):
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    REVIEW = "REVIEW"
    DISCARD = "DISCARD"

def classify_confidence_tier(score: float) -> ConfidenceTier:
    """Classifies similarity score into high confidence, review, or discard tiers."""
    if score >= settings.HIGH_CONFIDENCE_THRESHOLD:
        return ConfidenceTier.HIGH_CONFIDENCE
    elif score >= settings.REVIEW_THRESHOLD:
        return ConfidenceTier.REVIEW
    else:
        return ConfidenceTier.DISCARD

def rank_and_tier_matches(candidates: List[Dict[str, Any]], threshold: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Filters candidates by threshold and attaches confidence tier classifications.

    Each candidate dict is expected to have 'score' and 'student_id'.
    """
    cutoff = threshold if threshold is not None else settings.SIMILARITY_THRESHOLD
    
    results = []
    for c in candidates:
        score = float(c.get("score", 0.0))
        if score >= cutoff:
            tier = classify_confidence_tier(score)
            item = dict(c)
            item["score"] = round(score, 4)
            item["confidence_tier"] = tier.value
            results.append(item)
            
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
