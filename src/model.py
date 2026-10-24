"""TF-IDF + KMeans prototype for unsupervised narrative theme discovery."""
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score


def fit_cluster_model(texts, n_clusters=6, random_state=42, max_features=30000):
    texts = list(texts)
    if len(texts) < max(3, n_clusters + 1):
        raise ValueError("Need more non-empty narratives than the requested cluster count.")
    vectorizer = TfidfVectorizer(
        stop_words="english", ngram_range=(1, 2), min_df=2,
        max_df=0.95, max_features=max_features, sublinear_tf=True
    )
    matrix = vectorizer.fit_transform(texts)
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = model.fit_predict(matrix)
    score = None
    if len(set(labels)) > 1 and len(set(labels)) < len(labels):
        # Sample rows to keep silhouette evaluation practical on larger datasets.
        score = float(silhouette_score(matrix, labels, sample_size=min(5000, len(texts)), random_state=random_state))
    return vectorizer, model, matrix, labels, score


def top_terms_by_cluster(vectorizer, model, top_n=12):
    terms = vectorizer.get_feature_names_out()
    output = {}
    for idx, center in enumerate(model.cluster_centers_):
        top_idx = center.argsort()[::-1][:top_n]
        output[int(idx)] = [str(terms[i]) for i in top_idx]
    return output
