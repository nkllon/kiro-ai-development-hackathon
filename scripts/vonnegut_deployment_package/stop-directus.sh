#!/bin/bash

# Directus CMS Stop Script
# Systematic shutdown with cleanup

set -e

echo "🛑 Stopping Directus CMS..."

# Check if services are running
if ! docker-compose -f docker-compose.directus.yml ps | grep -q "Up"; then
    echo "ℹ️  No Directus services are currently running"
    exit 0
fi

# Stop services gracefully
echo "🔄 Stopping services gracefully..."
docker-compose -f docker-compose.directus.yml stop

# Wait a moment for graceful shutdown
sleep 5

# Remove containers
echo "🗑️  Removing containers..."
docker-compose -f docker-compose.directus.yml down

echo "✅ Directus CMS stopped successfully"
echo ""
echo "💾 Data preserved in Docker volumes:"
echo "   - postgres_data (database)"
echo "   - directus_uploads (file uploads)"
echo "   - directus_extensions (custom extensions)"
echo "   - redis_data (cache data)"
echo ""
echo "🗑️  To completely remove all data:"
echo "   docker-compose -f docker-compose.directus.yml down -v"
echo ""