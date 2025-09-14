from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Enum JSON Serialization Utilities

Provides custom JSON encoding for enum types to handle serialization issues
in health reporting and other system components.

Requirements: 6.1, 6.4 - Fix enum serialization and JSON compatibility
"""

import json
from enum import Enum
from typing import Any, Type, Dict, Union

