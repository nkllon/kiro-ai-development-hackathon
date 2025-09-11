#!/usr/bin/env python3
"""
project_manager - Simplified for size compliance
"""

from .project_manager_methods import ProjectStatus, DevpostProjectManager
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Export the main classes
__all__ = ['ProjectStatus', 'DevpostProjectManager']
