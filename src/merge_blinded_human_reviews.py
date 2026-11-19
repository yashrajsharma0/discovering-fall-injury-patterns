"""Merge independent R1/R2 reviews, report agreement, and attach the internal key.

Agreed labels are transferred to human_verified_fall_label. Disagreements remain
blank and require an adjudicator. No AI labels are used as ground truth.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from sklearn.metrics import cohen_kappa_score

VALID = {"yes", "no", "uncertain"}
KEY_FIELDS = ["Source_Year", "CPSC_Case_Number", "screen_group", "sampling_weight"]


def normalize(s):
    return s.fillna("").astype(str).str.strip().str.lower()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reviewer1", required=True)
    ap.add_argument("--reviewer2", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--agreement-json", required=True)
    args = ap.parse_args()
    p1, p2, pk, po, pa = map(Path, (args.reviewer1, args.reviewer2, args.key, args.output, args.agreement_json))
    for p in (p1, p2, pk):
        if not p.exists(): raise FileNotFoundError(p)
    if po.exists() or pa.exists(): raise FileExistsError("Refusing to overwrite output files.")
    r1, r2, key = (pd.read_csv(p, low_memory=False) for p in (p1, p2, pk))
    id_cols = ["Source_Year", "CPSC_Case_Number"]
    for label, df in (("R1", r1), ("R2", r2), ("key", key)):
        if not set(id_cols + ["human_verified_fall_label"] if label != "key" else id_cols).issubset(df.columns):
            raise ValueError(f"{label} missing required fields.")
        if df[id_cols].duplicated().any(): raise ValueError(f"Duplicate IDs in {label}.")
    r1 = r1.rename(columns={
        "human_verified_fall_label":"R1_label", "human_confidence_1_to_3":"R1_confidence",
        "human_evidence_phrase":"R1_evidence", "human_review_date_yyyy_mm_dd":"R1_review_date",
        "human_adjudication_notes":"R1_notes", "human_verification_status":"R1_status"
    })
    r2 = r2.rename(columns={
        "human_verified_fall_label":"R2_label", "human_confidence_1_to_3":"R2_confidence",
        "human_evidence_phrase":"R2_evidence", "human_review_date_yyyy_mm_dd":"R2_review_date",
        "human_adjudication_notes":"R2_notes", "human_verification_status":"R2_status"
    })
    merged = r1.merge(r2, on=id_cols, how="outer", validate="one_to_one", suffixes=("_R1", "_R2"), indicator=True)
    if not merged["_merge"].eq("both").all(): raise ValueError("R1/R2 case IDs do not match exactly.")
    merged = merged.drop(columns="_merge")
    # The source narrative and age should be identical across both blinded files.
    for col in ("Narrative_1", "Age"):
        c1, c2 = f"{col}_R1", f"{col}_R2"
        if c1 not in merged or c2 not in merged:
            raise ValueError(f"Both reviewer files must contain {col}.")
        if not merged[c1].fillna("").astype(str).equals(merged[c2].fillna("").astype(str)):
            raise ValueError(f"R1 and R2 disagree on {col}; source rows may have changed.")
        merged[col] = merged[c1]
        merged = merged.drop(columns=[c1, c2])
    a, b = normalize(merged["R1_label"]), normalize(merged["R2_label"])
    bad = (a.ne("") & ~a.isin(VALID)) | (b.ne("") & ~b.isin(VALID))
    if bad.any(): raise ValueError("Invalid reviewer labels found; use yes/no/uncertain.")
    both = a.isin(VALID) & b.isin(VALID)
    agreement = both & a.eq(b)
    disagreement = both & a.ne(b)
    kappa = float(cohen_kappa_score(a[both], b[both], labels=["yes", "no", "uncertain"])) if both.sum() else None
    merged["human_verified_fall_label"] = ""
    merged.loc[agreement, "human_verified_fall_label"] = a[agreement]
    merged["human_verification_status"] = "requires_review"
    merged.loc[agreement, "human_verification_status"] = "verified_two_reviewer_agreement"
    merged["adjudicator_label"] = ""
    merged["adjudicator_id"] = ""
    merged["adjudication_note"] = ""
    merged["final_human_label_status"] = merged["human_verification_status"]
    # Attach internal sampling key only after independent review has been recorded.
    key_cols = [c for c in KEY_FIELDS if c in key.columns]
    final = merged.merge(key[key_cols], on=id_cols, how="left", validate="one_to_one")
    if final["screen_group"].isna().any() or final["sampling_weight"].isna().any():
        raise ValueError("Internal key did not match every reviewed case.")
    report = {
        "n_cases": int(len(final)),
        "r1_labelled": int(a.isin(VALID).sum()),
        "r2_labelled": int(b.isin(VALID).sum()),
        "both_labelled": int(both.sum()),
        "agreements": int(agreement.sum()),
        "disagreements_requiring_adjudication": int(disagreement.sum()),
        "unlabelled_or_incomplete_pairs": int((~both).sum()),
        "raw_percent_agreement": float(agreement.sum()/both.sum()) if both.sum() else None,
        "cohen_kappa_three_categories": kappa,
        "warning": "Agreement is not accuracy. Disagreements must be adjudicated by a human; AI labels and prior approval of AI suggestions are not reference truth. Cohen's kappa is interpretable only with completed independent labels.",
    }
    po.parent.mkdir(parents=True, exist_ok=True); pa.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(po, index=False)
    pa.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("Merged review saved:", po)
    print("For each disagreement, an adjudicator must enter adjudicator_label, adjudicator_id and adjudication_note; copy the adjudicated label into human_verified_fall_label and set human_verification_status=verified_adjudicated. Then rerun calculate_screening_metrics.py.")

if __name__ == "__main__": main()
