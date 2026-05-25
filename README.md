# IntelliWealth

IntelliWealth is a Docker-based microservice application for portfolio tracking, asset allocation analysis, and market intelligence.

The application is intentionally kept simple for EC2 deployment later: React frontend, FastAPI backend services, PostgreSQL, Redis, and Docker Compose.

## Services

```text
frontend             React + Vite + TypeScript + Nginx
portfolio-service    FastAPI + SQLAlchemy + Alembic + PostgreSQL
market-service       FastAPI + SQLAlchemy + PostgreSQL + Redis
postgres             Local development database
redis                Local/cache service
```

AI, Kubernetes, and monitoring stacks have been removed from the active application setup.

## Local Development

Start the full local stack:

```bash
docker compose up --build -d
```

Open:

```text
Frontend:       http://localhost:3000
Portfolio API:  http://localhost:8000/docs
Market API:     http://localhost:8001/docs
PostgreSQL:     localhost:5432
Redis:          localhost:6379
```

Stop:

```bash
docker compose down
```

Reset local data:

```bash
docker compose down -v
```

## Production Docker Files

Backend EC2 compose file:

```text
docker-compose.prod.yml
```

Runs:

```text
portfolio-service
market-service
redis
```

Frontend EC2 compose file:

```text
docker-compose.frontend.prod.yml
```

Runs:

```text
frontend
```

Production environment template:

```text
.env.prod.example
```

DockerHub build script:

```text
scripts/build-and-push.sh
```

## API Routing

The frontend uses:

```text
VITE_API_BASE_URL=/api/v1
```

Backend route ownership:

```text
/api/v1/auth       -> portfolio-service:8000
/api/v1/customers  -> portfolio-service:8000
/api/v1/portfolio  -> portfolio-service:8000
/api/v1/market     -> market-service:8001
```

For local Docker development, `frontend/nginx.dev.conf` proxies API calls to backend containers.

For production, `frontend/nginx.conf` serves static files only. API routing should be handled outside the frontend container, for example by a load balancer or reverse proxy.

## Repository Structure

```text
.
├── docker/                         # Local database initialization
├── docs/                           # Docker-focused documentation
├── frontend/                       # React frontend
├── market-service/                 # Market intelligence API
├── portfolio-service/              # Auth, customer, portfolio APIs
├── scripts/                        # Docker build/push helper
├── docker-compose.yml              # Local development stack
├── docker-compose.prod.yml         # Backend production stack
├── docker-compose.frontend.prod.yml# Frontend production stack
├── .env.example                    # Local environment template
└── .env.prod.example               # Production environment template
```

## Notes

- Do not commit real `.env` files or production secrets.
- PostgreSQL is local only in `docker-compose.yml`; production should inject `DATABASE_URL`.
- Redis is included in production compose as an ephemeral cache.
