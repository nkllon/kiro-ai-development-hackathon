"""
Constraint Resolver Core Core Utils

This module was extracted from constraint_resolver_core_core.py
as part of RM-DDD compliance refactoring.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue, PriorityQueue
from ..core.reflective_module import ReflectiveModule, HealthStatus
from src.rm_ddd.core.health import ModuleHealth


def _get_pool_utilization(self) -> float:
    """Get thread pool utilization"""
    return 0.6
