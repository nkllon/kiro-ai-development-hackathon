#!/bin/bash

# Directus CMS Health Check Script
# Comprehensive health monitoring for all services

set -e

echo "🔍 Directus CMS Health Check"
echo "=========================="

# Check Docker
echo "🐳 Docker Status:"
if docker info > /dev/null 2>&1; then
    echo "   ✅ Docker is running"
else
    echo "   ❌ Docker is not running"
    exit 1
fi

# Check if services are running
echo ""
echo "📊 Service Status:"
if docker-compose -f docker-compose.directus.yml ps | grep -q "Up"; then
    docker-compose -f docker-compose.directus.yml ps
else
    echo "   ❌ No Directus services are running"
    echo "   💡 Run: ./scripts/start-directus.sh"
    exit 1
fi

# Check PostgreSQL health
echo ""
echo "🐘 PostgreSQL Health:"
if docker-compose -f docker-compose.directus.yml exec -T postgres pg_isready -U directus -d directus > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL is healthy"
    
    # Get database info
    DB_INFO=$(docker-compose -f docker-compose.directus.yml exec -T postgres psql -U directus -d directus -t -c "
        SELECT 
            'Tables: ' || COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'repository_content'
    " 2>/dev/null | xargs)
    echo "   📊 $DB_INFO"
else
    echo "   ❌ PostgreSQL is not healthy"
fi

# Check Redis health
echo ""
echo "🔴 Redis Health:"
if docker-compose -f docker-compose.directus.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis is healthy"
    
    # Get Redis info
    REDIS_INFO=$(docker-compose -f docker-compose.directus.yml exec -T redis redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
    echo "   📊 Memory usage: $REDIS_INFO"
else
    echo "   ❌ Redis is not healthy"
fi

# Check Directus health
echo ""
echo "🎯 Directus Health:"
if curl -f http://localhost:8055/server/health > /dev/null 2>&1; then
    echo "   ✅ Directus is healthy"
    
    # Get Directus info
    DIRECTUS_INFO=$(curl -s http://localhost:8055/server/info 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'Version: {data.get(\"directus\", {}).get(\"version\", \"unknown\")}')
except:
    print('Info not available')
" 2>/dev/null || echo "Info not available")
    echo "   📊 $DIRECTUS_INFO"
else
    echo "   ❌ Directus is not healthy"
    echo "   🔗 Expected URL: http://localhost:8055"
fi

# Check schema validation
echo ""
echo "🗄️  Schema Validation:"
python3 -c "
from src.beast_mode.directus_cms.schema_manager import SchemaManager
import os

try:
    manager = SchemaManager(
        database_url='postgresql://directus:directus@localhost:5432/directus',
        database_type='postgresql'
    )
    
    health = manager.get_health_status()
    print(f'   📊 Schema Manager Health: {health.status.value}')
    print(f'   📊 Health Score: {health.health_score:.2f}')
    
    if health.issues:
        print('   ⚠️  Issues:')
        for issue in health.issues:
            print(f'      - {issue}')
    else:
        print('   ✅ No schema issues detected')
    
    # Get performance metrics
    metrics = manager.get_performance_metrics()
    print(f'   📊 Operations: {metrics[\"operation_count\"]}')
    print(f'   📊 Uptime: {metrics[\"uptime_seconds\"]:.1f}s')
    
except Exception as e:
    print(f'   ❌ Schema validation failed: {e}')
"

# Check network connectivity
echo ""
echo "🌐 Network Connectivity:"
PORTS=("5432:PostgreSQL" "6379:Redis" "8055:Directus")
for port_service in "${PORTS[@]}"; do
    port=$(echo $port_service | cut -d: -f1)
    service=$(echo $port_service | cut -d: -f2)
    
    if nc -z localhost $port 2>/dev/null; then
        echo "   ✅ $service (port $port) is accessible"
    else
        echo "   ❌ $service (port $port) is not accessible"
    fi
done

# Check disk usage
echo ""
echo "💾 Disk Usage:"
docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}"

echo ""
echo "🎉 Health check completed!"
echo ""
echo "📋 Quick Actions:"
echo "   - View logs: docker-compose -f docker-compose.directus.yml logs -f [service]"
echo "   - Restart service: docker-compose -f docker-compose.directus.yml restart [service]"
echo "   - Access Directus: http://localhost:8055"
echo ""