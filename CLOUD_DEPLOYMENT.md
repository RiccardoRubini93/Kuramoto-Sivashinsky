# Cloud Deployment Guide for Kuramoto-Sivashinsky Simulator

This guide provides comprehensive instructions for deploying the KS Simulator to Google Cloud Platform (GCP) using three different deployment options: Cloud Run, App Engine, and Compute Engine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial GCP Setup](#initial-gcp-setup)
3. [GitHub Actions Setup](#github-actions-setup)
4. [Deployment Options](#deployment-options)
   - [Option 1: Cloud Run (Recommended)](#option-1-cloud-run-recommended)
   - [Option 2: App Engine](#option-2-app-engine)
   - [Option 3: Compute Engine](#option-3-compute-engine)
5. [Local Testing with Docker](#local-testing-with-docker)
6. [Manual Deployment](#manual-deployment)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

1. **A Google Cloud Platform account** - [Sign up here](https://cloud.google.com/free)
2. **A GitHub account** with access to this repository
3. **Billing enabled** on your GCP project (required for deploying services)
4. **Docker installed locally** (for local testing)

### Required Tools

Install the following tools on your local machine:

```bash
# Google Cloud SDK (gcloud)
# Visit: https://cloud.google.com/sdk/docs/install

# Docker
# Visit: https://docs.docker.com/get-docker/

# Docker Compose (optional, for local testing)
# Visit: https://docs.docker.com/compose/install/
```

---

## Initial GCP Setup

### Step 1: Create a GCP Project

1. Go to the [GCP Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., `ks-simulator`)
5. Note your **Project ID** (you'll need this later)

### Step 2: Enable Required APIs

Enable the necessary Google Cloud APIs:

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com \
  appengine.googleapis.com \
  iamcredentials.googleapis.com
```

Or enable via the Console:
- Navigate to "APIs & Services" → "Enable APIs and Services"
- Search and enable: Cloud Build, Cloud Run, Artifact Registry, Compute Engine, App Engine

### Step 3: Create Artifact Registry Repository

Create a Docker repository to store container images:

```bash
# Create the repository
gcloud artifacts repositories create ks-simulator \
  --repository-format=docker \
  --location=us-central1 \
  --description="KS Simulator Docker images"

# Verify creation
gcloud artifacts repositories list
```

---

## GitHub Actions Setup

### Step 1: Set Up Workload Identity Federation (Recommended)

Workload Identity Federation allows GitHub Actions to authenticate to GCP without service account keys (more secure).

#### 1.1 Create a Workload Identity Pool

```bash
export PROJECT_ID="your-project-id"
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Create the pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Get the pool ID
export WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools describe "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)")
```

#### 1.2 Create a Workload Identity Provider

```bash
# Replace YOUR-GITHUB-ORG and YOUR-REPO with your values
export GITHUB_REPO="RiccardoRubini93/Kuramoto-Sivashinsky"

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

#### 1.3 Create a Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions-sa \
  --project="${PROJECT_ID}" \
  --display-name="GitHub Actions Service Account"

# Get the service account email
export SERVICE_ACCOUNT_EMAIL="github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# For App Engine (optional)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/appengine.appAdmin"

# For Compute Engine (optional)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/compute.admin"
```

#### 1.4 Allow GitHub Actions to Impersonate the Service Account

```bash
gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${GITHUB_REPO}"
```

#### 1.5 Get the Workload Identity Provider Resource Name

```bash
# This is what you'll add to GitHub Secrets
gcloud iam workload-identity-pools providers describe "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"
```

### Step 2: Configure GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GCP_PROJECT_ID` | `your-project-id` | Your GCP project ID |
| `WIF_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider` | Full provider resource name from step 1.5 |
| `WIF_SERVICE_ACCOUNT` | `github-actions-sa@PROJECT_ID.iam.gserviceaccount.com` | Service account email |

**Note:** Replace `PROJECT_NUMBER` and `PROJECT_ID` with your actual values.

### Alternative: Service Account Key (Less Secure)

If you prefer using a service account key instead of Workload Identity Federation:

```bash
# Create a service account
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions"

# Grant permissions (same as above)

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Add the entire contents of key.json as a GitHub secret named GCP_SA_KEY
# Then modify the workflows to use google-github-actions/auth@v2 with credentials_json
```

---

## Deployment Options

### Option 1: Cloud Run (Recommended)

**Best for:** Serverless, auto-scaling, pay-per-use applications

**Advantages:**
- Automatic scaling (including to zero)
- Pay only for what you use
- No infrastructure management
- Built-in HTTPS
- Fastest to deploy

#### Automatic Deployment via GitHub Actions

The deployment happens automatically when you push to the `cloud-deploy` or `main` branch.

**Workflow file:** `.github/workflows/deploy-cloud-run.yml`

To trigger a manual deployment:
1. Go to **Actions** tab in GitHub
2. Select "Deploy to Cloud Run"
3. Click "Run workflow"

#### Manual Deployment

```bash
# Build the Docker image
docker build -t gcr.io/$PROJECT_ID/ks-simulator:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/ks-simulator:latest

# Deploy to Cloud Run
gcloud run deploy ks-simulator \
  --image=gcr.io/$PROJECT_ID/ks-simulator:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --port=8080

# Get the service URL
gcloud run services describe ks-simulator \
  --platform=managed \
  --region=us-central1 \
  --format='value(status.url)'
```

#### Configuration Options

Adjust these parameters in `.github/workflows/deploy-cloud-run.yml`:

```yaml
env:
  REGION: us-central1        # Change deployment region
  SERVICE_NAME: ks-simulator # Change service name
```

Adjust resource limits:
```bash
--memory=2Gi    # Memory allocation (128Mi, 256Mi, 512Mi, 1Gi, 2Gi, 4Gi, 8Gi)
--cpu=2         # CPU allocation (1, 2, 4)
--timeout=300   # Request timeout in seconds (max 3600)
```

---

### Option 2: App Engine

**Best for:** Traditional web applications with managed infrastructure

**Advantages:**
- Integrated with other Google services
- Traffic splitting for A/B testing
- Custom domain mapping
- Application versioning

#### Deployment via GitHub Actions

This deployment is manual-triggered only:

1. Go to **Actions** tab in GitHub
2. Select "Deploy to App Engine"
3. Click "Run workflow"
4. Choose environment: `standard` or `flexible`
5. Click "Run workflow"

**Workflow file:** `.github/workflows/deploy-app-engine.yml`

#### Manual Deployment

##### Standard Environment

Create `app.yaml`:
```yaml
runtime: python311
instance_class: F2

entrypoint: gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 120 wsgi:server

env_variables:
  PORT: 8080
  HOST: 0.0.0.0

automatic_scaling:
  min_instances: 0
  max_instances: 10
  target_cpu_utilization: 0.65
```

Deploy:
```bash
gcloud app deploy --project=$PROJECT_ID
```

##### Flexible Environment

Create `app.yaml`:
```yaml
runtime: custom
env: flex

env_variables:
  PORT: 8080
  HOST: 0.0.0.0

automatic_scaling:
  min_num_instances: 1
  max_num_instances: 10
  cpu_utilization:
    target_utilization: 0.65

resources:
  cpu: 2
  memory_gb: 2
  disk_size_gb: 10
```

Deploy:
```bash
gcloud app deploy --project=$PROJECT_ID
```

#### Get App URL

```bash
gcloud app describe --format='value(defaultHostname)'
```

Your app will be available at: `https://PROJECT_ID.appspot.com`

---

### Option 3: Compute Engine

**Best for:** Full control over VM infrastructure

**Advantages:**
- Complete control over the VM
- SSH access for debugging
- Can run multiple services
- Persistent storage

#### Deployment via GitHub Actions

This deployment is manual-triggered only:

1. Go to **Actions** tab in GitHub
2. Select "Deploy to Compute Engine"
3. Click "Run workflow"
4. Choose machine type (e.g., `e2-standard-2`)
5. Click "Run workflow"

**Workflow file:** `.github/workflows/deploy-compute-engine.yml`

#### Manual Deployment

```bash
# Create instance with container
gcloud compute instances create-with-container ks-simulator-vm \
  --project=$PROJECT_ID \
  --zone=us-central1-a \
  --machine-type=e2-standard-2 \
  --container-image=gcr.io/$PROJECT_ID/ks-simulator:latest \
  --container-restart-policy=always \
  --container-env=PORT=8080,HOST=0.0.0.0 \
  --tags=http-server \
  --boot-disk-size=10GB

# Create firewall rule
gcloud compute firewall-rules create allow-ks-simulator \
  --project=$PROJECT_ID \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:8080 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server

# Get the external IP
gcloud compute instances describe ks-simulator-vm \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

Access the application at: `http://EXTERNAL_IP:8080`

#### SSH into the VM

```bash
gcloud compute ssh ks-simulator-vm --zone=us-central1-a
```

#### Update the container

```bash
gcloud compute instances update-container ks-simulator-vm \
  --zone=us-central1-a \
  --container-image=gcr.io/$PROJECT_ID/ks-simulator:latest
```

---

## Local Testing with Docker

### Build and Run Locally

```bash
# Build the image
docker build -t ks-simulator:local .

# Run the container
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e HOST=0.0.0.0 \
  ks-simulator:local

# Access at http://localhost:8080
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Test the container

```bash
# Health check
curl http://localhost:8080/

# Check container logs
docker logs <container-id>
```

---

## Manual Deployment

### Prerequisites for Manual Deployment

Authenticate with GCP:

```bash
gcloud auth login
gcloud config set project $PROJECT_ID
gcloud auth configure-docker
```

### Build and Push Container

```bash
# Tag for GCP
docker tag ks-simulator:local gcr.io/$PROJECT_ID/ks-simulator:latest

# Or for Artifact Registry
docker tag ks-simulator:local us-central1-docker.pkg.dev/$PROJECT_ID/ks-simulator/ks-simulator:latest

# Push to GCP
docker push gcr.io/$PROJECT_ID/ks-simulator:latest

# Or push to Artifact Registry
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ks-simulator/ks-simulator:latest
```

---

## Monitoring and Maintenance

### View Logs

#### Cloud Run
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ks-simulator" \
  --limit=50 \
  --format=json
```

Or via Console: Cloud Run → Select service → Logs tab

#### App Engine
```bash
gcloud app logs tail -s default
```

Or via Console: App Engine → Versions → Logs

#### Compute Engine
```bash
gcloud compute instances get-serial-port-output ks-simulator-vm \
  --zone=us-central1-a

# Or SSH and view logs
gcloud compute ssh ks-simulator-vm --zone=us-central1-a
docker logs $(docker ps -q)
```

### Monitor Performance

#### Cloud Run
- Go to Cloud Console → Cloud Run → Select service
- View metrics: Request count, latency, error rate, memory/CPU usage

#### App Engine
- Go to Cloud Console → App Engine → Dashboard
- View metrics: Requests, latency, memory, CPU

#### Compute Engine
- Go to Cloud Console → Compute Engine → VM instances
- Click on instance name → Monitoring tab

### Set Up Alerts

Create an alert policy:
```bash
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=0.1 \
  --condition-threshold-filter='resource.type="cloud_run_revision"'
```

### Update the Application

#### Cloud Run
```bash
# Build new image
docker build -t gcr.io/$PROJECT_ID/ks-simulator:v2 .
docker push gcr.io/$PROJECT_ID/ks-simulator:v2

# Deploy update
gcloud run deploy ks-simulator \
  --image=gcr.io/$PROJECT_ID/ks-simulator:v2 \
  --region=us-central1
```

#### App Engine
```bash
# Deploy new version
gcloud app deploy --version=v2

# Split traffic between versions
gcloud app services set-traffic default --splits=v1=0.5,v2=0.5
```

#### Compute Engine
```bash
# Update container
gcloud compute instances update-container ks-simulator-vm \
  --container-image=gcr.io/$PROJECT_ID/ks-simulator:v2 \
  --zone=us-central1-a
```

---

## Troubleshooting

### Common Issues

#### 1. Build Fails

**Error:** `unable to prepare context: unable to evaluate symlinks`
**Solution:** Check `.dockerignore` and ensure no broken symlinks exist

**Error:** `requirements.txt not found`
**Solution:** Ensure you're building from the repository root

#### 2. Container Fails to Start

Check logs:
```bash
# Cloud Run
gcloud run services logs read ks-simulator --region=us-central1

# Docker locally
docker logs <container-id>
```

Common causes:
- Port mismatch (ensure PORT=8080)
- Missing dependencies
- Application crashes on startup

#### 3. Permission Denied Errors

**Error:** `Permission denied` when pushing to Artifact Registry
**Solution:**
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
gcloud auth application-default login
```

#### 4. Service Unreachable

**Cloud Run:** Check IAM permissions - ensure `--allow-unauthenticated` is set

**Compute Engine:** 
```bash
# Check firewall rules
gcloud compute firewall-rules list

# Ensure tag is applied
gcloud compute instances describe ks-simulator-vm \
  --zone=us-central1-a \
  --format='get(tags.items)'
```

#### 5. Memory/CPU Issues

If the application is slow or crashes:

**Increase resources:**
```bash
# Cloud Run
gcloud run services update ks-simulator \
  --memory=4Gi \
  --cpu=4 \
  --region=us-central1

# App Engine: Edit app.yaml and redeploy
# Compute Engine: Change machine type
gcloud compute instances set-machine-type ks-simulator-vm \
  --machine-type=e2-standard-4 \
  --zone=us-central1-a
```

### Debug Checklist

1. ✅ Check logs for errors
2. ✅ Verify environment variables are set correctly
3. ✅ Ensure all required APIs are enabled
4. ✅ Check IAM permissions
5. ✅ Verify firewall rules (for Compute Engine)
6. ✅ Test Docker image locally first
7. ✅ Check resource limits (memory/CPU)

### Get Help

- **GCP Documentation:** https://cloud.google.com/docs
- **Cloud Run:** https://cloud.google.com/run/docs
- **App Engine:** https://cloud.google.com/appengine/docs
- **Compute Engine:** https://cloud.google.com/compute/docs
- **GitHub Actions:** https://docs.github.com/actions
- **Stack Overflow:** Tag questions with `google-cloud-platform`

---

## Cost Estimation

### Cloud Run (Pay-per-use)
- **Free tier:** 2 million requests/month
- **Pricing:** ~$0.40 per million requests + compute time
- **Estimated cost:** $5-20/month for moderate usage

### App Engine (Standard)
- **Free tier:** 28 instance hours/day
- **Pricing:** ~$0.05-0.10/hour per instance
- **Estimated cost:** $10-30/month

### Compute Engine
- **e2-standard-2:** ~$50/month (continuous)
- **e2-micro:** ~$7/month (free tier eligible)
- **Estimated cost:** $7-50/month depending on machine type

**Recommendation:** Start with Cloud Run for the best cost-to-performance ratio.

---

## Security Best Practices

1. **Use Workload Identity Federation** instead of service account keys
2. **Restrict service accounts** to minimum required permissions
3. **Enable Cloud Armor** for DDoS protection (Cloud Run/App Engine)
4. **Use Secret Manager** for sensitive configuration
5. **Enable HTTPS only** (automatic for Cloud Run/App Engine)
6. **Regular updates** - keep dependencies up to date
7. **Monitor logs** for suspicious activity
8. **Set up alerts** for anomalies

---

## Next Steps

1. Choose your deployment option (Cloud Run recommended)
2. Complete the GCP setup steps
3. Configure GitHub Actions secrets
4. Push to the `cloud-deploy` branch to trigger deployment
5. Monitor your application
6. Set up custom domain (optional)
7. Configure alerting and monitoring

**Happy Deploying! 🚀**
