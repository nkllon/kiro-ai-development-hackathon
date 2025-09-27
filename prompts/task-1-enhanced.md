# Task 1: WebSocket Tunnel Configuration and Validation Framework

## Ontological Context (22 Dimensions)
- **Problem Taxonomy**: Tunnel configuration lacks WebSocket proxy settings
- **Infrastructure**: Cloudflare tunnel (cloudflared) process configuration
- **Solution Architecture**: Immediate fix through configuration update
- **Risk Assessment**: Configuration changes may disrupt HTTP traffic
- **Constraints**: 2-hour implementation, existing Cloudflare plan
- **Performance**: Must maintain <100ms latency
- **Security**: TLS 1.3 compliance, no security regression
- **Cost**: Zero additional costs, use existing features
- **Dependencies**: cloudflared version 2025.9.1+
- **Scalability**: Must support multiple concurrent connections
- **Operations**: Backup/rollback procedures required
- **Compliance**: Audit trail for configuration changes

## Task Requirements
Create tunnel configuration validation utilities, implement cloudflared version compatibility checks, write configuration backup and rollback mechanisms.

**Requirements Coverage**: 2.1, 2.2, 2.3, 2.4, 2.5

## Implementation Instructions

**CRITICAL LOGGING REQUIREMENTS:**
- Log ALL actions in JSON format to stdout
- Use this exact format: `{"timestamp": "ISO8601", "task": "1", "action": "description", "status": "in_progress|completed|error", "details": {...}}`
- Log every file creation, modification, test execution
- Include error details and stack traces in JSON
- Final log entry must be: `{"task": "1", "status": "completed", "summary": "brief description"}`

**File Structure to Create:**
```
src/beast_mode/observatory/tunnel/
├── __init__.py
├── config_manager.py
├── validator.py
├── backup_manager.py
└── version_checker.py

tests/unit/tunnel/
├── test_config_manager.py
├── test_validator.py
├── test_backup_manager.py
└── test_version_checker.py
```

**Core Components:**
1. **ConfigManager**: Manage cloudflared configuration with WebSocket support
2. **Validator**: Validate tunnel configuration syntax and WebSocket settings
3. **BackupManager**: Backup/restore configuration with versioning
4. **VersionChecker**: Verify cloudflared version compatibility

**WebSocket Configuration Template:**
```yaml
tunnel: observatory
credentials-file: /path/to/credentials.json
ingress:
  - hostname: observatory.nkllon.com
    service: http://localhost:8888
    originRequest:
      httpHostHeader: observatory.nkllon.com
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 10
      keepAliveTimeout: 90s
      proxyType: ""  # Enable WebSocket upgrade
  - service: http_status:404
```

**Success Criteria:**
- Configuration validation passes for WebSocket settings
- Backup/restore functionality works correctly
- Version compatibility check identifies supported cloudflared versions
- All tests pass with >90% coverage
- JSON logs capture all operations

**Cross-Cutting Concerns:**
- Security: Validate configuration doesn't introduce vulnerabilities
- Performance: Configuration optimized for <100ms latency
- Reliability: Robust error handling and recovery
- Maintainability: Clear code structure and documentation

Begin implementation immediately. Log every action in JSON format.