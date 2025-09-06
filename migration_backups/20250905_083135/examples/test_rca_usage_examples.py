#!/usr/bin/env python3
"""
Test RCA Integration Usage Examples

This file demonstrates various usage scenarios for the Test RCA Integration system.
These examples show how to use RCA integration in different development workflows.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from beast_mode.testing.test_failure_detector import TestFailureDetector
from beast_mode.testing.rca_integration import TestRCAIntegrator
from beast_mode.testing.rca_report_generator import RCAReportGenerator
from beast_mode.testing.models import TestFailure


def example_1_basic_rca_usage():
    """
    Example 1: Basic RCA usage after test failures
    
    This example shows the most common usage pattern:
    1. Tests fail during development
    2. RCA automatically analyzes failures
    3. Developer gets actionable insights
    """
    print("=" * 60)
    print("Example 1: Basic RCA Usage")
    print("=" * 60)
    
    # Simulate pytest output with failures
    pytest_output = """
    ========================= FAILURES =========================
    _________________________ test_user_login _________________________
    
        def test_user_login():
            user = User("testuser", "password123")
    >       assert user.login() == True
    E       AssertionError: assert False == True
    E        +  where False = <bound method User.login of <User testuser>>()
    
    tests/test_auth.py:15: AssertionError
    
    _________________________ test_database_connection _________________________
    
        def test_database_connection():
    >       conn = get_database_connection()
    E       ConnectionError: Unable to connect to database: Connection timeout
    
    tests/test_db.py:23: ConnectionError
    =========================== short test summary info ============================
    FAILED tests/test_auth.py::test_user_login - AssertionError: assert False == True
    FAILED tests/test_db.py::test_database_connection - ConnectionError: Unable to connect to database
    ========================= 2 failed, 0 passed in 5.23s =========================
    """
    
    print("Step 1: Detect test failures from pytest output")
    detector = TestFailureDetector()
    failures = detector.parse_pytest_output(pytest_output)
    
    print(f"Detected {len(failures)} test failures:")
    for failure in failures:
        print(f"  - {failure.test_name}: {failure.failure_type}")
    
    print("\nStep 2: Trigger RCA analysis")
    integrator = TestRCAIntegrator()
    
    start_time = time.time()
    analysis_result = integrator.analyze_test_failures(failures)
    analysis_time = time.time() - start_time
    
    print(f"RCA analysis completed in {analysis_time:.2f} seconds")
    
    print("\nStep 3: Generate and display report")
    report_generator = RCAReportGenerator()
    console_report = report_generator.generate_console_report(analysis_result)
    
    print(console_report)
    
    print("\n" + "=" * 60)
    print("Example 1 Complete")
    print("=" * 60 + "\n")


def example_2_manual_rca_analysis():
    """
    Example 2: Manual RCA analysis for specific failures
    
    This example shows how to manually trigger RCA analysis
    for specific test failures or when automatic analysis
    didn't run.
    """
    print("=" * 60)
    print("Example 2: Manual RCA Analysis")
    print("=" * 60)
    
    print("Scenario: Developer wants to analyze a specific failing test")
    
    # Create a specific test failure manually
    specific_failure = TestFailure(
        test_name="test_payment_processing",
        test_file="tests/test_payments.py",
        failure_type="timeout",
        error_message="Payment processing timed out after 30 seconds",
        stack_trace="""
        Traceback (most recent call last):
          File "tests/test_payments.py", line 45, in test_payment_processing
            result = process_payment(payment_data)
          File "src/payments/processor.py", line 123, in process_payment
            response = external_api.charge(amount, card_token)
          File "src/payments/external_api.py", line 67, in charge
            raise TimeoutError("Payment processing timed out")
        TimeoutError: Payment processing timed out after 30 seconds
        """,
        test_function="test_payment_processing",
        failure_timestamp=datetime.now(),
        test_context={
            "framework": "pytest",
            "test_duration": 30.5,
            "environment": "development",
            "external_dependencies": ["payment_api", "database"]
        },
        pytest_node_id="tests/test_payments.py::test_payment_processing"
    )
    
    print(f"Analyzing specific failure: {specific_failure.test_name}")
    
    # Perform focused RCA analysis
    integrator = TestRCAIntegrator()
    
    # Configure for detailed analysis of single failure
    integrator.config.update({
        'detailed_analysis': True,
        'include_external_factors': True,
        'timeout_analysis': True
    })
    
    analysis_result = integrator.analyze_single_failure(specific_failure)
    
    print("\nDetailed RCA Results:")
    print(f"Root Causes Found: {len(analysis_result.root_causes)}")
    
    for i, root_cause in enumerate(analysis_result.root_causes, 1):
        print(f"\n{i}. {root_cause.category.upper()}: {root_cause.description}")
        print(f"   Confidence: {root_cause.confidence:.0%}")
        print(f"   Systematic Fix: {root_cause.systematic_fix.description}")
        
        if root_cause.systematic_fix.steps:
            print("   Implementation Steps:")
            for step in root_cause.systematic_fix.steps:
                print(f"     - {step}")
    
    print("\n" + "=" * 60)
    print("Example 2 Complete")
    print("=" * 60 + "\n")


def example_3_batch_failure_analysis():
    """
    Example 3: Batch analysis of multiple related failures
    
    This example shows how RCA handles multiple failures
    that might be related, grouping them for efficient
    analysis and providing comprehensive insights.
    """
    print("=" * 60)
    print("Example 3: Batch Failure Analysis")
    print("=" * 60)
    
    print("Scenario: Multiple tests failing after infrastructure change")
    
    # Create multiple related failures
    failures = [
        TestFailure(
            test_name="test_user_registration",
            test_file="tests/test_user_management.py",
            failure_type="connection_error",
            error_message="Database connection failed: Connection refused",
            stack_trace="ConnectionError: [Errno 111] Connection refused",
            test_function="test_user_registration",
            failure_timestamp=datetime.now(),
            test_context={"framework": "pytest", "database": "postgresql"},
            pytest_node_id="tests/test_user_management.py::test_user_registration"
        ),
        TestFailure(
            test_name="test_user_login",
            test_file="tests/test_authentication.py",
            failure_type="connection_error",
            error_message="Database connection failed: Connection refused",
            stack_trace="ConnectionError: [Errno 111] Connection refused",
            test_function="test_user_login",
            failure_timestamp=datetime.now(),
            test_context={"framework": "pytest", "database": "postgresql"},
            pytest_node_id="tests/test_authentication.py::test_user_login"
        ),
        TestFailure(
            test_name="test_order_creation",
            test_file="tests/test_orders.py",
            failure_type="connection_error",
            error_message="Database connection failed: Connection refused",
            stack_trace="ConnectionError: [Errno 111] Connection refused",
            test_function="test_order_creation",
            failure_timestamp=datetime.now(),
            test_context={"framework": "pytest", "database": "postgresql"},
            pytest_node_id="tests/test_orders.py::test_order_creation"
        ),
        TestFailure(
            test_name="test_api_health_check",
            test_file="tests/test_api.py",
            failure_type="assertion_error",
            error_message="API health check failed: Expected 200, got 503",
            stack_trace="AssertionError: Expected 200, got 503",
            test_function="test_api_health_check",
            failure_timestamp=datetime.now(),
            test_context={"framework": "pytest", "api_endpoint": "/health"},
            pytest_node_id="tests/test_api.py::test_api_health_check"
        )
    ]
    
    print(f"Analyzing {len(failures)} related failures...")
    
    integrator = TestRCAIntegrator()
    
    # Enable batch analysis features
    integrator.config.update({
        'group_related_failures': True,
        'identify_common_causes': True,
        'prioritize_critical_issues': True
    })
    
    analysis_result = integrator.analyze_test_failures(failures)
    
    print(f"\nFailure Grouping Results:")
    print(f"Total Failures: {len(failures)}")
    print(f"Failure Groups: {len(analysis_result.grouped_failures)}")
    
    for group_name, group_failures in analysis_result.grouped_failures.items():
        print(f"\nGroup: {group_name}")
        print(f"  Failures: {len(group_failures)}")
        print(f"  Tests affected:")
        for failure in group_failures:
            print(f"    - {failure.test_name}")
    
    print(f"\nCommon Root Causes:")
    common_causes = analysis_result.get_common_root_causes()
    for cause in common_causes:
        print(f"  - {cause.description} (affects {cause.affected_tests} tests)")
        print(f"    Confidence: {cause.confidence:.0%}")
        print(f"    Priority: {cause.priority}")
    
    print(f"\nSystematic Fixes (prioritized):")
    systematic_fixes = analysis_result.get_prioritized_fixes()
    for i, fix in enumerate(systematic_fixes, 1):
        print(f"  {i}. {fix.title}")
        print(f"     Impact: {fix.impact_description}")
        print(f"     Estimated Time: {fix.estimated_time_minutes} minutes")
        print(f"     Steps: {len(fix.steps)} implementation steps")
    
    print("\n" + "=" * 60)
    print("Example 3 Complete")
    print("=" * 60 + "\n")


def example_4_custom_report_generation():
    """
    Example 4: Custom report generation for different audiences
    
    This example shows how to generate different types of reports
    for different audiences (developers, managers, CI/CD systems).
    """
    print("=" * 60)
    print("Example 4: Custom Report Generation")
    print("=" * 60)
    
    # Create sample analysis result
    sample_failures = [
        TestFailure(
            test_name="test_integration_workflow",
            test_file="tests/test_integration.py",
            failure_type="integration_error",
            error_message="Service integration failed: Authentication error",
            stack_trace="AuthenticationError: Invalid API key",
            test_function="test_integration_workflow",
            failure_timestamp=datetime.now(),
            test_context={"framework": "pytest", "service": "external_api"},
            pytest_node_id="tests/test_integration.py::test_integration_workflow"
        )
    ]
    
    integrator = TestRCAIntegrator()
    analysis_result = integrator.analyze_test_failures(sample_failures)
    
    report_generator = RCAReportGenerator()
    
    print("Generating reports for different audiences...\n")
    
    # 1. Developer Console Report (immediate feedback)
    print("1. Developer Console Report:")
    print("-" * 30)
    console_report = report_generator.generate_console_report(
        analysis_result,
        format_options={
            'include_stack_traces': True,
            'include_fix_steps': True,
            'color_output': True,
            'verbose': True
        }
    )
    print(console_report)
    
    # 2. Manager Summary Report (high-level overview)
    print("\n2. Manager Summary Report:")
    print("-" * 30)
    manager_report = report_generator.generate_summary_report(
        analysis_result,
        format_options={
            'focus_on_impact': True,
            'include_time_estimates': True,
            'highlight_critical_issues': True,
            'business_language': True
        }
    )
    print(manager_report)
    
    # 3. CI/CD JSON Report (machine-readable)
    print("\n3. CI/CD JSON Report:")
    print("-" * 30)
    json_report = report_generator.generate_json_report(
        analysis_result,
        format_options={
            'include_metadata': True,
            'structured_fixes': True,
            'machine_readable': True
        }
    )
    print(json.dumps(json_report, indent=2))
    
    # 4. Documentation Markdown Report (for knowledge base)
    print("\n4. Documentation Markdown Report:")
    print("-" * 30)
    markdown_report = report_generator.generate_markdown_report(
        analysis_result,
        format_options={
            'include_prevention_patterns': True,
            'detailed_analysis': True,
            'learning_outcomes': True,
            'searchable_format': True
        }
    )
    print(markdown_report[:500] + "..." if len(markdown_report) > 500 else markdown_report)
    
    print("\n" + "=" * 60)
    print("Example 4 Complete")
    print("=" * 60 + "\n")


def example_5_performance_optimization():
    """
    Example 5: Performance optimization and timeout handling
    
    This example demonstrates how RCA handles performance
    requirements and timeout constraints.
    """
    print("=" * 60)
    print("Example 5: Performance Optimization")
    print("=" * 60)
    
    print("Scenario: Large test suite with many failures needs fast analysis")
    
    # Create many failures to test performance
    many_failures = []
    for i in range(20):
        failure = TestFailure(
            test_name=f"test_function_{i}",
            test_file=f"tests/test_module_{i % 5}.py",
            failure_type="assertion_error" if i % 2 == 0 else "runtime_error",
            error_message=f"Test {i} failed with error",
            stack_trace=f"Traceback for test {i}...",
            test_function=f"test_function_{i}",
            failure_timestamp=datetime.now(),
            test_context={"framework": "pytest", "module": f"module_{i % 5}"},
            pytest_node_id=f"tests/test_module_{i % 5}.py::test_function_{i}"
        )
        many_failures.append(failure)
    
    print(f"Created {len(many_failures)} test failures for analysis")
    
    integrator = TestRCAIntegrator()
    
    # Configure for performance optimization
    integrator.config.update({
        'max_analysis_time': 30,  # 30-second timeout
        'parallel_analysis': True,
        'quick_pattern_matching': True,
        'limit_deep_analysis': True,
        'prioritize_critical_failures': True
    })
    
    print("\nStarting performance-optimized RCA analysis...")
    start_time = time.time()
    
    try:
        analysis_result = integrator.analyze_test_failures(
            many_failures,
            timeout=30,
            performance_mode=True
        )
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        print(f"✅ Analysis completed successfully!")
        print(f"   Total time: {analysis_time:.2f} seconds")
        print(f"   Failures analyzed: {analysis_result.failures_analyzed}")
        print(f"   Root causes found: {len(analysis_result.all_root_causes)}")
        print(f"   Performance: {analysis_result.failures_analyzed / analysis_time:.1f} failures/second")
        
        # Show performance metrics
        if hasattr(analysis_result, 'performance_metrics'):
            metrics = analysis_result.performance_metrics
            print(f"\nPerformance Metrics:")
            print(f"   Pattern matching time: {metrics.get('pattern_matching_time', 0):.2f}s")
            print(f"   Analysis time: {metrics.get('analysis_time', 0):.2f}s")
            print(f"   Report generation time: {metrics.get('report_time', 0):.2f}s")
            print(f"   Memory usage: {metrics.get('memory_usage_mb', 0):.1f} MB")
        
    except TimeoutError as e:
        end_time = time.time()
        analysis_time = end_time - start_time
        
        print(f"⚠️  Analysis timed out after {analysis_time:.2f} seconds")
        print(f"   Partial results available: {e.partial_results is not None}")
        
        if e.partial_results:
            print(f"   Failures analyzed: {e.partial_results.failures_analyzed}")
            print(f"   Root causes found: {len(e.partial_results.all_root_causes)}")
    
    print("\n" + "=" * 60)
    print("Example 5 Complete")
    print("=" * 60 + "\n")


def example_6_pattern_learning():
    """
    Example 6: Pattern learning and library management
    
    This example shows how RCA learns from successful
    analyses and builds up a pattern library for faster
    future analysis.
    """
    print("=" * 60)
    print("Example 6: Pattern Learning")
    print("=" * 60)
    
    print("Scenario: RCA learns from repeated failure patterns")
    
    # Simulate a common failure pattern that appears multiple times
    common_failure_pattern = [
        TestFailure(
            test_name="test_database_query_1",
            test_file="tests/test_db_queries.py",
            failure_type="connection_timeout",
            error_message="Database query timed out after 5 seconds",
            stack_trace="TimeoutError: Query execution exceeded timeout",
            test_function="test_database_query_1",
            failure_timestamp=datetime.now(),
            test_context={"framework": "pytest", "query_type": "complex_join"},
            pytest_node_id="tests/test_db_queries.py::test_database_query_1"
        ),
        TestFailure(
            test_name="test_database_query_2",
            test_file="tests/test_db_queries.py",
            failure_type="connection_timeout",
            error_message="Database query timed out after 5 seconds",
            stack_trace="TimeoutError: Query execution exceeded timeout",
            test_function="test_database_query_2",
            failure_timestamp=datetime.now(),
            test_context={"framework": "pytest", "query_type": "complex_join"},
            pytest_node_id="tests/test_db_queries.py::test_database_query_2"
        )
    ]
    
    integrator = TestRCAIntegrator()
    
    # Enable pattern learning
    integrator.config.update({
        'pattern_learning_enabled': True,
        'learn_from_successful_analysis': True,
        'update_pattern_library': True
    })
    
    print("First analysis (no existing patterns):")
    start_time = time.time()
    first_analysis = integrator.analyze_test_failures(common_failure_pattern)
    first_time = time.time() - start_time
    print(f"  Analysis time: {first_time:.2f} seconds")
    print(f"  Patterns learned: {first_analysis.patterns_learned}")
    
    # Simulate the same pattern appearing again
    print("\nSecond analysis (with learned patterns):")
    start_time = time.time()
    second_analysis = integrator.analyze_test_failures(common_failure_pattern)
    second_time = time.time() - start_time
    print(f"  Analysis time: {second_time:.2f} seconds")
    print(f"  Pattern matches found: {second_analysis.pattern_matches}")
    print(f"  Speed improvement: {((first_time - second_time) / first_time * 100):.1f}%")
    
    # Show pattern library growth
    pattern_library = integrator.get_pattern_library()
    print(f"\nPattern Library Status:")
    print(f"  Total patterns: {len(pattern_library.patterns)}")
    print(f"  Database timeout patterns: {len(pattern_library.get_patterns_by_type('database_timeout'))}")
    print(f"  Success rate: {pattern_library.get_success_rate():.1%}")
    
    # Show most effective patterns
    top_patterns = pattern_library.get_top_patterns(limit=3)
    print(f"\nMost Effective Patterns:")
    for i, pattern in enumerate(top_patterns, 1):
        print(f"  {i}. {pattern.name}")
        print(f"     Match rate: {pattern.match_rate:.1%}")
        print(f"     Success rate: {pattern.success_rate:.1%}")
        print(f"     Times used: {pattern.usage_count}")
    
    print("\n" + "=" * 60)
    print("Example 6 Complete")
    print("=" * 60 + "\n")


def example_7_ci_cd_integration():
    """
    Example 7: CI/CD pipeline integration
    
    This example shows how to integrate RCA with CI/CD
    pipelines for automated failure analysis and reporting.
    """
    print("=" * 60)
    print("Example 7: CI/CD Integration")
    print("=" * 60)
    
    print("Scenario: Automated RCA in CI/CD pipeline")
    
    # Simulate CI/CD environment variables
    ci_environment = {
        'CI': 'true',
        'BUILD_ID': '12345',
        'BRANCH_NAME': 'feature/user-authentication',
        'COMMIT_SHA': 'abc123def456',
        'PR_NUMBER': '42',
        'BUILD_URL': 'https://ci.example.com/builds/12345'
    }
    
    # Simulate test failures in CI/CD
    ci_failures = [
        TestFailure(
            test_name="test_user_authentication",
            test_file="tests/test_auth.py",
            failure_type="integration_error",
            error_message="Authentication service unavailable",
            stack_trace="ConnectionError: Service unavailable",
            test_function="test_user_authentication",
            failure_timestamp=datetime.now(),
            test_context={
                "framework": "pytest",
                "environment": "ci",
                "build_id": ci_environment['BUILD_ID'],
                "branch": ci_environment['BRANCH_NAME']
            },
            pytest_node_id="tests/test_auth.py::test_user_authentication"
        )
    ]
    
    print(f"CI/CD Environment: {ci_environment['BRANCH_NAME']} (Build {ci_environment['BUILD_ID']})")
    
    integrator = TestRCAIntegrator()
    
    # Configure for CI/CD environment
    integrator.config.update({
        'ci_mode': True,
        'generate_artifacts': True,
        'notify_on_critical_issues': True,
        'include_build_context': True
    })
    
    analysis_result = integrator.analyze_test_failures(
        ci_failures,
        ci_context=ci_environment
    )
    
    # Generate CI/CD artifacts
    report_generator = RCAReportGenerator()
    
    # 1. JUnit XML for test reporting integration
    junit_xml = report_generator.generate_junit_xml(analysis_result)
    print("Generated JUnit XML artifact for test reporting")
    
    # 2. JSON artifact for build systems
    build_artifact = {
        'build_id': ci_environment['BUILD_ID'],
        'branch': ci_environment['BRANCH_NAME'],
        'commit_sha': ci_environment['COMMIT_SHA'],
        'rca_analysis': report_generator.generate_json_report(analysis_result),
        'critical_issues': analysis_result.get_critical_issues(),
        'recommended_actions': analysis_result.get_recommended_actions()
    }
    
    print("Generated build artifact:")
    print(json.dumps(build_artifact, indent=2)[:300] + "...")
    
    # 3. Notification payload for team communication
    if analysis_result.has_critical_issues():
        notification = {
            'type': 'critical_test_failure',
            'build_id': ci_environment['BUILD_ID'],
            'branch': ci_environment['BRANCH_NAME'],
            'pr_number': ci_environment.get('PR_NUMBER'),
            'critical_issues': len(analysis_result.get_critical_issues()),
            'estimated_fix_time': analysis_result.get_estimated_fix_time(),
            'build_url': ci_environment['BUILD_URL'],
            'rca_summary': analysis_result.get_executive_summary()
        }
        
        print("\nCritical issue notification:")
        print(json.dumps(notification, indent=2))
    
    # 4. Exit code for CI/CD pipeline control
    exit_code = 0 if not analysis_result.has_critical_issues() else 1
    print(f"\nCI/CD Exit Code: {exit_code}")
    print("(0 = continue pipeline, 1 = fail pipeline)")
    
    print("\n" + "=" * 60)
    print("Example 7 Complete")
    print("=" * 60 + "\n")


def main():
    """Run all RCA integration usage examples."""
    print("Test RCA Integration Usage Examples")
    print("=" * 80)
    print("This script demonstrates various usage scenarios for RCA integration.")
    print("Each example shows different aspects of the system.\n")
    
    examples = [
        ("Basic RCA Usage", example_1_basic_rca_usage),
        ("Manual RCA Analysis", example_2_manual_rca_analysis),
        ("Batch Failure Analysis", example_3_batch_failure_analysis),
        ("Custom Report Generation", example_4_custom_report_generation),
        ("Performance Optimization", example_5_performance_optimization),
        ("Pattern Learning", example_6_pattern_learning),
        ("CI/CD Integration", example_7_ci_cd_integration),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ Example '{name}' failed: {e}")
            print(f"   This is expected in demo mode - actual implementation required")
            print()
    
    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)
    
    print("\nNext Steps:")
    print("1. Try running 'make test-with-rca' to see RCA in action")
    print("2. Use 'make rca' to analyze recent test failures")
    print("3. Check 'make rca-task TASK=specific_test' for focused analysis")
    print("4. Review generated reports in different formats")
    print("5. Explore pattern learning with repeated failure types")


if __name__ == "__main__":
    main()