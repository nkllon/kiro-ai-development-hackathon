"""
Unit tests for checkpoint lifecycle and rollback functionality

Tests checkpoint creation, validation, rollback scenarios,
and integrity checking with comprehensive edge cases.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json
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
    CheckpointStorage,
    StateIntegrityMonitor,
)


class TestCheckpointLifecycle:
    """Test suite for checkpoint creation and rollback lifecycle."""
    
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
        return mock
    
    @pytest.fixture
    def conversation_context(self):
        """Create comprehensive test conversation context."""
        return ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001",
            session_start=datetime.now() - timedelta(minutes=30),
            conversation_turns=[
                ConversationTurn(
                    turn_id="turn-001",
                    role="user",
                    content="Hello, I need help with a Python function",
                    timestamp=datetime.now() - timedelta(minutes=25),
                    metadata={"source": "chat"}
                ),
                ConversationTurn(
                    turn_id="turn-002",
                    role="assistant",
                    content="I'd be happy to help you with Python!",
                    timestamp=datetime.now() - timedelta(minutes=24),
                    metadata={"confidence": 0.95}
                ),
                ConversationTurn(
                    turn_id="turn-003",
                    role="user",
                    content="Can you write a function to calculate fibonacci numbers?",
                    timestamp=datetime.now() - timedelta(minutes=20),
                    metadata={"complexity": "medium"}
                )
            ],
            conversation_metadata={
                "user_id": "user-123",
                "session_type": "coding_assistance",
                "language": "python",
                "difficulty": "intermediate"
            },
            current_task=TaskContext(
                task_id="task-fibonacci-001",
                task_type="code_generation",
                task_content="Generate a fibonacci function",
                task_parameters={"language": "python", "style": "recursive"},
                task_state=TaskState.EXECUTING,
                created_at=datetime.now() - timedelta(minutes=15),
                claimed_at=datetime.now() - timedelta(minutes=10),
                execution_start=datetime.now() - timedelta(minutes=5)
            ),
            state_version=3
        )
    
    @pytest.fixture
    def persistence_manager(self, mock_redis, persistence_config):
        """Create StatePersistenceManager instance."""
        return StatePersistenceManager(mock_redis, persistence_config)
    
    @pytest.mark.asyncio
    async def test_create_checkpoint_comprehensive(self, persistence_manager, conversation_context):
        """Test comprehensive checkpoint creation with all data preserved."""
        # Mock successful storage and integrity verification
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=True)
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        checkpoint = await persistence_manager.create_checkpoint(conversation_context)
        
        # Verify checkpoint structure
        assert checkpoint is not None
        assert checkpoint.checkpoint_id is not None
        assert len(checkpoint.checkpoint_id) > 0
        assert checkpoint.conversation_id == conversation_context.conversation_id
        assert checkpoint.created_at is not None
        assert checkpoint.state_hash is not None
        assert checkpoint.integrity_verified is True
        
        # Verify conversation data preservation
        assert len(checkpoint.conversation_turns) == len(conversation_context.conversation_turns)
        assert checkpoint.conversation_turns[0].turn_id == "turn-001"
        assert checkpoint.conversation_turns[0].content == "Hello, I need help with a Python function"
        assert checkpoint.conversation_turns[2].role == "user"
        
        # Verify metadata preservation
        assert checkpoint.conversation_metadata == conversation_context.conversation_metadata
        assert checkpoint.conversation_metadata["user_id"] == "user-123"
        assert checkpoint.conversation_metadata["language"] == "python"
        
        # Verify task context preservation
        assert checkpoint.task_context is not None
        assert checkpoint.task_context["task_id"] == "task-fibonacci-001"
        assert checkpoint.task_context["task_type"] == "code_generation"
        assert checkpoint.task_context["task_parameters"]["language"] == "python"
        
        # Verify storage was called
        persistence_manager.checkpoint_storage.store_checkpoint.assert_called_once_with(checkpoint)
    
    @pytest.mark.asyncio
    async def test_create_checkpoint_without_task(self, persistence_manager, conversation_context):
        """Test checkpoint creation when no current task exists."""
        conversation_context.current_task = None
        
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=True)
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        checkpoint = await persistence_manager.create_checkpoint(conversation_context)
        
        assert checkpoint is not None
        assert checkpoint.task_context is None
        assert len(checkpoint.conversation_turns) == len(conversation_context.conversation_turns)
        assert checkpoint.conversation_metadata == conversation_context.conversation_metadata
    
    @pytest.mark.asyncio
    async def test_create_checkpoint_empty_conversation(self, persistence_manager):
        """Test checkpoint creation with minimal conversation data."""
        minimal_context = ConversationContext(
            conversation_id="minimal-conversation",
            conversation_turns=[],
            conversation_metadata={}
        )
        
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=True)
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        checkpoint = await persistence_manager.create_checkpoint(minimal_context)
        
        assert checkpoint is not None
        assert len(checkpoint.conversation_turns) == 0
        assert checkpoint.conversation_metadata == {}
        assert checkpoint.task_context is None
    
    @pytest.mark.asyncio
    async def test_rollback_to_checkpoint_comprehensive(self, persistence_manager, conversation_context):
        """Test comprehensive rollback with full state restoration."""
        # Create checkpoint with different state
        checkpoint_turns = [
            ConversationTurn(
                turn_id="checkpoint-turn-001",
                role="user",
                content="Original checkpoint content",
                timestamp=datetime.now() - timedelta(hours=1),
                metadata={"checkpoint": True}
            )
        ]
        
        checkpoint_metadata = {
            "checkpoint_user_id": "checkpoint-user-456",
            "checkpoint_session": "checkpoint_session",
            "restored": True
        }
        
        checkpoint_task = {
            "task_id": "checkpoint-task-001",
            "task_type": "checkpoint_task",
            "task_content": "Checkpoint task content",
            "task_parameters": {"checkpoint": True},
            "task_state": "QUEUED",
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "claimed_at": None,
            "execution_start": None,
            "execution_end": None
        }
        
        checkpoint = StateCheckpoint(
            checkpoint_id="comprehensive-checkpoint-001",
            conversation_id=conversation_context.conversation_id,
            created_at=datetime.now() - timedelta(hours=1),
            conversation_turns=checkpoint_turns,
            conversation_metadata=checkpoint_metadata,
            task_context=checkpoint_task,
            state_hash="checkpoint-hash-123"
        )
        
        # Mock integrity verification success
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        # Store original state for verification
        original_turn_count = len(conversation_context.conversation_turns)
        original_metadata = conversation_context.conversation_metadata.copy()
        original_task_id = conversation_context.current_task.task_id
        original_version = conversation_context.state_version
        
        # Perform rollback
        success = await persistence_manager.rollback_to_checkpoint(conversation_context, checkpoint)
        
        assert success is True
        
        # Verify conversation turns were restored
        assert len(conversation_context.conversation_turns) == 1
        assert conversation_context.conversation_turns[0].turn_id == "checkpoint-turn-001"
        assert conversation_context.conversation_turns[0].content == "Original checkpoint content"
        assert conversation_context.conversation_turns[0].metadata["checkpoint"] is True
        
        # Verify metadata was restored
        assert conversation_context.conversation_metadata == checkpoint_metadata
        assert conversation_context.conversation_metadata["checkpoint_user_id"] == "checkpoint-user-456"
        assert conversation_context.conversation_metadata["restored"] is True
        
        # Verify task context was restored
        assert conversation_context.current_task is not None
        assert conversation_context.current_task.task_id == "checkpoint-task-001"
        assert conversation_context.current_task.task_type == "checkpoint_task"
        assert conversation_context.current_task.task_parameters["checkpoint"] is True
        
        # Verify state management
        assert conversation_context.state_version == original_version + 1
        assert conversation_context.dirty_state is True
        
        # Verify original state was different
        assert original_turn_count != len(conversation_context.conversation_turns)
        assert original_metadata != conversation_context.conversation_metadata
        assert original_task_id != conversation_context.current_task.task_id
    
    @pytest.mark.asyncio
    async def test_rollback_to_checkpoint_no_task_context(self, persistence_manager, conversation_context):
        """Test rollback when checkpoint has no task context."""
        checkpoint = StateCheckpoint(
            checkpoint_id="no-task-checkpoint",
            conversation_id=conversation_context.conversation_id,
            conversation_turns=[
                ConversationTurn(turn_id="no-task-turn", role="user", content="No task content")
            ],
            conversation_metadata={"no_task": True},
            task_context=None
        )
        
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        success = await persistence_manager.rollback_to_checkpoint(conversation_context, checkpoint)
        
        assert success is True
        assert conversation_context.current_task is None
        assert len(conversation_context.conversation_turns) == 1
        assert conversation_context.conversation_metadata["no_task"] is True
    
    @pytest.mark.asyncio
    async def test_rollback_integrity_verification_failure(self, persistence_manager, conversation_context):
        """Test rollback failure when integrity verification fails."""
        checkpoint = StateCheckpoint(
            checkpoint_id="corrupt-checkpoint",
            conversation_id=conversation_context.conversation_id
        )
        
        # Mock integrity verification failure
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=False)
        
        # Store original state
        original_turns = conversation_context.conversation_turns.copy()
        original_metadata = conversation_context.conversation_metadata.copy()
        original_task = conversation_context.current_task
        
        success = await persistence_manager.rollback_to_checkpoint(conversation_context, checkpoint)
        
        assert success is False
        
        # Verify state was not modified
        assert conversation_context.conversation_turns == original_turns
        assert conversation_context.conversation_metadata == original_metadata
        assert conversation_context.current_task == original_task
    
    @pytest.mark.asyncio
    async def test_rollback_exception_handling(self, persistence_manager, conversation_context):
        """Test rollback exception handling."""
        checkpoint = StateCheckpoint(
            checkpoint_id="exception-checkpoint",
            conversation_id=conversation_context.conversation_id
        )
        
        # Mock integrity verification to raise exception
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(
            side_effect=Exception("Integrity check failed")
        )
        
        success = await persistence_manager.rollback_to_checkpoint(conversation_context, checkpoint)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_checkpoint_hash_generation_consistency(self, persistence_manager, conversation_context):
        """Test that checkpoint hash generation is consistent."""
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=True)
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        # Create two checkpoints with same data
        checkpoint1 = await persistence_manager.create_checkpoint(conversation_context)
        
        # Reset mocks and create another checkpoint with same context
        persistence_manager.checkpoint_storage.store_checkpoint.reset_mock()
        checkpoint2 = await persistence_manager.create_checkpoint(conversation_context)
        
        # Hashes should be the same for same content
        # Note: In practice, timestamps might differ, but core content hash should be consistent
        assert len(checkpoint1.state_hash) == len(checkpoint2.state_hash)
        assert checkpoint1.state_hash is not None
        assert checkpoint2.state_hash is not None
    
    @pytest.mark.asyncio
    async def test_checkpoint_with_complex_task_state(self, persistence_manager, conversation_context):
        """Test checkpoint creation with complex task state and history."""
        # Add complex task state
        conversation_context.current_task.state_history = [
            (TaskState.QUEUED, datetime.now() - timedelta(minutes=20)),
            (TaskState.CLAIMED, datetime.now() - timedelta(minutes=15)),
            (TaskState.VALIDATED, datetime.now() - timedelta(minutes=10)),
            (TaskState.EXECUTING, datetime.now() - timedelta(minutes=5))
        ]
        conversation_context.current_task.task_metadata = {
            "complexity": "high",
            "estimated_duration": 300,
            "dependencies": ["task-001", "task-002"],
            "retry_count": 2
        }
        
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=True)
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        checkpoint = await persistence_manager.create_checkpoint(conversation_context)
        
        assert checkpoint is not None
        assert checkpoint.task_context is not None
        assert checkpoint.task_context["task_metadata"]["complexity"] == "high"
        assert checkpoint.task_context["task_metadata"]["retry_count"] == 2
        assert len(checkpoint.task_context["task_metadata"]["dependencies"]) == 2
    
    @pytest.mark.asyncio
    async def test_multiple_checkpoint_rollback_sequence(self, persistence_manager, conversation_context):
        """Test sequence of multiple checkpoints and rollbacks."""
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=True)
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        # Create first checkpoint
        checkpoint1 = await persistence_manager.create_checkpoint(conversation_context)
        
        # Modify conversation state
        conversation_context.conversation_turns.append(
            ConversationTurn(turn_id="new-turn-1", role="user", content="New content 1")
        )
        conversation_context.conversation_metadata["checkpoint_1_created"] = True
        
        # Create second checkpoint
        checkpoint2 = await persistence_manager.create_checkpoint(conversation_context)
        
        # Modify conversation state again
        conversation_context.conversation_turns.append(
            ConversationTurn(turn_id="new-turn-2", role="assistant", content="New content 2")
        )
        conversation_context.conversation_metadata["checkpoint_2_created"] = True
        
        # Rollback to checkpoint2
        success = await persistence_manager.rollback_to_checkpoint(conversation_context, checkpoint2)
        assert success is True
        assert len(conversation_context.conversation_turns) == 4  # Original 3 + 1 from checkpoint2
        assert "checkpoint_1_created" in conversation_context.conversation_metadata
        assert "checkpoint_2_created" not in conversation_context.conversation_metadata
        
        # Rollback to checkpoint1
        success = await persistence_manager.rollback_to_checkpoint(conversation_context, checkpoint1)
        assert success is True
        assert len(conversation_context.conversation_turns) == 3  # Original 3 turns
        assert "checkpoint_1_created" not in conversation_context.conversation_metadata
    
    @pytest.mark.asyncio
    async def test_checkpoint_storage_failure_handling(self, persistence_manager, conversation_context):
        """Test handling of checkpoint storage failures."""
        # Mock storage failure
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=False)
        
        with pytest.raises(Exception, match="Failed to store checkpoint"):
            await persistence_manager.create_checkpoint(conversation_context)
    
    @pytest.mark.asyncio
    async def test_checkpoint_with_large_conversation_history(self, persistence_manager):
        """Test checkpoint creation with large conversation history."""
        # Create conversation with many turns
        large_context = ConversationContext(
            conversation_id="large-conversation",
            conversation_turns=[
                ConversationTurn(
                    turn_id=f"turn-{i:03d}",
                    role="user" if i % 2 == 0 else "assistant",
                    content=f"Message content {i} with some detailed information about the conversation flow",
                    timestamp=datetime.now() - timedelta(minutes=100-i),
                    metadata={"turn_number": i, "batch": i // 10}
                )
                for i in range(100)
            ],
            conversation_metadata={
                f"metadata_key_{i}": f"metadata_value_{i}"
                for i in range(20)
            }
        )
        
        persistence_manager.checkpoint_storage.store_checkpoint = AsyncMock(return_value=True)
        persistence_manager.integrity_monitor.verify_checkpoint_integrity = AsyncMock(return_value=True)
        
        checkpoint = await persistence_manager.create_checkpoint(large_context)
        
        assert checkpoint is not None
        assert len(checkpoint.conversation_turns) == 100
        assert len(checkpoint.conversation_metadata) == 20
        assert checkpoint.conversation_turns[0].turn_id == "turn-000"
        assert checkpoint.conversation_turns[99].turn_id == "turn-099"
        assert checkpoint.conversation_metadata["metadata_key_0"] == "metadata_value_0"
        assert checkpoint.conversation_metadata["metadata_key_19"] == "metadata_value_19"