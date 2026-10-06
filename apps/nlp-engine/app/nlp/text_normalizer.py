import re


def normalize_text(text: str) -> str:
    """
    Normalize OCR text while preserving useful name information.
    """

    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def normalize_name(name: str) -> str:
    """
    Normalize a person's name for later matching.
    """

    if not name:
        return ""

    # Convert to uppercase
    name = name.upper()

    # Remove unwanted characters
    name = re.sub(r"[^A-Z\s'-]", "", name)

    # Normalize whitespace
    name = re.sub(r"\s+", " ", name)

    return name.strip()