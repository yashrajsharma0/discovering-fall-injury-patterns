# Handoff status — 17 November 2026

## Work completed in this pack

- Audited and documented the NEISS candidate frame and its scope limitations.
- Built a conservative DX parser that preserves source narratives and flags uncertainty.
- Ran controlled 5k and 10k comparisons across full-text TF–IDF, event-text TF–IDF and event-text LSA.
- Ran five-repeat holdout stability tests for K=8 and K=10 in both samples.
- Ran an exploratory LSA K=8 cluster assignment across all 201,627 candidates.
- Tested HDBSCAN at three settings; high noise proportions mean it is not selected.
- Built a local Explorer source file and created blinded independent fall-label and cluster-coherence review sheets.
- Prepared report-content and 10-slide presentation drafts.

## Decisions from measured experiments

- Provisional candidate for human theme review: event-text LSA K=8.
- K=10 has higher silhouette and smaller maximum cluster, but lower holdout ARI in both 5k and 10k tests; it may fragment themes. Review both before selecting a final K.
- HDBSCAN is not selected with the tested parameters because it labels most cases as noise.
- The earlier local negation-preservation change is a justified text-quality fix, but its original local comparison did not demonstrate meaningful cluster-quality improvement.

## Still requires people or local access

1. Written instructor approval for the NEISS dataset substitution.
2. Two independent reviewers to complete the 160-case fall-label sheets; adjudicate disagreements; only then compute weighted precision/recall.
3. Two independent reviewers to complete the K=8 theme-coherence sheets; optionally repeat for K=10.
4. Restore original NEISS `Stratum` and `PSU` variables if design-based SE/CI are required.
5. Copy this pack into the Windows project, run the local Streamlit app, verify it with the local data and demo it.
6. Fill in group/member details and transfer the report draft into the official report template.
7. Prepare slides from the outline and add team-specific contributions/signatures.

This pack does not modify the user's Windows folder or public GitHub branch. It is supplied as a set of files for local integration.
