from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Enhanced Compliance Monitoring System - Lessons Learned Implementation
==================================================================
Implements validated methodologies from 98.5% compliance achievement
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from src.rm_ddd.core.health import ModuleHealth

