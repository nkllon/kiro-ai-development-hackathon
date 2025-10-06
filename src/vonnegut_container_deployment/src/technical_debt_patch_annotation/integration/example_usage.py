#!/usr/bin/env python3
"""
Example usage of CI/CD Integration for Technical Debt Patch Annotation System.

This script demonstrates how to use the CI/CD integration module in various scenarios:
- Validating patch annotations in CI/CD pipelines
- Checking debt thresholds with automated merge blocking
- Generating pull request impact reports
- Creating CI/CD workflow configurations
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.technical_debt_patch_annotation.integration.cicd_integration import (
    CICDIntegration,
    ThresholdConfiguration,
    create_github_actions_workflow,
    create_gitlab_ci_config,
    create_jenkins_pipeline
)


def example_basic_validation():
    """Example: Basic patch annotation validation."""
    print("=" * 60)
    print("Example 1: Basic Patch Annotation Validation")
    print("=" * 60)
    
    # Initialize CI/CD integration with default configuration
    cicd = CICDIntegration()
    
    # Validate patches in current repository
    repository_path = "."
    result = cicd.validate_patch_annotations(repository_path)
    
    print(f"Repository: {repository_path}")
    print(f"Patches validated: {result.patches_validated}")
    print(f"Validation success: {result.success}")
    print(f"Execution time: {result.execution_time_seconds:.2f} seconds")
    
    if result.validation_issues:
        print(f"\nValidation Issues ({len(result.validation_issues)}):")
        for issue in result.validation_issues:
            print(f"  {issue.severity.upper()}: {issue.message}")
            if issue.file_path:
                print(f"    File: {issue.file_path}:{issue.line_number or 'N/A'}")
            if issue.suggestion:
                print(f"    Suggestion: {issue.suggestion}")
    
    if result.should_block_merge:
        print(f"\n❌ MERGE BLOCKED")
        print(f"Reasons: {[r.value for r in result.block_reasons]}")
    else:
        print(f"\n✅ VALIDATION PASSED")
    
    return result.success


def example_custom_thresholds():
    """Example: Custom threshold configuration with strict limits."""
    print("\n" + "=" * 60)
    print("Example 2: Custom Threshold Configuration")
    print("=" * 60)
    
    # Create custom threshold configuration
    strict_thresholds = ThresholdConfiguration(
        max_patches_per_component=3,           # Very strict component limit
        max_critical_patches_per_component=0,  # No critical patches allowed
        max_total_patches=10,                  # Low total patch limit
        max_total_critical_patches=0,          # No critical patches in repo
        max_patch_age_days=30,                 # Patches must be resolved within 30 days
        component_debt_blocking_threshold=60.0 # Lower blocking threshold
    )
    
    # Initialize with custom configuration
    cicd = CICDIntegration(threshold_config=strict_thresholds)
    
    # Check thresholds
    repository_path = "."
    result = cicd.check_debt_thresholds(repository_path)
    
    print("Custom Threshold Configuration:")
    print(f"  Max patches per component: {strict_thresholds.max_patches_per_component}")
    print(f"  Max critical patches per component: {strict_thresholds.max_critical_patches_per_component}")
    print(f"  Max total patches: {strict_thresholds.max_total_patches}")
    print(f"  Component debt blocking threshold: {strict_thresholds.component_debt_blocking_threshold}%")
    
    print(f"\nThreshold Check Results:")
    print(f"  Patches analyzed: {result.patches_validated}")
    print(f"  Success: {result.success}")
    print(f"  Should block merge: {result.should_block_merge}")
    
    if result.threshold_violations:
        print(f"\nThreshold Violations ({len(result.threshold_violations)}):")
        for violation in result.threshold_violations:
            print(f"  ⚠️  {violation}")
    
    if result.validation_issues:
        print(f"\nValidation Issues ({len(result.validation_issues)}):")
        for issue in result.validation_issues[:3]:  # Show first 3
            print(f"  {issue.severity.upper()}: {issue.message}")
    
    return result.success


def example_pull_request_report():
    """Example: Generate pull request impact report."""
    print("\n" + "=" * 60)
    print("Example 3: Pull Request Impact Report")
    print("=" * 60)
    
    # Initialize CI/CD integration
    cicd = CICDIntegration()
    
    # Generate PR impact report
    repository_path = "."
    report = cicd.generate_pull_request_report(
        repository_path=repository_path,
        base_branch="main",
        head_branch="feature-branch",
        pull_request_id="PR-123"
    )
    
    print("Pull Request Impact Analysis:")
    print(f"  Repository: {repository_path}")
    print(f"  Base branch: main")
    print(f"  Head branch: feature-branch")
    print(f"  Pull request: PR-123")
    
    print(f"\nPatch Changes:")
    print(f"  Patches added: {report.patches_added}")
    print(f"  Patches removed: {report.patches_removed}")
    print(f"  Patches modified: {report.patches_modified}")
    print(f"  Net change: {report.net_patch_change:+d}")
    
    if report.patches_by_debt_level:
        print(f"\nDebt Level Distribution:")
        for level, count in report.patches_by_debt_level.items():
            print(f"  {level}: {count}")
    
    if report.affected_components:
        print(f"\nAffected Components:")
        for component in report.affected_components:
            debt_score = report.component_debt_changes.get(component, 0.0)
            print(f"  {component}: debt score {debt_score:.1f}")
    
    if report.validation_issues:
        print(f"\nValidation Issues ({len(report.validation_issues)}):")
        for issue in report.validation_issues[:3]:
            print(f"  {issue.severity.upper()}: {issue.message}")
    
    if report.recommendations:
        print(f"\nRecommendations:")
        for rec in report.recommendations:
            print(f"  • {rec}")
    
    print(f"\nMerge Decision:")
    if report.should_block_merge:
        print(f"  ❌ MERGE BLOCKED")
        print(f"  Reasons: {[r.value for r in report.block_reasons]}")
    else:
        print(f"  ✅ MERGE APPROVED")
    
    return not report.should_block_merge


def example_workflow_generation():
    """Example: Generate CI/CD workflow configurations."""
    print("\n" + "=" * 60)
    print("Example 4: CI/CD Workflow Generation")
    print("=" * 60)
    
    # Generate GitHub Actions workflow
    print("Generating GitHub Actions workflow...")
    github_workflow = create_github_actions_workflow()
    
    # Save to file
    github_file = ".github/workflows/patch-validation.yml"
    os.makedirs(os.path.dirname(github_file), exist_ok=True)
    with open(github_file, "w") as f:
        f.write(github_workflow)
    print(f"✅ GitHub Actions workflow saved to: {github_file}")
    
    # Generate GitLab CI configuration
    print("\nGenerating GitLab CI configuration...")
    gitlab_config = create_gitlab_ci_config()
    
    # Save to file
    gitlab_file = ".gitlab-ci-patch-validation.yml"
    with open(gitlab_file, "w") as f:
        f.write(gitlab_config)
    print(f"✅ GitLab CI configuration saved to: {gitlab_file}")
    
    # Generate Jenkins pipeline
    print("\nGenerating Jenkins pipeline...")
    jenkins_pipeline = create_jenkins_pipeline()
    
    # Save to file
    jenkins_file = "Jenkinsfile.patch-validation"
    with open(jenkins_file, "w") as f:
        f.write(jenkins_pipeline)
    print(f"✅ Jenkins pipeline saved to: {jenkins_file}")
    
    print(f"\nWorkflow files generated:")
    print(f"  GitHub Actions: {github_file}")
    print(f"  GitLab CI: {gitlab_file}")
    print(f"  Jenkins: {jenkins_file}")
    
    return True


def example_health_monitoring():
    """Example: Health status monitoring and capabilities."""
    print("\n" + "=" * 60)
    print("Example 5: Health Status Monitoring")
    print("=" * 60)
    
    # Initialize CI/CD integration
    cicd = CICDIntegration()
    
    # Get module information
    module_info = cicd.get_module_info()
    print("Module Information:")
    print(f"  Name: {module_info['module_name']}")
    print(f"  Version: {module_info['version']}")
    print(f"  Description: {module_info['description']}")
    
    # Get capabilities
    capabilities = cicd.get_capabilities()
    print(f"\nCapabilities ({len(capabilities)}):")
    for capability in capabilities:
        print(f"  • {capability}")
    
    # Get health status
    health_status = cicd.get_health_status()
    print(f"\nHealth Status:")
    print(f"  Service: {health_status['service']}")
    print(f"  Status: {health_status['status']}")
    print(f"  Configuration:")
    for key, value in health_status['configuration'].items():
        print(f"    {key}: {value}")
    
    return True


def example_cli_integration():
    """Example: Command-line interface usage."""
    print("\n" + "=" * 60)
    print("Example 6: Command-Line Interface Usage")
    print("=" * 60)
    
    print("The CI/CD integration module provides a command-line interface:")
    print()
    
    print("Validate patch annotations:")
    print("  python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .")
    print()
    
    print("Check debt thresholds:")
    print("  python -m technical_debt_patch_annotation.integration.cicd_integration check-thresholds .")
    print()
    
    print("Generate pull request report:")
    print("  python -m technical_debt_patch_annotation.integration.cicd_integration pr-report . --base-branch main --head-branch feature")
    print()
    
    print("Generate workflow configurations:")
    print("  python -m technical_debt_patch_annotation.integration.cicd_integration generate-workflows --platform github")
    print("  python -m technical_debt_patch_annotation.integration.cicd_integration generate-workflows --platform gitlab")
    print("  python -m technical_debt_patch_annotation.integration.cicd_integration generate-workflows --platform jenkins")
    
    return True


def main():
    """Run all CI/CD integration examples."""
    print("Technical Debt Patch Annotation System - CI/CD Integration Examples")
    print("=" * 80)
    print()
    print("This script demonstrates various CI/CD integration capabilities:")
    print("• Patch annotation validation in build pipelines")
    print("• Debt threshold checking with automated merge blocking")
    print("• Pull request impact assessment and reporting")
    print("• CI/CD workflow configuration generation")
    print("• Health monitoring and system capabilities")
    print()
    
    examples = [
        ("Basic Validation", example_basic_validation),
        ("Custom Thresholds", example_custom_thresholds),
        ("Pull Request Report", example_pull_request_report),
        ("Workflow Generation", example_workflow_generation),
        ("Health Monitoring", example_health_monitoring),
        ("CLI Integration", example_cli_integration)
    ]
    
    results = []
    
    for example_name, example_func in examples:
        try:
            print(f"\n🚀 Running {example_name} example...")
            success = example_func()
            results.append((example_name, "SUCCESS" if success else "COMPLETED"))
        except Exception as e:
            print(f"❌ {example_name} example failed: {str(e)}")
            results.append((example_name, f"ERROR: {str(e)}"))
    
    # Print summary
    print("\n" + "=" * 80)
    print("📋 Example Execution Summary")
    print("=" * 80)
    
    for example_name, result in results:
        status_icon = "✅" if result in ["SUCCESS", "COMPLETED"] else "❌"
        print(f"{status_icon} {example_name}: {result}")
    
    print(f"\n🎉 All CI/CD integration examples completed!")
    print()
    print("Next Steps:")
    print("• Integrate the CI/CD module into your build pipelines")
    print("• Configure custom thresholds for your project requirements")
    print("• Set up automated patch validation in code reviews")
    print("• Monitor technical debt trends and cleanup progress")


if __name__ == "__main__":
    main()