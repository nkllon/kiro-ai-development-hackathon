#!/usr/bin/env python3
"""
Beast Mode Daemon Client Core
=============================

Background daemon that handles Beast Mode network communication with message queuing.
Allows non-blocking operation - you can work while the daemon handles network traffic.
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

from ..messaging.message_models import BeastModeMessage, MessageType


@dataclass
class QueuedMessage:
    """Message stored in the local queue."""

    message: BeastModeMessage
    received_at: datetime
    processed: bool = False


class BeastModeDaemon:
    """
    Background daemon for Beast Mode network communication.

    Runs in a separate thread, handles all Redis pub/sub operations,
    and maintains local message queues for non-blocking access.
    """

    def __init__(
        self,
        agent_id: str,
        redis_url: str = "redis://localhost:6379",
        channel: str = "beast_mode_network",
        max_queue_size: int = 1000,
    ):
        self.agent_id = agent_id
        self.redis_url = redis_url
        self.channel = channel
        self.max_queue_size = max_queue_size

        # Message queues
        self.inbox = deque(maxlen=max_queue_size)
        self.outbox = deque(maxlen=max_queue_size)

        # Connection state
        self.redis_client = None
        self.pubsub = None
        self.is_running = False
        self.is_connected = False

        # Threading
        self.daemon_thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None

        # Statistics
        self.stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "connection_errors": 0,
            "last_activity": None,
        }

        self.logger = logging.getLogger(__name__)

    def start_daemon(self) -> bool:
        """Start the background daemon thread."""
        if self.is_running:
            self.logger.warning("Daemon already running")
            return True

        try:
            self.daemon_thread = threading.Thread(
                target=self._run_daemon,
                name=f"BeastModeDaemon-{self.agent_id}",
                daemon=True,
            )
            self.daemon_thread.start()

            # Wait a moment for connection
            time.sleep(1)

            self.logger.info(f"Beast Mode daemon started for {self.agent_id}")
            return self.is_connected

        except Exception as e:
            self.logger.error(f"Failed to start daemon: {str(e)}")
            return False

    def stop_daemon(self):
        """Stop the background daemon thread."""
        self.is_running = False
        if self.daemon_thread:
            self.daemon_thread.join(timeout=5)
            self.logger.info("Beast Mode daemon stopped")

    def send_message(self, message: BeastModeMessage) -> bool:
        """Send a message through the daemon."""
        try:
            self.outbox.append(QueuedMessage(
                message=message,
                received_at=datetime.now(),
                processed=False
            ))
            self.stats["messages_sent"] += 1
            self.stats["last_activity"] = datetime.now()
            return True
        except Exception as e:
            self.logger.error(f"Failed to queue message: {str(e)}")
            return False

    def check_mail(self) -> List[QueuedMessage]:
        """Check for new messages in the inbox."""
        return list(self.inbox)

    def get_status(self) -> Dict[str, Any]:
        """Get daemon status."""
        return {
            'is_running': self.is_running,
            'is_connected': self.is_connected,
            'inbox_count': len(self.inbox),
            'outbox_count': len(self.outbox),
            'stats': self.stats.copy(),
        }

    def announce_presence(self):
        """Announce presence on the network."""
        announcement = BeastModeMessage(
            message_type=MessageType.AGENT_ANNOUNCEMENT,
            sender_id=self.agent_id,
            content={"action": "presence_announcement"},
        )
        self.send_message(announcement)

    def send_spore(self, spore_data: Dict[str, Any]):
        """Send spore data to the network."""
        spore_message = BeastModeMessage(
            message_type=MessageType.SPORE_SHARE,
            sender_id=self.agent_id,
            content=spore_data,
        )
        self.send_message(spore_message)

    def get_unread_count(self) -> int:
        """Get count of unread messages."""
        return len([msg for msg in self.inbox if not msg.processed])

    def _run_daemon(self):
        """Main daemon loop."""
        self.is_running = True

        try:
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Run the async daemon
            self.loop.run_until_complete(self._async_daemon())

        except Exception as e:
            self.logger.error(f"Daemon loop failed: {str(e)}")
        finally:
            if self.loop:
                self.loop.close()
            self.is_running = False

    async def _async_daemon(self):
        """Async daemon implementation."""
        try:
            # Connect to Redis
            self.redis_client = await self._connect_redis()
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(self.channel)

            self.is_connected = True
            self.logger.info(f"Connected to Redis channel: {self.channel}")

            # Announce presence
            await self._announce_async()

            # Main message processing loop
            while self.is_running:
                try:
                    # Process outgoing messages
                    await self._process_outbox()

                    # Process incoming messages
                    await self._process_inbox()

                    # Check for new messages
                    await self._receive_messages()

                    # Sleep to prevent busy loop
                    await asyncio.sleep(0.1)

                except Exception as e:
                    self.logger.error(f"Error in message processing: {str(e)}")
                    await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Daemon connection failed: {str(e)}")
            self.is_connected = False
            self.stats["connection_errors"] += 1

    async def _connect_redis(self):
        """Connect to Redis server."""
        try:
            # For now, we'll simulate Redis functionality
            # In a real implementation, this would connect to actual Redis
            self.logger.info("Redis connection simulated (no actual Redis server)")
            return None  # Mock client
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def _announce_async(self):
        """Announce presence asynchronously."""
        try:
            if self.redis_client:
                await self.redis_client.publish(
                    self.channel,
                    json.dumps({
                        "message_type": MessageType.AGENT_ANNOUNCEMENT.value,
                        "sender_id": self.agent_id,
                        "content": {"action": "presence_announcement"},
                        "timestamp": datetime.now().isoformat(),
                    })
                )
        except Exception as e:
            self.logger.error(f"Failed to announce presence: {str(e)}")

    async def _process_outbox(self):
        """Process messages in the outbox."""
        while self.outbox and self.is_running:
            queued_msg = self.outbox.popleft()
            try:
                if self.redis_client:
                    await self.redis_client.publish(
                        self.channel,
                        json.dumps(queued_msg.message.to_dict())
                    )
                queued_msg.processed = True
            except Exception as e:
                self.logger.error(f"Failed to send message: {str(e)}")
                # Put message back in queue for retry
                self.outbox.appendleft(queued_msg)

    async def _process_inbox(self):
        """Process messages in the inbox."""
        # For now, this is a no-op since we're not actually receiving messages
        # In a real implementation, this would handle message processing
        pass

    async def _receive_messages(self):
        """Receive messages from Redis."""
        # Simulate receiving messages for testing
        # In a real implementation, this would listen to Redis pub/sub
        pass


# Export for use by Redis transport
__all__ = ["BeastModeDaemon", "QueuedMessage"]
