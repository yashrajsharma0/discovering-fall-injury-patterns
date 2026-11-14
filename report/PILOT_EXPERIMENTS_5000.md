# 5,000-record pilot experiment and evaluation results

**Scope:** Four TF-IDF + KMeans experiments run locally on the same 5,000-record candidate sample, each requesting six clusters. These are exploratory candidate-narrative results, not final findings.

## Sample

The four experiments used the same 5,000-record CSV sample. The original candidate file contains 201,627 records; those are not confirmed falls. Confirm and describe the exact sampling procedure from the local sample-generation script before final submission.

## Clustering results observed in local runs

| Model | Sampled silhouette | Cluster sizes (IDs 0–5) | Largest-cluster share |
|---|---:|---|---:|
| Original control | 0.00680 | 1,458; 469; 244; 844; 381; 1,604 | 32.08% |
| V2 | 0.01187 | 527; 614; 211; 3,071; 251; 326 | 61.42% |
| V3 | 0.00764 | 2,433; 379; 626; 778; 485; 299 | 48.66% |
| V4 | 0.00775 | 171; 249; 3,127; 855; 208; 390 | 62.54% |

The values above were captured from the local experiment outputs. `silhouette_score_sampled` is a sampled silhouette score, not a full-data score.

### Interpretation

- All four scores are close to zero; the clusters are weakly separated in TF-IDF space.
- V2 has the highest numerical score in this pilot, but cluster 3 contains 61.42% of all records.
- V4 preserves circumstance context in several inspected narratives, but cluster 2 contains 62.54% of records.
- The original model is more evenly distributed than V2/V4, but its top terms show substantial injury/diagnosis vocabulary.
- No model is established as a validated winner from silhouette and sample examples alone.

## Subsample stability pilot: V2 vs V4

The local command used three repeats and an 0.8 sample fraction, producing three pairwise comparisons for each model. The script saved `results/stability_comparison_5000_fasttrack.json`.

| Model | Mean pairwise ARI | Standard deviation | Pairwise comparisons |
|---|---:|---:|---:|
| V2 | 0.5010 | 0.1192 | 3 |
| V4 | 0.6502 | 0.1430 | 3 |

V4 showed higher agreement than V2 across this small pilot. ARI measures agreement between clustering runs on overlapping subsamples; it does not show that a cluster is a meaningful or correct human theme. Three pairwise comparisons are limited evidence and should be described as a pilot.

## Human-rated theme coherence: V4

One reviewer (R1) inspected three reproducibly sampled example narratives from each of the six V4 clusters (18 example narratives total) and saved one rating per cluster.

| Cluster | Provisional working theme | Rating |
|---|---|---:|
| 0 | Falls to floor – mixed mechanisms | 2/5 |
| 1 | Loss of balance while walking | 4/5 |
| 2 | Mixed fall circumstances (general) | 2/5 |
| 3 | Falls involving impact with nearby objects | 3/5 |
| 4 | Falls in nursing-home settings | 4/5 |
| 5 | Falls from bed | 5/5 |
| **Mean** | **Equal-weight mean of six cluster ratings** | **3.33/5** |

The rating is an exploratory, single-reviewer coherence assessment. Three examples per cluster are not sufficient to establish cluster-wide coherence, and no inter-rater reliability was measured. Cluster 2 is particularly broad: 3,127 of 5,000 records (62.54%) and a 2/5 coherence rating. Its provisional label should not be interpreted as a well-defined circumstance theme.

### V4 cluster shares in the 5,000-record sample

| Cluster | Records | Share |
|---|---:|---:|
| 0 | 171 | 3.42% |
| 1 | 249 | 4.98% |
| 2 | 3,127 | 62.54% |
| 3 | 855 | 17.10% |
| 4 | 208 | 4.16% |
| 5 | 390 | 7.80% |

Shares describe only the loaded 5,000-record keyword-screened sample, not all falls or population prevalence.

## Manual fall-label review pilot

Twenty records were manually classified by one reviewer: 19 labelled `yes` and 1 labelled `no`. This was a small sequential pilot from the beginning of the 2019 records, not a representative stratified sample. The 95% observed yes share must not be presented as the precision of the 201,627-record candidate set.

## Provisional conclusion

V4 is the stronger *provisional candidate for further exploration* because its V2/V4 stability pilot was higher (mean ARI 0.6502 vs 0.5010) and its six sampled clusters received a mean one-reviewer coherence rating of 3.33/5. However, V4's sampled silhouette is only 0.00775 and its largest cluster accounts for 62.54% of the sample, with low coherence (2/5). V2 has a higher silhouette (0.01187) but also has a dominant 61.42% cluster, and a comparable human-coherence assessment of V2 has not been completed. Therefore **do not claim V4 or V2 is validated or definitively superior**.

## Required caveats

1. NEISS is a substitute for the assigned DrivenData dataset; written instructor approval is required.
2. NEISS represents consumer-product-related ED injury visits, not all falls in the community.
3. Keyword candidates can include false positives and false negatives.
4. Shares from these 5,000 candidates are not population prevalence.
5. The human coherence sample is small and single-reviewer; stability uses only three pairwise comparisons.
6. Full 201,627-candidate model results have not been generated in this pilot report and must not be implied.
