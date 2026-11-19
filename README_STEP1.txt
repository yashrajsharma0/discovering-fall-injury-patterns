STEP 1 — DATASET AND SCREENING VALIDATION

Contents:
- src/data_quality_audit.py: reproducible audit + review-sample generator
- data/fall_screen_validation_review_randomized.csv: tested randomized 160-row review sample
- results/data_audit/data_quality_audit.json: aggregate audit from the supplied 2019–2022 NEISS files

HOW TO USE IN THE PROJECT
1. Extract this ZIP into the root of your project folder, merging the src/data/results folders.
2. Open PowerShell in the project root and activate the environment:
   .\.venv\Scripts\Activate.ps1
3. Run:
   python src\data_quality_audit.py
4. The default command reads:
   data\neiss_2019_2022_fall_candidates.csv
   data\neiss_2019_2022_age65plus.csv
   and writes an aggregate audit to results\data_audit\data_quality_audit.json.
5. It also regenerates data\fall_screen_validation_review_randomized.csv using seed 42.

SAFETY / REPRODUCIBILITY
- The script does not edit or delete either source dataset.
- The old data\neiss_fall_candidate_review_sample.csv is not overwritten.
- Keep review CSVs and source narratives local. The current .gitignore excludes data\*.csv.
- Do not call keyword candidates confirmed falls.

HOW TO LABEL THE REVIEW SAMPLE
- YES: the narrative clearly describes the patient's fall as part of this injury event.
- NO: the incident clearly does not involve a fall (for example, a negated fall, a near-fall with no fall, or an unrelated event).
- UNCERTAIN: the narrative does not contain enough information to decide safely.
- Copy a short evidence phrase from the narrative into evidence_phrase.
- confidence_1_to_3: 1=low, 2=medium, 3=high.
- Review both candidate and non_candidate rows. Candidate rows help estimate precision; non_candidate rows help detect missed falls and estimate recall.
- sampling_weight is the frame size divided by sample size for that year and screen group. Do not calculate pooled precision/recall from unweighted row percentages.
- This is an initial validation pilot, not a definitive estimate. We should review the results and then decide whether to expand the sample and arrange a second independent reviewer.
