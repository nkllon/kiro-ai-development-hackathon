#!/usr/bin/env python3
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
