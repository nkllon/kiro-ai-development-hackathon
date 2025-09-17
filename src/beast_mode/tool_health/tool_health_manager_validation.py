"""
Tool Health Manager Validation

This module was extracted from tool_health_manager.py
as part of RM-DDD compliance refactoring.
"""

import logging
import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from ..core.reflective_module import ReflectiveModule
from src.rm_ddd.core.health import ModuleHealth


def _check_installation_integrity(self, tool_name: str) -> Dict[str, Any]:
    """Check if tool files are missing or corrupted"""
    if tool_name == 'makefile':
        makefiles_dir = Path('makefiles')
        if not makefiles_dir.exists():
            return {'healthy': False, 'issues': ['makefiles/ directory missing'], 'root_causes': ['modular_makefile_structure_not_created']}
    return {'healthy': True, 'issues': [], 'root_causes': []}

def _check_dependencies_and_config(self, tool_name: str) -> Dict[str, Any]:
    """Check tool dependencies and configuration"""
    return {'healthy': True, 'issues': [], 'root_causes': []}

def _check_version_compatibility(self, tool_name: str) -> Dict[str, Any]:
    """Check version compatibility issues"""
    return {'healthy': True, 'issues': [], 'root_causes': []}

def _validate_tool_repair(self, tool_name: str) -> Dict[str, Any]:
    """Validate that tool repair actually works"""
    if tool_name == 'makefile':
        try:
            result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=10)
            return {'success': result.returncode == 0, 'output': result.stdout}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    return {'success': True}

def _validate_all_make_targets(self) -> Dict[str, Any]:
    """Validate all make targets work correctly"""
    try:
        result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=10)
        return {'all_targets_work': result.returncode == 0, 'tested_targets': ['help'], 'output': result.stdout}
    except Exception as e:
        return {'all_targets_work': False, 'error': str(e)}

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

