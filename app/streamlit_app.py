"""Local Streamlit Explorer for saved fall-narrative cluster assignments.

The app reads local CSVs only. It does not upload datasets to a server.
"""
from datetime import date
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RATING_FILE = RESULTS / "human_coherence_ratings.csv"

EXPERIMENT_FILES = {
    "Existing prototype": RESULTS / "prototype_assignments.csv",
    "Original 5k control": RESULTS / "control_5000" / "prototype_assignments.csv",
    "V2 candidate (exploratory)": RESULTS / "circumstance_v2_5000" / "prototype_assignments.csv",
    "V3 candidate (exploratory)": RESULTS / "circumstance_v3_5000" / "prototype_assignments.csv",
    "V4 candidate (exploratory)": RESULTS / "circumstance_v4_5000" / "prototype_assignments.csv",
}

st.set_page_config(page_title="Fall Narrative Explorer", page_icon="🔎", layout="wide")
st.title("Older-Adult Fall Narrative Explorer")
st.caption(
    "Exploratory research tool. Keyword-screened candidates are not confirmed falls; "
    "cluster shares describe only the loaded candidate file, not population prevalence."
)

with st.sidebar:
    st.header("Choose experiment")
    upload = st.file_uploader("Or upload an assignments CSV", type=["csv"])
    available = {name: path for name, path in EXPERIMENT_FILES.items() if path.exists()}
    selected_name = None
    selected_path = None
    if available:
        selected_name = st.selectbox("Local results", list(available))
        selected_path = available[selected_name]
    else:
        st.info("No saved local assignments found. Upload an assignments CSV.")
    st.divider()
    st.caption("The full source dataset and assignments remain on this computer.")

if upload is not None:
    df = pd.read_csv(upload, low_memory=False)
    experiment_name = Path(upload.name).stem
    metrics_path = None
    st.info(f"Using uploaded file: {upload.name}")
elif selected_path is not None:
    df = pd.read_csv(selected_path, low_memory=False)
    experiment_name = selected_name or selected_path.parent.name
    metrics_path = selected_path.parent / "prototype_metrics.json"
else:
    st.warning(
        "Run a clustering experiment locally, then select its results/prototype_assignments.csv "
        "file here or upload the assignments CSV."
    )
    st.stop()

if "cluster_id" not in df.columns:
    st.error("This file has no cluster_id column. Select a saved clustering assignments CSV.")
    st.stop()

df = df.copy()
df["cluster_id"] = df["cluster_id"].astype(str)
cluster_ids = sorted(df["cluster_id"].dropna().unique(), key=lambda x: int(x) if x.isdigit() else x)
if not cluster_ids:
    st.error("No cluster IDs were found in this file.")
    st.stop()

ratings = pd.read_csv(RATING_FILE) if RATING_FILE.exists() else pd.DataFrame(
    columns=["experiment", "cluster_id", "theme_name", "rating_1_to_5", "reviewer_id", "notes", "review_date", "examples_reviewed"]
)
current_ratings = ratings[ratings["experiment"].astype(str) == str(experiment_name)] if not ratings.empty else ratings
label_map = {}
if not current_ratings.empty:
    label_map = {
        str(row["cluster_id"]): str(row["theme_name"])
        for _, row in current_ratings.iterrows()
        if pd.notna(row.get("theme_name")) and str(row.get("theme_name")).strip()
    }

narrative_col = "Original_Narrative_1" if "Original_Narrative_1" in df.columns else (
    "Narrative_1" if "Narrative_1" in df.columns else ("clean_text" if "clean_text" in df.columns else None)
)
if narrative_col is None:
    st.error("No narrative text column was found.")
    st.stop()

cluster_counts = df["cluster_id"].value_counts().reindex(cluster_ids, fill_value=0)
cluster_summary = pd.DataFrame({
    "cluster_id": cluster_ids,
    "working_theme_name": [label_map.get(c, f"Cluster {c} — provisional") for c in cluster_ids],
    "records": [int(cluster_counts[c]) for c in cluster_ids],
})
cluster_summary["share_of_loaded_candidates_pct"] = (
    100 * cluster_summary["records"] / max(len(df), 1)
).round(2)

metric_path = metrics_path if metrics_path and metrics_path.exists() else None
metrics = {}
if metric_path:
    try:
        metrics = json.loads(metric_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        metrics = {}

st.subheader(f"Experiment: {experiment_name}")
if metrics.get("warning"):
    st.warning(metrics["warning"])

m1, m2, m3, m4 = st.columns(4)
m1.metric("Narratives loaded", f"{len(df):,}")
m2.metric("Clusters", f"{len(cluster_ids)}")
m3.metric("Years represented", f"{df['Source_Year'].nunique()}" if "Source_Year" in df.columns else "Not available")
m4.metric("Silhouette (saved run)", f"{metrics['silhouette_score_sampled']:.4f}" if isinstance(metrics.get("silhouette_score_sampled"), (int, float)) else "Not available")

st.subheader("Theme distribution")
st.caption("Shares are calculated within the selected assignments file. They are not estimates of all real-world falls.")
st.dataframe(cluster_summary, use_container_width=True, hide_index=True)
st.bar_chart(cluster_summary.set_index("working_theme_name")[["records"]])

st.subheader("Theme drill-down")
f1, f2 = st.columns(2)
with f1:
    chosen_cluster = st.selectbox("Cluster", ["All"] + cluster_ids)
with f2:
    years = sorted(df["Source_Year"].dropna().unique().tolist()) if "Source_Year" in df.columns else []
    chosen_year = st.selectbox("Treatment year", ["All"] + years) if years else "All"

filtered = df.copy()
if chosen_cluster != "All":
    filtered = filtered[filtered["cluster_id"] == str(chosen_cluster)]
if chosen_year != "All" and "Source_Year" in filtered.columns:
    filtered = filtered[filtered["Source_Year"] == chosen_year]

search_text = st.text_input("Search narratives (optional)", placeholder="e.g. slipped on water, getting out of bed, stairs")
if search_text.strip():
    filtered = filtered[filtered[narrative_col].fillna("").astype(str).str.contains(search_text.strip(), case=False, regex=False)]

if chosen_cluster != "All" and metrics.get("top_terms_by_cluster"):
    terms = metrics["top_terms_by_cluster"].get(str(chosen_cluster), [])
    if terms:
        st.write("**Model terms for this cluster:**", ", ".join(terms))

display_cols = [c for c in [
    "CPSC_Case_Number", "Source_Year", "Treatment_Date", "Age", "Sex",
    "Body_Part", "Diagnosis", "baseline_group", "cluster_id", "Fall_Keywords_Matched"
] if c in filtered.columns]
display = filtered[display_cols].copy() if display_cols else pd.DataFrame(index=filtered.index)
display["Narrative"] = filtered[narrative_col].fillna("").astype(str)
st.write(f"Showing {len(filtered):,} matching records.")
st.dataframe(display.head(500), use_container_width=True, hide_index=True)
st.download_button(
    "Download filtered records",
    data=display.to_csv(index=False).encode("utf-8"),
    file_name=f"{experiment_name.replace(' ', '_')}_filtered_records.csv",
    mime="text/csv",
)

st.divider()
st.subheader("Human-rated theme coherence")
st.write(
    "For one cluster at a time, inspect three reproducibly sampled narratives and rate whether "
    "they express one recognizable circumstance theme. This is a single-reviewer pilot rating, "
    "not inter-rater reliability."
)

rating_cluster = st.selectbox("Cluster to rate", cluster_ids, key="rating_cluster")
group = df[df["cluster_id"] == str(rating_cluster)]
examples = group.sample(n=min(3, len(group)), random_state=42) if len(group) else group
for i, (_, row) in enumerate(examples.iterrows(), start=1):
    case_id = row.get("CPSC_Case_Number", "Unknown case")
    year = row.get("Source_Year", "Year unavailable")
    st.markdown(f"**Example {i} · Case {case_id} · {year}**")
    st.write(str(row.get(narrative_col, "")))

old = current_ratings[current_ratings["cluster_id"].astype(str) == str(rating_cluster)] if not current_ratings.empty else pd.DataFrame()
old_row = old.iloc[-1] if not old.empty else None
default_theme = str(old_row["theme_name"]) if old_row is not None and pd.notna(old_row["theme_name"]) else ""
default_rating = int(old_row["rating_1_to_5"]) if old_row is not None and pd.notna(old_row["rating_1_to_5"]) else 3
default_reviewer = str(old_row["reviewer_id"]) if old_row is not None and pd.notna(old_row["reviewer_id"]) else "R1"
default_notes = str(old_row["notes"]) if old_row is not None and pd.notna(old_row["notes"]) else ""

with st.form(f"coherence-form-{experiment_name}-{rating_cluster}"):
    theme_name = st.text_input("Working theme name (write a short descriptive label)", value=default_theme)
    score = st.slider(
        "How coherent are these examples as one circumstance theme? (1 = not coherent, 5 = very coherent)",
        min_value=1, max_value=5, value=default_rating
    )
    reviewer_id = st.text_input("Reviewer ID", value=default_reviewer)
    notes = st.text_area("Brief reason or mixed patterns noticed", value=default_notes)
    submitted = st.form_submit_button("Save this cluster rating")

if submitted:
    if not theme_name.strip() or not reviewer_id.strip():
        st.error("Enter a theme name and reviewer ID before saving.")
    else:
        new_row = {
            "experiment": experiment_name,
            "cluster_id": str(rating_cluster),
            "theme_name": theme_name.strip(),
            "rating_1_to_5": int(score),
            "reviewer_id": reviewer_id.strip(),
            "notes": notes.strip(),
            "review_date": date.today().isoformat(),
            "examples_reviewed": int(len(examples)),
        }
        RESULTS.mkdir(parents=True, exist_ok=True)
        existing = pd.read_csv(RATING_FILE) if RATING_FILE.exists() else pd.DataFrame()
        if not existing.empty:
            same = (
                existing["experiment"].astype(str).eq(str(experiment_name))
                & existing["cluster_id"].astype(str).eq(str(rating_cluster))
                & existing["reviewer_id"].astype(str).eq(reviewer_id.strip())
            )
            existing = existing.loc[~same]
        updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
        updated.to_csv(RATING_FILE, index=False)
        st.success(f"Saved rating for cluster {rating_cluster} to {RATING_FILE.name}.")
        st.rerun()

if RATING_FILE.exists():
    st.subheader("Saved coherence ratings")
    st.dataframe(pd.read_csv(RATING_FILE), use_container_width=True, hide_index=True)
    st.download_button(
        "Download coherence ratings",
        data=RATING_FILE.read_bytes(),
        file_name="human_coherence_ratings.csv",
        mime="text/csv",
    )
