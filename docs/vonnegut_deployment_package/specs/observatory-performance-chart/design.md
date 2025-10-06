# Design Document

## Overview

This design implements a **Living Observatory Dashboard** that combines structured performance metrics with real-time unstructured observations. Following the proven HealthChartInitializer and TokenChartInitializer patterns, it creates a dynamic dashboard that shows both what the metrics say AND what's actually happening right now through Beastly Module observability streams.

## Architecture

### Living Dashboard Integration
```
PerformanceChartInitializer + ObservationStreamHandler
    ↓
Structured Data: /api/dashboard/all-data → apiData.metrics
    ↓
Unstructured Data: Beastly Module Streams → ReflectiveModule events
    ↓
Dual Rendering: Chart.js + Real-time Activity Feed
```

### Data Flow Architecture
```
Beastly Modules (ReflectiveModule instances)
    ↓ (structured metrics)
/api/dashboard/all-data → Performance Charts
    ↓ (unstructured observations)  
WebSocket/SSE Stream → Activity Feed
    ↓ (correlation)
Timeline Correlation → "What just happened" annotations
```

## Data Models

### Structured Performance Data
**API Response Format**:
```javascript
{
    metrics: {
        responseTime: 200.0,    // Milliseconds (primary Y-axis)
        errorRate: 5.0,         // Percentage (secondary Y-axis)  
        throughput: 150.0       // Operations per second (secondary Y-axis)
    }
}
```

### Unstructured Observation Stream
**Beastly Module Event Format**:
```javascript
{
    timestamp: "2024-01-15T10:30:45Z",
    module: "WebSocketManager",
    event_type: "operation",
    message: "Just locked 5 certificates 🔒",
    context: {
        operation: "certificate_lock",
        count: 5,
        correlation_id: "req_abc123"
    },
    emoji: "🔒",
    severity: "info"
}
```

### Dashboard Layout
**Left Side**: Performance Charts
- **Response Time**: Blue line, left Y-axis (ms)
- **Error Rate**: Red line, right Y-axis (%)
- **Throughput**: Green line, right Y-axis (ops/sec)

**Right Side**: Live Activity Feed
- **Real-time observations** from Beastly Modules
- **Contextual emojis** and timestamps
- **Correlation markers** linking events to metric changes

## Implementation Components

### Core Components
1. **PerformanceChartInitializer** - Structured metrics visualization
2. **ObservationStreamHandler** - Real-time unstructured data feed
3. **ActivityFeedRenderer** - Live observation display with emojis
4. **CorrelationEngine** - Links events to metric changes

### Beastly Module Integration
**Automatic Data Collection**:
- All ReflectiveModule instances automatically emit structured metrics
- Observability streams capture unstructured events and state changes
- No additional instrumentation needed - leverage existing Beastly powers

### Dashboard Layout
**Split-Screen Design**:
```
┌─────────────────┬─────────────────┐
│  Performance    │  Live Activity  │
│  Charts         │  Feed           │
│  📊 Metrics     │  🔒 Just locked │
│                 │  5 certificates │
│                 │  ⚡ WebSocket   │
│                 │  reconnected    │
└─────────────────┴─────────────────┘
```

## Technical Implementation

### Data Sources
**Structured Metrics** (existing):
- `/api/dashboard/all-data` endpoint
- Prometheus metrics from Beastly Modules
- Health check responses

**Unstructured Observations** (new):
- ReflectiveModule event streams
- WebSocket connections for real-time updates
- Structured logging with correlation IDs

**Distributed Traces** (opportunistic enhancement):
- Jaeger trace spans for complete request flow visibility
- OpenTelemetry instrumentation across all components
- Trace correlation with observations and metrics
- Deployment process tracing for systematic debugging

### Real-time Updates
**Triple Update Streams**:
- **Charts**: 5-second polling for metrics
- **Activity Feed**: WebSocket/SSE for instant observations
- **Distributed Traces**: Jaeger spans for complete request flow
- **Correlation**: Link events, metrics, and traces with timestamps and correlation IDs

### Brownfield Safety
- Isolated error handling for each component
- Graceful degradation if observation stream fails
- Existing charts continue working independently

## Success Metrics

✅ **Living Dashboard**: Shows metrics and real-time activity with correlation
✅ **Automatic Observations**: Beastly Modules emit observations via `emit_observation()` method
✅ **Contextual Correlation**: Events and metrics linked with visual indicators via CorrelationEngine
✅ **Dynamic Content**: Dashboard reflects "what just happened" in real-time
✅ **Emoji Integration**: Visual context through emoji annotations in activity feed
✅ **WebSocket Integration**: Real-time observation streaming via `/ws/observations` endpoint
✅ **HTTP API Fallback**: Polling support via `/api/observations/recent` endpoint
✅ **Brownfield Success**: All existing functionality preserved and enhanced

## Implementation Status

**Phase 1: Core Performance Charts** ✅ COMPLETED
- PerformanceChartInitializer implemented and working
- Dual Y-axis configuration for response time vs rates
- Brownfield safety with comprehensive error handling

**Phase 2: Living Observatory Dashboard** ✅ COMPLETED  
- ObservationStreamHandler for real-time WebSocket connections
- ActivityFeedRenderer for emoji-rich event display
- CorrelationEngine for event-metric correlation
- Split-screen dashboard layout implemented
- Beastly Module observation emission integrated
- End-to-end testing completed

**Phase 3: Distributed Tracing** ⏸️ SKIPPED (Opportunistic Enhancement)
- Marked as optional enhancement for future implementation
- Core Living Observatory functionality is complete without tracing