#!/bin/bash
# Beast Mode GKE Deployment Script
# Systematic GKE cluster deployment with enterprise-grade configuration

set -euo pipefail

# Configuration
PROJECT_ID="${PROJECT_ID:-}"
CLUSTER_NAME="${CLUSTER_NAME:-beast-mode-cluster}"
REGION="${REGION:-us-central1}"
ENVIRONMENT="${ENVIRONMENT:-dev}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Show usage information
show_usage() {
    echo "Beast Mode GKE Deployment Script"
    echo ""
    echo "Usage:"
    echo "  PROJECT_ID=your-project ./deploy-gke.sh [command]"
    echo ""
    echo "Commands:"
    echo "  (none)    - Deploy using Terraform infrastructure"
    echo "  legacy    - Deploy using legacy gcloud commands"
    echo "  destroy   - Destroy the infrastructure"
    echo ""
    echo "Environment Variables:"
    echo "  PROJECT_ID     - GCP project ID (required)"
    echo "  CLUSTER_NAME   - Name of the cluster (default: beast-mode-cluster)"
    echo "  REGION         - GCP region (default: us-central1)"
    echo "  ENVIRONMENT    - Environment name (default: dev)"
}

# Check if this is a legacy deployment request
if [[ "${1:-}" == "legacy" ]]; then
    log_info "🚀 Deploying Beast Mode using legacy gcloud commands..."
    log_info "📋 Configuration:"
    log_info "   Project: $PROJECT_ID"
    log_info "   Cluster: $CLUSTER_NAME"
    log_info "   Region: $REGION"
    log_info "   Environment: $ENVIRONMENT"
    echo ""
else
    log_info "🚀 Beast Mode GKE deployment now uses Terraform!"
    log_info "📋 Please use the Terraform-based deployment:"
    log_info "   cd terraform"
    log_info "   terraform init"
    log_info "   terraform plan -var=\"project_id=$PROJECT_ID\""
    log_info "   terraform apply -var=\"project_id=$PROJECT_ID\""
    echo ""
    log_info "🔧 Or use the automated deployment script:"
    log_info "   PROJECT_ID=$PROJECT_ID ./deploy-gke.sh terraform"
    echo ""
    exit 0
fi

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

# Set the project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
    container.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    compute.googleapis.com \
    iam.googleapis.com

# Create GKE cluster if it doesn't exist
echo "🏗️  Creating/updating GKE cluster..."
if ! gcloud container clusters describe $CLUSTER_NAME --region=$REGION &>/dev/null; then
    echo "Creating new GKE cluster..."
    gcloud container clusters create $CLUSTER_NAME \
        --region=$REGION \
        --machine-type=e2-standard-4 \
        --num-nodes=1 \
        --min-nodes=1 \
        --max-nodes=5 \
        --enable-autoscaling \
        --enable-autorepair \
        --enable-autoupgrade \
        --enable-network-policy \
        --enable-ip-alias \
        --workload-pool=$PROJECT_ID.svc.id.goog \
        --addons=HorizontalPodAutoscaling,HttpLoadBalancing,NetworkPolicy \
        --release-channel=regular
else
    echo "GKE cluster already exists"
fi

# Get cluster credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Create service account for Workload Identity
echo "🔐 Setting up Workload Identity..."
gcloud iam service-accounts create systematic-pdca \
    --display-name="Systematic PDCA Orchestrator Service Account" || echo "Service account may already exist"

# Grant IAM permissions
echo "🛡️  Granting IAM permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:systematic-pdca@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:systematic-pdca@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/monitoring.metricWriter"

# Bind Kubernetes service account to Google service account
kubectl create namespace systematic-pdca || echo "Namespace may already exist"

kubectl create serviceaccount systematic-pdca-sa \
    --namespace systematic-pdca || echo "Service account may already exist"

gcloud iam service-accounts add-iam-policy-binding \
    systematic-pdca@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[systematic-pdca/systematic-pdca-sa]"

kubectl annotate serviceaccount systematic-pdca-sa \
    --namespace systematic-pdca \
    iam.gke.io/gcp-service-account=systematic-pdca@$PROJECT_ID.iam.gserviceaccount.com \
    --overwrite

# Build and push container image
echo "🏗️  Building and pushing container image..."
gcloud builds submit --config=deployment/systematic-pdca/cloudbuild.yaml .

# Reserve static IP for ingress
echo "🌐 Reserving static IP..."
gcloud compute addresses create systematic-pdca-ip --global || echo "IP may already exist"

# Deploy using kubectl
echo "📦 Deploying to Kubernetes..."
# Replace PROJECT_ID in manifests
sed "s/PROJECT_ID/$PROJECT_ID/g" deployment/gke/kubernetes-manifests.yaml > /tmp/k8s-manifests.yaml
sed -i "s/YOUR_DOMAIN.com/$DOMAIN/g" /tmp/k8s-manifests.yaml

kubectl apply -f /tmp/k8s-manifests.yaml

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/systematic-pdca-orchestrator -n systematic-pdca

# Get service information
echo "🔍 Getting service information..."
EXTERNAL_IP=$(gcloud compute addresses describe systematic-pdca-ip --global --format="value(address)")
SERVICE_URL="https://systematic-pdca.$DOMAIN"

echo ""
echo "🎉 GKE Deployment completed successfully!"
echo "================================================"
echo "Cluster: $CLUSTER_NAME"
echo "Namespace: systematic-pdca"
echo "External IP: $EXTERNAL_IP"
echo "Service URL: $SERVICE_URL"
echo ""
echo "🔍 Useful commands:"
echo "kubectl get pods -n systematic-pdca"
echo "kubectl logs -f deployment/systematic-pdca-orchestrator -n systematic-pdca"
echo "kubectl describe hpa systematic-pdca-hpa -n systematic-pdca"
echo ""
echo "🧪 Test the deployment:"
echo "curl https://systematic-pdca.$DOMAIN/health"
echo ""
echo "📊 Monitor with:"
echo "kubectl top pods -n systematic-pdca"
echo "kubectl get hpa -n systematic-pdca"
echo ""
echo "🎯 Systematic PDCA Orchestrator is now running on GKE with:"
echo "  ✅ High availability (3 replicas)"
echo "  ✅ Auto-scaling (2-10 pods)"
echo "  ✅ Load balancing (Google Cloud Load Balancer)"
echo "  ✅ SSL termination (Managed certificates)"
echo "  ✅ Network policies (Security)"
echo "  ✅ Workload Identity (GCP integration)"

# Clean up temp file
rm -f /tmp/k8s-manifests.yaml