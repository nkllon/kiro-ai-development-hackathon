# CI/CD Pipeline Integration

This module provides comprehensive integration with CI/CD pipelines for the Technical Debt Patch Annotation System, enabling automated patch validation, debt threshold checking, merge blocking, and pull request impact reporting.

## Features

### 🔍 Patch Annotation Validation
- Validates patch annotations in build pipelines
- Checks format, completeness, and compliance with standards
- Reports validation errors and warnings with specific file locations
- Integrates with existing CI/CD workflows

### 📊 Debt Threshold Checking
- Configurable thresholds for technical debt levels
- Component-level and repository-level limits
- Automated merge blocking when thresholds are exceeded
- Age-based patch expiration monitoring

### 🚫 Automated Merge Blocking
- Blocks merges when validation fails
- Prevents critical patches from being merged without review
- Configurable blocking criteria and exceptions
- Clear reporting of block reasons

### 📈 Pull Request Impact Reporting
- Analyzes patch changes in pull requests
- Provides debt level distribution and component impact
- Generates recommendations for cleanup priorities
- Supports multiple CI/CD platforms

### ⚙️ Workflow Generation
- Generates CI/CD configurations for popular platforms
- GitHub Actions, GitLab CI, and Jenkins support
- Customizable workflow templates
- Ready-to-use pipeline configurations

## Quick Start

### Basic Usage

```python
from src.technical_debt_patch_annotation.integration import CICDIntegration

# Initialize with default configuration
cicd = CICDIntegration()

# Validate patch annotations
result = cicd.validate_patch_annotations(".")
if not result.success:
    print("Validation failed!")
    for issue in result.validation_issues:
        print(f"  {issue.severity}: {issue.message}")

# Check debt thresholds
threshold_result = cicd.check_debt_thresholds(".")
if threshold_result.should_block_merge:
    print("Merge blocked due to debt thresholds!")
```

### Custom Configuration

```python
from src.technical_debt_patch_annotation.integration import (
    CICDIntegration, 
    ThresholdConfiguration
)

# Create custom threshold configuration
config = ThresholdConfiguration(
    max_patches_per_component=5,
    max_critical_patches_per_component=1,
    max_total_patches=20,
    component_debt_blocking_threshold=80.0
)

# Initialize with custom configuration
cicd = CICDIntegration(threshold_config=config)
```

## Command Line Interface

The module provides a comprehensive CLI for integration with CI/CD pipelines:

### Validate Patch Annotations
```bash
python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .
```

### Check Debt Thresholds
```bash
python -m technical_debt_patch_annotation.integration.cicd_integration check-thresholds .
```

### Generate Pull Request Report
```bash
python -m technical_debt_patch_annotation.integration.cicd_integration pr-report . \
  --base-branch main \
  --head-branch feature-branch \
  --pr-id PR-123
```

### Generate Workflow Configurations
```bash
# GitHub Actions
python -m technical_debt_patch_annotation.integration.cicd_integration generate-workflows --platform github

# GitLab CI
python -m technical_debt_patch_annotation.integration.cicd_integration generate-workflows --platform gitlab

# Jenkins
python -m technical_debt_patch_annotation.integration.cicd_integration generate-workflows --platform jenkins
```

## CI/CD Platform Integration

### GitHub Actions

The module generates a complete GitHub Actions workflow:

```yaml
name: Technical Debt Patch Validation

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main, develop ]

jobs:
  patch-validation:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Validate patch annotations
      run: python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .
```

### GitLab CI

Generated GitLab CI configuration includes:

```yaml
patch-validation:
  stage: validate
  script:
    - python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .
    - python -m technical_debt_patch_annotation.integration.cicd_integration check-thresholds .
```

### Jenkins

Generated Jenkins pipeline includes:

```groovy
pipeline {
    agent any
    stages {
        stage('Validate Patch Annotations') {
            steps {
                sh 'python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .'
            }
        }
    }
}
```

## Configuration Options

### Threshold Configuration

```python
ThresholdConfiguration(
    # Component-level thresholds
    max_patches_per_component=10,
    max_critical_patches_per_component=2,
    max_high_patches_per_component=5,
    
    # Repository-level thresholds
    max_total_patches=50,
    max_total_critical_patches=5,
    max_total_high_patches=15,
    
    # Age-based thresholds
    max_patch_age_days=90,
    critical_patch_max_age_days=30,
    
    # Component debt score thresholds (0-100 scale)
    component_debt_warning_threshold=70.0,
    component_debt_blocking_threshold=85.0,
    
    # Custom thresholds by component
    component_specific_thresholds={
        "core_system": {"max_patches": 3, "max_critical": 0},
        "api_layer": {"max_patches": 8, "max_critical": 1}
    }
)
```

### Scanner Configuration

```python
from src.technical_debt_patch_annotation.discovery import ScanConfiguration

scanner_config = ScanConfiguration(
    include_patterns=["*.py", "*.js", "*.ts", "*.java"],
    exclude_patterns=["*.pyc", "node_modules/*"],
    max_file_size_mb=10.0,
    parallel_scanning=True,
    max_workers=4
)

cicd = CICDIntegration(scanner_config=scanner_config)
```

## API Reference

### CICDIntegration Class

#### Methods

##### `validate_patch_annotations(repository_path, changed_files=None)`
Validates patch annotations in the repository.

**Parameters:**
- `repository_path` (str): Path to the repository
- `changed_files` (List[str], optional): List of changed files to focus on

**Returns:**
- `CIPipelineResult`: Validation results with issues and recommendations

##### `check_debt_thresholds(repository_path, component_filter=None)`
Checks debt threshold compliance with automated merge blocking.

**Parameters:**
- `repository_path` (str): Path to the repository
- `component_filter` (List[str], optional): Components to focus on

**Returns:**
- `CIPipelineResult`: Threshold analysis with merge decision

##### `generate_pull_request_report(repository_path, base_branch, head_branch=None, pull_request_id=None)`
Generates pull request impact report.

**Parameters:**
- `repository_path` (str): Path to the repository
- `base_branch` (str): Base branch for comparison
- `head_branch` (str, optional): Head branch for comparison
- `pull_request_id` (str, optional): Pull request identifier

**Returns:**
- `PatchImpactReport`: Detailed impact analysis and recommendations

### Data Classes

#### `ValidationIssue`
Represents a validation issue found during CI/CD checks.

```python
@dataclass
class ValidationIssue:
    severity: str          # "error", "warning", "info"
    category: str          # "annotation", "threshold", "validation", "policy"
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    patch_id: Optional[str] = None
    component: Optional[str] = None
    suggestion: Optional[str] = None
```

#### `PatchImpactReport`
Report on patch impact for pull requests.

```python
@dataclass
class PatchImpactReport:
    patches_added: int = 0
    patches_modified: int = 0
    patches_removed: int = 0
    net_patch_change: int = 0
    patches_by_debt_level: Dict[str, int]
    affected_components: Set[str]
    component_debt_changes: Dict[str, float]
    validation_issues: List[ValidationIssue]
    threshold_violations: List[str]
    recommendations: List[str]
    should_block_merge: bool = False
    block_reasons: List[MergeBlockReason]
```

#### `CIPipelineResult`
Result of CI/CD pipeline patch validation.

```python
@dataclass
class CIPipelineResult:
    stage: CIPipelineStage
    success: bool
    execution_time_seconds: float
    patches_validated: int = 0
    validation_issues: List[ValidationIssue]
    impact_report: Optional[PatchImpactReport] = None
    threshold_violations: List[str]
    should_block_merge: bool = False
    block_reasons: List[MergeBlockReason]
```

## Integration Examples

### Pre-commit Hook Integration

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Validating patch annotations..."
python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .

if [ $? -ne 0 ]; then
    echo "❌ Patch validation failed. Commit blocked."
    exit 1
fi

echo "✅ Patch validation passed."
```

### Docker Integration

```dockerfile
FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Validate patches during build
RUN python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .
```

### Makefile Integration

```makefile
.PHONY: validate-patches check-thresholds

validate-patches:
	python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .

check-thresholds:
	python -m technical_debt_patch_annotation.integration.cicd_integration check-thresholds .

ci-checks: validate-patches check-thresholds
	@echo "✅ All CI checks passed"
```

## Monitoring and Observability

The CI/CD integration module provides comprehensive monitoring through:

### Prometheus Metrics
- `cicd_integration_pipeline_runs_total`: Total pipeline runs by stage and result
- `cicd_integration_patches_validated_total`: Total patches validated
- `cicd_integration_merge_blocks_total`: Total merges blocked by reason
- `cicd_integration_validation_duration_seconds`: Validation execution time
- `cicd_integration_current_debt_score`: Current debt score by component

### Health Endpoints
- `/health`: Overall system health status
- `/ready`: Readiness for processing requests
- `/metrics`: Prometheus metrics endpoint

### Structured Logging
All operations are logged with structured data including:
- Correlation IDs for request tracing
- Performance metrics and timing
- Error details and stack traces
- Component and patch identifiers

## Best Practices

### 1. Threshold Configuration
- Start with lenient thresholds and gradually tighten
- Configure component-specific limits based on criticality
- Monitor threshold violations and adjust as needed
- Use warning thresholds before blocking thresholds

### 2. Validation Integration
- Run validation on every pull request
- Include validation in pre-commit hooks
- Provide clear error messages and suggestions
- Allow emergency bypasses with proper approval

### 3. Reporting and Monitoring
- Generate reports for all pull requests
- Monitor debt trends over time
- Set up alerts for critical threshold violations
- Review and update thresholds regularly

### 4. Team Adoption
- Provide training on patch annotation standards
- Create templates and examples for common scenarios
- Establish clear escalation procedures for blocked merges
- Regular review of patch cleanup progress

## Troubleshooting

### Common Issues

#### Validation Failures
```
ERROR: Reason field is required and cannot be empty
```
**Solution:** Ensure all patch annotations include required fields (reason, upstream_issue, cleanup_task, component).

#### Threshold Violations
```
Component 'core' has 6 patches, exceeds limit (5)
```
**Solution:** Either clean up patches in the component or adjust threshold configuration.

#### Git Integration Issues
```
Failed to get changed files: Command 'git diff' returned non-zero exit status
```
**Solution:** Ensure the repository has proper git history and the specified branches exist.

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

cicd = CICDIntegration()
result = cicd.validate_patch_annotations(".")
```

### Performance Optimization

For large repositories:
- Use `changed_files` parameter to focus validation
- Enable parallel scanning in scanner configuration
- Adjust `max_workers` based on available CPU cores
- Consider excluding large binary files or generated code

## Contributing

When contributing to the CI/CD integration module:

1. Follow the existing code patterns and documentation style
2. Add comprehensive tests for new functionality
3. Update this README with new features or changes
4. Ensure all examples and CLI commands work correctly
5. Test integration with multiple CI/CD platforms

## Requirements Compliance

This implementation addresses the following requirements:

- **Requirement 6.1**: Code review integration with debt impact assessment
- **Requirement 6.2**: CI/CD pipeline flagging when patches exceed thresholds
- **Requirement 6.3**: Automated checks preventing merge of improperly annotated patches
- **Requirement 6.4**: Automatic validation of completed cleanup tasks
- **Requirement 6.5**: Technical debt report generation from current codebase state

The module provides comprehensive CI/CD integration capabilities that ensure technical debt patches are properly managed throughout the development lifecycle.