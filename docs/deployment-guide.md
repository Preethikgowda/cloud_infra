# IntelliWealth – Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development (Docker Compose)](#local-development)
3. [EKS Deployment](#eks-deployment)
4. [Manifest Reference](#manifest-reference)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24+ | Container runtime |
| Docker Compose | 2.20+ | Local orchestration |
| kubectl | 1.28+ | Kubernetes CLI |
| AWS CLI | 2.x | ECR authentication |
| eksctl | 0.170+ | EKS cluster management |
| Helm | 3.x | ALB controller install |

---

## Local Development

### Quick Start

```bash
# Clone and configure
cd NewIntelliwealth
cp .env.example .env

# Start all services
docker-compose up --build -d

# Verify health
curl http://localhost:8000/health   # Portfolio Service
curl http://localhost:8001/health   # Market Service
curl http://localhost:8002/health   # AI Insight Service
curl http://localhost:3000          # Frontend
```

### Service URLs

| Service | URL | Swagger |
|---------|-----|---------|
| Frontend | http://localhost:3000 | — |
| Portfolio API | http://localhost:8000 | http://localhost:8000/docs |
| Market API | http://localhost:8001 | http://localhost:8001/docs |
| AI Insight API | http://localhost:8002 | http://localhost:8002/docs |
| PostgreSQL | localhost:5432 | — |
| Redis | localhost:6379 | — |

### Docker Commands

```bash
# Rebuild a single service
docker-compose up --build portfolio-service -d

# View logs
docker-compose logs -f market-service

# Stop everything
docker-compose down

# Reset data (removes volumes)
docker-compose down -v
```

---

## EKS Deployment

### Step 1: Create EKS Cluster

```bash
eksctl create cluster \
  --name intelliwealth-prod \
  --region us-east-1 \
  --version 1.29 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 6 \
  --managed
```

### Step 2: Install AWS Load Balancer Controller

```bash
# Add EKS chart repo
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install the controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=intelliwealth-prod \
  --set serviceAccount.create=true
```

### Step 3: Create ECR Repositories

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com"

for repo in portfolio-service market-service ai-insight-service frontend; do
  aws ecr create-repository \
    --repository-name intelliwealth/$repo \
    --region us-east-1
done
```

### Step 4: Build & Push Images

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_REGISTRY

# Build and push each service
for service in portfolio-service market-service ai-insight-service frontend; do
  docker build -t $ECR_REGISTRY/intelliwealth/$service:latest ./$service/
  docker push $ECR_REGISTRY/intelliwealth/$service:latest
done
```

### Step 5: Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/base/namespace.yaml

# Deploy infrastructure
kubectl apply -f k8s/base/postgres/
kubectl apply -f k8s/base/redis/

# Wait for infrastructure readiness
kubectl wait --for=condition=ready pod -l app=postgres -n intelliwealth --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n intelliwealth --timeout=60s

# Deploy application services
kubectl apply -f k8s/base/portfolio-service/
kubectl apply -f k8s/base/market-service/
kubectl apply -f k8s/base/ai-insight-service/
kubectl apply -f k8s/base/frontend/

# Deploy ingress
kubectl apply -f k8s/base/ingress.yaml

# Verify deployment
kubectl get pods -n intelliwealth
kubectl get svc -n intelliwealth
kubectl get ingress -n intelliwealth
```

### Step 6: Update Secrets (Production)

```bash
# Update database password
kubectl create secret generic postgres-secret \
  -n intelliwealth \
  --from-literal=POSTGRES_USER=intelliwealth \
  --from-literal=POSTGRES_PASSWORD='<STRONG_PASSWORD>' \
  --from-literal=POSTGRES_DB=intelliwealth_db \
  --from-literal=DATABASE_URL='postgresql://intelliwealth:<STRONG_PASSWORD>@postgres:5432/intelliwealth_db' \
  --dry-run=client -o yaml | kubectl apply -f -

# Update JWT secret
kubectl create secret generic portfolio-service-secret \
  -n intelliwealth \
  --from-literal=DATABASE_URL='postgresql://intelliwealth:<STRONG_PASSWORD>@postgres:5432/intelliwealth_db' \
  --from-literal=JWT_SECRET_KEY='<SECURE_JWT_KEY>' \
  --dry-run=client -o yaml | kubectl apply -f -

# Set AWS Bedrock credentials (when switching to production LLM)
kubectl create secret generic ai-insight-secret \
  -n intelliwealth \
  --from-literal=AWS_ACCESS_KEY_ID='<ACCESS_KEY>' \
  --from-literal=AWS_SECRET_ACCESS_KEY='<SECRET_KEY>' \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Step 7: Configure Ingress Domain

Edit `k8s/base/ingress.yaml`:
- Replace `${DOMAIN_NAME}` with your domain
- Replace `${ACM_CERTIFICATE_ARN}` with your ACM certificate ARN

```bash
kubectl apply -f k8s/base/ingress.yaml
```

---

## Manifest Reference

### Directory Structure

```
k8s/base/
├── namespace.yaml
├── ingress.yaml
├── postgres/
│   ├── secret.yaml
│   ├── configmap.yaml
│   ├── pvc.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── redis/
│   ├── configmap.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── portfolio-service/
│   ├── secret.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── market-service/
│   ├── secret.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── ai-insight-service/
│   ├── secret.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
└── frontend/
    ├── configmap.yaml
    ├── deployment.yaml
    ├── service.yaml
    └── hpa.yaml
```

### Resource Budget

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit | Min Replicas | Max Replicas |
|---------|------------|-----------|----------------|-------------|-------------|-------------|
| PostgreSQL | 250m | 1000m | 256Mi | 1Gi | 1 | 1 |
| Redis | 100m | 250m | 128Mi | 256Mi | 1 | 1 |
| Portfolio Service | 250m | 500m | 256Mi | 512Mi | 2 | 8 |
| Market Service | 250m | 500m | 256Mi | 512Mi | 2 | 6 |
| AI Insight Service | 250m | 500m | 256Mi | 512Mi | 2 | 10 |
| Frontend | 50m | 200m | 64Mi | 128Mi | 2 | 6 |
| **Total (min)** | **1.15 vCPU** | — | **1.22 Gi** | — | **10** | — |

### Health Probe Summary

| Service | Startup | Readiness | Liveness |
|---------|---------|-----------|----------|
| PostgreSQL | — | pg_isready (10s) | pg_isready (30s) |
| Redis | — | redis-cli ping (5s) | redis-cli ping (15s) |
| Portfolio | /health (5s×30) | /readiness (20s) | /liveness (40s) |
| Market | /health (5s×30) | /readiness (25s) | /liveness (40s) |
| AI Insight | /health (5s×20) | /readiness (15s) | /liveness (25s) |
| Frontend | — | /nginx-health (5s) | /nginx-health (10s) |

---

## Troubleshooting

### Pod Not Starting

```bash
kubectl describe pod <pod-name> -n intelliwealth
kubectl logs <pod-name> -n intelliwealth --previous
```

### Database Migration Failed

```bash
kubectl exec -it deploy/portfolio-service -n intelliwealth -- alembic upgrade head
kubectl exec -it deploy/market-service -n intelliwealth -- alembic upgrade head
```

### Check HPA Status

```bash
kubectl get hpa -n intelliwealth
kubectl describe hpa portfolio-service-hpa -n intelliwealth
```

### Rolling Restart

```bash
kubectl rollout restart deployment/portfolio-service -n intelliwealth
kubectl rollout status deployment/portfolio-service -n intelliwealth
```

### View Ingress ALB

```bash
kubectl get ingress -n intelliwealth
kubectl describe ingress intelliwealth-ingress -n intelliwealth
```
