# Constellation Orchestrator

A sophisticated DAG-based execution system designed to manage the parallel execution of 90+ AI prompts with comprehensive dependency management, multi-agent coordination, and systematic observability.

## Overview

The Constellation Orchestrator transforms complex prompt workflows into a systematic, observable, and resumable process that can handle large-scale AI orchestration scenarios. It provides:

- **DAG-based dependency management** with cycle detection and topological sorting
- **Multi-agent execution** with dynamic scaling and load balancing
- **Comprehensive state persistence** with Redis-based recovery
- **Beast Mode framework integration** for systematic observability
- **Performance monitoring** and optimization recommendations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Constellation Orchestrator                  │
├─────────────────┬─────────────────┬─────────────────────────┤
│   DAG Manager   │ Execution Mgr   │    Status Manager       │
│                 │                 │                         │
│ • Task loading  │ • Agent pool    │ • State persistence     │
│ • Validation    │ • Parallel exec │ • Recovery support      │
│ • Ordering      │ • Retry logic   │ • Progress tracking     │
└─────────────────┴─────────────────┴─────────────────────────┘
         │                 │                     │
         ▼                 ▼                     ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Graph Algorithms│ │  Claude Agents  │ │  Redis Store    │
│                 │ │                 │ │                 │
│ • Cycle detect  │ │ • CLI wrapper   │ │ • Execution     │
│ • Topo sort     │ │ • Health check  │ │   state         │
│ • Ready tasks   │ │ • Performance   │ │ • Task results  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Key Features

### 1. DAG Management
- **Dependency validation**: Automatic cycle detection and prevention
- **Topological sorting**: Optimal execution order calculation
- **Ready task identification**: Dynamic task readiness based on dependencies
- **Execution batching**: Parallel execution groups for maximum efficiency

### 2. Agent Management
- **Dynamic scaling**: Automatic agent pool scaling based on demand
- **Health monitoring**: Continuous agent health checks and recovery
- **Load balancing**: Intelligent task assignment to available agents
- **Performance tracking**: Comprehensive agent performance metrics

### 3. Execution Management
- **Parallel processing**: Concurrent task execution with configurable limits
- **Retry logic**: Exponential backoff retry with agent reassignment
- **Error handling**: Comprehensive error classification and recovery
- **Resource management**: Memory and CPU optimization

### 4. State Management
- **Persistent state**: Redis-based execution state persistence
- **Recovery support**: Resume interrupted executions from checkpoints
- **Progress tracking**: Real-time execution progress and metrics
- **Audit trails**: Complete execution history and event logging

### 5. Observability
- **Structured logging**: JSON-formatted logs with correlation IDs
- **Performance monitoring**: System resource and execution metrics
- **Health endpoints**: Beast Mode compliant health and metrics APIs
- **Real-time dashboards**: Execution progress and system status

## Installation

### Prerequisites

1. **Python 3.9+**
2. **Redis server** (for state persistence)
3. **Claude CLI** (for AI prompt execution)

### Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment variables**:
```bash
# Redis configuration
export REDIS_URL="redis://localhost:6379/0"
export REDIS_PASSWORD="your_redis_password"

# Agent configuration
export MAX_CONCURRENT_AGENTS=5
export CLAUDE_CLI_PATH="claude"

# Execution configuration
export DEFAULT_TASK_TIMEOUT=300
export MAX_RETRY_COUNT=3
```

3. **Initialize structured logging**:
```python
from constellation_orchestrator.observability.logging_config import setup_structured_logging
setup_structured_logging(log_level="INFO", json_output=True)
```

## Usage

### Basic Usage

```python
import asyncio
from constellation_orchestrator import ConstellationOrchestrator, ConstellationConfig, TaskDefinition

async def main():
    # Create configuration
    config = ConstellationConfig.load_from_env()
    
    # Create orchestrator
    orchestrator = ConstellationOrchestrator(config)
    
    # Initialize
    await orchestrator.initialize()
    
    # Define tasks with dependencies
    tasks = [
        TaskDefinition(
            task_id="analyze_requirements",
            prompt="Analyze the system requirements and provide key insights",
            dependencies=[],
            timeout=60
        ),
        TaskDefinition(
            task_id="design_architecture", 
            prompt="Design system architecture based on requirements",
            dependencies=["analyze_requirements"],
            timeout=90
        ),
        TaskDefinition(
            task_id="create_implementation_plan",
            prompt="Create detailed implementation plan",
            dependencies=["design_architecture"],
            timeout=120
        )
    ]
    
    # Load and execute tasks
    await orchestrator.load_tasks(tasks)
    execution_id = await orchestrator.start_execution("my_workflow")
    
    # Monitor progress
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if state.is_execution_complete():
            break
        await asyncio.sleep(1)
    
    # Shutdown
    await orchestrator.shutdown()

asyncio.run(main())
```

### Advanced Configuration

```python
from constellation_orchestrator.core.config import ConstellationConfig

config = ConstellationConfig(
    # Redis configuration
    redis_url="redis://localhost:6379/0",
    redis_password="secure_password",
    
    # Agent scaling
    max_concurrent_agents=10,
    base_agent_count=3,
    max_agent_count=20,
    scale_threshold=0.8,
    
    # Execution settings
    default_task_timeout=300,
    max_retry_count=3,
    
    # Storage
    log_directory="/var/log/constellation",
    max_memory_tasks=1000,
    
    # Monitoring
    enable_metrics=True,
    metrics_port=8080
)
```

### Task Definition Options

```python
TaskDefinition(
    task_id="complex_analysis",
    prompt="Perform comprehensive system analysis...",
    dependencies=["data_collection", "requirements_gathering"],
    
    # Execution parameters
    estimated_duration=180,
    timeout=300,
    retry_count=3,
    
    # Metadata
    category="analysis",
    priority=1,  # 1=highest, 10=lowest
    tags=["analysis", "system-design"],
    
    # Output configuration
    output_format="markdown",
    capture_logs=True,
    
    # Advanced options
    agent_requirements={"min_memory_mb": 512},
    environment_variables={"ANALYSIS_MODE": "detailed"}
)
```

## Examples

### 1. Simple Sequential Workflow
```bash
python examples/basic_constellation_usage.py
```

### 2. Complex Analysis Pipeline
See `examples/basic_constellation_usage.py` for a comprehensive e-commerce analysis workflow with:
- Requirements gathering
- Market research
- System architecture design
- Database design
- API specification
- Security analysis
- Implementation roadmap

### 3. Testing and Validation
```bash
python scripts/test_constellation_orchestrator.py
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `REDIS_PASSWORD` | `""` | Redis password |
| `MAX_CONCURRENT_AGENTS` | `5` | Maximum concurrent agents |
| `BASE_AGENT_COUNT` | `3` | Base number of agents |
| `MAX_AGENT_COUNT` | `20` | Maximum agents for scaling |
| `CLAUDE_CLI_PATH` | `claude` | Path to Claude CLI |
| `DEFAULT_TASK_TIMEOUT` | `300` | Default task timeout (seconds) |
| `MAX_RETRY_COUNT` | `3` | Maximum retry attempts |
| `SCALE_THRESHOLD` | `0.8` | Agent utilization threshold for scaling |
| `LOG_DIRECTORY` | `/tmp/constellation_logs` | Log file directory |

### Redis Configuration

The orchestrator requires Redis for state persistence and recovery:

```bash
# Start Redis server
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:alpine
```

### Claude CLI Setup

Install and configure Claude CLI:

```bash
# Install Claude CLI (example)
pip install claude-cli

# Configure authentication
claude auth login
```

## Monitoring and Observability

### Health Checks

```python
# Check orchestrator health
health = await orchestrator.health_check()
print(f"Status: {health['status']}")
print(f"Components healthy: {health['components_healthy']}")
print(f"Available agents: {health['available_agents']}")
```

### Performance Metrics

```python
# Get execution statistics
stats = orchestrator.dag_manager.get_dag_statistics()
print(f"Total tasks: {stats['total_tasks']}")
print(f"Critical path length: {stats['critical_path_length']}")

# Get agent performance
agent_stats = orchestrator.agent_manager.get_pool_statistics()
print(f"Agent utilization: {agent_stats['utilization']:.2f}")
print(f"Success rate: {agent_stats['average_success_rate']:.2f}")
```

### Structured Logging

All components use structured logging with correlation IDs:

```json
{
  "timestamp": "2025-01-27T10:30:45.123Z",
  "level": "INFO",
  "event": "constellation_task_completed",
  "correlation_id": "abc123",
  "execution_id": "constellation_20250127_103045_def456",
  "task_id": "analyze_requirements",
  "duration": 45.2,
  "status": "completed"
}
```

## Error Handling and Recovery

### Automatic Recovery
- **Agent failures**: Automatic agent restart and task reassignment
- **Network issues**: Exponential backoff retry with different agents
- **Timeout handling**: Configurable timeouts with graceful degradation
- **State corruption**: Checkpoint-based recovery from Redis

### Manual Recovery
```python
# Resume interrupted execution
execution_id = "constellation_20250127_103045_def456"
if await orchestrator.status_manager.can_resume(execution_id):
    task_states = await orchestrator.status_manager.resume_execution(execution_id)
    print(f"Resumed execution with {len(task_states)} tasks")
```

## Performance Optimization

### Scaling Configuration
```python
config = ConstellationConfig(
    # Optimize for large workloads
    max_concurrent_agents=20,
    scale_threshold=0.7,  # Scale up earlier
    scale_cooldown=30,    # Faster scaling decisions
    
    # Memory optimization
    max_memory_tasks=2000,
    
    # Timeout optimization
    default_task_timeout=180,  # Shorter timeouts
    max_retry_count=2          # Fewer retries
)
```

### Performance Monitoring
```python
# Enable performance monitoring
from constellation_orchestrator.observability.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor(snapshot_interval=30)
monitor.start_monitoring()

# Get performance recommendations
recommendations = monitor.get_performance_recommendations()
for rec in recommendations:
    print(f"💡 {rec}")
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check Redis is running
   redis-cli ping
   
   # Check connection string
   export REDIS_URL="redis://localhost:6379/0"
   ```

2. **Claude CLI Not Found**
   ```bash
   # Install Claude CLI
   pip install claude-cli
   
   # Set path
   export CLAUDE_CLI_PATH="/usr/local/bin/claude"
   ```

3. **Agent Scaling Issues**
   ```bash
   # Check agent health
   health = await orchestrator.agent_manager.health_check_agents()
   print(health)
   ```

4. **DAG Validation Errors**
   ```python
   # Check for cycles
   validation = await orchestrator.dag_manager.validate_dag()
   if not validation.is_valid:
       print(f"Cycles: {validation.cycles}")
       print(f"Orphaned: {validation.orphaned_tasks}")
   ```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
from constellation_orchestrator.observability.logging_config import setup_structured_logging
setup_structured_logging(log_level="DEBUG", json_output=False)
```

## Contributing

1. **Code Style**: Follow PEP 8 and use type hints
2. **Testing**: Add tests for new functionality
3. **Documentation**: Update docstrings and README
4. **Logging**: Use structured logging with correlation IDs
5. **Error Handling**: Implement comprehensive error handling

## License

This project is part of the Beast Mode framework and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the examples and test scripts
3. Enable debug logging for detailed diagnostics
4. Check Redis and Claude CLI connectivity