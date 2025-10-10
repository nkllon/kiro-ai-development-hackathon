"""Lightweight Redis-backed mailbox service for inter-agent messaging."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional
from uuid import uuid4

import redis.asyncio as redis


@dataclass
class MailboxConfig:
    """Configuration for connecting to Redis streams."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    stream_prefix: str = "beast:mailbox"
    max_stream_length: int = 1000
    poll_interval: float = 2.0


@dataclass
class MailboxMessage:
    """Structured message exchanged between agents."""

    message_id: str
    sender: str
    recipient: str
    payload: Dict[str, Any]
    message_type: str = "direct_message"
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())

    def to_redis_fields(self) -> Dict[str, str]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": json.dumps(self.payload),
            "message_type": self.message_type,
            "timestamp": str(self.timestamp),
        }

    @classmethod
    def from_redis_fields(cls, fields: Dict[bytes, bytes]) -> "MailboxMessage":
        decoded = {k.decode(): v.decode() for k, v in fields.items()}
        payload = json.loads(decoded.get("payload", "{}"))
        return cls(
            message_id=decoded.get("message_id", str(uuid4())),
            sender=decoded.get("sender", "unknown"),
            recipient=decoded.get("recipient", "unknown"),
            payload=payload,
            message_type=decoded.get("message_type", "direct_message"),
            timestamp=float(decoded.get("timestamp", "0.0")),
        )


class RedisMailboxService:
    """Async Redis stream consumer/producer for inter-agent communication."""

    def __init__(self, agent_id: str, config: Optional[MailboxConfig] = None):
        self.agent_id = agent_id
        self.config = config or MailboxConfig()
        self.logger = logging.getLogger(f"beast_mailbox.{agent_id}")
        self._client: Optional[redis.Redis] = None
        self._processing_task: Optional[asyncio.Task] = None
        self._handlers: List[Callable[[MailboxMessage], Awaitable[None]]] = []
        self._running = False
        self._consumer_group = f"{agent_id}:group"
        self._consumer_name = f"{agent_id}:{uuid4().hex[:6]}"

    @property
    def inbox_stream(self) -> str:
        return f"{self.config.stream_prefix}:{self.agent_id}:in"

    async def connect(self) -> None:
        if self._client is None:
            self._client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.db,
                decode_responses=False,
            )

    async def start(self) -> bool:
        await self.connect()
        assert self._client is not None
        try:
            await self._client.xgroup_create(
                name=self.inbox_stream,
                groupname=self._consumer_group,
                id="$",
                mkstream=True,
            )
            self.logger.info(
                "Created consumer group %s for stream %s",
                self._consumer_group,
                self.inbox_stream,
            )
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise
        self._running = True
        self._processing_task = asyncio.create_task(self._consume_loop())
        return True

    async def stop(self) -> None:
        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            self._processing_task = None
        if self._client:
            await self._client.close()
            self._client = None

    def register_handler(self, handler: Callable[[MailboxMessage], Awaitable[None]]) -> None:
        self._handlers.append(handler)

    async def send_message(
        self,
        recipient: str,
        payload: Dict[str, Any],
        message_type: str = "direct_message",
        message_id: Optional[str] = None,
    ) -> str:
        await self.connect()
        assert self._client is not None
        message = MailboxMessage(
            message_id=message_id or str(uuid4()),
            sender=self.agent_id,
            recipient=recipient,
            payload=payload,
            message_type=message_type,
        )
        stream = f"{self.config.stream_prefix}:{recipient}:in"
        await self._client.xadd(
            stream,
            message.to_redis_fields(),
            maxlen=self.config.max_stream_length,
            approximate=True,
        )
        self.logger.debug("Sent message %s to stream %s", message.message_id, stream)
        return message.message_id

    async def _consume_loop(self) -> None:
        assert self._client is not None
        while self._running:
            try:
                response = await self._client.xreadgroup(
                    groupname=self._consumer_group,
                    consumername=self._consumer_name,
                    streams={self.inbox_stream: ">"},
                    count=10,
                    block=int(self.config.poll_interval * 1000),
                )
                if not response:
                    continue
                for stream_name, messages in response:
                    self.logger.debug(
                        "Redis mailbox received %d messages from %s",
                        len(messages),
                        stream_name,
                    )
                    for message_id, fields in messages:
                        mailbox_message = MailboxMessage.from_redis_fields(fields)
                        await self._dispatch(mailbox_message)
                        await self._client.xack(stream_name, self._consumer_group, message_id)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.exception("Error in mailbox consume loop: %s", exc)
                await asyncio.sleep(self.config.poll_interval)

    async def _dispatch(self, message: MailboxMessage) -> None:
        if not self._handlers:
            self.logger.info("Mailbox message received with no handlers registered: %s", message)
            return
        for handler in list(self._handlers):
            try:
                await handler(message)
            except Exception as exc:
                self.logger.exception("Mailbox handler failed: %s", exc)

