# Fall Injury Narrative Project — improvement and handoff pack

This pack adds a conservative DX-aware parser, controlled TF–IDF/LSA experiments, holdout stability evaluation, HDBSCAN alternative results, a full 201,627-candidate exploratory clustering run, blinded fall-label review, blinded cluster-coherence review and a NEISS-weight-aware local Explorer.

**The project is not fully validated.** Event-text LSA K=8 is a provisional candidate for human review, not a proved winning model. The rows are broad keyword-screened NEISS candidates, not confirmed falls. Written instructor approval for the source substitution remains necessary.

## Pack contents

- `src/build_circumstance_text_v3.py` — conservative DX boundary extraction, original-text preservation and ambiguity flags.
- `src/run_discovery_benchmark.py` — controlled full-text TF–IDF, event-text TF–IDF and event-text LSA benchmarks; stratified by year; corrected expansion weights for the balanced-by-year samples.
- `src/evaluate_holdout_stability.py` — five-repeat refit stability on a fixed holdout; reports pairwise ARI.
- `src/run_hdbscan_lsa_benchmark.py` — HDBSCAN alternative test with explicit noise reporting.
- `src/run_full_candidate_lsa.py` — full-frame exploratory LSA K=8 run.
- `src/create_blinded_human_review_package.py` and `src/merge_blinded_human_reviews.py` — independent R1/R2 screening review workflow and agreement calculation.
- `src/create_blinded_theme_review_package.py` — independent R1/R2 theme-coherence review sheets.
- `src/calculate_screening_metrics.py` — guarded weighted screening metrics; refuses AI-only or unresolved labels.
- `app/streamlit_app_neiss_weighted.py` — local Explorer for benchmark samples and the full candidate cluster index.
- `review_materials/` — blinded R1/R2 screening-review sheets and blinded theme-coherence sheets. The internal analysis key is supplied separately as `fall_project_internal_analysis_key_DO_NOT_SHARE.csv`; copy it into `review_materials/` locally before merging, and never share it with reviewers or GitHub.
- `results/benchmark_5000_final/`, `results/benchmark_10000_final/` — reproducible sample results, assignments, metrics and human-review templates.
- `results/full_candidate_event_lsa_k8/` — all-candidate cluster index, cluster counts/shares, metrics and review templates. No narratives in the index; dashboard joins locally to the source file.
- `results/hdbscan_5000/` — tested HDBSCAN alternative and review sheets.
- `docs/` — audit/results, annotation protocol, CA1 checklist, report-content draft and slide outline.

## Scope and dataset warning

The allocated DrivenData dataset was unavailable, so the current work uses prepared CPSC NEISS 2019–2022 data, age 65+, broadly screened by fall-related keywords. NEISS covers consumer-product-associated emergency-department injury cases; it is not a census of older-adult falls. The 201,627 rows are keyword candidates, **not confirmed falls**. Obtain written instructor approval for this substitution. Never describe candidate counts or cluster shares as prevalence of all older-adult falls.

The prepared candidate CSV includes NEISS `Weight` but omits `Stratum` and `PSU`. This pack reports weighted point estimates only; no design-based SE/95% CI is supplied.

## Install into the local project

Extract this pack. Copy its `src`, `app`, `docs`, `review_materials`, and `results` folders into the local project root, merging folders. The scripts use new filenames and refuse to overwrite outputs. Keep your historical `model.py`, `preprocess.py`, source files and experiment outputs.

```powershell
.\.venv\Scripts\Activate.ps1
```

The benchmark scripts use pandas, numpy and scikit-learn, all already listed by the starter project. The Streamlit app source is syntax-checked but could not be launched in the build environment because Streamlit was not installed there; launch locally after installing the existing `requirements.txt`.

## Reproduce the 5k and 10k controlled benchmarks

```powershell
python .\src\run_discovery_benchmark.py --input .\data\neiss_2019_2022_fall_candidates.csv --output-dir .\results\benchmark_5000_local --per-year 1250 --seed 42 --silhouette-sample 2000 --k-values 4 6 8 10
python .\src\run_discovery_benchmark.py --input .\data\neiss_2019_2022_fall_candidates.csv --output-dir .\results\benchmark_10000_local --per-year 2500 --seed 42 --silhouette-sample 2000 --k-values 6 8 10
```

For balanced-by-year samples, candidate-frame expansion weights are:

`candidate_frame_analysis_weight = NEISS Weight × candidate rows in year / sampled candidate rows in year`.

This expands weighted point estimates to the keyword-candidate frame; it does not turn the keyword screen into confirmed falls.

## Reproduce holdout stability

Example for 5k event-text LSA K=8:

```powershell
python .\src\evaluate_holdout_stability.py --input .\results\benchmark_5000_local\benchmark_sample_5000.csv --output .\results\benchmark_5000_local\stability_event_lsa_k8.json --representation event_lsa --clusters 8 --repeats 5 --seed 42
```

Repeat with `--clusters 10` to compare K=10. ARI measures repeatability of assignments on the same holdout, not semantic correctness or human theme coherence.

## Reproduce HDBSCAN check

```powershell
python .\src\run_hdbscan_lsa_benchmark.py --input .\results\benchmark_5000_local\benchmark_sample_5000.csv --output-dir .\results\hdbscan_local --min-cluster-sizes 30 50 100 --min-samples 10
```

The supplied HDBSCAN run assigned 57%–84% of the 5k records to noise at these settings. Its non-noise silhouette excludes noise rows and is not directly comparable to K-Means silhouette over all rows. It is not the recommended default.

## Full candidate-frame run (already completed in supplied results)

The supplied `results/full_candidate_event_lsa_k8/` holds the full 201,627-candidate run. To reproduce locally in a new folder:

```powershell
python .\src\run_full_candidate_lsa.py --input .\data\neiss_2019_2022_fall_candidates.csv --output-dir .\results\full_candidate_event_lsa_k8_local --clusters 8 --seed 42
```

It creates an index (year, case ID, weight, cluster only), summary CSV, metrics JSON and 80-case review template. Keep the original candidate CSV in `data/` so the Explorer can join narratives locally.

## Blinded screening review: do this before accuracy metrics

Give `reviewer_R1_BLINDED.csv` only to reviewer 1 and `reviewer_R2_BLINDED.csv` only to reviewer 2. **Do not share `analysis_key_INTERNAL_DO_NOT_SHARE.csv` with reviewers.** Download the separate internal key file and place it in `review_materials/` locally; review independently without seeing the screen group or AI-draft labels. Use `yes`, `no`, or `uncertain` and quote evidence.

Merge only after both are complete:

```powershell
python .\src\merge_blinded_human_reviews.py --reviewer1 .\review_materials\reviewer_R1_BLINDED.csv --reviewer2 .\review_materials\reviewer_R2_BLINDED.csv --key .\review_materials\analysis_key_INTERNAL_DO_NOT_SHARE.csv --output .\results\human_review_merged_for_adjudication.csv --agreement-json .\results\human_review_agreement.json
```

Resolve every disagreement with a human adjudicator; leave ambiguous cases uncertain. Only when each row has a verified two-reviewer or adjudicated status can this run:

```powershell
python .\src\calculate_screening_metrics.py --input .\results\human_review_final_verified.csv --output .\results\human_verified_screening_metrics.json
```

This metric script deliberately rejects AI-only labels and unresolved disagreements. Sampling weights here estimate filter metrics in the 257,245-row NEISS age-65+ universe; they are separate from NEISS case `Weight`.

## Blinded cluster-coherence review

Give R1 and R2 their respective files in `review_materials/reviewer_R1_FULL_CANDIDATE_K8_THEME_COHERENCE.csv` and `reviewer_R2_FULL_CANDIDATE_K8_THEME_COHERENCE.csv`. Both contain the same 10 examples in each full-candidate K=8 cluster, but shuffled within cluster. Reviewers should independently name each cluster and score coherence 1–5, adding notes for mixed/non-fall/ambiguous cases. Do not provide the AI-drafted theme-hypothesis file as the answer key.

## Run the local Explorer

```powershell
streamlit run .\app\streamlit_app_neiss_weighted.py
```

The full-candidate index is joined to `data/neiss_2019_2022_fall_candidates.csv` for local drill-down. Weighted shares are labelled as candidate-frame shares, not all-fall prevalence.

## Do not push to public GitHub

Do not commit full/raw datasets, case-level narrative review sheets, `analysis_key_INTERNAL_DO_NOT_SHARE.csv`, local human ratings or adjudication files. The instructor guidelines require an AI-tool-use declaration; your team must understand, review and reproduce every submitted line and result.
