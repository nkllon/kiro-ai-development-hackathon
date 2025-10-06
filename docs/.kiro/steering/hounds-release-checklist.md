---
inclusion: manual
context_key: hounds-checklist
---

# Hounds Release Execution Checklist
====================================

## Quick Reference for "Prepare to Release the Hounds" Protocol

### Pre-Flight Checklist ✈️

- [ ] **Specification Structure**
  - [ ] `requirements.md` exists with EARS format
  - [ ] `design.md` exists with architecture details
  - [ ] `tasks.md` exists with DAG-optimized structure
  - [ ] All tasks have `_Dependencies:` and `_Parallel Group:`
  - [ ] Zero circular dependencies verified

- [ ] **Environment Readiness**
  - [ ] Beast Mode infrastructure available
  - [ ] Redis connection active (for tracking)
  - [ ] Python environment with required packages
  - [ ] Sufficient disk space and memory

### Execution Commands 🚀

#### Step 1: Prepare the Hounds
```bash
python3 src/spec_framework/cli/prepare_spec_cli.py prepare .kiro/specs/[SPEC_NAME] --allow-warnings | tee [SPEC_NAME]-preparation.log
```

**Expected Output:**
- ✅ Validation confidence >95%
- ✅ Efficiency gain >90%
- ✅ 3 scripts generated in `scripts/[SPEC_NAME]/`

#### Step 2: Validate Readiness
```bash
python3 scripts/[SPEC_NAME]/[SPEC_NAME]_prelaunch_check_v2.py | tee [SPEC_NAME]-prelaunch.log
```

**Expected Output:**
- ✅ "Validation Complete - Ready for Execution!"
- ✅ Confidence Score >95%

#### Step 3: Release the Hounds (Foreground Test)
```bash
PYTHONPATH=. python3 scripts/[SPEC_NAME]/[SPEC_NAME]_launch_v2.py | tee [SPEC_NAME]-launch.log
```

**Expected Output:**
- ✅ Redis connection established
- ✅ Execution ID generated
- ✅ All modules registered
- ✅ "Execution Complete!"

#### Step 4: Release the Hounds (Background Production)
```bash
./scripts/[SPEC_NAME]/[SPEC_NAME]_background_launch_v2.sh | tee [SPEC_NAME]-background.log
```

**Expected Output:**
- ✅ Execution lock acquired
- ✅ Background processes running
- ✅ Execution lock released
- ✅ "Background execution completed successfully"

#### Step 5: MANDATORY Redis Execution Verification
```bash
python3 scripts/validate_redis_execution_tracking.py [EXECUTION_ID]
```

**Expected Output:**
- ✅ VALIDATION PASSED: All executions verified
- 📄 Detailed report saved with verification results

**CRITICAL**: If validation fails, the execution must be marked as UNVERIFIED and investigated.

### Monitoring Commands 👁️

#### Check Redis Execution Status
```bash
redis-cli -h [REDIS_HOST] -p [REDIS_PORT] keys "*[SPEC_NAME]*"
```

#### Monitor Background Processes
```bash
ps aux | grep [SPEC_NAME]
```

#### Check Generated Files
```bash
find src/ -name "*[SPEC_NAME]*" -type f -newer [SPEC_NAME]-preparation.log
```

### Validation Commands ✅

#### Test Generated Components
```bash
python3 scripts/test_[COMPONENT].py
```

#### Check Health Endpoints
```bash
curl -s http://localhost:8888/health | jq .
```

#### Verify Beast Mode Compliance
```bash
python3 -c "from src.[MODULE] import [CLASS]; print([CLASS]().get_health_status())"
```

### Troubleshooting Commands 🔧

#### Check Validation Issues
```bash
python3 src/spec_framework/validation/prelaunch_validator.py .kiro/specs/[SPEC_NAME]
```

#### Analyze Execution Logs
```bash
grep -E "(ERROR|FAILED|Exception)" [SPEC_NAME]-*.log
```

#### Check DAG Dependencies
```bash
python3 src/dag_orchestration/core/dag_orchestrator.py validate .kiro/specs/[SPEC_NAME]/tasks.md
```

### Success Indicators 🎯

#### Preparation Success
- [ ] Validation confidence >95%
- [ ] Efficiency gain >90%
- [ ] All 3 scripts generated
- [ ] No critical validation failures

#### Execution Success
- [ ] Redis execution ID created
- [ ] All modules registered successfully
- [ ] Background processes running
- [ ] Complete audit trail captured

#### Implementation Success
- [ ] Generated code follows Beast Mode patterns
- [ ] Health endpoints functional
- [ ] Test scripts pass
- [ ] Graceful degradation works

### Common Issues & Solutions 🛠️

#### "No module named 'src'" Error
```bash
# Solution: Set PYTHONPATH
export PYTHONPATH=.
# Or use inline:
PYTHONPATH=. python3 [SCRIPT]
```

#### Validation Warnings
```bash
# Solution: Use --allow-warnings flag
python3 src/spec_framework/cli/prepare_spec_cli.py prepare [SPEC_PATH] --allow-warnings
```

#### Redis Connection Issues
```bash
# Check Redis status
redis-cli ping
# Check connection details in logs
grep -i redis [SPEC_NAME]-*.log
```

#### Background Process Stuck
```bash
# Check for execution locks
ls -la /tmp/*[SPEC_NAME]*lock* 2>/dev/null || echo "No locks found"
# Kill stuck processes
pkill -f [SPEC_NAME]
```

### File Locations 📁

#### Generated Scripts
- `scripts/[SPEC_NAME]/[SPEC_NAME]_prelaunch_check_v2.py`
- `scripts/[SPEC_NAME]/[SPEC_NAME]_launch_v2.py`
- `scripts/[SPEC_NAME]/[SPEC_NAME]_background_launch_v2.sh`
- `scripts/[SPEC_NAME]/PREPARATION_SUMMARY.md`

#### Log Files
- `[SPEC_NAME]-preparation.log`
- `[SPEC_NAME]-prelaunch.log`
- `[SPEC_NAME]-launch.log`
- `[SPEC_NAME]-background.log`

#### Generated Code
- `src/[MODULE_PATH]/` - Implementation files
- `scripts/test_[COMPONENT].py` - Test scripts

### Quick Commands Reference 📋

```bash
# Full sequence (copy-paste ready)
SPEC_NAME="your-spec-name"
python3 src/spec_framework/cli/prepare_spec_cli.py prepare .kiro/specs/$SPEC_NAME --allow-warnings | tee $SPEC_NAME-preparation.log
python3 scripts/$SPEC_NAME/${SPEC_NAME}_prelaunch_check_v2.py | tee $SPEC_NAME-prelaunch.log
PYTHONPATH=. python3 scripts/$SPEC_NAME/${SPEC_NAME}_launch_v2.py | tee $SPEC_NAME-launch.log
./scripts/$SPEC_NAME/${SPEC_NAME}_background_launch_v2.sh | tee $SPEC_NAME-background.log
```

### Redis Execution Verification 🔍

#### Pre-Execution Redis Validation
```bash
# Test local Redis connectivity
redis-cli ping
# Expected: PONG

# Test remote Redis connectivity (if configured)
redis-cli -h [REDIS_HOST] -p [REDIS_PORT] ping
# Expected: PONG (not NOAUTH error)

# Check Redis authentication status
redis-cli info server | grep "redis_version"
# Should return version info without auth errors
```

#### Post-Execution Redis Verification
```bash
# Verify execution tracking records exist
redis-cli keys "*[SPEC_NAME]*"
# Expected: At least one key with execution ID

# Check execution record details
redis-cli get "[SPEC_NAME]_[EXECUTION_ID]"
# Expected: JSON with execution details

# Verify execution completion status
redis-cli hget "[SPEC_NAME]_[EXECUTION_ID]" status
# Expected: "completed" or detailed status

# Count total execution records for spec
redis-cli keys "*[SPEC_NAME]*" | wc -l
# Expected: >0 (at least one execution record)
```

#### Execution Integrity Validation
```bash
# Cross-reference execution logs with Redis records
EXECUTION_ID=$(grep "Execution ID:" [SPEC_NAME]-*.log | cut -d: -f2 | tr -d ' ')
redis-cli exists "$EXECUTION_ID"
# Expected: 1 (key exists)

# Validate execution timestamp consistency
LOG_TIME=$(grep "Starting.*execution" [SPEC_NAME]-*.log | head -1 | cut -d] -f1 | tr -d '[')
REDIS_TIME=$(redis-cli hget "$EXECUTION_ID" start_time)
# Times should be within seconds of each other

# Verify claimed task count matches Redis
CLAIMED_TASKS=$(grep "Total Tasks:" [SPEC_NAME]-*.log | cut -d: -f2 | tr -d ' ')
REDIS_TASKS=$(redis-cli hget "$EXECUTION_ID" total_tasks)
# Numbers should match exactly
```

### Emergency Stop 🛑

```bash
# Stop all background processes for a spec
pkill -f [SPEC_NAME]

# Remove execution locks
rm -f /tmp/*[SPEC_NAME]*lock*

# Clear Redis tracking (if needed - use with caution)
redis-cli keys "*[SPEC_NAME]*" | xargs redis-cli del
```

### Permanent Corrective Actions 🔧

#### When Redis Validation Fails
1. **Document the failure** in execution logs
2. **Update requirements** to prevent recurrence
3. **Implement Redis connectivity checks** in prelaunch validation
4. **Add execution verification** to success criteria
5. **Create automated validation scripts** for future executions

#### When Execution Claims Cannot Be Verified
1. **Mark execution as UNVERIFIED** in all documentation
2. **Require re-execution** with proper Redis tracking
3. **Update governance** to mandate verification before completion claims
4. **Implement automated verification** in background launch scripts

---

**Use this checklist to systematically execute the "Prepare to Release the Hounds" protocol for any DAG-optimized specification with full verification and permanent corrective action capabilities.**