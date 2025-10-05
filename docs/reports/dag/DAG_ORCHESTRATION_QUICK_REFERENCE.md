# DAG Orchestration - Quick Reference Card

## 🚀 **ESSENTIAL COMMANDS**

### **Basic Setup**
```python
from src.dag_orchestration.core.dag_orchestrator import DAGOrchestrator, OrchestrationConfig
from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition, ExecutionStrategy

# Create orchestrator
config = OrchestrationConfig(max_workers=10, execution_strategy=ExecutionStrategy.CONSERVATIVE)
orchestrator = DAGOrchestrator(config)
```

### **Define Tasks**
```python
# Simple task
task = TaskDefinition("task_id", "Task Name", dependencies={"dep1", "dep2"})

# Task with function
task = TaskDefinition("task_id", "Task Name", execution_function=my_function)

# Task with priority and timeout
task = TaskDefinition("task_id", "Task Name", priority=2, timeout_seconds=30.0)
```

### **Execute DAG**
```python
# Validate first
validation = orchestrator.validate_execution_plan(tasks)
print(f"Ready: {validation['readiness_assessment']}")

# Execute
result = await orchestrator.execute_dag(tasks)
print(f"Status: {result.status.value}, Success: {result.completed_tasks}/{result.total_tasks}")

# Cleanup
await orchestrator.shutdown()
```

## 📊 **MONITORING COMMANDS**

```python
# Health check
health = orchestrator.get_health_status()
print(f"Health: {health.status.value} ({health.health_score:.2f})")

# Current execution
status = orchestrator.get_current_orchestration_status()
if status: print(f"Active: {status['completed_tasks']}/{status['total_tasks']}")

# Statistics
stats = orchestrator.get_orchestration_statistics()
print(f"Success Rate: {stats['success_rate']:.1%}")
```

## ⚙️ **CONFIGURATION OPTIONS**

| Parameter | Options | Description |
|-----------|---------|-------------|
| `max_workers` | 1-50 | Parallel worker count |
| `execution_strategy` | CONSERVATIVE, AGGRESSIVE, SEQUENTIAL | Execution approach |
| `scheduling_strategy` | FIFO, PRIORITY, CRITICAL_PATH, ADAPTIVE | Task scheduling |
| `enable_prefire_testing` | True/False | Infrastructure validation |
| `enable_continuous_monitoring` | True/False | Real-time monitoring |

## 🔧 **TROUBLESHOOTING**

| Issue | Solution |
|-------|----------|
| Circular dependencies | Check `validation_report['plan_valid']` |
| High resource usage | Reduce `max_workers` or use CONSERVATIVE strategy |
| Task failures | Check `result.task_results[task_id].error_message` |
| Poor performance | Use ADAPTIVE scheduling, monitor `stats` |

## 📝 **TASK FUNCTION PATTERNS**

```python
# Sync function
def sync_task(arg1, arg2):
    return f"Result: {arg1 + arg2}"

# Async function  
async def async_task():
    await asyncio.sleep(1)
    return "Async result"

# Error handling
def robust_task():
    try:
        return perform_operation()
    except Exception as e:
        raise RuntimeError(f"Task failed: {e}")
```

## 🎯 **EXECUTION STRATEGIES**

- **CONSERVATIVE**: Balanced performance and stability
- **AGGRESSIVE**: Maximum parallelism for speed
- **SEQUENTIAL**: Safe fallback mode

## 📈 **SCHEDULING STRATEGIES**

- **ADAPTIVE**: Best overall performance (recommended)
- **CRITICAL_PATH**: Optimize for shortest completion time
- **PRIORITY**: Honor task priority settings
- **RESOURCE_AWARE**: Optimize resource utilization
- **FIFO**: Simple first-in-first-out

## 🚨 **EMERGENCY COMMANDS**

```python
# Force shutdown
await orchestrator.shutdown()

# Check all component health
for name, health in orchestrator.get_module_info()['component_status'].items():
    print(f"{name}: {health}")

# Clear caches
orchestrator._infrastructure_validator.clear_validation_cache()
```

---

**📖 Full Documentation**: `DAG_ORCHESTRATION_OPERATING_INSTRUCTIONS.md`  
**🎮 Demo**: `python demo_dag_orchestration_system.py`  
**🧪 Tests**: `python -m pytest test_dag_orchestrator.py -v`