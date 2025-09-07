#!/usr/bin/env python3
"""
Unit tests for Devpost Integration File Monitor

Tests intelligent change detection, media file detection, and Git integration.
"""

import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.devpost_integration.file_monitor import (
    ProjectFileMonitor, ContentBasedChangeDetector, MediaFileDetector, 
    GitIntegration, ProjectFileEventHandler
)
from src.devpost_integration.models import (
    DevpostConfig, FileChangeEvent, ChangeType, ContentType, 
    MediaType, MediaFile
)


class TestContentBasedChangeDetector:
    """Test content-based change detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ContentBasedChangeDetector()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_significant_change_new_file(self):
        """Test that new files are considered significant changes."""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("# New Document\n\nThis is new content.")
        
        is_significant = self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        assert is_significant is True
    
    def test_significant_change_deleted_file(self):
        """Test that deleted files are considered significant changes."""
        test_file = self.temp_dir / "deleted.md"
        
        # File doesn't exist - should be significant (deletion)
        is_significant = self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        assert is_significant is True
    
    def test_no_change_same_content(self):
        """Test that identical content is not considered significant."""
        test_file = self.temp_dir / "same.md"
        content = "# Same Document\n\nThis content doesn't change."
        test_file.write_text(content)
        
        # First check - should be significant (new file)
        is_significant = self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        assert is_significant is True
        
        # Second check with same content - should not be significant
        is_significant = self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        assert is_significant is False
    
    def test_structural_changes_significant(self):
        """Test that structural changes are considered significant."""
        test_file = self.temp_dir / "structural.md"
        
        # Initial content
        initial_content = "# Original Title\n\nSome content here."
        test_file.write_text(initial_content)
        self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        
        # Change header structure
        modified_content = "## Modified Title\n\nSome content here."
        test_file.write_text(modified_content)
        
        is_significant = self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        assert is_significant is True
    
    def test_minor_content_changes_not_significant(self):
        """Test that minor content changes are not significant."""
        test_file = self.temp_dir / "minor.md"
        
        # Initial content
        initial_content = "# Title\n\nThis is some content with many words to test."
        test_file.write_text(initial_content)
        self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        
        # Minor change (typo fix)
        modified_content = "# Title\n\nThis is some content with many words to test!"
        test_file.write_text(modified_content)
        
        is_significant = self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        assert is_significant is False
    
    def test_large_content_changes_significant(self):
        """Test that large content changes are significant."""
        test_file = self.temp_dir / "large.md"
        
        # Initial content (short)
        initial_content = "# Title\n\nShort content."
        test_file.write_text(initial_content)
        self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        
        # Large addition
        modified_content = initial_content + "\n\n" + "Additional content. " * 50
        test_file.write_text(modified_content)
        
        is_significant = self.detector.is_significant_change(test_file, ContentType.DOCUMENTATION)
        assert is_significant is True
    
    def test_non_documentation_files_always_significant(self):
        """Test that non-documentation files are always considered significant."""
        test_file = self.temp_dir / "code.py"
        test_file.write_text("print('hello')")
        
        is_significant = self.detector.is_significant_change(test_file, ContentType.SOURCE_CODE)
        assert is_significant is True


class TestMediaFileDetector:
    """Test media file detection and categorization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = MediaFileDetector()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_detect_image_file(self):
        """Test detection of image files."""
        image_file = self.temp_dir / "test_image.png"
        image_file.write_bytes(b"fake png data")
        
        media_file = self.detector.detect_media_files(image_file)
        
        assert media_file is not None
        assert media_file.media_type == MediaType.IMAGE
        assert media_file.filename == "test_image.png"
        assert media_file.file_path == image_file
    
    def test_detect_video_file(self):
        """Test detection of video files."""
        video_file = self.temp_dir / "demo_video.mp4"
        video_file.write_bytes(b"fake mp4 data")
        
        media_file = self.detector.detect_media_files(video_file)
        
        assert media_file is not None
        assert media_file.media_type == MediaType.DEMO  # Should be categorized as demo
        assert media_file.filename == "demo_video.mp4"
    
    def test_detect_screenshot(self):
        """Test detection and categorization of screenshots."""
        screenshot_file = self.temp_dir / "app_screenshot.png"
        screenshot_file.write_bytes(b"fake png data")
        
        media_file = self.detector.detect_media_files(screenshot_file)
        
        assert media_file is not None
        assert media_file.media_type == MediaType.SCREENSHOT
        assert media_file.filename == "app_screenshot.png"
    
    def test_detect_document_file(self):
        """Test detection of document files."""
        doc_file = self.temp_dir / "presentation.pdf"
        doc_file.write_bytes(b"fake pdf data")
        
        media_file = self.detector.detect_media_files(doc_file)
        
        assert media_file is not None
        assert media_file.media_type == MediaType.DOCUMENT
        assert media_file.filename == "presentation.pdf"
    
    def test_non_media_file_returns_none(self):
        """Test that non-media files return None."""
        text_file = self.temp_dir / "readme.txt"
        text_file.write_text("This is not a media file")
        
        media_file = self.detector.detect_media_files(text_file)
        
        assert media_file is None
    
    def test_generate_caption(self):
        """Test caption generation from filename."""
        test_file = self.temp_dir / "my_app_screenshot.png"
        test_file.write_bytes(b"fake data")
        
        media_file = self.detector.detect_media_files(test_file)
        
        assert media_file is not None
        assert media_file.caption == "My App Screenshot"
    
    def test_get_media_metadata(self):
        """Test media metadata extraction."""
        image_file = self.temp_dir / "test.jpg"
        image_file.write_bytes(b"fake jpg data")
        
        media_file = MediaFile(
            filename="test.jpg",
            file_path=image_file,
            media_type=MediaType.IMAGE,
            file_size=100
        )
        
        metadata = self.detector.get_media_metadata(media_file)
        
        assert metadata['filename'] == "test.jpg"
        assert metadata['file_size'] == 100
        assert metadata['media_type'] == "image"
        assert 'mime_type' in metadata


class TestGitIntegration:
    """Test Git integration functionality."""
    
    def setup_method(self):
        """Set up test fixtures with Git repository."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize Git repository
        subprocess.run(['git', 'init'], cwd=self.temp_dir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=self.temp_dir, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.temp_dir, check=True)
        
        # Create initial commit
        readme_file = self.temp_dir / "README.md"
        readme_file.write_text("# Test Project\n\nInitial content.")
        subprocess.run(['git', 'add', 'README.md'], cwd=self.temp_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.temp_dir, check=True)
        
        self.git_integration = GitIntegration(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_is_git_repo(self):
        """Test Git repository detection."""
        assert self.git_integration.is_git_repo is True
    
    def test_get_current_commit_hash(self):
        """Test getting current commit hash."""
        commit_hash = self.git_integration._get_current_commit_hash()
        assert commit_hash is not None
        assert len(commit_hash) == 40  # SHA-1 hash length
    
    def test_detect_new_tag(self):
        """Test detection of new Git tags."""
        # Create a new tag
        subprocess.run(['git', 'tag', 'v1.0.0'], cwd=self.temp_dir, check=True)
        
        releases = self.git_integration.check_for_releases()
        
        assert len(releases) == 1
        assert releases[0]['tag'] == 'v1.0.0'
        assert releases[0]['is_release'] is True
    
    def test_version_file_detection(self):
        """Test detection of version file changes."""
        # Create package.json with version
        package_json = self.temp_dir / "package.json"
        package_json.write_text(json.dumps({
            "name": "test-project",
            "version": "1.0.0",
            "description": "Test project"
        }, indent=2))
        
        subprocess.run(['git', 'add', 'package.json'], cwd=self.temp_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Add package.json'], cwd=self.temp_dir, check=True)
        
        releases = self.git_integration.check_for_releases()
        
        # Should detect version file change
        version_changes = [r for r in releases if r.get('type') == 'version_file_change']
        assert len(version_changes) >= 1
    
    def test_get_recent_commits(self):
        """Test getting recent commits."""
        commits = self.git_integration.get_recent_commits(limit=5)
        
        assert len(commits) >= 1
        assert 'hash' in commits[0]
        assert 'subject' in commits[0]
        assert 'author_name' in commits[0]
    
    def test_non_git_directory(self):
        """Test behavior with non-Git directory."""
        non_git_dir = Path(tempfile.mkdtemp())
        try:
            git_integration = GitIntegration(non_git_dir)
            assert git_integration.is_git_repo is False
            
            releases = git_integration.check_for_releases()
            assert releases == []
        finally:
            shutil.rmtree(non_git_dir)


class TestProjectFileMonitor:
    """Test the main ProjectFileMonitor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = DevpostConfig("test-project", "test-hackathon")
        self.sync_manager = Mock()
        
        self.monitor = ProjectFileMonitor(
            project_path=self.temp_dir,
            sync_manager=self.sync_manager,
            config=self.config
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.monitor._is_monitoring:
            self.monitor.stop_monitoring()
        
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        assert self.monitor.project_path.resolve() == self.temp_dir.resolve()
        assert self.monitor.config == self.config
        assert self.monitor.sync_manager == self.sync_manager
        assert isinstance(self.monitor.content_detector, ContentBasedChangeDetector)
        assert isinstance(self.monitor.media_detector, MediaFileDetector)
        assert isinstance(self.monitor.git_integration, GitIntegration)
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping file monitoring."""
        assert self.monitor._is_monitoring is False
        
        self.monitor.start_monitoring()
        assert self.monitor._is_monitoring is True
        assert self.monitor._observer is not None
        
        self.monitor.stop_monitoring()
        assert self.monitor._is_monitoring is False
        assert self.monitor._observer is None
    
    def test_context_manager(self):
        """Test using monitor as context manager."""
        with self.monitor as monitor:
            assert monitor._is_monitoring is True
        
        assert self.monitor._is_monitoring is False
    
    def test_file_change_detection(self):
        """Test file change detection and processing."""
        # Create a test file
        test_file = self.temp_dir / "test.md"
        test_file.write_text("# Test Document\n\nInitial content.")
        
        # Simulate file change event
        from watchdog.events import FileModifiedEvent
        event = FileModifiedEvent(str(test_file))
        
        self.monitor.handle_file_change(event)
        
        # Should have processed the event
        assert self.monitor._stats["total_events"] == 1
    
    def test_media_file_detection_integration(self):
        """Test integration with media file detection."""
        # Create a media file
        image_file = self.temp_dir / "screenshot.png"
        image_file.write_bytes(b"fake png data")
        
        # Test affects_sync for media file
        affects_sync = self.monitor._affects_sync(image_file, ContentType.MEDIA)
        assert affects_sync is True
        assert self.monitor._stats["media_detected"] == 1
    
    def test_documentation_change_detection_integration(self):
        """Test integration with content-based change detection."""
        # Create a documentation file
        doc_file = self.temp_dir / "README.md"
        doc_file.write_text("# Project Title\n\nProject description.")
        
        # First check - should be significant (new file)
        affects_sync = self.monitor._affects_sync(doc_file, ContentType.DOCUMENTATION)
        assert affects_sync is True
        assert self.monitor._stats["content_analyzed"] == 1
        
        # Second check with same content - should not be significant
        affects_sync = self.monitor._affects_sync(doc_file, ContentType.DOCUMENTATION)
        assert affects_sync is False
    
    def test_get_media_files(self):
        """Test getting all media files in project."""
        # Create various media files
        (self.temp_dir / "image.png").write_bytes(b"fake png")
        (self.temp_dir / "video.mp4").write_bytes(b"fake mp4")
        (self.temp_dir / "doc.pdf").write_bytes(b"fake pdf")
        (self.temp_dir / "text.txt").write_text("not media")
        
        media_files = self.monitor.get_media_files()
        
        assert len(media_files) == 3  # Should find 3 media files
        media_types = [mf.media_type for mf in media_files]
        assert MediaType.IMAGE in media_types
        assert MediaType.VIDEO in media_types
        assert MediaType.DOCUMENT in media_types
    
    def test_monitoring_stats(self):
        """Test monitoring statistics collection."""
        stats = self.monitor.get_monitoring_stats()
        
        assert "total_events" in stats
        assert "is_monitoring" in stats
        assert "project_path" in stats
        assert "git_repo" in stats
        assert Path(stats["project_path"]).resolve() == self.temp_dir.resolve()
    
    def test_debouncing_mechanism(self):
        """Test file change debouncing."""
        test_file = self.temp_dir / "debounce_test.md"
        test_file.write_text("Initial content")
        
        # Simulate rapid file changes
        from watchdog.events import FileModifiedEvent
        event = FileModifiedEvent(str(test_file))
        
        # Multiple rapid changes
        for i in range(5):
            test_file.write_text(f"Content change {i}")
            self.monitor.handle_file_change(event)
        
        # Should have debounced the changes
        assert self.monitor._stats["debounced_events"] >= 1
        assert len(self.monitor._debounce_timers) <= 1  # Should have at most one timer per file
    
    def test_change_queue_management(self):
        """Test change event queue management."""
        # Create multiple file changes
        for i in range(5):
            test_file = self.temp_dir / f"test_{i}.md"
            test_file.write_text(f"Content {i}")
            
            change_event = FileChangeEvent(
                file_path=test_file,
                change_type=ChangeType.CREATED,
                content_type=ContentType.DOCUMENTATION
            )
            
            self.monitor._change_queue.append(change_event)
        
        recent_changes = self.monitor.get_recent_changes(limit=3)
        assert len(recent_changes) == 3
        
        # Test getting all changes
        all_changes = self.monitor.get_change_events()
        assert len(all_changes) == 5
        assert len(self.monitor._change_queue) == 0  # Queue should be cleared
    
    @pytest.mark.timeout(30)  # 30-second timeout to prevent hanging
    def test_file_monitoring_with_timeout(self):
        """Test file monitoring with timeout to prevent test hangs."""
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Create a file change
        test_file = self.temp_dir / "timeout_test.md"
        test_file.write_text("Test content for timeout")
        
        # Wait briefly for change detection
        time.sleep(0.5)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        
        # Should have processed at least one event
        stats = self.monitor.get_monitoring_stats()
        assert stats["is_monitoring"] is False
    
    def test_error_handling(self):
        """Test error handling in file monitoring."""
        # Test with invalid project path
        invalid_path = Path("/nonexistent/path")
        
        with pytest.raises(ValueError):
            invalid_monitor = ProjectFileMonitor(invalid_path)
            invalid_monitor.start_monitoring()
    
    def test_watch_pattern_matching(self):
        """Test file pattern matching for monitoring."""
        # Test files that should be watched
        watched_files = [
            "README.md",
            "script.py", 
            "config.json"
        ]
        
        for filename in watched_files:
            test_file = self.temp_dir / filename
            test_file.write_text("test content")
            
            from watchdog.events import FileModifiedEvent
            event = FileModifiedEvent(str(test_file))
            
            should_process = self.monitor._should_process_change(test_file, event)
            assert should_process is True, f"Should process {filename}"
        
        # Test media files separately (they have different logic)
        media_file = self.temp_dir / "image.png"
        media_file.write_bytes(b"fake png data")
        
        from watchdog.events import FileModifiedEvent
        event = FileModifiedEvent(str(media_file))
        
        should_process = self.monitor._should_process_change(media_file, event)
        assert should_process is True, "Should process image.png"
        
        # Test files that should be ignored
        ignored_files = [
            "__pycache__/test.pyc",
            ".git/config",
            "node_modules/package.json",
            ".DS_Store"
        ]
        
        for filename in ignored_files:
            test_file = self.temp_dir / filename
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("test content")
            
            from watchdog.events import FileModifiedEvent
            event = FileModifiedEvent(str(test_file))
            
            should_process = self.monitor._should_process_change(test_file, event)
            assert should_process is False, f"Should ignore {filename}"


class TestProjectFileEventHandler:
    """Test the file system event handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.monitor = Mock(spec=ProjectFileMonitor)
        self.handler = ProjectFileEventHandler(self.monitor)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_file_event_handling(self):
        """Test handling of file system events."""
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("test content")
        
        from watchdog.events import FileModifiedEvent
        event = FileModifiedEvent(str(test_file))
        
        self.handler.on_any_event(event)
        
        # Should have called monitor's handle_file_change
        self.monitor.handle_file_change.assert_called_once_with(event)
    
    def test_directory_event_ignored(self):
        """Test that directory events are ignored."""
        test_dir = self.temp_dir / "test_dir"
        test_dir.mkdir()
        
        from watchdog.events import DirModifiedEvent
        event = DirModifiedEvent(str(test_dir))
        
        self.handler.on_any_event(event)
        
        # Should not have called monitor's handle_file_change for directory
        self.monitor.handle_file_change.assert_not_called()


# Integration tests
class TestFileMonitorIntegration:
    """Integration tests for file monitoring system."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize Git repository for full integration
        subprocess.run(['git', 'init'], cwd=self.temp_dir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=self.temp_dir, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.temp_dir, check=True)
        
        self.config = DevpostConfig("integration-test", "test-hackathon")
        self.sync_manager = Mock()
        
        self.monitor = ProjectFileMonitor(
            project_path=self.temp_dir,
            sync_manager=self.sync_manager,
            config=self.config
        )
    
    def teardown_method(self):
        """Clean up integration test fixtures."""
        if self.monitor._is_monitoring:
            self.monitor.stop_monitoring()
        
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.timeout(30)
    def test_full_workflow_integration(self):
        """Test complete workflow integration."""
        # Create project files
        readme = self.temp_dir / "README.md"
        readme.write_text("# Integration Test Project\n\nThis is a test project.")
        
        image = self.temp_dir / "screenshot.png"
        image.write_bytes(b"fake png data")
        
        package_json = self.temp_dir / "package.json"
        package_json.write_text(json.dumps({
            "name": "integration-test",
            "version": "1.0.0"
        }))
        
        # Commit files to Git
        subprocess.run(['git', 'add', '.'], cwd=self.temp_dir, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.temp_dir, check=True)
        subprocess.run(['git', 'tag', 'v1.0.0'], cwd=self.temp_dir, check=True)
        
        # Test various detection mechanisms
        
        # 1. Test content-based change detection
        readme.write_text("# Updated Project\n\nThis content has changed significantly.")
        affects_sync = self.monitor._affects_sync(readme, ContentType.DOCUMENTATION)
        assert affects_sync is True
        
        # 2. Test media file detection
        media_files = self.monitor.get_media_files()
        assert len(media_files) == 1
        assert media_files[0].media_type == MediaType.SCREENSHOT
        
        # 3. Test Git integration
        releases = self.monitor.check_for_releases()
        assert len(releases) >= 1  # Should detect the tag
        
        # 4. Test monitoring stats
        stats = self.monitor.get_monitoring_stats()
        assert stats["git_repo"] is True
        assert stats["known_tags"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])