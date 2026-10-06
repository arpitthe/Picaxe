from app.nlp.candidate_scorer import CandidateScorer


scorer = CandidateScorer()


candidates = [
    {
        "name": "DAKSH CHAUDHARY",
        "ocr_confidence": 0.99996,
        "recipient_context": True,
        "is_person": False,
    },
    {
        "name": "Michelle Jrg",
        "ocr_confidence": 0.8736,
        "recipient_context": False,
        "is_person": True,
    },
    {
        "name": "Michelle Vaz",
        "ocr_confidence": 0.99997,
        "recipient_context": False,
        "is_person": False,
    },
]


print("\n========== CANDIDATE SCORES ==========\n")


results = []

for candidate in candidates:

    result = scorer.score_candidate(
        candidate=candidate["name"],
        ocr_confidence=candidate["ocr_confidence"],
        recipient_context=candidate["recipient_context"],
        is_person=candidate["is_person"],
    )

    results.append(result)

    print(f"Name   : {result['name']}")
    print(f"Score  : {result['score']}")
    print(f"Reasons: {', '.join(result['reasons'])}")
    print("-" * 50)


print("\n======================================")