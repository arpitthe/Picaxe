from app.ocr.ocr_engine import CertificateOCR
from app.nlp.name_extractor import NameExtractor


image_path = "samples/certificates/certificate1.jpg"


print("\n========== CANDIDATE GENERATION ==========\n")


# OCR
ocr = CertificateOCR()
detections = ocr.extract_text(image_path)

print(f"OCR detections: {len(detections)}")


# Candidate extraction
extractor = NameExtractor()

candidates = extractor.extract_candidates(detections)


for candidate in candidates:

    print(f"Name              : {candidate['name']}")
    print(f"OCR confidence    : {candidate['ocr_confidence']:.4f}")
    print(f"Recipient context : {candidate['recipient_context']}")
    print(f"Detection index   : {candidate['detection_index']}")

    print("-" * 50)


print("\n===========================================")