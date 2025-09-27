# WebSocket Fix Monitoring Agent

A comprehensive monitoring system for overseeing WebSocket infrastructure fix deployment phases with real-time monitoring, timeout detection, auto-remediation, and detailed status reporting.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Required packages: `psutil`, `pyyaml`, `requests`
- WebSocket fix agent scripts in place

### Installation
```bash
# Install dependencies
pip install psutil pyyaml requests

# Make launcher executable
chmod +x scripts/launch_websocket_fix_monitoring.sh
```

### Basic Usage
```bash
# Launch monitoring agent
./scripts/launch_websocket_fix_monitoring.sh

# Or run directly
python3 scripts/websocket_fix_monitoring_agent.py
```

## 📋 What It Monitors

### Phase 1: WebSocket Deployment Fix
- **Script**: `scripts/deploy_websocket_fix.py`
- **Purpose**: Deploy WebSocket infrastructure fixes
- **Health Checks**: Cloudflare tunnel, WebSocket connectivity
- **Timeout**: 30 minutes

### Phase 2: SSL/TLS Configuration
- **Script**: `scripts/ssl_tls_full_strict_deployment.sh`
- **Purpose**: Deploy SSL/TLS security configurations
- **Health Checks**: SSL certificate validation, HTTPS connectivity
- **Timeout**: 45 minutes
- **Dependencies**: Phase 1

### Phase 3: Production WebSocket Testing
- **Script**: `scripts/production_websocket_tester.py`
- **Purpose**: Validate production WebSocket functionality
- **Health Checks**: Production WebSocket endpoint health
- **Timeout**: 60 minutes
- **Dependencies**: Phase 1, Phase 2

## 🔧 Configuration

### Default Configuration
The monitoring agent uses `websocket_fix_monitoring_config.yml` for configuration:

```yaml
agents:
  phase_1:
    script_path: "scripts/deploy_websocket_fix.py"
    timeout_minutes: 30
    health_check_interval: 60
    stuck_threshold_minutes: 10
    max_restart_attempts: 3
    auto_remediation: true
    critical: true
```

### Key Configuration Options
- `timeout_minutes`: Maximum execution time before timeout
- `health_check_interval`: Seconds between health checks
- `stuck_threshold_minutes`: Time without activity before considering stuck
- `max_restart_attempts`: Maximum number of restart attempts
- `dependencies`: List of phases that must complete first
- `auto_remediation`: Enable automatic remediation actions

## 📊 Monitoring Features

### Real-Time Monitoring
- **Process Tracking**: Monitors PID, CPU usage, memory consumption
- **Status Detection**: Tracks agent status (running, completed, failed, etc.)
- **Health Validation**: Performs phase-specific health checks
- **Stuck Detection**: Identifies unresponsive agents

### Auto-Remediation
- **Automatic Restart**: Restarts failed or stuck agents
- **Timeout Handling**: Kills timed-out agents and restarts them
- **Escalation**: Alerts for human intervention when needed
- **Dependency Management**: Ensures proper phase ordering

### Status Reporting
- **5-Minute Reports**: Comprehensive status reports every 5 minutes
- **Real-Time Console**: Live status updates in terminal
- **Detailed Logging**: Structured JSON logs for analysis
- **Final Summary**: Complete session report at completion

## 📈 Status Report Example

```
================================================================================
WEBSOCKET FIX MONITORING AGENT - STATUS REPORT
================================================================================
Timestamp: 2024-01-15 14:30:00
Overall Status: PHASES_IN_PROGRESS

PHASE STATUS:
----------------------------------------
  PHASE_1:
    Status: running
    PID: 12345
    Health Score: 0.85
    Restart Count: 0

  PHASE_2:
    Status: not_started
    PID: None
    Health Score: 0.00
    Restart Count: 0

HEALTH METRICS:
----------------------------------------
  Overall Health Score: 0.43
  Agents Running: 1
  Agents Completed: 0
  Agents Failed: 0
  Total Restarts: 0

RECOMMENDATIONS:
----------------------------------------
  • All agents operating normally

Next Report: 2024-01-15 14:35:00
================================================================================
```

## 🗂️ Log Files

The monitoring agent creates several types of log files:

### Monitoring Logs
- `logs/websocket_fix_monitoring_YYYYMMDD_HHMMSS.log` - Main monitoring log
- `logs/websocket_fix_monitoring_report_YYYYMMDD_HHMMSS.json` - Status reports
- `logs/websocket_fix_monitoring_final_report_YYYYMMDD_HHMMSS.json` - Final summary

### Agent Logs
- `logs/phase_1_output_YYYYMMDD_HHMMSS.log` - Phase 1 standard output
- `logs/phase_1_error_YYYYMMDD_HHMMSS.log` - Phase 1 error output
- Similar files for Phase 2 and Phase 3

## 🧪 Testing

### Run Test Suite
```bash
# Test monitoring agent functionality
python3 scripts/test_websocket_fix_monitoring.py
```

### Test Mode
```bash
# Run in test mode (no actual agent execution)
./scripts/launch_websocket_fix_monitoring.sh --test-mode
```

## 🎛️ Command Line Options

### Basic Options
- `--config`: Path to configuration file
- `--phases`: Specify which phases to monitor
- `--test-mode`: Run in test mode without starting actual agents

### Examples
```bash
# Monitor specific phases only
./scripts/launch_websocket_fix_monitoring.sh --phases phase_1 phase_2

# Use custom configuration
python3 scripts/websocket_fix_monitoring_agent.py --config custom_config.yml

# Test mode
python3 scripts/websocket_fix_monitoring_agent.py --test-mode
```

## 🔍 Troubleshooting

### Common Issues

#### Agent Won't Start
- Check script path in configuration
- Verify dependencies are met
- Check file permissions

#### Health Checks Failing
- Verify network connectivity
- Check service dependencies
- Review health check timeouts

#### Excessive Restarts
- Review agent logs for errors
- Check resource constraints
- Adjust timeout and threshold settings

### Debug Mode
Enable debug logging in configuration:
```yaml
monitoring:
  log_level: "DEBUG"
```

### Manual Intervention
If auto-remediation fails:
1. Check agent log files for specific errors
2. Manually restart problematic agents
3. Adjust configuration parameters
4. Escalate to system administrators

## 📚 Documentation

- [Complete Documentation](WEBSOCKET_FIX_MONITORING_AGENT_DOCUMENTATION.md) - Comprehensive technical documentation
- [Configuration Reference](websocket_fix_monitoring_config.yml) - Configuration file reference
- [Test Suite](scripts/test_websocket_fix_monitoring.py) - Test validation script

## 🏗️ Architecture

### Components
- **WebSocketFixMonitoringAgent**: Main monitoring orchestrator
- **AgentProcess**: Tracks individual agent state and metrics
- **AgentConfig**: Configuration for each agent phase
- **MonitoringReport**: Comprehensive status reporting structure
- **Health Validators**: Phase-specific health check implementations

### Monitoring Flow
1. **Initialization**: Load configuration and initialize agents
2. **Dependency Check**: Verify phase dependencies are met
3. **Agent Launch**: Start agents in proper order
4. **Continuous Monitoring**: Track process status and health
5. **Auto-Remediation**: Handle failures and stuck processes
6. **Status Reporting**: Generate regular comprehensive reports
7. **Completion**: Generate final summary report

## 🔒 Security Considerations

- **Process Isolation**: Agents run in separate processes
- **Limited Access**: Restricted system resource access
- **Secure Execution**: Safe subprocess execution
- **Log Security**: Sensitive information filtered from logs
- **Configuration Validation**: YAML configuration validation

## 🚀 Future Enhancements

### Planned Features
- Web-based monitoring dashboard
- Real-time alerting via Discord/Slack
- Historical trend analysis
- Machine learning-based anomaly detection

### Integration Opportunities
- Prometheus metrics export
- Grafana dashboard integration
- CI/CD pipeline integration
- Automated rollback capabilities

## 📞 Support

For issues or questions:
1. Check the log files for detailed error information
2. Review the configuration file for proper settings
3. Run the test suite to validate functionality
4. Consult the comprehensive documentation

---

**WebSocket Fix Monitoring Agent** - Ensuring reliable WebSocket infrastructure deployment with comprehensive monitoring and auto-remediation capabilities.