"""
Rdi Chain Orchestrator Validation

This module was extracted from rdi_chain_orchestrator.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import subprocess
import json
from ..autonomous.pdca_langgraph_orchestrator import PDCALangGraphOrchestrator
from ..core.reflective_module import ReflectiveModule, HealthStatus
from src.rm_ddd.core.health import ModuleHealth


def _discover_test_files(self) -> List[str]:
    """Discover all test files for analysis"""
    test_files = []
    test_dir = Path('tests')
    if test_dir.exists():
        for test_file in test_dir.rglob('test_*.py'):
            test_files.append(str(test_file))
    return test_files

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

