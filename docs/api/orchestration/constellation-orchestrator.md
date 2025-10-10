# Constellation Orchestrator API

## Overview

The `ConstellationOrchestrator` is the main orchestration engine for DAG-based AI prompt execution. It provides systematic orchestration of 90+ AI prompts with comprehensive dependency management, multi-agent coordination, and Beast Mode observability.

## Location

```python
from src.constellation_orchestrator.core.orchestrator import ConstellationOrchestrator
```

## Class Definition

```python
class ConstellationOrchestrator(ReflectiveModule):
    """
    Main orchestrator for DAG-based AI prompt execution.
    
    Provides systematic orchestration of 90+ AI prompts with comprehensive
    dependency management, multi-agent coordination, and Beast Mode observability.
    """
```

## Constructor

```python
def __init__(self, config: Optional[ConstellationConfig] = None):
    """Initialize the Constellation Orchestrator."""
```

**Parameters:**
- `config` (ConstellationConfig, optional): Configuration object. If None, loads from environment variables.

**Example:**
```python
from src.constellation_orchestrator.core.orchestrator import ConstellationOrchestrator
from src.constellation_orchestrator.core.config import ConstellationConfig

# Use default configuration (from environment)
orchestrator = ConstellationOrchestrator()

# Use custom configuration
config = ConstellationConfig(
    max_concurrent_tasks=5,
    task_timeout_seconds=1800,
    redis_host='localhost',
    redis_port=6379
)
orchestrator = ConstellationOrchestrator(config)
```

## Core Methods

### Initialization

#### `async initialize() -> bool`

Initialize all orchestrator components including DAG manager, execution manager, status manager, and agent manager.

```python
orchestrator = ConstellationOrchestrator()
success = await orchestrator.initialize()

if success:
    print("Orchestrator initialized successfully")
else:
    print("Failed to initialize orchestrator")
```

**Returns:**
- `bool`: True if initialization successful, False otherwise

**Components Initialized:**
- Status Manager: Execution state tracking
- Agent Manager: AI agent coordination
- DAG Manager: Dependency graph management
- Execution Manager: Task execution coordination

### Task Management

#### `async load_tasks(task_definitions: List[TaskDefinition]) -> bool`

Load task definitions and validate DAG structure.

```python
from src.constellation_orchestrator.models.task_definition import TaskDefinition

# Define tasks
tasks = [
    TaskDefinition(
        task_id="task_1",
        name="Initialize System",
        description="Set up system components",
        dependencies=[],
        prompt_template="Initialize the system with {config}",
        expected_output="System initialized successfully",
        timeout_seconds=300
    ),
    TaskDefinition(
        task_id="task_2",
        name="Process Data",
        description="Process input data",
        dependencies=["task_1"],
        prompt_template="Process the data: {data}",
        expected_output="Data processed successfully",
        timeout_seconds=600
    )
]

# Load tasks
success = await orchestrator.load_tasks(tasks)
if success:
    print(f"Loaded {len(tasks)} tasks successfully")
```

**Parameters:**
- `task_definitions` (List[TaskDefinition]): List of task definitions to load

**Returns:**
- `bool`: True if tasks loaded and DAG validated successfully

**Validation Performed:**
- Dependency cycle detection
- Orphaned task identification
- Task definition completeness
- Execution order calculation

### Execution Control

#### `async start_execution(execution_name: Optional[str] = None) -> Optional[str]`

Start DAG execution and return execution ID.

```python
# Start execution with auto-generated name
execution_id = await orchestrator.start_execution()

# Start execution with custom name
execution_id = await orchestrator.start_execution("data_processing_pipeline")

if execution_id:
    print(f"Execution started: {execution_id}")
else:
    print("Failed to start execution")
```

**Parameters:**
- `execution_name` (str, optional): Custom name for the execution

**Returns:**
- `str`: Unique execution ID if successful, None if failed

**Execution Process:**
1. Generate unique execution ID
2. Initialize execution state tracking
3. Start background DAG execution
4. Return execution ID for monitoring

#### `async get_execution_state(execution_id: Optional[str] = None) -> Optional[ExecutionState]`

Get current execution state for monitoring progress.

```python
# Get state for current execution
state = await orchestrator.get_execution_state()

# Get state for specific execution
state = await orchestrator.get_execution_state("specific_execution_id")

if state:
    print(f"Status: {state.status}")
    print(f"Progress: {state.completed_tasks}/{state.total_tasks}")
    print(f"Duration: {state.duration_seconds}s")
```

**Parameters:**
- `execution_id` (str, optional): Specific execution ID. If None, uses current execution.

**Returns:**
- `ExecutionState`: Current execution state with progress information

### Health and Monitoring

#### `async health_check() -> Dict[str, Any]`

Comprehensive health check for all orchestrator components.

```python
health = await orchestrator.health_check()

print(f"Status: {health['status']}")
print(f"Components healthy: {health['components_healthy']}")
print(f"Available agents: {health['available_agents']}")
print(f"Total agents: {health['total_agents']}")
```

**Returns:**
- `Dict[str, Any]`: Comprehensive health status including:
  - `instance_id`: Unique orchestrator instance ID
  - `is_initialized`: Whether orchestrator is initialized
  - `current_execution_id`: Current execution ID if any
  - `available_agents`: Number of available agents
  - `total_agents`: Total number of agents
  - `components_healthy`: Whether all components are healthy

#### `async shutdown() -> None`

Graceful shutdown of all orchestrator components.

```python
# Graceful shutdown
await orchestrator.shutdown()
print("Orchestrator shutdown complete")
```

**Shutdown Process:**
1. Stop execution manager
2. Shutdown agent manager
3. Close status manager connections
4. Clean up DAG manager resources

## Data Models

### TaskDefinition

```python
@dataclass
class TaskDefinition:
    task_id: str
    name: str
    description: str
    dependencies: List[str]
    prompt_template: str
    expected_output: str
    timeout_seconds: int = 1800
    retry_count: int = 3
    agent_requirements: Optional[Dict[str, Any]] = None
    context_requirements: Optional[List[str]] = None
```

### ExecutionState

```python
@dataclass
class ExecutionState:
    execution_id: str
    status: ExecutionStatus
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    running_tasks: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: float
    current_phase: Optional[str]
    error_message: Optional[str]
```

### ExecutionStatus

```python
class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

## Configuration

### ConstellationConfig

```python
@dataclass
class ConstellationConfig:
    # Execution settings
    max_concurrent_tasks: int = 10
    task_timeout_seconds: int = 1800
    retry_attempts: int = 3
    
    # Redis settings (loaded from environment)
    redis_host: str = field(default_factory=lambda: os.getenv('REDIS_HOST', 'localhost'))
    redis_port: int = field(default_factory=lambda: int(os.getenv('REDIS_PORT', '6379')))
    redis_password: str = field(default_factory=lambda: os.getenv('REDIS_PASSWORD', ''))
    
    # Agent settings
    agent_pool_size: int = 5
    agent_timeout_seconds: int = 300
    
    # Monitoring settings
    health_check_interval_seconds: int = 30
    status_update_interval_seconds: int = 10
    
    @classmethod
    def load_from_env(cls) -> 'ConstellationConfig':
        """Load configuration from environment variables."""
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
```

## Usage Examples

### Basic Usage

```python
import asyncio
from src.constellation_orchestrator.core.orchestrator import ConstellationOrchestrator
from src.constellation_orchestrator.models.task_definition import TaskDefinition

async def main():
    # Initialize orchestrator
    orchestrator = ConstellationOrchestrator()
    
    if not await orchestrator.initialize():
        print("Failed to initialize orchestrator")
        return
    
    # Define tasks
    tasks = [
        TaskDefinition(
            task_id="setup",
            name="System Setup",
            description="Initialize system components",
            dependencies=[],
            prompt_template="Set up the system with configuration: {config}",
            expected_output="System setup complete"
        ),
        TaskDefinition(
            task_id="process",
            name="Data Processing",
            description="Process input data",
            dependencies=["setup"],
            prompt_template="Process data: {data}",
            expected_output="Data processing complete"
        ),
        TaskDefinition(
            task_id="finalize",
            name="Finalization",
            description="Finalize processing",
            dependencies=["process"],
            prompt_template="Finalize the processing results",
            expected_output="Processing finalized"
        )
    ]
    
    # Load and execute tasks
    if await orchestrator.load_tasks(tasks):
        execution_id = await orchestrator.start_execution("example_pipeline")
        
        if execution_id:
            print(f"Started execution: {execution_id}")
            
            # Monitor execution
            while True:
                state = await orchestrator.get_execution_state(execution_id)
                if not state:
                    break
                
                print(f"Progress: {state.completed_tasks}/{state.total_tasks}")
                
                if state.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                    print(f"Execution {state.status.value}")
                    break
                
                await asyncio.sleep(5)
    
    # Cleanup
    await orchestrator.shutdown()

# Run the example
asyncio.run(main())
```

### Advanced Usage with Custom Configuration

```python
import asyncio
from src.constellation_orchestrator.core.orchestrator import ConstellationOrchestrator
from src.constellation_orchestrator.core.config import ConstellationConfig

async def advanced_example():
    # Custom configuration
    config = ConstellationConfig(
        max_concurrent_tasks=3,
        task_timeout_seconds=900,
        retry_attempts=2,
        agent_pool_size=3,
        health_check_interval_seconds=15
    )
    
    orchestrator = ConstellationOrchestrator(config)
    
    try:
        # Initialize with error handling
        if not await orchestrator.initialize():
            raise RuntimeError("Orchestrator initialization failed")
        
        # Check health before proceeding
        health = await orchestrator.health_check()
        if not health.get('components_healthy', False):
            raise RuntimeError("Components not healthy")
        
        # Load complex task definitions
        tasks = load_complex_task_definitions()  # Your task loading logic
        
        if not await orchestrator.load_tasks(tasks):
            raise RuntimeError("Failed to load tasks")
        
        # Start execution with monitoring
        execution_id = await orchestrator.start_execution("complex_pipeline")
        
        if not execution_id:
            raise RuntimeError("Failed to start execution")
        
        # Advanced monitoring with health checks
        while True:
            # Check orchestrator health
            health = await orchestrator.health_check()
            if not health.get('components_healthy', False):
                print("Warning: Components unhealthy")
            
            # Check execution state
            state = await orchestrator.get_execution_state(execution_id)
            if not state:
                break
            
            print(f"Status: {state.status.value}")
            print(f"Progress: {state.completed_tasks}/{state.total_tasks}")
            print(f"Running: {state.running_tasks}")
            print(f"Failed: {state.failed_tasks}")
            
            if state.status == ExecutionStatus.FAILED:
                print(f"Execution failed: {state.error_message}")
                break
            elif state.status == ExecutionStatus.COMPLETED:
                print("Execution completed successfully")
                break
            
            await asyncio.sleep(10)
    
    except Exception as e:
        print(f"Error: {e}")
        # Trigger graceful degradation
        degradation = await orchestrator.graceful_degradation(e)
        print(f"Graceful degradation: {degradation.success}")
    
    finally:
        await orchestrator.shutdown()

asyncio.run(advanced_example())
```

### Error Handling and Recovery

```python
async def robust_execution():
    orchestrator = ConstellationOrchestrator()
    
    try:
        # Initialize with validation
        if not await orchestrator.initialize():
            raise RuntimeError("Initialization failed")
        
        # Validate health before execution
        health = await orchestrator.get_health_status()
        if health.status != ModuleStatus.HEALTHY:
            print(f"Warning: Orchestrator health issues: {health.issues}")
        
        # Load tasks with validation
        tasks = create_task_definitions()
        if not await orchestrator.load_tasks(tasks):
            raise RuntimeError("Task loading failed")
        
        # Start execution with retry logic
        max_retries = 3
        execution_id = None
        
        for attempt in range(max_retries):
            execution_id = await orchestrator.start_execution(f"attempt_{attempt + 1}")
            if execution_id:
                break
            
            print(f"Execution start attempt {attempt + 1} failed")
            await asyncio.sleep(5)
        
        if not execution_id:
            raise RuntimeError("Failed to start execution after retries")
        
        # Monitor with error recovery
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while True:
            try:
                state = await orchestrator.get_execution_state(execution_id)
                if not state:
                    break
                
                consecutive_errors = 0  # Reset error count on success
                
                if state.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                    break
                
                await asyncio.sleep(5)
                
            except Exception as monitor_error:
                consecutive_errors += 1
                print(f"Monitoring error {consecutive_errors}: {monitor_error}")
                
                if consecutive_errors >= max_consecutive_errors:
                    print("Too many consecutive monitoring errors")
                    break
                
                await asyncio.sleep(10)  # Longer wait on error
    
    except Exception as e:
        print(f"Critical error: {e}")
        
        # Attempt graceful degradation
        try:
            degradation = await orchestrator.graceful_degradation(e)
            if degradation.success:
                print("Graceful degradation successful")
                print(f"Remaining capabilities: {degradation.remaining_capabilities}")
            else:
                print("Graceful degradation failed")
        except Exception as degradation_error:
            print(f"Degradation error: {degradation_error}")
    
    finally:
        try:
            await orchestrator.shutdown()
        except Exception as shutdown_error:
            print(f"Shutdown error: {shutdown_error}")

asyncio.run(robust_execution())
```

## Integration with Other Components

### With Execution Tracking

```python
from src.execution_tracking.redis_execution_tracker import (
    initialize_execution_tracker,
    start_tracking_execution,
    update_execution_status
)

async def integrated_execution():
    # Initialize execution tracker
    await initialize_execution_tracker()
    
    # Initialize orchestrator
    orchestrator = ConstellationOrchestrator()
    await orchestrator.initialize()
    
    # Start tracking
    tracking_id = await start_tracking_execution("constellation_pipeline")
    
    # Load and start execution
    tasks = create_task_definitions()
    await orchestrator.load_tasks(tasks)
    execution_id = await orchestrator.start_execution()
    
    # Monitor both systems
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if not state:
            break
        
        # Update tracking system
        await update_execution_status(
            tracking_id,
            ExecutionStatus(state.status.value),
            progress_percentage=(state.completed_tasks / state.total_tasks) * 100
        )
        
        if state.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            break
        
        await asyncio.sleep(5)
    
    await orchestrator.shutdown()
```

### With AI Memory Palace

```python
from src.ai_memory_palace.engine.context_engine import ContextEngine

async def context_aware_execution():
    # Initialize components
    orchestrator = ConstellationOrchestrator()
    context_engine = ContextEngine()
    
    await orchestrator.initialize()
    
    # Load context-aware tasks
    context = load_session_context()
    filtered_context = context_engine.filter_relevant_context(context, "data processing")
    
    # Create tasks based on context
    tasks = create_context_aware_tasks(filtered_context)
    
    await orchestrator.load_tasks(tasks)
    execution_id = await orchestrator.start_execution("context_aware_pipeline")
    
    # Monitor and update context
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if not state:
            break
        
        # Update context with execution progress
        context.add_execution_event({
            'execution_id': execution_id,
            'status': state.status.value,
            'progress': state.completed_tasks / state.total_tasks,
            'timestamp': datetime.utcnow()
        })
        
        if state.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            break
        
        await asyncio.sleep(5)
    
    await orchestrator.shutdown()
```

## Best Practices

### 1. Proper Initialization

```python
async def proper_initialization():
    orchestrator = ConstellationOrchestrator()
    
    # Always check initialization success
    if not await orchestrator.initialize():
        raise RuntimeError("Failed to initialize orchestrator")
    
    # Validate health after initialization
    health = await orchestrator.health_check()
    if not health.get('components_healthy', False):
        print("Warning: Some components are unhealthy")
        # Decide whether to proceed or abort
```

### 2. Task Definition Best Practices

```python
def create_robust_task_definitions():
    return [
        TaskDefinition(
            task_id="unique_task_id",
            name="Human Readable Name",
            description="Clear description of what this task does",
            dependencies=["prerequisite_task_id"],  # Clear dependencies
            prompt_template="Specific prompt with {parameters}",
            expected_output="Clear expected output description",
            timeout_seconds=1800,  # Reasonable timeout
            retry_count=3,  # Allow retries for transient failures
            agent_requirements={
                'capabilities': ['text_processing'],
                'min_memory_mb': 512
            }
        )
    ]
```

### 3. Monitoring and Error Handling

```python
async def robust_monitoring(orchestrator, execution_id):
    error_count = 0
    max_errors = 5
    
    while True:
        try:
            state = await orchestrator.get_execution_state(execution_id)
            if not state:
                break
            
            # Reset error count on successful monitoring
            error_count = 0
            
            # Log progress
            print(f"Progress: {state.completed_tasks}/{state.total_tasks}")
            
            # Check for completion
            if state.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                break
            
            await asyncio.sleep(5)
            
        except Exception as e:
            error_count += 1
            print(f"Monitoring error {error_count}: {e}")
            
            if error_count >= max_errors:
                print("Too many monitoring errors, aborting")
                break
            
            # Exponential backoff on errors
            await asyncio.sleep(min(2 ** error_count, 60))
```

### 4. Resource Cleanup

```python
async def execution_with_cleanup():
    orchestrator = ConstellationOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Your execution logic here
        tasks = create_task_definitions()
        await orchestrator.load_tasks(tasks)
        execution_id = await orchestrator.start_execution()
        
        # Monitor execution
        await monitor_execution(orchestrator, execution_id)
        
    except Exception as e:
        print(f"Execution error: {e}")
        # Handle error appropriately
        
    finally:
        # Always cleanup resources
        try:
            await orchestrator.shutdown()
        except Exception as shutdown_error:
            print(f"Shutdown error: {shutdown_error}")
```

---

**Next**: [DAG Management](./dag-management.md) | **Up**: [Orchestration APIs](../orchestration/)