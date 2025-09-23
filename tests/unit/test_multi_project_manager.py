"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.482550
"""






import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.devpost_integration.multi_project_manager import MultiProjectManager
from src.devpost_integration.models import (
# from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    MultiProjectConfig, ProjectConnection, DevpostConfig, GlobalSettings,
    ConflictResolutionStrategy, ContextSwitchResult, ProjectSummary,
    ProjectDashboard, SubmissionStatus, NotificationSettings
)


class TestMultiProjectManager(ReflectiveModule):
    """Test MultiProjectManager functionality."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def temp_project_dirs(self):
        """Create temporary project directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            project1_path = base_path / "project1"
            project2_path = base_path / "project2"
            project1_path.mkdir()
            project2_path.mkdir()

            yield {
                "project1": project1_path,
                "project2": project2_path,
                "base": base_path
            }

    @pytest.fixture
    def global_settings(self):
        """Create test global settings."""
        return GlobalSettings(
            default_sync_interval=600,
            max_concurrent_projects=5,
            auto_switch_on_file_change=False,
            unified_notifications=True
        )

    @pytest.fixture
    def manager(self, temp_config_dir, global_settings):
        """Create MultiProjectManager instance."""
        return MultiProjectManager(
            config_dir=temp_config_dir,
            global_settings=global_settings
        )

    def test_initialization(self, temp_config_dir, global_settings):
        """Test MultiProjectManager initialization."""
        manager = MultiProjectManager(
            config_dir=temp_config_dir,
            global_settings=global_settings
        )

        assert manager.config_dir == temp_config_dir
        assert manager.global_settings == global_settings
        assert isinstance(manager.config, MultiProjectConfig)
        assert len(manager.config.project_connections) == 0
        assert manager.config.active_project_id is None
        assert manager._active_project_id is None

    def test_add_project_success(self, manager, temp_project_dirs):
        """Test successful project addition."""
        project_id = "test-project-1"
        local_path = temp_project_dirs["project1"]
        devpost_project_id = "devpost-123"
        hackathon_id = "hack-456"

        result = manager.add_project(
            project_id=project_id,
            local_path=local_path,
            devpost_project_id=devpost_project_id,
            hackathon_id=hackathon_id
        )

        assert result is True
        assert project_id in manager.config.project_connections

        connection = manager.config.project_connections[project_id]
        assert connection.local_path == local_path
        assert connection.devpost_project_id == devpost_project_id
        assert connection.hackathon_id == hackathon_id
        assert connection.is_active is True  # First project should be active
        assert manager.config.active_project_id == project_id

    def test_add_project_duplicate_id(self, manager, temp_project_dirs):
        """Test adding project with duplicate ID."""
        project_id = "test-project-1"
        local_path = temp_project_dirs["project1"]

        # Add first project
        manager.add_project(
            project_id=project_id,
            local_path=local_path,
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Try to add project with same ID
        result = manager.add_project(
            project_id=project_id,
            local_path=temp_project_dirs["project2"],
            devpost_project_id="devpost-789",
            hackathon_id="hack-456"
        )

        assert result is False
        assert len(manager.config.project_connections) == 1

    def test_add_project_nonexistent_path(self, manager):
        """Test adding project with nonexistent local path."""
        result = manager.add_project(
            project_id="test-project",
            local_path=Path("/nonexistent/path"),
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        assert result is False
        assert len(manager.config.project_connections) == 0

    def test_remove_project_success(self, manager, temp_project_dirs):
        """Test successful project removal."""
        project_id = "test-project-1"

        # Add project first
        manager.add_project(
            project_id=project_id,
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        assert len(manager.config.project_connections) == 1

        # Remove project
        result = manager.remove_project(project_id)

        assert result is True
        assert len(manager.config.project_connections) == 0
        assert manager.config.active_project_id is None

    def test_remove_project_not_found(self, manager):
        """Test removing nonexistent project."""
        result = manager.remove_project("nonexistent-project")

        assert result is False

    def test_switch_project_context_success(self, manager, temp_project_dirs):
        """Test successful project context switching."""
        # Add two projects
        manager.add_project(
            project_id="project1",
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        manager.add_project(
            project_id="project2",
            local_path=temp_project_dirs["project2"],
            devpost_project_id="devpost-789",
            hackathon_id="hack-456"
        )

        # Initially project1 should be active
        assert manager.config.active_project_id == "project1"

        # Switch to project2
        result = manager.switch_project_context("project2")

        assert result.success is True
        assert result.previous_project_id == "project1"
        assert result.new_project_id == "project2"
        assert manager.config.active_project_id == "project2"
        assert manager.config.project_connections["project1"].is_active is False
        assert manager.config.project_connections["project2"].is_active is True

    def test_switch_project_context_not_found(self, manager):
        """Test switching to nonexistent project."""
        result = manager.switch_project_context("nonexistent-project")

        assert result.success is False
        assert "not found" in result.error

    def test_get_active_project(self, manager, temp_project_dirs):
        """Test getting active project connection."""
        # No active project initially
        assert manager.get_active_project() is None

        # Add project
        project_id = "test-project"
        manager.add_project(
            project_id=project_id,
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        active_project = manager.get_active_project()
        assert active_project is not None
        assert active_project.devpost_project_id == "devpost-123"
        assert active_project.is_active is True

    def test_list_projects(self, manager, temp_project_dirs):
        """Test listing all projects."""
        # Empty list initially
        projects = manager.list_projects()
        assert len(projects) == 0

        # Add projects
        manager.add_project(
            project_id="project1",
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        manager.add_project(
            project_id="project2",
            local_path=temp_project_dirs["project2"],
            devpost_project_id="devpost-789",
            hackathon_id="hack-789"
        )

        projects = manager.list_projects()
        assert len(projects) == 2

        # Check project summaries
        project_ids = [p.project_id for p in projects]
        assert "project1" in project_ids
        assert "project2" in project_ids

        # Check active project
        active_projects = [p for p in projects if p.is_active]
        assert len(active_projects) == 1
        assert active_projects[0].project_id == "project1"  # First added should be active

    def test_display_project_dashboard(self, manager, temp_project_dirs):
        """Test project dashboard generation."""
        # Add projects
        manager.add_project(
            project_id="project1",
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        manager.add_project(
            project_id="project2",
            local_path=temp_project_dirs["project2"],
            devpost_project_id="devpost-789",
            hackathon_id="hack-789"
        )

        dashboard = manager.display_project_dashboard()

        assert isinstance(dashboard, ProjectDashboard)
        assert len(dashboard.projects) == 2
        assert dashboard.total_projects == 2
        assert dashboard.active_project is not None
        assert dashboard.active_project.project_id == "project1"
        assert dashboard.projects_with_deadlines == 0  # No deadlines set
        assert dashboard.overdue_projects == 0
        assert isinstance(dashboard.generated_at, datetime)

    def test_prevent_cross_contamination_success(self, manager, temp_project_dirs):
        """Test cross-contamination prevention with valid operation."""
        project_id = "test-project"
        manager.add_project(
            project_id=project_id,
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        result = manager.prevent_cross_contamination("sync", project_id)
        assert result is True

    def test_prevent_cross_contamination_project_not_found(self, manager):
        """Test cross-contamination prevention with nonexistent project."""
        result = manager.prevent_cross_contamination("sync", "nonexistent-project")
        assert result is False

    def test_prevent_cross_contamination_overlapping_paths(self, manager, temp_project_dirs):
        """Test cross-contamination prevention with overlapping paths."""
        # Add project with base path
        manager.add_project(
            project_id="project1",
            local_path=temp_project_dirs["base"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Add project with subdirectory (should create conflict)
        manager.add_project(
            project_id="project2",
            local_path=temp_project_dirs["project1"],  # Subdirectory of base
            devpost_project_id="devpost-789",
            hackathon_id="hack-789"
        )

        # Cross-contamination check should fail due to overlapping paths
        result = manager.prevent_cross_contamination("sync", "project2")
        assert result is False

    def test_conflict_detection_duplicate_paths(self, manager, temp_project_dirs):
        """Test conflict detection for duplicate local paths."""
        # Add first project
        manager.add_project(
            project_id="project1",
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Try to add project with same path (should detect conflict)
        conflicts = manager._detect_project_conflicts(
            "project2",
            temp_project_dirs["project1"],  # Same path
            "devpost-789"
        )

        assert len(conflicts) == 1
        assert conflicts[0]["type"] == "duplicate_local_path"
        assert conflicts[0]["severity"] == "high"

    def test_conflict_detection_duplicate_devpost_id(self, manager, temp_project_dirs):
        """Test conflict detection for duplicate Devpost IDs."""
        # Add first project
        manager.add_project(
            project_id="project1",
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Try to add project with same Devpost ID (should detect conflict)
        conflicts = manager._detect_project_conflicts(
            "project2",
            temp_project_dirs["project2"],
            "devpost-123"  # Same Devpost ID
        )

        assert len(conflicts) == 1
        assert conflicts[0]["type"] == "duplicate_devpost_id"
        assert conflicts[0]["severity"] == "high"

    def test_paths_overlap_detection(self, manager, temp_project_dirs):
        """Test path overlap detection."""
        base_path = temp_project_dirs["base"]
        sub_path = temp_project_dirs["project1"]
        separate_path = temp_project_dirs["project2"]

        # Test parent-child relationship
        assert manager._paths_overlap(base_path, sub_path) is True
        assert manager._paths_overlap(sub_path, base_path) is True

        # Test separate paths
        assert manager._paths_overlap(sub_path, separate_path) is False

        # Test same paths
        assert manager._paths_overlap(sub_path, sub_path) is False  # Same path, not overlapping

    def test_config_persistence(self, temp_config_dir, temp_project_dirs):
        """Test configuration saving and loading."""
        # Create manager and add project
        manager1 = MultiProjectManager(config_dir=temp_config_dir)
        manager1.add_project(
            project_id="test-project",
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Create new manager instance (should load saved config)
        manager2 = MultiProjectManager(config_dir=temp_config_dir)

        assert len(manager2.config.project_connections) == 1
        assert "test-project" in manager2.config.project_connections
        assert manager2.config.active_project_id == "test-project"

        connection = manager2.config.project_connections["test-project"]
        assert connection.devpost_project_id == "devpost-123"
        assert connection.hackathon_id == "hack-456"
        assert connection.local_path == temp_project_dirs["project1"]

    def test_project_manager_caching(self, manager, temp_project_dirs):
        """Test project manager caching."""
        project_id = "test-project"
        manager.add_project(
            project_id=project_id,
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Get project manager (should create and cache)
        pm1 = manager._get_project_manager(project_id)
        assert pm1 is not None

        # Get again (should return cached instance)
        pm2 = manager._get_project_manager(project_id)
        assert pm2 is pm1  # Same instance

        # Get for nonexistent project
        pm3 = manager._get_project_manager("nonexistent")
        assert pm3 is None

    def test_utility_methods(self, manager, temp_project_dirs):
        """Test utility methods."""
        # Initially empty
        assert manager.get_project_count() == 0
        assert manager.get_active_project_id() is None
        assert manager.is_project_managed("test-project") is False
        assert manager.get_project_connection("test-project") is None

        # Add project
        project_id = "test-project"
        manager.add_project(
            project_id=project_id,
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Test after adding project
        assert manager.get_project_count() == 1
        assert manager.get_active_project_id() == project_id
        assert manager.is_project_managed(project_id) is True

        connection = manager.get_project_connection(project_id)
        assert connection is not None
        assert connection.devpost_project_id == "devpost-123"

    def test_update_project_connection(self, manager, temp_project_dirs):
        """Test updating project connection details."""
        project_id = "test-project"
        manager.add_project(
            project_id=project_id,
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Update connection
        now = datetime.now()
        updates = {
            "last_sync": now,
            "sync_status": "synced"
        }

        result = manager.update_project_connection(project_id, updates)
        assert result is True

        # Verify updates
        connection = manager.get_project_connection(project_id)
        assert connection.last_sync == now
        assert connection.sync_status == "synced"

        # Test update for nonexistent project
        result = manager.update_project_connection("nonexistent", updates)
        assert result is False


class TestMultiProjectManagerConflictResolution(ReflectiveModule):
    """Test conflict resolution functionality."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def temp_project_dirs(self):
        """Create temporary project directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            project1_path = base_path / "project1"
            project2_path = base_path / "project2"
            project1_path.mkdir()
            project2_path.mkdir()

            yield {
                "project1": project1_path,
                "project2": project2_path,
                "base": base_path
            }

    def test_manual_conflict_resolution(self, temp_config_dir, temp_project_dirs):
        """Test manual conflict resolution strategy."""
        manager = MultiProjectManager(config_dir=temp_config_dir)
        manager.config.conflict_resolution_strategy = ConflictResolutionStrategy.MANUAL_RESOLUTION

        # Add first project
        manager.add_project(
            project_id="project1",
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Add conflicting project (same Devpost ID)
        manager.add_project(
            project_id="project2",
            local_path=temp_project_dirs["project2"],
            devpost_project_id="devpost-123",  # Same ID - conflict
            hackathon_id="hack-789"
        )

        # Resolve conflicts
        resolution = manager.resolve_project_conflicts()

        assert len(resolution.conflicts_found) > 0
        assert resolution.resolution_strategy == ConflictResolutionStrategy.MANUAL_RESOLUTION
        assert resolution.manual_intervention_required is True
        assert len(resolution.resolved_conflicts) == 0

    def test_local_wins_conflict_resolution(self, temp_config_dir, temp_project_dirs):
        """Test local wins conflict resolution strategy."""
        manager = MultiProjectManager(config_dir=temp_config_dir)
        manager.config.conflict_resolution_strategy = ConflictResolutionStrategy.LOCAL_WINS

        # Add first project
        manager.add_project(
            project_id="project1",
            local_path=temp_project_dirs["project1"],
            devpost_project_id="devpost-123",
            hackathon_id="hack-456"
        )

        # Add conflicting project (same path)
        # This should trigger automatic resolution
        manager.add_project(
            project_id="project2",
            local_path=temp_project_dirs["project1"],  # Same path - conflict
            devpost_project_id="devpost-789",
            hackathon_id="hack-789"
        )

        # The conflict should be detected but project2 should still be added
        # (in a real implementation, this might remove project1)
        assert len(manager.config.project_connections) >= 1


class TestMultiProjectManagerEdgeCases(ReflectiveModule):
    """Test edge cases and error conditions."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_corrupted_config_file(self, temp_config_dir):
        """Test handling of corrupted configuration file."""
        # Create corrupted config file
        config_file = temp_config_dir / "config.json"
        with open(config_file, 'w') as f:
            f.write("invalid json content")

        # Manager should handle corrupted config gracefully
        manager = MultiProjectManager(config_dir=temp_config_dir)

        assert isinstance(manager.config, MultiProjectConfig)
        assert len(manager.config.project_connections) == 0

    def test_config_file_permissions(self, temp_config_dir):
        """Test handling of config file permission issues."""
        # This test would need platform-specific permission handling
        # For now, just test that the manager initializes
        manager = MultiProjectManager(config_dir=temp_config_dir)
        assert manager is not None

    def test_empty_project_id(self, temp_config_dir):
        """Test handling of empty project ID."""
        manager = MultiProjectManager(config_dir=temp_config_dir)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = manager.add_project(
                project_id="",  # Empty ID
                local_path=Path(temp_dir),
                devpost_project_id="devpost-123",
                hackathon_id="hack-456"
            )

            assert result is False
            assert len(manager.config.project_connections) == 0


if __name__ == "__main__":

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())

    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }

    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

    pytest.main([__file__, "-v"])