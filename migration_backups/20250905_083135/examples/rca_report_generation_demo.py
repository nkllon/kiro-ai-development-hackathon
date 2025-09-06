#!/usr/bin/env python3
"""
Demo script for RCA Report Generation System
Shows different report formats and configurations in action
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.testing.rca_report_generator import (
    RCAReportGenerator, ReportConfiguration, ReportFormat, ReportSection
)
from beast_mode.testing.rca_integration import (
    TestFailureData, TestRCASummaryData, TestRCAReportData
)
from beast_mode.analysis.rca_engine import (
    RCAResult, Failure, FailureCategory, RootCauseType, RootCause,
    SystematicFix, PreventionPattern, ComprehensiveAnalysisResult
)


def create_sample_test_failures():
    """Create sample test failure data for demonstration"""
    failures = []
    
    # Test failure 1: Import error
    failures.append(TestFailureData(
        test_name="test_import_functionality",
        test_file="tests/test_imports.py",
        failure_type="error",
        error_message="ImportError: No module named 'missing_package'",
        stack_trace="Traceback (most recent call last):\n  File tests/test_imports.py, line 5\n    import missing_package\nImportError: No module named 'missing_package'",
        test_function="test_import_functionality",
        test_class="TestImports",
        failure_timestamp=datetime.now(),
        test_context={"test_type": "integration", "priority": "high"},
        pytest_node_id="tests/test_imports.py::TestImports::test_import_functionality"
    ))
    
    # Test failure 2: Assertion error
    failures.append(TestFailureData(
        test_name="test_calculation_accuracy",
        test_file="tests/test_calculations.py",
        failure_type="assertion",
        error_message="AssertionError: Expected 10, got 8",
        stack_trace="Traceback (most recent call last):\n  File tests/test_calculations.py, line 15\n    assert result == 10\nAssertionError: Expected 10, got 8",
        test_function="test_calculation_accuracy",
        test_class="TestCalculations",
        failure_timestamp=datetime.now(),
        test_context={"test_type": "unit", "priority": "medium"},
        pytest_node_id="tests/test_calculations.py::TestCalculations::test_calculation_accuracy"
    ))
    
    # Test failure 3: File not found
    failures.append(TestFailureData(
        test_name="test_file_operations",
        test_file="tests/test_files.py",
        failure_type="error",
        error_message="FileNotFoundError: [Errno 2] No such file or directory: 'config.json'",
        stack_trace="Traceback (most recent call last):\n  File tests/test_files.py, line 20\n    with open('config.json') as f:\nFileNotFoundError: [Errno 2] No such file or directory: 'config.json'",
        test_function="test_file_operations",
        test_class=None,
        failure_timestamp=datetime.now(),
        test_context={"test_type": "integration", "priority": "critical"},
        pytest_node_id="tests/test_files.py::test_file_operations"
    ))
    
    return failures


def create_sample_rca_results(test_failures):
    """Create sample RCA results for demonstration"""
    rca_results = []
    
    for i, test_failure in enumerate(test_failures):
        # Create corresponding RCA failure
        failure = Failure(
            failure_id=f"test_failure_{i+1}",
            timestamp=test_failure.failure_timestamp,
            component=f"test:{test_failure.test_file}",
            error_message=test_failure.error_message,
            stack_trace=test_failure.stack_trace,
            context={"test_file": test_failure.test_file, "test_function": test_failure.test_function},
            category=FailureCategory.DEPENDENCY_ISSUE if "ImportError" in test_failure.error_message 
                     else FailureCategory.CONFIGURATION_ERROR if "FileNotFoundError" in test_failure.error_message
                     else FailureCategory.UNKNOWN
        )
        
        # Create root cause
        if "ImportError" in test_failure.error_message:
            root_cause = RootCause(
                cause_type=RootCauseType.BROKEN_DEPENDENCIES,
                description="Missing Python package dependency",
                evidence=["ImportError in test execution", "Package not in requirements.txt"],
                confidence_score=0.9,
                impact_severity="high",
                affected_components=[test_failure.test_file]
            )
            fix_description = "Install missing package and update requirements.txt"
            fix_steps = [
                "Identify missing package name",
                "Install package using pip",
                "Add package to requirements.txt",
                "Verify tests pass"
            ]
        elif "FileNotFoundError" in test_failure.error_message:
            root_cause = RootCause(
                cause_type=RootCauseType.MISSING_FILES,
                description="Required configuration file missing",
                evidence=["FileNotFoundError in test execution", "config.json not found"],
                confidence_score=0.85,
                impact_severity="critical",
                affected_components=[test_failure.test_file]
            )
            fix_description = "Create missing configuration file"
            fix_steps = [
                "Create config.json file",
                "Add required configuration values",
                "Verify file permissions",
                "Run tests to confirm fix"
            ]
        else:
            root_cause = RootCause(
                cause_type=RootCauseType.SYSTEM_CORRUPTION,
                description="Calculation logic error",
                evidence=["Assertion failure", "Incorrect calculation result"],
                confidence_score=0.7,
                impact_severity="medium",
                affected_components=[test_failure.test_file]
            )
            fix_description = "Fix calculation logic error"
            fix_steps = [
                "Review calculation algorithm",
                "Fix mathematical error",
                "Update test expectations if needed",
                "Verify all related tests pass"
            ]
        
        # Create systematic fix
        systematic_fix = SystematicFix(
            fix_id=f"fix_{i+1}",
            root_cause=root_cause,
            fix_description=fix_description,
            implementation_steps=fix_steps,
            validation_criteria=[
                "Root cause no longer present",
                "All tests pass",
                "No regression in other functionality"
            ],
            rollback_plan="Revert changes if issues occur",
            estimated_time_minutes=15 if "ImportError" in test_failure.error_message else 10
        )
        
        # Create prevention pattern
        prevention_pattern = PreventionPattern(
            pattern_id=f"pattern_{i+1}",
            pattern_name=f"Prevent {root_cause.cause_type.value} in tests",
            failure_signature=test_failure.error_message[:50],
            root_cause_pattern=root_cause.description,
            prevention_steps=[
                "Add automated dependency checks",
                "Validate configuration files in CI",
                "Add pre-commit hooks for validation"
            ],
            detection_criteria=[
                "ImportError patterns",
                "FileNotFoundError patterns",
                "Assertion failure patterns"
            ],
            automated_checks=[
                "pip check",
                "config file validation",
                "unit test coverage"
            ],
            pattern_hash=f"hash_{i+1}"
        )
        
        # Create RCA result
        rca_result = RCAResult(
            failure=failure,
            analysis=ComprehensiveAnalysisResult(
                symptoms=[root_cause.cause_type.value],
                tool_health_status={"python": "healthy", "pip": "healthy"},
                dependency_analysis={"missing_packages": ["missing_package"] if "ImportError" in test_failure.error_message else []},
                configuration_analysis={"missing_files": ["config.json"] if "FileNotFoundError" in test_failure.error_message else []},
                installation_integrity={"python_version": "3.11", "pip_version": "23.0"},
                environmental_factors={"working_directory": "/test/project", "path_set": True},
                analysis_confidence=root_cause.confidence_score
            ),
            root_causes=[root_cause],
            systematic_fixes=[systematic_fix],
            validation_results=[],
            prevention_patterns=[prevention_pattern],
            total_analysis_time_seconds=2.3,
            rca_confidence_score=root_cause.confidence_score
        )
        
        rca_results.append(rca_result)
    
    return rca_results


def create_sample_rca_report():
    """Create complete sample RCA report for demonstration"""
    test_failures = create_sample_test_failures()
    rca_results = create_sample_rca_results(test_failures)
    
    # Create summary
    summary = TestRCASummaryData(
        most_common_root_causes=[
            (RootCauseType.BROKEN_DEPENDENCIES, 1),
            (RootCauseType.MISSING_FILES, 1),
            (RootCauseType.SYSTEM_CORRUPTION, 1)
        ],
        systematic_fixes_available=3,
        pattern_matches_found=2,
        estimated_fix_time_minutes=35,
        confidence_score=0.82,
        critical_issues=["Missing critical configuration file", "Broken dependency blocking tests"]
    )
    
    # Create grouped failures
    grouped_failures = {
        "dependency_errors": [test_failures[0]],
        "assertion_errors": [test_failures[1]],
        "file_errors": [test_failures[2]]
    }
    
    # Create recommendations
    recommendations = [
        "Fix missing dependencies first as they block other tests",
        "Create missing configuration files to resolve file errors",
        "Review calculation logic for assertion failures",
        "Add automated checks to prevent similar issues",
        "Update CI pipeline to catch these issues early"
    ]
    
    # Create next steps
    next_steps = [
        "Install missing Python packages",
        "Create config.json with required settings",
        "Fix calculation algorithm in test_calculations.py",
        "Add dependency validation to CI pipeline",
        "Document configuration requirements"
    ]
    
    # Create prevention patterns
    all_prevention_patterns = []
    for result in rca_results:
        all_prevention_patterns.extend(result.prevention_patterns)
    
    return TestRCAReportData(
        analysis_timestamp=datetime.now(),
        total_failures=len(test_failures),
        failures_analyzed=len(rca_results),
        grouped_failures=grouped_failures,
        rca_results=rca_results,
        summary=summary,
        recommendations=recommendations,
        prevention_patterns=all_prevention_patterns,
        next_steps=next_steps
    )


def demo_console_report():
    """Demonstrate console report generation"""
    print("🔍 RCA Report Generation Demo - Console Format")
    print("=" * 60)
    
    # Create report generator
    generator = RCAReportGenerator()
    
    # Create sample data
    rca_report = create_sample_rca_report()
    
    # Generate console report with colors
    print("\n📺 Console Report (with colors):")
    print("-" * 40)
    console_output = generator.format_for_console(rca_report, use_colors=True)
    print(console_output)
    
    # Generate console report without colors
    print("\n📺 Console Report (no colors):")
    print("-" * 40)
    console_output_plain = generator.format_for_console(rca_report, use_colors=False)
    print(console_output_plain[:500] + "..." if len(console_output_plain) > 500 else console_output_plain)


def demo_json_report():
    """Demonstrate JSON report generation"""
    print("\n📄 JSON Report Format:")
    print("-" * 40)
    
    # Create report generator
    generator = RCAReportGenerator()
    
    # Create sample data
    rca_report = create_sample_rca_report()
    
    # Generate JSON report
    json_data = generator.generate_json_report(rca_report)
    
    # Pretty print key sections
    import json
    print("Report Metadata:")
    print(json.dumps(json_data["report_metadata"], indent=2))
    
    print("\nAnalysis Summary:")
    print(json.dumps(json_data["analysis_summary"], indent=2))
    
    print("\nRoot Causes:")
    print(json.dumps(json_data["root_causes"], indent=2))
    
    print(f"\nFull JSON report has {len(json.dumps(json_data))} characters")


def demo_markdown_report():
    """Demonstrate markdown report generation"""
    print("\n📝 Markdown Report Format:")
    print("-" * 40)
    
    # Create report generator
    generator = RCAReportGenerator()
    
    # Create sample data
    rca_report = create_sample_rca_report()
    
    # Generate markdown report
    markdown_content = generator.generate_markdown_report(rca_report)
    
    # Show first part of markdown
    lines = markdown_content.split('\n')
    preview_lines = lines[:30]  # Show first 30 lines
    
    print('\n'.join(preview_lines))
    if len(lines) > 30:
        print(f"\n... and {len(lines) - 30} more lines")
    
    print(f"\nFull markdown report has {len(markdown_content)} characters")


def demo_custom_configurations():
    """Demonstrate custom report configurations"""
    print("\n⚙️  Custom Report Configurations:")
    print("-" * 40)
    
    # Create report generator
    generator = RCAReportGenerator()
    
    # Create sample data
    rca_report = create_sample_rca_report()
    
    # Configuration 1: Summary only
    print("\n1. Summary-only report:")
    config1 = ReportConfiguration(
        format=ReportFormat.CONSOLE,
        include_sections=[ReportSection.HEADER, ReportSection.SUMMARY],
        color_output=False
    )
    
    report1 = generator.generate_report(rca_report, config1)
    combined_content = '\n'.join([section.content for section in report1.sections])
    print(combined_content)
    
    # Configuration 2: Verbose with stack traces
    print("\n2. Verbose report with stack traces:")
    config2 = ReportConfiguration(
        format=ReportFormat.CONSOLE,
        include_sections=[ReportSection.FAILURES, ReportSection.SYSTEMATIC_FIXES],
        include_stack_traces=True,
        verbose_mode=True,
        max_failures_displayed=2,
        color_output=False
    )
    
    report2 = generator.generate_report(rca_report, config2)
    combined_content2 = '\n'.join([section.content for section in report2.sections])
    print(combined_content2[:800] + "..." if len(combined_content2) > 800 else combined_content2)


def demo_report_metrics():
    """Demonstrate report generation metrics"""
    print("\n📊 Report Generation Metrics:")
    print("-" * 40)
    
    # Create report generator
    generator = RCAReportGenerator()
    
    # Create sample data
    rca_report = create_sample_rca_report()
    
    print("Initial metrics:")
    print(f"Reports generated: {generator.reports_generated}")
    print(f"Console reports: {generator.console_reports}")
    print(f"JSON reports: {generator.json_reports}")
    print(f"Markdown reports: {generator.markdown_reports}")
    
    # Generate different types of reports
    generator.format_for_console(rca_report)
    generator.generate_json_report(rca_report)
    generator.generate_markdown_report(rca_report)
    
    print("\nAfter generating reports:")
    print(f"Reports generated: {generator.reports_generated}")
    print(f"Console reports: {generator.console_reports}")
    print(f"JSON reports: {generator.json_reports}")
    print(f"Markdown reports: {generator.markdown_reports}")
    
    # Show module status
    print("\nModule status:")
    status = generator.get_module_status()
    for key, value in status.items():
        print(f"  {key}: {value}")


def main():
    """Run all demonstrations"""
    print("🚀 RCA Report Generation System Demo")
    print("=" * 60)
    print("This demo shows the RCA report generation system in action")
    print("with sample test failure data and different output formats.")
    print()
    
    try:
        # Run demonstrations
        demo_console_report()
        demo_json_report()
        demo_markdown_report()
        demo_custom_configurations()
        demo_report_metrics()
        
        print("\n✅ Demo completed successfully!")
        print("The RCA Report Generation System supports:")
        print("  • Console output with colors and clear sections")
        print("  • JSON reports for CI/CD integration")
        print("  • Markdown reports for documentation")
        print("  • Configurable sections and formatting options")
        print("  • Comprehensive metrics and health monitoring")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())