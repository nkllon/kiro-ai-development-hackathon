#!/bin/bash
# Observatory Data Backup Scheduler
# Add this to crontab for automatic backups
# Example: 0 2 * * * /path/to/this/script

cd "$(dirname "$0")/.."
python scripts/backup_observatory_data.py backup

# Keep only last 7 backups
ls -t observatory_data_backup_*.tar.gz | tail -n +8 | xargs -r rm
