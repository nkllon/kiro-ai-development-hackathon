# State Model Architecture for Conversational Reliability
## Claude Code Redis Task Queue Integration

**Version:** 1.0
**Date:** 2025-09-23
**Status:** Draft

## Executive Summary

This document defines the state model architecture for reliable conversational AI interactions with Redis-backed task queues. The architecture implements a multi-layered state management system that ensures conversation continuity, task execution reliability, and system resilience through formal state machine modeling and distributed consistency patterns.

## Architecture Overview

### High-Level State Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Conversational State Machine                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  [IDLE] ──→ [TASK_PENDING] ──→ [TASK_EXECUTING] ──→ [TASK_COMPLETE] ──→ [IDLE] │
│     │            │                   │                      │              │
│     │            ▼                   ▼                      ▼              │
│     │       [QUEUE_CHECK]      [STATE_SNAPSHOT]     [STATE_PERSIST]       │
│     │            │                   │                      │              │
│     │            ▼                   ▼                      ▼              │
│     │      [HOOK_TRIGGERED]    [ERROR_RECOVERY]      [CLEANUP_TEMP]       │
│     │                               │                                      │
│     └─────────────────────────────── ▼ ─────────────────────────────────────┘
│                            [ROLLBACK_STATE]                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### State Persistence Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          State Persistence Architecture                     │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│   HOT LAYER     │   WARM LAYER    │   COLD LAYER    │   CHECKPOINT LAYER  │
│                 │                 │                 │                     │
│  Redis Memory   │  Redis Streams  │ Local Storage   │   Redis Snapshots   │
│  < 1ms access   │  < 10ms access  │ < 100ms access  │   Immutable State   │
│  TTL: 1 hour    │  TTL: 7 days    │ TTL: 30 days    │   TTL: 90 days      │
│                 │                 │                 │                     │
│ • Active State  │ • Conversation  │ • Archived      │ • Recovery Points   │
│ • Task Context  │   History       │   Sessions      │ • Audit Trail       │
│ • Session Data  │ • Event Log     │ • Cold Backups  │ • State Integrity   │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
```

## State Machine Specifications

### Core Conversation State Machine

```python
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
import asyncio
import time
import uuid
from datetime import datetime, timedelta

class ConversationState(Enum):
    """Primary conversation states"""
    IDLE = auto()
    TASK_PENDING = auto()
    TASK_EXECUTING = auto()
    TASK_COMPLETE = auto()
    ERROR_RECOVERY = auto()
    ROLLBACK_STATE = auto()
    HOOK_TRIGGERED = auto()
    QUEUE_CHECK = auto()
    STATE_SNAPSHOT = auto()
    STATE_PERSIST = auto()
    CLEANUP_TEMP = auto()

class StateTransitionTrigger(Enum):
    """State transition triggers"""
    HOOK_EXECUTION = auto()
    TASK_AVAILABLE = auto()
    TASK_START = auto()
    TASK_SUCCESS = auto()
    TASK_FAILURE = auto()
    ERROR_DETECTED = auto()
    RECOVERY_COMPLETE = auto()
    ROLLBACK_REQUIRED = auto()
    TIMEOUT_REACHED = auto()
    CLEANUP_REQUIRED = auto()

@dataclass
class ConversationContext:
    """Comprehensive conversation context state"""

    # Core identification
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_start: datetime = field(default_factory=datetime.now)

    # State tracking
    current_state: ConversationState = ConversationState.IDLE
    previous_state: Optional[ConversationState] = None
    state_history: List[tuple[ConversationState, datetime]] = field(default_factory=list)

    # Task execution context
    current_task: Optional['TaskContext'] = None
    task_queue: List['TaskContext'] = field(default_factory=list)
    completed_tasks: List['TaskResult'] = field(default_factory=list)
    failed_tasks: List['TaskFailure'] = field(default_factory=list)

    # Conversation data
    conversation_turns: List['ConversationTurn'] = field(default_factory=list)
    conversation_metadata: Dict[str, Any] = field(default_factory=dict)
    user_context: Dict[str, Any] = field(default_factory=dict)

    # State management
    checkpoints: List['StateCheckpoint'] = field(default_factory=list)
    state_version: int = 1
    last_persistence: Optional[datetime] = None
    dirty_state: bool = False

    # Error handling
    error_count: int = 0
    last_error: Optional['ConversationError'] = None
    recovery_attempts: int = 0

    # Performance tracking
    processing_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, Any] = field(default_factory=dict)

class ConversationStateMachine:
    """Formal state machine for conversation management"""

    def __init__(self, context: ConversationContext, persistence_manager: 'StatePersistenceManager'):
        self.context = context
        self.persistence = persistence_manager
        self.transition_handlers: Dict[tuple[ConversationState, StateTransitionTrigger], Callable] = {}
        self.state_validators: Dict[ConversationState, Callable] = {}
        self.state_entry_actions: Dict[ConversationState, Callable] = {}
        self.state_exit_actions: Dict[ConversationState, Callable] = {}

        self._setup_transition_table()
        self._setup_state_validators()
        self._setup_state_actions()

    def _setup_transition_table(self):
        """Define valid state transitions and their handlers"""

        transitions = {
            # Hook-triggered transitions
            (ConversationState.IDLE, StateTransitionTrigger.HOOK_EXECUTION):
                self._transition_to_hook_triggered,

            (ConversationState.HOOK_TRIGGERED, StateTransitionTrigger.TASK_AVAILABLE):
                self._transition_to_task_pending,

            (ConversationState.HOOK_TRIGGERED, StateTransitionTrigger.TIMEOUT_REACHED):
                self._transition_to_idle,

            # Task processing transitions
            (ConversationState.TASK_PENDING, StateTransitionTrigger.TASK_START):
                self._transition_to_state_snapshot,

            (ConversationState.STATE_SNAPSHOT, StateTransitionTrigger.TASK_START):
                self._transition_to_task_executing,

            (ConversationState.TASK_EXECUTING, StateTransitionTrigger.TASK_SUCCESS):
                self._transition_to_task_complete,

            (ConversationState.TASK_EXECUTING, StateTransitionTrigger.TASK_FAILURE):
                self._transition_to_error_recovery,

            # Success path
            (ConversationState.TASK_COMPLETE, StateTransitionTrigger.CLEANUP_REQUIRED):
                self._transition_to_state_persist,

            (ConversationState.STATE_PERSIST, StateTransitionTrigger.CLEANUP_REQUIRED):
                self._transition_to_cleanup_temp,

            (ConversationState.CLEANUP_TEMP, StateTransitionTrigger.CLEANUP_REQUIRED):
                self._transition_to_idle,

            # Error handling transitions
            (ConversationState.ERROR_RECOVERY, StateTransitionTrigger.ROLLBACK_REQUIRED):
                self._transition_to_rollback_state,

            (ConversationState.ERROR_RECOVERY, StateTransitionTrigger.RECOVERY_COMPLETE):
                self._transition_to_idle,

            (ConversationState.ROLLBACK_STATE, StateTransitionTrigger.RECOVERY_COMPLETE):
                self._transition_to_idle,

            # Queue check transitions
            (ConversationState.IDLE, StateTransitionTrigger.TIMEOUT_REACHED):
                self._transition_to_queue_check,

            (ConversationState.QUEUE_CHECK, StateTransitionTrigger.TASK_AVAILABLE):
                self._transition_to_task_pending,

            (ConversationState.QUEUE_CHECK, StateTransitionTrigger.TIMEOUT_REACHED):
                self._transition_to_idle
        }

        self.transition_handlers.update(transitions)

    async def trigger_transition(self, trigger: StateTransitionTrigger, **kwargs) -> bool:
        """Trigger a state transition with validation"""

        current_state = self.context.current_state
        transition_key = (current_state, trigger)

        if transition_key not in self.transition_handlers:
            logger.warning(f"Invalid transition: {current_state} -> {trigger}")
            return False

        try:
            # Record state before transition
            previous_state = current_state

            # Execute transition handler
            handler = self.transition_handlers[transition_key]
            success = await handler(**kwargs)

            if success:
                # Record state history
                self.context.state_history.append((previous_state, datetime.now()))
                self.context.previous_state = previous_state
                self.context.dirty_state = True

                logger.info(f"State transition: {previous_state} -> {self.context.current_state}")

                # Persist state if critical transition
                if self._is_critical_state(self.context.current_state):
                    await self.persistence.persist_state_immediately(self.context)

            return success

        except Exception as e:
            logger.error(f"State transition failed: {current_state} -> {trigger}: {e}")
            await self._handle_transition_error(e, current_state, trigger)
            return False

    async def _transition_to_hook_triggered(self, hook_event: 'HookEvent') -> bool:
        """Transition to hook triggered state"""

        await self._exit_state_actions(self.context.current_state)
        self.context.current_state = ConversationState.HOOK_TRIGGERED
        self.context.conversation_metadata['last_hook_event'] = hook_event.model_dump()
        await self._enter_state_actions(ConversationState.HOOK_TRIGGERED)

        return True

    async def _transition_to_task_pending(self, task: 'TaskContext') -> bool:
        """Transition to task pending state"""

        await self._exit_state_actions(self.context.current_state)
        self.context.current_state = ConversationState.TASK_PENDING
        self.context.current_task = task
        self.context.task_queue.append(task)
        await self._enter_state_actions(ConversationState.TASK_PENDING)

        return True

    async def _transition_to_state_snapshot(self) -> bool:
        """Transition to state snapshot creation"""

        await self._exit_state_actions(self.context.current_state)
        self.context.current_state = ConversationState.STATE_SNAPSHOT

        # Create checkpoint before task execution
        checkpoint = await self.persistence.create_checkpoint(self.context)
        self.context.checkpoints.append(checkpoint)

        await self._enter_state_actions(ConversationState.STATE_SNAPSHOT)
        return True

    async def _transition_to_task_executing(self) -> bool:
        """Transition to task executing state"""

        await self._exit_state_actions(self.context.current_state)
        self.context.current_state = ConversationState.TASK_EXECUTING

        if self.context.current_task:
            self.context.current_task.execution_start = datetime.now()

        await self._enter_state_actions(ConversationState.TASK_EXECUTING)
        return True

    async def _transition_to_task_complete(self, result: 'TaskResult') -> bool:
        """Transition to task complete state"""

        await self._exit_state_actions(self.context.current_state)
        self.context.current_state = ConversationState.TASK_COMPLETE

        if self.context.current_task:
            self.context.current_task.execution_end = datetime.now()

        self.context.completed_tasks.append(result)

        await self._enter_state_actions(ConversationState.TASK_COMPLETE)
        return True

    async def _transition_to_error_recovery(self, error: 'ConversationError') -> bool:
        """Transition to error recovery state"""

        await self._exit_state_actions(self.context.current_state)
        self.context.current_state = ConversationState.ERROR_RECOVERY
        self.context.last_error = error
        self.context.error_count += 1

        await self._enter_state_actions(ConversationState.ERROR_RECOVERY)
        return True

    async def _transition_to_rollback_state(self) -> bool:
        """Transition to rollback state"""

        await self._exit_state_actions(self.context.current_state)
        self.context.current_state = ConversationState.ROLLBACK_STATE

        # Execute rollback to last checkpoint
        if self.context.checkpoints:
            latest_checkpoint = self.context.checkpoints[-1]
            await self.persistence.rollback_to_checkpoint(self.context, latest_checkpoint)

        await self._enter_state_actions(ConversationState.ROLLBACK_STATE)
        return True

    async def _transition_to_idle(self) -> bool:
        """Transition to idle state"""

        await self._exit_state_actions(self.context.current_state)
        self.context.current_state = ConversationState.IDLE
        self.context.current_task = None

        await self._enter_state_actions(ConversationState.IDLE)
        return True

    def _is_critical_state(self, state: ConversationState) -> bool:
        """Check if state is critical and requires immediate persistence"""
        critical_states = {
            ConversationState.STATE_SNAPSHOT,
            ConversationState.TASK_EXECUTING,
            ConversationState.ERROR_RECOVERY,
            ConversationState.ROLLBACK_STATE
        }
        return state in critical_states
```

### Task Context State Model

```python
@dataclass
class TaskContext:
    """Complete task execution context with state tracking"""

    # Task identification
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""
    task_priority: str = "normal"

    # Task content
    task_content: str = ""
    task_parameters: Dict[str, Any] = field(default_factory=dict)
    task_metadata: Dict[str, Any] = field(default_factory=dict)

    # Execution tracking
    created_at: datetime = field(default_factory=datetime.now)
    claimed_at: Optional[datetime] = None
    execution_start: Optional[datetime] = None
    execution_end: Optional[datetime] = None

    # State management
    task_state: 'TaskState' = field(default_factory=lambda: TaskState.QUEUED)
    state_history: List[tuple['TaskState', datetime]] = field(default_factory=list)

    # Processing context
    processing_instance: Optional[str] = None
    conversation_context: Optional[str] = None
    checkpoint_refs: List[str] = field(default_factory=list)

    # Error handling
    execution_attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None

    # Resource tracking
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    processing_metrics: Dict[str, float] = field(default_factory=dict)

class TaskState(Enum):
    """Task lifecycle states"""
    QUEUED = auto()
    CLAIMED = auto()
    VALIDATED = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    RETRYING = auto()
    CANCELLED = auto()
    EXPIRED = auto()

class TaskStateMachine:
    """State machine for individual task lifecycle management"""

    def __init__(self, task_context: TaskContext):
        self.task_context = task_context
        self.valid_transitions = self._define_valid_transitions()

    def _define_valid_transitions(self) -> Dict[TaskState, List[TaskState]]:
        """Define valid state transitions for tasks"""
        return {
            TaskState.QUEUED: [TaskState.CLAIMED, TaskState.EXPIRED, TaskState.CANCELLED],
            TaskState.CLAIMED: [TaskState.VALIDATED, TaskState.QUEUED, TaskState.EXPIRED],
            TaskState.VALIDATED: [TaskState.EXECUTING, TaskState.FAILED],
            TaskState.EXECUTING: [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED],
            TaskState.FAILED: [TaskState.RETRYING, TaskState.CANCELLED],
            TaskState.RETRYING: [TaskState.VALIDATED, TaskState.CANCELLED],
            TaskState.COMPLETED: [],  # Terminal state
            TaskState.CANCELLED: [],  # Terminal state
            TaskState.EXPIRED: []     # Terminal state
        }

    async def transition_to(self, new_state: TaskState, reason: str = "") -> bool:
        """Transition task to new state with validation"""

        current_state = self.task_context.task_state

        if new_state not in self.valid_transitions[current_state]:
            logger.error(f"Invalid task transition: {current_state} -> {new_state}")
            return False

        # Record state history
        self.task_context.state_history.append((current_state, datetime.now()))

        # Update state
        self.task_context.task_state = new_state

        # State-specific actions
        await self._execute_state_actions(new_state, reason)

        logger.info(f"Task {self.task_context.task_id} transitioned: {current_state} -> {new_state}")
        return True

    async def _execute_state_actions(self, state: TaskState, reason: str):
        """Execute actions when entering a state"""

        now = datetime.now()

        if state == TaskState.CLAIMED:
            self.task_context.claimed_at = now

        elif state == TaskState.EXECUTING:
            self.task_context.execution_start = now
            self.task_context.execution_attempts += 1

        elif state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
            self.task_context.execution_end = now

        elif state == TaskState.RETRYING:
            # Reset for retry
            self.task_context.execution_start = None
            self.task_context.execution_end = None
```

### State Persistence Manager

```python
class StatePersistenceManager:
    """Manages multi-layered state persistence with reliability guarantees"""

    def __init__(self, redis_client, config: 'PersistenceConfig'):
        self.redis = redis_client
        self.config = config
        self.hot_storage = HotStateStorage(redis_client)
        self.warm_storage = WarmStateStorage(redis_client)
        self.cold_storage = ColdStateStorage()
        self.checkpoint_storage = CheckpointStorage(redis_client)

    async def persist_conversation_state(self, context: ConversationContext) -> bool:
        """Persist conversation state across all layers"""

        try:
            # Serialize state with compression
            state_data = self._serialize_state(context)

            # Persist to hot storage (immediate access)
            await self.hot_storage.store(context.conversation_id, state_data)

            # Persist to warm storage (history)
            await self.warm_storage.append_state_event(
                context.conversation_id,
                {
                    "state": context.current_state.name,
                    "timestamp": datetime.now().isoformat(),
                    "version": context.state_version,
                    "metadata": context.conversation_metadata
                }
            )

            # Update persistence tracking
            context.last_persistence = datetime.now()
            context.dirty_state = False

            return True

        except Exception as e:
            logger.error(f"State persistence failed: {e}")
            return False

    async def create_checkpoint(self, context: ConversationContext) -> 'StateCheckpoint':
        """Create immutable state checkpoint"""

        checkpoint_id = f"checkpoint_{context.conversation_id}_{int(time.time())}"

        # Create deep copy of current state
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "conversation_id": context.conversation_id,
            "state": context.current_state.name,
            "conversation_turns": [turn.model_dump() for turn in context.conversation_turns],
            "conversation_metadata": context.conversation_metadata.copy(),
            "task_context": context.current_task.model_dump() if context.current_task else None,
            "state_version": context.state_version,
            "created_at": datetime.now().isoformat(),
            "hash": self._calculate_state_hash(context)
        }

        # Store checkpoint immutably
        await self.checkpoint_storage.store_checkpoint(checkpoint_id, checkpoint_data)

        checkpoint = StateCheckpoint(
            checkpoint_id=checkpoint_id,
            conversation_id=context.conversation_id,
            created_at=datetime.now(),
            state_hash=checkpoint_data["hash"]
        )

        return checkpoint

    async def rollback_to_checkpoint(self, context: ConversationContext, checkpoint: 'StateCheckpoint') -> bool:
        """Rollback conversation to specific checkpoint"""

        try:
            # Retrieve checkpoint data
            checkpoint_data = await self.checkpoint_storage.get_checkpoint(checkpoint.checkpoint_id)

            if not checkpoint_data:
                raise CheckpointNotFoundError(f"Checkpoint {checkpoint.checkpoint_id} not found")

            # Verify checkpoint integrity
            if not self._verify_checkpoint_integrity(checkpoint_data):
                raise CheckpointCorruptionError(f"Checkpoint {checkpoint.checkpoint_id} is corrupted")

            # Restore conversation state
            context.current_state = ConversationState[checkpoint_data["state"]]
            context.conversation_turns = [
                ConversationTurn.parse_obj(turn) for turn in checkpoint_data["conversation_turns"]
            ]
            context.conversation_metadata = checkpoint_data["conversation_metadata"]

            if checkpoint_data["task_context"]:
                context.current_task = TaskContext.parse_obj(checkpoint_data["task_context"])
            else:
                context.current_task = None

            context.state_version = checkpoint_data["state_version"] + 1
            context.dirty_state = True

            # Log rollback event
            await self._log_rollback_event(context, checkpoint)

            logger.info(f"Rolled back conversation {context.conversation_id} to checkpoint {checkpoint.checkpoint_id}")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def _serialize_state(self, context: ConversationContext) -> bytes:
        """Serialize conversation state with compression"""

        state_dict = {
            "conversation_id": context.conversation_id,
            "current_state": context.current_state.name,
            "conversation_turns": [turn.model_dump() for turn in context.conversation_turns],
            "conversation_metadata": context.conversation_metadata,
            "state_version": context.state_version,
            "serialized_at": datetime.now().isoformat()
        }

        # Serialize and compress
        json_data = json.dumps(state_dict, sort_keys=True)
        compressed_data = gzip.compress(json_data.encode('utf-8'))

        return compressed_data

    def _calculate_state_hash(self, context: ConversationContext) -> str:
        """Calculate hash of conversation state for integrity checking"""

        hash_data = {
            "conversation_id": context.conversation_id,
            "state": context.current_state.name,
            "turns_count": len(context.conversation_turns),
            "metadata_keys": sorted(context.conversation_metadata.keys()),
            "state_version": context.state_version
        }

        hash_json = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_json.encode()).hexdigest()
```

### Distributed Consistency Model

```python
class DistributedConversationCoordinator:
    """Coordinates conversation state across multiple Claude instances"""

    def __init__(self, redis_client, instance_id: str):
        self.redis = redis_client
        self.instance_id = instance_id
        self.consensus_manager = ConsensusManager(redis_client)
        self.conflict_resolver = ConflictResolver()

    async def coordinate_conversation_access(self, conversation_id: str) -> 'ConversationLock':
        """Coordinate exclusive access to conversation across instances"""

        lock_key = f"conversation:lock:{conversation_id}"
        lease_duration = 30  # 30 seconds

        # Attempt to acquire distributed lock
        lock_acquired = await self.redis.set(
            lock_key,
            f"{self.instance_id}:{time.time()}",
            nx=True,  # Only if not exists
            ex=lease_duration
        )

        if not lock_acquired:
            # Check if lock is expired and can be claimed
            current_lock = await self.redis.get(lock_key)
            if current_lock and self._is_lock_expired(current_lock, lease_duration):
                await self.redis.delete(lock_key)
                return await self.coordinate_conversation_access(conversation_id)
            else:
                raise ConversationLockError(f"Cannot acquire lock for conversation {conversation_id}")

        # Create and return lock object
        lock = ConversationLock(
            conversation_id=conversation_id,
            instance_id=self.instance_id,
            acquired_at=datetime.now(),
            lease_duration=timedelta(seconds=lease_duration)
        )

        # Start lease renewal background task
        asyncio.create_task(self._maintain_conversation_lock(lock))

        return lock

    async def resolve_state_conflicts(self, conversation_id: str, conflicted_states: List['ConversationContext']) -> ConversationContext:
        """Resolve conflicts when multiple instances modify the same conversation"""

        if len(conflicted_states) <= 1:
            return conflicted_states[0] if conflicted_states else None

        # Use vector clocks for conflict resolution
        canonical_state = await self.conflict_resolver.resolve_using_vector_clocks(conflicted_states)

        # If vector clocks are inconclusive, use timestamp-based resolution
        if not canonical_state:
            canonical_state = self.conflict_resolver.resolve_by_latest_timestamp(conflicted_states)

        # Persist resolved state
        await self._propagate_resolved_state(conversation_id, canonical_state)

        return canonical_state

    async def _maintain_conversation_lock(self, lock: 'ConversationLock'):
        """Maintain conversation lock through periodic renewal"""

        renewal_interval = lock.lease_duration.total_seconds() / 3  # Renew at 1/3 intervals

        while lock.active:
            try:
                await asyncio.sleep(renewal_interval)

                # Check if we still own the lock
                lock_key = f"conversation:lock:{lock.conversation_id}"
                current_lock = await self.redis.get(lock_key)

                if current_lock and current_lock.startswith(self.instance_id):
                    # Renew the lock
                    await self.redis.expire(lock_key, lock.lease_duration.total_seconds())
                else:
                    # We've lost the lock
                    lock.active = False
                    logger.warning(f"Lost conversation lock for {lock.conversation_id}")
                    break

            except Exception as e:
                logger.error(f"Lock maintenance failed: {e}")
                lock.active = False
                break

class ConsensusManager:
    """Manages distributed consensus for conversation state decisions"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.consensus_timeout = 5.0  # 5 seconds

    async def achieve_consensus(self, conversation_id: str, proposed_action: 'ConversationAction') -> bool:
        """Achieve consensus across participating instances for conversation actions"""

        consensus_id = f"consensus_{conversation_id}_{int(time.time())}"

        # Publish proposal to all instances
        await self.redis.publish(
            f"consensus_channel_{conversation_id}",
            json.dumps({
                "consensus_id": consensus_id,
                "proposed_action": proposed_action.model_dump(),
                "proposer": self.instance_id,
                "timestamp": time.time()
            })
        )

        # Collect votes with timeout
        votes = await self._collect_consensus_votes(consensus_id, conversation_id)

        # Determine consensus result
        total_votes = len(votes)
        approve_votes = sum(1 for vote in votes if vote["decision"] == "approve")

        consensus_achieved = approve_votes > total_votes / 2

        # Record consensus result
        await self.redis.hset(
            f"consensus_result_{consensus_id}",
            mapping={
                "conversation_id": conversation_id,
                "consensus_achieved": consensus_achieved,
                "total_votes": total_votes,
                "approve_votes": approve_votes,
                "timestamp": time.time()
            }
        )

        return consensus_achieved

    async def _collect_consensus_votes(self, consensus_id: str, conversation_id: str) -> List[Dict]:
        """Collect consensus votes from participating instances"""

        votes = []
        vote_collection_key = f"consensus_votes_{consensus_id}"

        # Wait for votes with timeout
        start_time = time.time()

        while time.time() - start_time < self.consensus_timeout:
            # Check for new votes
            vote_data = await self.redis.lpop(vote_collection_key)

            if vote_data:
                vote = json.loads(vote_data)
                votes.append(vote)
            else:
                # No votes available, wait briefly
                await asyncio.sleep(0.1)

        return votes
```

## Implementation Guidelines

### State Machine Integration with Claude Code Hooks

```python
class ClaudeCodeStateIntegration:
    """Integration layer between Claude Code hooks and state machine"""

    def __init__(self, state_machine: ConversationStateMachine, task_processor: 'TaskProcessor'):
        self.state_machine = state_machine
        self.task_processor = task_processor

    async def setup_hook_integration(self):
        """Setup Claude Code hooks with state machine integration"""

        @hook.on_event("UserPromptSubmit")
        async def on_user_prompt(hook_context):
            """Handle user prompt submission with state management"""

            # Trigger state machine
            await self.state_machine.trigger_transition(
                StateTransitionTrigger.HOOK_EXECUTION,
                hook_event=HookEvent(
                    event_type="UserPromptSubmit",
                    context=hook_context,
                    timestamp=datetime.now()
                )
            )

            # Check for tasks if in appropriate state
            if self.state_machine.context.current_state == ConversationState.HOOK_TRIGGERED:
                await self._check_and_process_tasks()

        @hook.on_event("PreToolUse")
        async def on_pre_tool_use(hook_context):
            """Handle pre-tool use with state checkpoint"""

            # Create checkpoint before tool execution
            if self.state_machine.context.current_state == ConversationState.IDLE:
                await self.state_machine.trigger_transition(
                    StateTransitionTrigger.HOOK_EXECUTION,
                    hook_event=HookEvent(
                        event_type="PreToolUse",
                        context=hook_context,
                        timestamp=datetime.now()
                    )
                )

        @hook.on_event("PostToolUse")
        async def on_post_tool_use(hook_context, result):
            """Handle post-tool use with state persistence"""

            # Update conversation state with tool result
            if result.success:
                await self._record_successful_tool_use(result)
            else:
                await self._handle_tool_failure(result)

            # Return to idle state
            await self.state_machine.trigger_transition(StateTransitionTrigger.CLEANUP_REQUIRED)

    async def _check_and_process_tasks(self):
        """Check Redis queue and process available tasks"""

        try:
            # Peek at task queue (non-blocking)
            task_data = await self.redis.lindex("task:queue", 0)

            if task_data:
                # Parse task
                task_dict = json.loads(task_data)
                task = TaskContext.parse_obj(task_dict)

                # Claim task atomically
                if await self._claim_task_atomically(task.task_id):
                    # Transition to task processing
                    await self.state_machine.trigger_transition(
                        StateTransitionTrigger.TASK_AVAILABLE,
                        task=task
                    )

                    # Process task
                    await self._process_task_with_state_management(task)
            else:
                # No tasks available, return to idle
                await self.state_machine.trigger_transition(StateTransitionTrigger.TIMEOUT_REACHED)

        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            await self.state_machine.trigger_transition(
                StateTransitionTrigger.ERROR_DETECTED,
                error=ConversationError(message=str(e), error_type="task_processing")
            )

    async def _process_task_with_state_management(self, task: TaskContext):
        """Process task with comprehensive state management"""

        try:
            # Transition to task execution
            await self.state_machine.trigger_transition(StateTransitionTrigger.TASK_START)

            # Execute task
            result = await self.task_processor.execute_task(task)

            # Handle result
            if result.success:
                await self.state_machine.trigger_transition(
                    StateTransitionTrigger.TASK_SUCCESS,
                    result=result
                )
            else:
                await self.state_machine.trigger_transition(
                    StateTransitionTrigger.TASK_FAILURE,
                    error=ConversationError(
                        message=f"Task execution failed: {result.error_message}",
                        error_type="task_execution"
                    )
                )

        except Exception as e:
            logger.error(f"Task execution error: {e}")
            await self.state_machine.trigger_transition(
                StateTransitionTrigger.TASK_FAILURE,
                error=ConversationError(message=str(e), error_type="task_execution")
            )
```

## Monitoring and Observability

### State Machine Metrics

```python
class StateMetricsCollector:
    """Collect and report state machine metrics"""

    def __init__(self, metrics_client):
        self.metrics = metrics_client
        self.state_durations = {}
        self.transition_counts = {}

    async def record_state_transition(self, from_state: ConversationState, to_state: ConversationState, duration: float):
        """Record state transition metrics"""

        # Record transition count
        transition_key = f"{from_state.name}_to_{to_state.name}"
        self.transition_counts[transition_key] = self.transition_counts.get(transition_key, 0) + 1

        self.metrics.counter("conversation_state_transitions").labels(
            from_state=from_state.name,
            to_state=to_state.name
        ).inc()

        # Record state duration
        if from_state in self.state_durations:
            self.metrics.histogram("conversation_state_duration").labels(
                state=from_state.name
            ).observe(duration)

    async def record_state_health(self, context: ConversationContext):
        """Record overall state machine health metrics"""

        self.metrics.gauge("conversation_active_states").labels(
            state=context.current_state.name
        ).set(1)

        self.metrics.gauge("conversation_error_count").labels(
            conversation_id=context.conversation_id
        ).set(context.error_count)

        self.metrics.gauge("conversation_checkpoint_count").labels(
            conversation_id=context.conversation_id
        ).set(len(context.checkpoints))
```

## Conclusion

This state model architecture provides a robust foundation for reliable conversational AI interactions with Redis-backed task queues. The formal state machine approach ensures predictable behavior, comprehensive error handling, and system resilience through:

1. **Formal State Management** - Well-defined states and transitions prevent invalid system behaviors
2. **Multi-Layer Persistence** - Hot/warm/cold storage strategy ensures data durability and performance
3. **Distributed Coordination** - Consensus mechanisms and conflict resolution for multi-instance deployments
4. **Comprehensive Error Handling** - Automatic rollback and recovery capabilities
5. **Production Observability** - Detailed metrics and monitoring for operational excellence

The architecture scales from single-instance development environments to production-ready distributed deployments while maintaining conversation continuity and task execution reliability.