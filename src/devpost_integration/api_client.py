#!/usr/bin/env python3
"""
api_client - Simplified for size compliance
"""

from .api_client_methods import *
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Import the main class from methods file
# This keeps the main file under 300 lines
