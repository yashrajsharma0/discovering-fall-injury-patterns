import re

REMOVE_TERMS = {
    "patient", "pt", "dx", "fx", "inj", "lac", "cont",
    "lt", "rt", "loc", "yo", "yom", "yof",
    "injury", "injuries", "fracture", "fractures",
    "contusion", "contusions", "abrasion", "abrasions",
    "laceration", "lacerations", "hematoma", "hematomas",
    "concussion", "concussions", "ecchymosis",
    "pain", "sustained", "admitted", "diagnosis",
    "diagnosed", "closed", "traumatic", "consciousness",
    "sprain", "strain", "rhabdomyolysis", "uti",
    "anemia", "afib", "hemorrhage", "hemorrhagic"
}

BODY_TERMS = {
    "head", "forehead", "scalp", "face", "hip", "knee",
    "arm", "leg", "wrist", "shoulder", "ankle", "foot",
    "feet", "chest", "rib", "neck", "hand", "elbow"
}


def circumstance_text(value):
    if value is None:
        return ""

    text = str(value).lower()

    # Remove age and sex shorthand.
    text = re.sub(r"\b\d{1,3}\s*(?:yom|yof)\b", " ", text)

    # Remove common reporting abbreviations.
    text = re.sub(
        r"(?<![a-z0-9])(?:c/o|s/p|w/o|w/|n/s)(?![a-z0-9])",
        " ", text
    )

    # Remove medical and injury terminology.
    for term in sorted(REMOVE_TERMS, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(term)}\b", " ", text)

    # Remove anatomical descriptions, not environmental objects.
    for term in BODY_TERMS:
        text = re.sub(rf"\b{term}\b", " ", text)

    # Normalize circumstance verbs.
    replacements = {
        r"\b(?:fell|falling)\b": "fall",
        r"\b(?:slipped|slipping)\b": "slip",
        r"\b(?:tripped|tripping)\b": "trip",
        r"\b(?:stumbled|stumbling)\b": "stumble",
        r"\b(?:struck|striking|hitting)\b": "hit",
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text
