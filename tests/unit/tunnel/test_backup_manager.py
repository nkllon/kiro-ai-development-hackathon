"""
Unit tests for BackupManager - Configuration Backup and Restore
"""

import json
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from src.beast_mode.observatory.tunnel.backup_manager import BackupManager


class TestBackupManager:
    """Test cases for BackupManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test-config.yml"
        self.backup_dir = Path(self.temp_dir) / "backups"
        self.manager = BackupManager(str(self.config_path), str(self.backup_dir))

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test BackupManager initialization."""
        assert self.manager.config_path == self.config_path
        assert self.manager.backup_dir == self.backup_dir
        assert self.backup_dir.exists()

    def test_log_action(self, capsys):
        """Test JSON logging functionality."""
        self.manager.log_action("test_action", "completed", {"key": "value"})
        
        captured = capsys.readouterr()
        log_entry = json.loads(captured.out.strip())
        
        assert log_entry["task"] == "1"
        assert log_entry["action"] == "BackupManager.test_action"
        assert log_entry["status"] == "completed"
        assert log_entry["details"]["key"] == "value"
        assert "timestamp" in log_entry

    def test_create_backup_success(self):
        """Test successful backup creation."""
        # Create test config file
        test_config = {
            "tunnel": "test-tunnel",
            "ingress": [{"service": "http_status:404"}]
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Create backup
        success, backup_path = self.manager.create_backup("test_backup")
        
        assert success is True
        assert backup_path is not None
        
        backup_file = Path(backup_path)
        assert backup_file.exists()
        assert "test_backup" in backup_file.name
        
        # Check metadata file
        metadata_file = backup_file.with_suffix('.metadata.json')
        assert metadata_file.exists()
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        assert metadata["label"] == "test_backup"
        assert metadata["original_path"] == str(self.config_path)
        assert "checksum" in metadata
        assert "created_at" in metadata

    def test_create_backup_no_config_file(self):
        """Test backup creation when config file doesn't exist."""
        success, error_msg = self.manager.create_backup()
        
        assert success is False
        assert "Configuration file does not exist" in error_msg

    def test_create_backup_without_label(self):
        """Test backup creation without label."""
        # Create test config file
        test_config = {"tunnel": "test"}
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        success, backup_path = self.manager.create_backup()
        
        assert success is True
        backup_file = Path(backup_path)
        assert backup_file.exists()
        assert "config_backup_" in backup_file.name
        assert backup_file.name.count("_") == 2  # timestamp only

    def test_create_backup_error(self):
        """Test backup creation error handling."""
        # Create test config file
        test_config = {"tunnel": "test"}
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Mock shutil.copy2 to raise exception
        with patch("shutil.copy2", side_effect=PermissionError("Permission denied")):
            success, error_msg = self.manager.create_backup()
            
            assert success is False
            assert "Failed to create backup" in error_msg

    def test_restore_backup_success(self):
        """Test successful backup restoration."""
        # Create test config file
        test_config = {
            "tunnel": "original-tunnel",
            "ingress": [{"service": "http_status:404"}]
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Create backup
        success, backup_path = self.manager.create_backup("restore_test")
        assert success is True
        
        # Modify original config
        modified_config = {
            "tunnel": "modified-tunnel",
            "ingress": [{"service": "http_status:404"}]
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(modified_config, f)
        
        # Restore backup
        success, message = self.manager.restore_backup(backup_path)
        
        assert success is True
        assert "Configuration restored" in message
        
        # Verify restoration
        with open(self.config_path, 'r') as f:
            restored_config = yaml.safe_load(f)
        
        assert restored_config["tunnel"] == "original-tunnel"

    def test_restore_backup_nonexistent_file(self):
        """Test restore backup when backup file doesn't exist."""
        success, error_msg = self.manager.restore_backup("/nonexistent/backup.yml")
        
        assert success is False
        assert "Backup file does not exist" in error_msg

    def test_restore_backup_checksum_mismatch(self):
        """Test restore backup with checksum mismatch."""
        # Create test config file
        test_config = {"tunnel": "test"}
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Create backup
        success, backup_path = self.manager.create_backup()
        assert success is True
        
        # Mock _calculate_checksum to return different checksums
        with patch.object(self.manager, '_calculate_checksum', side_effect=["checksum1", "checksum2"]):
            success, error_msg = self.manager.restore_backup(backup_path)
            
            assert success is False
            assert "Checksum mismatch" in error_msg

    def test_restore_backup_error(self):
        """Test restore backup error handling."""
        # Create test config file
        test_config = {"tunnel": "test"}
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Create backup
        success, backup_path = self.manager.create_backup()
        assert success is True
        
        # Mock shutil.copy2 to raise exception
        with patch("shutil.copy2", side_effect=PermissionError("Permission denied")):
            success, error_msg = self.manager.restore_backup(backup_path)
            
            assert success is False
            assert "Failed to restore backup" in error_msg

    def test_list_backups_empty(self):
        """Test listing backups when none exist."""
        backups = self.manager.list_backups()
        
        assert isinstance(backups, list)
        assert len(backups) == 0

    def test_list_backups_with_files(self):
        """Test listing backups with existing backup files."""
        # Create test config file
        test_config = {"tunnel": "test"}
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Create multiple backups
        self.manager.create_backup("backup1")
        self.manager.create_backup("backup2")
        self.manager.create_backup("backup3")
        
        backups = self.manager.list_backups()
        
        assert len(backups) == 3
        
        # Check backup information
        for backup in backups:
            assert "path" in backup
            assert "filename" in backup
            assert "created_at" in backup
            assert "size" in backup
            assert "checksum" in backup
            assert "is_valid" in backup
        
        # Verify backups are sorted by creation time (newest first)
        assert backups[0]["created_at"] >= backups[1]["created_at"]
        assert backups[1]["created_at"] >= backups[2]["created_at"]

    def test_list_backups_invalid_file(self):
        """Test listing backups with invalid backup file."""
        # Create invalid backup file
        invalid_backup = self.backup_dir / "config_backup_20240101_120000.yml"
        with open(invalid_backup, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        backups = self.manager.list_backups()
        
        # Should still return the backup but mark it as invalid
        assert len(backups) == 1
        assert backups[0]["is_valid"] is False

    def test_cleanup_old_backups_within_limit(self):
        """Test cleanup when backup count is within limit."""
        # Create test config file
        test_config = {"tunnel": "test"}
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Create 5 backups (within limit of 10)
        for i in range(5):
            self.manager.create_backup(f"backup{i}")
        
        deleted_count, deleted_files = self.manager.cleanup_old_backups(keep_count=10)
        
        assert deleted_count == 0
        assert len(deleted_files) == 0

    def test_cleanup_old_backups_exceeds_count(self):
        """Test cleanup when backup count exceeds limit."""
        # Create test config file
        test_config = {"tunnel": "test"}
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Create 15 backups (exceeds limit of 10)
        for i in range(15):
            self.manager.create_backup(f"backup{i}")
        
        deleted_count, deleted_files = self.manager.cleanup_old_backups(keep_count=10)
        
        assert deleted_count > 0
        assert len(deleted_files) > 0
        assert deleted_count == len(deleted_files)

    def test_cleanup_old_backups_error(self):
        """Test cleanup error handling."""
        # Mock list_backups to raise exception
        with patch.object(self.manager, 'list_backups', side_effect=Exception("Test exception")):
            deleted_count, deleted_files = self.manager.cleanup_old_backups()
            
            assert deleted_count == 0
            assert len(deleted_files) == 0

    def test_rollback_to_previous_success(self):
        """Test successful rollback to previous backup."""
        # Create test config file
        test_config = {"tunnel": "original"}
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Create backup
        self.manager.create_backup("rollback_test")
        
        # Modify config
        modified_config = {"tunnel": "modified"}
        with open(self.config_path, 'w') as f:
            yaml.dump(modified_config, f)
        
        # Rollback
        success, message = self.manager.rollback_to_previous()
        
        assert success is True
        
        # Verify rollback
        with open(self.config_path, 'r') as f:
            rolled_back_config = yaml.safe_load(f)
        
        assert rolled_back_config["tunnel"] == "original"

    def test_rollback_to_previous_no_backups(self):
        """Test rollback when no backups exist."""
        success, error_msg = self.manager.rollback_to_previous()
        
        assert success is False
        assert "No backups available" in error_msg

    def test_rollback_to_previous_error(self):
        """Test rollback error handling."""
        # Mock list_backups to raise exception
        with patch.object(self.manager, 'list_backups', side_effect=Exception("Test exception")):
            success, error_msg = self.manager.rollback_to_previous()
            
            assert success is False
            assert "Rollback failed" in error_msg

    def test_calculate_checksum(self):
        """Test checksum calculation."""
        # Create test file
        test_file = self.temp_dir / "test.txt"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        checksum = self.manager._calculate_checksum(test_file)
        
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA-256 hex length

    def test_calculate_checksum_error(self):
        """Test checksum calculation error handling."""
        nonexistent_file = Path("/nonexistent/file.txt")
        checksum = self.manager._calculate_checksum(nonexistent_file)
        
        assert checksum == ""

    def test_validate_backup_file_valid(self):
        """Test backup file validation with valid file."""
        # Create valid backup file
        valid_config = {
            "tunnel": "test-tunnel",
            "ingress": [{"service": "http_status:404"}]
        }
        backup_file = self.backup_dir / "valid_backup.yml"
        with open(backup_file, 'w') as f:
            yaml.dump(valid_config, f)
        
        is_valid = self.manager._validate_backup_file(backup_file)
        assert is_valid is True

    def test_validate_backup_file_invalid(self):
        """Test backup file validation with invalid file."""
        # Create invalid backup file
        invalid_backup = self.backup_dir / "invalid_backup.yml"
        with open(invalid_backup, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        is_valid = self.manager._validate_backup_file(invalid_backup)
        assert is_valid is False

    def test_validate_backup_file_missing_fields(self):
        """Test backup file validation with missing required fields."""
        # Create backup file missing required fields
        incomplete_config = {"tunnel": "test"}  # Missing ingress
        backup_file = self.backup_dir / "incomplete_backup.yml"
        with open(backup_file, 'w') as f:
            yaml.dump(incomplete_config, f)
        
        is_valid = self.manager._validate_backup_file(backup_file)
        assert is_valid is False

    def test_get_backup_status(self):
        """Test getting backup status."""
        # Create test config file
        test_config = {"tunnel": "test"}
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Create some backups
        self.manager.create_backup("status_test1")
        self.manager.create_backup("status_test2")
        
        status = self.manager.get_backup_status()
        
        assert "backup_dir" in status
        assert "config_path" in status
        assert "total_backups" in status
        assert "valid_backups" in status
        assert "total_size" in status
        assert "latest_backup" in status
        
        assert status["total_backups"] == 2
        assert status["valid_backups"] == 2
        assert status["total_size"] > 0

    def test_get_backup_status_error(self):
        """Test backup status error handling."""
        # Mock list_backups to raise exception
        with patch.object(self.manager, 'list_backups', side_effect=Exception("Test exception")):
            status = self.manager.get_backup_status()
            
            assert "error" in status
            assert "Test exception" in status["error"]

    def test_backup_manager_integration(self):
        """Test complete BackupManager workflow."""
        # Create initial config
        initial_config = {
            "tunnel": "integration-test",
            "credentials-file": "/path/to/credentials.json",
            "ingress": [
                {
                    "hostname": "test.example.com",
                    "service": "http://localhost:8080",
                    "originRequest": {
                        "proxyType": "",
                        "keepAliveConnections": 10,
                        "keepAliveTimeout": "90s"
                    }
                },
                {"service": "http_status:404"}
            ]
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(initial_config, f)
        
        # Create backup
        success, backup_path = self.manager.create_backup("integration_backup")
        assert success is True
        
        # Modify config
        modified_config = initial_config.copy()
        modified_config["tunnel"] = "modified-integration-test"
        
        with open(self.config_path, 'w') as f:
            yaml.dump(modified_config, f)
        
        # List backups
        backups = self.manager.list_backups()
        assert len(backups) == 1
        assert backups[0]["is_valid"] is True
        
        # Restore backup
        success, message = self.manager.restore_backup(backup_path)
        assert success is True
        
        # Verify restoration
        with open(self.config_path, 'r') as f:
            restored_config = yaml.safe_load(f)
        assert restored_config["tunnel"] == "integration-test"
        
        # Get backup status
        status = self.manager.get_backup_status()
        assert status["total_backups"] == 1
        assert status["valid_backups"] == 1
        assert status["latest_backup"] is not None