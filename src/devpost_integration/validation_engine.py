#!/usr/bin/env python3
"""
validation_engine - Simplified for size compliance
"""

from .validation_engine_methods import ValidationEngine
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Export the main class
__all__ = ['ValidationEngine']
