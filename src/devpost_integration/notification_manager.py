#!/usr/bin/env python3
"""
notification_manager - Simplified for size compliance
"""

from .notification_manager_methods import NotificationConfig, NotificationManager
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Export the main class
__all__ = ['NotificationConfig']
