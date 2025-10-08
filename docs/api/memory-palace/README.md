# AI Memory Palace APIs

## Overview

The AI Memory Palace APIs provide intelligent context management and summarization capabilities for large-scale AI interactions. These APIs handle context compression, relevance filtering, and performance optimization for memory-intensive AI workflows.

## Components

### [Context Engine](./context-engine.md)
Intelligent context processing and summarization with performance optimization for large datasets.

**Key Features:**
- Context summarization for large datasets
- Relevance-based context filtering
- Automatic context compression
- Staleness validation and refresh detection
- Memory-efficient event pagination

### [Session Management](./session-management.md)
Context persistence and retrieval with session-based organization.

**Key Features:**
- Session-based context organization
- Persistent context storage
- Context versioning and history
- Multi-session context merging

### [Summarization](./summarization.md)
Advanced context summarization with configurable compression strategies.

**Key Features:**
- Configurable summarization strategies
- Hierarchical context compression
- Key information preservation
- Performance-optimized processing

## Quick Reference

### Basic Context Processing

```python
from src.ai_memory_palace.engine.context_engine import ContextEngine
from src.ai_memory_palace.models.context_models import SessionContext

engine = ContextEngine()

# Load and summarize context
context = load_session_context()
summary = engine.summarize_context(context)

print(f"Context: {summary.total_events} events, {summary.context_size_mb:.2f} MB")
print(f"Health: {summary.system_health}")
print(f"Recent decisions: {summary.recent_decisions}")
```

### Context Filtering

```python
# Filter context for specific queries
query = "database migration error handling"
relevant_context = engine.filter_relevant_context(context, query)

print(f"Original: {len(context.conversation_history)} events")
print(f"Filtered: {len(relevant_context.conversation_history)} relevant events")
```

### Context Compression

```python
# Compress large contexts
original_size = len(str(context)) / (1024 * 1024)
compressed_context = engine.compress_old_data(context, threshold_mb=10)
compressed_size = len(str(compressed_context)) / (1024 * 1024)

print(f"Compressed from {original_size:.1f}MB to {compressed_size:.1f}MB")
print(f"Reduction: {((original_size - compressed_size) / original_size) * 100:.1f}%")
```

### Memory-Efficient Processing

```python
# Process large event collections in chunks
large_events = load_large_event_collection()

for page in engine.paginate_events(large_events, page_size=100):
    print(f"Processing {len(page)} events")
    for event in page:
        await process_event(event)
```

### Context Validation

```python
# Check context freshness
staleness_info = engine.validate_staleness(context)

if staleness_info['is_stale']:
    print(f"Context is {staleness_info['age_hours']:.1f} hours old")
    if staleness_info['refresh_needed']:
        context = refresh_context(context)
```

## Data Models

### SessionContext

```python
@dataclass
class SessionContext:
    project_id: str
    session_id: str
    timestamp: datetime
    conversation_history: List[Dict[str, Any]]
    project_state: Optional[Dict[str, Any]]
    decisions_made: List[Dict[str, Any]]
    work_completed: List[Dict[str, Any]]
    system_discoveries: List[Dict[str, Any]]
    spec_states: Dict[str, Any]
```

### ContextSummary

```python
@dataclass
class ContextSummary:
    project_id: str
    last_session: datetime
    total_events: int
    recent_decisions: List[str]
    active_specs: List[str]
    system_health: str
    context_size_mb: float
```

## Usage Patterns

### Large Context Management

```python
async def manage_large_context():
    engine = ContextEngine()
    context = load_large_context()
    
    # Check size and compress if needed
    context_size = len(str(context)) / (1024 * 1024)
    if context_size > 50:  # 50MB threshold
        print(f"Large context: {context_size:.1f}MB - compressing...")
        context = engine.compress_old_data(context, threshold_mb=20)
        print(f"Compressed to: {len(str(context)) / (1024 * 1024):.1f}MB")
    
    # Process in chunks for memory efficiency
    events = context.conversation_history
    for page in engine.paginate_events(events, page_size=100):
        await process_event_batch(page)
```

### Query-Specific Context

```python
def process_query_with_context(query, full_context):
    engine = ContextEngine()
    
    # Filter context for query relevance
    relevant_context = engine.filter_relevant_context(full_context, query)
    
    # Summarize for overview
    summary = engine.summarize_context(relevant_context)
    
    # Generate response with filtered context
    response = generate_ai_response(query, relevant_context, summary)
    
    return response, summary
```

### Context Freshness Management

```python
def ensure_fresh_context(context):
    engine = ContextEngine()
    
    staleness_info = engine.validate_staleness(context)
    
    if staleness_info['is_stale']:
        age_hours = staleness_info['age_hours']
        
        if age_hours > 24:
            # Very stale - full refresh
            return perform_full_refresh(context)
        elif age_hours > 6:
            # Moderately stale - partial refresh
            return perform_partial_refresh(context)
        else:
            # Slightly stale - update timestamp
            context.timestamp = datetime.now()
    
    return context
```

## Performance Optimization

### Memory Management

The Memory Palace APIs implement several memory optimization strategies:

- **Automatic Compression**: Contexts are compressed when size thresholds are exceeded
- **Event Pagination**: Large event collections are processed in chunks
- **Relevance Filtering**: Only relevant context is kept for specific queries
- **Staleness Detection**: Old contexts are identified for refresh or cleanup

### Processing Efficiency

- **Lazy Loading**: Context data is loaded on-demand
- **Caching**: Frequently accessed contexts are cached
- **Streaming**: Large contexts can be processed as streams
- **Parallel Processing**: Independent context operations run in parallel

### Scalability Considerations

- **Distributed Storage**: Context can be stored across multiple Redis instances
- **Horizontal Scaling**: Context processing can be distributed across multiple workers
- **Load Balancing**: Context requests are balanced across available processors

## Integration Examples

### With Orchestration

```python
async def context_aware_orchestration():
    # Initialize components
    engine = ContextEngine()
    orchestrator = ConstellationOrchestrator()
    await orchestrator.initialize()
    
    # Load and process context
    context = load_session_context()
    relevant_context = engine.filter_relevant_context(context, "data processing")
    
    # Create context-aware tasks
    tasks = create_tasks_from_context(relevant_context)
    
    # Execute with orchestrator
    await orchestrator.load_tasks(tasks)
    execution_id = await orchestrator.start_execution()
    
    # Monitor and update context
    while True:
        state = await orchestrator.get_execution_state(execution_id)
        if not state:
            break
        
        # Update context with execution progress
        context.add_execution_event({
            'execution_id': execution_id,
            'status': state.status.value,
            'progress': state.completed_tasks / state.total_tasks
        })
        
        if state.status.value in ['completed', 'failed']:
            break
        
        await asyncio.sleep(5)
    
    await orchestrator.shutdown()
```

### With Execution Tracking

```python
async def tracked_context_processing():
    from src.execution_tracking.redis_execution_tracker import (
        start_tracking_execution, checkin_execution, ExecutionStatus
    )
    
    engine = ContextEngine()
    
    # Start tracking
    execution_id = await start_tracking_execution("context_processing")
    
    try:
        # Load context
        context = load_large_context()
        
        # Check staleness
        staleness_info = engine.validate_staleness(context)
        if staleness_info['refresh_needed']:
            await checkin_execution(
                execution_id,
                phase="context_refresh",
                message="Refreshing stale context"
            )
            context = refresh_context(context)
        
        # Compress if needed
        original_size = len(str(context)) / (1024 * 1024)
        if original_size > 10:
            await checkin_execution(
                execution_id,
                phase="compression",
                message=f"Compressing {original_size:.1f}MB context"
            )
            context = engine.compress_old_data(context, threshold_mb=10)
        
        # Process queries
        queries = ["database", "API", "performance"]
        for i, query in enumerate(queries):
            await checkin_execution(
                execution_id,
                phase="query_processing",
                progress_percentage=(i / len(queries)) * 100,
                message=f"Processing: {query}"
            )
            
            relevant = engine.filter_relevant_context(context, query)
            summary = engine.summarize_context(relevant)
            await process_query(query, relevant, summary)
        
        await update_execution_status(execution_id, ExecutionStatus.COMPLETED)
        
    except Exception as e:
        await update_execution_status(
            execution_id, 
            ExecutionStatus.FAILED,
            error_message=str(e)
        )
        raise
```

## Best Practices

### 1. Memory Management

```python
# ✅ CORRECT: Check context size before processing
context_size_mb = len(str(context)) / (1024 * 1024)
if context_size_mb > 50:
    context = engine.compress_old_data(context, threshold_mb=20)

# ✅ CORRECT: Use pagination for large collections
for page in engine.paginate_events(large_events, page_size=100):
    process_page(page)
```

### 2. Context Freshness

```python
# ✅ CORRECT: Always validate staleness
staleness_info = engine.validate_staleness(context)
if staleness_info['is_stale']:
    context = refresh_context_appropriately(context, staleness_info)
```

### 3. Query Optimization

```python
# ✅ CORRECT: Filter context for specific queries
relevant_context = engine.filter_relevant_context(full_context, query)
summary = engine.summarize_context(relevant_context)
response = generate_response(query, relevant_context, summary)
```

### 4. Error Handling

```python
# ✅ CORRECT: Handle context processing errors
try:
    summary = engine.summarize_context(context)
except Exception as e:
    # Create minimal summary on error
    summary = create_minimal_summary(context)
    logger.warning(f"Context summarization failed: {e}")
```

---

**Components:** [Context Engine](./context-engine.md) | [Session Management](./session-management.md) | [Summarization](./summarization.md)