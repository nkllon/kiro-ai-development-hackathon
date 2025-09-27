"""
Intelligent HTTP Polling Fallback System

This module provides intelligent HTTP polling capabilities as a fallback
when WebSocket connections fail. It includes rate limiting, bot-safe headers,
request deduplication, and exponential backoff strategies.

Components:
- IntelligentPoller: Main polling orchestrator
- RateLimiter: Per-endpoint and global rate limiting
- RequestDeduplicator: Request caching and batching
- BotSafeHeaders: Bot-safe header configuration
- PollingStrategy: Exponential backoff with jitter
"""

from .intelligent_poller import IntelligentPoller
from .rate_limiter import RateLimiter
from .request_deduplicator import RequestDeduplicator
from .bot_safe_headers import BotSafeHeaders
from .polling_strategy import PollingStrategy

__all__ = [
    "IntelligentPoller",
    "RateLimiter", 
    "RequestDeduplicator",
    "BotSafeHeaders",
    "PollingStrategy"
]