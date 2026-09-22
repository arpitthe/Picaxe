from paddleocr import PaddleOCR


class CertificateOCR:
    """
    OCR engine for extracting text from certificates using PaddleOCR.
    """

    def __init__(self):
        print("Initializing PaddleOCR...")

        self.ocr = PaddleOCR(
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

        print("PaddleOCR initialized successfully.")

    def extract_text(self, image_path: str):
        """
        Extract text, confidence and bounding boxes from an image.

        Returns:
            list[dict]: OCR detections
        """

        results = self.ocr.predict(image_path)

        extracted = []

        for result in results:

            # PaddleOCR 3.x result structure
            data = result.json

            if isinstance(data, str):
                import json
                data = json.loads(data)

            # Important: actual OCR data is inside "res"
            data = data.get("res", data)

            texts = data.get("rec_texts", [])
            scores = data.get("rec_scores", [])
            boxes = data.get("rec_boxes", [])

            for text, score, box in zip(texts, scores, boxes):

                extracted.append({
                    "text": text,
                    "confidence": float(score),
                    "box": box.tolist()
                    if hasattr(box, "tolist")
                    else box,
                })

        return extracted


if __name__ == "__main__":

    ocr = CertificateOCR()

    image_path = "samples/certificates/certificate1.jpg"

    results = ocr.extract_text(image_path)

    print("\n========== OCR RESULT ==========\n")

    if not results:
        print("No text detected.")

    for item in results:

        print(f"Text       : {item['text']}")
        print(f"Confidence : {item['confidence']:.4f}")
        print(f"Box        : {item['box']}")
        print("-" * 60)

    print("\n================================")