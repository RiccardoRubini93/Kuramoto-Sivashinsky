#!/bin/bash

# GCP Setup Script for KS Simulator
# This script automates the initial GCP setup process

set -e

echo "=================================================="
echo "KS Simulator - GCP Setup Script"
echo "=================================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud CLI is installed"
echo ""

# Get project ID
read -p "Enter your GCP Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID cannot be empty"
    exit 1
fi

echo ""
echo "Setting project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# Get project number
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
echo "Project Number: $PROJECT_NUMBER"
echo ""

# Enable required APIs
echo "=================================================="
echo "Step 1: Enabling Required APIs"
echo "=================================================="
echo ""

APIs=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
    "compute.googleapis.com"
    "appengine.googleapis.com"
    "iamcredentials.googleapis.com"
)

for api in "${APIs[@]}"; do
    echo "Enabling $api..."
    gcloud services enable "$api" --project="$PROJECT_ID"
done

echo ""
echo "✅ All APIs enabled"
echo ""

# Create Artifact Registry repository
echo "=================================================="
echo "Step 2: Creating Artifact Registry Repository"
echo "=================================================="
echo ""

REGION="us-central1"
REPO_NAME="ks-simulator"

if gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID" &> /dev/null; then
    echo "ℹ️  Repository already exists"
else
    echo "Creating Artifact Registry repository..."
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="KS Simulator Docker images" \
        --project="$PROJECT_ID"
    echo "✅ Repository created"
fi

echo ""

# Create Workload Identity Pool
echo "=================================================="
echo "Step 3: Setting up Workload Identity Federation"
echo "=================================================="
echo ""

POOL_NAME="github-pool"
PROVIDER_NAME="github-provider"

read -p "Enter your GitHub repository (format: owner/repo): " GITHUB_REPO

if [ -z "$GITHUB_REPO" ]; then
    echo "❌ Error: GitHub repository cannot be empty"
    exit 1
fi

# Create pool
if gcloud iam workload-identity-pools describe "$POOL_NAME" --location=global --project="$PROJECT_ID" &> /dev/null; then
    echo "ℹ️  Workload Identity Pool already exists"
else
    echo "Creating Workload Identity Pool..."
    gcloud iam workload-identity-pools create "$POOL_NAME" \
        --project="$PROJECT_ID" \
        --location=global \
        --display-name="GitHub Actions Pool"
    echo "✅ Pool created"
fi

echo ""

# Create provider
if gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
    --workload-identity-pool=$POOL_NAME \
    --location=global \
    --project=$PROJECT_ID &> /dev/null; then
    echo "ℹ️  Workload Identity Provider already exists"
else
    echo "Creating Workload Identity Provider..."
    gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
        --project=$PROJECT_ID \
        --location=global \
        --workload-identity-pool=$POOL_NAME \
        --display-name="GitHub provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
        --issuer-uri="https://token.actions.githubusercontent.com"
    echo "✅ Provider created"
fi

echo ""

# Create Service Account
echo "=================================================="
echo "Step 4: Creating Service Account"
echo "=================================================="
echo ""

SA_NAME="github-actions-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe "$SA_EMAIL" --project=$PROJECT_ID &> /dev/null; then
    echo "ℹ️  Service account already exists"
else
    echo "Creating service account..."
    gcloud iam service-accounts create "$SA_NAME" \
        --project=$PROJECT_ID \
        --display-name="GitHub Actions Service Account"
    echo "✅ Service account created"
fi

echo ""

# Grant permissions
echo "=================================================="
echo "Step 5: Granting Permissions"
echo "=================================================="
echo ""

ROLES=(
    "roles/run.admin"
    "roles/storage.admin"
    "roles/artifactregistry.writer"
    "roles/iam.serviceAccountUser"
    "roles/appengine.appAdmin"
    "roles/compute.admin"
)

for role in "${ROLES[@]}"; do
    echo "Granting $role..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="$role" \
        --condition=None \
        --quiet
done

echo ""
echo "✅ Permissions granted"
echo ""

# Allow GitHub Actions to impersonate service account
echo "=================================================="
echo "Step 6: Configuring Workload Identity"
echo "=================================================="
echo ""

WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools describe "$POOL_NAME" \
    --project=$PROJECT_ID \
    --location=global \
    --format="value(name)")

echo "Allowing GitHub Actions to impersonate service account..."
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
    --project=$PROJECT_ID \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${GITHUB_REPO}"

echo "✅ Workload Identity configured"
echo ""

# Get provider resource name
PROVIDER_RESOURCE=$(gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
    --project=$PROJECT_ID \
    --location=global \
    --workload-identity-pool=$POOL_NAME \
    --format="value(name)")

# Summary
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "📝 Add the following secrets to your GitHub repository:"
echo ""
echo "1. Go to: https://github.com/${GITHUB_REPO}/settings/secrets/actions"
echo "2. Click 'New repository secret' and add:"
echo ""
echo "   Secret Name: GCP_PROJECT_ID"
echo "   Value: ${PROJECT_ID}"
echo ""
echo "   Secret Name: WIF_PROVIDER"
echo "   Value: ${PROVIDER_RESOURCE}"
echo ""
echo "   Secret Name: WIF_SERVICE_ACCOUNT"
echo "   Value: ${SA_EMAIL}"
echo ""
echo "=================================================="
echo "🚀 You're ready to deploy!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Add the secrets above to your GitHub repository"
echo "2. Push to the 'cloud-deploy' branch"
echo "3. GitHub Actions will automatically deploy to Cloud Run"
echo ""
echo "For manual deployment, see: CLOUD_DEPLOYMENT.md"
echo ""
