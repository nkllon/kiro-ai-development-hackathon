# System Health Mitigation Framework Design

## Overview

This design provides systematic solutions for the critical system health issues identified in the October 3, 2025 assessment. The framework addresses specific problems: Cloudflare tunnel failures, Docker health check misconfigurations, Observatory health scoring issues, Prometheus exporter gaps, disk space management, and service auto-restart policies.

## Architecture

### Core Components

#### 1. Service Recovery Manager
```python
class ServiceRecoveryManager(ReflectiveModule):
    """Manages automatic service recovery and restart policies."""
    
    def __init__(self):
        super().__init__()
        self.restart_policies = self._load_restart_policies()
        self.failure_tracker = ServiceFailureTracker()
        self.recovery_strategies = RecoveryStrategyRegistry()
    
    def monitor_service_health(self, service_name: str) -> ServiceHealthStatus:
        """Monitor service health and trigger recovery if needed."""
        
    def execute_recovery_action(self, service_name: str, failure_type: FailureType) -> RecoveryResult:
        """Execute appropriate recovery action based on failure type."""
        
    def validate_restart_policy(self, service_config: ServiceConfig) -> ValidationResult:
        """Validate that restart policy will work correctly."""
```

#### 2. Health Check Validator
```python
class HealthCheckValidator(ReflectiveModule):
    """Validates and standardizes health check configurations."""
    
    def __init__(self):
        super().__init__()
        self.tool_detector = ContainerToolDetector()
        self.config_templates = HealthCheckTemplates()
    
    def validate_health_check_config(self, config: HealthCheckConfig) -> ValidationResult:
        """Validate health check configuration for correctness."""
        
    def fix_localhost_ipv6_issues(self, config: HealthCheckConfig) -> HealthCheckConfig:
        """Fix IPv6/IPv4 localhost resolution issues."""
        
    def test_health_check_in_environment(self, config: HealthCheckConfig, environment: str) -> TestResult:
        """Test health check in actual deployment environment."""
```

#### 3. Observatory Health Scorer
```python
class ObservatoryHealthScorer(ReflectiveModule):
    """Manages Observatory health scoring with proper feature state handling."""
    
    def __init__(self):
        super().__init__()
        self.feature_registry = FeatureRegistry()
        self.scoring_rules = HealthScoringRules()
    
    def calculate_health_score(self, system_state: SystemState) -> HealthScore:
        """Calculate health score excluding disabled features."""
        
    def update_feature_status(self, feature_name: str, status: FeatureStatus) -> None:
        """Update feature status (enabled/disabled/failed)."""
        
    def generate_health_report(self) -> HealthReport:
        """Generate comprehensive health report with feature breakdown."""
```

#### 4. Prometheus Exporter Manager
```python
class PrometheusExporterManager(ReflectiveModule):
    """Manages Prometheus exporters and metrics endpoints."""
    
    def __init__(self):
        super().__init__()
        self.exporter_registry = ExporterRegistry()
        self.scrape_config_manager = ScrapeConfigManager()
    
    def deploy_missing_exporters(self, required_exporters: List[str]) -> DeploymentResult:
        """Deploy missing Prometheus exporters."""
        
    def add_metrics_endpoint(self, service_name: str, endpoint_config: MetricsEndpointConfig) -> None:
        """Add /metrics endpoint to existing service."""
        
    def validate_scrape_targets(self, prometheus_config: PrometheusConfig) -> ValidationResult:
        """Validate all scrape targets are reachable."""
```

#### 5. Disk Space Manager
```python
class DiskSpaceManager(ReflectiveModule):
    """Manages disk space monitoring and automated cleanup."""
    
    def __init__(self):
        super().__init__()
        self.cleanup_policies = CleanupPolicyRegistry()
        self.space_monitor = DiskSpaceMonitor()
    
    def monitor_disk_usage(self) -> DiskUsageReport:
        """Monitor disk usage and generate alerts if needed."""
        
    def execute_cleanup_policy(self, policy_name: str) -> CleanupResult:
        """Execute specific cleanup policy."""
        
    def predict_space_exhaustion(self, usage_history: List[DiskUsage]) -> PredictionResult:
        """Predict when disk space will be exhausted."""
```

### Specific Issue Solutions

#### 1. Cloudflare Tunnel Recovery
```python
class CloudflareTunnelManager(ReflectiveModule):
    """Manages Cloudflare tunnel health and recovery."""
    
    def __init__(self):
        super().__init__()
        self.tunnel_monitor = TunnelConnectionMonitor()
        self.restart_policy = ExponentialBackoffPolicy(
            initial_delay=5,
            max_delay=300,
            max_attempts=10
        )
    
    def monitor_tunnel_connections(self) -> TunnelStatus:
        """Monitor tunnel connection status."""
        tunnel_status = self._check_tunnel_process()
        connection_count = self._count_active_connections()
        
        if tunnel_status.is_running and connection_count >= 2:
            return TunnelStatus.HEALTHY
        elif tunnel_status.is_running and connection_count < 2:
            return TunnelStatus.DEGRADED
        else:
            return TunnelStatus.FAILED
    
    def restart_tunnel_if_needed(self) -> RestartResult:
        """Restart tunnel if connections are down."""
        status = self.monitor_tunnel_connections()
        
        if status in [TunnelStatus.FAILED, TunnelStatus.DEGRADED]:
            return self._execute_tunnel_restart()
        
        return RestartResult.NOT_NEEDED
    
    def _execute_tunnel_restart(self) -> RestartResult:
        """Execute tunnel restart with proper verification."""
        try:
            # Stop existing tunnel process
            self._stop_tunnel_container()
            
            # Start tunnel container
            self._start_tunnel_container()
            
            # Wait for connections to establish
            return self._wait_for_tunnel_connections(timeout=120)
            
        except Exception as e:
            self.logger.error(f"Tunnel restart failed: {e}")
            return RestartResult.FAILED
```

#### 2. Directus Health Check Fix
```python
class DirectusHealthCheckFixer(ReflectiveModule):
    """Fixes Directus CMS health check IPv6/IPv4 issues."""
    
    def __init__(self):
        super().__init__()
        self.docker_compose_manager = DockerComposeManager()
    
    def fix_directus_health_check(self) -> FixResult:
        """Fix Directus health check to use IPv4."""
        try:
            # Read current docker-compose configuration
            config = self.docker_compose_manager.read_config('docker-compose.directus-fixed.yml')
            
            # Update health check to use 127.0.0.1 instead of localhost
            if 'services' in config and 'directus' in config['services']:
                service_config = config['services']['directus']
                
                if 'healthcheck' in service_config:
                    # Replace localhost with 127.0.0.1 in health check
                    health_check = service_config['healthcheck']['test']
                    updated_check = self._replace_localhost_with_ipv4(health_check)
                    service_config['healthcheck']['test'] = updated_check
                    
                    # Write updated configuration
                    self.docker_compose_manager.write_config(config, 'docker-compose.directus-fixed.yml')
                    
                    # Restart service to apply new health check
                    return self._restart_directus_service()
            
            return FixResult.NO_CHANGES_NEEDED
            
        except Exception as e:
            self.logger.error(f"Failed to fix Directus health check: {e}")
            return FixResult.FAILED
    
    def _replace_localhost_with_ipv4(self, health_check_command: List[str]) -> List[str]:
        """Replace localhost with 127.0.0.1 in health check command."""
        updated_command = []
        for arg in health_check_command:
            if 'localhost:' in arg:
                updated_arg = arg.replace('localhost:', '127.0.0.1:')
                updated_command.append(updated_arg)
            else:
                updated_command.append(arg)
        return updated_command
```

#### 3. Observatory Health Scoring Fix
```python
class ObservatoryHealthScoringFixer(ReflectiveModule):
    """Fixes Observatory health scoring to handle disabled features."""
    
    def __init__(self):
        super().__init__()
        self.feature_config = FeatureConfiguration()
    
    def fix_health_scoring_algorithm(self) -> FixResult:
        """Update health scoring to exclude disabled features."""
        try:
            # Update health calculation logic
            health_calculator = self._get_health_calculator()
            
            # Configure feature states
            self.feature_config.set_feature_status('engagement', FeatureStatus.DISABLED)
            self.feature_config.set_feature_status('observatory_core', FeatureStatus.ENABLED)
            
            # Update scoring algorithm
            updated_algorithm = self._create_updated_scoring_algorithm()
            health_calculator.update_scoring_algorithm(updated_algorithm)
            
            return FixResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed to fix health scoring: {e}")
            return FixResult.FAILED
    
    def _create_updated_scoring_algorithm(self) -> HealthScoringAlgorithm:
        """Create updated scoring algorithm that excludes disabled features."""
        def calculate_score(system_state: SystemState) -> float:
            enabled_features = self.feature_config.get_enabled_features()
            total_score = 0.0
            feature_count = 0
            
            for feature_name in enabled_features:
                feature_health = system_state.get_feature_health(feature_name)
                if feature_health is not None:
                    total_score += feature_health.score
                    feature_count += 1
            
            return total_score / feature_count if feature_count > 0 else 0.0
        
        return HealthScoringAlgorithm(calculate_score)
```

#### 4. Prometheus Exporter Deployment
```python
class PrometheusExporterDeployer(ReflectiveModule):
    """Deploys missing Prometheus exporters."""
    
    def __init__(self):
        super().__init__()
        self.docker_manager = DockerManager()
        self.prometheus_config_manager = PrometheusConfigManager()
    
    def deploy_redis_exporter(self) -> DeploymentResult:
        """Deploy Redis exporter for monitoring Redis instances."""
        try:
            # Create Redis exporter container configuration
            exporter_config = {
                'image': 'oliver006/redis_exporter:latest',
                'container_name': 'redis-exporter',
                'ports': ['9121:9121'],
                'environment': {
                    'REDIS_ADDR': 'redis://msp-ssl-redis:6379'
                },
                'networks': ['observatory-network'],
                'restart': 'unless-stopped'
            }
            
            # Deploy container
            deployment_result = self.docker_manager.deploy_container(exporter_config)
            
            if deployment_result.success:
                # Update Prometheus configuration
                self._add_exporter_to_prometheus_config('redis-exporter', 'localhost:9121')
                return DeploymentResult.SUCCESS
            else:
                return DeploymentResult.FAILED
                
        except Exception as e:
            self.logger.error(f"Failed to deploy Redis exporter: {e}")
            return DeploymentResult.FAILED
    
    def add_metrics_endpoint_to_engagement_manager(self) -> DeploymentResult:
        """Add /metrics endpoint to engagement manager service."""
        try:
            # Update engagement manager code to include metrics endpoint
            service_code = self._read_engagement_manager_code()
            updated_code = self._add_prometheus_metrics_endpoint(service_code)
            self._write_engagement_manager_code(updated_code)
            
            # Restart engagement manager to apply changes
            restart_result = self.docker_manager.restart_container('observatory-engagement-manager')
            
            return DeploymentResult.SUCCESS if restart_result.success else DeploymentResult.FAILED
            
        except Exception as e:
            self.logger.error(f"Failed to add metrics endpoint: {e}")
            return DeploymentResult.FAILED
```

#### 5. Disk Space Cleanup Automation
```python
class DiskSpaceCleanupAutomator(ReflectiveModule):
    """Automates disk space cleanup procedures."""
    
    def __init__(self):
        super().__init__()
        self.cleanup_policies = self._load_cleanup_policies()
        self.space_threshold = 85  # Alert at 85% usage
    
    def execute_automated_cleanup(self) -> CleanupResult:
        """Execute automated cleanup based on current disk usage."""
        current_usage = self._get_disk_usage_percentage()
        
        if current_usage > self.space_threshold:
            cleanup_result = CleanupResult()
            
            # Execute cleanup policies in order of safety
            cleanup_result.add_result(self._cleanup_docker_build_cache())
            cleanup_result.add_result(self._cleanup_old_log_files())
            cleanup_result.add_result(self._cleanup_temporary_backups())
            cleanup_result.add_result(self._cleanup_unused_docker_images())
            
            return cleanup_result
        
        return CleanupResult.NOT_NEEDED
    
    def _cleanup_docker_build_cache(self) -> PolicyResult:
        """Clean up Docker build cache."""
        try:
            result = subprocess.run(['docker', 'builder', 'prune', '-f'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse space freed from output
                space_freed = self._parse_space_freed(result.stdout)
                return PolicyResult.success(f"Docker build cache cleaned: {space_freed} freed")
            else:
                return PolicyResult.failed(f"Docker cleanup failed: {result.stderr}")
                
        except Exception as e:
            return PolicyResult.failed(f"Docker cleanup exception: {e}")
    
    def _cleanup_old_log_files(self) -> PolicyResult:
        """Clean up log files older than 30 days."""
        try:
            # Find and remove log files older than 30 days
            log_dirs = ['logs/', 'var/log/', '*.log']
            total_freed = 0
            
            for log_pattern in log_dirs:
                files_removed = self._remove_old_files(log_pattern, days=30)
                total_freed += files_removed.size_freed
            
            return PolicyResult.success(f"Old log files cleaned: {total_freed} bytes freed")
            
        except Exception as e:
            return PolicyResult.failed(f"Log cleanup exception: {e}")
```

## Components and Interfaces

### Service Health Monitor Interface
```python
class ServiceHealthMonitor(ReflectiveModule):
    """Monitors service health across all platforms."""
    
    def register_service(self, service_config: ServiceConfig) -> bool:
        """Register service for health monitoring."""
    
    def check_service_health(self, service_name: str) -> HealthStatus:
        """Check current health status of service."""
    
    def get_health_history(self, service_name: str, duration: timedelta) -> List[HealthEvent]:
        """Get health history for analysis."""
    
    def set_health_thresholds(self, service_name: str, thresholds: HealthThresholds) -> bool:
        """Set custom health thresholds for service."""
```

### Configuration Validator Interface
```python
class ConfigurationValidator(ReflectiveModule):
    """Validates service configurations for correctness."""
    
    def validate_docker_compose_config(self, config_path: str) -> ValidationResult:
        """Validate Docker Compose configuration."""
    
    def validate_health_check_config(self, health_check: HealthCheckConfig) -> ValidationResult:
        """Validate health check configuration."""
    
    def validate_restart_policy(self, restart_policy: RestartPolicy) -> ValidationResult:
        """Validate restart policy configuration."""
    
    def fix_common_configuration_issues(self, config_path: str) -> FixResult:
        """Automatically fix common configuration issues."""
```

### Automated Remediation Engine Interface
```python
class AutomatedRemediationEngine(ReflectiveModule):
    """Executes automated remediation procedures."""
    
    def register_remediation_procedure(self, issue_type: str, procedure: RemediationProcedure) -> bool:
        """Register automated remediation procedure."""
    
    def execute_remediation(self, issue: SystemIssue) -> RemediationResult:
        """Execute appropriate remediation for issue."""
    
    def test_remediation_procedure(self, procedure_name: str) -> TestResult:
        """Test remediation procedure in safe environment."""
    
    def get_remediation_history(self, duration: timedelta) -> List[RemediationEvent]:
        """Get history of remediation actions."""
```

## Data Models

### Service Health Status Model
```python
@dataclass
class ServiceHealthStatus:
    """Current health status of a service."""
    
    service_name: str
    status: ServiceStatus  # HEALTHY, DEGRADED, FAILED, UNKNOWN
    health_score: float  # 0.0 to 1.0
    last_check: datetime
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    restart_count: int = 0
    uptime: Optional[timedelta] = None
    dependencies_healthy: bool = True
```

### System Issue Model
```python
@dataclass
class SystemIssue:
    """Represents a detected system issue."""
    
    issue_id: str
    issue_type: IssueType
    severity: IssueSeverity  # CRITICAL, WARNING, INFO
    description: str
    affected_services: List[str]
    detection_time: datetime
    auto_remediable: bool
    remediation_procedures: List[str]
    escalation_required: bool = False
```

### Remediation Result Model
```python
@dataclass
class RemediationResult:
    """Result of automated remediation attempt."""
    
    issue_id: str
    procedure_name: str
    success: bool
    execution_time: float
    actions_taken: List[str]
    verification_result: Optional[VerificationResult] = None
    error_message: Optional[str] = None
    requires_manual_intervention: bool = False
```

## Error Handling

### Issue Classification System
```python
class IssueClassifier:
    """Classifies system issues for appropriate handling."""
    
    CLASSIFICATION_RULES = {
        'service_down': {
            'patterns': ['connection refused', 'service unavailable', 'container not running'],
            'severity': IssueSeverity.CRITICAL,
            'auto_remediable': True,
            'remediation_procedures': ['restart_service', 'check_dependencies']
        },
        'health_check_misconfigured': {
            'patterns': ['health check failing', 'localhost resolution', 'ipv6 connection refused'],
            'severity': IssueSeverity.WARNING,
            'auto_remediable': True,
            'remediation_procedures': ['fix_health_check_config', 'restart_service']
        },
        'disk_space_critical': {
            'patterns': ['disk full', 'no space left', 'disk usage >85%'],
            'severity': IssueSeverity.CRITICAL,
            'auto_remediable': True,
            'remediation_procedures': ['cleanup_docker_cache', 'cleanup_logs', 'cleanup_temp_files']
        }
    }
    
    def classify_issue(self, issue_description: str, context: Dict[str, Any]) -> IssueClassification:
        """Classify issue based on description and context."""
        for issue_type, rules in self.CLASSIFICATION_RULES.items():
            if self._matches_patterns(issue_description, rules['patterns']):
                return IssueClassification(
                    issue_type=issue_type,
                    severity=rules['severity'],
                    auto_remediable=rules['auto_remediable'],
                    remediation_procedures=rules['remediation_procedures']
                )
        
        return IssueClassification.UNKNOWN
```

### Recovery Strategy Registry
```python
class RecoveryStrategyRegistry:
    """Registry of recovery strategies for different failure types."""
    
    def __init__(self):
        self.strategies = {
            'cloudflare_tunnel_down': CloudflareTunnelRecoveryStrategy(),
            'directus_health_check_failing': DirectusHealthCheckRecoveryStrategy(),
            'observatory_health_score_zero': ObservatoryHealthScoringRecoveryStrategy(),
            'prometheus_exporter_down': PrometheusExporterRecoveryStrategy(),
            'disk_space_critical': DiskSpaceRecoveryStrategy(),
            'service_auto_restart_missing': ServiceAutoRestartRecoveryStrategy()
        }
    
    def get_recovery_strategy(self, failure_type: str) -> RecoveryStrategy:
        """Get appropriate recovery strategy for failure type."""
        return self.strategies.get(failure_type, DefaultRecoveryStrategy())
    
    def register_strategy(self, failure_type: str, strategy: RecoveryStrategy) -> None:
        """Register new recovery strategy."""
        self.strategies[failure_type] = strategy
```

## Testing Strategy

### Health Check Validation Testing
```python
class HealthCheckValidationTester:
    """Tests health check configurations in various environments."""
    
    def test_health_check_in_container(self, health_check: HealthCheckConfig, image: str) -> TestResult:
        """Test health check configuration in actual container."""
        
    def test_ipv4_vs_ipv6_resolution(self, hostname: str) -> ResolutionTestResult:
        """Test hostname resolution for IPv4/IPv6 issues."""
        
    def validate_health_check_tools(self, image: str, required_tools: List[str]) -> ToolValidationResult:
        """Validate required tools are available in container image."""
```

### Service Recovery Testing
```python
class ServiceRecoveryTester:
    """Tests service recovery procedures."""
    
    def test_service_restart_policy(self, service_name: str) -> RestartTestResult:
        """Test service restart policy by simulating failure."""
        
    def test_dependency_recovery(self, service_name: str) -> DependencyTestResult:
        """Test service recovery when dependencies fail."""
        
    def test_cascading_failure_recovery(self, services: List[str]) -> CascadeTestResult:
        """Test recovery from cascading service failures."""
```

### Automated Remediation Testing
```python
class AutomatedRemediationTester:
    """Tests automated remediation procedures."""
    
    def test_remediation_procedure(self, procedure_name: str, test_environment: str) -> TestResult:
        """Test remediation procedure in controlled environment."""
        
    def simulate_system_issues(self, issue_scenarios: List[IssueScenario]) -> SimulationResult:
        """Simulate various system issues to test remediation."""
        
    def validate_remediation_safety(self, procedure: RemediationProcedure) -> SafetyValidationResult:
        """Validate remediation procedure won't cause additional issues."""
```

## Security Considerations

### Remediation Action Security
- All automated remediation actions logged with full audit trails
- Remediation procedures run with minimal required privileges
- Critical system files protected from automated cleanup
- Configuration changes validated before application

### Monitoring Data Security
- Health check data sanitized to remove sensitive information
- Monitoring endpoints protected with appropriate authentication
- Log files rotated and archived securely
- Metrics data retention policies enforced

## Deployment Considerations

### Rollout Strategy
1. **Phase 1**: Deploy health check fixes for immediate issues (Directus, Observatory)
2. **Phase 2**: Implement service recovery automation (Cloudflare tunnel, MCP service)
3. **Phase 3**: Deploy Prometheus exporter management and disk space automation
4. **Phase 4**: Full automated remediation and monitoring integration

### Integration with Existing Systems
- Builds upon existing service-auto-start-governance framework
- Integrates with current Prometheus and Grafana monitoring
- Uses existing Docker and Docker Compose infrastructure
- Maintains compatibility with current deployment procedures

### Monitoring and Alerting Integration
- Integrates with existing Prometheus metrics collection
- Uses current Grafana dashboards with additional panels
- Maintains existing alert routing and escalation procedures
- Adds new metrics for remediation effectiveness tracking