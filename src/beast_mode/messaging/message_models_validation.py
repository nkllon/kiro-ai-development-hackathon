"""
Message Models Validation

This module was extracted from message_models.py
as part of RM-DDD compliance refactoring.
"""

import json
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from uuid import uuid4
from pydantic import BaseModel, Field, validator
from src.rm_ddd.core.health import ModuleHealth


def validate_message_chain(messages: List[BeastModeMessage]) -> bool:
    """Validate a chain of related messages."""
    if not messages:
        return True
    correlation_id = messages[0].correlation_id or messages[0].message_id
    for msg in messages[1:]:
        if msg.correlation_id != correlation_id:
            return False
    for i, msg in enumerate(messages[1:], 1):
        if msg.reply_to and msg.reply_to not in [m.message_id for m in messages[:i]]:
            return False
    return True

@validator('capabilities')
def validate_capabilities(cls, v):
    """Validate capabilities list."""
    if not v:
        raise ValueError('Agent must have at least one capability')
    return v

@validator('agent_id')
def validate_agent_id(cls, v):
    """Validate agent ID format."""
    if not v or len(v) < 3:
        raise ValueError('Agent ID must be at least 3 characters')
    return v

@validator('priority')
def validate_priority(cls, v):
    """Validate priority level."""
    valid_priorities = ['low', 'normal', 'high', 'urgent']
    if v not in valid_priorities:
        raise ValueError(f'Priority must be one of: {valid_priorities}')
    return v

@validator('content')
def validate_content(cls, v):
    """Validate message content is serializable."""
    try:
        json.dumps(v)
        return v
    except (TypeError, ValueError) as e:
        raise ValueError(f'Message content must be JSON serializable: {str(e)}')

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

