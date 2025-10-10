# WebSocket Fix Monitoring Agent Documentation

## Overview

The WebSocket Fix Monitoring Agent is a comprehensive monitoring system designed to oversee the execution of three WebSocket fix agents (Phase 1, Phase 2, Phase 3). It provides real-time monitoring, timeout detection, auto-remediation, and regular status reporting until all phases complete.

## Features

### Core Monitoring Capabilities
- **Real-time Process Monitoring**: Tracks running processes, CPU usage, memory consumption, and process responsiveness
- **Timeout Detection**: Automatically detects when agents exceed their configured timeout limits
- **Stuck Process Detection**: Identifies agents that appear to be stuck or unresponsive
- **Health Check Validation**: Performs phase-specific health checks on WebSocket infrastructure
- **Auto-remediation**: Automatically restarts, kills, or escalates problematic agents

### Status Reporting
- **5-minute Status Reports**: Generates comprehensive status reports every 5 minutes
- **Real-time Console Output**: Provides live status updates in the console
- **Detailed Logging**: Maintains structured JSON logs for analysis
- **Final Comprehensive Report**: Generates a complete summary at the end of monitoring

### Agent Management
- **Dependency Management**: Ensures agents start in the correct order based on dependencies
- **Restart Logic**: Automatically restarts failed or stuck agents with configurable limits
- **Graceful Termination**: Properly terminates agents when monitoring stops
- **Signal Handling**: Responds to SIGINT and SIGTERM for clean shutdown

## Architecture

### Components

1. **WebSocketFixMonitoringAgent**: Main monitoring orchestrator
2. **AgentProcess**: Tracks individual agent state and metrics
3. **AgentConfig**: Configuration for each agent phase
4. **MonitoringReport**: Comprehensive status reporting structure
5. **Health Validators**: Phase-specific health check implementations

### Monitoring Phases

#### Phase 1: WebSocket Deployment Fix
- **Script**: `scripts/deploy_websocket_fix.py`
- **Purpose**: Deploy WebSocket infrastructure fixes
- **Health Checks**: Cloudflare tunnel status, WebSocket endpoint connectivity
- **Timeout**: 30 minutes
- **Dependencies**: None

#### Phase 2: SSL/TLS Configuration
- **Script**: `scripts/ssl_tls_full_strict_deployment.sh`
- **Purpose**: Deploy SSL/TLS security configurations
- **Health Checks**: SSL certificate validation, HTTPS connectivity
- **Timeout**: 45 minutes
- **Dependencies**: Phase 1

#### Phase 3: Production WebSocket Testing
- **Script**: `scripts/production_websocket_tester.py`
- **Purpose**: Validate production WebSocket functionality
- **Health Checks**: Production WebSocket endpoint health, performance metrics
- **Timeout**: 60 minutes
- **Dependencies**: Phase 1, Phase 2

## Configuration

### Configuration File: `websocket_fix_monitoring_config.yml`

```yaml
agents:
  phase_1:
    phase: "phase_1"
    script_path: "scripts/deploy_websocket_fix.py"
    timeout_minutes: 30
    health_check_interval: 60
    stuck_threshold_minutes: 10
    max_restart_attempts: 3
    dependencies: []
    auto_remediation: true
    critical: true

monitoring:
  report_interval_minutes: 5
  health_check_timeout_seconds: 30
  process_check_interval_seconds: 10
  log_level: "INFO"

health_thresholds:
  cpu_usage_percent: 90
  memory_usage_mb: 1000
  health_score_minimum: 0.5
  stuck_detection_count: 3

remediation:
  enable_auto_restart: true
  enable_auto_escalation: true
  escalation_threshold_restarts: 3
  escalation_threshold_health_score: 0.3
```

### Configuration Parameters

#### Agent Configuration
- `script_path`: Path to the agent script to execute
- `timeout_minutes`: Maximum execution time before timeout
- `health_check_interval`: Seconds between health checks
- `stuck_threshold_minutes`: Time without activity before considering stuck
- `max_restart_attempts`: Maximum number of restart attempts
- `dependencies`: List of phases that must complete first
- `auto_remediation`: Enable automatic remediation actions
- `critical`: Whether this phase is critical for overall success

#### Monitoring Configuration
- `report_interval_minutes`: Interval between status reports
- `health_check_timeout_seconds`: Timeout for health check operations
- `process_check_interval_seconds`: Interval for process status checks
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)

#### Health Thresholds
- `cpu_usage_percent`: CPU usage threshold for health degradation
- `memory_usage_mb`: Memory usage threshold in MB
- `health_score_minimum`: Minimum health score before remediation
- `stuck_detection_count`: Number of consecutive stuck detections before action

## Usage

### Basic Usage

```bash
# Launch monitoring agent with default configuration
./scripts/launch_websocket_fix_monitoring.sh

# Or run directly with Python
python3 scripts/websocket_fix_monitoring_agent.py
```

### Advanced Usage

```bash
# Monitor specific phases only
./scripts/launch_websocket_fix_monitoring.sh --phases phase_1 phase_2

# Run in test mode (no actual agent execution)
./scripts/launch_websocket_fix_monitoring.sh --test-mode

# Use custom configuration
python3 scripts/websocket_fix_monitoring_agent.py --config custom_config.yml
```

### Command Line Options

- `--config`: Path to configuration file
- `--phases`: Specify which phases to monitor (phase_1, phase_2, phase_3)
- `--test-mode`: Run in test mode without starting actual agents

## Monitoring Output

### Console Output

The monitoring agent provides real-time console output showing:

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
    Remediation Actions: 

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
  Total Remediation Actions: 0

RECOMMENDATIONS:
----------------------------------------
  • All agents operating normally

Next Report: 2024-01-15 14:35:00
================================================================================
```

### Log Files

The monitoring agent creates several types of log files:

1. **Monitoring Log**: `logs/websocket_fix_monitoring_YYYYMMDD_HHMMSS.log`
   - Structured JSON logs of all monitoring activities
   - Includes process status changes, health checks, remediation actions

2. **Agent Output**: `logs/{phase}_output_YYYYMMDD_HHMMSS.log`
   - Standard output from each agent process

3. **Agent Errors**: `logs/{phase}_error_YYYYMMDD_HHMMSS.log`
   - Error output from each agent process

4. **Status Reports**: `logs/websocket_fix_monitoring_report_YYYYMMDD_HHMMSS.json`
   - Detailed JSON status reports generated every 5 minutes

5. **Final Report**: `logs/websocket_fix_monitoring_final_report_YYYYMMDD_HHMMSS.json`
   - Comprehensive final report with complete session summary

## Agent Status Types

### Status Values
- `NOT_STARTED`: Agent has not been started yet
- `STARTING`: Agent is in the process of starting
- `RUNNING`: Agent is actively running
- `HEALTH_CHECKING`: Agent is undergoing health validation
- `COMPLETED`: Agent has completed successfully
- `FAILED`: Agent has failed
- `TIMEOUT`: Agent has exceeded timeout limit
- `STUCK`: Agent appears to be stuck or unresponsive
- `TERMINATED`: Agent process has been terminated

### Remediation Actions
- `RESTART_AGENT`: Restart the agent process
- `KILL_AND_RESTART`: Force kill and restart the agent
- `SKIP_PHASE`: Skip this phase (non-critical only)
- `ESCALATE`: Escalate to human intervention
- `NO_ACTION`: No remediation action taken

## Health Check System

### Phase-Specific Health Checks

#### Phase 1: WebSocket Deployment
- Cloudflare tunnel process status
- WebSocket endpoint connectivity (`ws://localhost:8888/ws`)
- Tunnel configuration validation

#### Phase 2: SSL/TLS Configuration
- SSL certificate validity
- HTTPS connectivity to production domain
- Certificate chain validation

#### Phase 3: Production WebSocket
- Production WebSocket endpoint health (`wss://observatory.nkllon.com/ws`)
- WebSocket connection performance
- End-to-end functionality validation

### Health Score Calculation

Health scores range from 0.0 (unhealthy) to 1.0 (healthy):

- **Process Health**: Based on CPU usage, memory consumption, responsiveness
- **Phase-Specific Health**: Based on infrastructure-specific checks
- **Overall Score**: Weighted combination of all health factors

## Auto-Remediation System

### Remediation Triggers

1. **Timeout Detection**: Agent exceeds configured timeout
2. **Stuck Process**: Agent shows no activity for threshold period
3. **Health Score Degradation**: Health score falls below minimum threshold
4. **Process Failure**: Agent process terminates unexpectedly

### Remediation Actions

1. **Restart Agent**: Graceful restart of the agent process
2. **Kill and Restart**: Force termination followed by restart
3. **Skip Phase**: Skip non-critical phases that repeatedly fail
4. **Escalation**: Alert for human intervention on critical failures

### Remediation Limits

- Maximum restart attempts per agent (configurable)
- Escalation after exceeding restart limits
- Automatic escalation for critical phases

## Error Handling

### Process Monitoring Errors
- Handles `psutil.NoSuchProcess` exceptions
- Graceful handling of permission errors
- Timeout handling for health checks

### Agent Execution Errors
- Captures agent stdout/stderr to log files
- Handles subprocess creation failures
- Manages process termination errors

### Network and Health Check Errors
- Timeout handling for network operations
- Graceful degradation when health checks fail
- Retry logic for transient failures

## Integration Points

### WebSocket Infrastructure
- Integrates with existing WebSocket health validators
- Uses observatory monitoring components
- Leverages Cloudflare tunnel management

### Logging and Monitoring
- Structured JSON logging for analysis
- Integration with existing log management
- Real-time status broadcasting

### Configuration Management
- YAML-based configuration
- Environment-specific settings
- Runtime configuration updates

## Troubleshooting

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

#### Monitoring Agent Crashes
- Check Python dependencies
- Review configuration file syntax
- Verify log directory permissions

### Debug Mode

Enable debug logging by setting log level to DEBUG in configuration:

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

## Performance Considerations

### Resource Usage
- Monitoring agent uses minimal CPU and memory
- Health checks are throttled to prevent overload
- Log rotation prevents disk space issues

### Scalability
- Configurable check intervals
- Efficient process monitoring
- Minimal impact on monitored agents

### Reliability
- Graceful error handling
- Automatic recovery mechanisms
- Comprehensive logging for analysis

## Security Considerations

### Process Isolation
- Agents run in separate processes
- Limited access to system resources
- Secure subprocess execution

### Log Security
- Sensitive information filtered from logs
- Secure log file permissions
- Audit trail for all actions

### Configuration Security
- YAML configuration validation
- Secure file path handling
- Input sanitization

## Future Enhancements

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

## Support and Maintenance

### Monitoring Agent Updates
- Version tracking in logs
- Backward compatibility considerations
- Configuration migration tools

### Agent Script Updates
- Dynamic script path configuration
- Version compatibility checking
- Automatic script validation

### Performance Optimization
- Continuous monitoring of monitoring overhead
- Optimization of health check intervals
- Resource usage optimization

---

This documentation provides comprehensive information about the WebSocket Fix Monitoring Agent. For additional support or questions, refer to the log files and configuration examples provided.