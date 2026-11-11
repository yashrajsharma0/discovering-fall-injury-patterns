# Fast-track submission checklist

This is the shortest responsible route to a complete, honestly reported project. Stop creating additional preprocessing versions.

## Already completed

- [x] Project repository and Python environment.
- [x] NEISS 2019–2022 source audit and candidate CSV preparation.
- [x] Keyword-frequency baseline.
- [x] Three-record single-reviewer manual pilot; all three explicitly describe falls. Too small for precision estimates.
- [x] Reproducible 5,000-record experiment sample.
- [x] Original, V2, V3 and V4 six-cluster pilot runs.
- [x] Pilot model comparison documented.

## Do next (minimum remaining work)

1. **Dataset approval:** Ask the instructor to approve NEISS as a replacement for the ended DrivenData dataset. Keep the written response.
2. **Stability:** From the repository root, run:

   ```powershell
   python src\compare_stability.py --repeats 3
   ```

   This compares V2 and V4 on the existing 5,000-record assignments and writes `results/stability_comparison_5000.json`.

3. **Human theme coherence:** Run `streamlit run app\streamlit_app.py`. Select V2 or V4. For each of six clusters, inspect three examples, enter a provisional theme name, rate coherence 1–5, and save. The app records the ratings locally.
4. **Final model choice:** Select a model only after considering silhouette, cluster-size imbalance, stability, and the six human ratings. Current pilot evidence does not justify claiming a winner.
5. **Full candidate run:** Only after model choice and instructor approval, rerun the selected approach on the 201,627 local candidate records. Save it to a new results folder.
6. **Report and demo:** Fill the instructor's CA-1 report/presentation templates. Use actual saved metrics; clearly identify candidate data, sample results, and limitations.

## Do not spend time on

- More cleaner versions (V5, V6, etc.).
- Tuning silhouette alone.
- Labeling all 160 review rows unless the instructor explicitly requires it.
- Uploading the raw/full NEISS dataset to GitHub.
- Calling keyword-screened records confirmed falls.
- Claiming high coherence, stability, or accuracy without measurements.

## Minimum evidence to include in the report

- Source substitution and approval status.
- Data audit and candidate-screening limitations.
- Keyword baseline and overlapping keyword shares.
- Pilot experiment table (in `PILOT_EXPERIMENTS_5000.md`).
- Stability settings, pairwise ARI results, and interpretation.
- Six human coherence ratings, one-reviewer limitation.
- Named themes and their shares among the analyzed candidates.
- Dashboard screenshots and drill-down demonstration.
