"""
Makefile Integrator Core Core Processing

This module was extracted from makefile_integrator_core_core.py
as part of RM-DDD compliance refactoring.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from .base import DomainSystemComponent
from .interfaces import MakefileIntegratorInterface
from .models import Domain, MakeTarget, ExecutionResult, ValidationResult
from .exceptions import MakefileIntegrationError, MakefileNotFoundError, MakeTargetExecutionError
from .config import get_config
from src.rm_ddd.core.health import ModuleHealth


def _parse_makefile(self, makefile_path: Path) -> List[MakeTarget]:
    """Parse a makefile and extract targets"""
    targets = []
    try:
        with open(makefile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        current_target = None
        current_commands = []
        current_description = ''
        for line in lines:
            line = line.rstrip()
            if not line:
                continue
            if line.startswith('#') and current_target is None:
                current_description = line[1:].strip()
                continue
            if ':' in line and (not line.startswith('\t')) and (not line.startswith(' ')):
                if current_target:
                    target = MakeTarget(name=current_target, description=current_description, dependencies=self._parse_dependencies(current_target), commands=current_commands.copy(), domain_specific=self._is_domain_specific_target(current_target))
                    targets.append(target)
                target_line = line.split(':')[0].strip()
                current_target = target_line
                current_commands = []
            elif line.startswith('\t') or (line.startswith(' ') and current_target):
                command = line.strip()
                if command and (not command.startswith('#')):
                    current_commands.append(command)
            elif current_target and (not line.startswith('\t')) and (not line.startswith(' ')):
                current_description = ''
        if current_target:
            target = MakeTarget(name=current_target, description=current_description, dependencies=self._parse_dependencies(current_target), commands=current_commands.copy(), domain_specific=self._is_domain_specific_target(current_target))
            targets.append(target)
    except Exception as e:
        self.logger.error(f'Error parsing makefile {makefile_path}: {e}')
    return targets

def _parse_dependencies(self, target_line: str) -> List[str]:
    """Parse target dependencies from target line"""
    if ':' in target_line:
        parts = target_line.split(':', 1)
        if len(parts) > 1 and parts[1].strip():
            return [dep.strip() for dep in parts[1].split()]
    return []
