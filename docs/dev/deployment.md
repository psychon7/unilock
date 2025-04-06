# Deployment Guide

<<<<<<< HEAD
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
=======
Instructions for deploying the application.
>>>>>>> db91a5192e96e6e8b41e9bb543a166b3257a9e05
