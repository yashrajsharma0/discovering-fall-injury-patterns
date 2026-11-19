"""Create separate R1/R2 theme-coherence review sheets from a cluster review sample.

The input should contain sampled examples per cluster with original narratives and
an extracted circumstance-text field. AI theme hypotheses are deliberately not
included in reviewer files.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

REQUIRED = {
    "cluster_id", "Source_Year", "CPSC_Case_Number", "Age",
    "original_narrative", "circumstance_text"
}
COLUMNS = [
    "cluster_id", "review_order_within_cluster", "Source_Year",
    "CPSC_Case_Number", "Age", "original_narrative", "circumstance_text",
    "human_theme_name_for_cluster", "coherence_1_to_5_for_cluster",
    "reviewer_id", "review_date_yyyy_mm_dd", "review_notes",
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="Human cluster review template CSV")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--seed-r1", type=int, default=17)
    ap.add_argument("--seed-r2", type=int, default=29)
    args = ap.parse_args()

    src, out = Path(args.input), Path(args.output_dir)
    if not src.exists():
        raise FileNotFoundError(src)
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite existing folder: {out}")

    frame = pd.read_csv(src, low_memory=False)
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Input missing columns: {sorted(missing)}")
    if frame[["Source_Year", "CPSC_Case_Number", "cluster_id"]].duplicated().any():
        raise ValueError("Duplicate case/cluster rows in theme review source.")

    out.mkdir(parents=True)
    for reviewer, seed in (("R1", args.seed_r1), ("R2", args.seed_r2)):
        rows: list[dict] = []
        for cid, group in frame.groupby("cluster_id", sort=True):
            shuffled = group.sample(frac=1, random_state=seed + int(cid)).reset_index(drop=True)
            for idx, row in shuffled.iterrows():
                rows.append({
                    "cluster_id": int(cid),
                    "review_order_within_cluster": idx + 1,
                    "Source_Year": row["Source_Year"],
                    "CPSC_Case_Number": row["CPSC_Case_Number"],
                    "Age": row["Age"],
                    "original_narrative": row["original_narrative"],
                    "circumstance_text": row["circumstance_text"],
                    "human_theme_name_for_cluster": "",
                    "coherence_1_to_5_for_cluster": "",
                    "reviewer_id": reviewer,
                    "review_date_yyyy_mm_dd": "",
                    "review_notes": "",
                })
        pd.DataFrame(rows, columns=COLUMNS).to_csv(
            out / f"reviewer_{reviewer}_FULL_CANDIDATE_K8_THEME_COHERENCE.csv",
            index=False,
        )

    instructions = """# Independent theme-coherence review\n\nGive each reviewer their own file. Both files contain the same cases, with different within-cluster order. Do not share ratings before both are complete.\n\nFor each cluster, read all sampled narratives. Enter one short descriptive theme name and one coherence score (1–5) on the first row of that cluster only; leave those two fields blank on the remaining rows in that cluster. Add notes for mixed mechanisms, possible non-falls, parser mistakes or ambiguity.\n\nCoherence scale: 1 = no common circumstance; 2 = weak/mixed; 3 = partly coherent; 4 = mostly coherent; 5 = one clear recurring circumstance. Human theme judgement is not model accuracy. The records remain keyword-screened candidates, not confirmed falls.\n"""
    (out / "README_THEME_COHERENCE_REVIEW.md").write_text(instructions, encoding="utf-8")
    print(f"Created separate R1/R2 theme review files in {out}")


if __name__ == "__main__":
    main()
