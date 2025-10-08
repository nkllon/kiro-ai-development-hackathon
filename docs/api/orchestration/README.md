# Orchestration APIs

## Overview

The Orchestration APIs provide DAG-based task execution, dependency management, and comprehensive execution tracking. These APIs enable systematic orchestration of complex AI workflows with parallel execution, health monitoring, and state persistence.

## Components

### [Constellation Orchestrator](./constellation-orchestrator.md)
Main orchestration engine for DAG-based AI prompt execution with multi-agent coordination.

**Key Features:**
- DAG-based task dependency management
- Parallel task execution
- Multi-agent coordination
- Comprehensive health monitoring
- Graceful degradation and recovery

### [Execution Tracking](./execution-tracking.md)
Redis-based centralized tracking of specification executions with status monitoring and history.

**Key Features:**
- Redis-based state persistence
- Real-time execution monitoring
- Check-in history tracking
- Stuck execution detection
- Comprehensive execution analytics

### [DAG Management](./dag-management.md)
Dependency graph management with cycle detection and execution order optimization.

**Key Features:**
- Dependency cycle detection
- Execution order optimization
- Task validation and verification
- Dynamic dependency resolution

## Quick Reference

### Basic Orchestration

```python
from src.constellation_orchestrator.core.orchestrator import ConstellationOrchestrator
from src.constellation_orchestrator.models.task_definition import TaskDefinition

# Initialize orchestrator
orchestrator = ConstellationOrchestrator()
await orchestrator.initialize()

# Define tasks with dependencies
tasks = [
    TaskDefinition(
        task_id="setup",
        name="System Setup",
        dependencies=[],
        prompt_template="Initialize system"
    ),
    TaskDefinition(
        task_id="process",
        name="Data Processing", 
        dependencies=["setup"],
        prompt_template="Process data"
    )
]

# Execute tasks
await orchestrator.load_tasks(tasks)
execution_id = await orchestrator.start_execution()

# Monitor execution
while True:
    state = await orchestrator.get_execution_state(execution_id)
    if state.status.value in ['completed', 'failed']:
        break
    await asyncio.sleep(5)

await orchestrator.shutdown()
```

### Execution Tracking

```python
from src.execution_tracking.redis_execution_tracker import (
    initialize_execution_tracker,
    start_tracking_execution,
    update_execution_status,
    checkin_execution,
    ExecutionStatus
)

# Initialize tracking
await initialize_execution_tracker()

# Start tracking execution
execution_id = await start_tracking_execution(
    "my_pipeline",
    total_tasks=5,
    estimated_hours=2.0
)

# Update status and check in
await update_execution_status(execution_id, ExecutionStatus.RUNNING)
await checkin_execution(
    execution_id,
    phase="processing",
    progress_percentage=50.0,
    message="Halfway complete"
)

# Complete execution
await update_execution_status(execution_id, ExecutionStatus.COMPLETED)
```

### Integrated Usage

```python
async def integrated_orchestration():
    # Initialize both systems
    await initialize_execution_tracker()
    orchestrator = ConstellationOrchestrator()
    await orchestrator.initialize()
    
    # Start tracking
    tracking_id = await start_tracking_execution("integrated_pipeline")
    
    # Execute with orchestrator
    tasks = create_task_definitions()
    await orchestrator.load_tasks(tasks)
    execution_id = await orchestrator.start_execution()
    
    # Monitor both systems
    while True:
        orch_state = await orchestrator.get_execution_state(execution_id)
        if not orch_state:
            break
        
        # Update tracking
        progress = (orch_state.completed_tasks / orch_state.total_tasks) * 100
        await checkin_execution(
            tracking_id,
            progress_percentage=progress,
            message=f"Orchestrator: {orch_state.status.value}"
        )
        
        if orch_state.status.value in ['completed', 'failed']:
            break
        
        await asyncio.sleep(10)
    
    await orchestrator.shutdown()
```

## Architecture Patterns

### DAG-Based Execution
Tasks are organized in a Directed Acyclic Graph (DAG) where:
- Each task has explicit dependencies
- Parallel execution is automatic for independent tasks
- Dependency cycles are detected and prevented
- Execution order is optimized for performance

### Multi-Agent Coordination
The orchestrator manages multiple AI agents:
- Agent pool management with load balancing
- Task assignment based on agent capabilities
- Health monitoring and failover
- Resource usage optimization

### State Persistence
All execution state is persisted in Redis:
- Real-time status updates
- Check-in history tracking
- Execution analytics and metrics
- Recovery from failures

## Best Practices

### 1. Task Definition

```python
# ✅ CORRECT: Well-defined tasks
TaskDefinition(
    task_id="unique_id",
    name="Human Readable Name",
    description="Clear description",
    dependencies=["prerequisite_task"],
    prompt_template="Specific prompt with {parameters}",
    expected_output="Clear expected output",
    timeout_seconds=1800,
    retry_count=3
)
```

### 2. Error Handling

```python
# ✅ CORRECT: Comprehensive error handling
try:
    execution_id = await orchestrator.start_execution()
except Exception as e:
    degradation = await orchestrator.graceful_degradation(e)
    if degradation.success:
        # Continue with reduced functionality
        pass
    else:
        raise
```

### 3. Resource Management

```python
# ✅ CORRECT: Always cleanup resources
try:
    await orchestrator.initialize()
    # Your execution logic
finally:
    await orchestrator.shutdown()
```

### 4. Health Monitoring

```python
# ✅ CORRECT: Regular health checks
health = await orchestrator.health_check()
if not health.get('components_healthy', False):
    print("Components unhealthy - taking corrective action")
    # Implement recovery logic
```

## Performance Considerations

### Concurrency Control
- Configure `max_concurrent_tasks` based on system resources
- Use agent pool sizing to control resource usage
- Implement task timeouts to prevent runaway executions

### Memory Management
- Monitor execution state size
- Clean up old execution records regularly
- Use check-in intervals appropriate for task duration

### Scalability
- Redis-based state enables horizontal scaling
- Agent pools can be distributed across multiple machines
- Execution tracking supports thousands of concurrent executions

---

**Components:** [Constellation Orchestrator](./constellation-orchestrator.md) | [Execution Tracking](./execution-tracking.md) | [DAG Management](./dag-management.md)