# ATLAS Data Lake

This directory contains ingested stakeholder profile data from various external sources.

## Directory Structure

```
data-lake/
├── coresignal/
│   └── {year}/
│       └── {month}/
│           └── {day}/
│               └── stakeholder.json
└── rocketreach/
    └── {year}/
        └── {month}/
            └── {day}/
                └── stakeholder.json
```

## Data Sources

### CoreSignal
Professional employment and career history data.

**Key Fields:**
- `person_id`: Unique identifier (format: CS_XXXXXX)
- `full_name`, `first_name`, `last_name`: Identity
- `current_company`, `title`, `department`: Current position
- `education`: Educational background
- `experience`: Work history
- `skills`, `research_interests`: Areas of expertise
- `h_index`, `total_citations`, `total_publications`: Academic metrics
- `data_quality_score`: Data confidence (0.0-1.0)

### RocketReach
Contact information and social profiles.

**Key Fields:**
- `id`: Unique identifier (format: RR_XXXXXX)
- `name`, `first_name`, `last_name`: Identity
- `current_employer`, `current_title`: Current position
- `emails[]`: Email addresses
- `phones[]`: Phone numbers
- `social_profiles`: LinkedIn, Twitter, Google Scholar, ORCID, ResearchGate
- `publications[]`: Recent publications with citations
- `research_areas[]`: Research focus areas
- `confidence_score`: Data confidence (0.0-1.0)

## Data Generation

For PoC purposes, synthetic data is generated using:
```bash
python scripts/generate_dummy_data.py
```

This creates 100 realistic profiles per source for the current date.

## Current Dataset

- **Date**: 2026-08-21
- **CoreSignal profiles**: 100 (165KB)
- **RocketReach profiles**: 100 (329KB)
- **Total profiles**: 200

## Data Quality

All synthetic profiles include:
- Realistic academic institutions and titles
- Publication records with citation counts
- Professional experience and education history
- Research areas and skills
- Contact information (emails, phones, social profiles)
- Academic metrics (h-index, citations, publication counts)

## Next Steps

1. **Data Ingestion Pipeline**: Build ETL to process these JSON files
2. **Data Validation**: Schema validation and quality checks
3. **Identity Resolution**: Merge profiles across sources
4. **Data Enrichment**: Add additional computed fields
5. **Storage**: Load into central database/data warehouse
