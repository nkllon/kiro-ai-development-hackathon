# Coordinator-Worker Architecture Pattern

## Core Principle

The coordinator LLM should be a **pure orchestrator** - never executing tasks directly, always delegating to specialized workers through a uniform interface.

## Architecture Layers

### Coordinator LLM
- **Role**: Task planning, orchestration, result aggregation
- **Never does**: Direct code execution, file operations, complex analysis
- **Always does**: Delegates through uniform worker interface
- **Context**: Keeps only summaries, not full work products

### Worker Types

#### Micro-Workers (Deterministic Functions)
- **Implementation**: Sandboxed Python scripts
- **Use case**: URL generation, simple lookups, deterministic operations
- **Execution time**: < 1 second
- **Security**: Isolated process/container

#### Standard Workers (Lightweight LLMs)
- **Implementation**: Focused LLM instances
- **Use case**: Analysis, reasoning, content generation
- **Execution time**: 1-30 seconds
- **Specialization**: Task-specific prompting

#### Heavy Workers (Full LLMs + Tools)
- **Implementation**: Complete LLM with tool access
- **Use case**: Complex analysis, multi-step operations
- **Execution time**: 30+ seconds
- **Capabilities**: File access, external APIs, complex reasoning

## Uniform Interface

All workers return structured responses:
```json
{
  "summary": "Brief result for coordinator context",
  "full_response": "Complete work product",
  "metadata": {
    "worker_type": "micro|standard|heavy",
    "execution_time": "duration",
    "interpretation": "which path taken",
    "cost": "resource usage"
  }
}
```

## Benefits

### For Ambiguous Requests
- **Parallel execution**: Multiple interpretations run concurrently
- **Resource efficiency**: Right tool for each job
- **Context preservation**: Coordinator stays lean

### For System Architecture
- **Security isolation**: No code execution in coordinator context
- **Fault tolerance**: Worker failures don't crash coordinator
- **Observability**: Every operation logged uniformly
- **Scalability**: Unlimited parallel capacity
- **Specialization**: Workers optimized for specific tasks

### For Development
- **Consistent interface**: Same pattern regardless of complexity
- **Easy optimization**: Promote micro-workers to full workers as needed
- **Perfect audit trail**: Every decision and action preserved
- **Reusability**: Cached results for similar requests

## Implementation Strategy

1. **Start simple**: Begin with micro-workers for deterministic operations
2. **Promote gradually**: Move complex operations to appropriate worker types
3. **Maintain interface**: Never break the uniform response format
4. **Optimize by usage**: Profile and optimize based on actual patterns

## Decision Matrix

**Use micro-worker when:**
- Operation is deterministic
- Result is predictable
- Execution time < 1 second
- No reasoning required

**Use standard worker when:**
- Requires analysis or reasoning
- Multiple valid approaches exist
- Execution time 1-30 seconds
- Context-dependent decisions

**Use heavy worker when:**
- Complex multi-step operations
- Requires external tools/APIs
- Execution time > 30 seconds
- Deep analysis required

## Success Metrics

- **Context efficiency**: Coordinator context window usage
- **Fault isolation**: Worker failures don't propagate
- **Parallel utilization**: Multiple workers active simultaneously
- **Response consistency**: Uniform interface compliance
- **Audit completeness**: Full traceability of all operations

This architecture transforms the LLM from a "do everything" system into a "coordinate everything" system - a fundamental shift toward specialization and scalability.