# ML Models Directory

This directory contains trained machine learning models for Atlas identity resolution.

## Directory Structure

```
models/
├── embeddings/           # Trained TF-IDF and SVD models
│   ├── name_tfidf_vectorizer.pkl
│   ├── name_svd_model.pkl
│   ├── location_tfidf_vectorizer.pkl
│   └── location_svd_model.pkl
│
└── fasttext/            # Pre-trained FastText word embeddings
    └── cc.en.100.bin    # Download required (958MB)
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure these packages are enabled:
- `scikit-learn==1.4.0`
- `fuzzywuzzy==0.18.0`
- `python-Levenshtein==0.23.0`
- `fasttext==0.9.2`
- `pyyaml==6.0.1`

### 2. Download FastText Model

**Option A: Using the download script (recommended)**
```bash
python scripts/download_fasttext.py
```

**Option B: Manual download**
1. Download: https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.100.bin.gz
2. Extract the `.gz` file
3. Place `cc.en.100.bin` in `models/fasttext/`

### 3. Train ML Models

```bash
python scripts/train_ml_models.py
```

This will:
- Load all 200 CoreSignal and RocketReach profiles
- Train TF-IDF vectorizers on names and locations
- Fit TruncatedSVD for dimensionality reduction
- Save 4 pickle files to `models/embeddings/`

### 4. Run Hybrid Matching

```bash
python scripts/hybrid_matching.py
```

This combines deterministic matching (Phase 1) with ML matching (Phase 2).

### 5. Validate Results

```bash
python scripts/validate_ml_matches.py
```

Shows match statistics and detailed analysis of ML matches.

## Model Details

### Name Embeddings
- **TF-IDF**: Character-level n-grams (2-5), 100 SVD components, 70% weight
- **FastText**: Word-level semantic embeddings, 100 dimensions, 30% weight
- Captures: Typos, spelling variations, name variants (e.g., "Robert" vs "Bob")

### Location Embeddings
- **TF-IDF**: Word-level n-grams (1-2), 50 SVD components, 30% weight
- **FastText**: Semantic location embeddings, 100 dimensions, 70% weight
- Captures: Geographic proximity, abbreviations (e.g., "SF" vs "San Francisco")

### Similarity Scoring
- **Final score** = 0.6 × name_similarity + 0.4 × location_similarity
- **Threshold**: 0.95 (very strict, prioritizes precision)

## Configuration

Edit `config/ml_config.yaml` to tune:
- Similarity threshold
- Name/location weights
- TF-IDF/FastText weights
- N-gram ranges
- SVD components

## Troubleshooting

**FastText model not found error**:
- Ensure `cc.en.100.bin` exists in `models/fasttext/`
- Run `python scripts/download_fasttext.py`

**Import errors**:
- Install dependencies: `pip install -r requirements.txt`
- Ensure scikit-learn, fasttext, pyyaml are installed

**No ML matches found**:
- Check threshold in `config/ml_config.yaml` (try lowering from 0.95 to 0.85)
- Run `validate_ml_matches.py` to see top candidate scores
- Verify unmatched profiles have similar names/locations in the candidate pool
