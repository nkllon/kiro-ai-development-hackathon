# Design Document

## Overview

Migrate AI Memory Palace components from ReflectiveModule (Layer 2) to BeastlyModule (Layer 3) to enable full Beast Mode observability. This migration provides mandatory Jaeger distributed tracing, enhanced observation correlation, and complete system integration with the Beast Mode ecosystem.

## Architecture

### Current State (Layer 2)
```
AI Memory Palace Components
├── Import: from ..core.reflective_module import ReflectiveModule
├── Inheritance: class Component(ReflectiveModule)
├── Observability: Optional Prometheus, graceful degradation
└── Tracing: Optional, fallback to basic logging
```

### Target State (Layer 3)
```
AI Memory Palace Components
├── Import: from src.beast_mode.core.beastly_module import BeastlyModule
├── Inheritance: class Component(BeastlyModule)
├── Observability: Full Prometheus + Jaeger integration
└── Tracing: Mandatory distributed tracing with correlation
```

### Layer Cake Architecture
- **Layer 1**: Abstract interfaces and pure abstractions
- **Layer 2**: ReflectiveModule - optional dependencies, graceful degradation
- **Layer 3**: BeastlyModule - full Beast Mode experience, requires infrastructure

## Components and Interfaces

### Components to Migrate
1. **ContextManager** - Main orchestrator
2. **ContextRegistry** - Storage and retrieval
3. **ContextEngine** - Processing and summarization
4. **ContextValidator** - Integrity validation
5. **SessionManager** - Session restoration
6. **ContextAPI** - REST API endpoints
7. **ContextCLITools** - Command-line interface
8. **All other AI Memory Palace components** (15+ total)

### Import Path Changes
```python
# Before (deprecated)
from ..core.reflective_module import ReflectiveModule

# After (direct BeastlyModule)
from src.beast_mode.core.beastly_module import BeastlyModule
```

### Enhanced Capabilities Gained
- **Automatic Jaeger tracing** with service discovery
- **Enhanced observation emission** with trace correlation
- **Distributed span creation** for all operations
- **Trace event emission** for debugging
- **System topology discovery** through tracing

## Data Models

### Tracing Integration
```python
class AIMemoryPalaceComponent(BeastlyModule):
    def __init__(self):
        super().__init__()
        # Inherits:
        # - self._tracer (Jaeger tracer)
        # - self._tracing_enabled (availability check)
        # - Enhanced observation methods
```

### Observation Enhancement
```python
# Enhanced observations with trace correlation
self.emit_observation(
    message="Context operation completed",
    event_type="info",
    context={"session_id": session_id},
    emoji="🧠"
)
# Automatically includes trace_id when available
```

## Error Handling

### Graceful Degradation Strategy
1. **Tracing Available**: Full BeastlyModule capabilities
2. **Tracing Unavailable**: Falls back to ReflectiveModule behavior
3. **Infrastructure Missing**: Components still function with reduced observability

### Error Scenarios
- **Jaeger service down**: Components continue operating, log warnings
- **Network connectivity issues**: Local operation continues, tracing queued
- **Configuration errors**: Graceful fallback to basic observability

## Testing Strategy

### Unit Tests
- **Mock tracing infrastructure** for isolated testing
- **Test graceful degradation** when tracing unavailable
- **Verify backward compatibility** of existing APIs

### Integration Tests
- **End-to-end tracing** with real Jaeger infrastructure
- **Cross-component correlation** testing
- **Performance impact** measurement

### Migration Validation
- **Before/after comparison** of functionality
- **Tracing data validation** in test environment
- **Performance regression** testing

## Implementation Approach

### Phase 1: Core Components
1. Migrate ContextManager (main orchestrator)
2. Migrate ContextRegistry (storage layer)
3. Validate tracing integration

### Phase 2: Processing Components
1. Migrate ContextEngine and ContextValidator
2. Migrate SessionManager
3. Test cross-component tracing

### Phase 3: Interface Components
1. Migrate ContextAPI and ContextCLITools
2. Migrate remaining components
3. End-to-end validation

### Rollback Strategy
- Keep deprecated import wrapper temporarily
- Gradual migration with component-by-component validation
- Easy revert to ReflectiveModule if issues arise