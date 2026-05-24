# IntelliWealth

IntelliWealth is a microservices-based wealth management dashboard for portfolio tracking, asset allocation analysis, market intelligence, and AI-assisted portfolio explanations.

The project is designed as a production-style learning and portfolio project. It combines a React frontend, Python FastAPI services, PostgreSQL, Redis, Docker Compose, Kubernetes manifests, and AWS infrastructure preparation.

## Core Idea

IntelliWealth is not a stock trading platform. It does not execute trades or connect to a broker.

The application helps a user:

- Register and log in with a real database-backed account.
- Create investment portfolios.
- Add portfolio assets such as stocks, bonds, gold, crypto, mutual funds, and cash.
- View portfolio value, holdings, and asset allocation.
- Save portfolio history snapshots.
- Use AI services to explain portfolio state and risk in plain language.
- Allow admins to manage users stored in PostgreSQL.

## Current Functional Scope

The current app includes:

- Real user registration and login backed by PostgreSQL.
- JWT authentication.
- Admin user management backed by the `customers` table.
- Real portfolio creation and asset management.
- Dashboard metrics calculated from saved portfolio data.
- Allocation views calculated from saved assets.
- Portfolio history snapshots.
- Market service and AI insight service scaffolding.
- Docker Compose local orchestration.
- Monitoring stack with Prometheus and Grafana.
- Kubernetes manifests for future cluster deployment.
- AWS CLI-based infrastructure preparation documentation.

## Architecture

```text
Frontend
React + TypeScript + Tailwind + Recharts
Runs on port 3000 through nginx in Docker

Portfolio Service
FastAPI + SQLAlchemy + JWT
Handles auth, customers, portfolios, assets, allocation, history
Runs on port 8000

Market Service
FastAPI + Redis
Provides market and risk analytics scaffolding
Runs on port 8001

AI Insight Service
FastAPI
Uses mock AI by default and can later use AWS Bedrock
Runs on port 8002

PostgreSQL
Primary relational database
Runs on port 5432

Redis
Cache layer for market analytics
Runs on port 6379

Prometheus
Metrics collection
Runs on port 9090

Grafana
Dashboards
Runs on port 3001
```

## Repository Structure

```text
.
├── ai-insight-service/       # AI explanation and scenario service
├── docker/                   # Database initialization scripts
├── docs/                     # Project documentation
├── frontend/                 # React frontend
├── k8s/                      # Kubernetes manifests
├── market-service/           # Market intelligence service
├── monitoring/               # Prometheus and Grafana configuration
├── portfolio-service/        # Auth, customer, portfolio, asset APIs
├── docker-compose.yml        # Local full-stack orchestration
├── .env.example              # Example environment variables
└── README.md
```

## Quick Start With Docker Compose

Prerequisites:

- Docker Desktop
- Docker Compose v2

Start the complete application:

```bash
docker compose up --build -d
```

Check containers:

```bash
docker compose ps
```

Open the frontend:

```text
http://localhost:3000
```

API docs:

```text
Portfolio API:  http://localhost:8000/docs
Market API:     http://localhost:8001/docs
AI API:         http://localhost:8002/docs
Prometheus:     http://localhost:9090
Grafana:        http://localhost:3001
```

Grafana default login:

```text
Username: admin
Password: intelliwealth2026
```

## User Flow

1. Open `http://localhost:3000`.
2. Sign up as a new user.
3. The user is saved in PostgreSQL.
4. Login uses the saved database record.
5. Go to Portfolio.
6. Create a portfolio.
7. Add real assets to the portfolio.
8. Dashboard and Allocation update from saved records.
9. Go to History and record snapshots.

Admin login is seeded by the backend:

```text
Email: admin@intelliwealth.io
Password: admin123
```

## Important Documentation

- [Application Overview](docs/application-overview.md)
- [Local Docker Setup](docs/local-docker-setup.md)
- [API and Data Flow](docs/api-and-data-flow.md)
- [AWS CLI Infrastructure](docs/aws-cli-infrastructure.md)
- [GitHub Publishing Guide](docs/github-publishing.md)
- [Architecture](docs/architecture.md)
- [Deployment Guide](docs/deployment-guide.md)

## Development Commands

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run build
```

Docker:

```bash
docker compose up --build -d
docker compose logs -f
docker compose down
```

Reset local database volumes:

```bash
docker compose down -v
```

## Production Direction

The project is prepared for a future AWS and Kubernetes deployment path:

- Amazon EKS for containers.
- Private app subnets for workloads.
- Public subnets for load balancers.
- Private database subnet for future PostgreSQL/RDS.
- NAT gateways for private outbound access.
- Security groups for bastion, ALB, EKS nodes, and PostgreSQL.

Current AWS infrastructure automation intentionally prepares infrastructure only. It does not create EKS, RDS, Route53, ACM, CloudFront, CI/CD, Helm releases, or Kubernetes workloads.

## Notes

- The default AI provider is `mock`, so AWS Bedrock credentials are not required for local development.
- Never commit real `.env` files, AWS credentials, SSH private keys, or production secrets.
- The frontend build output and `node_modules` are intentionally ignored.
