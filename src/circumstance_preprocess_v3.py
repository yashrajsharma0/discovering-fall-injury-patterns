import re

REMOVE_TERMS = {
    "patient", "pt", "dx", "fx", "inj", "lac", "cont", "loc",
    "injury", "injuries", "fracture", "fractures",
    "contusion", "contusions", "abrasion", "abrasions",
    "laceration", "lacerations", "hematoma", "hematomas",
    "pain", "sustained", "admitted", "diagnosis", "diagnosed",
    "traumatic", "concussion", "concussions", "ecchymosis",
    "sprain", "strain", "rhabdomyolysis", "uti",
    "anemia", "afib", "hemorrhage", "hemorrhagic"
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

    # Remove specific consciousness documentation phrases.
    text = re.sub(
        r"\b(?:no\s+loc|no\s+loss\s+of\s+consciousness|without\s+loss\s+of\s+consciousness)\b",
        " ", text
    )

    # Expand left/right shorthand instead of deleting it.
    text = re.sub(r"\blt\b", "left", text)
    text = re.sub(r"\brt\b", "right", text)

    # Remove injury and diagnosis terminology.
    for term in sorted(REMOVE_TERMS, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(term)}\b", " ", text)

    # Normalize fall-related verbs.
    replacements = {
        r"\b(?:fell|falling)\b": "fall",
        r"\b(?:slipped|slipping)\b": "slip",
        r"\b(?:tripped|tripping)\b": "trip",
        r"\b(?:stumbled|stumbling)\b": "stumble",
        r"\b(?:struck|striking|hitting)\b": "hit"
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    # Preserve body parts, mobility aids and environmental objects.
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text
