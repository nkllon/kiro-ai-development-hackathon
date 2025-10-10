# CMS Platform Backup and Recovery

## Automated Backup

The CMS platform includes automated backup procedures for:
- PostgreSQL database (Directus data)
- Redis cache data
- Directus uploads and extensions
- Configuration files

### Running Backup

```bash
# Manual backup
./scripts/backup_cms_platform.sh

# Automated backup (add to crontab)
0 2 * * * /path/to/scripts/backup_cms_platform.sh
```

### Backup Location

Backups are stored in `/tmp/cms_backups/` with the format:
- `cms_backup_YYYYMMDD_HHMMSS.tar.gz`

### Retention Policy

- Backups are automatically cleaned up after 7 days
- Critical backups should be moved to permanent storage

## Recovery Procedures

### Full System Recovery

```bash
# List available backups
./scripts/recover_cms_platform.sh

# Restore from specific backup
./scripts/recover_cms_platform.sh /tmp/cms_backups/cms_backup_20250127_120000.tar.gz
```

### Partial Recovery

For partial recovery, extract the backup and restore specific components:

```bash
# Extract backup
tar -xzf cms_backup_20250127_120000.tar.gz
cd cms_backup_20250127_120000

# Restore only database
docker exec -i local-directus-db-1 psql -U directus -d directus < directus_db.sql

# Restore only files
docker cp uploads local-directus-1:/directus/
docker cp extensions local-directus-1:/directus/
```

## Disaster Recovery

### RTO (Recovery Time Objective)
- Target: < 30 minutes for full system recovery
- Database recovery: < 10 minutes
- File recovery: < 5 minutes

### RPO (Recovery Point Objective)
- Target: < 24 hours data loss maximum
- Recommended: Daily automated backups
- Critical systems: Consider hourly backups

### Testing Recovery

Regular recovery testing is essential:

```bash
# Test recovery in isolated environment
docker-compose -f docker-compose.test.yml up -d
./scripts/recover_cms_platform.sh <backup_file>
# Validate functionality
# Cleanup test environment
```
