# Beast Mode Framework: Troubleshooting Guide

## Quick Diagnostic Commands

Before diving deep, run these commands to get a quick system overview:

```bash
# Check Beast Mode system health
make beast-mode-health

# Check Redis connectivity
redis-cli ping

# Verify Python environment
python -c "import beast_mode; print('✅ Beast Mode available')"

# Check system resources
make beast-mode-status
```

## Common Issues and Solutions

### 1. Installation and Setup Issues

#### Problem: ImportError when importing beast_mode modules

**Symptoms:**
```python
ImportError: No module named 'beast_mode'
ModuleNotFoundError: No module named 'beast_mode.core'
```

**Solutions:**

1. **Verify Virtual Environment:**
   ```bash
   # Check if you're in the right environment
   which python
   pip list | grep beast

   # If not activated:
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Reinstall Dependencies:**
   ```bash
   make clean
   make venv
   make install
   ```

3. **Check Python Path:**
   ```python
   import sys
   print(sys.path)
   # Ensure your project directory is included
   ```

#### Problem: Redis connection refused

**Symptoms:**
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solutions:**

1. **Start Redis Server:**
   ```bash
   # Using Docker (recommended)
   docker run -d --name redis-beast -p 6379:6379 redis:latest

   # Or system service
   sudo systemctl start redis-server  # Linux
   brew services start redis          # macOS
   ```

2. **Check Redis Configuration:**
   ```bash
   # Test connection
   redis-cli ping
   # Should return: PONG

   # Check Redis configuration
   redis-cli config get "*"
   ```

3. **Use Alternative Redis Host:**
   ```python
   config = {
       "redis": {
           "host": "your-redis-host.com",  # Instead of localhost
           "port": 6379,
           "password": "your-password"     # If required
       }
   }
   ```

### 2. Task Queue Issues

#### Problem: Tasks stuck in PENDING status

**Symptoms:**
- Tasks never change from PENDING to RUNNING
- No task execution logs
- Queue appears frozen

**Diagnostic Steps:**
```python
# Check task queue status
from beast_mode.task_queue import TaskQueueManager

async def diagnose_queue():
    queue = TaskQueueManager(config)
    await queue.initialize()

    # Get queue statistics
    stats = await queue.get_queue_stats()
    print(f"Pending tasks: {stats['pending']}")
    print(f"Running tasks: {stats['running']}")
    print(f"Workers active: {stats['active_workers']}")

    # Check specific task
    task_status = await queue.get_task_status("your-task-id")
    print(f"Task status: {task_status}")
```

**Solutions:**

1. **Start Task Workers:**
   ```bash
   # Start worker processes
   python -m beast_mode.task_queue.worker --workers=4

   # Or using make command
   make start-workers
   ```

2. **Check Task Handler Registration:**
   ```python
   # Ensure handlers are registered before submitting tasks
   from beast_mode.task_queue import TaskRegistry

   @TaskRegistry.register("my_task_type")
   class MyTaskHandler:
       async def execute(self, task):
           # Task execution logic
           pass

   # Verify registration
   print(TaskRegistry.list_registered_handlers())
   ```

3. **Verify Redis Memory:**
   ```bash
   # Check Redis memory usage
   redis-cli info memory

   # Clear Redis if needed (CAUTION: This deletes all data)
   redis-cli flushall
   ```

#### Problem: Task execution timeout

**Symptoms:**
- Tasks fail with timeout errors
- Long-running tasks never complete
- Escalation system triggers unexpectedly

**Solutions:**

1. **Adjust Timeout Configuration:**
   ```python
   config = {
       "escalation": {
           "levels": 4,
           "base_timeout": 300,  # Increase from 30 to 300 seconds
           "timeout_multiplier": 2.0,
           "max_timeout": 1800   # 30 minutes maximum
       }
   }
   ```

2. **Implement Progress Reporting:**
   ```python
   class LongRunningTaskHandler:
       async def execute(self, task):
           total_steps = 10
           for step in range(total_steps):
               # Do work for this step
               await self.do_step_work(step)

               # Report progress to prevent timeout
               progress = (step + 1) / total_steps * 100
               await task.update_progress(progress)

               # Check if cancellation was requested
               if await task.is_cancelled():
                   return {"status": "cancelled", "completed_steps": step}

           return {"status": "completed", "completed_steps": total_steps}
   ```

3. **Break Down Large Tasks:**
   ```python
   # Instead of one large task, create a pipeline
   async def process_large_dataset(data_url):
       # Split into smaller chunks
       chunks = await create_data_chunks(data_url)

       task_ids = []
       for chunk in chunks:
           task_id = await submit_task({
               "task_type": "process_chunk",
               "chunk_data": chunk
           })
           task_ids.append(task_id)

       # Wait for all chunks to complete
       results = await wait_for_tasks(task_ids)
       return combine_results(results)
   ```

### 3. Performance Issues

#### Problem: Slow task processing

**Symptoms:**
- High task queue latency
- Tasks taking much longer than expected
- System resource exhaustion

**Diagnostic Tools:**
```python
# Enable performance profiling
from beast_mode.monitoring import PerformanceProfiler

profiler = PerformanceProfiler()

@profiler.profile("task_execution")
async def execute_task(task):
    # Your task code here
    result = await process_task(task)
    return result

# View profiling results
profiler.print_stats()
```

**Solutions:**

1. **Scale Worker Processes:**
   ```bash
   # Increase worker count
   python -m beast_mode.task_queue.worker --workers=8 --max-tasks-per-worker=100

   # Monitor worker performance
   make monitor-workers
   ```

2. **Optimize Database Operations:**
   ```python
   # Use connection pooling
   from beast_mode.persistence import DatabasePool

   db_pool = DatabasePool(
       min_connections=5,
       max_connections=20,
       connection_timeout=30
   )

   # Batch operations
   async def batch_process_tasks(tasks):
       async with db_pool.transaction() as conn:
           for task in tasks:
               await conn.execute("INSERT INTO results ...", task.result)
   ```

3. **Implement Caching:**
   ```python
   from beast_mode.caching import RedisCache

   cache = RedisCache(ttl=3600)  # 1 hour cache

   async def cached_expensive_operation(key, data):
       # Check cache first
       result = await cache.get(key)
       if result:
           return result

       # Perform expensive operation
       result = await expensive_computation(data)

       # Store in cache
       await cache.set(key, result)
       return result
   ```

#### Problem: Memory leaks in long-running processes

**Symptoms:**
- Memory usage continuously increases
- System becomes unresponsive over time
- Out-of-memory errors

**Diagnostic Commands:**
```bash
# Monitor memory usage
python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'CPU: {process.cpu_percent():.2f}%')
"

# Use memory profiler
pip install memory-profiler
python -m memory_profiler your_script.py
```

**Solutions:**

1. **Implement Proper Cleanup:**
   ```python
   class TaskHandler:
       def __init__(self):
           self.resources = []

       async def execute(self, task):
           try:
               # Acquire resources
               connection = await self.get_db_connection()
               self.resources.append(connection)

               # Do work
               result = await self.process_data(task, connection)
               return result

           finally:
               # Always cleanup
               await self.cleanup_resources()

       async def cleanup_resources(self):
           for resource in self.resources:
               if hasattr(resource, 'close'):
                   await resource.close()
           self.resources.clear()
   ```

2. **Use Context Managers:**
   ```python
   from contextlib import asynccontextmanager

   @asynccontextmanager
   async def managed_resources():
       resources = []
       try:
           # Acquire resources
           db_conn = await get_db_connection()
           redis_conn = await get_redis_connection()
           resources.extend([db_conn, redis_conn])

           yield {"db": db_conn, "redis": redis_conn}

       finally:
           # Cleanup guaranteed
           for resource in resources:
               await resource.close()

   # Usage
   async def execute_task(task):
       async with managed_resources() as resources:
           result = await process_with_resources(task, resources)
           return result
   ```

3. **Set Worker Recycling:**
   ```python
   # Configure worker lifecycle
   worker_config = {
       "max_tasks_per_worker": 1000,  # Recycle after 1000 tasks
       "max_memory_per_worker": "512MB",  # Recycle if memory exceeds limit
       "worker_timeout": 3600  # Recycle after 1 hour
   }
   ```

### 4. Concurrency and Race Condition Issues

#### Problem: Race conditions in task processing

**Symptoms:**
- Inconsistent task results
- Data corruption
- Duplicate processing

**Solutions:**

1. **Use Distributed Locks:**
   ```python
   from beast_mode.coordination import DistributedLock

   async def execute_critical_section(task):
       lock_key = f"task_lock_{task.resource_id}"

       async with DistributedLock(lock_key, timeout=30) as lock:
           if lock.acquired:
               # Critical section - only one worker can execute this
               result = await process_exclusive_resource(task)
               return result
           else:
               # Lock not acquired, handle appropriately
               return {"status": "skipped", "reason": "resource_locked"}
   ```

2. **Implement Idempotency:**
   ```python
   class IdempotentTaskHandler:
       async def execute(self, task):
           # Check if task was already processed
           result_key = f"result_{task.id}"
           existing_result = await self.cache.get(result_key)

           if existing_result:
               return existing_result

           # Process task
           result = await self.process_task(task)

           # Store result to prevent reprocessing
           await self.cache.set(result_key, result, ttl=86400)  # 24 hours

           return result
   ```

3. **Use Transaction-Safe Operations:**
   ```python
   async def transfer_data(source_id, target_id, amount):
       async with self.db_pool.transaction() as tx:
           try:
               # Atomic operations within transaction
               await tx.execute(
                   "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
                   amount, source_id
               )
               await tx.execute(
                   "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
                   amount, target_id
               )

               # Transaction commits automatically if no exceptions

           except Exception as e:
               # Transaction automatically rolls back
               raise TaskExecutionError(f"Transfer failed: {e}")
   ```

### 5. Configuration and Environment Issues

#### Problem: Configuration not loading correctly

**Symptoms:**
- Default values used instead of custom config
- Environment variables ignored
- Configuration validation errors

**Solutions:**

1. **Debug Configuration Loading:**
   ```python
   from beast_mode.config import ConfigManager

   # Enable configuration debugging
   config_manager = ConfigManager(debug=True)
   config = config_manager.load_config()

   # Print loaded configuration
   import json
   print(json.dumps(config, indent=2))

   # Check environment variables
   import os
   print("Environment variables:")
   for key, value in os.environ.items():
       if key.startswith('BEAST_MODE_'):
           print(f"  {key}={value}")
   ```

2. **Validate Configuration Schema:**
   ```python
   from beast_mode.config import ConfigValidator

   validator = ConfigValidator()
   validation_result = validator.validate(config)

   if not validation_result.is_valid:
       print("Configuration errors:")
       for error in validation_result.errors:
           print(f"  {error.field}: {error.message}")
   ```

3. **Use Configuration Files:**
   ```yaml
   # config.yaml
   redis:
     host: localhost
     port: 6379
     db: 0

   task_queue:
     max_workers: 8
     batch_size: 50

   logging:
     level: INFO
     file: beast_mode.log
   ```

   ```python
   # Load from file
   config = ConfigManager.from_file("config.yaml")
   ```

### 6. Monitoring and Debugging

#### Problem: Insufficient visibility into system behavior

**Solutions:**

1. **Enable Structured Logging:**
   ```python
   import structlog

   logger = structlog.get_logger("beast_mode.task_processor")

   async def execute_task(task):
       logger.info(
           "Task execution started",
           task_id=task.id,
           task_type=task.task_type,
           priority=task.priority
       )

       try:
           result = await self.process_task(task)
           logger.info(
               "Task execution completed",
               task_id=task.id,
               duration=result.get('duration'),
               status="success"
           )
           return result

       except Exception as e:
           logger.error(
               "Task execution failed",
               task_id=task.id,
               error=str(e),
               exc_info=True
           )
           raise
   ```

2. **Set up Health Monitoring:**
   ```python
   from beast_mode.monitoring import HealthMonitor

   monitor = HealthMonitor()

   # Add custom health checks
   @monitor.health_check("database")
   async def check_database():
       try:
           await db.execute("SELECT 1")
           return {"status": "healthy", "latency": 0.05}
       except Exception as e:
           return {"status": "unhealthy", "error": str(e)}

   # Get comprehensive health report
   health_report = await monitor.get_health_report()
   ```

3. **Implement Metrics Collection:**
   ```python
   from beast_mode.metrics import MetricsCollector

   metrics = MetricsCollector()

   # Custom metrics
   metrics.counter("tasks.processed").inc()
   metrics.histogram("task.duration").observe(duration)
   metrics.gauge("queue.size").set(queue_size)

   # Export metrics for Prometheus
   from beast_mode.metrics.exporters import PrometheusExporter
   exporter = PrometheusExporter(port=8080)
   exporter.start()
   ```

## Advanced Debugging Techniques

### 1. Task Execution Tracing

```python
from beast_mode.debugging import TaskTracer

tracer = TaskTracer()

@tracer.trace_execution
async def traced_task_handler(task):
    # Automatic tracing of execution path
    result = await complex_processing(task)
    return result

# View execution trace
trace_data = tracer.get_trace(task_id)
print(trace_data.to_json())
```

### 2. Redis Data Inspection

```bash
# Useful Redis commands for debugging

# List all Beast Mode keys
redis-cli keys "beast_mode:*"

# Inspect task data
redis-cli hgetall "beast_mode:task:your-task-id"

# Check queue contents
redis-cli lrange "beast_mode:queue:default" 0 -1

# Monitor Redis operations in real-time
redis-cli monitor
```

### 3. Network Connectivity Testing

```python
async def test_connectivity():
    """Test all external connections"""

    tests = [
        ("Redis", test_redis_connection),
        ("Database", test_database_connection),
        ("External API", test_api_connection),
    ]

    for name, test_func in tests:
        try:
            await test_func()
            print(f"✅ {name}: Connected")
        except Exception as e:
            print(f"❌ {name}: Failed - {e}")

async def test_redis_connection():
    import redis.asyncio as redis
    client = redis.Redis(host='localhost', port=6379)
    await client.ping()
    await client.close()
```

## Getting Help

### 1. Enable Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable Beast Mode debug logging
import beast_mode
beast_mode.set_debug_mode(True)
```

### 2. Collect Diagnostic Information
```bash
# Generate diagnostic report
make diagnostic-report

# This creates: diagnostic_report_TIMESTAMP.json
# Share this file when asking for help
```

### 3. Community Support
- **GitHub Issues**: [Report bugs and ask questions](https://github.com/your-org/kiro-ai-development-hackathon/issues)
- **Discord Community**: [Real-time help](https://discord.gg/beast-mode)
- **Stack Overflow**: Tag questions with `beast-mode-framework`

### 4. Professional Support
For production systems, consider professional support:
- Email: support@beast-mode.dev
- Priority support plans available
- Custom training and consulting

## Prevention Best Practices

1. **Always use try-catch blocks** in task handlers
2. **Implement health checks** for all critical components
3. **Monitor resource usage** continuously
4. **Use configuration management** for all environments
5. **Implement proper logging** from day one
6. **Test failure scenarios** regularly
7. **Keep dependencies updated** but test thoroughly
8. **Document your custom configurations** and extensions

---

*This troubleshooting guide is maintained by Documentation Agent Gamma and the Beast Mode community. Last updated: 2025-09-24*