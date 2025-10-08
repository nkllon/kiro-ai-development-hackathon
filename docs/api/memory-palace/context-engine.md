# AI Memory Palace Context Engine API

## Overview

The Context Engine provides intelligent context processing and summarization with performance optimization for large datasets. It implements the ReflectiveModule pattern and offers advanced context management capabilities including filtering, compression, and staleness validation.

## Location

```python
from src.ai_memory_palace.engine.context_engine import ContextEngine
from src.ai_memory_palace.models.context_models import SessionContext, ContextSummary, ContextEvent
```

## Class Definition

```python
class ContextEngine(ReflectiveModule):
    """Intelligent context processing and summarization."""
    
    def __init__(self):
        """Initialize the Context Engine with default configuration."""
```

## Core Methods

### Context Summarization

#### `summarize_context(full_context: SessionContext) -> ContextSummary`

Summarize context for large datasets to reduce memory usage and improve processing efficiency.

```python
from src.ai_memory_palace.engine.context_engine import ContextEngine
from src.ai_memory_palace.models.context_models import SessionContext

engine = ContextEngine()

# Summarize large context
summary = engine.summarize_context(full_context)

print(f"Project: {summary.project_id}")
print(f"Total events: {summary.total_events}")
print(f"Context size: {summary.context_size_mb:.2f} MB")
print(f"System health: {summary.system_health}")
print(f"Recent decisions: {summary.recent_decisions}")
```

**Parameters:**
- `full_context` (SessionContext): Complete session context to summarize

**Returns:**
- `ContextSummary`: Condensed summary with key metrics and recent activity

**Summary Includes:**
- Project identification
- Event count and size metrics
- Recent decisions (last 5)
- Active specifications
- System health status
- Context size in MB

### Context Filtering

#### `filter_relevant_context(context: SessionContext, query: str) -> SessionContext`

Filter context for relevance based on query keywords to improve processing efficiency.

```python
# Filter context based on query
query = "database migration error handling"
filtered_context = engine.filter_relevant_context(full_context, query)

print(f"Original events: {len(full_context.conversation_history)}")
print(f"Filtered events: {len(filtered_context.conversation_history)}")
```

**Parameters:**
- `context` (SessionContext): Full context to filter
- `query` (str): Query string for relevance filtering

**Returns:**
- `SessionContext`: Filtered context containing only relevant items

**Filtering Logic:**
- Keyword-based relevance matching
- Preserves full project state
- Maintains all completed work
- Filters conversation history and decisions

### Context Compression

#### `compress_old_data(context: SessionContext, threshold_mb: int = 10) -> SessionContext`

Compress old context data when size limits are exceeded.

```python
# Compress context if it exceeds 10MB
compressed_context = engine.compress_old_data(full_context, threshold_mb=10)

# Check compression results
original_size = len(str(full_context)) / (1024 * 1024)
compressed_size = len(str(compressed_context)) / (1024 * 1024)

print(f"Original size: {original_size:.2f} MB")
print(f"Compressed size: {compressed_size:.2f} MB")
print(f"Reduction: {((original_size - compressed_size) / original_size) * 100:.1f}%")
```

**Parameters:**
- `context` (SessionContext): Context to compress
- `threshold_mb` (int): Size threshold in MB for triggering compression

**Returns:**
- `SessionContext`: Compressed context with reduced size

**Compression Strategy:**
- Keeps most recent 100 conversation items
- Preserves most recent 50 decisions
- Maintains most recent 20 system discoveries
- Logs compression activity

### Data Pagination

#### `paginate_events(events: List[Dict[str, Any]], page_size: int = 100) -> Iterator[List[Dict[str, Any]]]`

Paginate large event collections for memory-efficient processing.

```python
# Process large event collections in chunks
large_event_list = load_large_event_collection()

for page in engine.paginate_events(large_event_list, page_size=50):
    print(f"Processing page with {len(page)} events")
    
    # Process events in manageable chunks
    for event in page:
        process_event(event)
```

**Parameters:**
- `events` (List[Dict[str, Any]]): Large list of events to paginate
- `page_size` (int): Number of events per page (default: 100)

**Returns:**
- `Iterator[List[Dict[str, Any]]]`: Iterator yielding pages of events

### Context Validation

#### `validate_staleness(context: SessionContext) -> Dict[str, Any]`

Validate context freshness and determine if refresh is needed.

```python
# Check if context is stale
staleness_info = engine.validate_staleness(context)

if staleness_info['is_stale']:
    print(f"Context is stale (age: {staleness_info['age_hours']:.1f} hours)")
    print("Refresh recommended")
else:
    print("Context is fresh")

print(f"Age: {staleness_info['age_hours']:.1f} hours")
print(f"Threshold: {staleness_info['threshold_hours']} hours")
```

**Parameters:**
- `context` (SessionContext): Context to validate

**Returns:**
- `Dict[str, Any]`: Staleness validation results
  - `is_stale` (bool): Whether context is considered stale
  - `age_hours` (float): Age of context in hours
  - `threshold_hours` (float): Staleness threshold
  - `refresh_needed` (bool): Whether refresh is recommended

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

### ContextEvent

```python
@dataclass
class ContextEvent:
    event_id: str
    timestamp: datetime
    event_type: str
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
```

## Usage Examples

### Basic Context Processing

```python
import asyncio
from datetime import datetime
from src.ai_memory_palace.engine.context_engine import ContextEngine
from src.ai_memory_palace.models.context_models import SessionContext

async def basic_context_processing():
    engine = ContextEngine()
    
    # Create sample context
    context = SessionContext(
        project_id="example_project",
        session_id="session_123",
        timestamp=datetime.now(),
        conversation_history=[
            {"role": "user", "content": "How do I set up database migration?"},
            {"role": "assistant", "content": "Here's how to set up database migration..."},
            {"role": "user", "content": "What about error handling?"},
            {"role": "assistant", "content": "For error handling in migrations..."}
        ],
        project_state={"active_specs": ["database_migration", "error_handling"]},
        decisions_made=[
            {"summary": "Use Alembic for database migrations"},
            {"summary": "Implement retry logic for failed migrations"}
        ],
        work_completed=[
            {"task": "Database schema design", "status": "completed"}
        ],
        system_discoveries=[
            {"discovery": "PostgreSQL version compatibility issue"}
        ],
        spec_states={"database_migration": "in_progress"}
    )
    
    # Summarize context
    summary = engine.summarize_context(context)
    print(f"Summary: {summary.total_events} events, {summary.context_size_mb:.2f} MB")
    
    # Filter for database-related content
    filtered = engine.filter_relevant_context(context, "database migration")
    print(f"Filtered: {len(filtered.conversation_history)} relevant items")
    
    # Check staleness
    staleness = engine.validate_staleness(context)
    print(f"Context age: {staleness['age_hours']:.1f} hours")

asyncio.run(basic_context_processing())
```

### Large Context Management

```python
import asyncio
from src.ai_memory_palace.engine.context_engine import ContextEngine

async def large_context_management():
    engine = ContextEngine()
    
    # Load large context (simulated)
    large_context = load_large_session_context()  # Your loading logic
    
    print(f"Original context size: {len(str(large_context)) / (1024 * 1024):.2f} MB")
    
    # Compress if too large
    compressed_context = engine.compress_old_data(large_context, threshold_mb=5)
    
    print(f"Compressed size: {len(str(compressed_context)) / (1024 * 1024):.2f} MB")
    
    # Process in chunks for memory efficiency
    all_events = large_context.conversation_history
    
    processed_count = 0
    for event_page in engine.paginate_events(all_events, page_size=100):
        # Process each page
        for event in event_page:
            # Your event processing logic
            await process_event(event)
            processed_count += 1
        
        print(f"Processed {processed_count} events so far...")
        
        # Optional: yield control to other tasks
        await asyncio.sleep(0.1)
    
    print(f"Total events processed: {processed_count}")

async def process_event(event):
    """Simulate event processing."""
    await asyncio.sleep(0.01)  # Simulate processing time

asyncio.run(large_context_management())
```

### Context-Aware Query Processing

```python
from src.ai_memory_palace.engine.context_engine import ContextEngine

def context_aware_query_processing():
    engine = ContextEngine()
    
    # Load full context
    full_context = load_session_context()
    
    # Different queries for different use cases
    queries = [
        "database migration errors",
        "API integration testing",
        "performance optimization",
        "security vulnerabilities"
    ]
    
    for query in queries:
        print(f"\nProcessing query: '{query}'")
        
        # Filter context for relevance
        relevant_context = engine.filter_relevant_context(full_context, query)
        
        # Summarize relevant context
        summary = engine.summarize_context(relevant_context)
        
        print(f"  Relevant events: {summary.total_events}")
        print(f"  Recent decisions: {len(summary.recent_decisions)}")
        print(f"  Context size: {summary.context_size_mb:.2f} MB")
        
        # Process with filtered context
        response = generate_response_with_context(query, relevant_context)
        print(f"  Response length: {len(response)} characters")

def generate_response_with_context(query, context):
    """Simulate response generation with context."""
    # Your AI response generation logic here
    return f"Response to '{query}' based on {len(context.conversation_history)} relevant items"

context_aware_query_processing()
```

### Performance Monitoring

```python
import time
import asyncio
from src.ai_memory_palace.engine.context_engine import ContextEngine

async def performance_monitoring_example():
    engine = ContextEngine()
    
    # Create contexts of different sizes
    contexts = {
        "small": create_context_with_events(100),
        "medium": create_context_with_events(1000),
        "large": create_context_with_events(10000)
    }
    
    for size_name, context in contexts.items():
        print(f"\nTesting {size_name} context:")
        
        # Test summarization performance
        start_time = time.time()
        summary = engine.summarize_context(context)
        summarize_time = time.time() - start_time
        
        print(f"  Summarization: {summarize_time:.3f}s")
        print(f"  Events: {summary.total_events}")
        print(f"  Size: {summary.context_size_mb:.2f} MB")
        
        # Test filtering performance
        start_time = time.time()
        filtered = engine.filter_relevant_context(context, "test query")
        filter_time = time.time() - start_time
        
        print(f"  Filtering: {filter_time:.3f}s")
        print(f"  Filtered events: {len(filtered.conversation_history)}")
        
        # Test compression performance
        start_time = time.time()
        compressed = engine.compress_old_data(context, threshold_mb=1)
        compress_time = time.time() - start_time
        
        print(f"  Compression: {compress_time:.3f}s")
        
        # Calculate compression ratio
        original_size = len(str(context))
        compressed_size = len(str(compressed))
        ratio = (original_size - compressed_size) / original_size * 100
        
        print(f"  Compression ratio: {ratio:.1f}%")

def create_context_with_events(event_count):
    """Create a context with specified number of events."""
    from datetime import datetime
    from src.ai_memory_palace.models.context_models import SessionContext
    
    events = []
    for i in range(event_count):
        events.append({
            "id": f"event_{i}",
            "content": f"This is event number {i} with some content",
            "timestamp": datetime.now().isoformat()
        })
    
    return SessionContext(
        project_id="performance_test",
        session_id="test_session",
        timestamp=datetime.now(),
        conversation_history=events,
        project_state={"test": True},
        decisions_made=[],
        work_completed=[],
        system_discoveries=[],
        spec_states={}
    )

asyncio.run(performance_monitoring_example())
```

### Integration with Other Systems

```python
import asyncio
from src.ai_memory_palace.engine.context_engine import ContextEngine
from src.execution_tracking.redis_execution_tracker import RedisExecutionTracker

async def integrated_context_tracking():
    # Initialize systems
    context_engine = ContextEngine()
    execution_tracker = RedisExecutionTracker()
    
    await execution_tracker.initialize()
    
    # Start execution tracking
    execution_id = await execution_tracker.start_execution("context_processing_pipeline")
    
    try:
        # Load and process context
        full_context = load_large_session_context()
        
        # Check if context needs compression
        staleness_info = context_engine.validate_staleness(full_context)
        
        if staleness_info['refresh_needed']:
            await execution_tracker.checkin_execution(
                execution_id,
                phase="context_refresh",
                message="Context is stale, refreshing..."
            )
            
            # Refresh context logic here
            full_context = refresh_context(full_context)
        
        # Compress if needed
        original_size = len(str(full_context)) / (1024 * 1024)
        if original_size > 10:  # 10MB threshold
            await execution_tracker.checkin_execution(
                execution_id,
                phase="context_compression",
                message=f"Compressing {original_size:.1f}MB context"
            )
            
            full_context = context_engine.compress_old_data(full_context, threshold_mb=10)
            
            compressed_size = len(str(full_context)) / (1024 * 1024)
            await execution_tracker.checkin_execution(
                execution_id,
                phase="context_compression",
                message=f"Compressed to {compressed_size:.1f}MB"
            )
        
        # Process queries with context
        queries = ["database", "API", "performance", "security"]
        
        for i, query in enumerate(queries):
            await execution_tracker.checkin_execution(
                execution_id,
                phase="query_processing",
                progress_percentage=(i / len(queries)) * 100,
                message=f"Processing query: {query}"
            )
            
            # Filter and process
            relevant_context = context_engine.filter_relevant_context(full_context, query)
            summary = context_engine.summarize_context(relevant_context)
            
            # Your query processing logic here
            await process_query_with_context(query, relevant_context)
        
        # Mark as completed
        await execution_tracker.update_execution_status(
            execution_id,
            ExecutionStatus.COMPLETED,
            completed_tasks=len(queries)
        )
        
    except Exception as e:
        await execution_tracker.update_execution_status(
            execution_id,
            ExecutionStatus.FAILED,
            error_message=str(e)
        )
        raise

async def process_query_with_context(query, context):
    """Process query with filtered context."""
    # Simulate processing time
    await asyncio.sleep(1)
    return f"Processed query '{query}' with {len(context.conversation_history)} relevant items"

def refresh_context(context):
    """Refresh stale context."""
    # Your context refresh logic
    context.timestamp = datetime.now()
    return context

asyncio.run(integrated_context_tracking())
```

## Best Practices

### 1. Memory Management

```python
def memory_efficient_processing():
    engine = ContextEngine()
    
    # Always check context size before processing
    context = load_context()
    context_size_mb = len(str(context)) / (1024 * 1024)
    
    if context_size_mb > 50:  # 50MB threshold
        print(f"Large context detected: {context_size_mb:.1f}MB")
        
        # Compress before processing
        context = engine.compress_old_data(context, threshold_mb=20)
        print(f"Compressed to: {len(str(context)) / (1024 * 1024):.1f}MB")
    
    # Use pagination for large event collections
    if len(context.conversation_history) > 1000:
        for page in engine.paginate_events(context.conversation_history, page_size=100):
            process_event_page(page)
    else:
        process_all_events(context.conversation_history)
```

### 2. Context Freshness Management

```python
def manage_context_freshness():
    engine = ContextEngine()
    context = load_context()
    
    # Always validate staleness
    staleness_info = engine.validate_staleness(context)
    
    if staleness_info['is_stale']:
        print(f"Context is {staleness_info['age_hours']:.1f} hours old")
        
        if staleness_info['age_hours'] > 24:
            # Very stale - full refresh needed
            context = perform_full_context_refresh(context)
        elif staleness_info['age_hours'] > 6:
            # Moderately stale - partial refresh
            context = perform_partial_context_refresh(context)
        else:
            # Slightly stale - just update timestamp
            context.timestamp = datetime.now()
    
    return context
```

### 3. Query-Specific Context Filtering

```python
def smart_context_filtering():
    engine = ContextEngine()
    full_context = load_context()
    
    # Different filtering strategies for different query types
    query_strategies = {
        "technical": ["error", "bug", "fix", "implementation"],
        "planning": ["roadmap", "timeline", "milestone", "deadline"],
        "architecture": ["design", "pattern", "structure", "component"],
        "performance": ["slow", "optimization", "bottleneck", "latency"]
    }
    
    def get_query_type(query):
        query_lower = query.lower()
        for query_type, keywords in query_strategies.items():
            if any(keyword in query_lower for keyword in keywords):
                return query_type
        return "general"
    
    def filter_for_query(query):
        query_type = get_query_type(query)
        
        if query_type == "technical":
            # For technical queries, include more system discoveries
            filtered = engine.filter_relevant_context(full_context, query)
            # Ensure we keep all system discoveries for technical context
            filtered.system_discoveries = full_context.system_discoveries
            return filtered
        elif query_type == "planning":
            # For planning queries, focus on decisions and work completed
            filtered = engine.filter_relevant_context(full_context, query)
            # Keep all decisions for planning context
            filtered.decisions_made = full_context.decisions_made
            return filtered
        else:
            # Standard filtering for other queries
            return engine.filter_relevant_context(full_context, query)
    
    return filter_for_query
```

### 4. Error Handling and Recovery

```python
async def robust_context_processing():
    engine = ContextEngine()
    
    try:
        context = load_context()
        
        # Validate context integrity
        if not context.conversation_history:
            raise ValueError("Empty conversation history")
        
        if not context.project_id:
            raise ValueError("Missing project ID")
        
        # Process with error handling
        try:
            summary = engine.summarize_context(context)
        except Exception as e:
            print(f"Summarization failed: {e}")
            # Create minimal summary
            summary = create_minimal_summary(context)
        
        try:
            staleness_info = engine.validate_staleness(context)
        except Exception as e:
            print(f"Staleness validation failed: {e}")
            # Assume stale and refresh
            staleness_info = {'is_stale': True, 'refresh_needed': True}
        
        # Continue processing with available data
        return process_with_available_data(context, summary, staleness_info)
        
    except Exception as e:
        print(f"Context processing failed: {e}")
        
        # Trigger graceful degradation
        degradation = await engine.graceful_degradation(e)
        if degradation.success:
            print("Using degraded context processing")
            return process_with_degraded_capabilities()
        else:
            raise

def create_minimal_summary(context):
    """Create minimal summary when full summarization fails."""
    return ContextSummary(
        project_id=context.project_id,
        last_session=context.timestamp,
        total_events=len(context.conversation_history),
        recent_decisions=[],
        active_specs=[],
        system_health="unknown",
        context_size_mb=len(str(context)) / (1024 * 1024)
    )
```

## Performance Considerations

### Memory Usage
- Context compression automatically triggers at configurable thresholds
- Pagination prevents memory exhaustion with large event collections
- Filtering reduces memory footprint for query-specific processing

### Processing Speed
- Summarization is optimized for large contexts
- Filtering uses efficient keyword matching
- Compression preserves most recent and important data

### Scalability
- Supports contexts with 10,000+ events
- Handles multi-gigabyte context sizes
- Efficient pagination for streaming processing

---

**Next**: [Session Management](./session-management.md) | **Up**: [Memory Palace APIs](../memory-palace/)