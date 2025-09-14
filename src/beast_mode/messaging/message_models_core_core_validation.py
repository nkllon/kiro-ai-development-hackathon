"""
Message Models Core Core Validation

This module was extracted from message_models_core_core.py
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
