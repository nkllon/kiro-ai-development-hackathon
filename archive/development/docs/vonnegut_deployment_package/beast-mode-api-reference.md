# Beast Mode Framework: API Reference

## Table of Contents
1. [Core Models](#core-models)
2. [Task Queue System](#task-queue-system)
3. [State Management](#state-management)
4. [Persistence Layer](#persistence-layer)
5. [Coordination & Distribution](#coordination--distribution)
6. [Configuration](#configuration)
7. [Monitoring & Health](#monitoring--health)
8. [Error Handling](#error-handling)
9. [Examples](#examples)

## Core Models

### TaskContext

The primary data structure for task execution context.

```python
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
```

**Usage Example:**
```python
from beast_mode.task_queue.models import TaskContext, TaskState

# Create a new task
task = TaskContext(
    task_type="data_processing",
    task_content="Process customer data",
    task_parameters={
        "input_file": "customers.csv",
        "output_format": "parquet",
        "batch_size": 1000
    },
    task_priority="high"
)

# Check task state
if task.task_state == TaskState.QUEUED:
    print("Task is ready for execution")
```

### ConversationContext

Manages conversation state and task coordination.

```python
@dataclass
class ConversationContext:
    """Comprehensive conversation context state."""

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
    completed_tasks: List[TaskResult] = field(default_factory=list)
    failed_tasks: List[TaskFailure] = field(default_factory=list)
```

**Usage Example:**
```python
from beast_mode.task_queue.models import ConversationContext, ConversationState

# Create conversation context
conversation = ConversationContext()

# Add task to queue
task = TaskContext(task_type="code_generation", task_content="Generate API endpoint")
conversation.task_queue.append(task)

# Transition to task pending state
conversation.current_state = ConversationState.TASK_PENDING
```

### State Enumerations

#### TaskState

```python
class TaskState(Enum):
    """Task lifecycle states."""
    QUEUED = auto()      # Task is in queue waiting for execution
    CLAIMED = auto()     # Task has been claimed by a worker
    VALIDATED = auto()   # Task has passed validation
    EXECUTING = auto()   # Task is currently being executed
    COMPLETED = auto()   # Task completed successfully
    FAILED = auto()      # Task failed during execution
    RETRYING = auto()    # Task is being retried after failure
    CANCELLED = auto()   # Task was cancelled before completion
    EXPIRED = auto()     # Task expired before execution
```

#### ConversationState

```python
class ConversationState(Enum):
    """Primary conversation states."""
    IDLE = auto()           # No active tasks
    TASK_PENDING = auto()   # Task queued for execution
    TASK_EXECUTING = auto() # Task currently executing
    TASK_COMPLETE = auto()  # Task completed
    ERROR_RECOVERY = auto() # Recovering from error
    ROLLBACK_STATE = auto() # Rolling back to previous state
    HOOK_TRIGGERED = auto() # Hook execution in progress
    QUEUE_CHECK = auto()    # Checking task queue
    STATE_SNAPSHOT = auto() # Creating state snapshot
    STATE_PERSIST = auto()  # Persisting state
    CLEANUP_TEMP = auto()   # Cleaning up temporary resources
```

## Task Queue System

### TaskQueueManager

Primary interface for task queue operations.

```python
class TaskQueueManager:
    """Main task queue management interface."""

    def __init__(self, config: TaskQueueConfig):
        """Initialize task queue manager with configuration."""

    async def initialize(self) -> None:
        """Initialize the task queue system."""

    async def submit_task(self, task: TaskContext) -> str:
        """Submit a task to the queue."""

    async def claim_task(self, worker_id: str) -> Optional[TaskContext]:
        """Claim the next available task."""

    async def complete_task(self, task_id: str, result: TaskResult) -> None:
        """Mark task as completed with result."""

    async def fail_task(self, task_id: str, failure: TaskFailure) -> None:
        """Mark task as failed."""

    async def get_task_status(self, task_id: str) -> Optional[TaskState]:
        """Get current status of a task."""

    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics."""

    async def cleanup(self) -> None:
        """Clean up resources."""
```

**Usage Example:**
```python
from beast_mode.task_queue import TaskQueueManager
from beast_mode.task_queue.models import TaskQueueConfig, RedisConfig

# Configuration
config = TaskQueueConfig(
    redis_config=RedisConfig(
        host="localhost",
        port=6379
    ),
    queue_configs=[
        QueueConfig(
            name="default",
            priority=1,
            max_concurrent_tasks=10,
            task_timeout_seconds=300,
            retry_policy=RetryPolicy(max_retries=3)
        )
    ],
    performance_limits=PerformanceLimits(),
    security_settings=SecuritySettings(),
    monitoring_config=MonitoringConfig(),
    persistence_config=PersistenceConfig()
)

# Initialize and use queue
async def example_usage():
    queue_manager = TaskQueueManager(config)
    await queue_manager.initialize()

    try:
        # Submit a task
        task = TaskContext(
            task_type="data_processing",
            task_content="Process uploaded file",
            task_parameters={"file_path": "/tmp/upload.csv"}
        )

        task_id = await queue_manager.submit_task(task)
        print(f"Task submitted: {task_id}")

        # Check status
        status = await queue_manager.get_task_status(task_id)
        print(f"Task status: {status}")

        # Get queue statistics
        stats = await queue_manager.get_queue_stats()
        print(f"Queue stats: {stats}")

    finally:
        await queue_manager.cleanup()
```

### TaskRegistry

Registry for task handlers.

```python
class TaskRegistry:
    """Registry for task type handlers."""

    @classmethod
    def register(cls, task_type: str):
        """Decorator to register a task handler."""
        def decorator(handler_class):
            cls._handlers[task_type] = handler_class
            return handler_class
        return decorator

    @classmethod
    def get_handler(cls, task_type: str) -> Optional[Type]:
        """Get handler class for task type."""
        return cls._handlers.get(task_type)

    @classmethod
    def list_registered_handlers(cls) -> List[str]:
        """List all registered task types."""
        return list(cls._handlers.keys())
```

**Usage Example:**
```python
from beast_mode.task_queue import TaskRegistry

@TaskRegistry.register("email_notification")
class EmailNotificationHandler:
    async def execute(self, task: TaskContext) -> TaskResult:
        # Send email notification
        await send_email(
            to=task.task_parameters["recipient"],
            subject=task.task_parameters["subject"],
            body=task.task_content
        )

        return TaskResult(
            task_id=task.task_id,
            success=True,
            result_data={"email_sent": True},
            execution_time_ms=150.0
        )

# Check registered handlers
handlers = TaskRegistry.list_registered_handlers()
print(f"Registered handlers: {handlers}")
```

## State Management

### ConversationStateMachine

Manages conversation state transitions.

```python
class ConversationStateMachine:
    """State machine for conversation state management."""

    def __init__(self, context: ConversationContext):
        """Initialize with conversation context."""

    async def transition_to(
        self,
        new_state: ConversationState,
        trigger: StateTransitionTrigger
    ) -> bool:
        """Attempt to transition to new state."""

    def can_transition_to(self, new_state: ConversationState) -> bool:
        """Check if transition to new state is valid."""

    def get_valid_transitions(self) -> List[ConversationState]:
        """Get list of valid transitions from current state."""

    def get_state_history(self) -> List[Tuple[ConversationState, datetime]]:
        """Get history of state transitions."""
```

**Usage Example:**
```python
from beast_mode.task_queue.state_machine import ConversationStateMachine
from beast_mode.task_queue.models import ConversationContext, ConversationState, StateTransitionTrigger

# Create state machine
context = ConversationContext()
state_machine = ConversationStateMachine(context)

# Check valid transitions
valid_transitions = state_machine.get_valid_transitions()
print(f"Valid transitions: {valid_transitions}")

# Transition state
if state_machine.can_transition_to(ConversationState.TASK_PENDING):
    success = await state_machine.transition_to(
        ConversationState.TASK_PENDING,
        StateTransitionTrigger.TASK_AVAILABLE
    )
    if success:
        print("State transition successful")
```

### TaskStateMachine

Manages individual task state transitions.

```python
class TaskStateMachine:
    """State machine for task lifecycle management."""

    def __init__(self, task: TaskContext):
        """Initialize with task context."""

    async def transition_to(self, new_state: TaskState) -> bool:
        """Attempt to transition task to new state."""

    def can_transition_to(self, new_state: TaskState) -> bool:
        """Check if transition is valid."""

    def get_execution_duration(self) -> Optional[float]:
        """Get task execution duration in seconds."""
```

## Persistence Layer

### StatePersistenceManager

Multi-layer persistence for conversation and task state.

```python
class StatePersistenceManager:
    """Multi-layer persistence manager."""

    def __init__(self, config: PersistenceConfig):
        """Initialize persistence manager."""

    async def save_conversation_state(
        self,
        conversation: ConversationContext
    ) -> None:
        """Save conversation state to appropriate storage layer."""

    async def load_conversation_state(
        self,
        conversation_id: str
    ) -> Optional[ConversationContext]:
        """Load conversation state from storage."""

    async def create_checkpoint(
        self,
        conversation: ConversationContext
    ) -> StateCheckpoint:
        """Create immutable state checkpoint."""

    async def restore_from_checkpoint(
        self,
        checkpoint_id: str
    ) -> Optional[ConversationContext]:
        """Restore conversation from checkpoint."""

    async def cleanup_expired_data(self) -> None:
        """Clean up expired data from all storage layers."""
```

**Usage Example:**
```python
from beast_mode.task_queue.persistence import StatePersistenceManager
from beast_mode.task_queue.models import PersistenceConfig

# Configure persistence
persistence_config = PersistenceConfig(
    hot_storage_ttl_hours=1,
    warm_storage_ttl_days=7,
    cold_storage_ttl_days=30,
    enable_compression=True,
    integrity_checking=True
)

persistence_manager = StatePersistenceManager(persistence_config)

# Save conversation state
conversation = ConversationContext()
await persistence_manager.save_conversation_state(conversation)

# Create checkpoint for rollback capability
checkpoint = await persistence_manager.create_checkpoint(conversation)
print(f"Checkpoint created: {checkpoint.checkpoint_id}")

# Load state later
loaded_conversation = await persistence_manager.load_conversation_state(
    conversation.conversation_id
)
```

### Storage Layers

#### HotStateStorage
- **Purpose**: Active conversation state (Redis)
- **TTL**: 1 hour (configurable)
- **Access**: Immediate, high-performance

#### WarmStateStorage
- **Purpose**: Recent conversation history (Database)
- **TTL**: 7 days (configurable)
- **Access**: Fast, queryable

#### ColdStateStorage
- **Purpose**: Long-term archival (Object storage)
- **TTL**: 30 days (configurable)
- **Access**: Slower, cost-optimized

## Coordination & Distribution

### DistributedConversationCoordinator

Manages distributed conversation coordination.

```python
class DistributedConversationCoordinator:
    """Distributed coordination for conversation management."""

    async def acquire_conversation_lock(
        self,
        conversation_id: str,
        instance_id: str,
        timeout: float = 30.0
    ) -> ConversationLock:
        """Acquire exclusive lock on conversation."""

    async def release_conversation_lock(
        self,
        lock: ConversationLock
    ) -> None:
        """Release conversation lock."""

    async def achieve_consensus(
        self,
        conversation_id: str,
        proposed_state: ConversationState
    ) -> bool:
        """Achieve consensus on state change."""

    async def resolve_conflict(
        self,
        conversation_id: str,
        conflicting_states: List[ConversationState]
    ) -> ConversationState:
        """Resolve state conflicts using defined strategy."""
```

**Usage Example:**
```python
from beast_mode.task_queue.coordination import DistributedConversationCoordinator

coordinator = DistributedConversationCoordinator()

# Acquire lock for exclusive access
async with await coordinator.acquire_conversation_lock(
    conversation_id="conv_123",
    instance_id="instance_456",
    timeout=30.0
) as lock:
    if lock.acquired:
        # Perform operations that require exclusive access
        await process_conversation_safely()
    else:
        print("Could not acquire lock - conversation in use")

# Achieve consensus on state change
consensus = await coordinator.achieve_consensus(
    conversation_id="conv_123",
    proposed_state=ConversationState.TASK_EXECUTING
)
```

## Configuration

### TaskQueueConfig

Complete configuration for the task queue system.

```python
@dataclass
class TaskQueueConfig:
    """Configuration for task queue system."""
    redis_config: RedisConfig
    queue_configs: List[QueueConfig]
    performance_limits: PerformanceLimits
    security_settings: SecuritySettings
    monitoring_config: MonitoringConfig
    persistence_config: PersistenceConfig

    def validate(self) -> ValidationResult:
        """Validate configuration parameters."""
```

### Configuration Examples

#### Basic Configuration
```python
from beast_mode.task_queue.models import *

config = TaskQueueConfig(
    redis_config=RedisConfig(
        host="localhost",
        port=6379
    ),
    queue_configs=[
        QueueConfig(
            name="default",
            priority=1,
            max_concurrent_tasks=10,
            task_timeout_seconds=300,
            retry_policy=RetryPolicy(max_retries=3)
        )
    ],
    performance_limits=PerformanceLimits(
        task_retrieval_timeout_ms=100,
        max_conversation_history_turns=100
    ),
    security_settings=SecuritySettings(
        validate_task_content=True,
        max_payload_size_bytes=1048576  # 1MB
    ),
    monitoring_config=MonitoringConfig(
        prometheus_enabled=True,
        log_level="INFO"
    ),
    persistence_config=PersistenceConfig(
        hot_storage_ttl_hours=1,
        warm_storage_ttl_days=7
    )
)

# Validate configuration
validation_result = config.validate()
if not validation_result.valid:
    print(f"Configuration errors: {validation_result.errors}")
```

#### Production Configuration
```python
production_config = TaskQueueConfig(
    redis_config=RedisConfig(
        host="redis-cluster.example.com",
        port=6379,
        password="secure_password",
        ssl=True,
        connection_pool_size=20,
        socket_timeout=5.0
    ),
    queue_configs=[
        QueueConfig(
            name="high_priority",
            priority=1,
            max_concurrent_tasks=50,
            task_timeout_seconds=1800,  # 30 minutes
            retry_policy=RetryPolicy(
                max_retries=5,
                backoff_multiplier=2.0,
                max_backoff_seconds=300
            )
        ),
        QueueConfig(
            name="normal_priority",
            priority=2,
            max_concurrent_tasks=20,
            task_timeout_seconds=600,  # 10 minutes
            retry_policy=RetryPolicy(max_retries=3)
        ),
        QueueConfig(
            name="low_priority",
            priority=3,
            max_concurrent_tasks=5,
            task_timeout_seconds=300,  # 5 minutes
            retry_policy=RetryPolicy(max_retries=2)
        )
    ],
    performance_limits=PerformanceLimits(
        task_retrieval_timeout_ms=50,
        checkpoint_creation_timeout_ms=25,
        max_conversation_history_turns=500,
        max_memory_usage_mb=2048,
        max_cpu_time_seconds=120
    ),
    security_settings=SecuritySettings(
        validate_task_content=True,
        sanitize_inputs=True,
        max_payload_size_bytes=10485760,  # 10MB
        allowed_task_types=[
            "data_processing", "file_analysis", "report_generation",
            "notification", "cleanup", "monitoring"
        ]
    ),
    monitoring_config=MonitoringConfig(
        prometheus_enabled=True,
        prometheus_port=8080,
        log_level="INFO",
        structured_logging=True,
        correlation_ids=True
    ),
    persistence_config=PersistenceConfig(
        hot_storage_ttl_hours=2,
        warm_storage_ttl_days=14,
        cold_storage_ttl_days=90,
        checkpoint_storage_ttl_days=180,
        enable_compression=True,
        integrity_checking=True
    )
)
```

## Monitoring & Health

### Health Check API

```python
class HealthChecker:
    """System health monitoring."""

    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connection health."""

    async def check_queue_health(self) -> Dict[str, Any]:
        """Check task queue health."""

    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""

    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
```

**Usage Example:**
```python
from beast_mode.monitoring import HealthChecker

health_checker = HealthChecker()

# Quick health check
health_status = await health_checker.comprehensive_health_check()

print(f"Overall healthy: {health_status['overall_healthy']}")
print(f"Redis status: {health_status['redis']['status']}")
print(f"Queue status: {health_status['task_queue']['status']}")
print(f"System memory: {health_status['system']['memory_percent']:.1f}%")
```

### Metrics Collection

```python
from beast_mode.metrics import MetricsCollector

metrics = MetricsCollector()

# Increment counters
metrics.counter("tasks.submitted").inc()
metrics.counter("tasks.completed").inc()
metrics.counter("tasks.failed").inc()

# Record timing
with metrics.timer("task.execution_time"):
    await execute_task()

# Set gauge values
metrics.gauge("queue.pending_tasks").set(pending_count)
metrics.gauge("workers.active").set(active_workers)

# Record histogram values
metrics.histogram("task.payload_size").observe(payload_size)
```

## Error Handling

### Exception Classes

```python
class BeastModeError(Exception):
    """Base exception for Beast Mode errors."""

class TaskQueueError(BeastModeError):
    """Task queue specific errors."""

class StateTransitionError(BeastModeError):
    """Invalid state transition errors."""

class PersistenceError(BeastModeError):
    """Persistence layer errors."""

class CoordinationError(BeastModeError):
    """Distributed coordination errors."""

class ConfigurationError(BeastModeError):
    """Configuration validation errors."""

class SecurityError(BeastModeError):
    """Security validation errors."""
```

### Error Handling Patterns

```python
from beast_mode.task_queue.exceptions import TaskQueueError, StateTransitionError

async def robust_task_processing():
    try:
        # Task processing logic
        task = await queue_manager.claim_task("worker_1")
        if task:
            result = await process_task(task)
            await queue_manager.complete_task(task.task_id, result)

    except TaskQueueError as e:
        # Handle task queue specific errors
        logger.error(f"Task queue error: {e}")
        await handle_queue_error(e)

    except StateTransitionError as e:
        # Handle state transition errors
        logger.error(f"Invalid state transition: {e}")
        await rollback_state_change()

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await emergency_cleanup()
```

## Examples

### Complete Task Processing System

```python
import asyncio
from typing import Dict, Any
from beast_mode.task_queue import TaskQueueManager, TaskRegistry
from beast_mode.task_queue.models import *

# Define custom task handler
@TaskRegistry.register("data_analysis")
class DataAnalysisHandler:
    async def execute(self, task: TaskContext) -> TaskResult:
        """Execute data analysis task."""

        start_time = time.time()

        try:
            # Extract parameters
            dataset_path = task.task_parameters["dataset_path"]
            analysis_type = task.task_parameters["analysis_type"]

            # Perform analysis (simulated)
            await asyncio.sleep(2)  # Simulate processing time

            # Generate results
            results = {
                "dataset_path": dataset_path,
                "analysis_type": analysis_type,
                "rows_processed": 10000,
                "insights_generated": 15,
                "processing_time": time.time() - start_time
            }

            return TaskResult(
                task_id=task.task_id,
                success=True,
                result_data=results,
                execution_time_ms=(time.time() - start_time) * 1000
            )

        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )

async def main():
    # Configuration
    config = TaskQueueConfig(
        redis_config=RedisConfig(host="localhost", port=6379),
        queue_configs=[
            QueueConfig(
                name="data_processing",
                priority=1,
                max_concurrent_tasks=5,
                task_timeout_seconds=300,
                retry_policy=RetryPolicy(max_retries=3)
            )
        ],
        performance_limits=PerformanceLimits(),
        security_settings=SecuritySettings(),
        monitoring_config=MonitoringConfig(),
        persistence_config=PersistenceConfig()
    )

    # Initialize task queue
    queue_manager = TaskQueueManager(config)
    await queue_manager.initialize()

    try:
        # Submit tasks
        tasks_to_submit = [
            {
                "task_type": "data_analysis",
                "task_content": "Analyze customer behavior patterns",
                "task_parameters": {
                    "dataset_path": "/data/customers.csv",
                    "analysis_type": "behavior_analysis"
                }
            },
            {
                "task_type": "data_analysis",
                "task_content": "Generate sales report",
                "task_parameters": {
                    "dataset_path": "/data/sales.csv",
                    "analysis_type": "sales_analysis"
                }
            }
        ]

        task_ids = []
        for task_data in tasks_to_submit:
            task = TaskContext(**task_data)
            task_id = await queue_manager.submit_task(task)
            task_ids.append(task_id)
            print(f"Submitted task: {task_id}")

        # Process tasks
        worker_count = 2
        workers = [
            asyncio.create_task(worker_process(f"worker_{i}", queue_manager))
            for i in range(worker_count)
        ]

        # Wait for tasks to complete
        await asyncio.sleep(10)

        # Check results
        for task_id in task_ids:
            status = await queue_manager.get_task_status(task_id)
            print(f"Task {task_id}: {status}")

        # Get queue statistics
        stats = await queue_manager.get_queue_stats()
        print(f"Queue statistics: {stats}")

        # Cancel workers
        for worker in workers:
            worker.cancel()

    finally:
        await queue_manager.cleanup()

async def worker_process(worker_id: str, queue_manager: TaskQueueManager):
    """Worker process to handle tasks."""

    while True:
        try:
            # Claim a task
            task = await queue_manager.claim_task(worker_id)

            if task:
                print(f"{worker_id}: Processing task {task.task_id}")

                # Get handler for task type
                handler_class = TaskRegistry.get_handler(task.task_type)
                if handler_class:
                    handler = handler_class()
                    result = await handler.execute(task)

                    if result.success:
                        await queue_manager.complete_task(task.task_id, result)
                        print(f"{worker_id}: Completed task {task.task_id}")
                    else:
                        failure = TaskFailure(
                            task_id=task.task_id,
                            error_type="ExecutionError",
                            error_message=result.error_message or "Unknown error"
                        )
                        await queue_manager.fail_task(task.task_id, failure)
                        print(f"{worker_id}: Failed task {task.task_id}")
                else:
                    print(f"{worker_id}: No handler for task type {task.task_type}")
            else:
                # No tasks available, wait a bit
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            print(f"{worker_id}: Worker cancelled")
            break
        except Exception as e:
            print(f"{worker_id}: Worker error: {e}")
            await asyncio.sleep(5)  # Wait before retry

if __name__ == "__main__":
    asyncio.run(main())
```

---

## API Versioning

Current API version: `v1.0.0`

### Version History
- **v1.0.0**: Initial release with core functionality
- Future versions will maintain backward compatibility where possible

### Deprecation Policy
- Deprecated features will be supported for at least 2 major versions
- Deprecation warnings will be issued before removal
- Migration guides will be provided for breaking changes

---

*This API reference was generated by Documentation Agent Gamma for the Beast Mode Framework. Last updated: 2025-09-24*