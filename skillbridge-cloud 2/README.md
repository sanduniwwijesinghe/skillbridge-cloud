# SkillBridge – Cloud-Native Microservices on AWS (SE6020)

**Author:** sanduniwijesinghe  
**Region:** ap-south-1 (Asia Pacific – Mumbai)

This repository contains a minimal end-to-end solution for the SkillBridge assignment:
- 3 microservices (FastAPI) — user, mentor, booking
- Dockerfiles for each service
- Kubernetes manifests (`/k8s`) for EKS or minikube
- CloudFormation templates (`/infra`) for VPC + S3 (+ optional RDS)
- GitHub Actions workflow to build & push images to ECR

## Architecture (High Level)

```
[Client]
  └──> API Gateway / Ingress
        └──> EKS (user, mentor, booking)
               ├──> RDS (PostgreSQL) – data
               └──> S3 – uploads
```

## Run Locally (Fast)

```bash
# User Service
cd services/user-service
pip install -r requirements.txt
uvicorn main:app --reload  # http://127.0.0.1:8000/docs

# Mentor Service
cd ../mentor-service
pip install -r requirements.txt
uvicorn main:app --reload

# Booking Service
cd ../booking-service
pip install -r requirements.txt
uvicorn main:app --reload
```

## Docker (Local)

```bash
docker build -t user-service:local services/user-service
docker run -p 8000:8000 user-service:local
```

## Kubernetes (minikube/EKS)

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/user-deploy.yaml
kubectl apply -f k8s/mentor-deploy.yaml
kubectl apply -f k8s/booking-deploy.yaml
kubectl apply -f k8s/ingress.yaml
```

> Replace image URIs in `k8s/*-deploy.yaml` with your ECR repo URIs.

## CloudFormation

Order:
1. Create stack with `infra/vpc.yaml`
2. Create stack with `infra/s3-and-rds.yaml` (set `CreateRDS=No` to avoid charges)

## GitHub Actions (CI/CD)

- Add GitHub secrets:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `ECR_URI` ⇒ e.g. `123456789012.dkr.ecr.ap-south-1.amazonaws.com`
- On `main` push, images are built and pushed to ECR.

## Folder Structure

```
skillbridge-cloud/
 ├─ services/
 │   ├─ user-service/
 │   ├─ mentor-service/
 │   └─ booking-service/
 ├─ k8s/
 ├─ infra/
 ├─ .github/workflows/
 └─ README.md
```

## Viva Tips (25 Oct)

- Show AWS Console (region = ap-south-1), S3 bucket, CloudFormation stacks.
- Run at least one service (`/health` endpoint) locally or on EC2.
- Explain NFRs: scalability (pods), security (IAM), affordability (free tier).
