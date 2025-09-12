"""
Message Handlers Handlers Handlers Validation

This module was extracted from message_handlers_handlers_handlers.py
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

def validate_message(self, message: BeastModeMessage) -> None:
    """
        Validate message structure and content.
        
        Raises:
            MessageValidationError: If message is invalid
        """
    if not message.type:
        raise MessageValidationError('Message type is required')
    if not message.source:
        raise MessageValidationError('Message source is required')
    if message.priority < 1 or message.priority > 10:
        raise MessageValidationError('Message priority must be between 1 and 10')

def validate_message(self, message: BeastModeMessage) -> None:
    """Validate prompt request message"""
    super().validate_message(message)
    if 'prompt' not in message.payload:
        raise MessageValidationError("Prompt request must contain 'prompt' in payload")

def validate_message(self, message: BeastModeMessage) -> None:
    """Validate agent discovery message"""
    super().validate_message(message)
    if 'agent_capabilities' not in message.payload:
        raise MessageValidationError("Agent discovery must contain 'agent_capabilities' in payload")

def validate_message(self, message: BeastModeMessage) -> None:
    """Validate help wanted message"""
    super().validate_message(message)
    if 'required_capabilities' not in message.payload:
        raise MessageValidationError("Help wanted must contain 'required_capabilities' in payload")
    if 'description' not in message.payload:
        raise MessageValidationError("Help wanted must contain 'description' in payload")

def validate_message(self, message: BeastModeMessage) -> None:
    """Validate spore delivery message"""
    super().validate_message(message)
    if 'spore_name' not in message.payload:
        raise MessageValidationError("Spore delivery must contain 'spore_name' in payload")
    if 'spore_content' not in message.payload:
        raise MessageValidationError("Spore delivery must contain 'spore_content' in payload")

def validate_message(self, message: BeastModeMessage) -> None:
    """Validate spore request message"""
    super().validate_message(message)
    if 'spore_name' not in message.payload:
        raise MessageValidationError("Spore request must contain 'spore_name' in payload")

def validate_message(self, message: BeastModeMessage) -> None:
    """Validate spore spawn message"""
    super().validate_message(message)
    if 'spore_type' not in message.payload:
        raise MessageValidationError("Spore spawn must contain 'spore_type' in payload")
