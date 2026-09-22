from app.nlp.name_extractor import NameExtractor
from app.nlp.ner import NameNER
from app.nlp.candidate_scorer import CandidateScorer


class CandidatePipeline:
    """
    Combines:
    - Rule-based recipient extraction
    - spaCy NER
    - Candidate scoring
    """

    def __init__(self):

        self.name_extractor = NameExtractor()
        self.ner = NameNER()
        self.scorer = CandidateScorer()

    def process(self, detections):

        # -----------------------------------------
        # 1. Generate candidates from context
        # -----------------------------------------

        candidates = self.name_extractor.extract_candidates(
            detections
        )

        if not candidates:
            return {
                "name": None,
                "score": 0.0,
                "candidates": [],
            }

        # -----------------------------------------
        # 2. Run spaCy over all OCR text
        # -----------------------------------------

        full_text = " ".join(
            detection["text"]
            for detection in detections
        )

        persons = self.ner.extract_persons(full_text)

        person_names = {
            person["name"].strip().upper()
            for person in persons
        }

        # -----------------------------------------
        # 3. Score every candidate
        # -----------------------------------------

        scored_candidates = []

        for candidate in candidates:

            candidate_name = candidate["name"]

            is_person = (
                candidate_name.upper()
                in person_names
            )

            scored = self.scorer.score_candidate(
                candidate=candidate_name,
                ocr_confidence=candidate["ocr_confidence"],
                recipient_context=candidate["recipient_context"],
                is_person=is_person,
            )

            scored_candidates.append(scored)

        # -----------------------------------------
        # 4. Select highest scoring candidate
        # -----------------------------------------

        scored_candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        winner = scored_candidates[0]

        return {
            "name": winner["name"],
            "score": winner["score"],
            "candidates": scored_candidates,
        }