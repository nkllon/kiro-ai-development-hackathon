#!/bin/bash
# Deploy Node B to Vonnegut Docker
# Usage: ./deploy_to_vonnegut.sh

set -e

VONNEGUT_HOST="192.168.1.119"
DEPLOY_DIR="/tmp/beast_mode_deploy"

echo "🚀 Deploying Node B to Vonnegut Docker..."

# Create deployment directory
mkdir -p $DEPLOY_DIR

# Copy files
cp node_b_container.py $DEPLOY_DIR/
cp docker-compose.yml $DEPLOY_DIR/

echo "📦 Files prepared for deployment"

# Note: Actual deployment would require SSH access to Vonnegut
echo "📋 To complete deployment on Vonnegut:"
echo "1. Copy $DEPLOY_DIR/* to Vonnegut server"
echo "2. SSH to 192.168.1.119"
echo "3. Run: docker-compose up -d"
echo "4. Monitor: docker logs -f node-b-vonnegut"

echo "✅ Deployment package ready"
