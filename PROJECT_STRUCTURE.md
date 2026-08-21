# ATLAS Project Structure

## Overview
ATLAS is an AI-powered identity resolution and talent intelligence platform for researcher profiles.

## Current Directory Structure

```
atlas/
├── data-lake/                          # Raw ingested data storage
│   ├── coresignal/                     # CoreSignal data source
│   │   └── 2026/08/21/
│   │       └── stakeholder.json        # 100 profiles (165KB)
│   ├── rocketreach/                    # RocketReach data source
│   │   └── 2026/08/21/
│   │       └── stakeholder.json        # 100 profiles (329KB)
│   └── README.md                       # Data lake documentation
│
├── scripts/                            # Utility scripts
│   ├── generate_dummy_data.py          # Generate synthetic profiles
│   └── inspect_data.py                 # Analyze and inspect data
│
└── PROJECT_STRUCTURE.md                # This file
```

## Planned Architecture

```
atlas/
├── data-lake/                          # Raw data storage (current)
│   ├── coresignal/
│   ├── rocketreach/
│   └── borealis/                       # Future: Internal system data
│
├── src/                                # Source code
│   ├── ingestion/                      # Data ingestion pipelines
│   │   ├── coresignal_ingestion.py
│   │   ├── rocketreach_ingestion.py
│   │   └── borealis_ingestion.py
│   │
│   ├── validation/                     # Data quality and validation
│   │   ├── schema_validator.py
│   │   └── data_quality_checks.py
│   │
│   ├── resolution/                     # Identity resolution engine
│   │   ├── entity_matcher.py          # Match profiles across sources
│   │   ├── deduplication.py           # Remove duplicates
│   │   └── confidence_scoring.py      # Score match confidence
│   │
│   ├── enrichment/                     # Data enrichment
│   │   ├── profile_enricher.py        # Enhance profiles
│   │   ├── publication_enricher.py    # Add publication data
│   │   └── affiliation_tracker.py     # Track affiliations over time
│   │
│   ├── api/                           # REST API layer
│   │   ├── app.py                     # FastAPI/Flask application
│   │   ├── routes/
│   │   └── models/
│   │
│   ├── ml/                            # ML models
│   │   ├── entity_resolution_model.py
│   │   ├── deduplication_model.py
│   │   └── profile_similarity.py
│   │
│   └── utils/                         # Shared utilities
│       ├── config.py
│       ├── logger.py
│       └── db_connector.py
│
├── database/                          # Database schemas and migrations
│   ├── migrations/
│   └── schemas/
│       ├── unified_profile.sql
│       └── source_mapping.sql
│
├── config/                            # Configuration files
│   ├── config.yaml
│   ├── data_sources.yaml
│   └── resolution_rules.yaml
│
├── tests/                             # Test suite
│   ├── unit/
│   ├── integration/
│   └── test_data/
│
├── notebooks/                         # Jupyter notebooks for analysis
│   ├── data_exploration.ipynb
│   └── ml_model_development.ipynb
│
├── docs/                              # Documentation
│   ├── architecture.md
│   ├── api_docs.md
│   └── deployment.md
│
├── scripts/                           # Utility scripts (current)
│   ├── generate_dummy_data.py
│   └── inspect_data.py
│
├── .env.example                       # Environment variables template
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                 # Docker setup
└── README.md                          # Project README
```

## Data Flow

1. **Ingestion Layer**
   - Pull data from CoreSignal, RocketReach, Borealis APIs
   - Store raw data in data-lake with timestamp structure
   - Validate against schemas

2. **Validation Layer**
   - Schema validation
   - Data quality checks
   - Anomaly detection

3. **Resolution Layer**
   - Match profiles across sources using ML
   - Deduplicate within sources
   - Calculate confidence scores
   - Create unified profiles

4. **Enrichment Layer**
   - Add computed fields
   - Enhance publication data
   - Track affiliation changes
   - Calculate derived metrics

5. **Storage Layer**
   - Unified profile database
   - Source mapping tables
   - Historical tracking

6. **API Layer**
   - RESTful API for SMS integration
   - Search and query endpoints
   - Real-time updates

## Current Status

✅ **Completed:**
- Data lake folder structure (coresignal, rocketreach)
- Synthetic data generation (100 profiles each)
- Data inspection utilities

🚧 **Next Steps:**
1. Database schema design
2. Data ingestion pipeline
3. Identity resolution engine
4. API development
5. SMS integration

## Technology Stack (Proposed)

- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **Database**: PostgreSQL + TimescaleDB (for time-series)
- **Data Lake**: File-based (JSON) → Future: S3/Azure Blob
- **ML**: scikit-learn, spaCy, sentence-transformers
- **API**: REST (FastAPI) + GraphQL (optional)
- **Orchestration**: Apache Airflow (for ETL pipelines)
- **Monitoring**: Prometheus + Grafana
- **Deployment**: Docker + Kubernetes

## Data Sources

### CoreSignal
- Employment history
- Education background
- Career trajectory
- Skills and expertise
- 100 profiles generated

### RocketReach
- Contact information (email, phone)
- Social profiles (LinkedIn, Twitter, Scholar, ORCID)
- Publication records with citations
- Research areas
- 100 profiles generated

### Borealis (Future)
- Internal stakeholder management data
- Engagement history
- Custom attributes

## Key Features

1. **Identity Resolution**: Match researchers across multiple data sources
2. **Profile Enrichment**: Combine data to create comprehensive profiles
3. **Real-time Updates**: Keep SMS data current
4. **Publication Tracking**: Monitor research output
5. **Affiliation Changes**: Track career moves
6. **Confidence Scoring**: Indicate data quality
7. **API Access**: RESTful API for SMS integration
