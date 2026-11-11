"""Compare subsample clustering stability for two saved assignments files.

Uses the already-cleaned Narrative_1 field from each saved experiment. The metric is
mean pairwise adjusted Rand index (ARI) over overlapping random subsamples.
"""
from pathlib import Path
import argparse
import json

import pandas as pd

from stability import evaluate_stability


def load_texts(path: Path, text_column: str) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Assignments file not found: {path}")
    frame = pd.read_csv(path, low_memory=False)
    if text_column not in frame.columns:
        raise ValueError(f"{path} does not contain text column {text_column!r}")
    texts = frame[text_column].fillna("").astype(str).str.strip()
    texts = texts[texts.str.len() > 0].tolist()
    if len(texts) < 20:
        raise ValueError(f"Only {len(texts)} non-empty narratives in {path}; need at least 20.")
    return texts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v2", default="results/circumstance_v2_5000/prototype_assignments.csv")
    parser.add_argument("--v4", default="results/circumstance_v4_5000/prototype_assignments.csv")
    parser.add_argument("--text-column", default="Narrative_1")
    parser.add_argument("--clusters", type=int, default=6)
    parser.add_argument("--repeats", type=int, default=3, help="Use 3 for a quick pilot; 5+ for a more stable estimate.")
    parser.add_argument("--sample-fraction", type=float, default=0.8)
    parser.add_argument("--output", default="results/stability_comparison_5000.json")
    args = parser.parse_args()

    if args.repeats < 2:
        parser.error("--repeats must be at least 2")
    if not 0.5 <= args.sample_fraction < 1:
        parser.error("--sample-fraction must be >= 0.5 and < 1")

    experiments = [
        ("V2", Path(args.v2)),
        ("V4", Path(args.v4)),
    ]
    report = {
        "purpose": "Exploratory subsample stability comparison; ARI does not measure semantic correctness.",
        "settings": {
            "n_clusters": args.clusters,
            "repeats": args.repeats,
            "sample_fraction": args.sample_fraction,
            "text_column": args.text_column,
            "random_state": 42,
        },
        "experiments": {},
    }

    for name, path in experiments:
        texts = load_texts(path, args.text_column)
        result = evaluate_stability(
            texts,
            n_clusters=args.clusters,
            repeats=args.repeats,
            sample_fraction=args.sample_fraction,
            random_state=42,
        )
        result["input_file"] = str(path)
        report["experiments"][name] = result

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("STABILITY COMPARISON COMPLETE")
    for name, result in report["experiments"].items():
        print(
            f"{name}: mean ARI={result['mean_pairwise_ari']:.4f}, "
            f"SD={result['std_pairwise_ari']:.4f}, "
            f"pairwise comparisons={len(result['pairwise_ari'])}"
        )
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
