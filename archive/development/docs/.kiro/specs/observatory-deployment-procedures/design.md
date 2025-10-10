# Observatory Deployment Procedures - Design Document

## Overview

This design document outlines a systematic approach to observatory deployment that addresses the critical gaps in current procedures. The solution provides unified documentation, automated startup procedures, dependency management, comprehensive monitoring, and recovery mechanisms to ensure reliable observatory operations.

The design follows the **observation-first leadership principle** by building upon existing infrastructure rather than creating new systems, and implements **mathematical governance** through explicit dependency ordering and deterministic procedures.

## ADR Conformance Review

### Relevant ADRs Reviewed
- ADR-005: ReflectiveModule Pattern for Universal Observability - ✅ Compliant
- ADR-007: Integration-First Design Strategy - ✅ Compliant  
- ADR-008: Failure Isolation Over Cascade Prevention - ✅ Compliant
- ADR-010: CMS-Based Configuration Management - ✅ Compliant

### Conformance Assessment
- **Infrastructure**: Leverages existing Makefile system and ReflectiveModule patterns
- **Integration**: Builds upon existing Cloudflare tunnel and observatory infrastructure
- **Operations**: Implements failure isolation and systematic recovery procedures
- **Technology**: Uses established Python/shell scripting patterns

## Architecture

### System Components

The observatory deployment system consists of four primary components arranged in a dependency hierarchy:

```
┌─────────────────────────────────────────────────────────────┐
│                    Makefile Interface                       │
│  (observatory-start, observatory-stop, observatory-status)  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Deployment Orchestrator                        │
│         (Python script with ReflectiveModule)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────▼─────────────┐    ┌─────────────────────┐
        │    Observatory Service    │    │   Monitoring Agent  │
        │   (Health endpoints)      │    │  (Status checker)   │
        └─────────────┬─────────────┘    └─────────────────────┘
                      │
        ┌─────────────▼─────────────┐
        │   Cloudflare Tunnel       │
        │  (External access)        │
        └───────────────────────────┘
```

### Dependency Management Strategy

**Mathematical Ordering**: The system enforces a strict DAG (Directed Acyclic Graph) for service dependencies:

1. **Prerequisites** → Observatory Service
2. **Observatory Service** → Cloudflare Tunnel  
3. **Both Services** → Monitoring Agent
4. **All Components** → Status Reporting

This ordering prevents circular dependencies and ensures deterministic startup/shutdown sequences.

## Components and Interfaces

### 1. Deployment Orchestrator

**Location**: `scripts/observatory_deployment_orchestrator.py`

**Purpose**: Central coordination point that manages the entire deployment lifecycle.

**Key Interfaces**:
```python
class ObservatoryDeploymentOrchestrator(ReflectiveModule):
    def start_observatory(self) -> DeploymentResult
    def stop_observatory(self) -> DeploymentResult  
    def get_status(self) -> SystemStatus
    def validate_prerequisites(self) -> ValidationResult
    def recover_from_failure(self, failure_type: str) -> RecoveryResult
```

**Design Rationale**: Inherits from ReflectiveModule to provide automatic health monitoring, Prometheus metrics, and structured logging. This ensures the orchestrator itself is observable and debuggable.

### 2. Service Health Monitor

**Location**: `scripts/observatory_health_monitor.py`

**Purpose**: Continuous monitoring of observatory and tunnel health with automatic recovery triggers.

**Key Interfaces**:
```python
class ObservatoryHealthMonitor(ReflectiveModule):
    def check_observatory_health(self) -> HealthStatus
    def check_tunnel_health(self) -> HealthStatus
    def test_external_access(self) -> AccessibilityStatus
    def trigger_recovery(self, component: str) -> RecoveryResult
```

**Design Rationale**: Separates monitoring concerns from deployment logic, enabling independent scaling and failure isolation per ADR-008.

### 3. Configuration Validator

**Location**: `scripts/observatory_config_validator.py`

**Purpose**: Validates system configuration and detects inconsistencies before deployment.

**Key Interfaces**:
```python
class ObservatoryConfigValidator(ReflectiveModule):
    def validate_tunnel_config(self) -> ValidationResult
    def validate_observatory_config(self) -> ValidationResult
    def detect_port_conflicts(self) -> ConflictReport
    def suggest_fixes(self, issues: List[Issue]) -> FixSuggestions
```

### 4. Documentation Generator

**Location**: `scripts/observatory_docs_generator.py`

**Purpose**: Automatically updates documentation based on current system state and procedures.

**Key Interfaces**:
```python
class ObservatoryDocsGenerator(ReflectiveModule):
    def update_readme(self) -> UpdateResult
    def generate_troubleshooting_guide(self) -> DocumentResult
    def sync_makefile_docs(self) -> SyncResult
```

## Data Models

### System Status Model
```python
@dataclass
class SystemStatus:
    observatory_status: ServiceStatus
    tunnel_status: TunnelStatus
    external_access: AccessibilityStatus
    overall_health: HealthLevel
    last_check: datetime
    issues: List[Issue]
    recovery_suggestions: List[RecoverySuggestion]
```

### Deployment Result Model
```python
@dataclass
class DeploymentResult:
    success: bool
    operation: str
    duration: float
    services_affected: List[str]
    errors: List[Error]
    warnings: List[Warning]
    next_steps: List[str]
```

### Health Status Model
```python
@dataclass
class HealthStatus:
    component: str
    status: Literal["healthy", "degraded", "failed", "unknown"]
    response_time: Optional[float]
    error_message: Optional[str]
    last_success: Optional[datetime]
    metrics: Dict[str, Any]
```

## Error Handling

### Failure Classification

The system categorizes failures into four types with specific recovery strategies:

1. **Configuration Errors**: Invalid settings, missing files, port conflicts
   - **Recovery**: Automatic validation and repair suggestions
   - **Escalation**: Manual intervention required for complex conflicts

2. **Service Failures**: Observatory crashes, unresponsive endpoints
   - **Recovery**: Automatic restart with exponential backoff
   - **Escalation**: Alert operators after 3 failed restart attempts

3. **Network Failures**: Tunnel disconnections, DNS issues, connectivity problems
   - **Recovery**: Automatic reconnection with circuit breaker pattern
   - **Escalation**: Switch to maintenance mode after sustained failures

4. **Resource Exhaustion**: Out of memory, disk space, file descriptors
   - **Recovery**: Graceful degradation and resource cleanup
   - **Escalation**: Immediate operator notification

### Error Recovery Patterns

**Circuit Breaker Implementation**:
```python
class TunnelCircuitBreaker:
    def __init__(self):
        self.failure_count = 0
        self.last_failure = None
        self.state = "closed"  # closed, open, half-open
    
    def call_with_breaker(self, operation):
        if self.state == "open" and self._should_attempt_reset():
            self.state = "half-open"
        
        if self.state == "open":
            raise CircuitBreakerOpenError()
        
        try:
            result = operation()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

**Exponential Backoff for Retries**:
- Initial delay: 1 second
- Maximum delay: 300 seconds (5 minutes)
- Backoff multiplier: 2.0
- Jitter: ±25% to prevent thundering herd

## Testing Strategy

### Unit Testing
- **Coverage Target**: >90% for all deployment orchestrator components
- **Mock Strategy**: Mock external services (Cloudflare API, system processes)
- **Test Categories**: Configuration validation, health checking, error handling

### Integration Testing
- **Local Integration**: Test observatory + tunnel startup sequence
- **Network Integration**: Test external accessibility and tunnel connectivity
- **Failure Simulation**: Inject failures to test recovery procedures

### End-to-End Testing
- **Full Deployment Cycle**: Complete start → validate → stop sequence
- **Failure Recovery**: Test automatic recovery from common failure scenarios
- **Documentation Sync**: Verify documentation updates reflect actual procedures

### Performance Testing
- **Startup Time**: Target <30 seconds for full deployment
- **Health Check Latency**: Target <5 seconds for status queries
- **Recovery Time**: Target <60 seconds for automatic recovery

## Implementation Details

### Makefile Integration

The design extends the existing Makefile with observatory-specific targets:

```makefile
# Observatory deployment targets
observatory-start:
	@python scripts/observatory_deployment_orchestrator.py start

observatory-stop:
	@python scripts/observatory_deployment_orchestrator.py stop

observatory-status:
	@python scripts/observatory_deployment_orchestrator.py status

observatory-logs:
	@python scripts/observatory_deployment_orchestrator.py logs

observatory-recover:
	@python scripts/observatory_deployment_orchestrator.py recover
```

**Design Rationale**: Integrates seamlessly with existing project workflows while providing consistent command interface per Requirement 7.

### Startup Sequence Implementation

**Phase 1: Prerequisites Validation**
1. Check Python environment and dependencies
2. Validate configuration files exist and are readable
3. Verify port availability (8888 for observatory, tunnel ports)
4. Check Cloudflare credentials and tunnel configuration

**Phase 2: Observatory Service Startup**
1. Start observatory service with health endpoint enabled
2. Wait for `/health` endpoint to respond (max 30 seconds)
3. Verify `/ready` endpoint indicates service readiness
4. Register service with local process manager

**Phase 3: Tunnel Startup**
1. Verify observatory health before tunnel start
2. Start Cloudflare tunnel with validated configuration
3. Wait for tunnel connection establishment (max 60 seconds)
4. Test external accessibility through tunnel

**Phase 4: Monitoring Activation**
1. Start health monitoring agent
2. Begin periodic status checks (every 30 seconds)
3. Enable automatic recovery procedures
4. Update system documentation with current status

### Custom Error Pages

**Cloudflare Configuration**:
```yaml
# cloudflare-tunnel-config.yml
tunnel: <tunnel-id>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: observatory.example.com
    service: http://localhost:8888
    originRequest:
      connectTimeout: 30s
      tlsTimeout: 10s
  - service: http_status:503
    path: /error-pages/observatory-down.html
```

**Error Page Template**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Observatory Temporarily Unavailable</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>Observatory Service Temporarily Unavailable</h1>
    <p>The observatory service is currently undergoing maintenance or experiencing technical difficulties.</p>
    <p><strong>Estimated Recovery Time:</strong> <span id="recovery-time">Unknown</span></p>
    <p><strong>Support Contact:</strong> <a href="mailto:support@example.com">support@example.com</a></p>
    <p><strong>Status Page:</strong> <a href="/status">Service Status</a></p>
</body>
</html>
```

### Documentation Automation

**README Integration**:
The system automatically updates the main README.md with current deployment procedures:

```python
def update_readme_deployment_section():
    """Update README with current deployment procedures."""
    readme_path = "README.md"
    
    deployment_section = generate_deployment_docs()
    
    # Replace section between markers
    with open(readme_path, 'r') as f:
        content = f.read()
    
    updated_content = replace_section(
        content,
        "<!-- DEPLOYMENT-PROCEDURES-START -->",
        "<!-- DEPLOYMENT-PROCEDURES-END -->",
        deployment_section
    )
    
    with open(readme_path, 'w') as f:
        f.write(updated_content)
```

**Troubleshooting Guide Generation**:
The system maintains a living troubleshooting guide based on encountered issues:

```python
def update_troubleshooting_guide(issue: Issue, resolution: Resolution):
    """Add new troubleshooting entry based on resolved issue."""
    guide_path = "docs/observatory-troubleshooting.md"
    
    entry = TroubleshootingEntry(
        symptom=issue.description,
        cause=issue.root_cause,
        solution=resolution.steps,
        prevention=resolution.prevention_steps
    )
    
    append_troubleshooting_entry(guide_path, entry)
```

## Security Considerations

### Credential Management
- Cloudflare tunnel credentials stored in secure location outside repository
- Environment variable injection for sensitive configuration
- Automatic credential rotation support

### Access Control
- Health endpoints protected with authentication tokens
- Administrative operations require elevated privileges
- Audit logging for all deployment operations

### Network Security
- Tunnel traffic encrypted end-to-end
- Local services bound to localhost only
- Firewall rules restrict external access to tunnel endpoints only

## Performance Considerations

### Resource Usage
- **Memory**: Target <100MB for orchestrator components
- **CPU**: Minimal impact during steady-state operation
- **Network**: Efficient health checking with exponential backoff
- **Disk**: Structured logging with automatic rotation

### Scalability
- Health monitoring scales with number of services
- Configuration validation parallelizable across components
- Documentation generation asynchronous and non-blocking

### Optimization Strategies
- Cache health check results for 30 seconds
- Batch configuration validations
- Lazy loading of non-critical components
- Connection pooling for external API calls

## Monitoring and Observability

### Metrics Collection
All components inherit from ReflectiveModule and automatically expose:
- **Deployment metrics**: Success/failure rates, duration distributions
- **Health metrics**: Response times, error rates, availability percentages  
- **Recovery metrics**: Recovery attempt counts, success rates, time to recovery

### Logging Strategy
- **Structured logging**: JSON format with correlation IDs
- **Log levels**: DEBUG for development, INFO for operations, ERROR for failures
- **Log rotation**: Daily rotation with 7-day retention
- **Centralized collection**: Compatible with existing logging infrastructure

### Alerting Integration
- **Prometheus integration**: Automatic metric registration via ReflectiveModule
- **Grafana dashboards**: Pre-configured dashboards for observatory health
- **Alert rules**: Configurable thresholds for automated notifications

This design provides a comprehensive, systematic approach to observatory deployment that addresses all requirements while building upon existing infrastructure and following established architectural patterns.