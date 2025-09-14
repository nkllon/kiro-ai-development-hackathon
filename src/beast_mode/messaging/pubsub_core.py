"""
Pubsub Core

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
from src.rm_ddd.core.health import ModuleHealth


@abstractmethod
def get_supported_types(self) -> List[MessageType]:
    """Return list of supported message types"""
    pass

def __init__(self, redis_url: str='redis://localhost:6379'):
    self.redis_url = redis_url
    self.client: Optional[redis.Redis] = None
    self.pubsub: Optional[redis.client.PubSub] = None
    self.is_initialized = False
    self.is_listening = False
    self.listening_channels: Set[str] = set()
    self.handlers: Dict[str, List[MessageHandler]] = {}
    self.metrics = {'messages_sent': 0, 'messages_received': 0, 'messages_processed': 0, 'processing_errors': 0, 'last_activity': None}
    self.listener_task: Optional[asyncio.Task] = None

def register_handler(self, handler: MessageHandler, channel: str) -> None:
    """Register a message handler for a channel"""
    if channel not in self.handlers:
        self.handlers[channel] = []
    self.handlers[channel].append(handler)
    logger.info(f'Registered handler for channel {channel}')

def get_health_status(self) -> Dict[str, Any]:
    """Get health status and metrics"""
    return {'status': 'healthy' if self.is_initialized else 'not_initialized', 'is_listening': self.is_listening, 'listening_channels': list(self.listening_channels), 'registered_handlers': {channel: len(handlers) for channel, handlers in self.handlers.items()}, 'metrics': self.metrics.copy()}
