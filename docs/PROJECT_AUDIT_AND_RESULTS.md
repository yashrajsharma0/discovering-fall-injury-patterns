# Project audit and refreshed experimental results

**Prepared:** 17 November 2026
**Scope:** Uploaded project files and NEISS candidate data; new controlled 5k/10k experiments; full 201,627-candidate exploratory clustering; HDBSCAN alternative check.

## 1. Executive decision

The original TF–IDF + K-Means prototype did not establish coherent circumstance themes. A new, reproducible pipeline is now available: conservative DX-aware incident-text extraction → negation-preserving domain TF–IDF → 100-dimensional TruncatedSVD (LSA) → L2 normalization → K-Means. Across two stratified samples, event-text LSA with K=8 had higher holdout assignment repeatability than the tested TF–IDF controls and K=10 LSA. A full-frame K=8 run was completed across all 201,627 keyword-screened candidates.

**Decision:** treat event-text LSA K=8 as the *provisional candidate for human theme-coherence review*, not as a validated winner. K=10 has higher sampled silhouette and smaller largest clusters, but lower holdout repeatability and may fragment themes. HDBSCAN was tested and is not selected because it labelled 57%–84% of the 5k sample as noise at the tested settings. No algorithm has yet been shown to discover clinically or operationally valid themes through independent human evaluation.

The dataset substitution remains a critical scope limitation: the input rows are NEISS 2019–2022, age 65+, keyword-screened candidates, **not confirmed falls and not all older-adult falls**. Obtain written instructor approval before submission.

## 2. Dataset and screening audit

The prepared data contains 257,245 NEISS records for people aged 65+ in 2019–2022 and 201,627 broad fall-keyword candidates.

| Year | Age-65+ NEISS rows | Keyword candidates | Candidate-screen share |
|---|---:|---:|---:|
| 2019 | 65,977 | 50,672 | 76.80% |
| 2020 | 60,343 | 47,502 | 78.72% |
| 2021 | 66,769 | 52,440 | 78.54% |
| 2022 | 64,156 | 51,013 | 79.51% |
| **Total** | **257,245** | **201,627** | **78.38%** |

The candidate-screen share is a property of the keyword rule, not prevalence or accuracy. NEISS is a probability sample of consumer-product-associated emergency-department injury visits. It is not a census of all falls or older adults. CPSC explains that case weights support national point estimates and cautions against using raw sample counts for comparative estimates.

Prepared-file audit:
- 0 candidate year/case keys outside the age-65+ universe in the uploaded audit.
- 0 missing narratives and 0 missing case numbers in that universe audit.
- 0 duplicate year/case keys in the universe audit.
- 670 repeated narrative rows in the universe; these were reported, not automatically removed.
- The prepared candidate CSV includes `Weight` but lacks the NEISS `Stratum` and `PSU` design variables. Therefore, this pack reports weighted point estimates only; it does not calculate design-based standard errors or confidence intervals.

## 3. Fall-screen validation status

A 160-record stratified sample was created: 20 candidates and 20 non-candidates for each year (2019–2022). Each row has design weight `sampling_frame_n / sample_n_in_stratum`.

The AI-assisted draft contains 83 yes, 62 no and 15 uncertain labels. Four suggestions were subsequently approved by the user in chat. These remain **AI-assisted labels**, not independent human reference labels. The old 20-record sequential review (19 yes, 1 no) is not representative and must not be used as a screening-accuracy estimate.

Separate blinded R1/R2 review files and an internal analysis key are supplied. Reviewers must not see the internal key or each other's responses. The merge script calculates raw agreement and Cohen's kappa, keeps disagreements unresolved, and requires human adjudication. The screening-metrics script refuses AI-only or unresolved labels. Therefore, screening precision/recall is **not yet available**.

## 4. Parser and representation findings

### Earlier issue found in the local prototype

The earlier TF–IDF model used scikit-learn's built-in English stop-word set, which removes important negation terms. The local model was changed to retain `no`, `nor`, `not`, `never`, `neither`, `none` and `without`. In the 5,000-narrative audit, `no` occurred in 233 documents, `not` in 96 and `without` in 49; the cleaned text retained all occurrences. `never` occurred once and was excluded by `min_df=2`, not by the stop-word set.

### DX-aware extraction

A sample audit initially found many DX formats beyond `DX:`. Parser V3 was then tested on all 201,627 candidates. It extracts only the prefix before the first recognized DX boundary, preserves the original narrative and flags ambiguous patterns.

| Parser method | Records |
|---|---:|
| Split at first DX | 195,217 |
| Full narrative, no DX | 6,322 |
| Full narrative, unparsed DX substring suspect | 68 |
| Full narrative, leading-DX review | 20 |
| Multiple-marker review flags | 788 |

The parser is heuristic, not a clinical NLP parser. The 788 multiple-marker cases and 68 unparsed suspects should be inspected. Records without a recognized DX marker keep the full narrative and may still contain diagnosis text. Original source text is never overwritten.

## 5. Controlled 5k and 10k benchmarks

A new deterministic sample was drawn from the uploaded candidate CSV, stratified by source year and sampled without replacement (seed 42): 1,250 rows/year for 5k and 2,500 rows/year for 10k. This is a fresh benchmark sample and is not identical to the user's earlier local `experiment_sample_5000.csv`.

Variants:
1. Full narrative + negation-preserving domain TF–IDF + K-Means.
2. DX-aware event text + the same TF–IDF + K-Means.
3. DX-aware event text + TF–IDF → 100D LSA → L2 normalization + K-Means.

Silhouette is computed in cosine distance for TF–IDF and Euclidean distance in normalized LSA space. Scores from different spaces are **not direct apples-to-apples comparisons**.

### 5k benchmark

| Representation | K | Sampled silhouette | Silhouette space | Largest cluster |
|---|---:|---:|---|---:|
| Full TF–IDF | 4 | 0.01455 | cosine / TF–IDF | 59.50% |
| Full TF–IDF | 6 | 0.01876 | cosine / TF–IDF | 47.18% |
| Full TF–IDF | 8 | 0.02131 | cosine / TF–IDF | 41.50% |
| Full TF–IDF | 10 | 0.02360 | cosine / TF–IDF | 23.78% |
| Event TF–IDF | 4 | 0.01946 | cosine / TF–IDF | 64.78% |
| Event TF–IDF | 6 | 0.02991 | cosine / TF–IDF | 58.24% |
| Event TF–IDF | 8 | 0.03113 | cosine / TF–IDF | 57.60% |
| Event TF–IDF | 10 | 0.03422 | cosine / TF–IDF | 46.16% |
| Event LSA | 4 | 0.03560 | Euclidean / normalized LSA | 55.28% |
| Event LSA | 6 | 0.05090 | Euclidean / normalized LSA | 41.22% |
| **Event LSA** | **8** | **0.06553** | **Euclidean / normalized LSA** | **34.86%** |
| Event LSA | 10 | 0.07094 | Euclidean / normalized LSA | 28.68% |

### 10k benchmark

| Representation | K | Sampled silhouette | Silhouette space | Largest cluster |
|---|---:|---:|---|---:|
| Full TF–IDF | 6 | 0.01628 | cosine / TF–IDF | 51.38% |
| Full TF–IDF | 8 | 0.01857 | cosine / TF–IDF | 41.74% |
| Full TF–IDF | 10 | 0.01672 | cosine / TF–IDF | 40.00% |
| Event TF–IDF | 6 | 0.01735 | cosine / TF–IDF | 65.42% |
| Event TF–IDF | 8 | 0.01846 | cosine / TF–IDF | 54.79% |
| Event TF–IDF | 10 | 0.01463 | cosine / TF–IDF | 41.66% |
| Event LSA | 6 | 0.05078 | Euclidean / normalized LSA | 48.25% |
| **Event LSA** | **8** | **0.06345** | **Euclidean / normalized LSA** | **34.84%** |
| Event LSA | 10 | 0.07201 | Euclidean / normalized LSA | 28.86% |

The LSA scores remain modest rather than demonstrating clear, well-separated themes. K=10's smaller maximum cluster may indicate better granularity or over-fragmentation; the human reviewers must decide whether those groups are coherent.

### Correcting NEISS weights in balanced-by-year samples

Because the benchmark takes the same number of records from each year, summing raw NEISS `Weight` values alone would not expand the sample back to the full candidate frame correctly. The benchmark instead uses:

`candidate_frame_analysis_weight = NEISS Weight × (candidate rows in year / sampled rows in year)`.

This is an expansion of NEISS weighted point estimates within the keyword-candidate frame. It does not turn candidates into all falls. `Stratum` and `PSU` are missing, so no design-based variance is calculated.

## 6. Holdout stability

A fixed 20%-per-year holdout is retained. Each of five repeats refits the vectorizer (and LSA where relevant) on a different 80% sample of the remaining training pool, predicts the same holdout, then computes pairwise ARI across the ten pairs. ARI here is assignment repeatability, not semantic correctness.

| Sample | Representation | K | Holdout rows | Repeats | Mean pairwise ARI | SD |
|---|---|---:|---:|---:|---:|---:|
| 5k | Full TF–IDF | 8 | 1,000 | 5 | 0.4351 | 0.0912 |
| 5k | Event TF–IDF | 8 | 1,000 | 5 | 0.4832 | 0.1600 |
| 5k | Event LSA | 8 | 1,000 | 5 | **0.8205** | 0.1115 |
| 5k | Event LSA | 10 | 1,000 | 5 | 0.6647 | 0.0651 |
| 10k | Event TF–IDF | 8 | 2,000 | 5 | 0.5182 | 0.1772 |
| 10k | Event LSA | 8 | 2,000 | 5 | **0.7759** | 0.1196 |
| 10k | Event LSA | 10 | 2,000 | 5 | 0.6391 | 0.1348 |

These results support reviewing LSA K=8 before K=10: K=8 was more repeatable in both sampled frames, while K=10 had higher within-LSA-space silhouette and smaller largest clusters. Human coherence remains the deciding validation gate.

## 7. HDBSCAN alternative check (5k LSA representation)

HDBSCAN was evaluated on the same 5k sample and 100D normalized LSA space with `min_samples=10` and `min_cluster_size` 30, 50 and 100.

| min cluster size | Non-noise clusters | Noise rows | Noise share | Non-noise-only sampled silhouette |
|---:|---:|---:|---:|---:|
| 30 | 17 | 4,125 | 82.50% | 0.4088 |
| 50 | 2 | 2,864 | 57.28% | 0.0426 |
| 100 | 3 | 4,185 | 83.70% | 0.1177 |

The high silhouette at minimum cluster size 30 applies only to 875 retained rows and excludes 82.5% of the sample labelled as noise. It is not directly comparable to K-Means silhouette computed over all rows. At min size 50 it yielded only two clusters. HDBSCAN is therefore documented as a tested alternative, not selected as the project default under these settings.

## 8. Full-candidate exploratory run (all 201,627 keyword candidates)

A full-frame run was completed using parser V3 → negation-preserving domain TF–IDF (30,000 features) → TruncatedSVD 100 components → L2 normalization → K-Means K=8 (seed 42, 10 initializations). The sum of the SVD explained variance ratios was 0.26828. Sampled silhouette was 0.06145 in Euclidean distance on normalized LSA vectors.

| Full-frame result | Value |
|---|---:|
| Candidate rows clustered | 201,627 |
| Largest cluster | 71,080 (35.253%) |
| Smallest cluster | 10,067 (4.993%) |
| NEISS-weighted candidate-frame total point estimate | 9,355,019.27 |

| Cluster | Raw records | Raw share | NEISS-weighted estimate | Weighted share in candidate frame |
|---:|---:|---:|---:|---:|
| 0 | 71,080 | 35.253% | 3,338,739.05 | 35.689% |
| 1 | 17,598 | 8.728% | 774,014.39 | 8.274% |
| 2 | 20,099 | 9.968% | 954,116.52 | 10.199% |
| 3 | 16,770 | 8.317% | 801,092.93 | 8.563% |
| 4 | 10,067 | 4.993% | 469,797.42 | 5.022% |
| 5 | 33,214 | 16.473% | 1,603,966.95 | 17.146% |
| 6 | 13,449 | 6.670% | 575,126.46 | 6.148% |
| 7 | 19,350 | 9.597% | 838,165.56 | 8.960% |

Because the full keyword-candidate frame was clustered, original NEISS `Weight` values are summed directly; no sample expansion factor is applied. These are weighted point estimates within the keyword-candidate frame only—not counts of all older-adult falls or all injuries. No design-based confidence intervals are reported because the prepared CSV lacks `Stratum` and `PSU`.

### AI-drafted theme hypotheses (not final theme names)

Spot inspection suggests candidate families such as bed/transfer falls, stair/step falls, trip/obstacle falls, slip/wet-surface falls, head/furniture impact, nursing-home/residential-care contexts, and broad general/unwitnessed mechanisms. Some clusters are broad or overlapping. The file `provisional_theme_hypotheses_AI_DRAFT.csv` is a review aid only. Review 10 cases per cluster in both independent R1/R2 theme-coherence sheets before assigning final names and shares.

## 9. Current completion status and remaining gates

- Objective 1: clustering and quantification implemented for all candidates, but recurrence patterns still need human validation.
- Objective 2: numeric cluster IDs and raw/weighted candidate-frame shares exist; final named themes and coherence are outstanding.
- Objective 3: silhouette and 5-repeat holdout ARI reported; independent human-rated coherence is outstanding.
- Baseline: existing keyword-frequency baseline remains the simple comparator; report its exact scope and overlapping-group caveat.
- Screening accuracy: not available. AI draft labels must not be used as ground truth. Two independent reviewers must label the 160-case stratified sample, disagreements must be adjudicated, and only then may weighted precision/recall be calculated.
- Dataset approval: written instructor approval for the NEISS substitution remains outstanding.
- Source design: recover `Stratum` and `PSU` from source workbooks before calculating design-based standard errors or confidence intervals.
- Dashboard: a new local Explorer source file is included; it is syntax-checked but Streamlit could not be run in this build environment because the Streamlit package is not installed. Test locally after copying into the user's project.
- Final report/slides: draft content and an 8–10 slide outline are supplied, but group/course identifiers and the official report template were not available here. Complete them in the instructor's required template.

## 10. Research basis

- WHO, *Falls* (21 October 2026): https://www.who.int/en/news-room/fact-sheets/detail/falls — definition of a fall as inadvertently coming to rest on the ground, floor or another lower level.
- CPSC, *Explanation of NEISS Estimates*: https://www.cpsc.gov/cgibin/NEISSQuery/webestimates.html — probability sample and case weights for national estimates; cautions against comparing raw sample counts.
- CPSC, *NEISS Frequently Asked Questions*: https://www.cpsc.gov/Research--Statistics/NEISS-Injury-Data/Neiss-Frequently-Asked-Questions — scope and data limitations.
- scikit-learn, *Clustering text documents using K-means*: https://scikit-learn.org/stable/auto_examples/text/plot_document_clustering.html — TF–IDF, K-Means and LSA/TruncatedSVD.
- scikit-learn, *Clustering performance evaluation*: https://scikit-learn.org/stable/modules/clustering.html — silhouette limitations and metric interpretation.
- Reimers & Gurevych (2019), *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*: https://aclanthology.org/D19-1410/.
- scikit-learn, *HDBSCAN*: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html — density-based clustering and noise assignments.
