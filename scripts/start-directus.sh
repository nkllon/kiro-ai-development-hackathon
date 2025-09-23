#!/bin/bash

# Directus CMS Startup Script
# Systematic startup with health checks and validation

set -e

echo "🚀 Starting Directus CMS with systematic validation..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p directus/snapshots
mkdir -p directus/uploads
mkdir -p directus/extensions

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Copying environment configuration..."
    cp .env.directus .env
    echo "⚠️  Please review and update .env file with your configuration"
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.directus.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."

# Wait for PostgreSQL
echo "🔍 Checking PostgreSQL health..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if docker-compose -f docker-compose.directus.yml exec -T postgres pg_isready -U directus -d directus > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    echo "⏳ Waiting for PostgreSQL... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo "❌ PostgreSQL failed to start within $timeout seconds"
    docker-compose -f docker-compose.directus.yml logs postgres
    exit 1
fi

# Wait for Redis
echo "🔍 Checking Redis health..."
counter=0
while [ $counter -lt $timeout ]; do
    if docker-compose -f docker-compose.directus.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is ready"
        break
    fi
    echo "⏳ Waiting for Redis... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo "❌ Redis failed to start within $timeout seconds"
    docker-compose -f docker-compose.directus.yml logs redis
    exit 1
fi

# Wait for Directus
echo "🔍 Checking Directus health..."
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:8055/server/health > /dev/null 2>&1; then
        echo "✅ Directus is ready"
        break
    fi
    echo "⏳ Waiting for Directus... ($counter/$timeout)"
    sleep 3
    counter=$((counter + 3))
done

if [ $counter -ge $timeout ]; then
    echo "❌ Directus failed to start within $timeout seconds"
    docker-compose -f docker-compose.directus.yml logs directus
    exit 1
fi

# Validate schema
echo "🔍 Validating database schema..."
python3 -c "
from src.beast_mode.directus_cms.schema_manager import SchemaManager
import os

try:
    manager = SchemaManager(
        database_url=os.getenv('DATABASE_URL', 'postgresql://directus:directus@localhost:5432/directus'),
        database_type='postgresql'
    )
    
    validation = manager.validate_schema()
    if validation.is_valid:
        print('✅ Database schema validation passed')
    else:
        print('⚠️  Database schema validation issues found:')
        for issue in validation.issues:
            print(f'   - {issue}')
        
        print('📋 Recommendations:')
        for rec in validation.recommendations:
            print(f'   - {rec}')
    
    # Get schema info
    info = manager.get_schema_info()
    print(f'📊 Schema info: {info[\"table_count\"]} tables, status: {info[\"validation_status\"]}')
    
except Exception as e:
    print(f'❌ Schema validation failed: {e}')
    print('💡 You may need to run the schema creation manually')
"

echo ""
echo "🎉 Directus CMS is running!"
echo ""
echo "📍 Access URLs:"
echo "   - Directus Admin: http://localhost:8055"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "🔑 Default Credentials:"
echo "   - Email: admin@directus.local"
echo "   - Password: directus"
echo ""
echo "📋 Management Commands:"
echo "   - View logs: docker-compose -f docker-compose.directus.yml logs -f"
echo "   - Stop services: docker-compose -f docker-compose.directus.yml down"
echo "   - Restart services: docker-compose -f docker-compose.directus.yml restart"
echo ""
echo "🔍 Health Check:"
echo "   - curl http://localhost:8055/server/health"
echo ""