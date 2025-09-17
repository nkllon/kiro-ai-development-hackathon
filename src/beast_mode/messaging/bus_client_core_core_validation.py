"""
Bus Client Core Core Validation

This module was extracted from bus_client_core_core.py
as part of RM-DDD compliance refactoring.
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


def validate_message_format(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
        Validate message format using the router.
        
        Args:
            message_data: Raw message data
            
        Returns:
            Validation result
        """
    if self.message_router:
        return self.message_router.validate_message_compatibility(message_data)
    try:
        BeastModeMessage(**message_data)
        return {'is_valid': True, 'is_legacy': False, 'errors': []}
    except Exception as e:
        return {'is_valid': False, 'is_legacy': False, 'errors': [str(e)]}

def create_test_message(self, msg_type: MessageType, **kwargs) -> BeastModeMessage:
    """
        Create a test message for a specific type.
        
        Args:
            msg_type: Message type to create
            **kwargs: Additional message parameters
            
        Returns:
            Test message
        """
    if self.message_router:
        return self.message_router.create_test_message(msg_type, **kwargs)
    return BeastModeMessage(type=msg_type, source=kwargs.get('source', self.agent_id), target=kwargs.get('target'), payload=kwargs.get('payload', {}), priority=kwargs.get('priority', 5))

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

