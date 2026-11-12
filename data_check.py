
"""Inspect and validate raw Amazon Electronics reviews before preprocessing."""

import pandas as pd
import re

INPUT_FILE = "amazon_reviews_raw.csv"
REPORT_FILE = "data_check_report.txt"

REQUIRED_COLUMNS = [
    "doc_id",
    "title",
    "review_text",
    "rating",
    "product_id",
    "timestamp",
    "verified_purchase"
]


def clean_text(series):
    return series.fillna("").astype(str).str.strip()


def normalize_document(text):
    text = str(text).lower()
    return re.sub(r"\s+", " ", text).strip()


def format_distribution(series):
    counts = series.value_counts(dropna=False).sort_index()
    return [
        f"{value}: {count}"
        for value, count in counts.items()
    ]


print("Reading raw reviews...")
data = pd.read_csv(INPUT_FILE)

# 1. Check required columns
missing_columns = [
    column for column in REQUIRED_COLUMNS
    if column not in data.columns
]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# 2. Basic data information
rows_total = len(data)

# 3. Check missing values
missing_values = data[REQUIRED_COLUMNS].isna().sum()

# 4. Check empty text fields
doc_ids = clean_text(data["doc_id"])
titles = clean_text(data["title"])
reviews = clean_text(data["review_text"])
products = clean_text(data["product_id"])

empty_ids = int(doc_ids.eq("").sum())
empty_titles = int(titles.eq("").sum())
empty_reviews = int(reviews.eq("").sum())
empty_products = int(products.eq("").sum())

# 5. Check duplicate document IDs
duplicate_ids = int(
    doc_ids[doc_ids.ne("")].duplicated().sum()
)

# 6. Check duplicate full documents
document_text = (titles + " " + reviews).str.strip()
normalized_documents = document_text.apply(normalize_document)

duplicate_documents = int(
    normalized_documents[
        normalized_documents.ne("")
    ].duplicated().sum()
)

# 7. Check rating values
ratings = pd.to_numeric(data["rating"], errors="coerce")

missing_ratings = int(ratings.isna().sum())

invalid_ratings = int(
    (ratings.notna() & ~ratings.between(1, 5)).sum()
)

valid_ratings = ratings[
    ratings.between(1, 5)
]

rating_distribution = format_distribution(
    ratings[ratings.between(1, 5)]
)

# 8. Review length statistics
valid_reviews = reviews[reviews.ne("")]

review_char_lengths = valid_reviews.str.len()
review_word_lengths = valid_reviews.str.split().str.len()

if len(valid_reviews) > 0:
    char_min = int(review_char_lengths.min())
    char_max = int(review_char_lengths.max())
    char_mean = round(review_char_lengths.mean(), 2)
    char_median = round(review_char_lengths.median(), 2)

    word_min = int(review_word_lengths.min())
    word_max = int(review_word_lengths.max())
    word_mean = round(review_word_lengths.mean(), 2)
    word_median = round(review_word_lengths.median(), 2)
else:
    char_min = char_max = char_mean = char_median = 0
    word_min = word_max = word_mean = word_median = 0

# 9. Check timestamps
timestamps = pd.to_numeric(data["timestamp"], errors="coerce")

missing_timestamps = int(timestamps.isna().sum())

invalid_timestamps = int(
    (timestamps.notna() & (timestamps <= 0)).sum()
)

# 10. Check verified purchase values
verified = clean_text(data["verified_purchase"]).str.lower()

accepted_values = [
    "true", "false", "1", "0", "yes", "no"
]

invalid_verified = int(
    (verified.ne("") & ~verified.isin(accepted_values)).sum()
)

verified_distribution = format_distribution(verified)

# 11. Calculate usable rows
# Exclude empty reviews, missing IDs and duplicate documents.
valid_mask = (
    reviews.ne("")
    & doc_ids.ne("")
    & ~normalized_documents.duplicated()
)

valid_data = data[valid_mask].copy()

rows_after_cleaning = len(valid_data)
removed_rows = rows_total - rows_after_cleaning

# 12. Calculate data quality percentage
quality_percentage = (
    round((rows_after_cleaning / rows_total) * 100, 2)
    if rows_total > 0 else 0
)

# 13. Generate report
report = [
    "CUSTOMER PRODUCT REVIEW SEARCH",
    "RAW DATA QUALITY ASSESSMENT",
    "=" * 55,
    "",
    "1. DATASET OVERVIEW",
    "-" * 55,
    f"Total rows: {rows_total}",
    f"Total columns: {len(data.columns)}",
    f"Required columns: {len(REQUIRED_COLUMNS)}",
    f"Missing required columns: {len(missing_columns)}",
    "",
    "Available columns:",
    ", ".join(data.columns.astype(str)),
    "",
    "2. MISSING AND EMPTY VALUES",
    "-" * 55,
]

for column in REQUIRED_COLUMNS:
    report.append(
        f"{column}: {int(missing_values[column])} missing values"
    )

report.extend([
    "",
    f"Empty document IDs: {empty_ids}",
    f"Empty titles: {empty_titles}",
    f"Empty review texts: {empty_reviews}",
    f"Empty product IDs: {empty_products}",
    "",
    "3. DUPLICATE CHECK",
    "-" * 55,
    f"Duplicate document IDs: {duplicate_ids}",
    f"Duplicate full documents: {duplicate_documents}",
    "",
    "4. RATING VALIDATION",
    "-" * 55,
    f"Missing or non-numeric ratings: {missing_ratings}",
    f"Ratings outside the range 1-5: {invalid_ratings}",
    "",
    "Rating distribution (valid ratings):",
])

report.extend(rating_distribution or ["No valid ratings found."])

report.extend([
    "",
    "5. REVIEW LENGTH STATISTICS",
    "-" * 55,
    f"Reviews with non-empty text: {len(valid_reviews)}",
    "",
    "Character length:",
    f"Minimum: {char_min}",
    f"Maximum: {char_max}",
    f"Average: {char_mean}",
    f"Median: {char_median}",
    "",
    "Word length:",
    f"Minimum: {word_min}",
    f"Maximum: {word_max}",
    f"Average: {word_mean}",
    f"Median: {word_median}",
    "",
    "6. TIMESTAMP VALIDATION",
    "-" * 55,
    f"Missing or non-numeric timestamps: {missing_timestamps}",
    f"Non-positive timestamps: {invalid_timestamps}",
    "",
    "7. VERIFIED PURCHASE CHECK",
    "-" * 55,
    f"Invalid verified purchase values: {invalid_verified}",
    "",
    "Verified purchase distribution:",
])

report.extend(verified_distribution or ["No values found."])

report.extend([
    "",
    "8. FINAL DATASET SUMMARY",
    "-" * 55,
    f"Original rows: {rows_total}",
    f"Rows with non-empty reviews: {rows_total - empty_reviews}",
    f"Rows after removing empty reviews, missing IDs, "
    f"and duplicate documents: {rows_after_cleaning}",
    f"Removed rows: {removed_rows}",
    f"Retained data percentage: {quality_percentage}%",
    "",
    "9. SAMPLE REVIEW",
    "-" * 55,
])

if not valid_data.empty:
    sample = valid_data.iloc[0]

    report.extend([
        f"Document ID: {sample['doc_id']}",
        f"Title: {str(sample['title'])[:250]}",
        f"Review: {str(sample['review_text'])[:500]}",
    ])
else:
    report.append("No valid reviews available.")

report.extend([
    "",
    "=" * 55,
    "END OF DATA QUALITY REPORT"
])

# 14. Save report without modifying the original dataset
with open(REPORT_FILE, "w", encoding="utf-8") as file:
    file.write("\n".join(report))

print("\n".join(report))
print(f"\nReport saved to: {REPORT_FILE}")
print("\nRaw dataset was not modified.")
