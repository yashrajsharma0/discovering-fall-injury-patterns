"""Explore HDBSCAN on the same circumstance-text LSA space as the KMeans benchmark.

Noise label -1 is retained as a reported outcome, not silently discarded.
Silhouette is computed only on non-noise rows and in the normalized LSA space.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import Normalizer
from build_circumstance_text_v3 import clean_text

NEGATION = {"no", "nor", "not", "never", "neither", "none", "without"}
DOMAIN_BOILERPLATE = {
    "pt", "pts", "patient", "patients", "states", "stated", "state",
    "reports", "reported", "report", "presents", "presented", "present",
    "complains", "complaint", "complaining", "inj", "ed", "dx", "yom",
    "yof", "yo", "yrs", "yr", "yearold", "year", "old", "male", "female",
}
STOP_WORDS = sorted((set(ENGLISH_STOP_WORDS) - NEGATION) | DOMAIN_BOILERPLATE)


def top_terms(X, labels, terms, cid, n=15):
    rows = labels == cid
    avg = np.asarray(X[rows].mean(axis=0)).ravel()
    idx = np.argsort(avg)[::-1][:n]
    return [str(terms[i]) for i in idx if avg[i] > 0]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="Benchmark sample CSV with circumstance_text_raw")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--silhouette-sample", type=int, default=2000)
    ap.add_argument("--min-cluster-sizes", type=int, nargs="+", default=[30, 50, 100])
    ap.add_argument("--min-samples", type=int, default=10)
    args = ap.parse_args()
    src, out = Path(args.input), Path(args.output_dir)
    if not src.exists(): raise FileNotFoundError(src)
    if out.exists(): raise FileExistsError(f"Refusing to overwrite {out}")

    df = pd.read_csv(src, low_memory=False)
    required = {"CPSC_Case_Number", "Source_Year", "Narrative_1", "circumstance_text_raw"}
    missing = required - set(df.columns)
    if missing: raise ValueError(f"Missing fields: {sorted(missing)}")
    texts = df["circumstance_text_raw"].fillna("").map(clean_text).tolist()
    vectorizer = TfidfVectorizer(
        stop_words=STOP_WORDS, ngram_range=(1, 2), min_df=3, max_df=.95,
        max_features=30000, sublinear_tf=True, strip_accents="unicode"
    )
    X = vectorizer.fit_transform(texts)
    terms = vectorizer.get_feature_names_out()
    n_comp = min(100, X.shape[0]-1, X.shape[1]-1)
    svd = TruncatedSVD(n_components=n_comp, n_iter=7, random_state=args.seed)
    X_lsa = Normalizer(copy=False).fit_transform(svd.fit_transform(X))
    out.mkdir(parents=True)
    reports=[]

    for min_size in args.min_cluster_sizes:
        print(f"Fitting HDBSCAN min_cluster_size={min_size}, min_samples={args.min_samples}...", flush=True)
        model = HDBSCAN(
            min_cluster_size=min_size, min_samples=args.min_samples,
            metric="euclidean", cluster_selection_method="eom", n_jobs=-1
        )
        labels = model.fit_predict(X_lsa)
        unique = sorted(set(labels) - {-1})
        n_noise = int((labels == -1).sum())
        clustered_mask = labels != -1
        sil = None
        if len(unique) >= 2 and int(clustered_mask.sum()) > len(unique):
            X_clustered = X_lsa[clustered_mask]
            y_clustered = labels[clustered_mask]
            sil = float(silhouette_score(
                X_clustered, y_clustered, metric="euclidean",
                sample_size=min(args.silhouette_sample, len(y_clustered)), random_state=args.seed
            ))
        sizes = pd.Series(labels).value_counts().sort_index()
        weights = pd.to_numeric(df.get("candidate_frame_analysis_weight", df.get("Weight", pd.Series(np.ones(len(df))))), errors="coerce").fillna(0).to_numpy(dtype=float)
        if len(weights) != len(labels) or (weights < 0).any() or weights.sum() <= 0:
            raise ValueError("Invalid/unaligned weights")
        weighted = pd.DataFrame({"cluster_id":labels,"weight":weights}).groupby("cluster_id")["weight"].sum().sort_index()
        summary = {
            "min_cluster_size": int(min_size), "min_samples": int(args.min_samples),
            "rows": int(len(df)), "n_clusters_excluding_noise": int(len(unique)),
            "noise_rows": n_noise, "noise_share_pct": round(100*n_noise/len(df),3),
            "silhouette_non_noise_sampled": sil,
            "silhouette_metric_space": "euclidean_on_normalized_100d_LSA_non_noise_only",
            "cluster_sizes_including_noise": {str(int(k)): int(v) for k,v in sizes.items()},
            "weighted_shares_including_noise_pct": {str(int(k)): round(100*float(v)/float(weights.sum()),3) for k,v in weighted.items()},
            "top_terms_by_cluster": {str(int(cid)): top_terms(X, labels, terms, cid) for cid in unique},
            "warning": "HDBSCAN may mark records as noise (-1). Silhouette excludes noise rows and therefore is not directly comparable with KMeans silhouette over all rows. Density clustering scores do not establish semantic theme correctness."
        }
        reports.append(summary)
        out_df=df.copy(); out_df["cluster_id_hdbscan"]=labels.astype(int)
        out_df.to_csv(out / f"assignments_hdbscan_mcs{min_size}.csv", index=False)
        review=[]
        for cid in unique:
            group=out_df[out_df["cluster_id_hdbscan"]==cid]
            ex=group.sample(n=min(10,len(group)),random_state=args.seed)
            for _,r in ex.iterrows():
                review.append({"cluster_id":int(cid),"CPSC_Case_Number":r["CPSC_Case_Number"],"Source_Year":r["Source_Year"],"Age":r.get("Age"),"original_narrative":r["Narrative_1"],"circumstance_text":r["circumstance_text_raw"],"human_theme_name":"","coherence_1_to_5":"","reviewer_id":"","review_notes":""})
        noise=out_df[out_df["cluster_id_hdbscan"]==-1]
        if len(noise):
            for _,r in noise.sample(n=min(20,len(noise)),random_state=args.seed).iterrows():
                review.append({"cluster_id":-1,"CPSC_Case_Number":r["CPSC_Case_Number"],"Source_Year":r["Source_Year"],"Age":r.get("Age"),"original_narrative":r["Narrative_1"],"circumstance_text":r["circumstance_text_raw"],"human_theme_name":"noise / inspect","coherence_1_to_5":"","reviewer_id":"","review_notes":"Why was this record not assigned to a dense cluster?"})
        pd.DataFrame(review).to_csv(out / f"human_review_hdbscan_mcs{min_size}.csv",index=False)
        print(f"clusters={len(unique)}, noise={n_noise} ({summary['noise_share_pct']}%), silhouette={sil}", flush=True)

    report={"input":str(src),"rows":int(len(df)),"svd_components":int(n_comp),"svd_explained_variance_ratio_sum":float(svd.explained_variance_ratio_.sum()),"experiments":reports}
    (out/"hdbscan_lsa_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("HDBSCAN BENCHMARK COMPLETE",flush=True)

if __name__ == "__main__": main()
