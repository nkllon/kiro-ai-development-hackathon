# Service Auto-Start Governance Specification

**Status:** ✅ Ready for DAG Execution
**Last Updated:** 2025-10-03
**Context:** System Health Mitigation (MITIGATION_REPORT_20251003.md)

---

## Quick Start

### Execute DAG

```bash
# Validate DAG structure
python scripts/execute_service_autostart_dag.py --validate

# Show current status
python scripts/execute_service_autostart_dag.py --status

# Execute MVP (Phase 1 + critical tasks)
python scripts/execute_service_autostart_dag.py --phase mvp --dry-run

# Execute specific task
python scripts/execute_service_autostart_dag.py --task 1.0

# Execute complete Phase 1
python scripts/execute_service_autostart_dag.py --phase 1
```

---

## Specification Files

| File | Purpose | Status |
|------|---------|--------|
| `requirements.md` | 8 comprehensive requirements with acceptance criteria | ✅ Complete |
| `design.md` | Detailed architecture and component design | ✅ Complete |
| `tasks.md` | Phase-based implementation plan (24 tasks) | ✅ Complete |
| `DAG_EXECUTION_PLAN.md` | DAG structure and execution strategy | ✅ Complete |
| `README.md` | This file - quick reference | ✅ Complete |

---

## Overview

This specification addresses the **service auto-start governance gap** identified in the system health mitigation report where services are configured with Docker restart policies but lack proper system integration for automatic startup.

### Critical Issues Addressed

From `MITIGATION_REPORT_20251003.md`:
- ✅ Cloudflare Tunnel requires auto-restart policy
- ✅ Google Workspace MCP requires auto-restart policy
- ✅ Directus CMS health check misconfiguration (IPv6/IPv4)
- ✅ Observatory Engagement missing /metrics endpoint
- ✅ Prometheus Exporters not deployed or misconfigured

---

## Key Features

### 1. Cross-Platform Auto-Start
- macOS LaunchAgent
- Linux systemd
- Docker Compose restart policies
- Kubernetes deployments (future)

### 2. Health Check Standardization
- Container-native tool detection (wget, curl, nc, python, node)
- IPv6/IPv4 compatibility fixes
- Structured health responses
- Dependency verification

### 3. Boot Simulation Testing
- Clean boot simulation
- Dependency ordering validation
- Failure scenario testing
- Performance benchmarking

### 4. Comprehensive Monitoring
- Prometheus metrics integration
- Cross-platform log aggregation
- Startup pattern analysis
- Failure alerting

### 5. Requirements Governance
- WHO/WHEN/HOW/WHAT validation
- Passive voice detection
- Acceptance test generation
- Traceability system

---

## DAG Execution Strategy

### MVP (31 hours / 4 business days)
**Goal:** Fix current mitigation report issues

1. **Phase 1** (Tasks 1.0-1.3): Foundation - 16 hours
2. **Task 4.0**: CMS Integration - 6 hours
3. **Task 2.2**: Monitoring - 4 hours
4. **Task 3.1**: Deployment Integration - 5 hours

**MVP Deliverables:**
- ✅ Directus CMS health check fixed (127.0.0.1 vs localhost)
- ✅ Cloudflare tunnel auto-restart configured
- ✅ Google Workspace MCP auto-restart configured
- ✅ Framework proven with real service
- ✅ Basic monitoring in place

### Full Production (58 hours / 7.5 business days)
**Goal:** All services under governance

After MVP, add:
1. **Phase 2** (Tasks 2.0-2.1): Testing & Recovery - 11 hours
2. **Task 4.1**: All Docker Services - 8 hours
3. **Phase 3** (Tasks 3.0, 3.2): Governance & Docs - 8 hours

### Long-term (2-3 months)
**Goal:** Self-healing, cross-platform, continuous improvement

1. **Task 4.2**: Cross-platform - 10 hours
2. **Phase 5**: Advanced features - 15+ hours
3. **Phase 6**: Knowledge management - 8+ hours

---

## Task Dependencies

```
Phase 1 (Foundation - Sequential with some parallelism)
├── 1.0 Platform Abstraction Layer (no deps)
├── 1.1 Service Registry (depends: 1.0)
├── 1.2 Health Check System (depends: 1.0)
└── 1.3 Config Manager (depends: 1.0, 1.1, 1.2)

Phase 2 & 3 (Parallel after Phase 1)
├── 2.0 Boot Simulation (depends: 1.3)
├── 2.1 Failure Recovery (depends: 1.3)
├── 2.2 Startup Metrics (depends: 1.3)
├── 3.0 Requirements Governance (depends: 1.3)
├── 3.1 Deployment Integration (depends: 1.3)
└── 3.2 Documentation System (depends: 1.3)

Phase 4 (Sequential validation)
├── 4.0 CMS Integration (depends: Phase 1-3)
├── 4.1 All Docker Services (depends: 4.0)
└── 4.2 Cross-Platform (depends: 4.1)
```

---

## Success Metrics

### MVP Success
- [ ] Directus CMS auto-starts on boot without manual intervention
- [ ] Health check passes (no IPv6/IPv4 issues)
- [ ] Cloudflare tunnel auto-restarts on failure
- [ ] Google Workspace MCP auto-starts on boot
- [ ] Boot simulation test passes for CMS
- [ ] Startup metrics visible in Prometheus

### Full Production Success
- [ ] All 11 Docker services auto-start reliably
- [ ] Multi-service boot completes in <120 seconds
- [ ] Zero manual intervention required
- [ ] Comprehensive monitoring operational
- [ ] Deployment checklists include auto-start verification

---

## Requirements Traceability

| Requirement | Design Component | Implementation Tasks | Tests |
|-------------|------------------|---------------------|-------|
| Req 1: Auto-Start Framework | AutoStartManager | 1.0, 1.3, 4.0 | Boot simulation |
| Req 2: Health Check Std | HealthCheckStandardizer | 1.2, 4.0 | Health check tests |
| Req 3: Requirements Gov | RequirementsValidator | 3.0 | Validation tests |
| Req 4: Deployment Integration | DeploymentIntegrator | 3.1, 4.1 | Deployment tests |
| Req 5: Cross-Platform | Platform Adapters | 1.0, 4.2 | Platform tests |
| Req 6: Monitoring | MetricsCollector | 2.2 | Metrics tests |
| Req 7: Failure Recovery | RecoveryManager | 2.1 | Resilience tests |
| Req 8: Documentation | DocGenerator | 3.2 | Doc tests |

---

## Architecture Components

### Core Classes
- `PlatformAdapter` - Abstract interface for platform-specific operations
- `AutoStartManager` - Configuration generation and management (ReflectiveModule)
- `ServiceRegistry` - Central registry with dependency resolution
- `HealthCheckStandardizer` - Container-native health check generation
- `BootSimulationEngine` - Testing and validation (ReflectiveModule)
- `RecoveryManager` - Failure recovery and retry logic
- `MetricsCollector` - Prometheus integration (ReflectiveModule)

### Platform Implementations
- `MacOSLaunchAgentAdapter` - LaunchAgent plist generation
- `LinuxSystemdAdapter` - systemd unit file generation
- `DockerComposeAdapter` - Compose service configuration
- `KubernetesAdapter` - K8s deployment generation (future)

---

## Files to be Created

### Phase 1 - Foundation (16 hours)
```
src/system_architecture/autostart/
├── __init__.py
├── platform_adapter.py
├── models.py
├── service_registry.py
├── health_check.py
├── health_templates.py
├── config_manager.py
└── platforms/
    ├── __init__.py
    ├── macos.py
    ├── linux.py
    └── docker.py

tests/unit/system_architecture/autostart/
├── test_platforms.py
└── test_service_registry.py

tests/integration/system_architecture/autostart/
├── test_health_checks.py
└── test_config_manager.py
```

### Phase 2 - Testing (15 hours)
```
src/system_architecture/autostart/
├── boot_simulator.py
├── test_scenarios.py
├── recovery_manager.py
├── retry_policies.py
├── metrics_collector.py
└── log_aggregator.py

tests/
├── unit/system_architecture/autostart/
│   ├── test_recovery.py
│   └── test_metrics.py
└── integration/system_architecture/autostart/
    └── test_boot_simulation.py
```

### Phase 3 - Governance (13 hours)
```
src/system_architecture/autostart/
├── requirements_validator.py
├── requirements_templates.py
├── deployment_integrator.py
├── makefile_generator.py
├── doc_generator.py
└── templates/
    ├── setup_macos.md.j2
    ├── setup_linux.md.j2
    ├── troubleshooting.md.j2
    └── runbook.md.j2

tests/
├── unit/system_architecture/autostart/
│   ├── test_requirements.py
│   └── test_documentation.py
└── integration/system_architecture/autostart/
    └── test_deployment.py
```

### Phase 4 - Integration (24 hours)
```
config/autostart/
├── directus-cms.json
├── observatory.json
├── grafana.json
└── ... (all 11 services)

~/Library/LaunchAgents/
├── com.beastmode.directus-cms.plist
├── com.beastmode.observatory.plist
└── ... (all services)

Modified files:
- docker-compose.directus-fixed.yml (health check fix)
- docker-compose.yml (restart policies)
```

---

## Risk Mitigation

### Technical Risks
- **Platform incompatibility**: Test on all target platforms before rollout
- **Health check tool unavailability**: Multi-tool fallback strategy
- **Service dependency complexity**: Gradual rollout, start with simple services
- **Performance impact**: Monitoring from day 1, optimization built in

### Operational Risks
- **Team adoption resistance**: Prove value with CMS first, clear benefits
- **Existing service disruption**: Rollback procedures, careful migration
- **Documentation drift**: Automated generation where possible
- **Knowledge transfer gaps**: Training materials, comprehensive docs

---

## Next Steps

### Today
1. ✅ Validate spec completeness
2. ✅ Create DAG execution plan
3. ✅ Generate DAG orchestrator script
4. ⏳ Execute Task 1.0 (Platform Abstraction Layer)

### This Week
1. Execute Phase 1 (Foundation)
2. Execute Task 4.0 (CMS Integration - MVP validation)
3. Execute Task 2.2 (Monitoring)
4. Review progress and adjust timeline

### Next Week
1. Execute Phase 2 (Testing & Recovery)
2. Execute Task 4.1 (All Docker Services)
3. Execute Phase 3 (Governance & Docs)
4. Production readiness review

---

## Related Documents

- **Mitigation Report**: `MITIGATION_REPORT_20251003.md` - Root cause analysis
- **Health Report**: `system-health-report-20251003.md` - Current system state
- **Action Log**: `mitigation-actions.log` - Detailed mitigation actions
- **CMS Governance**: `.kiro/steering/mcp-server-configuration-governance.md`
- **Deployment Governance**: `.kiro/steering/deployment-data-governance.md`

---

## Contact & Support

For questions or issues with this specification:
1. Review the design document (`design.md`) for architectural details
2. Check the DAG execution plan for task-specific information
3. Consult the mitigation report for context on issues being addressed
4. Run DAG validation to ensure structure integrity

---

**Last Validation:** 2025-10-03 22:07:01
**DAG Status:** ✓ Valid structure, 13 tasks, 1 ready to execute
**Next Executable:** Task 1.0 - Platform Detection and Abstraction Layer
