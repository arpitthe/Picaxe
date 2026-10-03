from app.matching.name_matcher import NameMatcher


matcher = NameMatcher(threshold=85)


print("\n========== EDGE CASE TESTS ==========\n")


# Test 1: No participants
print("TEST 1: No participants")

result = matcher.match(
    "DAKSH CHAUDHARY",
    []
)

print(result)

assert result["status"] == "no_participants"


# Test 2: No extracted name
print("\nTEST 2: No extracted name")

participants = [
    {"id": "P001", "name": "Daksh Chaudhary"},
    {"id": "P002", "name": "Rahul Sharma"},
]

result = matcher.match(
    None,
    participants
)

print(result)

assert result["status"] == "no_name"


print("\n====================================")
print("ALL EDGE CASE TESTS PASSED")
print("====================================\n")