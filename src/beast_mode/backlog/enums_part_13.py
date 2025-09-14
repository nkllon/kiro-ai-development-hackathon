from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""Enums for OpenFlow Backlog Management System

This module defines all enums used throughout the backlog management system
for type safety and consistency.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from src.rm_ddd.core.health import ModuleHealth


