# Discovering Fall Injury Patterns in Medical Narratives

**Status:** exploratory research prototype with a local Explorer dashboard. The assigned DrivenData source was substituted with prepared CPSC NEISS 2019–2022 data; written instructor approval is still required.

## Official project allocation

**Objectives (copied from allocation):**
1. Build a discovery system that clusters narratives into recurring circumstance patterns and quantifies each.
2. Produce a clustering of narratives with named themes and their share of incidents.
3. Report silhouette, cluster stability, human-rated theme coherence.

**Required baseline and deliverable:** keyword-frequency counts and an Explorer dashboard with theme drill-down.

## Important dataset caveat

The allocated source was the DrivenData competition *Unsupervised Wisdom: Explore Medical Narratives on Older Adult Falls*. The working data used in the current experiments is a prepared subset of CPSC NEISS annual public-use data (2019–2022), because the allocated event/data access was unavailable. This is a dataset substitution, not the original competition data. **Obtain written instructor approval before submission.**

NEISS covers consumer-product-related emergency-department injury visits; it is not a census of all older-adult falls. The 201,627 records are **keyword-screened candidates, not confirmed falls**. The keyword filter can include false positives and miss falls phrased differently. Never describe the candidate count or cluster shares as prevalence among all older adults.

Official sources:
- DrivenData allocation: https://www.drivendata.org/competitions/217/cdc-fall-narratives/
- CPSC NEISS data portal: https://www.cpsc.gov/Research--Statistics/NEISS-Injury-Data

Full datasets are local and excluded from Git. Do not commit raw/full CSVs or private records.

## What's completed

- Python project and virtual environment setup.
- NEISS 2019–2022 preparation and source audit.
- 201,627 keyword-screened candidates across 2019–2022.
- Keyword-frequency baseline.
- 20-record manual fall-label pilot: 19 labelled "yes" and 1 labelled "no" by one reviewer. This small sequential pilot is not a representative estimate of candidate precision.
- Four six-cluster TF-IDF + KMeans pilot runs on the same 5,000-record experiment sample.
- V2/V4 subsample stability pilot (three pairwise comparisons per model).
- V4 human theme-coherence pilot: six clusters, three sampled examples per cluster, one reviewer.
- Local Streamlit Explorer dashboard with filters, cluster drill-down and downloadable ratings.

See [pilot experiment results](report/PILOT_EXPERIMENTS_5000.md) and [fast-track checklist](report/FAST_TRACK_CHECKLIST.md).

## Setup

Use Python 3.10 or 3.11:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the Explorer

```powershell
streamlit run app\streamlit_app.py
```

Select the original control, V2, V3 or V4 local assignments. The app supports cluster and year filtering, narrative search, record inspection, filtered-record export, and one-reviewer coherence ratings saved locally to `results/human_coherence_ratings.csv`.

## Pilot model comparison (same 5,000 narratives, 6 clusters)

| Model | Sampled silhouette | Largest cluster | Largest-cluster share |
|---|---:|---:|---:|
| Original control | 0.00680 | 1,604 | 32.08% |
| V2 | 0.01187 | 3,071 | 61.42% |
| V3 | 0.00764 | 2,433 | 48.66% |
| V4 | 0.00775 | 3,127 | 62.54% |

All four silhouette scores are close to zero, indicating weak separation in the TF-IDF feature space. V2 has the highest pilot silhouette but a highly dominant cluster. V4 has the best measured V2/V4 subsample stability and has been human-rated, but its dominant cluster is also very large. **Do not claim a validated winning model.**

## Stability pilot (V2 vs V4)

The local command `python src\compare_stability.py --repeats 3 --output results\stability_comparison_5000_fasttrack.json` completed successfully.

| Model | Mean pairwise ARI | Standard deviation | Pairwise comparisons |
|---|---:|---:|---:|
| V2 | 0.5010 | 0.1192 | 3 |
| V4 | 0.6502 | 0.1430 | 3 |

V4 showed higher agreement across these repeated subsample comparisons. This is a small exploratory stability pilot, not proof of semantic correctness or a precise population estimate.

## V4 human-rated theme coherence pilot

One reviewer (R1) inspected three reproducibly sampled narratives in each of the six V4 clusters and saved one rating per cluster in `results/human_coherence_ratings.csv`.

| Cluster | Provisional working theme | Coherence rating |
|---|---|---:|
| 0 | Falls to floor – mixed mechanisms | 2/5 |
| 1 | Loss of balance while walking | 4/5 |
| 2 | Mixed fall circumstances (general) | 2/5 |
| 3 | Falls involving impact with nearby objects | 3/5 |
| 4 | Falls in nursing-home settings | 4/5 |
| 5 | Falls from bed | 5/5 |
| **Mean** | **Equal-weight mean across six clusters** | **3.33/5** |

This represents 18 example-level judgments by one reviewer, not 18 independent raters and not inter-rater reliability. The ratings are a pilot qualitative assessment; cluster 2 is especially broad and weakly coherent.

V4 cluster shares within the 5,000 loaded candidate records:

| Cluster | Records | Share of loaded candidates |
|---|---:|---:|
| 0 | 171 | 3.42% |
| 1 | 249 | 4.98% |
| 2 | 3,127 | 62.54% |
| 3 | 855 | 17.10% |
| 4 | 208 | 4.16% |
| 5 | 390 | 7.80% |

These percentages are shares of this 5,000-record keyword-screened sample only. They are not all-incident shares or population prevalence.

## Existing scripts

- `src/eda.py`: exploratory data summaries and figures.
- `src/keyword_frequency_baseline.py`: required keyword-frequency baseline.
- `src/run_experiment.py`: TF-IDF + KMeans assignments and sampled silhouette.
- `src/stability.py`: subsample stability helper.
- `src/compare_stability.py`: quick V2/V4 stability comparison.

## Reproducibility and interpretation

- Fixed random state: 42.
- Pilot sample: 5,000 records. Confirm and describe the exact sampling procedure from the local sample-generation script before final submission.
- Clustering: TF-IDF word unigrams/bigrams + KMeans, six clusters.
- Silhouette is sampled by the prototype; report it as such.
- ARI stability measures agreement across repeated subsamples, not semantic correctness.
- Human coherence ratings are single-reviewer pilot judgments, not inter-rater reliability.
- Keyword groups overlap; their shares must not be summed to 100%.
- Keep the exploratory warning wherever candidate records or candidate shares are displayed.

## Still required before final submission

1. Written instructor approval for the NEISS substitution.
2. Decide, with the instructor's scope in mind, whether to run the selected exploratory pipeline on all 201,627 candidates. Do not call that a confirmed-fall dataset.
3. If a full-candidate run is completed, report its exact cluster counts/shares and sampled silhouette; do not reuse the 5,000-record pilot metrics as full-data results.
4. Final report and presentation using the instructor's required template.
5. Student review of all code, results and AI-tool disclosure according to course rules.

## AI-tool disclosure

ChatGPT assisted with planning, code scaffolding, debugging support and documentation. The team must review, understand, test and disclose the assistance actually used, following course guidelines.
