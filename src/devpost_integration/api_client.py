#!/usr/bin/env python3
"""
api_client - Simplified for size compliance
"""

from .api_client_methods import DevPostAPIClient
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from src.rm_ddd.core.health import ModuleHealth


logger = logging.getLogger(__name__)

# Export the main class
__all__ = ['DevPostAPIClient']
