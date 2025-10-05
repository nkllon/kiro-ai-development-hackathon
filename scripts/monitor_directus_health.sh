#!/bin/bash
# Directus Health Monitoring Script
# Usage: ./monitor_directus_health.sh

echo "🏥 Directus Health Monitor"
echo "========================="

# Check container status
echo "📦 Container Status:"
docker ps --filter name=directus_cms_fixed --format "table {{.Names}}\t{{.Status}}"

# Check health status
echo ""
echo "🩺 Health Status:"
HEALTH=$(docker inspect directus_cms_fixed --format '{{.State.Health.Status}}' 2>/dev/null)
if [ "$HEALTH" = "healthy" ]; then
    echo "✅ Container Health: $HEALTH"
else
    echo "❌ Container Health: $HEALTH"
fi

# Test health endpoint
echo ""
echo "🌐 Health Endpoint Test:"
RESPONSE=$(curl -s -w "%{http_code}" http://localhost:8055/server/health)
HTTP_CODE="${RESPONSE: -3}"
BODY="${RESPONSE%???}"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HTTP Status: $HTTP_CODE"
    echo "📄 Response: $BODY"
else
    echo "❌ HTTP Status: $HTTP_CODE"
    echo "📄 Response: $BODY"
fi

# Check logs for errors
echo ""
echo "📋 Recent Logs (last 10 lines):"
docker logs directus_cms_fixed --tail 10

echo ""
echo "🔍 Health Check Logs:"
docker inspect directus_cms_fixed | jq '.[] | .State.Health.Log[-3:]' 2>/dev/null || echo "No health logs available"

# Network connectivity test
echo ""
echo "🌐 Network Connectivity:"
echo "Testing database connection..."
docker exec directus_cms_fixed ping -c 1 directus_postgres_fixed >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database (PostgreSQL) reachable"
else
    echo "❌ Database (PostgreSQL) unreachable"
fi

echo "Testing Redis connection..."
docker exec directus_cms_fixed ping -c 1 directus_redis_fixed >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Cache (Redis) reachable"
else
    echo "❌ Cache (Redis) unreachable"
fi

echo ""
echo "📊 Summary:"
if [ "$HEALTH" = "healthy" ] && [ "$HTTP_CODE" = "200" ]; then
    echo "🎉 Directus is HEALTHY and OPERATIONAL"
else
    echo "⚠️  Directus has issues - check logs above"
fi