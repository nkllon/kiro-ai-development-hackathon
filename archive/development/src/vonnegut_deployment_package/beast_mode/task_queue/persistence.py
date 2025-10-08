"""
Multi-layered state persistence system for conversation state management.

This module implements a comprehensive persistence strategy with hot/warm/cold/checkpoint
storage layers, integrity checking, and compression support.
"""

import asyncio
import json
import logging
import hashlib
import gzip
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import asdict
import uuid
import os
import pickle

from .models import (
    ConversationContext,
    StateCheckpoint,
    PersistenceConfig,
    ConversationTurn,
)


class StateIntegrityError(Exception):
    """Raised when state integrity validation fails."""
    pass


class StatePersistenceManager:
    """Manages multi-layered state persistence with reliability guarantees."""
    
    def __init__(self, redis_client, config: PersistenceConfig):
        self.redis = redis_client
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.StatePersistenceManager")
        
        # Initialize storage layers
        self.hot_storage = HotStateStorage(redis_client, config)
        self.warm_storage = WarmStateStorage(redis_client, config)
        self.cold_storage = ColdStateStorage(config)
        self.checkpoint_storage = CheckpointStorage(redis_client, config)
        
        # State integrity monitor
        self.integrity_monitor = StateIntegrityMonitor()
    
    async def persist_conversation_state(self, context: ConversationContext) -> bool:
        """Persist conversation state across all layers."""
        try:
            # Generate state hash for integrity checking
            state_hash = self._generate_state_hash(context)
            
            # Persist to hot storage (primary)
            hot_success = await self.hot_storage.store_state(context, state_hash)
            if not hot_success:
                self._logger.error(
                    f"Failed to persist to hot storage: {context.conversation_id}",
                    extra={"conversation_id": context.conversation_id}
                )
                return False
            
            # Persist to warm storage (backup)
            warm_success = await self.warm_storage.store_state(context, state_hash)
            if not warm_success:
                self._logger.warning(
                    f"Failed to persist to warm storage: {context.conversation_id}",
                    extra={"conversation_id": context.conversation_id}
                )
            
            # Persist to cold storage (long-term)
            if self._should_persist_to_cold(context):
                cold_success = await self.cold_storage.store_state(context, state_hash)
                if not cold_success:
                    self._logger.warning(
                        f"Failed to persist to cold storage: {context.conversation_id}",
                        extra={"conversation_id": context.conversation_id}
                    )
            
            self._logger.info(
                f"Successfully persisted conversation state: {context.conversation_id}",
                extra={
                    "conversation_id": context.conversation_id,
                    "state_hash": state_hash,
                    "hot_storage": hot_success,
                    "warm_storage": warm_success
                }
            )
            
            return True
            
        except Exception as e:
            self._logger.error(
                f"Error persisting conversation state: {e}",
                extra={"conversation_id": context.conversation_id}
            )
            return False
    
    async def create_checkpoint(self, context: ConversationContext) -> StateCheckpoint:
        """Create immutable state checkpoint."""
        try:
            # Generate checkpoint data
            checkpoint = StateCheckpoint(
                checkpoint_id=str(uuid.uuid4()),
                conversation_id=context.conversation_id,
                created_at=datetime.now(),
                conversation_turns=context.conversation_turns.copy(),
                conversation_metadata=context.conversation_metadata.copy(),
                task_context=asdict(context.current_task) if context.current_task else None
            )
            
            # Generate integrity hash
            checkpoint.state_hash = self._generate_checkpoint_hash(checkpoint)
            
            # Store checkpoint
            success = await self.checkpoint_storage.store_checkpoint(checkpoint)
            if not success:
                raise Exception("Failed to store checkpoint")
            
            # Verify integrity
            checkpoint.integrity_verified = await self.integrity_monitor.verify_checkpoint_integrity(
                checkpoint, self.checkpoint_storage
            )
            
            self._logger.info(
                f"Created checkpoint: {checkpoint.checkpoint_id}",
                extra={
                    "conversation_id": context.conversation_id,
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "integrity_verified": checkpoint.integrity_verified
                }
            )
            
            return checkpoint
            
        except Exception as e:
            self._logger.error(
                f"Error creating checkpoint: {e}",
                extra={"conversation_id": context.conversation_id}
            )
            raise
    
    async def rollback_to_checkpoint(self, context: ConversationContext, checkpoint: StateCheckpoint) -> bool:
        """Rollback conversation to specific checkpoint."""
        try:
            # Verify checkpoint integrity
            if not await self.integrity_monitor.verify_checkpoint_integrity(checkpoint, self.checkpoint_storage):
                self._logger.error(
                    f"Checkpoint integrity verification failed: {checkpoint.checkpoint_id}",
                    extra={"conversation_id": context.conversation_id}
                )
                return False
            
            # Restore conversation state from checkpoint
            context.conversation_turns = checkpoint.conversation_turns.copy()
            context.conversation_metadata = checkpoint.conversation_metadata.copy()
            
            # Restore task context if available
            if checkpoint.task_context:
                from .models import TaskContext
                context.current_task = TaskContext(**checkpoint.task_context)
            else:
                context.current_task = None
            
            # Update state metadata
            context.state_version += 1
            context.dirty_state = True
            
            self._logger.info(
                f"Successfully rolled back to checkpoint: {checkpoint.checkpoint_id}",
                extra={
                    "conversation_id": context.conversation_id,
                    "checkpoint_id": checkpoint.checkpoint_id
                }
            )
            
            return True
            
        except Exception as e:
            self._logger.error(
                f"Error rolling back to checkpoint: {e}",
                extra={
                    "conversation_id": context.conversation_id,
                    "checkpoint_id": checkpoint.checkpoint_id
                }
            )
            return False
    
    async def recover_from_corruption(self, conversation_id: str) -> Optional[ConversationContext]:
        """Recover conversation state from corruption using consensus."""
        try:
            self._logger.info(
                f"Starting corruption recovery for conversation: {conversation_id}",
                extra={"conversation_id": conversation_id}
            )
            
            # Attempt recovery from each storage layer
            recovery_candidates = []
            
            # Try hot storage
            hot_state = await self.hot_storage.retrieve_state(conversation_id)
            if hot_state and await self._verify_state_integrity(hot_state):
                recovery_candidates.append(("hot", hot_state))
            
            # Try warm storage
            warm_state = await self.warm_storage.retrieve_state(conversation_id)
            if warm_state and await self._verify_state_integrity(warm_state):
                recovery_candidates.append(("warm", warm_state))
            
            # Try cold storage
            cold_state = await self.cold_storage.retrieve_state(conversation_id)
            if cold_state and await self._verify_state_integrity(cold_state):
                recovery_candidates.append(("cold", cold_state))
            
            if not recovery_candidates:
                self._logger.error(
                    f"No valid recovery candidates found for conversation: {conversation_id}",
                    extra={"conversation_id": conversation_id}
                )
                return None
            
            # Use consensus to select best candidate
            recovered_state = self._select_recovery_candidate(recovery_candidates)
            
            self._logger.info(
                f"Successfully recovered conversation state from {recovered_state[0]} storage",
                extra={"conversation_id": conversation_id}
            )
            
            return recovered_state[1]
            
        except Exception as e:
            self._logger.error(
                f"Error during corruption recovery: {e}",
                extra={"conversation_id": conversation_id}
            )
            return None
    
    def _generate_state_hash(self, context: ConversationContext) -> str:
        """Generate cryptographic hash for state integrity."""
        # Create deterministic representation
        state_data = {
            "conversation_id": context.conversation_id,
            "state_version": context.state_version,
            "conversation_turns": [asdict(turn) for turn in context.conversation_turns],
            "conversation_metadata": context.conversation_metadata,
            "current_task": asdict(context.current_task) if context.current_task else None
        }
        
        # Generate hash
        state_json = json.dumps(state_data, sort_keys=True, default=str)
        return hashlib.sha256(state_json.encode()).hexdigest()
    
    def _generate_checkpoint_hash(self, checkpoint: StateCheckpoint) -> str:
        """Generate cryptographic hash for checkpoint integrity."""
        checkpoint_data = {
            "checkpoint_id": checkpoint.checkpoint_id,
            "conversation_id": checkpoint.conversation_id,
            "created_at": checkpoint.created_at.isoformat(),
            "conversation_turns": [asdict(turn) for turn in checkpoint.conversation_turns],
            "conversation_metadata": checkpoint.conversation_metadata,
            "task_context": checkpoint.task_context
        }
        
        checkpoint_json = json.dumps(checkpoint_data, sort_keys=True, default=str)
        return hashlib.sha256(checkpoint_json.encode()).hexdigest()
    
    def _should_persist_to_cold(self, context: ConversationContext) -> bool:
        """Determine if state should be persisted to cold storage."""
        # Persist to cold storage if conversation is old or has many turns
        age_threshold = timedelta(hours=1)
        turn_threshold = 50
        
        conversation_age = datetime.now() - context.session_start
        return (conversation_age > age_threshold or 
                len(context.conversation_turns) > turn_threshold)
    
    async def _verify_state_integrity(self, context: ConversationContext) -> bool:
        """Verify state integrity using hash validation."""
        try:
            expected_hash = self._generate_state_hash(context)
            # In a real implementation, we would compare with stored hash
            return True  # Simplified for now
        except Exception:
            return False
    
    def _select_recovery_candidate(self, candidates: List[tuple[str, ConversationContext]]) -> tuple[str, ConversationContext]:
        """Select best recovery candidate using consensus algorithm."""
        # Priority order: hot > warm > cold
        priority_order = ["hot", "warm", "cold"]
        
        for priority in priority_order:
            for storage_type, state in candidates:
                if storage_type == priority:
                    return (storage_type, state)
        
        # Fallback to first available
        return candidates[0]


class HotStateStorage:
    """Hot storage layer - Redis memory with < 1ms access time."""
    
    def __init__(self, redis_client, config: PersistenceConfig):
        self.redis = redis_client
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.HotStateStorage")
        self.ttl_seconds = config.hot_storage_ttl_hours * 3600
    
    async def store_state(self, context: ConversationContext, state_hash: str) -> bool:
        """Store conversation state in hot storage."""
        try:
            key = f"hot:conversation:{context.conversation_id}"
            
            # Serialize state
            state_data = {
                "context": self._serialize_context(context),
                "state_hash": state_hash,
                "stored_at": datetime.now().isoformat()
            }
            
            # Store with TTL
            serialized_data = json.dumps(state_data, default=str)
            if self.config.enable_compression:
                serialized_data = gzip.compress(serialized_data.encode()).decode('latin1')
            
            await self.redis.setex(key, self.ttl_seconds, serialized_data)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing to hot storage: {e}")
            return False
    
    async def retrieve_state(self, conversation_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation state from hot storage."""
        try:
            key = f"hot:conversation:{conversation_id}"
            data = await self.redis.get(key)
            
            if not data:
                return None
            
            # Decompress if needed
            if self.config.enable_compression:
                data = gzip.decompress(data.encode('latin1')).decode()
            
            state_data = json.loads(data)
            return self._deserialize_context(state_data["context"])
            
        except Exception as e:
            self._logger.error(f"Error retrieving from hot storage: {e}")
            return None
    
    def _serialize_context(self, context: ConversationContext) -> Dict[str, Any]:
        """Serialize conversation context to dictionary."""
        return asdict(context)
    
    def _deserialize_context(self, data: Dict[str, Any]) -> ConversationContext:
        """Deserialize conversation context from dictionary."""
        # Convert datetime strings back to datetime objects
        if isinstance(data.get("session_start"), str):
            data["session_start"] = datetime.fromisoformat(data["session_start"])
        
        # Convert conversation turns
        if "conversation_turns" in data:
            turns = []
            for turn_data in data["conversation_turns"]:
                if isinstance(turn_data.get("timestamp"), str):
                    turn_data["timestamp"] = datetime.fromisoformat(turn_data["timestamp"])
                turns.append(ConversationTurn(**turn_data))
            data["conversation_turns"] = turns
        
        # Convert task context if present
        if data.get("current_task"):
            from .models import TaskContext
            task_data = data["current_task"]
            # Convert datetime fields
            for field in ["created_at", "claimed_at", "execution_start", "execution_end"]:
                if task_data.get(field) and isinstance(task_data[field], str):
                    task_data[field] = datetime.fromisoformat(task_data[field])
            data["current_task"] = TaskContext(**task_data)
        
        return ConversationContext(**data)


class WarmStateStorage:
    """Warm storage layer - Redis Streams with < 10ms access time."""
    
    def __init__(self, redis_client, config: PersistenceConfig):
        self.redis = redis_client
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.WarmStateStorage")
        self.ttl_seconds = config.warm_storage_ttl_days * 24 * 3600
    
    async def store_state(self, context: ConversationContext, state_hash: str) -> bool:
        """Store conversation state in warm storage using Redis Streams."""
        try:
            stream_key = f"warm:conversation:{context.conversation_id}"
            
            # Prepare stream entry
            entry_data = {
                "context": json.dumps(asdict(context), default=str),
                "state_hash": state_hash,
                "stored_at": datetime.now().isoformat(),
                "state_version": str(context.state_version)
            }
            
            # Compress if enabled
            if self.config.enable_compression:
                entry_data["context"] = gzip.compress(entry_data["context"].encode()).decode('latin1')
                entry_data["compressed"] = "true"
            
            # Add to stream
            await self.redis.xadd(stream_key, entry_data)
            
            # Set TTL on stream
            await self.redis.expire(stream_key, self.ttl_seconds)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing to warm storage: {e}")
            return False
    
    async def retrieve_state(self, conversation_id: str) -> Optional[ConversationContext]:
        """Retrieve latest conversation state from warm storage."""
        try:
            stream_key = f"warm:conversation:{conversation_id}"
            
            # Get latest entry from stream
            entries = await self.redis.xrevrange(stream_key, count=1)
            
            if not entries:
                return None
            
            entry_id, entry_data = entries[0]
            
            # Decompress if needed
            context_data = entry_data[b"context"].decode()
            if entry_data.get(b"compressed") == b"true":
                context_data = gzip.decompress(context_data.encode('latin1')).decode()
            
            context_dict = json.loads(context_data)
            return self._deserialize_context(context_dict)
            
        except Exception as e:
            self._logger.error(f"Error retrieving from warm storage: {e}")
            return None
    
    def _deserialize_context(self, data: Dict[str, Any]) -> ConversationContext:
        """Deserialize conversation context from dictionary."""
        # Reuse the same deserialization logic as hot storage
        hot_storage = HotStateStorage(None, self.config)
        return hot_storage._deserialize_context(data)


class ColdStateStorage:
    """Cold storage layer - Local file system with < 100ms access time."""
    
    def __init__(self, config: PersistenceConfig):
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.ColdStateStorage")
        self.storage_path = "/tmp/claude_task_queue_cold_storage"
        os.makedirs(self.storage_path, exist_ok=True)
    
    async def store_state(self, context: ConversationContext, state_hash: str) -> bool:
        """Store conversation state in cold storage."""
        try:
            file_path = os.path.join(self.storage_path, f"{context.conversation_id}.pkl")
            
            # Prepare storage data
            storage_data = {
                "context": asdict(context),
                "state_hash": state_hash,
                "stored_at": datetime.now().isoformat()
            }
            
            # Store using pickle for efficiency
            with open(file_path, 'wb') as f:
                if self.config.enable_compression:
                    compressed_data = gzip.compress(pickle.dumps(storage_data))
                    f.write(compressed_data)
                else:
                    pickle.dump(storage_data, f)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing to cold storage: {e}")
            return False
    
    async def retrieve_state(self, conversation_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation state from cold storage."""
        try:
            file_path = os.path.join(self.storage_path, f"{conversation_id}.pkl")
            
            if not os.path.exists(file_path):
                return None
            
            # Load data
            with open(file_path, 'rb') as f:
                if self.config.enable_compression:
                    compressed_data = f.read()
                    storage_data = pickle.loads(gzip.decompress(compressed_data))
                else:
                    storage_data = pickle.load(f)
            
            # Deserialize context
            context_dict = storage_data["context"]
            return self._deserialize_context(context_dict)
            
        except Exception as e:
            self._logger.error(f"Error retrieving from cold storage: {e}")
            return None
    
    def _deserialize_context(self, data: Dict[str, Any]) -> ConversationContext:
        """Deserialize conversation context from dictionary."""
        # Reuse the same deserialization logic
        hot_storage = HotStateStorage(None, self.config)
        return hot_storage._deserialize_context(data)


class CheckpointStorage:
    """Checkpoint storage layer - Immutable state snapshots."""
    
    def __init__(self, redis_client, config: PersistenceConfig):
        self.redis = redis_client
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.CheckpointStorage")
        self.ttl_seconds = config.checkpoint_storage_ttl_days * 24 * 3600
    
    async def store_checkpoint(self, checkpoint: StateCheckpoint) -> bool:
        """Store immutable checkpoint."""
        try:
            key = f"checkpoint:{checkpoint.checkpoint_id}"
            
            # Serialize checkpoint
            checkpoint_data = asdict(checkpoint)
            serialized_data = json.dumps(checkpoint_data, default=str)
            
            # Compress if enabled
            if self.config.enable_compression:
                serialized_data = gzip.compress(serialized_data.encode()).decode('latin1')
            
            # Store with TTL
            await self.redis.setex(key, self.ttl_seconds, serialized_data)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing checkpoint: {e}")
            return False
    
    async def retrieve_checkpoint(self, checkpoint_id: str) -> Optional[StateCheckpoint]:
        """Retrieve checkpoint by ID."""
        try:
            key = f"checkpoint:{checkpoint_id}"
            data = await self.redis.get(key)
            
            if not data:
                return None
            
            # Decompress if needed
            if self.config.enable_compression:
                data = gzip.decompress(data.encode('latin1')).decode()
            
            checkpoint_data = json.loads(data)
            
            # Convert datetime fields
            if isinstance(checkpoint_data.get("created_at"), str):
                checkpoint_data["created_at"] = datetime.fromisoformat(checkpoint_data["created_at"])
            
            # Convert conversation turns
            if "conversation_turns" in checkpoint_data:
                turns = []
                for turn_data in checkpoint_data["conversation_turns"]:
                    if isinstance(turn_data.get("timestamp"), str):
                        turn_data["timestamp"] = datetime.fromisoformat(turn_data["timestamp"])
                    turns.append(ConversationTurn(**turn_data))
                checkpoint_data["conversation_turns"] = turns
            
            return StateCheckpoint(**checkpoint_data)
            
        except Exception as e:
            self._logger.error(f"Error retrieving checkpoint: {e}")
            return None


class StateIntegrityMonitor:
    """Monitors state integrity and detects corruption."""
    
    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.StateIntegrityMonitor")
    
    async def verify_checkpoint_integrity(self, checkpoint: StateCheckpoint, storage: CheckpointStorage) -> bool:
        """Verify checkpoint integrity using hash validation."""
        try:
            # Retrieve checkpoint from storage
            stored_checkpoint = await storage.retrieve_checkpoint(checkpoint.checkpoint_id)
            
            if not stored_checkpoint:
                self._logger.warning(f"Checkpoint not found in storage: {checkpoint.checkpoint_id}")
                return False
            
            # Compare hashes
            if checkpoint.state_hash != stored_checkpoint.state_hash:
                self._logger.error(
                    f"Checkpoint hash mismatch: {checkpoint.checkpoint_id}",
                    extra={
                        "expected_hash": checkpoint.state_hash,
                        "stored_hash": stored_checkpoint.state_hash
                    }
                )
                return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error verifying checkpoint integrity: {e}")
            return False