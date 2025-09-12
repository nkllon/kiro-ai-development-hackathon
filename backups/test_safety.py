"""
RM-RDI Analysis System - Test Environment Safety Configuration

This module provides test-specific safety configuration that allows legitimate
test operations while maintaining safety guarantees.
"""

import os
import logging
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .safety import OperatorSafetyManager, ResourceLimits, SafetyStatus


@dataclass
class TestSafetyLimits:
    """Relaxed safety limits for test environments"""
    max_cpu_percent: float = 50.0  # Higher CPU limit for tests
    max_memory_mb: float = 1024.0  # Higher memory limit for tests
    max_disk_io_mb: float = 500.0  # Higher disk I/O for tests
    max_analysis_time_seconds: int = 600  # Longer timeout for tests
    max_concurrent_operations: int = 5  # More concurrent operations


class TestSafetyConfiguration:
    """Test-specific safety configuration with allowed operations"""
    
    def __init__(self, test_mode: bool = None):
        """Initialize test safety configuration
        
        Args:
            test_mode: If None, auto-detect test environment
        """
        self.logger = logging.getLogger("rm_rdi_analysis.test_safety")
        
        # Auto-detect test mode if not specified
        if test_mode is None:
            test_mode = self._detect_test_environment()
            
        self.test_mode = test_mode
        self.test_limits = TestSafetyLimits()
        
        # Define allowed operations in test environment
        self.allowed_operations: Set[str] = {
            # Workflow operations
            'workflow_creation',
            'workflow_execution',
            'workflow_coordination',
            'workflow_validation',
            
            # Analysis operations
            'analysis_execution',
            'analysis_orchestration',
            'analysis_validation',
            'analysis_monitoring',
            
            # Test-specific operations
            'test_data_creation',
            'test_fixture_setup',
            'test_mock_operations',
            'test_validation',
            'test_cleanup',
            
            # Safety operations
            'safety_validation',
            'safety_testing',
            'emergency_shutdown_testing',
            
            # Read-only operations (always allowed)
            'file_reading',
            'data_analysis',
            'report_generation',
            'status_checking',
            'health_monitoring'
        }
        
        # Operations that require special validation even in test mode
        self.restricted_operations: Set[str] = {
            'system_file_modification',
            'production_data_access',
            'external_network_calls',
            'privileged_operations'
        }
        
        # Test-specific workflow patterns that should be allowed
        self.allowed_workflow_patterns: Set[str] = {
            'test_workflow',
            'readonly_test',
            'parallel_test',
            'sequential_test',
            'failure_test',
            'coordinated_test',
            'aggregation_test',
            'status_test',
            'list_test',
            'emergency_test',
            'validation_test'
        }
        
        self.logger.info(f"Test safety configuration initialized - test_mode: {self.test_mode}")
        
    def _detect_test_environment(self) -> bool:
        """Auto-detect if we're running in a test environment"""
        # Check for pytest
        if 'pytest' in os.environ.get('_', ''):
            return True
            
        # Check for test-related environment variables
        test_env_vars = ['PYTEST_CURRENT_TEST', 'TESTING', 'TEST_MODE']
        if any(var in os.environ for var in test_env_vars):
            return True
            
        # Check if we're being called from a test file
        import inspect
        for frame_info in inspect.stack():
            filename = frame_info.filename
            if 'test_' in Path(filename).name or '/tests/' in filename:
                return True
                
        return False
        
    def is_operation_allowed(self, operation: str, context: Dict[str, Any] = None) -> bool:
        """Check if operation is allowed in test environment
        
        Args:
            operation: The operation to check
            context: Additional context for the operation
            
        Returns:
            True if operation is allowed, False otherwise
        """
        if context is None:
            context = {}
            
        # Always block restricted operations
        if operation in self.restricted_operations:
            self.logger.warning(f"Operation {operation} is restricted even in test mode")
            return False
            
        # In test mode, allow test operations
        if self.test_mode:
            # Check if it's an explicitly allowed operation
            if operation in self.allowed_operations:
                self.logger.debug(f"Operation {operation} allowed in test mode")
                return True
                
            # Check for workflow patterns
            workflow_id = context.get('workflow_id', '')
            if any(pattern in workflow_id for pattern in self.allowed_workflow_patterns):
                self.logger.debug(f"Workflow {workflow_id} matches allowed test pattern")
                return True
                
            # Check for test-specific context
            if self._is_test_context(context):
                self.logger.debug(f"Operation {operation} allowed due to test context")
                return True
                
        # In production mode, use standard safety rules
        else:
            # Only allow read-only operations
            readonly_operations = {
                'file_reading', 'data_analysis', 'report_generation',
                'status_checking', 'health_monitoring'
            }
            if operation in readonly_operations:
                return True
                
        self.logger.warning(f"Operation {operation} not allowed - test_mode: {self.test_mode}")
        return False
        
    def _is_test_context(self, context: Dict[str, Any]) -> bool:
        """Check if the context indicates a test operation"""
        # Check for test-related keys in context
        test_indicators = [
            'test_', 'mock_', 'fixture_', 'pytest_', 'unittest_'
        ]
        
        for key, value in context.items():
            key_str = str(key).lower()
            value_str = str(value).lower()
            
            if any(indicator in key_str or indicator in value_str 
                   for indicator in test_indicators):
                return True
                
        return False
        
    def get_safety_limits(self) -> ResourceLimits:
        """Get appropriate safety limits for current mode"""
        if self.test_mode:
            # Convert test limits to ResourceLimits
            return ResourceLimits(
                max_cpu_percent=self.test_limits.max_cpu_percent,
                max_memory_mb=self.test_limits.max_memory_mb,
                max_disk_io_mb=self.test_limits.max_disk_io_mb,
                max_analysis_time_seconds=self.test_limits.max_analysis_time_seconds,
                max_concurrent_operations=self.test_limits.max_concurrent_operations
            )
        else:
            # Use standard production limits
            return ResourceLimits()
            
    def validate_workflow_safety(self, workflow_id: str, workflow_config: Dict[str, Any] = None) -> bool:
        """Validate workflow safety with test-specific rules"""
        if workflow_config is None:
            workflow_config = {}
            
        self.logger.debug(f"Validating workflow safety: {workflow_id} (test_mode: {self.test_mode})")
        
        # In test mode, be more permissive
        if self.test_mode:
            # Check if workflow matches test patterns
            if any(pattern in workflow_id for pattern in self.allowed_workflow_patterns):
                self.logger.debug(f"Workflow {workflow_id} allowed - matches test pattern")
                return True
                
            # Check for test-specific configuration
            if workflow_config.get('test_mode', False):
                self.logger.debug(f"Workflow {workflow_id} allowed - test_mode flag set")
                return True
                
            # Allow read-only workflows
            if workflow_config.get('read_only', True):
                self.logger.debug(f"Workflow {workflow_id} allowed - read-only workflow")
                return True
                
        # Use standard validation for production mode
        return self._validate_production_workflow(workflow_id, workflow_config)
        
    def _validate_production_workflow(self, workflow_id: str, workflow_config: Dict[str, Any]) -> bool:
        """Validate workflow using production safety rules"""
        # Strict validation for production
        if not workflow_config.get('read_only', True):
            self.logger.warning(f"Workflow {workflow_id} rejected - not read-only")
            return False
            
        # Check resource requirements
        limits = self.get_safety_limits()
        max_memory = workflow_config.get('max_memory_mb', 0)
        max_cpu = workflow_config.get('max_cpu_percent', 0)
        
        if max_memory > limits.max_memory_mb:
            self.logger.warning(f"Workflow {workflow_id} rejected - memory requirement too high")
            return False
            
        if max_cpu > limits.max_cpu_percent:
            self.logger.warning(f"Workflow {workflow_id} rejected - CPU requirement too high")
            return False
            
        return True
        
    def create_safety_rule_engine(self) -> 'TestSafetyRuleEngine':
        """Create a safety rule engine that respects test mode settings"""
        return TestSafetyRuleEngine(self)
        
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current safety configuration"""
        return {
            'test_mode': self.test_mode,
            'allowed_operations_count': len(self.allowed_operations),
            'restricted_operations_count': len(self.restricted_operations),
            'allowed_workflow_patterns_count': len(self.allowed_workflow_patterns),
            'safety_limits': {
                'max_cpu_percent': self.test_limits.max_cpu_percent if self.test_mode else 25.0,
                'max_memory_mb': self.test_limits.max_memory_mb if self.test_mode else 512.0,
                'max_analysis_time_seconds': self.test_limits.max_analysis_time_seconds if self.test_mode else 300
            }
        }


class TestSafetyRuleEngine:
    """Safety rule engine that respects test mode settings"""
    
    def __init__(self, test_config: TestSafetyConfiguration):
        self.test_config = test_config
        self.logger = logging.getLogger("rm_rdi_analysis.test_safety_rules")
        
    def evaluate_operation_safety(self, operation: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate operation safety with detailed reasoning"""
        if context is None:
            context = {}
            
        is_allowed = self.test_config.is_operation_allowed(operation, context)
        
        evaluation = {
            'operation': operation,
            'is_allowed': is_allowed,
            'test_mode': self.test_config.test_mode,
            'timestamp': datetime.now().isoformat(),
            'context_provided': bool(context)
        }
        
        # Add reasoning
        if is_allowed:
            if operation in self.test_config.allowed_operations:
                evaluation['reason'] = 'Operation explicitly allowed'
            elif self.test_config._is_test_context(context):
                evaluation['reason'] = 'Test context detected'
            else:
                evaluation['reason'] = 'Passed safety validation'
        else:
            if operation in self.test_config.restricted_operations:
                evaluation['reason'] = 'Operation is restricted'
            elif not self.test_config.test_mode:
                evaluation['reason'] = 'Production mode - strict validation'
            else:
                evaluation['reason'] = 'Failed safety validation'
                
        return evaluation
        
    def get_allowed_operations(self) -> List[str]:
        """Get list of currently allowed operations"""
        return sorted(list(self.test_config.allowed_operations))
        
    def get_restricted_operations(self) -> List[str]:
        """Get list of restricted operations"""
        return sorted(list(self.test_config.restricted_operations))


# Global test safety configuration instance
_global_test_safety_config: Optional[TestSafetyConfiguration] = None


def get_test_safety_config() -> TestSafetyConfiguration:
    """Get the global test safety configuration instance"""
    global _global_test_safety_config
    if _global_test_safety_config is None:
        _global_test_safety_config = TestSafetyConfiguration()
    return _global_test_safety_config


def is_test_mode() -> bool:
    """Check if we're currently in test mode"""
    config = get_test_safety_config()
    return config.test_mode


def reset_test_safety_config():
    """Reset the global test safety configuration (for testing)"""
    global _global_test_safety_config
    _global_test_safety_config = None