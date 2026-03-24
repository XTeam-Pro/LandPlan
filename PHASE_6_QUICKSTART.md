# Phase 6 ETL Pipeline - Quick Start Guide

## 30-Second Overview

Phase 6 adds a complete ETL (Extract, Transform, Load) pipeline to LandPlan:
- **Admin API** to trigger data imports from 3 sources
- **3 Mock importers** that generate 100 realistic land records
- **Deduplication** to prevent duplicate imports
- **Job tracking** with statistics and error logs
- **15 integration tests** covering all scenarios

## Quick Start

### Option 1: Docker Compose (Easiest)
```bash
cd /root/LandPlan/LandPlan

# Start all services
docker-compose up

# In another terminal, run tests
docker-compose exec backend pytest tests/integration/test_import_endpoints.py -v

# Check the API
curl http://localhost:8000/api/v1/admin/imports/sources
```

### Option 2: Manual Setup
```bash
cd /root/LandPlan/LandPlan/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
# Or: pip install poetry && poetry install

# Run migrations (creates database schema)
alembic upgrade head

# Run tests
pytest tests/integration/test_import_endpoints.py -v

# Start backend
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs for interactive API docs
```

## Try the API

### 1. Get All Sources
```bash
curl http://localhost:8000/api/v1/admin/imports/sources
```
Should return 3 sources: private, bankruptcy, government

### 2. Trigger Private Listings Import (50 items)
```bash
curl -X POST http://localhost:8000/api/v1/admin/imports/sources/1/run
```
Response:
```json
{
  "id": 1,
  "status": "completed",
  "total_items": 50,
  "imported_items": 50,
  "duplicates_found": 0
}
```

### 3. Trigger Bankruptcy Auctions Import (20 items)
```bash
curl -X POST http://localhost:8000/api/v1/admin/imports/sources/2/run
```

### 4. Trigger Government Sales Import (30 items)
```bash
curl -X POST http://localhost:8000/api/v1/admin/imports/sources/3/run
```

### 5. View All Import Jobs
```bash
curl http://localhost:8000/api/v1/admin/imports/import-jobs
```

### 6. Check Imported Lands in Main API
```bash
curl http://localhost:8000/api/v1/lands
```
Should show 100 lands total (50 + 20 + 30)

### 7. Test Deduplication
```bash
# Run the same import again
curl -X POST http://localhost:8000/api/v1/admin/imports/sources/1/run

# Check the job - should show:
# "imported_items": 0
# "duplicates_found": 50
```

## Using Swagger UI

1. Start the backend: `uvicorn app.main:app --reload`
2. Open http://localhost:8000/docs
3. Scroll to "Admin - Imports" section
4. Try the endpoints interactively:
   - Try `/api/v1/admin/imports/sources` GET
   - Try `/api/v1/admin/imports/sources/1/run` POST
   - Try `/api/v1/admin/imports/import-jobs` GET

## File Structure

```
backend/app/
├── bounded_contexts/
│   └── integrations/          ← NEW
│       ├── __init__.py
│       ├── base_importer.py   ← Abstract base class
│       ├── service.py         ← ImportService
│       ├── routes.py          ← Admin API endpoints
│       └── importers/         ← Concrete implementations
│           ├── private_listings.py (50 items)
│           ├── bankruptcy_auctions.py (20 items)
│           └── government_sales.py (30 items)
├── schemas/
│   └── importer.py            ← NEW (Pydantic models)
└── main.py                    ← UPDATED (added router)

backend/app/db/migrations/versions/
└── 003_seed_sources_and_regions.py  ← NEW (migration)

backend/tests/integration/
└── test_import_endpoints.py   ← NEW (15 test cases)
```

## Key Features

### 1. Abstract Importer Base Class
All importers inherit from `BaseImporter` and implement:
- `fetch_raw_data()` - Get raw data from source
- `normalize()` - Convert to LandCreate schema

The base class handles:
- Job creation and tracking
- Error handling
- Deduplication
- Statistics collection

### 2. Three Mock Importers

| Importer | Items | Deal Types | Categories | Price Range |
|----------|-------|-----------|-----------|------------|
| Private | 50 | purchase, rent, lease | residential, commercial, agricultural | 500K-10M RUB |
| Bankruptcy | 20 | auction | commercial, industrial | 200K-5M RUB |
| Government | 30 | purchase, lease | agricultural, residential | 800K-8M RUB |

### 3. ImportService Orchestration
Routes requests to the correct importer based on source type

### 4. ImportJob Tracking
Every import creates a job record with:
- `status` - pending, in_progress, completed, failed
- `imported_items` - New records created
- `duplicates_found` - Skipped due to external_id match
- `errors` - Items that failed
- `error_log` - Text log of failures

### 5. Deduplication
Checks by composite key: `(source_id, external_id)`
- Prevents duplicate imports of same data
- Allows same external_id from different sources

## Common Tasks

### Trigger All Imports
```bash
for source_id in 1 2 3; do
  curl -X POST http://localhost:8000/api/v1/admin/imports/sources/$source_id/run
done
```

### Filter Import Jobs by Source
```bash
curl "http://localhost:8000/api/v1/admin/imports/import-jobs?source_id=1"
```

### Create Custom Source
```bash
curl -X POST http://localhost:8000/api/v1/admin/imports/sources \
  -H "Content-Type: application/json" \
  -d '{
    "type": "custom",
    "name": "My Custom Source",
    "config": {"api_key": "xxx"},
    "is_active": true
  }'
```

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you've installed dependencies
pip install -e .
# Or
poetry install
```

### "Database connection" errors
```bash
# Make sure migrations are applied
alembic upgrade head
```

### Import job fails
```bash
# Check the import job details for error_log
curl http://localhost:8000/api/v1/admin/imports/import-jobs/1
```

### No lands appear in API
```bash
# Make sure you've triggered an import
curl -X POST http://localhost:8000/api/v1/admin/imports/sources/1/run

# Then query lands
curl http://localhost:8000/api/v1/lands
```

## Testing

### Run All Import Tests
```bash
pytest tests/integration/test_import_endpoints.py -v
```

### Run Specific Test
```bash
pytest tests/integration/test_import_endpoints.py::TestImportEndpoints::test_deduplication_same_source -v
```

### Run with Coverage
```bash
pytest tests/integration/test_import_endpoints.py --cov=app.bounded_contexts.integrations
```

## What's New in This Release

### Before Phase 6
- No way to import data
- No tracking of import jobs
- Manual data insertion only

### After Phase 6
- ✅ 3 data source importers
- ✅ Job tracking with statistics
- ✅ Automatic deduplication
- ✅ Error logging and handling
- ✅ Admin API for import management
- ✅ Comprehensive test coverage

## Next Steps

1. **Deploy** the backend with Phase 6
2. **Run imports** to populate the database
3. **Monitor jobs** using the API
4. **Plan Phase 7** for scheduled imports (APScheduler)
5. **Implement Phase 8** with real data integrations

## API Documentation

Full interactive documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Questions?

Check these files for more details:
- `PHASE_6_IMPLEMENTATION.md` - Comprehensive guide
- `PHASE_6_CHECKLIST.md` - Implementation checklist
- `tests/integration/test_import_endpoints.py` - Test examples
- `CLAUDE.md` - Architecture guidelines

---

**Status**: ✅ Ready to use
**Test Coverage**: 15 test cases
**Data Volume**: 100 mock records
**Endpoints**: 6 admin API endpoints
