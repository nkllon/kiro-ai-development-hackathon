"""
Message Handlers Processing

This module was extracted from message_handlers.py
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


class ConvertlegacymessageClass:
    """Auto-generated class for functions."""

    def _convert_legacy_message(self, message_data: Dict[str, Any]) -> BeastModeMessage:
    """
    Convert legacy message formats to current format.

    Args:
    message_data: Raw message data

    Returns:
    BeastModeMessage: Converted message

    Raises:
    MessageCompatibilityError: If conversion fails
    """
    try:
    if 'type' not in message_data:
    message_data['type'] = MessageType.SIMPLE_MESSAGE.value
    if 'source' not in message_data:
    message_data['source'] = 'unknown_agent'
    msg_type = message_data['type']
    if isinstance(msg_type, str):
    type_mapping = {'message': MessageType.SIMPLE_MESSAGE.value, 'request': MessageType.PROMPT_REQUEST.value, 'response': MessageType.PROMPT_RESPONSE.value, 'discovery': MessageType.AGENT_DISCOVERY.value, 'help': MessageType.HELP_WANTED.value, 'spore': MessageType.SPORE_DELIVERY.value}
    if msg_type in type_mapping:
    message_data['type'] = type_mapping[msg_type]
    if 'payload' not in message_data:
    message_data['payload'] = {}
    if 'timestamp' in message_data and isinstance(message_data['timestamp'], str):
    try:
    message_data['timestamp'] = datetime.fromisoformat(message_data['timestamp'].replace('Z', '+00:00'))
    except ValueError:
    message_data['timestamp'] = datetime.now()
    return BeastModeMessage(**message_data)
    except Exception as e:
    raise MessageCompatibilityError(f'Failed to convert legacy message: {e}')

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

