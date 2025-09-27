# Task 2.1: WebSocket Connection Manager with Retry Logic

## Ontological Context (22 Dimensions)
- **Problem Taxonomy**: WebSocket connections fail through Cloudflare tunnel
- **Infrastructure**: Browser → CF Edge → CF Tunnel → Observatory Server
- **Solution Architecture**: Intelligent connection management with fallback
- **Risk Assessment**: Connection failures cascade to service outage
- **Constraints**: Must work with existing FastAPI WebSocket endpoints
- **Performance**: <100ms message round-trip, >1000 msg/sec throughput
- **Security**: JWT authentication, origin validation, rate limiting
- **Scalability**: Support multiple concurrent connections per user
- **Temporal**: <60s recovery time, exponential backoff retry

## Task Requirements
Write WebSocketManager class with connection pooling, implement exponential backoff retry mechanism, create connection state tracking and health monitoring.

**Requirements Coverage**: 1.1, 1.2, 1.3, 1.4, 1.5

## Implementation Instructions

**CRITICAL LOGGING REQUIREMENTS:**
- Log ALL actions in JSON format to stdout
- Use format: `{"timestamp": "ISO8601", "task": "2.1", "action": "description", "status": "in_progress|completed|error", "details": {...}}`
- Log connection attempts, failures, retries, state changes
- Include WebSocket endpoint URLs, error codes, retry counts
- Final log: `{"task": "2.1", "status": "completed", "summary": "WebSocket manager implemented"}`

**File Structure to Create:**
```
src/beast_mode/observatory/websocket/
├── __init__.py
├── manager.py
├── connection.py
├── retry_strategy.py
├── health_monitor.py
└── exceptions.py

tests/unit/websocket/
├── test_manager.py
├── test_connection.py
├── test_retry_strategy.py
└── test_health_monitor.py
```

**Core Components:**

1. **WebSocketManager Class:**
```python
class WebSocketManager:
    def __init__(self, endpoints: List[str]):
        self.endpoints = endpoints
        self.connections = {}  # endpoint -> WebSocketConnection
        self.retry_strategies = {}  # endpoint -> RetryStrategy
        self.health_monitor = HealthMonitor()
    
    async def connect_websocket(self, endpoint: str) -> WebSocket
    async def disconnect_websocket(self, endpoint: str)
    async def send_message(self, endpoint: str, message: dict)
    async def handle_connection_failure(self, endpoint: str, error: Exception)
    def get_connection_status(self, endpoint: str) -> ConnectionStatus
```

2. **RetryStrategy Class:**
```python
class ExponentialBackoffRetry:
    def __init__(self, base_delay=1.0, max_delay=60.0, multiplier=2.0, jitter=True):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter = jitter
        self.attempt_count = 0
    
    def calculate_delay(self) -> float
    def should_retry(self, error: Exception) -> bool
    def reset(self)
```

3. **WebSocket Endpoints to Support:**
- `/ws/emoji-rain`
- `/ws/observatory` 
- `/ws/anomalies`
- `/ws/doctor-status`

**Connection State Management:**
```python
@dataclass
class ConnectionState:
    endpoint: str
    status: ConnectionStatus  # CONNECTED, DISCONNECTED, CONNECTING, FAILED
    connection_time: Optional[datetime]
    last_message_time: Optional[datetime]
    failure_count: int
    last_error: Optional[str]
```

**Health Monitoring:**
- Track connection uptime/downtime
- Monitor message latency
- Detect connection quality degradation
- Trigger reconnection when needed

**Error Handling:**
- Connection refused (tunnel issue)
- Upgrade failed (protocol issue)
- Timeout (network issue)
- Authentication failed
- Rate limiting

**Success Criteria:**
- WebSocket connections establish successfully
- Retry logic works with exponential backoff
- Connection state accurately tracked
- Health monitoring detects issues
- All tests pass with >90% coverage
- JSON logs capture all connection events

Begin implementation. Focus on robust connection management with comprehensive error handling.