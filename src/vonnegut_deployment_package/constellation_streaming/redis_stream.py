#!/usr/bin/env python3
"""
Redis-based Status Streaming for Constellation Execution

Publishes status updates to Redis pub/sub for real-time monitoring.
"""

import json
import redis
from typing import Dict, Optional
from datetime import datetime


class RedisStatusStream:
    """Streams constellation execution status via Redis pub/sub"""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        channel_prefix: str = "constellation",
    ):
        """
        Initialize Redis status stream.

        Args:
            redis_url: Redis connection URL
            channel_prefix: Prefix for Redis channels
        """
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.channel_prefix = channel_prefix

        # Channel names
        self.status_channel = f"{channel_prefix}:status"
        self.prompt_channel = f"{channel_prefix}:prompt"
        self.event_channel = f"{channel_prefix}:event"
        self.heartbeat_channel = f"{channel_prefix}:heartbeat"

    def publish_status(self, status: Dict):
        """
        Publish full status update.

        Args:
            status: Complete status dictionary
        """
        message = {
            "type": "status_update",
            "timestamp": datetime.now().isoformat(),
            "data": status,
        }
        self.redis_client.publish(self.status_channel, json.dumps(message))

    def publish_prompt_update(
        self,
        prompt_name: str,
        prompt_status: str,
        agent_id: Optional[str] = None,
        duration_min: Optional[float] = None,
        error: Optional[str] = None,
    ):
        """
        Publish individual prompt status update.

        Args:
            prompt_name: Name of the prompt
            prompt_status: Status (pending/running/completed/failed)
            agent_id: Agent executing the prompt
            duration_min: Execution duration in minutes
            error: Error message if failed
        """
        message = {
            "type": "prompt_update",
            "timestamp": datetime.now().isoformat(),
            "prompt_name": prompt_name,
            "status": prompt_status,
            "agent_id": agent_id,
            "duration_min": duration_min,
            "error": error,
        }
        self.redis_client.publish(self.prompt_channel, json.dumps(message))

    def publish_event(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict] = None,
    ):
        """
        Publish execution event.

        Args:
            event_type: Type of event (started/completed/error/info)
            message: Event message
            data: Optional event data
        """
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "data": data or {},
        }
        self.redis_client.publish(self.event_channel, json.dumps(event))

    def publish_heartbeat(self, execution_id: str, stats: Dict):
        """
        Publish heartbeat with execution statistics.

        Args:
            execution_id: Execution identifier
            stats: Execution statistics
        """
        heartbeat = {
            "type": "heartbeat",
            "timestamp": datetime.now().isoformat(),
            "execution_id": execution_id,
            "stats": stats,
        }
        self.redis_client.publish(self.heartbeat_channel, json.dumps(heartbeat))

    def subscribe_to_status(self):
        """
        Subscribe to status updates.

        Yields:
            Parsed status update messages
        """
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.status_channel)

        for message in pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])

    def subscribe_to_prompts(self):
        """
        Subscribe to prompt updates.

        Yields:
            Parsed prompt update messages
        """
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.prompt_channel)

        for message in pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])

    def subscribe_to_events(self):
        """
        Subscribe to execution events.

        Yields:
            Parsed event messages
        """
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.event_channel)

        for message in pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])

    def subscribe_to_all(self):
        """
        Subscribe to all channels.

        Yields:
            Parsed messages from all channels
        """
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(
            self.status_channel,
            self.prompt_channel,
            self.event_channel,
            self.heartbeat_channel,
        )

        for message in pubsub.listen():
            if message["type"] == "message":
                yield {
                    "channel": message["channel"],
                    "data": json.loads(message["data"]),
                }

    def get_latest_status(self) -> Optional[Dict]:
        """
        Get latest cached status from Redis.

        Returns:
            Latest status dictionary or None
        """
        status_key = f"{self.channel_prefix}:latest_status"
        data = self.redis_client.get(status_key)
        return json.loads(data) if data else None

    def cache_status(self, status: Dict, ttl: int = 3600):
        """
        Cache status in Redis for quick retrieval.

        Args:
            status: Status dictionary to cache
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        status_key = f"{self.channel_prefix}:latest_status"
        self.redis_client.setex(status_key, ttl, json.dumps(status))

    def close(self):
        """Close Redis connection"""
        self.redis_client.close()
