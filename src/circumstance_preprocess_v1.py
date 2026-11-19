import re

REMOVE_TERMS = {
    "patient", "pt", "dx", "fx", "inj", "lac",
    "injury", "injuries", "fracture", "fractures",
    "contusion", "contusions", "abrasion", "abrasions",
    "laceration", "lacerations", "hematoma", "hematomas",
    "pain", "sustained", "admitted", "diagnosis",
    "diagnosed", "closed", "yo", "yom", "yof"
}


def circumstance_text(value):
    """Reduce demographic and injury-documentation noise while retaining fall circumstances."""
    if value is None:
        return ""

    text = str(value).lower()

    # Remove age and sex shorthand, e.g. 81YOM and 87YOF.
    text = re.sub(r"\b\d{1,3}\s*(?:yom|yof)\b", " ", text)

    # Remove common medical-reporting abbreviations.
    text = re.sub(
        r"(?<![a-z0-9])(?:c/o|s/p|w/o|w/|n/s)(?![a-z0-9])",
        " ", text
    )

    # Remove medical outcome and documentation terms.
    for term in REMOVE_TERMS:
        text = re.sub(rf"\b{re.escape(term)}\b", " ", text)

    # Normalize common circumstance verbs.
    text = re.sub(r"\b(?:fell|falling)\b", "fall", text)
    text = re.sub(r"\b(?:slipped|slipping)\b", "slip", text)
    text = re.sub(r"\b(?:tripped|tripping)\b", "trip", text)
    text = re.sub(r"\b(?:stumbled|stumbling)\b", "stumble", text)

    # Normalize punctuation and whitespace.
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text
