import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from .models import BeastModeMessage, MessageType, AgentCapabilities
from .message_handlers import MessageRouter, BaseMessageHandler, SimpleMessageHandler, PromptRequestHandler, PromptResponseHandler, AgentDiscoveryHandler, AgentResponseHandler, HelpWantedHandler, HelpResponseHandler, SporeDeliveryHandler, SporeRequestHandler, SporeSpawnHandler, TechnicalExchangeHandler, SystemHealthHandler, MessageValidationError, MessageCompatibilityError
from .message_router_core_core import *
from .message_router_core_validation import *
from src.rm_ddd.core.health import ModuleHealth


class RegistermoduleClass:
    """Auto-generated class for functions."""

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

