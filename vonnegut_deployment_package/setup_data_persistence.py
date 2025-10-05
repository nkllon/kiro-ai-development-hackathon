#!/usr/bin/env python3
"""
Observatory Data Persistence Setup
=================================

Sets up local filesystem directories and data recovery procedures.
Part of Observatory Vonnegut Deployment Recovery.
"""

import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path

class DataPersistenceManager:
    def __init__(self):
        self.base_data_dir = Path("observatory_data")
        self.backup_dir = None
        
        # Find the most recent backup directory
        backup_dirs = [d for d in Path(".").glob("observatory_backup_*") if d.is_dir()]
        if backup_dirs:
            self.backup_dir = max(backup_dirs, key=lambda x: x.stat().st_mtime)
    
    def create_data_directories(self):
        """Create local filesystem directories for Observatory data storage."""
        print("📁 Creating Observatory data directories...")
        
        directories = {
            "metrics": "Prometheus-style metrics storage",
            "dashboards": "Dashboard configurations and layouts",
            "logs": "Application and access logs",
            "config": "Runtime configuration files",
            "cache": "Temporary cache files",
            "uploads": "User uploaded files",
            "exports": "Data export files"
        }
        
        created_dirs = []
        
        for dir_name, description in directories.items():
            dir_path = self.base_data_dir / dir_name
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Set proper permissions (readable/writable by owner, readable by group)
                os.chmod(dir_path, 0o755)
                
                print(f"✅ Created {dir_path} - {description}")
                created_dirs.append(str(dir_path))
                
                # Create a README file in each directory
                readme_file = dir_path / "README.md"
                with open(readme_file, 'w') as f:
                    f.write(f"# {dir_name.title()} Directory\n\n")
                    f.write(f"{description}\n\n")
                    f.write(f"Created: {datetime.now().isoformat()}\n")
                    f.write(f"Purpose: Observatory data persistence\n")
                
            except Exception as e:
                print(f"❌ Failed to create {dir_path}: {e}")
                return False
        
        print(f"✅ Successfully created {len(created_dirs)} data directories")
        return True
    
    def set_directory_permissions(self):
        """Set proper permissions on data directories."""
        print("🔐 Setting directory permissions...")
        
        try:
            # Set base directory permissions
            os.chmod(self.base_data_dir, 0o755)
            
            # Set subdirectory permissions
            for subdir in self.base_data_dir.iterdir():
                if subdir.is_dir():
                    os.chmod(subdir, 0o755)
            
            print("✅ Directory permissions set correctly")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set permissions: {e}")
            return False
    
    def recover_existing_data(self):
        """Recover data from existing backups if available."""
        print("🔄 Checking for existing data to recover...")
        
        if not self.backup_dir:
            print("ℹ️  No backup directory found, starting with clean data")
            return True
        
        print(f"📦 Found backup directory: {self.backup_dir}")
        
        # Check for Prometheus data backup
        prometheus_backup = self.backup_dir / "observatory_prometheus_data.tar.gz"
        if prometheus_backup.exists():
            print("🔄 Recovering Prometheus metrics data...")
            try:
                # Extract to metrics directory
                metrics_dir = self.base_data_dir / "metrics"
                import subprocess
                result = subprocess.run([
                    "tar", "xzf", str(prometheus_backup), "-C", str(metrics_dir)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Prometheus data recovered successfully")
                else:
                    print(f"⚠️  Prometheus data recovery failed: {result.stderr}")
            except Exception as e:
                print(f"❌ Error recovering Prometheus data: {e}")
        
        # Check for Grafana data backup
        grafana_backup = self.backup_dir / "observatory_grafana_data.tar.gz"
        if grafana_backup.exists():
            print("🔄 Recovering Grafana configuration...")
            try:
                # Extract to dashboards directory
                dashboards_dir = self.base_data_dir / "dashboards"
                import subprocess
                result = subprocess.run([
                    "tar", "xzf", str(grafana_backup), "-C", str(dashboards_dir)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Grafana data recovered successfully")
                else:
                    print(f"⚠️  Grafana data recovery failed: {result.stderr}")
            except Exception as e:
                print(f"❌ Error recovering Grafana data: {e}")
        
        return True
    
    def create_backup_procedures(self):
        """Create simple file-based backup procedures."""
        print("📋 Creating backup procedures...")
        
        backup_script_content = '''#!/usr/bin/env python3
"""
Observatory Data Backup Script
=============================

Simple file-based backup for Observatory data.
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

def create_backup():
    """Create a backup of Observatory data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"observatory_data_backup_{timestamp}")
    data_dir = Path("observatory_data")
    
    if not data_dir.exists():
        print("❌ Observatory data directory not found")
        return False
    
    print(f"📦 Creating backup: {backup_dir}")
    
    try:
        # Create backup directory
        backup_dir.mkdir(exist_ok=True)
        
        # Copy data directory
        shutil.copytree(data_dir, backup_dir / "observatory_data")
        
        # Create compressed archive
        archive_name = f"{backup_dir}.tar.gz"
        subprocess.run([
            "tar", "czf", archive_name, "-C", ".", str(backup_dir.name)
        ], check=True)
        
        # Remove uncompressed backup
        shutil.rmtree(backup_dir)
        
        print(f"✅ Backup created: {archive_name}")
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def restore_backup(backup_file):
    """Restore from a backup file."""
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    print(f"🔄 Restoring from: {backup_file}")
    
    try:
        # Extract backup
        subprocess.run([
            "tar", "xzf", str(backup_path)
        ], check=True)
        
        # Find extracted directory
        extracted_dirs = [d for d in Path(".").glob("observatory_data_backup_*") if d.is_dir()]
        if not extracted_dirs:
            print("❌ No extracted backup directory found")
            return False
        
        extracted_dir = extracted_dirs[0]
        
        # Remove existing data directory
        data_dir = Path("observatory_data")
        if data_dir.exists():
            shutil.rmtree(data_dir)
        
        # Move restored data
        shutil.move(extracted_dir / "observatory_data", data_dir)
        
        # Clean up
        shutil.rmtree(extracted_dir)
        
        print("✅ Backup restored successfully")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backup_observatory_data.py [backup|restore] [backup_file]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        success = create_backup()
    elif command == "restore" and len(sys.argv) > 2:
        success = restore_backup(sys.argv[2])
    else:
        print("Usage: python backup_observatory_data.py [backup|restore] [backup_file]")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
'''
        
        backup_script = Path("scripts/backup_observatory_data.py")
        try:
            with open(backup_script, 'w') as f:
                f.write(backup_script_content)
            
            os.chmod(backup_script, 0o755)
            print(f"✅ Backup script created: {backup_script}")
            
        except Exception as e:
            print(f"❌ Failed to create backup script: {e}")
            return False
        
        # Create a simple cron-style backup scheduler
        scheduler_content = '''#!/bin/bash
# Observatory Data Backup Scheduler
# Add this to crontab for automatic backups
# Example: 0 2 * * * /path/to/this/script

cd "$(dirname "$0")/.."
python scripts/backup_observatory_data.py backup

# Keep only last 7 backups
ls -t observatory_data_backup_*.tar.gz | tail -n +8 | xargs -r rm
'''
        
        scheduler_script = Path("scripts/schedule_backup.sh")
        try:
            with open(scheduler_script, 'w') as f:
                f.write(scheduler_content)
            
            os.chmod(scheduler_script, 0o755)
            print(f"✅ Backup scheduler created: {scheduler_script}")
            
        except Exception as e:
            print(f"❌ Failed to create backup scheduler: {e}")
            return False
        
        return True
    
    def create_data_recovery_procedures(self):
        """Create data recovery procedures documentation."""
        print("📖 Creating data recovery procedures...")
        
        recovery_doc = '''# Observatory Data Recovery Procedures

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
'''
        
        recovery_doc_file = Path("docs/data_recovery_procedures.md")
        try:
            recovery_doc_file.parent.mkdir(exist_ok=True)
            with open(recovery_doc_file, 'w') as f:
                f.write(recovery_doc)
            
            print(f"✅ Recovery procedures documented: {recovery_doc_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create recovery documentation: {e}")
            return False
    
    def setup_data_persistence(self):
        """Execute complete data persistence setup."""
        print("🚀 Observatory Data Persistence Setup")
        print("=" * 50)
        
        # Step 1: Create data directories
        if not self.create_data_directories():
            return False
        
        # Step 2: Set proper permissions
        if not self.set_directory_permissions():
            return False
        
        # Step 3: Recover existing data
        if not self.recover_existing_data():
            return False
        
        # Step 4: Create backup procedures
        if not self.create_backup_procedures():
            return False
        
        # Step 5: Create recovery documentation
        if not self.create_data_recovery_procedures():
            return False
        
        print(f"\n🎉 Data Persistence Setup Complete!")
        print(f"📁 Data directory: {self.base_data_dir}")
        print(f"💾 Backup script: scripts/backup_observatory_data.py")
        print(f"📖 Recovery docs: docs/data_recovery_procedures.md")
        
        return True

def main():
    """Main data persistence setup execution."""
    manager = DataPersistenceManager()
    
    try:
        success = manager.setup_data_persistence()
        
        if success:
            print("\n🎯 Data persistence setup completed!")
            return True
        else:
            print("\n❌ Data persistence setup failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Data persistence setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)