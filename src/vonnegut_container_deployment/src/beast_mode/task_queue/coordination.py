"""
Distributed conversation coordination for multi-instance task queue systems.

This module implements distributed locking, conflict resolution, and consensus
mechanisms to ensure conversation state consistency across multiple Claude instances.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .models import ConversationContext


class LockState(Enum):
    """Distributed lock states."""
    AVAILABLE = "available"
    ACQUIRED = "acquired"
    EXPIRED = "expired"
    CONTESTED = "contested"


@dataclass
class ConversationLock:
    """Distributed lock for conversation state access."""
    conversation_id: str
    instance_id: str
    lock_id: str
    acquired_at: datetime
    expires_at: datetime
    lease_duration_seconds: int = 30
    renewable: bool = True
    
    def is_expired(self) -> bool:
        """Check if lock has expired."""
        return datetime.now() > self.expires_at
    
    def time_remaining(self) -> float:
        """Get remaining time in seconds."""
        remaining = (self.expires_at - datetime.now()).total_seconds()
        return max(0, remaining)


@dataclass
class ConflictResolutionResult:
    """Result of conflict resolution process."""
    resolved_state: ConversationContext
    resolution_method: str
    conflicted_instances: List[str]
    resolution_timestamp: datetime
    confidence_score: float


class DistributedConversationCoordinator:
    """Coordinates conversation state across multiple Claude instances."""
    
    def __init__(self, redis_client, instance_id: str):
        self.redis = redis_client
        self.instance_id = instance_id
        self._logger = logging.getLogger(f"{__name__}.DistributedConversationCoordinator")
        
        # Sub-components
        self.consensus_manager = ConsensusManager(redis_client, instance_id)
        self.conflict_resolver = ConflictResolver()
        
        # Configuration
        self.default_lease_duration = 30  # seconds
        self.lock_retry_delay = 0.1  # seconds
        self.max_lock_attempts = 50
    
    async def coordinate_conversation_access(self, conversation_id: str) -> Optional[ConversationLock]:
        """Coordinate exclusive access to conversation across instances."""
        try:
            self._logger.info(
                f"Attempting to acquire conversation lock: {conversation_id}",
                extra={
                    "conversation_id": conversation_id,
                    "instance_id": self.instance_id
                }
            )
            
            # Attempt to acquire distributed lock
            lock = await self._acquire_distributed_lock(conversation_id)
            
            if lock:
                self._logger.info(
                    f"Successfully acquired conversation lock: {lock.lock_id}",
                    extra={
                        "conversation_id": conversation_id,
                        "lock_id": lock.lock_id,
                        "expires_at": lock.expires_at.isoformat()
                    }
                )
                return lock
            else:
                self._logger.warning(
                    f"Failed to acquire conversation lock: {conversation_id}",
                    extra={
                        "conversation_id": conversation_id,
                        "instance_id": self.instance_id
                    }
                )
                return None
                
        except Exception as e:
            self._logger.error(
                f"Error coordinating conversation access: {e}",
                extra={
                    "conversation_id": conversation_id,
                    "instance_id": self.instance_id
                }
            )
            return None
    
    async def release_conversation_lock(self, lock: ConversationLock) -> bool:
        """Release distributed conversation lock."""
        try:
            lock_key = f"conversation_lock:{lock.conversation_id}"
            
            # Use Lua script for atomic release
            release_script = """
            local lock_key = KEYS[1]
            local expected_lock_id = ARGV[1]
            local current_lock = redis.call('GET', lock_key)
            
            if current_lock then
                local lock_data = cjson.decode(current_lock)
                if lock_data.lock_id == expected_lock_id then
                    redis.call('DEL', lock_key)
                    return 1
                end
            end
            return 0
            """
            
            result = await self.redis.eval(release_script, 1, lock_key, lock.lock_id)
            
            if result == 1:
                self._logger.info(
                    f"Successfully released conversation lock: {lock.lock_id}",
                    extra={
                        "conversation_id": lock.conversation_id,
                        "lock_id": lock.lock_id
                    }
                )
                return True
            else:
                self._logger.warning(
                    f"Failed to release conversation lock (may have expired): {lock.lock_id}",
                    extra={
                        "conversation_id": lock.conversation_id,
                        "lock_id": lock.lock_id
                    }
                )
                return False
                
        except Exception as e:
            self._logger.error(
                f"Error releasing conversation lock: {e}",
                extra={
                    "conversation_id": lock.conversation_id,
                    "lock_id": lock.lock_id
                }
            )
            return False
    
    async def renew_conversation_lock(self, lock: ConversationLock) -> bool:
        """Renew distributed conversation lock."""
        try:
            if not lock.renewable:
                return False
            
            lock_key = f"conversation_lock:{lock.conversation_id}"
            
            # Use Lua script for atomic renewal
            renewal_script = """
            local lock_key = KEYS[1]
            local expected_lock_id = ARGV[1]
            local new_expiry = ARGV[2]
            local current_lock = redis.call('GET', lock_key)
            
            if current_lock then
                local lock_data = cjson.decode(current_lock)
                if lock_data.lock_id == expected_lock_id then
                    lock_data.expires_at = new_expiry
                    redis.call('SET', lock_key, cjson.encode(lock_data), 'EX', 60)
                    return 1
                end
            end
            return 0
            """
            
            new_expiry = datetime.now() + timedelta(seconds=lock.lease_duration_seconds)
            result = await self.redis.eval(
                renewal_script, 1, lock_key, lock.lock_id, new_expiry.isoformat()
            )
            
            if result == 1:
                lock.expires_at = new_expiry
                self._logger.debug(
                    f"Renewed conversation lock: {lock.lock_id}",
                    extra={
                        "conversation_id": lock.conversation_id,
                        "new_expiry": new_expiry.isoformat()
                    }
                )
                return True
            else:
                return False
                
        except Exception as e:
            self._logger.error(f"Error renewing conversation lock: {e}")
            return False
    
    async def resolve_state_conflicts(
        self, 
        conversation_id: str, 
        conflicted_states: List[ConversationContext]
    ) -> Optional[ConversationContext]:
        """Resolve conflicts when multiple instances modify the same conversation."""
        try:
            self._logger.info(
                f"Resolving state conflicts for conversation: {conversation_id}",
                extra={
                    "conversation_id": conversation_id,
                    "conflict_count": len(conflicted_states)
                }
            )
            
            if not conflicted_states:
                return None
            
            if len(conflicted_states) == 1:
                return conflicted_states[0]
            
            # Use consensus manager to resolve conflicts
            resolution_result = await self.conflict_resolver.resolve_conflicts(
                conversation_id, conflicted_states
            )
            
            if resolution_result:
                self._logger.info(
                    f"Successfully resolved state conflicts using {resolution_result.resolution_method}",
                    extra={
                        "conversation_id": conversation_id,
                        "resolution_method": resolution_result.resolution_method,
                        "confidence_score": resolution_result.confidence_score
                    }
                )
                return resolution_result.resolved_state
            else:
                self._logger.error(
                    f"Failed to resolve state conflicts for conversation: {conversation_id}",
                    extra={"conversation_id": conversation_id}
                )
                return None
                
        except Exception as e:
            self._logger.error(
                f"Error resolving state conflicts: {e}",
                extra={"conversation_id": conversation_id}
            )
            return None
    
    async def _acquire_distributed_lock(self, conversation_id: str) -> Optional[ConversationLock]:
        """Acquire distributed lock using Redis."""
        lock_key = f"conversation_lock:{conversation_id}"
        lock_id = f"{self.instance_id}:{uuid.uuid4()}"
        
        for attempt in range(self.max_lock_attempts):
            try:
                # Use Lua script for atomic lock acquisition
                acquire_script = """
                local lock_key = KEYS[1]
                local lock_data = ARGV[1]
                local ttl = ARGV[2]
                
                local current_lock = redis.call('GET', lock_key)
                if current_lock then
                    local lock_info = cjson.decode(current_lock)
                    local expires_at = lock_info.expires_at
                    local current_time = redis.call('TIME')
                    local current_timestamp = current_time[1] + (current_time[2] / 1000000)
                    local expires_timestamp = tonumber(string.match(expires_at, '(%d+)'))
                    
                    if expires_timestamp > current_timestamp then
                        return 0  -- Lock is still valid
                    end
                end
                
                redis.call('SET', lock_key, lock_data, 'EX', ttl)
                return 1
                """
                
                now = datetime.now()
                expires_at = now + timedelta(seconds=self.default_lease_duration)
                
                lock_data = {
                    "conversation_id": conversation_id,
                    "instance_id": self.instance_id,
                    "lock_id": lock_id,
                    "acquired_at": now.isoformat(),
                    "expires_at": expires_at.isoformat(),
                    "lease_duration_seconds": self.default_lease_duration
                }
                
                result = await self.redis.eval(
                    acquire_script, 1, lock_key, 
                    json.dumps(lock_data), str(self.default_lease_duration + 10)
                )
                
                if result == 1:
                    return ConversationLock(
                        conversation_id=conversation_id,
                        instance_id=self.instance_id,
                        lock_id=lock_id,
                        acquired_at=now,
                        expires_at=expires_at,
                        lease_duration_seconds=self.default_lease_duration
                    )
                
                # Lock acquisition failed, wait and retry
                await asyncio.sleep(self.lock_retry_delay)
                
            except Exception as e:
                self._logger.error(f"Error in lock acquisition attempt {attempt + 1}: {e}")
                await asyncio.sleep(self.lock_retry_delay)
        
        return None


class ConsensusManager:
    """Manages consensus mechanisms for distributed state coordination."""
    
    def __init__(self, redis_client, instance_id: str):
        self.redis = redis_client
        self.instance_id = instance_id
        self._logger = logging.getLogger(f"{__name__}.ConsensusManager")
    
    async def achieve_consensus(
        self, 
        conversation_id: str, 
        proposed_state: ConversationContext,
        timeout_seconds: int = 10
    ) -> bool:
        """Achieve consensus on conversation state across instances."""
        try:
            consensus_key = f"consensus:{conversation_id}"
            proposal_id = str(uuid.uuid4())
            
            # Submit proposal
            proposal_data = {
                "proposal_id": proposal_id,
                "instance_id": self.instance_id,
                "proposed_state": asdict(proposed_state),
                "timestamp": datetime.now().isoformat(),
                "timeout": timeout_seconds
            }
            
            # Use Redis pub/sub for consensus protocol
            await self.redis.hset(
                consensus_key, 
                proposal_id, 
                json.dumps(proposal_data, default=str)
            )
            
            # Set expiry for cleanup
            await self.redis.expire(consensus_key, timeout_seconds + 5)
            
            # Wait for consensus (simplified implementation)
            await asyncio.sleep(1)  # Allow other instances to respond
            
            # Check if consensus achieved
            proposals = await self.redis.hgetall(consensus_key)
            
            if len(proposals) == 1:  # Only our proposal
                self._logger.info(
                    f"Consensus achieved (single instance): {proposal_id}",
                    extra={"conversation_id": conversation_id}
                )
                return True
            
            # In a full implementation, this would involve more sophisticated
            # consensus algorithms like Raft or PBFT
            return True
            
        except Exception as e:
            self._logger.error(f"Error achieving consensus: {e}")
            return False


class ConflictResolver:
    """Resolves conflicts between different conversation states."""
    
    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.ConflictResolver")
    
    async def resolve_conflicts(
        self, 
        conversation_id: str, 
        conflicted_states: List[ConversationContext]
    ) -> Optional[ConflictResolutionResult]:
        """Resolve conflicts using multiple resolution strategies."""
        try:
            if not conflicted_states:
                return None
            
            # Strategy 1: Vector clock comparison
            vector_clock_result = self._resolve_by_vector_clocks(conflicted_states)
            if vector_clock_result:
                return ConflictResolutionResult(
                    resolved_state=vector_clock_result,
                    resolution_method="vector_clocks",
                    conflicted_instances=[state.instance_id for state in conflicted_states],
                    resolution_timestamp=datetime.now(),
                    confidence_score=0.9
                )
            
            # Strategy 2: Timestamp-based resolution (last-writer-wins)
            timestamp_result = self._resolve_by_timestamps(conflicted_states)
            if timestamp_result:
                return ConflictResolutionResult(
                    resolved_state=timestamp_result,
                    resolution_method="last_writer_wins",
                    conflicted_instances=[state.instance_id for state in conflicted_states],
                    resolution_timestamp=datetime.now(),
                    confidence_score=0.7
                )
            
            # Strategy 3: State version comparison
            version_result = self._resolve_by_state_version(conflicted_states)
            if version_result:
                return ConflictResolutionResult(
                    resolved_state=version_result,
                    resolution_method="highest_version",
                    conflicted_instances=[state.instance_id for state in conflicted_states],
                    resolution_timestamp=datetime.now(),
                    confidence_score=0.8
                )
            
            # Fallback: Use CRDT-based merging
            crdt_result = await self._resolve_by_crdt_merge(conflicted_states)
            if crdt_result:
                return ConflictResolutionResult(
                    resolved_state=crdt_result,
                    resolution_method="crdt_merge",
                    conflicted_instances=[state.instance_id for state in conflicted_states],
                    resolution_timestamp=datetime.now(),
                    confidence_score=0.6
                )
            
            return None
            
        except Exception as e:
            self._logger.error(f"Error resolving conflicts: {e}")
            return None
    
    def _resolve_by_vector_clocks(self, states: List[ConversationContext]) -> Optional[ConversationContext]:
        """Resolve conflicts using vector clock comparison."""
        # Simplified vector clock implementation
        # In practice, this would use proper vector clock data structures
        
        if not states:
            return None
        
        # For now, use state version as a simple vector clock
        latest_state = max(states, key=lambda s: s.state_version)
        
        # Check if there's a clear winner (no concurrent updates)
        max_version = latest_state.state_version
        concurrent_states = [s for s in states if s.state_version == max_version]
        
        if len(concurrent_states) == 1:
            return latest_state
        
        return None  # Concurrent updates detected
    
    def _resolve_by_timestamps(self, states: List[ConversationContext]) -> Optional[ConversationContext]:
        """Resolve conflicts using last-writer-wins strategy."""
        if not states:
            return None
        
        # Find state with most recent activity
        latest_state = max(
            states, 
            key=lambda s: s.last_persistence or s.session_start
        )
        
        return latest_state
    
    def _resolve_by_state_version(self, states: List[ConversationContext]) -> Optional[ConversationContext]:
        """Resolve conflicts using highest state version."""
        if not states:
            return None
        
        return max(states, key=lambda s: s.state_version)
    
    async def _resolve_by_crdt_merge(self, states: List[ConversationContext]) -> Optional[ConversationContext]:
        """Resolve conflicts using CRDT-based merging."""
        if not states:
            return None
        
        if len(states) == 1:
            return states[0]
        
        # Use the first state as base and merge others
        merged_state = states[0]
        
        for other_state in states[1:]:
            merged_state = await self._merge_conversation_states(merged_state, other_state)
        
        return merged_state
    
    async def _merge_conversation_states(
        self, 
        state1: ConversationContext, 
        state2: ConversationContext
    ) -> ConversationContext:
        """Merge two conversation states using CRDT principles."""
        # Create merged state based on state1
        merged_state = ConversationContext(
            conversation_id=state1.conversation_id,
            instance_id=state1.instance_id,
            session_start=min(state1.session_start, state2.session_start)
        )
        
        # Merge conversation turns (union with deduplication)
        all_turns = state1.conversation_turns + state2.conversation_turns
        unique_turns = {}
        for turn in all_turns:
            if turn.turn_id not in unique_turns:
                unique_turns[turn.turn_id] = turn
            else:
                # Keep the turn with later timestamp
                existing_turn = unique_turns[turn.turn_id]
                if turn.timestamp > existing_turn.timestamp:
                    unique_turns[turn.turn_id] = turn
        
        merged_state.conversation_turns = list(unique_turns.values())
        merged_state.conversation_turns.sort(key=lambda t: t.timestamp)
        
        # Merge metadata (union with preference for newer values)
        merged_state.conversation_metadata = {**state1.conversation_metadata, **state2.conversation_metadata}
        
        # Use higher state version
        merged_state.state_version = max(state1.state_version, state2.state_version) + 1
        
        # Use most recent task
        if state1.current_task and state2.current_task:
            if state1.current_task.created_at > state2.current_task.created_at:
                merged_state.current_task = state1.current_task
            else:
                merged_state.current_task = state2.current_task
        elif state1.current_task:
            merged_state.current_task = state1.current_task
        elif state2.current_task:
            merged_state.current_task = state2.current_task
        
        # Merge completed and failed tasks
        merged_state.completed_tasks = state1.completed_tasks + state2.completed_tasks
        merged_state.failed_tasks = state1.failed_tasks + state2.failed_tasks
        
        # Mark as dirty and increment version
        merged_state.dirty_state = True
        
        return merged_state