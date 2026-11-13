# Import the inverted index
from inverted_index import inverted_index

# Get all document IDs
all_docs = set(data["doc_id"])

# Get user's query
query = input("Enter your search query: ").lower()

# Split the query into parts
parts = query.split()

# Identify the Boolean operator
if "and" in parts:
    operator = "and"

elif "or" in parts:
    operator = "or"

elif "not" in parts:
    operator = "not"

else:
    operator = None


# Get the search terms (excluding operators)
search_terms = []

# Remove Boolean operators from search terms 
search_terms = [
    word for word in parts
    if word not in ["and", "or", "not"]
]

# Preprocess search terms
from preprocessing.preprocessing import preprocess_text

search_terms = [
    preprocess_text(term) for term in search_terms
]

# Perform Boolean operations
if operator == "and":

    if "not" in parts:
        result = (
            inverted_index.get(search_terms[0], set())
            - inverted_index.get(search_terms[1], set())
        )
    else:
        result = (
            inverted_index.get(search_terms[0], set())
            & inverted_index.get(search_terms[1], set())
        )

elif operator == "or":

    result = (
        inverted_index.get(search_terms[0], set())
        | inverted_index.get(search_terms[1], set())
    )

elif operator == "not":

    result = (
        all_docs - inverted_index.get(search_terms[0], set())
    )

else:
    result = set()

# Display matching documents
print("\nSearch Results:")
print("-" * 40)

matching_docs = data[data["doc_id"].isin(result)]

for _, row in matching_docs.iterrows():
    print("Document ID:", row["doc_id"])
    print("Title:", row["title"])
    print("-" * 40)

print("Total results:", len(matching_docs)) 


# Reviewed and verified by sondos


