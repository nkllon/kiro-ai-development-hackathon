"""
Shared State Core Core

This module was extracted from shared_state_core.py
as part of RM-DDD compliance refactoring.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import redis.asyncio as redis


@dataclass
class SharedStateConfig:
    """Configuration for shared state management"""

    redis_url: str = "redis://localhost:6379"
    key_prefix: str = "beast_mode"
    ttl_seconds: int = 3600
    max_spore_size: int = 1024 * 1024


class BeastModeSharedState:
    """
    Manages shared state in Redis regardless of transport choice.

    Provides fast collaborative state access for:
    - Agent state and capabilities
    - Spore storage and metadata
    - Collaboration sessions
    - Performance metrics
    """

    def __init__(self, config: Optional[SharedStateConfig] = None):
        """Initialize shared state manager"""
        self.config = config or SharedStateConfig()
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)
        if not REDIS_AVAILABLE:
            self.logger.error(
                "Redis not available - install with: uv add redis[hiredis]"
            )

    async def initialize(self) -> bool:
        """Initialize Redis connection for shared state"""
        if not REDIS_AVAILABLE:
            return False
        try:
            self.redis_client = redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            self.logger.info("Shared state manager connected to Redis")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            return False

    async def update_agent_state(self, agent_id: str, state: Dict[str, Any]) -> bool:
        """
        Update agent state in shared model.

        Args:
            agent_id: Unique agent identifier
            state: Agent state data

        Returns:
            True if updated successfully
        """
        if not self.redis_client:
            return False
        try:
            key = f"{self.config.key_prefix}:agents:{agent_id}"
            state_with_timestamp = {
                **state,
                "last_updated": datetime.now().isoformat(),
                "agent_id": agent_id,
            }
            await self.redis_client.hset(key, mapping=state_with_timestamp)
            await self.redis_client.expire(key, self.config.ttl_seconds)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update agent state for {agent_id}: {e}")
            return False

    async def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent state from shared model.

        Args:
            agent_id: Unique agent identifier

        Returns:
            Agent state data or None if not found
        """
        if not self.redis_client:
            return None
        try:
            key = f"{self.config.key_prefix}:agents:{agent_id}"
            state = await self.redis_client.hgetall(key)
            if not state:
                return None
            return self._deserialize_state(state)
        except Exception as e:
            self.logger.error(f"Failed to get agent state for {agent_id}: {e}")
            return None

    async def get_active_agents(self) -> List[str]:
        """
        Get list of currently active agents.

        Returns:
            List of active agent IDs
        """
        if not self.redis_client:
            return []
        try:
            pattern = f"{self.config.key_prefix}:agents:*"
            keys = await self.redis_client.keys(pattern)
            agent_ids = []
            for key in keys:
                if isinstance(key, bytes):
                    key = key.decode("utf-8")
                agent_id = key.split(":")[-1]
                agent_ids.append(agent_id)
            return agent_ids
        except Exception as e:
            self.logger.error(f"Failed to get active agents: {e}")
            return []

    async def remove_agent_state(self, agent_id: str) -> bool:
        """
        Remove agent state from shared model.

        Args:
            agent_id: Agent to remove

        Returns:
            True if removed successfully
        """
        if not self.redis_client:
            return False
        try:
            key = f"{self.config.key_prefix}:agents:{agent_id}"
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove agent state for {agent_id}: {e}")
            return False

    async def store_spore(self, spore_id: str, spore_data: Dict[str, Any]) -> bool:
        """
        Store spore in shared model.

        Args:
            spore_id: Unique spore identifier
            spore_data: Spore data and metadata

        Returns:
            True if stored successfully
        """
        if not self.redis_client:
            return False
        try:
            spore_json = json.dumps(spore_data)
            if len(spore_json.encode("utf-8")) > self.config.max_spore_size:
                self.logger.error(f"Spore {spore_id} exceeds max size limit")
                return False
            key = f"{self.config.key_prefix}:spores:{spore_id}"
            spore_with_metadata = {
                **spore_data,
                "spore_id": spore_id,
                "stored_at": datetime.now().isoformat(),
                "size_bytes": len(spore_json.encode("utf-8")),
            }
            await self.redis_client.set(key, json.dumps(spore_with_metadata))
            await self.redis_client.expire(key, self.config.ttl_seconds * 24)
            return True
        except Exception as e:
            self.logger.error(f"Failed to store spore {spore_id}: {e}")
            return False

    async def get_spore(self, spore_id: str) -> Optional[Dict[str, Any]]:
        """
        Get spore from shared model.

        Args:
            spore_id: Spore identifier

        Returns:
            Spore data or None if not found
        """
        if not self.redis_client:
            return None
        try:
            key = f"{self.config.key_prefix}:spores:{spore_id}"
            spore_json = await self.redis_client.get(key)
            if not spore_json:
                return None
            return json.loads(spore_json)
        except Exception as e:
            self.logger.error(f"Failed to get spore {spore_id}: {e}")
            return None

    async def list_spores(self, pattern: str = "*") -> List[str]:
        """
        List available spores matching pattern.

        Args:
            pattern: Pattern to match spore IDs

        Returns:
            List of matching spore IDs
        """
        if not self.redis_client:
            return []
        try:
            key_pattern = f"{self.config.key_prefix}:spores:{pattern}"
            keys = await self.redis_client.keys(key_pattern)
            spore_ids = []
            for key in keys:
                if isinstance(key, bytes):
                    key = key.decode("utf-8")
                spore_id = key.split(":")[-1]
                spore_ids.append(spore_id)
            return spore_ids
        except Exception as e:
            self.logger.error(f"Failed to list spores: {e}")
            return []

    async def create_collaboration_session(
        self, session_id: str, session_data: Dict[str, Any]
    ) -> bool:
        """
        Create collaboration session in shared state.

        Args:
            session_id: Unique session identifier
            session_data: Session configuration and metadata

        Returns:
            True if created successfully
        """
        if not self.redis_client:
            return False
        try:
            key = f"{self.config.key_prefix}:sessions:{session_id}"
            session_with_metadata = {
                **session_data,
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "status": "active",
            }
            await self.redis_client.hset(key, mapping=session_with_metadata)
            await self.redis_client.expire(key, self.config.ttl_seconds * 8)
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to create collaboration session {session_id}: {e}"
            )
            return False

    async def update_collaboration_session(
        self, session_id: str, updates: Dict[str, Any]
    ) -> bool:
        """
        Update collaboration session state.

        Args:
            session_id: Session identifier
            updates: Fields to update

        Returns:
            True if updated successfully
        """
        if not self.redis_client:
            return False
        try:
            key = f"{self.config.key_prefix}:sessions:{session_id}"
            updates_with_timestamp = {
                **updates,
                "last_updated": datetime.now().isoformat(),
            }
            await self.redis_client.hset(key, mapping=updates_with_timestamp)
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to update collaboration session {session_id}: {e}"
            )
            return False

    async def get_collaboration_session(
        self, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get collaboration session state.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found
        """
        if not self.redis_client:
            return None
        try:
            key = f"{self.config.key_prefix}:sessions:{session_id}"
            session = await self.redis_client.hgetall(key)
            if not session:
                return None
            return self._deserialize_state(session)
        except Exception as e:
            self.logger.error(f"Failed to get collaboration session {session_id}: {e}")
            return None

    async def end_collaboration_session(self, session_id: str) -> bool:
        """
        End collaboration session.

        Args:
            session_id: Session to end

        Returns:
            True if ended successfully
        """
        if not self.redis_client:
            return False
        try:
            await self.update_collaboration_session(
                session_id, {"status": "ended", "ended_at": datetime.now().isoformat()}
            )
            key = f"{self.config.key_prefix}:sessions:{session_id}"
            await self.redis_client.expire(key, 3600)
            return True
        except Exception as e:
            self.logger.error(f"Failed to end collaboration session {session_id}: {e}")
            return False

    async def increment_counter(
        self, counter_name: str, agent_id: str, amount: int = 1
    ) -> int:
        """
        Increment performance counter.

        Args:
            counter_name: Name of counter (e.g., 'messages_sent')
            agent_id: Agent the counter belongs to
            amount: Amount to increment by

        Returns:
            New counter value
        """
        if not self.redis_client:
            return 0
        try:
            key = f"{self.config.key_prefix}:metrics:{agent_id}:{counter_name}"
            new_value = await self.redis_client.incrby(key, amount)
            await self.redis_client.expire(key, self.config.ttl_seconds)
            return new_value
        except Exception as e:
            self.logger.error(
                f"Failed to increment counter {counter_name} for {agent_id}: {e}"
            )
            return 0

    async def get_metrics(self, agent_id: str) -> Dict[str, int]:
        """
        Get performance metrics for agent.

        Args:
            agent_id: Agent to get metrics for

        Returns:
            Dictionary of metric name -> value
        """
        if not self.redis_client:
            return {}
        try:
            pattern = f"{self.config.key_prefix}:metrics:{agent_id}:*"
            keys = await self.redis_client.keys(pattern)
            metrics = {}
            for key in keys:
                if isinstance(key, bytes):
                    key = key.decode("utf-8")
                metric_name = key.split(":")[-1]
                value = await self.redis_client.get(key)
                if value:
                    metrics[metric_name] = int(value)
            return metrics
        except Exception as e:
            self.logger.error(f"Failed to get metrics for {agent_id}: {e}")
            return {}

    def _deserialize_state(self, redis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Redis string values back to appropriate Python types"""
        result = {}
        for key, value in redis_data.items():
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            if isinstance(value, str) and (
                value.startswith("{") or value.startswith("[")
            ):
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value
            else:
                result[key] = value
        return result

    async def get_connection_status(self) -> Dict[str, Any]:
        """Get shared state connection status"""
        if not self.redis_client:
            return {"connected": False, "error": "Redis client not initialized"}
        try:
            await self.redis_client.ping()
            return {
                "connected": True,
                "redis_url": self.config.redis_url,
                "key_prefix": self.config.key_prefix,
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data and return cleanup stats"""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        try:
            agent_count = len(await self.get_active_agents())
            spore_count = len(await self.list_spores())
            return {
                "active_agents": agent_count,
                "stored_spores": spore_count,
                "cleanup_method": "automatic_ttl",
            }
        except Exception as e:
            self.logger.error(f"Failed to get cleanup stats: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Gracefully shutdown shared state manager"""
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info("Shared state manager shutdown complete")


def __init__(self, config: Optional[SharedStateConfig] = None):
    """Initialize shared state manager"""
    self.config = config or SharedStateConfig()
    self.redis_client: Optional[redis.Redis] = None
    self.logger = logging.getLogger(__name__)
    if not REDIS_AVAILABLE:
        self.logger.error("Redis not available - install with: uv add redis[hiredis]")


def _deserialize_state(self, redis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Redis string values back to appropriate Python types"""
    result = {}
    for key, value in redis_data.items():
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, str) and (value.startswith("{") or value.startswith("[")):
            try:
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                result[key] = value
        else:
            result[key] = value
    return result


def __init__(self, config: Optional[SharedStateConfig] = None):
    """Initialize shared state manager"""
    self.config = config or SharedStateConfig()
    self.redis_client: Optional[redis.Redis] = None
    self.logger = logging.getLogger(__name__)
    if not REDIS_AVAILABLE:
        self.logger.error("Redis not available - install with: uv add redis[hiredis]")


def _deserialize_state(self, redis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Redis string values back to appropriate Python types"""
    result = {}
    for key, value in redis_data.items():
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, str) and (value.startswith("{") or value.startswith("[")):
            try:
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                result[key] = value
        else:
            result[key] = value
    return result
