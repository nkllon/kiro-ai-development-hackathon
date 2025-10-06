# Observatory Server Management

## Overview

The Beast Mode Observatory server now includes comprehensive daemon management with proper process control, logging, and developer-friendly operational commands.

## Server Management Commands

### Basic Operations

```bash
# Start the Observatory server
make dashboard-up
# or simply
make dashboard

# Stop the Observatory server
make dashboard-down

# Restart the Observatory server (loads latest code)
make dashboard-restart

# Check server status
make dashboard-status
```

### Development & Monitoring

```bash
# Start in development mode (foreground, stops with Ctrl+C)
make dashboard-dev

# View server logs
make dashboard-logs

# Follow logs in real-time
make dashboard-logs-follow
```

## Observatory Features

### 🚨 Anomaly Detection System
- **Baseline Calculation**: Automatic statistical baselines from historical metrics
- **Threshold Detection**: Immediate alerts for health, cost, error rate, and response time
- **ML Detection**: Isolation Forest algorithm for pattern anomaly detection
- **Classification**: Intelligent severity scoring (LOW/MEDIUM/HIGH/CRITICAL)

### 📊 Real-time Dashboard
- **Live Analytics**: Current window metrics with coordination health
- **Anomaly Alerts**: Visual alerts with interactive management
- **Research Theme**: Multi-agent coordination research interface
- **Emoji Rain**: Delightful celebration system for events

### 🔗 API Endpoints

#### Core Observatory
- `GET /health` - Server health check
- `GET /api/observatory/status` - Observatory status and metrics
- `GET /` - Main dashboard interface

#### Anomaly Detection
- `GET /api/anomalies/active` - Active anomalies and stats
- `GET /api/anomalies/stats` - Detection performance statistics
- `GET /api/anomalies/health` - Anomaly detection engine health
- `POST /api/anomalies/resolve/{id}` - Manually resolve anomaly
- `POST /api/anomalies/false-positive/{id}` - Mark false positive

#### Analytics & Monitoring
- `GET /api/analytics/current` - Current analytics data
- `GET /api/metrics/components` - Discovered Beast Mode components
- `GET /api/costs/overview` - LLM cost overview and metrics

#### WebSocket Endpoints
- `WS /ws/emoji-rain` - Real-time emoji rain updates
- `WS /ws/observatory` - Observatory status updates
- `WS /ws/anomalies` - Real-time anomaly alerts

## Process Management

### Daemon Features
- **PID Files**: Proper process tracking in `var/run/observatory.pid`
- **Log Files**: Structured logging in `var/log/observatory.log`
- **Graceful Shutdown**: SIGTERM handling with timeout fallback
- **Auto-restart**: Development-friendly restart with code reload

### Directory Structure
```
var/
├── run/
│   └── observatory.pid    # Process ID file
└── log/
    └── observatory.log    # Server logs
```

### Log Management
- Startup/shutdown events are logged with timestamps
- Application logs include debug info for troubleshooting
- Real-time log following available with `make dashboard-logs-follow`

## Development Workflow

### Quick Start
```bash
# Start the server
make dashboard

# Check it's running
make dashboard-status

# View the dashboard
open http://localhost:8080

# Follow logs for debugging
make dashboard-logs-follow
```

### Code Development
```bash
# Make changes to Observatory code
vim src/beast_mode/observatory/

# Restart to load changes
make dashboard-restart

# Verify changes
curl http://localhost:8080/api/anomalies/active
```

### Troubleshooting
```bash
# Check server status
make dashboard-status

# View recent logs
make dashboard-logs

# Stop and start fresh
make dashboard-down
make dashboard-up
```

## Configuration

The Observatory server automatically configures itself with sensible defaults:
- **Host**: 0.0.0.0 (accessible from network)
- **Port**: 8080
- **Redis**: Connects to local Redis instance
- **Anomaly Detection**: Threshold-based enabled by default
- **ML Detection**: Disabled by default (enable in config)

## Integration with Beast Mode Framework

The Observatory server integrates seamlessly with the Beast Mode framework:
- **Metrics Collection**: Discovers and monitors Beast Mode components
- **Cost Tracking**: Monitors LLM API usage and costs
- **Analytics Engine**: Real-time coordination analysis
- **PDCA Integration**: Supports Plan-Do-Check-Act workflow monitoring

## Security & Production Notes

- Server binds to all interfaces (0.0.0.0) for development convenience
- In production, configure firewall rules appropriately
- Logs may contain sensitive debug information
- API endpoints are currently open - add authentication as needed
- WebSocket connections are unlimited - consider rate limiting

## Architecture

The Observatory server consists of:

1. **FastAPI Server** (`server.py`) - HTTP/WebSocket endpoints
2. **Observatory Core** (`core.py`) - Component orchestration
3. **Analytics Engine** (`analytics_engine.py`) - Real-time analysis
4. **Anomaly Detection** (`anomaly_detection.py`) - Pattern detection
5. **Metrics Collector** (`metrics_collector.py`) - Component discovery
6. **Cost Tracker** (`llm_cost_tracker.py`) - LLM cost monitoring
7. **Emoji Rain** (`emoji_rain.py`) - Celebration system

All components start automatically and are managed by the Observatory Core with proper error handling and graceful degradation.