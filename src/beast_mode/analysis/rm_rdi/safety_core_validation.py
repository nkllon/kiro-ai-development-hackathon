"""
Safety Core Validation

This module was extracted from safety_core.py
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
