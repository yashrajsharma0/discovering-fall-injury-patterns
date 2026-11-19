# CA-1 submission checklist

Based on the uploaded `CA1_Submission_Guidelines.docx`:

- [ ] Obtain written instructor approval for the NEISS source substitution before representing it as the project dataset.
- [ ] Copy the three official objectives unchanged from the allocation into the report.
- [ ] Use the official report template and complete every section; remove all placeholder instructions.
- [ ] Report the original problem source / problem-statement ID and link, and explain the substitution accurately.
- [ ] Document CPSC NEISS source, year range, age filter, keyword screening rule, and limits of the data.
- [ ] Include baseline and model comparison on controlled samples; include actual code and saved metrics.
- [ ] Report sampled silhouette with distance/feature space; report stability with repeat count and method; report human coherence with example count and reviewer count.
- [ ] Use only human-verified labels for screening precision/recall; separately report unresolved/uncertain share and sensitivity bounds. The current AI-assisted annotation sample is not ground truth.
- [ ] State cluster shares are among keyword-screened candidates; distinguish raw sample shares from NEISS-weighted candidate-frame shares.
- [ ] Do not report national estimate confidence intervals unless Stratum/PSU and a valid design-based variance method are available. The supplied prepared candidate CSV omits these fields.
- [ ] Include figures/tables with captions, references cited in body, and AI-use declaration.
- [ ] Presentation: 8–10 slides, about 8 minutes plus Q&A; all group members contribute and can explain the code/results.
- [ ] Implementation: deliver ZIP or GitHub link, keep large datasets and case-level review files out of public GitHub, explain data download/preparation, and ensure README commands reproduce report numbers.
- [x] Full-candidate exploratory LSA K=8 run completed on all 201,627 candidates; counts and candidate-frame NEISS-weighted point shares are saved. This does not validate themes or confirm falls.
- [x] HDBSCAN alternative was tested on the 5k LSA sample; noise was 57%–84% at tested settings, so it was not selected as the default.
- [ ] Online UMS submission is one PDF, uploaded by every member under their own login, before 30 November 2026; bring/share the same PDF with instructor on presentation day.
- [ ] Check final PDF opens correctly and file is correctly named according to the course/section/group convention.
