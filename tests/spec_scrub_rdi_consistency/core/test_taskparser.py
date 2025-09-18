#!/usr/bin/env python3
"""
Tests for Taskparser - Taskparser Tests
================

Comprehensive tests for Taskparser functionality.
Tests RM-DDD compliance and core functionality.

Author: Beast Mode Framework
Date: 2025-09-18
Version: 1.0
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.spec_scrub_rdi_consistency.core.taskparser import Taskparser
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestTaskparser:
    """Test Taskparser functionality"""
    
    @pytest.fixture
    def taskparser(self):
        """Create Taskparser instance"""
        return Taskparser()
    
    def test_module_info(self, taskparser):
        """Test module information compliance"""
        info = taskparser.get_module_info()
        
        assert info["module_id"] == "Taskparser"
        assert info["name"] == "Taskparser"
        assert info["version"] == "1.0.0"
        assert "description" in info
        assert "capabilities" in info
    
    def test_capabilities(self, taskparser):
        """Test module capabilities"""
        capabilities = taskparser.get_capabilities()
        
        assert ModuleCapability.CORE_FUNCTIONALITY in capabilities
        assert ModuleCapability.DATA_PROCESSING in capabilities
        assert ModuleCapability.VALIDATION in capabilities
    
    def test_health_status(self, taskparser):
        """Test health status reporting"""
        health = taskparser.get_health_status()
        
        assert health.module_id == "Taskparser"
        assert health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.ERROR]
        assert 0.0 <= health.health_score <= 1.0
        assert isinstance(health.issues, list)
    
    def test_graceful_degradation(self, taskparser):
        """Test graceful degradation"""
        result = taskparser.graceful_degradation()
        
        assert result.success is True
        assert isinstance(result.degraded_capabilities, list)
        assert isinstance(result.remaining_capabilities, list)
        assert ModuleCapability.CORE_FUNCTIONALITY in result.remaining_capabilities
    
        def test_process_functionality(self, taskparser):
        """Test main processing functionality"""
        test_data = {"test": "data"}
        result = taskparser.process(test_data)
        
        assert result["success"] is True
        assert result["processed"] is True
        assert result["data"] == test_data
    
    def test_error_handling(self, taskparser):
        """Test error handling"""
        # Test with invalid data that should cause an error
        try:
            result = taskparser.process(None)
            # If no error, check result indicates failure gracefully
            if "success" in result:
                assert result["success"] is False
        except Exception:
            # Exception is acceptable for invalid input
            pass


if __name__ == "__main__":
    pytest.main([__file__])
