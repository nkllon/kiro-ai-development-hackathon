#!/bin/bash
# Stop Monitoring Stack
# ====================
# 
# Stops Prometheus + Grafana + Beast Mode metrics cleanly.

set -e

echo "🛑 Stopping Beast Mode Monitoring Stack"
echo "======================================="

cd deployment/local

echo "🔄 Stopping monitoring services..."
docker-compose --profile monitoring down

echo "✅ Monitoring stack stopped!"
echo ""
echo "💾 Data preserved in Docker volumes:"
echo "   - prometheus-data"
echo "   - grafana-storage"
echo ""
echo "🗑️  To remove all data:"
echo "   docker-compose --profile monitoring down -v"