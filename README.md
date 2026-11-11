# Discovering Fall Injury Patterns in Medical Narratives

**Status:** reproducible exploratory pipeline and local Explorer dashboard. Dataset substitution and candidate-label limitations are documented below.

## Official project allocation

**Topic:** Discovering Fall Injury Patterns in Medical Narratives

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

## What's already done

- Python project and virtual environment setup.
- NEISS 2019–2022 preparation and source audit.
- 201,627 keyword-screened candidates across 2019–2022.
- Keyword-frequency baseline.
- Twenty-record manual pilot review: 19 marked as falls and 1 as not a fall. This was a small sequential 2019 pilot, not a representative estimate of candidate precision.
- A reproducible 5,000-record sample with year mix: 2019 = 1,257; 2020 = 1,178; 2021 = 1,300; 2022 = 1,265.
- Four 6-cluster TF-IDF + KMeans pilot runs on the same 5,000 records. The measured silhouette scores were all very low; none is established as a final model.

See [pilot experiment results](report/PILOT_EXPERIMENTS_5000.md) and [fast-track checklist](report/FAST_TRACK_CHECKLIST.md).

## Setup

Use Python 3.10 or 3.11:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Fastest remaining workflow

1. Bring in the latest project branch (instructions are in the PR).
2. Run the V2-versus-V4 stability pilot:

```powershell
python src\compare_stability.py --repeats 3
```

The script compares mean pairwise adjusted Rand index (ARI) across overlapping random subsamples. It reads the existing 5,000-record assignments and writes `results/stability_comparison_5000.json`. Three repeats are a quick pilot, not a high-precision stability estimate.

3. Launch the Explorer:

```powershell
streamlit run app\streamlit_app.py
```

The app discovers local result files for the original control, V2, V3 and V4. Select a cluster, inspect examples, filter by year/search text, and download filtered records.

4. In the dashboard's **Human-rated theme coherence** section, inspect three reproducibly sampled examples per cluster, give each cluster a short working name, and rate consistency from 1 (not coherent) to 5 (very coherent). The app saves ratings to `results/human_coherence_ratings.csv`. This is a single-reviewer pilot; do not claim inter-rater reliability.

## Existing scripts

- `src/eda.py`: exploratory data summaries and figures.
- `src/keyword_frequency_baseline.py`: required keyword-frequency baseline.
- `src/run_experiment.py`: TF-IDF + KMeans assignments and sampled silhouette.
- `src/stability.py`: subsample stability helper.
- `src/compare_stability.py`: quick V2/V4 stability comparison.

## Pilot model comparison (same 5,000 narratives, 6 clusters)

| Model | Sampled silhouette | Largest cluster | Largest-cluster share |
|---|---:|---:|---:|
| Original control | 0.00680 | 1,604 | 32.08% |
| V2 | 0.01187 | 3,071 | 61.42% |
| V3 | 0.00764 | 2,433 | 48.66% |
| V4 | 0.00775 | 3,127 | 62.54% |

These scores are close to zero and indicate weakly separated clusters. V2 has the highest score in this pilot, but its largest cluster contains 61.42% of the sample. This is not enough evidence to declare V2 the winner. Theme names must be based on inspecting actual narratives and human ratings.

## Reproducibility and interpretation

- Fixed random state: 42.
- Pilot sample: 5,000 records, sampled with a year-proportional allocation from the keyword candidate file.
- Clustering: TF-IDF word unigrams/bigrams + KMeans, six clusters.
- Silhouette is sampled by the prototype; report it as such.
- ARI stability measures agreement across overlapping subsamples, not semantic correctness.
- Human coherence ratings in this repository are single-reviewer pilot judgments, not inter-rater reliability.
- Keyword groups overlap; their shares must not be summed to 100%.
- Keep the exploratory warning wherever candidate records or candidate shares are displayed.

## Still required before final submission

1. Written instructor approval for the NEISS substitution.
2. A broader and appropriately sampled human validation review, or explicit reporting that validation remains a small pilot.
3. Completed stability evaluation and human coherence ratings, with settings and limitations.
4. Defensible named themes, theme counts/shares, and full-data rerun only after selecting a model.
5. Final report and presentation using the instructor's required template.
6. Student review of all code, results and AI-tool disclosure according to course rules.

## AI-tool disclosure

ChatGPT assisted with planning, code scaffolding, debugging support and documentation. The team must review, understand, test and disclose the assistance actually used, following course guidelines.
