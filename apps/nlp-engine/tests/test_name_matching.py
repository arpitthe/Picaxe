from app.matching.name_matcher import NameMatcher


participants = [
    {"id": "P001", "name": "Daksh Chaudhary"},
    {"id": "P002", "name": "Rahul Sharma"},
    {"id": "P003", "name": "Ananya Singh"},
    {"id": "P004", "name": "Aditya Kumar"},
    {"id": "P005", "name": "Priya Patel"},
]


matcher = NameMatcher(threshold=85)


test_names = [
    "DAKSH CHAUDHARY",    # Perfect OCR
    "DAKSH CHAUDHARV",    # One character wrong
    "DAKSH CHAUDHARYY",   # Extra character
    "DAKSH  CHAUDHARY",   # Extra space
    "DAKSH CHAUDHARI",    # One character wrong
    "DAKS CHAUDHARY",     # Missing character
    "RAHUL SHARMA",       # Different participant
    "UNKNOWN PERSON",     # No participant
]


print("\n========== FUZZY NAME MATCHING ==========\n")


for extracted_name in test_names:

    result = matcher.match(
        extracted_name,
        participants
    )

    print(f"Extracted : {extracted_name}")
    print(f"Status    : {result['status']}")
    print(f"Score     : {result['score']}")
    print(f"Confidence: {result['confidence_level']}")
    print(f"2nd best  : {result['second_best_score']}")
    print(f"Margin    : {result['margin']}")

    if result["match"]:
        print(f"Matched   : {result['match']['name']}")
        print(f"ID        : {result['match']['id']}")

    print("-" * 50)


# ============================================================
# AMBIGUOUS NAME TEST
# ============================================================

print("\n========== AMBIGUOUS NAME TEST ==========\n")


ambiguous_participants = [
    {"id": "P001", "name": "Daksh Chaudhary"},
    {"id": "P006", "name": "Daksh Chaudharyy"},
]


ambiguous_name = "DAKSH CHAUDHARY"


result = matcher.match(
    ambiguous_name,
    ambiguous_participants
)


print(f"Extracted : {ambiguous_name}")
print(f"Status    : {result['status']}")
print(f"Score     : {result['score']}")
print(f"Confidence: {result['confidence_level']}")
print(f"2nd best  : {result['second_best_score']}")
print(f"Margin    : {result['margin']}")

if result["match"]:
    print(f"Best Match: {result['match']['name']}")
    print(f"ID        : {result['match']['id']}")

print("-" * 50)


print("\n==========================================")