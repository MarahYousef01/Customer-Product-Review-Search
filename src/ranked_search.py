import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocessing.preprocessing import preprocess_text


# =============================================================================
# 1. Load Dataset
# =============================================================================
df = pd.read_csv("data/processed/documents.csv")
print("Total documents:", len(df))


# =============================================================================
# 2. TF-IDF Document Representation
# =============================================================================
documents = df["processed_text"].fillna("").astype(str)
vectorizer = TfidfVectorizer(
    tokenizer=str.split,
    token_pattern=None,
    lowercase=False,
)
tfidf_matrix = vectorizer.fit_transform(documents)

print("Vocabulary size:", len(vectorizer.vocabulary_))
print("TF-IDF matrix shape:", tfidf_matrix.shape)


# =============================================================================
# 3. Cosine Similarity and Top-K Ranking
# =============================================================================
def ranked_search(query, top_k=5):
    columns = ["Rank", "doc_id", "title", "Similarity Score"]
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
        raise ValueError("top_k must be a positive integer.")
    if not isinstance(query, str) or not query.strip():
        return pd.DataFrame(columns=columns)

    processed_query = preprocess_text(query)
    if not processed_query.strip():
        return pd.DataFrame(columns=columns)

    query_vector = vectorizer.transform([processed_query])
    if query_vector.nnz == 0:
        return pd.DataFrame(columns=columns)

    scores = cosine_similarity(query_vector, tfidf_matrix).ravel()
    valid_indices = np.flatnonzero(scores > 0)
    order = np.lexsort((valid_indices, -scores[valid_indices]))
    top_indices = valid_indices[order[:top_k]]

    results = df.iloc[top_indices][["doc_id", "title"]].copy()
    results.insert(0, "Rank", range(1, len(results) + 1))
    results["Similarity Score"] = np.round(scores[top_indices], 4)
    return results.reset_index(drop=True)


# =============================================================================
# 4. Test Three Queries
# =============================================================================
test_queries = [
    "gasoline smell",
    "battery life",
    "wireless headphones sound quality",
]

for query in test_queries:
    print(f"\nQuery: {query}")
    results = ranked_search(query, top_k=5)
    print(results.to_string(index=False))


# =============================================================================
# 5. Results and Discussion
# =============================================================================
# Query: gasoline smell
# Top result: R00295 - Nice cover for my Kindle (0.3876)
# This result is only partially relevant, illustrating that TF-IDF ranks
# lexical similarity rather than fully understanding the query's meaning.

# Query: battery life
# Top result: R05569 - Best battery life of any I’ve had. (0.6966)
# This result directly matches the battery-life topic of the query.

# Query: wireless headphones sound quality
# Top result: R10809 - Great headphones (0.5845)
# This result is relevant to headphones but does not fully cover every
# detail of the query, such as wireless connectivity and sound quality.


# =============================================================================
# 6. Input Validation
# =============================================================================
for query in ["", "the and of", "zzzxxyyqqq"]:
    assert ranked_search(query).empty
print("\nInput validation passed.")
