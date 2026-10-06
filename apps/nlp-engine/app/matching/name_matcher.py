from rapidfuzz import fuzz


class NameMatcher:
    """
    Matches an extracted certificate name
    against known participant names.

    Uses:
    - Fuzzy name similarity
    - Best-vs-second-best margin
    - Confidence levels
    """

    def __init__(
        self,
        threshold=85,
        high_confidence_threshold=92,
        review_threshold=80,
        minimum_margin=5,
        
    ):
        self.match_threshold =  threshold
        self.high_confidence_threshold = high_confidence_threshold
        self.review_threshold = review_threshold
        self.minimum_margin = minimum_margin

    def normalize(self, name: str) -> str:
        """
        Normalize a name before comparison.
        """

        if not name:
            return ""

        return " ".join(
            name.upper().strip().split()
        )

    def match(self, extracted_name, participants):
        """
        Find the closest participant.

        Returns:
            {
                "status": "...",
                "match": {...},
                "score": ...,
                "confidence_level": "...",
                "second_best_score": ...,
                "margin": ...
            }
        """

        # -----------------------------------------
        # No extracted name
        # -----------------------------------------

        if not extracted_name:
            return {
                "status": "no_name",
                "match": None,
                "score": 0.0,
                "confidence_level": "none",
                "second_best_score": 0.0,
                "margin": 0.0,
            }

        extracted = self.normalize(extracted_name)

        # -----------------------------------------
        # No participants
        # -----------------------------------------

        if not participants:
            return {
                "status": "no_participants",
                "match": None,
                "score": 0.0,
                "confidence_level": "none",
                "second_best_score": 0.0,
                "margin": 0.0,
            }

        # -----------------------------------------
        # Calculate similarity scores
        # -----------------------------------------

        scored_participants = []

        for participant in participants:

            participant_name = self.normalize(
                participant["name"]
            )

            score = fuzz.ratio(
                extracted,
                participant_name
            )

            scored_participants.append(
                {
                    "participant": participant,
                    "score": score,
                }
            )

        # -----------------------------------------
        # Sort highest → lowest
        # -----------------------------------------

        scored_participants.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        best = scored_participants[0]

        best_match = best["participant"]
        best_score = best["score"]

        # -----------------------------------------
        # Second-best score
        # -----------------------------------------

        if len(scored_participants) > 1:
            second_best_score = scored_participants[1]["score"]
        else:
            second_best_score = 0.0

        margin = best_score - second_best_score

        # -----------------------------------------
        # Determine confidence
        # -----------------------------------------

        if best_score >= self.high_confidence_threshold:

            if margin >= self.minimum_margin:
                confidence_level = "high"
                status = "matched"

            else:
                confidence_level = "review"
                status = "review_required"

        elif best_score >= self.review_threshold:

            confidence_level = "medium"
            status = "review_required"

        else:

            confidence_level = "low"
            status = "no_match"

        # -----------------------------------------
        # Return result
        # -----------------------------------------

        return {
            "status": status,
            "match": (
                best_match
                if status in ["matched", "review_required"]
                else None
            ),
            "score": round(best_score, 2),
            "confidence_level": confidence_level,
            "second_best_score": round(second_best_score, 2),
            "margin": round(margin, 2),
        }