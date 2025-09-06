#!/bin/bash
# Systematic PDCA Orchestrator - Helm Deployment to GKE

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
CLUSTER_NAME=${2:-"systematic-pdca-cluster"}
REGION=${3:-"us-central1"}
DOMAIN=${4:-"YOUR_DOMAIN.com"}
RELEASE_NAME=${5:-"systematic-pdca"}

echo "🚀 Deploying Systematic PDCA Orchestrator to GKE with Helm"
echo "Project: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Domain: $DOMAIN"
echo "Release: $RELEASE_NAME"
echo "======================================================="

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm not found. Installing Helm..."
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

# Set the project and get cluster credentials
echo "📋 Setting up cluster access..."
gcloud config set project $PROJECT_ID
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Create namespace
echo "📦 Creating namespace..."
kubectl create namespace systematic-pdca || echo "Namespace may already exist"

# Update Helm values with project-specific settings
echo "🔧 Updating Helm values..."
sed "s/PROJECT_ID/$PROJECT_ID/g" deployment/gke/helm-chart/values.yaml > /tmp/values.yaml
sed -i "s/YOUR_DOMAIN.com/$DOMAIN/g" /tmp/values.yaml

# Build and push container image
echo "🏗️  Building container image..."
gcloud builds submit --config=deployment/systematic-pdca/cloudbuild.yaml .

# Reserve static IP
echo "🌐 Reserving static IP..."
gcloud compute addresses create systematic-pdca-ip --global || echo "IP may already exist"

# Deploy with Helm
echo "📦 Deploying with Helm..."
helm upgrade --install $RELEASE_NAME deployment/gke/helm-chart \
    --namespace systematic-pdca \
    --values /tmp/values.yaml \
    --set image.repository=gcr.io/$PROJECT_ID/systematic-pdca-orchestrator \
    --set serviceAccount.annotations."iam\.gke\.io/gcp-service-account"=systematic-pdca@$PROJECT_ID.iam.gserviceaccount.com \
    --set ingress.hosts[0].host=systematic-pdca.$DOMAIN \
    --wait --timeout=10m

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/$RELEASE_NAME-systematic-pdca-orchestrator -n systematic-pdca

# Get service information
EXTERNAL_IP=$(gcloud compute addresses describe systematic-pdca-ip --global --format="value(address)")
SERVICE_URL="https://systematic-pdca.$DOMAIN"

echo ""
echo "🎉 Helm Deployment completed successfully!"
echo "======================================================="
echo "Release: $RELEASE_NAME"
echo "Namespace: systematic-pdca"
echo "External IP: $EXTERNAL_IP"
echo "Service URL: $SERVICE_URL"
echo ""
echo "🔍 Helm commands:"
echo "helm status $RELEASE_NAME -n systematic-pdca"
echo "helm get values $RELEASE_NAME -n systematic-pdca"
echo "helm rollback $RELEASE_NAME -n systematic-pdca"
echo ""
echo "🧪 Test the deployment:"
echo "curl https://systematic-pdca.$DOMAIN/health"
echo ""
echo "🔧 Update deployment:"
echo "helm upgrade $RELEASE_NAME deployment/gke/helm-chart -n systematic-pdca --values /tmp/values.yaml"

# Clean up temp file
rm -f /tmp/values.yaml