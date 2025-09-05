"""
Tests for the Devpost ProjectFileMonitor class.

This module tests the file monitoring functionality including:
- File system watching using watchdog
- Configurable file pattern matching
- Change event filtering and debouncing
- Change event queuing and processing
"""

import asyncio
import tempfile
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.beast_mode.integration.devpost.monitoring.file_monitor import (
    ProjectFileMonitor,
    DevpostFileEventHandler
)
from src.beast_mode.integration.devpost.models import (
    DevpostConfig,
    FileChangeEvent,
    ChangeType,
    SyncOperation,
    SyncOperationType
)


class TestDevpostFileEventHandler:
    """Test the custom file event handler."""
    
    def test_handler_initialization(self):
        """Test handler initialization."""
        monitor = Mock()
        handler = DevpostFileEventHandler(monitor)
        assert handler.monitor is monitor
    
    def test_on_created_calls_monitor(self):
        """Test that file creation events are passed to monitor."""
        monitor = Mock()
        handler = DevpostFileEventHandler(monitor)
        
        event = Mock()
        event.is_directory = False
        event.src_path = "/test/file.txt"
        
        handler.on_created(event)
        monitor._handle_file_event.assert_called_once_with("/test/file.txt", ChangeType.CREATED)
    
    def test_on_modified_calls_monitor(self):
        """Test that file modification events are passed to monitor."""
        monitor = Mock()
        handler = DevpostFileEventHandler(monitor)
        
        event = Mock()
        event.is_directory = False
        event.src_path = "/test/file.txt"
        
        handler.on_modified(event)
        monitor._handle_file_event.assert_called_once_with("/test/file.txt", ChangeType.MODIFIED)
    
    def test_on_deleted_calls_monitor(self):
        """Test that file deletion events are passed to monitor."""
        monitor = Mock()
        handler = DevpostFileEventHandler(monitor)
        
        event = Mock()
        event.is_directory = False
        event.src_path = "/test/file.txt"
        
        handler.on_deleted(event)
        monitor._handle_file_event.assert_called_once_with("/test/file.txt", ChangeType.DELETED)
    
    def test_on_moved_calls_monitor_twice(self):
        """Test that file move events are handled as delete + create."""
        monitor = Mock()
        handler = DevpostFileEventHandler(monitor)
        
        event = Mock()
        event.is_directory = False
        event.src_path = "/test/old_file.txt"
        event.dest_path = "/test/new_file.txt"
        
        handler.on_moved(event)
        
        assert monitor._handle_file_event.call_count == 2
        monitor._handle_file_event.assert_any_call("/test/old_file.txt", ChangeType.DELETED)
        monitor._handle_file_event.assert_any_call("/test/new_file.txt", ChangeType.CREATED)
    
    def test_ignores_directory_events(self):
        """Test that directory events are ignored."""
        monitor = Mock()
        handler = DevpostFileEventHandler(monitor)
        
        event = Mock()
        event.is_directory = True
        event.src_path = "/test/directory"
        
        handler.on_created(event)
        handler.on_modified(event)
        handler.on_deleted(event)
        
        monitor._handle_file_event.assert_not_called()


class TestProjectFileMonitor:
    """Test the ProjectFileMonitor class."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create some test files
            (project_path / "README.md").write_text("# Test Project")
            (project_path / "package.json").write_text('{"name": "test"}')
            (project_path / "src").mkdir()
            (project_path / "src" / "main.py").write_text("print('hello')")
            
            yield project_path
    
    @pytest.fixture
    def devpost_config(self):
        """Create a test Devpost configuration."""
        return DevpostConfig(
            project_id="test-project-123",
            hackathon_id="hackathon-456",
            watch_patterns=["README*", "*.md", "package.json", "src/*.py"],
            sync_interval=60
        )
    
    @pytest.fixture
    def mock_sync_manager(self):
        """Create a mock sync manager."""
        sync_manager = Mock()
        sync_manager.queue_sync_operation = Mock()
        return sync_manager
    
    def test_monitor_initialization(self, temp_project_dir, devpost_config):
        """Test monitor initialization."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config,
            debounce_delay=1.0,
            max_queue_size=100
        )
        
        assert monitor.project_path == temp_project_dir.resolve()
        assert monitor.config == devpost_config
        assert monitor.debounce_delay == 1.0
        assert monitor.max_queue_size == 100
        assert not monitor._is_monitoring
        assert len(monitor._watch_paths) == 0
    
    def test_start_monitoring(self, temp_project_dir, devpost_config):
        """Test starting file monitoring."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        try:
            monitor.start_monitoring()
            
            assert monitor._is_monitoring
            assert monitor._observer is not None
            assert monitor._event_handler is not None
            assert monitor._processing_thread is not None
            assert monitor._processing_thread.is_alive()
            assert temp_project_dir.resolve() in monitor._watch_paths
            
        finally:
            monitor.stop_monitoring()
    
    def test_stop_monitoring(self, temp_project_dir, devpost_config):
        """Test stopping file monitoring."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        monitor.start_monitoring()
        assert monitor._is_monitoring
        
        monitor.stop_monitoring()
        
        assert not monitor._is_monitoring
        assert monitor._observer is None
        assert monitor._event_handler is None
        assert len(monitor._debounce_timers) == 0
    
    def test_context_manager(self, temp_project_dir, devpost_config):
        """Test using monitor as context manager."""
        with ProjectFileMonitor(temp_project_dir, devpost_config) as monitor:
            assert monitor._is_monitoring
        
        assert not monitor._is_monitoring
    
    def test_add_watch_path(self, temp_project_dir, devpost_config):
        """Test adding watch paths."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        # Create additional directory
        sub_dir = temp_project_dir / "docs"
        sub_dir.mkdir()
        
        monitor.add_watch_path(sub_dir)
        assert sub_dir.resolve() in monitor._watch_paths
    
    def test_add_nonexistent_watch_path(self, temp_project_dir, devpost_config):
        """Test adding non-existent watch path."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        nonexistent_path = temp_project_dir / "nonexistent"
        monitor.add_watch_path(nonexistent_path)
        
        # Should not be added to watch paths
        assert nonexistent_path.resolve() not in monitor._watch_paths
    
    def test_add_file_as_watch_path(self, temp_project_dir, devpost_config):
        """Test adding file (not directory) as watch path."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        file_path = temp_project_dir / "README.md"
        monitor.add_watch_path(file_path)
        
        # Should not be added to watch paths
        assert file_path.resolve() not in monitor._watch_paths
    
    def test_remove_watch_path(self, temp_project_dir, devpost_config):
        """Test removing watch paths."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        sub_dir = temp_project_dir / "docs"
        sub_dir.mkdir()
        
        monitor.add_watch_path(sub_dir)
        assert sub_dir.resolve() in monitor._watch_paths
        
        monitor.remove_watch_path(sub_dir)
        assert sub_dir.resolve() not in monitor._watch_paths
    
    def test_is_relevant_file(self, temp_project_dir, devpost_config):
        """Test file relevance checking."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        # Relevant files
        assert monitor._is_relevant_file(temp_project_dir / "README.md")
        assert monitor._is_relevant_file(temp_project_dir / "src" / "main.py")
        
        # Irrelevant files
        assert not monitor._is_relevant_file(temp_project_dir / "file.pyc")
        assert not monitor._is_relevant_file(temp_project_dir / "__pycache__" / "module.pyc")
        assert not monitor._is_relevant_file(temp_project_dir / ".git" / "config")
        assert not monitor._is_relevant_file(Path("/outside/project/file.txt"))
    
    def test_should_trigger_sync(self, temp_project_dir, devpost_config):
        """Test sync trigger logic."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        # Files that should trigger sync
        assert monitor._should_trigger_sync(temp_project_dir / "README.md")
        assert monitor._should_trigger_sync(temp_project_dir / "package.json")
        assert monitor._should_trigger_sync(temp_project_dir / "src" / "main.py")
        
        # Files that should not trigger sync
        assert not monitor._should_trigger_sync(temp_project_dir / "random.txt")
        assert not monitor._should_trigger_sync(temp_project_dir / "build" / "output.js")
    
    def test_create_change_event(self, temp_project_dir, devpost_config):
        """Test change event creation."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        file_path = temp_project_dir / "README.md"
        event = monitor._create_change_event(file_path, ChangeType.MODIFIED)
        
        assert event is not None
        assert event.file_path == file_path
        assert event.change_type == ChangeType.MODIFIED
        assert isinstance(event.timestamp, datetime)
        assert event.affects_sync  # README.md should trigger sync
        assert event.file_size is not None
    
    def test_create_change_event_deleted_file(self, temp_project_dir, devpost_config):
        """Test change event creation for deleted file."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        file_path = temp_project_dir / "deleted_file.md"
        event = monitor._create_change_event(file_path, ChangeType.DELETED)
        
        assert event is not None
        assert event.file_path == file_path
        assert event.change_type == ChangeType.DELETED
        assert event.file_size is None  # Deleted files don't have size
    
    def test_handle_file_event(self, temp_project_dir, devpost_config):
        """Test file event handling."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        file_path = str(temp_project_dir / "README.md")
        
        # Mock the internal methods
        with patch.object(monitor, '_is_relevant_file', return_value=True), \
             patch.object(monitor, '_create_change_event') as mock_create, \
             patch.object(monitor, '_schedule_debounced_processing') as mock_schedule:
            
            mock_event = Mock()
            mock_create.return_value = mock_event
            
            monitor._handle_file_event(file_path, ChangeType.MODIFIED)
            
            mock_create.assert_called_once()
            mock_schedule.assert_called_once_with(file_path)
            assert mock_event in monitor._event_queue
    
    def test_handle_irrelevant_file_event(self, temp_project_dir, devpost_config):
        """Test handling of irrelevant file events."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        file_path = str(temp_project_dir / "irrelevant.pyc")
        
        with patch.object(monitor, '_is_relevant_file', return_value=False), \
             patch.object(monitor, '_create_change_event') as mock_create:
            
            monitor._handle_file_event(file_path, ChangeType.MODIFIED)
            
            mock_create.assert_not_called()
            assert len(monitor._event_queue) == 0
    
    def test_debounced_processing(self, temp_project_dir, devpost_config):
        """Test debounced processing of file changes."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config, debounce_delay=0.1)
        
        file_path = str(temp_project_dir / "README.md")
        
        with patch.object(monitor, '_process_debounced_file') as mock_process:
            monitor._schedule_debounced_processing(file_path)
            
            # Should not be called immediately
            mock_process.assert_not_called()
            
            # Wait for debounce delay
            time.sleep(0.2)
            
            # Should be called after delay
            mock_process.assert_called_once_with(file_path)
    
    def test_debounced_processing_cancellation(self, temp_project_dir, devpost_config):
        """Test that rapid changes cancel previous timers."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config, debounce_delay=0.2)
        
        file_path = str(temp_project_dir / "README.md")
        
        with patch.object(monitor, '_process_debounced_file') as mock_process:
            # Schedule first processing
            monitor._schedule_debounced_processing(file_path)
            
            # Schedule second processing before first completes
            time.sleep(0.1)
            monitor._schedule_debounced_processing(file_path)
            
            # Wait for debounce delay
            time.sleep(0.3)
            
            # Should only be called once (second call)
            mock_process.assert_called_once_with(file_path)
    
    def test_process_change_event_with_sync_manager(self, temp_project_dir, devpost_config, mock_sync_manager):
        """Test processing change event with sync manager."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config, sync_manager=mock_sync_manager)
        
        # Create a change event that affects sync
        event = FileChangeEvent(
            file_path=temp_project_dir / "README.md",
            change_type=ChangeType.MODIFIED,
            affects_sync=True
        )
        
        monitor._process_change_event(event)
        
        # Should queue sync operation
        mock_sync_manager.queue_sync_operation.assert_called_once()
        
        # Check the sync operation
        sync_op = mock_sync_manager.queue_sync_operation.call_args[0][0]
        assert isinstance(sync_op, SyncOperation)
        assert sync_op.operation_type == SyncOperationType.DOCUMENTATION_UPDATE
    
    def test_process_change_event_without_sync(self, temp_project_dir, devpost_config):
        """Test processing change event that doesn't affect sync."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        event = FileChangeEvent(
            file_path=temp_project_dir / "random.txt",
            change_type=ChangeType.MODIFIED,
            affects_sync=False
        )
        
        monitor._process_change_event(event)
        
        # Should be stored in recent changes
        assert str(event.file_path) in monitor._recent_changes
    
    def test_get_recent_changes(self, temp_project_dir, devpost_config):
        """Test getting recent changes."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        # Add some test events
        event1 = FileChangeEvent(
            file_path=temp_project_dir / "file1.md",
            change_type=ChangeType.MODIFIED,
            timestamp=datetime.now() - timedelta(minutes=30)
        )
        event2 = FileChangeEvent(
            file_path=temp_project_dir / "file2.md",
            change_type=ChangeType.CREATED,
            timestamp=datetime.now() - timedelta(minutes=10)
        )
        
        monitor._recent_changes[str(event1.file_path)] = event1
        monitor._recent_changes[str(event2.file_path)] = event2
        
        # Get changes from last 20 minutes
        since = datetime.now() - timedelta(minutes=20)
        recent = monitor.get_recent_changes(since)
        
        assert len(recent) == 1
        assert recent[0] == event2
    
    def test_change_callbacks(self, temp_project_dir, devpost_config):
        """Test change event callbacks."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        callback_mock = Mock()
        monitor.add_change_callback(callback_mock)
        
        event = FileChangeEvent(
            file_path=temp_project_dir / "test.md",
            change_type=ChangeType.MODIFIED
        )
        
        monitor._process_change_event(event)
        
        callback_mock.assert_called_once_with(event)
    
    def test_remove_change_callback(self, temp_project_dir, devpost_config):
        """Test removing change callbacks."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        callback_mock = Mock()
        monitor.add_change_callback(callback_mock)
        monitor.remove_change_callback(callback_mock)
        
        event = FileChangeEvent(
            file_path=temp_project_dir / "test.md",
            change_type=ChangeType.MODIFIED
        )
        
        monitor._process_change_event(event)
        
        callback_mock.assert_not_called()
    
    def test_max_queue_size_limit(self, temp_project_dir, devpost_config):
        """Test that event queue respects max size limit."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config, max_queue_size=3)
        
        # Add more events than max size
        for i in range(5):
            event = FileChangeEvent(
                file_path=temp_project_dir / f"file{i}.md",
                change_type=ChangeType.MODIFIED
            )
            monitor._event_queue.append(event)
        
        # Should only keep the last 3 events
        assert len(monitor._event_queue) == 3
    
    def test_recent_changes_size_limit(self, temp_project_dir, devpost_config):
        """Test that recent changes are limited in size."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        # Add many events to trigger cleanup
        for i in range(1100):
            event = FileChangeEvent(
                file_path=temp_project_dir / f"file{i}.md",
                change_type=ChangeType.MODIFIED,
                timestamp=datetime.now() - timedelta(seconds=i)
            )
            monitor._recent_changes[str(event.file_path)] = event
        
        # Process an event to trigger cleanup
        test_event = FileChangeEvent(
            file_path=temp_project_dir / "test.md",
            change_type=ChangeType.MODIFIED
        )
        monitor._process_change_event(test_event)
        
        # Should be limited to reasonable size
        assert len(monitor._recent_changes) <= 1000


@pytest.mark.integration
class TestProjectFileMonitorIntegration:
    """Integration tests for ProjectFileMonitor with real file system."""
    
    def test_real_file_monitoring(self):
        """Test monitoring real file system changes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            config = DevpostConfig(
                project_id="test-project",
                hackathon_id="test-hackathon",
                watch_patterns=["*.md", "*.txt"]
            )
            
            changes_detected = []
            
            def change_callback(event):
                changes_detected.append(event)
            
            with ProjectFileMonitor(project_path, config, debounce_delay=0.1) as monitor:
                monitor.add_change_callback(change_callback)
                
                # Give monitor time to start
                time.sleep(0.1)
                
                # Create a file
                test_file = project_path / "test.md"
                test_file.write_text("# Test")
                
                # Wait for event processing
                time.sleep(0.3)
                
                # Modify the file
                test_file.write_text("# Modified Test")
                
                # Wait for event processing
                time.sleep(0.3)
                
                # Delete the file
                test_file.unlink()
                
                # Wait for event processing
                time.sleep(0.3)
            
            # Should have detected changes
            assert len(changes_detected) > 0
            
            # Check that we got the expected change types
            change_types = [event.change_type for event in changes_detected]
            assert ChangeType.CREATED in change_types
            assert ChangeType.MODIFIED in change_types
            assert ChangeType.DELETED in change_types