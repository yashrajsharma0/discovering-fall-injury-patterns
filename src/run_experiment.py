"""Run an exploratory fall-narrative clustering experiment using V4."""

from pathlib import Path
import argparse
import json

import pandas as pd

from circumstance_preprocess_v4 import circumstance_text
from baseline import assign_baseline_group
from model import fit_cluster_model, top_terms_by_cluster


ROOT = Path(__file__).resolve().parents[1]


def main():

    parser = argparse.ArgumentParser(
        description="Run fall narrative clustering with V4 preprocessing."
    )

    parser.add_argument(
        "--input",
        default=str(ROOT / "data" / "sample_fall_candidates.csv"),
        help="Input CSV containing Narrative_1."
    )

    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "results"),
        help="Directory for experiment results."
    )

    parser.add_argument(
        "--clusters",
        type=int,
        default=6,
        help="Number of requested clusters."
    )

    parser.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="Optional row cap for smoke tests; 0 means all rows."
    )

    args = parser.parse_args()

    if args.clusters < 2:
        parser.error("--clusters must be at least 2.")

    if args.max_rows < 0:
        parser.error("--max-rows cannot be negative.")

    input_path = Path(args.input)

    if not input_path.is_absolute():
        input_path = ROOT / input_path

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {input_path}"
        )

    output_dir = Path(args.output_dir)

    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading dataset...")

    df = pd.read_csv(input_path, low_memory=False)

    if args.max_rows:
        df = df.head(args.max_rows).copy()

    # Use the known narrative column.
    source_col = "Narrative_1"

    if source_col not in df.columns:
        raise ValueError(
            f"Required column '{source_col}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    original_count = len(df)

    # Apply the corrected V4 cleaner.
    print("Cleaning narratives with V4...")

    df["clean_text"] = df[source_col].map(circumstance_text)

    # Remove only empty cleaned narratives.
    df = df.loc[
        df["clean_text"].str.len() > 0
    ].copy().reset_index(drop=True)

    if len(df) < max(10, args.clusters + 1):
        raise ValueError(
            "Too few non-empty narratives remain after cleaning."
        )

    print(f"Rows loaded: {original_count}")
    print(f"Rows retained: {len(df)}")
    print(f"Rows removed as empty: {original_count - len(df)}")

    # Apply the existing keyword-frequency baseline.
    df["baseline_group"] = (
        df["clean_text"].map(assign_baseline_group)
    )

    print("Running TF-IDF and KMeans clustering...")

    vectorizer, model, matrix, labels, silhouette = (
        fit_cluster_model(
            df["clean_text"],
            n_clusters=args.clusters
        )
    )

    df["cluster_id"] = labels

    # Preserve original Narrative_1 and all source metadata.
    assignments_path = output_dir / "prototype_assignments.csv"

    df.to_csv(
        assignments_path,
        index=False
    )

    # Aggregate cluster and baseline counts.
    cluster_sizes = {
        str(k): int(v)
        for k, v in (
            df["cluster_id"]
            .value_counts()
            .sort_index()
            .items()
        )
    }

    baseline_sizes = {
        str(k): int(v)
        for k, v in (
            df["baseline_group"]
            .value_counts()
            .items()
        )
    }

    # Save aggregate experiment metrics.
    summary = {
        "experiment": "V4 circumstance preprocessing",
        "input_file": input_path.name,
        "rows_loaded": int(original_count),
        "rows_used": int(len(df)),
        "rows_removed_as_empty": int(original_count - len(df)),
        "text_column": source_col,
        "preprocessing_version": "V4",
        "n_clusters_requested": int(args.clusters),
        "cluster_sizes": cluster_sizes,
        "baseline_group_sizes": baseline_sizes,
        "silhouette_score_sampled": silhouette,
        "top_terms_by_cluster": top_terms_by_cluster(
            vectorizer,
            model
        ),
        "warning": (
            "Exploratory analysis only. Keyword-screened candidates "
            "are not verified fall labels. Cluster shares describe "
            "only the loaded candidate dataset."
        )
    }

    metrics_path = output_dir / "prototype_metrics.json"

    metrics_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8"
    )

    print("\nEXPERIMENT COMPLETE")
    print("-------------------")
    print(f"Preprocessing: V4")
    print(f"Rows used: {len(df)}")
    print(f"Clusters: {args.clusters}")
    print(f"Silhouette: {silhouette}")
    print(f"Assignments saved: {assignments_path}")
    print(f"Metrics saved: {metrics_path}")
    print("\nCluster sizes:")
    print(json.dumps(cluster_sizes, indent=2))
    print("\nTop terms:")
    print(json.dumps(summary["top_terms_by_cluster"], indent=2))


if __name__ == "__main__":
    main()
