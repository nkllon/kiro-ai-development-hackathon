"""
Daemon Client Core Core

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
        self.inbox = deque(maxlen=max_queue_size)
        self.outbox = deque(maxlen=max_queue_size)
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.is_running = False
        self.is_connected = False
        self.daemon_thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
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
            time.sleep(1)
            self.logger.info(f"Beast Mode daemon started for {self.agent_id}")
            return self.is_connected
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {str(e)}")
            return False

    def stop_daemon(self):
        """Stop the background daemon."""
        self.is_running = False
        if self.daemon_thread and self.daemon_thread.is_alive():
            self.daemon_thread.join(timeout=5)
        self.logger.info("Beast Mode daemon stopped")

    def _run_daemon(self):
        """Main daemon loop - runs in background thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._daemon_main())
        except Exception as e:
            self.logger.error(f"Daemon error: {str(e)}")
        finally:
            self.loop.close()

    async def _daemon_main(self):
        """Main async daemon logic."""
        self.is_running = True
        while self.is_running:
            try:
                if not self.is_connected:
                    await self._connect()
                if self.is_connected:
                    await self._process_outbox()
                    await self._listen_for_messages()
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Daemon loop error: {str(e)}")
                self.is_connected = False
                await asyncio.sleep(1)

    async def _connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            await self.redis_client.ping()
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(self.channel)
            self.is_connected = True
            self.logger.info(f"Daemon connected to Redis: {self.redis_url}")
        except Exception as e:
            self.logger.error(f"Daemon connection failed: {str(e)}")
            self.stats["connection_errors"] += 1
            self.is_connected = False

    async def _process_outbox(self):
        """Send queued outgoing messages."""
        while self.outbox and self.is_connected:
            try:
                message_data = self.outbox.popleft()
                message_json = json.dumps(message_data, default=str)
                await self.redis_client.publish(self.channel, message_json)
                self.stats["messages_sent"] += 1
                self.stats["last_activity"] = datetime.now()
            except Exception as e:
                self.logger.error(f"Error sending message: {str(e)}")
                break

    async def _listen_for_messages(self):
        """Listen for incoming messages (non-blocking)."""
        if not self.pubsub:
            return
        try:
            raw_message = await asyncio.wait_for(
                self.pubsub.get_message(ignore_subscribe_messages=True), timeout=0.1
            )
            if raw_message and raw_message["type"] == "message":
                try:
                    message_data = json.loads(raw_message["data"])
                    message = BeastModeMessage(**message_data)
                    if message.source == self.agent_id:
                        return
                    queued_msg = QueuedMessage(
                        message=message, received_at=datetime.now()
                    )
                    self.inbox.append(queued_msg)
                    self.stats["messages_received"] += 1
                    self.stats["last_activity"] = datetime.now()
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON message: {str(e)}")
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            self.logger.error(f"Error listening for messages: {str(e)}")

    def send_message(self, message: BeastModeMessage):
        """Queue a message for sending (non-blocking)."""
        if not message.source:
            message.source = self.agent_id
        message_data = message.model_dump()
        self.outbox.append(message_data)

    def check_mail(self) -> List[QueuedMessage]:
        """Check for new messages (non-blocking)."""
        messages = []
        while self.inbox:
            messages.append(self.inbox.popleft())
        return messages

    def get_unread_count(self) -> int:
        """Get count of unread messages."""
        return len(self.inbox)

    def get_status(self) -> Dict[str, Any]:
        """Get daemon status."""
        return {
            "agent_id": self.agent_id,
            "is_running": self.is_running,
            "is_connected": self.is_connected,
            "inbox_count": len(self.inbox),
            "outbox_count": len(self.outbox),
            "stats": self.stats.copy(),
        }

    def announce_presence(self):
        """Announce agent presence to network."""
        announcement = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source=self.agent_id,
            payload={
                "agent_type": "DaemonClient",
                "status": "online",
                "capabilities": ["background_processing", "message_queuing"],
                "daemon_version": "1.0",
            },
        )
        self.send_message(announcement)

    def send_spore(self, spore_data: Dict[str, Any]):
        """Send a spore to the network."""
        spore_message = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source=self.agent_id,
            payload={
                "spore_type": "systematic_pattern",
                "spore_data": spore_data,
                "shared_at": datetime.now().isoformat(),
            },
        )
        self.send_message(spore_message)


class BeastModeClient:
    """
    High-level client for Beast Mode network using daemon backend.

    Provides simple, non-blocking interface for network communication.
    """

    def __init__(self, agent_id: str, **daemon_kwargs):
        self.agent_id = agent_id
        self.daemon = BeastModeDaemon(agent_id, **daemon_kwargs)
        self.message_handlers: Dict[MessageType, List[Callable]] = {}

    def start(self) -> bool:
        """Start the Beast Mode client."""
        success = self.daemon.start_daemon()
        if success:
            self.daemon.announce_presence()
        return success

    def stop(self):
        """Stop the Beast Mode client."""
        self.daemon.stop_daemon()

    def send_message(self, message: BeastModeMessage):
        """Send a message (non-blocking)."""
        self.daemon.send_message(message)

    def check_messages(self) -> List[QueuedMessage]:
        """Check for new messages (non-blocking)."""
        return self.daemon.check_mail()

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
                        logging.error(f"Handler error: {str(e)}")
            queued_msg.processed = True

    def register_handler(
        self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]
    ):
        """Register a message handler."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    def get_status(self) -> Dict[str, Any]:
        """Get client status."""
        return self.daemon.get_status()

    def send_spore(self, spore_data: Dict[str, Any]):
        """Send a spore to the network."""
        self.daemon.send_spore(spore_data)


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
    self.inbox = deque(maxlen=max_queue_size)
    self.outbox = deque(maxlen=max_queue_size)
    self.redis_client: Optional[redis.Redis] = None
    self.pubsub: Optional[redis.client.PubSub] = None
    self.is_running = False
    self.is_connected = False
    self.daemon_thread: Optional[threading.Thread] = None
    self.loop: Optional[asyncio.AbstractEventLoop] = None
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
        time.sleep(1)
        self.logger.info(f"Beast Mode daemon started for {self.agent_id}")
        return self.is_connected
    except Exception as e:
        self.logger.error(f"Failed to start daemon: {str(e)}")
        return False


def stop_daemon(self):
    """Stop the background daemon."""
    self.is_running = False
    if self.daemon_thread and self.daemon_thread.is_alive():
        self.daemon_thread.join(timeout=5)
    self.logger.info("Beast Mode daemon stopped")


def _run_daemon(self):
    """Main daemon loop - runs in background thread."""
    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.loop)
    try:
        self.loop.run_until_complete(self._daemon_main())
    except Exception as e:
        self.logger.error(f"Daemon error: {str(e)}")
    finally:
        self.loop.close()


def send_message(self, message: BeastModeMessage):
    """Queue a message for sending (non-blocking)."""
    if not message.source:
        message.source = self.agent_id
    message_data = message.model_dump()
    self.outbox.append(message_data)


def get_unread_count(self) -> int:
    """Get count of unread messages."""
    return len(self.inbox)


def get_status(self) -> Dict[str, Any]:
    """Get daemon status."""
    return {
        "agent_id": self.agent_id,
        "is_running": self.is_running,
        "is_connected": self.is_connected,
        "inbox_count": len(self.inbox),
        "outbox_count": len(self.outbox),
        "stats": self.stats.copy(),
    }


def announce_presence(self):
    """Announce agent presence to network."""
    announcement = BeastModeMessage(
        type=MessageType.AGENT_DISCOVERY,
        source=self.agent_id,
        payload={
            "agent_type": "DaemonClient",
            "status": "online",
            "capabilities": ["background_processing", "message_queuing"],
            "daemon_version": "1.0",
        },
    )
    self.send_message(announcement)


def send_spore(self, spore_data: Dict[str, Any]):
    """Send a spore to the network."""
    spore_message = BeastModeMessage(
        type=MessageType.SPORE_DELIVERY,
        source=self.agent_id,
        payload={
            "spore_type": "systematic_pattern",
            "spore_data": spore_data,
            "shared_at": datetime.now().isoformat(),
        },
    )
    self.send_message(spore_message)


def __init__(self, agent_id: str, **daemon_kwargs):
    self.agent_id = agent_id
    self.daemon = BeastModeDaemon(agent_id, **daemon_kwargs)
    self.message_handlers: Dict[MessageType, List[Callable]] = {}


def start(self) -> bool:
    """Start the Beast Mode client."""
    success = self.daemon.start_daemon()
    if success:
        self.daemon.announce_presence()
    return success


def stop(self):
    """Stop the Beast Mode client."""
    self.daemon.stop_daemon()


def send_message(self, message: BeastModeMessage):
    """Send a message (non-blocking)."""
    self.daemon.send_message(message)


def register_handler(
    self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]
):
    """Register a message handler."""
    if message_type not in self.message_handlers:
        self.message_handlers[message_type] = []
    self.message_handlers[message_type].append(handler)


def get_status(self) -> Dict[str, Any]:
    """Get client status."""
    return self.daemon.get_status()


def send_spore(self, spore_data: Dict[str, Any]):
    """Send a spore to the network."""
    self.daemon.send_spore(spore_data)


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
    self.inbox = deque(maxlen=max_queue_size)
    self.outbox = deque(maxlen=max_queue_size)
    self.redis_client: Optional[redis.Redis] = None
    self.pubsub: Optional[redis.client.PubSub] = None
    self.is_running = False
    self.is_connected = False
    self.daemon_thread: Optional[threading.Thread] = None
    self.loop: Optional[asyncio.AbstractEventLoop] = None
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
        time.sleep(1)
        self.logger.info(f"Beast Mode daemon started for {self.agent_id}")
        return self.is_connected
    except Exception as e:
        self.logger.error(f"Failed to start daemon: {str(e)}")
        return False


def stop_daemon(self):
    """Stop the background daemon."""
    self.is_running = False
    if self.daemon_thread and self.daemon_thread.is_alive():
        self.daemon_thread.join(timeout=5)
    self.logger.info("Beast Mode daemon stopped")


def _run_daemon(self):
    """Main daemon loop - runs in background thread."""
    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.loop)
    try:
        self.loop.run_until_complete(self._daemon_main())
    except Exception as e:
        self.logger.error(f"Daemon error: {str(e)}")
    finally:
        self.loop.close()


def send_message(self, message: BeastModeMessage):
    """Queue a message for sending (non-blocking)."""
    if not message.source:
        message.source = self.agent_id
    message_data = message.model_dump()
    self.outbox.append(message_data)


def get_unread_count(self) -> int:
    """Get count of unread messages."""
    return len(self.inbox)


def get_status(self) -> Dict[str, Any]:
    """Get daemon status."""
    return {
        "agent_id": self.agent_id,
        "is_running": self.is_running,
        "is_connected": self.is_connected,
        "inbox_count": len(self.inbox),
        "outbox_count": len(self.outbox),
        "stats": self.stats.copy(),
    }


def announce_presence(self):
    """Announce agent presence to network."""
    announcement = BeastModeMessage(
        type=MessageType.AGENT_DISCOVERY,
        source=self.agent_id,
        payload={
            "agent_type": "DaemonClient",
            "status": "online",
            "capabilities": ["background_processing", "message_queuing"],
            "daemon_version": "1.0",
        },
    )
    self.send_message(announcement)


def send_spore(self, spore_data: Dict[str, Any]):
    """Send a spore to the network."""
    spore_message = BeastModeMessage(
        type=MessageType.SPORE_DELIVERY,
        source=self.agent_id,
        payload={
            "spore_type": "systematic_pattern",
            "spore_data": spore_data,
            "shared_at": datetime.now().isoformat(),
        },
    )
    self.send_message(spore_message)


def __init__(self, agent_id: str, **daemon_kwargs):
    self.agent_id = agent_id
    self.daemon = BeastModeDaemon(agent_id, **daemon_kwargs)
    self.message_handlers: Dict[MessageType, List[Callable]] = {}


def start(self) -> bool:
    """Start the Beast Mode client."""
    success = self.daemon.start_daemon()
    if success:
        self.daemon.announce_presence()
    return success


def stop(self):
    """Stop the Beast Mode client."""
    self.daemon.stop_daemon()


def send_message(self, message: BeastModeMessage):
    """Send a message (non-blocking)."""
    self.daemon.send_message(message)


def register_handler(
    self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]
):
    """Register a message handler."""
    if message_type not in self.message_handlers:
        self.message_handlers[message_type] = []
    self.message_handlers[message_type].append(handler)


def get_status(self) -> Dict[str, Any]:
    """Get client status."""
    return self.daemon.get_status()


def send_spore(self, spore_data: Dict[str, Any]):
    """Send a spore to the network."""
    self.daemon.send_spore(spore_data)
