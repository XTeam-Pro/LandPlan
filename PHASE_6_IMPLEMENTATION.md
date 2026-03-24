# Phase 6: ETL Pipeline & Importers - Implementation Complete ✅

## Overview
Phase 6 implements a full ETL (Extract, Transform, Load) pipeline for importing land data from multiple sources. The implementation includes:
- Abstract importer base class for shared logic
- 3 concrete mock importers (private listings, bankruptcy auctions, government sales)
- Import job tracking with statistics
- Deduplication via external_id + source_id
- Admin API for scheduling and monitoring imports
- Comprehensive integration tests

## Files Created

### 1. Core Infrastructure
```
app/bounded_contexts/integrations/
├── __init__.py                              # Module initialization
├── base_importer.py                         # Abstract base class with import pipeline
├── service.py                               # ImportService for orchestration
├── routes.py                                # Admin API endpoints
└── importers/
    ├── __init__.py
    ├── private_listings.py                  # Mock private listings importer (50 items)
    ├── bankruptcy_auctions.py               # Mock bankruptcy auctions importer (20 items)
    └── government_sales.py                  # Mock government sales importer (30 items)
```

### 2. Schemas & DTOs
```
app/schemas/importer.py                      # Pydantic models for request/response
```

### 3. Database Migrations
```
app/db/migrations/versions/003_seed_sources_and_regions.py
                                             # Seeds regions, cities, and source configs
```

### 4. Tests
```
tests/integration/test_import_endpoints.py   # 15+ integration test cases
```

### 5. Updated Files
```
app/main.py                                  # Registered integrations router
```

## Key Features

### BaseImporter Class
Abstract base class that implements the full ETL pipeline:
- **fetch_raw_data()**: Abstract method for data source
- **normalize()**: Abstract method to convert to LandCreate schema
- **run()**: Complete pipeline implementation
  - Creates ImportJob with status tracking
  - Fetches and processes items
  - Deduplicates by external_id + source_id
  - Updates ImportJob statistics
  - Handles errors gracefully

### Three Mock Importers

#### PrivateListingsImporter
- **Type**: `private`
- **Volume**: 50 records
- **Distribution**: 3 regions (Moscow, Saint Petersburg, Novosibirsk), 6 cities
- **Deal Types**: purchase, rent, lease
- **Categories**: residential, commercial, agricultural
- **Features**: Basic info, mostly user-uploaded

#### BankruptcyAuctionsImporter
- **Type**: `bankruptcy`
- **Volume**: 20 records
- **Deal Type**: auction (distressed sales)
- **Categories**: commercial, industrial
- **Pricing**: Lower (200K-5M RUB vs 500K-10M for private)
- **Features**: Often well-defined (official records)

#### GovernmentSalesImporter
- **Type**: `government`
- **Volume**: 30 records
- **Deal Types**: purchase, lease
- **Categories**: agricultural, residential
- **Pricing**: Mid-range (800K-8M RUB)
- **Features**: boundaries_defined=True, has_roads=True

### ImportService
Orchestrates imports with methods:
- `get_sources()` - List all sources
- `get_source(id)` - Get specific source
- `create_source()` - Create new source config
- `run_import(source_id)` - Trigger import immediately
- `get_import_jobs()` - List all import jobs (optionally filtered)
- `get_import_job(id)` - Get specific job details
- `seed_default_sources()` - Initialize 3 default sources

### Admin API Endpoints
All endpoints under `/api/v1/admin/imports` prefix:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/sources` | List all data sources |
| POST | `/sources` | Create new source |
| GET | `/sources/{id}` | Get source details |
| POST | `/sources/{id}/run` | Trigger import job |
| GET | `/import-jobs` | List all jobs (newest first) |
| GET | `/import-jobs/{id}` | Get job details with stats |

### Deduplication Strategy
```python
# Check for existing land
existing = db.query(Land).filter(
    Land.source_id == source.id,
    Land.external_id == item.external_id,
).first()

if existing:
    job.duplicates_found += 1
else:
    # Insert new land
    job.imported_items += 1
```

## Database Schema Integration

### Existing Models Used
- `app/models/land.py:Land` - Target table for imported lands
- `app/models/land.py:LandFeature` - Associated features
- `app/models/reference.py:Source` - Source configuration
- `app/models/recommendation.py:ImportJob` - Job tracking
- `app/models/reference.py:Region` - Geographic region reference
- `app/models/reference.py:City` - City reference data

### New Migration (003)
Seeds initial data:
- **3 Regions**: Moscow, Saint Petersburg, Novosibirsk
- **6 Cities**: 2 per region
- **3 Sources**: private, bankruptcy, government

## Import Job Statistics

### ImportJob Model Fields
- `id` - Unique identifier
- `source_id` - Foreign key to source
- `status` - pending, in_progress, completed, failed
- `total_items` - Total raw items fetched
- `imported_items` - Successfully created lands
- `duplicates_found` - Skipped due to existing external_id + source_id
- `errors` - Items that failed to process
- `error_log` - Text log of errors
- `started_at`, `completed_at` - Timing

## Integration Tests (test_import_endpoints.py)

### Test Coverage
```python
class TestImportEndpoints:
    ✅ test_list_sources()                       # List all sources
    ✅ test_get_source()                         # Get specific source
    ✅ test_get_source_not_found()               # 404 handling
    ✅ test_create_source()                      # Create new source
    ✅ test_trigger_import_private_listings()    # Run private import
    ✅ test_trigger_import_bankruptcy_auctions() # Run bankruptcy import
    ✅ test_trigger_import_government_sales()    # Run government import
    ✅ test_deduplication_same_source()          # Run same import twice
    ✅ test_list_import_jobs()                   # List all jobs
    ✅ test_list_import_jobs_filtered_by_source()# Filter by source
    ✅ test_get_import_job()                     # Get job details
    ✅ test_get_import_job_not_found()           # 404 handling
    ✅ test_imported_lands_are_queryable()       # Verify lands API integration
    ✅ test_imported_lands_have_correct_source() # Check source tracking
    ✅ test_all_three_imports_run_independently()# Total: 100 items imported
```

### Test Statistics
- **Total lands imported across all importers**: 100 (50 + 20 + 30)
- **Deduplication verification**: Run same import twice → 0 new imports, 50+ duplicates
- **API integration**: Imported lands appear in `/api/v1/lands`
- **Source tracking**: Each land has correct source_id

## API Response Examples

### POST /api/v1/admin/imports/sources/{id}/run
```json
{
  "id": 1,
  "source_id": 1,
  "status": "completed",
  "total_items": 50,
  "imported_items": 50,
  "duplicates_found": 0,
  "errors": 0,
  "started_at": "2026-03-17T20:00:00Z"
}
```

### GET /api/v1/admin/imports/import-jobs
```json
[
  {
    "id": 1,
    "source_id": 1,
    "status": "completed",
    "total_items": 50,
    "imported_items": 50,
    "duplicates_found": 0,
    "errors": 0,
    "error_log": null,
    "started_at": "2026-03-17T20:00:00Z",
    "completed_at": "2026-03-17T20:00:05Z",
    "created_at": "2026-03-17T20:00:00Z"
  }
]
```

## Running the Implementation

### With Docker Compose
```bash
cd /root/LandPlan/LandPlan
docker-compose up                          # Start all services
docker-compose exec backend pytest tests/integration/test_import_endpoints.py -v
```

### Manual Setup
```bash
cd /root/LandPlan/LandPlan/backend
python3 -m venv venv
source venv/bin/activate
pip install poetry
poetry install
alembic upgrade head                       # Run migrations (includes seed)
pytest tests/integration/test_import_endpoints.py -v
```

### Using FastAPI Swagger UI
1. Start backend: `uvicorn app.main:app --reload`
2. Visit http://localhost:8000/docs
3. Try import endpoints under "Admin - Imports" section:
   - POST `/api/v1/admin/imports/sources/{source_id}/run`
   - GET `/api/v1/admin/imports/import-jobs`
   - etc.

## Verification Steps

### 1. Trigger all three imports
```bash
# Get sources
curl http://localhost:8000/api/v1/admin/imports/sources

# Run private listings import
curl -X POST http://localhost:8000/api/v1/admin/imports/sources/1/run

# Run bankruptcy auctions import
curl -X POST http://localhost:8000/api/v1/admin/imports/sources/2/run

# Run government sales import
curl -X POST http://localhost:8000/api/v1/admin/imports/sources/3/run
```

### 2. Verify imported data in Lands API
```bash
# Should return 100 total lands (50+20+30)
curl http://localhost:8000/api/v1/lands
```

### 3. Test deduplication
```bash
# Run private import again
curl -X POST http://localhost:8000/api/v1/admin/imports/sources/1/run

# Should show: duplicates_found=50, imported_items=0
```

### 4. Verify job tracking
```bash
# Get all import jobs
curl http://localhost:8000/api/v1/admin/imports/import-jobs

# Should show multiple jobs with correct statistics
```

## Architecture Notes

### Design Decisions

1. **Mock Data with Geographic Realism**
   - Uses real Russian city coordinates
   - Generates diverse deal types and categories
   - Varied pricing based on source type

2. **Flexible Source Configuration**
   - `Source.type` determines which importer to use
   - `Source.config` stores metadata (description, update frequency)
   - Can add new importers without schema changes

3. **Robust Error Handling**
   - Failed items increment `errors` counter
   - Error log captures all failures
   - Job status is still marked completed (partial success OK)
   - Import failure doesn't corrupt existing data

4. **Deduplication by Composite Key**
   - Uses `(source_id, external_id)` as natural key
   - Prevents duplicates within a source
   - Allows same external_id from different sources

5. **Integration with Existing Services**
   - Uses `LandsService.create_land()` for insertion
   - Respects all Land validation and LandFeature creation
   - Generates valid geographic coordinates

## Next Steps (Phase 7+)

1. **Real Data Integrations**
   - Replace mock importers with actual API clients
   - Add real source authentication
   - Implement incremental updates

2. **Scheduled Imports**
   - Integrate APScheduler for background jobs
   - Add cron-style scheduling per source
   - Email notifications on import completion

3. **Advanced Features**
   - Duplicate detection across sources (geo-spatial)
   - Data quality scoring
   - Automatic price updates
   - Source-specific validation rules

4. **Admin Dashboard**
   - Visualize import history and trends
   - Manage source configurations
   - Monitor import health and errors

## Files Changed Summary

### New Files (12)
- ✅ `app/bounded_contexts/integrations/__init__.py`
- ✅ `app/bounded_contexts/integrations/base_importer.py` (82 lines)
- ✅ `app/bounded_contexts/integrations/service.py` (122 lines)
- ✅ `app/bounded_contexts/integrations/routes.py` (106 lines)
- ✅ `app/bounded_contexts/integrations/importers/__init__.py`
- ✅ `app/bounded_contexts/integrations/importers/private_listings.py` (76 lines)
- ✅ `app/bounded_contexts/integrations/importers/bankruptcy_auctions.py` (73 lines)
- ✅ `app/bounded_contexts/integrations/importers/government_sales.py` (73 lines)
- ✅ `app/schemas/importer.py` (60 lines)
- ✅ `app/db/migrations/versions/003_seed_sources_and_regions.py` (115 lines)
- ✅ `tests/integration/test_import_endpoints.py` (400+ lines)
- ✅ `PHASE_6_IMPLEMENTATION.md` (this file)

### Modified Files (1)
- ✅ `app/main.py` (added integrations router import and registration)

## Code Quality

- ✅ Follows existing code patterns and conventions
- ✅ Proper error handling and logging
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ No security vulnerabilities
- ✅ All tests follow existing patterns
- ✅ Compatible with SQLAlchemy ORM
- ✅ Works with existing database schema

## Statistics

- **Total LOC added**: ~900 lines
- **Test coverage**: 15 test cases covering all endpoints and scenarios
- **API endpoints**: 6 new admin endpoints
- **Importers**: 3 concrete implementations
- **Data generated**: 100 mock land records across 3 sources
