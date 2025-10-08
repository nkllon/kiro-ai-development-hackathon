# Execution Tracking API

## Overview

The Execution Tracking API provides Redis-based centralized tracking of specification executions with comprehensive status monitoring, check-in history, and stuck execution detection. It implements the ReflectiveModule pattern for systematic health monitoring and graceful degradation.

## Location

```python
from src.execution_tracking.redis_execution_tracker import (
    RedisExecutionTracker,
    ExecutionStatus,
    ExecutionRecord,
    CheckinRecord,
    # Convenience functions
    initialize_execution_tracker,
    start_tracking_execution,
    update_execution_status,
    checkin_execution,
    get_active_executions,
    get_execution_history
)
```

## Core Classes

### RedisExecutionTracker

Main class for execution tracking with Redis persistence.

```python
class RedisExecutionTracker(ReflectiveModule):
    """Redis-based execution tracking system."""
    
    def __init__(self, redis_host: str = None, redis_port: int = None, redis_password: str = None):
        """Initialize with optional Redis connection parameters."""
```

**Constructor Parameters:**
- `redis_host` (str, optional): Redis server hostname (defaults to environment variable)
- `redis_port` (int, optional): Redis server port (defaults to environment variable)
- `redis_password` (str, optional): Redis password (defaults to environment variable)

**Security Note:** All Redis credentials are loaded securely from environment variables using the secure credentials system.

## Data Models

### ExecutionStatus

```python
class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STUCK = "stuck"
    UNKNOWN = "unknown"
```

### ExecutionRecord

```python
@dataclass
class ExecutionRecord:
    execution_id: str
    spec_name: str
    status: ExecutionStatus
    started_at: datetime
    last_checkin: datetime
    completed_at: Optional[datetime] = None
    pid: Optional[int] = None
    log_file: Optional[str] = None
    progress_file: Optional[str] = None
    lock_file: Optional[str] = None
    workflow_version: str = "v2.0"
    efficiency_gain: Optional[float] = None
    total_tasks: Optional[int] = None
    completed_tasks: Optional[int] = None
    estimated_hours: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

### CheckinRecord

```python
@dataclass
class CheckinRecord:
    execution_id: str
    timestamp: datetime
    status: ExecutionStatus
    phase: Optional[str] = None
    progress_percentage: Optional[float] = None
    message: Optional[str] = None
    resource_usage: Optional[Dict[str, float]] = None
```

## Core Methods

### Initialization

#### `async initialize() -> bool`

Initialize Redis connection with secure credentials.

```python
tracker = RedisExecutionTracker()
success = await tracker.initialize()

if success:
    print("✅ Redis connection established")
else:
    print("❌ Redis connection failed")
```

**Returns:**
- `bool`: True if Redis connection successful, False otherwise

**Security Features:**
- Automatic credential loading from environment variables
- Connection timeout and retry logic
- Graceful degradation if Redis unavailable

### Execution Management

#### `async start_execution(spec_name: str, **kwargs) -> str`

Start tracking a new execution.

```python
execution_id = await tracker.start_execution(
    spec_name="data_processing_pipeline",
    total_tasks=10,
    estimated_hours=2.5,
    pid=os.getpid(),
    log_file="/path/to/execution.log",
    metadata={"version": "1.0", "environment": "production"}
)

print(f"Started tracking execution: {execution_id}")
```

**Parameters:**
- `spec_name` (str): Name of the specification being executed
- `**kwargs`: Additional execution metadata

**Common kwargs:**
- `total_tasks` (int): Total number of tasks in execution
- `estimated_hours` (float): Estimated execution time
- `pid` (int): Process ID of executing process
- `log_file` (str): Path to execution log file
- `progress_file` (str): Path to progress tracking file
- `metadata` (Dict): Additional metadata

**Returns:**
- `str`: Unique execution ID for tracking

#### `async update_execution_status(execution_id: str, status: ExecutionStatus, **kwargs) -> bool`

Update execution status and metadata.

```python
# Update to running status
success = await tracker.update_execution_status(
    execution_id,
    ExecutionStatus.RUNNING,
    completed_tasks=3,
    progress_percentage=30.0
)

# Mark as completed
success = await tracker.update_execution_status(
    execution_id,
    ExecutionStatus.COMPLETED,
    completed_tasks=10,
    efficiency_gain=1.2
)

# Mark as failed with error
success = await tracker.update_execution_status(
    execution_id,
    ExecutionStatus.FAILED,
    error_message="Database connection timeout"
)
```

**Parameters:**
- `execution_id` (str): Execution ID to update
- `status` (ExecutionStatus): New execution status
- `**kwargs`: Additional fields to update

**Returns:**
- `bool`: True if update successful, False otherwise

#### `async checkin_execution(execution_id: str, **kwargs) -> bool`

Record a check-in for execution monitoring.

```python
# Basic check-in
success = await tracker.checkin_execution(execution_id)

# Detailed check-in with progress
success = await tracker.checkin_execution(
    execution_id,
    phase="data_processing",
    progress_percentage=45.0,
    message="Processing batch 3 of 10",
    resource_usage={
        "cpu_percent": 75.0,
        "memory_mb": 512.0,
        "disk_io_mb": 100.0
    }
)
```

**Parameters:**
- `execution_id` (str): Execution ID to check in
- `phase` (str, optional): Current execution phase
- `progress_percentage` (float, optional): Progress percentage (0-100)
- `message` (str, optional): Status message
- `resource_usage` (Dict, optional): Resource usage metrics

**Returns:**
- `bool`: True if check-in recorded successfully

### Query Methods

#### `async get_active_executions() -> List[ExecutionRecord]`

Get all currently active executions.

```python
active_executions = await tracker.get_active_executions()

for execution in active_executions:
    print(f"Active: {execution.spec_name} ({execution.status.value})")
    print(f"  Started: {execution.started_at}")
    print(f"  Progress: {execution.completed_tasks}/{execution.total_tasks}")
```

**Returns:**
- `List[ExecutionRecord]`: List of active execution records

#### `async get_execution_record(execution_id: str) -> Optional[ExecutionRecord]`

Get specific execution record by ID.

```python
record = await tracker.get_execution_record(execution_id)

if record:
    print(f"Execution: {record.spec_name}")
    print(f"Status: {record.status.value}")
    print(f"Duration: {(record.last_checkin - record.started_at).total_seconds()}s")
else:
    print("Execution not found")
```

**Parameters:**
- `execution_id` (str): Execution ID to retrieve

**Returns:**
- `ExecutionRecord`: Execution record if found, None otherwise

#### `async get_execution_history(spec_name: Optional[str] = None, limit: int = 50) -> List[ExecutionRecord]`

Get execution history with optional filtering.

```python
# Get all recent executions
history = await tracker.get_execution_history(limit=20)

# Get history for specific spec
spec_history = await tracker.get_execution_history(
    spec_name="data_processing_pipeline",
    limit=10
)

for record in history:
    print(f"{record.spec_name}: {record.status.value}")
```

**Parameters:**
- `spec_name` (str, optional): Filter by specification name
- `limit` (int): Maximum number of records to return

**Returns:**
- `List[ExecutionRecord]`: List of execution records

#### `async get_execution_checkins(execution_id: str) -> List[CheckinRecord]`

Get check-in history for an execution.

```python
checkins = await tracker.get_execution_checkins(execution_id)

for checkin in checkins:
    print(f"{checkin.timestamp}: {checkin.phase} - {checkin.message}")
    if checkin.progress_percentage:
        print(f"  Progress: {checkin.progress_percentage}%")
```

**Parameters:**
- `execution_id` (str): Execution ID to get check-ins for

**Returns:**
- `List[CheckinRecord]`: List of check-in records sorted by timestamp

### Monitoring and Maintenance

#### `async detect_stuck_executions(timeout_minutes: int = 60) -> List[ExecutionRecord]`

Detect executions that haven't checked in recently.

```python
# Detect executions stuck for more than 1 hour
stuck_executions = await tracker.detect_stuck_executions(timeout_minutes=60)

for execution in stuck_executions:
    print(f"Stuck execution: {execution.spec_name}")
    print(f"  Last check-in: {execution.last_checkin}")
    print(f"  Duration: {(datetime.now() - execution.last_checkin).total_seconds()}s")
```

**Parameters:**
- `timeout_minutes` (int): Minutes without check-in to consider stuck

**Returns:**
- `List[ExecutionRecord]`: List of stuck executions (automatically marked as STUCK)

#### `async cleanup_old_records(days: int = 30) -> int`

Clean up old execution records and check-ins.

```python
# Clean up records older than 30 days
cleaned_count = await tracker.cleanup_old_records(days=30)
print(f"Cleaned up {cleaned_count} old records")

# Clean up records older than 7 days
cleaned_count = await tracker.cleanup_old_records(days=7)
```

**Parameters:**
- `days` (int): Age threshold for cleanup

**Returns:**
- `int`: Number of records cleaned up

## Convenience Functions

For simple usage without managing tracker instances:

### `async initialize_execution_tracker() -> bool`

Initialize the global execution tracker.

```python
success = await initialize_execution_tracker()
if success:
    print("Global execution tracker initialized")
```

### `async start_tracking_execution(spec_name: str, **kwargs) -> str`

Start tracking using global tracker.

```python
execution_id = await start_tracking_execution(
    "my_specification",
    total_tasks=5,
    estimated_hours=1.0
)
```

### `async update_execution_status(execution_id: str, status: ExecutionStatus, **kwargs) -> bool`

Update status using global tracker.

```python
await update_execution_status(
    execution_id,
    ExecutionStatus.RUNNING,
    completed_tasks=2
)
```

### `async checkin_execution(execution_id: str, **kwargs) -> bool`

Check in using global tracker.

```python
await checkin_execution(
    execution_id,
    phase="processing",
    progress_percentage=40.0
)
```

## Usage Examples

### Basic Execution Tracking

```python
import asyncio
from src.execution_tracking.redis_execution_tracker import (
    initialize_execution_tracker,
    start_tracking_execution,
    update_execution_status,
    checkin_execution,
    ExecutionStatus
)

async def basic_tracking_example():
    # Initialize tracker
    await initialize_execution_tracker()
    
    # Start tracking
    execution_id = await start_tracking_execution(
        "example_pipeline",
        total_tasks=3,
        estimated_hours=0.5
    )
    
    # Update to running
    await update_execution_status(execution_id, ExecutionStatus.RUNNING)
    
    # Simulate work with check-ins
    for i in range(3):
        await checkin_execution(
            execution_id,
            phase=f"task_{i+1}",
            progress_percentage=(i + 1) * 33.3,
            message=f"Completed task {i + 1}"
        )
        
        await asyncio.sleep(2)  # Simulate work
    
    # Mark as completed
    await update_execution_status(
        execution_id,
        ExecutionStatus.COMPLETED,
        completed_tasks=3,
        efficiency_gain=1.1
    )
    
    print(f"Execution {execution_id} completed")

asyncio.run(basic_tracking_example())
```

### Advanced Monitoring

```python
import asyncio
from datetime import datetime
from src.execution_tracking.redis_execution_tracker import RedisExecutionTracker, ExecutionStatus

async def advanced_monitoring_example():
    tracker = RedisExecutionTracker()
    
    if not await tracker.initialize():
        print("Failed to initialize tracker")
        return
    
    # Start multiple executions
    executions = []
    for i in range(3):
        execution_id = await tracker.start_execution(
            f"pipeline_{i}",
            total_tasks=5,
            estimated_hours=1.0
        )
        executions.append(execution_id)
        
        # Update to running
        await tracker.update_execution_status(execution_id, ExecutionStatus.RUNNING)
    
    # Monitor executions
    monitoring_duration = 30  # seconds
    start_time = datetime.now()
    
    while (datetime.now() - start_time).total_seconds() < monitoring_duration:
        # Get active executions
        active = await tracker.get_active_executions()
        print(f"\nActive executions: {len(active)}")
        
        for execution in active:
            print(f"  {execution.spec_name}: {execution.status.value}")
            
            # Simulate progress
            if execution.completed_tasks is None:
                completed = 0
            else:
                completed = min(execution.completed_tasks + 1, execution.total_tasks or 5)
            
            await tracker.update_execution_status(
                execution.execution_id,
                ExecutionStatus.RUNNING,
                completed_tasks=completed
            )
            
            # Check in with progress
            progress = (completed / (execution.total_tasks or 5)) * 100
            await tracker.checkin_execution(
                execution.execution_id,
                progress_percentage=progress,
                message=f"Completed {completed} tasks"
            )
            
            # Complete if all tasks done
            if completed >= (execution.total_tasks or 5):
                await tracker.update_execution_status(
                    execution.execution_id,
                    ExecutionStatus.COMPLETED
                )
        
        # Check for stuck executions
        stuck = await tracker.detect_stuck_executions(timeout_minutes=1)
        if stuck:
            print(f"Stuck executions detected: {len(stuck)}")
        
        await asyncio.sleep(5)
    
    # Get execution history
    history = await tracker.get_execution_history(limit=10)
    print(f"\nExecution history: {len(history)} records")
    
    for record in history:
        duration = (record.last_checkin - record.started_at).total_seconds()
        print(f"  {record.spec_name}: {record.status.value} ({duration:.1f}s)")

asyncio.run(advanced_monitoring_example())
```

### Error Handling and Recovery

```python
import asyncio
from src.execution_tracking.redis_execution_tracker import RedisExecutionTracker, ExecutionStatus

async def error_handling_example():
    tracker = RedisExecutionTracker()
    
    try:
        # Initialize with error handling
        if not await tracker.initialize():
            print("Redis not available, using fallback tracking")
            # Implement file-based fallback
            return
        
        # Start execution
        execution_id = await tracker.start_execution("error_prone_pipeline")
        
        try:
            # Simulate execution with potential errors
            await tracker.update_execution_status(execution_id, ExecutionStatus.RUNNING)
            
            # Simulate work that might fail
            for i in range(5):
                try:
                    # Simulate task that might fail
                    if i == 3:  # Simulate failure on task 3
                        raise Exception("Simulated task failure")
                    
                    await tracker.checkin_execution(
                        execution_id,
                        phase=f"task_{i+1}",
                        progress_percentage=(i + 1) * 20,
                        message=f"Completed task {i + 1}"
                    )
                    
                    await asyncio.sleep(1)
                    
                except Exception as task_error:
                    print(f"Task {i+1} failed: {task_error}")
                    
                    # Update execution with error
                    await tracker.update_execution_status(
                        execution_id,
                        ExecutionStatus.FAILED,
                        error_message=str(task_error),
                        completed_tasks=i
                    )
                    break
            else:
                # All tasks completed successfully
                await tracker.update_execution_status(
                    execution_id,
                    ExecutionStatus.COMPLETED,
                    completed_tasks=5
                )
        
        except Exception as execution_error:
            print(f"Execution error: {execution_error}")
            await tracker.update_execution_status(
                execution_id,
                ExecutionStatus.FAILED,
                error_message=str(execution_error)
            )
    
    except Exception as tracker_error:
        print(f"Tracker error: {tracker_error}")
        
        # Trigger graceful degradation
        degradation = await tracker.graceful_degradation(tracker_error)
        if degradation.success:
            print("Graceful degradation successful")
            print(f"Remaining capabilities: {degradation.remaining_capabilities}")
        else:
            print("Graceful degradation failed")

asyncio.run(error_handling_example())
```

### Integration with Other Systems

```python
import asyncio
from src.execution_tracking.redis_execution_tracker import RedisExecutionTracker, ExecutionStatus
from src.constellation_orchestrator.core.orchestrator import ConstellationOrchestrator

async def integrated_tracking_example():
    # Initialize both systems
    tracker = RedisExecutionTracker()
    orchestrator = ConstellationOrchestrator()
    
    await tracker.initialize()
    await orchestrator.initialize()
    
    # Start tracking
    tracking_id = await tracker.start_execution(
        "constellation_pipeline",
        total_tasks=10,
        estimated_hours=2.0
    )
    
    # Load tasks and start orchestrator execution
    tasks = create_task_definitions()  # Your task creation logic
    await orchestrator.load_tasks(tasks)
    execution_id = await orchestrator.start_execution()
    
    # Monitor both systems
    while True:
        # Get orchestrator state
        orch_state = await orchestrator.get_execution_state(execution_id)
        if not orch_state:
            break
        
        # Update tracking system
        await tracker.update_execution_status(
            tracking_id,
            ExecutionStatus(orch_state.status.value),
            completed_tasks=orch_state.completed_tasks,
            total_tasks=orch_state.total_tasks
        )
        
        # Check in with detailed progress
        progress = (orch_state.completed_tasks / orch_state.total_tasks) * 100
        await tracker.checkin_execution(
            tracking_id,
            phase=orch_state.current_phase,
            progress_percentage=progress,
            message=f"Orchestrator: {orch_state.status.value}"
        )
        
        if orch_state.status.value in ['completed', 'failed']:
            break
        
        await asyncio.sleep(10)
    
    # Cleanup
    await orchestrator.shutdown()

asyncio.run(integrated_tracking_example())
```

## Best Practices

### 1. Regular Check-ins

```python
async def execution_with_regular_checkins():
    execution_id = await start_tracking_execution("my_pipeline")
    
    try:
        await update_execution_status(execution_id, ExecutionStatus.RUNNING)
        
        # Regular check-ins during long-running operations
        for i in range(100):
            # Do work
            await do_work_unit(i)
            
            # Check in every 10 iterations
            if i % 10 == 0:
                await checkin_execution(
                    execution_id,
                    progress_percentage=(i / 100) * 100,
                    message=f"Processed {i}/100 items"
                )
        
        await update_execution_status(execution_id, ExecutionStatus.COMPLETED)
        
    except Exception as e:
        await update_execution_status(
            execution_id,
            ExecutionStatus.FAILED,
            error_message=str(e)
        )
```

### 2. Resource Usage Monitoring

```python
import psutil

async def execution_with_resource_monitoring():
    execution_id = await start_tracking_execution("resource_intensive_pipeline")
    
    try:
        await update_execution_status(execution_id, ExecutionStatus.RUNNING)
        
        while not work_completed():
            # Do work
            await do_work()
            
            # Monitor resource usage
            cpu_percent = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            
            await checkin_execution(
                execution_id,
                resource_usage={
                    "cpu_percent": cpu_percent,
                    "memory_mb": memory_info.used / (1024 * 1024),
                    "memory_percent": memory_info.percent,
                    "disk_read_mb": disk_io.read_bytes / (1024 * 1024),
                    "disk_write_mb": disk_io.write_bytes / (1024 * 1024)
                }
            )
            
            await asyncio.sleep(30)  # Check in every 30 seconds
        
        await update_execution_status(execution_id, ExecutionStatus.COMPLETED)
        
    except Exception as e:
        await update_execution_status(
            execution_id,
            ExecutionStatus.FAILED,
            error_message=str(e)
        )
```

### 3. Stuck Execution Detection

```python
async def monitor_for_stuck_executions():
    tracker = RedisExecutionTracker()
    await tracker.initialize()
    
    while True:
        # Check for stuck executions every 5 minutes
        stuck_executions = await tracker.detect_stuck_executions(timeout_minutes=30)
        
        for execution in stuck_executions:
            print(f"ALERT: Stuck execution detected: {execution.spec_name}")
            print(f"  Execution ID: {execution.execution_id}")
            print(f"  Last check-in: {execution.last_checkin}")
            
            # Take corrective action
            # - Send notification
            # - Attempt to restart
            # - Mark as failed
            
        await asyncio.sleep(300)  # Check every 5 minutes
```

### 4. Cleanup and Maintenance

```python
async def maintenance_routine():
    tracker = RedisExecutionTracker()
    await tracker.initialize()
    
    # Clean up old records weekly
    cleaned_count = await tracker.cleanup_old_records(days=7)
    print(f"Cleaned up {cleaned_count} old execution records")
    
    # Get statistics
    active_count = len(await tracker.get_active_executions())
    recent_history = await tracker.get_execution_history(limit=100)
    
    print(f"Active executions: {active_count}")
    print(f"Recent executions: {len(recent_history)}")
    
    # Analyze execution patterns
    completed = [r for r in recent_history if r.status == ExecutionStatus.COMPLETED]
    failed = [r for r in recent_history if r.status == ExecutionStatus.FAILED]
    
    print(f"Success rate: {len(completed) / len(recent_history) * 100:.1f}%")
    print(f"Failure rate: {len(failed) / len(recent_history) * 100:.1f}%")
```

## Security Considerations

### Environment Variables

All Redis credentials must be configured through environment variables:

```bash
# Required environment variables
REDIS_PASSWORD=your_secure_redis_password
REDIS_HOST=your_redis_host
REDIS_PORT=6379
```

### Data Encryption

For sensitive execution data, consider:

```python
import json
from cryptography.fernet import Fernet

class EncryptedExecutionTracker(RedisExecutionTracker):
    def __init__(self, encryption_key: bytes = None):
        super().__init__()
        self.cipher = Fernet(encryption_key or Fernet.generate_key())
    
    def _serialize_execution_record(self, record: ExecutionRecord) -> Dict[str, str]:
        data = super()._serialize_execution_record(record)
        
        # Encrypt sensitive fields
        if 'metadata' in data and data['metadata']:
            encrypted_metadata = self.cipher.encrypt(data['metadata'].encode())
            data['metadata'] = encrypted_metadata.decode()
        
        return data
```

---

**Next**: [DAG Management](./dag-management.md) | **Up**: [Orchestration APIs](../orchestration/)