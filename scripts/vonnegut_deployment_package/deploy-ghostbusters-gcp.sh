#!/bin/bash
# Deploy Ghostbusters to GCP Cloud Functions

set -e

echo "🚀 Deploying Ghostbusters to GCP Cloud Functions..."

# Check if gcloud is installed
if ! command -v gcloud &>/dev/null; then
	echo "❌ gcloud CLI not found. Please install Google Cloud SDK first."
	echo "Visit: https://cloud.google.com/sdk/docs/install"
	exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
	echo "❌ Not authenticated with gcloud. Please run: gcloud auth login"
	exit 1
fi

# Set project ID (you can override this with environment variable)
PROJECT_ID=${GCP_PROJECT_ID:-"ghostbusters-project"}
REGION=${GCP_REGION:-"us-central1"}

echo "📋 Configuration:"
echo "  Project ID: "PROJECT_I"D"
echo "  Region: "REGIO"N"
echo "  Source: src/ghostbusters_gcp"

# Deploy main analysis function
echo "📦 Deploying ghostbusters-analyze function..."
gcloud functions deploy ghostbusters-analyze \
	--project=""PROJECT_I"D" \
	--region=""REGIO"N" \
	--runtime=python311 \
	--trigger=http \
	--memory=2048MB \
	--timeout=540s \
	--max-instances=10 \
	--source=src/ghostbusters_gcp \
	--entry-point=ghostbusters_analyze \
	--allow-unauthenticated \
	--set-env-vars="PROJECT_ID="PROJECT_ID",ENVIRONMENT=production,LOG_LEVEL=INFO"

# Deploy status check function
echo "📦 Deploying ghostbusters-status function..."
gcloud functions deploy ghostbusters-status \
	--project=""PROJECT_I"D" \
	--region=""REGIO"N" \
	--runtime=python311 \
	--trigger=http \
	--memory=512MB \
	--timeout=60s \
	--max-instances=20 \
	--source=src/ghostbusters_gcp \
	--entry-point=ghostbusters_status \
	--allow-unauthenticated \
	--set-env-vars="PROJECT_ID="PROJECT_ID",ENVIRONMENT=production,LOG_LEVEL=INFO"

# Deploy history function
echo "📦 Deploying ghostbusters-history function..."
gcloud functions deploy ghostbusters-history \
	--project=""PROJECT_I"D" \
	--region=""REGIO"N" \
	--runtime=python311 \
	--trigger=http \
	--memory=512MB \
	--timeout=60s \
	--max-instances=20 \
	--source=src/ghostbusters_gcp \
	--entry-point=ghostbusters_history \
	--allow-unauthenticated \
	--set-env-vars="PROJECT_ID="PROJECT_ID",ENVIRONMENT=production,LOG_LEVEL=INFO"

# Deploy enhanced analysis function (Phase 2)
echo "📦 Deploying ghostbusters-analyze-enhanced function..."
gcloud functions deploy ghostbusters-analyze-enhanced \
	--project=""PROJECT_I"D" \
	--region=""REGIO"N" \
	--runtime=python311 \
	--trigger=http \
	--memory=4096MB \
	--timeout=540s \
	--max-instances=5 \
	--source=src/ghostbusters_gcp \
	--entry-point=ghostbusters_analyze_enhanced \
	--allow-unauthenticated \
	--set-env-vars="PROJECT_ID="PROJECT_ID",ENVIRONMENT=production,LOG_LEVEL=INFO"

# Deploy progress tracking function (Phase 2)
echo "📦 Deploying ghostbusters-progress function..."
gcloud functions deploy ghostbusters-progress \
	--project=""PROJECT_I"D" \
	--region=""REGIO"N" \
	--runtime=python311 \
	--trigger=http \
	--memory=512MB \
	--timeout=60s \
	--max-instances=20 \
	--source=src/ghostbusters_gcp \
	--entry-point=ghostbusters_progress \
	--allow-unauthenticated \
	--set-env-vars="PROJECT_ID="PROJECT_ID",ENVIRONMENT=production,LOG_LEVEL=INFO"

# Deploy user analyses function (Phase 2)
echo "📦 Deploying ghostbusters-user-analyses function..."
gcloud functions deploy ghostbusters-user-analyses \
	--project=""PROJECT_I"D" \
	--region=""REGIO"N" \
	--runtime=python311 \
	--trigger=http \
	--memory=512MB \
	--timeout=60s \
	--max-instances=20 \
	--source=src/ghostbusters_gcp \
	--entry-point=ghostbusters_user_analyses \
	--allow-unauthenticated \
	--set-env-vars="PROJECT_ID="PROJECT_ID",ENVIRONMENT=production,LOG_LEVEL=INFO"

echo "✅ Ghostbusters Phase 1 & 2 deployed successfully!"
echo ""
echo "📊 Function URLs:"
echo "  Analysis: https://"REGION"-"PROJECT_ID".cloudfunctions.net/ghostbusters-analyze"
echo "  Status: https://"REGION"-"PROJECT_ID".cloudfunctions.net/ghostbusters-status"
echo "  History: https://"REGION"-"PROJECT_ID".cloudfunctions.net/ghostbusters-history"
echo " Enhanced Analysis:
https://"REGION"-"PROJECT_ID".cloudfunctions.net/ghostbusters-analyze-enhanced"
echo " Progress:
https://"REGION"-"PROJECT_ID".cloudfunctions.net/ghostbusters-progress"
echo " User Analyses:
https://"REGION"-"PROJECT_ID".cloudfunctions.net/ghostbusters-user-analyses"
echo ""
echo "🧪 Test with:"
echo " curl -X POST
https://"REGION"-"PROJECT_ID".cloudfunctions.net/ghostbusters-analyze-enhanced \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -H 'Authorization: Bearer YOUR_FIREBASE_TOKEN' \\"
echo "    -d '{\"project_path\": \".\"}'"
