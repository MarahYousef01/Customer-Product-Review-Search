
# Import the inverted index and dataset
from inverted_index import inverted_index, data

# Import preprocessing
from preprocessing.preprocessing import preprocess_text

# Get all document IDs
all_docs = set(data["doc_id"])

# Get user's query
query = input("Enter your search query: ").lower().strip()

# Split the query
parts = query.split()

# Remove Boolean operators and preprocess search terms
operators = ["and", "or", "not"]

search_terms = [
    preprocess_text(word)
    for word in parts
    if word not in operators
]

# Remove empty terms
search_terms = [term for term in search_terms if term]

# Perform Boolean operations
if len(search_terms) == 0:
    result = set()

elif "and" in parts and "not" in parts:

    result = (
        inverted_index.get(search_terms[0], set())
        - inverted_index.get(search_terms[1], set())
    )

elif "and" in parts:

    result = (
        inverted_index.get(search_terms[0], set())
        & inverted_index.get(search_terms[1], set())
    )

elif "or" in parts:

    result = (
        inverted_index.get(search_terms[0], set())
        | inverted_index.get(search_terms[1], set())
    )

elif "not" in parts and parts[0] == "not":

    result = (
        all_docs - inverted_index.get(search_terms[0], set())
    )

elif "not" in parts:

    result = (
        inverted_index.get(search_terms[0], set())
        - inverted_index.get(search_terms[1], set())
    )

else:
    result = inverted_index.get(search_terms[0], set())

# Display matching documents
print("\nSearch Results:")
print("-" * 40)

matching_docs = data[data["doc_id"].isin(result)]

for _, row in matching_docs.iterrows():
    print("Document ID:", row["doc_id"])
    print("Title:", row["title"])
    print("Review:", row["review_text"])
    print("-" * 40)

print("Total results:", len(matching_docs))

# Reviewed and verified by Sondos
