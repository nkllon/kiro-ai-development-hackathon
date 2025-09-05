"""
Unit tests for DevpostProjectManager.

Tests project connection establishment, metadata extraction,
configuration management, and validation functionality.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

from src.beast_mode.integration.devpost.project.manager import DevpostProjectManager
from src.beast_mode.integration.devpost.models import (
    DevpostConfig,
    ProjectConnection,
    ProjectMetadata,
    SyncStatus,
    ValidationResult,
)
from src.beast_mode.core.exceptions import ConfigurationError


class TestDevpostProjectManager:
    """Test cases for DevpostProjectManager."""
    
    @pytest.fixture
    def temp_project_dir(self, tmp_path):
        """Create a temporary project directory."""
        return tmp_path / "test_project"
    
    @pytest.fixture
    def project_manager(self, temp_project_dir):
        """Create a DevpostProjectManager instance."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        return DevpostProjectManager(temp_project_dir)
    
    @pytest.fixture
    def sample_readme_content(self):
        """Sample README content for testing."""
        return """# Test Project

This is a test project for hackathon integration.

## Description

A comprehensive test project that demonstrates various features
and capabilities for hackathon submissions.

## Installation

pip install test-project

## Usage

Run the project with: python main.py
"""
    
    @pytest.fixture
    def sample_package_json(self):
        """Sample package.json content."""
        return {
            "name": "test-hackathon-project",
            "version": "1.0.0",
            "description": "A test project for hackathon",
            "repository": {
                "type": "git",
                "url": "https://github.com/user/test-project.git"
            },
            "author": "Test Author"
        }
    
    @pytest.fixture
    def sample_pyproject_toml(self):
        """Sample pyproject.toml content."""
        return """[project]
name = "test-hackathon-project"
version = "1.0.0"
description = "A Python test project for hackathon"
authors = [{name = "Test Author", email = "test@example.com"}]

[project.urls]
repository = "https://github.com/user/test-project.git"
homepage = "https://github.com/user/test-project"
"""
    
    def test_init_creates_config_manager(self, temp_project_dir):
        """Test that initialization creates a config manager."""
        manager = DevpostProjectManager(temp_project_dir)
        
        assert manager.project_root == temp_project_dir
        assert manager.config_manager is not None
        assert manager.config_manager.project_root == temp_project_dir
    
    def test_init_with_no_path_uses_cwd(self, tmp_path):
        """Test that initialization without path uses current directory."""
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = tmp_path
            manager = DevpostProjectManager()
            
            assert manager.project_root == tmp_path
    
    def test_connect_to_devpost_creates_connection(self, project_manager):
        """Test connecting to a Devpost project."""
        project_id = "test-project-123"
        hackathon_id = "hackathon-456"
        
        with patch.object(project_manager.config_manager, 'save_connection') as mock_save:
            connection = project_manager.connect_to_devpost(project_id, hackathon_id)
            
            assert connection.devpost_project_id == project_id
            assert connection.hackathon_id == hackathon_id
            assert connection.local_path == project_manager.project_root
            assert connection.sync_status == SyncStatus.PENDING
            assert connection.configuration.project_id == project_id
            assert connection.configuration.hackathon_id == hackathon_id
            
            mock_save.assert_called_once_with(connection)
    
    def test_connect_to_devpost_handles_errors(self, project_manager):
        """Test error handling during connection setup."""
        with patch.object(project_manager.config_manager, 'save_connection', side_effect=Exception("Save failed")):
            with pytest.raises(ConfigurationError, match="Failed to connect to Devpost project"):
                project_manager.connect_to_devpost("test-id", "hackathon-id")
    
    def test_get_project_config_from_connection(self, project_manager):
        """Test getting configuration from current connection."""
        config = DevpostConfig(project_id="test", hackathon_id="hack")
        connection = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="test",
            hackathon_id="hack",
            configuration=config
        )
        project_manager._current_connection = connection
        
        result = project_manager.get_project_config()
        assert result == config
    
    def test_get_project_config_from_config_manager(self, project_manager):
        """Test getting configuration from config manager."""
        config = DevpostConfig(project_id="test", hackathon_id="hack")
        
        with patch.object(project_manager.config_manager, 'load_config', return_value=config):
            result = project_manager.get_project_config()
            assert result == config
    
    def test_get_project_config_no_config_raises_error(self, project_manager):
        """Test error when no configuration is found."""
        with patch.object(project_manager.config_manager, 'load_config', return_value=None):
            with pytest.raises(ConfigurationError, match="No project configuration found"):
                project_manager.get_project_config()
    
    def test_update_config_with_connection(self, project_manager):
        """Test updating configuration with active connection."""
        config = DevpostConfig(project_id="test", hackathon_id="hack", sync_enabled=True)
        connection = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="test",
            hackathon_id="hack",
            configuration=config
        )
        project_manager._current_connection = connection
        
        updates = {"sync_enabled": False, "sync_interval": 600}
        
        with patch.object(project_manager.config_manager, 'save_connection') as mock_save:
            result = project_manager.update_config(updates)
            
            assert result is True
            assert connection.configuration.sync_enabled is False
            assert connection.configuration.sync_interval == 600
            mock_save.assert_called_once_with(connection)
    
    def test_update_config_without_connection(self, project_manager):
        """Test updating configuration without active connection."""
        config = DevpostConfig(project_id="test", hackathon_id="hack", sync_enabled=True)
        
        with patch.object(project_manager, 'get_project_config', return_value=config):
            with patch.object(project_manager.config_manager, 'save_config') as mock_save:
                updates = {"sync_enabled": False}
                result = project_manager.update_config(updates)
                
                assert result is True
                mock_save.assert_called_once()
    
    def test_update_config_validation_error(self, project_manager):
        """Test error handling during configuration update."""
        config = DevpostConfig(project_id="test", hackathon_id="hack")
        
        with patch.object(project_manager, 'get_project_config', return_value=config):
            # Invalid sync_interval
            updates = {"sync_interval": -1}
            
            with pytest.raises(ConfigurationError):
                project_manager.update_config(updates)
    
    def test_extract_readme_metadata_markdown(self, project_manager, sample_readme_content):
        """Test extracting metadata from Markdown README."""
        readme_path = project_manager.project_root / "README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        readme_path.write_text(sample_readme_content)
        
        metadata = project_manager.get_project_metadata()
        
        assert metadata.title == "Test Project"
        assert "test project for hackathon integration" in metadata.tagline
        assert "comprehensive test project" in metadata.description
        assert metadata.readme_path == readme_path
    
    def test_extract_package_json_metadata(self, project_manager, sample_package_json):
        """Test extracting metadata from package.json."""
        package_path = project_manager.project_root / "package.json"
        package_path.parent.mkdir(parents=True, exist_ok=True)
        package_path.write_text(json.dumps(sample_package_json))
        
        metadata = project_manager.get_project_metadata()
        
        assert metadata.title == "test-hackathon-project"
        assert metadata.description == "A test project for hackathon"
        assert metadata.repository_url == "https://github.com/user/test-project.git"
        assert "name" in metadata.package_info
    
    def test_extract_pyproject_metadata(self, project_manager, sample_pyproject_toml):
        """Test extracting metadata from pyproject.toml."""
        pyproject_path = project_manager.project_root / "pyproject.toml"
        pyproject_path.parent.mkdir(parents=True, exist_ok=True)
        pyproject_path.write_text(sample_pyproject_toml)
        
        # Mock tomllib since it might not be available in all Python versions
        mock_data = {
            "project": {
                "name": "test-hackathon-project",
                "version": "1.0.0",
                "description": "A Python test project for hackathon",
                "authors": [{"name": "Test Author", "email": "test@example.com"}]
            }
        }
        
        with patch('builtins.open', mock_open(read_data=b'mock')), \
             patch.object(project_manager, '_extract_pyproject_metadata', return_value=mock_data['project']):
            metadata = project_manager.get_project_metadata()
            
            assert metadata.title == "test-hackathon-project"
            assert metadata.description == "A Python test project for hackathon"
    
    def test_extract_git_metadata(self, project_manager):
        """Test extracting metadata from Git configuration."""
        git_dir = project_manager.project_root / ".git"
        git_dir.mkdir(parents=True, exist_ok=True)
        
        git_config = """[core]
    repositoryformatversion = 0
[remote "origin"]
    url = https://github.com/user/test-project.git
    fetch = +refs/heads/*:refs/remotes/origin/*
"""
        
        config_path = git_dir / "config"
        config_path.write_text(git_config)
        
        metadata = project_manager.get_project_metadata()
        
        assert metadata.repository_url == "https://github.com/user/test-project.git"
    
    def test_validate_project_complete(self, project_manager, sample_readme_content):
        """Test validation of a complete project."""
        # Set up complete project
        readme_path = project_manager.project_root / "README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        readme_path.write_text(sample_readme_content)
        
        # Mock metadata with all required fields
        metadata = ProjectMetadata(
            title="Test Project",
            description="A comprehensive test project that demonstrates various features",
            repository_url="https://github.com/user/test-project.git",
            tags=["python", "test"]
        )
        
        with patch.object(project_manager, 'get_project_metadata', return_value=metadata):
            with patch.object(project_manager, '_find_media_files', return_value=[Path("screenshot.png")]):
                result = project_manager.validate_project()
                
                assert result.is_valid is True
                assert len(result.missing_fields) == 0
                assert len(result.validation_errors) == 0
    
    def test_validate_project_missing_fields(self, project_manager):
        """Test validation with missing required fields."""
        metadata = ProjectMetadata(title="Test Project")  # Valid title but missing other fields
        
        with patch.object(project_manager, 'get_project_metadata', return_value=metadata):
            result = project_manager.validate_project()
            
            assert result.is_valid is False
            assert 'description (minimum 50 characters)' in result.missing_fields
            assert 'repository_url or demo_url' in result.missing_fields
    
    def test_validate_project_with_warnings(self, project_manager):
        """Test validation that generates warnings."""
        metadata = ProjectMetadata(
            title="Test Project",
            description="A comprehensive test project that demonstrates various features and capabilities",
            repository_url="https://github.com/user/test-project.git"
        )
        
        with patch.object(project_manager, 'get_project_metadata', return_value=metadata):
            with patch.object(project_manager, '_find_media_files', return_value=[]):
                with patch.object(project_manager, '_validate_readme', return_value=[]):
                    result = project_manager.validate_project()
                    
                    assert result.is_valid is True
                    assert 'No media files found (screenshots, videos, etc.)' in result.warnings
    
    def test_find_media_files(self, project_manager):
        """Test finding media files in project."""
        # Create media directory with files
        media_dir = project_manager.project_root / "media"
        media_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test media files
        (media_dir / "screenshot.png").touch()
        (media_dir / "demo.mp4").touch()
        (project_manager.project_root / "preview.jpg").touch()
        
        media_files = project_manager._find_media_files()
        
        assert len(media_files) == 3
        filenames = [f.name for f in media_files]
        assert "screenshot.png" in filenames
        assert "demo.mp4" in filenames
        assert "preview.jpg" in filenames
    
    def test_validate_readme_missing(self, project_manager):
        """Test README validation when file is missing."""
        issues = project_manager._validate_readme()
        
        assert "No README file found" in issues
    
    def test_validate_readme_too_short(self, project_manager):
        """Test README validation for short content."""
        readme_path = project_manager.project_root / "README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        readme_path.write_text("# Short\n\nToo short.")
        
        issues = project_manager._validate_readme()
        
        assert any("too short" in issue for issue in issues)
    
    def test_check_project_files(self, project_manager):
        """Test checking for common project files."""
        # Create some files
        (project_manager.project_root / "LICENSE").touch()
        (project_manager.project_root / "CHANGELOG.md").touch()
        
        result = project_manager._check_project_files()
        
        assert "LICENSE" in result['found']
        assert "CHANGELOG.md" in result['found']
        assert "CONTRIBUTING" in result['missing']
    
    def test_load_current_connection_success(self, temp_project_dir):
        """Test loading existing connection on initialization."""
        config = DevpostConfig(project_id="test", hackathon_id="hack")
        connection = ProjectConnection(
            local_path=temp_project_dir,
            devpost_project_id="test",
            hackathon_id="hack",
            configuration=config
        )
        
        with patch('src.beast_mode.integration.devpost.config.DevpostConfigManager.load_connection', return_value=connection):
            manager = DevpostProjectManager(temp_project_dir)
            assert manager._current_connection == connection
    
    def test_load_current_connection_failure(self, project_manager):
        """Test handling connection loading failure during initialization."""
        with patch.object(project_manager.config_manager, 'load_connection', side_effect=Exception("Load failed")):
            manager = DevpostProjectManager(project_manager.project_root)
            assert manager._current_connection is None
    
    # Multi-project support tests
    
    def test_list_projects_empty(self, project_manager):
        """Test listing projects when none are connected."""
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[]):
            projects = project_manager.list_projects()
            assert projects == []
    
    def test_list_projects_with_connections(self, project_manager):
        """Test listing projects with existing connections."""
        config1 = DevpostConfig(project_id="project1", hackathon_id="hack1")
        config2 = DevpostConfig(project_id="project2", hackathon_id="hack2")
        
        connection1 = ProjectConnection(
            local_path=Path("/path1"),
            devpost_project_id="project1",
            hackathon_id="hack1",
            sync_status=SyncStatus.COMPLETED,
            configuration=config1,
            last_sync=datetime(2023, 1, 1),
            created_at=datetime(2023, 1, 1)
        )
        
        connection2 = ProjectConnection(
            local_path=Path("/path2"),
            devpost_project_id="project2",
            hackathon_id="hack2",
            sync_status=SyncStatus.PENDING,
            configuration=config2,
            created_at=datetime(2023, 1, 2)
        )
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection1, connection2]):
            projects = project_manager.list_projects()
            
            assert len(projects) == 2
            assert projects[0]['project_id'] == "project1"
            assert projects[0]['sync_status'] == "completed"
            assert projects[0]['last_sync'] == "2023-01-01T00:00:00"
            assert projects[1]['project_id'] == "project2"
            assert projects[1]['sync_status'] == "pending"
            assert projects[1]['last_sync'] is None
    
    def test_switch_project_success(self, project_manager):
        """Test successful project switching."""
        config = DevpostConfig(project_id="project1", hackathon_id="hack1")
        connection = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config
        )
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection]):
            result = project_manager.switch_project("project1")
            
            assert result is True
            assert project_manager._current_connection == connection
            assert project_manager._active_project_id == "project1"
    
    def test_switch_project_not_found(self, project_manager):
        """Test switching to non-existent project."""
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[]):
            with pytest.raises(ConfigurationError, match="Project nonexistent not found"):
                project_manager.switch_project("nonexistent")
    
    def test_switch_project_path_missing(self, project_manager):
        """Test switching to project with missing path."""
        config = DevpostConfig(project_id="project1", hackathon_id="hack1")
        connection = ProjectConnection(
            local_path=Path("/nonexistent/path"),
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config
        )
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection]):
            with pytest.raises(ConfigurationError, match="Project path .* no longer exists"):
                project_manager.switch_project("project1")
    
    def test_get_project_status_current(self, project_manager):
        """Test getting status for current project."""
        config = DevpostConfig(project_id="project1", hackathon_id="hack1")
        connection = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config,
            last_sync=datetime(2023, 1, 1),
            created_at=datetime(2023, 1, 1)
        )
        project_manager._current_connection = connection
        
        metadata = ProjectMetadata(
            title="Test Project",
            description="A test project with sufficient description length for validation",
            repository_url="https://github.com/user/test"
        )
        validation = ValidationResult(is_valid=True)
        
        with patch.object(project_manager, 'get_project_metadata', return_value=metadata):
            with patch.object(project_manager, 'validate_project', return_value=validation):
                status = project_manager.get_project_status()
                
                assert status['project_id'] == "project1"
                assert status['hackathon_id'] == "hack1"
                assert status['sync_status'] == "pending"
                assert status['last_sync'] == "2023-01-01T00:00:00"
                assert status['validation']['is_valid'] is True
                assert status['path_exists'] is True
    
    def test_get_project_status_specific(self, project_manager):
        """Test getting status for specific project."""
        config = DevpostConfig(project_id="project1", hackathon_id="hack1")
        connection = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config,
            created_at=datetime(2023, 1, 1)
        )
        
        metadata = ProjectMetadata(
            title="Test Project",
            description="A test project with sufficient description length for validation",
            repository_url="https://github.com/user/test"
        )
        validation = ValidationResult(is_valid=True)
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection]):
            with patch.object(project_manager, 'get_project_metadata', return_value=metadata):
                with patch.object(project_manager, 'validate_project', return_value=validation):
                    status = project_manager.get_project_status("project1")
                    
                    assert status['project_id'] == "project1"
                    assert status['validation']['is_valid'] is True
    
    def test_get_project_status_not_found(self, project_manager):
        """Test getting status for non-existent project."""
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[]):
            with pytest.raises(ConfigurationError, match="Project nonexistent not found"):
                project_manager.get_project_status("nonexistent")
    
    def test_get_project_status_no_active(self, project_manager):
        """Test getting status when no project is active."""
        with pytest.raises(ConfigurationError, match="No active project"):
            project_manager.get_project_status()
    
    def test_disconnect_project_success(self, project_manager):
        """Test successful project disconnection."""
        config = DevpostConfig(project_id="project1", hackathon_id="hack1")
        connection = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config
        )
        
        project_manager._current_connection = connection
        project_manager._active_project_id = "project1"
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection]):
            with patch.object(project_manager.config_manager, 'remove_connection', return_value=True):
                result = project_manager.disconnect_project("project1")
                
                assert result is True
                assert project_manager._current_connection is None
                assert project_manager._active_project_id is None
    
    def test_disconnect_project_not_found(self, project_manager):
        """Test disconnecting non-existent project."""
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[]):
            with pytest.raises(ConfigurationError, match="Project nonexistent not found"):
                project_manager.disconnect_project("nonexistent")
    
    def test_detect_project_conflicts_none(self, project_manager):
        """Test conflict detection with no conflicts."""
        config = DevpostConfig(project_id="project1", hackathon_id="hack1")
        connection = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config
        )
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection]):
            conflicts = project_manager.detect_project_conflicts()
            assert conflicts == []
    
    def test_detect_project_conflicts_duplicate_id(self, project_manager, tmp_path):
        """Test detecting duplicate project ID conflicts."""
        # Create temporary paths that exist
        path1 = tmp_path / "path1"
        path2 = tmp_path / "path2"
        path1.mkdir()
        path2.mkdir()
        
        config1 = DevpostConfig(project_id="project1", hackathon_id="hack1")
        config2 = DevpostConfig(project_id="project1", hackathon_id="hack2")
        
        connection1 = ProjectConnection(
            local_path=path1,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config1
        )
        
        connection2 = ProjectConnection(
            local_path=path2,
            devpost_project_id="project1",
            hackathon_id="hack2",
            configuration=config2
        )
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection1, connection2]):
            conflicts = project_manager.detect_project_conflicts()
            
            # Should only have duplicate_project_id conflict, not missing_path
            duplicate_conflicts = [c for c in conflicts if c['type'] == 'duplicate_project_id']
            assert len(duplicate_conflicts) == 1
            assert duplicate_conflicts[0]['project_id'] == 'project1'
            assert str(path1) in duplicate_conflicts[0]['paths']
            assert str(path2) in duplicate_conflicts[0]['paths']
    
    def test_detect_project_conflicts_missing_path(self, project_manager):
        """Test detecting missing path conflicts."""
        config = DevpostConfig(project_id="project1", hackathon_id="hack1")
        connection = ProjectConnection(
            local_path=Path("/nonexistent/path"),
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config
        )
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection]):
            conflicts = project_manager.detect_project_conflicts()
            
            assert len(conflicts) == 1
            assert conflicts[0]['type'] == 'missing_path'
            assert conflicts[0]['project_id'] == 'project1'
            assert conflicts[0]['path'] == '/nonexistent/path'
    
    def test_resolve_conflict_duplicate_project_id(self, project_manager):
        """Test resolving duplicate project ID conflict."""
        with patch.object(project_manager.config_manager, 'list_connections') as mock_list:
            with patch.object(project_manager.config_manager, 'remove_connection') as mock_remove:
                config1 = DevpostConfig(project_id="project1", hackathon_id="hack1")
                config2 = DevpostConfig(project_id="project1", hackathon_id="hack2")
                
                connection1 = ProjectConnection(
                    local_path=Path("/path1"),
                    devpost_project_id="project1",
                    hackathon_id="hack1",
                    configuration=config1
                )
                
                connection2 = ProjectConnection(
                    local_path=Path("/path2"),
                    devpost_project_id="project1",
                    hackathon_id="hack2",
                    configuration=config2
                )
                
                mock_list.return_value = [connection1, connection2]
                
                result = project_manager.resolve_conflict(
                    'duplicate_project_id',
                    'keep_one',
                    project_id='project1',
                    keep_path='/path1'
                )
                
                assert result is True
                mock_remove.assert_called_once_with(Path("/path2"))
    
    def test_resolve_conflict_missing_path_remove(self, project_manager):
        """Test resolving missing path conflict by removal."""
        with patch.object(project_manager, 'disconnect_project', return_value=True) as mock_disconnect:
            result = project_manager.resolve_conflict(
                'missing_path',
                'remove',
                project_id='project1'
            )
            
            assert result is True
            mock_disconnect.assert_called_once_with('project1')
    
    def test_resolve_conflict_unknown_type(self, project_manager):
        """Test resolving unknown conflict type."""
        with pytest.raises(ConfigurationError, match="Unknown conflict type"):
            project_manager.resolve_conflict('unknown_type', 'resolution')
    
    # Additional comprehensive multi-project tests
    
    def test_switch_project_updates_active_context(self, project_manager):
        """Test that switching projects properly updates the active context."""
        config1 = DevpostConfig(project_id="project1", hackathon_id="hack1")
        config2 = DevpostConfig(project_id="project2", hackathon_id="hack2")
        
        connection1 = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config1
        )
        
        connection2 = ProjectConnection(
            local_path=project_manager.project_root / "other",
            devpost_project_id="project2",
            hackathon_id="hack2",
            configuration=config2
        )
        
        # Create the other directory
        (project_manager.project_root / "other").mkdir(exist_ok=True)
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection1, connection2]):
            # Initially no active project
            assert project_manager._active_project_id is None
            
            # Switch to project1
            project_manager.switch_project("project1")
            assert project_manager._active_project_id == "project1"
            assert project_manager._current_connection == connection1
            
            # Switch to project2
            project_manager.switch_project("project2")
            assert project_manager._active_project_id == "project2"
            assert project_manager._current_connection == connection2
    
    def test_list_projects_shows_active_status(self, project_manager):
        """Test that list_projects correctly shows which project is active."""
        config1 = DevpostConfig(project_id="project1", hackathon_id="hack1")
        config2 = DevpostConfig(project_id="project2", hackathon_id="hack2")
        
        connection1 = ProjectConnection(
            local_path=Path("/path1"),
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config1,
            created_at=datetime(2023, 1, 1)
        )
        
        connection2 = ProjectConnection(
            local_path=Path("/path2"),
            devpost_project_id="project2",
            hackathon_id="hack2",
            configuration=config2,
            created_at=datetime(2023, 1, 2)
        )
        
        project_manager._active_project_id = "project1"
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection1, connection2]):
            projects = project_manager.list_projects()
            
            assert len(projects) == 2
            
            # Find project1 and project2 in results
            project1_info = next(p for p in projects if p['project_id'] == 'project1')
            project2_info = next(p for p in projects if p['project_id'] == 'project2')
            
            assert project1_info['is_active'] is True
            assert project2_info['is_active'] is False
    
    def test_get_project_status_preserves_context(self, project_manager):
        """Test that getting status for a specific project doesn't change active context."""
        config1 = DevpostConfig(project_id="project1", hackathon_id="hack1")
        config2 = DevpostConfig(project_id="project2", hackathon_id="hack2")
        
        connection1 = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config1,
            created_at=datetime(2023, 1, 1)
        )
        
        connection2 = ProjectConnection(
            local_path=project_manager.project_root / "other",
            devpost_project_id="project2",
            hackathon_id="hack2",
            configuration=config2,
            created_at=datetime(2023, 1, 2)
        )
        
        # Create the other directory
        (project_manager.project_root / "other").mkdir(exist_ok=True)
        
        # Set initial active project
        project_manager._current_connection = connection1
        project_manager._active_project_id = "project1"
        
        metadata = ProjectMetadata(
            title="Test Project",
            description="A test project with sufficient description length for validation",
            repository_url="https://github.com/user/test"
        )
        validation = ValidationResult(is_valid=True)
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection1, connection2]):
            with patch.object(project_manager, 'get_project_metadata', return_value=metadata):
                with patch.object(project_manager, 'validate_project', return_value=validation):
                    # Get status for project2 (not the active one)
                    status = project_manager.get_project_status("project2")
                    
                    # Verify we got project2's status
                    assert status['project_id'] == "project2"
                    
                    # Verify active context is preserved
                    assert project_manager._active_project_id == "project1"
                    assert project_manager._current_connection == connection1
    
    def test_detect_project_conflicts_comprehensive(self, project_manager, tmp_path):
        """Test comprehensive conflict detection scenarios."""
        # Create test paths
        path1 = tmp_path / "path1"
        path2 = tmp_path / "path2"
        path1.mkdir()
        path2.mkdir()
        
        config1 = DevpostConfig(project_id="project1", hackathon_id="hack1")
        config2 = DevpostConfig(project_id="project1", hackathon_id="hack1")  # Same project and hackathon
        config3 = DevpostConfig(project_id="project3", hackathon_id="hack1")
        
        # Duplicate project ID conflict
        connection1 = ProjectConnection(
            local_path=path1,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config1
        )
        
        connection2 = ProjectConnection(
            local_path=path2,
            devpost_project_id="project1",  # Same project ID
            hackathon_id="hack1",
            configuration=config2
        )
        
        # Missing path conflict
        connection3 = ProjectConnection(
            local_path=Path("/nonexistent"),
            devpost_project_id="project3",
            hackathon_id="hack1",
            configuration=config3
        )
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection1, connection2, connection3]):
            conflicts = project_manager.detect_project_conflicts()
            
            # Should detect both duplicate project ID and missing path
            conflict_types = [c['type'] for c in conflicts]
            assert 'duplicate_project_id' in conflict_types
            assert 'missing_path' in conflict_types
            
            # Check duplicate project ID conflict details
            duplicate_conflict = next(c for c in conflicts if c['type'] == 'duplicate_project_id')
            assert duplicate_conflict['project_id'] == 'project1'
            assert str(path1) in duplicate_conflict['paths']
            assert str(path2) in duplicate_conflict['paths']
            
            # Check missing path conflict details
            missing_conflict = next(c for c in conflicts if c['type'] == 'missing_path')
            assert missing_conflict['project_id'] == 'project3'
            assert missing_conflict['path'] == '/nonexistent'
    
    def test_resolve_conflict_duplicate_hackathon_path(self, project_manager):
        """Test resolving duplicate hackathon path conflicts."""
        with patch.object(project_manager.config_manager, 'list_connections') as mock_list:
            with patch.object(project_manager.config_manager, 'remove_connection') as mock_remove:
                config1 = DevpostConfig(project_id="project1", hackathon_id="hack1")
                config2 = DevpostConfig(project_id="project2", hackathon_id="hack1")
                
                connection1 = ProjectConnection(
                    local_path=Path("/same/path"),
                    devpost_project_id="project1",
                    hackathon_id="hack1",
                    configuration=config1
                )
                
                connection2 = ProjectConnection(
                    local_path=Path("/same/path"),  # Same path, same hackathon
                    devpost_project_id="project2",
                    hackathon_id="hack1",
                    configuration=config2
                )
                
                mock_list.return_value = [connection1, connection2]
                
                result = project_manager.resolve_conflict(
                    'duplicate_hackathon_path',
                    'keep_one',
                    hackathon_id='hack1',
                    path='/same/path',
                    keep_project_id='project1'
                )
                
                assert result is True
                mock_remove.assert_called_once_with(Path("/same/path"))
    
    def test_resolve_conflict_missing_path_update(self, project_manager):
        """Test resolving missing path conflict by updating path."""
        config = DevpostConfig(project_id="project1", hackathon_id="hack1")
        connection = ProjectConnection(
            local_path=Path("/old/path"),
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config
        )
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection]):
            with patch.object(project_manager.config_manager, 'remove_connection') as mock_remove:
                with patch.object(project_manager.config_manager, 'save_connection') as mock_save:
                    result = project_manager.resolve_conflict(
                        'missing_path',
                        'update_path',
                        project_id='project1',
                        new_path='/new/path'
                    )
                    
                    assert result is True
                    mock_remove.assert_called_once_with(Path("/old/path"))
                    mock_save.assert_called_once()
                    
                    # Verify the connection was updated
                    saved_connection = mock_save.call_args[0][0]
                    assert saved_connection.local_path == Path("/new/path")
    
    def test_resolve_conflict_invalid_parameters(self, project_manager):
        """Test error handling for invalid conflict resolution parameters."""
        # Missing required parameters for keep_one resolution
        with pytest.raises(ConfigurationError, match="project_id and keep_path required"):
            project_manager.resolve_conflict(
                'duplicate_project_id',
                'keep_one'
            )
        
        # Missing required parameters for update_path resolution
        with pytest.raises(ConfigurationError, match="project_id and new_path required"):
            project_manager.resolve_conflict(
                'missing_path',
                'update_path',
                project_id='project1'
            )
        
        # Missing required parameters for remove resolution
        with pytest.raises(ConfigurationError, match="project_id required for remove resolution"):
            project_manager.resolve_conflict(
                'missing_path',
                'remove'
            )
    
    def test_disconnect_project_not_active(self, project_manager):
        """Test disconnecting a project that is not currently active."""
        config1 = DevpostConfig(project_id="project1", hackathon_id="hack1")
        config2 = DevpostConfig(project_id="project2", hackathon_id="hack2")
        
        connection1 = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config1
        )
        
        connection2 = ProjectConnection(
            local_path=project_manager.project_root / "other",
            devpost_project_id="project2",
            hackathon_id="hack2",
            configuration=config2
        )
        
        # Set project1 as active
        project_manager._current_connection = connection1
        project_manager._active_project_id = "project1"
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection1, connection2]):
            with patch.object(project_manager.config_manager, 'remove_connection', return_value=True):
                # Disconnect project2 (not active)
                result = project_manager.disconnect_project("project2")
                
                assert result is True
                # Active project should remain unchanged
                assert project_manager._current_connection == connection1
                assert project_manager._active_project_id == "project1"
    
    def test_multi_project_workflow_integration(self, project_manager, tmp_path):
        """Test complete multi-project workflow integration."""
        # Create multiple project directories
        project1_dir = tmp_path / "project1"
        project2_dir = tmp_path / "project2"
        project1_dir.mkdir()
        project2_dir.mkdir()
        
        # Create README files for each project
        (project1_dir / "README.md").write_text("# Project 1\nFirst test project")
        (project2_dir / "README.md").write_text("# Project 2\nSecond test project")
        
        # Create project managers for each directory
        manager1 = DevpostProjectManager(project1_dir)
        manager2 = DevpostProjectManager(project2_dir)
        
        # Connect both projects
        with patch.object(manager1.config_manager, 'save_connection'):
            connection1 = manager1.connect_to_devpost("project1", "hack1")
        
        with patch.object(manager2.config_manager, 'save_connection'):
            connection2 = manager2.connect_to_devpost("project2", "hack2")
        
        # Mock the connections for listing
        all_connections = [connection1, connection2]
        
        with patch.object(manager1.config_manager, 'list_connections', return_value=all_connections):
            # List all projects from manager1
            projects = manager1.list_projects()
            assert len(projects) == 2
            
            project_ids = [p['project_id'] for p in projects]
            assert 'project1' in project_ids
            assert 'project2' in project_ids
            
            # Switch to project2
            manager1.switch_project("project2")
            assert manager1._active_project_id == "project2"
            
            # Get status for both projects
            status1 = manager1.get_project_status("project1")
            status2 = manager1.get_project_status("project2")
            
            assert status1['project_id'] == "project1"
            assert status2['project_id'] == "project2"
            
            # Detect conflicts (should be none)
            conflicts = manager1.detect_project_conflicts()
            assert len(conflicts) == 0
    
    def test_active_project_isolation(self, project_manager):
        """Test that operations only affect the active project (Requirement 6.3)."""
        config1 = DevpostConfig(project_id="project1", hackathon_id="hack1", sync_enabled=True)
        config2 = DevpostConfig(project_id="project2", hackathon_id="hack2", sync_enabled=False)
        
        connection1 = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            configuration=config1
        )
        
        connection2 = ProjectConnection(
            local_path=project_manager.project_root / "other",
            devpost_project_id="project2",
            hackathon_id="hack2",
            configuration=config2
        )
        
        # Set project1 as active
        project_manager._current_connection = connection1
        project_manager._active_project_id = "project1"
        
        # Get config should return active project's config
        active_config = project_manager.get_project_config()
        assert active_config.project_id == "project1"
        assert active_config.sync_enabled is True
        
        # Switch to project2
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection1, connection2]):
            # Create the other directory
            (project_manager.project_root / "other").mkdir(exist_ok=True)
            
            project_manager.switch_project("project2")
            
            # Now config should be for project2
            active_config = project_manager.get_project_config()
            assert active_config.project_id == "project2"
            assert active_config.sync_enabled is False
    
    def test_project_listing_includes_required_fields(self, project_manager):
        """Test that project listing includes all required fields (Requirement 6.4)."""
        config = DevpostConfig(project_id="project1", hackathon_id="hack1")
        connection = ProjectConnection(
            local_path=project_manager.project_root,
            devpost_project_id="project1",
            hackathon_id="hack1",
            sync_status=SyncStatus.COMPLETED,
            configuration=config,
            last_sync=datetime(2023, 1, 1),
            created_at=datetime(2023, 1, 1)
        )
        
        with patch.object(project_manager.config_manager, 'list_connections', return_value=[connection]):
            projects = project_manager.list_projects()
            
            assert len(projects) == 1
            project_info = projects[0]
            
            # Verify all required fields are present
            required_fields = [
                'project_id', 'hackathon_id', 'local_path', 'sync_status',
                'last_sync', 'created_at', 'is_active', 'sync_enabled'
            ]
            
            for field in required_fields:
                assert field in project_info, f"Missing required field: {field}"
            
            # Verify field values
            assert project_info['project_id'] == "project1"
            assert project_info['hackathon_id'] == "hack1"
            assert project_info['sync_status'] == "completed"
            assert project_info['sync_enabled'] is True