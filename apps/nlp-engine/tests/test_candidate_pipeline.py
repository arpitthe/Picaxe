from app.ocr.ocr_engine import CertificateOCR
from app.nlp.candidate_pipeline import CandidatePipeline


IMAGE_PATH = "samples/certificates/certificate1.jpg"


print("\n==========================================")
print("       PICAXE NLP CANDIDATE PIPELINE")
print("==========================================\n")


# -----------------------------------------
# OCR
# -----------------------------------------

print("[1] Running OCR...")

ocr = CertificateOCR()

detections = ocr.extract_text(
    IMAGE_PATH
)

print(
    f"OCR detected {len(detections)} regions."
)


# -----------------------------------------
# NLP Pipeline
# -----------------------------------------

print("\n[2] Running NLP pipeline...")

pipeline = CandidatePipeline()

result = pipeline.process(
    detections
)


# -----------------------------------------
# Results
# -----------------------------------------

print("\n========== NLP RESULT ==========\n")

print(
    f"Selected name : {result['name']}"
)

print(
    f"Final score   : {result['score']}"
)

print("\nCandidates:\n")

for candidate in result["candidates"]:

    print(
        f"Name    : {candidate['name']}"
    )

    print(
        f"Score   : {candidate['score']}"
    )

    print(
        f"Reasons : "
        f"{', '.join(candidate['reasons'])}"
    )

    print("-" * 50)


print("\n================================")