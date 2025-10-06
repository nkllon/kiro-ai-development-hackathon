# Observatory Data Recovery Procedures

## Overview

This document describes how to recover Observatory data in various scenarios.

## Data Directory Structure

```
observatory_data/
├── metrics/          # Prometheus-style metrics storage
├── dashboards/       # Dashboard configurations
├── logs/            # Application logs
├── config/          # Runtime configuration
├── cache/           # Temporary cache files
├── uploads/         # User uploaded files
└── exports/         # Data export files
```

## Recovery Scenarios

### 1. Complete Data Loss

If the entire `observatory_data` directory is lost:

```bash
# Restore from most recent backup
python scripts/backup_observatory_data.py restore observatory_data_backup_YYYYMMDD_HHMMSS.tar.gz
```

### 2. Partial Data Loss

If only specific subdirectories are lost:

```bash
# Recreate data directories
python scripts/setup_data_persistence.py

# Manually restore specific data from backups
tar xzf observatory_data_backup_YYYYMMDD_HHMMSS.tar.gz
cp -r observatory_data_backup_YYYYMMDD_HHMMSS/observatory_data/metrics/ observatory_data/
```

### 3. Corruption Recovery

If data appears corrupted:

```bash
# Create backup of current state
mv observatory_data observatory_data_corrupted_$(date +%Y%m%d_%H%M%S)

# Restore from known good backup
python scripts/backup_observatory_data.py restore observatory_data_backup_YYYYMMDD_HHMMSS.tar.gz
```

### 4. Migration Recovery

When moving to a new server:

```bash
# On old server
python scripts/backup_observatory_data.py backup

# Transfer backup file to new server
scp observatory_data_backup_*.tar.gz user@newserver:/path/to/observatory/

# On new server
python scripts/setup_data_persistence.py
python scripts/backup_observatory_data.py restore observatory_data_backup_*.tar.gz
```

## Backup Management

### Create Manual Backup

```bash
python scripts/backup_observatory_data.py backup
```

### Schedule Automatic Backups

Add to crontab for daily backups at 2 AM:

```bash
crontab -e
# Add this line:
0 2 * * * cd /path/to/observatory && ./scripts/schedule_backup.sh
```

### Backup Retention

The backup scheduler automatically keeps the last 7 backups and removes older ones.

## Validation

After any recovery operation, validate the data:

```bash
# Check directory structure
ls -la observatory_data/

# Check permissions
ls -ld observatory_data/*/

# Test Observatory startup
python start_observatory.py
```

## Emergency Contacts

- System Administrator: [contact info]
- Observatory Maintainer: [contact info]
- Backup Storage Location: [location info]

---

Created: {datetime.now().isoformat()}
