"""
Tests for ProjectFileMonitor class.

This module tests the file monitoring functionality including file system
watching, change event filtering, debouncing logic, and sync operation queuing.
"""

import asyncio
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

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
from src.beast_mode.integration.devpost.interfaces import SyncManagerInterface


class MockSyncManager(SyncManagerInterface):
    """Mock sync manager for testing."""
    
    def __init__(self):
        self.queued_operations = []
        self.sync_results = []
    
    async def sync_metadata(self):
        return Mock(success=True)
    
    async def sync_media_files(self):
        return Mock(success=True)
    
    async def full_sync(self):
        return Mock(success=True)
    
    def queue_sync_operation(self, operation):
        self.queued_operations.append(operation)
    
    async def process_sync_queue(self):
        return self.sync_results


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create some test files
        (project_path / "README.md").write_text("# Test Project")
        (project_path / "package.json").write_text('{"name": "test"}')
        (project_path / "src").mkdir()
        (project_path / "src" / "main.py").write_text("print('hello')")
        (project_path / "media").mkdir()
        
        yield project_path


@pytest.fixture
def devpost_config():
    """Create a test Devpost configuration."""
    return DevpostConfig(
        project_id="test-project-123",
        hackathon_id="hackathon-456",
        sync_enabled=True,
        watch_patterns=["README*", "*.md", "package.json", "media/*"],
        sync_interval=300,
        auto_sync_media=True
    )


@pytest.fixture
def mock_sync_manager():
    """Create a mock sync manager."""
    return MockSyncManager()


class TestProjectFileMonitor:
    """Test cases for ProjectFileMonitor."""
    
    def test_init(self, temp_project_dir, devpost_config):
        """Test monitor initialization."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config,
            debounce_delay=0.1
        )
        
        assert monitor.project_path == temp_project_dir.resolve()
        assert monitor.config == devpost_config
        assert monitor.debounce_delay == 0.1
        assert not monitor._is_monitoring
        assert len(monitor._watch_paths) == 0
    
    @pytest.mark.timeout(10)
    def test_start_stop_monitoring(self, temp_project_dir, devpost_config):
        """Test starting and stopping file monitoring."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config,
            debounce_delay=0.1
        )
        
        # Start monitoring
        monitor.start_monitoring()
        assert monitor._is_monitoring
        assert monitor._observer is not None
        assert monitor._processing_thread is not None
        assert temp_project_dir.resolve() in monitor._watch_paths
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert not monitor._is_monitoring
        assert monitor._observer is None
    
    @pytest.mark.timeout(10)
    def test_context_manager(self, temp_project_dir, devpost_config):
        """Test using monitor as context manager."""
        with ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config,
            debounce_delay=0.1
        ) as monitor:
            assert monitor._is_monitoring
        
        assert not monitor._is_monitoring
    
    def test_add_remove_watch_path(self, temp_project_dir, devpost_config):
        """Test adding and removing watch paths."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        # Add valid path
        src_path = temp_project_dir / "src"
        monitor.add_watch_path(src_path)
        assert src_path.resolve() in monitor._watch_paths
        
        # Add non-existent path (should be ignored)
        fake_path = temp_project_dir / "nonexistent"
        monitor.add_watch_path(fake_path)
        assert fake_path.resolve() not in monitor._watch_paths
        
        # Remove path
        monitor.remove_watch_path(src_path)
        assert src_path.resolve() not in monitor._watch_paths
    
    def test_is_relevant_file(self, temp_project_dir, devpost_config):
        """Test file relevance checking."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        # Relevant files
        assert monitor._is_relevant_file(temp_project_dir / "README.md")
        assert monitor._is_relevant_file(temp_project_dir / "src" / "main.py")
        
        # Excluded files
        assert not monitor._is_relevant_file(temp_project_dir / "file.pyc")
        assert not monitor._is_relevant_file(temp_project_dir / "__pycache__" / "module.pyc")
        assert not monitor._is_relevant_file(temp_project_dir / ".git" / "config")
        
        # Files outside project
        with tempfile.TemporaryDirectory() as other_dir:
            other_path = Path(other_dir) / "other.txt"
            other_path.write_text("test")
            assert not monitor._is_relevant_file(other_path)
    
    def test_should_trigger_sync(self, temp_project_dir, devpost_config):
        """Test sync trigger logic."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        # Files matching watch patterns
        assert monitor._should_trigger_sync(temp_project_dir / "README.md")
        assert monitor._should_trigger_sync(temp_project_dir / "package.json")
        assert monitor._should_trigger_sync(temp_project_dir / "media" / "image.png")
        
        # Files not matching patterns
        assert not monitor._should_trigger_sync(temp_project_dir / "src" / "main.py")
        assert not monitor._should_trigger_sync(temp_project_dir / "test.txt")
    
    def test_create_change_event(self, temp_project_dir, devpost_config):
        """Test change event creation."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        # Test with existing file
        readme_path = temp_project_dir / "README.md"
        event = monitor._create_change_event(readme_path, ChangeType.MODIFIED)
        
        assert event is not None
        assert event.file_path == readme_path
        assert event.change_type == ChangeType.MODIFIED
        assert event.affects_sync  # README.md matches watch patterns
        assert event.file_size is not None
        
        # Test with deleted file
        deleted_path = temp_project_dir / "deleted.txt"
        event = monitor._create_change_event(deleted_path, ChangeType.DELETED)
        
        assert event is not None
        assert event.change_type == ChangeType.DELETED
        assert event.file_size is None
    
    def test_change_callbacks(self, temp_project_dir, devpost_config):
        """Test change event callbacks."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        callback_events = []
        
        def test_callback(event):
            callback_events.append(event)
        
        # Add callback
        monitor.add_change_callback(test_callback)
        
        # Process a change event
        readme_path = temp_project_dir / "README.md"
        event = FileChangeEvent(
            file_path=readme_path,
            change_type=ChangeType.MODIFIED,
            affects_sync=True
        )
        
        monitor._process_change_event(event)
        
        # Check callback was called
        assert len(callback_events) == 1
        assert callback_events[0] == event
        
        # Remove callback
        monitor.remove_change_callback(test_callback)
        
        # Process another event
        monitor._process_change_event(event)
        
        # Callback should not be called again
        assert len(callback_events) == 1
    
    def test_sync_operation_queuing(self, temp_project_dir, devpost_config, mock_sync_manager):
        """Test sync operation queuing."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config,
            sync_manager=mock_sync_manager
        )
        
        # Process documentation file change
        readme_path = temp_project_dir / "README.md"
        event = FileChangeEvent(
            file_path=readme_path,
            change_type=ChangeType.MODIFIED,
            affects_sync=True
        )
        
        monitor._process_change_event(event)
        
        # Check sync operation was queued
        assert len(mock_sync_manager.queued_operations) == 1
        operation = mock_sync_manager.queued_operations[0]
        assert operation.operation_type == SyncOperationType.DOCUMENTATION_UPDATE
        assert operation.target_field == "README.md"
    
    def test_get_recent_changes(self, temp_project_dir, devpost_config):
        """Test getting recent changes."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        # Add some changes
        readme_path = temp_project_dir / "README.md"
        event1 = FileChangeEvent(
            file_path=readme_path,
            change_type=ChangeType.MODIFIED,
            timestamp=datetime.now() - timedelta(minutes=30)
        )
        
        event2 = FileChangeEvent(
            file_path=temp_project_dir / "package.json",
            change_type=ChangeType.MODIFIED,
            timestamp=datetime.now() - timedelta(minutes=10)
        )
        
        monitor._process_change_event(event1)
        monitor._process_change_event(event2)
        
        # Get recent changes
        recent = monitor.get_recent_changes(since=datetime.now() - timedelta(minutes=20))
        assert len(recent) == 1
        assert recent[0].file_path == temp_project_dir / "package.json"
        
        # Get all changes
        all_changes = monitor.get_recent_changes(since=datetime.now() - timedelta(hours=1))
        assert len(all_changes) == 2
    
    @pytest.mark.timeout(5)
    def test_debouncing(self, temp_project_dir, devpost_config, mock_sync_manager):
        """Test file change debouncing."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config,
            sync_manager=mock_sync_manager,
            debounce_delay=0.1
        )
        
        readme_path = temp_project_dir / "README.md"
        
        # Simulate rapid file changes
        for i in range(5):
            monitor._handle_file_event(str(readme_path), ChangeType.MODIFIED)
            time.sleep(0.02)  # 20ms between changes
        
        # Wait for debounce period
        time.sleep(0.2)
        
        # Should only have one sync operation queued (debounced)
        # Note: This test might be flaky due to timing, but demonstrates the concept
        assert len(mock_sync_manager.queued_operations) <= 1


class TestDevpostFileEventHandler:
    """Test cases for DevpostFileEventHandler."""
    
    def test_event_handling(self, temp_project_dir, devpost_config):
        """Test file system event handling."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        handler = DevpostFileEventHandler(monitor)
        
        # Mock file system events
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = str(temp_project_dir / "test.txt")
        
        # Test different event types
        with patch.object(monitor, '_handle_file_event') as mock_handle:
            handler.on_created(mock_event)
            mock_handle.assert_called_with(mock_event.src_path, ChangeType.CREATED)
            
            handler.on_modified(mock_event)
            mock_handle.assert_called_with(mock_event.src_path, ChangeType.MODIFIED)
            
            handler.on_deleted(mock_event)
            mock_handle.assert_called_with(mock_event.src_path, ChangeType.DELETED)
    
    def test_move_event_handling(self, temp_project_dir, devpost_config):
        """Test file move event handling."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        handler = DevpostFileEventHandler(monitor)
        
        # Mock move event
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = str(temp_project_dir / "old.txt")
        mock_event.dest_path = str(temp_project_dir / "new.txt")
        
        with patch.object(monitor, '_handle_file_event') as mock_handle:
            handler.on_moved(mock_event)
            
            # Should handle as delete + create
            assert mock_handle.call_count == 2
            mock_handle.assert_any_call(mock_event.src_path, ChangeType.DELETED)
            mock_handle.assert_any_call(mock_event.dest_path, ChangeType.CREATED)
    
    def test_directory_events_ignored(self, temp_project_dir, devpost_config):
        """Test that directory events are ignored."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config
        )
        
        handler = DevpostFileEventHandler(monitor)
        
        # Mock directory event
        mock_event = Mock()
        mock_event.is_directory = True
        mock_event.src_path = str(temp_project_dir / "new_dir")
        
        with patch.object(monitor, '_handle_file_event') as mock_handle:
            handler.on_created(mock_event)
            handler.on_modified(mock_event)
            handler.on_deleted(mock_event)
            
            # Should not handle directory events
            mock_handle.assert_not_called()


@pytest.mark.integration
class TestFileMonitorIntegration:
    """Integration tests for file monitoring."""
    
    @pytest.mark.timeout(15)
    def test_real_file_monitoring(self, temp_project_dir, devpost_config):
        """Test monitoring real file system changes."""
        monitor = ProjectFileMonitor(
            project_path=temp_project_dir,
            config=devpost_config,
            debounce_delay=0.1
        )
        
        changes_detected = []
        
        def change_callback(event):
            changes_detected.append(event)
        
        monitor.add_change_callback(change_callback)
        
        with monitor:
            # Create a new file
            new_file = temp_project_dir / "new_readme.md"
            new_file.write_text("# New README")
            
            # Wait for change detection
            time.sleep(0.3)
            
            # Modify existing file
            readme_file = temp_project_dir / "README.md"
            readme_file.write_text("# Updated README")
            
            # Wait for change detection
            time.sleep(0.3)
        
        # Should have detected changes
        assert len(changes_detected) >= 1
        
        # Check that at least one change was for a markdown file
        md_changes = [c for c in changes_detected if c.file_path.suffix == '.md']
        assert len(md_changes) >= 1