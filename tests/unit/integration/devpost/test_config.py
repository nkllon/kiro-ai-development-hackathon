"""
Unit tests for Devpost configuration management.

This module tests the DevpostConfigManager class including configuration
loading, saving, validation, and error handling functionality.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open

from src.beast_mode.integration.devpost.config import DevpostConfigManager
from src.beast_mode.integration.devpost.models import (
    DevpostConfig,
    ProjectConnection,
    SyncStatus
)
from src.beast_mode.core.exceptions import ConfigurationError


class TestDevpostConfigManager:
    """Test DevpostConfigManager functionality."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config_manager(self, temp_project_dir):
        """Create DevpostConfigManager instance for testing."""
        return DevpostConfigManager(project_root=temp_project_dir)
    
    @pytest.fixture
    def sample_config(self):
        """Create sample DevpostConfig for testing."""
        return DevpostConfig(
            project_id="test-project-123",
            hackathon_id="test-hackathon-456",
            sync_enabled=True,
            watch_patterns=["README*", "*.md", "package.json"],
            sync_interval=300,
            auto_sync_media=True,
            notification_enabled=True
        )
    
    @pytest.fixture
    def sample_connection(self, temp_project_dir, sample_config):
        """Create sample ProjectConnection for testing."""
        return ProjectConnection(
            local_path=temp_project_dir,
            devpost_project_id="test-project-123",
            hackathon_id="test-hackathon-456",
            last_sync=datetime.now() - timedelta(hours=1),
            sync_status=SyncStatus.COMPLETED,
            configuration=sample_config,
            created_at=datetime.now() - timedelta(days=1)
        )
    
    def test_initialization(self, temp_project_dir):
        """Test DevpostConfigManager initialization."""
        manager = DevpostConfigManager(project_root=temp_project_dir)
        
        assert manager.project_root == temp_project_dir
        assert manager.config_dir == temp_project_dir / ".kiro/devpost"
        assert manager.config_file == temp_project_dir / ".kiro/devpost/config.json"
        assert manager.connections_file == temp_project_dir / ".kiro/devpost/connections.json"
        
        # Config directory should be created
        assert manager.config_dir.exists()
    
    def test_initialization_default_project_root(self):
        """Test initialization with default project root."""
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path("/test/project")
            with patch.object(Path, 'mkdir') as mock_mkdir:
                manager = DevpostConfigManager()
                
                assert manager.project_root == Path("/test/project")
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_load_config_nonexistent_file(self, config_manager):
        """Test loading config when file doesn't exist."""
        config = config_manager.load_config()
        assert config is None
    
    def test_save_and_load_default_config(self, config_manager, sample_config):
        """Test saving and loading default configuration."""
        # Save config
        config_manager.save_config(sample_config)
        
        # Load config
        loaded_config = config_manager.load_config()
        
        assert loaded_config is not None
        assert loaded_config.project_id == sample_config.project_id
        assert loaded_config.hackathon_id == sample_config.hackathon_id
        assert loaded_config.sync_enabled == sample_config.sync_enabled
        assert loaded_config.watch_patterns == sample_config.watch_patterns
    
    def test_save_and_load_project_specific_config(self, config_manager, sample_config):
        """Test saving and loading project-specific configuration."""
        project_id = "specific-project-789"
        
        # Save project-specific config
        config_manager.save_config(sample_config, project_id=project_id)
        
        # Load project-specific config
        loaded_config = config_manager.load_config(project_id=project_id)
        
        assert loaded_config is not None
        assert loaded_config.project_id == sample_config.project_id
        
        # Default config should still be None
        default_config = config_manager.load_config()
        assert default_config is None
    
    def test_save_multiple_configs(self, config_manager, sample_config):
        """Test saving multiple configurations."""
        # Save default config
        config_manager.save_config(sample_config)
        
        # Save project-specific config
        project_config = DevpostConfig(
            project_id="another-project-999",
            hackathon_id="another-hackathon-888",
            sync_enabled=False
        )
        config_manager.save_config(project_config, project_id="another-project-999")
        
        # Load both configs
        default_config = config_manager.load_config()
        project_config_loaded = config_manager.load_config(project_id="another-project-999")
        
        assert default_config.project_id == sample_config.project_id
        assert project_config_loaded.project_id == "another-project-999"
        assert project_config_loaded.sync_enabled is False
    
    def test_load_config_invalid_json(self, config_manager):
        """Test loading config with invalid JSON."""
        # Create invalid JSON file
        config_manager.config_file.write_text("invalid json content")
        
        with pytest.raises(ConfigurationError, match="Invalid configuration file"):
            config_manager.load_config()
    
    def test_load_config_invalid_data(self, config_manager):
        """Test loading config with invalid data structure."""
        # Create JSON with invalid data
        invalid_data = {
            "default": {
                "project_id": "test",
                "sync_interval": "invalid"  # Should be int
            }
        }
        config_manager.config_file.write_text(json.dumps(invalid_data))
        
        with pytest.raises(ConfigurationError, match="Invalid configuration file"):
            config_manager.load_config()
    
    def test_save_config_file_error(self, config_manager, sample_config):
        """Test save config with file write error."""
        # Make config directory read-only
        config_manager.config_dir.chmod(0o444)
        
        try:
            with pytest.raises(ConfigurationError, match="Failed to save configuration"):
                config_manager.save_config(sample_config)
        finally:
            # Restore permissions for cleanup
            config_manager.config_dir.chmod(0o755)
    
    def test_load_connection_nonexistent_file(self, config_manager):
        """Test loading connection when file doesn't exist."""
        connection = config_manager.load_connection()
        assert connection is None
    
    def test_save_and_load_connection(self, config_manager, sample_connection):
        """Test saving and loading project connection."""
        # Save connection
        config_manager.save_connection(sample_connection)
        
        # Load connection
        loaded_connection = config_manager.load_connection()
        
        assert loaded_connection is not None
        assert loaded_connection.local_path == sample_connection.local_path
        assert loaded_connection.devpost_project_id == sample_connection.devpost_project_id
        assert loaded_connection.hackathon_id == sample_connection.hackathon_id
        assert loaded_connection.sync_status == sample_connection.sync_status
        assert loaded_connection.configuration.project_id == sample_connection.configuration.project_id
    
    def test_save_and_load_connection_specific_path(self, config_manager, sample_connection, temp_project_dir):
        """Test saving and loading connection for specific path."""
        specific_path = temp_project_dir / "subproject"
        specific_path.mkdir()
        
        # Update connection path
        sample_connection.local_path = specific_path
        
        # Save connection
        config_manager.save_connection(sample_connection)
        
        # Load connection for specific path
        loaded_connection = config_manager.load_connection(project_path=specific_path)
        
        assert loaded_connection is not None
        assert loaded_connection.local_path == specific_path
        
        # Loading for different path should return None
        other_connection = config_manager.load_connection(project_path=temp_project_dir)
        assert other_connection is None
    
    def test_load_connection_invalid_json(self, config_manager):
        """Test loading connection with invalid JSON."""
        # Create invalid JSON file
        config_manager.connections_file.write_text("invalid json content")
        
        with pytest.raises(ConfigurationError, match="Invalid connections file"):
            config_manager.load_connection()
    
    def test_load_connection_invalid_data(self, config_manager, temp_project_dir):
        """Test loading connection with invalid data structure."""
        # Create JSON with invalid data
        invalid_data = {
            str(temp_project_dir): {
                "local_path": str(temp_project_dir),
                "devpost_project_id": "test",
                "hackathon_id": "test",
                "sync_status": "invalid_status",  # Invalid enum value
                "configuration": {
                    "project_id": "test",
                    "hackathon_id": "test"
                }
            }
        }
        config_manager.connections_file.write_text(json.dumps(invalid_data))
        
        with pytest.raises(ConfigurationError, match="Invalid connections file"):
            config_manager.load_connection()
    
    def test_save_connection_file_error(self, config_manager, sample_connection):
        """Test save connection with file write error."""
        # Make config directory read-only
        config_manager.config_dir.chmod(0o444)
        
        try:
            with pytest.raises(ConfigurationError, match="Failed to save connection"):
                config_manager.save_connection(sample_connection)
        finally:
            # Restore permissions for cleanup
            config_manager.config_dir.chmod(0o755)
    
    def test_list_connections_empty(self, config_manager):
        """Test listing connections when file doesn't exist."""
        connections = config_manager.list_connections()
        assert connections == []
    
    def test_list_connections_multiple(self, config_manager, sample_config, temp_project_dir):
        """Test listing multiple connections."""
        # Create multiple connections
        connection1 = ProjectConnection(
            local_path=temp_project_dir / "project1",
            devpost_project_id="project-1",
            hackathon_id="hackathon-1",
            sync_status=SyncStatus.COMPLETED,
            configuration=sample_config
        )
        
        connection2 = ProjectConnection(
            local_path=temp_project_dir / "project2",
            devpost_project_id="project-2",
            hackathon_id="hackathon-2",
            sync_status=SyncStatus.PENDING,
            configuration=sample_config
        )
        
        # Save connections
        config_manager.save_connection(connection1)
        config_manager.save_connection(connection2)
        
        # List connections
        connections = config_manager.list_connections()
        
        assert len(connections) == 2
        project_ids = [conn.devpost_project_id for conn in connections]
        assert "project-1" in project_ids
        assert "project-2" in project_ids
    
    def test_list_connections_file_error(self, config_manager):
        """Test list connections with file read error."""
        # Create invalid JSON file
        config_manager.connections_file.write_text("invalid json")
        
        with pytest.raises(ConfigurationError, match="Failed to list connections"):
            config_manager.list_connections()
    
    def test_remove_connection_nonexistent_file(self, config_manager, temp_project_dir):
        """Test removing connection when file doesn't exist."""
        result = config_manager.remove_connection(temp_project_dir)
        assert result is False
    
    def test_remove_connection_nonexistent_path(self, config_manager, sample_connection, temp_project_dir):
        """Test removing connection for non-existent path."""
        # Save a connection
        config_manager.save_connection(sample_connection)
        
        # Try to remove different path
        other_path = temp_project_dir / "other"
        result = config_manager.remove_connection(other_path)
        assert result is False
        
        # Original connection should still exist
        loaded_connection = config_manager.load_connection()
        assert loaded_connection is not None
    
    def test_remove_connection_success(self, config_manager, sample_connection):
        """Test successful connection removal."""
        # Save connection
        config_manager.save_connection(sample_connection)
        
        # Verify it exists
        loaded_connection = config_manager.load_connection()
        assert loaded_connection is not None
        
        # Remove connection
        result = config_manager.remove_connection(sample_connection.local_path)
        assert result is True
        
        # Verify it's gone
        loaded_connection = config_manager.load_connection()
        assert loaded_connection is None
    
    def test_remove_connection_file_error(self, config_manager, sample_connection):
        """Test remove connection with file write error."""
        # Save connection first
        config_manager.save_connection(sample_connection)
        
        # Mock file operations to simulate error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(ConfigurationError, match="Failed to remove connection"):
                config_manager.remove_connection(sample_connection.local_path)
    
    def test_get_default_config(self, config_manager):
        """Test getting default configuration."""
        default_config = config_manager.get_default_config()
        
        assert isinstance(default_config, DevpostConfig)
        assert default_config.project_id == ""
        assert default_config.hackathon_id == ""
        assert default_config.sync_enabled is True
        assert default_config.auto_sync_media is True
        assert default_config.notification_enabled is True
        assert "README*" in default_config.watch_patterns
        assert "*.md" in default_config.watch_patterns
        assert default_config.sync_interval == 300
    
    def test_datetime_serialization_handling(self, config_manager, sample_connection):
        """Test proper handling of datetime serialization/deserialization."""
        # Save connection with datetime fields
        config_manager.save_connection(sample_connection)
        
        # Load connection
        loaded_connection = config_manager.load_connection()
        
        assert loaded_connection is not None
        assert isinstance(loaded_connection.last_sync, datetime)
        assert isinstance(loaded_connection.created_at, datetime)
        
        # Verify datetime values are preserved (within reasonable tolerance)
        time_diff = abs((loaded_connection.last_sync - sample_connection.last_sync).total_seconds())
        assert time_diff < 1  # Less than 1 second difference
    
    def test_path_serialization_handling(self, config_manager, sample_connection):
        """Test proper handling of Path serialization/deserialization."""
        # Save connection with Path objects
        config_manager.save_connection(sample_connection)
        
        # Load connection
        loaded_connection = config_manager.load_connection()
        
        assert loaded_connection is not None
        assert isinstance(loaded_connection.local_path, Path)
        assert loaded_connection.local_path == sample_connection.local_path
    
    def test_nested_config_serialization(self, config_manager, sample_connection):
        """Test proper handling of nested configuration serialization."""
        # Save connection with nested configuration
        config_manager.save_connection(sample_connection)
        
        # Load connection
        loaded_connection = config_manager.load_connection()
        
        assert loaded_connection is not None
        assert isinstance(loaded_connection.configuration, DevpostConfig)
        assert loaded_connection.configuration.project_id == sample_connection.configuration.project_id
        assert loaded_connection.configuration.sync_enabled == sample_connection.configuration.sync_enabled
        assert loaded_connection.configuration.watch_patterns == sample_connection.configuration.watch_patterns


@pytest.mark.integration
class TestDevpostConfigManagerIntegration:
    """Integration tests for DevpostConfigManager."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_full_configuration_workflow(self, temp_project_dir):
        """Test complete configuration management workflow."""
        manager = DevpostConfigManager(project_root=temp_project_dir)
        
        # 1. Start with default config
        default_config = manager.get_default_config()
        assert default_config.project_id == ""
        
        # 2. Update and save config
        default_config.project_id = "workflow-test-123"
        default_config.hackathon_id = "workflow-hackathon-456"
        manager.save_config(default_config)
        
        # 3. Create and save connection
        connection = ProjectConnection(
            local_path=temp_project_dir,
            devpost_project_id="workflow-test-123",
            hackathon_id="workflow-hackathon-456",
            sync_status=SyncStatus.PENDING,
            configuration=default_config
        )
        manager.save_connection(connection)
        
        # 4. Verify everything is saved correctly
        loaded_config = manager.load_config()
        loaded_connection = manager.load_connection()
        
        assert loaded_config.project_id == "workflow-test-123"
        assert loaded_connection.devpost_project_id == "workflow-test-123"
        assert loaded_connection.configuration.project_id == "workflow-test-123"
        
        # 5. List connections
        connections = manager.list_connections()
        assert len(connections) == 1
        assert connections[0].devpost_project_id == "workflow-test-123"
        
        # 6. Remove connection
        removed = manager.remove_connection(temp_project_dir)
        assert removed is True
        
        # 7. Verify removal
        connections_after_removal = manager.list_connections()
        assert len(connections_after_removal) == 0
    
    def test_multiple_projects_workflow(self, temp_project_dir):
        """Test managing multiple projects simultaneously."""
        manager = DevpostConfigManager(project_root=temp_project_dir)
        
        # Create multiple project directories
        project1_dir = temp_project_dir / "project1"
        project2_dir = temp_project_dir / "project2"
        project1_dir.mkdir()
        project2_dir.mkdir()
        
        # Create configurations for each project
        config1 = DevpostConfig(
            project_id="multi-project-1",
            hackathon_id="hackathon-1",
            sync_interval=300
        )
        
        config2 = DevpostConfig(
            project_id="multi-project-2",
            hackathon_id="hackathon-2",
            sync_interval=600
        )
        
        # Create connections for each project
        connection1 = ProjectConnection(
            local_path=project1_dir,
            devpost_project_id="multi-project-1",
            hackathon_id="hackathon-1",
            sync_status=SyncStatus.COMPLETED,
            configuration=config1
        )
        
        connection2 = ProjectConnection(
            local_path=project2_dir,
            devpost_project_id="multi-project-2",
            hackathon_id="hackathon-2",
            sync_status=SyncStatus.PENDING,
            configuration=config2
        )
        
        # Save both connections
        manager.save_connection(connection1)
        manager.save_connection(connection2)
        
        # Verify both connections exist
        connections = manager.list_connections()
        assert len(connections) == 2
        
        # Verify we can load each connection individually
        loaded_conn1 = manager.load_connection(project_path=project1_dir)
        loaded_conn2 = manager.load_connection(project_path=project2_dir)
        
        assert loaded_conn1.devpost_project_id == "multi-project-1"
        assert loaded_conn2.devpost_project_id == "multi-project-2"
        assert loaded_conn1.configuration.sync_interval == 300
        assert loaded_conn2.configuration.sync_interval == 600
        
        # Remove one connection
        removed = manager.remove_connection(project1_dir)
        assert removed is True
        
        # Verify only one connection remains
        connections_after_removal = manager.list_connections()
        assert len(connections_after_removal) == 1
        assert connections_after_removal[0].devpost_project_id == "multi-project-2"
    
    def test_config_persistence_across_instances(self, temp_project_dir):
        """Test configuration persistence across different manager instances."""
        # Create first manager instance and save config
        manager1 = DevpostConfigManager(project_root=temp_project_dir)
        config = DevpostConfig(
            project_id="persistence-test-123",
            hackathon_id="persistence-hackathon-456"
        )
        manager1.save_config(config)
        
        # Create second manager instance and load config
        manager2 = DevpostConfigManager(project_root=temp_project_dir)
        loaded_config = manager2.load_config()
        
        assert loaded_config is not None
        assert loaded_config.project_id == "persistence-test-123"
        assert loaded_config.hackathon_id == "persistence-hackathon-456"
    
    def test_error_recovery_and_validation(self, temp_project_dir):
        """Test error recovery and validation scenarios."""
        manager = DevpostConfigManager(project_root=temp_project_dir)
        
        # Test with corrupted config file
        manager.config_file.write_text("corrupted json {")
        
        with pytest.raises(ConfigurationError):
            manager.load_config()
        
        # Recovery: remove corrupted file and save valid config
        manager.config_file.unlink()  # Remove corrupted file
        valid_config = DevpostConfig(
            project_id="recovery-test-123",
            hackathon_id="recovery-hackathon-456"
        )
        manager.save_config(valid_config)
        
        # Verify recovery worked
        loaded_config = manager.load_config()
        assert loaded_config.project_id == "recovery-test-123"