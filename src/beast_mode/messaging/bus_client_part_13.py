from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Bus Client Core Core Core

This module was extracted from bus_client_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Bus_Client - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for bus_client.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/beast_mode/messaging/bus_client_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.486219
"""



import asyncio
import json
import logging
import uuid
from datetime import datetime, time
from typing import Any, Callable, Dict, List, Optional, Set
import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError
from .models import BeastModeMessage, MessageType, AgentCapabilities
from .agent_registry import AgentRegistry, DiscoveredAgent
from .help_system import HelpWantedSystem, HelpUrgency
from .message_router import StandardMessageRouter
from .collaboration_scheduler import CollaborationScheduler, CollaborationType, OfficeHoursPattern
from src.rm_ddd.core.health import ModuleHealth

