# Fast-track submission checklist

This is the shortest responsible route to a complete, honestly reported project. Stop creating additional preprocessing versions.

## Completed

- [x] Project repository and Python environment.
- [x] NEISS 2019–2022 source audit and candidate CSV preparation.
- [x] Keyword-frequency baseline.
- [x] Twenty-record single-reviewer fall-label pilot (19 yes, 1 no); documented as non-representative.
- [x] Reproducible 5,000-record experiment sample.
- [x] Original, V2, V3 and V4 six-cluster pilot runs.
- [x] Pilot model comparison documented.
- [x] V2/V4 stability pilot: three repeats, 0.8 sample fraction, three pairwise comparisons per model.
- [x] V4 human-coherence pilot: three examples per cluster, six saved ratings, one reviewer.
- [x] Local Streamlit Explorer tested; ratings and filtered-record exports available.

## Minimum remaining work

1. **Dataset approval:** Ask the instructor to approve NEISS as a replacement for the ended DrivenData dataset. Keep the written response. This is the critical scope issue.
2. **Full candidate analysis:** Confirm whether the instructor expects metrics on the full 201,627 keyword-screened candidates. If proceeding, create a distinct full-data run and clearly call the records keyword-screened candidates, not confirmed falls. Do not reuse the 5,000-record metrics as full-data results.
3. **Report and demo:** Fill the instructor's CA-1 report/presentation templates. Use the actual pilot metrics in `PILOT_EXPERIMENTS_5000.md`, include dashboard screenshots, and state the limitations plainly.
4. **Final repository check:** Ensure only code and non-identifying aggregate results are committed. Keep full datasets and local assignments out of public GitHub.
5. **AI disclosure:** Review all code and follow the course's AI-tool disclosure rules.

## Do not spend time on

- More cleaner versions (V5, V6, etc.).
- Tuning silhouette alone.
- Labeling all 160 review rows unless the instructor explicitly requires it.
- Uploading the raw/full NEISS dataset to GitHub.
- Calling keyword-screened records confirmed falls.
- Claiming high coherence, stability, or accuracy without measurements.

## Minimum evidence to include in the report

- Source substitution and instructor approval status.
- Data audit and candidate-screening limitations.
- Keyword baseline and overlapping keyword shares.
- Four-model silhouette and cluster-size pilot table.
- V2/V4 stability settings, mean ARI, SD and limited number of comparisons.
- Six V4 human coherence ratings and the 3.33/5 equal-weight mean, with the one-reviewer limitation.
- V4 cluster names and their shares among the 5,000 loaded candidates only.
- Dashboard screenshots showing theme distribution and drill-down.
