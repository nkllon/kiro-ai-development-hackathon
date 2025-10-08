"""
Claude Code Redis Task Queue Integration

This module provides Redis-backed task queue integration for Claude Code
using the Beast Mode Framework's ReflectiveModule pattern.
"""

from .models import (
    ConversationState,
    TaskState,
    StateTransitionTrigger,
    ConversationContext,
    TaskContext,
    StateCheckpoint,
    TaskQueueConfig,
    QueueConfig,
    TaskResult,
    TaskFailure,
)

from .state_machine import (
    ConversationStateMachine,
    TaskStateMachine,
)

from .persistence import (
    StatePersistenceManager,
    HotStateStorage,
    WarmStateStorage,
    ColdStateStorage,
    CheckpointStorage,
)

from .coordination import (
    DistributedConversationCoordinator,
    ConversationLock,
    ConsensusManager,
    ConflictResolver,
)

from .task_queue_manager import TaskQueueManager

from .state_protection import (
    StatePersistenceStrategy,
    EnhancedStateIntegrityMonitor,
    ConversationStateLockManager,
    PersistenceLayer,
    IntegrityStatus,
)

from .task_protection import (
    TaskDeduplicationManager,
    IdempotentTaskProcessor,
    PriorityTaskScheduler,
    TaskPriority,
    ProcessingStatus,
    TaskSecurityValidator,
    TaskExecutionSandbox,
    ConversationStateEncryption,
    SecurityThreatLevel,
    SecurityScanResult,
    SandboxExecutionResult,
)

__all__ = [
    # Models
    "ConversationState",
    "TaskState", 
    "StateTransitionTrigger",
    "ConversationContext",
    "TaskContext",
    "StateCheckpoint",
    "TaskQueueConfig",
    "QueueConfig",
    "TaskResult",
    "TaskFailure",
    
    # State Machines
    "ConversationStateMachine",
    "TaskStateMachine",
    
    # Persistence
    "StatePersistenceManager",
    "HotStateStorage",
    "WarmStateStorage", 
    "ColdStateStorage",
    "CheckpointStorage",
    
    # Coordination
    "DistributedConversationCoordinator",
    "ConversationLock",
    "ConsensusManager",
    "ConflictResolver",
    
    # Main Manager
    "TaskQueueManager",

    # State Protection
    "StatePersistenceStrategy",
    "EnhancedStateIntegrityMonitor",
    "ConversationStateLockManager",
    "PersistenceLayer",
    "IntegrityStatus",

    # Task Protection
    "TaskDeduplicationManager",
    "IdempotentTaskProcessor",
    "PriorityTaskScheduler",
    "TaskPriority",
    "ProcessingStatus",
    "TaskSecurityValidator",
    "TaskExecutionSandbox",
    "ConversationStateEncryption",
    "SecurityThreatLevel",
    "SecurityScanResult",
    "SandboxExecutionResult",
]