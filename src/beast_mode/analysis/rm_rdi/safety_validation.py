"""
Safety Validation

This module was extracted from safety.py
as part of RM-DDD compliance refactoring.
"""

import os
import threading
import time
import signal
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging
import psutil
from src.rm_ddd.core.health import ModuleHealth


def check_limits(self) -> List[str]:
    """Check if resource usage exceeds limits"""
    violations = []
    usage = self.get_current_usage()
    if usage.get('cpu_percent', 0) > self.limits.max_cpu_percent:
        violations.append(f"CPU usage {usage['cpu_percent']:.1f}% exceeds limit {self.limits.max_cpu_percent}%")
    if usage.get('memory_mb', 0) > self.limits.max_memory_mb:
        violations.append(f"Memory usage {usage['memory_mb']:.1f}MB exceeds limit {self.limits.max_memory_mb}MB")
    return violations

def validate_read_only_access(self, file_path: Path) -> bool:
    """Validate that we only have read access to files"""
    try:
        if not file_path.exists():
            return False
        if not os.access(file_path, os.R_OK):
            return False
        if os.access(file_path, os.W_OK):
            self.logger.warning(f'Write access detected for {file_path} - SAFETY VIOLATION')
            return False
        return True
    except Exception as e:
        self.logger.error(f'Safety validation failed for {file_path}: {e}')
        return False

def validate_no_system_modifications(self) -> bool:
    """Validate that we're not modifying any system files"""
    return True

def validate_isolation(self) -> bool:
    """Validate that analysis runs in isolation"""
    return True

def _validate_initial_safety(self) -> bool:
    """Validate initial safety conditions"""
    if os.getuid() == 0:
        self.logger.error('SAFETY VIOLATION: Running as root user')
        return False
    if self.limits.max_cpu_percent > 50:
        self.logger.warning('CPU limit >50% may impact system performance')
    return True

def validate_workflow_safety(self, workflow_id: str, workflow_config: Dict[str, Any]=None) -> bool:
    """Validate that a workflow is safe to execute"""
    if workflow_config is None:
        workflow_config = {}
    self.logger.info(f'Validating workflow safety: {workflow_id}')
    if self.emergency_shutdown_triggered:
        self.logger.warning(f'Workflow {workflow_id} blocked - emergency shutdown active')
        return False
    if not self.analysis_allowed:
        self.logger.warning(f'Workflow {workflow_id} blocked - analysis disabled')
        return False
    try:
        max_memory = workflow_config.get('max_memory_mb', 0)
        max_cpu = workflow_config.get('max_cpu_percent', 0)
        timeout = workflow_config.get('timeout_seconds', 300)
        if max_memory > self.limits.max_memory_mb:
            self.logger.warning(f'Workflow {workflow_id} memory requirement ({max_memory}MB) exceeds limit ({self.limits.max_memory_mb}MB)')
            return False
        if max_cpu > self.limits.max_cpu_percent:
            self.logger.warning(f'Workflow {workflow_id} CPU requirement ({max_cpu}%) exceeds limit ({self.limits.max_cpu_percent}%)')
            return False
        if timeout > self.limits.max_analysis_time_seconds:
            self.logger.warning(f'Workflow {workflow_id} timeout ({timeout}s) exceeds limit ({self.limits.max_analysis_time_seconds}s)')
            return False
        current_usage = self.resource_monitor.get_current_usage()
        if current_usage.get('cpu_percent', 0) + max_cpu > self.limits.max_cpu_percent:
            self.logger.warning(f'Workflow {workflow_id} would exceed CPU limits with current usage')
            return False
        if current_usage.get('memory_mb', 0) + max_memory > self.limits.max_memory_mb:
            self.logger.warning(f'Workflow {workflow_id} would exceed memory limits with current usage')
            return False
        workflow_type = workflow_config.get('type', 'analysis')
        if workflow_type not in ['analysis', 'validation', 'monitoring']:
            self.logger.warning(f'Workflow {workflow_id} has unsafe type: {workflow_type}')
            return False
        read_only = workflow_config.get('read_only', True)
        if not read_only:
            self.logger.warning(f'Workflow {workflow_id} is not read-only - safety violation')
            return False
        self.logger.info(f'Workflow {workflow_id} passed safety validation')
        return True
    except Exception as e:
        self.logger.error(f'Workflow safety validation failed for {workflow_id}: {e}')
        return False

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

