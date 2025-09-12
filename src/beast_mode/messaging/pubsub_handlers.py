"""
Pubsub Handlers

This module was extracted from pubsub.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import uuid
import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError
from .models import BeastModeMessage, MessageType

class MessageHandler(ABC):
    """Abstract base class for message handlers"""

    @abstractmethod
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """
        Handle an incoming message.
        
        Args:
            message: The message to handle
            
        Returns:
            Optional response message
        """
        pass

    @abstractmethod
    def get_supported_types(self) -> List[MessageType]:
        """Return list of supported message types"""
        pass
