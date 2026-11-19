# Human annotation protocol

## Purpose

Independently verify whether each sampled NEISS narrative describes a fall event. The current AI-generated labels are drafts only and must not be treated as reference truth.

## Operational definition

Use the WHO definition: a fall is an event in which a person comes to rest inadvertently on the ground, floor, or another lower level. In the narrative, look for evidence of the person's unintended descent; do not infer a fall from an isolated keyword.

## Labels

- `yes`: The narrative explicitly supports that the person unintentionally came to rest on the ground/floor/another lower level (including falling from bed/chair/wheelchair/ladder or slipping/tripping and falling).
- `no`: The narrative clearly describes no fall by the person (e.g. an object fell onto the person; the person tripped but recovered; a tool/product slipped but the person did not fall).
- `uncertain`: The record does not establish whether the person fell (e.g. “found on floor” without event description; unexplained collapse; only a diagnosis code; ambiguous wording; multiple possible events).

Do not use a keyword alone to label a fall. A trip or slip is not necessarily a fall. “Syncope” does not establish a fall by itself, but “syncope and fell to floor” can support yes. “Object fell on person” is not a person-fall.

## Confidence

- 1 = low: ambiguous or incomplete wording.
- 2 = moderate: some evidence, but context is incomplete.
- 3 = high: explicit and unambiguous event description.

Confidence is a reviewer judgement, not a calibrated probability.

## Evidence and notes

Quote a short phrase from the original narrative that directly supports the label. Note ambiguity rather than reconstructing missing details.

## Blinding and independent review

1. Reviewers use separate copies of `reviewer_R1_BLINDED.csv` and `reviewer_R2_BLINDED.csv`.
2. Reviewers should not see `analysis_key_INTERNAL_DO_NOT_SHARE.csv`, previous AI labels, candidate/non-candidate group, or each other's labels before submitting.
3. Keep all 160 cases; do not delete or reorder rows.
4. After independent completion, run `merge_blinded_human_reviews.py`.
5. Report raw agreement and Cohen's kappa for the three labels. Kappa is agreement beyond chance, not accuracy.
6. An adjudicator resolves disagreements and documents the reason. Unresolved ambiguity stays `uncertain`, not forced into yes/no.

## Cluster-coherence review

For cluster coherence, separately review 10–15 representative narratives from each selected cluster. Each reviewer independently proposes a short theme name and rates coherence 1–5. Do not name clusters from top terms alone. Report the number of examples and reviewers, show disagreements and mixed examples, and keep fall-label accuracy separate from theme coherence.

## Privacy / reproducibility

Keep case-level review files local and out of public GitHub. Use the same seed and sample IDs for independent reviewers. Record reviewer IDs and dates. Disclose the use of AI for draft suggestions and code assistance, but do not attribute AI suggestions to human reviewers.
