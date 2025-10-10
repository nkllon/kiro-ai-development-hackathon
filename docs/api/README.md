# Beast Mode AI Development Framework - API Documentation

## Overview

The Beast Mode AI Development Framework provides a comprehensive set of APIs for building intelligent, self-reflective AI systems with systematic orchestration, memory management, and observability capabilities.

## Core Architecture

The framework is built around several key architectural patterns:

- **ReflectiveModule Pattern**: All components implement self-monitoring and health reporting
- **DAG Orchestration**: Task execution with dependency management
- **AI Memory Palace**: Intelligent context management and summarization
- **Secure Configuration**: Environment-based credential management
- **Graceful Degradation**: Systematic error handling and fallback mechanisms

## API Categories

### [Core APIs](./core/)
- [ReflectiveModule](./core/reflective-module.md) - Base class for all framework components
- [Configuration Management](./core/configuration.md) - Secure credential and environment handling
- [Error Handling](./core/error-handling.md) - Systematic error management

### [Orchestration APIs](./orchestration/)
- [Constellation Orchestrator](./orchestration/constellation-orchestrator.md) - DAG-based task execution
- [DAG Management](./orchestration/dag-management.md) - Dependency graph management
- [Execution Tracking](./orchestration/execution-tracking.md) - Redis-based execution monitoring

### [AI Memory Palace APIs](./memory-palace/)
- [Context Engine](./memory-palace/context-engine.md) - Intelligent context processing
- [Session Management](./memory-palace/session-management.md) - Context persistence and retrieval
- [Summarization](./memory-palace/summarization.md) - Large context compression

### [Security APIs](./security/)
- [Secure Credentials](./security/secure-credentials.md) - Environment-based credential management
- [Authentication](./security/authentication.md) - Service authentication patterns
- [Validation](./security/validation.md) - Input validation and sanitization

### [Monitoring APIs](./monitoring/)
- [Health Checks](./monitoring/health-checks.md) - Component health monitoring
- [Metrics Collection](./monitoring/metrics.md) - Performance and usage metrics
- [Observability](./monitoring/observability.md) - Distributed tracing and logging

## Quick Start

### Installation

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

### Basic Usage

```python
from src.beast_mode.core import ReflectiveModule
from src.constellation_orchestrator.core import ConstellationOrchestrator
from src.ai_memory_palace.engine import ContextEngine

# Initialize components
orchestrator = ConstellationOrchestrator()
await orchestrator.initialize()

# Load and execute tasks
task_definitions = load_task_definitions()
await orchestrator.load_tasks(task_definitions)
execution_id = await orchestrator.start_execution()

# Monitor execution
state = await orchestrator.get_execution_state(execution_id)
print(f"Execution status: {state.status}")
```

## Environment Variables

All sensitive configuration is managed through environment variables. See [Configuration Guide](./core/configuration.md) for details.

### Required Variables

```bash
# Redis Configuration
REDIS_PASSWORD=your_redis_password
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database
DATABASE_PASSWORD=your_db_password
```

### Optional Variables

```bash
# Application Settings
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Performance Tuning
MAX_CONCURRENT_TASKS=10
CONTEXT_CACHE_SIZE_MB=100
```

## Security Best Practices

⚠️ **CRITICAL**: Never hardcode credentials in source code. Always use environment variables.

```python
# ✅ CORRECT: Use environment variables
import os
redis_password = os.getenv('REDIS_PASSWORD')
if not redis_password:
    raise ValueError("REDIS_PASSWORD environment variable required")

# ❌ WRONG: Never hardcode credentials
redis_password = "hardcoded_password"  # NEVER DO THIS
```

## Error Handling

All framework components implement systematic error handling with graceful degradation:

```python
try:
    result = await component.execute_operation()
except Exception as e:
    # Components automatically handle graceful degradation
    degradation_result = await component.graceful_degradation(e)
    if degradation_result.success:
        # Continue with reduced functionality
        pass
    else:
        # Handle complete failure
        raise
```

## Health Monitoring

All components provide health status information:

```python
# Check component health
health = await component.get_health_status()
print(f"Status: {health.status}")
print(f"Health Score: {health.health_score}")
print(f"Issues: {health.issues}")

# Get component capabilities
capabilities = component.get_capabilities()
print(f"Available capabilities: {capabilities}")
```

## Performance Considerations

### Memory Management
- Context data is automatically compressed when size limits are exceeded
- Old execution records are cleaned up automatically
- Components implement memory-efficient streaming for large datasets

### Concurrency
- All APIs are async/await compatible
- Components support concurrent execution with proper resource management
- Built-in rate limiting and backpressure handling

### Scalability
- Redis-based state management for distributed deployments
- Horizontal scaling support through agent management
- Configurable resource limits and timeouts

## Migration Guide

### From Legacy Systems

If migrating from older versions or similar frameworks:

1. **Update Imports**: Use unified interfaces from `src.rm_ddd.core`
2. **Environment Variables**: Convert hardcoded credentials to environment variables
3. **Error Handling**: Implement ReflectiveModule pattern for systematic error handling
4. **Health Monitoring**: Add health check endpoints to all components

### Breaking Changes

- ReflectiveModule interface has been unified in `src.rm_ddd.core.unified_reflective_module`
- All credential management must use environment variables
- Legacy synchronous APIs have been replaced with async/await patterns

## Support and Contributing

- [Contributing Guide](../../CONTRIBUTING.md)
- [Issue Templates](../../.github/ISSUE_TEMPLATE/)
- [Community Guidelines](../community/COMMUNITY_GUIDELINES.md)

## API Reference Index

- [Core APIs](./core/) - Fundamental framework components
- [Orchestration APIs](./orchestration/) - Task execution and management
- [Memory Palace APIs](./memory-palace/) - Context and memory management
- [Security APIs](./security/) - Authentication and credential management
- [Monitoring APIs](./monitoring/) - Health checks and observability
- [Utility APIs](./utilities/) - Helper functions and tools

---

**Next Steps**: Explore the [Core APIs](./core/) to understand the fundamental building blocks of the framework.