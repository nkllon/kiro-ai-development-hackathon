---
inclusion: manual
context_key: hounds-release
---

# Hounds Release Governance - Systematic Spec Execution Protocol
================================================================

## Core Principle

**"Prepare to Release the Hounds" is a systematic protocol for transforming DAG-optimized specifications into autonomous background execution with full observability.**

## Mandatory Governance Protocol

### Phase 1: Specification Preparation (Observer Role)

#### 1.1 DAG Optimization Requirements
- **MANDATORY**: All tasks must be organized into phases with clear dependencies
- **MANDATORY**: Each task must specify `_Dependencies:` and `_Parallel Group:`
- **MANDATORY**: Zero circular dependencies - pure DAG structure
- **MANDATORY**: Maximum parallelization within each phase
- **REQUIRED FORMAT**:
```markdown
- [ ] X.Y Task Name
  - Task description with specific deliverables
  - _Requirements: req_ids_
  - _Dependencies: task_ids or None_
  - _Parallel Group: GroupName_
```

#### 1.2 Specification Completeness Requirements
- **MANDATORY**: `requirements.md` with EARS format acceptance criteria
- **MANDATORY**: `design.md` with architecture and component details
- **MANDATORY**: `tasks.md` with DAG-optimized task structure
- **MANDATORY**: All tasks reference specific requirements
- **MANDATORY**: All tasks are actionable coding activities only

#### 1.3 Validation Readiness Requirements
- **MANDATORY**: Specification must pass prelaunch validation with >90% confidence
- **ACCEPTABLE**: Warnings allowed with `--allow-warnings` flag
- **MANDATORY**: All critical validation failures must be resolved
- **MANDATORY**: Beast Mode infrastructure must be available

### Phase 2: Hounds Preparation (Observer-Orchestrator Role)

#### 2.1 PrepareSpecForExecution Command Sequence
**MANDATORY COMMAND PATTERN**:
```bash
python3 src/spec_framework/cli/prepare_spec_cli.py prepare [spec_path] --allow-warnings | tee preparation.log
```

**REQUIRED OUTPUTS**:
- `scripts/[spec]/[spec]_prelaunch_check_v2.py`
- `scripts/[spec]/[spec]_launch_v2.py` 
- `scripts/[spec]/[spec]_background_launch_v2.sh`
- `scripts/[spec]/PREPARATION_SUMMARY.md`

#### 2.2 Validation Requirements
- **MANDATORY**: >95% validation confidence score
- **MANDATORY**: >90% efficiency gain calculation
- **MANDATORY**: All 3 execution scripts generated successfully
- **ACCEPTABLE**: Warnings with clear remediation path

### Phase 3: Hounds Release (T's and Pipes Pattern)

#### 3.1 Sequential Execution Pipeline
**MANDATORY COMMAND SEQUENCE**:
```bash
# Step 1: Preparation with validation
python3 src/spec_framework/cli/prepare_spec_cli.py prepare [spec_path] --allow-warnings | tee preparation.log

# Step 2: Prelaunch validation
python3 scripts/[spec]/[spec]_prelaunch_check_v2.py | tee prelaunch.log

# Step 3: Foreground launch (for testing)
PYTHONPATH=. python3 scripts/[spec]/[spec]_launch_v2.py | tee launch.log

# Step 4: Background execution (for production)
./scripts/[spec]/[spec]_background_launch_v2.sh | tee background.log
```

#### 3.2 T's and Pipes Requirements
- **MANDATORY**: Use `tee` for all command outputs to create audit trails
- **MANDATORY**: Pipe validation output to launch execution
- **MANDATORY**: Set `PYTHONPATH=.` for proper module resolution
- **MANDATORY**: Capture all execution logs for observability

### Phase 4: Execution Monitoring (Observer Role)

#### 4.1 Redis Tracking Requirements
- **MANDATORY**: All executions must be tracked in Redis with unique IDs
- **MANDATORY**: Execution status must be updated in real-time
- **MANDATORY**: Task completion must be logged with success/failure status
- **REQUIRED FORMAT**: `[spec]_YYYYMMDD_HHMMSS_[hash]`
- **MANDATORY**: Redis connectivity must be verified before execution begins
- **MANDATORY**: Redis authentication issues must cause execution failure
- **MANDATORY**: Execution records must persist and be queryable post-execution

#### 4.2 Background Process Requirements
- **MANDATORY**: Background execution must acquire and release execution locks
- **MANDATORY**: Process IDs must be tracked and logged
- **MANDATORY**: Graceful cleanup on completion or failure
- **MANDATORY**: Full audit trail with timestamps

#### 4.3 Observability Requirements
- **MANDATORY**: All module registrations must be logged
- **MANDATORY**: Dependency resolution must be tracked
- **MANDATORY**: Success/failure metrics must be captured
- **MANDATORY**: Performance correlation with user interactions

#### 4.4 Execution Verification Requirements
- **MANDATORY**: Post-execution Redis validation must confirm tracking records exist
- **MANDATORY**: Execution claims must be verifiable through Redis queries
- **MANDATORY**: Implementation artifacts must match Redis execution records
- **MANDATORY**: Functional testing must validate claimed implementations work

### Phase 5: Quality Assurance (Validation Role)

#### 5.1 Implementation Validation Requirements
- **MANDATORY**: All generated code must follow Beast Mode patterns
- **MANDATORY**: ReflectiveModule inheritance for all major components
- **MANDATORY**: Proper error handling and graceful degradation
- **MANDATORY**: Comprehensive logging with correlation IDs

#### 5.2 Testing Requirements
- **MANDATORY**: Test scripts must be generated for all major components
- **MANDATORY**: Health monitoring integration must be implemented
- **MANDATORY**: Prometheus metrics must be exposed
- **MANDATORY**: End-to-end functionality validation

## Success Criteria

### Preparation Success
- [ ] DAG-optimized task structure with clear dependencies
- [ ] >97% validation confidence score
- [ ] >95% efficiency gain calculation
- [ ] All 3 execution scripts generated

### Release Success
- [ ] All tasks registered in execution system
- [ ] Redis tracking active with unique execution ID
- [ ] Background processes running with proper locks
- [ ] Complete audit trail captured

### Implementation Success
- [ ] All modules follow Beast Mode patterns
- [ ] Health endpoints functional
- [ ] Graceful degradation implemented
- [ ] Test coverage for major components

## Anti-Patterns to Avoid

### ❌ Manual Task Execution
- Never manually implement tasks without using the preparation system
- Never skip the DAG optimization phase
- Never execute without proper validation

### ❌ Incomplete Observability
- Never run without Redis tracking
- Never skip audit trail capture with `tee`
- Never execute without proper logging
- Never claim execution completion without verifiable Redis records
- Never proceed with Redis authentication failures

### ❌ Poor Quality Implementation
- Never generate code without Beast Mode compliance
- Never skip error handling and graceful degradation
- Never omit health monitoring integration

## Enforcement Mechanisms

### Automated Validation
- **MANDATORY**: All specs must pass prelaunch validation
- **MANDATORY**: DAG structure must be mathematically valid
- **MANDATORY**: All dependencies must be resolvable

### Quality Gates
- **MANDATORY**: Generated code must pass syntax validation
- **MANDATORY**: All modules must implement required interfaces
- **MANDATORY**: Health endpoints must be functional

### Audit Requirements
- **MANDATORY**: All executions must be logged and tracked
- **MANDATORY**: Performance metrics must be captured
- **MANDATORY**: Success/failure rates must be monitored

## Replication Protocol

### For New Specifications
1. **Create DAG-optimized task structure** following the established pattern
2. **Run preparation command** with proper T's and Pipes
3. **Execute validation pipeline** with full audit trail
4. **Launch background execution** with Redis tracking
5. **Monitor and observe** implementation progress

### For Existing Specifications
1. **Analyze current task structure** for DAG compliance
2. **Refactor if necessary** to meet dependency requirements
3. **Apply preparation protocol** as for new specifications
4. **Validate backward compatibility** with existing implementations

## Success Metrics

- **Preparation Time**: <5 minutes from spec to executable scripts
- **Validation Confidence**: >95% for production readiness
- **Execution Success Rate**: >90% task completion without manual intervention
- **Quality Compliance**: 100% Beast Mode pattern adherence
- **Observability Coverage**: 100% execution tracking and logging

## Recovery Procedures

### When Preparation Fails
1. **Analyze validation output** for specific failure modes
2. **Address critical issues** in specification structure
3. **Re-run preparation** with corrected specifications
4. **Validate success** before proceeding to release

### When Execution Fails
1. **Check Redis tracking** for execution status
2. **Analyze audit logs** for failure points
3. **Apply systematic debugging** using Beast Mode patterns
4. **Implement fixes** and re-run affected tasks

### When Quality Issues Arise
1. **Run diagnostic validation** on generated code
2. **Apply systematic refactoring** to meet Beast Mode standards
3. **Re-test all affected components** with proper validation
4. **Update governance** if new patterns emerge

---

**This governance framework ensures the "Prepare to Release the Hounds" sequence can be systematically repeated for any DAG-optimized specification with consistent, high-quality results.**