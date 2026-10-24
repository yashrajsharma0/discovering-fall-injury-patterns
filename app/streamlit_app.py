"""Lightweight Explorer for inspecting saved prototype assignments."""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / 'results' / 'prototype_assignments.csv'
SAMPLE = ROOT / 'data' / 'sample_fall_candidates.csv'

st.set_page_config(page_title='Fall Narrative Explorer', layout='wide')
st.title('Older-Adult Injury Narrative Explorer')
st.caption('Research prototype only — keyword candidates are not confirmed fall cases or medical advice.')
file_path = DEFAULT_RESULTS if DEFAULT_RESULTS.exists() else SAMPLE
try:
    df = pd.read_csv(file_path, low_memory=False)
except Exception as exc:
    st.error(f'Could not load the data file: {exc}')
    st.stop()
text_col = 'Narrative_1' if 'Narrative_1' in df.columns else ('clean_text' if 'clean_text' in df.columns else df.columns[0])
left, right = st.columns(2)
with left:
    st.metric('Narratives loaded', f'{len(df):,}')
with right:
    st.metric('Years represented', df['Source_Year'].nunique() if 'Source_Year' in df.columns else 'N/A')
if 'cluster_id' in df.columns:
    clusters = sorted(df['cluster_id'].dropna().unique().tolist())
    selected = st.selectbox('Choose model cluster', ['All'] + clusters)
    if selected != 'All':
        df = df[df['cluster_id'] == selected]
if 'Source_Year' in df.columns:
    years = sorted(df['Source_Year'].dropna().unique().tolist())
    selected_year = st.selectbox('Filter year', ['All'] + years)
    if selected_year != 'All':
        df = df[df['Source_Year'] == selected_year]
st.dataframe(df.head(300), use_container_width=True, hide_index=True)
st.caption('Showing up to 300 rows. Review and validate records before drawing conclusions.')
