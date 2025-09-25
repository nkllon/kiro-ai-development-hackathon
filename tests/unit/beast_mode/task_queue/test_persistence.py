"""
Unit tests for StatePersistenceManager and storage layers

Tests multi-layer persistence, integrity checking, compression,
and recovery mechanisms with Redis mocks.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import json
import gzip
import pickle
import os
import tempfile
import uuid

from src.beast_mode.task_queue.models import (
    ConversationContext,
    TaskContext,
    StateCheckpoint,
    PersistenceConfig,
    ConversationTurn,
    TaskState,
)
from src.beast_mode.task_queue.persistence import (
    StatePersistenceManager,
    HotStateStorage,
    WarmStateStorage,
    ColdStateStorage,
    CheckpointStorage,
    StateIntegrityMonitor,
    StateIntegrityError,
)


class TestStatePersistenceManager:
    """Test suite for StatePersistenceManager."""
    
    @pytest.fixture
    def persistence_config(self):
        """Create test persistence configuration."""
        return PersistenceConfig(
            hot_storage_ttl_hours=1,
            warm_storage_ttl_days=7,
            cold_storage_ttl_days=30,
            checkpoint_storage_ttl_days=90,
            enable_compression=True,
            integrity_checking=True
        )
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.setex.return_value = True
        mock.get.return_value = None
        mock.xadd.return_value = b"1234567890-0"
        mock.expire.return_value = True
        mock.xrevrange.return_value = []
        return mock
    
    @pytest.fixture
    def conversation_context(self):
        """Create test conversation context."""
        return ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001",
            conversation_turns=[
                ConversationTurn(
                    turn_id="turn-001",
                    role="user",
                    content="Hello, world!",
                    timestamp=datetime.now()
                )
            ],
            conversation_metadata={"test_key": "test_value"},
            current_task=TaskContext(
                task_id="test-task-001",
                task_type="test",
                task_state=TaskState.EXECUTING
            )
        )
    
    @pytest.fixture
    def persistence_manager(self, mock_redis, persistence_config):
        """Create StatePersistenceManager instance."""
        return StatePersistenceManager(mock_redis, persistence_config)
    
    @pytest.mark.asyncio
    async def test_persist_conversation_state_success(self, persistence_manager, conversation_context):
        """Test successful conversation state persistence."""
        # Mock storage layer successes
        persistence_manager.hot_storage.store_state = AsyncMock(return_value=True)
        persistence_manager.warm_storage.store_state = AsyncMock(return_value=True)
        persistence_manager.cold_storage.store_state = AsyncMock(return_value=True)
        
        success = await persistence_manager.persist_conversation_state(conversation_context)
        
        assert success is True
        
        # Verify hot storage was called
        persistence_manager.hot_storage.store_state.assert_called_once()
        args = persistence_manager.hot_storage.store_state.call_args[0]
        assert args[0] == conversation_context
        assert isinstance(args[1], str)  # state_hash
        
        # Verify warm storage was called
        persistence_manager.warm_storage.store_state.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_persist_conversation_state_hot_failure(self, persistence_manager, conversation_context):
        """Test persistence failure when hot storage fails."""
        # Mock hot storage failure
        persistence_manager.hot_storage.store_state = AsyncMock(return_value=False)
        
        success = await persistence_manager.persist_conversation_state(conversation_context)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_persist_conversation_state_warm_failure_continues(self, persistence_manager, conversation_context):
        """Test that warm storage failure doesn't stop persistence."""
        # Mock hot success, warm failure
        persistence_manager.hot_storage.store_state = AsyncMock(return_value=True)
        persistence_manager.warm_storage.store_state = AsyncMock(return_value=False)
        
        success = await persistence_manager.persist_conversation_state(conversation_context)
        
        assert success is True  # Should still succeed if hot storage works
    
    @pytest.mark.asyncio
    async def test_create_checkpoint_success(self, persistence_manager, conversation_context):
        """Test successful checkpoint creation."""
        # Mock checkpoint storage success
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=True)
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        checkpoint = await persistence_manager.create_checkpoint(conversation_context)
        
        assert checkpoint is not None
        assert checkpoint.conversation_id == conversation_context.conversation_id
        assert checkpoint.checkpoint_id is not None
        assert checkpoint.state_hash is not None
        assert checkpoint.integrity_verified is True
        assert len(checkpoint.conversation_turns) == len(conversation_context.conversation_turns)
        
        # Verify storage was called
        persistence_manager.checkpoint_storage.store_checkpoint.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_checkpoint_storage_failure(self, persistence_manager, conversation_context):
        """Test checkpoint creation when storage fails."""
        # Mock storage failure
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=False)
        
        with pytest.raises(Exception, match="Failed to store checkpoint"):
            await persistence_manager.create_checkpoint(conversation_context)
    
    @pytest.mark.asyncio
    async def test_rollback_to_checkpoint_success(self, persistence_manager, conversation_context):
        """Test successful rollback to checkpoint."""
        # Create checkpoint data
        checkpoint = StateCheckpoint(
            checkpoint_id="test-checkpoint-001",
            conversation_id=conversation_context.conversation_id,
            conversation_turns=[
                ConversationTurn(turn_id="old-turn", role="user", content="Old content")
            ],
            conversation_metadata={"old_key": "old_value"},
            task_context={"task_id": "old-task", "task_type": "old_type"}
        )
        
        # Mock integrity verification success
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        # Store original state for comparison
        original_turns = conversation_context.conversation_turns.copy()
        original_metadata = conversation_context.conversation_metadata.copy()
        original_version = conversation_context.state_version
        
        success = await persistence_manager.rollback_to_checkpoint(conversation_context, checkpoint)
        
        assert success is True
        
        # Verify state was restored
        assert len(conversation_context.conversation_turns) == 1
        assert conversation_context.conversation_turns[0].turn_id == "old-turn"
        assert conversation_context.conversation_metadata == {"old_key": "old_value"}
        assert conversation_context.current_task.task_id == "old-task"
        assert conversation_context.state_version == original_version + 1
        assert conversation_context.dirty_state is True
    
    @pytest.mark.asyncio
    async def test_rollback_to_checkpoint_integrity_failure(self, persistence_manager, conversation_context):
        """Test rollback failure when checkpoint integrity fails."""
        checkpoint = StateCheckpoint(checkpoint_id="test-checkpoint")
        
        # Mock integrity verification failure
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=False)
        
        success = await persistence_manager.rollback_to_checkpoint(conversation_context, checkpoint)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_recover_from_corruption_success(self, persistence_manager):
        """Test successful corruption recovery."""
        conversation_id = "test-conversation-001"
        
        # Mock recovery candidates
        hot_context = ConversationContext(conversation_id=conversation_id)
        warm_context = ConversationContext(conversation_id=conversation_id)
        
        persistence_manager.hot_storage.retrieve_state = AsyncMock(return_value=hot_context)
        persistence_manager.warm_storage.retrieve_state = AsyncMock(return_value=warm_context)
        persistence_manager.cold_storage.retrieve_state = AsyncMock(return_value=None)
        persistence_manager._verify_state_integrity = AsyncMock(return_value=True)
        
        recovered_state = await persistence_manager.recover_from_corruption(conversation_id)
        
        assert recovered_state is not None
        assert recovered_state.conversation_id == conversation_id
        # Should prefer hot storage
        assert recovered_state == hot_context
    
    @pytest.mark.asyncio
    async def test_recover_from_corruption_no_candidates(self, persistence_manager):
        """Test corruption recovery when no valid candidates exist."""
        conversation_id = "test-conversation-001"
        
        # Mock no valid candidates
        persistence_manager.hot_storage.retrieve_state = AsyncMock(return_value=None)
        persistence_manager.warm_storage.retrieve_state = AsyncMock(return_value=None)
        persistence_manager.cold_storage.retrieve_state = AsyncMock(return_value=None)
        
        recovered_state = await persistence_manager.recover_from_corruption(conversation_id)
        
        assert recovered_state is None
    
    def test_generate_state_hash(self, persistence_manager, conversation_context):
        """Test state hash generation."""
        hash1 = persistence_manager._generate_state_hash(conversation_context)
        hash2 = persistence_manager._generate_state_hash(conversation_context)
        
        # Same context should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length
        
        # Different context should produce different hash
        conversation_context.state_version += 1
        hash3 = persistence_manager._generate_state_hash(conversation_context)
        assert hash1 != hash3
    
    def test_generate_checkpoint_hash(self, persistence_manager):
        """Test checkpoint hash generation."""
        checkpoint = StateCheckpoint(
            checkpoint_id="test-checkpoint",
            conversation_id="test-conversation",
            created_at=datetime.now()
        )
        
        hash1 = persistence_manager._generate_checkpoint_hash(checkpoint)
        hash2 = persistence_manager._generate_checkpoint_hash(checkpoint)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length
    
    def test_should_persist_to_cold_age_threshold(self, persistence_manager, conversation_context):
        """Test cold storage persistence based on age threshold."""
        # New conversation should not persist to cold
        assert persistence_manager._should_persist_to_cold(conversation_context) is False
        
        # Old conversation should persist to cold
        conversation_context.session_start = datetime.now() - timedelta(hours=2)
        assert persistence_manager._should_persist_to_cold(conversation_context) is True
    
    def test_should_persist_to_cold_turn_threshold(self, persistence_manager, conversation_context):
        """Test cold storage persistence based on turn threshold."""
        # Add many turns
        for i in range(60):
            conversation_context.conversation_turns.append(
                ConversationTurn(turn_id=f"turn-{i}", role="user", content=f"Message {i}")
            )
        
        assert persistence_manager._should_persist_to_cold(conversation_context) is True


class TestHotStateStorage:
    """Test suite for HotStateStorage."""
    
    @pytest.fixture
    def persistence_config(self):
        return PersistenceConfig(
            hot_storage_ttl_hours=1,
            enable_compression=True,
            integrity_checking=True
        )
    
    @pytest.fixture
    def mock_redis(self):
        mock = AsyncMock()
        mock.setex.return_value = True
        mock.get.return_value = None
        return mock
    
    @pytest.fixture
    def hot_storage(self, mock_redis, persistence_config):
        return HotStateStorage(mock_redis, persistence_config)
    
    @pytest.fixture
    def conversation_context(self):
        return ConversationContext(
            conversation_id="test-conversation-001",
            conversation_turns=[
                ConversationTurn(role="user", content="Test message")
            ]
        )
    
    @pytest.mark.asyncio
    async def test_store_state_success(self, hot_storage, conversation_context):
        """Test successful state storage in hot storage."""
        state_hash = "test-hash"
        
        success = await hot_storage.store_state(conversation_context, state_hash)
        
        assert success is True
        
        # Verify Redis was called correctly
        hot_storage.redis.setex.assert_called_once()
        call_args = hot_storage.redis.setex.call_args[0]
        assert call_args[0] == f"hot:conversation:{conversation_context.conversation_id}"
        assert call_args[1] == 3600  # TTL in seconds
        assert isinstance(call_args[2], str)  # Serialized data
    
    @pytest.mark.asyncio
    async def test_store_state_redis_failure(self, hot_storage, conversation_context):
        """Test state storage failure when Redis fails."""
        hot_storage.redis.setex.side_effect = Exception("Redis error")
        
        success = await hot_storage.store_state(conversation_context, "test-hash")
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_retrieve_state_success(self, hot_storage, conversation_context):
        """Test successful state retrieval from hot storage."""
        # Mock stored data
        stored_data = {
            "context": hot_storage._serialize_context(conversation_context),
            "state_hash": "test-hash",
            "stored_at": datetime.now().isoformat()
        }
        serialized_data = json.dumps(stored_data, default=str)
        compressed_data = gzip.compress(serialized_data.encode()).decode('latin1')
        
        hot_storage.redis.get.return_value = compressed_data
        
        retrieved_context = await hot_storage.retrieve_state(conversation_context.conversation_id)
        
        assert retrieved_context is not None
        assert retrieved_context.conversation_id == conversation_context.conversation_id
        assert len(retrieved_context.conversation_turns) == len(conversation_context.conversation_turns)
    
    @pytest.mark.asyncio
    async def test_retrieve_state_not_found(self, hot_storage):
        """Test state retrieval when data not found."""
        hot_storage.redis.get.return_value = None
        
        retrieved_context = await hot_storage.retrieve_state("nonexistent-id")
        
        assert retrieved_context is None
    
    @pytest.mark.asyncio
    async def test_retrieve_state_redis_failure(self, hot_storage):
        """Test state retrieval failure when Redis fails."""
        hot_storage.redis.get.side_effect = Exception("Redis error")
        
        retrieved_context = await hot_storage.retrieve_state("test-id")
        
        assert retrieved_context is None
    
    def test_serialize_deserialize_context(self, hot_storage, conversation_context):
        """Test context serialization and deserialization."""
        # Serialize
        serialized = hot_storage._serialize_context(conversation_context)
        assert isinstance(serialized, dict)
        assert serialized["conversation_id"] == conversation_context.conversation_id
        
        # Deserialize
        deserialized = hot_storage._deserialize_context(serialized)
        assert isinstance(deserialized, ConversationContext)
        assert deserialized.conversation_id == conversation_context.conversation_id
        assert len(deserialized.conversation_turns) == len(conversation_context.conversation_turns)


class TestWarmStateStorage:
    """Test suite for WarmStateStorage."""
    
    @pytest.fixture
    def persistence_config(self):
        return PersistenceConfig(
            warm_storage_ttl_days=7,
            enable_compression=True
        )
    
    @pytest.fixture
    def mock_redis(self):
        mock = AsyncMock()
        mock.xadd.return_value = b"1234567890-0"
        mock.expire.return_value = True
        mock.xrevrange.return_value = []
        return mock
    
    @pytest.fixture
    def warm_storage(self, mock_redis, persistence_config):
        return WarmStateStorage(mock_redis, persistence_config)
    
    @pytest.fixture
    def conversation_context(self):
        return ConversationContext(conversation_id="test-conversation-001")
    
    @pytest.mark.asyncio
    async def test_store_state_success(self, warm_storage, conversation_context):
        """Test successful state storage in warm storage."""
        success = await warm_storage.store_state(conversation_context, "test-hash")
        
        assert success is True
        
        # Verify Redis stream operations
        warm_storage.redis.xadd.assert_called_once()
        warm_storage.redis.expire.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retrieve_state_success(self, warm_storage, conversation_context):
        """Test successful state retrieval from warm storage."""
        # Mock stream entry
        context_json = json.dumps({"conversation_id": "test-conversation-001"}, default=str)
        compressed_context = gzip.compress(context_json.encode()).decode('latin1')
        
        mock_entry = (
            b"1234567890-0",
            {
                b"context": compressed_context.encode(),
                b"state_hash": b"test-hash",
                b"compressed": b"true"
            }
        )
        warm_storage.redis.xrevrange.return_value = [mock_entry]
        
        retrieved_context = await warm_storage.retrieve_state("test-conversation-001")
        
        assert retrieved_context is not None
        assert retrieved_context.conversation_id == "test-conversation-001"
    
    @pytest.mark.asyncio
    async def test_retrieve_state_not_found(self, warm_storage):
        """Test state retrieval when stream is empty."""
        warm_storage.redis.xrevrange.return_value = []
        
        retrieved_context = await warm_storage.retrieve_state("nonexistent-id")
        
        assert retrieved_context is None


class TestColdStateStorage:
    """Test suite for ColdStateStorage."""
    
    @pytest.fixture
    def persistence_config(self):
        return PersistenceConfig(enable_compression=True)
    
    @pytest.fixture
    def cold_storage(self, persistence_config):
        storage = ColdStateStorage(persistence_config)
        # Use temporary directory for testing
        storage.storage_path = tempfile.mkdtemp()
        return storage
    
    @pytest.fixture
    def conversation_context(self):
        return ConversationContext(conversation_id="test-conversation-001")
    
    @pytest.mark.asyncio
    async def test_store_state_success(self, cold_storage, conversation_context):
        """Test successful state storage in cold storage."""
        success = await cold_storage.store_state(conversation_context, "test-hash")
        
        assert success is True
        
        # Verify file was created
        file_path = os.path.join(cold_storage.storage_path, f"{conversation_context.conversation_id}.pkl")
        assert os.path.exists(file_path)
    
    @pytest.mark.asyncio
    async def test_retrieve_state_success(self, cold_storage, conversation_context):
        """Test successful state retrieval from cold storage."""
        # First store the state
        await cold_storage.store_state(conversation_context, "test-hash")
        
        # Then retrieve it
        retrieved_context = await cold_storage.retrieve_state(conversation_context.conversation_id)
        
        assert retrieved_context is not None
        assert retrieved_context.conversation_id == conversation_context.conversation_id
    
    @pytest.mark.asyncio
    async def test_retrieve_state_not_found(self, cold_storage):
        """Test state retrieval when file doesn't exist."""
        retrieved_context = await cold_storage.retrieve_state("nonexistent-id")
        
        assert retrieved_context is None


class TestCheckpointStorage:
    """Test suite for CheckpointStorage."""
    
    @pytest.fixture
    def persistence_config(self):
        return PersistenceConfig(
            checkpoint_storage_ttl_days=90,
            enable_compression=True
        )
    
    @pytest.fixture
    def mock_redis(self):
        mock = AsyncMock()
        mock.setex.return_value = True
        mock.get.return_value = None
        return mock
    
    @pytest.fixture
    def checkpoint_storage(self, mock_redis, persistence_config):
        return CheckpointStorage(mock_redis, persistence_config)
    
    @pytest.fixture
    def state_checkpoint(self):
        return StateCheckpoint(
            checkpoint_id="test-checkpoint-001",
            conversation_id="test-conversation-001",
            created_at=datetime.now(),
            conversation_turns=[
                ConversationTurn(role="user", content="Test message")
            ]
        )
    
    @pytest.mark.asyncio
    async def test_store_checkpoint_success(self, checkpoint_storage, state_checkpoint):
        """Test successful checkpoint storage."""
        success = await checkpoint_storage.store_checkpoint(state_checkpoint)
        
        assert success is True
        
        # Verify Redis was called
        checkpoint_storage.redis.setex.assert_called_once()
        call_args = checkpoint_storage.redis.setex.call_args[0]
        assert call_args[0] == f"checkpoint:{state_checkpoint.checkpoint_id}"
    
    @pytest.mark.asyncio
    async def test_retrieve_checkpoint_success(self, checkpoint_storage, state_checkpoint):
        """Test successful checkpoint retrieval."""
        # Mock stored checkpoint data
        checkpoint_data = {
            "checkpoint_id": state_checkpoint.checkpoint_id,
            "conversation_id": state_checkpoint.conversation_id,
            "created_at": state_checkpoint.created_at.isoformat(),
            "conversation_turns": [
                {
                    "turn_id": "test-turn",
                    "role": "user",
                    "content": "Test message",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {}
                }
            ],
            "conversation_metadata": {},
            "task_context": None,
            "state_hash": "",
            "integrity_verified": False
        }
        
        serialized_data = json.dumps(checkpoint_data, default=str)
        compressed_data = gzip.compress(serialized_data.encode()).decode('latin1')
        checkpoint_storage.redis.get.return_value = compressed_data
        
        retrieved_checkpoint = await checkpoint_storage.retrieve_checkpoint(state_checkpoint.checkpoint_id)
        
        assert retrieved_checkpoint is not None
        assert retrieved_checkpoint.checkpoint_id == state_checkpoint.checkpoint_id
        assert retrieved_checkpoint.conversation_id == state_checkpoint.conversation_id
    
    @pytest.mark.asyncio
    async def test_retrieve_checkpoint_not_found(self, checkpoint_storage):
        """Test checkpoint retrieval when not found."""
        checkpoint_storage.redis.get.return_value = None
        
        retrieved_checkpoint = await checkpoint_storage.retrieve_checkpoint("nonexistent-id")
        
        assert retrieved_checkpoint is None


class TestStateIntegrityMonitor:
    """Test suite for StateIntegrityMonitor."""
    
    @pytest.fixture
    def integrity_monitor(self):
        return StateIntegrityMonitor()
    
    @pytest.fixture
    def mock_checkpoint_storage(self):
        return AsyncMock()
    
    @pytest.fixture
    def state_checkpoint(self):
        return StateCheckpoint(
            checkpoint_id="test-checkpoint-001",
            state_hash="test-hash-123"
        )
    
    @pytest.mark.asyncio
    async def test_verify_checkpoint_integrity_success(self, integrity_monitor, mock_checkpoint_storage, state_checkpoint):
        """Test successful checkpoint integrity verification."""
        # Mock storage returns matching checkpoint
        stored_checkpoint = StateCheckpoint(
            checkpoint_id=state_checkpoint.checkpoint_id,
            state_hash=state_checkpoint.state_hash
        )
        mock_checkpoint_storage.retrieve_checkpoint.return_value = stored_checkpoint
        
        is_valid = await integrity_monitor.verify_checkpoint_integrity(state_checkpoint, mock_checkpoint_storage)
        
        assert is_valid is True
        mock_checkpoint_storage.retrieve_checkpoint.assert_called_once_with(state_checkpoint.checkpoint_id)
    
    @pytest.mark.asyncio
    async def test_verify_checkpoint_integrity_not_found(self, integrity_monitor, mock_checkpoint_storage, state_checkpoint):
        """Test checkpoint integrity verification when checkpoint not found."""
        mock_checkpoint_storage.retrieve_checkpoint.return_value = None
        
        is_valid = await integrity_monitor.verify_checkpoint_integrity(state_checkpoint, mock_checkpoint_storage)
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_verify_checkpoint_integrity_hash_mismatch(self, integrity_monitor, mock_checkpoint_storage, state_checkpoint):
        """Test checkpoint integrity verification with hash mismatch."""
        # Mock storage returns checkpoint with different hash
        stored_checkpoint = StateCheckpoint(
            checkpoint_id=state_checkpoint.checkpoint_id,
            state_hash="different-hash-456"
        )
        mock_checkpoint_storage.retrieve_checkpoint.return_value = stored_checkpoint
        
        is_valid = await integrity_monitor.verify_checkpoint_integrity(state_checkpoint, mock_checkpoint_storage)
        
        assert is_valid is False