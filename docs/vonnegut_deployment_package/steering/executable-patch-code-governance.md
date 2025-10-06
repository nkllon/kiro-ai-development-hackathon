# Executable Patch Code Governance

## Core Principle

**"Every requirement should include executable patch code that demonstrates the exact fix needed. Code is the clearest specification."**

## Mandatory Pattern for Observer Mode Patches

When patching functional code in observer mode, ALWAYS:

### 1. Create Executable Patch Script
```python
#!/usr/bin/env python3
"""
Patch Script: [Clear Problem Description]
Root Cause: [Analysis of what was broken and why]
Fix: [Description of solution approach]
"""

def apply_fix(target_path: str) -> Dict[str, Any]:
    """Apply the specific fix with detailed logging."""
    # Actual implementation code here
    return {"status": "success", "fixes_applied": [...]}

def validate_fix(target_path: str) -> Dict[str, Any]:
    """Validate the fix was applied correctly."""
    # Validation logic that checks all criteria
    return {"status": "passed", "validation_results": {...}}
```

### 2. Include in Requirements as Reference Implementation
```markdown
#### Reference Implementation

**Executable Patch Code:** `scripts/fix_[problem_name].py`

Key implementation:
```python
# Show the critical code snippet that solves the problem
```

**Usage:**
- Apply fix: `python scripts/fix_[problem_name].py <target>`
- Validate: `python scripts/fix_[problem_name].py --validate <target>`
```

### 3. Benefits of This Approach

#### For Current Development
- **Immediate solution**: Patch script can be run to fix the problem
- **Validation**: Can verify the fix works correctly
- **Documentation**: Code shows exactly what was done

#### For Future LLMs
- **Precise specification**: No ambiguity about what the requirement means
- **Executable example**: Can run the code to understand the fix
- **Reusable solution**: Can apply the same fix to similar problems
- **Learning**: Can study the implementation to understand the pattern

#### For System Maintenance
- **Consistency**: All similar problems get fixed the same way
- **Traceability**: Clear path from problem to solution
- **Regression prevention**: Can re-run validation to ensure fixes persist

## Implementation Guidelines

### Script Structure
```python
# 1. Clear problem description in docstring
# 2. Root cause analysis
# 3. Solution approach explanation
# 4. apply_fix() function with detailed implementation
# 5. validate_fix() function with comprehensive checks
# 6. CLI interface for easy usage
# 7. Detailed return values for debugging
```

### Requirements Integration
```markdown
### Requirement X: [Problem Description]

**User Story:** [Clear user perspective]

#### Acceptance Criteria
[Standard acceptance criteria]

#### Reference Implementation
**Executable Patch Code:** `scripts/fix_[problem].py`

[Key code snippets showing the solution]

**Usage:** [How to run the patch script]
```

### Validation Requirements
- Patch script MUST be executable and work correctly
- Validation function MUST check all acceptance criteria
- Code MUST be well-commented and self-explanatory
- Return values MUST provide detailed status information

## Success Metrics

- **100% patch success rate**: All patches work when executed
- **Zero ambiguity**: Future LLMs can understand and apply fixes
- **Consistent solutions**: Similar problems get fixed the same way
- **Regression prevention**: Validation catches when fixes break

## Anti-Patterns to Avoid

### ❌ Vague Requirements
```markdown
"The system should handle execution modes properly"
```

### ✅ Executable Requirements
```markdown
"The system should check os.getenv('EXECUTION_MODE') and branch accordingly"
+ executable patch code showing exactly how
```

### ❌ Manual Patches Only
- Fixing code without creating reusable patch script
- No validation of the fix
- No documentation of the solution approach

### ✅ Systematic Patch Process
- Create executable patch script with automatic technical debt annotations
- Include validation function that checks all acceptance criteria
- Document in requirements with executable code examples
- Test the patch script works correctly and annotations are complete

## The Meta-Principle

**"The best specification is working code that solves the problem."**

By including executable patch code with automatic technical debt annotations, we ensure that:
- Requirements are precise and unambiguous
- Solutions are immediately applicable
- Future developers can learn from working examples
- System maintenance becomes systematic rather than ad-hoc
- All patches are automatically tracked and managed
- Technical debt is visible and actionable
- Cleanup guidance is specific and comprehensive

---

*This governance pattern transforms requirements from documentation into executable solutions, making the development process more efficient and reliable.*