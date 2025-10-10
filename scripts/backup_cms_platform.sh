#!/bin/bash
# CMS Platform Backup Script
# Automated backup for Directus CMS, PostgreSQL, and Redis

set -e

BACKUP_DIR="/tmp/cms_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="cms_backup_${TIMESTAMP}"

echo "🔄 Starting CMS platform backup: ${BACKUP_NAME}"

# Create backup directory
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# Backup PostgreSQL database
echo "📊 Backing up PostgreSQL database..."
docker exec local-directus-db-1 pg_dump -U directus directus > "${BACKUP_DIR}/${BACKUP_NAME}/directus_db.sql"

# Backup Redis data
echo "🔄 Backing up Redis data..."
docker exec local-redis-1 redis-cli BGSAVE 2>/dev/null || echo "Redis backup skipped (not running)"

# Backup Directus uploads and extensions
echo "📁 Backing up Directus files..."
docker cp local-directus-1:/directus/uploads "${BACKUP_DIR}/${BACKUP_NAME}/uploads" 2>/dev/null || echo "Uploads backup skipped"
docker cp local-directus-1:/directus/extensions "${BACKUP_DIR}/${BACKUP_NAME}/extensions" 2>/dev/null || echo "Extensions backup skipped"

# Create backup metadata
cat > "${BACKUP_DIR}/${BACKUP_NAME}/backup_metadata.json" << EOF
{
  "backup_name": "${BACKUP_NAME}",
  "timestamp": "${TIMESTAMP}",
  "services": ["directus", "postgres", "redis"],
  "backup_type": "full",
  "created_by": "automated_backup_script"
}
EOF

# Compress backup
echo "🗜️ Compressing backup..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"

echo "✅ Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📊 Backup size: $(du -h ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz | cut -f1)"

# Cleanup old backups (keep last 7 days)
find "${BACKUP_DIR}" -name "cms_backup_*.tar.gz" -mtime +7 -delete

echo "🎉 CMS backup process completed successfully!"
