# Discovering Fall Injury Patterns in Medical Narratives

**Status: working prototype; dataset substitution documented; validation and model evaluation still in progress.**

## Official project allocation
**Topic:** Discovering Fall Injury Patterns in Medical Narratives

**Problem statement (from allocation):** Older adult falls are recorded as free-text narratives that nobody reads in aggregate, so prevention is designed on assumption.

**Objectives (copied from allocation):**
1. Build a discovery system that clusters narratives into recurring circumstance patterns and quantifies each.
2. Produce a clustering of narratives with named themes and their share of incidents.
3. Report silhouette, cluster stability, human-rated theme coherence.

**Mandatory baseline and deliverable (from allocation):** Baseline: keyword frequency counts. Deliver Explorer dashboard with theme drill-down.

**Assigned source:** DrivenData — *Unsupervised Wisdom: Explore Medical Narratives on Older Adult Falls*. Organizer: DrivenData (challenge sponsor stated on the official page — VR). Dataset access: competition dataset (platform account / rules acceptance).

Official link: https://www.drivendata.org/competitions/217/cdc-fall-narratives/

## Research goal
Discover recurring circumstance themes in older-adult fall narratives, quantify each theme's share, assess silhouette and cluster stability, and arrange a human-rated coherence review. Compare against the allocated keyword-frequency baseline and provide an Explorer dashboard with theme drill-down.

## Important dataset caveat
The team has selected a prepared subset derived from CPSC NEISS annual public data (2019–2022) as its **working dataset**, because the allocated DrivenData event has ended. This is a documented substitution, not the same dataset. NEISS focuses on consumer-product-related ED injuries. The keyword-filtered records are *candidates*, not confirmed fall cases. Obtain instructor written approval for the substitution and check the source terms before redistributing any data. Official portal: https://www.cpsc.gov/Research--Statistics/NEISS-Injury-Data

The repository includes only a small sample and a 160-record manual-review template. Do not commit the full data files. The full prepared CSV should be stored in an approved data host and downloaded separately.

## Project structure
- `data/`: small example sample and dataset notes
- `notebooks/`: EDA and experiments (to be added)
- `src/`: cleaning, keyword baseline, clustering model, EDA and stability evaluation
- `app/`: Streamlit Explorer prototype
- `results/`: source validation summary and generated experiment outputs
- `report/`: final report PDF (to be added after real evaluation)
- `presentation/`: final slides (to be added)

## Setup
Use Python 3.10 or 3.11 in a virtual environment.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run a small smoke-test experiment
From the repository root:

```bash
python src/run_experiment.py --input data/sample_fall_candidates.csv --clusters 6
streamlit run app/streamlit_app.py
```

The sample is for testing the pipeline only. Metrics generated on it are not final project results. For the full experiment, download the approved dataset and pass its local path to `--input`.

## Data validation and human coherence review

Open `data/manual_validation_template.csv` and code each reviewed narrative using `is_actual_fall` (`yes`, `no`, `uncertain`), confidence (1–3), and a short circumstance theme. Do not infer a fall solely from a keyword match. Preserve the review decisions and summarize reviewer agreement where multiple reviewers are available. This human review is necessary before making claims about candidate precision or human-rated theme coherence.

Run EDA on the full local candidate CSV with:

```bash
python src/eda.py --input PATH_TO/neiss_2019_2022_fall_candidates.csv --out results/eda
```

The stability helper is available in `src/stability.py`; report its settings and ARI results only after actually running it on the selected data.

## Reproducibility
- Fixed random seed: 42
- Clustering prototype: TF-IDF word uni/bi-grams + KMeans
- Transparent baseline: rule-based keyword grouping
- Generated assignments and summary metrics are saved under `results/`
- Do not report numbers until data validation, manual review, objective alignment and full-run testing are complete.

## Required before submission
1. Obtain and retain written instructor approval for the NEISS dataset substitution.
2. Validate a stratified sample of candidate narratives and document false positives/false negatives; never call keyword candidates confirmed falls without evidence.
3. Run EDA and experiments on the approved data. Include silhouette, cluster stability, human-rated theme coherence, the required keyword-frequency baseline, theme shares, and Explorer dashboard drill-down.
4. Complete the report using the supplied CA-1 template and slides/demo. Report only reproducible results generated by this implementation.

## AI-tool disclosure
This project has been developed with assistance from ChatGPT for planning, code scaffolding, debugging support and documentation. The team must review, understand, test and accurately disclose the assistance actually used, as required by the course guidelines.
