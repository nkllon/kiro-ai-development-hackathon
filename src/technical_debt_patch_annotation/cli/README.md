# Technical Debt Patch Annotation CLI

Comprehensive command-line interface for managing technical debt patches, providing integration with development workflows, CI/CD pipelines, and systematic cleanup processes.

## Overview

The Technical Debt Patch Annotation CLI provides a complete set of commands for:

- **Patch Discovery**: Automated scanning and validation of patch annotations
- **Interactive Management**: Creating, editing, and managing patch annotations
- **CI/CD Integration**: Threshold checking and merge validation
- **Cleanup Orchestration**: Systematic planning and execution of patch cleanup
- **Reporting & Analytics**: Comprehensive reporting on technical debt status
- **Batch Operations**: Bulk operations on patches and notifications

## Requirements Coverage

This CLI implementation satisfies all integration requirements:

### Requirement 6.1: Code Review Integration
- **Commands**: `scan --validate`, `report --type inventory`
- **Functionality**: Provides debt impact assessment for code review processes
- **Integration**: Generates reports showing patch impact on components

### Requirement 6.2: CI/CD Pipeline Integration
- **Commands**: `ci-check --threshold-*`, `validate --all`
- **Functionality**: Validates debt thresholds and blocks builds when exceeded
- **Integration**: Returns appropriate exit codes for CI/CD pipeline control

### Requirement 6.3: Automated Merge Prevention
- **Commands**: `validate --strict`, `ci-check --block-merge`
- **Functionality**: Prevents merges when patches lack proper annotation
- **Integration**: Strict validation mode catches annotation deficiencies

### Requirement 6.4: Cleanup Validation
- **Commands**: `cleanup --plan`, `cleanup --execute`, `validate --all`
- **Functionality**: Systematic cleanup planning and validation
- **Integration**: Validates cleanup completion and provides rollback capabilities

### Requirement 6.5: Technical Debt Reporting
- **Commands**: `report --type [inventory|trends|cleanup|executive]`
- **Functionality**: Generates comprehensive reports from current codebase state
- **Integration**: Multiple report formats and filtering options

## Installation

The CLI is part of the Technical Debt Patch Annotation System:

```bash
# Install the system
pip install -e .

# The CLI will be available as:
python -m src.technical_debt_patch_annotation.cli.patch_cli

# Or create an alias:
alias patch-cli="python -m src.technical_debt_patch_annotation.cli.patch_cli"
```

## Quick Start

### Basic Usage

```bash
# Scan current directory for patches
patch-cli scan .

# Validate all patches
patch-cli validate --all

# Generate inventory report
patch-cli report --type inventory

# Check CI/CD thresholds
patch-cli ci-check --threshold-critical 3
```

### Interactive Annotation

```bash
# Interactive mode for creating annotations
patch-cli annotate --interactive

# Direct annotation
patch-cli annotate --file auth.py --line 45 \
  --reason "Temporary LDAP bypass" \
  --upstream "LDAP-001" \
  --debt-level High
```

### Cleanup Management

```bash
# Generate cleanup plan
patch-cli cleanup --plan --priority high

# Execute cleanup plan (dry run)
patch-cli cleanup --execute PLAN-001 --dry-run

# Execute cleanup plan
patch-cli cleanup --execute PLAN-001
```

## Command Reference

### Global Options

- `--verbose, -v`: Verbose output
- `--quiet, -q`: Quiet mode (errors only)
- `--config`: Configuration file path
- `--output, -o`: Output file path
- `--format`: Output format (json, yaml, csv, text)

### Commands

#### `scan` - Patch Discovery

Scan directories for patch annotations and validate them.

```bash
patch-cli scan [PATH] [OPTIONS]

Options:
  --recursive, -r     Recursive directory scan
  --include PATTERN   File patterns to include
  --exclude PATTERN   File patterns to exclude
  --validate          Validate found patches
  --summary           Show summary only

Examples:
  patch-cli scan .                    # Scan current directory
  patch-cli scan src --recursive      # Recursive scan of src/
  patch-cli scan . --validate         # Scan and validate
```

#### `annotate` - Create Annotations

Create or edit patch annotations interactively or directly.

```bash
patch-cli annotate [OPTIONS]

Options:
  --interactive, -i           Interactive annotation mode
  --file FILE                 File to annotate
  --line LINE                 Line number to annotate
  --reason REASON             Reason for patch
  --upstream ISSUE            Upstream issue reference
  --cleanup TASK              Cleanup task description
  --debt-level LEVEL          Debt severity (Low|Medium|High|Critical)
  --bypass-type TYPE          Type of bypass
  --component COMPONENT       Component name
  --expected-resolution DATE  Expected resolution (YYYY-MM-DD)
  --validation-criteria TEXT  Validation criteria

Examples:
  patch-cli annotate --interactive
  patch-cli annotate --file auth.py --line 45 --reason "LDAP bypass"
```

#### `validate` - Validation

Validate patch annotations for completeness and correctness.

```bash
patch-cli validate [OPTIONS]

Options:
  --all               Validate all patches
  --patch-id ID       Validate specific patch
  --component COMP    Validate patches in component
  --fix               Attempt to fix validation errors
  --strict            Strict validation mode

Examples:
  patch-cli validate --all
  patch-cli validate --patch-id PATCH-001
  patch-cli validate --component auth_service --strict
```

#### `cleanup` - Cleanup Management

Manage systematic patch cleanup processes.

```bash
patch-cli cleanup [OPTIONS]

Options:
  --plan              Generate cleanup plan
  --execute PLAN_ID   Execute cleanup plan
  --component COMP    Focus on specific component
  --priority LEVEL    Minimum priority level
  --dry-run           Show what would be done
  --force             Force cleanup execution

Examples:
  patch-cli cleanup --plan --priority high
  patch-cli cleanup --execute PLAN-001 --dry-run
  patch-cli cleanup --plan --component auth_service
```

#### `report` - Reporting

Generate comprehensive reports on technical debt patches.

```bash
patch-cli report [OPTIONS]

Options:
  --type TYPE         Report type (inventory|trends|cleanup|executive)
  --component COMP    Filter by component
  --debt-level LEVEL  Filter by debt level
  --since DATE        Include patches since date
  --until DATE        Include patches until date
  --template FILE     Report template file

Examples:
  patch-cli report --type inventory
  patch-cli report --type executive --format json
  patch-cli report --type trends --since 2024-01-01
```

#### `ci-check` - CI/CD Integration

Perform CI/CD integration checks with threshold validation.

```bash
patch-cli ci-check [OPTIONS]

Options:
  --threshold-low N       Maximum low-priority patches (default: 50)
  --threshold-medium N    Maximum medium-priority patches (default: 20)
  --threshold-high N      Maximum high-priority patches (default: 10)
  --threshold-critical N  Maximum critical patches (default: 3)
  --block-merge          Block merge on threshold violation
  --changed-files FILE   File with list of changed files

Examples:
  patch-cli ci-check --threshold-critical 2
  patch-cli ci-check --block-merge --changed-files changed.txt
```

#### `batch` - Batch Operations

Perform batch operations on patches.

```bash
patch-cli batch [OPTIONS]

Options:
  --expire-days N     Find patches expiring in N days
  --notify            Send notifications
  --update-status ST  Update patch status
  --bulk-edit FILE    JSON file with bulk edits
  --archive           Archive resolved patches

Examples:
  patch-cli batch --expire-days 30 --notify
  patch-cli batch --archive
```

#### `export` - Export Data

Export patch data in various formats.

```bash
patch-cli export [OPTIONS]

Options:
  --format FORMAT         Export format (json|yaml|csv|xml)
  --include-resolved      Include resolved patches
  --template FILE         Export template file

Examples:
  patch-cli export --format json --output patches.json
  patch-cli export --format csv --include-resolved
```

#### `import` - Import Data

Import patch data from external sources.

```bash
patch-cli import FILE [OPTIONS]

Options:
  --format FORMAT     Import format (auto-detect if not specified)
  --merge             Merge with existing patches
  --validate          Validate before import

Examples:
  patch-cli import patches.json --validate
  patch-cli import external.yaml --merge
```

## Configuration

The CLI can be configured using a configuration file:

```yaml
# patch-cli.yaml
scanner:
  include_patterns:
    - "*.py"
    - "*.js"
    - "*.ts"
  exclude_patterns:
    - "node_modules/**"
    - ".git/**"

thresholds:
  low: 50
  medium: 20
  high: 10
  critical: 3

notifications:
  email:
    enabled: true
    smtp_server: "smtp.company.com"
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/..."

cleanup:
  auto_plan: true
  require_approval: true
  backup_before_cleanup: true
```

Use with: `patch-cli --config patch-cli.yaml <command>`

## CI/CD Integration Examples

### GitHub Actions

```yaml
name: Technical Debt Check
on: [pull_request]

jobs:
  debt-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -e .
      - name: Check technical debt thresholds
        run: |
          patch-cli ci-check --threshold-critical 2 --threshold-high 5 --block-merge
      - name: Generate debt report
        run: |
          patch-cli report --type inventory --format json --output debt-report.json
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: debt-report
          path: debt-report.json
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Technical Debt Check') {
            steps {
                script {
                    def result = sh(
                        script: 'patch-cli ci-check --threshold-critical 2',
                        returnStatus: true
                    )
                    if (result != 0) {
                        error("Technical debt thresholds exceeded")
                    }
                }
            }
        }
        stage('Generate Report') {
            steps {
                sh 'patch-cli report --type executive --format json --output debt-report.json'
                archiveArtifacts artifacts: 'debt-report.json'
            }
        }
    }
}
```

### GitLab CI

```yaml
technical-debt-check:
  stage: test
  script:
    - pip install -e .
    - patch-cli ci-check --threshold-critical 2 --threshold-high 5
    - patch-cli report --type inventory --format json --output debt-report.json
  artifacts:
    reports:
      junit: debt-report.json
    paths:
      - debt-report.json
  only:
    - merge_requests
```

## Output Formats

### JSON Output

```json
{
  "report_type": "inventory",
  "generated_at": "2024-01-15T10:30:00Z",
  "total_patches": 15,
  "by_debt_level": {
    "Critical": 2,
    "High": 5,
    "Medium": 6,
    "Low": 2
  },
  "by_component": {
    "auth_service": 8,
    "data_processor": 4,
    "config_manager": 3
  },
  "patches": [...]
}
```

### Text Output

```
📊 Inventory Report
Generated: 2024-01-15T10:30:00Z
Total Patches: 15

Debt Levels:
  Critical: 2
  High: 5
  Medium: 6
  Low: 2

Components:
  auth_service: 8
  data_processor: 4
  config_manager: 3
```

### CSV Output

```csv
patch_id,component,debt_level,created_date,expected_resolution,reason
PATCH-001,auth_service,High,2024-01-10,2024-02-10,LDAP bypass
PATCH-002,data_processor,Critical,2024-01-12,2024-01-20,Security fix
```

## Error Handling

The CLI provides comprehensive error handling with appropriate exit codes:

- **0**: Success
- **1**: General error or validation failure
- **2**: Configuration error
- **3**: Permission error
- **4**: File not found error

Error messages include context and suggestions for resolution:

```
❌ Validation failed: 3 patches have missing required fields
  • PATCH-001: Missing upstream issue reference
  • PATCH-002: Missing cleanup task description
  • PATCH-003: Missing expected resolution date

💡 Use 'patch-cli annotate --interactive' to fix annotations
```

## Extensibility

The CLI is built using the ReflectiveModule pattern and can be extended:

### Custom Commands

```python
from src.technical_debt_patch_annotation.cli.patch_cli import PatchCLI

class ExtendedPatchCLI(PatchCLI):
    def _add_custom_parser(self, subparsers):
        custom_parser = subparsers.add_parser("custom", help="Custom command")
        # Add custom arguments
    
    def _execute_custom(self, args):
        # Custom command implementation
        return 0
```

### Custom Report Types

```python
def _generate_custom_report(self, patches):
    # Custom report generation logic
    return {
        "report_type": "custom",
        "data": custom_analysis(patches)
    }
```

## Testing

Run the compliance tests to verify all requirements are met:

```bash
python src/technical_debt_patch_annotation/cli/test_requirements_compliance.py
```

Run the demo to see all functionality:

```bash
python src/technical_debt_patch_annotation/cli/demo_cli_interface.py
```

## Architecture

The CLI follows the ReflectiveModule pattern and integrates with all system components:

```
PatchCLI (ReflectiveModule)
├── PatchScanner (discovery)
├── DebtClassifier (classification)
├── IssueTracker (integration)
├── CleanupOrchestrator (cleanup)
└── LifecycleManager (lifecycle)
```

Key architectural features:

- **Modular Design**: Each command delegates to specialized components
- **Health Monitoring**: Built-in health checks and graceful degradation
- **Observability**: Prometheus metrics and structured logging
- **Configuration**: Flexible configuration system
- **Extensibility**: Plugin architecture for custom commands

## Best Practices

### For Development Teams

1. **Integrate with Code Review**: Use `scan --validate` in PR checks
2. **Set Appropriate Thresholds**: Configure CI/CD thresholds based on team capacity
3. **Regular Cleanup**: Schedule regular cleanup planning sessions
4. **Monitor Trends**: Use trend reports to track debt accumulation

### For CI/CD Pipelines

1. **Fail Fast**: Use `--block-merge` for critical threshold violations
2. **Generate Reports**: Always generate reports for visibility
3. **Archive Results**: Store reports as build artifacts
4. **Notify Teams**: Use batch operations for notifications

### For Operations Teams

1. **Monitor Health**: Regular health checks on CLI components
2. **Backup Data**: Export patch data regularly
3. **Track Metrics**: Monitor debt trends and cleanup effectiveness
4. **Automate Cleanup**: Use scheduled cleanup execution

## Troubleshooting

### Common Issues

**CLI not found**
```bash
# Ensure proper installation
pip install -e .
python -m src.technical_debt_patch_annotation.cli.patch_cli --help
```

**Permission errors**
```bash
# Check file permissions
ls -la src/technical_debt_patch_annotation/cli/
chmod +x src/technical_debt_patch_annotation/cli/patch_cli.py
```

**Import errors**
```bash
# Verify Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -c "from src.technical_debt_patch_annotation.cli.patch_cli import PatchCLI"
```

**Configuration issues**
```bash
# Validate configuration
patch-cli --config config.yaml scan . --dry-run
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
patch-cli --verbose scan .
```

### Health Checks

Check CLI component health:

```bash
python -c "
from src.technical_debt_patch_annotation.cli.patch_cli import PatchCLI
cli = PatchCLI()
health = cli.get_health_status()
print(f'Status: {health.status.value}')
print(f'Issues: {health.issues}')
"
```

## Contributing

The CLI follows the project's development standards:

1. **ReflectiveModule Pattern**: All components inherit from ReflectiveModule
2. **Requirements Traceability**: Each feature maps to specific requirements
3. **Comprehensive Testing**: Unit tests and integration tests required
4. **Documentation**: All commands and options must be documented

See the main project README for contribution guidelines.

## License

This CLI is part of the Technical Debt Patch Annotation System and follows the same license terms as the main project.