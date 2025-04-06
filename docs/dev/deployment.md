# Deployment Guide

## Docker Compose
```bash
docker-compose up -d --build
```

## Kubernetes (Helm)
```bash
helm install unilock ./helm --values ./helm/prod-values.yaml
```

## Cloud Providers

### AWS ECS
```bash
# Create ECR repository
aws ecr create-repository --repository-name unilock

# Build and push
docker build -t unilock .
docker tag unilock:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/unilock:latest
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/unilock:latest

# Deploy stack
aws cloudformation deploy --template-file ecs.yaml --stack-name unilock
```

### Google Cloud Run
```bash
gcloud run deploy unilock --image gcr.io/PROJECT_ID/unilock
```

## Monitoring
- Prometheus: `/metrics` endpoint
- Health checks: `/health`
