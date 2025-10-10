#!/usr/bin/env python3
"""Redis-backed mailbox service for Beast Mode network messaging."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional
from uuid import uuid4

from .redis_foundation import RedisFoundation, RedisConfig
from src.rm_ddd.core.unified_reflective_module import (
    GracefulDegradationResult,
    ReflectiveModule,
)


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


class RedisMailboxService(ReflectiveModule):
    """Mailbox service built on top of Redis streams for durable messaging."""

    STREAM_PREFIX = "beast:mailbox"

    def __init__(
        self,
        agent_id: str,
        redis_config: Optional[RedisConfig] = None,
        poll_interval: float = 2.0,
    ):
        super().__init__()
        self.module_id = f"mailbox_service:{agent_id}"
        self.agent_id = agent_id
        self.redis = RedisFoundation(redis_config)
        self.poll_interval = poll_interval
        self.logger = logging.getLogger(f"mailbox.{agent_id}")
        self._consumer_group = f"{agent_id}:group"
        self._consumer_name = f"{agent_id}:{uuid4().hex[:6]}"
        self._processing_task: Optional[asyncio.Task] = None
        self._handlers: List[Callable[[MailboxMessage], Awaitable[None]]] = []
        self._running = False

    @property
    def inbox_stream(self) -> str:
        return f"{self.STREAM_PREFIX}:{self.agent_id}:in"

    async def start(self) -> bool:
        """Initialise Redis connection and begin consuming messages."""
        if not await self.redis.initialize():
            self.logger.error("Redis initialization failed")
            return False

        client = self.redis.client
        if client is None:
            self.logger.error("Redis client unavailable after initialization")
            return False

        try:
            await client.xgroup_create(
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
        await self.redis.shutdown()

    def register_handler(self, handler: Callable[[MailboxMessage], Awaitable[None]]) -> None:
        self._handlers.append(handler)

    async def send_message(
        self,
        recipient: str,
        payload: Dict[str, Any],
        message_type: str = "direct_message",
        message_id: Optional[str] = None,
    ) -> str:
        client = self.redis.client
        if not client:
            raise RuntimeError("Redis client not initialised")

        msg = MailboxMessage(
            message_id=message_id or str(uuid4()),
            sender=self.agent_id,
            recipient=recipient,
            payload=payload,
            message_type=message_type,
        )

        stream = f"{self.STREAM_PREFIX}:{recipient}:in"
        await client.xadd(stream, msg.to_redis_fields(), maxlen=1000, approximate=True)
        self.logger.debug("Sent message %s to %s", msg.message_id, stream)
        return msg.message_id

    async def _consume_loop(self) -> None:
        client = self.redis.client
        if not client:
            self.logger.error("Redis client missing for consume loop")
            return

        while self._running:
            try:
                response = await client.xreadgroup(
                    groupname=self._consumer_group,
                    consumername=self._consumer_name,
                    streams={self.inbox_stream: ">"},
                    count=10,
                    block=int(self.poll_interval * 1000),
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
                        await client.xack(stream_name, self._consumer_group, message_id)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.exception("Error in mailbox consume loop: %s", exc)
                await asyncio.sleep(self.poll_interval)

    async def _dispatch(self, message: MailboxMessage) -> None:
        if not self._handlers:
            self.logger.info(
                "Mailbox message received with no handlers registered: %s",
                message,
            )
            return

        for handler in list(self._handlers):
            try:
                await handler(message)
            except Exception as exc:
                self.logger.exception("Mailbox handler failed: %s", exc)

    # ------------------------------------------------------------------
    # ReflectiveModule interface
    # ------------------------------------------------------------------
    def get_module_info(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "agent_id": self.agent_id,
            "redis_host": getattr(self.redis.config, "host", "unknown"),
            "redis_port": getattr(self.redis.config, "port", "unknown"),
        }

    def get_capabilities(self) -> List[str]:
        return ["mailbox", "redis_streams", "durable_delivery"]

    def get_health_status(self) -> Dict[str, Any]:
        return {
            "module": self.module_id,
            "running": self._running,
            "handler_count": len(self._handlers),
            "connection_status": getattr(self.redis, "status", None).value
            if getattr(self.redis, "status", None)
            else "unknown",
        }

    def graceful_degradation(self) -> GracefulDegradationResult:
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=["mailbox"],
            remaining_capabilities=[],
            error_message="Redis mailbox operating in degraded mode",
        )
