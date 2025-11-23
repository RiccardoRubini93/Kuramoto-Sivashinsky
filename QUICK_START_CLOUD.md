# Quick Start Guide - Cloud Deployment

This is a quick reference for deploying the KS Simulator to Google Cloud Platform.

For comprehensive documentation, see [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)

## Prerequisites

- Google Cloud Platform account with billing enabled
- GitHub account
- Docker installed locally (for testing)

## Quick Setup (5 minutes)

### 1. Automated Setup

Run the automated setup script:

```bash
./setup-gcp.sh
```

This will:
- Enable all required GCP APIs
- Create Artifact Registry repository
- Set up Workload Identity Federation
- Create and configure service account
- Display GitHub secrets to add

### 2. Add GitHub Secrets

Go to your GitHub repository settings and add the three secrets displayed by the setup script:

1. `GCP_PROJECT_ID`
2. `WIF_PROVIDER`
3. `WIF_SERVICE_ACCOUNT`

### 3. Deploy

Push to the `cloud-deploy` branch:

```bash
git push origin cloud-deploy
```

The GitHub Action will automatically deploy to Cloud Run!

## Testing Locally

### Using Docker

```bash
# Build
docker build -t ks-simulator .

# Run
docker run -p 8080:8080 ks-simulator

# Access at http://localhost:8080
```

### Using Docker Compose

```bash
docker-compose up
```

## Deployment Options

### Option 1: Cloud Run (Automatic)

- Pushes to `cloud-deploy` or `main` trigger automatic deployment
- See workflow: `.github/workflows/deploy-cloud-run.yml`

### Option 2: App Engine (Manual)

1. Go to GitHub Actions
2. Select "Deploy to App Engine"
3. Click "Run workflow"

### Option 3: Compute Engine (Manual)

1. Go to GitHub Actions
2. Select "Deploy to Compute Engine"
3. Click "Run workflow"

## Manual Deployment

### Cloud Run

```bash
gcloud run deploy ks-simulator \
  --image=gcr.io/$PROJECT_ID/ks-simulator:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated
```

### App Engine

```bash
gcloud app deploy app.yaml
```

## Troubleshooting

### Build Fails

```bash
# Test build locally
docker build -t ks-simulator .
```

### Permission Errors

```bash
# Re-authenticate
gcloud auth login
gcloud auth configure-docker
```

### View Logs

```bash
# Cloud Run
gcloud run services logs read ks-simulator

# Local Docker
docker logs <container-id>
```

## Architecture

```
GitHub Repository
    ↓
GitHub Actions (CI/CD)
    ↓
Google Cloud Build
    ↓
Artifact Registry (Docker images)
    ↓
[Cloud Run / App Engine / Compute Engine]
    ↓
Application Running
```

## Files Overview

| File | Purpose |
|------|---------|
| `Dockerfile` | Container definition |
| `docker-compose.yml` | Local testing |
| `wsgi.py` | Production WSGI entry point |
| `app.yaml` | App Engine Standard config |
| `app.flexible.yaml` | App Engine Flexible config |
| `setup-gcp.sh` | Automated GCP setup script |
| `.github/workflows/` | CI/CD pipelines |
| `CLOUD_DEPLOYMENT.md` | Comprehensive guide |

## Support

- **Full Documentation**: [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)
- **GCP Console**: https://console.cloud.google.com
- **GitHub Actions**: Check the "Actions" tab in your repository

## Cost Estimate

- **Cloud Run**: $5-20/month (pay-per-use)
- **App Engine**: $10-30/month
- **Compute Engine**: $7-50/month (continuous)

**Recommendation**: Start with Cloud Run for best cost-efficiency.
