
"""Clean and preprocess Amazon Electronics reviews for information retrieval."""

import re
from pathlib import Path

import pandas as pd
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = ROOT_DIR / "data" / "raw" / "amazon_reviews_raw.csv"
OUTPUT_FILE = ROOT_DIR / "data" / "processed" / "documents.csv"
REPORT_FILE = ROOT_DIR / "reports" / "preprocessing_report.txt"
MIN_DOCUMENTS = 100

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

REQUIRED_COLUMNS = [
    "doc_id",
    "title",
    "review_text",
    "rating",
    "product_id",
    "timestamp",
    "verified_purchase"
]

stemmer = PorterStemmer()

# Preserve negation because it changes review meaning.
NEGATION_WORDS = {"no", "not", "nor", "never"}

STOP_WORDS = set(ENGLISH_STOP_WORDS) - NEGATION_WORDS


def preprocess_text(text):
    """Normalize, tokenize, remove stop words, and stem text."""

    text = str(text).lower()

    # Preserve negation in common English contractions.
    text = re.sub(r"n't\b", " not", text)

    # Keep English words and numeric/product-related tokens.
    tokens = re.findall(r"[a-z0-9]+", text)

    processed_tokens = []

    for token in tokens:
        if token in STOP_WORDS:
            continue

        # Remove single-letter noise but preserve numeric tokens.
        if len(token) == 1 and not token.isdigit():
            continue

        processed_tokens.append(stemmer.stem(token))

    return " ".join(processed_tokens)


def normalize_document(text):
    """Normalize text for duplicate detection."""

    return re.sub(r"\s+", " ", str(text).lower()).strip()


def main():

    print("Reading raw Amazon Electronics reviews...")

    data = pd.read_csv(INPUT_FILE)

    # 1. Validate required columns.
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    original_rows = len(data)

    # 2. Prepare text fields without modifying the original file.
    titles = data["title"].fillna("").astype(str).str.strip()
    reviews = data["review_text"].fillna("").astype(str).str.strip()
    doc_ids = data["doc_id"].fillna("").astype(str).str.strip()

    # 3. Check document IDs.
    missing_ids = int(doc_ids.eq("").sum())

    duplicate_ids = int(
        doc_ids[doc_ids.ne("")].duplicated().sum()
    )

    if duplicate_ids > 0:
        raise ValueError(
            f"Found {duplicate_ids} duplicate document IDs. "
            "Document IDs must be unique."
        )

    # 4. Remove empty reviews and missing document IDs.
    valid_mask = reviews.ne("") & doc_ids.ne("")

    valid_data = data.loc[valid_mask].copy()

    valid_data["title"] = titles.loc[valid_mask]
    valid_data["review_text"] = reviews.loc[valid_mask]
    valid_data["doc_id"] = doc_ids.loc[valid_mask]

    rows_after_validation = len(valid_data)

    # 5. Combine title and review text.
    valid_data["document_text"] = (
        valid_data["title"] + " " +
        valid_data["review_text"]
    ).str.strip()

    # 6. Remove duplicate full documents.
    normalized_documents = (
        valid_data["document_text"].apply(normalize_document)
    )

    duplicate_documents = int(
        normalized_documents.duplicated().sum()
    )

    valid_data = valid_data.loc[
        ~normalized_documents.duplicated()
    ].copy()

    rows_after_duplicates = len(valid_data)

    # 7. Apply text preprocessing.
    print("Applying text preprocessing...")

    valid_data["processed_text"] = (
        valid_data["document_text"].apply(preprocess_text)
    )

    # 8. Remove documents with no remaining searchable tokens.
    empty_processed = int(
        valid_data["processed_text"].str.strip().eq("").sum()
    )

    valid_data = valid_data[
        valid_data["processed_text"].str.strip().ne("")
    ].copy()

    final_rows = len(valid_data)

    # 9. Calculate token statistics.
    valid_data["token_count"] = (
        valid_data["processed_text"].str.split().str.len()
    )

    if final_rows > 0:
        average_tokens = round(
            valid_data["token_count"].mean(), 2
        )
        minimum_tokens = int(
            valid_data["token_count"].min()
        )
        maximum_tokens = int(
            valid_data["token_count"].max()
        )
    else:
        average_tokens = 0
        minimum_tokens = 0
        maximum_tokens = 0

    # 10. Check minimum dataset size.
    if final_rows < MIN_DOCUMENTS:
        raise ValueError(
            f"Only {final_rows} documents remain after preprocessing. "
            f"Minimum required: {MIN_DOCUMENTS}."
        )

    # 11. Save processed documents.
    valid_data.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # 12. Generate preprocessing report.
    report = [
        "CUSTOMER PRODUCT REVIEW SEARCH",
        "PREPROCESSING REPORT",
        "=" * 55,
        "",
        "1. DATASET SUMMARY",
        "-" * 55,
        f"Original rows: {original_rows}",
        f"Empty document IDs: {missing_ids}",
        f"Duplicate document IDs: {duplicate_ids}",
        f"Rows after removing empty reviews and missing IDs: "
        f"{rows_after_validation}",
        f"Duplicate full documents removed: {duplicate_documents}",
        f"Rows after duplicate removal: {rows_after_duplicates}",
        f"Empty processed documents removed: {empty_processed}",
        f"Final processed documents: {final_rows}",
        f"Total removed rows: {original_rows - final_rows}",
        "",
        "2. PREPROCESSING OPERATIONS",
        "-" * 55,
        "1. Convert text to lowercase.",
        "2. Preserve negation words.",
        "3. Tokenize text into words and numbers.",
        "4. Remove English stop words except negations.",
        "5. Remove single-letter alphabetic tokens.",
        "6. Apply Porter Stemming.",
        "7. Remove empty processed documents.",
        "",
        "3. TOKEN STATISTICS",
        "-" * 55,
        f"Average tokens per document: {average_tokens}",
        f"Minimum tokens: {minimum_tokens}",
        f"Maximum tokens: {maximum_tokens}",
        "",
        "4. OUTPUT INFORMATION",
        "-" * 55,
        f"Output file: {OUTPUT_FILE}",
        f"Report file: {REPORT_FILE}",
        "Original metadata and text fields are preserved.",
        "Additional fields: document_text, processed_text, token_count",
        "",
        "5. SAMPLE PROCESSED DOCUMENT",
        "-" * 55,
    ]

    if final_rows > 0:
        sample = valid_data.iloc[0]

        report.extend([
            f"Document ID: {sample['doc_id']}",
            f"Original text: {sample['document_text'][:500]}",
            f"Processed text: {sample['processed_text'][:500]}",
            f"Token count: {sample['token_count']}"
        ])

    report.extend([
        "",
        "=" * 55,
        "END OF PREPROCESSING REPORT"
    ])

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(report))

    print("\n".join(report))
    print("\nPreprocessing completed successfully.")


if __name__ == "__main__":
    main()
