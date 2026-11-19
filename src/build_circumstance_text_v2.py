import sys
import re
import json
from pathlib import Path
from collections import Counter

import pandas as pd

sys.path.insert(0, "src")
from preprocess import clean_narrative

source = Path("data/experiment_sample_5000.csv")
output = Path("data/experiment_sample_5000_circumstance_v2.csv")
report_path = Path("results/circumstance_text_audit_v2.json")

if not source.exists():
    raise FileNotFoundError(source)

if output.exists() or report_path.exists():
    raise FileExistsError("V2 output already exists. Nothing overwritten.")

df = pd.read_csv(source, low_memory=False)

if "Narrative_1" not in df.columns:
    raise ValueError("Narrative_1 column missing.")

# Recognize DX followed by observed punctuation or whitespace.
pattern = re.compile(
    r"\bDX\b(?P<gap>\s*)(?P<punct>[:;.\-–—])?\s*",
    re.IGNORECASE
)

texts = df["Narrative_1"].fillna("").astype(str)
circumstances = []
methods = []
marker_counts = []
marker_styles = []
empty_prefix_count = 0

for text in texts:
    matches = list(pattern.finditer(text))
    marker_counts.append(len(matches))

    if not matches:
        circumstances.append(text)
        methods.append("full_narrative_no_DX")
        marker_styles.append("none")
        continue

    first = matches[0]
    prefix = text[:first.start()].strip()

    punctuation = first.group("punct")
    gap = first.group("gap")

    if punctuation:
        style = {
            ":": "colon",
            ";": "semicolon",
            ".": "period",
            "-": "hyphen",
            "–": "en_dash",
            "—": "em_dash"
        }.get(punctuation, "other")
    elif gap:
        style = "space"
    else:
        style = "token_only"

    marker_styles.append(style)

    if prefix:
        circumstances.append(prefix)
        methods.append("split_at_first_DX")
    else:
        circumstances.append(text)
        methods.append("fallback_empty_prefix")
        empty_prefix_count += 1

df["circumstance_text_raw"] = circumstances
df["circumstance_text_clean"] = [
    clean_narrative(x) for x in circumstances
]
df["circumstance_text_method"] = methods
df["dx_marker_count"] = marker_counts
df["dx_marker_style"] = marker_styles
df["dx_multiple_marker_review"] = [
    n > 1 for n in marker_counts
]

output.parent.mkdir(parents=True, exist_ok=True)
report_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output, index=False)

summary = {
    "records": len(df),
    "records_with_DX": sum(n > 0 for n in marker_counts),
    "records_without_DX": sum(n == 0 for n in marker_counts),
    "marker_style_counts": dict(Counter(marker_styles)),
    "multiple_marker_records": sum(n > 1 for n in marker_counts),
    "empty_prefix_fallbacks": empty_prefix_count,
    "empty_cleaned_text": int(
        df["circumstance_text_clean"].eq("").sum()
    ),
    "method_counts": dict(Counter(methods)),
    "output": str(output),
    "warning": (
        "Experimental representation. Original narratives retained. "
        "DX token parsing may require manual review where DX is not "
        "being used as a diagnosis separator. Narratives without DX "
        "retain possible diagnosis text."
    )
}

report_path.write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8"
)

print(json.dumps(summary, indent=2))

print("\nPARSER V2 COMPLETE")
