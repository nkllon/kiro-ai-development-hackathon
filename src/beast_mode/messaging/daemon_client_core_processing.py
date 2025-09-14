"""
Daemon Client Core Processing

This module was extracted from daemon_client_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
import threading
import time
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
import redis.asyncio as redis
from .models import BeastModeMessage, MessageType
from src.rm_ddd.core.health import ModuleHealth


class ProcessmessagesClass:
    """Auto-generated class for functions."""

    def process_messages(self):
    """Process all pending messages with registered handlers."""
    messages = self.check_messages()
    for queued_msg in messages:
    message = queued_msg.message
    if message.type in self.message_handlers:
    for handler in self.message_handlers[message.type]:
    try:
    handler(message)
    except Exception as e:
    logging.error(f'Handler error: {str(e)}')
    queued_msg.processed = True

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

