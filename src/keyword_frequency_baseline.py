"""Required keyword-frequency baseline for the allocated objective."""
from pathlib import Path
import argparse
import re
import pandas as pd

KEYWORDS = {
    'fall_word': r'\b(fall|falls|fell|fallen|falling)\b',
    'slip': r'\b(slip|slips|slipped|slipping)\b',
    'trip': r'\b(trip|trips|tripped|tripping)\b',
    'stumble_or_tumble': r'\b(stumble|stumbled|stumbling|tumble|tumbled|tumbling)\b',
    'missed_step': r'\b(missed step|missed a step|misstep)\b',
    'balance': r'\b(lost balance|loss of balance|losing balance|unsteady)\b',
    'bed_or_floor': r'\b(bed|floor|couch|sofa|recliner|chair)\b',
    'stairs_or_steps': r'\b(stairs|staircase|steps|step stool|ladder)\b',
    'bathroom_or_shower': r'\b(bathroom|shower|bathtub|tub|toilet)\b',
    'walker_or_cane': r'\b(walker|cane|walking stick)\b',
}

def frequency_table(texts):
    texts = pd.Series(texts).fillna('').astype(str).str.lower()
    rows=[]
    for label, pattern in KEYWORDS.items():
        count=int(texts.str.contains(pattern, regex=True).sum())
        rows.append({'keyword_group':label,'narratives_matching':count,'share_of_candidates_pct':round(100*count/max(len(texts),1),3)})
    return pd.DataFrame(rows).sort_values('narratives_matching',ascending=False).reset_index(drop=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True)
    p.add_argument('--out',default='results/keyword_frequency_baseline.csv')
    p.add_argument('--text-column',default='Narrative_1')
    a=p.parse_args()
    df=pd.read_csv(a.input,low_memory=False)
    if a.text_column not in df.columns: raise SystemExit(f'Missing text column {a.text_column}; columns={list(df.columns)}')
    result=frequency_table(df[a.text_column])
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); result.to_csv(out,index=False)
    print(result.to_string(index=False))
if __name__=='__main__': main()
