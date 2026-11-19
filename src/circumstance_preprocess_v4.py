import math
import re


def circumstance_text(value):
    """
    Clean medical narratives while preserving fall circumstances.
    Original narratives must remain unchanged in the source dataset.
    """

    if value is None:
        return ""

    if isinstance(value, float) and math.isnan(value):
        return ""

    text = str(value).lower()
    text = text.replace("\n", " ")

    # 1. Remove demographic shorthand.
    text = re.sub(
        r"\b\d{1,3}\s*(?:yom|yof|yo\s*[mf]?|y\s*/\s*[omf])\b",
        " ",
        text
    )

    text = re.sub(
        r"\b\d{1,3}\s*[- ]?year[- ]old\b",
        " ",
        text
    )

    # 2. Remove an explicitly marked appended diagnosis section.
    # Preserve potentially relevant mechanisms and triggers.
    diagnosis_match = re.search(
        r"\b(?:dx|diagnosis)\b\s*[:\-]?\s*",
        text
    )

    if diagnosis_match:
        narrative_part = text[:diagnosis_match.start()].strip()
        diagnosis_tail = text[diagnosis_match.end():]

        mechanism_pattern = (
            r"\b(?:fall(?:ing|en|s)?|fell|"
            r"slip(?:ped|ping|s)?|"
            r"trip(?:ped|ping|s)?|"
            r"stumble(?:d|s|s)?|"
            r"syncope|dizziness|dizzy|vertigo|"
            r"seizure|weakness|loss of balance|"
            r"lost balance|passed out)\b"
        )

        mechanism_terms = re.findall(
            mechanism_pattern,
            diagnosis_tail
        )

        if narrative_part:
            text = " ".join([narrative_part, *mechanism_terms])
        else:
            text = " ".join(mechanism_terms) or diagnosis_tail

    # 3. Normalize common medical-report abbreviations.
    text = re.sub(r"\bc\s*/\s*o\b", "complains of", text)
    text = re.sub(r"\bw\s*/\s*o\b", "without", text)
    text = re.sub(r"\bw\s*/\s*", "with ", text)
    text = re.sub(r"\bs\s*/\s*p\b", "after", text)

    # 4. Normalize left/right shorthand.
    text = re.sub(r"\blt\b", "left", text)
    text = re.sub(r"\brt\b", "right", text)

    body_parts = (
        r"(?:side|arm|leg|hand|foot|hip|knee|shoulder|wrist|"
        r"ankle|elbow|chest|rib|face|head)"
    )

    text = re.sub(
        rf"\bl[.\s]+(?={body_parts}\b)",
        "left ",
        text
    )

    text = re.sub(
        rf"\br[.\s]+(?={body_parts}\b)",
        "right ",
        text
    )

    # 5. Normalize nursing-home abbreviations.
    text = re.sub(
        r"\bn\.?\s*h\.?\b",
        "nursing home",
        text
    )

    # 6. Remove reporting boilerplate.
    text = re.sub(
        r"\b(?:patient|pt|states|reports|reported|says)\b",
        " ",
        text
    )

    # 7. Normalize circumstance verbs.
    replacements = {
        r"\b(?:fell|falling|fallen|falls)\b": "fall",
        r"\b(?:slipped|slipping|slips)\b": "slip",
        r"\b(?:tripped|tripping|trips)\b": "trip",
        r"\b(?:stumbled|stumbling|stumbles)\b": "stumble",
        r"\b(?:struck|striking|hitting|hits)\b": "hit"
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    # 8. Clean punctuation and whitespace.
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text
