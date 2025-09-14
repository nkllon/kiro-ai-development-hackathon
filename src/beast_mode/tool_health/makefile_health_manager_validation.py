"""
Makefile Health Manager Validation

This module was extracted from makefile_health_manager.py
as part of RM-DDD compliance refactoring.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..metrics.baseline_metrics_engine import BaselineMetricsEngine
from src.rm_ddd.core.health import ModuleHealth


class ValidatemakefilerepairClass:
    """Auto-generated class for functions."""

    def _validate_makefile_repair(self) -> bool:
    """
    Validate that Makefile repair was successful
    Required by R3.4: Validate fixes work before proceeding
    """
    try:
    result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
    self.logger.info('✓ Makefile repair validation PASSED')
    return True
    else:
    self.logger.error(f'✗ Makefile repair validation FAILED: {result.stderr}')
    return False
    except Exception as e:
    self.logger.error(f'✗ Makefile validation error: {e}')
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

