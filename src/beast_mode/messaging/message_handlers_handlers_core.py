"""
Message Handlers Handlers Core

This module was extracted from message_handlers_handlers.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
from .models import BeastModeMessage, MessageType, AgentCapabilities
from src.rm_ddd.core.health import ModuleHealth


def __init__(self, agent_id: str):
    self.agent_id = agent_id
    self.handled_count = 0
    self.error_count = 0
    self.last_handled = None

@abstractmethod
def get_supported_types(self) -> List[MessageType]:
    """Return list of supported message types"""
    pass

def can_handle(self, message: BeastModeMessage) -> bool:
    """Check if this handler can process the message"""
    return message.type in self.get_supported_types()

def get_stats(self) -> Dict[str, Any]:
    """Get handler statistics"""
    return {'handler_type': self.__class__.__name__, 'supported_types': [t.value for t in self.get_supported_types()], 'handled_count': self.handled_count, 'error_count': self.error_count, 'last_handled': self.last_handled.isoformat() if self.last_handled else None}

def __init__(self, agent_id: str, message_callback: Optional[Callable[[str, str], None]]=None):
    super().__init__(agent_id)
    self.message_callback = message_callback

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.SIMPLE_MESSAGE]

def __init__(self, agent_id: str, prompt_processor: Optional[Callable[[str], str]]=None):
    super().__init__(agent_id)
    self.prompt_processor = prompt_processor

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.PROMPT_REQUEST]

def __init__(self, agent_id: str, response_callback: Optional[Callable[[str, str, str], None]]=None):
    super().__init__(agent_id)
    self.response_callback = response_callback
    self.pending_requests: Dict[str, BeastModeMessage] = {}

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.PROMPT_RESPONSE]

def track_request(self, request: BeastModeMessage) -> None:
    """Track a sent prompt request for correlation"""
    if request.type == MessageType.PROMPT_REQUEST:
        self.pending_requests[request.id] = request

def __init__(self, agent_id: str, capabilities: List[str], discovery_callback: Optional[Callable[[str, AgentCapabilities], None]]=None):
    super().__init__(agent_id)
    self.capabilities = capabilities
    self.discovery_callback = discovery_callback

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.AGENT_DISCOVERY]

def __init__(self, agent_id: str, response_callback: Optional[Callable[[str, AgentCapabilities], None]]=None):
    super().__init__(agent_id)
    self.response_callback = response_callback

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.AGENT_RESPONSE]

def __init__(self, agent_id: str, capabilities: List[str], help_callback: Optional[Callable[[str, List[str], str], bool]]=None):
    super().__init__(agent_id)
    self.capabilities = capabilities
    self.help_callback = help_callback

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.HELP_WANTED]

def __init__(self, agent_id: str, response_callback: Optional[Callable[[str, Dict[str, Any]], None]]=None):
    super().__init__(agent_id)
    self.response_callback = response_callback
    self.pending_requests: Dict[str, BeastModeMessage] = {}

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.HELP_RESPONSE]

def track_help_request(self, request: BeastModeMessage) -> None:
    """Track a sent help request for correlation"""
    if request.type == MessageType.HELP_WANTED:
        request_id = request.payload.get('request_id', request.id)
        self.pending_requests[request_id] = request

def __init__(self, agent_id: str, spore_callback: Optional[Callable[[str, str, Dict[str, Any]], None]]=None):
    super().__init__(agent_id)
    self.spore_callback = spore_callback

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.SPORE_DELIVERY]

def __init__(self, agent_id: str, spore_provider: Optional[Callable[[str], Optional[Dict[str, Any]]]]=None):
    super().__init__(agent_id)
    self.spore_provider = spore_provider

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.SPORE_REQUEST]

def __init__(self, agent_id: str, tech_callback: Optional[Callable[[str, Dict[str, Any]], None]]=None):
    super().__init__(agent_id)
    self.tech_callback = tech_callback

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.TECHNICAL_EXCHANGE]

def __init__(self, agent_id: str, spawn_callback: Optional[Callable[[str, str, Dict[str, Any]], None]]=None):
    super().__init__(agent_id)
    self.spawn_callback = spawn_callback

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.SPORE_SPAWN]

def __init__(self, agent_id: str, health_callback: Optional[Callable[[str, Dict[str, Any]], None]]=None):
    super().__init__(agent_id)
    self.health_callback = health_callback

def get_supported_types(self) -> List[MessageType]:
    return [MessageType.SYSTEM_HEALTH]

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

