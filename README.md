# ATLAS - Identity Resolution & Talent Intelligence Platform

ATLAS is an AI-powered identity resolution and talent intelligence platform designed to match, deduplicate, and enrich researcher profiles from multiple data sources.

## Overview

ATLAS ingests stakeholder profile data from multiple external sources (CoreSignal, RocketReach, Borealis) and uses deterministic matching and future ML-based techniques to create unified, enriched profiles. The platform enables accurate identity resolution across disparate data sources to power talent intelligence systems.

## Key Features

- **Multi-Source Data Ingestion**: Ingest profiles from CoreSignal, RocketReach, and Borealis
- **Data Normalization**: Standardize profiles into a unified schema
- **Deterministic Matching**: Match profiles across sources using LinkedIn usernames and contact numbers
- **Profile Enrichment**: Combine data from multiple sources to create comprehensive profiles
- **Hierarchical Matching Priority**: RocketReach → CoreSignal priority-based matching
- **Future ML Matching**: Planned TF-IDF + FastText embedding-based matching for name and location similarity

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
├── scripts/                            # Utility scripts
│   ├── generate_dummy_data.py          # Generate synthetic profiles for PoC
│   ├── generate_borealis.py            # Generate Borealis test data
│   ├── normalize.py                    # Normalize profiles to unified schema
│   ├── deterministic_matching.py       # Deterministic matching engine
│   └── inspect_data.py                 # Data analysis and inspection tools
│
└── README.md                           # This file
```

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

### 4. Run Deterministic Matching

Match Borealis profiles against RocketReach and CoreSignal using deterministic rules:

```bash
python scripts/deterministic_matching.py
```

**Matching Logic:**
1. Try matching Borealis → RocketReach (by phone, then LinkedIn username)
2. If no match, try Borealis → CoreSignal (by phone, then LinkedIn username)
3. Enrich missing Borealis fields from matched profile
4. Save to `processed-data/matched/`

**Output:**
- Enriched profiles with `match_info` metadata
- Match type, source, and matched ID tracking

### 5. Inspect Data

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

### Future: ML-Based Embedding Matching

For profiles without exact LinkedIn username or phone matches, use similarity-based matching with embeddings.

#### Name Matching

**Approach:** TF-IDF + FastText hybrid embeddings

**TF-IDF Component (70% weight):**
- Character-level n-grams for handling typos and variations
- Configuration: `TfidfVectorizer(analyzer="char", ngram_range=(2,5))`
- Pipeline: TF-IDF → Truncated SVD → L2 Normalization
- Use case: Captures character patterns, spelling variations, partial matches

**FastText Component (30% weight):**
- Semantic word-level embeddings
- Pre-trained FastText model
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
- Pipeline: TF-IDF → Truncated SVD → L2 Normalization
- Use case: Exact location name matches

**FastText Component (70% weight):**
- Semantic location embeddings
- Pre-trained FastText model
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

# Threshold for match (e.g., > 0.85)
is_match = final_score > 0.95
```

**Implementation Status:** Planned (not yet implemented)

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
│                  IDENTITY RESOLUTION                            │
│  Phase 1: Deterministic matching (LinkedIn, phone)              │
│  Phase 2: ML embedding matching (name + location) [FUTURE]      │
│  Priority: RocketReach > CoreSignal                             │
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

## Development Roadmap

### Phase 1: Core Matching (Current)
- [x] Data lake setup with timestamped ingestion
- [x] Synthetic data generation for testing
- [x] Data normalization pipeline
- [x] Deterministic matching (LinkedIn + phone)
- [x] Profile enrichment and merge
- [x] Data inspection and analysis tools

### Phase 2: ML Matching (Planned)
- [ ] Name embedding pipeline (TF-IDF + FastText)
- [ ] Location embedding pipeline (TF-IDF + FastText)
- [ ] Similarity scoring and threshold tuning
- [ ] Confidence scoring for ML matches
- [ ] Match validation and quality metrics

## Technology Stack

- **Language**: Python 3.10+
- **Data Processing**: JSON file-based (transitioning to database)
- **ML Libraries** (Planned):
  - scikit-learn (TF-IDF, SVD, similarity metrics)
  - fasttext (word embeddings)
  - numpy (numerical operations)
- **Future Stack**:
  - FastAPI (REST API)
  - PostgreSQL (database)
  - Apache Airflow (orchestration)
  - Docker (containerization)

## Testing

### Sample Data Statistics

**CoreSignal:**
- 100 profiles generated
- File size: ~165KB
- Average profile completeness: 85%

**RocketReach:**
- 100 profiles generated
- File size: ~329KB
- Average confidence score: 0.87

**Borealis:**
- 10 test profiles
- 8 overlap with CoreSignal/RocketReach
- 2 completely new profiles

### Match Coverage

Run deterministic matching to see current coverage:
```bash
python scripts/deterministic_matching.py
```

Expected output:
```
Building RocketReach indexes...
Building CoreSignal indexes...
Matching Borealis profiles...
Matched BOR_100 with rocketreach (RR_000001)
Matched BOR_101 with coresignal (CS_000001)
...
Deterministic matching complete. Matched 8 profiles.
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
