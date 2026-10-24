# Dataset notes — NEISS 2019–2022

**Working data source:** U.S. Consumer Product Safety Commission (CPSC), National Electronic Injury Surveillance System (NEISS), annual public-use injury data. Official portal: https://www.cpsc.gov/Research--Statistics/NEISS-Injury-Data

**Files prepared locally (not committed to GitHub):**
- `neiss_2019_2022_age65plus.csv`: 257,245 records aged 65+ from 2019–2022.
- `neiss_2019_2022_fall_candidates.csv`: 201,627 records selected by broad narrative keyword screening.
- `neiss_2019_2022_validation_summary.csv`: source-row and cleaning audit by year.
- `neiss_fall_candidate_review_sample.csv`: stratified review sample of 160 candidates (40/year).

The 201,627 records are **keyword-screened candidates, not confirmed falls**. Keyword screening can produce false positives and false negatives. Manually code the review sample using `manual_validation_template.csv`, document selection method and reviewer decisions, and do not report the candidate count as a confirmed fall count. The review sample is 40 records per year and is useful for an initial quality check; it is not necessarily representative of all candidate types.

NEISS represents consumer-product-related emergency department injuries, not all falls in the community and not the original DrivenData competition dataset. The substitution differs from the assigned source. Obtain instructor written approval and verify applicable source terms before public redistribution. Do not upload raw/full data to GitHub.

Age filter: age 65+; infant age values encoded in months were excluded according to the source data convention. The source-validation summary records no missing narratives, invalid dates, or duplicate case numbers among the retained age-65+ records for these four annual files.
