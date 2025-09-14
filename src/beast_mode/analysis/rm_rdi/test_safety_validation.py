"""
Test Safety Validation

This module was extracted from test_safety.py
as part of RM-DDD compliance refactoring.
"""

import os
import logging
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from .safety import OperatorSafetyManager, ResourceLimits, SafetyStatus
import inspect

class GettestsafetyconfigClass:
    """Auto-generated class for functions."""

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

    def _detect_test_environment(self) -> bool:
    """Auto-detect if we're running in a test environment"""
    if 'pytest' in os.environ.get('_', ''):
    return True
    test_env_vars = ['PYTEST_CURRENT_TEST', 'TESTING', 'TEST_MODE']
    if any((var in os.environ for var in test_env_vars)):
    return True
    import inspect
    from src.rm_ddd.core.health import ModuleHealth

    for frame_info in inspect.stack():
    filename = frame_info.filename
    if 'test_' in Path(filename).name or '/tests/' in filename:
    return True
    return False

    def _is_test_context(self, context: Dict[str, Any]) -> bool:
    """Check if the context indicates a test operation"""
    test_indicators = ['test_', 'mock_', 'fixture_', 'pytest_', 'unittest_']
    for key, value in context.items():
    key_str = str(key).lower()
    value_str = str(value).lower()
    if any((indicator in key_str or indicator in value_str for indicator in test_indicators)):
    return True
    return False

    def validate_workflow_safety(self, workflow_id: str, workflow_config: Dict[str, Any]=None) -> bool:
    """Validate workflow safety with test-specific rules"""
    if workflow_config is None:
    workflow_config = {}
    self.logger.debug(f'Validating workflow safety: {workflow_id} (test_mode: {self.test_mode})')
    if self.test_mode:
    if any((pattern in workflow_id for pattern in self.allowed_workflow_patterns)):
    self.logger.debug(f'Workflow {workflow_id} allowed - matches test pattern')
    return True
    if workflow_config.get('test_mode', False):
    self.logger.debug(f'Workflow {workflow_id} allowed - test_mode flag set')
    return True
    if workflow_config.get('read_only', True):
    self.logger.debug(f'Workflow {workflow_id} allowed - read-only workflow')
    return True
    return self._validate_production_workflow(workflow_id, workflow_config)

    def _validate_production_workflow(self, workflow_id: str, workflow_config: Dict[str, Any]) -> bool:
    """Validate workflow using production safety rules"""
    if not workflow_config.get('read_only', True):
    self.logger.warning(f'Workflow {workflow_id} rejected - not read-only')
    return False
    limits = self.get_safety_limits()
    max_memory = workflow_config.get('max_memory_mb', 0)
    max_cpu = workflow_config.get('max_cpu_percent', 0)
    if max_memory > limits.max_memory_mb:
    self.logger.warning(f'Workflow {workflow_id} rejected - memory requirement too high')
    return False
    if max_cpu > limits.max_cpu_percent:
    self.logger.warning(f'Workflow {workflow_id} rejected - CPU requirement too high')
    return False
    return True

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

