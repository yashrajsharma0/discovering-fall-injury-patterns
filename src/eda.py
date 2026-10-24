"""Exploratory summary and figures for age-65+ NEISS fall candidates."""
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input', required=True, help='Path to age65+ or fall-candidate CSV')
    p.add_argument('--out', default='results/eda')
    a=p.parse_args()
    out=Path(a.out); out.mkdir(parents=True, exist_ok=True)
    df=pd.read_csv(a.input, low_memory=False)
    summary={'rows':int(len(df)),'columns':list(df.columns)}
    if 'Source_Year' in df: summary['rows_by_year']={str(k):int(v) for k,v in df['Source_Year'].value_counts().sort_index().items()}
    if 'Age' in df:
        summary['age_summary']={k:float(v) for k,v in df['Age'].describe().to_dict().items()}
        plt.figure(figsize=(8,4.5)); df['Age'].dropna().astype(float).plot(kind='hist', bins=20, edgecolor='black'); plt.xlabel('Age'); plt.ylabel('Records'); plt.title('Age distribution (65+ NEISS records)'); plt.tight_layout(); plt.savefig(out/'age_distribution.png', dpi=160); plt.close()
    if 'Source_Year' in df:
        counts=df['Source_Year'].value_counts().sort_index()
        plt.figure(figsize=(8,4.5)); counts.plot(kind='bar', edgecolor='black'); plt.xlabel('Source year'); plt.ylabel('Records'); plt.title('Candidate records by year'); plt.tight_layout(); plt.savefig(out/'records_by_year.png', dpi=160); plt.close()
        summary['year_candidate_counts']={str(k):int(v) for k,v in counts.items()}
    if 'Fall_Keywords_Matched' in df:
        summary['keyword_match_counts']=df['Fall_Keywords_Matched'].fillna('none').value_counts().to_dict()
    (out/'eda_summary.json').write_text(__import__('json').dumps(summary,indent=2),encoding='utf-8')
    print(__import__('json').dumps(summary,indent=2))
if __name__=='__main__': main()
