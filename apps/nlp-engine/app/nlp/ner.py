import spacy


class NameNER:
    """
    spaCy-based Named Entity Recognition.

    Finds PERSON entities from OCR text.
    """

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def extract_persons(self, text: str):
        """
        Extract PERSON entities from text.

        Returns:
            list of dictionaries containing:
            - name
            - confidence
            - label
        """

        if not text:
            return []

        doc = self.nlp(text)

        persons = []

        for entity in doc.ents:

            if entity.label_ == "PERSON":

                persons.append({
                    "name": entity.text,
                    "label": entity.label_,
                })

        return persons


if __name__ == "__main__":

    ner = NameNER()

    text = """
    AWS Training & Certification
    Completion Certificate
    Fundamentals of Machine Learning and Artificial Intelligence
    Completed: March 27, 2026
    Awarded to
    DAKSH CHAUDHARY
    Michelle Jrg
    Michelle Vaz
    Director, AWS Training & Certification
    """

    persons = ner.extract_persons(text)

    print("\n========== SPACY NER RESULT ==========\n")

    for person in persons:
        print(f"Name  : {person['name']}")
        print(f"Label : {person['label']}")
        print("-" * 40)

    print("\n======================================")