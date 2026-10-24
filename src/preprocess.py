"""Text cleaning utilities for older-adult injury narratives."""
import re
import pandas as pd

TEXT_CANDIDATES = ("Narrative_1", "narrative", "text", "Narrative")

def find_text_column(df: pd.DataFrame) -> str:
    for col in TEXT_CANDIDATES:
        if col in df.columns:
            return col
    raise ValueError(f"No narrative text column found. Available columns: {list(df.columns)}")

def clean_narrative(value) -> str:
    """Normalize text while retaining medically meaningful words and numbers."""
    if pd.isna(value):
        return ""
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9\s'-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def add_clean_text(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    text_col = find_text_column(df)
    result = df.copy()
    result["clean_text"] = result[text_col].map(clean_narrative)
    result = result[result["clean_text"].str.len() > 0].reset_index(drop=True)
    return result, text_col
