#!/bin/bash
# Start Monitoring Stack
# =====================
# 
# Starts Prometheus + Grafana + Beast Mode metrics using Docker Compose.
# Proper Docker networking, no host networking issues.

set -e

echo "🚀 Starting Beast Mode Monitoring Stack"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to deployment directory
cd deployment/local

echo "🔄 Starting monitoring services..."

# Start the monitoring profile
docker-compose --profile monitoring up -d

echo "✅ Monitoring stack started!"
echo ""
echo "📊 Services available:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana:    http://localhost:3000 (admin/systematic)"
echo "   Beast Mode Metrics: http://localhost:8000/metrics"
echo ""
echo "🔍 Check status:"
echo "   docker-compose --profile monitoring ps"
echo ""
echo "📋 View logs:"
echo "   docker-compose --profile monitoring logs -f"
echo ""
echo "🛑 Stop monitoring:"
echo "   ./scripts/stop-monitoring.sh"