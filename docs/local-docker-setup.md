# Local Docker Setup

This guide explains how to run the full IntelliWealth application locally using Docker Compose.

## Prerequisites

Install:

- Docker Desktop
- Docker Compose v2

Check versions:

```bash
docker --version
docker compose version
```

## Start The Full Stack

From the project root:

```bash
docker compose up --build -d
```

This starts:

- PostgreSQL
- Redis
- Portfolio service
- Market service
- AI insight service
- Frontend
- Prometheus
- Grafana

## Check Status

```bash
docker compose ps
```

Healthy services should show `healthy` or `running`.

## Application URLs

```text
Frontend:       http://localhost:3000
Portfolio API:  http://localhost:8000/docs
Market API:     http://localhost:8001/docs
AI API:         http://localhost:8002/docs
Prometheus:     http://localhost:9090
Grafana:        http://localhost:3001
```

Grafana:

```text
Username: admin
Password: intelliwealth2026
```

## Health Checks

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

On PowerShell, use:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8001/health
curl.exe http://localhost:8002/health
```

## First User Flow

1. Open `http://localhost:3000`.
2. Click `Sign up`.
3. Create a new user.
4. The user is stored in PostgreSQL.
5. Go to Portfolio.
6. Create a portfolio.
7. Add assets.
8. View Dashboard and Allocation.
9. Go to History and record a snapshot.

## Admin Flow

Login:

```text
Email: admin@intelliwealth.io
Password: admin123
```

Then open Admin from the sidebar.

Admin can:

- View database users.
- Add a user.
- Edit user details.
- Activate or deactivate users.

## View Logs

All services:

```bash
docker compose logs -f
```

Specific service:

```bash
docker compose logs -f frontend
docker compose logs -f portfolio-service
docker compose logs -f market-service
docker compose logs -f ai-insight-service
docker compose logs -f postgres
```

## Stop The Stack

```bash
docker compose down
```

## Reset Database And Volumes

Use this only when you want a clean local environment:

```bash
docker compose down -v
docker compose up --build -d
```

## Rebuild After Code Changes

Frontend only:

```bash
docker compose up --build -d frontend
```

Portfolio service only:

```bash
docker compose up --build -d portfolio-service
```

Everything:

```bash
docker compose up --build -d
```

## Common Issues

### Port Already In Use

Stop the process using the port or change the compose mapping.

Common ports:

```text
3000 frontend
3001 grafana
5432 postgres
6379 redis
8000 portfolio service
8001 market service
8002 AI service
9090 prometheus
```

### Login Fails

Check:

- PostgreSQL is healthy.
- Portfolio service is healthy.
- The user exists in the database.
- Password is correct.

### Frontend Does Not Show New Code

Rebuild the frontend container:

```bash
docker compose up --build -d frontend
```
