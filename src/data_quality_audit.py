"""Audit the NEISS age-65+ keyword screen and draw a reproducible review sample.

This script does not decide whether an incident is a fall. It creates a balanced,
stratified sample from both screened candidates and non-candidates so a human can
review false positives and possible false negatives.

Example (run from the project root):
    python src\\data_quality_audit.py \
      --candidates data\\neiss_2019_2022_fall_candidates.csv \
      --universe data\\neiss_2019_2022_age65plus.csv
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_CANDIDATES = "data/neiss_2019_2022_fall_candidates.csv"
DEFAULT_UNIVERSE = "data/neiss_2019_2022_age65plus.csv"


def _clean_key_part(series: pd.Series) -> pd.Series:
    """Normalize join-key values without converting integer IDs to float strings."""
    return series.astype("string").str.strip().replace({"": pd.NA, "nan": pd.NA, "<NA>": pd.NA})


def _add_key(df: pd.DataFrame, year_col: str, id_col: str) -> pd.DataFrame:
    result = df.copy()
    year = _clean_key_part(result[year_col])
    case_id = _clean_key_part(result[id_col])
    result["__record_key"] = year + "|" + case_id
    return result


def _basic_stats(df: pd.DataFrame, name: str, year_col: str, id_col: str, age_col: str, text_col: str) -> dict[str, Any]:
    text = df[text_col].fillna("").astype(str).str.strip()
    age = pd.to_numeric(df[age_col], errors="coerce")
    keys = _add_key(df, year_col, id_col)["__record_key"]
    year_counts = df[year_col].astype("string").value_counts(dropna=False).sort_index()
    return {
        "name": name,
        "rows": int(len(df)),
        "rows_by_year": {str(k): int(v) for k, v in year_counts.items()},
        "missing_or_blank_narratives": int(text.eq("").sum()),
        "missing_case_numbers": int(df[id_col].isna().sum()),
        "duplicate_year_case_keys": int(keys.duplicated().sum()),
        "duplicate_narrative_rows": int(text[text.ne("")].duplicated().sum()),
        "invalid_or_missing_ages": int(age.isna().sum()),
        "under_65_rows": int((age < 65).fillna(False).sum()),
        "age_min": float(age.min()) if age.notna().any() else None,
        "age_max": float(age.max()) if age.notna().any() else None,
    }


def _select_review_fields(df: pd.DataFrame, args: argparse.Namespace, group: str, frame_n: int, sample_n: int) -> pd.DataFrame:
    wanted = [args.year_col, args.id_col, args.age_col, args.text_col]
    if args.keyword_col in df.columns:
        wanted.append(args.keyword_col)
    if args.match_flag_col in df.columns:
        wanted.append(args.match_flag_col)
    out = df[wanted].copy()
    out.insert(0, "screen_group", group)
    out["sampling_frame_n"] = int(frame_n)
    out["sample_n_in_stratum"] = int(sample_n)
    out["sampling_weight"] = float(frame_n / sample_n) if sample_n else None
    out["manual_fall_label_yes_no_uncertain"] = ""
    out["confidence_1_to_3"] = ""
    out["evidence_phrase"] = ""
    out["reviewer_id"] = ""
    out["review_date_yyyy_mm_dd"] = ""
    out["review_notes"] = ""
    return out


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    candidate_path = Path(args.candidates)
    if not candidate_path.exists():
        raise FileNotFoundError(f"Candidate CSV not found: {candidate_path}")
    candidates = pd.read_csv(candidate_path, low_memory=False)

    required = [args.year_col, args.id_col, args.age_col, args.text_col]
    missing = [column for column in required if column not in candidates.columns]
    if missing:
        raise ValueError(f"Candidate file is missing required columns: {missing}")
    candidates = _add_key(candidates, args.year_col, args.id_col)

    summary: dict[str, Any] = {
        "purpose": "Quality audit and human validation sampling for a keyword-screened candidate set.",
        "interpretation_warning": (
            "Keyword-screened records are candidates, not confirmed falls. Candidate shares are not fall prevalence. "
            "Manual labels are required to estimate screening performance."
        ),
        "sampling": {
            "method": "Stratified random sampling by source year and screen group; without replacement.",
            "sample_per_year_per_group_requested": int(args.sample_per_year_per_group),
            "random_seed": int(args.seed),
        },
        "candidates": _basic_stats(candidates.drop(columns="__record_key"), "keyword_screened_candidates", args.year_col, args.id_col, args.age_col, args.text_col),
    }

    if candidates["__record_key"].isna().any():
        raise ValueError("Candidate file contains missing year/case-number keys; resolve before sampling.")
    if candidates["__record_key"].duplicated().any():
        raise ValueError("Candidate file contains duplicate year+case-number keys; resolve before sampling.")
    if candidates[args.text_col].fillna("").astype(str).str.strip().eq("").any():
        raise ValueError("Candidate file contains blank narratives; inspect them before clustering.")

    rng = __import__("numpy").random.default_rng(args.seed)
    review_parts: list[pd.DataFrame] = []
    stratum_info: list[dict[str, Any]] = []

    universe_path = Path(args.universe) if args.universe else None
    if universe_path and universe_path.exists():
        universe = pd.read_csv(universe_path, low_memory=False)
        missing_u = [column for column in required if column not in universe.columns]
        if missing_u:
            raise ValueError(f"Age-65+ universe file is missing required columns: {missing_u}")
        universe = _add_key(universe, args.year_col, args.id_col)
        if universe["__record_key"].isna().any() or universe["__record_key"].duplicated().any():
            raise ValueError("Age-65+ universe has missing or duplicate year+case-number keys; resolve before sampling.")

        age = pd.to_numeric(universe[args.age_col], errors="coerce")
        if age.isna().any() or (age < 65).any():
            raise ValueError("Universe file must contain valid age-65+ records only.")
        if universe[args.text_col].fillna("").astype(str).str.strip().eq("").any():
            raise ValueError("Universe file contains blank narratives; inspect before review sampling.")

        universe_keys = set(universe["__record_key"].tolist())
        candidate_keys = set(candidates["__record_key"].tolist())
        not_in_universe = candidate_keys - universe_keys
        if not_in_universe:
            raise ValueError(f"{len(not_in_universe)} candidate keys are not present in the age-65+ universe.")

        universe["__screen_group"] = universe["__record_key"].map(
            lambda key: "candidate" if key in candidate_keys else "non_candidate"
        )
        summary["age65_plus_universe"] = _basic_stats(
            universe.drop(columns=["__record_key", "__screen_group"]),
            "all_age_65_plus_records", args.year_col, args.id_col, args.age_col, args.text_col
        )
        summary["candidate_screen_share_by_year_pct"] = {}
        for year, year_group in universe.groupby(args.year_col, dropna=False):
            cand_n = int((year_group["__screen_group"] == "candidate").sum())
            total_n = int(len(year_group))
            summary["candidate_screen_share_by_year_pct"][str(year)] = round(100 * cand_n / total_n, 3) if total_n else None

        # A review of candidates estimates precision; a review of non-candidates is
        # necessary to find missed cases and estimate recall/sensitivity.
        for year, year_group in universe.groupby(args.year_col, sort=True, dropna=False):
            for group_name in ("candidate", "non_candidate"):
                frame = year_group[year_group["__screen_group"] == group_name]
                frame_n = len(frame)
                take = min(args.sample_per_year_per_group, frame_n)
                if take == 0:
                    stratum_info.append({"year": str(year), "screen_group": group_name, "frame_n": 0, "sample_n": 0})
                    continue
                chosen_indices = rng.choice(frame.index.to_numpy(), size=take, replace=False)
                sampled = frame.loc[chosen_indices].drop(columns=["__record_key", "__screen_group"])
                review_parts.append(_select_review_fields(sampled, args, group_name, frame_n, take))
                stratum_info.append({"year": str(year), "screen_group": group_name, "frame_n": int(frame_n), "sample_n": int(take)})
        summary["candidate_keys_not_in_universe"] = 0
        summary["review_sample_scope"] = "candidate and non-candidate records, stratified by year"
    else:
        summary["universe_warning"] = (
            f"Age-65+ universe not found at {universe_path}. Only candidate precision can be sampled; "
            "false negatives/recall cannot be assessed without the complete age-65+ universe."
        )
        for year, frame in candidates.groupby(args.year_col, sort=True, dropna=False):
            take = min(args.sample_per_year_per_group, len(frame))
            if take == 0:
                continue
            chosen_indices = rng.choice(frame.index.to_numpy(), size=take, replace=False)
            sampled = frame.loc[chosen_indices].drop(columns="__record_key")
            review_parts.append(_select_review_fields(sampled, args, "candidate", len(frame), take))
            stratum_info.append({"year": str(year), "screen_group": "candidate", "frame_n": int(len(frame)), "sample_n": int(take)})
        summary["review_sample_scope"] = "candidates only; cannot estimate screening recall"

    review = pd.concat(review_parts, ignore_index=True) if review_parts else pd.DataFrame()
    if not review.empty:
        review = review.sort_values([args.year_col, "screen_group", args.id_col]).reset_index(drop=True)
    summary["sampling"]["strata"] = stratum_info
    summary["sampling"]["review_rows_created"] = int(len(review))
    summary["sampling"]["weight_note"] = (
        "sampling_weight = population size of the year x screen-group stratum divided by sampled rows in that stratum. "
        "Use these weights when calculating pooled screening metrics from the labelled sample."
    )
    summary["quality_notes"] = [
        "Duplicate narrative text is reported but not automatically removed; different incidents can have similar narratives.",
        "Candidate-screen share is a property of the keyword rule, not the real-world prevalence of falls.",
        "Reviewers should use yes/no/uncertain and record an evidence phrase; do not infer a fall from an isolated keyword alone.",
    ]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "data_quality_audit.json"
    review_path = Path(args.review_output)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    review.to_csv(review_path, index=False)
    print(json.dumps(summary, indent=2))
    print(f"\nSaved audit: {summary_path}")
    print(f"Saved review sample: {review_path}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", default=DEFAULT_CANDIDATES)
    parser.add_argument("--universe", default=DEFAULT_UNIVERSE)
    parser.add_argument("--out-dir", default="results/data_audit")
    parser.add_argument("--review-output", default="data/fall_screen_validation_review_randomized.csv")
    parser.add_argument("--sample-per-year-per-group", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--year-col", default="Source_Year")
    parser.add_argument("--id-col", default="CPSC_Case_Number")
    parser.add_argument("--age-col", default="Age")
    parser.add_argument("--text-col", default="Narrative_1")
    parser.add_argument("--keyword-col", default="Fall_Keywords_Matched")
    parser.add_argument("--match-flag-col", default="Fall_Keyword_Match")
    args = parser.parse_args()
    if args.sample_per_year_per_group < 1:
        parser.error("--sample-per-year-per-group must be at least 1")
    build_audit(args)


if __name__ == "__main__":
    main()
