"""
Beast Mode Pub/Sub Manager

Higher-level pub/sub management with message handlers and queuing.
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


logger = logging.getLogger(__name__)


class MessageHandler(ABC):
    """Abstract base class for message handlers"""

    @abstractmethod
    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
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


class PubSubManager:
    """Advanced pub/sub manager with handlers and queuing"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None

        # State management
        self.is_initialized = False
        self.is_listening = False
        self.listening_channels: Set[str] = set()

        # Handler management
        self.handlers: Dict[str, List[MessageHandler]] = {}  # channel -> handlers

        # Metrics
        self.metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_processed": 0,
            "processing_errors": 0,
            "last_activity": None,
        }

        # Background tasks
        self.listener_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize Redis connection"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                socket_connect_timeout=10.0,
                socket_timeout=10.0,
                retry_on_timeout=True,
                decode_responses=True,
            )

            # Test connection
            await self.client.ping()
            self.is_initialized = True

            logger.info(f"PubSubManager initialized with Redis at {self.redis_url}")

        except Exception as e:
            logger.error(f"Failed to initialize PubSubManager: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown pub/sub manager"""
        try:
            self.is_listening = False

            # Cancel listener task
            if self.listener_task and not self.listener_task.done():
                self.listener_task.cancel()
                try:
                    await self.listener_task
                except asyncio.CancelledError:
                    pass

            # Close pubsub
            if self.pubsub:
                await self.pubsub.unsubscribe()
                await self.pubsub.aclose()
                self.pubsub = None

            # Close client
            if self.client:
                await self.client.aclose()
                self.client = None

            self.is_initialized = False
            logger.info("PubSubManager shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def register_handler(self, handler: MessageHandler, channel: str) -> None:
        """Register a message handler for a channel"""
        if channel not in self.handlers:
            self.handlers[channel] = []

        self.handlers[channel].append(handler)
        logger.info(f"Registered handler for channel {channel}")

    async def start_listening(self, channels: List[str]) -> None:
        """Start listening on specified channels"""
        if not self.is_initialized:
            raise RuntimeError("PubSubManager not initialized")

        try:
            self.pubsub = self.client.pubsub()

            # Subscribe to channels
            for channel in channels:
                await self.pubsub.subscribe(channel)
                self.listening_channels.add(channel)

            self.is_listening = True

            # Start background listener
            self.listener_task = asyncio.create_task(self._message_listener())

            logger.info(f"Started listening on channels: {channels}")

        except Exception as e:
            logger.error(f"Error starting listener: {e}")
            raise

    async def _message_listener(self) -> None:
        """Background message listener"""
        try:
            async for raw_message in self.pubsub.listen():
                if not self.is_listening:
                    break

                if raw_message["type"] == "message":
                    await self._process_raw_message(raw_message)

        except asyncio.CancelledError:
            logger.info("Message listener cancelled")
        except Exception as e:
            logger.error(f"Error in message listener: {e}")

    async def _process_raw_message(self, raw_message: Dict[str, Any]) -> None:
        """Process a raw Redis message"""
        try:
            # Parse message
            message_data = json.loads(raw_message["data"])
            message = BeastModeMessage(**message_data)

            # Update metrics
            self.metrics["messages_received"] += 1
            self.metrics["last_activity"] = datetime.now()

            # Get channel
            channel = raw_message["channel"]

            # Process with handlers
            if channel in self.handlers:
                for handler in self.handlers[channel]:
                    try:
                        # Check if handler supports this message type
                        if message.type in handler.get_supported_types():
                            response = await handler.handle_message(message)

                            # Send response if provided
                            if response:
                                await self.publish_message(response, channel)

                            self.metrics["messages_processed"] += 1

                    except Exception as e:
                        self.metrics["processing_errors"] += 1
                        logger.error(
                            f"Error in handler {handler.__class__.__name__}: {e}"
                        )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message JSON: {e}")
            self.metrics["processing_errors"] += 1

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.metrics["processing_errors"] += 1

    async def publish_message(self, message: BeastModeMessage, channel: str) -> None:
        """Publish a message to a channel"""
        if not self.is_initialized:
            raise RuntimeError("PubSubManager not initialized")

        try:
            # Serialize message
            message_data = message.model_dump()
            message_json = json.dumps(message_data, default=str)

            # Publish
            await self.client.publish(channel, message_json)

            # Update metrics
            self.metrics["messages_sent"] += 1
            self.metrics["last_activity"] = datetime.now()

            logger.debug(f"Published {message.type} to channel {channel}")

        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            raise

    async def send_prompt_request(
        self, prompt: str, channel: str, priority: int = 5
    ) -> str:
        """Send a prompt request message"""
        message = BeastModeMessage(
            type=MessageType.PROMPT_REQUEST,
            source="pubsub_manager",
            payload={"prompt": prompt},
            priority=priority,
        )

        await self.publish_message(message, channel)
        return message.id

    async def send_spore_spawn_request(
        self, spore_type: str, metadata: Dict[str, Any]
    ) -> str:
        """Send a spore spawn request"""
        message = BeastModeMessage(
            type=MessageType.SPORE_SPAWN,
            source="pubsub_manager",
            payload={"spore_type": spore_type, "metadata": metadata},
            priority=6,
        )

        await self.publish_message(message, "spores")
        return message.id

    async def process_queue(self, queue_name: str, max_messages: int = 10) -> int:
        """Process messages from a Redis queue"""
        if not self.is_initialized:
            raise RuntimeError("PubSubManager not initialized")

        processed = 0

        try:
            for _ in range(max_messages):
                # Try to pop a message from the queue
                result = await self.client.lpop(queue_name)
                if not result:
                    break

                try:
                    # Parse and process message
                    message_data = json.loads(result)
                    message = BeastModeMessage(**message_data)

                    # Find appropriate handler
                    for channel, handlers in self.handlers.items():
                        for handler in handlers:
                            if message.type in handler.get_supported_types():
                                await handler.handle_message(message)
                                processed += 1
                                break

                except Exception as e:
                    logger.error(f"Error processing queued message: {e}")
                    self.metrics["processing_errors"] += 1

        except Exception as e:
            logger.error(f"Error processing queue {queue_name}: {e}")

        return processed

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status and metrics"""
        return {
            "status": "healthy" if self.is_initialized else "not_initialized",
            "is_listening": self.is_listening,
            "listening_channels": list(self.listening_channels),
            "registered_handlers": {
                channel: len(handlers) for channel, handlers in self.handlers.items()
            },
            "metrics": self.metrics.copy(),
        }
