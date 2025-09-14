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
