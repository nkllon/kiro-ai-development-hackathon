#!/bin/bash
# Observatory Deployment Script for Poe
# Run this script on the Poe server

set -e

echo "🚀 Observatory Deployment on Poe"
echo "================================"

# Extract deployment package
echo "📦 Extracting deployment package..."
tar -xzf observatory-poe-deployment-20251004_152642.tar.gz
cd poe_deployment_*/

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Setup Docker containers
echo "🐳 Starting Docker containers..."
docker-compose -f deployment/observatory/docker-compose.yml up -d redis prometheus grafana

# Wait for containers to be ready
echo "⏳ Waiting for containers to start..."
sleep 30

# Setup data persistence
echo "💾 Setting up data persistence..."
python setup_data_persistence.py

# Start Observatory
echo "🌟 Starting Observatory..."
nohup python start_observatory.py > observatory.log 2>&1 &

# Wait for Observatory to start
echo "⏳ Waiting for Observatory to start..."
sleep 15

# Validate deployment
echo "✅ Validating deployment..."
python validate_observatory_deployment.py

echo "🎉 Observatory deployed successfully on Poe!"
echo "🌐 Local access: http://localhost:8888"
echo "📊 Grafana: http://localhost:3000"
echo "📈 Prometheus: http://localhost:9090"
