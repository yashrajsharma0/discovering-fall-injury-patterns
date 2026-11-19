"""TF-IDF + KMeans prototype with negation-preserving stop words."""

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics import silhouette_score


# Preserve words that can reverse or qualify the meaning of a narrative.
NEGATION_TERMS = {
    "no", "nor", "not", "never", "neither", "none", "without"
}


def build_vectorizer(
    max_features=30000,
    min_df=2,
    max_df=0.95
):
    """Create TF-IDF vectorizer without removing negation terms."""
    custom_stop_words = sorted(
        ENGLISH_STOP_WORDS.difference(NEGATION_TERMS)
    )

    return TfidfVectorizer(
        stop_words=custom_stop_words,
        ngram_range=(1, 2),
        min_df=min_df,
        max_df=max_df,
        max_features=max_features,
        sublinear_tf=True
    )


def fit_cluster_model(texts, n_clusters=6, random_state=42, max_features=30000):
    texts = list(texts)

    if len(texts) < max(3, n_clusters + 1):
        raise ValueError(
            "Need more non-empty narratives than the requested cluster count."
        )

    vectorizer = build_vectorizer(max_features=max_features)
    matrix = vectorizer.fit_transform(texts)

    model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10
    )

    labels = model.fit_predict(matrix)

    score = None

    if len(set(labels)) > 1 and len(set(labels)) < len(labels):
        score = float(
            silhouette_score(
                matrix,
                labels,
                sample_size=min(5000, len(texts)),
                random_state=random_state
            )
        )

    return vectorizer, model, matrix, labels, score


def top_terms_by_cluster(vectorizer, model, top_n=12):
    terms = vectorizer.get_feature_names_out()
    output = {}

    for idx, center in enumerate(model.cluster_centers_):
        top_idx = center.argsort()[::-1][:top_n]
        output[int(idx)] = [
            str(terms[i]) for i in top_idx
        ]

    return output
