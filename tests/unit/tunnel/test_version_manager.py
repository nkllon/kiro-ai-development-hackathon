"""
Unit tests for VersionManager
"""

import pytest
import tempfile
import json
import uuid
from pathlib import Path
from unittest.mock import patch, mock_open

from src.beast_mode.observatory.tunnel.version_manager import (
    VersionManager,
    VersionMetadata,
    VersionStatus
)


class TestVersionStatus:
    """Test VersionStatus enum"""
    
    def test_version_status_values(self):
        """Test that all version status values are defined"""
        assert VersionStatus.ACTIVE.value == "active"
        assert VersionStatus.BACKUP.value == "backup"
        assert VersionStatus.ROLLBACK.value == "rollback"
        assert VersionStatus.ARCHIVED.value == "archived"


class TestVersionMetadata:
    """Test VersionMetadata data structure"""
    
    def test_version_metadata_creation(self):
        """Test version metadata creation"""
        metadata = VersionMetadata(
            version_id="test-version-123",
            timestamp="2024-01-01T00:00:00Z",
            tunnel_name="test_tunnel",
            config_hash="abc123",
            status=VersionStatus.BACKUP,
            description="Test version",
            created_by="test_user",
            tags=["test", "backup"],
            file_size=1024,
            validation_status="valid"
        )
        
        assert metadata.version_id == "test-version-123"
        assert metadata.timestamp == "2024-01-01T00:00:00Z"
        assert metadata.tunnel_name == "test_tunnel"
        assert metadata.config_hash == "abc123"
        assert metadata.status == VersionStatus.BACKUP
        assert metadata.description == "Test version"
        assert metadata.created_by == "test_user"
        assert metadata.tags == ["test", "backup"]
        assert metadata.file_size == 1024
        assert metadata.validation_status == "valid"
    
    def test_version_metadata_defaults(self):
        """Test version metadata with default values"""
        metadata = VersionMetadata(
            version_id="test-version-123",
            timestamp="2024-01-01T00:00:00Z",
            tunnel_name="test_tunnel",
            config_hash="abc123",
            status=VersionStatus.BACKUP
        )
        
        assert metadata.description is None
        assert metadata.created_by is None
        assert metadata.tags == []  # Default empty list
        assert metadata.file_size == 0
        assert metadata.validation_status is None


class TestVersionManager:
    """Test VersionManager functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir
    
    @pytest.fixture
    def version_manager(self, temp_dir):
        """Create version manager instance for tests"""
        return VersionManager(temp_dir)
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for tests"""
        return {
            "tunnel": "test_tunnel",
            "credentials-file": "/tmp/test.json",
            "ingress": [
                {"hostname": "test.com", "service": "http://localhost:8080"},
                {"service": "http_status:404"}
            ]
        }
    
    def test_version_manager_initialization(self, temp_dir):
        """Test version manager initialization"""
        manager = VersionManager(temp_dir)
        
        assert manager.versions_dir == Path(temp_dir)
        assert manager.versions_dir.exists()
        assert manager.metadata_file == Path(temp_dir) / "versions_metadata.json"
        assert isinstance(manager.metadata, dict)
    
    def test_create_version(self, version_manager, sample_config):
        """Test version creation"""
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Test version",
            tags=["test", "backup"],
            created_by="test_user"
        )
        
        # Check that version ID is returned
        assert version_id is not None
        assert isinstance(version_id, str)
        
        # Check that metadata was created
        assert version_id in version_manager.metadata
        
        metadata = version_manager.metadata[version_id]
        assert metadata.tunnel_name == "test_tunnel"
        assert metadata.description == "Test version"
        assert metadata.tags == ["test", "backup"]
        assert metadata.created_by == "test_user"
        assert metadata.status == VersionStatus.BACKUP
        
        # Check that version directory was created
        version_dir = version_manager.versions_dir / version_id
        assert version_dir.exists()
        
        # Check that config file was created
        config_file = version_dir / "config.yaml"
        assert config_file.exists()
    
    def test_create_version_minimal(self, version_manager, sample_config):
        """Test version creation with minimal parameters"""
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        assert version_id is not None
        
        metadata = version_manager.metadata[version_id]
        assert metadata.tunnel_name == "test_tunnel"
        assert metadata.description is None
        assert metadata.tags == []
        assert metadata.created_by is None
    
    def test_get_version_existing(self, version_manager, sample_config):
        """Test getting existing version"""
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        retrieved_config = version_manager.get_version(version_id)
        
        assert retrieved_config is not None
        assert retrieved_config["tunnel"] == "test_tunnel"
        assert retrieved_config["credentials-file"] == "/tmp/test.json"
        assert len(retrieved_config["ingress"]) == 2
    
    def test_get_version_nonexistent(self, version_manager):
        """Test getting non-existent version"""
        fake_version_id = str(uuid.uuid4())
        retrieved_config = version_manager.get_version(fake_version_id)
        
        assert retrieved_config is None
    
    def test_list_versions_no_filter(self, version_manager, sample_config):
        """Test listing versions without filters"""
        # Create multiple versions
        version1 = version_manager.create_version(
            config=sample_config,
            tunnel_name="tunnel1",
            description="Version 1"
        )
        version2 = version_manager.create_version(
            config=sample_config,
            tunnel_name="tunnel2",
            description="Version 2"
        )
        
        versions = version_manager.list_versions()
        
        assert len(versions) == 2
        version_ids = [v.version_id for v in versions]
        assert version1 in version_ids
        assert version2 in version_ids
    
    def test_list_versions_filter_by_tunnel(self, version_manager, sample_config):
        """Test listing versions filtered by tunnel name"""
        # Create versions for different tunnels
        version1 = version_manager.create_version(
            config=sample_config,
            tunnel_name="tunnel1"
        )
        version2 = version_manager.create_version(
            config=sample_config,
            tunnel_name="tunnel2"
        )
        
        # Filter by tunnel1
        versions = version_manager.list_versions(tunnel_name="tunnel1")
        
        assert len(versions) == 1
        assert versions[0].version_id == version1
        assert versions[0].tunnel_name == "tunnel1"
    
    def test_list_versions_filter_by_status(self, version_manager, sample_config):
        """Test listing versions filtered by status"""
        # Create versions
        version1 = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Set one as active
        version_manager.set_active_version(version1)
        
        # List active versions
        active_versions = version_manager.list_versions(status=VersionStatus.ACTIVE)
        assert len(active_versions) == 1
        assert active_versions[0].version_id == version1
        
        # List backup versions
        backup_versions = version_manager.list_versions(status=VersionStatus.BACKUP)
        assert len(backup_versions) == 0  # The active one is no longer backup
    
    def test_list_versions_with_limit(self, version_manager, sample_config):
        """Test listing versions with limit"""
        # Create multiple versions
        for i in range(5):
            version_manager.create_version(
                config=sample_config,
                tunnel_name=f"tunnel_{i}"
            )
        
        # List with limit
        versions = version_manager.list_versions(limit=3)
        
        assert len(versions) == 3
    
    def test_get_active_version_existing(self, version_manager, sample_config):
        """Test getting active version when one exists"""
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Set as active
        version_manager.set_active_version(version_id)
        
        active_version_id = version_manager.get_active_version("test_tunnel")
        
        assert active_version_id == version_id
    
    def test_get_active_version_nonexistent(self, version_manager):
        """Test getting active version when none exists"""
        active_version_id = version_manager.get_active_version("nonexistent_tunnel")
        
        assert active_version_id is None
    
    def test_set_active_version_existing(self, version_manager, sample_config):
        """Test setting existing version as active"""
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        success = version_manager.set_active_version(version_id)
        
        assert success is True
        
        # Check that version is now active
        metadata = version_manager.metadata[version_id]
        assert metadata.status == VersionStatus.ACTIVE
    
    def test_set_active_version_nonexistent(self, version_manager):
        """Test setting non-existent version as active"""
        fake_version_id = str(uuid.uuid4())
        success = version_manager.set_active_version(fake_version_id)
        
        assert success is False
    
    def test_set_active_version_switches_previous_active(self, version_manager, sample_config):
        """Test that setting new active version switches previous active"""
        # Create two versions
        version1 = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        version2 = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Set first as active
        version_manager.set_active_version(version1)
        
        # Set second as active
        version_manager.set_active_version(version2)
        
        # Check that first is now backup and second is active
        metadata1 = version_manager.metadata[version1]
        metadata2 = version_manager.metadata[version2]
        
        assert metadata1.status == VersionStatus.BACKUP
        assert metadata2.status == VersionStatus.ACTIVE
    
    def test_delete_version_existing(self, version_manager, sample_config):
        """Test deleting existing version"""
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        success = version_manager.delete_version(version_id)
        
        assert success is True
        
        # Check that version is removed from metadata
        assert version_id not in version_manager.metadata
        
        # Check that version directory is removed
        version_dir = version_manager.versions_dir / version_id
        assert not version_dir.exists()
    
    def test_delete_version_nonexistent(self, version_manager):
        """Test deleting non-existent version"""
        fake_version_id = str(uuid.uuid4())
        success = version_manager.delete_version(fake_version_id)
        
        assert success is False
    
    def test_delete_version_active(self, version_manager, sample_config):
        """Test that active version cannot be deleted"""
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Set as active
        version_manager.set_active_version(version_id)
        
        # Try to delete active version
        success = version_manager.delete_version(version_id)
        
        assert success is False
        
        # Check that version still exists
        assert version_id in version_manager.metadata
    
    def test_cleanup_old_versions(self, version_manager, sample_config):
        """Test cleanup of old versions"""
        # Create multiple versions for same tunnel
        versions = []
        for i in range(7):
            version_id = version_manager.create_version(
                config=sample_config,
                tunnel_name="test_tunnel",
                description=f"Version {i}"
            )
            versions.append(version_id)
        
        # Set one as active (should not be deleted)
        version_manager.set_active_version(versions[0])
        
        # Cleanup old versions, keep 3
        deleted_count = version_manager.cleanup_old_versions("test_tunnel", keep_count=3)
        
        # Should delete 3 versions (7 total - 1 active - 3 kept = 3 deleted)
        assert deleted_count == 3
        
        # Check remaining versions
        remaining_versions = version_manager.list_versions(tunnel_name="test_tunnel")
        assert len(remaining_versions) == 4  # 1 active + 3 kept
    
    def test_cleanup_old_versions_no_versions(self, version_manager):
        """Test cleanup when no versions exist"""
        deleted_count = version_manager.cleanup_old_versions("nonexistent_tunnel", keep_count=3)
        
        assert deleted_count == 0
    
    def test_get_version_info_existing(self, version_manager, sample_config):
        """Test getting version info for existing version"""
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Test version"
        )
        
        metadata = version_manager.get_version_info(version_id)
        
        assert metadata is not None
        assert metadata.version_id == version_id
        assert metadata.tunnel_name == "test_tunnel"
        assert metadata.description == "Test version"
    
    def test_get_version_info_nonexistent(self, version_manager):
        """Test getting version info for non-existent version"""
        fake_version_id = str(uuid.uuid4())
        metadata = version_manager.get_version_info(fake_version_id)
        
        assert metadata is None
    
    def test_export_version_existing(self, version_manager, sample_config, temp_dir):
        """Test exporting existing version"""
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        export_path = Path(temp_dir) / "exported_config.yaml"
        success = version_manager.export_version(version_id, str(export_path))
        
        assert success is True
        assert export_path.exists()
        
        # Check that exported file has content
        assert export_path.stat().st_size > 0
    
    def test_export_version_nonexistent(self, version_manager, temp_dir):
        """Test exporting non-existent version"""
        fake_version_id = str(uuid.uuid4())
        export_path = Path(temp_dir) / "exported_config.yaml"
        success = version_manager.export_version(fake_version_id, str(export_path))
        
        assert success is False
        assert not export_path.exists()
    
    def test_calculate_config_hash(self, version_manager):
        """Test config hash calculation"""
        config1 = {"tunnel": "test", "service": "http://localhost:8080"}
        config2 = {"tunnel": "test", "service": "http://localhost:8080"}  # Same
        config3 = {"tunnel": "test", "service": "http://localhost:8081"}  # Different
        
        hash1 = version_manager._calculate_config_hash(config1)
        hash2 = version_manager._calculate_config_hash(config2)
        hash3 = version_manager._calculate_config_hash(config3)
        
        # Same configs should have same hash
        assert hash1 == hash2
        
        # Different configs should have different hashes
        assert hash1 != hash3
        
        # Hash should be string
        assert isinstance(hash1, str)
        assert len(hash1) == 16  # Truncated to 16 characters
    
    def test_load_metadata_file_not_exists(self, temp_dir):
        """Test loading metadata when file doesn't exist"""
        manager = VersionManager(temp_dir)
        
        # Should return empty dict when file doesn't exist
        assert manager.metadata == {}
    
    def test_load_metadata_invalid_json(self, temp_dir):
        """Test loading metadata with invalid JSON"""
        metadata_file = Path(temp_dir) / "versions_metadata.json"
        
        # Write invalid JSON
        with open(metadata_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle gracefully and return empty dict
        manager = VersionManager(temp_dir)
        assert manager.metadata == {}
    
    def test_save_metadata_error_handling(self, version_manager, sample_config):
        """Test error handling in save metadata"""
        # Create a version to have some metadata
        version_id = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel"
        )
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            # Should not raise exception, just log error
            version_manager._save_metadata()
    
    def test_versions_sorted_by_timestamp(self, version_manager, sample_config):
        """Test that versions are sorted by timestamp (newest first)"""
        # Create versions with slight delays to ensure different timestamps
        version1 = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Version 1"
        )
        
        # Small delay to ensure different timestamp
        import time
        time.sleep(0.01)
        
        version2 = version_manager.create_version(
            config=sample_config,
            tunnel_name="test_tunnel",
            description="Version 2"
        )
        
        versions = version_manager.list_versions(tunnel_name="test_tunnel")
        
        # Should be sorted by timestamp (newest first)
        assert len(versions) == 2
        assert versions[0].version_id == version2  # Newer first
        assert versions[1].version_id == version1  # Older second