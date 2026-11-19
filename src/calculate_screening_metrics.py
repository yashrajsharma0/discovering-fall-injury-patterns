"""Calculate design-weighted keyword-screen metrics from HUMAN-adjudicated labels only.

This script deliberately refuses to use AI labels or chat-confirmed suggestions as
reference truth. Complete human_verified_fall_label with yes/no/uncertain and set
human_verification_status=verified only after a human has reviewed the narrative.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

VALID = {"yes", "no", "uncertain"}


def weighted_confusion(df: pd.DataFrame) -> dict:
    label = df["human_verified_fall_label"].astype(str).str.strip().str.lower()
    group = df["screen_group"].astype(str).str.strip().str.lower()
    w = pd.to_numeric(df["sampling_weight"], errors="raise").astype(float)
    yes = label.eq("yes")
    no = label.eq("no")
    undecided = label.eq("uncertain")
    cand = group.eq("candidate")
    noncand = group.eq("non_candidate")
    tp = float(w[cand & yes].sum())
    fp = float(w[cand & no].sum())
    up = float(w[cand & undecided].sum())
    fn = float(w[noncand & yes].sum())
    tn = float(w[noncand & no].sum())
    un = float(w[noncand & undecided].sum())
    decided_pos = tp + fp
    decided_neg = fn + tn
    total_decided = decided_pos + decided_neg
    metrics = {
        "weighted_tp": tp, "weighted_fp": fp, "weighted_fn": fn, "weighted_tn": tn,
        "weighted_uncertain_candidates": up, "weighted_uncertain_non_candidates": un,
        "precision_among_decided": tp / decided_pos if decided_pos else None,
        "recall_among_decided": tp / (tp + fn) if (tp + fn) else None,
        "specificity_among_decided": tn / (tn + fp) if (tn + fp) else None,
        "accuracy_among_decided": (tp + tn) / total_decided if total_decided else None,
        "weighted_unresolved_share_pct": 100 * (up + un) / (tp + fp + fn + tn + up + un)
            if (tp + fp + fn + tn + up + un) else None,
        "precision_sensitivity_bounds": {
            "lower_all_uncertain_candidates_non_fall": tp / (tp + fp + up) if (tp + fp + up) else None,
            "upper_all_uncertain_candidates_fall": (tp + up) / (tp + fp + up) if (tp + fp + up) else None,
        },
        "recall_sensitivity_bounds": {
            "lower_uncertain_noncandidates_are_falls": tp / (tp + fn + un) if (tp + fn + un) else None,
            "upper_uncertain_candidates_are_falls": (tp + up) / (tp + up + fn) if (tp + up + fn) else None,
        },
    }
    return metrics


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    src, dst = Path(a.input), Path(a.output)
    if not src.exists(): raise FileNotFoundError(src)
    if dst.exists(): raise FileExistsError(f"Refusing to overwrite {dst}")
    df = pd.read_csv(src, low_memory=False)
    required = {"screen_group", "sampling_weight", "human_verified_fall_label", "human_verification_status"}
    missing = required - set(df.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    status = df["human_verification_status"].astype(str).str.strip().str.lower()
    accepted_statuses = {"verified", "verified_two_reviewer_agreement", "verified_adjudicated"}
    if not status.isin(accepted_statuses).all():
        raise SystemExit(
            "STOP: every row must be independently reviewed by humans and marked "
            "verified, verified_two_reviewer_agreement, or verified_adjudicated. "
            "Unresolved disagreements and AI-only labels cannot be scored."
        )
    labels = df["human_verified_fall_label"].astype(str).str.strip().str.lower()
    bad = sorted(set(labels) - VALID)
    if bad: raise ValueError(f"Invalid/missing human labels: {bad}")
    metrics = weighted_confusion(df)
    report = {
        "input_file": str(src),
        "n_rows": int(len(df)),
        "reference_label_source": "human_verified_fall_label only",
        "sampling_design": "stratified by year and keyword-screen group; use provided sampling_weight",
        "metrics": metrics,
        "warning": (
            "Weighted complete-case metrics exclude uncertain human labels. Report unresolved share "
            "and sensitivity bounds. These estimate keyword-screen performance within this NEISS "
            "age-65+ universe, not population prevalence of all older-adult falls."
        ),
    }
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__": main()
