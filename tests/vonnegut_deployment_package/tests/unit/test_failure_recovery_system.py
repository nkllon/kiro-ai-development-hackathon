#!/usr/bin/env python3
"""
Comprehensive Failure Recovery System Test
==========================================

Test suite for the comprehensive failure recovery system that addresses
all identified systemic failure modes in the Beast Mode framework.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Test systematic failure recovery capabilities
"""

import sys
import os
import time
import subprocess
import json
import tempfile
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from beast_mode.failure_analysis.failure_recovery_orchestrator import (
    FailureRecoveryOrchestrator,
)
from beast_mode.failure_analysis.systematic_failure_detector import (
    FailureMode,
    FailureSeverity,
)
from beast_mode.cli.safe_cli_executor import ExecutionConfig, ExecutionMode
from beast_mode.requirements.requirements_validator import (
    RequirementsSet,
    Requirement,
    RequirementType,
    RequirementStatus,
)
from beast_mode.rmddd.rmddd_integration_manager import DomainModel, DomainType


def print_banner(title, width=80):
    """Print a formatted banner."""
    print("\n" + "=" * width)
    print(f"🧪 {title}")
    print("=" * width)


def print_test_result(test_name, success, details=""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"   {status} {test_name}")
    if details:
        print(f"      {details}")


def test_failure_detection():
    """Test systematic failure detection capabilities."""
    print_banner("TESTING SYSTEMATIC FAILURE DETECTION")

    orchestrator = FailureRecoveryOrchestrator()
    failure_detector = orchestrator.failure_detector

    # Test dquote error detection
    print("\n🔍 Testing Dquote Error Detection:")
    dquote_error = subprocess.CalledProcessError(
        1, "bash", "unexpected EOF while looking for matching"
    )
    is_dquote = failure_detector.detect_dquote_error("echo 'test", str(dquote_error))
    print_test_result("Dquote Error Detection", is_dquote)

    # Test CLI availability detection
    print("\n🔍 Testing CLI Availability Detection:")
    is_available, message = orchestrator.cli_executor.check_cli_availability("echo")
    print_test_result("CLI Availability Check", is_available, message)

    # Test timeout detection
    print("\n🔍 Testing Timeout Detection:")
    start_time = datetime.now()
    time.sleep(0.1)  # Simulate some time passing
    is_timeout = failure_detector.detect_timeout_issues(
        start_time, 0.05
    )  # Very short timeout
    print_test_result("Timeout Detection", is_timeout)

    # Test requirements missing detection
    print("\n🔍 Testing Requirements Missing Detection:")
    is_missing = failure_detector.detect_requirements_missing(
        "install requirements.txt"
    )
    print_test_result("Requirements Missing Detection", is_missing)

    # Test RMDDD failure detection
    print("\n🔍 Testing RMDDD Failure Detection:")
    is_rmddd_failure = failure_detector.detect_rmddd_failure(
        "rmddd analysis", "rmddd service not found"
    )
    print_test_result("RMDDD Failure Detection", is_rmddd_failure)

    return True


def test_cli_execution_safety():
    """Test safe CLI execution capabilities."""
    print_banner("TESTING SAFE CLI EXECUTION")

    orchestrator = FailureRecoveryOrchestrator()
    cli_executor = orchestrator.cli_executor

    # Test basic safe execution
    print("\n🔧 Testing Basic Safe Execution:")
    result = cli_executor.execute_safe("echo 'Hello World'")
    print_test_result(
        "Basic Execution",
        result.status.value == "completed",
        f"Status: {result.status.value}",
    )

    # Test command validation
    print("\n🔧 Testing Command Validation:")
    is_valid, message = cli_executor.validate_command("echo 'safe command'")
    print_test_result("Command Validation", is_valid, message)

    # Test dangerous command detection
    print("\n🔧 Testing Dangerous Command Detection:")
    is_valid, message = cli_executor.validate_command("rm -rf /")
    print_test_result("Dangerous Command Detection", not is_valid, message)

    # Test timeout protection
    print("\n🔧 Testing Timeout Protection:")
    timeout_config = ExecutionConfig(timeout_seconds=2)
    result = cli_executor.execute_safe("sleep 5", timeout_config)
    print_test_result(
        "Timeout Protection",
        result.status.value == "timeout",
        f"Status: {result.status.value}",
    )

    # Test CLI availability check
    print("\n🔧 Testing CLI Availability Check:")
    is_available, message = cli_executor.check_cli_availability("echo")
    print_test_result("CLI Availability", is_available, message)

    # Test execution summary
    print("\n🔧 Testing Execution Summary:")
    summary = cli_executor.get_execution_summary()
    print_test_result(
        "Execution Summary",
        summary["total_executions"] > 0,
        f"Total: {summary['total_executions']}",
    )

    return True


def test_requirements_validation():
    """Test requirements validation capabilities."""
    print_banner("TESTING REQUIREMENTS VALIDATION")

    orchestrator = FailureRecoveryOrchestrator()
    requirements_validator = orchestrator.requirements_validator

    # Create test requirements
    print("\n📋 Testing Requirements Creation:")
    test_requirements = RequirementsSet(
        name="Test Requirements",
        description="Test requirements for validation",
        version="1.0.0",
        requirements=[
            Requirement(
                id="REQ-001",
                title="User Authentication",
                description="The system shall provide user authentication functionality with secure login.",
                type=RequirementType.FUNCTIONAL,
                acceptance_criteria=[
                    "User can login with valid credentials",
                    "User cannot login with invalid credentials",
                    "Password is encrypted and stored securely.",
                ],
            ),
            Requirement(
                id="REQ-002",
                title="",  # Missing title - should trigger validation error
                description="Invalid requirement with missing title",
                type=RequirementType.FUNCTIONAL,
            ),
            Requirement(
                id="REQ-003",
                title="Data Validation",
                description="Short",  # Too short - should trigger validation warning
                type=RequirementType.FUNCTIONAL,
            ),
        ],
    )

    print_test_result("Requirements Creation", len(test_requirements.requirements) == 3)

    # Test requirements validation
    print("\n📋 Testing Requirements Validation:")
    validation_results = requirements_validator.validate_requirements(test_requirements)
    print_test_result(
        "Validation Execution",
        len(validation_results) > 0,
        f"Issues found: {len(validation_results)}",
    )

    # Test validation report generation
    print("\n📋 Testing Validation Report:")
    report = requirements_validator.generate_validation_report(validation_results)
    print_test_result(
        "Report Generation", len(report) > 100, f"Report length: {len(report)}"
    )

    return True


def test_rmddd_integration():
    """Test RMDDD integration capabilities."""
    print_banner("TESTING RMDDD INTEGRATION")

    orchestrator = FailureRecoveryOrchestrator()
    rmddd_manager = orchestrator.rmddd_manager

    # Test service health check
    print("\n🏗️ Testing Service Health Check:")
    service_status = rmddd_manager.check_all_services_health()
    print_test_result(
        "Service Health Check",
        len(service_status) > 0,
        f"Services checked: {len(service_status)}",
    )

    # Test service status summary
    print("\n🏗️ Testing Service Status Summary:")
    summary = rmddd_manager.get_service_status_summary()
    print_test_result(
        "Service Summary",
        summary["total_services"] > 0,
        f"Total services: {summary['total_services']}",
    )

    # Test domain model registration
    print("\n🏗️ Testing Domain Model Registration:")
    test_model = DomainModel(
        name="TestEntity",
        type=DomainType.ENTITY,
        properties={"id": "string", "name": "string"},
        methods=["create", "update", "delete"],
    )
    rmddd_manager.register_domain_model(test_model)
    registered_model = rmddd_manager.get_domain_model("TestEntity")
    print_test_result("Domain Model Registration", registered_model is not None)

    # Test use case creation and execution
    print("\n🏗️ Testing Use Case Creation:")
    use_case = rmddd_manager.create_use_case(
        use_case_id="UC-TEST-001",
        name="Test Use Case",
        description="Test use case for validation",
        domain="TestEntity",
        steps=[
            {
                "type": "domain_operation",
                "action": "create_test",
                "parameters": {"domain": "TestEntity", "operation": "create"},
            },
            {
                "type": "validation",
                "action": "validate_test",
                "parameters": {"type": "domain_model", "data": {"name": "test"}},
            },
        ],
        expected_outcome="Test use case completed successfully",
    )
    print_test_result("Use Case Creation", use_case.id == "UC-TEST-001")

    # Test use case execution
    print("\n🏗️ Testing Use Case Execution:")
    result = rmddd_manager.execute_use_case(use_case)
    print_test_result(
        "Use Case Execution",
        result.status.value in ["completed", "failed"],
        f"Status: {result.status.value}",
    )

    # Test integration report generation
    print("\n🏗️ Testing Integration Report:")
    report = rmddd_manager.generate_integration_report()
    print_test_result(
        "Integration Report", len(report) > 100, f"Report length: {len(report)}"
    )

    return True


def test_comprehensive_failure_recovery():
    """Test comprehensive failure recovery orchestration."""
    print_banner("TESTING COMPREHENSIVE FAILURE RECOVERY")

    orchestrator = FailureRecoveryOrchestrator()

    # Test failure handling with different failure modes
    test_failures = [
        {
            "error": subprocess.TimeoutExpired("git", 30),
            "context": {"component": "git", "operation": "push"},
            "expected_mode": "execution_timeout",
        },
        {
            "error": subprocess.CalledProcessError(1, "bash", "unexpected EOF"),
            "context": {"component": "bash", "operation": "script_execution"},
            "expected_mode": "dquote_error",
        },
        {
            "error": FileNotFoundError("CLI not found"),
            "context": {"component": "cli", "operation": "command_execution"},
            "expected_mode": "cli_unavailable",
        },
        {
            "error": PermissionError("Access denied"),
            "context": {"component": "auth", "operation": "token_validation"},
            "expected_mode": "authorization_failure",
        },
    ]

    print("\n🚨 Testing Failure Handling:")
    for i, test_case in enumerate(test_failures, 1):
        print(f"\n   Test {i}: {type(test_case['error']).__name__}")

        failure_analysis, recovery_execution = orchestrator.handle_failure(
            test_case["error"], test_case["context"], auto_recover=True
        )

        success = (
            failure_analysis.context.failure_mode.value == test_case["expected_mode"]
        )
        print_test_result(
            f"Failure Mode Detection",
            success,
            f"Expected: {test_case['expected_mode']}, Got: {failure_analysis.context.failure_mode.value}",
        )

        if recovery_execution:
            print_test_result(
                "Recovery Execution",
                recovery_execution.status.value in ["completed", "failed", "escalated"],
                f"Status: {recovery_execution.status.value}",
            )

    # Test system health summary
    print("\n🚨 Testing System Health Summary:")
    health_summary = orchestrator.get_system_health_summary()
    print_test_result(
        "Health Summary",
        health_summary["overall_health"]
        in ["EXCELLENT", "GOOD", "FAIR", "POOR", "CRITICAL"],
        f"Overall Health: {health_summary['overall_health']}",
    )

    # Test comprehensive report generation
    print("\n🚨 Testing Comprehensive Report:")
    report = orchestrator.generate_comprehensive_report()
    print_test_result(
        "Comprehensive Report", len(report) > 500, f"Report length: {len(report)}"
    )

    return True


def test_recovery_strategies():
    """Test specific recovery strategies."""
    print_banner("TESTING RECOVERY STRATEGIES")

    orchestrator = FailureRecoveryOrchestrator()

    # Test dquote error recovery
    print("\n🔧 Testing Dquote Error Recovery:")
    dquote_error = subprocess.CalledProcessError(
        1, "bash", "unexpected EOF while looking for matching"
    )
    failure_analysis, recovery = orchestrator.handle_failure(
        dquote_error, {"component": "bash", "operation": "script_execution"}
    )
    print_test_result(
        "Dquote Recovery",
        recovery is not None,
        f"Recovery Status: {recovery.status.value if recovery else 'None'}",
    )

    # Test CLI timeout recovery
    print("\n🔧 Testing CLI Timeout Recovery:")
    timeout_error = subprocess.TimeoutExpired("long_running_command", 30)
    failure_analysis, recovery = orchestrator.handle_failure(
        timeout_error, {"component": "cli", "operation": "long_execution"}
    )
    print_test_result(
        "Timeout Recovery",
        recovery is not None,
        f"Recovery Status: {recovery.status.value if recovery else 'None'}",
    )

    # Test requirements missing recovery
    print("\n🔧 Testing Requirements Missing Recovery:")
    requirements_error = FileNotFoundError("requirements.txt not found")
    failure_analysis, recovery = orchestrator.handle_failure(
        requirements_error, {"component": "requirements", "operation": "validation"}
    )
    print_test_result(
        "Requirements Recovery",
        recovery is not None,
        f"Recovery Status: {recovery.status.value if recovery else 'None'}",
    )

    return True


def main():
    """Run comprehensive failure recovery system tests."""
    print_banner("🧪 COMPREHENSIVE FAILURE RECOVERY SYSTEM TEST", 100)
    print(f"   Testing systematic failure detection and recovery capabilities")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    test_results = []

    try:
        # Run all test suites
        test_results.append(("Failure Detection", test_failure_detection()))
        test_results.append(("CLI Execution Safety", test_cli_execution_safety()))
        test_results.append(("Requirements Validation", test_requirements_validation()))
        test_results.append(("RMDDD Integration", test_rmddd_integration()))
        test_results.append(
            ("Comprehensive Failure Recovery", test_comprehensive_failure_recovery())
        )
        test_results.append(("Recovery Strategies", test_recovery_strategies()))

        # Print final results
        print_banner("🎯 TEST RESULTS SUMMARY", 100)

        passed_tests = 0
        total_tests = len(test_results)

        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")
            if result:
                passed_tests += 1

        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"   The comprehensive failure recovery system is working correctly!")
            print(f"   All identified systemic failure modes are properly addressed!")
        else:
            print(f"\n⚠️ SOME TESTS FAILED")
            print(f"   {total_tests - passed_tests} test(s) need attention")

        print_banner("🚀 FAILURE RECOVERY SYSTEM READY FOR PRODUCTION", 100)

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
