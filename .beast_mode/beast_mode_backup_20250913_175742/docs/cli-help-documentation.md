# Spec Reconciliation CLI Help Documentation

## Overview

The Spec Reconciliation CLI provides command-line access to governance and validation functionality for managing spec consistency and preventing technical debt.

## Installation

The CLI is available as part of the spec reconciliation system:

```bash
# Run from project root
python -m src.spec_reconciliation.cli --help
```

## Commands

### Governance Commands

#### `governance --status`
Shows the current governance system status including monitored specs and terminology registry size.

**Usage:**
```bash
python -m src.spec_reconciliation.cli governance --status
```

**Example Output:**
```json
{
  "module_name": "GovernanceController",
  "specs_monitored": 14,
  "terminology_terms": 127,
  "status": "healthy",
  "last_validation": "2025-01-09T10:30:00Z"
}
```

#### `governance --validate-spec <file>`
Validates a new spec proposal against existing specs to detect overlaps and conflicts.

**Usage:**
```bash
python -m src.spec_reconciliation.cli governance --validate-spec path/to/spec.md
```

**Example:**
```bash
python -m src.spec_reconciliation.cli governance --validate-spec .kiro/specs/new-feature/requirements.md
```

**Output:**
- `approved`: Spec has no conflicts and can be created
- `requires_review`: Spec has minor overlaps requiring architectural review
- `requires_consolidation`: Spec has significant overlaps requiring consolidation

#### `governance --check-overlaps`
Performs overlap detection across all existing specs to identify consolidation opportunities.

**Usage:**
```bash
python -m src.spec_reconciliation.cli governance --check-overlaps
```

**Example Output:**
```
Checking for spec overlaps...
Overlap severity: HIGH
Overlapping specs: [('beast-mode-framework', 'integrated-beast-mode-system')]
Recommendation: Consolidate immediately - 85% functional overlap detected
```

### Validation Commands

#### `validate --terminology <file>`
Validates terminology consistency in a spec file against the unified vocabulary registry.

**Usage:**
```bash
python -m src.spec_reconciliation.cli validate --terminology path/to/spec.md
```

**Example:**
```bash
python -m src.spec_reconciliation.cli validate --terminology .kiro/specs/feature/requirements.md
```

**Example Output:**
```
Terminology Consistency Score: 0.87
Consistent terms: 23
Inconsistent terms: 3
New terms: 1

Recommendations:
  - Standardize "RCA" vs "root cause analysis" usage
  - Use "ReflectiveModule" instead of "reflective module"
```

#### `validate --interfaces <file>`
Validates interface compliance in a spec file against standard patterns.

**Usage:**
```bash
python -m src.spec_reconciliation.cli validate --interfaces path/to/design.md
```

**Example:**
```bash
python -m src.spec_reconciliation.cli validate --interfaces .kiro/specs/feature/design.md
```

**Example Output:**
```
Interface Compliance Score: 0.92
Compliant interfaces: 4
Non-compliant interfaces: 1

Remediation steps:
  - Add missing get_health_indicators() method to TestModule
  - Follow ReflectiveModule naming conventions
```

#### `validate --consistency-score <files...>`
Generates overall consistency score across multiple spec files.

**Usage:**
```bash
python -m src.spec_reconciliation.cli validate --consistency-score file1.md file2.md file3.md
```

**Example:**
```bash
python -m src.spec_reconciliation.cli validate --consistency-score \
  .kiro/specs/*/requirements.md
```

**Example Output:**
```
Overall Consistency Score: 0.84
Consistency Level: GOOD
Terminology Score: 0.87
Interface Score: 0.82
Pattern Score: 0.83

Critical Issues:
  - Interface naming inconsistency in 3 specs
  - Terminology drift in RCA usage

Improvement Priorities:
  - Standardize interface patterns
  - Consolidate overlapping functionality
```

### Analysis Commands

#### `analyze --all-specs`
Performs comprehensive analysis of all existing specs in the system.

**Usage:**
```bash
python -m src.spec_reconciliation.cli analyze --all-specs
```

**Example Output:**
```
Analyzing all existing specs...
Specs monitored: 14
Terminology terms: 127
Terminology registry size: 127
Interface patterns loaded: 8
```

#### `analyze --overlap-matrix`
Generates a matrix showing overlap relationships between all specs.

**Usage:**
```bash
python -m src.spec_reconciliation.cli analyze --overlap-matrix
```

**Note:** This feature is currently under development.

## Common Workflows

### 1. New Spec Creation Workflow

Before creating a new spec, validate it doesn't conflict with existing specs:

```bash
# Step 1: Check current governance status
python -m src.spec_reconciliation.cli governance --status

# Step 2: Validate the new spec proposal
python -m src.spec_reconciliation.cli governance --validate-spec new-spec.md

# Step 3: Check for overlaps if validation requires review
python -m src.spec_reconciliation.cli governance --check-overlaps
```

### 2. Spec Quality Validation Workflow

Validate existing specs for consistency and compliance:

```bash
# Step 1: Validate terminology consistency
python -m src.spec_reconciliation.cli validate --terminology requirements.md

# Step 2: Validate interface compliance
python -m src.spec_reconciliation.cli validate --interfaces design.md

# Step 3: Generate overall consistency score
python -m src.spec_reconciliation.cli validate --consistency-score *.md
```

### 3. System Health Check Workflow

Regular system health monitoring:

```bash
# Step 1: Check governance system status
python -m src.spec_reconciliation.cli governance --status

# Step 2: Analyze all specs for issues
python -m src.spec_reconciliation.cli analyze --all-specs

# Step 3: Check for new overlaps
python -m src.spec_reconciliation.cli governance --check-overlaps
```

## Error Handling

The CLI provides comprehensive error handling:

### File Not Found
```bash
$ python -m src.spec_reconciliation.cli validate --terminology nonexistent.md
Spec file not found: nonexistent.md
```

### Permission Errors
```bash
$ python -m src.spec_reconciliation.cli validate --terminology protected.md
Error: [Errno 13] Permission denied: 'protected.md'
```

### Invalid Arguments
```bash
$ python -m src.spec_reconciliation.cli invalid-command
cli.py: error: argument command: invalid choice: 'invalid-command'
```

## Exit Codes

- `0`: Success
- `1`: General error (file not found, permission denied, etc.)
- `2`: Invalid command line arguments

## Integration with CI/CD

The CLI can be integrated into CI/CD pipelines for automated spec validation:

```yaml
# Example GitHub Actions workflow
name: Spec Validation
on: [push, pull_request]

jobs:
  validate-specs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Validate spec consistency
        run: |
          python -m src.spec_reconciliation.cli validate --consistency-score .kiro/specs/*/requirements.md
      - name: Check for overlaps
        run: |
          python -m src.spec_reconciliation.cli governance --check-overlaps
```

## Advanced Usage

### Batch Processing

Process multiple specs in batch:

```bash
# Validate all requirements files
for file in .kiro/specs/*/requirements.md; do
  echo "Validating $file"
  python -m src.spec_reconciliation.cli validate --terminology "$file"
done
```

### Output Formatting

Combine with standard Unix tools for advanced processing:

```bash
# Extract consistency scores
python -m src.spec_reconciliation.cli validate --consistency-score *.md | grep "Score:" | awk '{print $3}'

# Check governance status and extract spec count
python -m src.spec_reconciliation.cli governance --status | jq '.specs_monitored'
```

## Troubleshooting

### Common Issues

1. **Module not found error**
   ```bash
   # Ensure you're running from the project root
   cd /path/to/project
   python -m src.spec_reconciliation.cli --help
   ```

2. **Import errors**
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   ```

3. **Permission denied**
   ```bash
   # Check file permissions
   ls -la spec-file.md
   chmod 644 spec-file.md
   ```

### Debug Mode

For debugging, you can add verbose logging:

```bash
# Set logging level
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from src.spec_reconciliation.cli import main
main()
" governance --status
```

## Support

For additional help:

1. Check the main documentation in `docs/`
2. Review test examples in `tests/test_cli_integration.py`
3. Examine the CLI source code in `src/spec_reconciliation/cli.py`

## Version Information

CLI version corresponds to the spec reconciliation system version. Check the system status for current version information:

```bash
python -m src.spec_reconciliation.cli governance --status
```