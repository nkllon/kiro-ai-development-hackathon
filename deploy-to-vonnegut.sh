#!/bin/bash

# Observatory HA Deployment Script for vonnegut
set -e

HOST="lou@vonnegut"
REMOTE_DIR="/home/lou/observatory-ha"
LOCAL_DIR="."

echo "🚀 Deploying Observatory to vonnegut for HA setup..."

# Create remote directory
echo "📁 Creating remote directory..."
ssh $HOST "mkdir -p $REMOTE_DIR"

# Copy application files
echo "📦 Copying application files..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    $LOCAL_DIR/src/ $HOST:$REMOTE_DIR/src/

# Copy configuration and data
echo "⚙️ Copying configuration..."
rsync -avz $LOCAL_DIR/.kiro/ $HOST:$REMOTE_DIR/.kiro/
rsync -avz $LOCAL_DIR/data/ $HOST:$REMOTE_DIR/data/ || echo "No data directory to sync"

# Copy Docker files
echo "🐳 Copying Docker configuration..."
scp Dockerfile docker-compose.yml requirements.txt $HOST:$REMOTE_DIR/

# Create logs directory
ssh $HOST "mkdir -p $REMOTE_DIR/logs"

# Build and start the container
echo "🔨 Building Docker image on vonnegut..."
ssh $HOST "cd $REMOTE_DIR && docker-compose build"

echo "🚀 Starting Observatory container..."
ssh $HOST "cd $REMOTE_DIR && docker-compose up -d"

# Wait for health check
echo "🏥 Waiting for health check..."
sleep 10

# Test the deployment
echo "🧪 Testing deployment..."
HEALTH_CHECK=$(ssh $HOST "curl -s http://localhost:8888/health | jq -r '.status' 2>/dev/null || echo 'failed'")

if [ "$HEALTH_CHECK" = "healthy" ]; then
    echo "✅ Observatory deployed successfully on vonnegut!"
    echo "🌐 Access it at: http://192.168.1.146:8888"
    
    # Show container status
    echo "📊 Container status:"
    ssh $HOST "cd $REMOTE_DIR && docker-compose ps"
    
    echo ""
    echo "🎯 Next steps:"
    echo "1. Set up Cloudflare tunnel on vonnegut for public access"
    echo "2. Configure load balancing between Mac and Linux instances"
    echo "3. Set up monitoring and alerting"
    
else
    echo "❌ Deployment failed - health check returned: $HEALTH_CHECK"
    echo "📋 Container logs:"
    ssh $HOST "cd $REMOTE_DIR && docker-compose logs --tail=20"
    exit 1
fi