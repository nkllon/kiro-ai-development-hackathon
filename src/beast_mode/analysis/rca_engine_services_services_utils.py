"""
Rca Engine Services Services Utils

This module was extracted from rca_engine_services_services.py
as part of RM-DDD compliance refactoring.
"""

import os
import subprocess
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
import shutil
import shutil
import shutil
from src.rm_ddd.core.health import ModuleHealth


def _analyze_tool_health(self, failure: Failure) -> Dict[str, Any]:
    """Analyze tool health status"""
    tool_health = {}
    if failure.component in ['makefile', 'make']:
        try:
            result = subprocess.run(['which', 'make'], capture_output=True, text=True)
            tool_health['make_available'] = result.returncode == 0
            tool_health['makefile_exists'] = Path('Makefile').exists()
            tool_health['makefiles_dir_exists'] = Path('makefiles').exists()
        except Exception as e:
            tool_health['analysis_error'] = str(e)
    return tool_health
