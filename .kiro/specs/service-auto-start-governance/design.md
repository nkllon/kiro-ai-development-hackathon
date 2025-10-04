# Service Auto-Start Governance Design

## Overview

This design addresses the critical service auto-start governance gaps identified in the CMS root cause analysis. The solution provides a systematic framework for ensuring all services automatically start on system boot with proper health verification, cross-platform compatibility, and comprehensive monitoring.

## Architecture

### Core Components

#### 1. Auto-Start Configuration Manager
```python
class AutoStartManager(ReflectiveModule):
    """Manages service auto-start configuration across platforms."""
    
    def detect_platform(self) -> Platform:
        """Detect current platform (macOS, Linux, Docker, K8s)."""
    
    def generate_config(self, service: ServiceDefinition) -> AutoStartConfig:
        """Generate platform-specific auto-start configuration."""
    
    def install_config(self, config: AutoStartConfig) -> bool:
        """Install and activate auto-start configuration."""
    
    def verify_autostart(self, service: str) -> VerificationResult:
        """Verify service will auto-start correctly."""
```

#### 2. Health Check Standardizer
```python
class HealthCheckStandardizer(ReflectiveModule):
    """Standardizes health checks using container-native tools."""
    
    def detect_available_tools(self, container_image: str) -> List[Tool]:
        """Detect which tools are available in container."""
    
    def generate_health_check(self, service: ServiceDefinition) -> HealthCheck:
        """Generate health check using available tools."""
    
    def validate_health_check(self, check: HealthCheck) -> ValidationResult:
        """Validate health check works in target environment."""
```

#### 3. Platform Abstraction Layer
```python
class PlatformAdapter:
    """Abstract interface for platform-specific operations."""
    
    def create_service_config(self, service: ServiceDefinition) -> str:
        """Create platform-specific service configuration."""
    
    def install_service(self, config: str) -> bool:
        """Install service on platform."""
    
    def start_service(self, name: str) -> bool:
        """Start service using platform mechanisms."""
    
    def get_service_status(self, name: str) -> ServiceStatus:
        """Get current service status."""
    
    def get_service_logs(self, name: str) -> List[LogEntry]:
        """Get service startup logs."""
```

#### 4. Boot Simulation Tester
```python
class BootSimulationTester(ReflectiveModule):
    """Tests service auto-start behavior through simulation."""
    
    def simulate_boot(self, services: List[str]) -> BootTestResult:
        """Simulate system boot and verify service startup."""
    
    def test_dependency_ordering(self, services: List[str]) -> DependencyTestResult:
        """Test service startup dependency ordering."""
    
    def test_failure_recovery(self, service: str) -> RecoveryTestResult:
        """Test service failure recovery mechanisms."""
```

### Platform-Specific Implementations

#### macOS LaunchAgent Adapter
```python
class MacOSLaunchAgentAdapter(PlatformAdapter):
    """macOS LaunchAgent implementation."""
    
    LAUNCHAGENT_DIR = Path.home() / "Library/LaunchAgents"
    
    def create_service_config(self, service: ServiceDefinition) -> str:
        """Generate LaunchAgent plist configuration."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.beastmode.{service.name}</string>
    
    <key>ProgramArguments</key>
    <array>
        {self._generate_program_args(service)}
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>{self._get_log_path(service.name)}</string>
    
    <key>StandardErrorPath</key>
    <string>{self._get_error_log_path(service.name)}</string>
    
    <key>WorkingDirectory</key>
    <string>{service.working_directory}</string>
</dict>
</plist>"""
```

#### Linux systemd Adapter
```python
class LinuxSystemdAdapter(PlatformAdapter):
    """Linux systemd implementation."""
    
    def create_service_config(self, service: ServiceDefinition) -> str:
        """Generate systemd unit file."""
        return f"""[Unit]
Description={service.description}
Requires={' '.join(service.dependencies)}
After={' '.join(service.dependencies)}

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory={service.working_directory}
ExecStart={service.start_command}
ExecStop={service.stop_command}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target"""
```

#### Docker Compose Adapter
```python
class DockerComposeAdapter(PlatformAdapter):
    """Docker Compose implementation with proper restart policies."""
    
    def create_service_config(self, service: ServiceDefinition) -> str:
        """Generate Docker Compose service configuration."""
        return f"""
services:
  {service.name}:
    image: {service.image}
    restart: unless-stopped
    healthcheck:
      test: {self._generate_health_check(service)}
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    volumes:
      {self._generate_volumes(service)}
    environment:
      {self._generate_environment(service)}
    depends_on:
      {self._generate_dependencies(service)}
"""
```

### Health Check Generation

#### Container Tool Detection
```python
class ContainerToolDetector:
    """Detects available tools in container images."""
    
    TOOL_DETECTION_COMMANDS = {
        'curl': 'which curl',
        'wget': 'which wget', 
        'nc': 'which nc',
        'python': 'which python3',
        'node': 'which node'
    }
    
    def detect_tools(self, image: str) -> Set[str]:
        """Detect which tools are available in container image."""
        available_tools = set()
        
        for tool, command in self.TOOL_DETECTION_COMMANDS.items():
            if self._test_tool_availability(image, command):
                available_tools.add(tool)
        
        return available_tools
```

#### Health Check Templates
```python
class HealthCheckTemplates:
    """Templates for generating health checks with available tools."""
    
    TEMPLATES = {
        'wget': 'wget --no-verbose --tries=1 --spider {url} || exit 1',
        'curl': 'curl -f {url} || exit 1',
        'nc': 'nc -z {host} {port} || exit 1',
        'python': 'python3 -c "import urllib.request; urllib.request.urlopen(\'{url}\')" || exit 1',
        'node': 'node -e "require(\'http\').get(\'{url}\', (res) => process.exit(res.statusCode === 200 ? 0 : 1))" || exit 1'
    }
    
    def generate_health_check(self, service: ServiceDefinition, available_tools: Set[str]) -> str:
        """Generate health check using best available tool."""
        # Prefer wget > curl > nc > python > node
        for tool in ['wget', 'curl', 'nc', 'python', 'node']:
            if tool in available_tools:
                return self.TEMPLATES[tool].format(
                    url=service.health_url,
                    host=service.host,
                    port=service.port
                )
        
        raise ValueError(f"No suitable health check tool available for {service.name}")
```

### Service Definition Schema

```python
@dataclass
class ServiceDefinition:
    """Complete service definition for auto-start configuration."""
    
    name: str
    description: str
    image: Optional[str] = None
    start_command: str = ""
    stop_command: str = ""
    working_directory: str = ""
    health_url: str = ""
    host: str = "localhost"
    port: int = 80
    dependencies: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    restart_policy: str = "unless-stopped"
    startup_timeout: int = 120
    health_check_timeout: int = 30
    platform_specific: Dict[str, Any] = field(default_factory=dict)
```

### Boot Simulation Framework

#### Simulation Engine
```python
class BootSimulationEngine(ReflectiveModule):
    """Simulates system boot to test auto-start behavior."""
    
    def __init__(self):
        super().__init__()
        self.platform_adapter = self._get_platform_adapter()
        self.services = self._load_service_definitions()
    
    def simulate_clean_boot(self) -> BootSimulationResult:
        """Simulate clean system boot."""
        result = BootSimulationResult()
        
        # 1. Stop all services
        self._stop_all_services()
        
        # 2. Clear service state
        self._clear_service_state()
        
        # 3. Simulate boot process
        boot_start = time.time()
        
        # 4. Start services in dependency order
        for service in self._get_startup_order():
            service_result = self._start_service_with_monitoring(service)
            result.add_service_result(service, service_result)
        
        # 5. Verify all services healthy
        health_results = self._verify_all_services_healthy()
        result.health_results = health_results
        
        result.total_boot_time = time.time() - boot_start
        return result
    
    def test_failure_scenarios(self) -> List[FailureTestResult]:
        """Test various failure scenarios."""
        scenarios = [
            self._test_dependency_failure,
            self._test_resource_exhaustion,
            self._test_network_unavailable,
            self._test_configuration_invalid,
            self._test_partial_startup
        ]
        
        results = []
        for scenario in scenarios:
            results.append(scenario())
        
        return results
```

### Monitoring and Observability

#### Startup Metrics Collector
```python
class StartupMetricsCollector(ReflectiveModule):
    """Collects and exposes startup metrics."""
    
    def __init__(self):
        super().__init__()
        self.startup_duration = Histogram(
            'service_startup_duration_seconds',
            'Time taken for service to start',
            ['service_name', 'platform']
        )
        self.startup_success = Counter(
            'service_startup_success_total',
            'Number of successful service startups',
            ['service_name', 'platform']
        )
        self.startup_failures = Counter(
            'service_startup_failures_total',
            'Number of failed service startups',
            ['service_name', 'platform', 'error_type']
        )
    
    def record_startup_attempt(self, service: str, platform: str, duration: float, success: bool, error_type: str = None):
        """Record service startup attempt."""
        self.startup_duration.labels(service=service, platform=platform).observe(duration)
        
        if success:
            self.startup_success.labels(service=service, platform=platform).inc()
        else:
            self.startup_failures.labels(service=service, platform=platform, error_type=error_type).inc()
```

#### Log Aggregation
```python
class StartupLogAggregator(ReflectiveModule):
    """Aggregates startup logs from all platforms."""
    
    def __init__(self):
        super().__init__()
        self.platform_adapter = self._get_platform_adapter()
    
    def get_startup_logs(self, service: str, since: datetime = None) -> List[LogEntry]:
        """Get startup logs for service."""
        return self.platform_adapter.get_service_logs(service, since)
    
    def analyze_startup_patterns(self, service: str) -> StartupAnalysis:
        """Analyze startup patterns for optimization."""
        logs = self.get_startup_logs(service, since=datetime.now() - timedelta(days=7))
        
        analysis = StartupAnalysis()
        analysis.average_startup_time = self._calculate_average_startup_time(logs)
        analysis.failure_patterns = self._identify_failure_patterns(logs)
        analysis.performance_trends = self._analyze_performance_trends(logs)
        analysis.recommendations = self._generate_recommendations(analysis)
        
        return analysis
```

## Components and Interfaces

### Service Registry Interface
```python
class ServiceRegistry(ReflectiveModule):
    """Central registry for all services requiring auto-start."""
    
    def register_service(self, service: ServiceDefinition) -> bool:
        """Register service for auto-start management."""
    
    def get_service(self, name: str) -> ServiceDefinition:
        """Get service definition by name."""
    
    def list_services(self) -> List[ServiceDefinition]:
        """List all registered services."""
    
    def get_startup_order(self) -> List[str]:
        """Get services in dependency-resolved startup order."""
```

### Configuration Generator Interface
```python
class ConfigurationGenerator(ReflectiveModule):
    """Generates platform-specific configuration files."""
    
    def generate_all_configs(self) -> Dict[str, str]:
        """Generate configurations for all registered services."""
    
    def generate_makefile_targets(self) -> str:
        """Generate Makefile targets for service management."""
    
    def generate_deployment_checklist(self) -> str:
        """Generate deployment checklist including auto-start verification."""
```

## Data Models

### Service Status Model
```python
@dataclass
class ServiceStatus:
    """Current status of a service."""
    
    name: str
    state: ServiceState  # STOPPED, STARTING, RUNNING, FAILED, UNKNOWN
    pid: Optional[int] = None
    uptime: Optional[timedelta] = None
    last_restart: Optional[datetime] = None
    restart_count: int = 0
    health_status: HealthStatus = HealthStatus.UNKNOWN
    error_message: Optional[str] = None
```

### Boot Test Result Model
```python
@dataclass
class BootTestResult:
    """Result of boot simulation test."""
    
    total_boot_time: float
    services_started: int
    services_failed: int
    service_results: Dict[str, ServiceStartResult]
    health_results: Dict[str, HealthCheckResult]
    dependency_violations: List[DependencyViolation]
    recommendations: List[str]
```

## Error Handling

### Startup Failure Classification
```python
class StartupFailureClassifier:
    """Classifies startup failures for targeted remediation."""
    
    FAILURE_PATTERNS = {
        'dependency_unavailable': r'connection refused|no route to host',
        'configuration_invalid': r'invalid configuration|config error',
        'resource_exhaustion': r'out of memory|disk full|no space left',
        'permission_denied': r'permission denied|access denied',
        'port_conflict': r'port already in use|address already in use',
        'image_unavailable': r'image not found|pull failed'
    }
    
    def classify_failure(self, error_message: str, exit_code: int) -> FailureType:
        """Classify failure type for targeted remediation."""
        for failure_type, pattern in self.FAILURE_PATTERNS.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                return FailureType(failure_type)
        
        return FailureType.UNKNOWN
```

### Recovery Strategies
```python
class RecoveryStrategyManager:
    """Manages recovery strategies for different failure types."""
    
    RECOVERY_STRATEGIES = {
        FailureType.DEPENDENCY_UNAVAILABLE: [
            'wait_for_dependency',
            'start_dependency_first',
            'use_fallback_configuration'
        ],
        FailureType.CONFIGURATION_INVALID: [
            'validate_configuration',
            'regenerate_configuration',
            'use_default_configuration'
        ],
        FailureType.RESOURCE_EXHAUSTION: [
            'free_resources',
            'reduce_resource_requirements',
            'defer_startup'
        ]
    }
    
    def get_recovery_strategy(self, failure_type: FailureType) -> List[RecoveryAction]:
        """Get recovery strategy for failure type."""
        return self.RECOVERY_STRATEGIES.get(failure_type, ['manual_intervention'])
```

## Testing Strategy

### Unit Tests
- Platform adapter implementations
- Health check generation logic
- Service definition validation
- Configuration file generation

### Integration Tests
- Cross-platform configuration generation
- Service startup simulation
- Health check validation
- Dependency resolution

### End-to-End Tests
- Complete boot simulation
- Multi-service startup orchestration
- Failure recovery scenarios
- Platform migration testing

### Performance Tests
- Startup time optimization
- Resource usage monitoring
- Concurrent service startup
- Large-scale deployment simulation

## Security Considerations

### Configuration Security
- Service configurations stored with appropriate permissions
- Sensitive data (passwords, keys) handled through secure mechanisms
- Log files protected from unauthorized access
- Service isolation maintained across platforms

### Runtime Security
- Services run with minimal required privileges
- Network access restricted to necessary ports
- File system access limited to required directories
- Container security best practices enforced

## Deployment Considerations

### Rollout Strategy
1. **Phase 1**: Implement for existing CMS service (validation)
2. **Phase 2**: Extend to all Docker Compose services
3. **Phase 3**: Add cross-platform support (Linux/K8s)
4. **Phase 4**: Full automation and monitoring integration

### Migration Path
- Existing services gradually migrated to new framework
- Legacy startup scripts maintained during transition
- Configuration validation ensures compatibility
- Rollback procedures available for each phase

### Monitoring Integration
- Startup metrics integrated with existing Prometheus setup
- Log aggregation through existing logging infrastructure
- Alerting configured for startup failures
- Dashboard created for startup performance monitoring