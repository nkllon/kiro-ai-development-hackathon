#!/usr/bin/env python3
"""
Rollback mechanism for failed automated changes
"""
import os
import shutil
import json
from datetime import datetime
from pathlib import Path


class RollbackManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = Path(".beast_mode/rollback_backups")
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, description="Manual backup"):
        """Create backup of current state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}_{description.replace(' ', '_')}"
        backup_path = self.backup_dir / backup_name

        # Create backup of src directory
        src_backup = backup_path / "src"
        if os.path.exists("src"):
            shutil.copytree("src", src_backup)

        # Create backup of scripts
        scripts_backup = backup_path / "scripts"
        if os.path.exists("scripts"):
            shutil.copytree("scripts", scripts_backup)

        # Save backup metadata
        metadata = {
            "timestamp": timestamp,
            "description": description,
            "backup_path": str(backup_path),
        }

        with open(backup_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Backup created: {backup_name}")
        return str(backup_path)

    def list_backups(self):
        """List available backups"""
        backups = []
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                metadata_file = backup_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                    backups.append(metadata)
        return backups

    def rollback_to_backup(self, backup_name):
        """Rollback to specific backup"""
        backup_path = self.backup_dir / backup_name

        if not backup_path.exists():
            print(f"❌ Backup {backup_name} not found")
            return False

        try:
            # Restore src directory
            src_backup = backup_path / "src"
            if src_backup.exists():
                if os.path.exists("src"):
                    shutil.rmtree("src")
                shutil.copytree(src_backup, "src")

            # Restore scripts
            scripts_backup = backup_path / "scripts"
            if scripts_backup.exists():
                if os.path.exists("scripts"):
                    shutil.rmtree("scripts")
                shutil.copytree(scripts_backup, "scripts")

            print(f"✅ Rolled back to {backup_name}")
            return True

        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False


if __name__ == "__main__":
    manager = RollbackManager()

    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            backups = manager.list_backups()
            print("Available backups:")
            for backup in backups:
                print(f"  {backup['timestamp']}: {backup['description']}")
        elif sys.argv[1] == "rollback" and len(sys.argv) > 2:
            manager.rollback_to_backup(sys.argv[2])
        else:
            print("Usage: python rollback_manager.py [list|rollback <backup_name>]")
    else:
        # Create current backup
        manager.create_backup("Before targeted fixes")
