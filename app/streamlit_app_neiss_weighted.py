"""Local Streamlit Explorer for the refreshed NEISS fall-candidate benchmarks.

Only reads local CSV/JSON files. Cluster shares are within keyword-screened
candidate records. NEISS-weighted shares require the benchmark's expanded
candidate_frame_analysis_weight field and are not all-fall prevalence.
"""
from __future__ import annotations
from datetime import date
import json
from pathlib import Path
import re

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RATING_FILE = RESULTS / "human_coherence_ratings_v2.csv"
EXPERIMENTS = {
    "5k · full narrative TF-IDF · K=6": RESULTS / "benchmark_5000_final" / "assignments_full_tfidf_k6.csv",
    "5k · event text TF-IDF · K=6": RESULTS / "benchmark_5000_final" / "assignments_event_tfidf_k6.csv",
    "5k · event text LSA · K=8 (provisional)": RESULTS / "benchmark_5000_final" / "assignments_event_lsa_k8.csv",
    "5k · event text LSA · K=10 (review candidate)": RESULTS / "benchmark_5000_final" / "assignments_event_lsa_k10.csv",
    "10k · event text LSA · K=8 (provisional)": RESULTS / "benchmark_10000_final" / "assignments_event_lsa_k8.csv",
    "10k · event text LSA · K=10 (review candidate)": RESULTS / "benchmark_10000_final" / "assignments_event_lsa_k10.csv",
    "Full 201,627 candidate frame · event LSA K=8": RESULTS / "full_candidate_event_lsa_k8" / "full_candidate_cluster_index.csv",
}

st.set_page_config(page_title="Fall Circumstance Explorer", page_icon="🔎", layout="wide")
st.title("Older-Adult NEISS Fall-Candidate Circumstance Explorer")
st.warning(
    "Research limitation: these are keyword-screened NEISS injury candidates, not confirmed falls. "
    "Cluster shares describe this candidate frame only; they are not prevalence among all older-adult falls."
)

available = {label: path for label, path in EXPERIMENTS.items() if path.exists()}
if not available:
    st.error("No benchmark assignments found. Run the benchmark script and copy its results folder into this project's results directory.")
    st.stop()

with st.sidebar:
    st.header("Experiment")
    choice = st.selectbox("Select benchmark", list(available))
    path = available[choice]
    st.caption("All files are read from this computer; nothing is uploaded by this app.")

try:
    df = pd.read_csv(path, low_memory=False)
except Exception as exc:
    st.error(f"Could not read {path.name}: {exc}")
    st.stop()

# The full-frame assignment index excludes narratives to keep the results pack
# small. Join the original local source CSV for narrative drill-down.
if "Narrative_1" not in df.columns and path.name == "full_candidate_cluster_index.csv":
    source_path = ROOT / "data" / "neiss_2019_2022_fall_candidates.csv"
    if not source_path.exists():
        st.error(f"Full candidate narratives not found at {source_path}. Keep the candidate CSV in data/.")
        st.stop()
    source = pd.read_csv(source_path, usecols=[
        "Source_Year", "CPSC_Case_Number", "Narrative_1", "Age", "Sex", "Diagnosis", "Body_Part", "Fall_Keywords_Matched"
    ], low_memory=False)
    df = df.merge(source, on=["Source_Year", "CPSC_Case_Number"], how="left", validate="one_to_one")
    df["candidate_frame_analysis_weight"] = pd.to_numeric(df["Weight"], errors="coerce")

required = {"cluster_id", "Narrative_1", "Source_Year"}
if not required.issubset(df.columns):
    st.error(f"Assignment file is missing columns: {sorted(required - set(df.columns))}")
    st.stop()

df = df.copy()
df["cluster_id"] = df["cluster_id"].astype(str)
cluster_ids = sorted(df["cluster_id"].dropna().unique(), key=lambda x: int(x) if x.isdigit() else x)

# Load saved benchmark report and matching model summary.
report_path = path.parent / "benchmark_report.json"
full_model_path = path.parent / "full_candidate_metrics.json"
report = {}
selected_model = {}
if full_model_path.exists():
    try:
        full_report = json.loads(full_model_path.read_text(encoding="utf-8"))
        profile = pd.read_csv(path.parent / "full_candidate_cluster_summary.csv")
        top_terms_map = {str(int(r.cluster_id)): str(r.top_terms).split(" | ") for _, r in profile.iterrows()}
        selected_model = {
            "silhouette": full_report.get("silhouette_sampled"),
            "silhouette_metric_space": full_report.get("silhouette_metric_space"),
            "largest_cluster_share_pct": full_report.get("largest_cluster_share_pct"),
            "top_terms_by_cluster": top_terms_map,
        }
        report = {"interpretation_warning": full_report.get("warning", "")}
    except (OSError, json.JSONDecodeError, KeyError):
        report = {}
if report_path.exists():
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        match = re.fullmatch(r"assignments_(full_tfidf|event_tfidf|event_lsa)_k(\d+)\.csv", path.name)
        if match:
            rep, kval = match.group(1), int(match.group(2))
            selected_model = next((m for m in report.get("models", []) if m.get("representation") == rep and m.get("k") == kval), {})
    except (OSError, json.JSONDecodeError):
        report = {}

n = len(df)
cluster_count = df["cluster_id"].nunique()
metric_space = selected_model.get("silhouette_metric_space", "Not available")
sil = selected_model.get("silhouette")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Narratives loaded", f"{n:,}")
col2.metric("Clusters", str(cluster_count))
col3.metric("Silhouette (sampled)", f"{sil:.4f}" if isinstance(sil, (int, float)) else "N/A")
col4.metric("Largest cluster", f"{selected_model.get('largest_cluster_share_pct', float('nan')):.2f}%" if selected_model else "N/A")
st.caption(f"Silhouette space: {metric_space}. Do not compare silhouette scores across different feature spaces.")
if report.get("interpretation_warning"):
    st.info(report["interpretation_warning"])

counts = df["cluster_id"].value_counts().reindex(cluster_ids, fill_value=0)
summary = pd.DataFrame({
    "cluster_id": cluster_ids,
    "records": [int(counts[c]) for c in cluster_ids],
})
summary["raw_share_of_loaded_candidates_pct"] = (100 * summary["records"] / max(n, 1)).round(2)
weighted_available = "candidate_frame_analysis_weight" in df.columns
if weighted_available:
    w = pd.to_numeric(df["candidate_frame_analysis_weight"], errors="coerce")
    if w.isna().any() or (w < 0).any() or w.sum() <= 0:
        weighted_available = False
    else:
        grouped_w = df.assign(_w=w).groupby("cluster_id")["_w"].sum()
        total_w = float(w.sum())
        summary["NEISS_weighted_candidate_frame_estimate"] = [round(float(grouped_w.get(c, 0)), 1) for c in cluster_ids]
        summary["NEISS_weighted_share_within_candidate_frame_pct"] = [round(100 * float(grouped_w.get(c, 0)) / total_w, 2) for c in cluster_ids]

st.subheader("Cluster distribution")
st.caption("Cluster IDs are arbitrary; they are not theme names until human reviewers assign and validate names.")
st.dataframe(summary, use_container_width=True, hide_index=True)
st.bar_chart(summary.set_index("cluster_id")[["raw_share_of_loaded_candidates_pct"]])
if weighted_available:
    st.write("NEISS-weighted point-estimate share within keyword-candidate frame")
    st.bar_chart(summary.set_index("cluster_id")[["NEISS_weighted_share_within_candidate_frame_pct"]])
    if "candidate_sample_expansion_factor" in df.columns:
        st.caption("Weights = NEISS case Weight × candidate-frame rows in year / sampled rows in year. This corrects the balanced-by-year benchmark sample for its sampling fraction.")
    else:
        st.caption("Full-frame run: weights are the original NEISS Weight for every keyword-screened candidate record; no subsample expansion is applied.")
    st.caption("These shares refer only to the keyword-candidate frame, not all older-adult falls. The prepared candidate CSV lacks Stratum/PSU, so design-based uncertainty intervals are not available.")
else:
    st.warning("No candidate-frame-expanded NEISS analysis weight found; weighted shares are not displayed.")

st.subheader("Cluster inspection")
left, right = st.columns(2)
with left:
    chosen_cluster = st.selectbox("Cluster", cluster_ids)
with right:
    year_values = sorted(df["Source_Year"].dropna().unique().tolist())
    chosen_year = st.selectbox("Year", ["All"] + year_values)

filtered = df[df["cluster_id"] == str(chosen_cluster)].copy()
if chosen_year != "All":
    filtered = filtered[filtered["Source_Year"] == chosen_year]
query = st.text_input("Search narratives", placeholder="e.g. slipped on water, getting out of bed, stairs")
if query.strip():
    filtered = filtered[filtered["Narrative_1"].fillna("").astype(str).str.contains(query.strip(), case=False, regex=False)]

terms = selected_model.get("top_terms_by_cluster", {}).get(str(chosen_cluster), []) if selected_model else []
if terms:
    st.write("**Top model terms (not validated theme labels):**", " · ".join(terms))
st.write(f"Showing {len(filtered):,} matching records")
show_cols = [c for c in ["CPSC_Case_Number", "Source_Year", "Age", "Sex", "Diagnosis", "Weight", "cluster_id"] if c in filtered.columns]
display = filtered[show_cols].copy()
display["Narrative"] = filtered["Narrative_1"].fillna("").astype(str)
st.dataframe(display.head(500), use_container_width=True, hide_index=True)
st.download_button("Download filtered cluster records", display.to_csv(index=False).encode("utf-8"), file_name=f"{path.stem}_cluster_{chosen_cluster}.csv", mime="text/csv")

st.divider()
st.subheader("Human-rated theme coherence")
st.write("Inspect a reproducible sample of narratives. A provisional theme name and score must be assigned by a human reviewer, not copied from model terms.")
n_examples = st.select_slider("Examples to inspect", options=[5, 10, 15], value=10)
cluster_group = df[df["cluster_id"] == str(chosen_cluster)]
examples = cluster_group.sample(n=min(n_examples, len(cluster_group)), random_state=42) if len(cluster_group) else cluster_group
for i, (_, row) in enumerate(examples.iterrows(), 1):
    st.markdown(f"**Example {i} · Case {row.get('CPSC_Case_Number', 'unknown')} · Year {row.get('Source_Year', 'unknown')}**")
    st.write(str(row.get("Narrative_1", "")))

old = pd.read_csv(RATING_FILE) if RATING_FILE.exists() else pd.DataFrame()
old_row = old[(old["experiment"] == path.name) & (old["cluster_id"].astype(str) == str(chosen_cluster))].tail(1) if not old.empty else pd.DataFrame()
def_theme = str(old_row.iloc[0]["theme_name"]) if not old_row.empty else ""
def_score = int(old_row.iloc[0]["rating_1_to_5"]) if not old_row.empty else 3
def_reviewer = str(old_row.iloc[0]["reviewer_id"]) if not old_row.empty else "R1"
def_notes = str(old_row.iloc[0]["notes"]) if not old_row.empty else ""
with st.form("coherence_rating_form"):
    theme = st.text_input("Provisional human theme name", value=def_theme)
    rating = st.slider("Coherence (1 = mixed/unrecognizable; 5 = one clear circumstance theme)", 1, 5, def_score)
    reviewer = st.text_input("Human reviewer ID", value=def_reviewer)
    notes = st.text_area("Why is the cluster coherent or mixed?", value=def_notes)
    submit = st.form_submit_button("Save human rating")
if submit:
    if not theme.strip() or not reviewer.strip():
        st.error("Theme name and reviewer ID are required.")
    else:
        new = pd.DataFrame([{
            "experiment": path.name,
            "cluster_id": str(chosen_cluster),
            "theme_name": theme.strip(),
            "rating_1_to_5": int(rating),
            "reviewer_id": reviewer.strip(),
            "notes": notes.strip(),
            "review_date": date.today().isoformat(),
            "examples_reviewed": int(len(examples)),
        }])
        if not old.empty:
            same = old["experiment"].astype(str).eq(path.name) & old["cluster_id"].astype(str).eq(str(chosen_cluster)) & old["reviewer_id"].astype(str).eq(reviewer.strip())
            old = old.loc[~same]
        RESULTS.mkdir(parents=True, exist_ok=True)
        pd.concat([old, new], ignore_index=True).to_csv(RATING_FILE, index=False)
        st.success(f"Saved human rating in {RATING_FILE.name}")
        st.rerun()

if RATING_FILE.exists():
    st.subheader("Saved human theme-coherence ratings")
    st.dataframe(pd.read_csv(RATING_FILE), use_container_width=True, hide_index=True)
