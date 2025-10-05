"""
Configuration Backup and Restore Manager

Provides backup/restore functionality for cloudflared configurations with
versioning, rollback capabilities, and audit trail for configuration changes.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml


class BackupManager:
    """Manages backup and restore operations for tunnel configurations."""

    def __init__(self, config_path: str = "cloudflared-config.yml", backup_dir: str = "config_backups"):
        """
        Initialize backup manager.

        Args:
            config_path: Path to the main configuration file
            backup_dir: Directory to store backups
        """
        self.config_path = Path(config_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

        self.log_action("backup_manager_init", "completed", {
            "config_path": str(self.config_path),
            "backup_dir": str(self.backup_dir)
        })

    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format as required."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "1",
            "action": f"BackupManager.{action}",
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))

    def create_backup(self, label: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create backup of current configuration.

        Args:
            label: Optional label for the backup

        Returns:
            Tuple of (success, backup_path_or_error_message)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        label_suffix = f"_{label}" if label else ""
        backup_filename = f"config_backup_{timestamp}{label_suffix}.yml"
        backup_path = self.backup_dir / backup_filename

        self.log_action("create_backup", "in_progress", {
            "backup_filename": backup_filename,
            "label": label,
            "timestamp": timestamp
        })

        try:
            if not self.config_path.exists():
                error_msg = f"Configuration file does not exist: {self.config_path}"
                self.log_action("create_backup", "error", {"error": error_msg})
                return False, error_msg

            # Copy configuration file to backup
            shutil.copy2(self.config_path, backup_path)

            # Create backup metadata
            metadata = {
                "created_at": datetime.now().isoformat(),
                "original_path": str(self.config_path),
                "backup_path": str(backup_path),
                "label": label,
                "file_size": backup_path.stat().st_size,
                "checksum": self._calculate_checksum(backup_path)
            }

            metadata_path = backup_path.with_suffix('.metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            self.log_action("create_backup", "completed", {
                "backup_path": str(backup_path),
                "metadata_path": str(metadata_path),
                "file_size": metadata["file_size"],
                "checksum": metadata["checksum"]
            })

            return True, str(backup_path)

        except Exception as e:
            error_msg = f"Failed to create backup: {str(e)}"
            self.log_action("create_backup", "error", {
                "error": error_msg,
                "error_type": type(e).__name__
            })
            return False, error_msg

    def restore_backup(self, backup_path: str) -> Tuple[bool, str]:
        """
        Restore configuration from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            Tuple of (success, message)
        """
        backup_file = Path(backup_path)

        self.log_action("restore_backup", "in_progress", {
            "backup_path": backup_path,
            "backup_exists": backup_file.exists()
        })

        try:
            if not backup_file.exists():
                error_msg = f"Backup file does not exist: {backup_path}"
                self.log_action("restore_backup", "error", {"error": error_msg})
                return False, error_msg

            # Create backup of current config before restore
            if self.config_path.exists():
                pre_restore_backup = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.create_backup(pre_restore_backup)

            # Ensure target directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Restore the backup
            shutil.copy2(backup_file, self.config_path)

            # Verify restoration
            restored_checksum = self._calculate_checksum(self.config_path)
            backup_checksum = self._calculate_checksum(backup_file)

            if restored_checksum != backup_checksum:
                error_msg = "Checksum mismatch after restore"
                self.log_action("restore_backup", "error", {
                    "error": error_msg,
                    "restored_checksum": restored_checksum,
                    "backup_checksum": backup_checksum
                })
                return False, error_msg

            success_msg = f"Configuration restored from {backup_path}"
            self.log_action("restore_backup", "completed", {
                "backup_path": backup_path,
                "restored_to": str(self.config_path),
                "checksum": restored_checksum
            })

            return True, success_msg

        except Exception as e:
            error_msg = f"Failed to restore backup: {str(e)}"
            self.log_action("restore_backup", "error", {
                "error": error_msg,
                "error_type": type(e).__name__
            })
            return False, error_msg

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.

        Returns:
            List of backup information dictionaries
        """
        self.log_action("list_backups", "in_progress", {
            "backup_dir": str(self.backup_dir)
        })

        backups = []

        try:
            if not self.backup_dir.exists():
                self.log_action("list_backups", "completed", {
                    "backup_count": 0,
                    "message": "No backup directory found"
                })
                return backups

            # Find all backup files
            backup_files = list(self.backup_dir.glob("config_backup_*.yml"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for backup_file in backup_files:
                try:
                    # Load metadata if available
                    metadata_file = backup_file.with_suffix('.metadata.json')
                    metadata = {}
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)

                    # Basic backup information
                    stat = backup_file.stat()
                    backup_info = {
                        "path": str(backup_file),
                        "filename": backup_file.name,
                        "created_at": metadata.get("created_at", datetime.fromtimestamp(stat.st_ctime).isoformat()),
                        "size": stat.st_size,
                        "label": metadata.get("label"),
                        "checksum": metadata.get("checksum", self._calculate_checksum(backup_file))
                    }

                    # Validate backup file
                    backup_info["is_valid"] = self._validate_backup_file(backup_file)

                    backups.append(backup_info)

                except Exception as e:
                    self.log_action("list_backups_file_error", "error", {
                        "file": str(backup_file),
                        "error": str(e)
                    })

            self.log_action("list_backups", "completed", {
                "backup_count": len(backups),
                "total_size": sum(b["size"] for b in backups)
            })

            return backups

        except Exception as e:
            self.log_action("list_backups", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return []

    def cleanup_old_backups(self, keep_count: int = 10, keep_days: int = 30) -> Tuple[int, List[str]]:
        """
        Clean up old backup files.

        Args:
            keep_count: Number of recent backups to keep
            keep_days: Number of days of backups to keep

        Returns:
            Tuple of (deleted_count, deleted_files)
        """
        self.log_action("cleanup_old_backups", "in_progress", {
            "keep_count": keep_count,
            "keep_days": keep_days
        })

        deleted_files = []
        deleted_count = 0

        try:
            backups = self.list_backups()

            if len(backups) <= keep_count:
                self.log_action("cleanup_old_backups", "completed", {
                    "deleted_count": 0,
                    "reason": "backup count within limit"
                })
                return 0, []

            # Calculate cutoff date
            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 3600)

            # Sort backups by creation time (newest first)
            sorted_backups = sorted(backups, key=lambda x: x["created_at"], reverse=True)

            # Keep the most recent backups and those within keep_days
            for i, backup in enumerate(sorted_backups):
                should_delete = False

                # Keep first keep_count backups
                if i >= keep_count:
                    # Check if backup is older than keep_days
                    backup_time = datetime.fromisoformat(backup["created_at"].replace('Z', '+00:00')).timestamp()
                    if backup_time < cutoff_date:
                        should_delete = True

                if should_delete:
                    try:
                        backup_path = Path(backup["path"])
                        metadata_path = backup_path.with_suffix('.metadata.json')

                        # Delete backup file and metadata
                        if backup_path.exists():
                            backup_path.unlink()
                            deleted_files.append(str(backup_path))
                            deleted_count += 1

                        if metadata_path.exists():
                            metadata_path.unlink()
                            deleted_files.append(str(metadata_path))

                    except Exception as e:
                        self.log_action("cleanup_delete_error", "error", {
                            "file": backup["path"],
                            "error": str(e)
                        })

            self.log_action("cleanup_old_backups", "completed", {
                "deleted_count": deleted_count,
                "deleted_files": deleted_files,
                "remaining_backups": len(backups) - deleted_count
            })

            return deleted_count, deleted_files

        except Exception as e:
            self.log_action("cleanup_old_backups", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return 0, []

    def rollback_to_previous(self) -> Tuple[bool, str]:
        """
        Rollback to the most recent backup.

        Returns:
            Tuple of (success, message)
        """
        self.log_action("rollback_to_previous", "in_progress")

        try:
            backups = self.list_backups()

            if not backups:
                error_msg = "No backups available for rollback"
                self.log_action("rollback_to_previous", "error", {"error": error_msg})
                return False, error_msg

            # Get the most recent backup
            latest_backup = backups[0]

            # Restore from the latest backup
            success, message = self.restore_backup(latest_backup["path"])

            if success:
                self.log_action("rollback_to_previous", "completed", {
                    "restored_from": latest_backup["path"],
                    "backup_created_at": latest_backup["created_at"]
                })
            else:
                self.log_action("rollback_to_previous", "error", {
                    "restore_error": message
                })

            return success, message

        except Exception as e:
            error_msg = f"Rollback failed: {str(e)}"
            self.log_action("rollback_to_previous", "error", {
                "error": error_msg,
                "error_type": type(e).__name__
            })
            return False, error_msg

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file."""
        import hashlib

        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def _validate_backup_file(self, backup_path: Path) -> bool:
        """Validate that backup file is valid YAML configuration."""
        try:
            with open(backup_path, 'r') as f:
                config = yaml.safe_load(f)

            # Basic validation
            return (isinstance(config, dict) and
                   "tunnel" in config and
                   "ingress" in config)
        except Exception:
            return False

    def get_backup_status(self) -> Dict[str, Any]:
        """
        Get backup system status and statistics.

        Returns:
            Dictionary with backup status information
        """
        self.log_action("get_backup_status", "in_progress")

        try:
            backups = self.list_backups()

            total_size = sum(backup["size"] for backup in backups)
            valid_backups = sum(1 for backup in backups if backup.get("is_valid", False))

            # Calculate disk usage
            backup_dir_size = 0
            if self.backup_dir.exists():
                for item in self.backup_dir.rglob('*'):
                    if item.is_file():
                        backup_dir_size += item.stat().st_size

            status = {
                "backup_dir": str(self.backup_dir),
                "backup_dir_exists": self.backup_dir.exists(),
                "config_path": str(self.config_path),
                "config_exists": self.config_path.exists(),
                "total_backups": len(backups),
                "valid_backups": valid_backups,
                "total_size": total_size,
                "backup_dir_size": backup_dir_size,
                "latest_backup": backups[0] if backups else None,
                "oldest_backup": backups[-1] if backups else None
            }

            self.log_action("get_backup_status", "completed", {
                "total_backups": len(backups),
                "valid_backups": valid_backups,
                "total_size": total_size
            })

            return status

        except Exception as e:
            self.log_action("get_backup_status", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return {
                "error": str(e),
                "backup_dir": str(self.backup_dir),
                "config_path": str(self.config_path)
            }