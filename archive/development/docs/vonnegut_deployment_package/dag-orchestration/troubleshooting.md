# DAG Orchestration Troubleshooting Guide

## Common Issues and Solutions

### 1. DAG Validation Failures

#### Circular Dependencies Detected

**Symptoms:**
```
❌ DAG validation failed:
   • Circular dependency detected: task-a → task-b → task-c → task-a
```

**Causes:**
- Tasks have circular dependency relationships
- Incorrect dependency specification
- Copy-paste errors in task definitions

**Solutions:**

1. **Identify the cycle:**
```python
validation = orchestrator.validate_dag(tasks)
if not validation.is_valid:
    for error in validation.errors:
        if "Circular dependency" in error:
            print(f"Cycle found: {error}")
```

2. **Break the cycle by removing unnecessary dependencies:**
```python
# Before (circular)
TaskDefinition(id="task-a", dependencies=["task-c"])
TaskDefinition(id="task-b", dependencies=["task-a"])  
TaskDefinition(id="task-c", dependencies=["task-b"])

# After (fixed)
TaskDefinition(id="task-a", dependencies=[])
TaskDefinition(id="task-b", dependencies=["task-a"])
TaskDefinition(id="task-c", dependencies=["task-b"])
```

3. **Use DAG visualization to identify cycles:**
```python
from dag_orchestration.utils.dag_visualizer import visualize_dag
visualize_dag(tasks, output_file="dag_debug.png")
```

#### Missing Dependencies

**Symptoms:**
```
❌ Task execution failed: Dependency 'missing-task' not found
```

**Solutions:**

1. **Check dependency names match task IDs exactly:**
```python
# Ensure dependency names match task IDs
task_ids = [task.id for task in tasks]
for task in tasks:
    for dep in task.dependencies:
        if dep not in task_ids:
            print(f"Missing dependency: {dep} for task {task.id}")
```

2. **Add missing tasks or remove invalid dependencies:**
```python
# Add the missing task
missing_task = TaskDefinition(
    id="missing-task",
    name="Missing Task",
    command="echo 'Added missing task'",
    dependencies=[]
)
tasks.append(missing_task)
```

### 2. Execution Failures

#### Task Timeout Errors

**Symptoms:**
```
❌ Task 'long-running-task' failed: Execution timeout after 300s
```

**Solutions:**

1. **Increase task timeout:**
```python
TaskDefinition(
    id="long-running-task",
    timeout=600,  # Increase from 300s to 600s
    # ... other parameters
)
```

2. **Optimize task execution:**
```python
# Break long tasks into smaller chunks
TaskDefinition(id="process-part-1", timeout=300),
TaskDefinition(id="process-part-2", dependencies=["process-part-1"], timeout=300),
```

3. **Monitor task progress:**
```python
def monitor_long_task():
    while True:
        status = orchestrator.get_execution_status()
        for task in status.running_tasks:
            if task.duration > 240:  # Warn at 4 minutes
                print(f"⚠️  Long running task: {task.task_id}")
        time.sleep(30)
```

#### Resource Exhaustion

**Symptoms:**
```
❌ Resource exhaustion: CPU usage 95%, Memory usage 90%
❌ Cannot start new tasks: Resource limits exceeded
```

**Solutions:**

1. **Adjust resource limits:**
```python
resource_limits = ResourceLimits(
    max_cpu_percent=75,    # Reduce from 90%
    max_memory_percent=70, # Reduce from 85%
    max_concurrent_tasks=4 # Reduce from 8
)
```

2. **Implement resource monitoring:**
```python
def check_resources():
    import psutil
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    
    if cpu > 80 or memory > 80:
        print(f"⚠️  High resource usage: CPU {cpu}%, Memory {memory}%")
        return False
    return True
```

3. **Use adaptive execution strategy:**
```python
execution_engine = ParallelExecutionEngine(
    execution_strategy=ExecutionStrategy.ADAPTIVE,
    resource_limits=resource_limits
)
```

#### Command Execution Failures

**Symptoms:**
```
❌ Task 'shell-task' failed: Command returned non-zero exit code 1
❌ stderr: /bin/sh: command not found
```

**Solutions:**

1. **Check command syntax and availability:**
```python
import shutil

def validate_command(command):
    # Extract command name
    cmd_name = command.split()[0]
    if not shutil.which(cmd_name):
        print(f"❌ Command not found: {cmd_name}")
        return False
    return True

# Validate before creating task
if validate_command("python3 script.py"):
    task = TaskDefinition(command="python3 script.py", ...)
```

2. **Add error handling to commands:**
```python
TaskDefinition(
    command="python3 script.py || echo 'Script failed but continuing'",
    # or use explicit error handling
    command="set -e; python3 script.py; echo 'Success'"
)
```

3. **Use absolute paths:**
```python
TaskDefinition(
    command="/usr/bin/python3 /full/path/to/script.py",
    # instead of
    command="python3 script.py"
)
```

### 3. LLM Integration Issues

#### LLM Provider Not Available

**Symptoms:**
```
❌ No LLM providers available for task execution
❌ LLM selection failed: cursor CLI not found
```

**Solutions:**

1. **Check LLM CLI installation:**
```bash
# Check available LLM CLIs
which cursor
which claude
which kiro

# Install missing CLIs
# For Cursor: Follow official installation guide
# For Claude: pip install claude-cli
```

2. **Configure fallback providers:**
```python
llm_manager = LLMOrchestrationManager(
    preferred_providers=["cursor", "claude", "kiro"],
    fallback_to_simulation=True
)
```

3. **Test LLM connectivity:**
```python
def test_llm_providers():
    manager = LLMOrchestrationManager()
    for provider, config in manager.available_llms.items():
        try:
            # Test basic connectivity
            result = manager.test_provider(provider)
            print(f"✅ {provider}: {result.status}")
        except Exception as e:
            print(f"❌ {provider}: {e}")
```

#### Cost Budget Exceeded

**Symptoms:**
```
❌ Cost budget exceeded: $15.50 > $10.00 limit
❌ Cannot execute LLM task: Budget exhausted
```

**Solutions:**

1. **Increase budget or optimize usage:**
```python
llm_manager = LLMOrchestrationManager(
    cost_budget=25.0,  # Increase budget
    cost_optimization=True  # Enable optimization
)
```

2. **Use cost-effective providers:**
```python
# Prefer subscription-based providers
llm_manager = LLMOrchestrationManager(
    preferred_providers=["cursor", "kiro"],  # Subscription models
    avoid_providers=["claude"]  # Pay-per-token
)
```

3. **Implement cost monitoring:**
```python
def monitor_costs():
    cost_summary = llm_manager.get_cost_summary()
    if cost_summary.budget_remaining < 2.0:
        print(f"⚠️  Low budget: ${cost_summary.budget_remaining} remaining")
```

### 4. Performance Issues

#### Slow Execution

**Symptoms:**
- Tasks taking much longer than expected
- Low CPU/memory utilization during execution
- Sequential execution when parallel expected

**Solutions:**

1. **Check execution strategy:**
```python
# Ensure parallel execution is enabled
execution_engine = ParallelExecutionEngine(
    max_workers=8,
    execution_strategy=ExecutionStrategy.PARALLEL  # Not SEQUENTIAL
)
```

2. **Optimize task dependencies:**
```python
# Minimize unnecessary dependencies
# Before (over-constrained)
TaskDefinition(id="task-c", dependencies=["task-a", "task-b"])

# After (only necessary dependencies)
TaskDefinition(id="task-c", dependencies=["task-b"])  # Only if task-c truly needs task-b
```

3. **Profile task execution:**
```python
def profile_execution():
    start_time = time.time()
    result = orchestrator.execute_dag(tasks)
    
    for task_result in result.completed_tasks:
        efficiency = task_result.duration / (time.time() - start_time)
        if efficiency < 0.1:  # Less than 10% of total time
            print(f"⚠️  Inefficient task: {task_result.task_id}")
```

#### Memory Leaks

**Symptoms:**
- Memory usage continuously increasing
- System becomes unresponsive over time
- Out of memory errors

**Solutions:**

1. **Monitor memory usage:**
```python
import psutil
import gc

def monitor_memory():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")
    
    if memory_mb > 1000:  # Alert at 1GB
        print("⚠️  High memory usage detected")
        gc.collect()  # Force garbage collection
```

2. **Clean up task results:**
```python
# Limit result retention
execution_engine = ParallelExecutionEngine(
    max_result_history=100,  # Keep only last 100 results
    cleanup_interval=60      # Cleanup every 60 seconds
)
```

3. **Use streaming for large data:**
```python
# Instead of loading all data in memory
TaskDefinition(
    command="process_large_file.py --stream --chunk-size 1000",
    # instead of
    command="process_large_file.py --load-all"
)
```

### 5. Integration Issues

#### Redis Connection Failures

**Symptoms:**
```
❌ Redis connection failed: Connection refused
❌ Cannot connect to Redis at localhost:6379
```

**Solutions:**

1. **Check Redis server status:**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
redis-server --daemonize yes

# Check Redis logs
tail -f /var/log/redis/redis-server.log
```

2. **Configure Redis connection:**
```python
# Use custom Redis configuration
orchestrator = DAGOrchestrator(
    redis_url="redis://192.168.1.119:6379",
    redis_password="your_password",
    redis_timeout=30
)
```

3. **Implement Redis health checks:**
```python
def check_redis_health():
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        return True
    except Exception as e:
        print(f"❌ Redis health check failed: {e}")
        return False
```

#### Beast Mode Integration Issues

**Symptoms:**
```
❌ ReflectiveModule import failed
❌ Health endpoints not responding
❌ Metrics not being collected
```

**Solutions:**

1. **Check Beast Mode installation:**
```python
try:
    from rm_ddd.core.unified_reflective_module import ReflectiveModule
    print("✅ Beast Mode available")
except ImportError as e:
    print(f"❌ Beast Mode not available: {e}")
```

2. **Verify health endpoints:**
```bash
# Test health endpoints
curl http://localhost:8888/health
curl http://localhost:8888/ready
curl http://localhost:8888/metrics
```

3. **Enable observability:**
```python
class CustomDAGComponent(ReflectiveModule):
    def __init__(self):
        super().__init__()
        self.enable_health_endpoints()
        self.enable_metrics_collection()
```

## Debugging Tools

### 1. Execution Logging

Enable detailed logging for debugging:

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dag_execution.log'),
        logging.StreamHandler()
    ]
)

# Enable DAG orchestration logging
dag_logger = logging.getLogger('dag_orchestration')
dag_logger.setLevel(logging.DEBUG)
```

### 2. Task Execution Tracing

Trace individual task execution:

```python
def trace_task_execution(task_result):
    print(f"Task: {task_result.task_id}")
    print(f"  Status: {task_result.status}")
    print(f"  Duration: {task_result.duration:.2f}s")
    print(f"  Start: {task_result.start_time}")
    print(f"  End: {task_result.end_time}")
    print(f"  Output: {task_result.output[:100]}...")
    if task_result.error:
        print(f"  Error: {task_result.error}")
```

### 3. DAG Visualization

Generate visual representations of your DAG:

```python
def visualize_dag_structure(tasks):
    """Create a visual representation of the DAG."""
    import matplotlib.pyplot as plt
    import networkx as nx
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes and edges
    for task in tasks:
        G.add_node(task.id, label=task.name)
        for dep in task.dependencies:
            G.add_edge(dep, task.id)
    
    # Draw graph
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=1500, font_size=8, arrows=True)
    plt.title("DAG Structure")
    plt.savefig("dag_structure.png")
    plt.show()
```

### 4. Performance Profiling

Profile execution performance:

```python
import cProfile
import pstats

def profile_dag_execution():
    """Profile DAG execution performance."""
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Execute DAG
    result = orchestrator.execute_dag(tasks)
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

## Prevention Strategies

### 1. Validation Before Execution

Always validate before executing:

```python
def safe_dag_execution(tasks):
    """Safely execute DAG with comprehensive validation."""
    
    # 1. Validate DAG structure
    validation = orchestrator.validate_dag(tasks)
    if not validation.is_valid:
        raise ValueError(f"DAG validation failed: {validation.errors}")
    
    # 2. Check system resources
    if not check_resources():
        raise RuntimeError("Insufficient system resources")
    
    # 3. Validate task commands
    for task in tasks:
        if not validate_command(task.command):
            raise ValueError(f"Invalid command in task {task.id}")
    
    # 4. Execute with monitoring
    return orchestrator.execute_dag(tasks)
```

### 2. Comprehensive Testing

Test DAGs before production:

```python
def test_dag_execution():
    """Test DAG execution with mock tasks."""
    
    # Create test tasks with short durations
    test_tasks = [
        TaskDefinition(
            id=task.id,
            name=f"Test {task.name}",
            command="echo 'Test execution' && sleep 0.1",
            dependencies=task.dependencies,
            timeout=10
        )
        for task in tasks
    ]
    
    # Execute test DAG
    result = orchestrator.execute_dag(test_tasks)
    assert result.status == "COMPLETED", "Test DAG execution failed"
```

### 3. Monitoring and Alerting

Implement comprehensive monitoring:

```python
def setup_monitoring():
    """Setup monitoring and alerting for DAG execution."""
    
    # Resource monitoring
    def resource_alert():
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        
        if cpu > 90 or memory > 90:
            send_alert(f"High resource usage: CPU {cpu}%, Memory {memory}%")
    
    # Execution monitoring
    def execution_alert(result):
        if result.status == "FAILED":
            send_alert(f"DAG execution failed: {len(result.failed_tasks)} tasks failed")
        
        if result.execution_time > expected_time * 1.5:
            send_alert(f"DAG execution slow: {result.execution_time}s > {expected_time * 1.5}s")
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs** in `logs/dag-orchestration/` for detailed error information
2. **Run the diagnostic script**: `python scripts/diagnose_dag_orchestration.py`
3. **Verify prerequisites**: `bash scripts/check_dag_orchestrated_parallel_execution_prereqs.sh`
4. **Review the API documentation** for correct usage patterns
5. **Check system resources** and adjust limits accordingly
6. **Test with simple examples** before complex workflows

## Common Error Patterns

### Pattern: "It worked yesterday"

**Likely causes:**
- System resources changed (less memory/CPU available)
- Dependencies updated (different versions)
- Configuration files modified
- Network connectivity issues

**Solution approach:**
1. Compare current system state with previous working state
2. Check for recent changes in dependencies or configuration
3. Test with minimal example to isolate the issue

### Pattern: "Works locally but fails in production"

**Likely causes:**
- Different resource limits in production
- Missing dependencies in production environment
- Different network configuration
- Permission issues

**Solution approach:**
1. Compare local and production environments
2. Test production configuration locally
3. Validate all dependencies are available in production

### Pattern: "Random failures"

**Likely causes:**
- Race conditions in parallel execution
- Resource contention
- Network timeouts
- Flaky external dependencies

**Solution approach:**
1. Add retry logic to tasks
2. Implement proper synchronization
3. Add timeout handling
4. Monitor resource usage patterns

This troubleshooting guide covers the most common issues you'll encounter with the DAG orchestration system and provides practical solutions for each.