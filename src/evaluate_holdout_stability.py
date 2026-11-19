"""Evaluate end-to-end representation/cluster stability on a fixed holdout.

Each repeat refits the vectorizer (and LSA when requested) on a different
training subsample, then predicts cluster assignments for the same untouched
holdout narratives. Pairwise ARI on that common holdout measures repeatability,
not semantic correctness.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import Normalizer

NEGATION = {"no", "nor", "not", "never", "neither", "none", "without"}
BOILERPLATE = {"pt", "pts", "patient", "patients", "states", "stated", "reports", "reported", "presented", "presents", "complains", "complaint", "inj", "ed", "dx", "yom", "yof", "yo"}
STOP = sorted((set(ENGLISH_STOP_WORDS) - NEGATION) | BOILERPLATE)


def norm(x):
    x = str(x).lower()
    x = re.sub(r"\b\d{1,3}\s*y\s*o?\s*[mf]\b", " ", x)
    x = re.sub(r"\b(?:yom|yof|yo\s*[mf])\b", " ", x)
    x = re.sub(r"[^a-z0-9\s'-]", " ", x)
    return re.sub(r"\s+", " ", x).strip()


def make_texts(df, representation):
    if representation == "full": col = "Narrative_1"
    elif representation == "event": col = "circumstance_text_raw"
    else: raise ValueError(representation)
    return df[col].fillna("").map(norm).tolist()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="Benchmark sample CSV with circumstance_text_raw")
    p.add_argument("--output", required=True)
    p.add_argument("--representation", choices=["full", "event", "event_lsa"], default="event")
    p.add_argument("--clusters", type=int, default=6)
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--train-fraction", type=float, default=0.8)
    p.add_argument("--holdout-fraction", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    src, dst = Path(args.input), Path(args.output)
    if not src.exists(): raise FileNotFoundError(src)
    if dst.exists(): raise FileExistsError(f"Refusing to overwrite {dst}")
    if args.repeats < 3: raise ValueError("Use at least 3 repeats.")
    if not 0.5 <= args.train_fraction < 1 or not 0.1 <= args.holdout_fraction < 0.5:
        raise ValueError("Invalid train/holdout fractions.")

    df = pd.read_csv(src, low_memory=False)
    if "Source_Year" not in df or "CPSC_Case_Number" not in df:
        raise ValueError("Source_Year and CPSC_Case_Number required.")
    texts = make_texts(df, "full" if args.representation == "full" else "event")
    n = len(texts)
    rng = np.random.default_rng(args.seed)
    all_idx = np.arange(n)
    holdout_idx = []
    train_pool_idx = []
    # Fixed stratified holdout by year, with all other rows in the train pool.
    for _, group in df.groupby("Source_Year", sort=True):
        idx = group.index.to_numpy()
        n_hold = max(1, int(round(len(idx) * args.holdout_fraction)))
        chosen = rng.choice(idx, size=n_hold, replace=False)
        holdout_idx.extend(chosen.tolist())
        train_pool_idx.extend(np.setdiff1d(idx, chosen, assume_unique=False).tolist())
    holdout_idx = np.array(sorted(holdout_idx), dtype=int)
    train_pool_idx = np.array(sorted(train_pool_idx), dtype=int)
    holdout_texts = [texts[i] for i in holdout_idx]
    predictions = []

    for repeat in range(args.repeats):
        m = max(args.clusters + 2, int(round(len(train_pool_idx) * args.train_fraction)))
        train_idx = np.sort(rng.choice(train_pool_idx, size=m, replace=False))
        train_texts = [texts[i] for i in train_idx]
        vec = TfidfVectorizer(stop_words=STOP, ngram_range=(1, 2), min_df=3, max_df=.95, max_features=30000, sublinear_tf=True, strip_accents="unicode")
        X_train = vec.fit_transform(train_texts)
        X_hold = vec.transform(holdout_texts)
        if args.representation == "event_lsa":
            n_comp = min(100, X_train.shape[0] - 1, X_train.shape[1] - 1)
            svd = TruncatedSVD(n_components=n_comp, random_state=args.seed + repeat, n_iter=7)
            X_train = Normalizer(copy=False).fit_transform(svd.fit_transform(X_train))
            X_hold = Normalizer(copy=False).transform(svd.transform(X_hold))
        model = KMeans(n_clusters=args.clusters, random_state=args.seed + repeat, n_init=20, max_iter=500)
        model.fit(X_train)
        pred = model.predict(X_hold)
        predictions.append(pred)
        print(f"Repeat {repeat + 1}/{args.repeats}: holdout assignments created")

    pairwise = []
    for i in range(len(predictions)):
        for j in range(i + 1, len(predictions)):
            pairwise.append(float(adjusted_rand_score(predictions[i], predictions[j])))
    report = {
        "input_file": str(src), "representation": args.representation,
        "n_rows": n, "n_holdout": int(len(holdout_idx)),
        "clusters": args.clusters, "repeats": args.repeats,
        "train_fraction_of_train_pool": args.train_fraction,
        "holdout_fraction_by_year": args.holdout_fraction,
        "seed": args.seed, "pairwise_ari": pairwise,
        "mean_pairwise_ari": float(np.mean(pairwise)),
        "std_pairwise_ari": float(np.std(pairwise, ddof=1)) if len(pairwise) > 1 else 0.0,
        "warning": "ARI is repeatability of assignments on a common holdout, not semantic correctness or human theme coherence."
    }
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__": main()
