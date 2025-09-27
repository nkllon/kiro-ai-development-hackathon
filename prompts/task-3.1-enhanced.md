# Task 3.1: WebSocket Health Monitoring Framework

## Ontological Context (22 Dimensions)
- **Problem Taxonomy**: Need real-time visibility into WebSocket connection health
- **Infrastructure**: Monitoring layer across all WebSocket endpoints
- **Solution Architecture**: Comprehensive health monitoring with metrics collection
- **Performance**: <1ms monitoring overhead, real-time metrics
- **Monitoring**: Connection status, latency, throughput, error rates
- **Temporal**: Real-time monitoring with historical data retention
- **Data Management**: Time-series metrics, aggregation, retention policies

## Task Requirements
Write WebSocketHealthMonitor class with metrics collection, create real-time connection status tracking, implement performance metrics aggregation (latency, throughput).

**Requirements Coverage**: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6

## Implementation Instructions

**CRITICAL LOGGING REQUIREMENTS:**
- Log ALL actions in JSON format to stdout
- Use format: `{"timestamp": "ISO8601", "task": "3.1", "action": "description", "status": "in_progress|completed|error", "details": {...}}`
- Log all metrics collection, health status changes, performance data
- Final log: `{"task": "3.1", "status": "completed", "summary": "Health monitoring implemented"}`

**File Structure to Create:**
```
src/beast_mode/observatory/monitoring/
├── __init__.py
├── health_monitor.py
├── metrics_collector.py
├── connection_tracker.py
├── performance_analyzer.py
└── alert_manager.py

tests/unit/monitoring/
├── test_health_monitor.py
├── test_metrics_collector.py
├── test_connection_tracker.py
└── test_performance_analyzer.py
```

**Core Implementation:**

```python
class WebSocketHealthMonitor:
    def __init__(self):
        self.metrics = {
            'websocket_connections_active': 0,
            'websocket_connection_failures': 0,
            'websocket_message_latency_ms': [],
            'websocket_throughput_msgs_per_sec': 0,
            'websocket_error_rate': 0.0
        }
        self.connection_tracker = ConnectionTracker()
        self.performance_analyzer = PerformanceAnalyzer()
        
    async def monitor_connection(self, endpoint: str, websocket)
    async def record_message_sent(self, endpoint: str, timestamp: float)
    async def record_message_received(self, endpoint: str, timestamp: float)
    def get_health_status(self, endpoint: str) -> HealthStatus
    def get_performance_metrics(self) -> Dict[str, Any]
```

**Metrics to Track:**
- Connection count (active, failed, total)
- Message latency (min, max, avg, p95, p99)
- Throughput (messages/second, bytes/second)
- Error rates (connection failures, message failures)
- Connection duration and stability
- Endpoint-specific health scores

**Health Status Levels:**
- HEALTHY: All metrics within normal ranges
- DEGRADED: Some metrics showing issues
- CRITICAL: Major issues affecting functionality
- UNKNOWN: Insufficient data for assessment

**Performance Analysis:**
- Real-time latency calculation
- Throughput measurement and trending
- Error rate calculation and alerting
- Connection quality scoring
- Historical performance comparison

Begin implementation with focus on minimal overhead and accurate metrics collection.