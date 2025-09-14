"""
Message Handlers Core Validation

This module was extracted from message_handlers_core.py
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


def validate_message_format(self, message_data: Dict[str, Any]) -> bool:
    """
        Validate message format without processing.
        
        Args:
            message_data: Raw message data
            
        Returns:
            bool: True if valid format
        """
    try:
        BeastModeMessage(**message_data)
        return True
    except Exception:
        return False
