# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LandPlan** is a platform for land parcel selection and orchestration of their development through service contractors. The core value proposition is transforming the user journey from "find land + separately find contractors" into "find land → understand next steps → select contractors → execute development plan."

The product is in **active development**. The specification is documented in `README.md` (in Russian). Core infrastructure (authentication, database models, API structure) is implemented; major work is on the Recommendations Engine and frontend features.

## Core Architecture Vision

### Key Principle: Modular Monolith with Bounded Contexts

The system should be built as a **modular monolith with clear bounded contexts**, with an option to extract services later without rewriting domain logic. This approach balances speed of development against premature complexity.

### Bounded Contexts (from spec)

1. **Identity & Access** — User authentication, roles, permissions
2. **Lands** — Land parcel data, sources, features, filtering
3. **Catalog / Services** — Service categories and service definitions
4. **Companies** — Contractor organizations and their profiles
5. **Recommendations / Land Plan** — The core engine that connects land → recommended services → available contractors
6. **Applications / Requests** — User requests to contractors
7. **Reviews & Ratings** — User feedback on contractors
8. **Notifications** — System notifications
9. **Admin & Moderation** — Administrative functions and company verification
10. **Integrations / Data Import** — ETL pipelines for external data sources

### Critical Business Logic: Recommendations Engine

This is **the core differentiator**. Without it, the system is just another classifieds site + contractor directory. The recommendations engine should:

- Analyze land characteristics (water, electricity, boundaries defined, etc.)
- Map characteristics to required/recommended services
- Rank and suggest relevant contractors by region
- Generate a development plan (Land Plan) with sequential steps

**MVP approach**: Use rule-based decision logic (not heavy AI). Example rules:
- If `has_water = false` → recommend water analysis, drilling, water supply services
- If `boundaries_defined = false` → recommend cadastral services
- If `deal_type = purchase` → recommend lawyer, appraisal
- If planning construction → recommend geology, design, construction services

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript and Vite
- **Build**: Vite (fast dev server and bundling)
- **Routing**: React Router v6
- **State Management**: Zustand (lightweight, chosen over Redux)
- **HTTP Client**: Axios
- **Maps**: Yandex Maps API (for clustering dense land parcel datasets)
- **Styling**: CSS (Prettier configured)
- **Linting**: ESLint + TypeScript plugin, Prettier for formatting
- **Dev Server**: Runs on `http://localhost:5173` (dev), `http://localhost:3000` (alt)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ASGI Server**: Uvicorn with hot-reload in dev
- **Database**: PostgreSQL 15+ with PostGIS extension for geo-queries
- **ORM**: SQLAlchemy 2.0 with async support
- **Migrations**: Alembic (auto-migration generation)
- **Cache/Sessions**: Redis (Celery message broker)
- **Background Jobs**: Celery for async task processing
- **API Documentation**: Auto-generated at `/docs` (Swagger) and `/redoc` (ReDoc)
- **Code Style**: Black (100 char line length), isort for imports
- **Type Checking**: mypy with strict settings
- **Linting**: pylint
- **Testing**: pytest + pytest-asyncio + pytest-cov for coverage

### Containerization
- **Docker Compose**: Full stack (PostgreSQL + Redis + FastAPI + React)
- **PostgreSQL Image**: `postgis/postgis:15-3.3` (includes PostGIS extension)
- **Redis**: Official alpine image for minimal footprint

## Core Domain Model

### Central Entity: Land (Земельный участок)

All other elements pivot around the land parcel:

```
Land
├── LandFeatures (water, electricity, gas, roads, boundaries, etc.)
├── LandPlan (development roadmap)
│   └── LandPlanStep (individual stages)
├── RecommendedServices (computed from Land characteristics)
└── RelevantCompanies (filtered by service + region)
```

### Key Relationships

- **Land → Services**: 1:N (one land → many recommended services)
- **Service → Companies**: N:N (one service → many contractors; one contractor → many services)
- **Land → LandPlan**: 1:N (one land → one active plan, but historical versions)
- **LandPlan → Application**: 1:N (one plan → many contractor requests)
- **Application**: Connects User, Land, Service, Company, LandPlan

## API Design Principles

- **REST API** with `/api/v1` versioning
- **DTOs for frontend scenarios** (composite objects combining multiple bounded contexts)
- **Pagination and cursor-based navigation** for large result sets
- **Filtering and sorting** on backend (not frontend)
- **Idempotency keys** for sensitive operations

### Key API Endpoints (from spec)

- `GET /api/v1/lands` — List lands with filters (region, city, price, bbox, search)
- `GET /api/v1/lands/{id}` — Land card with full details
- `GET /api/v1/lands/{id}/recommendations` — Recommended services and next steps (powered by recommendations engine)
- `GET /api/v1/lands/{id}/companies` — Contractors relevant to this land
- `GET /api/v1/land-plans/{id}` — User's development plan for a land
- `PATCH /api/v1/land-plans/{id}` — Update plan steps/status
- `POST /api/v1/applications` — Create request to contractor
- `GET /api/v1/companies` — Company directory
- `GET /api/v1/services` — Service catalog

## Development Workflow

### Option 1: Docker Compose (Recommended for Full Stack)

Fastest way to get everything running (PostgreSQL, Redis, backend, frontend all in one go):

```bash
# Start all services (backend, frontend, database, redis)
docker-compose up

# In another terminal, run migrations once (one-time setup)
docker-compose exec backend poetry run alembic upgrade head

# Access:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development (Backend)

For backend-focused development with local IDE debugging:

```bash
# Install dependencies
cd backend
poetry install

# Copy and configure environment
cp .env.example .env
# Edit .env to point to your PostgreSQL and Redis (or use docker-compose for those)

# Run migrations
poetry run alembic upgrade head

# Start development server (auto-reload on file changes)
poetry run uvicorn app.main:app --reload

# Run all tests
poetry run pytest

# Run specific test
poetry run pytest tests/unit/test_auth.py

# Run with coverage
poetry run pytest --cov=app --cov-report=html
```

### Option 3: Local Development (Frontend)

For frontend-focused development:

```bash
# Install dependencies
cd frontend
npm install

# Create .env (if needed for API URL)
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server (auto-reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint and format
npm run lint               # Check for style issues
npm run format             # Auto-format code with Prettier
```

### Backend Code Quality

```bash
cd backend

# Format code with Black
poetry run black app tests

# Check linting
poetry run pylint app

# Type checking with mypy
poetry run mypy app

# Format imports with isort
poetry run isort app tests
```

### Database Migrations

```bash
cd backend

# Create new migration (Alembic auto-generates from model changes)
poetry run alembic revision --autogenerate -m "Add new field to Land model"

# Apply migrations
poetry run alembic upgrade head

# Revert last migration
poetry run alembic downgrade -1

# See migration history
poetry run alembic history
```

### Development Principles

1. **Start with the core recommendations engine** — This is what differentiates the product. Get the logic right early.
2. **API-first design** — Define API contracts before implementation.
3. **Geo-data handling** — Land parcels are geo-spatial data. Plan for efficient bounding-box queries, clustering, and distance-based filtering.
4. **Data normalization** — External sources (private listings, bankruptcy auctions, government sales) will have different schemas. Design ETL pipelines early.
5. **User context in applications** — When a user submits an application/request, the contractor should receive full context (land details, stage in development plan, user profile).

## Project Structure

### Directory Layout

```
LandPlan/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Settings (via pydantic-settings)
│   │   ├── core/
│   │   │   ├── security.py      # JWT, password hashing, auth helpers
│   │   │   ├── exceptions.py    # Custom exception classes
│   │   │   └── logging.py       # Logging configuration
│   │   ├── db/
│   │   │   ├── base.py          # SQLAlchemy engine/session setup
│   │   │   └── session.py       # Database session dependency
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── land.py          # Central Land model
│   │   │   ├── company.py
│   │   │   ├── service.py
│   │   │   ├── land_plan.py
│   │   │   ├── application.py
│   │   │   ├── recommendation.py
│   │   │   └── review.py
│   │   ├── schemas/             # Pydantic DTOs (request/response)
│   │   └── bounded_contexts/    # Domain logic organized by context
│   │       ├── identity_access/ # Authentication, authorization
│   │       ├── lands/           # Land search, filtering, geocoding
│   │       ├── services/        # Service catalog
│   │       ├── companies/       # Contractor management
│   │       ├── recommendations/ # **Core differentiator** — recommendations engine
│   │       ├── applications/    # Requests to contractors
│   │       ├── reviews/         # Ratings and feedback
│   │       └── admin/           # Admin functions
│   ├── tests/
│   │   ├── unit/                # Unit tests (isolated logic)
│   │   ├── integration/         # API contract tests
│   │   └── e2e/                 # End-to-end user flows
│   ├── alembic/                 # Database migrations (auto-generated)
│   ├── .env.example             # Template for environment variables
│   ├── pyproject.toml           # Poetry dependencies
│   ├── pytest.ini               # pytest configuration
│   ├── alembic.ini              # Alembic configuration
│   └── README.md                # Backend-specific docs
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # React entry point
│   │   ├── App.tsx              # Root component
│   │   ├── pages/               # Page components (Map, LandDetail, Cabinet, Auth)
│   │   ├── components/          # Reusable UI components
│   │   │   ├── Map/             # Yandex Maps integration
│   │   │   ├── FilterPanel/     # Land search filters
│   │   │   ├── LandCard/        # Land parcel card
│   │   │   ├── RecommendationsBlock/  # Recommendations display
│   │   │   └── ApplicationsList/      # Contractor requests
│   │   ├── api/                 # API client functions
│   │   │   ├── client.ts        # Axios instance with interceptors
│   │   │   ├── auth.ts
│   │   │   ├── lands.ts
│   │   │   ├── companies.ts
│   │   │   └── applications.ts
│   │   ├── store/               # Zustand store (global state)
│   │   │   └── authStore.ts
│   │   ├── types/               # TypeScript type definitions
│   │   └── styles/              # CSS files
│   ├── .env.example             # Vite env template
│   ├── vite.config.ts           # Vite configuration
│   ├── tsconfig.json            # TypeScript configuration
│   ├── .eslintrc.cjs            # ESLint rules
│   ├── .prettierrc               # Prettier formatting rules
│   ├── package.json
│   └── index.html               # HTML entry point
│
├── docker-compose.yml           # Full stack orchestration
├── README.md                    # Project specification (Russian)
└── CLAUDE.md                    # This file
```

### Key Implementation Notes

**Bounded Contexts**: The backend is organized by business domain (Identity, Lands, Services, etc.), not by technical layer. Each context has its own models, schemas, and route handlers. This makes it easy to:
- Reason about a feature in isolation
- Extract a context into a microservice later without rewriting domain logic
- Test business logic independently

**Recommendations Engine** (`backend/app/bounded_contexts/recommendations/`): This is the core of the platform. It analyzes land characteristics and generates recommended services and contractors. Keep this logic pure and testable.

**Models as the Source of Truth**: SQLAlchemy models in `backend/app/models/` define the schema. Alembic migrations are auto-generated from model changes. Always update models first, then generate migrations.

**Frontend State**: Zustand store is in `store/` — minimal global state (auth mostly). Component-local state with `useState` is preferred for UI state. API calls go through `api/` layer.

## Environment Configuration

### Backend (.env)

Key variables for `backend/.env` (copy from `.env.example`):

```ini
# Database (use docker-compose default or your own PostgreSQL instance)
DATABASE_URL=postgresql://landplan_user:landplan_password@localhost:5432/landplan_db

# Redis (for caching and Celery broker)
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
DEBUG=true
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# External APIs (when integrations are built)
YANDEX_MAPS_API_KEY=...
```

If you don't want to manage your own PostgreSQL, use `docker-compose up` to run it containerized.

### Frontend (.env)

```ini
VITE_API_URL=http://localhost:8000
```

Vite automatically loads `.env` files. Prefix variables with `VITE_` to expose them to the frontend.

## Common Development Tasks

### Adding a New API Endpoint

1. **Define the Pydantic schema** in `backend/app/schemas/` (request/response DTOs)
2. **Add the database model** in `backend/app/models/` if needed
3. **Generate migration** if model changed: `poetry run alembic revision --autogenerate`
4. **Implement business logic** in the appropriate bounded context
5. **Add route handler** in `backend/app/bounded_contexts/[context]/routes.py`
6. **Register route** in `backend/app/main.py`
7. **Write tests** in `backend/tests/`

Example:
```python
# backend/app/schemas/land.py
from pydantic import BaseModel
class LandCreate(BaseModel):
    title: str
    address: str
    price: float
    area: float

# backend/app/bounded_contexts/lands/routes.py
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1/lands", tags=["lands"])

@router.post("/")
async def create_land(land: LandCreate, db: AsyncSession = Depends(get_db)):
    # implementation
    pass
```

### Adding a Database Migration

After modifying a model:

```bash
cd backend
poetry run alembic revision --autogenerate -m "Add water feature to lands"
poetry run alembic upgrade head
```

Alembic auto-detects model changes. Always review the migration file before applying.

### Debugging Database Queries

Enable SQL logging in `.env`:

```ini
SQLALCHEMY_ECHO=true
```

This logs all SQL queries to the console.

### Running Tests with Coverage

```bash
cd backend
poetry run pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser to see coverage
```

### Testing API Endpoints

Start the dev server and visit `http://localhost:8000/docs` for the interactive Swagger UI. You can test any endpoint directly in the browser.

## Key Data Modeling Patterns

### Land Features Pattern

Rather than a wide table with many nullable columns, use a separate `land_features` table:

```
lands (id, title, address, price, area, ...)
land_features (land_id, has_water, has_electricity, has_gas, boundaries_defined, ...)
```

This allows flexible addition of features without schema changes.

### Land Plan as a Process

A `LandPlan` contains ordered `LandPlanStep`s. Each step:
- Is tied to a Service
- Has a status (pending, in_progress, completed)
- Can be assigned to a Company
- Can have associated Applications

This enables:
- Sequential workflow visualization
- Progress tracking
- Auditing the user's journey

### Source Tracking

Always track which external source a Land came from (`source_id` in lands table). This enables:
- Deduplication across sources
- Refreshing data from original sources
- Accounting for different data freshness
- Separate handling of different deal types (private, bankruptcy auctions, government sales)

## Database Design Considerations

- **Geo-indexing**: Use PostGIS extension for efficient bounding-box and distance queries
- **Denormalization**: Store computed fields like `recommendations` in a `land_recommendations` table to avoid expensive recalculation on every view
- **Audit trail**: Consider an `audit_logs` table for sensitive operations (admin actions, application status changes)
- **Soft deletes**: For user data, prefer marking records as inactive rather than hard deletion

## Integration Points

### External Data Sources

The system must ingest land data from multiple sources:
- Private listings APIs
- Bankruptcy auction databases
- Government land sales portals
- Future: Partner data feeds

Design ETL pipelines to:
1. Normalize schema from source to internal Land model
2. Detect duplicates (same geo-location, similar descriptions)
3. Mark data freshness and validity
4. Run on a schedule (background jobs)

## Security & Compliance

- **Authentication**: JWT + refresh tokens
- **Authorization**: RBAC by role (User, Company, Admin, Moderator)
- **Input validation**: Validate at API boundaries
- **Rate limiting**: Protect API endpoints
- **Audit logging**: Track admin actions and sensitive operations
- **Data privacy**: Contractor contact info should be shared only after user submits application

## Testing Strategy

- **Unit tests** for business logic (recommendations engine, calculations)
- **Integration tests** for API contracts
- **E2E tests** for critical user flows (land search → select → create plan → submit application)
- **Database tests** for complex queries (geo-queries, aggregations)

## Evolution Path (from spec)

### MVP
- Map + land list + filters
- Land card with basic details
- Service catalog + company directory
- Simple rule-based recommendations
- Basic application/request system
- User personal account

### Stage 2
- Company dashboard
- Reviews & ratings
- Company verification/moderation
- Advanced land plan features
- Analytics

### Stage 3
- Government data integrations
- Advanced auction workflows
- Communications hub
- Partner placement models

### Stage 4
- ML-based contractor ranking
- Intelligent next-step recommendations
- Budget/timeline forecasting
- User scenario personalization

## Important Concepts from Spec

**Land Plan** — Not just a to-do list. It's a sequential development roadmap tied to a specific land parcel. Users should see:
- What needs to be done (services)
- The order of steps (stage 1: cadastral, stage 2: geological, stage 3: design, etc.)
- Who can do it (contractors)
- Status tracking

**Relevance vs. Availability** — The system must distinguish between:
- Services **relevant to this land** (based on its characteristics)
- **Contractors capable** of performing that service in this region
- Contractor **preferences/SLA** (response time, verification status)

**Source Diversity** — Land data comes from different sources with different update frequencies. Always track provenance and freshness.

## Common Pitfalls to Avoid

1. **Treating it as just a classifieds site** — The core value is the recommendations engine connecting land characteristics to contractor services. Without this, it's a commodity marketplace.

2. **Overcomplicating the UI** — Resist the urge to show all fields and options. Guide users through a linear flow: find land → understand what's needed → select contractors → track progress.

3. **Ignoring data quality** — Imported land data will be messy (duplicate locations, inconsistent schemas, stale info). Plan for cleanup and deduplication early.

4. **Weak recommendations** — A naive rule engine is better than no recommendations. Even simple rules (has_water → recommend water services) significantly improve UX.

5. **Missing context in contractor requests** — When a contractor receives an application, they should see: the land location, its characteristics, the specific stage in development, the user's intent. Raw request forms lose this context.

## Recommendations Engine (Core Differentiator)

Located in `backend/app/bounded_contexts/recommendations/`, this is where the magic happens.

### What It Does

The recommendations engine takes a land's characteristics and outputs:
1. **Recommended services** (e.g., "water analysis", "cadastral survey", "geological study")
2. **Recommended contractors** for each service (ranked by relevance and region)
3. **Sequenced Land Plan** (stages 1, 2, 3, etc. in development order)

### MVP Approach: Rule-Based Logic

Don't overthink this. Simple rules work great:

```python
# backend/app/bounded_contexts/recommendations/engine.py

def get_recommendations(land: Land) -> RecommendationsDTO:
    """
    Example rule-based engine (MVP version)
    """
    recommendations = []

    # Rule 1: No water → recommend water analysis
    if not land.features.has_water:
        recommendations.append(
            RecommendedService(
                service_id=WATER_ANALYSIS_SERVICE_ID,
                stage=1,
                priority="required"
            )
        )

    # Rule 2: No boundaries defined → recommend cadastral
    if not land.features.boundaries_defined:
        recommendations.append(
            RecommendedService(
                service_id=CADASTRAL_SERVICE_ID,
                stage=1,
                priority="required"
            )
        )

    # Rule 3: Planning construction → recommend geology
    if land.intended_use == "construction":
        recommendations.append(
            RecommendedService(
                service_id=GEOLOGICAL_STUDY_SERVICE_ID,
                stage=2,
                priority="recommended"
            )
        )

    # Later: add more rules, weights, ML ranking
    return RecommendationsDTO(recommendations=recommendations)
```

### Adding New Rules

1. Open `backend/app/bounded_contexts/recommendations/engine.py`
2. Add a new rule function (keep them pure and testable)
3. Add test in `backend/tests/unit/recommendations/test_engine.py`
4. Update Swagger docs if needed

### Testing the Engine

```bash
cd backend
poetry run pytest tests/unit/recommendations/ -v
```

The engine should:
- Handle edge cases (missing data, null values)
- Be deterministic (same input = same output)
- Be fast (no expensive queries inside the engine)
- Be testable without a database (unit tests preferred over integration)

---

## Deployment & Production Notes

### Environment Variables

Before deploying, ensure these are set securely:
- `JWT_SECRET_KEY` — Use a strong, random key (not the dev key)
- `DEBUG=false` — Never run with debug enabled in production
- `CORS_ORIGINS` — Whitelist only your frontend domain
- `DATABASE_URL` — Use a managed PostgreSQL (AWS RDS, etc.)
- `REDIS_URL` — Use a managed Redis if possible

### Database Backups

PostgreSQL databases should be backed up regularly:
```bash
pg_dump landplan_db > backup.sql
```

### Monitoring

Add logging and monitoring for:
- API response times (Recommendations Engine especially)
- Database query performance (use `EXPLAIN ANALYZE`)
- Redis memory usage
- Celery task failures (if using background jobs)

---

When working on implementation, refer back to the full specification in README.md for business context, use cases, and detailed requirements.
