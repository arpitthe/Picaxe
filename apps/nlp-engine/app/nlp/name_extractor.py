import re

from app.nlp.text_normalizer import normalize_name


class NameExtractor:
    """
    Extract possible certificate recipients from OCR detections.
    """

    RECIPIENT_ANCHORS = [
        "awarded to",
        "presented to",
        "certificate is awarded to",
        "certificate awarded to",
        "this certificate is presented to",
        "proudly presented to",
        "given to",
        "completed by",
        "successfully completed by",
    ]

    def extract_candidates(self, detections):
        """
        Find possible recipient names.

        Returns:
            list of candidate dictionaries.
        """

        candidates = []

        for index, detection in enumerate(detections):

            text = detection["text"].strip()

            if not text:
                continue

            normalized_text = text.lower()

            # -----------------------------------------
            # Look for recipient anchor
            # -----------------------------------------

            for anchor in self.RECIPIENT_ANCHORS:

                if anchor in normalized_text:

                    # Look at the next OCR detection
                    if index + 1 < len(detections):

                        next_detection = detections[index + 1]

                        candidate_name = self._validate_candidate(
                            next_detection["text"]
                        )

                        if candidate_name:

                            candidates.append({
                                "name": candidate_name,
                                "ocr_confidence": next_detection["confidence"],
                                "recipient_context": True,
                                "detection_index": index + 1,
                            })

        return candidates

    def _validate_candidate(self, text: str):

        text = text.strip()

        if not text:
            return None

        if len(text) > 80:
            return None

        lower = text.lower()

        rejected_words = [
            "certificate",
            "director",
            "training",
            "completion",
            "completed",
            "machine",
            "learning",
            "artificial",
            "intelligence",
            "presented",
            "awarded",
            "aws",
        ]

        if any(word in lower for word in rejected_words):
            return None

        if not re.search(r"[A-Za-z]", text):
            return None

        words = text.split()

        if not 1 <= len(words) <= 5:
            return None

        if any(len(word) > 30 for word in words):
            return None

        return normalize_name(text)