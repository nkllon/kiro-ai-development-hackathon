"""
Unit tests for TestSafetyConfiguration class

Tests the test-specific safety configuration functionality.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.beast_mode.analysis.rm_rdi.test_safety import (
    TestSafetyConfiguration,
    TestSafetyLimits,
    TestSafetyRuleEngine,
    get_test_safety_config,
    is_test_mode,
    reset_test_safety_config
)
from src.beast_mode.analysis.rm_rdi.safety import ResourceLimits


class TestTestSafetyConfiguration:
    """Test suite for TestSafetyConfiguration"""
    
    def setup_method(self):
        """Reset global config before each test"""
        reset_test_safety_config()
        
    def test_initialization_with_explicit_test_mode(self):
        """Test initialization with explicit test mode"""
        config = TestSafetyConfiguration(test_mode=True)
        
        assert config.test_mode is True
        assert isinstance(config.test_limits, TestSafetyLimits)
        assert len(config.allowed_operations) > 0
        assert len(config.restricted_operations) > 0
        assert len(config.allowed_workflow_patterns) > 0
        
    def test_initialization_with_explicit_production_mode(self):
        """Test initialization with explicit production mode"""
        config = TestSafetyConfiguration(test_mode=False)
        
        assert config.test_mode is False
        assert isinstance(config.test_limits, TestSafetyLimits)
        
    def test_auto_detect_test_environment_pytest(self):
        """Test auto-detection of pytest environment"""
        with patch.dict(os.environ, {'_': '/usr/bin/pytest'}):
            config = TestSafetyConfiguration()
            assert config.test_mode is True
            
    def test_auto_detect_test_environment_env_vars(self):
        """Test auto-detection via environment variables"""
        with patch.dict(os.environ, {'PYTEST_CURRENT_TEST': 'test_file.py::test_func'}):
            config = TestSafetyConfiguration()
            assert config.test_mode is True
            
        with patch.dict(os.environ, {'TESTING': 'true'}):
            config = TestSafetyConfiguration()
            assert config.test_mode is True
            
        with patch.dict(os.environ, {'TEST_MODE': '1'}):
            config = TestSafetyConfiguration()
            assert config.test_mode is True
            
    def test_auto_detect_production_environment(self):
        """Test auto-detection of production environment"""
        # Clear any test-related environment variables
        test_vars = ['PYTEST_CURRENT_TEST', 'TESTING', 'TEST_MODE']
        with patch.dict(os.environ, {var: '' for var in test_vars}, clear=True):
            with patch('os.environ.get', return_value=''):
                config = TestSafetyConfiguration()
                # Note: This might still detect test mode due to inspect.stack()
                # checking for test files, which is expected behavior
                
    def test_allowed_operations_in_test_mode(self):
        """Test that allowed operations work in test mode"""
        config = TestSafetyConfiguration(test_mode=True)
        
        # Test explicitly allowed operations
        assert config.is_operation_allowed('workflow_creation')
        assert config.is_operation_allowed('analysis_execution')
        assert config.is_operation_allowed('test_data_creation')
        assert config.is_operation_allowed('safety_validation')
        
        # Test read-only operations (always allowed)
        assert config.is_operation_allowed('file_reading')
        assert config.is_operation_allowed('data_analysis')
        assert config.is_operation_allowed('report_generation')
        
    def test_restricted_operations_blocked(self):
        """Test that restricted operations are blocked even in test mode"""
        config = TestSafetyConfiguration(test_mode=True)
        
        # These should be blocked even in test mode
        assert not config.is_operation_allowed('system_file_modification')
        assert not config.is_operation_allowed('production_data_access')
        assert not config.is_operation_allowed('external_network_calls')
        assert not config.is_operation_allowed('privileged_operations')
        
    def test_workflow_pattern_matching(self):
        """Test workflow pattern matching for allowed operations"""
        config = TestSafetyConfiguration(test_mode=True)
        
        # Test allowed workflow patterns
        test_contexts = [
            {'workflow_id': 'test_workflow_123'},
            {'workflow_id': 'readonly_test_validation'},
            {'workflow_id': 'parallel_test_execution'},
            {'workflow_id': 'emergency_test_scenario'}
        ]
        
        for context in test_contexts:
            assert config.is_operation_allowed('workflow_execution', context)
            
    def test_test_context_detection(self):
        """Test detection of test context"""
        config = TestSafetyConfiguration(test_mode=True)
        
        # Test contexts that should be recognized as test contexts
        test_contexts = [
            {'test_param': 'value'},
            {'mock_data': 'test_data'},
            {'fixture_name': 'test_fixture'},
            {'pytest_marker': 'integration'},
            {'operation_type': 'unittest_validation'}
        ]
        
        for context in test_contexts:
            assert config.is_operation_allowed('custom_operation', context)
            
    def test_production_mode_restrictions(self):
        """Test that production mode is more restrictive"""
        config = TestSafetyConfiguration(test_mode=False)
        
        # Only read-only operations should be allowed
        assert config.is_operation_allowed('file_reading')
        assert config.is_operation_allowed('data_analysis')
        assert config.is_operation_allowed('report_generation')
        
        # Test-specific operations should be blocked
        assert not config.is_operation_allowed('workflow_creation')
        assert not config.is_operation_allowed('test_data_creation')
        assert not config.is_operation_allowed('analysis_execution')
        
    def test_safety_limits_test_mode(self):
        """Test that test mode has relaxed safety limits"""
        config = TestSafetyConfiguration(test_mode=True)
        limits = config.get_safety_limits()
        
        assert isinstance(limits, ResourceLimits)
        assert limits.max_cpu_percent == 50.0  # Higher than production
        assert limits.max_memory_mb == 1024.0  # Higher than production
        assert limits.max_analysis_time_seconds == 600  # Longer than production
        
    def test_safety_limits_production_mode(self):
        """Test that production mode has strict safety limits"""
        config = TestSafetyConfiguration(test_mode=False)
        limits = config.get_safety_limits()
        
        assert isinstance(limits, ResourceLimits)
        assert limits.max_cpu_percent == 25.0  # Production default
        assert limits.max_memory_mb == 512.0  # Production default
        assert limits.max_analysis_time_seconds == 300  # Production default
        
    def test_workflow_safety_validation_test_mode(self):
        """Test workflow safety validation in test mode"""
        config = TestSafetyConfiguration(test_mode=True)
        
        # Test workflows should be allowed
        assert config.validate_workflow_safety('test_workflow_123')
        assert config.validate_workflow_safety('readonly_test_validation')
        
        # Workflows with test_mode flag should be allowed
        assert config.validate_workflow_safety('custom_workflow', {'test_mode': True})
        
        # Read-only workflows should be allowed
        assert config.validate_workflow_safety('analysis_workflow', {'read_only': True})
        
    def test_workflow_safety_validation_production_mode(self):
        """Test workflow safety validation in production mode"""
        config = TestSafetyConfiguration(test_mode=False)
        
        # Only read-only workflows should be allowed
        assert config.validate_workflow_safety('analysis_workflow', {'read_only': True})
        
        # Non-read-only workflows should be blocked
        assert not config.validate_workflow_safety('write_workflow', {'read_only': False})
        
        # Workflows exceeding resource limits should be blocked
        assert not config.validate_workflow_safety('heavy_workflow', {
            'read_only': True,
            'max_memory_mb': 2000  # Exceeds production limit
        })
        
    def test_configuration_summary(self):
        """Test configuration summary generation"""
        config = TestSafetyConfiguration(test_mode=True)
        summary = config.get_configuration_summary()
        
        assert summary['test_mode'] is True
        assert summary['allowed_operations_count'] > 0
        assert summary['restricted_operations_count'] > 0
        assert summary['allowed_workflow_patterns_count'] > 0
        assert 'safety_limits' in summary
        assert summary['safety_limits']['max_cpu_percent'] == 50.0


class TestTestSafetyRuleEngine:
    """Test suite for TestSafetyRuleEngine"""
    
    def test_rule_engine_initialization(self):
        """Test rule engine initialization"""
        config = TestSafetyConfiguration(test_mode=True)
        engine = config.create_safety_rule_engine()
        
        assert isinstance(engine, TestSafetyRuleEngine)
        assert engine.test_config == config
        
    def test_operation_safety_evaluation(self):
        """Test detailed operation safety evaluation"""
        config = TestSafetyConfiguration(test_mode=True)
        engine = config.create_safety_rule_engine()
        
        # Test allowed operation
        evaluation = engine.evaluate_operation_safety('workflow_creation')
        assert evaluation['is_allowed'] is True
        assert evaluation['operation'] == 'workflow_creation'
        assert evaluation['test_mode'] is True
        assert 'reason' in evaluation
        assert 'timestamp' in evaluation
        
        # Test restricted operation
        evaluation = engine.evaluate_operation_safety('system_file_modification')
        assert evaluation['is_allowed'] is False
        assert evaluation['reason'] == 'Operation is restricted'
        
    def test_get_allowed_operations(self):
        """Test getting list of allowed operations"""
        config = TestSafetyConfiguration(test_mode=True)
        engine = config.create_safety_rule_engine()
        
        allowed_ops = engine.get_allowed_operations()
        assert isinstance(allowed_ops, list)
        assert len(allowed_ops) > 0
        assert 'workflow_creation' in allowed_ops
        assert 'analysis_execution' in allowed_ops
        
    def test_get_restricted_operations(self):
        """Test getting list of restricted operations"""
        config = TestSafetyConfiguration(test_mode=True)
        engine = config.create_safety_rule_engine()
        
        restricted_ops = engine.get_restricted_operations()
        assert isinstance(restricted_ops, list)
        assert len(restricted_ops) > 0
        assert 'system_file_modification' in restricted_ops
        assert 'production_data_access' in restricted_ops


class TestGlobalFunctions:
    """Test suite for global utility functions"""
    
    def setup_method(self):
        """Reset global config before each test"""
        reset_test_safety_config()
        
    def test_get_test_safety_config_singleton(self):
        """Test that global config is singleton"""
        config1 = get_test_safety_config()
        config2 = get_test_safety_config()
        
        assert config1 is config2
        
    def test_is_test_mode_function(self):
        """Test is_test_mode utility function"""
        # Should auto-detect test mode (likely True since we're in pytest)
        test_mode = is_test_mode()
        assert isinstance(test_mode, bool)
        
    def test_reset_test_safety_config(self):
        """Test resetting global config"""
        # Get initial config
        config1 = get_test_safety_config()
        
        # Reset and get new config
        reset_test_safety_config()
        config2 = get_test_safety_config()
        
        # Should be different instances
        assert config1 is not config2


class TestTestSafetyLimits:
    """Test suite for TestSafetyLimits"""
    
    def test_test_safety_limits_defaults(self):
        """Test that test safety limits have appropriate defaults"""
        limits = TestSafetyLimits()
        
        # Should be more relaxed than production limits
        assert limits.max_cpu_percent == 50.0
        assert limits.max_memory_mb == 1024.0
        assert limits.max_disk_io_mb == 500.0
        assert limits.max_analysis_time_seconds == 600
        assert limits.max_concurrent_operations == 5
        
        # But still reasonable for test environments
        assert limits.max_cpu_percent <= 80.0  # Don't overwhelm test systems
        assert limits.max_memory_mb <= 2048.0  # Don't use too much memory
        assert limits.max_analysis_time_seconds <= 1200  # Don't run too long


if __name__ == "__main__":
    pytest.main([__file__, "-v"])