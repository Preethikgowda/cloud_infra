# IntelliWealth Cloud Infrastructure

IntelliWealth is a Docker-based microservice application for portfolio tracking, customer portfolio management, asset allocation analysis, and market intelligence.

The repository is designed for local Docker development first, with separate production compose files for EC2-style deployments.

## Architecture

```text
React/Vite frontend
        |
        | /api/v1/*
        v
Nginx frontend reverse proxy
        |
        +--> portfolio-service:8000
        |      - Authentication
        |      - Customers
        |      - Portfolios
        |
        +--> market-service:8001
               - Market intelligence
               - Redis-backed caching

PostgreSQL stores application data.
Redis stores cache data for market-service.
```

## Services

| Service | Technology | Local URL |
| --- | --- | --- |
| frontend | React, Vite, TypeScript, Nginx | http://localhost:3000 |
| portfolio-service | FastAPI, SQLAlchemy, Alembic, PostgreSQL | http://localhost:8000/docs |
| market-service | FastAPI, SQLAlchemy, PostgreSQL, Redis | http://localhost:8001/docs |
| postgres | PostgreSQL 16 Alpine | localhost:5432 |
| redis | Redis 7 Alpine | localhost:6379 |

## Prerequisites

- Docker Desktop
- Docker Compose v2
- Git

No local Node.js or Python installation is required for the Docker workflow.

## Local Development

Start the full application stack:

```bash
docker compose up --build -d
```

Open the application:

```text
Frontend:       http://localhost:3000
Portfolio API:  http://localhost:8000/docs
Market API:     http://localhost:8001/docs
```

Check container status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop the stack:

```bash
docker compose down
```

Stop the stack and remove local database/cache volumes:

```bash
docker compose down -v
```

## Health Checks

```text
Frontend health:       http://localhost:3000/health
Portfolio API health:  http://localhost:8000/health
Market API health:     http://localhost:8001/health
```

Expected API health response:

```json
{"status":"ok"}
```

## Environment Configuration

Local Docker defaults are defined in `docker-compose.yml`. You can override them with a local `.env` file.

Start from the example:

```bash
cp .env.example .env
```

Important local variables:

| Variable | Purpose |
| --- | --- |
| POSTGRES_USER | PostgreSQL username |
| POSTGRES_PASSWORD | PostgreSQL password |
| POSTGRES_DB | PostgreSQL database name |
| DATABASE_URL | Backend database connection string |
| REDIS_URL | Market-service Redis connection string |
| JWT_SECRET_KEY | Signing key for JWT tokens |
| VITE_API_BASE_URL | Frontend API base path |
| PORTFOLIO_SERVICE_CORS_ORIGINS | Allowed frontend origins for portfolio-service |
| MARKET_SERVICE_CORS_ORIGINS | Allowed frontend origins for market-service |

Do not commit real `.env`, `.env.prod`, keys, certificates, or production secrets.

## API Routing

The frontend is built with:

```text
VITE_API_BASE_URL=/api/v1
```

In local Docker development, `frontend/nginx.dev.conf` proxies API requests to the backend containers:

| Route | Service |
| --- | --- |
| `/api/v1/auth` | portfolio-service:8000 |
| `/api/v1/customers` | portfolio-service:8000 |
| `/api/v1/portfolio` | portfolio-service:8000 |
| `/api/v1/market` | market-service:8001 |

## Production Compose Files

This repository includes separate production compose files:

| File | Purpose |
| --- | --- |
| `docker-compose.prod.yml` | Backend production services: portfolio-service, market-service, redis |
| `docker-compose.frontend.prod.yml` | Frontend production service |
| `.env.prod.example` | Production environment template |

For production, create `.env.prod` from `.env.prod.example` and provide real values:

```bash
cp .env.prod.example .env.prod
```

Backend production example:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

Frontend production example:

```bash
docker compose --env-file .env.prod -f docker-compose.frontend.prod.yml up -d
```

In production, `frontend/nginx.conf` serves static files only. API routing should be handled by an external reverse proxy or load balancer.

## Build And Publish Docker Images

The helper script is located at:

```text
scripts/build-and-push.sh
```

Set Docker Hub values in the environment before using it:

```bash
export DOCKERHUB_USERNAME=your-dockerhub-user
export IMAGE_TAG=latest
```

## Repository Structure

```text
.
|-- docker/                         Local database initialization
|-- docs/                           Docker and publishing notes
|-- frontend/                       React frontend and Nginx config
|-- market-service/                 Market intelligence FastAPI service
|-- portfolio-service/              Auth, customer, and portfolio FastAPI service
|-- scripts/                        Docker build/push helper scripts
|-- docker-compose.yml              Local development stack
|-- docker-compose.prod.yml         Backend production stack
|-- docker-compose.frontend.prod.yml Frontend production stack
|-- .env.example                    Local environment template
|-- .env.prod.example               Production environment template
`-- README.md                       Project documentation
```

## GitHub Publishing

Initialize and push to the existing `cloud_infra` repository:

```bash
git init
git add -A
git commit -m "Prepare Docker microservice application"
git branch -M main
git remote add cloud_infra https://github.com/Preethikgowda/cloud_infra.git
git push -u cloud_infra main
```

If the remote already has commits, pull or fetch first and resolve any conflicts before pushing.
