"""
Core data models for Claude Code Redis Task Queue Integration

This module defines the comprehensive data models and enumerations
for conversation state management, task processing, and system configuration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Union, Set
import uuid


class ConversationState(Enum):
    """Primary conversation states from architecture specification."""
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


class TaskState(Enum):
    """Task lifecycle states."""
    QUEUED = auto()
    CLAIMED = auto()
    VALIDATED = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    RETRYING = auto()
    CANCELLED = auto()
    EXPIRED = auto()


class StateTransitionTrigger(Enum):
    """State transition triggers."""
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
class ConversationTurn:
    """Individual conversation turn data."""
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    role: str = ""  # "user", "assistant", "system"
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateCheckpoint:
    """Immutable state checkpoint for rollback capability."""
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    state_hash: str = ""
    conversation_turns: List[ConversationTurn] = field(default_factory=list)
    conversation_metadata: Dict[str, Any] = field(default_factory=dict)
    task_context: Optional[Dict[str, Any]] = None
    integrity_verified: bool = False


@dataclass
class TaskContext:
    """Complete task execution context with state tracking."""
    
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
    task_state: TaskState = field(default_factory=lambda: TaskState.QUEUED)
    state_history: List[tuple[TaskState, datetime]] = field(default_factory=list)

    # Processing context
    processing_instance: Optional[str] = None
    conversation_context: Optional[str] = None
    checkpoint_refs: List[str] = field(default_factory=list)


@dataclass
class ConversationContext:
    """Comprehensive conversation context state based on architecture specification."""
    
    # Core identification
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_start: datetime = field(default_factory=datetime.now)

    # State tracking
    current_state: ConversationState = ConversationState.IDLE
    previous_state: Optional[ConversationState] = None
    state_history: List[tuple[ConversationState, datetime]] = field(default_factory=list)

    # Task execution context
    current_task: Optional[TaskContext] = None
    task_queue: List[TaskContext] = field(default_factory=list)
    completed_tasks: List["TaskResult"] = field(default_factory=list)
    failed_tasks: List["TaskFailure"] = field(default_factory=list)

    # Conversation data
    conversation_turns: List[ConversationTurn] = field(default_factory=list)
    conversation_metadata: Dict[str, Any] = field(default_factory=dict)
    user_context: Dict[str, Any] = field(default_factory=dict)

    # State management
    checkpoints: List[StateCheckpoint] = field(default_factory=list)
    state_version: int = 1
    last_persistence: Optional[datetime] = None
    dirty_state: bool = False


@dataclass
class TaskResult:
    """Task execution result."""
    task_id: str
    success: bool
    result_data: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    completed_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None


@dataclass
class TaskFailure:
    """Task execution failure information."""
    task_id: str
    error_type: str
    error_message: str
    failed_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    recoverable: bool = True
    stack_trace: Optional[str] = None


@dataclass
class RetryPolicy:
    """Task retry policy configuration."""
    max_retries: int = 3
    backoff_multiplier: float = 2.0
    max_backoff_seconds: int = 60
    retry_on_errors: List[str] = field(default_factory=lambda: ["ConnectionError", "TimeoutError"])


@dataclass
class QueueConfig:
    """Individual queue configuration."""
    name: str
    priority: int
    max_concurrent_tasks: int
    task_timeout_seconds: int
    retry_policy: RetryPolicy
    dead_letter_queue: Optional[str] = None


@dataclass
class RedisConfig:
    """Redis connection configuration."""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    ssl: bool = False
    connection_pool_size: int = 10
    socket_timeout: float = 2.0
    socket_connect_timeout: float = 2.0


@dataclass
class PerformanceLimits:
    """Performance and resource limits."""
    task_retrieval_timeout_ms: int = 100
    checkpoint_creation_timeout_ms: int = 50
    max_conversation_history_turns: int = 100
    max_memory_usage_mb: int = 512
    max_cpu_time_seconds: int = 30


@dataclass
class SecuritySettings:
    """Security configuration settings."""
    validate_task_content: bool = True
    sanitize_inputs: bool = True
    max_payload_size_bytes: int = 1048576  # 1MB
    allowed_task_types: List[str] = field(default_factory=lambda: [
        "code_generation", "file_analysis", "documentation", "testing", "refactoring"
    ])
    dangerous_patterns: List[str] = field(default_factory=lambda: [
        r'eval\s*\(', r'exec\s*\(', r'__import__\s*\(', r'subprocess\.', r'os\.system'
    ])


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    prometheus_enabled: bool = True
    prometheus_port: int = 8000
    log_level: str = "INFO"
    structured_logging: bool = True
    correlation_ids: bool = True


@dataclass
class PersistenceConfig:
    """Multi-layer persistence configuration."""
    hot_storage_ttl_hours: int = 1
    warm_storage_ttl_days: int = 7
    cold_storage_ttl_days: int = 30
    checkpoint_storage_ttl_days: int = 90
    enable_compression: bool = True
    integrity_checking: bool = True


@dataclass
class CoordinationConfig:
    """Distributed coordination configuration."""
    lock_timeout_seconds: int = 30
    lease_duration_seconds: int = 60
    coordination_enabled: bool = True
    vector_clock_enabled: bool = True
    conflict_resolution_strategy: str = "timestamp_latest"
    max_coordination_retries: int = 3


@dataclass
class TaskQueueConfig:
    """Configuration for task queue system."""
    redis_config: RedisConfig
    queue_configs: List[QueueConfig]
    performance_limits: PerformanceLimits
    security_settings: SecuritySettings
    monitoring_config: MonitoringConfig
    persistence_config: PersistenceConfig
    
    def validate(self) -> "ValidationResult":
        """Validate configuration parameters."""
        errors = []
        warnings = []
        
        # Validate Redis config
        if not self.redis_config.host:
            errors.append("Redis host is required")
        if self.redis_config.port <= 0 or self.redis_config.port > 65535:
            errors.append("Redis port must be between 1 and 65535")
            
        # Validate queue configs
        if not self.queue_configs:
            errors.append("At least one queue configuration is required")
        
        queue_names = set()
        for queue_config in self.queue_configs:
            if not queue_config.name:
                errors.append("Queue name is required")
            if queue_config.name in queue_names:
                errors.append(f"Duplicate queue name: {queue_config.name}")
            queue_names.add(queue_config.name)
            
            if queue_config.max_concurrent_tasks <= 0:
                errors.append(f"Queue {queue_config.name}: max_concurrent_tasks must be positive")
            if queue_config.task_timeout_seconds <= 0:
                errors.append(f"Queue {queue_config.name}: task_timeout_seconds must be positive")
                
        # Validate performance limits
        if self.performance_limits.task_retrieval_timeout_ms <= 0:
            errors.append("task_retrieval_timeout_ms must be positive")
        if self.performance_limits.checkpoint_creation_timeout_ms <= 0:
            errors.append("checkpoint_creation_timeout_ms must be positive")
            
        # Validate security settings
        if self.security_settings.max_payload_size_bytes <= 0:
            errors.append("max_payload_size_bytes must be positive")
        if not self.security_settings.allowed_task_types:
            warnings.append("No allowed task types specified - all tasks will be rejected")
            
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


@dataclass
class ValidationResult:
    """Configuration validation result."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class TaskProcessingResult:
    """Result of task processing operation."""
    tasks_processed: int = 0
    tasks_failed: int = 0
    processing_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class HookEvent:
    """Hook execution event data."""
    event_type: str
    event_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)