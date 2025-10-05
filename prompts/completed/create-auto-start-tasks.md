# Create Service Auto-Start Governance Tasks Document

## Context

Requirements and design documents are complete for Service Auto-Start Governance specification. Now need to create the tasks.md with DAG-executable tasks.

## Task

Create tasks.md that breaks down the implementation into parallelizable, independently executable tasks ready for DAG orchestrator.

## Input

- Requirements: `.kiro/specs/service-auto-start-governance/requirements.md`
- Design: `.kiro/specs/service-auto-start-governance/design.md` (will be created)
- Pattern Reference: `.kiro/specs/directus-ai-memory-palace-integration/tasks.md`
- DAG Pattern: Successful parallelized task specifications

## Output

Create: `.kiro/specs/service-auto-start-governance/tasks.md`

## Task Organization Requirements

### Phase Structure

Organize into 8 phases as outlined in original prompt:

**Phase 1: Foundation** (4 tasks, all parallel)
- Task 1.1: Create ServiceAutoStarter base class
- Task 1.2: Create HealthCheckValidator base class
- Task 1.3: Create ServiceRegistry base class
- Task 1.4: Define all data models and types

**Phase 2: Platform Implementations** (4 tasks, parallel after Phase 1)
- Task 2.1: Implement macOS LaunchAgent generator
- Task 2.2: Implement Linux systemd generator
- Task 2.3: Implement Docker restart policy integration
- Task 2.4: Create health check tool detector

**Phase 3: Service Integration** (4 tasks, parallel after Phase 2)
- Task 3.1: Register Directus in ServiceRegistry
- Task 3.2: Register Observatory in ServiceRegistry
- Task 3.3: Register Monitoring Daemon in ServiceRegistry
- Task 3.4: Generate Makefile targets for all services

**Phase 4: Verification System** (4 tasks, parallel after Phase 3)
- Task 4.1: Create boot simulation test framework
- Task 4.2: Implement health check validation tests
- Task 4.3: Create deployment verification script
- Task 4.4: Add auto-start items to deployment checklist

**Phase 5: Documentation** (4 tasks, parallel after Phase 4)
- Task 5.1: Auto-generate service documentation
- Task 5.2: Create service recovery runbooks
- Task 5.3: Update architecture diagrams
- Task 5.4: Generate service catalog

**Phase 6: Monitoring Integration** (4 tasks, sequential after Phase 5)
- Task 6.1: Add auto-start metrics to Prometheus
- Task 6.2: Create Grafana dashboard for service health
- Task 6.3: Configure Alertmanager for auto-start failures
- Task 6.4: Integrate with Observatory WebSocket events

**Phase 7: Migration** (4 tasks, sequential after Phase 6)
- Task 7.1: Migrate Directus to new framework
- Task 7.2: Migrate Observatory to new framework
- Task 7.3: Migrate Monitoring Daemon to new framework
- Task 7.4: Verify all services auto-start correctly

**Phase 8: Validation** (4 tasks, sequential after Phase 7)
- Task 8.1: Perform fresh boot test on macOS
- Task 8.2: Perform fresh boot test on Linux
- Task 8.3: Verify all health checks pass
- Task 8.4: Update compliance documentation

**Total: 32 tasks across 8 phases**

### Task Format (Required for Each Task)

```markdown
### Task X.Y: [Task Name]

**Dependencies:** [List of Task IDs, or "None" for Phase 1]
**Estimated Duration:** [e.g., 2 hours, 30 minutes]
**Priority:** [High/Medium/Low]
**Parallel Group:** [Phase X tasks are parallel]

**Description:**
[2-3 paragraph description of what to do]

**Acceptance Criteria:**
1. WHEN [condition] THEN [expected result]
2. WHEN [condition] THEN [expected result]
3. WHEN [condition] THEN [expected result]
[At least 3-5 criteria per task]

**Implementation Notes:**
- File to create: [path]
- Class/function to implement: [signature]
- Key algorithms: [brief description]
- Integration points: [what this connects to]
- Platform considerations: [platform-specific details]

**Files Created/Modified:**
- `path/to/file.py` - [purpose]
- `path/to/test.py` - [purpose]

**Verification:**
```bash
# Commands to verify task completion
pytest tests/unit/test_specific_task.py -v
python -m src.module.verify_task
make verify-task-X-Y
```

**Rollback:**
```bash
# Commands to rollback if task fails
git checkout path/to/file.py
rm -f path/to/generated/config
launchctl unload /path/to/plist  # if applicable
```

**Related Requirements:** R1, R2, R5  [list requirement numbers]
```

### DAG Validation Requirements

The tasks.md MUST:

1. **Form Valid DAG:**
   - No circular dependencies
   - Each task lists explicit dependencies
   - Dependencies reference existing task IDs

2. **Enable Parallelization:**
   - Phase 1: All 4 tasks run in parallel (no dependencies)
   - Phase 2: All 4 tasks run in parallel (depend only on Phase 1)
   - Phase 3-5: Similar parallel structure
   - Expected parallelization: 70-90%

3. **Independent Execution:**
   - Each task can run in isolated context
   - No shared mutable state between parallel tasks
   - Clear input/output contracts

4. **Verifiable:**
   - Every task has verification commands
   - Verification can run independently
   - Success/failure is deterministic

5. **Rollback-able:**
   - Every task has rollback procedure
   - Rollback doesn't break other tasks
   - Rollback is idempotent

### Specific Task Requirements

**Task 1.4 (Data Models):**
Must define all dataclasses from design:
- ServiceDefinition
- HealthCheckConfig
- AutoStartConfig
- AutoStartPlatform (enum)
- AutoStartTrigger (enum)
- ServiceType (enum)
- PlatformConfig
- DependencyGraph
- All result types

**Task 2.1 (macOS LaunchAgent):**
Must generate valid plist files like:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" ...>
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.beastmode.[service]</string>
    ...
</dict>
</plist>
```

**Task 3.X (Service Registration):**
Each must register specific service with:
- Complete ServiceDefinition
- Health check config
- Platform configs
- Dependencies
- Verification that service can be started

**Task 4.1 (Boot Simulation):**
Must create framework that:
- Stops all services
- Clears state
- Triggers auto-start
- Measures time to healthy
- Reports results

**Task 7.X (Migration):**
Each must:
- Create config for new framework
- Test new config works
- Disable old manual start
- Verify auto-start works
- Document changes

## Success Criteria

Tasks document is complete when:

1. All 32 tasks are defined with complete format
2. DAG is valid (can be validated with cycle detection)
3. Dependencies are explicit and correct
4. Each task is independently executable
5. Parallelization is ~70-90% (20+ tasks can run in parallel groups)
6. All tasks have verification and rollback
7. Tasks map to all 22 requirements
8. Ready for DAG orchestrator execution

## Validation

After creating tasks.md:

```bash
# Validate DAG structure
python scripts/validate_dag.py .kiro/specs/service-auto-start-governance/tasks.md

# Expected output:
# ✅ Valid DAG: No circular dependencies
# ✅ Parallelization: 78% (25/32 tasks can run in parallel)
# ✅ All tasks have dependencies specified
# ✅ All tasks have verification
# ✅ Ready for orchestration
```

**Output Location:** `.kiro/specs/service-auto-start-governance/tasks.md`
