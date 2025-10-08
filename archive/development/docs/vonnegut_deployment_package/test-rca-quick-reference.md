# Test RCA Integration Quick Reference

## Quick Start

```bash
# Run tests with automatic RCA on failures
make test

# Manual RCA analysis of recent failures
make rca

# Analyze specific test or task
make rca-task TASK=test_name

# Generate detailed report
make rca-report
```

## Essential Environment Variables

```bash
# Core settings
export RCA_ON_FAILURE=true          # Enable/disable automatic RCA
export RCA_TIMEOUT=30               # Analysis timeout (seconds)
export RCA_VERBOSE=true             # Verbose output
export RCA_MAX_FAILURES=10          # Max failures to analyze

# Output settings
export RCA_DEFAULT_FORMAT=console   # Output format (console/json/markdown)
export RCA_COLOR_OUTPUT=true        # Colored console output
```

## Common Usage Patterns

### Development Workflow
```bash
# Run tests with detailed RCA
RCA_VERBOSE=true make test-with-rca

# Quick analysis of specific failure
make rca-task TASK=failing_test_name

# Generate report for review
make rca-report OUTPUT=analysis.md
```

### CI/CD Integration
```bash
# Automated analysis with JSON output
RCA_DEFAULT_FORMAT=json RCA_COLOR_OUTPUT=false make test-with-rca

# Fast analysis for CI
RCA_TIMEOUT=15 RCA_MAX_FAILURES=3 make rca
```

### Debugging and Investigation
```bash
# Enable all debug output
DEBUG_RCA=true RCA_VERBOSE=true make test-with-rca

# Focus on pattern matching
DEBUG_PATTERNS=true make rca

# Analyze with extended timeout
RCA_TIMEOUT=60 make rca-task TASK=complex_test
```

## Output Examples

### Console Output
```
🔍 RCA Analysis Results
═══════════════════════
📊 Summary: 3 failures analyzed, 2 root causes found
🎯 Critical Issues: Database connection timeout
🔧 Systematic Fix: Update connection pool settings
⏭️  Next Steps: Apply configuration changes
```

### JSON Output
```json
{
  "analysis_timestamp": "2025-01-15T10:30:00Z",
  "total_failures": 3,
  "root_causes": [...],
  "systematic_fixes": [...],
  "recommendations": [...]
}
```

## Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| RCA not triggering | `export RCA_ON_FAILURE=true` |
| Analysis too slow | `export RCA_TIMEOUT=60` |
| No output shown | `export RCA_VERBOSE=true` |
| Pattern errors | Check `patterns/test_rca_patterns.json` exists |
| Memory issues | `export RCA_MEMORY_LIMIT_MB=1024` |

## Performance Tips

- **Fast analysis**: `RCA_MAX_FAILURES=3 RCA_TIMEOUT=15`
- **Thorough analysis**: `RCA_TIMEOUT=60 RCA_VERBOSE=true`
- **Pattern optimization**: Enable `RCA_PATTERN_LEARNING=true`
- **Memory optimization**: Set `RCA_MEMORY_LIMIT_MB` appropriately

## Configuration Files

- **Main config**: `config/rca_config.json`
- **Pattern library**: `patterns/test_rca_patterns.json`
- **Make config**: `makefiles/rca_config.mk`

## Documentation Links

- [Full Documentation](test-rca-integration.md)
- [Troubleshooting Guide](test-rca-troubleshooting.md)
- [Developer Guide](test-rca-developer-guide.md)
- [Configuration Reference](test-rca-configuration.md)
- [Usage Examples](../examples/test_rca_usage_examples.py)