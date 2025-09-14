"""
Performance Monitor Core Validation

This module was extracted from performance_monitor_core.py
as part of RM-DDD compliance refactoring.
"""

import time
import threading
import signal
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
import psutil
from src.rm_ddd.core.health import ModuleHealth


def _check_resource_limits(self) -> None:
    """Check if resource limits are being exceeded"""
    try:
        current_memory = self._get_memory_usage()
        current_cpu = self._get_cpu_usage()
        if current_memory > self.resource_limits.max_memory_mb:
            self.logger.warning(f'Memory limit exceeded: {current_memory}MB > {self.resource_limits.max_memory_mb}MB')
            self.resource_limit_violations += 1
            for operation_id in list(self.active_operations.keys()):
                self.optimize_resource_usage(operation_id)
        if current_cpu > self.resource_limits.max_cpu_percent:
            self.logger.warning(f'CPU limit exceeded: {current_cpu}% > {self.resource_limits.max_cpu_percent}%')
            self.resource_limit_violations += 1
    except Exception as e:
        self.logger.error(f'Resource limit check failed: {e}')
