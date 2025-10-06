# DAG Orchestration API Reference

## Core Components

### DAGOrchestrator

The main orchestrator class that coordinates DAG execution with LLM integration.

```python
from dag_orchestration.core.dag_orchestrator import DAGOrchestrator

# Initialize orchestrator
orchestrator = DAGOrchestrator(
    dag_registry=dag_registry,
    execution_engine=parallel_engine,
    llm_manager=llm_orchestration_manager
)

# Execute DAG
result = orchestrator.execute_dag(tasks)
```

#### Methods

##### `__init__(dag_registry, execution_engine, llm_manager=None)`

Initialize the DAG orchestrator.

**Parameters:**
- `dag_registry` (DAGRegistry): Registry for DAG validation and management
- `execution_engine` (ParallelExecutionEngine): Engine for parallel task execution
- `llm_manager` (LLMOrchestrationManager, optional): Manager for LLM task execution

**Example:**
```python
from dag_orchestration.core.dag_orchestrator import DAGOrchestrator
from dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine
from rm_ddd.core.dag_registry import DAGRegistry

dag_registry = DAGRegistry()
execution_engine = ParallelExecutionEngine(max_workers=4)
orchestrator = DAGOrchestrator(dag_registry, execution_engine)
```

##### `execute_dag(tasks: List[TaskDefinition]) -> OrchestrationResult`

Execute a DAG of tasks with dependency validation and parallel execution.

**Parameters:**
- `tasks` (List[TaskDefinition]): List of tasks to execute

**Returns:**
- `OrchestrationResult`: Result containing execution status, metrics, and task results

**Raises:**
- `CircularDependencyError`: If tasks contain circular dependencies
- `ValidationError`: If DAG validation fails
- `ExecutionError`: If task execution fails

**Example:**
```python
from dag_orchestration.core.task_definition import TaskDefinition

tasks = [
    TaskDefinition(
        id="task-1",
        name="Setup Infrastructure",
        dependencies=[],
        executor="python",
        command="python setup.py"
    ),
    TaskDefinition(
        id="task-2", 
        name="Run Tests",
        dependencies=["task-1"],
        executor="pytest",
        command="pytest tests/"
    )
]

result = orchestrator.execute_dag(tasks)
print(f"Execution status: {result.status}")
print(f"Completed tasks: {len(result.completed_tasks)}")
```

##### `validate_dag(tasks: List[TaskDefinition]) -> ValidationResult`

Validate DAG structure without executing tasks.

**Parameters:**
- `tasks` (List[TaskDefinition]): List of tasks to validate

**Returns:**
- `ValidationResult`: Validation result with cycle detection and topological ordering

**Example:**
```python
validation = orchestrator.validate_dag(tasks)
if validation.is_valid:
    print("DAG is valid")
    print(f"Execution order: {validation.topological_order}")
else:
    print(f"DAG validation failed: {validation.errors}")
```

##### `get_execution_status() -> ExecutionStatus`

Get current execution status and metrics.

**Returns:**
- `ExecutionStatus`: Current status including running tasks, completion rate, and resource usage

**Example:**
```python
status = orchestrator.get_execution_status()
print(f"Running tasks: {status.running_tasks}")
print(f"Completion rate: {status.completion_percentage}%")
print(f"Resource usage: {status.resource_usage}")
```

### ParallelExecutionEngine

Engine for executing tasks in parallel with resource management.

```python
from dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine

# Initialize with custom configuration
engine = ParallelExecutionEngine(
    max_workers=8,
    resource_limits={"cpu": 80, "memory": 70},
    execution_strategy=ExecutionStrategy.ADAPTIVE
)
```

#### Methods

##### `__init__(max_workers=4, resource_limits=None, execution_strategy=ExecutionStrategy.PARALLEL)`

Initialize the parallel execution engine.

**Parameters:**
- `max_workers` (int): Maximum number of concurrent workers
- `resource_limits` (dict, optional): Resource usage limits (cpu, memory percentages)
- `execution_strategy` (ExecutionStrategy): Execution strategy (PARALLEL, SEQUENTIAL, ADAPTIVE)

##### `execute_tasks(tasks: List[TaskDefinition]) -> List[TaskResult]`

Execute tasks in parallel with dependency awareness.

**Parameters:**
- `tasks` (List[TaskDefinition]): Tasks to execute

**Returns:**
- `List[TaskResult]`: Results for each executed task

**Example:**
```python
results = engine.execute_tasks(tasks)
for result in results:
    print(f"Task {result.task_id}: {result.status}")
    if result.status == TaskStatus.FAILED:
        print(f"Error: {result.error}")
```

##### `adjust_concurrency(resource_usage: ResourceUsage) -> int`

Dynamically adjust concurrency based on resource usage.

**Parameters:**
- `resource_usage` (ResourceUsage): Current resource usage metrics

**Returns:**
- `int`: New worker count

### LLMOrchestrationManager

Manager for LLM selection, cost tracking, and task execution.

```python
from dag_orchestration.execution.llm_orchestration_manager import LLMOrchestrationManager

# Initialize with budget constraints
llm_manager = LLMOrchestrationManager(
    cost_budget=100.0,
    preferred_providers=["cursor", "claude"]
)
```

#### Methods

##### `__init__(cost_budget=None, preferred_providers=None)`

Initialize LLM orchestration manager.

**Parameters:**
- `cost_budget` (float, optional): Maximum cost budget for LLM usage
- `preferred_providers` (List[str], optional): Preferred LLM providers in order

##### `select_llm_for_task(task: TaskDefinition) -> LLMSelection`

Select the best LLM for a specific task.

**Parameters:**
- `task` (TaskDefinition): Task requiring LLM execution

**Returns:**
- `LLMSelection`: Selected LLM with cost estimate and rationale

**Example:**
```python
selection = llm_manager.select_llm_for_task(task)
print(f"Selected LLM: {selection.provider}")
print(f"Estimated cost: ${selection.estimated_cost}")
print(f"Rationale: {selection.rationale}")
```

##### `execute_task_with_llm(task: TaskDefinition, llm_selection: LLMSelection) -> TaskResult`

Execute a task using the selected LLM.

**Parameters:**
- `task` (TaskDefinition): Task to execute
- `llm_selection` (LLMSelection): Selected LLM configuration

**Returns:**
- `TaskResult`: Execution result with cost tracking

##### `get_cost_summary() -> CostSummary`

Get current cost usage and budget status.

**Returns:**
- `CostSummary`: Cost breakdown by provider and task

**Example:**
```python
cost_summary = llm_manager.get_cost_summary()
print(f"Total cost: ${cost_summary.total_cost}")
print(f"Budget remaining: ${cost_summary.budget_remaining}")
print(f"Cost by provider: {cost_summary.cost_by_provider}")
```

### DependencyAwareScheduler

Scheduler that optimizes task execution order based on dependencies and resources.

```python
from dag_orchestration.execution.dependency_aware_scheduler import DependencyAwareScheduler

scheduler = DependencyAwareScheduler(
    strategy=SchedulingStrategy.CRITICAL_PATH,
    resource_predictor=resource_predictor
)
```

#### Methods

##### `schedule_tasks(tasks: List[TaskDefinition]) -> SchedulingPlan`

Create an optimized scheduling plan for tasks.

**Parameters:**
- `tasks` (List[TaskDefinition]): Tasks to schedule

**Returns:**
- `SchedulingPlan`: Optimized execution plan with timing and resource allocation

**Example:**
```python
plan = scheduler.schedule_tasks(tasks)
print(f"Total estimated time: {plan.estimated_duration}")
print(f"Critical path: {plan.critical_path}")
for batch in plan.execution_batches:
    print(f"Batch {batch.id}: {batch.task_ids}")
```

## Data Models

### TaskDefinition

Represents a task to be executed in the DAG.

```python
from dag_orchestration.core.task_definition import TaskDefinition

task = TaskDefinition(
    id="unique-task-id",
    name="Human readable task name",
    description="Detailed task description",
    dependencies=["dependency-task-id"],
    executor="python",  # or "llm", "shell", etc.
    command="python script.py",
    timeout=3600,  # seconds
    retry_count=3,
    resource_requirements={"cpu": 2, "memory": 1024}
)
```

#### Fields

- `id` (str): Unique task identifier
- `name` (str): Human-readable task name
- `description` (str): Detailed task description
- `dependencies` (List[str]): List of task IDs this task depends on
- `executor` (str): Executor type (python, llm, shell, etc.)
- `command` (str): Command or script to execute
- `timeout` (int, optional): Timeout in seconds
- `retry_count` (int, optional): Number of retry attempts
- `resource_requirements` (dict, optional): Resource requirements

### TaskResult

Result of task execution.

```python
class TaskResult:
    task_id: str
    status: TaskStatus  # PENDING, RUNNING, COMPLETED, FAILED
    start_time: datetime
    end_time: datetime
    duration: float  # seconds
    output: str
    error: str
    exit_code: int
    resource_usage: ResourceUsage
    cost: float  # for LLM tasks
```

### OrchestrationResult

Result of DAG orchestration execution.

```python
class OrchestrationResult:
    status: OrchestrationStatus  # COMPLETED, FAILED, PARTIAL
    total_tasks: int
    completed_tasks: List[TaskResult]
    failed_tasks: List[TaskResult]
    execution_time: float
    total_cost: float
    resource_usage_summary: ResourceUsage
    dag_metrics: DAGMetrics
```

### ValidationResult

Result of DAG validation.

```python
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    topological_order: List[str]
    cycle_detection_result: CycleDetectionResult
    dependency_graph: Dict[str, List[str]]
```

## Configuration

### ExecutionStrategy

Enumeration of execution strategies.

```python
from dag_orchestration.core.execution_strategy import ExecutionStrategy

# Available strategies
ExecutionStrategy.PARALLEL      # Maximum parallelization
ExecutionStrategy.SEQUENTIAL    # Sequential execution
ExecutionStrategy.ADAPTIVE      # Adaptive based on resources
ExecutionStrategy.CONSERVATIVE  # Conservative resource usage
```

### SchedulingStrategy

Enumeration of scheduling strategies.

```python
from dag_orchestration.execution.scheduling_strategy import SchedulingStrategy

# Available strategies
SchedulingStrategy.FIFO           # First In, First Out
SchedulingStrategy.PRIORITY       # Priority-based scheduling
SchedulingStrategy.CRITICAL_PATH  # Critical path optimization
SchedulingStrategy.RESOURCE_AWARE # Resource-aware scheduling
SchedulingStrategy.ADAPTIVE       # Adaptive strategy selection
```

### ResourceLimits

Configuration for resource limits.

```python
from dag_orchestration.core.resource_limits import ResourceLimits

limits = ResourceLimits(
    max_cpu_percent=80,      # Maximum CPU usage percentage
    max_memory_percent=70,   # Maximum memory usage percentage
    max_disk_io_mbps=100,    # Maximum disk I/O in MB/s
    max_network_mbps=50,     # Maximum network usage in MB/s
    max_concurrent_tasks=8   # Maximum concurrent tasks
)
```

## Error Handling

### Exception Hierarchy

```python
# Base exception
class DAGOrchestrationError(Exception):
    pass

# Validation errors
class ValidationError(DAGOrchestrationError):
    pass

class CircularDependencyError(ValidationError):
    pass

# Execution errors
class ExecutionError(DAGOrchestrationError):
    pass

class TaskExecutionError(ExecutionError):
    pass

class ResourceExhaustionError(ExecutionError):
    pass

# LLM errors
class LLMOrchestrationError(DAGOrchestrationError):
    pass

class LLMSelectionError(LLMOrchestrationError):
    pass

class CostBudgetExceededError(LLMOrchestrationError):
    pass
```

### Error Handling Patterns

```python
try:
    result = orchestrator.execute_dag(tasks)
except CircularDependencyError as e:
    print(f"Circular dependency detected: {e}")
    # Handle by breaking cycles or reordering tasks
except ResourceExhaustionError as e:
    print(f"Resource exhaustion: {e}")
    # Handle by reducing concurrency or freeing resources
except CostBudgetExceededError as e:
    print(f"Cost budget exceeded: {e}")
    # Handle by switching to cheaper LLMs or increasing budget
except DAGOrchestrationError as e:
    print(f"General orchestration error: {e}")
    # Handle with fallback strategies
```

## Integration with Beast Mode

### ReflectiveModule Integration

All DAG orchestration components inherit from ReflectiveModule for systematic observability.

```python
from rm_ddd.core.unified_reflective_module import ReflectiveModule

class CustomDAGComponent(ReflectiveModule):
    def __init__(self):
        super().__init__()
        self.module_id = "CustomDAGComponent"
    
    def get_capabilities(self) -> List[str]:
        return ["dag_processing", "task_execution"]
    
    def get_health_status(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "active_tasks": len(self.active_tasks),
            "resource_usage": self.get_resource_usage()
        }
```

### Prometheus Metrics

Automatic metrics collection for all components:

```python
# Metrics automatically available at /metrics endpoint
dag_orchestration_tasks_total
dag_orchestration_tasks_completed
dag_orchestration_tasks_failed
dag_orchestration_execution_duration_seconds
dag_orchestration_resource_usage_percent
dag_orchestration_llm_cost_total
```

### Health Endpoints

Standard health endpoints for all components:

- `/health` - Basic health check
- `/ready` - Readiness check for load balancers
- `/metrics` - Prometheus metrics
- `/status` - Detailed status information

## Usage Examples

### Basic DAG Execution

```python
from dag_orchestration.core.dag_orchestrator import DAGOrchestrator
from dag_orchestration.core.task_definition import TaskDefinition

# Create tasks
tasks = [
    TaskDefinition(
        id="setup",
        name="Setup Environment",
        command="python setup.py",
        dependencies=[]
    ),
    TaskDefinition(
        id="test",
        name="Run Tests", 
        command="pytest tests/",
        dependencies=["setup"]
    ),
    TaskDefinition(
        id="deploy",
        name="Deploy Application",
        command="python deploy.py",
        dependencies=["test"]
    )
]

# Execute DAG
orchestrator = DAGOrchestrator()
result = orchestrator.execute_dag(tasks)

if result.status == OrchestrationStatus.COMPLETED:
    print("All tasks completed successfully!")
else:
    print(f"Execution failed: {result.failed_tasks}")
```

### LLM Task Execution

```python
from dag_orchestration.execution.llm_orchestration_manager import LLMOrchestrationManager

# Create LLM task
llm_task = TaskDefinition(
    id="code-review",
    name="Automated Code Review",
    description="Review code changes for quality and security",
    executor="llm",
    command="Review the following code changes...",
    dependencies=["code-analysis"]
)

# Execute with LLM orchestration
llm_manager = LLMOrchestrationManager(cost_budget=50.0)
selection = llm_manager.select_llm_for_task(llm_task)
result = llm_manager.execute_task_with_llm(llm_task, selection)

print(f"Review completed by {selection.provider}")
print(f"Cost: ${result.cost}")
print(f"Output: {result.output}")
```

### Resource-Aware Execution

```python
from dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine
from dag_orchestration.core.resource_limits import ResourceLimits

# Configure resource limits
limits = ResourceLimits(
    max_cpu_percent=75,
    max_memory_percent=80,
    max_concurrent_tasks=6
)

# Create resource-aware engine
engine = ParallelExecutionEngine(
    max_workers=8,
    resource_limits=limits,
    execution_strategy=ExecutionStrategy.ADAPTIVE
)

# Execute with automatic resource adjustment
results = engine.execute_tasks(tasks)
```

This API reference provides comprehensive documentation for all major components and usage patterns in the DAG orchestration system.