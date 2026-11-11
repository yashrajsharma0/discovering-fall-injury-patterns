# 5,000-record pilot experiment comparison

**Scope:** Four TF-IDF + KMeans experiments run locally on the same reproducible 5,000-record sample, each requesting six clusters. These are exploratory candidate-narrative results, not final findings.

## Sample

The four experiments used the same 5,000-record CSV sample. The original candidate file contains 201,627 records; those are not confirmed falls. The sampling procedure should be confirmed from the local sample-generation script before final submission.

## Results observed in local runs

| Model | Sampled silhouette | Cluster sizes (IDs 0–5) | Largest-cluster share |
|---|---:|---|---:|
| Original control | 0.00680 | 1,458; 469; 244; 844; 381; 1,604 | 32.08% |
| V2 | 0.01187 | 527; 614; 211; 3,071; 251; 326 | 61.42% |
| V3 | 0.00764 | 2,433; 379; 626; 778; 485; 299 | 48.66% |
| V4 | 0.00775 | 171; 249; 3,127; 855; 208; 390 | 62.54% |

The values above were captured from the local experiment outputs. `silhouette_score_sampled` is a sampled silhouette score, not a full-data score.

## Interpretation

- All four scores are close to zero; the clusters are weakly separated in TF-IDF space.
- V2 has the highest numerical score in this pilot, but cluster 3 contains 61.42% of all records. It is not automatically the best theme solution.
- V4 preserves more context in several inspected narratives, but cluster 2 contains 62.54% of records.
- The original model is more evenly distributed than V2/V4, but its top terms show substantial injury/diagnosis vocabulary.
- Cluster terms and a few example records are not enough to validate themes. Inspect a fixed random sample within every cluster and use the dashboard's human coherence rubric.

**Decision:** Do not claim a final winning model from these results alone. Use V2 and V4 for the quick stability and human-coherence pilot. If neither yields coherent, stable themes, report this limitation rather than inventing an improvement.

## Human-review pilot completed

Three records have been manually reviewed so far by one reviewer, and all three explicitly describe falls. This is only a tiny workflow pilot; it cannot estimate precision or validate the full candidate set.

## Required caveats

1. NEISS is a substitute for the assigned DrivenData dataset; written instructor approval is required.
2. NEISS represents consumer-product-related ED injury visits, not all falls in the community.
3. Keyword candidates can include false positives and false negatives.
4. Shares from these 5,000 candidates are not population prevalence.
5. The stability and coherence sections remain to be completed from actual outputs.
