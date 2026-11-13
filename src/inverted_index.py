
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT_DIR / "data" / "processed" / "documents.csv"

# Load the processed dataset
data = pd.read_csv(INPUT_FILE)

# Create an empty inverted index
inverted_index = {}

# Go through every document
for _, row in data.iterrows():

    # Get the document ID
    doc_id = row["doc_id"]

    # Get the processed words
    terms = set(str(row["processed_text"]).split())

    # Add each word to the inverted index
    for term in terms:

        if term not in inverted_index:
            inverted_index[term] = set()

        inverted_index[term].add(doc_id)


# Display indexing results
print("Total documents:", len(data))
print("Total unique terms:", len(inverted_index))

''' 
Display a few examples
for term in list(inverted_index.keys())[:10]:
    print(term, ":", inverted_index[term])
'''
   