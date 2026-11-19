# 8-minute CA-1 presentation outline (10 slides)

> Adapt to the official allocation and add group/section/member details. Do not present AI-generated cluster names as validated human themes before the coherence review is complete.

## Slide 1 — Title and team (20 sec)
- Discovering Fall Injury Patterns in Medical Narratives
- Course, section, group, members
- One-sentence objective: explore repeatable circumstance patterns in injury narratives.

## Slide 2 — Problem and objective (45 sec)
- Medical injury narratives are short, abbreviated and heterogeneous.
- We want to group recurring event circumstances and quantify themes.
- Show the three official objectives verbatim.

## Slide 3 — Data source and substitution (55 sec)
- Original allocated source: DrivenData problem (cite exact PS ID/link).
- Working source: CPSC NEISS 2019–2022, age 65+.
- 257,245 age-65+ records; 201,627 broad keyword candidates.
- Explicitly state: candidates are not confirmed falls; NEISS is consumer-product ED injury data; written instructor approval required/obtained (show evidence).

## Slide 4 — Data preparation (50 sec)
- Source audit, missingness and duplicate keys.
- DX parser preserves original text, extracts event prefix heuristically, flags unusual cases.
- Preserve negation (`no`, `not`, `without`) and retain original narratives.
- Show a before/after example.

## Slide 5 — Baseline and model design (55 sec)
- Keyword-frequency / rule-based baseline.
- Full TF-IDF; event TF-IDF; event TF-IDF → 100D LSA → normalized vectors → K-Means.
- 5k / 10k stratified samples, seed 42; K=4/6/8/10 as relevant.

## Slide 6 — Controlled benchmark results (60 sec)
- Table comparing LSA K=8 vs K=10 on 5k and 10k.
- Explain K=10 higher silhouette/smaller max cluster, K=8 more stable.
- Mention silhouette in different feature spaces is not directly comparable.

## Slide 7 — Full candidate frame (55 sec)
- Full 201,627-candidate LSA K=8 run.
- Largest raw cluster 35.253%, smallest 4.993%; sampled silhouette 0.06145.
- Show raw and NEISS-weighted candidate-frame shares.
- State no all-fall prevalence claim and no design-based CI without Stratum/PSU.

## Slide 8 — Human validation and dashboard (55 sec)
- Blinded R1/R2 fall-label review on 160 stratified records.
- Separate cluster-coherence review, 10 examples per full-frame cluster.
- Dashboard drill-down and metrics; show live demonstration.
- State AI drafts are not ground truth.

## Slide 9 — Limitations and next steps (50 sec)
- Instructor approval for source substitution.
- Finish independent fall review and adjudication; compute precision/recall only after that.
- Finish independent human theme naming/coherence review.
- Restore Stratum/PSU for valid design variance; confirm full pipeline reproducibility.

## Slide 10 — Conclusion and Q&A (25 sec)
- Provisional event-text LSA K=8 is the human-review candidate, not a validated final model.
- The project now has full-frame cluster counts, point shares, an Explorer and a reproducible evaluation workflow.
- Invite questions.

## Likely viva questions
1. Why are NEISS records not equivalent to the original allocated dataset?
2. Why can keyword candidate share not be called fall prevalence?
3. Why did we preserve negation words?
4. What does DX parsing do, and what are its failure modes?
5. Why use LSA after TF-IDF? What information can it compress or lose?
6. What does silhouette measure, and why can't cosine TF-IDF and Euclidean LSA scores be ranked directly?
7. What does ARI stability measure? Why is it not accuracy?
8. Why did HDBSCAN mark so many rows as noise?
9. How are cluster shares calculated? What is the difference between NEISS case Weight and sampling expansion factor?
10. Why can't we calculate design-based standard errors without Stratum/PSU?
11. How will two human reviewers resolve disagreements?
12. What limitations remain before claiming final themes?
