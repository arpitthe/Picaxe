from app.nlp.name_extractor import NameExtractor


def test_same_line_recipient():
    extractor = NameExtractor()

    detections = [
        {
            "text": "Certificate awarded to John Doe",
            "confidence": 0.98,
            "box": [0, 0, 500, 50],
        }
    ]

    candidates = extractor.extract_candidates(detections)

    assert candidates
    assert candidates[0]["name"] == "JOHN DOE"


def test_split_recipient_across_detections():
    extractor = NameExtractor()

    detections = [
        {
            "text": "Awarded",
            "confidence": 0.98,
            "box": [0, 0, 200, 40],
        },
        {
            "text": "to",
            "confidence": 0.97,
            "box": [0, 50, 100, 90],
        },
        {
            "text": "John Doe",
            "confidence": 0.96,
            "box": [0, 100, 250, 150],
        },
    ]

    candidates = extractor.extract_candidates(detections)

    assert candidates
    assert candidates[0]["name"] == "JOHN DOE"


def test_recipient_below_anchor_using_spatial_position():
    extractor = NameExtractor()

    detections = [
        {
            "text": "Awarded to",
            "confidence": 0.98,
            "box": [100, 100, 300, 140],
        },
        {
            "text": "John Doe",
            "confidence": 0.97,
            "box": [110, 180, 300, 220],
        },
    ]

    candidates = extractor.extract_candidates(detections)

    assert candidates
    assert candidates[0]["name"] == "JOHN DOE"


def test_multiple_person_names_prefers_recipient():
    extractor = NameExtractor()

    detections = [
        {
            "text": "Presented to John Doe",
            "confidence": 0.98,
            "box": [0, 0, 300, 50],
        },
        {
            "text": "Signed by Jane Smith",
            "confidence": 0.96,
            "box": [0, 100, 300, 150],
        },
    ]

    candidates = extractor.extract_candidates(detections)

    assert candidates
    assert candidates[0]["name"] == "JOHN DOE"


def test_duplicate_recipient_anchors_are_deduplicated():
    extractor = NameExtractor()

    detections = [
        {
            "text": "Awarded to John Doe",
            "confidence": 0.98,
            "box": [0, 0, 300, 50],
        },
        {
            "text": "Presented to John Doe",
            "confidence": 0.97,
            "box": [0, 100, 300, 150],
        },
    ]

    candidates = extractor.extract_candidates(detections)

    assert len(candidates) == 1
    assert candidates[0]["name"] == "JOHN DOE"


def test_name_with_hyphen_and_apostrophe():
    extractor = NameExtractor()

    detections = [
        {
            "text": "Awarded to Mary-Anne O'Connor",
            "confidence": 0.98,
            "box": [0, 0, 400, 50],
        }
    ]

    candidates = extractor.extract_candidates(detections)

    assert candidates
    assert candidates[0]["name"] == "MARY-ANNE O'CONNOR"


def test_low_ocr_confidence_is_preserved():
    extractor = NameExtractor()

    detections = [
        {
            "text": "Awarded to John Doe",
            "confidence": 0.42,
            "box": [0, 0, 300, 50],
        }
    ]

    candidates = extractor.extract_candidates(detections)

    assert candidates
    assert candidates[0]["name"] == "JOHN DOE"
    assert candidates[0]["ocr_confidence"] == 0.42


def test_no_recipient_returns_no_candidates():
    extractor = NameExtractor()

    detections = [
        {
            "text": "Certificate of Completion",
            "confidence": 0.98,
            "box": [0, 0, 300, 50],
        },
        {
            "text": "Machine Learning Fundamentals",
            "confidence": 0.97,
            "box": [0, 100, 400, 150],
        },
    ]

    candidates = extractor.extract_candidates(detections)

    assert candidates == []


def test_extract_candidates_from_plain_text():
    extractor = NameExtractor()

    text = (
        "This certificate is awarded to "
        "John Doe for successfully completing the course."
    )

    candidates = extractor.extract_candidates_from_text(text)

    assert candidates
    assert candidates[0]["name"] == "JOHN DOE"