"""
Test suite for RM-RDI Analysis System Safety Framework

CRITICAL: These tests validate that the analysis system cannot impact production
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.beast_mode.analysis.rm_rdi.safety import (
    OperatorSafetyManager,
    ResourceLimits,
    KillSwitch,
    ResourceMonitor,
    SafetyValidator,
    get_safety_manager,
    initialize_safety,
    emergency_shutdown,
    is_safe_to_proceed
)
from src.beast_mode.analysis.rm_rdi.base import (
    BaseAnalyzer,
    BaseOrchestrator,
    SafetyViolationError,
    validate_analysis_parameters,
    ensure_read_only_path
)
from src.beast_mode.analysis.rm_rdi.data_models import (
    AnalysisResult,
    AnalysisStatus,
    Priority,
    RecommendationCategory
)


class TestSafetyFramework:
    """Test the core safety framework"""
    
    def test_resource_limits_defaults(self):
        """Test that resource limits have safe defaults"""
        limits = ResourceLimits()
        
        # Verify safe CPU limit
        assert limits.max_cpu_percent <= 25.0, "CPU limit too high for production safety"
        
        # Verify safe memory limit
        assert limits.max_memory_mb <= 512.0, "Memory limit too high for production safety"
        
        # Verify reasonable timeout
        assert limits.max_analysis_time_seconds <= 300, "Analysis timeout too long"
        
    def test_kill_switch_initialization(self):
        """Test that kill switch is properly initialized"""
        kill_switch = KillSwitch()
        
        assert kill_switch.is_armed, "Kill switch must be armed by default"
        assert len(kill_switch.shutdown_callbacks) == 0, "Should start with no callbacks"
        
    def test_kill_switch_callback_registration(self):
        """Test kill switch callback registration"""
        kill_switch = KillSwitch()
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
            
        kill_switch.register_shutdown_callback(test_callback)
        assert len(kill_switch.shutdown_callbacks) == 1
        
        # Test emergency shutdown calls callbacks
        kill_switch.emergency_shutdown("test")
        assert callback_called, "Shutdown callback should be called"
        
    @patch('psutil.Process')
    def test_resource_monitor_initialization(self, mock_process):
        """Test resource monitor initialization"""
        limits = ResourceLimits()
        monitor = ResourceMonitor(limits)
        
        assert monitor.limits == limits
        assert not monitor.monitoring, "Should not be monitoring initially"
        assert monitor.monitor_thread is None
        
    def test_safety_validator_read_only_check(self):
        """Test safety validator read-only access validation"""
        validator = SafetyValidator()
        
        # Test with temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test content")
            tmp_path = Path(tmp.name)
            
        try:
            # Make file read-only
            os.chmod(tmp_path, 0o444)
            
            # Should validate as read-only
            assert validator.validate_read_only_access(tmp_path), "Should validate read-only file"
            
        finally:
            # Cleanup
            os.chmod(tmp_path, 0o644)
            tmp_path.unlink()
            
    def test_safety_manager_initialization(self):
        """Test safety manager initialization"""
        manager = OperatorSafetyManager()
        
        assert manager.is_safe_mode, "Should start in safe mode"
        assert manager.analysis_allowed, "Should allow analysis initially"
        assert not manager.emergency_shutdown_triggered, "Should not be in emergency shutdown"
        
    def test_safety_manager_emergency_shutdown(self):
        """Test safety manager emergency shutdown"""
        manager = OperatorSafetyManager()
        
        manager.emergency_shutdown("test shutdown")
        
        assert manager.emergency_shutdown_triggered, "Emergency shutdown should be triggered"
        assert not manager.analysis_allowed, "Analysis should be disabled"


class TestBaseAnalyzer:
    """Test the base analyzer safety features"""
    
    def test_analyzer_cannot_be_created_without_safety(self):
        """Test that analyzers require safety systems"""
        
        class TestAnalyzer(BaseAnalyzer):
            def _execute_analysis(self, **kwargs):
                return AnalysisResult(
                    analysis_id="test",
                    timestamp=None,
                    analysis_types=["test"],
                    status=AnalysisStatus.COMPLETED
                )
                
        # Should initialize with safety systems
        analyzer = TestAnalyzer("test_analyzer")
        assert analyzer.safety_manager is not None
        
    def test_analyzer_safety_validation(self):
        """Test analyzer safety validation"""
        
        class TestAnalyzer(BaseAnalyzer):
            def _execute_analysis(self, **kwargs):
                return AnalysisResult(
                    analysis_id="test",
                    timestamp=None,
                    analysis_types=["test"],
                    status=AnalysisStatus.COMPLETED,
                    safety_validated=True,
                    emergency_shutdown_available=True,
                    can_be_safely_ignored=True
                )
                
        analyzer = TestAnalyzer("test_analyzer")
        
        # Mock safety check to pass
        with patch.object(analyzer.safety_manager, 'is_operation_safe', return_value=True):
            result = analyzer.execute_safe_analysis()
            
        assert result.safety_validated, "Result should be safety validated"
        assert result.emergency_shutdown_available, "Emergency shutdown should be available"
        assert result.can_be_safely_ignored, "Result should be safely ignorable"
        
    def test_analyzer_blocks_unsafe_operations(self):
        """Test that analyzer blocks unsafe operations"""
        
        class TestAnalyzer(BaseAnalyzer):
            def _execute_analysis(self, **kwargs):
                return AnalysisResult(
                    analysis_id="test",
                    timestamp=None,
                    analysis_types=["test"],
                    status=AnalysisStatus.COMPLETED
                )
                
        analyzer = TestAnalyzer("test_analyzer")
        
        # Mock safety check to fail
        with patch.object(analyzer.safety_manager, 'is_operation_safe', return_value=False):
            with pytest.raises(SafetyViolationError):
                analyzer.execute_safe_analysis()


class TestSafetyUtilities:
    """Test safety utility functions"""
    
    def test_validate_analysis_parameters_safe(self):
        """Test parameter validation with safe parameters"""
        safe_params = {
            "analysis_type": "architecture",
            "read_only": True,
            "timeout": 300
        }
        
        assert validate_analysis_parameters(**safe_params), "Safe parameters should be valid"
        
    def test_validate_analysis_parameters_unsafe(self):
        """Test parameter validation with unsafe parameters"""
        unsafe_params = {
            "write_file": "/etc/passwd",
            "modify_system": True,
            "delete_data": "all"
        }
        
        assert not validate_analysis_parameters(**unsafe_params), "Unsafe parameters should be invalid"
        
    def test_ensure_read_only_path_safe(self):
        """Test path validation with safe paths"""
        safe_path = Path("src/beast_mode/analysis")
        result = ensure_read_only_path(safe_path)
        
        assert result.is_absolute(), "Should return absolute path"
        
    def test_ensure_read_only_path_unsafe(self):
        """Test path validation with unsafe paths"""
        unsafe_paths = [
            Path("/etc/passwd"),
            Path("/usr/bin/python"),
            Path("/sys/kernel")
        ]
        
        for unsafe_path in unsafe_paths:
            with pytest.raises(SafetyViolationError):
                ensure_read_only_path(unsafe_path)


class TestDataModelSafety:
    """Test that data models enforce safety"""
    
    def test_analysis_result_immutability(self):
        """Test that AnalysisResult is immutable"""
        result = AnalysisResult(
            analysis_id="test",
            timestamp=None,
            analysis_types=["test"],
            status=AnalysisStatus.COMPLETED
        )
        
        # Should not be able to modify frozen dataclass
        with pytest.raises(AttributeError):
            result.analysis_id = "modified"
            
    def test_analysis_result_safety_defaults(self):
        """Test that AnalysisResult has safe defaults"""
        result = AnalysisResult(
            analysis_id="test",
            timestamp=None,
            analysis_types=["test"],
            status=AnalysisStatus.COMPLETED
        )
        
        assert result.safety_validated, "Should be safety validated by default"
        assert result.can_be_safely_ignored, "Should be safely ignorable by default"
        assert result.emergency_shutdown_available, "Emergency shutdown should be available"
        assert len(result.operator_notes) > 0, "Should have operator safety notes"


class TestIntegrationSafety:
    """Test integration safety features"""
    
    def test_global_safety_manager_singleton(self):
        """Test that global safety manager is singleton"""
        manager1 = get_safety_manager()
        manager2 = get_safety_manager()
        
        assert manager1 is manager2, "Should return same instance"
        
    def test_safety_initialization(self):
        """Test global safety initialization"""
        # Should be able to initialize safety systems
        result = initialize_safety()
        assert isinstance(result, bool), "Should return boolean result"
        
    def test_emergency_shutdown_global(self):
        """Test global emergency shutdown"""
        # Should not raise exception
        emergency_shutdown("test global shutdown")
        
        # Should block operations after shutdown
        assert not is_safe_to_proceed("test_operation"), "Should block operations after emergency shutdown"


class TestOperatorCommands:
    """Test operator command integration"""
    
    def test_analysis_control_script_exists(self):
        """Test that operator control script exists"""
        script_path = Path("scripts/analysis_control.py")
        assert script_path.exists(), "Operator control script must exist"
        assert os.access(script_path, os.X_OK), "Control script must be executable"
        
    def test_makefile_targets_exist(self):
        """Test that Makefile emergency targets exist"""
        makefile_path = Path("makefiles/analysis.mk")
        assert makefile_path.exists(), "Analysis Makefile must exist"
        
        content = makefile_path.read_text()
        
        # Check for emergency commands
        assert "analysis-kill:" in content, "Emergency kill target must exist"
        assert "analysis-throttle:" in content, "Throttle target must exist"
        assert "analysis-stop:" in content, "Stop target must exist"
        assert "analysis-uninstall:" in content, "Uninstall target must exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])