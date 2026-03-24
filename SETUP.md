# LandPlan - Setup Guide

This guide will help you get the LandPlan platform up and running in your development environment.

## Prerequisites

- Docker & Docker Compose installed
- Git
- Python 3.11+ (if not using Docker)
- Node.js 18+ (if not using Docker)

## Quick Start with Docker Compose

The easiest way to start development is using Docker Compose:

```bash
# Clone the repository
git clone <repo-url>
cd LandPlan

# Start all services
docker-compose up

# The application will be available at:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:5173
# - API Documentation: http://localhost:8000/docs
```

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install poetry
poetry install

# Setup environment
cp .env.example .env

# Initialize database (requires PostgreSQL running locally)
# Update DATABASE_URL in .env first
alembic upgrade head

# Run development server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

## Project Structure

```
backend/
├── app/
│   ├── main.py (FastAPI entry point)
│   ├── config.py (Settings)
│   ├── core/ (Security, logging, exceptions)
│   ├── db/ (Database configuration)
│   ├── models/ (SQLAlchemy ORM models)
│   ├── schemas/ (Pydantic DTOs)
│   └── bounded_contexts/ (Domain logic)
├── tests/ (Unit and integration tests)
└── pyproject.toml (Python dependencies)

frontend/
├── src/
│   ├── main.tsx (Entry point)
│   ├── App.tsx (Root component)
│   ├── pages/ (Page components)
│   ├── components/ (Reusable components)
│   ├── services/ (API clients)
│   ├── hooks/ (Custom React hooks)
│   ├── context/ (Context providers)
│   ├── types/ (TypeScript types)
│   └── utils/ (Utilities)
└── package.json (JavaScript dependencies)
```

## Database

PostgreSQL is required with PostGIS extension for geographic queries.

When using Docker Compose, the database is automatically set up. For manual setup:

```bash
# Create database
createdb -U landplan_user landplan_db

# Enable PostGIS
psql -U landplan_user -d landplan_db -c "CREATE EXTENSION postgis;"
```

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/
pytest tests/ --cov=app  # With coverage
pytest tests/unit/ -v     # Verbose output
```

### Frontend Tests

```bash
cd frontend
npm test
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development Workflow

1. Backend changes trigger auto-reload with `--reload` flag
2. Frontend changes trigger HMR (Hot Module Reload) automatically
3. Database migrations use Alembic:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Troubleshooting

### Docker port conflicts
If port 5432, 6379, 8000, or 5173 are already in use:
- Modify port mappings in `docker-compose.yml`
- Or stop conflicting containers: `docker ps` and `docker stop <container>`

### Database connection issues
- Ensure PostgreSQL is running (Docker Compose handles this)
- Check DATABASE_URL in .env matches your setup
- Verify database exists: `psql -l`

### Frontend won't build
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## Common Commands

```bash
# Start development environment
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild images after dependency changes
docker-compose up --build

# Run backend tests
docker-compose exec backend pytest

# Access database shell
docker-compose exec db psql -U landplan_user -d landplan_db
```

## Next Steps

1. Read [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) for implementation phases
2. Check [CLAUDE.md](./CLAUDE.md) for architecture guidelines
3. Start with Phase 1 implementation (Backend Fundament)

## Support

For issues and questions:
- Check existing GitHub issues
- Create a new issue with detailed description
- Contact the development team
