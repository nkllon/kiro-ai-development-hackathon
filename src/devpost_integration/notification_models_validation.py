"""
Notification Models Validation

This module was extracted from notification_models.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import NotificationTiming
from typing import Dict, List, Any, Optional

class CheckhealthClass:
    """Auto-generated class for functions."""

    def check_health(self) -> ModuleHealth:
    """Check module health."""
    issues = []
    health_score = self._calculate_health_score()
    if self._errors > 0:
    issues.append(f'{self._errors} internal errors occurred')
    if not self.channels:
    issues.append('No notification channels configured')
    if self.enabled and (not self.channels):
    issues.append('Notifications enabled but no channels available')
    status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
    return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

    def check_health(self) -> ModuleHealth:
    """Check module health."""
    issues = []
    health_score = self._calculate_health_score()
    if self._errors > 0:
    issues.append(f'{self._errors} internal errors occurred')
    if not self.message_id:
    issues.append('No message ID specified')
    if not self.title:
    issues.append('No message title specified')
    if not self.content:
    issues.append('No message content specified')
    if not self.recipients:
    issues.append('No recipients specified')
    status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
    return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())
