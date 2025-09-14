"""
Compatibility Validation

This module was extracted from compatibility.py
as part of RM-DDD compliance refactoring.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError
from .models import BeastModeMessage, MessageType, AgentCapabilities
import uuid
import uuid
from src.rm_ddd.core.health import ModuleHealth


class ValidatemessagecompatibilityClass:
    """Auto-generated class for functions."""

    def validate_message_compatibility(self, message: BeastModeMessage, target_agents: List[str]=None) -> List[str]:
    """
    Validate message compatibility with target agents.

    Args:
    message: Message to validate
    target_agents: List of target agent IDs (optional)

    Returns:
    List[str]: List of compatibility warnings
    """
    warnings = []
    newer_types = {MessageType.SPORE_SPAWN, MessageType.OFFICE_HOURS_ANNOUNCEMENT, MessageType.COLLABORATION_REQUEST, MessageType.COLLABORATION_RESPONSE, MessageType.COLLABORATION_START, MessageType.COLLABORATION_END, MessageType.COLLABORATION_UPDATE}
    if message.type in newer_types:
    warnings.append(f'Message type {message.type.value} may not be supported by older agents')
    if message.payload:
    payload_size = len(json.dumps(message.payload))
    if payload_size > 10000:
    warnings.append('Large payload may cause issues with older agents')
    if self._has_complex_payload(message.payload):
    warnings.append('Complex payload structure may not be compatible with all agents')
    return warnings

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

