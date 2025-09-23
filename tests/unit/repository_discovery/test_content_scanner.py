#!/usr/bin/env python3
"""
Unit tests for ContentScanner
"""

import pytest
import tempfile
from pathlib import Path
from src.repository_discovery.core.content_scanner import ContentScanner, ContentDiscoveryError


class TestContentScanner:
    """Test ContentScanner functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.scanner = ContentScanner()
    
    def test_scanner_initialization(self):
        """Test scanner initializes correctly"""
        assert self.scanner.module_id == "ContentScanner"
        assert self.scanner.get_capabilities() is not None
        assert self.scanner.get_health_status().status.value in ["healthy", "degraded", "error"]
    
    def test_discover_content_basic(self):
        """Test basic content discovery"""
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "test1.txt").write_text("test content 1")
            (temp_path / "test2.py").write_text("print('hello')")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "test3.md").write_text("# Test")
            
            # Scan the directory
            result = self.scanner.discover_all_content(temp_path)
            
            # Verify results
            assert result.scan_id is not None
            assert len(result.discovered_files) >= 3
            assert len(result.discovered_directories) >= 1
            assert result.error_count == 0
            assert result.total_size > 0
    
    def test_exclusion_patterns(self):
        """Test exclusion patterns work correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files that should be excluded
            (temp_path / "test.txt").write_text("include me")
            (temp_path / "test.pyc").write_text("exclude me")
            (temp_path / ".DS_Store").write_text("exclude me")
            
            result = self.scanner.discover_all_content(temp_path)
            
            # Should find test.txt but not the excluded files
            discovered_names = [Path(f).name for f in result.discovered_files]
            assert "test.txt" in discovered_names
            assert "test.pyc" not in discovered_names
            assert ".DS_Store" not in discovered_names
    
    def test_nonexistent_path_error(self):
        """Test error handling for nonexistent paths"""
        nonexistent_path = Path("/this/path/does/not/exist")
        
        with pytest.raises(ContentDiscoveryError):
            self.scanner.discover_all_content(nonexistent_path)
    
    def test_scan_progress_tracking(self):
        """Test scan progress tracking"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.txt").write_text("test")
            
            # Start scan (this will complete immediately for small directory)
            result = self.scanner.discover_all_content(temp_path)
            
            # Verify scan completed
            assert result.scan_id is not None
            progress = self.scanner.get_scan_progress(result.scan_id)
            assert progress is None  # Should be cleaned up after completion
    
    def test_reflective_module_compliance(self):
        """Test ReflectiveModule interface compliance"""
        # Test module info
        info = self.scanner.get_module_info()
        assert info["module_id"] == "ContentScanner"
        assert info["name"] == "ContentScanner"
        assert "capabilities" in info
        
        # Test health status
        health = self.scanner.get_health_status()
        assert health.module_id == "ContentScanner"
        assert health.health_score >= 0.0
        
        # Test graceful degradation
        degradation = self.scanner.graceful_degradation()
        assert degradation.success in [True, False]