#!/usr/bin/env python3
"""Redis-backed mailbox service for Beast Mode network messaging."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional
from uuid import uuid4

from .redis_foundation import RedisFoundation, RedisConfig
from src.rm_ddd.core.unified_reflective_module import (
    GracefulDegradationResult,
    ModuleCapability,
    ModuleHealth,
    ModuleStatus,
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
    def from_redis_fields(cls, fields: Dict[Any, Any]) -> "MailboxMessage":
        decoded: Dict[str, str] = {}
        for key, value in fields.items():
            decoded_key = key.decode() if isinstance(key, bytes) else str(key)
            decoded_value = value.decode() if isinstance(value, bytes) else str(value)
            decoded[decoded_key] = decoded_value
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
        self.module_id = f"mailbox_service:{agent_id}"
        self.agent_id = agent_id
        self._redis_config = redis_config or RedisConfig()
        self._handlers: List[Callable[[MailboxMessage], Awaitable[None]]] = []
        self._running = False
        super().__init__()
        self.redis = RedisFoundation(self._redis_config)
        self.poll_interval = poll_interval
        self.logger = logging.getLogger(f"mailbox.{agent_id}")
        self._consumer_group = f"{agent_id}:group"
        self._consumer_name = f"{agent_id}:{uuid4().hex[:6]}"
        self._processing_task: Optional[asyncio.Task] = None

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
            "redis_host": getattr(self._redis_config, "host", "unknown"),
            "redis_port": getattr(self._redis_config, "port", "unknown"),
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING,
        ]

    def get_health_status(self) -> ModuleHealth:
        redis_foundation = getattr(self, "redis", None)
        redis_status = getattr(redis_foundation, "status", None)
        is_running = (
            self._running
            and redis_status is not None
            and getattr(redis_status, "value", "") == "connected"
        )
        status = ModuleStatus.HEALTHY if is_running else ModuleStatus.WARNING
        issues: List[str] = []
        if not self._running:
            issues.append("mailbox_not_running")
        if redis_status is None:
            issues.append("redis_status_unknown")
        elif redis_status.value != "connected":
            issues.append(f"redis_{redis_status.value}")

        uptime_seconds = (datetime.now() - getattr(self, "_start_time", datetime.now())).total_seconds()
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=1.0 if status == ModuleStatus.HEALTHY else 0.5,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime_seconds,
            error_count=0,
            warning_count=len(issues),
        )

    def graceful_degradation(self) -> GracefulDegradationResult:
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
            remaining_capabilities=[ModuleCapability.MONITORING],
            error_message="Redis mailbox operating in degraded mode",
        )
