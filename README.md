# Customer Product Review Search

**Dataset:** Amazon Reviews 2023 by McAuley Lab  
**Selected category:** Electronics

**Original dataset:** [Amazon Reviews 2023 - McAuley Lab](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)

This project downloads a sample of Electronics reviews, validates the raw dataset, preprocesses the review text, and prepares a cleaned CSV for search indexing.

## Project structure

```text
Customer-Product-Review-Search/
├── README.md
├── requirements.txt
├── src/
│   ├── data_collection/
│   │   └── download_reviews.py
│   ├── data_quality/
│   │   └── data_check.py
│   └── preprocessing/
│       └── preprocessing.py
├── data/
│   ├── raw/
│   │   └── amazon_reviews_raw.csv
│   └── processed/
│       └── documents.csv
└── reports/
    ├── data_check_report.txt
    └── preprocessing_report.txt
```

## What each part does

- `src/data_collection/download_reviews.py`: downloads a streaming sample of Amazon Electronics reviews and writes the raw CSV to `data/raw/`.
- `src/data_quality/data_check.py`: checks for missing values, duplicates, invalid ratings, malformed timestamps, and other data-quality issues; writes a summary to `reports/data_check_report.txt`.
- `src/preprocessing/preprocessing.py`: lowercases text, removes stop words, applies stemming, removes empty records, and saves the cleaned dataset to `data/processed/documents.csv`.
- `data/raw/amazon_reviews_raw.csv`: raw review dataset after the initial download.
- `data/processed/documents.csv`: final searchable document dataset with original fields plus `document_text`, `processed_text`, and `token_count`.
- `reports/*.txt`: generated quality and preprocessing summaries for auditing and debugging.

## Setup

Install the required libraries:

```bash
python -m pip install -r requirements.txt
```

## Run the workflow in order

### 1. Download the reviews

```bash
python src/data_collection/download_reviews.py
```

### 2. Check the raw data

```bash
python src/data_quality/data_check.py
```

### 3. Preprocess the reviews

```bash
python src/preprocessing/preprocessing.py
```

## Preprocessing pipeline

1. Lowercase text.
2. Preserve negation words such as "not" and "no".
3. Tokenize text into words and numbers.
4. Remove English stop words except negations.
5. Remove single-letter noise.
6. Apply Porter stemming.
7. Drop empty processed documents.

The final dataset keeps the original review information and adds `document_text` and `processed_text`.

## Important for the team

Use the same `data/processed/documents.csv` file for both Boolean Search and Ranked Search.

- Use `doc_id` to identify each document.
- Use `processed_text` to build the inverted index and TF-IDF.
- Keep `document_text` or `review_text` for displaying original review content.

The preprocessing script checks that at least 100 searchable documents remain.
