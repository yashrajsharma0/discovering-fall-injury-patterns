"""Run a full-frame exploratory LSA+KMeans clustering over all keyword candidates.

This uses the same circumstance parser and TF-IDF/LSA pipeline as the benchmark.
It does not assert that every input row is a verified fall.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import Normalizer
from build_circumstance_text_v3 import transform_one, clean_text

NEGATION = {"no", "nor", "not", "never", "neither", "none", "without"}
DOMAIN_BOILERPLATE = {
    "pt", "pts", "patient", "patients", "states", "stated", "state",
    "reports", "reported", "report", "presents", "presented", "present",
    "complains", "complaint", "complaining", "inj", "ed", "dx", "yom",
    "yof", "yo", "yrs", "yr", "yearold", "year", "old", "male", "female",
}
STOP_WORDS = sorted((set(ENGLISH_STOP_WORDS) - NEGATION) | DOMAIN_BOILERPLATE)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--clusters", type=int, default=8)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--silhouette-sample", type=int, default=5000)
    ap.add_argument("--max-features", type=int, default=30000)
    ap.add_argument("--svd-components", type=int, default=100)
    ap.add_argument("--n-init", type=int, default=10)
    args = ap.parse_args()
    src, out = Path(args.input), Path(args.output_dir)
    if not src.exists(): raise FileNotFoundError(src)
    if out.exists(): raise FileExistsError(f"Refusing to overwrite {out}")

    print("Loading full keyword-candidate frame...", flush=True)
    df = pd.read_csv(src, low_memory=False)
    required = {"Source_Year", "CPSC_Case_Number", "Narrative_1", "Weight"}
    missing = required - set(df.columns)
    if missing: raise ValueError(f"Missing required fields: {sorted(missing)}")
    if df[["Source_Year", "CPSC_Case_Number"]].duplicated().any():
        raise ValueError("Duplicate Source_Year/CPSC_Case_Number key detected.")

    print(f"Rows: {len(df):,}; parsing incident text...", flush=True)
    parsed = pd.DataFrame([transform_one(x) for x in df["Narrative_1"]])
    event_texts = parsed["circumstance_text_raw"].map(clean_text).tolist()
    if any(not x for x in event_texts): raise ValueError("Empty circumstance text after parser fallback.")

    print("Vectorizing full event-text frame...", flush=True)
    vectorizer = TfidfVectorizer(
        stop_words=STOP_WORDS, ngram_range=(1, 2), min_df=3, max_df=0.95,
        max_features=args.max_features, sublinear_tf=True, strip_accents="unicode"
    )
    X = vectorizer.fit_transform(event_texts)
    terms = vectorizer.get_feature_names_out()
    n_components = min(args.svd_components, X.shape[0] - 1, X.shape[1] - 1)
    if n_components < 2: raise ValueError("Insufficient features for SVD.")

    print(f"TF-IDF: shape={X.shape}; fitting TruncatedSVD({n_components})...", flush=True)
    svd = TruncatedSVD(n_components=n_components, n_iter=7, random_state=args.seed)
    X_lsa = svd.fit_transform(X)
    X_lsa = Normalizer(copy=False).fit_transform(X_lsa)

    print(f"Fitting KMeans K={args.clusters}, n_init={args.n_init}...", flush=True)
    model = KMeans(
        n_clusters=args.clusters, random_state=args.seed,
        n_init=args.n_init, max_iter=300, algorithm="lloyd"
    )
    labels = model.fit_predict(X_lsa)

    print("Calculating sampled silhouette...", flush=True)
    sil = float(silhouette_score(
        X_lsa, labels, metric="euclidean",
        sample_size=min(args.silhouette_sample, len(labels)),
        random_state=args.seed
    ))

    weights = pd.to_numeric(df["Weight"], errors="raise").astype(float).to_numpy()
    if not np.isfinite(weights).all() or (weights < 0).any() or weights.sum() <= 0:
        raise ValueError("Invalid NEISS Weight values.")
    counts = pd.Series(labels).value_counts().sort_index()
    weighted = pd.DataFrame({"cluster_id": labels, "Weight": weights}).groupby("cluster_id")["Weight"].sum().sort_index()
    n = len(df)

    profile_rows = []
    for cid in sorted(np.unique(labels)):
        mask = labels == cid
        mean_w = np.asarray(X[mask].mean(axis=0)).ravel()
        top_idx = np.argsort(mean_w)[::-1][:15]
        top = [str(terms[i]) for i in top_idx if mean_w[i] > 0]
        profile_rows.append({"cluster_id": int(cid), "records": int(mask.sum()),
                             "raw_share_pct": round(100*int(mask.sum())/n, 3),
                             "NEISS_weighted_estimate": round(float(weighted.loc[cid]), 2),
                             "NEISS_weighted_share_pct": round(100*float(weighted.loc[cid])/float(weights.sum()), 3),
                             "top_terms": " | ".join(top)})

    out.mkdir(parents=True)
    index = df[["Source_Year", "CPSC_Case_Number", "Weight"]].copy()
    index["cluster_id"] = labels.astype(int)
    index.to_csv(out / "full_candidate_cluster_index.csv", index=False)
    pd.DataFrame(profile_rows).to_csv(out / "full_candidate_cluster_summary.csv", index=False)

    # Ten reproducibly sampled examples per cluster for human naming/coherence review.
    tmp = df.copy()
    tmp["circumstance_text_raw"] = parsed["circumstance_text_raw"].values
    tmp["circumstance_text_method"] = parsed["circumstance_extraction_method"].values
    tmp["dx_marker_count"] = parsed["dx_marker_count"].values
    tmp["cluster_id"] = labels.astype(int)
    examples = []
    for cid, group in tmp.groupby("cluster_id", sort=True):
        chosen = group.sample(n=min(10, len(group)), random_state=args.seed)
        for _, row in chosen.iterrows():
            examples.append({
                "cluster_id": int(cid), "Source_Year": row["Source_Year"],
                "CPSC_Case_Number": row["CPSC_Case_Number"], "Age": row.get("Age"),
                "original_narrative": row["Narrative_1"],
                "circumstance_text": row["circumstance_text_raw"],
                "human_theme_name": "", "human_coherence_1_to_5": "",
                "reviewer_id": "", "review_notes": "",
            })
    pd.DataFrame(examples).to_csv(out / "human_cluster_review_template.csv", index=False)

    report = {
        "input_file": str(src), "rows": int(n), "clusters": int(args.clusters),
        "seed": int(args.seed), "tfidf_vocabulary_size": int(len(terms)),
        "tfidf_shape": [int(X.shape[0]), int(X.shape[1])],
        "svd_components": int(n_components),
        "svd_explained_variance_ratio_sum": float(svd.explained_variance_ratio_.sum()),
        "silhouette_sampled": sil,
        "silhouette_metric_space": "euclidean_on_normalized_lsa",
        "largest_cluster_share_pct": round(100*int(counts.max())/n, 3),
        "smallest_cluster_share_pct": round(100*int(counts.min())/n, 3),
        "raw_cluster_counts": {str(int(k)): int(v) for k,v in counts.items()},
        "raw_cluster_shares_pct": {str(int(k)): round(100*int(v)/n,3) for k,v in counts.items()},
        "NEISS_weighted_estimated_injuries_by_cluster": {str(int(k)): round(float(v),2) for k,v in weighted.items()},
        "NEISS_weighted_cluster_share_pct": {str(int(k)): round(100*float(v)/float(weights.sum()),3) for k,v in weighted.items()},
        "NEISS_weighted_total_estimated_injuries_in_candidate_frame": round(float(weights.sum()),2),
        "DX_parser_methods": {str(k): int(v) for k,v in parsed["circumstance_extraction_method"].value_counts().items()},
        "DX_multi_marker_flags": int(parsed["dx_multiple_marker_review"].sum()),
        "DX_unparsed_suspect_flags": int(parsed["dx_unparsed_suspect_review"].sum()),
        "warning": (
            "Full-candidate exploratory clustering only. All inputs are keyword-screened candidates, not confirmed falls. "
            "NEISS-weighted shares are for the keyword-candidate frame, not all older-adult falls. "
            "Stratum/PSU are absent from the prepared candidate CSV, so no design-based SE/CIs are supplied. "
            "Human cluster-theme naming and coherence review are still required."
        ),
    }
    (out / "full_candidate_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)
    print("FULL CANDIDATE EXPERIMENT COMPLETE", flush=True)

if __name__ == "__main__": main()
