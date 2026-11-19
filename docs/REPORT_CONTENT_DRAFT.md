# CA-1 Report Content Draft — Discovering Fall Injury Patterns in Medical Narratives

> **Draft only.** Paste/adapt this material into the official CA-1 report template. The official template, group identifiers, member contributions, signatures and instructor's written approval were not available in the files used for this draft. Do not submit this Markdown file as the final report.

## Title page fields to complete

- Project title: Discovering Fall Injury Patterns in Medical Narratives
- Course / section / group: **[INSERT EXACT DETAILS]**
- Members, registration numbers and roll numbers: **[INSERT ALL MEMBERS]**
- Original problem statement ID and source link: **[COPY EXACTLY FROM ALLOCATION]**
- Dataset substitution approval date / instructor evidence: **[ATTACH WRITTEN APPROVAL OR STATE PENDING]**

## Official objectives (copy unchanged from allocation)

1. Build a discovery system that clusters narratives into recurring circumstance patterns and quantifies each.
2. Produce a clustering of narratives with named themes and their share of incidents.
3. Report silhouette, cluster stability, human-rated theme coherence.

## 1. Problem and motivation

Older adults may experience injuries during varied circumstances such as trips, slips, loss of balance, falls from furniture or stairs, and falls in care settings. Medical injury narratives provide short, abbreviated descriptions of incidents. The goal of this project is to explore whether recurring circumstances can be identified from the narrative text and quantified in a way that supports further human investigation.

## 2. Data source and scope

The originally allocated DrivenData source was unavailable for this work. The current prototype instead uses prepared CPSC NEISS public-use injury data from 2019–2022, filtered to age 65+ and broadly screened using fall-related keywords. The age-65+ universe contains 257,245 records and the keyword screen produced 201,627 candidate records. The candidate screen shares by year ranged from 76.80% to 79.51%.

This is a material dataset substitution and requires written instructor approval. NEISS is a probability sample of consumer-product-associated emergency-department injury visits. It does not capture all falls or all older adults. The 201,627 rows are keyword-screened candidates, not confirmed falls. Thus the project reports patterns among the keyword-candidate frame, not prevalence of all older-adult falls.

The prepared candidate CSV has NEISS `Weight`, but does not retain `Stratum` and `PSU`. Weighted point estimates are available; design-based standard errors and confidence intervals are not calculated.

## 3. Data preparation

The pipeline audits the age-65+ universe and candidate subset, checks missing narratives, duplicate year-case keys and repeated narrative text, and preserves source narratives. A conservative parser identifies common `DX` diagnosis-section markers and extracts the text preceding the first recognized marker as an experimental incident/circumstance representation. The full original narrative remains available; ambiguous multiple-marker, leading-marker and unparsed-suspect cases are flagged. Records without recognized `DX` markers retain the full narrative, which may still contain diagnosis information.

On the full candidate frame, the parser split at a first DX boundary in 195,217 records; 6,322 records had no recognized marker; 68 had an unparsed DX substring requiring review; 20 had leading-DX patterns kept intact for review; and 788 records contained multiple DX markers. This is a heuristic rather than a clinical parser.

The text pipeline preserves negation terms such as `no`, `not` and `without`. Generic English stop-word removal can delete negation and alter narrative meaning. Age/sex shorthand and common documentation boilerplate are handled conservatively; incident mechanism and context terms are retained.

## 4. Methods and baseline

The required baseline is the project's keyword-frequency / rule-based baseline. Its groups can overlap and must not be summed as mutually exclusive shares.

Three controlled candidate representations were compared:
1. Full narrative TF-IDF (word unigrams and bigrams) with K-Means.
2. Event/circumstance text TF-IDF with K-Means.
3. Event/circumstance text TF-IDF followed by 100-component TruncatedSVD (LSA), L2 normalization and K-Means.

The 5,000-row sample used 1,250 rows from each year; the 10,000-row sample used 2,500 rows from each year. Both were drawn without replacement from the candidate frame with seed 42. Model comparisons used identical records within each sample. LSA uses Euclidean distance on normalized SVD vectors; TF-IDF silhouette uses cosine distance. Silhouette scores in different feature spaces are not directly comparable.

## 5. Experimental results

The most promising provisional setting for further human review is event-text LSA with K=8. In the 5k sample, its sampled silhouette was 0.06553 and its largest cluster was 34.86%. In the 10k sample, its sampled silhouette was 0.06345 and its largest cluster was 34.84%. K=10 had higher silhouette (0.07094 in 5k; 0.07201 in 10k) and a smaller largest cluster (28.68%; 28.86%), but could over-fragment themes.

Five-repeat fixed-holdout stability gave K=8 event-LSA mean pairwise ARI 0.8205 (SD 0.1115) in the 5k sample and 0.7759 (SD 0.1196) in the 10k sample. K=10 event-LSA mean pairwise ARI was 0.6647 (SD 0.0651) in 5k and 0.6391 (SD 0.1348) in 10k. ARI measures repeatability of assignments on the common holdout, not semantic correctness.

HDBSCAN was tested on the 5k event-LSA space. At min cluster sizes 30, 50 and 100 (min_samples 10), noise proportions were 82.50%, 57.28% and 83.70%, respectively. The non-noise silhouette excluded noise records and is not comparable to K-Means over all records; HDBSCAN was not selected as the default.

## 6. Full candidate-frame exploratory result

A full-candidate event-text LSA K=8 run was completed on all 201,627 keyword-screened candidates. The sampled silhouette was 0.06145 in Euclidean distance on normalized 100-dimensional LSA. The largest raw cluster contained 71,080 records (35.253%) and the smallest 10,067 (4.993%).

The NEISS-weighted point-estimate total within the candidate frame was approximately 9,355,019, with cluster weighted candidate-frame shares: C0 35.689%, C1 8.274%, C2 10.199%, C3 8.563%, C4 5.022%, C5 17.146%, C6 6.148%, C7 8.960%. These are candidate-frame weighted shares only—not all-fall prevalence. No design-based confidence intervals are supplied because Stratum/PSU are missing.

The eight cluster IDs are provisional. Spot inspection suggests possible families such as bed/transfer falls, stair/step falls, trip/obstacle falls, wet-surface slips, head/furniture impact, nursing-home contexts and general/unwitnessed falls. Some clusters are broad or overlap. Final names and coherence ratings await independent human review of 10 examples per cluster by two reviewers.

## 7. Human validation

The AI-assisted fall-label draft for a 160-row stratified sample contains 83 yes, 62 no and 15 uncertain labels. Four AI suggestions were explicitly approved by the user; the draft still is not independent human ground truth. Screening accuracy is therefore not reported.

Two blinded independent reviewer files are provided, stratified across year and candidate/non-candidate status. Reviewers use the operational definition that a fall is an unintended descent to the ground, floor or another lower level. They label yes/no/uncertain independently, quote evidence, and record confidence. Agreement is measured with raw percent agreement and Cohen's kappa; disagreements require adjudication. Only verified/adjudicated human labels are used for weighted screening precision and recall. Uncertain cases must be reported and sensitivity bounds shown.

## 8. System implementation

The deliverable includes Python scripts for parsing, benchmarking, full-frame clustering, holdout stability, HDBSCAN comparison, blinded annotation merging, guarded screening metrics and a local Streamlit Explorer. The Explorer loads local assignments, joins the full-candidate index to the original candidate CSV locally, displays candidate-frame counts and weighted shares, and supports narrative drill-down and human coherence ratings.

The app source passed Python syntax compilation but could not be launched in the build environment because Streamlit was not installed in that environment. The team must test the dashboard locally and demonstrate it on presentation day.

## 9. Limitations and next steps

- Obtain written instructor approval for the NEISS substitution.
- Complete independent R1/R2 fall-label reviews and adjudicate disagreements.
- Complete independent theme-coherence reviews for K=8 and, ideally, K=10.
- Recover NEISS Stratum/PSU from source workbooks for valid design-based variance estimates.
- Test a larger sample/full-frame stability procedure if computational resources permit.
- Validate the Streamlit app locally; capture accurate screenshots for the report and presentation.
- Finalize report and slides using the instructor's official template and exact project identifiers.

## 10. AI-use declaration draft

ChatGPT assisted with research planning, code drafting, debugging, experiment design, interpretation of exploratory outputs and documentation. AI-assisted labels/theme hypotheses were treated as drafts and not as verified ground truth. The project team must inspect, understand and test every submitted line of code, review all generated results, disclose AI use according to course requirements and take responsibility for the final work.

## References

- WHO, *Falls* (21 October 2026), https://www.who.int/en/news-room/fact-sheets/detail/falls
- U.S. Consumer Product Safety Commission, *Explanation of NEISS Estimates*, https://www.cpsc.gov/cgibin/NEISSQuery/webestimates.html
- U.S. Consumer Product Safety Commission, *NEISS Frequently Asked Questions*, https://www.cpsc.gov/Research--Statistics/NEISS-Injury-Data/Neiss-Frequently-Asked-Questions
- scikit-learn, *Clustering text documents using K-means*, https://scikit-learn.org/stable/auto_examples/text/plot_document_clustering.html
- scikit-learn, *Clustering performance evaluation*, https://scikit-learn.org/stable/modules/clustering.html
- Reimers, N. & Gurevych, I. (2019), *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*, https://aclanthology.org/D19-1410/
- scikit-learn, *HDBSCAN*, https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html
