# Test RCA Integration Configuration Reference

## Overview

This document provides comprehensive information about configuring the Test RCA Integration system. Configuration can be set through environment variables, configuration files, or command-line parameters.

## Environment Variables

### Core RCA Settings

#### RCA_ON_FAILURE
Controls whether RCA analysis is automatically triggered when tests fail.

- **Type**: Boolean
- **Default**: `true`
- **Values**: `true`, `false`, `1`, `0`, `yes`, `no`
- **Example**: `export RCA_ON_FAILURE=false`

```bash
# Disable automatic RCA
RCA_ON_FAILURE=false make test

# Enable automatic RCA (default)
RCA_ON_FAILURE=true make test
```

#### RCA_TIMEOUT
Maximum time (in seconds) for RCA analysis to complete.

- **Type**: Integer
- **Default**: `30`
- **Range**: `10-300`
- **Example**: `export RCA_TIMEOUT=60`

```bash
# Increase timeout for complex analysis
RCA_TIMEOUT=60 make rca

# Quick analysis with shorter timeout
RCA_TIMEOUT=15 make rca
```

#### RCA_VERBOSE
Controls the verbosity level of RCA output and logging.

- **Type**: Boolean
- **Default**: `false`
- **Values**: `true`, `false`
- **Example**: `export RCA_VERBOSE=true`

```bash
# Enable verbose output for debugging
RCA_VERBOSE=true make test-with-rca

# Quiet mode (default)
RCA_VERBOSE=false make rca
```

#### RCA_MAX_FAILURES
Maximum number of test failures to analyze in a single RCA session.

- **Type**: Integer
- **Default**: `10`
- **Range**: `1-50`
- **Example**: `export RCA_MAX_FAILURES=5`

```bash
# Analyze only the first 3 failures
RCA_MAX_FAILURES=3 make test-with-rca

# Analyze up to 20 failures
RCA_MAX_FAILURES=20 make rca
```

### Pattern Library Settings

#### RCA_PATTERN_LEARNING
Enables or disables learning from successful RCA analyses to build pattern library.

- **Type**: Boolean
- **Default**: `true`
- **Values**: `true`, `false`
- **Example**: `export RCA_PATTERN_LEARNING=false`

```bash
# Disable pattern learning for debugging
RCA_PATTERN_LEARNING=false make rca

# Enable pattern learning (default)
RCA_PATTERN_LEARNING=true make test-with-rca
```

#### RCA_PATTERN_LIBRARY_PATH
Path to the pattern library file for storing learned patterns.

- **Type**: String (file path)
- **Default**: `patterns/test_rca_patterns.json`
- **Example**: `export RCA_PATTERN_LIBRARY_PATH=custom/patterns.json`

```bash
# Use custom pattern library
RCA_PATTERN_LIBRARY_PATH=custom_patterns.json make rca
```

#### RCA_MAX_PATTERNS_PER_FAILURE
Maximum number of patterns to match against each failure.

- **Type**: Integer
- **Default**: `5`
- **Range**: `1-20`
- **Example**: `export RCA_MAX_PATTERNS_PER_FAILURE=3`

```bash
# Limit pattern matching for faster analysis
RCA_MAX_PATTERNS_PER_FAILURE=3 make rca
```

### Performance Settings

#### RCA_PARALLEL_ANALYSIS
Enables parallel analysis of multiple failures (experimental).

- **Type**: Boolean
- **Default**: `false`
- **Values**: `true`, `false`
- **Example**: `export RCA_PARALLEL_ANALYSIS=true`

```bash
# Enable parallel analysis for large failure sets
RCA_PARALLEL_ANALYSIS=true make rca
```

#### RCA_MEMORY_LIMIT_MB
Memory limit for RCA analysis processes (in megabytes).

- **Type**: Integer
- **Default**: `512`
- **Range**: `128-2048`
- **Example**: `export RCA_MEMORY_LIMIT_MB=1024`

```bash
# Increase memory limit for complex analysis
RCA_MEMORY_LIMIT_MB=1024 make rca
```

#### RCA_CPU_LIMIT_PERCENT
CPU usage limit for RCA analysis (percentage of available CPU).

- **Type**: Integer
- **Default**: `80`
- **Range**: `10-100`
- **Example**: `export RCA_CPU_LIMIT_PERCENT=50`

```bash
# Limit CPU usage to 50% for background analysis
RCA_CPU_LIMIT_PERCENT=50 make rca
```

### Output and Reporting Settings

#### RCA_DEFAULT_FORMAT
Default output format for RCA reports.

- **Type**: String
- **Default**: `console`
- **Values**: `console`, `json`, `markdown`, `html`
- **Example**: `export RCA_DEFAULT_FORMAT=json`

```bash
# Generate JSON output by default
RCA_DEFAULT_FORMAT=json make rca-report

# Generate markdown report
RCA_DEFAULT_FORMAT=markdown make rca-report
```

#### RCA_COLOR_OUTPUT
Enables or disables colored output in console reports.

- **Type**: Boolean
- **Default**: `true`
- **Values**: `true`, `false`
- **Example**: `export RCA_COLOR_OUTPUT=false`

```bash
# Disable colors for CI/CD environments
RCA_COLOR_OUTPUT=false make test-with-rca
```

#### RCA_INCLUDE_STACK_TRACES
Controls whether stack traces are included in reports.

- **Type**: Boolean
- **Default**: `true`
- **Values**: `true`, `false`
- **Example**: `export RCA_INCLUDE_STACK_TRACES=false`

```bash
# Generate clean reports without stack traces
RCA_INCLUDE_STACK_TRACES=false make rca-report
```

#### RCA_MAX_RECOMMENDATIONS
Maximum number of recommendations to include in reports.

- **Type**: Integer
- **Default**: `10`
- **Range**: `1-50`
- **Example**: `export RCA_MAX_RECOMMENDATIONS=5`

```bash
# Limit recommendations for concise reports
RCA_MAX_RECOMMENDATIONS=5 make rca-report
```

### Debug and Development Settings

#### DEBUG_RCA
Enables debug mode for RCA components.

- **Type**: Boolean
- **Default**: `false`
- **Values**: `true`, `false`
- **Example**: `export DEBUG_RCA=true`

```bash
# Enable RCA debug mode
DEBUG_RCA=true make test-with-rca
```

#### DEBUG_PATTERNS
Enables debug mode specifically for pattern matching.

- **Type**: Boolean
- **Default**: `false`
- **Values**: `true`, `false`
- **Example**: `export DEBUG_PATTERNS=true`

```bash
# Debug pattern matching
DEBUG_PATTERNS=true make rca
```

#### DEBUG_FAILURE_DETECTION
Enables debug mode for test failure detection.

- **Type**: Boolean
- **Default**: `false`
- **Values**: `true`, `false`
- **Example**: `export DEBUG_FAILURE_DETECTION=true`

```bash
# Debug failure detection
DEBUG_FAILURE_DETECTION=true make test
```

## Configuration Files

### Main Configuration File

The main configuration file is located at `config/rca_config.json` and provides structured configuration options.

```json
{
  "rca_settings": {
    "default_timeout": 30,
    "max_failures_per_session": 10,
    "enable_pattern_learning": true,
    "parallel_analysis": false,
    "verbose_output": false
  },
  "pattern_library": {
    "path": "patterns/test_rca_patterns.json",
    "auto_update": true,
    "max_patterns": 10000,
    "cleanup_interval_days": 30,
    "learning_rate": 0.1,
    "confidence_threshold": 0.7
  },
  "performance": {
    "memory_limit_mb": 512,
    "cpu_limit_percent": 80,
    "io_timeout_seconds": 10,
    "max_concurrent_analyses": 3,
    "pattern_match_timeout": 1.0
  },
  "reporting": {
    "default_format": "console",
    "include_timestamps": true,
    "color_output": true,
    "max_recommendations": 10,
    "include_stack_traces": true,
    "include_prevention_patterns": true
  },
  "integrations": {
    "slack_webhook": null,
    "jira_integration": false,
    "github_issues": false,
    "email_notifications": false
  },
  "logging": {
    "level": "INFO",
    "file": "logs/rca_analysis.log",
    "max_file_size_mb": 10,
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

### Pattern Library Configuration

Pattern library settings can be configured in `config/pattern_config.json`:

```json
{
  "pattern_types": {
    "error_message": {
      "enabled": true,
      "weight": 1.0,
      "min_confidence": 0.6
    },
    "stack_trace": {
      "enabled": true,
      "weight": 0.8,
      "min_confidence": 0.7
    },
    "timing": {
      "enabled": true,
      "weight": 0.6,
      "min_confidence": 0.8
    },
    "resource": {
      "enabled": true,
      "weight": 0.7,
      "min_confidence": 0.75
    }
  },
  "learning_settings": {
    "auto_learn": true,
    "learn_threshold": 0.8,
    "max_learn_per_session": 5,
    "validation_required": true
  },
  "cleanup_settings": {
    "auto_cleanup": true,
    "cleanup_interval_days": 30,
    "min_usage_count": 3,
    "min_success_rate": 0.5
  }
}
```

### Make Target Configuration

Configuration for make targets can be set in `makefiles/rca_config.mk`:

```makefile
# RCA Configuration for Make Targets

# Default settings
RCA_ON_FAILURE ?= true
RCA_TIMEOUT ?= 30
RCA_VERBOSE ?= false
RCA_MAX_FAILURES ?= 10

# Performance settings
RCA_MEMORY_LIMIT_MB ?= 512
RCA_CPU_LIMIT_PERCENT ?= 80

# Output settings
RCA_DEFAULT_FORMAT ?= console
RCA_COLOR_OUTPUT ?= true

# Pattern library settings
RCA_PATTERN_LEARNING ?= true
RCA_PATTERN_LIBRARY_PATH ?= patterns/test_rca_patterns.json

# Export all RCA variables
export RCA_ON_FAILURE
export RCA_TIMEOUT
export RCA_VERBOSE
export RCA_MAX_FAILURES
export RCA_MEMORY_LIMIT_MB
export RCA_CPU_LIMIT_PERCENT
export RCA_DEFAULT_FORMAT
export RCA_COLOR_OUTPUT
export RCA_PATTERN_LEARNING
export RCA_PATTERN_LIBRARY_PATH
```

## Configuration Validation

### Validation Rules

The system validates configuration settings and provides warnings for invalid values:

```python
# Configuration validation rules
VALIDATION_RULES = {
    'RCA_TIMEOUT': {
        'type': int,
        'min': 10,
        'max': 300,
        'warning': 'RCA_TIMEOUT should be between 10 and 300 seconds'
    },
    'RCA_MAX_FAILURES': {
        'type': int,
        'min': 1,
        'max': 50,
        'warning': 'RCA_MAX_FAILURES should be between 1 and 50'
    },
    'RCA_MEMORY_LIMIT_MB': {
        'type': int,
        'min': 128,
        'max': 2048,
        'warning': 'RCA_MEMORY_LIMIT_MB should be between 128 and 2048'
    },
    'RCA_PATTERN_LIBRARY_PATH': {
        'type': str,
        'exists': True,
        'warning': 'Pattern library path must exist and be readable'
    }
}
```

### Validation Commands

```bash
# Validate current configuration
make rca-config-validate

# Show current configuration
make rca-config-show

# Reset to default configuration
make rca-config-reset
```

## Environment-Specific Configuration

### Development Environment

```bash
# Development settings for detailed analysis
export RCA_VERBOSE=true
export RCA_TIMEOUT=60
export RCA_PATTERN_LEARNING=true
export DEBUG_RCA=true
export RCA_INCLUDE_STACK_TRACES=true
```

### CI/CD Environment

```bash
# CI/CD settings for fast, automated analysis
export RCA_ON_FAILURE=true
export RCA_TIMEOUT=30
export RCA_VERBOSE=false
export RCA_COLOR_OUTPUT=false
export RCA_DEFAULT_FORMAT=json
export RCA_MAX_FAILURES=5
```

### Production Environment

```bash
# Production settings for critical issue detection
export RCA_ON_FAILURE=true
export RCA_TIMEOUT=45
export RCA_VERBOSE=false
export RCA_MAX_FAILURES=10
export RCA_PATTERN_LEARNING=true
export RCA_MEMORY_LIMIT_MB=1024
```

## Configuration Profiles

### Profile Files

Create configuration profiles for different scenarios:

```bash
# profiles/development.env
RCA_VERBOSE=true
RCA_TIMEOUT=60
DEBUG_RCA=true
RCA_INCLUDE_STACK_TRACES=true

# profiles/ci.env
RCA_COLOR_OUTPUT=false
RCA_DEFAULT_FORMAT=json
RCA_TIMEOUT=30
RCA_MAX_FAILURES=5

# profiles/production.env
RCA_MEMORY_LIMIT_MB=1024
RCA_TIMEOUT=45
RCA_PATTERN_LEARNING=true
```

### Using Profiles

```bash
# Load development profile
source profiles/development.env
make test-with-rca

# Load CI profile
source profiles/ci.env
make rca-report

# Load production profile
source profiles/production.env
make rca
```

## Advanced Configuration

### Custom Pattern Types

Configure custom pattern types in the pattern library:

```json
{
  "custom_patterns": {
    "database_timeout": {
      "enabled": true,
      "timeout_threshold": 5.0,
      "confidence_weight": 0.9,
      "systematic_fix_template": "database_optimization"
    },
    "memory_leak": {
      "enabled": true,
      "memory_threshold_mb": 100,
      "confidence_weight": 0.8,
      "systematic_fix_template": "memory_optimization"
    },
    "api_rate_limit": {
      "enabled": true,
      "rate_limit_indicators": ["429", "rate limit", "too many requests"],
      "confidence_weight": 0.95,
      "systematic_fix_template": "rate_limit_handling"
    }
  }
}
```

### Integration Settings

Configure integrations with external systems:

```json
{
  "integrations": {
    "slack": {
      "enabled": false,
      "webhook_url": "https://hooks.slack.com/services/...",
      "channel": "#test-failures",
      "notify_on_critical": true,
      "notify_on_patterns": true
    },
    "jira": {
      "enabled": false,
      "server_url": "https://company.atlassian.net",
      "project_key": "TEST",
      "create_issues_for_critical": true,
      "issue_type": "Bug"
    },
    "github": {
      "enabled": false,
      "repository": "company/project",
      "create_issues_for_critical": true,
      "label_prefix": "rca-"
    }
  }
}
```

### Performance Tuning

Fine-tune performance settings for different workloads:

```json
{
  "performance_profiles": {
    "fast": {
      "timeout": 15,
      "max_failures": 3,
      "pattern_match_timeout": 0.5,
      "deep_analysis": false
    },
    "balanced": {
      "timeout": 30,
      "max_failures": 10,
      "pattern_match_timeout": 1.0,
      "deep_analysis": true
    },
    "thorough": {
      "timeout": 60,
      "max_failures": 20,
      "pattern_match_timeout": 2.0,
      "deep_analysis": true,
      "include_external_factors": true
    }
  }
}
```

## Configuration Best Practices

### 1. Environment-Specific Settings

- Use different configurations for development, CI/CD, and production
- Store sensitive configuration in environment variables
- Use configuration files for complex settings

### 2. Performance Optimization

- Adjust timeout based on typical failure complexity
- Limit max failures for faster analysis in CI/CD
- Enable parallel analysis for large test suites

### 3. Pattern Library Management

- Enable pattern learning in development and production
- Regularly clean up unused patterns
- Back up pattern library before major changes

### 4. Monitoring and Logging

- Enable verbose logging in development
- Use structured logging in production
- Monitor RCA performance metrics

### 5. Integration Configuration

- Configure notifications for critical issues
- Use JSON output for CI/CD integration
- Set up automated issue creation for persistent failures

## Troubleshooting Configuration

### Common Configuration Issues

1. **RCA not triggering**: Check `RCA_ON_FAILURE` setting
2. **Analysis timeout**: Increase `RCA_TIMEOUT` value
3. **Pattern library errors**: Verify `RCA_PATTERN_LIBRARY_PATH` exists
4. **Memory issues**: Adjust `RCA_MEMORY_LIMIT_MB` setting
5. **Output formatting**: Check `RCA_DEFAULT_FORMAT` and `RCA_COLOR_OUTPUT`

### Configuration Debugging

```bash
# Show all RCA environment variables
env | grep RCA

# Validate configuration
make rca-config-validate

# Test configuration with dry run
RCA_DRY_RUN=true make test-with-rca

# Show effective configuration
make rca-config-show
```

### Reset Configuration

```bash
# Reset to defaults
unset $(env | grep RCA | cut -d= -f1)

# Or reset specific variables
unset RCA_TIMEOUT RCA_VERBOSE RCA_MAX_FAILURES

# Reload defaults
source config/rca_defaults.env
```