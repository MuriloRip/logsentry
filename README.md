# LogSentry

[![CI Pipeline](https://github.com/MuriloRip/logsentry/actions/workflows/ci.yml/badge.svg)](https://github.com/MuriloRip/logsentry/actions/workflows/ci.yml)

A log analysis microservice built with **Python** and **FastAPI**. Provides real-time log ingestion, flexible querying, and analytics for application monitoring.

## Tech Stack

- **Python 3.12** + **FastAPI** 0.110
- **SQLAlchemy 2.0** + **PostgreSQL**
- **JWT Authentication** (python-jose + passlib)
- **Pydantic v2** for data validation
- **Pytest** for testing (with SQLite in-memory)
- **Docker** + **Docker Compose**
- **GitHub Actions** CI/CD

## Architecture

```
app/
├── config.py          # Environment-based settings
├── database.py        # Database connection & session
├── main.py            # FastAPI application entry point
├── models/            # SQLAlchemy ORM models
│   ├── user.py        # User with auth fields
│   ├── log_entry.py   # Log entries with severity levels
│   └── api_key.py     # API keys for programmatic access
├── schemas/           # Pydantic request/response schemas
│   ├── user_schema.py
│   └── log_schema.py
├── routers/           # API endpoint handlers
│   ├── auth.py        # Register, login, profile
│   ├── logs.py        # CRUD + batch ingestion
│   └── analytics.py   # Stats, top errors, service breakdown
└── services/          # Business logic layer
    ├── auth_service.py
    ├── log_service.py
    └── analytics_service.py
```

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16+ (or Docker)

### Run with Docker Compose

```bash
git clone https://github.com/MuriloRip/logsentry.git
cd logsentry

docker-compose up -d

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Run Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/logsentry
export SECRET_KEY=your-secret-key

# Run the server
uvicorn app.main:app --reload
```

### Run Tests

```bash
pytest tests/ -v
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (OAuth2 form) |
| GET | `/api/v1/auth/me` | Get current user profile |

### Log Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/logs/` | Ingest single log entry |
| POST | `/api/v1/logs/batch` | Batch ingest (up to 100) |
| GET | `/api/v1/logs/` | Query logs with filters |
| GET | `/api/v1/logs/{id}` | Get specific log entry |
| DELETE | `/api/v1/logs/{id}` | Delete log entry |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/stats` | Aggregated log statistics |
| GET | `/api/v1/analytics/top-errors` | Top error sources |
| GET | `/api/v1/analytics/services` | Service breakdown |

## Usage Examples

### Register & Login
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "dev", "email": "dev@example.com", "password": "secret123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=dev@example.com&password=secret123"
```

### Ingest Logs
```bash
curl -X POST http://localhost:8000/api/v1/logs/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "ERROR",
    "message": "Connection timeout to database",
    "source": "app.database.pool",
    "service_name": "user-service",
    "environment": "production"
  }'
```

### Query Logs
```bash
# Filter by level and service
curl "http://localhost:8000/api/v1/logs/?level=ERROR&service_name=user-service&page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Analytics
```bash
# Stats for last 24 hours
curl "http://localhost:8000/api/v1/analytics/stats?hours=24" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | Database connection string |
| `SECRET_KEY` | — | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 1440 | Token expiry (24h) |
| `DEBUG` | false | Enable debug mode |

## License

MIT License
