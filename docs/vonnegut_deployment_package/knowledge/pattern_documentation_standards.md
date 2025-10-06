# Atomic Pattern Documentation Standards

## Overview

This document defines the standards and templates for documenting atomic patterns in the Beast Mode framework. Atomic patterns are proven, reproducible sequences of operations that reliably achieve specific outcomes.

## Pattern Documentation Template

### Basic Information
- **Pattern ID**: Unique identifier (kebab-case)
- **Name**: Human-readable pattern name
- **Description**: Clear, concise explanation of what the pattern accomplishes
- **Category**: Classification (spec_execution, cli_automation, etc.)
- **Status**: Current validation status (discovered, validated, production_ready, deprecated)

### Technical Details
- **Command Sequence**: Exact commands to execute the pattern
- **Expected Outputs**: What should be produced when successful
- **Success Criteria**: How to determine if the pattern worked
- **Failure Modes**: Common ways the pattern can fail
- **Remediation Steps**: How to fix common failures
- **Dependencies**: Required infrastructure and components

### Validation Information
- **Examples**: Working examples of the pattern in use
- **Tags**: Searchable keywords
- **Validation Count**: Number of times pattern has been tested
- **Success Rate**: Percentage of successful executions
- **Last Validated**: Most recent validation timestamp

## Documentation Standards

### 1. Command Sequences
- Use exact, copy-pasteable commands
- Include placeholder syntax: `[variable_name]`
- Provide concrete examples alongside placeholders
- Document required working directory
- Include any necessary environment setup

**Example:**
```bash
# Template
python src/spec_framework/cli/prepare_spec_cli.py prepare [spec_path] | tee [logfile]

# Concrete Example  
python src/spec_framework/cli/prepare_spec_cli.py prepare .kiro/specs/my-feature | tee my-feature-prep.log
```

### 2. Expected Outputs
- List all artifacts that should be created
- Include approximate timing expectations
- Describe success indicators in output
- Note any temporary files or side effects

**Example:**
- Generated 3 V2.0 pattern scripts (prelaunch, launch, background)
- PREPARATION_SUMMARY.md with execution instructions
- Efficiency gain calculation (typically 90%+ improvement)
- Execution completes in 30-60 seconds

### 3. Success Criteria
- Define measurable, objective criteria
- Include both functional and performance requirements
- Specify minimum acceptable thresholds
- Cover both immediate and downstream success indicators

**Example:**
- All 3 scripts generated successfully
- Prelaunch validation passes with >90% confidence
- Efficiency gain >50%
- No critical validation failures

### 4. Failure Modes and Remediation
- Document common failure scenarios
- Provide specific error messages when possible
- Include step-by-step remediation procedures
- Reference related troubleshooting resources

**Example:**
```
Failure: "❌ Critical import failure: No module named 'src.rm_ddd'"
Remediation: 
1. Verify Beast Mode infrastructure is installed
2. Check Python path includes project root
3. Run: python -c "from src.rm_ddd.core.unified_reflective_module import ReflectiveModule"
```

### 5. Dependencies
- List all required components and versions
- Include optional dependencies and their benefits
- Document infrastructure requirements
- Specify minimum system requirements

### 6. Examples and Evidence
- Provide working examples from real usage
- Include screenshots or output samples when helpful
- Reference successful implementations
- Document performance metrics from actual runs

## Pattern Categories

### spec_execution
Patterns for transforming specifications into executable implementations.

### cli_automation  
Patterns for command-line interface automation and tooling.

### script_generation
Patterns for generating executable scripts from templates or specifications.

### validation
Patterns for validating system state, prerequisites, or outcomes.

### orchestration
Patterns for coordinating multiple components or processes.

### monitoring
Patterns for observability, health checking, and performance monitoring.

### integration
Patterns for connecting different systems or components.

## Pattern Status Lifecycle

### discovered
- Pattern has been identified and initially documented
- May not be fully tested or validated
- Requires validation before broader use

### validated
- Pattern has been tested multiple times successfully
- Success rate >70%
- Safe for use with appropriate caution

### production_ready
- Pattern has been extensively validated
- Success rate >90% with 3+ validations
- Recommended for production use
- Includes comprehensive documentation

### deprecated
- Pattern is no longer recommended
- May have been superseded by better approaches
- Kept for historical reference

## Quality Gates

### Minimum Documentation Requirements
- [ ] All required fields completed
- [ ] At least one working example provided
- [ ] Command sequences are copy-pasteable
- [ ] Success criteria are measurable
- [ ] Failure modes include remediation steps

### Validation Requirements
- [ ] Pattern tested in clean environment
- [ ] Success criteria verified
- [ ] Failure modes reproduced and remediated
- [ ] Performance metrics documented
- [ ] Dependencies verified

### Production Readiness Requirements
- [ ] 3+ successful validations
- [ ] Success rate >90%
- [ ] Comprehensive failure mode documentation
- [ ] Integration with existing systems verified
- [ ] Performance meets requirements

## Best Practices

### Writing Clear Descriptions
- Start with the outcome the pattern achieves
- Use active voice and specific verbs
- Avoid jargon unless necessary and defined
- Include context about when to use the pattern

### Command Documentation
- Test all commands in a clean environment
- Use consistent formatting and syntax
- Include expected execution time
- Document any interactive prompts or confirmations

### Validation and Testing
- Test patterns on different systems when possible
- Document environment-specific variations
- Include both positive and negative test cases
- Validate that remediation steps actually work

### Maintenance
- Review patterns quarterly for accuracy
- Update success rates based on new validations
- Deprecate patterns that are no longer effective
- Keep examples current with system changes

## Tools and Automation

### Pattern Registry CLI
Use the AtomicPatternRegistry for programmatic access:

```python
from src.spec_framework.knowledge.atomic_pattern_registry import get_registry

registry = get_registry()

# Search patterns
patterns = registry.search_patterns(category=PatternCategory.SPEC_EXECUTION)

# Validate a pattern
registry.validate_pattern("spec-execution-cli-v1", success=True, notes="Worked perfectly")

# Export documentation
registry.export_patterns("markdown", "patterns.md")
```

### Integration with Specs
Reference patterns in specification documents:

```markdown
## Implementation Approach
This specification will use the proven **Spec Execution CLI Pattern** 
(ID: `spec-execution-cli-v1`) for implementation.

See: [Atomic Pattern Registry](.kiro/knowledge/atomic_patterns.md#spec-execution-cli-pattern)
```

## Conclusion

Following these standards ensures that atomic patterns are:
- **Discoverable**: Easy to find and understand
- **Reproducible**: Can be executed reliably by different people
- **Maintainable**: Can be updated and improved over time
- **Valuable**: Provide real benefit to development workflows

The goal is to build a comprehensive knowledge base of proven patterns that accelerate development and reduce risk through systematic reuse of validated approaches.