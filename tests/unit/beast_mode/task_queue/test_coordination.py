"""
Unit tests for distributed conversation coordination

Tests distributed locking, conflict resolution, consensus mechanisms,
and multi-instance coordination scenarios.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json
import uuid
import asyncio

from src.beast_mode.task_queue.models import (
    ConversationContext,
    TaskContext,
    ConversationTurn,
    TaskState,
)
from src.beast_mode.task_queue.coordination import (
    DistributedConversationCoordinator,
    ConversationLock,
    ConsensusManager,
    ConflictResolver,
    ConflictResolutionResult,
    LockState,
)


class TestDistributedConversationCoordinator:
    """Test suite for DistributedConversationCoordinator."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.eval.return_value = 1  # Success by default
        mock.hset.return_value = True
        mock.expire.return_value = True
        mock.hgetall.return_value = {}
        return mock
    
    @pytest.fixture
    def coordinator(self, mock_redis):
        """Create DistributedConversationCoordinator instance."""
        return DistributedConversationCoordinator(mock_redis, "test-instance-001")
    
    @pytest.fixture
    def conversation_context(self):
        """Create test conversation context."""
        return ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001",
            conversation_turns=[
                ConversationTurn(role="user", content="Test message")
            ]
        )
    
    @pytest.mark.asyncio
    async def test_coordinate_conversation_access_success(self, coordinator, mock_redis):
        """Test successful conversation access coordination."""
        conversation_id = "test-conversation-001"
        
        # Mock successful lock acquisition
        mock_redis.eval.return_value = 1
        
        lock = await coordinator.coordinate_conversation_access(conversation_id)
        
        assert lock is not None
        assert lock.conversation_id == conversation_id
        assert lock.instance_id == coordinator.instance_id
        assert lock.lock_id is not None
        assert lock.acquired_at is not None
        assert lock.expires_at > lock.acquired_at
        assert not lock.is_expired()
        
        # Verify Redis was called with correct parameters
        mock_redis.eval.assert_called_once()
        call_args = mock_redis.eval.call_args
        # Check that the key contains conversation_lock
        assert "conversation_lock:" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_coordinate_conversation_access_failure(self, coordinator, mock_redis):
        """Test conversation access coordination failure."""
        conversation_id = "test-conversation-001"
        
        # Mock lock acquisition failure
        mock_redis.eval.return_value = 0
        
        lock = await coordinator.coordinate_conversation_access(conversation_id)
        
        assert lock is None
    
    @pytest.mark.asyncio
    async def test_coordinate_conversation_access_redis_error(self, coordinator, mock_redis):
        """Test conversation access coordination with Redis error."""
        conversation_id = "test-conversation-001"
        
        # Mock Redis error
        mock_redis.eval.side_effect = Exception("Redis connection error")
        
        lock = await coordinator.coordinate_conversation_access(conversation_id)
        
        assert lock is None
    
    @pytest.mark.asyncio
    async def test_release_conversation_lock_success(self, coordinator, mock_redis):
        """Test successful conversation lock release."""
        lock = ConversationLock(
            conversation_id="test-conversation-001",
            instance_id=coordinator.instance_id,
            lock_id="test-lock-001",
            acquired_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30)
        )
        
        # Mock successful release
        mock_redis.eval.return_value = 1
        
        success = await coordinator.release_conversation_lock(lock)
        
        assert success is True
        
        # Verify Redis was called with correct parameters
        mock_redis.eval.assert_called_once()
        call_args = mock_redis.eval.call_args
        # Check that the lock_id is in the call arguments
        assert lock.lock_id in str(call_args)
    
    @pytest.mark.asyncio
    async def test_release_conversation_lock_failure(self, coordinator, mock_redis):
        """Test conversation lock release failure."""
        lock = ConversationLock(
            conversation_id="test-conversation-001",
            instance_id=coordinator.instance_id,
            lock_id="test-lock-001",
            acquired_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30)
        )
        
        # Mock release failure (lock not found or expired)
        mock_redis.eval.return_value = 0
        
        success = await coordinator.release_conversation_lock(lock)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_renew_conversation_lock_success(self, coordinator, mock_redis):
        """Test successful conversation lock renewal."""
        lock = ConversationLock(
            conversation_id="test-conversation-001",
            instance_id=coordinator.instance_id,
            lock_id="test-lock-001",
            acquired_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30),
            renewable=True
        )
        
        original_expiry = lock.expires_at
        
        # Mock successful renewal
        mock_redis.eval.return_value = 1
        
        success = await coordinator.renew_conversation_lock(lock)
        
        assert success is True
        assert lock.expires_at > original_expiry
    
    @pytest.mark.asyncio
    async def test_renew_conversation_lock_non_renewable(self, coordinator, mock_redis):
        """Test conversation lock renewal when lock is not renewable."""
        lock = ConversationLock(
            conversation_id="test-conversation-001",
            instance_id=coordinator.instance_id,
            lock_id="test-lock-001",
            acquired_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30),
            renewable=False
        )
        
        success = await coordinator.renew_conversation_lock(lock)
        
        assert success is False
        # Redis should not be called
        mock_redis.eval.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_resolve_state_conflicts_single_state(self, coordinator, conversation_context):
        """Test state conflict resolution with single state."""
        conflicted_states = [conversation_context]
        
        resolved_state = await coordinator.resolve_state_conflicts(
            conversation_context.conversation_id, conflicted_states
        )
        
        assert resolved_state == conversation_context
    
    @pytest.mark.asyncio
    async def test_resolve_state_conflicts_multiple_states(self, coordinator):
        """Test state conflict resolution with multiple states."""
        # Create conflicted states
        state1 = ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="instance-001",
            state_version=1,
            conversation_turns=[
                ConversationTurn(turn_id="turn-001", role="user", content="Message 1")
            ]
        )
        
        state2 = ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="instance-002",
            state_version=2,
            conversation_turns=[
                ConversationTurn(turn_id="turn-002", role="user", content="Message 2")
            ]
        )
        
        conflicted_states = [state1, state2]
        
        # Mock conflict resolver
        coordinator.conflict_resolver.resolve_conflicts = AsyncMock(
            return_value=ConflictResolutionResult(
                resolved_state=state2,
                resolution_method="highest_version",
                conflicted_instances=["instance-001", "instance-002"],
                resolution_timestamp=datetime.now(),
                confidence_score=0.8
            )
        )
        
        resolved_state = await coordinator.resolve_state_conflicts(
            "test-conversation-001", conflicted_states
        )
        
        assert resolved_state == state2
        coordinator.conflict_resolver.resolve_conflicts.assert_called_once_with(
            "test-conversation-001", conflicted_states
        )
    
    @pytest.mark.asyncio
    async def test_resolve_state_conflicts_empty_list(self, coordinator):
        """Test state conflict resolution with empty state list."""
        resolved_state = await coordinator.resolve_state_conflicts("test-conversation-001", [])
        
        assert resolved_state is None
    
    @pytest.mark.asyncio
    async def test_acquire_distributed_lock_retry_mechanism(self, coordinator, mock_redis):
        """Test distributed lock acquisition retry mechanism."""
        conversation_id = "test-conversation-001"
        
        # Mock first few attempts fail, then succeed
        mock_redis.eval.side_effect = [0, 0, 1]  # Fail, fail, succeed
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            lock = await coordinator.coordinate_conversation_access(conversation_id)
        
        assert lock is not None
        assert mock_redis.eval.call_count == 3
        assert mock_sleep.call_count == 2  # Two retries


class TestConversationLock:
    """Test suite for ConversationLock."""
    
    def test_lock_creation(self):
        """Test conversation lock creation."""
        now = datetime.now()
        expires_at = now + timedelta(seconds=30)
        
        lock = ConversationLock(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001",
            lock_id="test-lock-001",
            acquired_at=now,
            expires_at=expires_at
        )
        
        assert lock.conversation_id == "test-conversation-001"
        assert lock.instance_id == "test-instance-001"
        assert lock.lock_id == "test-lock-001"
        assert lock.acquired_at == now
        assert lock.expires_at == expires_at
        assert lock.lease_duration_seconds == 30
        assert lock.renewable is True
    
    def test_is_expired_false(self):
        """Test lock expiry check when not expired."""
        lock = ConversationLock(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001",
            lock_id="test-lock-001",
            acquired_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30)
        )
        
        assert lock.is_expired() is False
    
    def test_is_expired_true(self):
        """Test lock expiry check when expired."""
        lock = ConversationLock(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001",
            lock_id="test-lock-001",
            acquired_at=datetime.now() - timedelta(seconds=60),
            expires_at=datetime.now() - timedelta(seconds=30)
        )
        
        assert lock.is_expired() is True
    
    def test_time_remaining_positive(self):
        """Test time remaining calculation when positive."""
        lock = ConversationLock(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001",
            lock_id="test-lock-001",
            acquired_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30)
        )
        
        remaining = lock.time_remaining()
        assert 25 <= remaining <= 30  # Allow for small timing differences
    
    def test_time_remaining_expired(self):
        """Test time remaining calculation when expired."""
        lock = ConversationLock(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001",
            lock_id="test-lock-001",
            acquired_at=datetime.now() - timedelta(seconds=60),
            expires_at=datetime.now() - timedelta(seconds=30)
        )
        
        remaining = lock.time_remaining()
        assert remaining == 0


class TestConsensusManager:
    """Test suite for ConsensusManager."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.hset.return_value = True
        mock.expire.return_value = True
        mock.hgetall.return_value = {}
        return mock
    
    @pytest.fixture
    def consensus_manager(self, mock_redis):
        """Create ConsensusManager instance."""
        return ConsensusManager(mock_redis, "test-instance-001")
    
    @pytest.fixture
    def conversation_context(self):
        """Create test conversation context."""
        return ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001"
        )
    
    @pytest.mark.asyncio
    async def test_achieve_consensus_single_instance(self, consensus_manager, conversation_context, mock_redis):
        """Test consensus achievement with single instance."""
        # Mock single proposal
        mock_redis.hgetall.return_value = {"proposal-001": "proposal_data"}
        
        success = await consensus_manager.achieve_consensus(
            conversation_context.conversation_id, conversation_context
        )
        
        assert success is True
        
        # Verify Redis operations
        mock_redis.hset.assert_called_once()
        mock_redis.expire.assert_called_once()
        mock_redis.hgetall.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_achieve_consensus_multiple_instances(self, consensus_manager, conversation_context, mock_redis):
        """Test consensus achievement with multiple instances."""
        # Mock multiple proposals
        mock_redis.hgetall.return_value = {
            "proposal-001": "proposal_data_1",
            "proposal-002": "proposal_data_2"
        }
        
        success = await consensus_manager.achieve_consensus(
            conversation_context.conversation_id, conversation_context
        )
        
        # In simplified implementation, this still returns True
        assert success is True
    
    @pytest.mark.asyncio
    async def test_achieve_consensus_redis_error(self, consensus_manager, conversation_context, mock_redis):
        """Test consensus achievement with Redis error."""
        mock_redis.hset.side_effect = Exception("Redis error")
        
        success = await consensus_manager.achieve_consensus(
            conversation_context.conversation_id, conversation_context
        )
        
        assert success is False


class TestConflictResolver:
    """Test suite for ConflictResolver."""
    
    @pytest.fixture
    def conflict_resolver(self):
        """Create ConflictResolver instance."""
        return ConflictResolver()
    
    @pytest.fixture
    def conflicted_states(self):
        """Create conflicted conversation states."""
        state1 = ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="instance-001",
            state_version=1,
            session_start=datetime.now() - timedelta(minutes=10),
            conversation_turns=[
                ConversationTurn(turn_id="turn-001", role="user", content="Message 1", 
                               timestamp=datetime.now() - timedelta(minutes=5))
            ],
            conversation_metadata={"key1": "value1"}
        )
        
        state2 = ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="instance-002",
            state_version=2,
            session_start=datetime.now() - timedelta(minutes=8),
            conversation_turns=[
                ConversationTurn(turn_id="turn-002", role="assistant", content="Message 2",
                               timestamp=datetime.now() - timedelta(minutes=3))
            ],
            conversation_metadata={"key2": "value2"},
            last_persistence=datetime.now() - timedelta(minutes=1)
        )
        
        return [state1, state2]
    
    @pytest.mark.asyncio
    async def test_resolve_conflicts_empty_list(self, conflict_resolver):
        """Test conflict resolution with empty state list."""
        result = await conflict_resolver.resolve_conflicts("test-conversation-001", [])
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_resolve_conflicts_single_state(self, conflict_resolver, conflicted_states):
        """Test conflict resolution with single state."""
        single_state = [conflicted_states[0]]
        
        result = await conflict_resolver.resolve_conflicts("test-conversation-001", single_state)
        
        assert result is not None
        assert result.resolved_state == conflicted_states[0]
        assert result.resolution_method in ["vector_clocks", "last_writer_wins", "highest_version", "crdt_merge"]
    
    @pytest.mark.asyncio
    async def test_resolve_conflicts_multiple_states(self, conflict_resolver, conflicted_states):
        """Test conflict resolution with multiple states."""
        result = await conflict_resolver.resolve_conflicts("test-conversation-001", conflicted_states)
        
        assert result is not None
        assert result.resolved_state is not None
        assert result.resolution_method is not None
        assert result.confidence_score > 0
        assert len(result.conflicted_instances) == 2
        assert "instance-001" in result.conflicted_instances
        assert "instance-002" in result.conflicted_instances
    
    def test_resolve_by_vector_clocks_clear_winner(self, conflict_resolver, conflicted_states):
        """Test vector clock resolution with clear winner."""
        # State2 has higher version
        result = conflict_resolver._resolve_by_vector_clocks(conflicted_states)
        
        assert result == conflicted_states[1]  # Higher version state
    
    def test_resolve_by_vector_clocks_concurrent_updates(self, conflict_resolver):
        """Test vector clock resolution with concurrent updates."""
        # Create states with same version (concurrent)
        state1 = ConversationContext(conversation_id="test", state_version=2)
        state2 = ConversationContext(conversation_id="test", state_version=2)
        
        result = conflict_resolver._resolve_by_vector_clocks([state1, state2])
        
        assert result is None  # No clear winner
    
    def test_resolve_by_timestamps(self, conflict_resolver, conflicted_states):
        """Test timestamp-based resolution."""
        result = conflict_resolver._resolve_by_timestamps(conflicted_states)
        
        # State2 has more recent last_persistence
        assert result == conflicted_states[1]
    
    def test_resolve_by_state_version(self, conflict_resolver, conflicted_states):
        """Test state version-based resolution."""
        result = conflict_resolver._resolve_by_state_version(conflicted_states)
        
        # State2 has higher version
        assert result == conflicted_states[1]
    
    @pytest.mark.asyncio
    async def test_crdt_merge_single_state(self, conflict_resolver, conflicted_states):
        """Test CRDT merge with single state."""
        single_state = [conflicted_states[0]]
        
        result = await conflict_resolver._resolve_by_crdt_merge(single_state)
        
        assert result == conflicted_states[0]
    
    @pytest.mark.asyncio
    async def test_crdt_merge_multiple_states(self, conflict_resolver, conflicted_states):
        """Test CRDT merge with multiple states."""
        result = await conflict_resolver._resolve_by_crdt_merge(conflicted_states)
        
        assert result is not None
        assert result.conversation_id == "test-conversation-001"
        # Should have merged conversation turns
        assert len(result.conversation_turns) == 2
        # Should have merged metadata
        assert "key1" in result.conversation_metadata
        assert "key2" in result.conversation_metadata
        # Should have incremented version
        assert result.state_version > max(s.state_version for s in conflicted_states)
    
    @pytest.mark.asyncio
    async def test_merge_conversation_states_comprehensive(self, conflict_resolver):
        """Test comprehensive conversation state merging."""
        # Create states with overlapping and unique data
        state1 = ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="instance-001",
            session_start=datetime.now() - timedelta(minutes=10),
            state_version=1,
            conversation_turns=[
                ConversationTurn(turn_id="turn-001", role="user", content="Message 1",
                               timestamp=datetime.now() - timedelta(minutes=8)),
                ConversationTurn(turn_id="turn-shared", role="user", content="Shared message old",
                               timestamp=datetime.now() - timedelta(minutes=6))
            ],
            conversation_metadata={"shared_key": "old_value", "key1": "value1"},
            current_task=TaskContext(task_id="task-001", created_at=datetime.now() - timedelta(minutes=5))
        )
        
        state2 = ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="instance-002",
            session_start=datetime.now() - timedelta(minutes=8),
            state_version=2,
            conversation_turns=[
                ConversationTurn(turn_id="turn-002", role="assistant", content="Message 2",
                               timestamp=datetime.now() - timedelta(minutes=4)),
                ConversationTurn(turn_id="turn-shared", role="user", content="Shared message new",
                               timestamp=datetime.now() - timedelta(minutes=2))
            ],
            conversation_metadata={"shared_key": "new_value", "key2": "value2"},
            current_task=TaskContext(task_id="task-002", created_at=datetime.now() - timedelta(minutes=3))
        )
        
        merged = await conflict_resolver._merge_conversation_states(state1, state2)
        
        # Verify merge results
        assert merged.conversation_id == "test-conversation-001"
        assert merged.session_start == state1.session_start  # Earlier start time
        assert merged.state_version == 3  # max(1, 2) + 1
        assert merged.dirty_state is True
        
        # Verify conversation turns merge
        assert len(merged.conversation_turns) == 3  # 2 unique + 1 deduplicated
        turn_ids = [turn.turn_id for turn in merged.conversation_turns]
        assert "turn-001" in turn_ids
        assert "turn-002" in turn_ids
        assert "turn-shared" in turn_ids
        
        # Verify shared turn uses newer version
        shared_turn = next(turn for turn in merged.conversation_turns if turn.turn_id == "turn-shared")
        assert shared_turn.content == "Shared message new"
        
        # Verify metadata merge
        assert merged.conversation_metadata["shared_key"] == "new_value"  # state2 overwrites
        assert merged.conversation_metadata["key1"] == "value1"
        assert merged.conversation_metadata["key2"] == "value2"
        
        # Verify task selection (newer task)
        assert merged.current_task.task_id == "task-002"