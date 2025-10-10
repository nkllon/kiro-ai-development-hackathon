#!/bin/bash

# Directus Beast Mode Integration Startup Script
# Modern, fixed version that resolves network conflicts and Docker issues

set -e

echo "🚀 Starting Directus Beast Mode Integration..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available (try both docker-compose and docker compose)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose > /dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "❌ Neither docker-compose nor 'docker compose' is available."
    echo "   Please install Docker Compose or use Docker Desktop with Compose V2."
    exit 1
fi

echo "📋 Using Docker Compose command: $DOCKER_COMPOSE_CMD"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p directus/snapshots
mkdir -p directus/uploads
mkdir -p directus/extensions

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating environment configuration..."
    cp .env.directus .env
    echo "✅ Environment file created. Please review .env and update passwords for production use."
else
    echo "📋 Using existing .env file"
fi

# Clean up any existing conflicting networks
echo "🧹 Cleaning up potential network conflicts..."
docker network ls --format "table {{.Name}}" | grep -E "(directus|beast.*mode)" | while read network; do
    if [ "$network" != "NAME" ] && [ "$network" != "beast_mode_directus_network" ]; then
        echo "   Removing conflicting network: $network"
        docker network rm "$network" 2>/dev/null || true
    fi
done

# Stop any existing Directus containers that might conflict
echo "🛑 Stopping any existing Directus containers..."
docker ps -a --format "table {{.Names}}" | grep -E "(directus|beast.*mode)" | while read container; do
    if [ "$container" != "NAMES" ] && [[ "$container" != *"_fixed" ]]; then
        echo "   Stopping conflicting container: $container"
        docker stop "$container" 2>/dev/null || true
        docker rm "$container" 2>/dev/null || true
    fi
done

# Start the services
echo "🐳 Starting Directus Beast Mode services..."
$DOCKER_COMPOSE_CMD -f docker-compose.directus-fixed.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
timeout=300  # 5 minutes timeout
counter=0

while [ $counter -lt $timeout ]; do
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "directus.*healthy" > /dev/null; then
        echo "✅ Directus is healthy and ready!"
        break
    fi
    
    if [ $((counter % 10)) -eq 0 ]; then
        echo "   Waiting for Directus to be ready... (${counter}s/${timeout}s)"
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep directus || true
    fi
    
    sleep 1
    counter=$((counter + 1))
done

if [ $counter -ge $timeout ]; then
    echo "❌ Directus failed to start within $timeout seconds"
    echo "📋 Container logs:"
    $DOCKER_COMPOSE_CMD -f docker-compose.directus-fixed.yml logs directus
    exit 1
fi

# Verify Directus is accessible
echo "🔍 Verifying Directus accessibility..."
if curl -s -f http://localhost:8055/server/health > /dev/null; then
    echo "✅ Directus is accessible at http://localhost:8055"
else
    echo "⚠️  Directus may not be fully ready yet. Checking status..."
    curl -s http://localhost:8055/server/health || echo "Health check endpoint not responding"
fi

# Display status information
echo ""
echo "🎉 Directus Beast Mode Integration Started Successfully!"
echo "=" * 60
echo "📊 Service Status:"
$DOCKER_COMPOSE_CMD -f docker-compose.directus-fixed.yml ps

echo ""
echo "🔗 Access Information:"
echo "   - Directus Admin: http://localhost:8055"
echo "   - Database: localhost:5433 (directus_beast_mode)"
echo "   - Redis: localhost:6380"

echo ""
echo "🔑 Default Credentials (CHANGE IN PRODUCTION):"
echo "   - Email: admin@beast-mode.local"
echo "   - Password: beast_mode_admin_secure_2024"

echo ""
echo "📋 Management Commands:"
echo "   - View logs: $DOCKER_COMPOSE_CMD -f docker-compose.directus-fixed.yml logs -f"
echo "   - Stop services: $DOCKER_COMPOSE_CMD -f docker-compose.directus-fixed.yml down"
echo "   - Restart services: $DOCKER_COMPOSE_CMD -f docker-compose.directus-fixed.yml restart"

echo ""
echo "🔍 Health Check:"
echo "   - Directus: curl http://localhost:8055/server/health"
echo "   - Database: docker exec directus_postgres_fixed pg_isready -U directus"

echo ""
echo "✅ Directus Beast Mode Integration is ready for AI Memory Palace connection!"