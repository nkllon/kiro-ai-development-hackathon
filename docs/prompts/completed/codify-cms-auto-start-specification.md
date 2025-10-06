# Prompt: Codify CMS Auto-Start Findings into Full DAG-Ready Specification

## Context

We've completed a comprehensive root cause analysis of why the Directus CMS was not auto-starting. The investigation revealed a **requirements-to-implementation gap** where passive requirements ("SHALL be available") led to incomplete automation. The findings, solution, and permanent corrective actions are documented in:

- `docs/cms/cms-auto-start-root-cause-analysis.md` - Full analysis (15,000+ words)
- `docs/cms/CMS_AUTO_START_SOLUTION_SUMMARY.md` - Executive summary

## Objective

Transform these findings into a **complete Beast Mode specification** following the RM-DDD framework pattern, ready for DAG orchestrator execution. The specification should prevent similar auto-start issues across ALL Beast Mode services.

## Input Documents

1. **Root Cause Analysis:** `docs/cms/cms-auto-start-root-cause-analysis.md`
2. **Solution Summary:** `docs/cms/CMS_AUTO_START_SOLUTION_SUMMARY.md`
3. **Original CMS Spec:** `.kiro/specs/directus-ai-memory-palace-integration/`
4. **Pattern Reference:** Any existing spec in `.kiro/specs/` for structure

## Output Requirements

Create a new specification at:
```
.kiro/specs/service-auto-start-governance/
├── requirements.md
├── design.md
└── tasks.md
```

### Specification Scope

**Title:** Service Auto-Start Governance & Enforcement

**Purpose:** Systematically ensure ALL Beast Mode services auto-start correctly on system boot/login, with proper health checks, monitoring, and verification.

**Key Principle:** "Requirements must specify HOW, not just WHAT" - from findings

## Detailed Instructions

### 1. Requirements Document (`requirements.md`)

Transform the lessons learned into **active, specific requirements** that prevent future auto-start gaps:

#### Section 1: Auto-Start Requirements
From findings: "restart: unless-stopped ≠ auto-start"

Create requirements for:
- **R1:** System SHALL provide auto-start for all critical services (not just restart-on-failure)
- **R2:** Auto-start mechanisms SHALL be platform-specific (LaunchAgent/systemd/Docker Compose with proper init)
- **R3:** Services SHALL verify auto-start works through reboot testing
- **R4:** Auto-start configuration SHALL be documented in deployment procedures

Use the improved requirements pattern from findings:
```
❌ BAD: "Service SHALL be available"
✅ GOOD: "System SHALL auto-start service at boot using [LaunchAgent/systemd]
         AND verify availability within [N] seconds using [specific tool]
         AND log startup to [location]"
```

#### Section 2: Health Check Requirements
From findings: Health checks must use tools available in container

Create requirements for:
- **R5:** Health checks SHALL use only tools available in base container image
- **R6:** Health checks SHALL be tested before deployment
- **R7:** Health check failures SHALL trigger alerts and logging
- **R8:** Health checks SHALL have appropriate timeouts and retry logic

#### Section 3: Service Discovery Requirements
From findings: No Makefile targets, no deployment integration

Create requirements for:
- **R9:** All services SHALL be registered in Makefile with start/stop/status targets
- **R10:** Services SHALL appear in `make help` output
- **R11:** Services SHALL be included in deployment checklists
- **R12:** Service dependencies SHALL be explicitly documented and enforced

#### Section 4: Verification Requirements
From findings: No acceptance test for auto-start

Create requirements for:
- **R13:** Fresh boot scenarios SHALL be tested before deployment
- **R14:** Auto-start SHALL be verified through automated testing
- **R15:** Service availability SHALL be monitored post-boot
- **R16:** Startup failures SHALL trigger rollback procedures

#### Section 5: Documentation Requirements
From findings: Documentation gaps led to manual-only operation

Create requirements for:
- **R17:** Auto-start configuration SHALL be documented in deployment guide
- **R18:** Runbooks SHALL include service recovery procedures
- **R19:** Architecture diagrams SHALL show service startup dependencies
- **R20:** Deployment checklists SHALL verify auto-start configuration

**Format:** Use standard Beast Mode requirements format with User Stories and Acceptance Criteria

### 2. Design Document (`design.md`)

Create a comprehensive design based on the permanent solution from findings:

#### Section 1: Architecture Overview
Design a **Service Auto-Start Framework** that includes:

1. **Auto-Start Abstraction Layer**
   - Platform-agnostic interface
   - Platform-specific implementations (macOS LaunchAgent, Linux systemd, Docker init)
   - Configuration management

2. **Health Check Framework**
   - Container-aware tool detection
   - Health check template generator
   - Verification testing

3. **Service Registry**
   - Centralized service catalog
   - Dependency tracking
   - Auto-start status monitoring

4. **Verification System**
   - Boot simulation testing
   - Health check validation
   - Deployment verification

#### Section 2: Component Design

**Component 1: ServiceAutoStarter**
```python
class ServiceAutoStarter(ReflectiveModule):
    """Manages auto-start configuration for all Beast Mode services."""

    def configure_autostart(
        self,
        service_name: str,
        platform: AutoStartPlatform,
        config: AutoStartConfig
    ) -> AutoStartResult

    def verify_autostart(
        self,
        service_name: str
    ) -> VerificationResult

    def test_boot_scenario(
        self,
        service_name: str
    ) -> TestResult
```

**Component 2: HealthCheckValidator**
```python
class HealthCheckValidator(ReflectiveModule):
    """Validates health checks use available tools."""

    def detect_available_tools(
        self,
        container_image: str
    ) -> List[str]

    def validate_health_check(
        self,
        health_check: HealthCheckConfig,
        available_tools: List[str]
    ) -> ValidationResult

    def generate_health_check(
        self,
        service: ServiceConfig,
        available_tools: List[str]
    ) -> HealthCheckConfig
```

**Component 3: ServiceRegistry**
```python
class ServiceRegistry(ReflectiveModule):
    """Central registry of all Beast Mode services."""

    def register_service(
        self,
        service: ServiceDefinition
    ) -> RegistrationResult

    def get_service_dependencies(
        self,
        service_name: str
    ) -> List[ServiceDependency]

    def verify_all_autostart(self) -> RegistryStatus
```

#### Section 3: Platform Implementations

Design platform-specific implementations:

**macOS LaunchAgent Implementation:**
- Template generation
- Plist file creation
- launchctl integration
- Log management

**Linux systemd Implementation:**
- Service file generation
- systemctl integration
- Dependency management
- Boot sequence ordering

**Docker Init Implementation:**
- restart policy management
- Init process integration
- Health check verification

#### Section 4: Integration Points

Show how this integrates with:
- Makefile system
- Deployment procedures
- Observatory monitoring
- DAG orchestrator
- Prometheus metrics

#### Section 5: Data Models

Define all data structures:
```python
@dataclass
class ServiceDefinition:
    name: str
    type: ServiceType
    docker_compose_file: Optional[Path]
    port: int
    dependencies: List[str]
    auto_start_required: bool
    health_check: HealthCheckConfig
    platform_configs: Dict[AutoStartPlatform, PlatformConfig]

@dataclass
class HealthCheckConfig:
    endpoint: str
    tool: str  # wget, curl, nc, etc.
    timeout: int
    retries: int
    interval: int
    start_period: int

@dataclass
class AutoStartConfig:
    enabled: bool
    trigger: AutoStartTrigger  # boot, login, docker-start
    user: Optional[str]
    working_directory: Path
    environment: Dict[str, str]
    log_file: Path
```

#### Section 6: Failure Scenarios & Recovery

Design recovery procedures for:
- Health check failures
- Auto-start failures
- Dependency failures
- Platform-specific issues

### 3. Tasks Document (`tasks.md`)

Break down implementation into **DAG-executable tasks** following the pattern from the findings:

#### Task Structure

Each task must be:
- **Independently executable** (isolated context)
- **Mathematically validated** (no circular dependencies)
- **Parallelizable** where possible
- **Verifiable** (clear success criteria)

#### Task Organization (Example)

**Phase 1: Foundation (Parallel)**
- Task 1.1: Create ServiceAutoStarter base class
- Task 1.2: Create HealthCheckValidator base class
- Task 1.3: Create ServiceRegistry base class
- Task 1.4: Define all data models

**Phase 2: Platform Implementations (Parallel after Phase 1)**
- Task 2.1: Implement macOS LaunchAgent generator
- Task 2.2: Implement Linux systemd generator
- Task 2.3: Implement Docker init integration
- Task 2.4: Create health check tool detector

**Phase 3: Service Integration (Parallel after Phase 2)**
- Task 3.1: Register Directus in ServiceRegistry
- Task 3.2: Register Observatory in ServiceRegistry
- Task 3.3: Register Monitoring Daemon in ServiceRegistry
- Task 3.4: Add Makefile targets for all services

**Phase 4: Verification System (Parallel after Phase 3)**
- Task 4.1: Create boot simulation test framework
- Task 4.2: Implement health check validation tests
- Task 4.3: Create deployment verification script
- Task 4.4: Add auto-start to deployment checklist

**Phase 5: Documentation (Parallel after Phase 4)**
- Task 5.1: Update deployment guide with auto-start procedures
- Task 5.2: Create service recovery runbooks
- Task 5.3: Update architecture diagrams
- Task 5.4: Generate service catalog documentation

**Phase 6: Monitoring Integration (After Phase 5)**
- Task 6.1: Add auto-start metrics to Prometheus
- Task 6.2: Create Grafana dashboard for service health
- Task 6.3: Configure alerts for auto-start failures
- Task 6.4: Integrate with Observatory monitoring

**Phase 7: Migration (After Phase 6)**
- Task 7.1: Migrate Directus to new auto-start framework
- Task 7.2: Migrate Observatory to new auto-start framework
- Task 7.3: Migrate Monitoring Daemon to new auto-start framework
- Task 7.4: Verify all services auto-start correctly

**Phase 8: Validation (Final Phase)**
- Task 8.1: Perform fresh boot test on macOS
- Task 8.2: Perform fresh boot test on Linux
- Task 8.3: Verify all health checks pass
- Task 8.4: Update compliance documentation

#### Task Format (per task)

For EACH task, provide:

```markdown
### Task X.Y: [Task Name]

**Dependencies:** [List task IDs this depends on]
**Estimated Duration:** [Time estimate]
**Priority:** [High/Medium/Low]
**Parallel Group:** [Which tasks can run in parallel]

**Description:**
[Clear description of what to do]

**Acceptance Criteria:**
1. WHEN [condition] THEN [expected result]
2. WHEN [condition] THEN [expected result]
...

**Implementation Notes:**
- [Specific technical details]
- [Files to create/modify]
- [Tools/technologies to use]

**Verification:**
```bash
# Commands to verify task completion
[verification commands]
```

**Rollback:**
```bash
# Commands to rollback if task fails
[rollback commands]
```
```

#### DAG Validation Requirements

The tasks.md MUST:
1. **Define a valid DAG** (no circular dependencies)
2. **Identify parallel execution groups** (independent tasks)
3. **Specify clear dependencies** between tasks
4. **Provide verification for each task**
5. **Include rollback procedures**

Expected parallelization efficiency: **70-90%** based on independent task groups

## Key Insights to Incorporate

From the findings, ensure the specification addresses:

1. **"Requirements must specify HOW, not just WHAT"**
   - All requirements use active voice
   - Specify exact mechanisms (LaunchAgent, systemd, etc.)
   - Define verification methods
   - Include timing constraints

2. **"restart ≠ auto-start"**
   - Clearly distinguish restart policies from auto-start
   - Require both for resilience
   - Document the difference

3. **"Container-native tools only"**
   - Health checks must use tools in the image
   - Provide tool detection mechanism
   - Generate appropriate health checks

4. **"Testing prevents deployment gaps"**
   - Require boot simulation tests
   - Verify before deployment
   - Include in acceptance criteria

5. **"Documentation is part of implementation"**
   - Docs are required deliverables
   - Include in tasks
   - Verify completeness

## Success Criteria

The specification is complete when:

1. **Requirements** are specific, active, and testable
2. **Design** provides clear architecture and component interactions
3. **Tasks** form a valid DAG ready for orchestrator execution
4. **Tasks** include verification and rollback procedures
5. **Specification** prevents the auto-start gap from recurring
6. **Pattern** is reusable for other service governance needs

## Output Format

Create three files following Beast Mode spec conventions:

```
.kiro/specs/service-auto-start-governance/
├── requirements.md       # 20+ requirements across 5+ categories
├── design.md            # Complete architecture with diagrams (Mermaid)
└── tasks.md             # 30+ tasks organized in 8 phases
```

Each file should:
- Follow Beast Mode RM-DDD patterns
- Reference the findings documents
- Use consistent terminology
- Include code examples where appropriate
- Provide verification methods

## Additional Considerations

1. **Reusability:** Design should work for ANY Beast Mode service, not just CMS
2. **Platform Flexibility:** Support macOS, Linux, Docker deployments
3. **Monitoring Integration:** Connect to existing Observatory/Prometheus
4. **Failure Resilience:** Graceful degradation when auto-start fails
5. **Future-Proofing:** Easy to add new platforms or services

## References

- Root Cause Analysis: `docs/cms/cms-auto-start-root-cause-analysis.md`
- Solution Summary: `docs/cms/CMS_AUTO_START_SOLUTION_SUMMARY.md`
- Original CMS Spec: `.kiro/specs/directus-ai-memory-palace-integration/`
- DAG Orchestrator Pattern: Check any completed spec with tasks.md for reference
- Requirements Pattern: Use improved format from findings section

## Execution

Once specification is created:

1. Validate DAG using: `python scripts/validate_dag.py .kiro/specs/service-auto-start-governance/tasks.md`
2. Review for completeness
3. Execute via DAG orchestrator: `python scripts/execute_dag.py .kiro/specs/service-auto-start-governance/tasks.md`

---

**Prompt Ready for Execution**
**Expected Output:** Complete specification ready for DAG orchestration
**Time Estimate:** Specification creation: 30-60 minutes | Implementation via DAG: 4-8 hours
