#!/usr/bin/env python3
"""
cli_main - Simplified for size compliance
"""

from .cli_main_methods import DevPostCLI
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from src.rm_ddd.core.health import ModuleHealth


logger = logging.getLogger(__name__)

# Export the main class
__all__ = ['DevPostCLI']
