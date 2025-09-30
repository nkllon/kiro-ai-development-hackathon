# DAG Orchestrated Parallel Execution - Operating Instructions

## 📋 **SYSTEM OVERVIEW**

The DAG Orchestrated Parallel Execution System provides intelligent, mathematically-validated parallel task execution with comprehensive monitoring and learning capabilities.

---

## 🚀 **QUICK START GUIDE**

### **1. Basic Usage**

```python
import asyncio
from src.dag_orchestration.core.dag_orchestrator import (
    DAGOrchestrator, 
    OrchestrationConfig
)
from src.dag_orchestration.execution.parallel_execution_engine import (
    TaskDefinition,
    ExecutionStrategy
)

# Create configuration
config = OrchestrationConfig(
    max_workers=10,
    execution_strategy=ExecutionStrategy.CONSERVATIVE,
    enable_prefire_testing=True
)

# Create orchestrator
orchestrator = DAGOrchestrator(config)

# Define tasks
tasks = [
    TaskDefinition("task_1", "First Task", dependencies=set()),
    TaskDefinition("task_2", "Second Task", dependencies={"task_1"})
]

# Execute DAG
async def main():
    result = await orchestrator.execute_dag(tasks)
    print(f"Execution completed: {result.status.value}")
    await orchestrator.shutdown()

asyncio.run(main())
```

### **2. Run Demo**

```bash
python demo_dag_orchestration_system.py
```

---

## ⚙️ **CONFIGURATION OPTIONS**

### **OrchestrationConfig Parameters**

```python
config = OrchestrationConfig(
    max_workers=10,                    # Maximum parallel workers
    execution_strategy=ExecutionStrategy.CONSERVATIVE,  # CONSERVATIVE, AGGRESSIVE, SEQUENTIAL
    scheduling_strategy=SchedulingStrategy.ADAPTIVE,    # FIFO, PRIORITY, CRITICAL_PATH, RESOURCE_AWARE, ADAPTIVE
    enable_prefire_testing=True,       # Infrastructure validation before execution
    enable_continuous_monitoring=True, # Real-time system monitoring
    timeout_seconds=None              # Optional execution timeout
)
```

### **Execution Strategies**

- **CONSERVATIVE**: Balanced approach with moderate parallelism
- **AGGRESSIVE**: Maximum parallelism for performance
- **SEQUENTIAL**: Fallback to sequential execution

### **Scheduling Strategies**

- **FIFO**: First In, First Out scheduling
- **PRIORITY**: Priority-based task scheduling
- **CRITICAL_PATH**: Critical path method optimization
- **RESOURCE_AWARE**: Resource-optimized scheduling
- **ADAPTIVE**: Combines multiple factors intelligently

---

## 📝 **TASK DEFINITION**

### **Creating Tasks**

```python
from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition

# Simple task
task = TaskDefinition(
    task_id="unique_task_id",
    name="Human Readable Name",
    dependencies={"dependency_task_1", "dependency_task_2"},
    execution_function=my_function,
    execution_args=(arg1, arg2),
    execution_kwargs={"key": "value"},
    priority=1,                    # Higher number = higher priority
    timeout_seconds=30.0,          # Optional timeout
    max_retries=3                  # Retry attempts on failure
)

# Task with async function
async def async_task():
    await asyncio.sleep(1)
    return "Async result"

async_task_def = TaskDefinition(
    task_id="async_task",
    name="Async Task",
    execution_function=async_task
)
```

### **Task Function Requirements**

- Functions can be sync or async
- Should return a result value
- Exceptions will be caught and reported
- Use `await` for async operations

---

## 🔍 **VALIDATION AND MONITORING**

### **Pre-execution Validation**

```python
# Validate execution plan before running
validation_report = orchestrator.validate_execution_plan(tasks)

print(f"Plan Valid: {validation_report['plan_valid']}")
print(f"Readiness Score: {validation_report['readiness_score']}")
print(f"Assessment: {validation_report['readiness_assessment']}")

if validation_report['recommendations']:
    print("Recommendations:")
    for rec in validation_report['recommendations']:
        print(f"  • {rec}")
```

### **Health Monitoring**

```python
# Check orchestrator health
health = orchestrator.get_health_status()
print(f"Health: {health.status.value} (score: {health.health_score})")

# Get system statistics
stats = orchestrator.get_orchestration_statistics()
print(f"Success Rate: {stats['success_rate']:.1%}")
print(f"Average Duration: {stats['average_duration_seconds']:.2f}s")
```

### **Real-time Status**

```python
# Check current execution status
current_status = orchestrator.get_current_orchestration_status()
if current_status:
    print(f"Active: {current_status['orchestration_id']}")
    print(f"Progress: {current_status['completed_tasks']}/{current_status['total_tasks']}")

# Get execution history
history = orchestrator.get_orchestration_history(limit=5)
for execution in history:
    print(f"{execution['orchestration_id']}: {execution['status']}")
```

---

## 📊 **EXECUTION RESULTS**

### **Result Analysis**

```python
result = await orchestrator.execute_dag(tasks)

# Basic information
print(f"Orchestration ID: {result.orchestration_id}")
print(f"Status: {result.status.value}")
print(f"Duration: {result.duration_seconds:.2f}s")
print(f"Success Rate: {result.completed_tasks/result.total_tasks:.1%}")

# Task details
for task_id, task_result in result.task_results.items():
    print(f"{task_id}: {task_result.status.value} ({task_result.duration_seconds:.2f}s)")
    if task_result.error:
        print(f"  Error: {task_result.error_message}")

# Performance metrics
if result.performance_metrics:
    engine_stats = result.performance_metrics['execution_engine_stats']
    print(f"Engine Success Rate: {engine_stats['success_rate']:.1%}")
    
    learning_insights = result.performance_metrics.get('learning_insights', {})
    if learning_insights.get('optimization_suggestions'):
        print("AI Optimization Suggestions:")
        for suggestion in learning_insights['optimization_suggestions']:
            print(f"  • {suggestion['suggestion']} (confidence: {suggestion['confidence']:.1%})")
```

---

## 🛠️ **ADVANCED USAGE**

### **Custom Task Functions**

```python
# Task with complex logic
def data_processing_task(input_data, config):
    """Process data with configuration."""
    processed = []
    for item in input_data:
        if item > config['threshold']:
            processed.append(item * config['multiplier'])
    return processed

# Task with external API calls
async def api_integration_task(endpoint, payload):
    """Integrate with external API."""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=payload) as response:
            return await response.json()

# Task with file operations
def file_processing_task(input_file, output_file):
    """Process files."""
    with open(input_file, 'r') as f:
        data = f.read()
    
    processed_data = data.upper()  # Example processing
    
    with open(output_file, 'w') as f:
        f.write(processed_data)
    
    return f"Processed {len(data)} characters"
```

### **Error Handling**

```python
def robust_task():
    """Task with built-in error handling."""
    try:
        # Your task logic here
        result = perform_operation()
        return result
    except SpecificException as e:
        # Handle specific errors
        return f"Handled error: {e}"
    except Exception as e:
        # Re-raise unexpected errors for orchestrator handling
        raise RuntimeError(f"Task failed: {e}")

# Task with retry logic (handled by orchestrator)
retry_task = TaskDefinition(
    task_id="retry_task",
    name="Task with Retries",
    execution_function=potentially_failing_function,
    max_retries=5,
    timeout_seconds=60.0
)
```

### **Resource Management**

```python
# Resource-intensive task
heavy_task = TaskDefinition(
    task_id="heavy_computation",
    name="Heavy Computation",
    execution_function=cpu_intensive_function,
    resource_requirements={
        'weight': 3.0,        # Higher resource weight
        'cpu_cores': 4,       # Preferred CPU cores
        'memory_mb': 2048     # Memory requirement
    },
    priority=2                # Higher priority
)

# I/O bound task
io_task = TaskDefinition(
    task_id="file_operations",
    name="File Operations", 
    execution_function=file_processing_function,
    resource_requirements={
        'weight': 0.5,        # Lower resource weight
        'io_intensive': True  # Mark as I/O bound
    }
)
```

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues**

#### **1. Circular Dependencies**
```
Error: Task creates circular dependency
```
**Solution**: Check task dependencies for cycles. Use validation to identify problematic dependencies.

```python
validation_report = orchestrator.validate_execution_plan(tasks)
if not validation_report['plan_valid']:
    print("DAG validation failed - check for circular dependencies")
```

#### **2. Resource Exhaustion**
```
Warning: High resource utilization
```
**Solution**: Reduce max_workers or optimize task resource requirements.

```python
config = OrchestrationConfig(
    max_workers=5,  # Reduce workers
    execution_strategy=ExecutionStrategy.CONSERVATIVE
)
```

#### **3. Task Failures**
```
Task failed with error: [error message]
```
**Solution**: Check task function implementation and add error handling.

```python
# Check failed tasks
for task_id, result in execution_result.task_results.items():
    if result.status.value == "failed":
        print(f"Failed task {task_id}: {result.error_message}")
```

### **Debug Mode**

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Check component health
health = orchestrator.get_health_status()
if health.issues:
    print("Health Issues:")
    for issue in health.issues:
        print(f"  • {issue}")
```

---

## 📈 **PERFORMANCE OPTIMIZATION**

### **Tuning Guidelines**

1. **Worker Count**: Start with CPU core count, adjust based on workload
2. **Execution Strategy**: Use AGGRESSIVE for CPU-bound, CONSERVATIVE for mixed workloads
3. **Scheduling Strategy**: ADAPTIVE works well for most cases, CRITICAL_PATH for time-sensitive workflows
4. **Resource Requirements**: Set appropriate weights for resource-intensive tasks

### **Monitoring Performance**

```python
# Get detailed performance metrics
stats = orchestrator.get_orchestration_statistics()
component_stats = stats['component_statistics']

print(f"Parallel Engine Success Rate: {component_stats['parallel_engine']['success_rate']:.1%}")
print(f"Scheduler Decisions: {component_stats['scheduler']['total_scheduling_decisions']}")
print(f"Validation Cache Hit Rate: {component_stats['infrastructure_validator']['cache_hit_rate']:.1%}")
```

---

## 🔒 **SECURITY CONSIDERATIONS**

### **Task Function Security**

- Validate all inputs in task functions
- Use proper error handling to prevent information leakage
- Avoid executing untrusted code in task functions
- Implement proper authentication for external API calls

### **Resource Limits**

```python
# Set conservative resource limits
config = OrchestrationConfig(
    max_workers=5,                    # Limit parallel workers
    timeout_seconds=300,              # Set execution timeout
    enable_continuous_monitoring=True # Monitor resource usage
)
```

---

## 📚 **API REFERENCE**

### **Main Classes**

- `DAGOrchestrator`: Main orchestration component
- `OrchestrationConfig`: Configuration settings
- `TaskDefinition`: Task definition structure
- `OrchestrationResult`: Execution result data

### **Key Methods**

- `execute_dag(tasks)`: Execute DAG with tasks
- `validate_execution_plan(tasks)`: Validate before execution
- `get_health_status()`: Check system health
- `get_orchestration_statistics()`: Get performance stats
- `shutdown()`: Clean shutdown

### **Enums**

- `ExecutionStrategy`: CONSERVATIVE, AGGRESSIVE, SEQUENTIAL
- `SchedulingStrategy`: FIFO, PRIORITY, CRITICAL_PATH, RESOURCE_AWARE, ADAPTIVE
- `OrchestrationStatus`: IDLE, VALIDATING, SCHEDULING, EXECUTING, COMPLETED, FAILED, CANCELLED

---

## 🆘 **SUPPORT**

### **Getting Help**

1. Check validation reports for configuration issues
2. Review health status for component problems
3. Examine execution results for task-specific errors
4. Use debug logging for detailed troubleshooting

### **Best Practices**

1. Always validate execution plans before running
2. Monitor system health regularly
3. Use appropriate resource requirements for tasks
4. Implement proper error handling in task functions
5. Shutdown orchestrator cleanly when done

---

*For additional support, refer to the comprehensive test suite in `test_dag_orchestrator.py` and the working demo in `demo_dag_orchestration_system.py`.*