#!/bin/bash
# Start Beast Mode Pub/Sub Infrastructure

set -e

echo "🧬 Starting Beast Mode Pub/Sub Infrastructure"
echo "============================================="

# Create necessary directories
mkdir -p logs config

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start services
echo "🔧 Building and starting services..."
docker-compose -f docker-compose.pubsub.yml up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose -f docker-compose.pubsub.yml ps

# Test Redis connection
echo "🧪 Testing Redis connection..."
if docker exec beast-mode-redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis health check failed"
    exit 1
fi

echo ""
echo "🎉 Beast Mode Pub/Sub Infrastructure Started!"
echo "============================================="
echo "📊 Redis UI: http://localhost:8081"
echo "🔌 API: http://localhost:8000"
echo "📡 Redis: localhost:6379"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose -f docker-compose.pubsub.yml logs -f"
echo "  Stop: docker-compose -f docker-compose.pubsub.yml down"
echo "  Restart: docker-compose -f docker-compose.pubsub.yml restart"
echo ""
echo "🧬 Ready for Beast Mode systematic excellence!"