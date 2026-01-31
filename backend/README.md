# Backend API

FastAPI backend for Atlassian Cloud Migration Bug Dashboard.

## Setup

### 1. Install Dependencies

```bash
cd backend
poetry install
poetry shell
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start PostgreSQL

```bash
# From project root
docker-compose up -d postgres
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

### 5. Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## First Time Setup - Load Data

Once the API is running, load initial bug data:

```bash
curl -X POST "http://localhost:8000/api/bugs/sync?fetch_all=false"
```

This will:
1. Fetch open bugs from Jira API
2. Parse and store them in PostgreSQL
3. Return a summary

## API Endpoints

### Health
- `GET /api/health` - Health check

### Bugs
- `GET /api/bugs` - List bugs (paginated)
  - Query params: `page`, `page_size`, `status`, `priority`, `search`
- `GET /api/bugs/{jira_key}` - Get bug details
- `POST /api/bugs/sync` - Sync bugs from Jira
- `GET /api/bugs/statuses/list` - List all statuses
- `GET /api/bugs/priorities/list` - List all priorities

### Analytics
- `GET /api/analytics/overview` - Dashboard overview stats
- `GET /api/analytics/trends` - Trend data for charts
- `GET /api/analytics/resolution-times` - Resolution time analysis

## Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black .
ruff check .
```

### Database Migrations (Future)
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/       # API endpoints
│   ├── core/             # Config & database
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
├── etl/                  # ETL scripts (future)
├── scripts/              # Utility scripts
└── tests/                # Unit tests
```

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **PostgreSQL** - Database
- **Poetry** - Dependency management

## Environment Variables

```bash
DATABASE_URL=postgresql://atlassian_user:atlassian_pass@localhost:5432/atlassian_bugs
JIRA_BASE_URL=https://jira.atlassian.com
JIRA_PROJECT=MIG
JIRA_ISSUE_TYPE=Bug
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```
