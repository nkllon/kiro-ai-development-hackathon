# Getting Started with DAG Orchestration

## Prerequisites

Before using the DAG orchestration system, ensure you have:

1. **Python 3.9+** installed
2. **Redis server** running (for distributed coordination)
3. **Required dependencies** installed
4. **LLM CLI tools** (optional, for AI-powered tasks)

### System Requirements

- **CPU**: 2+ cores recommended for parallel execution
- **Memory**: 4GB+ RAM for moderate workloads
- **Disk**: 1GB+ free space for logs and temporary files
- **Network**: Internet access for LLM providers (if used)

## Installation

### 1. Check Prerequisites

Run the prerequisite checker to validate your environment:

```bash
bash scripts/check_dag_orchestrated_parallel_execution_prereqs.sh
```

This will check for:
- Python dependencies
- Redis connectivity
- System resources
- LLM CLI availability

### 2. Install Dependencies

If prerequisites are missing, install them:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Redis (if not running)
redis-server --daemonize yes

# Install LLM CLI tools (optional)
# For Cursor CLI: Follow Cursor installation guide
# For Claude CLI: pip install claude-cli
```

### 3. Verify Installation

Test the installation with a simple example:

```bash
python -c "
from dag_orchestration.core.dag_orchestrator import DAGOrchestrator
print('DAG Orchestration system ready!')
"
```

## Your First DAG

Let's create a simple DAG with three tasks that demonstrate dependency management.

### Step 1: Create Task Definitions

Create a file called `my_first_dag.py`:

```python
#!/usr/bin/env python3
"""
My First DAG - A simple example demonstrating DAG orchestration
"""

from dag_orchestration.core.dag_orchestrator import DAGOrchestrator
from dag_orchestration.core.task_definition import TaskDefinition
from dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine
from rm_ddd.core.dag_registry import DAGRegistry

def create_sample_tasks():
    """Create a sample set of tasks with dependencies."""
    
    tasks = [
        TaskDefinition(
            id="setup-env",
            name="Setup Environment",
            description="Initialize the working environment",
            command="echo 'Setting up environment...' && sleep 2",
            executor="shell",
            dependencies=[],
            timeout=30
        ),
        
        TaskDefinition(
            id="fetch-data",
            name="Fetch Data",
            description="Download required data files",
            command="echo 'Fetching data...' && sleep 3",
            executor="shell", 
            dependencies=["setup-env"],
            timeout=60
        ),
        
        TaskDefinition(
            id="process-data",
            name="Process Data",
            description="Process the downloaded data",
            command="echo 'Processing data...' && sleep 2",
            executor="shell",
            dependencies=["fetch-data"],
            timeout=120
        ),
        
        TaskDefinition(
            id="generate-report",
            name="Generate Report",
            description="Generate final report",
            command="echo 'Generating report...' && sleep 1",
            executor="shell",
            dependencies=["process-data"],
            timeout=60
        ),
        
        TaskDefinition(
            id="cleanup",
            name="Cleanup",
            description="Clean up temporary files",
            command="echo 'Cleaning up...' && sleep 1",
            executor="shell",
            dependencies=["generate-report"],
            timeout=30
        )
    ]
    
    return tasks

def main():
    """Execute the sample DAG."""
    
    print("🚀 My First DAG Execution")
    print("=" * 30)
    
    # Create components
    dag_registry = DAGRegistry()
    execution_engine = ParallelExecutionEngine(max_workers=3)
    orchestrator = DAGOrchestrator(dag_registry, execution_engine)
    
    # Create tasks
    tasks = create_sample_tasks()
    
    print(f"📋 Created {len(tasks)} tasks")
    
    # Validate DAG structure
    print("\n🔍 Validating DAG structure...")
    validation = orchestrator.validate_dag(tasks)
    
    if not validation.is_valid:
        print("❌ DAG validation failed:")
        for error in validation.errors:
            print(f"   • {error}")
        return False
    
    print("✅ DAG validation passed")
    print(f"📊 Execution order: {' → '.join(validation.topological_order)}")
    
    # Execute DAG
    print("\n🎯 Executing DAG...")
    result = orchestrator.execute_dag(tasks)
    
    # Report results
    print(f"\n📊 Execution Results:")
    print(f"   Status: {result.status}")
    print(f"   Total tasks: {result.total_tasks}")
    print(f"   Completed: {len(result.completed_tasks)}")
    print(f"   Failed: {len(result.failed_tasks)}")
    print(f"   Duration: {result.execution_time:.2f}s")
    
    if result.failed_tasks:
        print("\n❌ Failed tasks:")
        for task_result in result.failed_tasks:
            print(f"   • {task_result.task_id}: {task_result.error}")
    
    return result.status == "COMPLETED"

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
```

### Step 2: Run Your First DAG

Execute the DAG:

```bash
python my_first_dag.py
```

You should see output like:

```
🚀 My First DAG Execution
==============================
📋 Created 5 tasks

🔍 Validating DAG structure...
✅ DAG validation passed
📊 Execution order: setup-env → fetch-data → process-data → generate-report → cleanup

🎯 Executing DAG...
📊 Execution Results:
   Status: COMPLETED
   Total tasks: 5
   Completed: 5
   Failed: 0
   Duration: 9.23s
```

### Step 3: Understanding the Output

The execution shows several key concepts:

1. **DAG Validation**: The system validates that tasks form a valid DAG (no cycles)
2. **Topological Ordering**: Tasks are ordered based on dependencies
3. **Parallel Execution**: Independent tasks can run concurrently
4. **Result Tracking**: Complete execution metrics are provided

## Adding Parallel Tasks

Let's modify the example to show parallel execution:

```python
def create_parallel_tasks():
    """Create tasks that can run in parallel."""
    
    tasks = [
        TaskDefinition(
            id="setup",
            name="Setup",
            command="echo 'Setup complete' && sleep 1",
            executor="shell",
            dependencies=[]
        ),
        
        # These three tasks can run in parallel after setup
        TaskDefinition(
            id="task-a",
            name="Task A",
            command="echo 'Task A running' && sleep 3",
            executor="shell",
            dependencies=["setup"]
        ),
        
        TaskDefinition(
            id="task-b", 
            name="Task B",
            command="echo 'Task B running' && sleep 2",
            executor="shell",
            dependencies=["setup"]
        ),
        
        TaskDefinition(
            id="task-c",
            name="Task C", 
            command="echo 'Task C running' && sleep 4",
            executor="shell",
            dependencies=["setup"]
        ),
        
        # Final task depends on all parallel tasks
        TaskDefinition(
            id="finalize",
            name="Finalize",
            command="echo 'All tasks complete!'",
            executor="shell",
            dependencies=["task-a", "task-b", "task-c"]
        )
    ]
    
    return tasks
```

This creates a DAG where tasks A, B, and C run in parallel after setup completes.

## Working with LLM Tasks

The system supports AI-powered tasks using LLM providers:

### Step 1: Configure LLM Provider

First, ensure you have an LLM CLI tool installed (e.g., Cursor):

```bash
# Check available LLM providers
python -c "
from dag_orchestration.execution.llm_orchestration_manager import LLMOrchestrationManager
manager = LLMOrchestrationManager()
print('Available LLMs:', list(manager.available_llms.keys()))
"
```

### Step 2: Create LLM Tasks

```python
def create_llm_tasks():
    """Create tasks that use LLM providers."""
    
    tasks = [
        TaskDefinition(
            id="analyze-code",
            name="Code Analysis",
            description="Analyze code quality and suggest improvements",
            command="Analyze the following Python code for quality issues...",
            executor="llm",
            dependencies=[],
            timeout=300
        ),
        
        TaskDefinition(
            id="generate-docs",
            name="Generate Documentation", 
            description="Generate API documentation from code",
            command="Generate comprehensive API documentation for...",
            executor="llm",
            dependencies=["analyze-code"],
            timeout=600
        ),
        
        TaskDefinition(
            id="create-tests",
            name="Create Unit Tests",
            description="Generate unit tests for the analyzed code",
            command="Create comprehensive unit tests for...",
            executor="llm", 
            dependencies=["analyze-code"],
            timeout=400
        )
    ]
    
    return tasks

def execute_llm_dag():
    """Execute DAG with LLM tasks."""
    
    from dag_orchestration.execution.llm_orchestration_manager import LLMOrchestrationManager
    
    # Create orchestrator with LLM support
    dag_registry = DAGRegistry()
    execution_engine = ParallelExecutionEngine(max_workers=2)
    llm_manager = LLMOrchestrationManager(cost_budget=10.0)
    
    orchestrator = DAGOrchestrator(
        dag_registry=dag_registry,
        execution_engine=execution_engine,
        llm_manager=llm_manager
    )
    
    # Execute LLM tasks
    tasks = create_llm_tasks()
    result = orchestrator.execute_dag(tasks)
    
    # Show cost summary
    cost_summary = llm_manager.get_cost_summary()
    print(f"💰 Total LLM cost: ${cost_summary.total_cost}")
    print(f"💳 Budget remaining: ${cost_summary.budget_remaining}")
    
    return result
```

## Resource Management

The system automatically manages resources during execution:

### Configure Resource Limits

```python
from dag_orchestration.core.resource_limits import ResourceLimits
from dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine

# Set resource limits
limits = ResourceLimits(
    max_cpu_percent=75,      # Don't exceed 75% CPU
    max_memory_percent=80,   # Don't exceed 80% memory
    max_concurrent_tasks=4   # Maximum 4 tasks at once
)

# Create resource-aware engine
engine = ParallelExecutionEngine(
    max_workers=6,
    resource_limits=limits,
    execution_strategy=ExecutionStrategy.ADAPTIVE
)
```

### Monitor Resource Usage

```python
# During execution, check resource usage
status = orchestrator.get_execution_status()
print(f"CPU usage: {status.resource_usage.cpu_percent}%")
print(f"Memory usage: {status.resource_usage.memory_percent}%")
print(f"Active tasks: {len(status.running_tasks)}")
```

## Error Handling

Handle common error scenarios:

```python
from dag_orchestration.core.exceptions import (
    CircularDependencyError,
    ResourceExhaustionError,
    TaskExecutionError
)

try:
    result = orchestrator.execute_dag(tasks)
    
except CircularDependencyError as e:
    print(f"❌ Circular dependency detected: {e}")
    print("💡 Check task dependencies for cycles")
    
except ResourceExhaustionError as e:
    print(f"❌ Resource exhaustion: {e}")
    print("💡 Reduce concurrency or free up system resources")
    
except TaskExecutionError as e:
    print(f"❌ Task execution failed: {e}")
    print("💡 Check task commands and dependencies")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print("💡 Check logs for detailed error information")
```

## Monitoring and Observability

The system provides comprehensive monitoring:

### Health Checks

```python
# Check system health
health = orchestrator.get_health_status()
print(f"System status: {health['status']}")
print(f"Active components: {health['active_components']}")
```

### Prometheus Metrics

Access metrics at the `/metrics` endpoint:

```bash
curl http://localhost:8888/metrics
```

Key metrics include:
- `dag_orchestration_tasks_total` - Total tasks executed
- `dag_orchestration_execution_duration_seconds` - Execution time
- `dag_orchestration_resource_usage_percent` - Resource usage

### Logging

All operations are logged with structured data:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logs will include correlation IDs and execution context
```

## Best Practices

### 1. Task Design

- **Keep tasks focused**: Each task should have a single responsibility
- **Make tasks idempotent**: Tasks should be safe to retry
- **Set appropriate timeouts**: Prevent tasks from hanging indefinitely
- **Handle failures gracefully**: Include error handling in task commands

### 2. Dependency Management

- **Minimize dependencies**: Reduce coupling between tasks
- **Validate dependencies**: Ensure all dependencies are necessary
- **Avoid deep chains**: Long dependency chains reduce parallelization
- **Test DAG structure**: Always validate before execution

### 3. Resource Management

- **Set resource limits**: Prevent resource exhaustion
- **Monitor usage**: Track resource consumption during execution
- **Scale appropriately**: Adjust worker count based on workload
- **Plan for peak usage**: Consider maximum resource requirements

### 4. Error Handling

- **Implement retries**: Use retry logic for transient failures
- **Isolate failures**: Prevent task failures from cascading
- **Log comprehensively**: Include detailed error information
- **Plan recovery**: Have strategies for handling failures

## Next Steps

Now that you understand the basics:

1. **Explore Examples**: Check out [examples/](examples/) for more complex patterns
2. **Read API Reference**: See [api-reference.md](api-reference.md) for detailed API docs
3. **Integration Guide**: Learn about [Beast Mode integration](integration-guide.md)
4. **Performance Tuning**: Optimize your DAGs with [performance-tuning.md](performance-tuning.md)
5. **Troubleshooting**: Solve common issues with [troubleshooting.md](troubleshooting.md)

## Common Patterns

### Sequential Pipeline

```python
# Tasks that must run in order
tasks = [
    TaskDefinition(id="step1", dependencies=[]),
    TaskDefinition(id="step2", dependencies=["step1"]),
    TaskDefinition(id="step3", dependencies=["step2"]),
]
```

### Fan-Out/Fan-In

```python
# One task triggers multiple parallel tasks, then converges
tasks = [
    TaskDefinition(id="trigger", dependencies=[]),
    TaskDefinition(id="parallel1", dependencies=["trigger"]),
    TaskDefinition(id="parallel2", dependencies=["trigger"]),
    TaskDefinition(id="parallel3", dependencies=["trigger"]),
    TaskDefinition(id="converge", dependencies=["parallel1", "parallel2", "parallel3"]),
]
```

### Diamond Pattern

```python
# Complex dependency pattern
tasks = [
    TaskDefinition(id="start", dependencies=[]),
    TaskDefinition(id="left", dependencies=["start"]),
    TaskDefinition(id="right", dependencies=["start"]),
    TaskDefinition(id="end", dependencies=["left", "right"]),
]
```

This getting started guide provides a comprehensive introduction to using the DAG orchestration system effectively.