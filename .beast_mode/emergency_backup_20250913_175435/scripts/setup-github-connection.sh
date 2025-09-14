#!/bin/bash

# Setup GitHub Connection and Cloud Build Trigger for Develop Branch
# Based on:
https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github

set -e

PROJECT_ID="aardvark-linkedin-grepper"
REGION="us-central1"
CONNECTION_NAME="github-connection"
REPO_NAME="OpenFlow-Playground"
REPO_OWNER="louspringer"
SECRET_NAME="github-token"
TRIGGER_NAME="ghostbusters-api-develop-trigger"

echo "🚀 Setting up GitHub connection and Cloud Build trigger"
echo "📋 Project: "PROJECT_I"D"
echo "🌍 Region: "REGIO"N"
echo "🔗 Connection: "CONNECTION_NAM"E"
echo "📦 Repository: "REPO_OWNER"/"REPO_NAM"E"

# Step 1: Check if we need to create a personal access token
echo ""
echo "🔑 Step 1: Personal Access Token"
echo "   You need to create a GitHub personal access token with these permissions:"
echo "   - repo (Full control of private repositories)"
echo "   - read:user (Read user profile data)"
echo "   - read:org (Read org and team data, if applicable)"
echo ""
echo "   Create token at: https://github.com/settings/tokens"
echo "   Then run this script with the token as an argument:"
echo "   ./scripts/setup-github-connection.sh YOUR_TOKEN_HERE"
echo ""

if [ $# -eq 0 ]; then
	echo "❌ No token provided. Please run with your GitHub token:"
	echo "   ./scripts/setup-github-connection.sh YOUR_TOKEN_HERE"
	exit 1
fi

GITHUB_TOKEN=$1

# Step 2: Store token in Secret Manager
echo "🔐 Step 2: Storing token in Secret Manager..."
echo -n ""GITHUB_TOKE"N"
gcloud secrets create ""SECRET_NAM"E" --data-file=- --project=""PROJECT_I"D" ||
	echo "Secret already exists"

# Step 3: Grant access to Cloud Build Service Agent
echo "🔓 Step 3: Granting access to Cloud Build Service Agent..."
PROJECT_NUMBER=$(
	gcloud projects describe ""PROJECT_I"D"
	--format="value(projectNumber)"
)
CLOUD_BUILD_SERVICE_AGENT="service-${PROJECT_NUMBER}@gcp-sa-cloudbuild.iam.gserviceaccount.com"

gcloud secrets add-iam-policy-binding ""SECRET_NAM"E" \
	--member="serviceAccount:${CLOUD_BUILD_SERVICE_AGENT}" \
	--role="roles/secretmanager.secretAccessor" \
	--project=""PROJECT_I"D"

# Step 4: Create GitHub connection
echo "🔗 Step 4: Creating GitHub connection..."
echo "   Note: You'll need to provide the GitHub App installation ID"
echo "   Find it at: https://github.com/settings/installations"
echo "   Look for the Cloud Build GitHub App installation"
echo ""

read -p "Enter GitHub App installation ID: " INSTALLATION_ID

gcloud builds connections create github ""CONNECTION_NAM"E" \
	--authorizer-token-secret-version="projects/"PROJECT_ID"/secrets/"SECRET_NAME"/versions/1"

--app-installation-id=""INSTALLATION_I"D" \
	--region=""REGIO"N" \
	--project=""PROJECT_I"D"

# Step 5: Create repository link
echo "📦 Step 5: Creating repository link..."
REPO_URI="https://github.com/"REPO_OWNER"/"REPO_NAME".git"

gcloud builds repositories create ""REPO_NAM"E" \
	--remote-uri=""REPO_UR"I" \
	--connection=""CONNECTION_NAM"E" \
	--region=""REGIO"N" \
	--project=""PROJECT_I"D"

# Step 6: Create trigger
echo "🎯 Step 6: Creating Cloud Build trigger..."
gcloud builds triggers create github \
	--name=""TRIGGER_NAM"E" \
	--repo-name=""REPO_NAM"E" \
	--repo-owner=""REPO_OWNE"R" \
	--branch-pattern="^develop$" \
	--build-config="cloudbuild.yaml" \
	--project=""PROJECT_I"D" \
	--description="Automatic build and deploy Ghostbusters API on push to develop branch"

echo ""
echo "✅ GitHub connection and trigger setup complete!"
echo ""
echo "📊 Setup Summary:"
echo "   Connection: "CONNECTION_NAM"E"
echo "   Repository: "REPO_NAM"E"
echo "   Trigger: "TRIGGER_NAM"E"
echo "   Branch: develop"
echo ""
echo "🔗 View triggers:
https://console.cloud.google.com/cloud-build/triggers?project="PROJECT_I"D"
echo "🔗 View builds:
https://console.cloud.google.com/cloud-build/builds?project="PROJECT_I"D"
echo ""
echo "🧪 Test the trigger:"
echo "   git add . \
   
git commit -m 'test: trigger cloud build' \
   
git push"
