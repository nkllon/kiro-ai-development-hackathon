"""
Sync Models Core Core Validation

This module was extracted from sync_models_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import SyncOperationType, ChangeType
from typing import Dict, List, Any, Optional

def check_health(self) -> ModuleHealth:
    """Check module health."""
    issues = []
    health_score = self._calculate_health_score()
    if self._errors > 0:
        issues.append(f'{self._errors} internal errors occurred')
    if not self.success and (not self.error_message):
        issues.append('Failed sync without error message')
    if self.records_failed > self.records_processed:
        issues.append('More failures than processed records')
    status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
    return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

def check_health(self) -> ModuleHealth:
    """Check module health."""
    issues = []
    health_score = self._calculate_health_score()
    if self._errors > 0:
        issues.append(f'{self._errors} internal errors occurred')
    if not self.file_path:
        issues.append('No file path specified')
    if self.file_size < 0:
        issues.append('Invalid file size')
    status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
    return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())
