"""
Automated Quality Gates Utils

This module was extracted from automated_quality_gates.py
as part of RM-DDD compliance refactoring.
"""

import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from src.rm_ddd.core.health import ModuleHealth


def _execute_formatting_gate(self, config: QualityGateConfig, target_path: Path, start_time: float) -> QualityGateResult:
    """Execute formatting quality gate using black"""
    try:
        cmd = ['python3', '-m', 'black', '--check', '--diff', str(target_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.timeout_seconds)
        if result.returncode == 0:
            score = 1.0
            status = QualityGateStatus.PASSED
            details = {'formatting_issues': 0, 'status': 'all_files_formatted'}
            recommendations = []
        else:
            score = 0.0
            status = QualityGateStatus.FAILED
            details = {'formatting_issues': result.stdout.count('would reformat'), 'diff_output': result.stdout[:1000]}
            recommendations = ['Fix formatting issues with: python3 -m black src/', 'Ensure consistent code formatting across all files', 'Consider adding pre-commit hooks for automatic formatting']
        return QualityGateResult(gate_type=QualityGateType.FORMATTING, status=status, score=score, details=details, execution_time_seconds=time.time() - start_time, recommendations=recommendations)
    except subprocess.TimeoutExpired:
        return QualityGateResult(gate_type=QualityGateType.FORMATTING, status=QualityGateStatus.FAILED, score=0.0, details={'error': 'Formatting check timeout'}, execution_time_seconds=time.time() - start_time, error_message='Formatting check timed out', recommendations=['Check for infinite loops or very large files'])

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

