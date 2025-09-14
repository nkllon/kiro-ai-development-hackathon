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

def _discover_test_files(self) -> List[str]:
    """Discover all test files for analysis"""
    test_files = []
    test_dir = Path('tests')
    if test_dir.exists():
        for test_file in test_dir.rglob('test_*.py'):
            test_files.append(str(test_file))
    return test_files
