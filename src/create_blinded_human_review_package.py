"""Create separate blinded CSVs for two independent human reviewers.

AI draft labels and candidate/non-candidate status are kept in a separate
analysis key, not shown to the reviewers. Do not send the key to reviewers.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

KEY_COLUMNS = [
    "Source_Year", "CPSC_Case_Number", "screen_group", "sampling_frame_n",
    "sample_n_in_stratum", "sampling_weight", "manual_fall_label_yes_no_uncertain",
    "confidence_1_to_3", "evidence_phrase", "reviewer_id", "review_date_yyyy_mm_dd",
    "review_notes", "annotation_status", "user_confirmation_status",
    "user_confirmation_date", "user_confirmation_note", "final_adjudication_status",
]
REVIEW_COLUMNS = [
    "Source_Year", "CPSC_Case_Number", "Age", "Narrative_1",
    "human_verified_fall_label", "human_confidence_1_to_3",
    "human_evidence_phrase", "human_reviewer_id",
    "human_review_date_yyyy_mm_dd", "human_adjudication_notes",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="AI-assisted annotation CSV")
    ap.add_argument("--output-dir", required=True, help="New output folder")
    args = ap.parse_args()
    src, out = Path(args.input), Path(args.output_dir)
    if not src.exists():
        raise FileNotFoundError(src)
    if out.exists():
        raise FileExistsError(f"Output directory exists; refusing to overwrite: {out}")
    df = pd.read_csv(src, low_memory=False)
    required = {"Source_Year", "CPSC_Case_Number", "Age", "Narrative_1", "screen_group", "sampling_weight"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df[["Source_Year", "CPSC_Case_Number"]].duplicated().any():
        raise ValueError("Duplicate year/case IDs in source review file.")

    out.mkdir(parents=True)
    blind = df[["Source_Year", "CPSC_Case_Number", "Age", "Narrative_1"]].copy()
    for reviewer in ("R1", "R2"):
        review = blind.copy()
        review["human_verified_fall_label"] = ""
        review["human_confidence_1_to_3"] = ""
        review["human_evidence_phrase"] = ""
        review["human_reviewer_id"] = reviewer
        review["human_review_date_yyyy_mm_dd"] = ""
        review["human_adjudication_notes"] = ""
        review["human_verification_status"] = "not_reviewed"
        review.to_csv(out / f"reviewer_{reviewer}_BLINDED.csv", index=False)

    key_cols = [c for c in KEY_COLUMNS if c in df.columns]
    key = df[key_cols + ["Age", "Narrative_1"]].copy()
    key.to_csv(out / "analysis_key_INTERNAL_DO_NOT_SHARE.csv", index=False)
    readme = """# Human verification instructions

Two reviewers should complete their own CSV independently. Do not share the analysis key with reviewers until both files are returned.

1. Open only your assigned `reviewer_R1_BLINDED.csv` or `reviewer_R2_BLINDED.csv`.
2. Read the original narrative. Do not use the old AI label or the screening group to decide.
3. Enter `yes`, `no`, or `uncertain` in `human_verified_fall_label`.
4. Confidence: 1=low, 2=moderate, 3=high. This is reviewer confidence, not a probability.
5. Quote the shortest phrase that supports your label in `human_evidence_phrase`.
6. Fill review date and brief notes; keep reviewer ID unchanged.
7. Save as CSV. Do not sort rows or delete records.

Definition used for this project: YES only when the narrative supports that the person unintentionally came to rest on the ground, floor, or another lower level. NO when the event clearly does not describe the person falling (for example, an object fell onto them, or a near-trip with recovery). UNCERTAIN when the description does not establish whether the person fell. A trip/slip word alone is not sufficient. A person found on the floor without a described event is generally uncertain, not automatically yes.

The `analysis_key_INTERNAL_DO_NOT_SHARE.csv` contains candidate/non-candidate status, sampling weights, and prior AI annotations. Keep it away from reviewers to reduce anchoring bias.
"""
    (out / "README_HUMAN_REVIEW.md").write_text(readme, encoding="utf-8")
    print(f"Created blinded review package with {len(df)} cases in {out}")
    print("R1 and R2 files contain narratives and blank human fields only.")

if __name__ == "__main__":
    main()
