# Runtime State Registry Requirements

## Introduction

The system has operational blindness because we're not leveraging our existing observability infrastructure. Redis is constantly screaming with real-time system state information, but we can't hear it. The CMS contains canonical configurations, but we don't know if runtime matches expectations. Prometheus and Grafana have rich service data, but it's not integrated with runtime state queries. The core requirement is to create a unified runtime state registry that bridges the gap between expected state (CMS), actual state (Redis), and observability data (Prometheus/Grafana).

## Requirements

### Requirement 1: Listen to Redis State Information

**User Story:** As a system operator, I want to hear what Redis is already screaming about system state so that I can instantly understand what's running without manual discovery.

#### Acceptance Criteria
1. WHEN I query "what's running" THEN Redis existing data SHALL be parsed and presented
2. WHEN Redis contains execution tracking data THEN it SHALL be interpreted as current operations
3. WHEN Redis contains service registration data THEN it SHALL be surfaced as active services
4. WHEN Redis contains health check data THEN it SHALL be displayed as system status
5. WHEN Redis contains configuration data THEN it SHALL be presented as runtime settings

### Requirement 2: Decode Redis's Screaming Data

**User Story:** As a developer, I want Redis's existing data decoded into human-readable system state so that I can understand what the system is telling me.

#### Acceptance Criteria
1. WHEN Redis contains DAG execution keys THEN they SHALL be decoded as "X is running on Y"
2. WHEN Redis contains Celery task data THEN it SHALL be interpreted as active operations
3. WHEN Redis contains service health keys THEN they SHALL be presented as service status
4. WHEN Redis contains configuration keys THEN they SHALL be displayed as runtime settings
5. WHEN Redis contains connection data THEN it SHALL be shown as service topology

### Requirement 3: Real-Time Redis Listening

**User Story:** As a system monitor, I want to hear Redis's real-time screaming so that I always know the current system state as it changes.

#### Acceptance Criteria
1. WHEN Redis keys change THEN the state reflection SHALL update immediately
2. WHEN new execution data appears THEN it SHALL be surfaced as new operations
3. WHEN service data disappears THEN it SHALL be reflected as stopped services
4. WHEN Redis pub/sub messages occur THEN they SHALL be interpreted as state changes
5. WHEN querying state THEN Redis timestamps SHALL indicate data freshness

### Requirement 4: Unified Reflective Module State Interpretation

**User Story:** As a system architect, I want to leverage the fact that every ReflectiveModule is already reporting to Redis so that accurate real-time state is guaranteed to be available.

#### Acceptance Criteria
1. WHEN any ReflectiveModule starts THEN its health, metrics, and status data SHALL already be in Redis via auto-registration
2. WHEN I query system state THEN ReflectiveModule Redis keys SHALL be the authoritative source for service health and configuration
3. WHEN services are unhealthy THEN their Redis health data SHALL reflect this immediately with health scores and error counts
4. WHEN services change configuration THEN their Redis state SHALL be updated automatically within 60 seconds
5. WHEN services crash THEN their Redis heartbeat SHALL stop updating within 60 seconds, indicating failure
6. WHEN ReflectiveModule auto-registration is working THEN all active services SHALL have corresponding Redis health keys

### Requirement 5: Query Interface for Redis State

**User Story:** As any system user, I want a simple query interface so that I can understand what Redis is screaming without complex Redis commands.

#### Acceptance Criteria
1. WHEN I query "what's running" THEN ReflectiveModule Redis keys SHALL be parsed for active services
2. WHEN I query "where is service X" THEN its Redis registration data SHALL provide location and connection info
3. WHEN I query "how is service X configured" THEN its Redis configuration keys SHALL be displayed
4. WHEN I query "what's on port Y" THEN Redis service data SHALL be searched for port bindings
5. WHEN I query "system health" THEN all ReflectiveModule health keys SHALL be aggregated

### Requirement 6: Automatic Stale State Cleanup

**User Story:** As a system administrator, I want stale runtime state automatically cleaned up so that the registry remains accurate.

#### Acceptance Criteria
1. WHEN a service hasn't updated its state for 60 seconds THEN it SHALL be marked as stale
2. WHEN a service is marked stale for 300 seconds THEN it SHALL be removed from active registry
3. WHEN cleanup runs THEN it SHALL verify process existence before removal
4. WHEN cleanup runs THEN it SHALL log all state changes for audit
5. WHEN querying state THEN stale services SHALL be clearly marked

### Requirement 7: Leverage Existing Redis Data

**User Story:** As a system operator, I want to immediately use the real-time data already in Redis so that I don't wait for new infrastructure to get runtime visibility.

#### Acceptance Criteria
1. WHEN I query runtime state THEN existing Redis keys SHALL be analyzed and presented
2. WHEN DAG executions are running THEN their status SHALL be visible from existing execution tracking
3. WHEN services have registered health data THEN it SHALL be surfaced in runtime queries
4. WHEN Celery tasks are active THEN their status SHALL be included in runtime state
5. WHEN existing Redis data contains service information THEN it SHALL be parsed and displayed

### Requirement 8: Redis Data Discovery and Analysis

**User Story:** As a developer, I want to discover what data is already available in Redis so that I can understand the current system state without guessing.

#### Acceptance Criteria
1. WHEN I run discovery THEN all Redis keys SHALL be scanned and categorized
2. WHEN analyzing keys THEN data patterns SHALL be identified and documented
3. WHEN finding service data THEN connection information SHALL be extracted
4. WHEN finding execution data THEN current operations SHALL be identified
5. WHEN finding configuration data THEN runtime settings SHALL be surfaced

### Requirement 9: Integration with Existing Services

**User Story:** As a system architect, I want the runtime registry to integrate with existing services so that we get immediate value without major refactoring.

#### Acceptance Criteria
1. WHEN ReflectiveModule services start THEN they SHALL automatically register runtime state via Redis auto-registration
2. WHEN Docker containers start THEN their runtime state SHALL be captured via Bonjour service discovery integration
3. WHEN Prometheus services start THEN their metrics endpoints SHALL be registered via service discovery targets
4. WHEN Grafana starts THEN its dashboard URLs SHALL be registered and dashboard intelligence extracted
5. WHEN any Beast Mode service starts THEN its complete observability endpoints SHALL be registered automatically
6. WHEN Hybrid Service Discovery system is active THEN it SHALL be leveraged for service detection and registration

### Requirement 10: Command Line Interface

**User Story:** As a developer, I want a command-line interface so that I can query runtime state from scripts and manual operations.

#### Acceptance Criteria
1. WHEN I run `runtime-state list` THEN I SHALL see all active services
2. WHEN I run `runtime-state show <service>` THEN I SHALL see complete service details
3. WHEN I run `runtime-state health` THEN I SHALL see system-wide health status
4. WHEN I run `runtime-state ports` THEN I SHALL see all port bindings
5. WHEN I run `runtime-state cleanup` THEN stale entries SHALL be removed

### Requirement 11: Web Dashboard Integration

**User Story:** As a system operator, I want runtime state visible in web dashboards so that I can monitor the system visually.

#### Acceptance Criteria
1. WHEN I access the Admin Dashboard at localhost:8889 THEN runtime state SHALL be displayed in the existing interface
2. WHEN services change state THEN dashboard SHALL update in real-time via WebSocket connections
3. WHEN I click on a service THEN I SHALL see detailed runtime information including multi-source data reconciliation
4. WHEN services are unhealthy THEN dashboard SHALL highlight them clearly with compliance scoring indicators
5. WHEN I need to debug THEN dashboard SHALL provide direct links to Prometheus metrics and Grafana dashboards
6. WHEN port conflicts exist THEN dashboard SHALL integrate with Port Conflict Detector for resolution guidance

### Requirement 12: Historical State Tracking

**User Story:** As a system analyst, I want historical runtime state information so that I can analyze system behavior over time.

#### Acceptance Criteria
1. WHEN services start/stop THEN events SHALL be logged with timestamps
2. WHEN configuration changes THEN old and new values SHALL be recorded
3. WHEN querying history THEN I SHALL get timeline of state changes
4. WHEN analyzing patterns THEN I SHALL have access to service lifecycle data
5. WHEN troubleshooting THEN I SHALL see what was running when issues occurred

### Requirement 13: CMS Configuration Authority Integration

**User Story:** As a system architect, I want the runtime state registry to use CMS as the authoritative source for canonical configurations so that I can detect configuration drift and ensure compliance.

#### Acceptance Criteria
1. WHEN querying service configuration THEN CMS SHALL be consulted for canonical/expected configuration
2. WHEN comparing runtime vs. canonical config THEN drift SHALL be detected and reported
3. WHEN a service is running but not in CMS THEN it SHALL be flagged as "ORPHANED"
4. WHEN a service is in CMS but not running THEN it SHALL be flagged as "MISSING"
5. WHEN configuration drift is detected THEN compliance score SHALL be calculated and remediation actions suggested

### Requirement 14: Configuration Drift Detection and Compliance

**User Story:** As a system operator, I want automatic detection of configuration drift so that I know when runtime configurations differ from canonical CMS definitions.

#### Acceptance Criteria
1. WHEN runtime config differs from CMS canonical THEN drift SHALL be detected and categorized by severity
2. WHEN calculating compliance THEN a quantitative score (0.0-1.0) SHALL be provided
3. WHEN drift is critical THEN automatic remediation SHALL be triggered if configured
4. WHEN drift is non-critical THEN alerts SHALL be generated for manual review
5. WHEN querying compliance THEN system-wide compliance metrics SHALL be available

### Requirement 15: Prometheus Integration for Service Discovery

**User Story:** As a system operator, I want the runtime state registry to leverage Prometheus service discovery as an authoritative source so that I don't duplicate service discovery infrastructure.

#### Acceptance Criteria
1. WHEN discovering services THEN Prometheus targets SHALL be used as primary service discovery source
2. WHEN determining service health THEN Prometheus 'up' metric SHALL be authoritative health indicator
3. WHEN querying service metrics THEN Prometheus data SHALL be integrated with runtime state
4. WHEN analyzing service dependencies THEN Prometheus metric relationships SHALL be parsed
5. WHEN services are discovered via Prometheus THEN they SHALL be cross-referenced with CMS definitions

### Requirement 16: Grafana Dashboard Intelligence Integration

**User Story:** As a system analyst, I want the runtime state registry to extract service intelligence from existing Grafana dashboards so that service relationships and monitoring patterns are automatically understood.

#### Acceptance Criteria
1. WHEN analyzing service dependencies THEN Grafana dashboard queries SHALL be parsed for relationships
2. WHEN discovering new services THEN Grafana dashboards SHALL be auto-provisioned based on service patterns
3. WHEN querying service observability THEN existing Grafana dashboard links SHALL be provided
4. WHEN Grafana alerts exist THEN they SHALL be integrated as health indicators
5. WHEN service topology changes THEN Grafana dashboards SHALL be updated automatically

### Requirement 17: Multi-Source State Reconciliation

**User Story:** As a system architect, I want runtime state reconciled from multiple authoritative sources so that I have a complete and accurate view of system state.

#### Acceptance Criteria
1. WHEN multiple sources provide conflicting data THEN conflict resolution rules SHALL determine authoritative source
2. WHEN CMS, Redis, Prometheus, and Grafana data exists THEN it SHALL be merged into unified service state
3. WHEN sources are unavailable THEN graceful degradation SHALL provide partial state with clear indicators
4. WHEN data freshness varies THEN timestamps SHALL indicate data currency and reliability
5. WHEN querying state THEN source attribution SHALL be provided for all data elements

### Requirement 18: Observability-Native Query Interface

**User Story:** As a system operator, I want to query runtime state using observability-native concepts so that I can leverage existing monitoring knowledge and workflows.

#### Acceptance Criteria
1. WHEN querying services THEN Prometheus metric queries SHALL be supported natively
2. WHEN requesting dashboards THEN Grafana dashboard links SHALL be provided automatically
3. WHEN analyzing alerts THEN Alertmanager integration SHALL show firing alerts
4. WHEN investigating issues THEN observability tool deep-links SHALL be generated
5. WHEN exploring metrics THEN Prometheus query suggestions SHALL be provided based on service type

### Requirement 19: Configuration Compliance Auditing

**User Story:** As a compliance officer, I want comprehensive auditing of configuration compliance so that I can ensure systems meet governance requirements.

#### Acceptance Criteria
1. WHEN auditing system compliance THEN percentage of CMS-compliant services SHALL be reported
2. WHEN identifying orphaned services THEN services running without CMS definitions SHALL be listed
3. WHEN finding missing services THEN CMS-defined services not running SHALL be identified
4. WHEN tracking compliance over time THEN historical compliance trends SHALL be available
5. WHEN generating compliance reports THEN detailed drift analysis SHALL be included

### Requirement 20: Auto-Remediation and Self-Healing

**User Story:** As a system administrator, I want automatic remediation of configuration drift so that systems self-heal when safe to do so.

#### Acceptance Criteria
1. WHEN critical configuration drift is detected THEN automatic remediation SHALL be triggered if configured
2. WHEN remediation is unsafe THEN manual intervention SHALL be required with clear guidance
3. WHEN auto-remediation occurs THEN all actions SHALL be logged for audit
4. WHEN remediation fails THEN escalation procedures SHALL be triggered
5. WHEN remediation succeeds THEN compliance scores SHALL be updated automatically

### Requirement 21: Specification State Authority (Spec-State)

**User Story:** As a system architect, I want the runtime state registry to understand what SHOULD be running according to architectural specifications so that I can detect when the system deviates from intended design.

#### Acceptance Criteria
1. WHEN querying desired state THEN specification definitions SHALL define what services should be running
2. WHEN comparing actual vs. spec-state THEN deviations SHALL be detected and reported as "SPEC_DRIFT"
3. WHEN services are running but not in spec THEN they SHALL be flagged as "UNSPECIFIED"
4. WHEN spec defines services not running THEN they SHALL be flagged as "SPEC_MISSING"
5. WHEN spec-state changes THEN impact analysis SHALL show what runtime changes are required

### Requirement 22: Three-Layer State Reconciliation

**User Story:** As a system operator, I want to understand the relationship between spec-state (what should run), CMS-state (how it should be configured), and runtime-state (what is actually running) so that I can maintain system integrity.

#### Acceptance Criteria
1. WHEN querying system state THEN all three layers SHALL be compared: Spec → CMS → Runtime
2. WHEN spec-state defines a service THEN CMS SHALL have corresponding configuration
3. WHEN CMS has configuration THEN runtime SHALL have corresponding active service
4. WHEN any layer is missing THEN the gap SHALL be identified with remediation guidance
5. WHEN layers conflict THEN conflict resolution SHALL follow hierarchy: Spec > CMS > Runtime

### Requirement 23: Specification Compliance Monitoring

**User Story:** As a system architect, I want continuous monitoring of specification compliance so that architectural drift is detected immediately.

#### Acceptance Criteria
1. WHEN spec defines required services THEN runtime SHALL be monitored for their presence
2. WHEN spec defines service relationships THEN runtime topology SHALL be validated against spec
3. WHEN spec defines performance requirements THEN runtime metrics SHALL be compared to spec SLAs
4. WHEN spec defines security requirements THEN runtime configuration SHALL be validated for compliance
5. WHEN spec changes THEN runtime impact analysis SHALL be automatically generated

### Requirement 24: DAG-Driven Spec State Calculation

**User Story:** As a system engineer, I want specification state calculated from DAG dependencies so that the desired system topology is mathematically derived from architectural requirements.

#### Acceptance Criteria
1. WHEN DAG defines service dependencies THEN spec-state SHALL include all required services
2. WHEN DAG calculates execution order THEN spec-state SHALL reflect proper service startup sequence
3. WHEN DAG identifies critical path THEN spec-state SHALL mark essential services for high availability
4. WHEN DAG detects cycles THEN spec-state SHALL flag architectural inconsistencies
5. WHEN DAG topology changes THEN spec-state SHALL be recalculated automatically

### Requirement 25: AI Memory Palace Context Integration

**User Story:** As an AI assistant user, I want the runtime state registry to integrate with AI Memory Palace for context-aware queries so that I can get O(1) system state information without expensive discovery operations.

#### Acceptance Criteria
1. WHEN AI Memory Palace context is available THEN runtime state queries SHALL use cached context for O(1) responses
2. WHEN runtime state changes THEN context events SHALL be contributed to AI Memory Palace session context
3. WHEN validating AI context THEN runtime state SHALL be used to verify context accuracy against current system reality
4. WHEN context is stale THEN runtime state SHALL refresh specific data and update context automatically
5. WHEN querying "what's running" from context THEN response SHALL be provided in <2 seconds without full system discovery
6. WHEN context lacks runtime state data THEN fallback to traditional discovery SHALL be seamless and transparent

### Requirement 26: Security and Access Control

**User Story:** As a security administrator, I want runtime state access controlled so that sensitive information is protected appropriately.

#### Acceptance Criteria
1. WHEN storing runtime state THEN sensitive credentials SHALL be excluded and masked
2. WHEN querying state THEN access SHALL be logged for audit with user attribution and timestamp
3. WHEN displaying configuration THEN sensitive values SHALL be masked with configurable reveal options
4. WHEN accessing remotely THEN authentication SHALL be required with role-based access control
5. WHEN storing connection strings THEN they SHALL be encrypted at rest using industry-standard encryption
6. WHEN audit logs are generated THEN they SHALL include correlation IDs for traceability