"""Subsample-based clustering stability; reports ARI across overlapping subsamples."""
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def evaluate_stability(texts, n_clusters=6, repeats=5, sample_fraction=0.8, random_state=42):
    texts=list(texts)
    if len(texts)<n_clusters+2: raise ValueError('Not enough texts for stability evaluation')
    vec=TfidfVectorizer(stop_words='english',ngram_range=(1,2),min_df=2,max_df=.95,max_features=30000,sublinear_tf=True)
    X=vec.fit_transform(texts)
    rng=np.random.default_rng(random_state); n=len(texts); m=max(n_clusters+2,int(n*sample_fraction))
    assignments=[]
    for i in range(repeats):
        idx=np.sort(rng.choice(n,size=min(m,n),replace=False))
        model=KMeans(n_clusters=n_clusters,random_state=random_state+i,n_init=10)
        labels=model.fit_predict(X[idx])
        assignments.append((idx,labels))
    scores=[]
    for i in range(len(assignments)):
        for j in range(i+1,len(assignments)):
            ix,li=assignments[i]; jx,lj=assignments[j]
            common, a, b=np.intersect1d(ix,jx,return_indices=True)
            if len(common)>n_clusters: scores.append(float(adjusted_rand_score(li[a],lj[b])))
    return {'method':'ARI between cluster assignments on overlapping random subsamples','n_rows':n,'n_clusters':n_clusters,'repeats':repeats,'sample_fraction':sample_fraction,'pairwise_ari':scores,'mean_pairwise_ari':float(np.mean(scores)) if scores else None,'std_pairwise_ari':float(np.std(scores)) if scores else None,'warning':'Stability is not semantic correctness; interpret alongside manual theme coherence review.'}
