#!/usr/bin/env python3
"""
preview_generator - Simplified for size compliance
"""

from .preview_generator_methods import DevpostPreviewGenerator, RealtimePreviewManager
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from src.rm_ddd.core.health import ModuleHealth


logger = logging.getLogger(__name__)

# Export the main classes
__all__ = ['DevpostPreviewGenerator', 'RealtimePreviewManager']
