#!/bin/bash
# CMS Platform Recovery Script
# Restore CMS platform from backup

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    echo "Available backups:"
    ls -la /tmp/cms_backups/cms_backup_*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"
BACKUP_DIR="/tmp/cms_backups"
TEMP_DIR="/tmp/cms_recovery_$$"

echo "🔄 Starting CMS platform recovery from: ${BACKUP_FILE}"

# Extract backup
echo "📦 Extracting backup..."
mkdir -p "${TEMP_DIR}"
cd "${TEMP_DIR}"
tar -xzf "${BACKUP_FILE}"

BACKUP_NAME=$(basename "${BACKUP_FILE}" .tar.gz)
cd "${BACKUP_NAME}"

# Stop services
echo "⏹️ Stopping CMS services..."
docker-compose -f deployment/local/docker-compose.yml down

# Restore PostgreSQL database
echo "📊 Restoring PostgreSQL database..."
docker-compose -f deployment/local/docker-compose.yml up -d directus-db
sleep 10
docker exec -i local-directus-db-1 psql -U directus -d directus < directus_db.sql

# Restore Directus files
echo "📁 Restoring Directus files..."
if [ -d "uploads" ]; then
    docker cp uploads local-directus-1:/directus/
fi
if [ -d "extensions" ]; then
    docker cp extensions local-directus-1:/directus/
fi

# Start all services
echo "🚀 Starting CMS services..."
docker-compose -f deployment/local/docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Validate recovery
echo "✅ Validating recovery..."
curl -f http://localhost:8055/server/health || echo "⚠️ Directus health check failed"

# Cleanup
cd /
rm -rf "${TEMP_DIR}"

echo "🎉 CMS recovery completed successfully!"
