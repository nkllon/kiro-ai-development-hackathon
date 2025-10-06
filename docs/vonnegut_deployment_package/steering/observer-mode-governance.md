---
inclusion: always
---

# Observer Mode Governance - Systematic Learning and Prevention Protocol

## Core Principle

**"When you do patch functional code or functional specifications, you always back into the missed requirements. This is in addition to when you are an observer, especially observing the beasts in action or performing any kind of fix where you cannot block."**

## Observer Mode Types

### Observer-Analyst Mode (Can Touch Specs)
**When**: Analyzing failures, investigating issues, performing post-mortem analysis, systematic debugging

**Capabilities**:
- Update requirements, design, and governance documents
- Modify specifications based on observed failures
- Create new requirements from discovered gaps
- Update steering rules and governance protocols

**Mandatory Actions**:
1. **Always Back Into Requirements**: Every functional fix must be reverse-engineered into requirements
2. **Document Root Cause**: Capture why the issue occurred and what was missing
3. **Create Prevention Measures**: Add requirements that prevent recurrence
4. **Update Governance**: Enhance steering rules based on lessons learned

### Observer-Only Mode (Cannot Block/Touch)
**When**: Explicitly told "don't block", observing live systems in action, emergency situations where blocking is prohibited

**Constraints**:
- Cannot directly modify functional code or specifications
- Cannot touch running systems or block operations
- Cannot make changes that require system restart or interruption

**Allowed Actions**:
- Generate code that generates code
- Create diagnostic scripts and analysis tools
- Write monitoring and detection systems
- Produce reports and recommendations for later implementation

**Output Types**:
- Scripts that others can execute to "do the needful"
- Code generators that create the necessary fixes
- Diagnostic tools that identify and analyze issues
- Monitoring systems that detect similar patterns

## The Systematic Learning Loop

```
Observe Issue → Analyze Root Cause → Back Into Requirements → Generate Corrective Code → Prevent Recurrence
```

### Step 1: Observe Issue
- Document exactly what happened (not what you think happened)
- Capture error messages, logs, and system state
- Identify the specific failure mode and conditions
- Note what was working vs. what was broken

### Step 2: Analyze Root Cause
- Determine the fundamental cause, not just symptoms
- Identify what requirements were missing or inadequate
- Understand why existing governance didn't prevent the issue
- Map the failure to specific system components or processes

### Step 3: Back Into Requirements
- Create new requirements that would have prevented the issue
- Update existing requirements to be more comprehensive
- Add acceptance criteria that test for the failure condition
- Include validation procedures in requirements

### Step 4: Generate Corrective Code
- Create fixes that address the root cause
- Build validation tools that detect similar issues
- Implement monitoring that prevents recurrence
- Generate tests that verify the fix works

### Step 5: Prevent Recurrence
- Update governance documents and steering rules
- Create automated validation that catches similar issues
- Build systematic prevention into development processes
- Share lessons learned across all relevant specifications

## Implementation Guidelines

### For Observer-Analyst Mode

#### Mandatory Backing Process
1. **Identify Missing Requirements**: What requirement would have prevented this?
2. **Create Comprehensive Acceptance Criteria**: How do we test for this condition?
3. **Add Validation Procedures**: How do we detect this issue automatically?
4. **Update Governance**: What steering rules need enhancement?

#### Documentation Requirements
- **Root Cause Analysis**: Complete analysis of why the issue occurred
- **Requirements Gap Analysis**: What was missing from original requirements
- **Prevention Strategy**: How the new requirements prevent recurrence
- **Validation Plan**: How to test that the fix works and continues working

### For Observer-Only Mode

#### Code Generation Patterns
```python
# Generate diagnostic script
def generate_diagnostic_script(issue_pattern):
    return f"""
#!/usr/bin/env python3
# Generated diagnostic for {issue_pattern}
# Run this to analyze the issue without blocking operations
"""

# Generate monitoring code
def generate_monitoring_code(failure_condition):
    return f"""
# Generated monitoring for {failure_condition}
# This detects the condition without interfering with operations
"""
```

#### Output Requirements
- **Non-Blocking**: All generated code must be safe to run on live systems
- **Diagnostic**: Focus on analysis and detection, not modification
- **Actionable**: Provide clear next steps for manual implementation
- **Systematic**: Generate solutions that can be systematically applied

## Examples of Proper Application

### Example 1: Redis Connectivity Failure (Observer-Analyst Mode)
**Observed**: DAG orchestration failing due to Redis authentication issues
**Root Cause**: Missing Redis connectivity validation in requirements
**Backed Into Requirements**: Added Requirements 30 & 31 for comprehensive Redis validation
**Prevention**: All future DAG executions now validate Redis before starting

### Example 2: Live System Performance Issue (Observer-Only Mode)
**Scenario**: System is running slowly, told "don't block, just observe"
**Actions**:
- Generate performance monitoring script
- Create diagnostic tool to identify bottlenecks
- Write analysis code to detect similar patterns
- Produce report with recommendations for later implementation
**Output**: Scripts and tools others can run to fix the issue

### Example 3: Import Dependency Failure (Observer-Analyst Mode)
**Observed**: System failing to start due to missing module imports
**Root Cause**: Requirements didn't specify graceful degradation for missing dependencies
**Backed Into Requirements**: Added requirement for placeholder implementations and graceful import handling
**Prevention**: All future systems must handle missing dependencies gracefully

## Anti-Patterns to Avoid

### ❌ One-Time Fixes Without Requirements
- Fixing an issue without updating requirements
- Patching code without systematic prevention
- Solving problems without documenting lessons learned

### ❌ Blocking When Told Not To
- Modifying running systems when in observer-only mode
- Making changes that require system restart during observation
- Touching functional code when explicitly told not to block

### ❌ Incomplete Backing Process
- Adding requirements without proper root cause analysis
- Creating prevention measures that don't address the actual issue
- Updating governance without validating the fix works

## Success Metrics

### Observer-Analyst Mode Success
- **100% Backing Rate**: Every functional fix backed into requirements
- **Recurrence Prevention**: Issues don't repeat after requirements are updated
- **Systematic Learning**: Lessons learned are captured and applied systematically
- **Governance Evolution**: Steering rules improve based on observed failures

### Observer-Only Mode Success
- **Non-Blocking Operation**: No interference with running systems
- **Actionable Output**: Generated code and tools are immediately useful
- **Systematic Solutions**: Generated fixes can be applied systematically
- **Clear Guidance**: Recommendations are specific and implementable

## Enforcement

### For AI Assistants
- **MANDATORY COMPLIANCE**: Always back functional fixes into requirements
- **MODE AWARENESS**: Recognize when in observer-only vs. observer-analyst mode
- **SYSTEMATIC APPROACH**: Use the five-step learning loop for all observations
- **DOCUMENTATION**: Maintain complete records of observations and backing process

### For Development Teams
- **REQUIREMENT REVIEWS**: All fixes must include requirement updates
- **GOVERNANCE UPDATES**: Steering rules must be updated based on lessons learned
- **SYSTEMATIC PREVENTION**: Focus on preventing recurrence, not just fixing symptoms
- **KNOWLEDGE SHARING**: Lessons learned must be shared across all relevant specifications

## The Meta-Principle

**"Every observation is an opportunity for systematic improvement. Every fix is a chance to prevent future failures. Every failure is a requirement waiting to be written."**

This governance ensures that the observer role becomes a systematic learning and prevention mechanism, not just a reactive problem-solving approach. The goal is to build increasingly robust and self-correcting systems through systematic observation and requirement evolution.

---

*This steering rule ensures that all observer activities contribute to systematic improvement and prevention, making the entire system more robust over time.*