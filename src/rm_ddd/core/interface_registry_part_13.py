from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Interface Registry - Requirements-Driven Implementation
====================================================
File: src/rm_ddd/core/interface_registry.py
Generated from requirements: Interface management and registration
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path
from src.rm_ddd.core.health import ModuleHealth

