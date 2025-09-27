# Task 7.1: Cloudflare Tunnel Configuration Management

## Ontological Context (22 Dimensions)
- **Infrastructure**: Cloudflare tunnel configuration with WebSocket support
- **Operations**: Configuration versioning, backup, rollback procedures
- **Risk Assessment**: Configuration changes may disrupt service
- **Compliance**: Audit trail for all configuration changes
- **Reliability**: Robust configuration validation and testing

## Task Requirements
Write tunnel configuration generation and validation, implement WebSocket-specific ingress rule creation, create configuration versioning and rollback system.

**Requirements Coverage**: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7

## Implementation Instructions

**CRITICAL LOGGING REQUIREMENTS:**
- Log ALL actions in JSON format to stdout
- Use format: `{"timestamp": "ISO8601", "task": "7.1", "action": "description", "status": "in_progress|completed|error", "details": {...}}`
- Log configuration changes, validation results, backup operations
- Final log: `{"task": "7.1", "status": "completed", "summary": "Tunnel configuration management implemented"}`

**File Structure to Create:**
```
src/beast_mode/observatory/tunnel/
├── config_generator.py
├── websocket_ingress.py
├── config_validator.py
├── version_manager.py
└── rollback_manager.py

tests/unit/tunnel/
├── test_config_generator.py
├── test_websocket_ingress.py
├── test_config_validator.py
└── test_version_manager.py
```

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

**Core Implementation:**

```python
class TunnelConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.version_manager = VersionManager()
        self.validator = ConfigValidator()
        
    def generate_websocket_config(self) -> Dict[str, Any]
    def validate_config(self, config: Dict) -> ValidationResult
    def backup_current_config(self) -> str
    def apply_config(self, config: Dict) -> bool
    def rollback_config(self, version: str) -> bool
```

Begin implementation with focus on safe configuration management and WebSocket support.