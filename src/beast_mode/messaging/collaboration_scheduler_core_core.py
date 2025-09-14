import asyncio
import json
import logging
from datetime import datetime, timedelta, time
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import uuid
from .models import BeastModeMessage, MessageType, AgentCapabilities
from .collaboration_scheduler_core_core_processing import *
from .collaboration_scheduler_core_core_core import *
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

