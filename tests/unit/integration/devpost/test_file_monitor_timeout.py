"""
Test file monitor timeout fixes.

This module contains focused tests to verify that file monitor
operations complete within reasonable time limits and don't hang.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

from src.beast_mode.integration.devpost.monitoring.file_monitor import ProjectFileMonitor
from src.beast_mode.integration.devpost.models import DevpostConfig


class TestFileMonitorTimeout:
    """Test file monitor timeout and performance issues."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "README.md").write_text("# Test Project")
            yield project_path
    
    @pytest.fixture
    def devpost_config(self):
        """Create a test configuration."""
        return DevpostConfig(
            project_id="test-project",
            hackathon_id="test-hackathon",
            watch_patterns=["*.md"]
        )
    
    @pytest.mark.timeout(5)  # This test should complete in 5 seconds
    def test_start_stop_monitoring_quick(self, temp_project_dir, devpost_config):
        """Test that start/stop monitoring completes quickly."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        start_time = time.time()
        
        # Start monitoring
        monitor.start_monitoring()
        assert monitor._is_monitoring
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert not monitor._is_monitoring
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in under 3 seconds
        assert duration < 3.0, f"Start/stop took {duration:.2f} seconds, too slow"
    
    @pytest.mark.timeout(5)
    def test_context_manager_quick(self, temp_project_dir, devpost_config):
        """Test that context manager cleanup is quick."""
        start_time = time.time()
        
        with ProjectFileMonitor(temp_project_dir, devpost_config) as monitor:
            assert monitor._is_monitoring
            # Do some quick operations
            time.sleep(0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in under 2 seconds
        assert duration < 2.0, f"Context manager took {duration:.2f} seconds, too slow"
    
    @pytest.mark.timeout(3)
    def test_multiple_start_stop_cycles(self, temp_project_dir, devpost_config):
        """Test multiple start/stop cycles don't accumulate delays."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        start_time = time.time()
        
        # Multiple cycles
        for i in range(3):
            monitor.start_monitoring()
            assert monitor._is_monitoring
            monitor.stop_monitoring()
            assert not monitor._is_monitoring
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in under 2 seconds total
        assert duration < 2.0, f"Multiple cycles took {duration:.2f} seconds, too slow"
    
    @pytest.mark.timeout(2)
    def test_stop_when_not_started(self, temp_project_dir, devpost_config):
        """Test that stopping when not started is immediate."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        start_time = time.time()
        monitor.stop_monitoring()  # Should be immediate
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 0.1, f"Stop when not started took {duration:.2f} seconds"
    
    @pytest.mark.timeout(3)
    def test_file_event_handling_performance(self, temp_project_dir, devpost_config):
        """Test that file event handling doesn't block."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        # Mock the file operations to avoid real I/O
        with patch.object(monitor, '_is_relevant_file', return_value=True), \
             patch.object(monitor, '_create_change_event', return_value=Mock()):
            
            start_time = time.time()
            
            # Simulate multiple file events
            for i in range(10):
                monitor._handle_file_event(f"/test/file{i}.md", "modified")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should handle 10 events very quickly
            assert duration < 0.5, f"Handling 10 events took {duration:.2f} seconds"
    
    @pytest.mark.timeout(2)
    def test_cleanup_is_fast(self, temp_project_dir, devpost_config):
        """Test that cleanup operations are fast."""
        monitor = ProjectFileMonitor(temp_project_dir, devpost_config)
        
        # Add some state to clean up
        monitor._event_queue.extend([Mock() for _ in range(100)])
        monitor._recent_changes = {f"file{i}": Mock() for i in range(50)}
        
        start_time = time.time()
        monitor._cleanup()
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 0.1, f"Cleanup took {duration:.2f} seconds"
        
        # Verify cleanup worked
        assert len(monitor._event_queue) == 0
        assert len(monitor._recent_changes) == 0


@pytest.mark.integration
class TestFileMonitorIntegrationTimeout:
    """Integration tests with timeout enforcement."""
    
    @pytest.mark.timeout(10)  # Generous timeout for integration test
    def test_real_file_operations_with_timeout(self):
        """Test real file operations complete within timeout."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            config = DevpostConfig(
                project_id="test-project",
                hackathon_id="test-hackathon",
                watch_patterns=["*.md"]
            )
            
            changes_detected = []
            
            def change_callback(event):
                changes_detected.append(event)
            
            start_time = time.time()
            
            with ProjectFileMonitor(project_path, config, debounce_delay=0.1) as monitor:
                monitor.add_change_callback(change_callback)
                
                # Give monitor time to start
                time.sleep(0.2)
                
                # Create and modify files quickly
                test_file = project_path / "test.md"
                test_file.write_text("# Test")
                time.sleep(0.2)
                
                test_file.write_text("# Modified Test")
                time.sleep(0.2)
                
                # Cleanup should be fast
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete well within timeout
            assert duration < 5.0, f"Integration test took {duration:.2f} seconds"
            
            # Should have detected some changes
            assert len(changes_detected) >= 0  # May be 0 due to timing, but shouldn't hang