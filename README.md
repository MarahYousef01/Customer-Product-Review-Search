# Customer Product Review Search

**Dataset:** Amazon Reviews 2023 by McAuley Lab  
**Selected category:** Electronics

**Original dataset:** [Amazon Reviews 2023 - McAuley Lab](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)

The downloader reads the official Electronics review file as a compressed stream and stops after collecting 1,200 unique reviews. It does not download the full 6+ GB file.

## My part: Data Collection, Data Checking and Preprocessing

### Files

- `download_reviews.py`: downloads up to 1,200 unique Electronics reviews from the official Amazon Reviews 2023 compressed data file using streaming.
- `data_check.py`: checks the raw data, required columns, missing values and duplicate records.
- `preprocessing.py`: cleans and preprocesses the review text.
- `amazon_reviews_raw.csv`: downloaded original review sample.
- `documents.csv`: cleaned documents for the search engine.
- `data_check_report.txt`: raw data quality report.
- `preprocessing_report.txt`: preprocessing summary and before/after example.

## Setup

Install the required libraries:

```bash
python -m pip install -r requirements.txt
```

## Run the files in this order

### 1. Download the reviews

```bash
python download_reviews.py
```

The script collects up to 1,200 unique reviews. It uses streaming, so it does not download the complete dataset.

### 2. Check the raw data

```bash
python data_check.py
```

### 3. Preprocess the reviews

```bash
python preprocessing.py
```

The preprocessing steps are:

1. Lowercase.
2. Tokenization.
3. Remove English stopwords.
4. Porter stemming.
5. Remove empty and duplicate documents.

The final dataset keeps the original review information and adds `document_text` and `processed_text`.

## Important for the team

Use **the same `documents.csv` file** for both Boolean Search and Ranked Search.

- Use `doc_id` to identify each document.
- Use `processed_text` to build the Inverted Index and TF-IDF.
- Keep `document_text` or `review_text` to display the original review in search results.

The preprocessing script checks that at least 100 searchable documents remain.
