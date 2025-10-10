# Design Document

## Overview

The Prometheus monitoring system repair implements a daemon-based architecture where monitoring runs as a separate, persistent service rather than embedded instances within application processes. This follows standard Unix daemon patterns with PID file management, proper service lifecycle, and centralized metrics collection. The daemon starts with the IDE/development environment and provides monitoring services to all components through a unified interface.

## Architecture

### Daemon-Based Monitoring Service

The monitoring system runs as a standalone daemon process (`prometheus-monitor-daemon`) that:
- Starts automatically with the development environment (IDE startup, docker-compose, etc.)
- Maintains a PID file for process management
- Provides a stable metrics endpoint on a reserved port
- Accepts metric registration from client processes via IPC or HTTP API
- Handles its own lifecycle independently of client applications

### Service Discovery and Registration

Client processes discover and register with the monitoring daemon through:
- Service discovery via well-known socket/port
- Registration API for metric definitions
- Health check endpoints for service availability
- Graceful fallback when daemon is unavailable

## Components and Interfaces

### 1. Prometheus Monitor Daemon (`prometheus-monitor-daemon`)

**Responsibilities:**
- Run as persistent background service
- Manage Prometheus HTTP server and metrics endpoint
- Accept metric registrations from client processes
- Maintain service health and availability
- Handle graceful shutdown and restart

**Interfaces:**
```python
class PrometheusMonitorDaemon:
    def start_daemon(self, port: int = 8000, pid_file: str = "/tmp/prometheus-monitor.pid")
    def stop_daemon(self, pid_file: str = "/tmp/prometheus-monitor.pid")
    def register_metrics_endpoint(self, client_id: str, metrics_config: Dict)
    def health_check(self) -> ServiceStatus
    def reload_config(self)
```

**Configuration:**
- Default metrics port: 8000
- PID file location: `/tmp/prometheus-monitor.pid` (configurable)
- Service socket: `/tmp/prometheus-monitor.sock`
- Log file: `/tmp/prometheus-monitor.log`

### 2. Monitoring Client Library (`MonitoringClient`)

**Responsibilities:**
- Discover running monitoring daemon
- Register application metrics with daemon
- Provide fallback behavior when daemon unavailable
- Abstract daemon communication from application code

**Interfaces:**
```python
class MonitoringClient:
    def __init__(self, client_id: str)
    def register_counter(self, name: str, description: str, labels: List[str] = None)
    def register_gauge(self, name: str, description: str, labels: List[str] = None)
    def register_histogram(self, name: str, description: str, buckets: List[float] = None)
    def increment_counter(self, name: str, labels: Dict[str, str] = None, value: float = 1)
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None)
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None)
    def is_daemon_available(self) -> bool
```

### 3. Service Management Integration

**Docker Compose Integration:**
```yaml
services:
  prometheus-monitor:
    build: .
    command: ["python", "-m", "src.beast_mode.monitoring.daemon", "--start"]
    ports:
      - "8000:8000"
    volumes:
      - /tmp:/tmp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-m", "src.beast_mode.monitoring.daemon", "--health-check"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**IDE Integration:**
- Start daemon automatically when IDE/development environment starts
- Register daemon shutdown with IDE exit hooks
- Provide IDE status indicator for monitoring service health

### 4. Process Management

**PID File Management:**
```python
class DaemonManager:
    def write_pid_file(self, pid_file: str)
    def read_pid_file(self, pid_file: str) -> Optional[int]
    def is_daemon_running(self, pid_file: str) -> bool
    def kill_daemon(self, pid_file: str, signal: int = signal.SIGTERM)
    def cleanup_stale_pid(self, pid_file: str)
```

**Service Commands:**
- `prometheus-monitor-daemon --start` - Start daemon
- `prometheus-monitor-daemon --stop` - Stop daemon
- `prometheus-monitor-daemon --restart` - Restart daemon
- `prometheus-monitor-daemon --status` - Check daemon status
- `prometheus-monitor-daemon --health-check` - Health check for monitoring

## Data Models

### Metric Registration Model
```python
@dataclass
class MetricRegistration:
    client_id: str
    metric_name: str
    metric_type: str  # counter, gauge, histogram
    description: str
    labels: List[str]
    buckets: Optional[List[float]] = None  # for histograms
    
@dataclass
class MetricUpdate:
    client_id: str
    metric_name: str
    operation: str  # increment, set, observe
    value: float
    labels: Dict[str, str]
    timestamp: datetime
```

### Service Status Model
```python
@dataclass
class ServiceStatus:
    is_running: bool
    pid: Optional[int]
    port: int
    uptime: timedelta
    metrics_endpoint: str
    registered_clients: List[str]
    total_metrics: int
    last_activity: datetime
```

## Error Handling

### Daemon Startup Failures
- Port already in use: Try alternative ports (8001-8010)
- Permission denied: Provide clear error message with resolution steps
- PID file conflicts: Check for stale processes and cleanup
- Configuration errors: Validate config and provide specific error messages

### Client Connection Failures
- Daemon not running: Log warning and continue with null monitoring
- Network errors: Retry with exponential backoff
- Registration failures: Cache metrics locally and retry
- Timeout errors: Use circuit breaker pattern

### Service Recovery
- Automatic restart on crash (via systemd/docker restart policies)
- Graceful degradation when daemon unavailable
- Client reconnection when daemon recovers
- Metric data preservation during restarts

## Testing Strategy

### Unit Tests
- Daemon lifecycle management (start, stop, restart)
- PID file operations and cleanup
- Metric registration and updates
- Client library functionality
- Error handling and edge cases

### Integration Tests
- End-to-end daemon startup and client registration
- Docker compose service integration
- IDE integration and lifecycle management
- Service discovery and failover scenarios
- Performance under load (multiple clients, high metric volume)

### System Tests
- Full development environment integration
- Monitoring across multiple Beast Mode components
- Service restart and recovery scenarios
- Resource usage and performance benchmarks
- Log analysis and debugging capabilities

## Migration Strategy

### Phase 1: Daemon Implementation
1. Implement `PrometheusMonitorDaemon` with basic functionality
2. Create `MonitoringClient` library with daemon communication
3. Add service management scripts and configuration
4. Implement PID file management and process control

### Phase 2: Integration and Testing
1. Integrate daemon with docker-compose and IDE startup
2. Migrate existing monitoring code to use `MonitoringClient`
3. Add comprehensive testing and error handling
4. Performance testing and optimization

### Phase 3: Deployment and Monitoring
1. Deploy daemon-based monitoring to development environment
2. Monitor service health and performance
3. Gather feedback and iterate on design
4. Document operational procedures and troubleshooting

### Backward Compatibility
- Existing `PrometheusExporter` class becomes a wrapper around `MonitoringClient`
- Legacy monitoring calls automatically route to daemon
- Gradual migration path with deprecation warnings
- Fallback to embedded monitoring if daemon unavailable (with warnings)

## Operational Considerations

### Service Management
- Use systemd service files for production deployment
- Docker health checks for containerized environments
- Log rotation and management for daemon logs
- Monitoring of the monitoring service itself

### Security
- Restrict daemon socket permissions to development user
- Validate client registrations to prevent metric pollution
- Rate limiting for metric updates to prevent abuse
- Secure communication between clients and daemon

### Performance
- Efficient metric storage and aggregation in daemon
- Batch metric updates to reduce IPC overhead
- Memory management for long-running daemon process
- Configurable metric retention and cleanup policies