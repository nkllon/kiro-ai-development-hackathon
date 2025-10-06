#!/bin/bash
set -e

echo "🚀 Deploying Beast Mode Monitoring Daemon to Vonnegut..."

# Configuration
VONNEGUT_HOST="vonnegut"
DEPLOY_DIR="/home/lou/beast-mode/monitoring-daemon"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "📦 Creating deployment package..."
cd "$PROJECT_ROOT"

# Create temporary deployment directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy necessary files
cp -r deployment/monitoring-daemon "$TEMP_DIR/"
cp -r src "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"

echo "📤 Transferring files to vonnegut..."
ssh "$VONNEGUT_HOST" "mkdir -p $DEPLOY_DIR"
rsync -avz --delete "$TEMP_DIR/" "$VONNEGUT_HOST:$DEPLOY_DIR/"

echo "🐳 Building and starting Docker container on vonnegut..."
ssh "$VONNEGUT_HOST" << 'EOF'
cd /home/lou/beast-mode/monitoring-daemon/monitoring-daemon
docker-compose down || true
docker-compose build
docker-compose up -d
docker-compose ps
EOF

echo "✅ Monitoring daemon deployed!"
echo ""
echo "📊 Metrics endpoint: http://vonnegut:8000/metrics"
echo ""
echo "To view logs:"
echo "  ssh vonnegut 'cd /home/lou/beast-mode/monitoring-daemon/monitoring-daemon && docker-compose logs -f'"
echo ""
echo "To check status:"
echo "  ssh vonnegut 'cd /home/lou/beast-mode/monitoring-daemon/monitoring-daemon && docker-compose ps'"
