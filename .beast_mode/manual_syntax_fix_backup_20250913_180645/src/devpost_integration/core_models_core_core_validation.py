"""
Core Models Core Core Validation

This module was extracted from core_models_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional
from enum import Enum

def check_health(self) -> ModuleHealth:
    """Check module health with comprehensive monitoring."""
    issues = []
    health_score = self._calculate_health_score()
    if self._errors > 0:
        issues.append(f'{self._errors} errors occurred')
    if self.status == 'failed' and (not self.error_message):
        issues.append('Failed operation without error message')
    if self.progress < 0 or self.progress > 1:
        issues.append('Invalid progress value')
    if health_score >= 0.9:
        status = ModuleStatus.HEALTHY
    elif health_score >= 0.7:
        status = ModuleStatus.WARNING
    else:
        status = ModuleStatus.ERROR
    return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

def check_health(self) -> ModuleHealth:
    """Check module health."""
    issues = []
    health_score = 1.0
    if self._errors > 0:
        issues.append(f'{self._errors} errors occurred')
        health_score -= 0.2
    if not self.connected:
        issues.append('Not connected to project')
        health_score -= 0.3
    status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
    return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())
