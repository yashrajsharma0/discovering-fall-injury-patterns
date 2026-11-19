"""Reproducible benchmark for fall-narrative text representations.

Creates a new stratified 5,000-row candidate sample and compares:
  A. Full narrative + negation-preserving domain TF-IDF + KMeans
  B. DX-aware event text + the same TF-IDF + KMeans
  C. DX-aware event text + TF-IDF -> LSA (TruncatedSVD + L2 normalization) -> KMeans

No model is automatically declared a winner. Silhouette values are computed in
separate feature spaces (cosine for TF-IDF, Euclidean for LSA) and are not
interpretable as a direct cross-space ranking. Human inspection remains required.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import Normalizer

from build_circumstance_text_v3 import transform_one, clean_text

NEGATION = {"no", "nor", "not", "never", "neither", "none", "without"}
# Only structural boilerplate/demographic shorthand is removed here. Do not
# remove mechanism/location/activity words or injury terms in this first test.
DOMAIN_BOILERPLATE = {
    "pt", "pts", "patient", "patients", "states", "stated", "state",
    "reports", "reported", "report", "presents", "presented", "present",
    "complains", "complaint", "complaining", "inj", "ed", "dx", "yom",
    "yof", "yo", "yrs", "yr", "yearold", "year", "old", "male", "female",
}
STOP_WORDS = sorted((set(ENGLISH_STOP_WORDS) - NEGATION) | DOMAIN_BOILERPLATE)


def make_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        stop_words=STOP_WORDS,
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.95,
        max_features=30000,
        sublinear_tf=True,
        strip_accents="unicode",
    )


def stratified_sample(frame: pd.DataFrame, per_year: int, seed: int) -> pd.DataFrame:
    if "Source_Year" not in frame.columns:
        raise ValueError("Source_Year column required for stratified sampling.")
    pieces = []
    for year, group in frame.groupby("Source_Year", sort=True):
        if len(group) < per_year:
            raise ValueError(f"Year {year} has only {len(group)} rows; need {per_year}.")
        pieces.append(group.sample(n=per_year, random_state=seed))
    sample = pd.concat(pieces, axis=0).sort_values(
        ["Source_Year", "CPSC_Case_Number"], kind="stable"
    ).reset_index(drop=True)
    return sample


def top_terms_by_cluster(matrix, labels, terms, top_n=15):
    profiles = {}
    for cluster_id in sorted(np.unique(labels)):
        mask = labels == cluster_id
        mean_weights = np.asarray(matrix[mask].mean(axis=0)).ravel()
        top_idx = np.argsort(mean_weights)[::-1][:top_n]
        profiles[str(int(cluster_id))] = [str(terms[i]) for i in top_idx if mean_weights[i] > 0]
    return profiles


def cluster_sizes(labels, case_weights=None):
    counts = pd.Series(labels).value_counts().sort_index()
    n = len(labels)
    result = {
        "cluster_sizes": {str(int(k)): int(v) for k, v in counts.items()},
        "cluster_shares_pct": {str(int(k)): round(100 * int(v) / n, 3) for k, v in counts.items()},
        "largest_cluster_share_pct": round(100 * int(counts.max()) / n, 3),
        "smallest_cluster_share_pct": round(100 * int(counts.min()) / n, 3),
    }
    if case_weights is not None:
        weights = np.asarray(case_weights, dtype=float)
        if len(weights) != len(labels) or not np.isfinite(weights).all() or (weights < 0).any() or weights.sum() <= 0:
            raise ValueError("Expanded NEISS analysis weights must be finite, non-negative and aligned to rows.")
        weighted = pd.DataFrame({"cluster": labels, "weight": weights}).groupby("cluster")["weight"].sum().sort_index()
        result["candidate_frame_neiss_weighted_estimate_by_cluster"] = {str(int(k)): round(float(v), 2) for k, v in weighted.items()}
        result["candidate_frame_neiss_weighted_share_pct"] = {str(int(k)): round(100 * float(v) / float(weights.sum()), 3) for k, v in weighted.items()}
        result["expanded_neiss_estimate_across_candidate_frame"] = round(float(weights.sum()), 2)
    return result


def fit_variant(texts, representation: str, k: int, seed: int, silhouette_n: int, case_weights=None):
    vectorizer = make_vectorizer()
    X = vectorizer.fit_transform(texts)
    terms = vectorizer.get_feature_names_out()

    if representation == "event_lsa":
        n_components = min(100, X.shape[0] - 1, X.shape[1] - 1)
        if n_components < 2:
            raise ValueError("Not enough features for LSA.")
        svd = TruncatedSVD(n_components=n_components, n_iter=7, random_state=seed)
        X_model = Normalizer(copy=False).fit_transform(svd.fit_transform(X))
        model = KMeans(n_clusters=k, random_state=seed, n_init=20, max_iter=500)
        labels = model.fit_predict(X_model)
        silhouette_metric = "euclidean_on_lsa_100d_normalized"
        score = float(silhouette_score(
            X_model, labels, metric="euclidean",
            sample_size=min(silhouette_n, len(texts)), random_state=seed
        ))
        explained = float(svd.explained_variance_ratio_.sum())
        # Terms are profiled in the original TF-IDF space, not the SVD axes.
        term_profiles = top_terms_by_cluster(X, labels, terms)
        extra = {"lsa_components": int(n_components), "lsa_explained_variance_ratio_sum": explained}
    else:
        model = KMeans(n_clusters=k, random_state=seed, n_init=20, max_iter=500)
        labels = model.fit_predict(X)
        silhouette_metric = "cosine_on_tfidf"
        score = float(silhouette_score(
            X, labels, metric="cosine",
            sample_size=min(silhouette_n, len(texts)), random_state=seed
        ))
        term_profiles = top_terms_by_cluster(X, labels, terms)
        extra = {}

    summary = {
        "representation": representation,
        "k": int(k),
        "rows": int(len(texts)),
        "vocabulary_size": int(len(terms)),
        "silhouette": score,
        "silhouette_metric_space": silhouette_metric,
        **cluster_sizes(labels, case_weights=case_weights),
        "top_terms_by_cluster": term_profiles,
        **extra,
    }
    return summary, labels, term_profiles


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Full keyword-screened candidate CSV")
    parser.add_argument("--output-dir", required=True, help="New output directory")
    parser.add_argument("--per-year", type=int, default=1250, help="Rows sampled per Source_Year")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--silhouette-sample", type=int, default=2000)
    parser.add_argument("--k-values", type=int, nargs="+", default=[4, 6, 8, 10])
    args = parser.parse_args()

    input_path = Path(args.input)
    out_dir = Path(args.output_dir)
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    if out_dir.exists():
        raise FileExistsError(f"Output directory exists; refusing to overwrite: {out_dir}")

    source = pd.read_csv(input_path, low_memory=False)
    required = {"Source_Year", "CPSC_Case_Number", "Narrative_1"}
    missing = required - set(source.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    sample = stratified_sample(source, args.per_year, args.seed)
    if sample[["Source_Year", "CPSC_Case_Number"]].duplicated().any():
        raise ValueError("Duplicate year/case ID in benchmark sample.")

    # Correct the equal-per-year subsampling when expanding NEISS Weight totals
    # back to the full keyword-candidate frame. Each sampled case represents
    # N_candidate_year / n_sample_year candidate records within its year.
    candidate_frame_n = source.groupby("Source_Year").size().to_dict()
    sample_n = sample.groupby("Source_Year").size().to_dict()
    sample["candidate_frame_rows_in_year"] = sample["Source_Year"].map(candidate_frame_n).astype(int)
    sample["candidate_sample_rows_in_year"] = sample["Source_Year"].map(sample_n).astype(int)
    sample["candidate_sample_expansion_factor"] = (
        sample["candidate_frame_rows_in_year"] / sample["candidate_sample_rows_in_year"]
    )
    if "Weight" in sample.columns:
        raw_neiss_weight = pd.to_numeric(sample["Weight"], errors="raise").astype(float)
        sample["candidate_frame_analysis_weight"] = raw_neiss_weight * sample["candidate_sample_expansion_factor"]
    else:
        sample["candidate_frame_analysis_weight"] = np.nan

    parsed = pd.DataFrame([transform_one(x) for x in sample["Narrative_1"]])
    sample = pd.concat([sample.reset_index(drop=True), parsed], axis=1)
    sample["full_text_clean"] = sample["Narrative_1"].map(clean_text)
    sample["event_text_clean"] = sample["circumstance_text_raw"].map(clean_text)

    if sample["full_text_clean"].eq("").any() or sample["event_text_clean"].eq("").any():
        raise ValueError("Empty cleaned text found; inspect parser before clustering.")

    out_dir.mkdir(parents=True, exist_ok=False)
    sample.to_csv(out_dir / f"benchmark_sample_{len(sample)}.csv", index=False)

    years = sample["Source_Year"].value_counts().sort_index().to_dict()
    print("Benchmark sample:", len(sample), "rows; by year:", years)
    print("DX extraction methods:", sample["circumstance_extraction_method"].value_counts().to_dict())
    print("Multiple DX flags:", int(sample["dx_multiple_marker_review"].sum()))
    print("Unparsed DX-suspect flags:", int(sample["dx_unparsed_suspect_review"].sum()))

    variants = {
        "full_tfidf": sample["full_text_clean"].tolist(),
        "event_tfidf": sample["event_text_clean"].tolist(),
        "event_lsa": sample["event_text_clean"].tolist(),
    }
    all_summaries = []
    labels_for_ari = {}
    profiles_for_k6 = {}

    for representation, texts in variants.items():
        for k in args.k_values:
            print(f"Fitting {representation}, k={k}...")
            summary, labels, profiles = fit_variant(
                texts, representation, k, args.seed, args.silhouette_sample,
                case_weights=(sample["candidate_frame_analysis_weight"].astype(float).to_numpy() if "Weight" in sample.columns else None)
            )
            all_summaries.append(summary)
            if k == 6:
                labels_for_ari[representation] = labels
                profiles_for_k6[representation] = profiles
            if k == 6 or (representation == "event_lsa" and k in {8, 10}):
                out = sample.copy()
                out["cluster_id"] = labels
                out.to_csv(out_dir / f"assignments_{representation}_k{k}.csv", index=False)

    # ARI is label permutation invariant, but it indicates agreement, not correctness.
    ari = {}
    for left, right in (("full_tfidf", "event_tfidf"), ("event_tfidf", "event_lsa"), ("full_tfidf", "event_lsa")):
        if left in labels_for_ari and right in labels_for_ari:
            ari[f"{left}__vs__{right}"] = float(adjusted_rand_score(labels_for_ari[left], labels_for_ari[right]))

    grid = pd.DataFrame([{k: v for k, v in x.items() if k not in {"top_terms_by_cluster"}} for x in all_summaries])
    grid.to_csv(out_dir / "benchmark_metrics.csv", index=False)

    terms_rows = []
    for summary in all_summaries:
        for cid, words in summary["top_terms_by_cluster"].items():
            terms_rows.append({
                "representation": summary["representation"],
                "k": summary["k"],
                "cluster_id": cid,
                "top_terms": " | ".join(words),
            })
    pd.DataFrame(terms_rows).to_csv(out_dir / "cluster_top_terms.csv", index=False)

    # Five random narratives per K=6 cluster create a reproducible human inspection file.
    review_rows = []
    for representation in labels_for_ari:
        assignment = sample.copy()
        assignment["cluster_id"] = labels_for_ari[representation]
        for cid, group in assignment.groupby("cluster_id", sort=True):
            examples = group.sample(n=min(5, len(group)), random_state=args.seed)
            for _, row in examples.iterrows():
                review_rows.append({
                    "representation": representation,
                    "cluster_id": int(cid),
                    "Source_Year": row["Source_Year"],
                    "CPSC_Case_Number": row["CPSC_Case_Number"],
                    "Age": row.get("Age"),
                    "screening_status": "keyword_candidate_not_confirmed_fall",
                    "original_narrative": row["Narrative_1"],
                    "circumstance_text": row["circumstance_text_raw"],
                    "human_theme_name": "",
                    "human_coherence_1_to_5": "",
                    "reviewer_id": "",
                    "review_notes": "",
                })
    # Add focused 10-example-per-cluster reviews for the LSA K=8 and K=10 candidates.
    for review_k in (8, 10):
        if review_k in args.k_values:
            lsa_review = pd.read_csv(out_dir / f"assignments_event_lsa_k{review_k}.csv", low_memory=False)
            for cid, group in lsa_review.groupby("cluster_id", sort=True):
                examples = group.sample(n=min(10, len(group)), random_state=args.seed)
                for _, row in examples.iterrows():
                    review_rows.append({
                        "representation": f"event_lsa_k{review_k}",
                        "cluster_id": int(cid),
                        "Source_Year": row["Source_Year"],
                        "CPSC_Case_Number": row["CPSC_Case_Number"],
                        "Age": row.get("Age"),
                        "screening_status": "keyword_candidate_not_confirmed_fall",
                        "original_narrative": row["Narrative_1"],
                        "circumstance_text": row["circumstance_text_raw"],
                        "human_theme_name": "",
                        "human_coherence_1_to_5": "",
                        "reviewer_id": "",
                        "review_notes": "",
                    })
    pd.DataFrame(review_rows).to_csv(out_dir / "human_cluster_review_template.csv", index=False)

    report = {
        "source_file": str(input_path),
        "sampling": {
            "design": "stratified random sample by Source_Year from keyword-screened candidates",
            "per_year": args.per_year,
            "seed": args.seed,
            "year_counts": {str(k): int(v) for k, v in years.items()},
            "candidate_frame_rows_by_year": {str(k): int(v) for k, v in candidate_frame_n.items()},
            "sample_expansion_factor_by_year": {str(k): float(candidate_frame_n[k] / sample_n[k]) for k in sample_n},
            "total_rows": int(len(sample)),
        },
        "models": all_summaries,
        "ari_between_representations": ari,
        "parser_audit": {
            "rows_with_dx": int((sample["dx_marker_count"] > 0).sum()),
            "rows_without_recognized_dx": int((sample["dx_marker_count"] == 0).sum()),
            "multiple_dx_review": int(sample["dx_multiple_marker_review"].sum()),
            "unparsed_dx_suspect_review": int(sample["dx_unparsed_suspect_review"].sum()),
        },
        "neiss_design_variables_present": {name: (name in sample.columns) for name in ["Weight", "Stratum", "PSU"]},
        "interpretation_warning": (
            "No model is selected automatically. Silhouette scores use cosine distance in each TF-IDF "
            "space and Euclidean distance in normalized LSA space; do not rank scores across these "
            "different spaces. ARI compares assignments, not correctness. All records are keyword-"
            "screened candidates, not confirmed falls. Weighted cluster shares are NEISS-weighted "
            "within this candidate sample, not falls prevalence. Stratum/PSU are required for "
            "design-based variance estimates and are absent unless preserved in the input. "
            "Use human_cluster_review_template.csv for "
            "independent theme-coherence review."
        ),
        "output_dir": str(out_dir),
    }
    (out_dir / "benchmark_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nBENCHMARK COMPLETE")
    print("Metrics:", out_dir / "benchmark_metrics.csv")
    print("Report:", out_dir / "benchmark_report.json")
    print("Review template:", out_dir / "human_cluster_review_template.csv")


if __name__ == "__main__":
    main()
