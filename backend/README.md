# LandPlan Backend

FastAPI-based backend for the LandPlan platform.

## Architecture

The backend is organized using **modular monolith** pattern with **bounded contexts**:

- **Identity & Access** — Authentication, authorization, user management
- **Lands** — Land parcel data, search, filtering
- **Services** — Service catalog, categories
- **Companies** — Contractor information, capabilities
- **Recommendations** — Land development recommendations engine (core logic)
- **Applications** — User requests to contractors
- **Reviews** — User feedback and ratings
- **Admin & Moderation** — Administrative functions
- **Integrations** — Data import from external sources
- **Notifications** — Email/SMS notifications (future)

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ with PostGIS
- Redis (optional, for caching)
- Poetry (for dependency management)

### Installation

```bash
# Install dependencies
poetry install

# Create .env file from example
cp .env.example .env

# Update DATABASE_URL in .env to point to your PostgreSQL instance
```

### Database Setup

```bash
# Initialize database (creates tables from models)
# This happens automatically on first app startup, but you can also run migrations:

# Install Alembic if not already installed
poetry add alembic

# Run migrations
poetry run alembic upgrade head
```

### Running

```bash
# Start development server
poetry run uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/unit/test_auth.py

# Run with verbose output
poetry run pytest -v

# Run only integration tests
poetry run pytest tests/integration/
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings and configuration
│   ├── core/                   # Core utilities
│   │   ├── security.py         # JWT, password hashing
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── logging.py          # Logging setup
│   ├── db/                     # Database
│   │   ├── base.py            # SQLAlchemy setup
│   │   ├── session.py         # Session management
│   │   └── migrations/        # Alembic migrations
│   ├── models/                # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic DTOs
│   └── bounded_contexts/      # Domain logic by context
│       ├── identity_access/
│       ├── lands/
│       ├── services/
│       ├── companies/
│       ├── recommendations/
│       ├── applications/
│       ├── reviews/
│       └── admin/
├── tests/                     # Tests
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── pyproject.toml            # Poetry dependencies
├── alembic.ini              # Alembic configuration
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` — Register new user
- `POST /api/v1/auth/login` — Login and get tokens
- `POST /api/v1/auth/refresh` — Refresh access token

### Health
- `GET /api/v1/health` — Health check

### (Later phases)
- `/api/v1/lands` — Land search and listing
- `/api/v1/services` — Service catalog
- `/api/v1/companies` — Company directory
- `/api/v1/land-plans` — Development plans
- `/api/v1/applications` — Contractor requests

## Development

### Code Style

Code is formatted with Black and follows PEP 8:

```bash
# Format code
poetry run black app tests

# Check linting
poetry run pylint app
```

### Type Checking

```bash
poetry run mypy app
```

### Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Revert last migration
poetry run alembic downgrade -1
```

## Environment Variables

See `.env.example` for all available options:

- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `JWT_SECRET_KEY` — Secret key for JWT (change in production!)
- `DEBUG` — Enable debug mode
- `CORS_ORIGINS` — Allowed CORS origins
- etc.

## Security Notes

- Change `JWT_SECRET_KEY` in production
- Use HTTPS in production
- Set `DEBUG=False` in production
- Use environment variables for secrets (never commit to git)
- Implement rate limiting for API endpoints
- Validate all user inputs

## Troubleshooting

### Database connection issues

```bash
# Check PostgreSQL is running
psql -U landplan_user -d landplan_db

# Create database if missing
createdb -U landplan_user landplan_db

# Enable PostGIS extension
psql -U landplan_user -d landplan_db -c "CREATE EXTENSION postgis;"
```

### Port already in use

Change port in command:
```bash
poetry run uvicorn app.main:app --port 8001
```

### Dependency issues

```bash
# Clear poetry cache
poetry cache clear . --all

# Reinstall dependencies
rm poetry.lock
poetry install
```

## Next Steps

1. Implement **Lands** API (Phase 2)
2. Implement **Services & Companies** API (Phase 2)
3. Build **Recommendations Engine** (Phase 3 — core logic)
4. Connect **Frontend** (Phase 4)

See `DEVELOPMENT_PLAN.md` for detailed implementation roadmap.
