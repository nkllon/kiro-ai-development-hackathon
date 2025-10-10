# Beast Mode Framework Deployment Architecture Requirements

## Introduction

This specification defines the comprehensive deployment architecture for the Beast Mode Framework - a microservices-based system that provides systematic PDCA (Plan-Do-Check-Act) orchestration for AI-assisted development. The system includes real-time monitoring via Prometheus and Grafana, CMS capabilities through Directus, reverse proxy and load balancing via Nginx, and a production-like local development environment.

## Requirements

### Requirement 1: Container-Based Microservices Architecture

**User Story:** As a system administrator, I want a containerized microservices architecture so that services are isolated, scalable, and maintainable.

#### Acceptance Criteria

1. WHEN the system is deployed THEN each service SHALL run in its own Docker container
2. WHEN services communicate THEN they SHALL use Docker DNS for service discovery
3. WHEN containers fail THEN they SHALL automatically restart unless manually stopped
4. WHEN the system starts THEN services SHALL start in proper dependency order
5. IF a service becomes unhealthy THEN it SHALL be automatically restarted
6. WHEN scaling is needed THEN individual services SHALL be scalable independently

### Requirement 2: Systematic PDCA Orchestration API

**User Story:** As a developer, I want a FastAPI-based PDCA orchestration service so that I can systematically manage AI-assisted development workflows.

#### Acceptance Criteria

1. WHEN the PDCA orchestrator starts THEN it SHALL expose REST API endpoints on port 8080
2. WHEN health checks are requested THEN the service SHALL respond with detailed health status
3. WHEN API documentation is accessed THEN Swagger UI SHALL be available at /docs
4. WHEN metrics are requested THEN both JSON and Prometheus formats SHALL be available
5. IF the service fails health checks THEN it SHALL be restarted automatically
6. WHEN source code changes THEN hot reload SHALL be supported in development mode

### Requirement 3: Comprehensive Monitoring and Observability

**User Story:** As a system operator, I want comprehensive monitoring with Prometheus and Grafana so that I can observe system health and performance.

#### Acceptance Criteria

1. WHEN monitoring is enabled THEN Prometheus SHALL scrape metrics from all services
2. WHEN metrics are collected THEN they SHALL include system, application, and health metrics
3. WHEN alerts are triggered THEN they SHALL be based on configurable thresholds
4. WHEN Grafana is accessed THEN dashboards SHALL visualize key system metrics
5. IF metric collection fails THEN the system SHALL continue operating with degraded observability
6. WHEN retention limits are reached THEN old metrics SHALL be automatically purged

### Requirement 4: Content Management System Integration

**User Story:** As a content manager, I want a Directus CMS integration so that I can manage content and data through a web interface.

#### Acceptance Criteria

1. WHEN Directus is deployed THEN it SHALL be accessible via web interface on port 8055
2. WHEN the database is initialized THEN PostgreSQL SHALL provide persistent storage
3. WHEN admin access is needed THEN default credentials SHALL be configurable via environment
4. WHEN email functionality is required THEN SMTP configuration SHALL be supported
5. IF the database becomes unavailable THEN Directus SHALL handle the failure gracefully
6. WHEN data is modified THEN changes SHALL be persisted across container restarts

### Requirement 5: Reverse Proxy and Load Balancing

**User Story:** As a system architect, I want Nginx as a reverse proxy so that I can provide unified access, load balancing, and security features.

#### Acceptance Criteria

1. WHEN external requests arrive THEN Nginx SHALL route them to appropriate backend services
2. WHEN rate limiting is needed THEN configurable limits SHALL be enforced per endpoint type
3. WHEN security headers are required THEN they SHALL be automatically added to responses
4. WHEN WebSocket connections are needed THEN they SHALL be properly proxied
5. IF backend services are unavailable THEN appropriate error pages SHALL be served
6. WHEN SSL/TLS is configured THEN HTTPS SHALL be properly terminated

### Requirement 6: Environment Configuration Management

**User Story:** As a DevOps engineer, I want hierarchical environment configuration so that I can manage settings across different deployment environments.

#### Acceptance Criteria

1. WHEN configuration is loaded THEN ~/.env SHALL take precedence over other sources
2. WHEN default values are needed THEN sample.env SHALL provide templates
3. WHEN service-specific config is required THEN dedicated env files SHALL be supported
4. WHEN secrets are managed THEN they SHALL never be hardcoded in configuration files
5. IF required environment variables are missing THEN services SHALL fail fast with clear errors
6. WHEN configuration changes THEN services SHALL be able to reload without full restart

### Requirement 7: Data Persistence and Backup Strategy

**User Story:** As a data administrator, I want persistent data storage with backup capabilities so that critical data is never lost.

#### Acceptance Criteria

1. WHEN data is stored THEN Docker volumes SHALL provide persistence across container restarts
2. WHEN backups are needed THEN critical volumes SHALL be identifiable and exportable
3. WHEN database backups are created THEN they SHALL include complete schema and data
4. WHEN volume restoration is needed THEN the process SHALL be documented and tested
5. IF data corruption occurs THEN backup restoration SHALL be possible
6. WHEN storage limits are approached THEN cleanup procedures SHALL be available

### Requirement 8: Health Monitoring and Auto-Recovery

**User Story:** As a system operator, I want comprehensive health monitoring so that failures are detected and resolved automatically.

#### Acceptance Criteria

1. WHEN services start THEN health checks SHALL verify proper initialization
2. WHEN health checks fail THEN services SHALL be restarted automatically
3. WHEN dependencies are unavailable THEN dependent services SHALL wait appropriately
4. WHEN system resources are exhausted THEN alerts SHALL be generated
5. IF cascading failures occur THEN the system SHALL isolate failures to prevent spread
6. WHEN recovery is needed THEN procedures SHALL be automated where possible

### Requirement 9: Security and Access Control

**User Story:** As a security administrator, I want proper security controls so that the system is protected against common threats.

#### Acceptance Criteria

1. WHEN network communication occurs THEN services SHALL be isolated in private networks
2. WHEN external access is provided THEN only necessary ports SHALL be exposed
3. WHEN authentication is required THEN configurable credentials SHALL be supported
4. WHEN security headers are needed THEN they SHALL be automatically applied
5. IF unauthorized access is attempted THEN rate limiting SHALL prevent abuse
6. WHEN container permissions are set THEN they SHALL follow least privilege principles

### Requirement 10: Deployment Automation and Procedures

**User Story:** As a deployment engineer, I want automated deployment procedures so that deployments are consistent and reliable.

#### Acceptance Criteria

1. WHEN initial deployment occurs THEN all services SHALL start in correct order
2. WHEN updates are deployed THEN rolling updates SHALL be supported for stateless services
3. WHEN configuration changes THEN affected services SHALL be restarted automatically
4. WHEN deployment fails THEN rollback procedures SHALL be available
5. IF monitoring stack is optional THEN it SHALL be deployable via profiles
6. WHEN troubleshooting is needed THEN diagnostic commands SHALL be documented

### Requirement 11: Performance Optimization and Resource Management

**User Story:** As a performance engineer, I want resource management and optimization so that the system performs efficiently under load.

#### Acceptance Criteria

1. WHEN resource limits are set THEN containers SHALL respect CPU and memory constraints
2. WHEN performance tuning is needed THEN configuration parameters SHALL be adjustable
3. WHEN caching is beneficial THEN appropriate caching strategies SHALL be implemented
4. WHEN load increases THEN the system SHALL scale horizontally where possible
5. IF resource contention occurs THEN monitoring SHALL identify bottlenecks
6. WHEN optimization is applied THEN performance improvements SHALL be measurable

### Requirement 12: Development and Production Parity

**User Story:** As a developer, I want development environments that match production so that deployment surprises are minimized.

#### Acceptance Criteria

1. WHEN development environment is used THEN it SHALL mirror production architecture
2. WHEN services are configured THEN the same container images SHALL be used across environments
3. WHEN networking is set up THEN service communication patterns SHALL be identical
4. WHEN data is managed THEN persistence mechanisms SHALL be consistent
5. IF environment differences exist THEN they SHALL be explicitly documented
6. WHEN testing occurs THEN it SHALL validate production-like scenarios
## Updated Requirements for Observatory Containerization

### Requirement 32: Observatory Container Architecture
**User Story**: As a system administrator, I need the Observatory service to run in Docker containers for consistent deployment and isolation.

**Acceptance Criteria**:
- Observatory service runs in dedicated Docker container
- Container includes all necessary dependencies and configurations
- Health checks verify container and service status
- Container integrates with existing Prometheus and Grafana containers
- Makefile targets manage containerized deployment lifecycle

**Technical Requirements**:
- Dockerfile for Observatory service in `deployment/observatory/`
- Docker Compose configuration for full Observatory stack
- Container health checks on ports 8888, 8889, 8890
- Volume mounts for persistent data and logs
- Network configuration for inter-container communication

### Requirement 33: Containerized Service Management
**User Story**: As a developer, I need Makefile targets that properly manage containerized Observatory services.

**Acceptance Criteria**:
- `make observatory-start` deploys containers using Docker Compose
- `make observatory-stop` stops and removes Observatory containers
- `make observatory-restart` performs clean restart of containerized services
- `make observatory-logs` shows container logs for debugging
- `make observatory-shell` provides container shell access

**Technical Requirements**:
- Updated `scripts/deploy_observatory.py` for container deployment
- Container lifecycle management in stop script
- Proper error handling for container operations
- Integration with existing Cloudflare tunnel configuration

### Requirement 34: Container Health Monitoring
**User Story**: As a system operator, I need comprehensive health monitoring for containerized Observatory services.

**Acceptance Criteria**:
- Docker health checks verify service availability
- Health endpoints accessible through container networking
- Monitoring integrates with existing Prometheus metrics
- Container status visible in `make observatory-status`
- Automatic restart on container health failures

**Technical Requirements**:
- Health check configuration in Dockerfile and Docker Compose
- Container networking allows health endpoint access
- Integration with existing monitoring infrastructure
- Status reporting includes container state information

### Requirement 35: Containerized Cloudflare Tunnel Integration
**User Story**: As a system administrator, I need the Cloudflare tunnel to run in a Docker container for complete containerization and proper networking.

**Acceptance Criteria**:
- Cloudflare tunnel runs in dedicated Docker container
- Tunnel connects to Observatory services using container networking
- Container uses proper environment variable configuration from ~/.env
- Tunnel integrates with Docker Compose stack lifecycle
- External URLs work correctly through containerized tunnel

**Technical Requirements**:
- Cloudflare tunnel container in Docker Compose configuration
- Container-specific tunnel configuration with service names
- Environment variable loading from ~/.env file
- Container networking between tunnel and Observatory services
- Proper dependency management in Docker Compose

**Implementation Details**:
- Container: `observatory-cloudflare-tunnel` using `cloudflare/cloudflared:latest`
- Configuration: `deployment/observatory/cloudflared-config.yml` with container service names
- Networking: Uses `observatory-network` for inter-container communication
- Dependencies: Depends on Observatory, Prometheus, and Grafana containers
- Credentials: Mounts ~/.cloudflared directory for tunnel credentials

**Validation**:
- External URLs accessible: https://observatory.nkllon.com/health
- Prometheus accessible: https://prometheus.observatory.nkllon.com/-/healthy  
- Grafana accessible: https://grafana.observatory.nkllon.com/api/health
- Container networking functional between tunnel and services
- Environment variables properly loaded from ~/.env###
 Requirement 36: External Redis Integration for Observatory
**User Story**: As a system administrator, I need the Observatory to connect to the existing Redis instance on vonnegut for distributed caching and session management.

**Acceptance Criteria**:
- Observatory connects to Redis instance on vonnegut server
- Redis connection uses environment variables from ~/.env for configuration
- Authentication handled via REDIS_PASSWORD environment variable
- No local Redis container created in Observatory stack
- Observatory services can read/write to shared Redis instance

**Technical Requirements**:
- Environment variables: REDIS_HOST (default: vonnegut), REDIS_PORT (default: 6379)
- Redis password authentication using REDIS_PASSWORD from ~/.env
- Container networking allows external Redis connectivity
- Observatory container configured with Redis connection parameters
- Shared Redis access for distributed Observatory deployments

**Implementation Details**:
- Redis host: `${REDIS_HOST:-vonnegut}` from environment variables
- Redis port: `${REDIS_PORT:-6379}` from environment variables  
- Authentication: Uses REDIS_PASSWORD from ~/.env file
- No local Redis container in docker-compose.yml
- Observatory container environment includes Redis connection settings

**Validation**:
- Observatory can connect to Redis on vonnegut
- Redis operations (get/set/pub/sub) functional from Observatory
- Environment variables properly loaded from ~/.env
- No Redis container running in Observatory stack
- Distributed caching operational across Observatory instances

### Requirement 37: Anonymous Access Configuration for Monitoring Services
**User Story**: As an Observatory service, I need anonymous access to Grafana and Prometheus for programmatic dashboard and metrics integration.

**Acceptance Criteria**:
- Grafana configured for anonymous viewer access
- Prometheus accessible without authentication
- Observatory can connect programmatically to both services
- No login challenges for service-to-service communication
- Admin access still available when needed

**Technical Requirements**:
- Grafana anonymous authentication enabled
- Grafana login form disabled for seamless access
- Prometheus default configuration (no auth required)
- Observatory environment variables for service URLs
- Container networking between Observatory and monitoring services

**Implementation Details**:
- Grafana environment variables:
  - `GF_AUTH_ANONYMOUS_ENABLED=true`
  - `GF_AUTH_DISABLE_LOGIN_FORM=true`
  - `GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer`
- Observatory environment variables:
  - `PROMETHEUS_URL=http://observatory-prometheus:9090`
  - `GRAFANA_URL=http://observatory-grafana:3000`
- Container networking via observatory-network

**Validation**:
- Observatory can access Grafana dashboards programmatically
- Observatory can query Prometheus metrics without authentication
- External access still requires proper authentication where configured
- Service-to-service communication functional within container network### Requir
ement 38: Distributed Observatory Architecture with Central Services
**User Story**: As a system administrator, I need Observatory instances to share state and data across multiple hosts using central services on vonnegut.

**Acceptance Criteria**:
- Local Prometheus instances federate to central Prometheus on vonnegut
- Grafana uses Redis sessions for shared authentication state
- Observatory uses Redis on vonnegut for distributed caching and coordination
- Dashboards and alerts are consistent across all Observatory instances
- Data persists and is accessible from any Observatory deployment

**Technical Requirements**:
- **Prometheus Federation**: Local instances (7-day retention) → Central instance (long-term)
- **Redis Integration**: Sessions, caching, and shared state on vonnegut
- **Grafana Configuration**: Redis sessions, central Prometheus datasource
- **Alert Management**: Central Alertmanager on vonnegut for unified alerting
- **Dashboard Provisioning**: Configuration-as-code for consistent dashboards

**Implementation Details**:
- **Local Prometheus**: 7-day retention, remote write to vonnegut:9090
- **Central Prometheus**: Long-term storage, federation from all instances
- **Redis Configuration**: 
  - DB 0: Observatory shared state
  - DB 1: Grafana sessions
  - DB 2: Engagement manager data
- **Grafana Datasources**: Both local and central Prometheus configured
- **Alert Rules**: Provisioned from configuration files

**Validation**:
- Observatory instances can be deployed on multiple hosts
- Grafana sessions persist across different Observatory instances
- Prometheus metrics are federated to central storage
- Dashboards and alerts are consistent across deployments
- Redis connectivity functional from all Observatory containers

### Requirement 39: Configuration-as-Code for Monitoring Stack
**User Story**: As a DevOps engineer, I need monitoring configurations (dashboards, alerts) stored in version control and automatically provisioned.

**Acceptance Criteria**:
- Grafana dashboards defined in JSON configuration files
- Prometheus alert rules defined in YAML configuration files
- Configurations automatically loaded on container startup
- Changes to configurations trigger automatic reloads
- All monitoring configurations are version controlled

**Technical Requirements**:
- **Dashboard Provisioning**: Grafana dashboard provider configuration
- **Alert Rule Loading**: Prometheus rule_files configuration
- **Automatic Reloads**: File watching for configuration changes
- **Version Control**: All configs stored in git repository
- **Validation**: Configuration syntax validation before deployment

**Implementation Details**:
- **Grafana Dashboards**: `deployment/observatory/grafana-config/dashboards/json/`
- **Prometheus Rules**: `deployment/observatory/prometheus-rules/`
- **Datasource Config**: `deployment/observatory/grafana-config/datasources/`
- **Volume Mounts**: Configuration directories mounted read-only
- **Provisioning**: Automatic loading via Grafana/Prometheus provisioning

**Validation**:
- Dashboards appear automatically in Grafana on startup
- Alert rules are loaded and active in Prometheus
- Configuration changes are reflected without manual intervention
- All configurations are tracked in version control
- Syntax validation prevents broken configurations

### Requirement 40: WebSocket Support Through Cloudflare Tunnel ✅ COMPLETED
**User Story**: As an Observatory user, I need WebSocket connections to work through the Cloudflare tunnel so that real-time features function properly without triggering bot protection.

**Acceptance Criteria**:
- All Observatory WebSocket endpoints accessible through Cloudflare tunnel
- WebSocket connections upgrade properly (HTTP/1.1 101 Switching Protocols)
- Bidirectional WebSocket communication functional
- No HTTP polling fallback activation
- No Error 1033 incidents from bot protection systems
- Real-time features (emoji rain, status updates, anomalies, health monitoring) work seamlessly

**Technical Requirements**:
- **Cloudflare Configuration**: WebSocket support parameters in tunnel configuration
- **Connection Management**: Proper timeout and keep-alive settings
- **Protocol Support**: HTTP/1.1 upgrade to WebSocket protocol
- **Error Handling**: Graceful degradation when WebSocket unavailable
- **Testing Framework**: Automated WebSocket connectivity validation

**Implementation Details**: ✅ COMPLETED 2025-10-02 18:28 UTC
- **Configuration File**: `deployment/observatory/cloudflared-config.yml`
- **WebSocket Parameters**:
  - `connectTimeout: 30s` - Connection timeout for WebSocket upgrades
  - `tlsTimeout: 10s` - TLS handshake timeout
  - `tcpKeepAlive: 30s` - TCP keep-alive for persistent connections
  - `keepAliveConnections: 100` - Maximum keep-alive connections
  - `keepAliveTimeout: 90s` - Keep-alive connection timeout
- **Container Integration**: Cloudflare tunnel runs in Docker container with updated config
- **Service Discovery**: Uses container networking (beast-mode-observatory:8888, etc.)

**Validation**: ✅ ALL TESTS PASSED
- ✅ `/ws/emoji-rain` - Real-time emoji rain updates working
- ✅ `/ws/observatory` - Observatory status updates working
- ✅ `/ws/anomalies` - Real-time anomaly alerts working
- ✅ `/ws/doctor-status` - System health monitoring working
- ✅ HTTP endpoints verified: `https://observatory.nkllon.com/health`
- ✅ Test Results: 4/4 tunnel endpoints successful, 4/4 local endpoints successful

**Testing Tools Created**:
- `scripts/test_websocket_connectivity.py` - Automated WebSocket endpoint testing
- `scripts/browser_websocket_test.html` - Browser-based WebSocket validation
- Comprehensive test coverage for all WebSocket endpoints and protocols

**Impact**:
- **Before**: WebSocket connections failed, HTTP polling fallback, Error 1033 risk
- **After**: Perfect WebSocket connectivity, real-time features functional, no bot protection issues

### Requirement 41: Prometheus Configuration Management ✅ COMPLETED
**User Story**: As a system administrator, I need Prometheus to start successfully without configuration parsing errors so that metrics collection and monitoring work reliably.

**Acceptance Criteria**:
- Prometheus container starts without restart loops
- Configuration file parses successfully without YAML syntax errors
- All scrape targets are accessible and collecting metrics
- Prometheus web interface accessible through Cloudflare tunnel
- Health endpoints respond correctly for monitoring validation

**Technical Requirements**:
- **Configuration Syntax**: Valid YAML without environment variable expansion issues
- **Container Stability**: No restart loops due to configuration errors
- **Scrape Targets**: Observatory, Engagement Manager, Jaeger metrics collection
- **Health Monitoring**: Prometheus self-monitoring and health endpoints
- **Tunnel Integration**: Accessible via `https://prometheus.observatory.nkllon.com/`

**Implementation Details**: ✅ COMPLETED 2025-10-02 18:37 UTC
- **Root Cause**: Environment variable syntax (`${VAR:-default}`) in prometheus.yml caused parsing errors
- **Solution**: Replaced environment variables with static configuration values
- **Configuration File**: `deployment/observatory/prometheus.yml` - fixed YAML syntax
- **Container Management**: Restarted observatory-prometheus container successfully
- **Scrape Configuration**:
  - Observatory: 5-second intervals on port 8888
  - Engagement Manager: 10-second intervals on port 8891
  - Jaeger: 30-second intervals on port 14269
  - Self-monitoring: Standard Prometheus metrics

**Validation**: ✅ ALL CHECKS PASSED
- ✅ Container Status: `observatory-prometheus` running stably (no restart loops)
- ✅ Local Health: `http://localhost:9090/-/healthy` returns "Prometheus Server is Healthy"
- ✅ Tunnel Health: `https://prometheus.observatory.nkllon.com/-/healthy` accessible
- ✅ Web Interface: `https://prometheus.observatory.nkllon.com/` functional
- ✅ Observatory Status: 5/5 services healthy, Prometheus response time 0.008s
- ✅ Metrics Collection: All scrape targets operational and collecting data

**Configuration Management**:
- **Current**: Static configuration values for reliable startup
- **Future**: Environment variable substitution via init container or envsubst
- **Monitoring**: Configuration syntax validation in deployment process
- **Backup**: Original configuration preserved for reference

**Impact**:
- **Before**: Prometheus restart loop, Bad Gateway errors, no metrics collection
- **After**: Stable Prometheus, full tunnel access, complete metrics collection operational