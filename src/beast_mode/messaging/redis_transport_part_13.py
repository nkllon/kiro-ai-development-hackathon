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



    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

