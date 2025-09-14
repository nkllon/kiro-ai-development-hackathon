#!/usr/bin/env python3
"""
file_watcher_core - Simplified for size compliance
"""

from .file_watcher_core_methods import FileWatcherCore
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Export the main class
__all__ = ['FileWatcherCore']
