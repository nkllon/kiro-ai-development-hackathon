"""
Daemon Client Core Core Validation

This module was extracted from daemon_client_core_core.py
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

def check_mail(self) -> List[QueuedMessage]:
    """Check for new messages (non-blocking)."""
    messages = []
    while self.inbox:
        messages.append(self.inbox.popleft())
    return messages

def check_messages(self) -> List[QueuedMessage]:
    """Check for new messages (non-blocking)."""
    return self.daemon.check_mail()
