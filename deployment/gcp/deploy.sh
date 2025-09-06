#!/bin/bash
# Research CMA System - One-Click GCP Deployment Script

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
ENVIRONMENT=${3:-"dev"}

echo "🚀 Deploying Research CMA System to GCP"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Environment: $ENVIRONMENT"
echo "=================================="

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set the project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    iam.googleapis.com

# Deploy infrastructure with Terraform (optional)
if command -v terraform &> /dev/null; then
    echo "🏗️  Deploying infrastructure with Terraform..."
    cd deployment/gcp/terraform
    
    terraform init
    terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="environment=$ENVIRONMENT"
    terraform apply -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="environment=$ENVIRONMENT"
    
    cd ../../..
else
    echo "⚠️  Terraform not found. Deploying with gcloud commands..."
    
    # Create Cloud SQL instance
    echo "🗄️  Creating Cloud SQL instance..."
    gcloud sql instances create research-cms-db-$ENVIRONMENT \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=$REGION \
        --backup-start-time=03:00 \
        --enable-bin-log \
        --storage-auto-increase || echo "Database instance may already exist"
    
    # Create database
    echo "📊 Creating database..."
    gcloud sql databases create research_cms \
        --instance=research-cms-db-$ENVIRONMENT || echo "Database may already exist"
    
    # Create database user
    echo "👤 Creating database user..."
    DB_PASSWORD=$(openssl rand -base64 32)
    gcloud sql users create research_cms \
        --instance=research-cms-db-$ENVIRONMENT \
        --password=$DB_PASSWORD || echo "User may already exist"
    
    # Store password in Secret Manager
    echo "🔐 Storing database password..."
    echo -n $DB_PASSWORD | gcloud secrets create research-cms-db-password --data-file=- || \
    echo -n $DB_PASSWORD | gcloud secrets versions add research-cms-db-password --data-file=-
    
    # Create storage bucket
    echo "🪣 Creating storage bucket..."
    gsutil mb gs://$PROJECT_ID-research-cms-documents-$ENVIRONMENT || echo "Bucket may already exist"
    
    # Create service account
    echo "🔑 Creating service account..."
    gcloud iam service-accounts create research-cms-$ENVIRONMENT \
        --display-name="Research CMS Service Account" || echo "Service account may already exist"
    
    # Grant IAM permissions
    echo "🛡️  Granting IAM permissions..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:research-cms-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/cloudsql.client"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:research-cms-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/storage.objectAdmin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:research-cms-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
fi

# Build and deploy the application
echo "🏗️  Building and deploying application..."
gcloud builds submit --config=deployment/gcp/cloudbuild.yaml .

# Get the service URL
SERVICE_URL=$(gcloud run services describe research-cms --region=$REGION --format="value(status.url)")

echo ""
echo "🎉 Deployment completed successfully!"
echo "=================================="
echo "Service URL: $SERVICE_URL"
echo "Database: research-cms-db-$ENVIRONMENT"
echo "Storage: gs://$PROJECT_ID-research-cms-documents-$ENVIRONMENT"
echo ""
echo "🔍 To monitor your deployment:"
echo "gcloud run services describe research-cms --region=$REGION"
echo ""
echo "📊 To view logs:"
echo "gcloud logs tail --follow --resource-type=cloud_run_revision --resource-labels=service_name=research-cms"
echo ""
echo "💰 To monitor costs:"
echo "Visit: https://console.cloud.google.com/billing/reports"