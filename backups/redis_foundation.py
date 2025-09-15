#!/usr/bin/env python3
"""
Beast Mode Redis Pub/Sub Foundation

Provides systematic Redis connection management with health monitoring,
reconnection logic, and Beast Mode compliance.

Requirements: 1.1, 1.2
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
from enum import Enum
import json

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..core.reflective_module import ReflectiveModule


class ConnectionStatus(str, Enum):
    """Redis connection status states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class RedisConfig:
    """Redis connection configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 10
    health_check_interval: float = 30.0
    reconnect_delay: float = 1.0
    max_reconnect_attempts: int = 5


class RedisFoundation(ReflectiveModule):
    """
    Systematic Redis pub/sub foundation with Beast Mode compliance.

    Provides connection management, health monitoring, and automatic
    reconnection with proper error handling and logging.
    """

    def __init__(self, config: Optional[RedisConfig] = None):
        """Initialize Redis foundation with configuration."""
        super().__init__("RedisFoundation")
        self.config = config or RedisConfig()
        self.connection_pool: Optional[redis.ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self.status = ConnectionStatus.DISCONNECTED
        self.last_health_check = 0.0
        self.reconnect_attempts = 0
        self.subscribers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)

        if not REDIS_AVAILABLE:
            self.logger.error(
                "Redis not available - install with: uv add redis[hiredis]"
            )
            self.status = ConnectionStatus.FAILED

    async def initialize(self) -> bool:
        """Initialize Redis connection and health monitoring."""
        if not REDIS_AVAILABLE:
            return False

        try:
            # Create connection pool
            self.connection_pool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                decode_responses=True,
            )

            # Create Redis client
            self.client = redis.Redis(connection_pool=self.connection_pool)

            # Test connection
            await self.client.ping()
            self.status = ConnectionStatus.CONNECTED
            self.reconnect_attempts = 0

            self.logger.info(f"Redis connected: {self.config.host}:{self.config.port}")
            return True

        except Exception as e:
            self.logger.error(f"Redis connection failed: {str(e)}")
            self.status = ConnectionStatus.FAILED
            return False

    async def health_check(self) -> bool:
        """Perform Redis health check."""
        if not self.client:
            return False

        try:
            await self.client.ping()
            self.last_health_check = time.time()
            if self.status != ConnectionStatus.CONNECTED:
                self.status = ConnectionStatus.CONNECTED
                self.logger.info("Redis health check passed - connection restored")
            return True

        except Exception as e:
            self.logger.warning(f"Redis health check failed: {str(e)}")
            if self.status == ConnectionStatus.CONNECTED:
                self.status = ConnectionStatus.RECONNECTING
                asyncio.create_task(self._reconnect())
            return False

    async def _reconnect(self) -> bool:
        """Attempt to reconnect to Redis with exponential backoff."""
        if self.reconnect_attempts >= self.config.max_reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")
            self.status = ConnectionStatus.FAILED
            return False

        self.reconnect_attempts += 1
        delay = self.config.reconnect_delay * (2 ** (self.reconnect_attempts - 1))

        self.logger.info(
            f"Reconnecting to Redis (attempt {self.reconnect_attempts}/{self.config.max_reconnect_attempts}) in {delay}s"
        )
        await asyncio.sleep(delay)

        return await self.initialize()

    async def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """
        Publish message to Redis channel.

        Args:
            channel: Redis channel name
            message: Message data to publish

        Returns:
            True if published successfully, False otherwise
        """
        if not self.client or self.status != ConnectionStatus.CONNECTED:
            self.logger.error("Cannot publish - Redis not connected")
            return False

        try:
            message_json = json.dumps(message)
            await self.client.publish(channel, message_json)
            return True

        except Exception as e:
            self.logger.error(f"Failed to publish to {channel}: {str(e)}")
            return False

    async def subscribe(
        self, channel: str, callback: Callable[[Dict[str, Any]], None]
    ) -> bool:
        """
        Subscribe to Redis channel with callback.

        Args:
            channel: Redis channel name
            callback: Function to call when message received

        Returns:
            True if subscribed successfully, False otherwise
        """
        if not self.client or self.status != ConnectionStatus.CONNECTED:
            self.logger.error("Cannot subscribe - Redis not connected")
            return False

        try:
            if channel not in self.subscribers:
                self.subscribers[channel] = []

            self.subscribers[channel].append(callback)

            # Start subscription task if first subscriber for this channel
            if len(self.subscribers[channel]) == 1:
                asyncio.create_task(self._subscription_loop(channel))

            return True

        except Exception as e:
            self.logger.error(f"Failed to subscribe to {channel}: {str(e)}")
            return False

    async def _subscription_loop(self, channel: str):
        """Handle subscription messages for a channel."""
        try:
            pubsub = self.client.pubsub()
            await pubsub.subscribe(channel)

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])

                        # Call all callbacks for this channel
                        for callback in self.subscribers.get(channel, []):
                            try:
                                callback(data)
                            except Exception as e:
                                self.logger.error(
                                    f"Callback error for {channel}: {str(e)}"
                                )

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON in {channel}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Subscription loop error for {channel}: {str(e)}")
        finally:
            await pubsub.close()

    async def unsubscribe(
        self, channel: str, callback: Optional[Callable] = None
    ) -> bool:
        """
        Unsubscribe from Redis channel.

        Args:
            channel: Redis channel name
            callback: Specific callback to remove (None for all)

        Returns:
            True if unsubscribed successfully, False otherwise
        """
        try:
            if channel not in self.subscribers:
                return True

            if callback:
                if callback in self.subscribers[channel]:
                    self.subscribers[channel].remove(callback)
            else:
                self.subscribers[channel].clear()

            # Clean up empty channel subscriptions
            if not self.subscribers[channel]:
                del self.subscribers[channel]

            return True

        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from {channel}: {str(e)}")
            return False

    async def get_connection_info(self) -> Dict[str, Any]:
        """Get Redis connection information."""
        return {
            "status": self.status.value,
            "host": self.config.host,
            "port": self.config.port,
            "db": self.config.db,
            "connected": self.status == ConnectionStatus.CONNECTED,
            "last_health_check": self.last_health_check,
            "reconnect_attempts": self.reconnect_attempts,
            "active_subscriptions": list(self.subscribers.keys()),
        }

    async def shutdown(self):
        """Gracefully shutdown Redis connection."""
        try:
            # Clear all subscriptions
            self.subscribers.clear()

            # Close Redis client
            if self.client:
                await self.client.close()

            # Close connection pool
            if self.connection_pool:
                await self.connection_pool.disconnect()

            self.status = ConnectionStatus.DISCONNECTED
            self.logger.info("Redis foundation shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during Redis shutdown: {str(e)}")

    # ReflectiveModule interface
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Beast Mode monitoring."""
        return {
            "module": "RedisFoundation",
            "status": self.status.value,
            "healthy": self.status == ConnectionStatus.CONNECTED,
            "last_health_check": self.last_health_check,
            "reconnect_attempts": self.reconnect_attempts,
            "active_subscriptions": len(self.subscribers),
            "redis_available": REDIS_AVAILABLE,
        }

    def get_capabilities(self) -> List[str]:
        """Get Redis foundation capabilities."""
        capabilities = [
            "redis_pubsub",
            "connection_management",
            "health_monitoring",
            "automatic_reconnection",
        ]

        if REDIS_AVAILABLE:
            capabilities.append("redis_client")

        return capabilities

    def _get_primary_responsibility(self) -> str:
        """Get primary responsibility for this module."""
        return "Redis pub/sub communication foundation"

    def get_health_indicators(self) -> Dict[str, Any]:
        """Get health indicators for monitoring."""
        return {
            "connection_status": self.status.value,
            "redis_available": REDIS_AVAILABLE,
            "active_subscriptions": len(self.subscribers),
            "reconnect_attempts": self.reconnect_attempts,
        }

    def get_module_status(self) -> str:
        """Get current module status."""
        return self.status.value

    def is_healthy(self) -> bool:
        """Check if module is healthy."""
        return self.status == ConnectionStatus.CONNECTED
