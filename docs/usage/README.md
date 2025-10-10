# Beast Mode AI Development Framework - Usage Guide

## Overview

This guide provides comprehensive usage instructions for the Beast Mode AI Development Framework, covering everything from basic setup to advanced orchestration patterns.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd beast-mode-framework

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your actual credentials
```

### 2. Basic Configuration

Create your `.env` file with required credentials:

```bash
# Redis Configuration (Required)
REDIS_PASSWORD=your_redis_password_here
REDIS_HOST=localhost
REDIS_PORT=6379

# AI API Keys (At least one required)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Application Settings
DEBUG=false
ENVIRONMENT=development
```

### 3. First Example

```python
import asyncio
from src.constellation_orchestrator.core.orchestrator import ConstellationOrchestrator
from src.constellation_orchestrator.models.task_definition import TaskDefinition

async def hello_world_example():
    # Initialize orchestrator
    orchestrator = ConstellationOrchestrator()
    
    if not await orchestrator.initialize():
        print("Failed to initialize orchestrator")
        return
    
    # Define a simple task
    tasks = [
        TaskDefinition(
            task_id="hello_world",
            name="Hello World Task",
            description="A simple greeting task",
            dependencies=[],
            prompt_template="Say hello to the world",
            expected_output="Hello, World!"
        )
    ]
    
    # Load and execute
    await orchestrator.load_tasks(tasks)
    execution_id = await orchestrator.start_execution("hello_world_demo")
    
    if execution_id:
        print(f"Started execution: {execution_id}")
        
        # Monitor execution
        while True:
            state = await orchestrator.get_execution_state(execution_id)
            if not state:
                break
            
            print(f"Status: {state.status.value}")
            
            if state.status.value in ['completed', 'failed']:
                break
            
            await asyncio.sleep(2)
    
    await orchestrator.shutdown()

# Run the example
asyncio.run(hello_world_example())
```

## Core Concepts

### ReflectiveModule Pattern

All framework components extend the `ReflectiveModule` base class, providing:

- **Health Monitoring**: Automatic health status reporting
- **Error Handling**: Systematic error management with graceful degradation
- **Observability**: Built-in metrics and logging
- **Capability Management**: Dynamic capability reporting

```python
from src.beast_mode.core import ReflectiveModule

# All components implement these methods:
health = await component.get_health_status()
capabilities = component.get_capabilities()
module_info = component.get_module_info()

# Automatic error handling
try:
    result = await component.perform_operation()
except Exception as e:
    degradation = await component.graceful_degradation(e)
    # Component continues with reduced functionality
```

### DAG Orchestration

The framework uses Directed Acyclic Graphs (DAGs) for task orchestration:

```python
# Tasks with dependencies
tasks = [
    TaskDefinition(
        task_id="setup",
        name="System Setup",
        dependencies=[],  # No dependencies
        prompt_template="Initialize system"
    ),
    TaskDefinition(
        task_id="process",
        name="Data Processing",
        dependencies=["setup"],  # Depends on setup
        prompt_template="Process data"
    ),
    TaskDefinition(
        task_id="finalize",
        name="Finalization",
        dependencies=["process"],  # Depends on process
        prompt_template="Finalize results"
    )
]
```

### AI Memory Palace

Intelligent context management for large-scale AI interactions:

```python
from src.ai_memory_palace.engine.context_engine import ContextEngine

engine = ContextEngine()

# Summarize large contexts
summary = engine.summarize_context(large_context)

# Filter for relevance
relevant_context = engine.filter_relevant_context(context, "database migration")

# Compress old data
compressed_context = engine.compress_old_data(context, threshold_mb=10)
```

## Common Usage Patterns

### 1. Simple Task Execution

```python
async def simple_task_execution():
    orchestrator = ConstellationOrchestrator()
    await orchestrator.initialize()
    
    # Single task
    task = TaskDefinition(
        task_id="analyze_data",
        name="Data Analysis",
        description="Analyze the provided dataset",
        dependencies=[],
        prompt_template="Analyze this data: {data}",
        expected_output="Analysis complete with insights"
    )
    
    await orchestrator.load_tasks([task])
    execution_id = await orchestrator.start_execution()
    
    # Wait for completion
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if state.status.value in ['completed', 'failed']:
            break
        await asyncio.sleep(1)
    
    await orchestrator.shutdown()
```

### 2. Multi-Stage Pipeline

```python
async def multi_stage_pipeline():
    orchestrator = ConstellationOrchestrator()
    await orchestrator.initialize()
    
    # Define pipeline stages
    stages = [
        TaskDefinition(
            task_id="data_ingestion",
            name="Data Ingestion",
            dependencies=[],
            prompt_template="Ingest data from source: {source}",
            timeout_seconds=600
        ),
        TaskDefinition(
            task_id="data_validation",
            name="Data Validation",
            dependencies=["data_ingestion"],
            prompt_template="Validate ingested data for quality",
            timeout_seconds=300
        ),
        TaskDefinition(
            task_id="data_transformation",
            name="Data Transformation",
            dependencies=["data_validation"],
            prompt_template="Transform data according to schema",
            timeout_seconds=900
        ),
        TaskDefinition(
            task_id="data_analysis",
            name="Data Analysis",
            dependencies=["data_transformation"],
            prompt_template="Perform statistical analysis on transformed data",
            timeout_seconds=1200
        ),
        TaskDefinition(
            task_id="report_generation",
            name="Report Generation",
            dependencies=["data_analysis"],
            prompt_template="Generate comprehensive analysis report",
            timeout_seconds=600
        )
    ]
    
    await orchestrator.load_tasks(stages)
    execution_id = await orchestrator.start_execution("data_pipeline")
    
    # Monitor with progress reporting
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if not state:
            break
        
        progress = (state.completed_tasks / state.total_tasks) * 100
        print(f"Pipeline progress: {progress:.1f}% ({state.completed_tasks}/{state.total_tasks})")
        
        if state.status.value in ['completed', 'failed']:
            print(f"Pipeline {state.status.value}")
            break
        
        await asyncio.sleep(5)
    
    await orchestrator.shutdown()
```

### 3. Parallel Task Execution

```python
async def parallel_task_execution():
    orchestrator = ConstellationOrchestrator()
    await orchestrator.initialize()
    
    # Tasks that can run in parallel
    parallel_tasks = [
        TaskDefinition(
            task_id="process_batch_1",
            name="Process Batch 1",
            dependencies=[],
            prompt_template="Process data batch 1: {batch_1_data}"
        ),
        TaskDefinition(
            task_id="process_batch_2",
            name="Process Batch 2",
            dependencies=[],
            prompt_template="Process data batch 2: {batch_2_data}"
        ),
        TaskDefinition(
            task_id="process_batch_3",
            name="Process Batch 3",
            dependencies=[],
            prompt_template="Process data batch 3: {batch_3_data}"
        ),
        TaskDefinition(
            task_id="merge_results",
            name="Merge Results",
            dependencies=["process_batch_1", "process_batch_2", "process_batch_3"],
            prompt_template="Merge results from all batches"
        )
    ]
    
    await orchestrator.load_tasks(parallel_tasks)
    execution_id = await orchestrator.start_execution("parallel_processing")
    
    # Monitor parallel execution
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if not state:
            break
        
        print(f"Running: {state.running_tasks}, Completed: {state.completed_tasks}")
        
        if state.status.value in ['completed', 'failed']:
            break
        
        await asyncio.sleep(3)
    
    await orchestrator.shutdown()
```

### 4. Context-Aware Processing

```python
async def context_aware_processing():
    from src.ai_memory_palace.engine.context_engine import ContextEngine
    
    # Initialize components
    orchestrator = ConstellationOrchestrator()
    context_engine = ContextEngine()
    
    await orchestrator.initialize()
    
    # Load and process context
    session_context = load_session_context()  # Your context loading logic
    
    # Filter context for current task
    relevant_context = context_engine.filter_relevant_context(
        session_context, 
        "API integration testing"
    )
    
    # Create context-aware tasks
    tasks = [
        TaskDefinition(
            task_id="analyze_context",
            name="Analyze Context",
            dependencies=[],
            prompt_template="Analyze the context: {context}",
            context_requirements=["api_integration", "testing"]
        ),
        TaskDefinition(
            task_id="generate_tests",
            name="Generate Tests",
            dependencies=["analyze_context"],
            prompt_template="Generate API tests based on context analysis"
        )
    ]
    
    await orchestrator.load_tasks(tasks)
    execution_id = await orchestrator.start_execution("context_aware_testing")
    
    # Monitor execution
    await monitor_execution(orchestrator, execution_id)
    await orchestrator.shutdown()

async def monitor_execution(orchestrator, execution_id):
    """Helper function to monitor execution."""
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if not state:
            break
        
        if state.status.value in ['completed', 'failed']:
            print(f"Execution {state.status.value}")
            if state.error_message:
                print(f"Error: {state.error_message}")
            break
        
        await asyncio.sleep(2)
```

### 5. Execution Tracking Integration

```python
async def execution_with_tracking():
    from src.execution_tracking.redis_execution_tracker import (
        initialize_execution_tracker,
        start_tracking_execution,
        update_execution_status,
        checkin_execution,
        ExecutionStatus
    )
    
    # Initialize tracking
    await initialize_execution_tracker()
    
    # Start tracking
    tracking_id = await start_tracking_execution(
        "comprehensive_pipeline",
        total_tasks=5,
        estimated_hours=2.0
    )
    
    # Initialize orchestrator
    orchestrator = ConstellationOrchestrator()
    await orchestrator.initialize()
    
    try:
        # Update tracking status
        await update_execution_status(tracking_id, ExecutionStatus.RUNNING)
        
        # Load and execute tasks
        tasks = create_comprehensive_tasks()  # Your task creation logic
        await orchestrator.load_tasks(tasks)
        execution_id = await orchestrator.start_execution()
        
        # Monitor both systems
        while True:
            # Get orchestrator state
            orch_state = await orchestrator.get_execution_state(execution_id)
            if not orch_state:
                break
            
            # Update tracking system
            progress = (orch_state.completed_tasks / orch_state.total_tasks) * 100
            await checkin_execution(
                tracking_id,
                phase=orch_state.current_phase,
                progress_percentage=progress,
                message=f"Orchestrator status: {orch_state.status.value}"
            )
            
            if orch_state.status.value == 'completed':
                await update_execution_status(tracking_id, ExecutionStatus.COMPLETED)
                break
            elif orch_state.status.value == 'failed':
                await update_execution_status(
                    tracking_id, 
                    ExecutionStatus.FAILED,
                    error_message=orch_state.error_message
                )
                break
            
            await asyncio.sleep(10)
    
    except Exception as e:
        await update_execution_status(
            tracking_id,
            ExecutionStatus.FAILED,
            error_message=str(e)
        )
        raise
    
    finally:
        await orchestrator.shutdown()
```

## Configuration Management

### Environment Variables

All configuration is managed through environment variables for security:

```bash
# Required Configuration
REDIS_PASSWORD=your_secure_redis_password
REDIS_HOST=localhost
REDIS_PORT=6379

# AI API Keys (at least one required)
OPENAI_API_KEY=sk-your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional Configuration
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_CONCURRENT_TASKS=10
CONTEXT_CACHE_SIZE_MB=100
EXECUTION_TIMEOUT_SECONDS=3600
```

### Configuration Classes

Use structured configuration for complex setups:

```python
from src.constellation_orchestrator.core.config import ConstellationConfig

# Custom configuration
config = ConstellationConfig(
    max_concurrent_tasks=5,
    task_timeout_seconds=1800,
    retry_attempts=3,
    agent_pool_size=3,
    health_check_interval_seconds=30
)

orchestrator = ConstellationOrchestrator(config)
```

### Secure Credential Management

```python
from src.security.secure_credentials import get_secure_credentials

# Get secure credentials
creds = get_secure_credentials()

# Access configuration
redis_config = creds.get_redis_config()
api_keys = creds.get_api_keys()
db_config = creds.get_database_config()

# Use in components
redis_client = redis.Redis(
    host=redis_config['host'],
    port=redis_config['port'],
    password=redis_config['password']
)
```

## Error Handling and Recovery

### Graceful Degradation

All components implement graceful degradation:

```python
async def robust_execution():
    orchestrator = ConstellationOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Your execution logic
        tasks = create_tasks()
        await orchestrator.load_tasks(tasks)
        execution_id = await orchestrator.start_execution()
        
        await monitor_execution(orchestrator, execution_id)
        
    except Exception as e:
        print(f"Error occurred: {e}")
        
        # Trigger graceful degradation
        degradation = await orchestrator.graceful_degradation(e)
        
        if degradation.success:
            print("Graceful degradation successful")
            print(f"Remaining capabilities: {degradation.remaining_capabilities}")
            
            # Continue with reduced functionality
            await continue_with_reduced_functionality(orchestrator, degradation)
        else:
            print("Graceful degradation failed")
            raise
    
    finally:
        await orchestrator.shutdown()
```

### Health Monitoring

```python
async def health_monitoring_example():
    orchestrator = ConstellationOrchestrator()
    await orchestrator.initialize()
    
    # Regular health checks
    while True:
        health = await orchestrator.health_check()
        
        if health.get('components_healthy', False):
            print("All components healthy")
        else:
            print("Some components unhealthy")
            
            # Get detailed health status
            detailed_health = await orchestrator.get_health_status()
            print(f"Health score: {detailed_health.health_score}")
            print(f"Issues: {detailed_health.issues}")
            
            # Take corrective action if needed
            if detailed_health.health_score < 0.5:
                print("Critical health issues detected")
                # Implement recovery logic
        
        await asyncio.sleep(30)  # Check every 30 seconds
```

## Performance Optimization

### Memory Management

```python
# Configure memory limits
config = ConstellationConfig(
    max_concurrent_tasks=5,  # Limit concurrent tasks
    task_timeout_seconds=1800,  # Prevent runaway tasks
)

# Use context compression
from src.ai_memory_palace.engine.context_engine import ContextEngine

engine = ContextEngine()
compressed_context = engine.compress_old_data(large_context, threshold_mb=10)
```

### Concurrency Control

```python
# Control concurrency at orchestrator level
config = ConstellationConfig(
    max_concurrent_tasks=3,  # Limit to 3 concurrent tasks
    agent_pool_size=5,       # Pool of 5 agents
    agent_timeout_seconds=300  # 5-minute agent timeout
)

# Control concurrency at task level
task = TaskDefinition(
    task_id="resource_intensive_task",
    name="Resource Intensive Task",
    dependencies=[],
    prompt_template="Process large dataset",
    timeout_seconds=3600,  # 1-hour timeout
    agent_requirements={
        'min_memory_mb': 1024,  # Require 1GB memory
        'capabilities': ['large_context_processing']
    }
)
```

### Monitoring and Metrics

```python
async def performance_monitoring():
    orchestrator = ConstellationOrchestrator()
    await orchestrator.initialize()
    
    # Start execution with performance tracking
    start_time = time.time()
    execution_id = await orchestrator.start_execution("performance_test")
    
    # Monitor performance metrics
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if not state:
            break
        
        # Calculate performance metrics
        elapsed_time = time.time() - start_time
        tasks_per_second = state.completed_tasks / elapsed_time if elapsed_time > 0 else 0
        
        print(f"Performance: {tasks_per_second:.2f} tasks/second")
        print(f"Memory usage: {get_memory_usage():.1f} MB")
        
        if state.status.value in ['completed', 'failed']:
            total_time = time.time() - start_time
            print(f"Total execution time: {total_time:.1f} seconds")
            break
        
        await asyncio.sleep(5)
    
    await orchestrator.shutdown()

def get_memory_usage():
    """Get current memory usage in MB."""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)
```

## Best Practices

### 1. Always Initialize Components

```python
# ✅ CORRECT: Always check initialization
orchestrator = ConstellationOrchestrator()
if not await orchestrator.initialize():
    raise RuntimeError("Failed to initialize orchestrator")

# ❌ WRONG: Don't assume initialization succeeds
orchestrator = ConstellationOrchestrator()
await orchestrator.initialize()  # No error checking
```

### 2. Use Environment Variables for Configuration

```python
# ✅ CORRECT: Use environment variables
redis_password = os.getenv('REDIS_PASSWORD')
if not redis_password:
    raise ValueError("REDIS_PASSWORD environment variable required")

# ❌ WRONG: Never hardcode credentials
redis_password = "hardcoded_password"  # SECURITY VIOLATION
```

### 3. Implement Proper Error Handling

```python
# ✅ CORRECT: Comprehensive error handling
try:
    result = await component.operation()
except Exception as e:
    degradation = await component.graceful_degradation(e)
    if degradation.success:
        # Continue with reduced functionality
        result = await component.fallback_operation()
    else:
        # Handle complete failure
        raise

# ❌ WRONG: Ignore errors
result = await component.operation()  # No error handling
```

### 4. Monitor Component Health

```python
# ✅ CORRECT: Regular health monitoring
health = await component.get_health_status()
if health.status != ModuleStatus.HEALTHY:
    print(f"Component issues: {health.issues}")
    # Take corrective action

# ❌ WRONG: Assume components are always healthy
# No health checking
```

### 5. Clean Up Resources

```python
# ✅ CORRECT: Always clean up
try:
    await orchestrator.initialize()
    # Your logic here
finally:
    await orchestrator.shutdown()

# ❌ WRONG: Forget cleanup
await orchestrator.initialize()
# Your logic here
# No cleanup - resources leak
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check Redis is running
   redis-cli ping
   
   # Verify credentials
   echo $REDIS_PASSWORD
   ```

2. **Task Execution Timeout**
   ```python
   # Increase timeout for long-running tasks
   task = TaskDefinition(
       task_id="long_task",
       timeout_seconds=3600,  # 1 hour
       # ... other parameters
   )
   ```

3. **Memory Issues with Large Contexts**
   ```python
   # Use context compression
   engine = ContextEngine()
   compressed = engine.compress_old_data(context, threshold_mb=10)
   ```

4. **Component Health Issues**
   ```python
   # Check component health
   health = await component.get_health_status()
   print(f"Issues: {health.issues}")
   
   # Trigger graceful degradation if needed
   if health.health_score < 0.5:
       degradation = await component.graceful_degradation()
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Components will provide detailed debug information
```

---

**Next**: [Advanced Patterns](./advanced-patterns.md) | **Up**: [Usage Guide](./)