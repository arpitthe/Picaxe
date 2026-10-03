import re

from app.nlp.text_normalizer import normalize_name


class NameExtractor:
    RECIPIENT_ANCHORS = [
        "this certificate is presented to",
        "this certificate is awarded to",
        "certificate is awarded to",
        "certificate awarded to",
        "successfully completed by",
        "completed by",
        "proudly presented to",
        "presented to",
        "awarded to",
        "given to",
    ]

    def extract_candidates(self, detections):
        """
        Extract recipient candidates from OCR detections.

        Handles:
        - "Awarded to John Doe"
        - "Awarded to" -> "John Doe"
        - "Awarded" -> "to" -> "John Doe"
        - OCR layouts where the recipient is spatially below the anchor
        """

        candidates = []

        for index, detection in enumerate(detections):
            text = detection.get("text", "").strip()

            if not text:
                continue

            normalized_text = text.lower()

            # Prefer longer anchors so overlapping phrases
            # do not generate duplicate candidates.
            for anchor in sorted(
                self.RECIPIENT_ANCHORS,
                key=len,
                reverse=True,
            ):
                # Case 1: anchor and recipient are on the same OCR line.
                candidate_text = self._extract_after_anchor(
                    text,
                    anchor,
                )

                if candidate_text:
                    candidate_name = self._validate_candidate(
                        candidate_text
                    )

                    if candidate_name:
                        candidates.append(
                            self._build_candidate(
                                candidate_name,
                                detection.get("confidence", 0.0),
                                index,
                            )
                        )

                    break

                # Case 2: anchor is split across OCR detections.
                split_result = self._extract_split_anchor_candidate(
                    detections,
                    index,
                    anchor,
                )

                if split_result:
                    candidate_text, candidate_index = split_result

                    candidate_name = self._validate_candidate(
                        candidate_text
                    )

                    if candidate_name:
                        candidates.append(
                            self._build_candidate(
                                candidate_name,
                                detections[candidate_index].get(
                                    "confidence",
                                    0.0,
                                ),
                                candidate_index,
                            )
                        )

                    break

                # Case 3: anchor exists as its own OCR region and
                # recipient is spatially nearby.
                if anchor in normalized_text:
                    spatial_candidate = self._find_spatial_candidate(
                        detections,
                        index,
                    )

                    if spatial_candidate:
                        candidate_text, candidate_index = (
                            spatial_candidate
                        )

                        candidate_name = self._validate_candidate(
                            candidate_text
                        )

                        if candidate_name:
                            candidates.append(
                                self._build_candidate(
                                    candidate_name,
                                    detections[candidate_index].get(
                                        "confidence",
                                        0.0,
                                    ),
                                    candidate_index,
                                )
                            )

                    break

        return self._deduplicate_candidates(candidates)

    def extract_candidates_from_text(self, text):
        """
        Extract recipient candidates from plain OCR text.

        Used by /certificate/extract-name where bounding boxes
        are not available.
        """

        if not text:
            return []

        candidates = []

        # Common phrases that indicate the recipient name ends.
        stop_phrases = [
            " for ",
            " on ",
            " in ",
            " with ",
            " successfully ",
            " having ",
            " who ",
        ]

        for anchor in sorted(
            self.RECIPIENT_ANCHORS,
            key=len,
            reverse=True,
        ):
            pattern = re.compile(
                rf"{re.escape(anchor)}\s*[:\-]?\s*"
                r"([A-Za-z][A-Za-z\s.'-]{1,79})",
                re.IGNORECASE,
            )

            match = pattern.search(text)

            if not match:
                continue

            candidate_text = match.group(1).strip()

            # Stop the candidate at common trailing certificate text.
            lower_candidate = candidate_text.lower()

            stop_position = len(candidate_text)

            for phrase in stop_phrases:
                position = lower_candidate.find(phrase)

                if position != -1:
                    stop_position = min(
                        stop_position,
                        position,
                    )

            candidate_text = candidate_text[:stop_position].strip()

            candidate_name = self._validate_candidate(
                candidate_text
            )

            if candidate_name:
                candidates.append(
                    {
                        "name": candidate_name,
                        "ocr_confidence": 1.0,
                        "recipient_context": True,
                        "detection_index": None,
                    }
                )

            break

        return self._deduplicate_candidates(candidates)

    def _extract_after_anchor(self, text, anchor):
        pattern = re.compile(
            rf"{re.escape(anchor)}\s*[:\-]?\s*"
            r"(.+)$",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if not match:
            return None

        return match.group(1).strip()

    def _extract_split_anchor_candidate(
        self,
        detections,
        start_index,
        anchor,
    ):
        """
        Look across the current and next few OCR detections for
        anchors such as:

            Awarded
            to
            John Doe
        """

        anchor_words = anchor.lower().split()

        max_window = min(
            len(detections),
            start_index + len(anchor_words) + 2,
        )

        for end_index in range(
            start_index + 1,
            max_window,
        ):
            combined = " ".join(
                detection.get("text", "").strip()
                for detection in detections[
                    start_index:end_index + 1
                ]
            )

            normalized = combined.lower()

            anchor_position = normalized.find(
                anchor.lower()
            )

            if anchor_position == -1:
                continue

            candidate_text = combined[
                anchor_position + len(anchor):
            ].strip(" :-")

            if candidate_text:
                return candidate_text, end_index

        return None

    def _find_spatial_candidate(
        self,
        detections,
        anchor_index,
    ):
        anchor_box = detections[anchor_index].get("box")

        if not anchor_box:
            return None

        anchor_center_x, anchor_center_y = (
            self._box_center(anchor_box)
        )

        candidates = []

        for index, detection in enumerate(detections):
            if index == anchor_index:
                continue

            text = detection.get("text", "").strip()
            box = detection.get("box")

            if not text or not box:
                continue

            center_x, center_y = self._box_center(box)

            vertical_distance = center_y - anchor_center_y
            horizontal_distance = abs(
                center_x - anchor_center_x
            )

            if vertical_distance < 0:
                continue

            if vertical_distance > 500:
                continue

            candidates.append(
                (
                    vertical_distance
                    + horizontal_distance * 0.25,
                    index,
                    text,
                )
            )

        candidates.sort(key=lambda item: item[0])

        for _, index, text in candidates:
            if self._validate_candidate(text):
                return text, index

        return None

    @staticmethod
    def _box_center(box):
        """
        Supports PaddleOCR boxes represented as:
        [x1, y1, x2, y2]
        """

        x1, y1, x2, y2 = box[:4]

        return (
            (float(x1) + float(x2)) / 2,
            (float(y1) + float(y2)) / 2,
        )

    @staticmethod
    def _build_candidate(
        name,
        ocr_confidence,
        detection_index,
    ):
        return {
            "name": name,
            "ocr_confidence": float(ocr_confidence),
            "recipient_context": True,
            "detection_index": detection_index,
        }

    def _deduplicate_candidates(self, candidates):
        unique = {}

        for candidate in candidates:
            key = normalize_name(candidate["name"])

            if key not in unique:
                unique[key] = candidate

        return list(unique.values())

    def _validate_candidate(self, text):
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
            "this",
            "for",
            "successfully",
        ]

        if any(
            word in lower
            for word in rejected_words
        ):
            return None

        if not re.search(r"[A-Za-z]", text):
            return None

        words = text.split()

        if not 1 <= len(words) <= 5:
            return None

        if any(
            len(word) > 30
            for word in words
        ):
            return None

        return normalize_name(text)