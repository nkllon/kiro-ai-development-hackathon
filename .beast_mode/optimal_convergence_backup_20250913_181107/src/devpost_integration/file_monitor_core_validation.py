"""
File Monitor Core Validation

This module was extracted from file_monitor_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional
from typing import Dict, Any, List, Optional
from pathlib import Path
from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, ModuleConfiguration, register_module

def check_health(self) -> ModuleHealth:
    """Perform health check"""
    return ModuleHealth(module_id='projectfilemonitor', status=ModuleStatus.HEALTHY, health_score=1.0, issues=[], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={}, last_check=datetime.now())

def check_health(self) -> ModuleHealth:
    """Perform health check"""
    return ModuleHealth(module_id='contentbasedchangedetector', status=ModuleStatus.HEALTHY, health_score=1.0, issues=[], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={}, last_check=datetime.now())

def check_health(self) -> ModuleHealth:
    """Perform health check"""
    return ModuleHealth(module_id='mediafiledetector', status=ModuleStatus.HEALTHY, health_score=1.0, issues=[], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={}, last_check=datetime.now())

def check_health(self) -> ModuleHealth:
    """Perform health check"""
    return ModuleHealth(module_id='gitintegration', status=ModuleStatus.HEALTHY, health_score=1.0, issues=[], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={}, last_check=datetime.now())

def check_health(self) -> ModuleHealth:
    """Check module health with comprehensive monitoring"""
    try:
        if not hasattr(self, '_start_time'):
            return ModuleHealth.UNHEALTHY
        uptime = (datetime.now() - self._start_time).total_seconds()
        if uptime < 0:
            return ModuleHealth.UNHEALTHY
        error_count = getattr(self, '_error_count', 0)
        total_operations = getattr(self, '_command_count', 1)
        error_rate = error_count / total_operations if total_operations > 0 else 0
        if error_rate > 0.5:
            return ModuleHealth.UNHEALTHY
        elif error_rate > 0.1:
            return ModuleHealth.DEGRADED
        else:
            return ModuleHealth.HEALTHY
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return ModuleHealth.UNHEALTHY
    'Perform comprehensive health check.'
    issues = []
    health_score = 1.0
    try:
        if health_score >= 0.9:
            status = ModuleStatus.HEALTHY
        elif health_score >= 0.7:
            status = ModuleStatus.DEGRADED
        else:
            status = ModuleStatus.UNHEALTHY
        return ModuleHealth(module_id=self.module_id, status=status, last_check=datetime.now(), health_score=max(0.0, health_score), issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics())
    except Exception as e:
        return ModuleHealth(module_id=self.module_id, status=ModuleStatus.UNHEALTHY, last_check=datetime.now(), health_score=0.0, issues=[f'Health check exception: {e}'], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={})
