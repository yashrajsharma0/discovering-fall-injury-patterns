"""Run the first reproducible prototype. Use only on a validated candidate set."""
from pathlib import Path
import argparse, json
import pandas as pd
from preprocess import add_clean_text
from baseline import assign_baseline_group
from model import fit_cluster_model, top_terms_by_cluster

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=str(ROOT / 'data' / 'sample_fall_candidates.csv'))
    parser.add_argument('--output-dir', default=str(ROOT / 'results'))
    parser.add_argument('--clusters', type=int, default=6)
    parser.add_argument('--max-rows', type=int, default=0, help='Optional row cap for smoke tests; 0 means all rows')
    args = parser.parse_args()
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.input, low_memory=False)
    if args.max_rows:
        df = df.head(args.max_rows)
    df, source_col = add_clean_text(df)
    if len(df) < 10:
        raise SystemExit('Too few non-empty narratives. Supply a larger dataset.')
    df['baseline_group'] = df['clean_text'].map(assign_baseline_group)
    vectorizer, model, matrix, labels, silhouette = fit_cluster_model(df['clean_text'], n_clusters=args.clusters)
    df['cluster_id'] = labels
    df.to_csv(out / 'prototype_assignments.csv', index=False)
    summary = {
        'input_file': str(Path(args.input).name), 'rows_used': int(len(df)),
        'text_column': source_col, 'n_clusters_requested': int(args.clusters),
        'cluster_sizes': {str(k): int(v) for k, v in df['cluster_id'].value_counts().sort_index().items()},
        'baseline_group_sizes': {str(k): int(v) for k, v in df['baseline_group'].value_counts().items()},
        'silhouette_score_sampled': silhouette,
        'top_terms_by_cluster': top_terms_by_cluster(vectorizer, model),
        'warning': 'Exploratory prototype only. Keyword candidates are not verified fall labels; do not report these as final results.'
    }
    (out / 'prototype_metrics.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
