#!/usr/bin/env python3
"""
RC1 Model Compliance Test

This test validates that RC1 modules fully comply with the unified ReflectiveModule interface.

TRACE: REQ-RC1-RDI-008, REQ-RC1-RMDDD-008
TEST: Comprehensive model compliance validation
IMPLEMENTATION: Model compliance testing framework
"""

import unittest
import sys
from pathlib import Path
from typing import Dict, Any, List
import inspect

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.rc1.foundation.makefile_health_manager import MakefileHealthManager
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)


class RC1ModelComplianceTest(unittest.TestCase):
    """Test case for RC1 model compliance validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rc1_module = MakefileHealthManager()
        self.unified_interface = ReflectiveModule
        
        # Get all methods from the unified interface
        self.required_methods = [
            method for method in dir(self.unified_interface)
            if not method.startswith('_') and callable(getattr(self.unified_interface, method))
        ]
        
        # Get all abstract methods from the unified interface
        self.abstract_methods = [
            method for method in dir(self.unified_interface)
            if hasattr(getattr(self.unified_interface, method), '__isabstractmethod__')
        ]
    
    def test_inheritance_compliance(self):
        """
        Test that RC1 module properly inherits from unified ReflectiveModule.
        
        TRACE: REQ-RC1-RDI-001, REQ-RC1-RMDDD-001
        TEST: Validates inheritance compliance
        IMPLEMENTATION: Inheritance validation
        """
        self.assertIsInstance(self.rc1_module, ReflectiveModule, 
                            "RC1 module must inherit from unified ReflectiveModule")
        self.assertTrue(issubclass(MakefileHealthManager, ReflectiveModule), 
                       "RC1 module class must be subclass of unified ReflectiveModule")
    
    def test_abstract_methods_implementation(self):
        """
        Test that RC1 module implements all abstract methods.
        
        TRACE: REQ-RC1-RDI-002, REQ-RC1-RMDDD-002
        TEST: Validates abstract method implementation
        IMPLEMENTATION: Abstract method validation
        """
        for method_name in self.abstract_methods:
            self.assertTrue(hasattr(self.rc1_module, method_name), 
                          f"RC1 module must implement abstract method: {method_name}")
            
            method = getattr(self.rc1_module, method_name)
            self.assertTrue(callable(method), 
                          f"RC1 module method {method_name} must be callable")
    
    def test_required_methods_exist(self):
        """
        Test that RC1 module has all required methods from unified interface.
        
        TRACE: REQ-RC1-RDI-003, REQ-RC1-RMDDD-003
        TEST: Validates required method existence
        IMPLEMENTATION: Required method validation
        """
        for method_name in self.required_methods:
            self.assertTrue(hasattr(self.rc1_module, method_name), 
                          f"RC1 module must have method: {method_name}")
    
    def test_get_module_info_compliance(self):
        """
        Test that get_module_info returns correct format.
        
        TRACE: REQ-RC1-RDI-004, REQ-RC1-RMDDD-004
        TEST: Validates get_module_info compliance
        IMPLEMENTATION: Module info validation
        """
        module_info = self.rc1_module.get_module_info()
        
        self.assertIsInstance(module_info, dict, "get_module_info must return dict")
        self.assertIn('module_id', module_info, "Module info must have module_id")
        self.assertIn('version', module_info, "Module info must have version")
        self.assertIn('class_name', module_info, "Module info must have class_name")
        self.assertIn('capabilities', module_info, "Module info must have capabilities")
    
    def test_get_capabilities_compliance(self):
        """
        Test that get_capabilities returns correct format.
        
        TRACE: REQ-RC1-RDI-005, REQ-RC1-RMDDD-005
        TEST: Validates get_capabilities compliance
        IMPLEMENTATION: Capabilities validation
        """
        capabilities = self.rc1_module.get_capabilities()
        
        self.assertIsInstance(capabilities, list, "get_capabilities must return list")
        self.assertGreater(len(capabilities), 0, "Must have at least one capability")
        
        for cap in capabilities:
            self.assertIsInstance(cap, ModuleCapability, 
                                "All capabilities must be ModuleCapability enum values")
    
    def test_get_health_status_compliance(self):
        """
        Test that get_health_status returns correct format.
        
        TRACE: REQ-RC1-RDI-006, REQ-RC1-RMDDD-006
        TEST: Validates get_health_status compliance
        IMPLEMENTATION: Health status validation
        """
        health_status = self.rc1_module.get_health_status()
        
        self.assertIsInstance(health_status, ModuleHealth, 
                            "get_health_status must return ModuleHealth object")
        self.assertIsInstance(health_status.module_id, str, 
                            "Health status must have module_id string")
        self.assertIsInstance(health_status.status, ModuleStatus, 
                            "Health status must have ModuleStatus enum")
        self.assertIsInstance(health_status.health_score, float, 
                            "Health status must have health_score float")
        self.assertIsInstance(health_status.issues, list, 
                            "Health status must have issues list")
    
    def test_graceful_degradation_compliance(self):
        """
        Test that graceful_degradation returns correct format.
        
        TRACE: REQ-RC1-RDI-007, REQ-RC1-RMDDD-007
        TEST: Validates graceful_degradation compliance
        IMPLEMENTATION: Graceful degradation validation
        """
        degradation_result = self.rc1_module.graceful_degradation()
        
        self.assertIsInstance(degradation_result, GracefulDegradationResult, 
                            "graceful_degradation must return GracefulDegradationResult")
        self.assertIsInstance(degradation_result.success, bool, 
                            "Degradation result must have success boolean")
        self.assertIsInstance(degradation_result.degraded_capabilities, list, 
                            "Degradation result must have degraded_capabilities list")
        self.assertIsInstance(degradation_result.remaining_capabilities, list, 
                            "Degradation result must have remaining_capabilities list")
    
    def test_registry_methods_compliance(self):
        """
        Test that registry methods work correctly.
        
        TRACE: REQ-RC1-RDI-008, REQ-RC1-RMDDD-008
        TEST: Validates registry methods compliance
        IMPLEMENTATION: Registry methods validation
        """
        # Test get_interface_metadata
        metadata = self.rc1_module.get_interface_metadata()
        self.assertIsInstance(metadata, dict, "get_interface_metadata must return dict")
        self.assertIn('module_id', metadata, "Metadata must have module_id")
        self.assertIn('interface_type', metadata, "Metadata must have interface_type")
        self.assertIn('version', metadata, "Metadata must have version")
        self.assertIn('capabilities', metadata, "Metadata must have capabilities")
        
        # Test register_module (with mock registry)
        class MockRegistry:
            def __init__(self):
                self.registered_modules = []
            
            def register(self, metadata):
                self.registered_modules.append(metadata)
        
        mock_registry = MockRegistry()
        self.rc1_module.register_module(mock_registry)
        self.assertEqual(len(mock_registry.registered_modules), 1, 
                        "register_module must register with registry")
    
    def test_health_check_compliance(self):
        """
        Test that health_check returns correct format.
        
        TRACE: REQ-RC1-RDI-009, REQ-RC1-RMDDD-009
        TEST: Validates health_check compliance
        IMPLEMENTATION: Health check validation
        """
        health_check_result = self.rc1_module.health_check()
        
        self.assertIsInstance(health_check_result, dict, "health_check must return dict")
        self.assertIn('status', health_check_result, "Health check must have status")
        self.assertIn('timestamp', health_check_result, "Health check must have timestamp")
        self.assertIn('module_id', health_check_result, "Health check must have module_id")
    
    def test_prometheus_methods_compliance(self):
        """
        Test that Prometheus methods exist and work correctly.
        
        TRACE: REQ-RC1-RDI-010, REQ-RC1-RMDDD-010
        TEST: Validates Prometheus methods compliance
        IMPLEMENTATION: Prometheus methods validation
        """
        # Test Prometheus methods exist
        prometheus_methods = [
            '_should_enable_prometheus',
            '_initialize_prometheus_metrics',
            '_collect_prometheus_metrics',
            'get_prometheus_metrics',
            'enable_prometheus_metrics'
        ]
        
        for method_name in prometheus_methods:
            self.assertTrue(hasattr(self.rc1_module, method_name), 
                          f"RC1 module must have Prometheus method: {method_name}")
        
        # Test _should_enable_prometheus
        should_enable = self.rc1_module._should_enable_prometheus()
        self.assertIsInstance(should_enable, bool, 
                            "_should_enable_prometheus must return boolean")
        
        # Test get_prometheus_metrics
        metrics = self.rc1_module.get_prometheus_metrics()
        self.assertIsInstance(metrics, dict, 
                            "get_prometheus_metrics must return dict")
    
    def test_activity_tracking_methods_compliance(self):
        """
        Test that activity tracking methods exist and work correctly.
        
        TRACE: REQ-RC1-RDI-011, REQ-RC1-RMDDD-011
        TEST: Validates activity tracking methods compliance
        IMPLEMENTATION: Activity tracking methods validation
        """
        # Test activity tracking methods exist
        activity_methods = [
            '_update_activity',
            '_increment_error_count',
            '_increment_warning_count'
        ]
        
        for method_name in activity_methods:
            self.assertTrue(hasattr(self.rc1_module, method_name), 
                          f"RC1 module must have activity tracking method: {method_name}")
        
        # Test _update_activity
        self.rc1_module._update_activity()
        self.assertIsNotNone(self.rc1_module._last_activity, 
                           "_update_activity must update last_activity")
        
        # Test error counting
        initial_error_count = self.rc1_module._error_count
        self.rc1_module._increment_error_count()
        self.assertEqual(self.rc1_module._error_count, initial_error_count + 1, 
                        "_increment_error_count must increment error count")
        
        # Test warning counting
        initial_warning_count = self.rc1_module._warning_count
        self.rc1_module._increment_warning_count()
        self.assertEqual(self.rc1_module._warning_count, initial_warning_count + 1, 
                        "_increment_warning_count must increment warning count")
    
    def test_base_class_initialization_compliance(self):
        """
        Test that base class initialization works correctly.
        
        TRACE: REQ-RC1-RDI-012, REQ-RC1-RMDDD-012
        TEST: Validates base class initialization compliance
        IMPLEMENTATION: Base class initialization validation
        """
        # Test that base class attributes are initialized
        self.assertIsNotNone(self.rc1_module._start_time, 
                           "Base class must initialize _start_time")
        self.assertIsNotNone(self.rc1_module._last_activity, 
                           "Base class must initialize _last_activity")
        self.assertIsInstance(self.rc1_module._error_count, int, 
                            "Base class must initialize _error_count as int")
        self.assertIsInstance(self.rc1_module._warning_count, int, 
                            "Base class must initialize _warning_count as int")
    
    def test_complete_interface_compliance(self):
        """
        Test complete interface compliance with unified ReflectiveModule.
        
        TRACE: REQ-RC1-RDI-013, REQ-RC1-RMDDD-013
        TEST: Validates complete interface compliance
        IMPLEMENTATION: Complete interface compliance validation
        """
        # Get all methods from RC1 module
        rc1_methods = [
            method for method in dir(self.rc1_module)
            if not method.startswith('_') and callable(getattr(self.rc1_module, method))
        ]
        
        # Check that RC1 module has all required methods
        missing_methods = []
        for method_name in self.required_methods:
            if method_name not in rc1_methods:
                missing_methods.append(method_name)
        
        self.assertEqual(len(missing_methods), 0, 
                        f"RC1 module missing required methods: {missing_methods}")
        
        # Check that RC1 module implements all abstract methods
        missing_abstract_methods = []
        for method_name in self.abstract_methods:
            if method_name not in rc1_methods:
                missing_abstract_methods.append(method_name)
        
        self.assertEqual(len(missing_abstract_methods), 0, 
                        f"RC1 module missing abstract methods: {missing_abstract_methods}")


if __name__ == '__main__':
    unittest.main()
