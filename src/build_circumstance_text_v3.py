"""Create a conservative DX-aware incident-text representation.

The script preserves the full source narrative and never deletes source rows.
It recognizes standalone and common fused DX separators, extracts text before
only the first marker, and flags records where parsing may need human review.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

# Standalone markers such as " DX:", " DX " or "DX;".
STANDALONE_DX = re.compile(r"(?i)\bDX\b")
# Fused suffixes such as "HOMEDX:", "PAINDX FRACTURE", "RIBDX LEFT RIB...".
FUSED_DX_WITH_BOUNDARY = re.compile(
    r"(?i)(?<=[A-Z0-9])DX(?=\s|[:;.,\-–—/]|$)"
)
# A small, explicitly documented set of fused markers with no separator before
# the diagnosis word (for example SOBDXFRACTURE). These remain review flags.
FUSED_DX_WITH_KNOWN_DIAGNOSIS = re.compile(
    r"(?i)(?<=[A-Z0-9])DX(?="
    r"FRACTURE|CONTUSION|LACERATION)"
)
# DX followed immediately by a diagnosis term at the start of a narrative.
LEADING_DX_WITH_KNOWN_DIAGNOSIS = re.compile(
    r"(?i)(?<![A-Z0-9])DX(?="
    r"OPEN|CLOSED|FRACTURE|CONTUSION|LACERATION)"
)
ANY_DX_SUBSTRING = re.compile(r"(?i)DX")


def marker_matches(text: str) -> list[tuple[int, int, str]]:
    """Return unique DX marker spans and their conservative style labels."""
    found: dict[tuple[int, int], str] = {}
    for pattern, style in (
        (STANDALONE_DX, "standalone"),
        (FUSED_DX_WITH_BOUNDARY, "fused_suffix_boundary"),
        (FUSED_DX_WITH_KNOWN_DIAGNOSIS, "fused_suffix_known_diagnosis"),
        (LEADING_DX_WITH_KNOWN_DIAGNOSIS, "leading_dx_known_diagnosis"),
    ):
        for match in pattern.finditer(text):
            span = (match.start(), match.end())
            # Prefer the most specific fused style when patterns overlap.
            if span not in found or style != "standalone":
                found[span] = style
    return [(start, end, style) for (start, end), style in sorted(found.items())]


def transform_one(value: object) -> dict[str, object]:
    text = "" if pd.isna(value) else str(value)
    matches = marker_matches(text)
    if not matches:
        suspect = bool(ANY_DX_SUBSTRING.search(text))
        return {
            "circumstance_text_raw": text,
            "diagnosis_suffix_raw": "",
            "circumstance_extraction_method": (
                "full_narrative_unparsed_dx_suspect" if suspect else "full_narrative_no_dx"
            ),
            "dx_marker_count": 0,
            "dx_marker_styles": "",
            "dx_multiple_marker_review": False,
            "dx_unparsed_suspect_review": suspect,
            "dx_empty_prefix_review": False,
        }

    first_start, first_end, _ = matches[0]
    prefix = text[:first_start].strip()
    suffix = text[first_end:].strip()
    # Some NEISS narratives start with age/sex then DX, followed by the event
    # narrative (e.g. "87YOF DX OPEN FX ... FALL AFTER ..."). In those cases
    # the first DX is not a safe split for circumstance text. Keep the entire
    # narrative and explicitly flag it for review rather than reducing it to age.
    prefix_has_meaningful_text = bool(clean_text(prefix))
    if not prefix_has_meaningful_text:
        event_text = text
        method = "full_narrative_leading_dx_review"
        empty_prefix = True
    else:
        event_text = prefix
        method = "split_at_first_dx"
        empty_prefix = False

    styles = sorted({style for _, _, style in matches})
    return {
        "circumstance_text_raw": event_text,
        "diagnosis_suffix_raw": suffix,
        "circumstance_extraction_method": method,
        "dx_marker_count": len(matches),
        "dx_marker_styles": ";".join(styles),
        "dx_multiple_marker_review": len(matches) > 1,
        "dx_unparsed_suspect_review": False,
        "dx_empty_prefix_review": empty_prefix,
    }


def clean_text(value: object) -> str:
    """Normalize narrative tokens and remove demographic/header boilerplate."""
    if pd.isna(value):
        return ""
    text = str(value).lower()
    # Age/sex strings are also represented in structured Age/Sex columns.
    text = re.sub(r"\b\d{1,3}\s*y\s*o?\s*[mf]\b", " ", text)
    text = re.sub(r"\b(?:yom|yof|yo\s*[mf])\b", " ", text)
    text = re.sub(r"[^a-z0-9\s'-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input candidate CSV")
    parser.add_argument("--output", required=True, help="Output CSV (new path)")
    parser.add_argument("--audit", required=True, help="Output JSON audit (new path)")
    parser.add_argument("--text-column", default="Narrative_1")
    args = parser.parse_args()

    input_path, output_path, audit_path = map(Path, (args.input, args.output, args.audit))
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    if output_path.exists() or audit_path.exists():
        raise FileExistsError("Refusing to overwrite an existing output or audit.")

    df = pd.read_csv(input_path, low_memory=False)
    if args.text_column not in df.columns:
        raise ValueError(f"Missing narrative column {args.text_column!r}")

    records = [transform_one(value) for value in df[args.text_column]]
    derived = pd.DataFrame(records, index=df.index)
    derived["circumstance_text_clean"] = derived["circumstance_text_raw"].map(clean_text)
    result = pd.concat([df.copy(), derived], axis=1)

    if len(result) != len(df):
        raise AssertionError("Row count changed during transformation.")
    if result["CPSC_Case_Number"].astype(str).equals(df["CPSC_Case_Number"].astype(str)) is False:
        raise AssertionError("Case IDs changed during transformation.")

    style_counts = Counter()
    for value in derived["dx_marker_styles"].fillna(""):
        for style in filter(None, value.split(";")):
            style_counts[style] += 1

    audit = {
        "input_file": str(input_path),
        "output_file": str(output_path),
        "rows_input": int(len(df)),
        "rows_output": int(len(result)),
        "rows_with_dx_marker": int((derived["dx_marker_count"] > 0).sum()),
        "rows_without_recognized_dx_marker": int((derived["dx_marker_count"] == 0).sum()),
        "marker_occurrences": int(derived["dx_marker_count"].sum()),
        "marker_style_counts_non_exclusive": dict(style_counts),
        "multiple_dx_marker_review_rows": int(derived["dx_multiple_marker_review"].sum()),
        "unparsed_dx_suspect_rows": int(derived["dx_unparsed_suspect_review"].sum()),
        "empty_prefix_review_rows": int(derived["dx_empty_prefix_review"].sum()),
        "empty_cleaned_circumstance_rows": int(derived["circumstance_text_clean"].eq("").sum()),
        "extraction_method_counts": {
            str(k): int(v) for k, v in derived["circumstance_extraction_method"].value_counts().items()
        },
        "warning": (
            "Experimental text representation, not an authoritative clinical parser. "
            "The original narrative is preserved. First DX marker is used as the split. "
            "Multiple markers, leading-DX cases and unparsed DX substrings are flagged. "
            "No-DX records retain their full narrative, which may still contain diagnoses."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))
    print("\nCIRCUMSTANCE TEXT V3 COMPLETE")


if __name__ == "__main__":
    main()
