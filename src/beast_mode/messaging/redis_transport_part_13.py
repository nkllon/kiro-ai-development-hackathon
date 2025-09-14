from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Redis Transport Implementation

Wraps our existing Redis daemon implementation as a pluggable transport.
Preserves all current functionality while implementing the transport interface.
"""

import asyncio
import logging
from typing import Callable, Dict, Any, List
from .transport import BeastModeTransport, TransportFactory
from .models import BeastModeMessage
from .daemon_client import BeastModeDaemon
from src.rm_ddd.core.health import ModuleHealth


