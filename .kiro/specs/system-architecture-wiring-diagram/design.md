# System Architecture Wiring Diagram - Design Document

## Overview

This design document outlines the creation of comprehensive system architecture documentation that maps the relationships between all infrastructure components in the Beast Mode framework ecosystem. The system encompasses multiple interconnected layers:

**Infrastructure Layer**: Cloudflare tunnels (d1e53e43-033f-4994-8f46-c83962ae3785), DNS routing (observatory.nkllon.com, grafana.observatory.nkllon.com, prometheus.observatory.nkllon.com), and network topology (192.168.1.x local network with Redis coordination at 192.168.1.119:6379 with localhost:6380 fallback).

**Observability Stack**: Observatory server (localhost:8888) with WebSocket endpoints (/ws/emoji-rain, /ws/observatory, /ws/anomalies, /ws/doctor-status), Prometheus metrics collection (localhost:9090), Grafana visualization (localhost:3000), and Beast Mode ReflectiveModule pattern for universal observability.

**Automation Layer**: Makefile orchestration with 50+ targets (tunnel-start, dashboard-up, dashboard-status, etc.), Python automation scripts (observatory-daemon.py, tunnel management, metrics collection), and systematic deployment workflows.

**Integration Points**: ACE Reporter for progress broadcasting, AI Memory Palace for context storage, DAG Registry for dependency validation, and CMS-based configuration management through Directus.

The solution will provide clear UML diagrams, sequence diagrams for operational workflows, network topology maps, and comprehensive interaction documentation that enables anyone to understand how these complex, interconnected systems work together as a cohesive Beast Mode framework.

## ADR Conformance Review

### Relevant ADRs Reviewed
- ADR-004: DAG Orchestration with Celery + Redis - ✅ Compliant (leverages existing Redis infrastructure)
- ADR-005: ReflectiveModule Pattern for Universal Observability - ✅ Compliant (uses existing observability patterns)
- ADR-007: Integration-First Design Strategy - ✅ Compliant (integrates with existing Beast Mode framework)
- ADR-010: CMS-Based Configuration Management - ✅ Compliant (uses existing Directus CMS for configuration)

### Conformance Assessment
- **Infrastructure**: Aligns with existing Redis, Prometheus, and Cloudflare infrastructure
- **Integration**: Follows integration-first strategy by documenting existing system relationships
- **Operations**: Maintains existing operational patterns while adding documentation layer
- **Technology**: Uses established UML and documentation generation tools

### Architectural Consistency
The design maintains architectural consistency by documenting rather than replacing existing systems, following the observation-first leadership principle, and leveraging existing Beast Mode framework patterns.

## Architecture

### System Constraints and Dependencies

#### Critical Infrastructure Dependencies
The system architecture documentation generator has the following hard dependencies that must be validated before operation:

**Directus CMS Availability (localhost:8055)**:
- **Constraint**: Directus CMS must be available for configuration management per ADR-010
- **Validation**: Health check endpoint `/server/ping` must respond with "pong"
- **Fallback Strategy**: File-based configuration storage when Directus unavailable
- **Impact**: Without Directus, configuration management features are degraded to read-only file-based mode

**Redis Coordination (192.168.1.119:6379 + localhost:6380)**:
- **Constraint**: At least one Redis instance must be available for coordination
- **Validation**: Redis PING command must succeed on primary or fallback
- **Fallback Strategy**: Automatic failover from primary to fallback Redis instance
- **Impact**: Without Redis, real-time coordination and caching features are disabled

**Observatory Server (localhost:8888)**:
- **Constraint**: Observatory server must be running for WebSocket endpoint discovery
- **Validation**: Health endpoints `/health`, `/ready`, `/metrics` must respond
- **Fallback Strategy**: Static configuration discovery when Observatory unavailable
- **Impact**: Without Observatory, real-time metrics and WebSocket documentation is incomplete

#### Dependency Validation Framework
```python
@dataclass
class SystemConstraint:
    name: str
    endpoint: str
    validation_method: str
    required: bool
    fallback_strategy: str
    impact_description: str
    validation_timeout_seconds: int

SYSTEM_CONSTRAINTS = [
    SystemConstraint(
        name="Directus CMS",
        endpoint="http://localhost:8055/server/ping",
        validation_method="HTTP GET expecting 'pong'",
        required=False,  # Has fallback
        fallback_strategy="File-based configuration storage",
        impact_description="Configuration management degraded to read-only mode",
        validation_timeout_seconds=5
    ),
    SystemConstraint(
        name="Redis Primary",
        endpoint="192.168.1.119:6379",
        validation_method="Redis PING command",
        required=False,  # Has fallback
        fallback_strategy="Automatic failover to localhost:6380",
        impact_description="Coordination features continue with fallback Redis",
        validation_timeout_seconds=3
    ),
    SystemConstraint(
        name="Observatory Server",
        endpoint="http://localhost:8888/health",
        validation_method="HTTP GET expecting 200 status",
        required=False,  # Has fallback
        fallback_strategy="Static configuration discovery",
        impact_description="Real-time metrics documentation incomplete",
        validation_timeout_seconds=5
    )
]
```

### Component Architecture

The system architecture documentation generator consists of four main components with dependency-aware initialization:

#### 1. Infrastructure Discovery Engine
**Purpose**: Automatically discovers and catalogs all infrastructure components
**Implementation**: Python-based discovery scripts that scan:
- Running processes and services
- Network configurations and port mappings
- Configuration files (YAML, JSON, ENV)
- Docker containers and compose files
- Cloudflare tunnel configurations
- DNS records and routing rules

#### 2. Relationship Mapper
**Purpose**: Analyzes dependencies and data flows between components
**Implementation**: Graph-based analysis engine that:
- Parses configuration files for service dependencies
- Traces network connections and routing paths
- Maps data flow from metrics collection to visualization
- Identifies automation scripts and their target components

#### 3. UML Diagram Generator
**Purpose**: Creates visual representations of system architecture
**Implementation**: Automated diagram generation using:
- PlantUML for component and sequence diagrams
- Mermaid for network topology and data flow diagrams
- Python-based diagram generation scripts
- SVG/PNG output for documentation embedding

#### 4. Documentation Orchestrator
**Purpose**: Coordinates discovery, analysis, and documentation generation
**Implementation**: ReflectiveModule-based orchestrator that:
- Schedules periodic infrastructure scans
- Manages diagram generation workflows
- Maintains documentation versioning
- Provides health monitoring and status reporting

### Network Architecture

#### Current Infrastructure Topology
```
Internet
    ↓
Cloudflare Edge (observatory.nkllon.com)
    ↓
Cloudflare Tunnel (d1e53e43-033f-4994-8f46-c83962ae3785)
    ↓
Local Network (192.168.1.x)
    ├── Observatory Server (localhost:8888)
    │   ├── WebSocket Endpoints (/ws/observatory, /ws/emoji-rain, /ws/anomalies, /ws/doctor-status)
    │   ├── Health Endpoints (/health, /ready, /metrics)
    │   └── ReflectiveModule Integration
    ├── Prometheus (localhost:9090)
    │   ├── Scrape Targets (Observatory, ReflectiveModules)
    │   └── Alert Rules & Storage
    ├── Grafana (localhost:3000)
    │   ├── Datasource (Prometheus)
    │   └── Dashboards & Visualization
    └── Redis Coordination
        ├── Primary (192.168.1.119:6379)
        └── Fallback (localhost:6380)
```

#### DNS Routing Configuration (Requirement 5.2)

**Primary Domain Routing**:
- **observatory.nkllon.com** → Observatory Server (localhost:8888)
- **DNS Propagation**: Through Cloudflare Edge with 30-60 second propagation time
- **SSL/TLS**: Automatic certificate provisioning and renewal
- **Health Check**: DNS resolution validation every 60 seconds

**Subdomain Routing with Service Mapping**:
- **grafana.observatory.nkllon.com** → Grafana Dashboard (localhost:3000)
- **prometheus.observatory.nkllon.com** → Prometheus Server (localhost:9090)
- **Tunnel-Specific DNS Propagation**: Cloudflare Edge routing with ingress rule validation
- **WebSocket Upgrade Handling**: HTTP/1.1 to WebSocket protocol upgrade for real-time connections

**WebSocket Endpoint Mappings** (Requirement 5.1):
- **/ws/observatory** → Real-time system events (port 8888)
- **/ws/emoji-rain** → Coordination visualization (port 8888)
- **/ws/anomalies** → Performance anomaly alerts (port 8888)
- **/ws/doctor-status** → Health monitoring updates (port 8888)

**Cloudflare Tunnel Ingress Rules with Specific Routing Logic** (Requirement 5.1):
```yaml
tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: /path/to/tunnel/credentials.json

ingress:
  - hostname: observatory.nkllon.com
    service: http://localhost:8888
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tlsTimeout: 10s
  
  - hostname: grafana.observatory.nkllon.com  
    service: http://localhost:3000
    originRequest:
      noTLSVerify: true
      
  - hostname: prometheus.observatory.nkllon.com
    service: http://localhost:9090
    originRequest:
      noTLSVerify: true
      
  - service: http_status:404
```

**DNS Failover Mechanisms for Service Continuity** (Requirement 5.2):
- Primary DNS resolution through Cloudflare Edge
- Fallback to direct IP resolution for local network access
- Health check integration with automatic DNS record updates
- Geographic routing for optimal performance and redundancy

#### Network Capacity and Scaling Constraints (Requirement 5.4)

**Cloudflare Tunnel Bandwidth Limitations and Optimization Strategies**:
- **Bandwidth Limit**: 1 Gbps per tunnel with burst capacity to 2 Gbps
- **Concurrent Connections**: Up to 1000 simultaneous WebSocket connections
- **Optimization Strategies**: 
  - Connection pooling for HTTP requests
  - WebSocket message compression (deflate-frame)
  - Request/response caching at Cloudflare Edge
  - Geographic load balancing for global access

**Local Network Capacity for Multi-Service Coordination**:
- **Network Range**: 192.168.1.x with /24 subnet (254 available addresses)
- **Bandwidth**: Gigabit Ethernet with 1000 Mbps theoretical maximum
- **Service Coordination**: Redis-based coordination with sub-millisecond latency
- **Capacity Planning**: Current services use <10% of available network capacity

**WebSocket Connection Limits and Load Balancing Considerations**:
- **Per-Endpoint Limits**: 250 connections per WebSocket endpoint
- **Total Capacity**: 1000 concurrent WebSocket connections across all endpoints
- **Load Balancing**: Round-robin distribution with sticky sessions
- **Connection Management**: Automatic cleanup of idle connections after 5 minutes
- **Scaling Strategy**: Horizontal scaling with multiple Observatory instances

**Redis Coordination Scalability with Multi-Node Support**:
- **Primary Node**: 192.168.1.119:6379 with 16GB memory capacity
- **Fallback Node**: localhost:6380 with 8GB memory capacity  
- **Scaling Pattern**: Redis Cluster mode for horizontal scaling
- **Performance**: 100,000+ operations/second with sub-millisecond latency
- **Multi-Node Coordination**: Automatic failover with <1 second detection time

**Port Allocation Strategies for New Services**:
- **Reserved Ranges**: 8000-8999 for Observatory services, 9000-9999 for monitoring
- **Dynamic Allocation**: Automatic port discovery and conflict resolution
- **Service Registration**: Consul-based service discovery integration
- **Health Monitoring**: Automatic port health checks and availability tracking

**DNS Propagation Timing for Service Additions or Modifications**:
- **Initial Propagation**: 30-60 seconds for new DNS records
- **Update Propagation**: 15-30 seconds for existing record modifications
- **Global Propagation**: 2-5 minutes for worldwide DNS cache updates
- **Validation**: Automated DNS propagation testing from multiple geographic locations

## Components and Interfaces

### 1. Infrastructure Discovery Engine

#### Core Interfaces
```python
class InfrastructureDiscoverer(ReflectiveModule):
    def discover_services(self) -> List[ServiceInfo]
    def discover_network_config(self) -> NetworkTopology
    def discover_configurations(self) -> ConfigurationMap
    def discover_automation_scripts(self) -> ScriptRegistry
```

#### Service Discovery
- **Process Scanner**: Identifies running services and their ports
- **Configuration Parser**: Extracts service configurations and dependencies
- **Network Analyzer**: Maps network connections and routing rules
- **File System Scanner**: Discovers configuration files and scripts

#### Enhanced Data Models with Versioning and Validation
```python
@dataclass
class ServiceInfo:
    name: str
    process_id: int
    port: int
    config_files: List[str]
    dependencies: List[str]
    health_endpoint: Optional[str]
    # Versioning and validation fields
    created_at: datetime
    updated_at: datetime
    version: str
    last_validated: Optional[datetime]
    validation_status: ValidationStatus
    validation_errors: List[str]
    changed_by: str
    change_reason: Optional[str]

@dataclass
class NetworkTopology:
    services: List[ServiceInfo]
    connections: List[NetworkConnection]
    dns_records: List[DNSRecord]
    routing_rules: List[RoutingRule]
    # Versioning and validation fields
    created_at: datetime
    updated_at: datetime
    version: str
    last_validated: Optional[datetime]
    validation_status: ValidationStatus
    accuracy_score: float  # 0.0-1.0 confidence in accuracy

@dataclass
class ValidationStatus:
    is_valid: bool
    last_check: datetime
    next_check_due: datetime
    confidence_score: float
    requires_manual_verification: bool
```

### 2. Relationship Mapper

#### Core Interfaces
```python
class RelationshipMapper(ReflectiveModule):
    def map_service_dependencies(self, services: List[ServiceInfo]) -> DependencyGraph
    def trace_data_flows(self, topology: NetworkTopology) -> DataFlowMap
    def analyze_automation_chains(self, scripts: ScriptRegistry) -> AutomationGraph
    def map_script_to_components(self, scripts: ScriptRegistry) -> ScriptComponentMapping
    def analyze_makefile_targets(self, makefile_path: str) -> MakefileTargetMapping
```

#### Dependency Analysis
- **Configuration Analysis**: Parses service configs for dependency declarations
- **Network Tracing**: Follows network connections to identify service relationships
- **Data Flow Mapping**: Traces metrics from collection to visualization
- **Automation Mapping**: Links scripts to their target infrastructure components

#### Script and Automation Mapping (Requirement 4)

**Python Script to Component Mapping** (Requirement 4.1):
```python
@dataclass
class ScriptComponentMapping:
    script_mappings: Dict[str, List[str]] = field(default_factory=lambda: {
        "observatory-daemon.py": ["Observatory server lifecycle management", "WebSocket endpoints", "ReflectiveModule health monitoring"],
        "tunnel management scripts": ["Cloudflare tunnel operations", "DNS routing", "Ingress rule management"],
        "prometheus integration scripts": ["Metrics collection", "Scrape target validation", "Alert rule management"],
        "grafana configuration scripts": ["Dashboard management", "Datasource configuration", "Visualization setup"],
        "Redis coordination scripts": ["Multi-node communication", "Failover management", "State synchronization"],
        "ReflectiveModule-based services": ["Systematic observability", "Health monitoring", "Metrics exposure"]
    })
    
    def get_script_impact(self, script_path: str) -> List[str]:
        """Return list of components affected by script changes"""
        pass
```

**Makefile Target to Infrastructure Mapping** (Requirement 4.2):
```python
@dataclass
class MakefileTargetMapping:
    target_mappings: Dict[str, List[str]] = field(default_factory=lambda: {
        "tunnel-start": ["Cloudflare tunnel (d1e53e43-033f-4994-8f46-c83962ae3785)", "DNS propagation", "Ingress rules"],
        "tunnel-stop": ["Cloudflare tunnel termination", "DNS cleanup", "Connection cleanup"],
        "dashboard-up": ["Observatory server (localhost:8888)", "WebSocket endpoints", "ReflectiveModule initialization"],
        "dashboard-stop": ["Observatory server shutdown", "WebSocket cleanup", "Metrics deregistration"],
        "dashboard-restart": ["Observatory server restart", "Connection restoration", "Health verification"],
        "dashboard-status": ["Health check execution", "Service validation", "Connectivity testing"],
        "dashboard-logs": ["Log aggregation", "Error analysis", "Performance monitoring"],
        "prometheus-start": ["Metrics collection (localhost:9090)", "Scrape target registration", "Alert rules"],
        "prometheus-stop": ["Metrics collection shutdown", "Target deregistration", "Data persistence"],
        "grafana-start": ["Visualization (localhost:3000)", "Datasource configuration", "Dashboard loading"],
        "grafana-stop": ["Grafana shutdown", "Session cleanup", "Configuration persistence"],
        "task-*": ["Specific Beast Mode components", "Component-specific operations", "Dependency validation"],
        "phase-*": ["Coordinated multi-component operations", "Dependency ordering", "Validation checkpoints"]
    })
    
    dependency_chains: Dict[str, List[str]] = field(default_factory=lambda: {
        "task-3.4": ["task-3.3", "task-3.2", "task-3.1"],  # Example dependency chain
        "dashboard-restart": ["dashboard-stop", "dashboard-up"],
        "phase-2": ["phase-1-complete", "infrastructure-validated"]
    })
```

**Automation Chain Analysis** (Requirement 4.3):
```python
@dataclass
class AutomationChainAnalysis:
    makefile_dependencies: Dict[str, List[str]]  # target -> [dependencies]
    script_parameters: Dict[str, List[Parameter]]  # script -> [parameters]
    environment_requirements: Dict[str, List[str]]  # script -> [env_vars]
    reflective_module_sequences: List[InitializationStep]
    websocket_registration_deps: Dict[str, List[str]]  # endpoint -> [dependencies]
    metrics_pipeline_deps: List[MetricsDependency]
    integration_coordination: Dict[str, str]  # ACE Reporter → AI Memory Palace → DAG Registry
    
    def analyze_downstream_impact(self, component: str) -> ImpactAnalysis:
        """Analyze downstream impact of component changes"""
        pass
```

**Downstream Impact Analysis** (Requirement 4.4):
```python
@dataclass
class ImpactAnalysis:
    primary_effects: List[str]  # Direct component impacts
    secondary_effects: List[str]  # Cascading effects
    affected_endpoints: List[str]  # WebSocket/HTTP endpoints affected
    affected_metrics: List[str]  # Metrics that will be impacted
    affected_integrations: List[str]  # Integration points affected
    
    # Specific impact scenarios
    observatory_daemon_changes: List[str] = field(default_factory=lambda: [
        "WebSocket endpoint availability (/ws/observatory, /ws/emoji-rain, /ws/anomalies, /ws/doctor-status)",
        "Metrics exposure (/metrics, /health, /ready)",
        "ReflectiveModule health monitoring",
        "Integration point connectivity (ACE Reporter, AI Memory Palace, DAG Registry)"
    ])
    
    tunnel_config_changes: List[str] = field(default_factory=lambda: [
        "DNS routing (observatory.nkllon.com, grafana.observatory.nkllon.com, prometheus.observatory.nkllon.com)",
        "Ingress rules and service routing",
        "WebSocket proxy configuration",
        "SSL/TLS certificate validation"
    ])
    
    prometheus_config_changes: List[str] = field(default_factory=lambda: [
        "Scrape targets and collection intervals",
        "Alert rules and notification routing",
        "Metrics retention and storage policies",
        "Grafana datasource connectivity"
    ])
    
    grafana_changes: List[str] = field(default_factory=lambda: [
        "Datasource connectivity (Prometheus localhost:9090)",
        "Dashboard availability and rendering",
        "Alert notification channels",
        "User authentication and authorization"
    ])
    
    reflective_module_changes: List[str] = field(default_factory=lambda: [
        "Systematic observability across all Beast Mode components",
        "Health endpoint standardization (/health, /ready, /metrics)",
        "Metrics collection and exposure patterns",
        "Error handling and correlation ID tracking"
    ])
```

### 3. UML Diagram Generator

#### Core Interfaces
```python
class DiagramGenerator(ReflectiveModule):
    def generate_component_diagram(self, topology: NetworkTopology) -> str
    def generate_sequence_diagrams(self, use_cases: List[UseCase]) -> List[str]
    def generate_network_topology(self, network: NetworkTopology) -> str
    def generate_data_flow_diagram(self, flows: DataFlowMap) -> str
```

#### Diagram Types (Requirements 1, 2)

**Static Component Diagrams** (Requirement 1.1):
- **Complete UML component diagram** with 100% service coverage from discovery scan
- **All documented integration points**: ACE Reporter, AI Memory Palace, DAG Registry with connection details
- **All WebSocket endpoints** with their message types: /ws/observatory (system events), /ws/emoji-rain (coordination), /ws/anomalies (alerts), /ws/doctor-status (health)
- **Component health status indicators** with real-time status from ReflectiveModule endpoints
- **Beast Mode framework integration** showing systematic observability patterns

**Sequence Diagrams** (Requirement 2.1, 2.2, 2.3):
- **tunnel-start/tunnel-stop operations** with DNS propagation timing estimates (30-60 seconds)
- **dashboard-up/dashboard-stop/dashboard-restart lifecycle** with validation checkpoints at each step
- **dashboard-status health check flows** with specific success/failure criteria and timeout values (5s per endpoint)
- **Emergency protocol activation and recovery procedures** with systematic error handling correlation IDs
- **Complete interaction chains** from Makefile target execution through service health verification

**Network Topology Diagrams** (Requirement 1.3, 5.1):
- **Physical and logical network layout** with IP allocations (192.168.1.x) and port mappings
- **Complete IP address allocations**: Observatory:8888, Prometheus:9090, Grafana:3000
- **Service port assignments** with protocol specifications (HTTP/HTTPS/WebSocket)
- **Redis coordination endpoints** (192.168.1.119:6379 primary, localhost:6380 fallback)
- **Cloudflare tunnel ingress rule configurations** with specific routing logic for each subdomain

**Data Flow Diagrams** (Requirement 1.4, 6.1, 6.2, 6.3):
- **Metrics flow from ReflectiveModule components** through Observatory to Prometheus and Grafana
- **Performance characteristics documented** including collection intervals and retention policies
- **WebSocket real-time metrics streaming** parallel to batch collection pipelines
- **Integration metrics flow**: ACE Reporter → AI Memory Palace → DAG Registry coordination
- **Error propagation through systematic error handling** with correlation ID tracking

**Use Case Diagrams** (Requirement 3.1):
- **Common operational scenarios** for all 50+ Makefile targets
- **Troubleshooting workflows** with decision trees and resolution paths
- **Emergency response procedures** with escalation paths and contact information
- **Maintenance workflows** including configuration changes and rolling updates

### 4. Documentation Orchestrator

#### Core Interfaces
```python
class DocumentationOrchestrator(ReflectiveModule):
    def generate_full_documentation(self) -> DocumentationPackage
    def update_diagrams(self) -> None
    def validate_documentation_accuracy(self) -> ValidationReport
    def schedule_periodic_updates(self) -> None
```

#### Orchestration Workflow
1. **Discovery Phase**: Scan infrastructure and collect current state
   - Identify running services and their configurations
   - Map Makefile targets to infrastructure components
   - Discover Python automation scripts and their dependencies
   - Catalog WebSocket endpoints and health check routes
2. **Analysis Phase**: Map relationships and dependencies
   - Trace service dependencies and data flows
   - Analyze automation chains and script interactions
   - Map ReflectiveModule integration patterns
   - Identify integration points (ACE Reporter, AI Memory Palace, DAG Registry)
3. **Generation Phase**: Create UML diagrams and comprehensive documentation
   - Generate component diagrams with Beast Mode framework context
   - Create sequence diagrams for operational workflows
   - Build network topology maps with IP/port details
   - Produce use case documentation for common scenarios
4. **Validation Phase**: Verify accuracy against live system
   - Test generated documentation against actual system behavior
   - Validate automation script mappings
   - Confirm network connectivity and routing
5. **Publication Phase**: Update documentation repositories and CMS integration

## Use Case and Operational Workflow Design

### Critical Use Cases (Requirement 3)

#### 1. Tunnel Management Workflows
**tunnel-start Operation Sequence** (Requirement 3.1):
1. Makefile target execution with dependency validation
2. Cloudflare tunnel (d1e53e43-033f-4994-8f46-c83962ae3785) startup
3. DNS propagation verification (observatory.nkllon.com, grafana.observatory.nkllon.com, prometheus.observatory.nkllon.com)
4. Ingress rule activation and routing validation
5. Service health verification through ReflectiveModule endpoints
6. WebSocket endpoint registration and connectivity testing

**Expected Outcomes and Validation Steps** (Requirement 3.2):
- Makefile target `tunnel-start` executes with exit code 0
- DNS propagation completes within 30-60 seconds
- All health endpoints (`/health`, `/ready`, `/metrics`) return 200 status
- WebSocket endpoints accept connections and respond to ping frames
- Integration point confirmations: ACE Reporter connectivity, AI Memory Palace access, DAG Registry validation

**tunnel-stop Operation Sequence** (Requirement 3.1):
1. Graceful WebSocket connection termination
2. Service health check suspension
3. Tunnel process termination
4. DNS propagation cleanup
5. Resource cleanup and validation

#### 2. Observatory Service Lifecycle
**dashboard-up Operation Sequence** (Requirement 3.1):
1. observatory-daemon.py startup with environment validation
2. ReflectiveModule initialization and health endpoint registration
3. Prometheus scrape target registration and metrics endpoint exposure
4. Grafana datasource configuration and connectivity validation
5. WebSocket endpoint establishment (/ws/observatory, /ws/emoji-rain, /ws/anomalies, /ws/doctor-status)
6. Real-time metrics streaming activation
7. Integration point verification (ACE Reporter, AI Memory Palace, DAG Registry)

**Expected Log Outputs and Success Indicators** (Requirement 3.2):
- `observatory-daemon.py` logs "ReflectiveModule initialized successfully"
- Prometheus logs "Target registered: observatory:8888/metrics"
- Grafana logs "Datasource connection established"
- WebSocket logs show successful endpoint registration for all four endpoints
- Metrics collection validation shows data flowing from Observatory to Prometheus

**dashboard-status Health Check Flow** (Requirement 3.1):
1. Makefile target execution
2. Python script health validation
3. ReflectiveModule health endpoints verification (/health, /ready, /metrics)
4. Prometheus target status validation
5. Grafana datasource connectivity testing
6. WebSocket connection status verification
7. Tunnel connectivity validation
8. Redis coordination status (192.168.1.119:6379 with localhost:6380 fallback)

**dashboard-restart Operation Sequence** (Requirement 3.1):
1. Graceful shutdown of existing Observatory processes
2. WebSocket connection cleanup and client notification
3. Prometheus scrape target deregistration
4. Process restart with configuration validation
5. Service reinitialization following dashboard-up sequence
6. Connection restoration and health verification

#### 3. Emergency and Recovery Procedures
**System Recovery Procedures** (Requirement 3.1):

**Redis Failover Sequence**:
1. Primary Redis connection failure detection (192.168.1.119:6379)
2. Automatic failover to localhost:6380
3. Connection pool reconfiguration
4. Coordination state synchronization
5. Service notification of failover completion

**WebSocket Reconnection Procedure**:
1. Connection failure detection with correlation ID logging
2. Client notification of impending reconnection
3. Connection cleanup and resource deallocation
4. Exponential backoff reconnection attempts
5. Session state restoration and client resubscription

**Tunnel Restoration Procedure**:
1. Tunnel connectivity failure detection
2. DNS propagation status verification
3. Cloudflare Edge connectivity testing
4. Tunnel process restart with credential validation
5. Ingress rule reactivation and service health verification

**Emergency Protocols** (Requirement 3.1):

**Service Isolation Procedure**:
1. Fault detection through ReflectiveModule health monitoring
2. Service isolation to prevent cascade failures
3. Load balancer reconfiguration (if applicable)
4. Alternative service activation
5. Incident escalation and notification

**Fallback Activation Procedure**:
1. Primary service failure confirmation
2. Fallback service health verification
3. Traffic redirection to fallback systems
4. Performance monitoring and capacity validation
5. Recovery planning and primary service restoration

**Systematic Error Handling Flow** (Requirement 3.4):
1. ReflectiveModule error capture with correlation IDs
2. Structured logging with context preservation
3. ACE Reporter broadcasting for coordination
4. AI Memory Palace context storage for analysis
5. Emergency protocol activation based on error severity
6. Fallback mechanism engagement (Redis failover, WebSocket reconnection)
7. Recovery procedure execution with validation steps

#### 4. Maintenance and Configuration Management Procedures (Requirement 3.4)

**CMS-Based Configuration Management through Directus**:
1. Configuration change request through Directus interface (localhost:8055)
2. Schema validation and approval workflow
3. Version control commit with change tracking
4. Staged deployment with validation checkpoints
5. Production deployment with rollback capability
6. Post-deployment validation and monitoring

**Version Control Workflows for Tunnel Configurations**:
1. Configuration file modification with version tagging
2. Git commit with descriptive change message
3. Automated testing of configuration syntax
4. Staging environment deployment and validation
5. Production deployment with DNS propagation monitoring
6. Configuration backup and rollback preparation

**Rolling Updates for Observatory Services**:
1. Health check validation of current service state
2. New version deployment to staging environment
3. Load balancer configuration for gradual traffic shift
4. Real-time monitoring of service performance metrics
5. Rollback trigger conditions and automated rollback
6. Post-update validation and performance verification

**Coordination with Existing Beast Mode Components**:
1. Dependency analysis and impact assessment
2. Component notification of planned changes
3. Coordinated shutdown and startup sequences
4. Integration point validation and testing
5. System-wide health verification
6. Documentation updates and team notification

### Troubleshooting Guide Structure (Requirement 3.3)

#### Error Propagation Paths with Specific Error Codes

**WebSocket Connection Failures** (Requirement 3.3):
- **Connection establishment** → Error Code WS001: "Connection refused"
- **Authentication** → Error Code WS002: "Authentication failed" 
- **Protocol upgrade** → Error Code WS003: "WebSocket upgrade failed"
- **Error classification** → Error Code WS004: "Unknown WebSocket error"
- **Recovery procedure** → Exponential backoff reconnection with correlation ID tracking

**Tunnel Connectivity Issues** (Requirement 3.3):
- **DNS resolution** → Error Code TUN001: "DNS resolution failed for observatory.nkllon.com"
- **Cloudflare Edge** → Error Code TUN002: "Cloudflare Edge unreachable"
- **Tunnel authentication** → Error Code TUN003: "Tunnel authentication failed"
- **Ingress routing** → Error Code TUN004: "Ingress rule routing failed"
- **Service connectivity** → Error Code TUN005: "Backend service unreachable"

**Metrics Collection Problems** (Requirement 3.3):
- **ReflectiveModule registration** → Error Code MET001: "Metrics endpoint registration failed"
- **Prometheus scraping** → Error Code MET002: "Prometheus scrape target unreachable"
- **Data validation** → Error Code MET003: "Metrics data validation failed"
- **Grafana visualization** → Error Code MET004: "Grafana datasource connection failed"

**Redis Coordination Failures** (Requirement 3.3):
- **Primary connection (192.168.1.119:6379)** → Error Code RED001: "Primary Redis connection failed"
- **Automatic failover** → Error Code RED002: "Redis failover initiated"
- **Secondary connection (localhost:6380)** → Error Code RED003: "Fallback Redis connection failed"
- **Coordination recovery** → Error Code RED004: "Redis coordination state recovery failed"

#### Specific Error Codes and Resolution Paths (Requirement 3.3)

**DNS Resolution Failures**:
- **TUN001**: Check Cloudflare DNS propagation status, clear local DNS cache, verify tunnel configuration
- **Resolution Steps**: `nslookup observatory.nkllon.com`, `dig observatory.nkllon.com`, restart tunnel service
- **Expected Resolution Time**: 5-15 minutes for DNS propagation

**WebSocket Protocol Errors**:
- **WS003**: Verify HTTP/HTTPS protocol compatibility, check proxy configurations, validate WebSocket headers
- **Resolution Steps**: Check nginx configuration, verify SSL/TLS certificates, test direct connection
- **Expected Resolution Time**: 1-5 minutes for configuration fixes

**Prometheus Scraping Issues**:
- **MET002**: Verify target registration, check network connectivity, validate metrics endpoint availability
- **Resolution Steps**: Check Prometheus configuration, verify service discovery, restart Prometheus service
- **Expected Resolution Time**: 2-10 minutes depending on service restart requirements

**ReflectiveModule Health Check Failures**:
- **Service initialization problems**: Check dependency availability, verify configuration files, validate environment variables
- **Dependency unavailability**: Verify Redis connectivity, check Directus CMS availability, validate network routing
- **Resource constraints**: Check memory usage, verify CPU availability, validate disk space
- **Resolution Steps**: Restart services in dependency order, verify resource allocation, check system logs
- **Expected Resolution Time**: 5-20 minutes depending on resource availability

#### Systematic Error Handling Procedures (Requirement 3.3)

**ReflectiveModule Systematic Error Handling**:
1. Error capture with correlation ID generation
2. Structured logging with context preservation
3. Health endpoint status update (`/health` returns 503)
4. Metrics emission for error tracking
5. Automatic retry with exponential backoff
6. Escalation to operations team if retry limit exceeded

**WebSocket Connection Recovery Steps**:
1. Connection failure detection with timestamp logging
2. Client notification of connection loss
3. Connection cleanup and resource deallocation
4. Exponential backoff reconnection (1s, 2s, 4s, 8s, 16s, max 60s)
5. Session state restoration from Redis coordination
6. Client resubscription to previous channels

**Tunnel Connectivity Diagnostics**:
1. DNS resolution testing for all subdomains
2. Cloudflare Edge connectivity verification
3. Tunnel process health check
4. Ingress rule validation
5. Backend service connectivity testing
6. End-to-end WebSocket connectivity verification

**Grafana Datasource Problems**:
1. Prometheus connectivity testing from Grafana container
2. Datasource configuration validation
3. Query execution testing with sample metrics
4. Dashboard rendering verification
5. Alert rule functionality testing
6. Performance metrics validation

## Security and Access Control Design

### Authentication and Authorization Framework (Requirement 8)

#### Security Architecture
The system implements multi-layered security controls across all infrastructure components:

**Service Authentication**:
- **Cloudflare Tunnel**: Certificate-based authentication with automatic rotation
- **Observatory WebSocket**: Token-based authentication with session management
- **Prometheus/Grafana**: Basic authentication with role-based access control
- **Redis Coordination**: Password authentication with connection encryption

**Credential Management**:
- **Tunnel Credentials**: Stored in secure credential files with restricted file permissions
- **API Keys**: Environment variable storage with rotation tracking
- **Database Credentials**: Encrypted storage in Directus CMS with audit trails
- **Service Tokens**: JWT-based tokens with configurable expiration

#### Access Control Matrix
```python
@dataclass
class AccessControlMatrix:
    service_name: str
    authentication_method: str  # certificate, token, basic_auth, password
    authorization_roles: List[str]  # admin, operator, readonly, monitor
    credential_rotation_schedule: str  # daily, weekly, monthly
    audit_requirements: List[str]
    isolation_procedures: List[str]

@dataclass
class SecurityIncidentResponse:
    incident_type: str
    isolation_steps: List[str]
    forensic_data_collection: List[str]
    escalation_contacts: List[str]
    recovery_procedures: List[str]
```

#### Security Monitoring Integration (Requirement 8)

**Authentication Mechanisms Documentation (Requirement 8.1)**:
```python
@dataclass
class AuthenticationDocumentation:
    service_name: str
    auth_mechanisms: List[AuthMechanism] = field(default_factory=lambda: [
        AuthMechanism(
            type="cloudflare_tunnel_certificate",
            service="Cloudflare Tunnel (d1e53e43-033f-4994-8f46-c83962ae3785)",
            rotation_schedule="90 days",
            validation_endpoint="/tunnel/health",
            access_control_matrix=["tunnel_admin", "infrastructure_read"]
        ),
        AuthMechanism(
            type="prometheus_basic_auth",
            service="Prometheus (localhost:9090)",
            rotation_schedule="30 days", 
            validation_endpoint="/api/v1/status/config",
            access_control_matrix=["metrics_read", "metrics_admin"]
        ),
        AuthMechanism(
            type="grafana_session_auth",
            service="Grafana (localhost:3000)",
            rotation_schedule="24 hours",
            validation_endpoint="/api/health",
            access_control_matrix=["dashboard_read", "dashboard_admin"]
        ),
        AuthMechanism(
            type="redis_auth_token",
            service="Redis Coordination (192.168.1.119:6379)",
            rotation_schedule="7 days",
            validation_endpoint="PING command",
            access_control_matrix=["coordination_read", "coordination_write"]
        )
    ])

@dataclass
class AuthMechanism:
    type: str
    service: str
    rotation_schedule: str
    validation_endpoint: str
    access_control_matrix: List[str]
    credential_storage_method: str = "environment_variables"
    audit_trail_enabled: bool = True
```

**Credential Management and Rotation (Requirement 8.2)**:
- **Tunnel Credentials**: Cloudflare tunnel credentials rotated every 90 days with automated validation
- **API Keys**: Prometheus and Grafana API keys rotated every 30 days with health check validation
- **Redis Authentication**: Redis AUTH tokens rotated weekly with automatic failover testing
- **Secrets Management**: Integration with environment variables and optional vault systems
- **Rotation Validation**: All credential rotations validated through service health endpoints

**Access Control Documentation (Requirement 8.3)**:
```python
@dataclass
class AccessControlMatrix:
    role_permissions: Dict[str, List[str]] = field(default_factory=lambda: {
        "infrastructure_admin": [
            "tunnel_management", "dns_configuration", "service_restart",
            "configuration_write", "credential_rotation", "emergency_procedures"
        ],
        "monitoring_operator": [
            "metrics_read", "dashboard_access", "alert_configuration",
            "health_check_execution", "performance_analysis"
        ],
        "developer": [
            "service_logs", "health_endpoints", "metrics_read",
            "documentation_access", "troubleshooting_guides"
        ],
        "security_auditor": [
            "audit_trail_access", "security_metrics", "compliance_reports",
            "access_control_review", "incident_investigation"
        ]
    })
    
    sensitive_components: List[str] = field(default_factory=lambda: [
        "Cloudflare tunnel credentials",
        "Redis coordination endpoints", 
        "Prometheus configuration",
        "Grafana admin access",
        "Observatory WebSocket endpoints"
    ])

@dataclass
class AuditTrail:
    event_timestamp: datetime
    user_id: str
    action: str
    component: str
    correlation_id: str
    success: bool
    ip_address: str
    user_agent: str
```

**Security Incident Response (Requirement 8.4)**:
```python
@dataclass
class SecurityIncidentResponse:
    incident_types: Dict[str, IncidentProcedure] = field(default_factory=lambda: {
        "unauthorized_access": IncidentProcedure(
            isolation_steps=["Disable compromised credentials", "Block IP address", "Rotate affected keys"],
            forensic_collection=["Access logs", "Authentication attempts", "Network traffic"],
            escalation_contacts=["security_team", "infrastructure_admin"],
            recovery_procedures=["Credential rotation", "Service restart", "Security validation"]
        ),
        "credential_compromise": IncidentProcedure(
            isolation_steps=["Immediate credential revocation", "Service isolation", "Traffic analysis"],
            forensic_collection=["Credential usage logs", "Service access patterns", "Configuration changes"],
            escalation_contacts=["security_team", "compliance_officer"],
            recovery_procedures=["Full credential rotation", "Access control review", "Audit trail analysis"]
        ),
        "service_compromise": IncidentProcedure(
            isolation_steps=["Service shutdown", "Network isolation", "Process termination"],
            forensic_collection=["System logs", "Process memory", "Network connections", "File modifications"],
            escalation_contacts=["incident_commander", "security_team", "infrastructure_admin"],
            recovery_procedures=["Clean service restoration", "Configuration validation", "Security hardening"]
        )
    })

@dataclass
class IncidentProcedure:
    isolation_steps: List[str]
    forensic_collection: List[str]
    escalation_contacts: List[str]
    recovery_procedures: List[str]
    max_response_time_minutes: int = 15
    documentation_requirements: List[str] = field(default_factory=lambda: [
        "Incident timeline", "Actions taken", "Evidence collected", "Lessons learned"
    ])
```

**Security Monitoring Integration**:
- **ReflectiveModule Security Metrics**: Authentication failures, unauthorized access attempts with correlation IDs
- **Audit Trail Generation**: All access events logged with correlation IDs and stored for compliance
- **Anomaly Detection**: Integration with Observatory WebSocket for real-time security alerts
- **Compliance Reporting**: Automated generation of security compliance reports with audit trail evidence

## Metrics and Observability Flow Design

### Comprehensive Observability Pipeline (Requirement 6)

#### Observatory Metrics Exposure to Prometheus (Requirement 6.1)

**ReflectiveModule Automatic Metrics Registration**:
```python
@dataclass
class ObservatoryMetricsConfig:
    automatic_registration: bool = True
    metrics_endpoints: List[str] = field(default_factory=lambda: ["/metrics", "/health", "/ready"])
    websocket_metrics: Dict[str, str] = field(default_factory=lambda: {
        "/ws/observatory": "observatory_websocket_connections",
        "/ws/emoji-rain": "emoji_rain_websocket_connections", 
        "/ws/anomalies": "anomaly_websocket_connections",
        "/ws/doctor-status": "doctor_status_websocket_connections"
    })
    beast_mode_error_metrics: List[str] = field(default_factory=lambda: [
        "beast_mode_errors_total",
        "beast_mode_correlation_ids_active",
        "beast_mode_systematic_recoveries_total"
    ])
    integration_metrics: Dict[str, str] = field(default_factory=lambda: {
        "ace_reporter_connections": "ace_reporter_connection_status",
        "ai_memory_palace_operations": "ai_memory_palace_operations_total",
        "dag_registry_validations": "dag_registry_validations_total"
    })
```

**WebSocket Connection Metrics and Real-Time Performance Indicators**:
- Connection count per endpoint with historical trends
- Message throughput rates (messages/second) per WebSocket endpoint
- Connection duration and session persistence metrics
- Error rates and reconnection frequency tracking
- Real-time latency measurements for WebSocket message delivery

#### Grafana Query Patterns for Prometheus Integration (Requirement 6.2)

**Datasource Configuration for Prometheus (localhost:9090)**:
```yaml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://localhost:9090
    access: proxy
    isDefault: true
    jsonData:
      timeInterval: "5s"
      queryTimeout: "60s"
      httpMethod: "POST"
```

**Query Patterns for ReflectiveModule Metrics Across Beast Mode Components**:
```promql
# System-wide ReflectiveModule health
up{job="reflective_modules"}

# WebSocket connection metrics
sum(rate(websocket_connections_total[5m])) by (endpoint)

# Beast Mode error correlation
increase(beast_mode_errors_total[1h]) and on() beast_mode_correlation_ids_active > 0

# Integration point health
(ace_reporter_connection_status + ai_memory_palace_connection_status + dag_registry_connection_status) / 3
```

**System Performance Metrics with Automatic Alerting**:
- CPU usage across all Beast Mode components with threshold alerting (>80%)
- Memory consumption patterns with leak detection algorithms
- Network I/O rates for WebSocket and HTTP traffic
- Disk usage trends with capacity planning projections
- Service health indicators with automatic incident creation

#### Metric Collection Intervals and Retention Policies (Requirement 6.3)

**Prometheus Scrape Intervals by Service Type**:
```yaml
scrape_configs:
  - job_name: 'observatory'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:8888']
  
  - job_name: 'reflective_modules'
    scrape_interval: 10s
    static_configs:
      - targets: ['localhost:8888', 'localhost:9090', 'localhost:3000']
  
  - job_name: 'websocket_endpoints'
    scrape_interval: 2s  # High frequency for real-time monitoring
    metrics_path: '/ws/metrics'
    static_configs:
      - targets: ['localhost:8888']
```

**ReflectiveModule Metrics Collection Frequency**:
- Health endpoint checks: Every 5 seconds
- Performance metrics: Every 10 seconds  
- Error and correlation tracking: Every 1 second
- Integration point status: Every 30 seconds

**Long-Term Storage Policies and Historical Analysis**:
- High-resolution data (5s intervals): Retained for 7 days
- Medium-resolution data (1m intervals): Retained for 30 days
- Low-resolution data (5m intervals): Retained for 1 year
- Correlation analysis data: Retained for 90 days with compression

#### Complete Observability Data Pipeline (Requirement 6.4)

**ReflectiveModule → Observatory → Prometheus → Grafana Flow**:
```python
@dataclass
class ObservabilityPipeline:
    stages: List[PipelineStage] = field(default_factory=lambda: [
        PipelineStage(
            name="ReflectiveModule Collection",
            description="Automatic metrics registration and health monitoring",
            inputs=["service_metrics", "health_status", "error_events"],
            outputs=["structured_metrics", "correlation_ids"],
            latency_target="<100ms"
        ),
        PipelineStage(
            name="Observatory Aggregation", 
            description="Central collection and WebSocket streaming",
            inputs=["structured_metrics", "websocket_events"],
            outputs=["prometheus_metrics", "real_time_streams"],
            latency_target="<200ms"
        ),
        PipelineStage(
            name="Prometheus Scraping",
            description="Time-series storage and alerting",
            inputs=["prometheus_metrics"],
            outputs=["time_series_data", "alert_triggers"],
            latency_target="<5s"
        ),
        PipelineStage(
            name="Grafana Visualization",
            description="Dashboard rendering and user interface",
            inputs=["time_series_data", "real_time_streams"],
            outputs=["dashboards", "user_alerts"],
            latency_target="<1s"
        )
    ])
    
    parallel_streams: Dict[str, str] = field(default_factory=lambda: {
        "websocket_real_time": "Direct WebSocket streaming for immediate alerts",
        "batch_collection": "Traditional Prometheus scraping for historical analysis",
        "correlation_tracking": "Error correlation with AI Memory Palace integration"
    })
```

**Integration with ACE Reporter and AI Memory Palace**:
- ACE Reporter: Progress broadcasting for coordination events
- AI Memory Palace: Context storage for error analysis and pattern recognition
- DAG Registry: Dependency validation metrics and orchestration health
- Fallback mechanisms: Local storage when integration points unavailable

**Diagnostic Procedures for Each Pipeline Stage**:
1. **ReflectiveModule Stage**: Health endpoint validation, metrics endpoint accessibility
2. **Observatory Stage**: WebSocket connectivity, aggregation performance, real-time streaming
3. **Prometheus Stage**: Scrape target health, storage performance, alert rule evaluation
4. **Grafana Stage**: Datasource connectivity, dashboard rendering, query performance

## Deployment and Configuration Management Design

### Deployment Orchestration Framework (Requirement 7)

#### Multi-Modal Deployment Architecture
The system supports three deployment patterns with consistent health check integration:

**Docker Container Deployment**:
- **Observatory Services**: Containerized with health check endpoints
- **Prometheus/Grafana**: Docker Compose orchestration with volume persistence
- **Configuration Management**: Environment-specific configuration injection
- **Health Integration**: Container health checks integrated with ReflectiveModule endpoints

**Host Process Deployment**:
- **Python Services**: Direct host execution with systemd integration
- **Tunnel Services**: Native cloudflared process management
- **Configuration Management**: File-based configuration with version control
- **Health Integration**: Process monitoring with automatic restart capabilities

**Cloud Service Integration**:
- **Cloudflare Services**: API-based configuration management
- **DNS Management**: Automated DNS record updates with propagation validation
- **Certificate Management**: Automatic SSL/TLS certificate provisioning and renewal
- **Health Integration**: Cloud service health monitoring with local fallback

#### DAG-Based Deployment Orchestration (Requirement 7.3)
```python
@dataclass
class DeploymentDAG:
    deployment_id: str
    dependency_graph: Dict[str, List[str]]  # service -> [dependencies]
    deployment_steps: List[DeploymentStep]
    validation_checkpoints: List[ValidationCheckpoint]
    rollback_procedures: List[RollbackStep]
    success_criteria: List[SuccessCriterion]
    mathematical_validation: DAGValidationResult
    
    def validate_dag_compliance(self) -> DAGValidationResult:
        """Mathematical validation of deployment dependencies (Requirement 7.3)"""
        # Detect cycles in dependency graph
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check all nodes for cycles
        for node in self.dependency_graph:
            if node not in visited:
                if has_cycle(node):
                    return DAGValidationResult(
                        is_valid=False,
                        error="Circular dependency detected",
                        topological_order=None
                    )
        
        # Generate topological ordering for deployment sequence
        topo_order = self._topological_sort()
        return DAGValidationResult(
            is_valid=True,
            error=None,
            topological_order=topo_order
        )
    
    def _topological_sort(self) -> List[str]:
        """Generate mathematically correct deployment order"""
        in_degree = {node: 0 for node in self.dependency_graph}
        for node in self.dependency_graph:
            for neighbor in self.dependency_graph[node]:
                in_degree[neighbor] += 1
        
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result

@dataclass
class DAGValidationResult:
    is_valid: bool
    error: Optional[str]
    topological_order: Optional[List[str]]
    dependency_depth: int = 0
    parallel_execution_groups: List[List[str]] = field(default_factory=list)

@dataclass
class DeploymentStep:
    step_id: str
    service_name: str
    deployment_method: str  # container, host_process, cloud_service
    configuration_source: str  # directus, file, environment
    health_check_endpoint: str
    timeout_seconds: int
    retry_policy: RetryPolicy
```

#### CMS-Based Configuration Management (ADR-010)
**Directus Availability Constraint**: This feature requires Directus CMS at localhost:8055

- **Directus Integration**: Centralized configuration storage with version control (when available)
- **Environment-Specific Configs**: Development, staging, production configuration management
- **Configuration Validation**: Schema validation before deployment
- **Change Tracking**: Audit trails for all configuration modifications
- **Rollback Capabilities**: Configuration rollback with dependency validation
- **Fallback Mode**: File-based configuration when Directus unavailable

```python
@dataclass
class ConfigurationManagementMode:
    mode: str  # "directus", "file_based", "hybrid"
    directus_available: bool
    capabilities: List[str]
    limitations: List[str]

def determine_configuration_mode() -> ConfigurationManagementMode:
    """Determine configuration management mode based on Directus availability"""
    try:
        response = requests.get("http://localhost:8055/server/ping", timeout=5)
        if response.text.strip() == "pong":
            return ConfigurationManagementMode(
                mode="directus",
                directus_available=True,
                capabilities=["version_control", "audit_trails", "schema_validation", "rollback"],
                limitations=[]
            )
    except Exception:
        pass
    
    return ConfigurationManagementMode(
        mode="file_based",
        directus_available=False,
        capabilities=["basic_storage", "file_versioning"],
        limitations=["no_audit_trails", "limited_rollback", "manual_schema_validation"]
    )
```

### Resource Requirements and Scaling Constraints
```python
@dataclass
class ScalingConstraints:
    min_instances: int
    max_instances: int
    cpu_limits: ResourceLimit
    memory_limits: ResourceLimit
    network_bandwidth: ResourceLimit
    storage_requirements: StorageRequirement
    performance_benchmarks: List[PerformanceBenchmark]
```

## Disaster Recovery and Operational Runbooks

### Disaster Recovery Framework (Requirement 9)

#### RTO/RPO Requirements by Service
```python
@dataclass
class RecoveryObjectives:
    service_name: str
    rto_minutes: int  # Recovery Time Objective
    rpo_minutes: int  # Recovery Point Objective
    criticality_level: str  # critical, high, medium, low
    backup_frequency: str
    recovery_validation_steps: List[str]
    dependencies: List[str]

# Complete RTO/RPO Matrix (Requirement 9.1)
RECOVERY_OBJECTIVES = {
    "observatory_server": RecoveryObjectives(
        service_name="Observatory Server (localhost:8888)",
        rto_minutes=5,  # Must be back online within 5 minutes
        rpo_minutes=1,  # Maximum 1 minute of data loss acceptable
        criticality_level="critical",
        backup_frequency="continuous",
        recovery_validation_steps=[
            "Verify WebSocket endpoints responding (/ws/observatory, /ws/emoji-rain, /ws/anomalies, /ws/doctor-status)",
            "Confirm metrics collection active (/metrics, /health, /ready)",
            "Validate ReflectiveModule health endpoints",
            "Test integration points (ACE Reporter, AI Memory Palace, DAG Registry)"
        ],
        dependencies=["redis_coordination", "prometheus_metrics"]
    ),
    "cloudflare_tunnel": RecoveryObjectives(
        service_name="Cloudflare Tunnel (d1e53e43-033f-4994-8f46-c83962ae3785)",
        rto_minutes=10,  # 10 minutes acceptable for tunnel restoration
        rpo_minutes=0,   # No data loss - stateless service
        criticality_level="critical",
        backup_frequency="configuration_only",
        recovery_validation_steps=[
            "Verify DNS propagation complete (observatory.nkllon.com, grafana.observatory.nkllon.com, prometheus.observatory.nkllon.com)",
            "Confirm ingress rules active for all subdomains",
            "Test WebSocket connectivity through tunnel",
            "Validate SSL/TLS certificate provisioning"
        ],
        dependencies=["dns_configuration", "certificate_management"]
    ),
    "prometheus_metrics": RecoveryObjectives(
        service_name="Prometheus (localhost:9090)",
        rto_minutes=15,  # 15 minutes acceptable for metrics restoration
        rpo_minutes=5,   # 5 minutes of metrics data loss acceptable
        criticality_level="high",
        backup_frequency="hourly",
        recovery_validation_steps=[
            "Verify scrape targets responding",
            "Confirm data retention policies active",
            "Test alert rule evaluation",
            "Validate Grafana datasource connectivity"
        ],
        dependencies=["storage_persistence", "configuration_files"]
    ),
    "grafana_dashboards": RecoveryObjectives(
        service_name="Grafana (localhost:3000)",
        rto_minutes=20,  # 20 minutes acceptable for dashboard restoration
        rpo_minutes=60,  # 1 hour of dashboard changes acceptable loss
        criticality_level="high", 
        backup_frequency="daily",
        recovery_validation_steps=[
            "Verify Prometheus datasource connectivity",
            "Confirm dashboard rendering",
            "Test user authentication",
            "Validate alert notification channels"
        ],
        dependencies=["prometheus_metrics", "user_authentication"]
    ),
    "redis_coordination": RecoveryObjectives(
        service_name="Redis Coordination (192.168.1.119:6379 + localhost:6380)",
        rto_minutes=3,   # 3 minutes for coordination restoration
        rpo_minutes=0,   # No data loss acceptable for coordination state
        criticality_level="critical",
        backup_frequency="continuous",
        recovery_validation_steps=[
            "Verify primary Redis connectivity (192.168.1.119:6379)",
            "Test fallback Redis functionality (localhost:6380)",
            "Confirm automatic failover mechanisms",
            "Validate coordination state synchronization"
        ],
        dependencies=["network_connectivity", "storage_persistence"]
    ),
    "directus_cms": RecoveryObjectives(
        service_name="Directus CMS (localhost:8055)",
        rto_minutes=30,  # 30 minutes acceptable for CMS restoration
        rpo_minutes=15,  # 15 minutes of configuration changes acceptable loss
        criticality_level="medium",
        backup_frequency="daily",
        recovery_validation_steps=[
            "Verify CMS health endpoint (/server/ping)",
            "Confirm configuration data integrity",
            "Test API connectivity",
            "Validate user authentication and permissions"
        ],
        dependencies=["database_storage", "configuration_files"]
    )
}
```

#### Emergency Escalation Procedures
```python
@dataclass
class EmergencyEscalation:
    severity_level: str  # P0, P1, P2, P3
    initial_response_time: int  # minutes
    escalation_contacts: List[Contact]
    decision_tree: List[DecisionNode]
    communication_channels: List[str]
    status_update_frequency: int  # minutes

@dataclass
class DecisionNode:
    condition: str
    action: str
    next_steps: List[str]
    timeout_action: str
```

#### Backup and Restore Procedures (Requirement 9.3)

**Automated Backup Procedures**:
```python
@dataclass
class BackupProcedure:
    service_name: str
    backup_type: str
    frequency: str
    retention_policy: str
    storage_location: str
    validation_schedule: str
    restore_testing_frequency: str
    automated_testing: bool = True

BACKUP_PROCEDURES = {
    "observatory_configuration": BackupProcedure(
        service_name="Observatory Server",
        backup_type="configuration_and_state",
        frequency="continuous",
        retention_policy="30 days",
        storage_location="local_persistent_volume + cloud_backup",
        validation_schedule="every_6_hours",
        restore_testing_frequency="weekly",
        automated_testing=True
    ),
    "cloudflare_tunnel_config": BackupProcedure(
        service_name="Cloudflare Tunnel",
        backup_type="configuration_only",
        frequency="on_change",
        retention_policy="90 days",
        storage_location="version_control + encrypted_backup",
        validation_schedule="daily",
        restore_testing_frequency="monthly",
        automated_testing=True
    ),
    "prometheus_data": BackupProcedure(
        service_name="Prometheus Metrics",
        backup_type="time_series_data",
        frequency="hourly",
        retention_policy="1 year",
        storage_location="persistent_storage + compressed_archive",
        validation_schedule="daily",
        restore_testing_frequency="weekly",
        automated_testing=True
    ),
    "redis_coordination_state": BackupProcedure(
        service_name="Redis Coordination",
        backup_type="memory_snapshot + aof",
        frequency="every_15_minutes",
        retention_policy="7 days",
        storage_location="local_disk + remote_backup",
        validation_schedule="hourly",
        restore_testing_frequency="daily",
        automated_testing=True
    ),
    "grafana_dashboards": BackupProcedure(
        service_name="Grafana Dashboards",
        backup_type="dashboard_json + datasources",
        frequency="daily",
        retention_policy="180 days",
        storage_location="version_control + database_backup",
        validation_schedule="daily",
        restore_testing_frequency="weekly",
        automated_testing=True
    ),
    "directus_cms_data": BackupProcedure(
        service_name="Directus CMS",
        backup_type="database + file_uploads",
        frequency="daily",
        retention_policy="90 days",
        storage_location="database_backup + file_system_backup",
        validation_schedule="daily",
        restore_testing_frequency="weekly",
        automated_testing=True
    )
}
```

**Restore Validation Processes**:
```python
@dataclass
class RestoreValidation:
    validation_id: str
    service_name: str
    validation_steps: List[str]
    success_criteria: List[str]
    automated_tests: List[str]
    manual_verification: List[str]
    rollback_procedure: List[str]

RESTORE_VALIDATIONS = {
    "observatory_restore": RestoreValidation(
        validation_id="observatory_full_restore",
        service_name="Observatory Server",
        validation_steps=[
            "Restore configuration files and environment variables",
            "Start Observatory daemon with restored configuration",
            "Verify all WebSocket endpoints responding",
            "Test ReflectiveModule health endpoints",
            "Validate integration point connectivity"
        ],
        success_criteria=[
            "All WebSocket endpoints (/ws/observatory, /ws/emoji-rain, /ws/anomalies, /ws/doctor-status) accepting connections",
            "Health endpoints (/health, /ready, /metrics) returning 200 status",
            "Integration points (ACE Reporter, AI Memory Palace, DAG Registry) accessible",
            "Metrics collection flowing to Prometheus"
        ],
        automated_tests=[
            "WebSocket connection test suite",
            "Health endpoint validation",
            "Metrics collection verification",
            "Integration point connectivity tests"
        ],
        manual_verification=[
            "Visual verification of Observatory dashboard",
            "Manual WebSocket message flow testing",
            "Integration point data flow validation"
        ],
        rollback_procedure=[
            "Stop restored Observatory service",
            "Restore previous working configuration",
            "Restart with known-good configuration",
            "Verify rollback success"
        ]
    )
}
```

**Automated Testing Schedules**:
- **Daily**: Redis coordination state restore testing with failover validation
- **Weekly**: Observatory, Prometheus, and Grafana restore testing with full validation
- **Monthly**: Cloudflare tunnel configuration restore testing with DNS propagation validation
- **Quarterly**: Full disaster recovery simulation with all services

### Operational Runbooks
```python
@dataclass
class OperationalRunbook:
    procedure_name: str
    trigger_conditions: List[str]
    step_by_step_instructions: List[RunbookStep]
    validation_checkpoints: List[ValidationStep]
    rollback_procedures: List[RollbackStep]
    estimated_duration: int  # minutes
    required_permissions: List[str]

@dataclass
class RunbookStep:
    step_number: int
    description: str
    commands: List[str]
    expected_output: str
    failure_handling: str
    timeout_seconds: int
```

## Automated Documentation Refresh and Staleness Detection

### Real-Time Documentation Maintenance (Requirement 10)

#### Automated Refresh Architecture (Requirement 10.1)
```python
@dataclass
class DocumentationRefreshSystem:
    change_detection_interval: int = 300  # 5 minutes for change detection
    max_refresh_time_hours: int = 1  # MANDATORY: Diagrams regenerated within 1 hour
    refresh_triggers: List[RefreshTrigger]
    staleness_thresholds: Dict[str, int]  # component -> max_age_hours (24 hours default)
    notification_channels: List[NotificationChannel]
    validation_schedules: List[ValidationSchedule]
    
    def ensure_one_hour_refresh_compliance(self) -> bool:
        """Ensures infrastructure changes trigger diagram regeneration within 1 hour"""
        return self.max_refresh_time_hours <= 1

@dataclass
class RefreshTrigger:
    trigger_type: str  # file_change, service_restart, configuration_update
    monitored_paths: List[str]
    trigger_conditions: List[str]
    refresh_scope: str  # full, partial, component_specific
    priority_level: str  # immediate, high, normal, low
```

#### Change Detection and Notification System (Requirement 10.1, 10.2)
- **File System Monitoring**: Real-time monitoring of configuration files and scripts with inotify integration
- **Service State Monitoring**: Integration with ReflectiveModule health endpoints for service lifecycle changes
- **Network Topology Changes**: Automatic detection of new services or port changes through periodic network scans
- **Configuration Drift Detection**: Comparison of live system state vs. documented state every 15 minutes
- **Stakeholder Notifications**: Automatic notifications sent to relevant stakeholders within 15 minutes of infrastructure changes
- **Timestamp and Validation Status**: All diagrams include "Last Updated" timestamp and validation status indicators (Requirement 10.2)
- **Accuracy Confidence Scoring**: Real-time confidence scores (0.0-1.0) based on automated verification against live system

#### Staleness Detection and Alerting (Requirement 10.3, 10.4)
```python
@dataclass
class StalenessDetector:
    component_name: str
    last_updated: datetime
    staleness_threshold_hours: int = 24  # Alert when >24 hours old (Requirement 10.3)
    accuracy_confidence_score: float  # 0.0-1.0
    validation_status: ValidationStatus
    alert_recipients: List[str]
    auto_refresh_enabled: bool
    manual_verification_required: bool = False  # Set when automated validation fails
    
    def check_staleness_alert_required(self) -> bool:
        """Check if staleness alert should be sent per Requirement 10.3"""
        hours_since_update = (datetime.now() - self.last_updated).total_seconds() / 3600
        return hours_since_update > self.staleness_threshold_hours

@dataclass
class ValidationChecklist:
    checklist_id: str
    component_type: str
    automated_tests: List[AutomatedTest]
    manual_verification_steps: List[ManualStep]  # Clear validation checklist (Requirement 10.4)
    success_criteria: List[str]
    failure_escalation: EscalationProcedure
    
    # Specific validation checklists for different component types
    infrastructure_checklist: List[str] = field(default_factory=lambda: [
        "Verify all services responding to health checks",
        "Confirm WebSocket endpoints accepting connections", 
        "Validate DNS resolution for all subdomains",
        "Test Cloudflare tunnel connectivity",
        "Verify Redis coordination endpoints accessible"
    ])
    
    automation_checklist: List[str] = field(default_factory=lambda: [
        "Execute sample Makefile targets and verify expected outcomes",
        "Validate Python script parameter documentation accuracy",
        "Test automation chain dependencies",
        "Verify integration point connectivity"
    ])
    
    security_checklist: List[str] = field(default_factory=lambda: [
        "Validate authentication mechanisms documented correctly",
        "Verify credential rotation schedules are current",
        "Test access control matrix accuracy",
        "Confirm audit trail functionality"
    ])
```

#### Accuracy Confidence Scoring
- **Automated Validation**: Continuous testing of documented endpoints and configurations
- **Live System Comparison**: Real-time comparison with actual system behavior
- **Historical Accuracy Tracking**: Trend analysis of documentation accuracy over time
- **Manual Verification Integration**: Incorporation of human validation results

### Documentation Lifecycle Management
```python
@dataclass
class DocumentationLifecycle:
    document_id: str
    creation_timestamp: datetime
    last_updated: datetime
    update_frequency: str  # real_time, hourly, daily
    validation_frequency: str
    retention_policy: str
    archive_schedule: str
    stakeholder_notifications: List[NotificationRule]
```

## Data Models

### Infrastructure Models
```python
@dataclass
class CloudflareConfig:
    tunnel_id: str
    credentials_file: str
    ingress_rules: List[IngressRule]
    dns_records: List[DNSRecord]

@dataclass
class PrometheusConfig:
    port: int
    scrape_configs: List[ScrapeConfig]
    alert_rules: List[AlertRule]
    storage_path: str

@dataclass
class GrafanaConfig:
    port: int
    datasources: List[DataSource]
    dashboards: List[Dashboard]
    admin_credentials: Optional[Credentials]

@dataclass
class ObservatoryConfig:
    port: int
    websocket_endpoints: List[WebSocketEndpoint]
    health_endpoints: List[str]
    reflective_module_config: ReflectiveModuleConfig
    integration_points: List[IntegrationPoint]

@dataclass
class RedisCoordinationConfig:
    primary_endpoint: str  # 192.168.1.119:6379
    fallback_endpoint: str  # localhost:6380
    coordination_channels: List[str]
    failover_timeout: int
```

### Automation and Script Models
```python
@dataclass
class MakefileTarget:
    name: str
    dependencies: List[str]
    commands: List[str]
    affected_components: List[str]
    expected_outcomes: List[str]

@dataclass
class PythonScript:
    path: str
    purpose: str
    target_components: List[str]
    parameters: List[Parameter]
    dependencies: List[str]
    integration_points: List[str]

@dataclass
class AutomationChain:
    trigger: str
    sequence: List[AutomationStep]
    validation_points: List[ValidationStep]
    rollback_procedure: List[str]

@dataclass
class WebSocketEndpoint:
    path: str  # /ws/observatory, /ws/emoji-rain, etc.
    purpose: str
    message_types: List[str]
    connection_limits: Optional[int]
    authentication_required: bool
```

### Deployment and Configuration Models
```python
@dataclass
class DeploymentConfiguration:
    service_name: str
    deployment_method: str  # container, host_process, daemon
    environment_variables: Dict[str, str]
    port_mappings: List[PortMapping]
    health_check_config: HealthCheckConfig
    scaling_constraints: ScalingConstraints

@dataclass
class NetworkTopology:
    local_network_range: str  # 192.168.1.x
    service_endpoints: List[ServiceEndpoint]
    dns_mappings: List[DNSMapping]
    tunnel_configuration: CloudflareConfig
    routing_rules: List[RoutingRule]

@dataclass
class IntegrationPoint:
    name: str  # ACE Reporter, AI Memory Palace, DAG Registry
    endpoint: str
    authentication_method: str
    data_flow_direction: str
    dependency_level: str
```

### Security and Access Control Models
```python
@dataclass
class SecurityConfiguration:
    service_name: str
    authentication_mechanisms: List[AuthenticationMethod]
    authorization_policies: List[AuthorizationPolicy]
    credential_management: CredentialManagement
    audit_configuration: AuditConfiguration
    incident_response_plan: IncidentResponsePlan

@dataclass
class AuthenticationMethod:
    method_type: str  # certificate, token, basic_auth, oauth
    configuration: Dict[str, Any]
    rotation_schedule: str
    validation_endpoint: str

@dataclass
class CredentialManagement:
    storage_method: str  # environment, file, cms, vault
    encryption_method: str
    rotation_frequency: str
    access_controls: List[str]
    audit_trail: bool
```

### Deployment and Configuration Models
```python
@dataclass
class DeploymentConfiguration:
    service_name: str
    deployment_method: str  # container, host_process, daemon
    environment_variables: Dict[str, str]
    port_mappings: List[PortMapping]
    health_check_config: HealthCheckConfig
    scaling_constraints: ScalingConstraints
    dependency_requirements: List[str]
    rollback_configuration: RollbackConfiguration

@dataclass
class ConfigurationManagement:
    configuration_source: str  # directus, file, environment
    schema_validation: SchemaValidation
    version_control: VersionControl
    change_tracking: ChangeTracking
    environment_specific: Dict[str, Any]

@dataclass
class RollbackConfiguration:
    rollback_triggers: List[str]
    rollback_steps: List[str]
    validation_checkpoints: List[str]
    timeout_seconds: int
    notification_recipients: List[str]
```

### Disaster Recovery Models
```python
@dataclass
class DisasterRecoveryPlan:
    service_name: str
    recovery_objectives: RecoveryObjectives
    backup_procedures: List[BackupProcedure]
    recovery_procedures: List[RecoveryProcedure]
    escalation_plan: EscalationPlan
    validation_procedures: List[ValidationProcedure]

@dataclass
class BackupProcedure:
    backup_type: str  # configuration, data, state
    backup_frequency: str
    retention_policy: str
    storage_location: str
    validation_schedule: str
    restore_testing_frequency: str

@dataclass
class EscalationPlan:
    severity_levels: List[SeverityLevel]
    contact_matrix: List[Contact]
    communication_channels: List[str]
    decision_trees: List[DecisionTree]
    status_reporting: StatusReporting
```

### Documentation Lifecycle Models
```python
@dataclass
class DocumentationMetadata:
    document_id: str
    document_type: str
    creation_timestamp: datetime
    last_updated: datetime
    last_validated: datetime
    accuracy_score: float
    staleness_status: StalenessStatus
    validation_history: List[ValidationResult]

@dataclass
class StalenessStatus:
    is_stale: bool
    staleness_threshold_hours: int
    time_since_update: int
    confidence_score: float
    requires_manual_verification: bool
    auto_refresh_enabled: bool

@dataclass
class ValidationResult:
    validation_timestamp: datetime
    validation_type: str  # automated, manual, hybrid
    success: bool
    confidence_score: float
    validation_details: Dict[str, Any]
    issues_found: List[str]
    corrective_actions: List[str]

@dataclass
class ComponentDiagram:
    diagram_type: str
    plantuml_source: str
    svg_output: str
    last_updated: datetime
    validation_status: ValidationResult
    accuracy_confidence: float
    staleness_status: StalenessStatus

@dataclass
class UseCase:
    name: str
    description: str
    actors: List[str]
    steps: List[str]
    sequence_diagram: Optional[ComponentDiagram]
    security_considerations: List[str]
    disaster_recovery_notes: List[str]

@dataclass
class DocumentationPackage:
    component_diagrams: List[ComponentDiagram]
    sequence_diagrams: List[ComponentDiagram]
    use_cases: List[UseCase]
    network_topology: ComponentDiagram
    automation_guide: str
    security_documentation: SecurityDocumentation
    disaster_recovery_runbooks: List[DisasterRecoveryPlan]
    deployment_guides: List[DeploymentGuide]
    metadata: DocumentationMetadata
```

## Error Handling

### Discovery Failures
- **Service Unavailable**: Continue with partial discovery, mark missing services
- **Configuration Parse Errors**: Log errors, use default configurations where possible
- **Network Connectivity Issues**: Implement retry logic with exponential backoff
- **Permission Denied**: Graceful degradation with available information
- **Authentication Failures**: Retry with credential refresh, escalate if persistent
- **Security Policy Violations**: Log security events, apply isolation procedures

### Generation Failures
- **PlantUML Errors**: Fallback to simplified diagrams, log detailed errors
- **File System Errors**: Implement backup locations and temporary storage
- **Diagram Complexity**: Automatic simplification for large topologies
- **Resource Constraints**: Implement diagram pagination and chunking
- **Security Context Errors**: Sanitize sensitive information, apply security templates
- **Deployment Documentation Errors**: Use fallback templates, mark as incomplete

### Validation Failures
- **Stale Documentation**: Automatic regeneration triggers
- **Inconsistent State**: Conflict resolution with live system as source of truth
- **Missing Components**: Partial documentation with clear gap identification
- **Version Mismatches**: Automatic version tracking and update notifications
- **Security Validation Failures**: Apply security incident response procedures
- **Disaster Recovery Validation Failures**: Escalate to operations team, update runbooks

### Security and Operational Error Handling
- **Credential Rotation Failures**: Automatic fallback to backup credentials, alert security team
- **Access Control Violations**: Immediate logging, potential service isolation
- **Backup Failures**: Retry with alternative backup methods, escalate if critical
- **Recovery Procedure Failures**: Activate emergency escalation, document lessons learned
- **Documentation Staleness Alerts**: Automatic refresh attempts, manual verification requests
- **Compliance Violations**: Immediate notification to compliance team, audit trail preservation

## Testing Strategy

### Unit Testing
- **Discovery Engine Tests**: Mock infrastructure components and verify discovery accuracy
- **Relationship Mapper Tests**: Test dependency analysis with known configurations
- **Diagram Generator Tests**: Validate PlantUML/Mermaid output for various inputs
- **Documentation Orchestrator Tests**: Test workflow coordination and error handling

### Integration Testing
- **Live Infrastructure Tests**: Run against actual development environment
- **End-to-End Documentation Generation**: Full workflow from discovery to publication
- **Diagram Accuracy Validation**: Compare generated diagrams with manual verification
- **Performance Testing**: Measure discovery and generation times for large topologies

### Validation Testing
- **Documentation Accuracy**: Automated comparison with live system state
- **Diagram Completeness**: Verify all discovered components appear in diagrams
- **Use Case Coverage**: Ensure all operational workflows are documented
- **Link Validation**: Verify all referenced endpoints and services are accessible

## Implementation Phases

### Phase 1: Infrastructure Discovery (Requirements 1, 4, 5)
- **Implement comprehensive service discovery** for Observatory, Prometheus, Grafana with ReflectiveModule integration (Requirement 1.1)
- **Create network topology scanner** for Cloudflare tunnel configuration with specific tunnel ID tracking (d1e53e43-033f-4994-8f46-c83962ae3785) (Requirement 5.1)
- **Build configuration file parser** for YAML/JSON configs including tunnel credentials and ingress rules (Requirement 5.2)
- **Develop comprehensive script registry** for 50+ Makefile targets and Python automation scripts with complete mapping (Requirement 4.1, 4.2)
- **Map WebSocket endpoints** (/ws/observatory, /ws/emoji-rain, /ws/anomalies, /ws/doctor-status) to their handlers with message types (Requirement 1.1)
- **Discover Redis coordination endpoints** (192.168.1.119:6379 primary, localhost:6380 fallback) with failover configuration (Requirement 5.1)
- **Map integration points** (ACE Reporter, AI Memory Palace, DAG Registry) with connection details and data flow directions (Requirement 1.1)

### Phase 2: Relationship Analysis (Requirements 2, 6)
- **Implement dependency mapping** between services with mathematical validation (DAG compliance) (Requirement 1.2)
- **Create comprehensive data flow tracer** for metrics pipeline through ReflectiveModule pattern with performance characteristics (Requirement 1.4, 6.1)
- **Build automation chain analyzer** for script dependencies and Makefile target relationships (task-3.4 depends on task-3.3) (Requirement 4.3)
- **Develop network path analysis** for routing and connectivity including DNS propagation flows with timing estimates (Requirement 2.1, 5.3)
- **Map integration points**: ACE Reporter → AI Memory Palace → DAG Registry coordination with data flow directions (Requirement 4.3, 6.4)
- **Analyze systematic error handling** and recovery procedure chains with correlation IDs and specific error codes (Requirement 2.4)
- **Trace complete interaction chains** from Makefile target execution through DNS propagation to service health verification (Requirement 2.1)

### Phase 3: Diagram Generation (Requirements 1, 2, 3)
- **Implement PlantUML component diagram generator** with 100% service coverage and component health status indicators (Requirement 1.1)
- **Create detailed sequence diagram generator** for operational workflows with timing estimates (Requirement 2.1, 2.2):
  - tunnel-start/tunnel-stop with DNS propagation timing (30-60 seconds) and service verification steps
  - dashboard-up/dashboard-stop/dashboard-restart with health check validation checkpoints
  - dashboard-status comprehensive health check flows with specific success/failure criteria and timeout values
  - Emergency protocol activation and systematic recovery procedures with correlation ID tracking
- **Build network topology visualization** with Mermaid including complete IP allocations (192.168.1.x) and port mappings (Requirement 1.3, 5.1)
- **Develop comprehensive data flow diagram generator** for observability pipeline showing ReflectiveModule → Observatory → Prometheus → Grafana flow (Requirement 1.4, 6.4)
- **Generate use case diagrams** for common operational scenarios and troubleshooting workflows (Requirement 3.1)

### Phase 4: Use Case and Operational Documentation (Requirements 3, 7)
- **Create comprehensive use case documentation** for critical workflows including tunnel management, dashboard lifecycle, monitoring, system recovery, and emergency protocols (Requirement 3.1)
- **Generate step-by-step procedures** with expected outcomes including Makefile target execution, Python script parameters, expected log outputs, WebSocket connection verification, and integration point confirmations (Requirement 3.2)
- **Implement troubleshooting guide generation** with error propagation paths, specific error codes (WS001-004, TUN001-005, MET001-004, RED001-004), and resolution paths (Requirement 3.3)
- **Build operational procedure documentation** for maintenance including CMS-based configuration management through Directus, version control workflows, rolling updates, and Beast Mode component coordination (Requirement 3.4)
- **Develop deployment and configuration management documentation** with DAG-based orchestration and mathematical validation (Requirement 7.3)
- **Create error handling guides** with ReflectiveModule systematic error handling procedures and correlation ID tracking (Requirement 3.3)

### Phase 5: Security and Access Control Implementation (Requirement 8)
- Implement comprehensive security documentation generator for all services
- Create authentication mechanism mapping and credential management documentation
- Build access control matrix generation with role-based permissions
- Develop security incident response procedure documentation
- Generate audit trail documentation and compliance reporting
- Create security monitoring integration with Observatory WebSocket alerts

### Phase 6: Metrics and Observability Flow Documentation (Requirement 6)
- **Document Observatory metrics exposure** to Prometheus including ReflectiveModule automatic registration, Observatory server endpoints (/metrics, /health, /ready), and WebSocket connection metrics (Requirement 6.1)
- **Map Grafana query patterns** for Prometheus datasource including ReflectiveModule metrics across Beast Mode components, WebSocket real-time metrics, and system performance indicators (Requirement 6.2)
- **Document metric collection intervals** and retention policies including Prometheus scrape intervals, ReflectiveModule collection frequency, and long-term storage policies (Requirement 6.3)
- **Create complete observability pipeline documentation** showing ReflectiveModule → Observatory → Prometheus → Grafana flow with WebSocket real-time streaming parallel to batch collection (Requirement 6.4)
- **Map integration metrics** from ACE Reporter and AI Memory Palace connections with custom metrics from DAG orchestration components (Requirement 6.1)
- **Document fallback mechanisms** when monitoring components fail with diagnostic procedures for each pipeline stage (Requirement 6.4)

### Phase 7: Deployment and Configuration Management (Requirement 7)
- **Implement dependency validation system** for Directus CMS availability (localhost:8055) with fallback to file-based configuration (Requirement 7.2)
- **Document DAG-based deployment orchestration** with mathematical validation, dependency ordering, and rollback procedures (Requirement 7.3)
- **Create multi-modal deployment pattern documentation** (Docker containers, host processes, cloud services) with health check integration (Requirement 7.1)
- **Build CMS-based configuration management documentation** through Directus with environment-specific handling and version control workflows (Requirement 7.2)
- **Develop resource requirements and scaling constraint documentation** with performance benchmarks and capacity planning guidelines (Requirement 7.4)
- **Generate deployment validation and rollback procedure documentation** with specific success criteria and automated testing (Requirement 7.3)

### Phase 7: Disaster Recovery and Operational Runbooks (Requirement 9)
- Implement RTO/RPO requirements documentation for all services
- Create comprehensive disaster recovery procedure documentation
- Build backup and restore procedure documentation with validation testing
- Develop emergency escalation procedure documentation with decision trees
- Generate operational runbook documentation for common scenarios
- Create business continuity planning documentation

### Phase 8: Automated Documentation Refresh and Validation (Requirement 10)
- Implement real-time change detection and documentation refresh system
- Create staleness detection and alerting system with confidence scoring
- Build automated validation system with live system comparison
- Develop notification system for stakeholders when documentation changes
- Generate accuracy monitoring and trend analysis reporting
- Create manual verification integration with automated validation results

## Design Decisions and Rationales

### Technology Choices

#### PlantUML for UML Diagrams
**Decision**: Use PlantUML for component and sequence diagrams
**Rationale**: 
- Text-based diagram definition enables version control
- Extensive UML support covers all required diagram types
- Mature ecosystem with good Python integration
- Automatic layout reduces manual diagram maintenance

#### Mermaid for Network Topology
**Decision**: Use Mermaid for network and data flow diagrams
**Rationale**:
- Better support for network topology visualization
- GitHub native rendering for documentation integration
- Simpler syntax for automated generation
- Good performance with large network diagrams

#### ReflectiveModule Pattern
**Decision**: Inherit from ReflectiveModule for all components
**Rationale**:
- Consistent with ADR-005 observability requirements
- Automatic health monitoring and metrics collection
- Integrated CLI generation for operational tools
- Systematic error handling and logging

#### File-Based Output with CMS Integration
**Decision**: Generate files locally with optional CMS publishing based on Directus availability
**Rationale**:
- Supports version control workflows regardless of CMS availability
- Enables offline documentation access as primary mode
- Integrates with Directus CMS (localhost:8055) when available per ADR-010
- Provides graceful degradation when CMS unavailable
- Validates Directus availability before attempting CMS operations

**Implementation Strategy**:
```python
class DocumentationPublisher(ReflectiveModule):
    def __init__(self):
        super().__init__()
        self.directus_available = self._validate_directus_availability()
        self.publication_mode = "hybrid" if self.directus_available else "file_only"
    
    def _validate_directus_availability(self) -> bool:
        """Validate Directus CMS availability before operations"""
        try:
            response = requests.get("http://localhost:8055/server/ping", timeout=5)
            return response.text.strip() == "pong"
        except Exception as e:
            self._logger.warning(f"Directus unavailable: {e}")
            return False
    
    def publish_documentation(self, docs: DocumentationPackage) -> PublicationResult:
        """Publish documentation with fallback strategy"""
        # Always save to files first (primary strategy)
        file_result = self._save_to_files(docs)
        
        # Attempt CMS publishing if available
        cms_result = None
        if self.directus_available:
            try:
                cms_result = self._publish_to_directus(docs)
            except Exception as e:
                self._logger.warning(f"CMS publishing failed, continuing with file-only: {e}")
        
        return PublicationResult(
            file_storage=file_result,
            cms_storage=cms_result,
            mode=self.publication_mode
        )
```

### Architectural Patterns

#### Discovery-First Approach
**Decision**: Always discover current state before generating documentation
**Rationale**:
- Ensures documentation accuracy reflects live system
- Follows observation-first leadership principle
- Prevents documentation drift from actual implementation
- Enables automated validation and updates

#### Modular Component Design
**Decision**: Separate discovery, analysis, generation, and orchestration
**Rationale**:
- Enables independent testing and development
- Supports different update frequencies for each component
- Allows selective execution based on what changed
- Facilitates future extension and customization

#### Graph-Based Relationship Modeling
**Decision**: Use graph data structures for dependency and flow analysis
**Rationale**:
- Natural representation of system relationships
- Enables sophisticated analysis algorithms
- Supports cycle detection and path finding
- Facilitates diagram generation from graph structures

## Success Metrics

### Documentation Accuracy and Completeness
- **Discovery Completeness**: >95% of running services discovered including all WebSocket endpoints and ReflectiveModule integrations
- **Relationship Accuracy**: >90% of dependencies correctly identified across Beast Mode framework components
- **Automation Mapping**: 100% of 50+ Makefile targets mapped to their infrastructure components
- **Script Documentation**: Complete mapping of Python automation scripts to target components
- **Diagram Currency**: Documentation updated within 1 hour of system changes
- **Validation Success**: >98% of generated documentation validates against live system

### Operational Effectiveness
- **Time to Understanding**: New team members can understand system architecture in <30 minutes
- **Use Case Coverage**: All critical workflows (tunnel management, dashboard lifecycle, emergency procedures) documented with step-by-step procedures
- **Troubleshooting Efficiency**: 50% reduction in time to identify component relationships and error resolution paths
- **Change Impact Analysis**: Clear identification of downstream effects for all infrastructure changes
- **Documentation Usage**: Regular access by development and operations teams with measurable improvement in operational efficiency

### Network and Infrastructure Documentation
- **Network Topology Accuracy**: Complete IP address allocations and port mappings documented
- **DNS Configuration Coverage**: All subdomain routing (observatory.nkllon.com, grafana.observatory.nkllon.com, prometheus.observatory.nkllon.com) mapped
- **Tunnel Configuration**: Cloudflare tunnel (d1e53e43-033f-4994-8f46-c83962ae3785) ingress rules and routing documented
- **WebSocket Endpoint Coverage**: All endpoints (/ws/observatory, /ws/emoji-rain, /ws/anomalies, /ws/doctor-status) documented with message flows

### System Performance and Scalability
- **Discovery Speed**: Full infrastructure scan including all Beast Mode components completes in <5 minutes
- **Generation Speed**: Complete documentation package with all diagrams generated in <10 minutes
- **Resource Usage**: <5% CPU and <500MB memory during generation
- **Storage Efficiency**: Generated documentation <100MB total size
- **Update Frequency**: Automated documentation updates triggered by infrastructure changes

### Security and Compliance Metrics
- **Security Documentation Coverage**: 100% of services have documented authentication mechanisms and access controls
- **Credential Rotation Tracking**: All credentials have documented rotation schedules and procedures
- **Audit Trail Completeness**: 100% of access events logged with correlation IDs
- **Incident Response Readiness**: All services have documented security incident response procedures
- **Compliance Reporting**: Automated generation of security compliance reports within required timeframes

### Deployment and Configuration Management Metrics
- **Deployment Documentation Accuracy**: >95% of deployment procedures validated against actual deployments
- **Configuration Management Coverage**: 100% of services integrated with CMS-based configuration management
- **Rollback Procedure Validation**: All deployment procedures have tested rollback capabilities
- **Resource Planning Accuracy**: Scaling constraints and capacity planning guidelines validated against actual usage
- **DAG Compliance**: 100% of deployment dependencies validated for mathematical correctness

### Disaster Recovery and Operational Metrics
- **RTO/RPO Documentation**: All critical services have documented recovery objectives with validation testing
- **Recovery Procedure Accuracy**: >98% of recovery procedures validated through testing
- **Backup Validation Success**: Weekly automated backup testing with >99% success rate
- **Emergency Response Time**: Emergency escalation procedures enable <5 minute initial response
- **Runbook Effectiveness**: Operational runbooks reduce incident resolution time by >50%

### Documentation Lifecycle and Accuracy Metrics
- **Staleness Detection Accuracy**: >99% accuracy in detecting outdated documentation
- **Automated Refresh Success**: >95% of documentation updates completed within 1 hour of infrastructure changes
- **Validation Confidence**: Average accuracy confidence score >90% across all documentation
- **Manual Verification Efficiency**: <10% of documentation requires manual verification
- **Stakeholder Notification**: 100% of relevant stakeholders notified within 15 minutes of significant changes

This comprehensive design provides a systematic solution for creating and maintaining system architecture documentation that automatically stays current with the live infrastructure while providing clear visual representations, operational guidance, security controls, disaster recovery procedures, and deployment management for all team members across the Beast Mode framework ecosystem.##
 ADR Conformance Review

### Relevant ADRs Reviewed
- ADR-004: DAG Orchestration with Celery + Redis - ✅ Compliant
- ADR-005: ReflectiveModule Pattern for Universal Observability - ✅ Compliant  
- ADR-007: Integration-First Design Strategy - ✅ Compliant
- ADR-010: CMS-Based Configuration Management - ✅ Compliant

### Conformance Assessment

#### **Infrastructure**: 
- Aligns with existing Redis infrastructure (ADR-004) for coordination and caching
- Follows ReflectiveModule patterns (ADR-005) for all discovery and generation components
- Integrates with CMS through Directus (ADR-010) for configuration management

#### **Integration**: 
- Follows integration-first design strategy (ADR-007) by building on existing Observatory, Prometheus, and Grafana infrastructure
- Leverages existing DAG Registry infrastructure for dependency validation
- Maintains consistency with Beast Mode framework patterns

#### **Operations**: 
- Implements systematic error handling with correlation IDs consistent with ReflectiveModule pattern
- Uses resource-aware approaches for discovery and generation processes
- Provides idempotent operations for diagram generation and validation

#### **Technology**: 
- Avoids creating new public APIs, instead documenting existing infrastructure
- Uses established automation patterns from existing Makefile and Python script ecosystem
- Follows evidence-based validation approaches for documentation accuracy

### Architectural Consistency
The design maintains architectural consistency by building upon established Beast Mode patterns rather than creating parallel systems. All components inherit from ReflectiveModule, use existing Redis coordination, integrate with established CMS configuration management, and follow systematic error handling patterns. The documentation system becomes part of the observability ecosystem rather than a separate documentation tool.