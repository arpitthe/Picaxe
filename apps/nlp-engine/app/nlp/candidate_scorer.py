class CandidateScorer:
    """
    Scores possible certificate recipients using
    multiple independent signals.
    """

    def score_candidate(
        self,
        candidate,
        ocr_confidence=0.0,
        recipient_context=False,
        is_person=False,
    ):
        """
        Calculate a recipient score.

        Signals:
        - recipient context
        - OCR confidence
        - spaCy PERSON detection
        """

        score = 0.0
        reasons = []

        # -----------------------------------------
        # 1. Recipient context
        # -----------------------------------------

        if recipient_context:
            score += 0.60
            reasons.append("recipient_context")

        # -----------------------------------------
        # 2. OCR confidence
        # -----------------------------------------

        score += 0.20 * ocr_confidence

        if ocr_confidence >= 0.90:
            reasons.append("high_ocr_confidence")

        # -----------------------------------------
        # 3. spaCy PERSON detection
        # -----------------------------------------

        if is_person:
            score += 0.20
            reasons.append("spacy_person")

        return {
            "name": candidate,
            "score": round(score, 4),
            "reasons": reasons,
        }