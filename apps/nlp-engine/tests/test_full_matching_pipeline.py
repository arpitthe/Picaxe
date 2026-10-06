from app.ocr.ocr_engine import CertificateOCR
from app.nlp.candidate_pipeline import CandidatePipeline
from app.matching.name_matcher import NameMatcher


# -----------------------------------------
# 1. Participant database (temporary)
# -----------------------------------------

participants = [
    {"id": "P001", "name": "Daksh Chaudhary"},
    {"id": "P002", "name": "Rahul Sharma"},
    {"id": "P003", "name": "Ananya Singh"},
    {"id": "P004", "name": "Aditya Kumar"},
    {"id": "P005", "name": "Priya Patel"},
]


# -----------------------------------------
# 2. Certificate image
# -----------------------------------------

image_path = "samples/certificates/certificate2.png"


# -----------------------------------------
# 3. Initialize components
# -----------------------------------------

print("\nInitializing AI pipeline...\n")

ocr = CertificateOCR()
candidate_pipeline = CandidatePipeline()
matcher = NameMatcher(threshold=85)


# -----------------------------------------
# 4. OCR
# -----------------------------------------

print("\n========== STEP 1: OCR ==========\n")

detections = ocr.extract_text(image_path)

print(f"OCR detections: {len(detections)}")


# -----------------------------------------
# 5. Name extraction + scoring
# -----------------------------------------

print("\n========== STEP 2: NAME EXTRACTION ==========\n")

candidate_result = candidate_pipeline.process(detections)

extracted_name = candidate_result["name"]

print(f"Extracted name : {extracted_name}")
print(f"Candidate score: {candidate_result['score']}")


# -----------------------------------------
# 6. Participant matching
# -----------------------------------------

print("\n========== STEP 3: PARTICIPANT MATCHING ==========\n")

match_result = matcher.match(
    extracted_name,
    participants
)

print(f"Match status        : {match_result['status']}")
print(f"Match score         : {match_result['score']}")
print(f"Confidence level    : {match_result['confidence_level']}")
print(f"Second-best score   : {match_result['second_best_score']}")
print(f"Match margin        : {match_result['margin']}")
if match_result["match"]:

    participant = match_result["match"]

    final_result = {
        "status": match_result["status"],
        "extracted_name": extracted_name,
        "candidate_score": candidate_result["score"],
        "participant_id": participant["id"],
        "participant_name": participant["name"],
        "match_score": match_result["score"],
        "confidence_level": match_result["confidence_level"],
        "second_best_score": match_result["second_best_score"],
        "match_margin": match_result["margin"],
    }

else:

    final_result = {
        "status": match_result["status"],
        "extracted_name": extracted_name,
        "candidate_score": candidate_result["score"],
        "participant_id": None,
        "participant_name": None,
        "match_score": match_result["score"],
        "confidence_level": match_result["confidence_level"],
        "second_best_score": match_result["second_best_score"],
        "match_margin": match_result["margin"],
    }

# -----------------------------------------
# 7. Final structured result
# -----------------------------------------

print("\n========== FINAL RESULT ==========\n")

if match_result["match"]:

    participant = match_result["match"]

    final_result = {
        "status": match_result["status"],
        "extracted_name": extracted_name,
        "candidate_score": candidate_result["score"],
        "participant_id": participant["id"],
        "participant_name": participant["name"],
        "match_score": match_result["score"],
        "confidence_level": match_result["confidence_level"],
        "second_best_score": match_result["second_best_score"],
        "match_margin": match_result["margin"],
    }

else:

    final_result = {
        "status": match_result["status"],
        "extracted_name": extracted_name,
        "candidate_score": candidate_result["score"],
        "participant_id": None,
        "participant_name": None,
        "match_score": match_result["score"],
        "confidence_level": match_result["confidence_level"],
        "second_best_score": match_result["second_best_score"],
        "match_margin": match_result["margin"],
    }



print(final_result)

print("\n==================================")