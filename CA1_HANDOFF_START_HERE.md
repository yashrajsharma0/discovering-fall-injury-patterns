# CA1 final handoff — start here

This is a working submission package, not a final approval-cleared submission. It contains the editable report, PDF report draft, editable 10-slide deck, PDF slide export, speaker/viva notes, reproducible analysis scripts, experiment outputs, full-candidate cluster index, dashboard source, and two-reviewer review templates.

## 1. Install the improvement files into your Windows project

1. Extract the ZIP to a folder such as `Downloads\CA1_Final_Submission_Handoff`.
2. Open PowerShell in the extracted folder.
3. Run this command (the path below is your existing local project folder):

```powershell
powershell -ExecutionPolicy Bypass -File .\Install_CA1_Handoff.ps1 -ProjectRoot "C:\Users\LENOVO\Downloads\Discovering_Fall_Injury_Patterns_CA1_starter (2)\Discovering_Fall_Injury_Patterns_CA1"
```

The installer copies new files from `improvement_pack\src`, `app`, `docs`, `review_materials`, and `results`, plus the report and presentation folders. Existing files are **never overwritten**. Warnings about skipped existing files mean you should compare the two versions manually before choosing one.

## 2. Launch the local Explorer

The original candidate dataset is not included. Confirm this file already exists locally:

`data\neiss_2019_2022_fall_candidates.csv`

Then run:

```powershell
cd "C:\Users\LENOVO\Downloads\Discovering_Fall_Injury_Patterns_CA1_starter (2)\Discovering_Fall_Injury_Patterns_CA1"
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\requirements.txt
streamlit run .\app\streamlit_app_neiss_weighted.py
```

The dashboard runs locally and reads the candidate CSV and cluster index from your machine. The Streamlit source was syntax-checked here but could not be launched in this build environment; test it on your laptop before claiming a live demo.

## 3. What the experimental results say

- Provisional human-review candidate: event-text TF-IDF -> 100-component TruncatedSVD/LSA -> L2 normalization -> K-Means, K=8.
- K=8 had higher five-repeat holdout assignment repeatability than K=10 in both 5k and 10k stratified samples. K=10 showed higher silhouette and smaller largest clusters, but weaker holdout stability.
- Full-frame K=8 completed across 201,627 keyword-screened candidates. Raw and NEISS-weighted shares are **within this keyword-candidate frame only**, not prevalence of all falls.
- HDBSCAN at the tested settings labelled 57.28%–83.70% of the 5k sample as noise; it was not selected.
- Silhouette values from TF-IDF cosine space and normalized-LSA Euclidean space are not directly comparable. ARI is repeatability/agreement, not semantic accuracy.

## 4. Do not skip the human review

- Give only `improvement_pack\review_materials\reviewer_R1_BLINDED.csv` to reviewer R1 and only `reviewer_R2_BLINDED.csv` to reviewer R2.
- Give each reviewer their matching `reviewer_R*_FULL_CANDIDATE_K8_THEME_COHERENCE.csv` file for independent theme review.
- Reviewers should not see the AI draft labels, the candidate/non-candidate group, or each other's responses.
- The internal analysis key is provided separately as `fall_project_internal_analysis_key_DO_NOT_SHARE.csv`. Put a copy in `review_materials` named `analysis_key_INTERNAL_DO_NOT_SHARE.csv` only after both reviewers return their work. Never send it to reviewers or GitHub.
- Merge the independent reviews with `src\merge_blinded_human_reviews.py`, adjudicate all disagreements and only then run `src\calculate_screening_metrics.py`. That script deliberately refuses AI-only or unresolved labels.

## 5. Instructor approval and report metadata

- Send `INSTRUCTOR_APPROVAL_REQUEST_DRAFT.md` to the instructor and obtain written approval or direction for the NEISS substitution.
- Fill every bracketed field in `report\CA1_Report_DRAFT.docx` and the first/last slides: course code/title, section, group, member names, registration/roll numbers, instructor, syllabus unit numbers, individual contributions and signatures. Add/remove member rows to match your group.
- The report main body (Chapter 1 through References) is 20 pages; total PDF is 28 pages including front matter and appendices. The template's main-body range is 12–20 pages.
- Refresh the table of contents after editing and export a new PDF. Do not use the supplied draft PDF after making changes to the DOCX.

## 6. Critical scope and privacy warnings

The allocated DrivenData dataset was not used. This project instead analyses prepared CPSC NEISS 2019–2022 public-use data, age 65+, screened with broad fall-related keywords. The 201,627 rows are keyword candidates, **not verified falls**. NEISS covers consumer-product-associated emergency-department injury visits, not every older-adult fall. Obtain instructor approval before final submission.

The prepared candidate CSV retains NEISS `Weight` but omits `Stratum` and `PSU`; therefore current weighted shares are point estimates only, without design-based standard errors or confidence intervals. Do not claim population prevalence.

Do not push raw/candidate CSVs, narrative-containing review sheets, assignments, internal keys or human review data to public GitHub. Use the recommended `.gitignore` text under `improvement_pack\docs`.

## 7. Official submission workflow and naming

The supplied CA-1 instructions specify:

- **UMS:** upload only the final report PDF, before 30 November 2026. Every member uploads the exact same PDF through their own UMS login. Do not upload the Word file, slides, code or screenshots to UMS.
- **Instructor:** share one report PDF per group on presentation day; submit the slide file (PPTX or PDF) before presenting; provide implementation as a ZIP or GitHub link and be ready for a live demo.
- **Presentation:** 8–10 slides, about 8 minutes, followed by questions. Every member must present and answer questions.
- **Implementation folder:** rename the project folder to `<Section>_<Course>_G<No>_CA1/` after you know your exact section, course code and group number. Keep the README, requirements, small sample/data note, notebooks, src, app, results, report and presentation folders.

After filling the actual group metadata, rename the final files exactly to the required pattern:

```text
<Section>_<Course>_G<No>_CA1_Report.pdf
<Section>_<Course>_G<No>_CA1_Slides.pptx   (or .pdf)
<Section>_<Course>_G<No>_CA1_Code.zip      (or submit a GitHub link)
```

Open the final PDF after upload and verify it is the same complete version for every member. Check the uploaded official instructions and any later instructor announcement before submission.

See `FINAL_STATUS.md` for the exact completion gates. This report and deck are drafts until those gates are closed.
