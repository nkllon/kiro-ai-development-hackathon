# DAG Task Failure Investigation Prompt

## Context
We have discovered a discrepancy between CMS task status and actual execution state:
- **CMS shows**: 1 task with "in_progress" status (Task ID 2: "Data Loading Test")
- **Redis shows**: No actively running tasks or DAG executions
- **Hypothesis**: The task failed but the CMS status was not updated to reflect the failure

## Investigation Required

### Primary Objective
Determine if the "Data Loading Test" task (ID 2) actually failed and why the CMS status remains "in_progress" when no execution is found in Redis.

### Specific Areas to Investigate

#### 1. Task Execution History
- Check Redis for any historical execution records of Task ID 2
- Look for error logs or failure traces in the execution tracking system
- Examine any crash dumps or exception records

#### 2. DAG Execution Analysis
- Verify if the task was part of a DAG execution workflow
- Check DAG orchestration logs for this specific task
- Determine if the DAG execution was interrupted or failed
- Look for any dependency failures that might have caused this task to fail

#### 3. Status Synchronization Issues
- Investigate why the CMS status was not updated when the task failed
- Check for broken status update mechanisms between execution system and CMS
- Look for any transaction rollback issues that left the status inconsistent

#### 4. System State Reconciliation
- Compare expected vs actual system state for this task
- Check if any resources or data created by this task exist
- Verify if the task's intended outcome (loading repository data) was achieved

### Technical Investigation Steps

#### Redis Deep Dive
```bash
# Check for any traces of Task ID 2 in Redis
redis-cli KEYS "*task*2*"
redis-cli KEYS "*execution*2*" 
redis-cli KEYS "*dag*2*"

# Look for error logs or failure records
redis-cli KEYS "*error*"
redis-cli KEYS "*failed*"
redis-cli KEYS "*exception*"
```

#### CMS Data Integrity Check
```sql
-- Check task history and updates
SELECT * FROM tasks WHERE id = 2;
SELECT * FROM task_history WHERE task_id = 2;
SELECT * FROM task_logs WHERE task_id = 2;
```

#### Log File Analysis
- Check application logs for Task ID 2 execution attempts
- Look for DAG orchestrator logs around the time this task was started
- Examine any error logs or exception traces

#### System Resource Verification
- Check if the "repository data" that this task was supposed to load actually exists
- Verify database connections and data integrity
- Look for any partial data loads that might indicate task interruption

### Expected Deliverables

#### 1. Root Cause Analysis
- Exact reason why the task failed
- Timeline of events leading to the failure
- System components involved in the failure

#### 2. Status Inconsistency Explanation
- Why the CMS status was not updated
- What mechanism should have updated it
- How to prevent this inconsistency in the future

#### 3. DAG Execution Context
- Was this task part of a larger DAG workflow?
- Did other tasks in the DAG succeed or fail?
- What was the intended execution sequence?

#### 4. Recovery Recommendations
- How to properly mark this task as failed in the CMS
- Whether the task should be retried
- What cleanup is needed before retry

#### 5. Prevention Measures
- System improvements to prevent status inconsistencies
- Better error handling and status synchronization
- Monitoring enhancements to catch such issues earlier

### Investigation Priority
**HIGH** - This represents a critical system reliability issue where task execution state is not properly tracked, which could lead to:
- Resource leaks from "zombie" tasks
- Incorrect system state assumptions
- Failed dependency chains in DAG executions
- Loss of operational visibility

### Success Criteria
- [ ] Exact failure cause identified
- [ ] CMS status corrected to reflect actual state
- [ ] System state reconciled (cleanup completed)
- [ ] Prevention measures implemented
- [ ] Documentation updated with lessons learned

## Prompt for AI Assistant

**"I need you to investigate a critical task execution failure. Task ID 2 ('Data Loading Test') shows 'in_progress' status in the CMS but there's no corresponding execution activity in Redis. This suggests the task failed but the status wasn't updated. Please:**

**1. Perform a comprehensive investigation of this task's execution history**
**2. Determine the exact failure cause and timeline**
**3. Explain why the CMS status wasn't updated**
**4. Analyze the DAG execution context and any cascade effects**
**5. Provide specific recovery steps and prevention measures**

**Focus on system reliability and data integrity. This is a critical operational issue that needs thorough analysis and resolution."**