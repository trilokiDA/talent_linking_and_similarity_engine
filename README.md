# ATLAS - Identity Resolution & Talent Intelligence Platform

ATLAS is an AI-powered identity resolution and talent intelligence platform designed to match, deduplicate, and enrich researcher profiles from multiple data sources.

## Overview

ATLAS ingests stakeholder profile data from multiple external sources (CoreSignal, RocketReach, Borealis) and uses deterministic matching and future ML-based techniques to create unified, enriched profiles. The platform enables accurate identity resolution across disparate data sources to power talent intelligence systems.

## Key Features

- **Multi-Source Data Ingestion**: Ingest profiles from CoreSignal, RocketReach, and Borealis
- **Data Normalization**: Standardize profiles into a unified schema
- **Deterministic Matching**: Match profiles across sources using LinkedIn usernames and contact numbers
- **ML-Based Matching**: TF-IDF + FastText hybrid embeddings for similarity-based matching
- **Profile Enrichment**: Combine data from multiple sources to create comprehensive profiles
- **Hierarchical Matching Priority**: RocketReach → CoreSignal priority-based matching
- **Configurable Thresholds**: Tune matching sensitivity via YAML configuration

## Project Structure

```
atlas/
├── data-lake/                          # Raw ingested data storage
│   ├── coresignal/                     # CoreSignal data source
│   │   └── 2026/08/21/
│   │       └── stakeholder.json
│   ├── rocketreach/                    # RocketReach data source
│   │   └── 2026/08/21/
│   │       └── stakeholder.json
│   └── borealis/                       # Borealis internal data
│       └── 2026/08/22/
│           └── stakeholder.json
│
├── processed-data/                     # Processed and matched data
│   ├── normalization/                  # Normalized profiles by source
│   │   ├── coresignal/
│   │   ├── rocketreach/
│   │   └── borealis/
│   └── matched/                        # Final matched and enriched profiles
│
├── processed-data/                     # Processed and matched data
│   ├── normalization/                  # Normalized profiles by source
│   │   ├── coresignal/
│   │   ├── rocketreach/
│   │   └── borealis/
│   └── matched/                        # Final matched and enriched profiles
│
├── models/                             # Trained ML models
│   ├── embeddings/                     # TF-IDF and SVD models
│   │   ├── name_tfidf_vectorizer.pkl
│   │   ├── name_svd_model.pkl
│   │   ├── location_tfidf_vectorizer.pkl
│   │   └── location_svd_model.pkl
│   ├── fasttext/                       # FastText word embeddings
│   │   └── cc.en.100.bin
│   └── README.md                       # Model documentation
│
├── config/                             # Configuration files
│   └── ml_config.yaml                  # ML matching parameters
│
├── scripts/                            # Utility scripts
│   ├── pipeline.py                     # ⭐ End-to-end pipeline (normalize → train → match)
│   ├── generate_dummy_data.py          # Generate synthetic profiles for PoC
│   ├── generate_borealis.py            # Generate Borealis test data
│   ├── normalize.py                    # Normalize profiles to unified schema
│   ├── deterministic_matching.py       # Deterministic matching engine
│   ├── ml_matching.py                  # ML embedding and similarity functions
│   ├── train_fasttext.py               # Train FastText model on data
│   ├── train_ml_models.py              # Train TF-IDF and SVD models
│   ├── hybrid_matching.py              # Hybrid deterministic + ML matching
│   ├── validate_ml_matches.py          # Validate and analyze matches
│   ├── download_fasttext.py            # Download pre-trained FastText (optional)
│   └── inspect_data.py                 # Data analysis and inspection tools
│
└── README.md                           # This file
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate sample data
python scripts/generate_dummy_data.py
python scripts/generate_borealis.py

# 3. Run the full pipeline (normalize → train → match) in one command ⭐
python scripts/pipeline.py

# 4. Validate results
python scripts/validate_ml_matches.py
```

> **Tip:** Use `python scripts/pipeline.py --help` to see all available flags (skip steps, deterministic-only mode, etc.).

## Installation

### Prerequisites

- Python 3.10+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd atlas
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### ⭐ Running the Full Pipeline (`pipeline.py`)

`pipeline.py` is the recommended way to run the entire ATLAS workflow in a single command.
It orchestrates all steps in order, prints per-step timing, and produces a final summary.

**Step order:**

| # | Step | Script |
|---|------|--------|
| 1 | Normalize raw data | `normalize.py` |
| 2 | Train FastText embeddings | `train_fasttext.py` |
| 3 | Train TF-IDF / SVD models | `train_ml_models.py` |
| 4 | Hybrid matching (deterministic + ML) | `hybrid_matching.py` |

**Commands:**

```bash
# Run everything end-to-end (recommended)
python scripts/pipeline.py

# Quick pass — normalization + deterministic matching only (no ML)
python scripts/pipeline.py --no-ml

# Resume after a partial run — skip already-completed steps
python scripts/pipeline.py --skip-normalize
python scripts/pipeline.py --skip-normalize --skip-train-fasttext --skip-train-ml

# See all available options
python scripts/pipeline.py --help
```

**Example output:**

```
======================================================================
  ATLAS PIPELINE -- START
======================================================================
  Project root : D:\...\talent_linking_and_similarity_engine
  Scripts dir  : D:\...\scripts

======================================================================
  PIPELINE PLAN
======================================================================
  [RUN]  Step 1 -- Normalize
  [RUN]  Step 2 -- Train FastText
  [RUN]  Step 3 -- Train ML models
  [RUN]  Step 4 -- Hybrid Matching

======================================================================
  PIPELINE SUMMARY
======================================================================
  [OK    ]  Normalize                        2.3s
  [OK    ]  Train FastText                  18.7s
  [OK    ]  Train ML Models                  1.1s
  [OK    ]  Hybrid Matching                  4.5s

  Total pipeline time: 26.6s
  All steps completed successfully!
  Matched profiles -> processed-data/matched/
```

---

### 1. Generate Sample Data

Generate synthetic stakeholder profiles for development and testing:

```bash
python scripts/generate_dummy_data.py
```

This creates:
- 100 CoreSignal profiles (employment history, education, academic metrics)
- 100 RocketReach profiles (contact info, social profiles, publications)

### 2. Generate Borealis Test Data

Create test Borealis profiles that overlap with normalized CoreSignal/RocketReach data:

```bash
python scripts/generate_borealis.py
```

Creates 10 Borealis profiles (4 from CoreSignal, 4 from RocketReach, 2 random).

### 3. Normalize Profiles

Convert all source profiles into a unified schema:

```bash
python scripts/normalize.py
```

**Unified Schema:**
```json
{
  "id": "CS_000001",
  "full_name": "Dr. James Smith",
  "current_employer": "Stanford University",
  "title": "Professor",
  "linkedin_username": "jamessmith123",
  "full_adress": "Palo Alto, CA, USA",
  "contact_number": "+1-650-555-1234"
}
```

### 4. Train ML Models (One-time Setup)

Train the machine learning models for similarity-based matching:

```bash
# Train FastText embeddings on Atlas data
python scripts/train_fasttext.py

# Train TF-IDF and SVD models
python scripts/train_ml_models.py
```

This creates:
- FastText model with 100-dimensional embeddings
- TF-IDF vectorizers for names and locations
- TruncatedSVD models for dimensionality reduction
- All models saved to `models/` directory

### 5. Run Hybrid Matching

Match Borealis profiles using both deterministic rules and ML similarity:

```bash
python scripts/hybrid_matching.py
```

**Two-Phase Pipeline:**

**Phase 1 - Deterministic Matching:**
1. Try matching Borealis → RocketReach (by phone, then LinkedIn username)
2. If no match, try Borealis → CoreSignal (by phone, then LinkedIn username)
3. Save matched profiles

**Phase 2 - ML Matching (for unmatched profiles):**
1. Load trained ML models and FastText embeddings
2. Compute hybrid name and location embeddings
3. Find best match above similarity threshold (configurable)
4. Save ML matches with confidence scores

**Output:**
- Enriched profiles with `match_info` metadata
- Match type: "deterministic" or "ml_embedding"
- Confidence scores for ML matches (name_similarity, location_similarity, final score)

### 6. Validate Matches

Analyze matching results and quality:

```bash
python scripts/validate_ml_matches.py
```

Provides statistics on:
- Match type distribution (deterministic vs ML)
- Source distribution (RocketReach vs CoreSignal)
- ML match confidence scores
- Detailed similarity breakdowns

### 7. Inspect Data

Analyze and explore the data lake:

```bash
python scripts/inspect_data.py
```

Provides statistics on:
- Profile counts by source
- Institution/employer distributions
- H-index and citation statistics
- Email verification rates
- Social profile coverage
- Research area distributions

## Data Sources

### CoreSignal
Professional employment and career history data.

**Key Fields:**
- `person_id`: Unique identifier (CS_XXXXXX)
- `full_name`, `first_name`, `last_name`: Identity
- `current_company`, `title`, `department`: Current position
- `education`: Educational background with degrees
- `experience`: Detailed work history
- `skills`, `research_interests`: Expertise areas
- `h_index`, `total_citations`, `total_publications`: Academic metrics
- `linkedin_url`: LinkedIn profile
- `data_quality_score`: Data confidence (0.0-1.0)

### RocketReach
Contact information and social profiles.

**Key Fields:**
- `id`: Unique identifier (RR_XXXXXX)
- `name`, `first_name`, `last_name`: Identity
- `current_employer`, `current_title`: Current position
- `emails[]`: Email addresses
- `phones[]`: Phone numbers
- `social_profiles`: LinkedIn, Twitter, Google Scholar, ORCID, ResearchGate
- `publications[]`: Recent publications with citation counts
- `research_areas[]`: Research focus areas
- `orcid_id`: ORCID identifier
- `confidence_score`: Data confidence (0.0-1.0)

### Borealis
Internal stakeholder management system data.

**Key Fields:**
- `b_id`: Unique identifier (BOR_XXX)
- `name`: Full name
- `company`: Current employer
- `position`: Job title
- `linkedin`: LinkedIn profile URL
- `location`: Geographic location
- `phone`: Contact number

## Matching Strategy

### Current: Deterministic Matching

**Priority Order:**
1. RocketReach (higher priority - better contact data)
2. CoreSignal (fallback - better employment history)

**Matching Keys:**
1. `contact_number` (phone number) - exact match
2. `linkedin_username` - case-insensitive exact match

**Process:**
```
For each Borealis profile:
  1. Extract phone and LinkedIn username
  2. Try phone match with RocketReach → return if found
  3. Try LinkedIn match with RocketReach → return if found
  4. Try phone match with CoreSignal → return if found
  5. Try LinkedIn match with CoreSignal → return if found
  6. No match found → profile remains unmatched
```

### Phase 2: ML-Based Embedding Matching (✅ Implemented)

For profiles without exact LinkedIn username or phone matches, ML similarity-based matching is used.

#### Name Matching

**Approach:** TF-IDF + FastText hybrid embeddings

**TF-IDF Component (70% weight):**
- Character-level n-grams for handling typos and variations
- Configuration: `TfidfVectorizer(analyzer="char", ngram_range=(2,5))`
- Pipeline: TF-IDF → Truncated SVD (100 components) → L2 Normalization
- Use case: Captures character patterns, spelling variations, partial matches

**FastText Component (30% weight):**
- Semantic word-level embeddings (100 dimensions)
- Custom trained FastText model on Atlas data
- Pipeline: FastText → L2 Normalization
- Use case: Semantic similarity, name variations (e.g., "Robert" vs "Bob")

**Final Name Embedding:**
```python
name_embedding = 0.7 * tfidf_embedding + 0.3 * fasttext_embedding
```

#### Location Matching

**Approach:** TF-IDF + FastText hybrid embeddings

**TF-IDF Component (30% weight):**
- Word-level n-grams for city/country matching
- Configuration: `TfidfVectorizer(analyzer="word", ngram_range=(1,2))`
- Pipeline: TF-IDF → Truncated SVD (50 components) → L2 Normalization
- Use case: Exact location name matches

**FastText Component (70% weight):**
- Semantic location embeddings (100 dimensions)
- Custom trained FastText model on Atlas data
- Pipeline: FastText → L2 Normalization
- Use case: Geographic proximity, regional variations (e.g., "SF" vs "San Francisco")

**Final Location Embedding:**
```python
location_embedding = 0.3 * tfidf_embedding + 0.7 * fasttext_embedding
```

#### Similarity Scoring

Compute combined similarity score:
```python
name_similarity = cosine_similarity(name_embedding_1, name_embedding_2)
location_similarity = cosine_similarity(location_embedding_1, location_embedding_2)

# Weighted combination
final_score = 0.6 * name_similarity + 0.4 * location_similarity

# Threshold for match (configurable, default: 0.95)
is_match = final_score > threshold
```

**Implementation Status:** ✅ Fully Implemented and Operational

#### Configuration

All ML parameters are configurable in `config/ml_config.yaml`:

```yaml
matching:
  similarity_threshold: 0.95  # Adjust for precision/recall tradeoff
  name_weight: 0.6
  location_weight: 0.4

embeddings:
  name:
    tfidf_weight: 0.7
    fasttext_weight: 0.3
    char_ngram_range: [2, 5]
    svd_components: 100
  
  location:
    tfidf_weight: 0.3
    fasttext_weight: 0.7
    word_ngram_range: [1, 2]
    svd_components: 50
```

## Performance & Results

### Current Match Rate
- **Test Dataset**: 11 Borealis profiles
- **Deterministic Matches**: 8/11 (72.7%)
- **ML Matches**: 0/11 at 0.95 threshold (configurable)
- **Total Match Rate**: 8/11 (72.7%)

### Matching Breakdown
- **RocketReach matches**: 4 profiles (priority source)
- **CoreSignal matches**: 4 profiles (fallback source)
- **Unmatched**: 3 profiles (no exact keys, below ML threshold)

### ML Model Statistics
- **Training corpus**: 201 profiles (100 CoreSignal + 101 RocketReach)
- **FastText vocabulary**: 209 unique words
- **Name embeddings**: 100 dimensions (TF-IDF-SVD + FastText)
- **Location embeddings**: 100 dimensions (TF-IDF-SVD + FastText)
- **Similarity threshold**: 0.95 (adjustable for higher recall)

### Tuning Recommendations
To increase ML match rate, lower the threshold in `config/ml_config.yaml`:
- **0.95**: Very strict (current) - prioritizes precision
- **0.90**: Strict - balanced precision/recall
- **0.85**: Moderate - higher recall, some false positives
- **0.80**: Permissive - maximum recall, check quality

## Data Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION                             │
│  CoreSignal API → data-lake/coresignal/{date}/stakeholder.json  │
│  RocketReach API → data-lake/rocketreach/{date}/stakeholder.json│
│  Borealis System → data-lake/borealis/{date}/stakeholder.json   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA NORMALIZATION                           │
│  Standardize to unified schema with common fields               │
│  Output: processed-data/normalization/{source}/{id}.json        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ML MODEL TRAINING                            │
│  Train TF-IDF, SVD, and FastText models on normalized data      │
│  Output: models/embeddings/*.pkl, models/fasttext/*.bin         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  IDENTITY RESOLUTION                            │
│  Phase 1: Deterministic matching (LinkedIn, phone)              │
│    - Priority: RocketReach > CoreSignal                         │
│    - Exact match on linkedin_username or contact_number         │
│  Phase 2: ML Similarity Matching (for unmatched profiles)       │
│    - Hybrid TF-IDF + FastText embeddings                        │
│    - Name similarity (60%) + Location similarity (40%)          │
│    - Configurable threshold (default: 0.95)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROFILE ENRICHMENT                            │
│  Merge data from matched profiles                               │
│  Fill missing fields from secondary sources                     │
│  Add match metadata (source, type, confidence)                  │
│  Output: processed-data/matched/{id}.json                       │
└─────────────────────────────────────────────────────────────────┘
```

## Matched Profile Schema

```json
{
  "id": "BOR_100",
  "full_name": "Dr. James Smith",
  "current_employer": "Stanford University",
  "title": "Professor",
  "linkedin_username": "jamessmith123",
  "full_adress": "Palo Alto, CA, USA",
  "contact_number": "+1-650-555-1234",
  
  "match_info": {
    "matched": true,
    "match_type": "deterministic",
    "source": "rocketreach",
    "matched_id": "RR_000001"
  }
}
```

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test thoroughly
3. Commit: `git commit -m "feat: your feature description"`
4. Push: `git push origin feature/your-feature`
5. Create Pull Request

## License

See [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please open a GitHub issue or contact the development team.

---

**Status**: Active Development | **Last Updated**: 2026-08-24
