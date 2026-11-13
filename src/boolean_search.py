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
