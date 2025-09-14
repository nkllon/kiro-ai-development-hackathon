"""
Config Models Core Core Validation

This module was extracted from config_models_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional

class CheckhealthClass:
    """Auto-generated class for functions."""

    def check_health(self) -> ModuleHealth:
    """Check module health."""
    issues = []
    health_score = self._calculate_health_score()
    if self._errors > 0:
    issues.append(f'{self._errors} errors occurred')
    if not self.config_data:
    issues.append('No configuration data available')
    status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
    return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

    def validate_configuration(self) -> bool:
    """Validate configuration values."""
    try:
    required_keys = ['api_base_url', 'api_version', 'timeout_seconds']
    for key in required_keys:
    if key not in self.config_data:
    return False
    timeout = self.config_data.get('timeout_seconds', 0)
    if not isinstance(timeout, (int, float)) or timeout <= 0:
    return False
    return True
    except Exception as e:
    logger.error(f'Configuration validation failed: {e}')
    self._errors += 1
    return False

    def check_health(self) -> ModuleHealth:
    """Check module health."""
    issues = []
    health_score = self._calculate_health_score()
    if self._errors > 0:
    issues.append(f'{self._errors} errors occurred')
    if not self.settings_data:
    issues.append('No settings data available')
    status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
    return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

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

