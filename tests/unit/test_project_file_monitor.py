"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.466446
"""






import pytest
import tempfile
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.devpost_integration.file_monitor import ProjectFileMonitor, ProjectFileEventHandler
from src.devpost_integration.models import (
# from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    FileChangeEvent, ChangeType, ContentType, DevpostConfig,
    SyncOperation, SyncOperationType
)


class TestProjectFileMonitor(ReflectiveModule):
    """Test ProjectFileMonitor functionality."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create test files
            (project_path / "README.md").write_text("# Test Project")
            (project_path / "main.py").write_text("print('hello')")
            (project_path / "config.json").write_text('{"test": true}')
            (project_path / "image.png").touch()

            # Create subdirectory
            sub_dir = project_path / "src"
            sub_dir.mkdir()
            (sub_dir / "module.py").write_text("def test(): pass")

            yield project_path

    @pytest.fixture
    def mock_sync_manager(self):
        """Create mock sync manager."""
        sync_manager = Mock()
        sync_manager.queue_sync_operation = Mock()
        return sync_manager

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return DevpostConfig(
            project_id="test-project",
            hackathon_id="test-hackathon",
            sync_enabled=True,
            watch_patterns=["*.md", "*.py", "*.json", "*.png"],
            auto_sync_media=True
        )

    @pytest.fixture
    def monitor(self, temp_project_dir, mock_sync_manager, config):
        """Create ProjectFileMonitor instance."""
        return ProjectFileMonitor(
            project_path=temp_project_dir,
            sync_manager=mock_sync_manager,
            config=config
        )

    def test_initialization(self, temp_project_dir, mock_sync_manager, config):
        """Test ProjectFileMonitor initialization."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            sync_manager=mock_sync_manager,
            config=config
        )

        assert monitor.project_path == temp_project_dir.resolve()
        assert monitor.sync_manager == mock_sync_manager
        assert monitor.config == config
        assert not monitor._is_monitoring
        assert monitor._observer is None
        assert len(monitor._change_queue) == 0
        assert len(monitor.watch_patterns) > 0
        assert len(monitor.ignore_patterns) > 0

    def test_default_watch_patterns(self, temp_project_dir):
        """Test default watch patterns when no config provided."""
        # Create monitor without config to get defaults
        monitor = ProjectFileMonitor(project_path=temp_project_dir, config=None)

        patterns = monitor.watch_patterns
        # These are the default patterns from DevpostConfig
        assert "*.md" in patterns
        assert "*.py" in patterns
        assert "*.js" in patterns
        assert "*.json" in patterns
        assert "*.yml" in patterns
        assert "*.yaml" in patterns

    def test_file_monitor_default_patterns(self, temp_project_dir):
        """Test file monitor's own default patterns when config has empty patterns."""
        # Create config with empty watch patterns to trigger file monitor defaults
        empty_config = DevpostConfig(
            project_id="test",
            hackathon_id="test",
            watch_patterns=[]  # Empty patterns
        )
        monitor = ProjectFileMonitor(project_path=temp_project_dir, config=empty_config)

        patterns = monitor.watch_patterns
        # These should be the file monitor's comprehensive default patterns
        assert "*.md" in patterns
        assert "*.py" in patterns
        assert "*.json" in patterns
        assert "*.png" in patterns
        assert "*.jpg" in patterns
        assert "README*" in patterns

    def test_ignore_patterns(self, monitor):
        """Test ignore patterns configuration."""
        patterns = monitor.ignore_patterns

        assert "*.pyc" in patterns
        assert "__pycache__/*" in patterns
        assert ".git/*" in patterns
        assert "node_modules/*" in patterns
        assert ".DS_Store" in patterns

    def test_content_type_mappings(self, monitor):
        """Test content type detection mappings."""
        mappings = monitor.content_type_mappings

        assert mappings[".md"] == ContentType.DOCUMENTATION
        assert mappings[".py"] == ContentType.SOURCE_CODE
        assert mappings[".png"] == ContentType.MEDIA
        assert mappings[".json"] == ContentType.CONFIGURATION

    def test_start_monitoring_success(self, monitor):
        """Test successful monitoring start."""
        assert not monitor._is_monitoring

        monitor.start_monitoring()

        assert monitor._is_monitoring
        assert monitor._observer is not None
        assert monitor._event_handler is not None

        # Clean up
        monitor.stop_monitoring()

    def test_start_monitoring_already_active(self, monitor):
        """Test starting monitoring when already active."""
        monitor.start_monitoring()
        assert monitor._is_monitoring

        # Try to start again
        monitor.start_monitoring()  # Should not raise error
        assert monitor._is_monitoring

        # Clean up
        monitor.stop_monitoring()

    def test_start_monitoring_invalid_path(self, mock_sync_manager, config):
        """Test starting monitoring with invalid path."""
        invalid_path = Path("/nonexistent/path")
        monitor = ProjectFileMonitor(
            project_path=invalid_path,
            sync_manager=mock_sync_manager,
            config=config
        )

        with pytest.raises(ValueError, match="Project path does not exist"):
            monitor.start_monitoring()

    def test_stop_monitoring(self, monitor):
        """Test stopping monitoring."""
        monitor.start_monitoring()
        assert monitor._is_monitoring

        monitor.stop_monitoring()

        assert not monitor._is_monitoring
        assert monitor._observer is None
        assert monitor._event_handler is None
        assert len(monitor._debounce_timers) == 0

    def test_stop_monitoring_not_active(self, monitor):
        """Test stopping monitoring when not active."""
        assert not monitor._is_monitoring

        monitor.stop_monitoring()  # Should not raise error
        assert not monitor._is_monitoring

    def test_context_manager(self, monitor):
        """Test using monitor as context manager."""
        assert not monitor._is_monitoring

        with monitor:
            assert monitor._is_monitoring

        assert not monitor._is_monitoring

    def test_should_process_change_watch_patterns(self, monitor, temp_project_dir):
        """Test change processing based on watch patterns."""
        # Create mock event
        mock_event = Mock()
        mock_event.event_type = 'modified'

        # Test matching pattern
        md_file = temp_project_dir / "test.md"
        md_file.touch()
        assert monitor._should_process_change(md_file, mock_event) is True

        # Test non-matching pattern
        exe_file = temp_project_dir / "test.exe"
        exe_file.touch()
        assert monitor._should_process_change(exe_file, mock_event) is False

        # Test special project files
        readme_file = temp_project_dir / "README.txt"
        readme_file.touch()
        assert monitor._should_process_change(readme_file, mock_event) is True

    def test_should_process_change_ignore_patterns(self, monitor, temp_project_dir):
        """Test change processing with ignore patterns."""
        mock_event = Mock()
        mock_event.event_type = 'modified'

        # Test ignored file
        pyc_file = temp_project_dir / "test.pyc"
        pyc_file.touch()
        assert monitor._should_process_change(pyc_file, mock_event) is False

        # Test ignored directory
        git_dir = temp_project_dir / ".git"
        git_dir.mkdir()
        git_file = git_dir / "config"
        git_file.touch()
        assert monitor._should_process_change(git_file, mock_event) is False

    def test_should_process_change_outside_project(self, monitor):
        """Test change processing for files outside project."""
        mock_event = Mock()
        mock_event.event_type = 'modified'

        # File outside project directory
        outside_file = Path("/tmp/outside.md")
        assert monitor._should_process_change(outside_file, mock_event) is False

    def test_matches_pattern(self, monitor):
        """Test pattern matching functionality."""
        assert monitor._matches_pattern("test.py", "*.py") is True
        assert monitor._matches_pattern("test.js", "*.py") is False
        assert monitor._matches_pattern("README.md", "README*") is True
        # fnmatch does match paths with directories, so this should be True
        assert monitor._matches_pattern("src/test.py", "*.py") is True

    def test_is_path_within_project(self, monitor, temp_project_dir):
        """Test path validation within project."""
        # Path within project
        internal_path = temp_project_dir / "src" / "test.py"
        assert monitor._is_path_within_project(internal_path) is True

        # Path outside project
        external_path = Path("/tmp/external.py")
        assert monitor._is_path_within_project(external_path) is False

    def test_get_change_type(self, monitor):
        """Test change type conversion."""
        # Test different event types
        mock_event = Mock()

        mock_event.event_type = 'created'
        assert monitor._get_change_type(mock_event) == ChangeType.CREATED

        mock_event.event_type = 'modified'
        assert monitor._get_change_type(mock_event) == ChangeType.MODIFIED

        mock_event.event_type = 'deleted'
        assert monitor._get_change_type(mock_event) == ChangeType.DELETED

        mock_event.event_type = 'moved'
        assert monitor._get_change_type(mock_event) == ChangeType.RENAMED

        mock_event.event_type = 'unknown'
        assert monitor._get_change_type(mock_event) == ChangeType.MODIFIED  # Default

    def test_get_content_type(self, monitor, temp_project_dir):
        """Test content type detection."""
        # Test by extension
        assert monitor._get_content_type(Path("test.md")) == ContentType.DOCUMENTATION
        assert monitor._get_content_type(Path("test.py")) == ContentType.SOURCE_CODE
        assert monitor._get_content_type(Path("test.png")) == ContentType.MEDIA
        assert monitor._get_content_type(Path("test.json")) == ContentType.CONFIGURATION

        # Test by filename
        assert monitor._get_content_type(Path("README")) == ContentType.DOCUMENTATION
        assert monitor._get_content_type(Path("CHANGELOG")) == ContentType.DOCUMENTATION
        assert monitor._get_content_type(Path("VERSION")) == ContentType.RELEASE

        # Test unknown extension
        assert monitor._get_content_type(Path("test.unknown")) == ContentType.SOURCE_CODE

    def test_affects_sync(self, monitor, temp_project_dir):
        """Test sync trigger detection."""
        # Documentation always triggers sync
        assert monitor._affects_sync(Path("README.md"), ContentType.DOCUMENTATION) is True

        # Media files trigger sync
        assert monitor._affects_sync(Path("image.png"), ContentType.MEDIA) is True

        # Release files trigger sync
        assert monitor._affects_sync(Path("VERSION"), ContentType.RELEASE) is True

        # Important project files
        assert monitor._affects_sync(Path("README.txt"), ContentType.SOURCE_CODE) is True
        assert monitor._affects_sync(Path("LICENSE"), ContentType.SOURCE_CODE) is True

        # Configuration files
        assert monitor._affects_sync(Path("package.json"), ContentType.CONFIGURATION) is True

        # Source code (depends on config)
        assert monitor._affects_sync(Path("main.py"), ContentType.SOURCE_CODE) is True  # sync_enabled=True

    def test_get_sync_operation_type(self, monitor):
        """Test sync operation type determination."""
        # Media change
        media_event = FileChangeEvent(
            file_path=Path("image.png"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.MEDIA
        )
        assert monitor._get_sync_operation_type(media_event) == SyncOperationType.UPLOAD_MEDIA

        # Documentation change
        doc_event = FileChangeEvent(
            file_path=Path("README.md"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.DOCUMENTATION
        )
        assert monitor._get_sync_operation_type(doc_event) == SyncOperationType.UPDATE_DESCRIPTION

        # Other changes
        code_event = FileChangeEvent(
            file_path=Path("main.py"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.SOURCE_CODE
        )
        assert monitor._get_sync_operation_type(code_event) == SyncOperationType.UPDATE_METADATA

    def test_get_target_field(self, monitor):
        """Test target field determination."""
        # README file
        readme_event = FileChangeEvent(
            file_path=Path("README.md"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.DOCUMENTATION
        )
        assert monitor._get_target_field(readme_event) == 'description'

        # Media file
        media_event = FileChangeEvent(
            file_path=Path("image.png"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.MEDIA
        )
        assert monitor._get_target_field(media_event) == 'media'

        # Changelog
        changelog_event = FileChangeEvent(
            file_path=Path("CHANGELOG.md"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.DOCUMENTATION
        )
        assert monitor._get_target_field(changelog_event) == 'changelog'

        # Other files
        other_event = FileChangeEvent(
            file_path=Path("main.py"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.SOURCE_CODE
        )
        assert monitor._get_target_field(other_event) == 'metadata'

    def test_debounce_change(self, monitor):
        """Test change debouncing functionality."""
        change_event = FileChangeEvent(
            file_path=Path("test.py"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.SOURCE_CODE,
            affects_sync=True
        )

        # Set short debounce delay for testing
        monitor.debounce_delay = 0.1

        # Trigger debounce
        monitor._debounce_change(change_event)

        # Check that timer was created
        file_key = str(change_event.file_path)
        assert file_key in monitor._debounce_timers
        assert file_key in monitor._recent_changes

        # Wait for debounce to complete
        time.sleep(0.2)

        # Check that change was processed
        assert len(monitor._change_queue) > 0
        assert file_key not in monitor._debounce_timers

    def test_debounce_multiple_changes_same_file(self, monitor):
        """Test debouncing multiple changes to the same file."""
        monitor.debounce_delay = 0.1

        file_path = Path("test.py")

        # Create multiple change events for same file
        change1 = FileChangeEvent(
            file_path=file_path,
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.SOURCE_CODE
        )

        change2 = FileChangeEvent(
            file_path=file_path,
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.SOURCE_CODE
        )

        # Trigger debounce for both changes
        monitor._debounce_change(change1)
        time.sleep(0.05)  # Small delay
        monitor._debounce_change(change2)

        # Wait for debounce to complete
        time.sleep(0.2)

        # Should only have one change in queue (the latest one)
        assert len(monitor._change_queue) == 1
        assert monitor._change_queue[0] == change2

    def test_get_recent_changes(self, monitor):
        """Test getting recent changes."""
        # Add some changes to queue
        change1 = FileChangeEvent(
            file_path=Path("test1.py"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.SOURCE_CODE
        )

        change2 = FileChangeEvent(
            file_path=Path("test2.py"),
            change_type=ChangeType.CREATED,
            content_type=ContentType.SOURCE_CODE
        )

        monitor._change_queue.append(change1)
        monitor._change_queue.append(change2)

        # Get recent changes
        changes = monitor.get_recent_changes()
        assert len(changes) == 2

        # Test with limit
        changes_limited = monitor.get_recent_changes(limit=1)
        assert len(changes_limited) == 1

    def test_get_change_events(self, monitor):
        """Test getting and clearing change events."""
        # Add changes to queue
        change1 = FileChangeEvent(
            file_path=Path("test1.py"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.SOURCE_CODE
        )

        monitor._change_queue.append(change1)
        assert len(monitor._change_queue) == 1

        # Get events (should clear queue)
        events = monitor.get_change_events()
        assert len(events) == 1
        assert events[0] == change1
        assert len(monitor._change_queue) == 0

    def test_cleanup_old_changes(self, monitor):
        """Test cleanup of old changes."""
        # Create old change
        old_change = FileChangeEvent(
            file_path=Path("old.py"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.SOURCE_CODE,
            timestamp=datetime.now() - timedelta(hours=2)
        )

        # Create recent change
        recent_change = FileChangeEvent(
            file_path=Path("recent.py"),
            change_type=ChangeType.MODIFIED,
            content_type=ContentType.SOURCE_CODE
        )

        # Add to queue and recent changes
        monitor._change_queue.append(old_change)
        monitor._change_queue.append(recent_change)
        monitor._recent_changes["old.py"] = old_change
        monitor._recent_changes["recent.py"] = recent_change

        # Cleanup
        monitor._cleanup_old_changes()

        # Old change should be removed, recent should remain
        assert len(monitor._change_queue) == 1
        assert monitor._change_queue[0] == recent_change
        assert "old.py" not in monitor._recent_changes
        assert "recent.py" in monitor._recent_changes

    def test_get_monitoring_stats(self, monitor):
        """Test monitoring statistics."""
        stats = monitor.get_monitoring_stats()

        assert "total_events" in stats
        assert "filtered_events" in stats
        assert "is_monitoring" in stats
        assert "project_path" in stats
        assert "queue_size" in stats
        assert "watch_patterns" in stats
        assert "ignore_patterns" in stats

        assert stats["is_monitoring"] is False
        assert stats["project_path"] == str(monitor.project_path)
        assert stats["queue_size"] == 0


class TestProjectFileEventHandler(ReflectiveModule):
    """Test ProjectFileEventHandler functionality."""

    @pytest.fixture
    def mock_monitor(self):
        """Create mock monitor."""
        monitor = Mock(spec=ProjectFileMonitor)
        monitor.handle_file_change = Mock()
        return monitor

    @pytest.fixture
    def event_handler(self, mock_monitor):
        """Create event handler."""
        return ProjectFileEventHandler(mock_monitor)

    def test_initialization(self, mock_monitor):
        """Test event handler initialization."""
        handler = ProjectFileEventHandler(mock_monitor)
        assert handler.monitor == mock_monitor

    def test_on_any_event_file(self, event_handler, mock_monitor):
        """Test handling file events."""
        # Create mock file event
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = "/test/file.py"

        event_handler.on_any_event(mock_event)

        # Should call monitor's handle_file_change
        mock_monitor.handle_file_change.assert_called_once_with(mock_event)

    def test_on_any_event_directory(self, event_handler, mock_monitor):
        """Test handling directory events."""
        # Create mock directory event
        mock_event = Mock()
        mock_event.is_directory = True
        mock_event.src_path = "/test/directory"

        event_handler.on_any_event(mock_event)

        # Should not call monitor's handle_file_change for directories
        mock_monitor.handle_file_change.assert_not_called()


class TestProjectFileMonitorIntegration(ReflectiveModule):
    """Integration tests for ProjectFileMonitor."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_sync_manager(self):
        """Create mock sync manager."""
        sync_manager = Mock()
        sync_manager.queue_sync_operation = Mock()
        return sync_manager

    def test_real_file_change_detection(self, temp_project_dir, mock_sync_manager):
        """Test real file change detection with actual file operations."""
        config = DevpostConfig(
            project_id="test",
            hackathon_id="test",
            sync_enabled=True,
            watch_patterns=["*.md", "*.py"]
        )

        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            sync_manager=mock_sync_manager,
            config=config
        )

        # Set short debounce delay for testing
        monitor.debounce_delay = 0.1

        try:
            monitor.start_monitoring()

            # Create a file
            test_file = temp_project_dir / "test.md"
            test_file.write_text("# Test")

            # Wait for file system event and debouncing
            time.sleep(0.3)

            # Check that change was detected
            changes = monitor.get_recent_changes()
            assert len(changes) > 0

            # Check that sync was triggered
            assert mock_sync_manager.queue_sync_operation.called

        finally:
            monitor.stop_monitoring()

    def test_file_modification_detection(self, temp_project_dir, mock_sync_manager):
        """Test detection of file modifications."""
        config = DevpostConfig(
            project_id="test",
            hackathon_id="test",
            sync_enabled=True
        )

        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            sync_manager=mock_sync_manager,
            config=config
        )

        monitor.debounce_delay = 0.1

        # Create initial file
        test_file = temp_project_dir / "README.md"
        test_file.write_text("Initial content")

        try:
            monitor.start_monitoring()

            # Modify the file
            test_file.write_text("Modified content")

            # Wait for detection
            time.sleep(0.3)

            # Check for changes
            changes = monitor.get_recent_changes()
            assert len(changes) > 0

            # Find the README change
            readme_changes = [c for c in changes if c.file_path.name == "README.md"]
            assert len(readme_changes) > 0

            readme_change = readme_changes[0]
            assert readme_change.content_type == ContentType.DOCUMENTATION
            assert readme_change.affects_sync is True

        finally:
            monitor.stop_monitoring()


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