# Create Service Auto-Start Governance Design Document

## Context

Requirements document has been completed at `.kiro/specs/service-auto-start-governance/requirements.md` with 22 comprehensive requirements across auto-start configuration, health checks, service discovery, verification, and monitoring.

## Task

Create the design.md document that implements these requirements with a complete architecture.

## Input

- Requirements: `.kiro/specs/service-auto-start-governance/requirements.md`
- Root Cause Analysis: `docs/cms/cms-auto-start-root-cause-analysis.md`
- Reference Implementation: Directus LaunchAgent at `/Users/lou/Library/LaunchAgents/com.beastmode.directus.plist`
- Pattern Reference: Other design docs in `.kiro/specs/*/design.md`

## Output

Create: `.kiro/specs/service-auto-start-governance/design.md`

## Requirements

The design must include:

### 1. Architecture Overview (with Mermaid diagram)
- Four main components: ServiceAutoStarter, HealthCheckValidator, ServiceRegistry, VerificationSystem
- Show how they interact
- Integration with Makefile, Observatory, Prometheus

### 2. Component Designs

**ServiceAutoStarter:**
```python
class ServiceAutoStarter(ReflectiveModule):
    """Platform-agnostic auto-start configuration manager."""

    def configure_autostart(
        service_name: str,
        platform: AutoStartPlatform,
        config: AutoStartConfig
    ) -> AutoStartResult

    def verify_autostart(service_name: str) -> VerificationResult
    def test_boot_scenario(service_name: str) -> TestResult
    def rollback(service_name: str) -> RollbackResult
```

**HealthCheckValidator:**
```python
class HealthCheckValidator(ReflectiveModule):
    """Container-aware health check validation."""

    def detect_available_tools(container_image: str) -> List[str]
    def validate_health_check(
        health_check: HealthCheckConfig,
        available_tools: List[str]
    ) -> ValidationResult
    def generate_health_check(
        service: ServiceConfig,
        available_tools: List[str]
    ) -> HealthCheckConfig
```

**ServiceRegistry:**
```python
class ServiceRegistry(ReflectiveModule):
    """Central catalog of all Beast Mode services."""

    def register_service(service: ServiceDefinition) -> RegistrationResult
    def get_service_dependencies(service_name: str) -> List[ServiceDependency]
    def verify_all_autostart() -> RegistryStatus
    def get_dependency_graph() -> DependencyGraph
```

**VerificationSystem:**
```python
class VerificationSystem(ReflectiveModule):
    """Automated verification and testing."""

    def run_boot_simulation(service_name: str) -> SimulationResult
    def verify_deployment(service_name: str) -> DeploymentResult
    def generate_deployment_checklist(service_name: str) -> Checklist
```

### 3. Platform Implementations

Design for each platform:

**macOS LaunchAgent:**
- Template structure
- Plist generation
- launchctl integration
- Log management at ~/Library/Logs/

**Linux systemd:**
- Service file structure
- systemctl integration
- Dependency ordering (After=, Requires=)
- Log management with journald

**Docker:**
- restart policy configuration
- Docker Compose integration
- Init process considerations
- Container orchestration

### 4. Data Models

Complete dataclass definitions:
- ServiceDefinition
- HealthCheckConfig
- AutoStartConfig
- PlatformConfig
- DependencyGraph
- VerificationResult
- All related types and enums

### 5. Integration Architecture

How this integrates with:
- Makefile system (target generation)
- Observatory (monitoring, WebSockets)
- Prometheus (metrics emission)
- DAG orchestrator (for parallel startup)
- Deployment procedures

### 6. Failure Handling & Recovery

Design patterns for:
- Health check failures
- Auto-start failures
- Dependency failures
- Platform-specific errors
- Graceful degradation
- Rollback procedures

### 7. Sequence Diagrams (Mermaid)

Create diagrams for:
- Service registration flow
- Auto-start configuration creation
- Boot simulation test flow
- Deployment verification flow
- Health check validation flow

### 8. Security Model

- User/permission model
- Secret management
- Config file permissions
- Audit logging

### 9. Performance Considerations

- Parallel startup optimization
- Dependency level computation
- Health check timing
- Startup time metrics

### 10. Testing Strategy

- Unit test approach
- Integration test requirements
- Boot simulation testing
- CI/CD integration

## Format

Follow Beast Mode design.md conventions:
- Use Mermaid for all diagrams
- Include code examples in Python
- Reference requirements by number (R1, R2, etc.)
- Provide implementation guidance
- Include configuration examples

## Success Criteria

Design is complete when:
- All 22 requirements are addressed
- Architecture is clear and implementable
- Platform implementations are detailed
- Data models are complete
- Integration points are specified
- Failure scenarios are handled

**Output Location:** `.kiro/specs/service-auto-start-governance/design.md`
