#!/bin/bash
# Deploy Ghostbusters API Container to GCP Cloud Run

set -e

echo "🚀 Deploying Ghostbusters API Container to GCP Cloud Run"
echo "========================================================"

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"aardvark-linkedin-grepper"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="ghostbusters-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "📋 Configuration:"
echo "  Project ID: "PROJECT_I"D"
echo "  Region: "REGIO"N"
echo "  Service Name: "SERVICE_NAM"E"
echo "  Image Name: "IMAGE_NAM"E"

# Check if gcloud CLI is available
if ! command -v gcloud &>/dev/null; then
	echo "❌ gcloud CLI not found. Please install Google Cloud SDK first."
	exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
	echo "❌ Not authenticated with gcloud"
	echo "Please run: gcloud auth login"
	exit 1
fi

echo "✅ gcloud CLI available and authenticated"

# Build and push Docker image
echo ""
echo "🔧 Building Docker image..."
cd src/ghostbusters_api

# Build the image
gcloud builds submit --tag ""IMAGE_NAM"E" --project=""PROJECT_I"D" .

# Deploy to Cloud Run
echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ""SERVICE_NAM"E" \
	--image=""IMAGE_NAM"E" \
	--platform=managed \
	--region=""REGIO"N" \
	--project=""PROJECT_I"D" \
	--allow-unauthenticated \
	--memory=2Gi \
	--cpu=2 \
	--concurrency=80 \
	--max-instances=10 \
	--timeout=900 \
	--set-env-vars="PROJECT_ID="PROJECT_I"D" \
	--service-account="1077539189076-compute@developer.gserviceaccount.com"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ""SERVICE_NAM"E" --region=""REGIO"N" \
	--project="$PROJECT_ID" --format="value(status.url)")

echo ""
echo "✅ Ghostbusters API Container deployed successfully!"
echo ""
echo "📋 Service URL: "SERVICE_UR"L"
echo ""
echo "🔧 Usage Examples:"
echo "  # Queue analysis"
echo "  curl -X POST "SERVICE_URL"/analyze \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"project_path\": \".\", \"agents\": [\"security\", \"code_quality\"]}'"
echo ""
echo "  # Check status"
echo "  curl "SERVICE_URL"/status/YOUR_JOB_ID"
echo ""
echo "  # List jobs"
echo "  curl "SERVICE_URL"/jobs"
echo ""
echo "  # Health check"
echo "  curl "SERVICE_URL"/health"
echo ""
echo "🎯 Performance Benefits:"
echo "  ✅ Warm start: <1 second"
echo "  ✅ More memory: 2GB"
echo "  ✅ More CPU: 2 vCPUs"
echo "  ✅ Persistent state"
echo "  ✅ API key caching"
echo "  ✅ Background processing"
