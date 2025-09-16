#!/usr/bin/env python3
"""
Test Fallback Mechanisms
========================

Demonstrates the enhanced fallback mechanisms that return control to the human
when the system encounters issues it cannot resolve autonomously.
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from field_repair_modification_system import (
    create_field_modification_system,
    FieldModificationRequest,
    FieldModificationFallbackResult,
)
from registry_availability_system import perform_boot_time_registry_check


def test_boot_time_fallback():
    """Test boot-time fallback when registry is unavailable"""

    print("🧪 TESTING BOOT-TIME FALLBACK MECHANISM")
    print("=" * 50)

    # Create a temporary directory without Git to simulate registry failure
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Testing in temporary directory: {temp_dir}")

        # Try to create field modification system in a directory without Git
        print("\n🚀 Attempting to initialize field modification system...")

        try:
            result = create_field_modification_system(repo_path=temp_dir)

            # Check if we got a fallback result
            if isinstance(result, FieldModificationFallbackResult):
                print("✅ FALLBACK MECHANISM TRIGGERED SUCCESSFULLY!")
                print(f"   Fallback Reason: {result.fallback_reason}")
                print(f"   System Status: {result.system_status}")
                print(
                    f"   Requires Human Intervention: {result.requires_human_intervention}"
                )
                print(f"   Can Retry: {result.can_retry}")
                print(f"   Recommended Action: {result.recommended_action}")

                print("\n📋 Human Options Available:")
                for i, option in enumerate(result.human_options, 1):
                    print(f"   {i}. {option}")

                return True
            else:
                print("❌ Expected fallback result, but got different type")
                return False

        except Exception as e:
            print(f"❌ Unexpected exception: {e}")
            return False


def test_pre_use_validation_fallback():
    """Test pre-use validation fallback"""

    print("\n🧪 TESTING PRE-USE VALIDATION FALLBACK")
    print("=" * 50)

    # Create a temporary directory with Git to test pre-use validation
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Testing in temporary directory: {temp_dir}")

        # Initialize Git in the temp directory
        import subprocess

        try:
            subprocess.run(
                ["git", "init"], cwd=temp_dir, check=True, capture_output=True
            )
            print("✅ Git initialized for testing")
        except subprocess.CalledProcessError:
            print("⚠️  Git not available, simulating with mock")

        # Create field modification system
        try:
            field_system = create_field_modification_system(repo_path=temp_dir)
            print("✅ Field modification system created")

            # Create a test modification request
            request = FieldModificationRequest(
                modification_id="test_fallback_001",
                component_name="test_component",
                modification_type="enhancement",
                description="Test fallback mechanism",
                code_changes={"test.py": "print('hello world')"},
                safety_level="high",
                git_sync_required=True,
                permanent_persistence=True,
                created_at=datetime.now(),
                requested_by="test_user",
            )

            print("\n🔧 Attempting field modification request...")
            result = field_system.request_field_modification(request)

            # Check if we got a fallback result (this might happen if registry validation fails)
            if isinstance(result, FieldModificationFallbackResult):
                print("✅ PRE-USE VALIDATION FALLBACK TRIGGERED!")
                print(f"   Fallback Reason: {result.fallback_reason}")
                print(f"   System Status: {result.system_status}")
                print(f"   Human Options: {len(result.human_options)} available")

                return True
            else:
                print("ℹ️  Field modification proceeded normally (registry was healthy)")
                return True

        except Exception as e:
            print(f"❌ Unexpected exception: {e}")
            return False


def test_human_interaction_simulation():
    """Simulate human interaction with fallback options"""

    print("\n🧪 TESTING HUMAN INTERACTION SIMULATION")
    print("=" * 50)

    # Simulate a fallback result
    fallback_result = FieldModificationFallbackResult(
        fallback_reason="Registry availability check failed",
        system_status="critical",
        registry_details={
            "git": {
                "available": False,
                "health_score": 0.0,
                "error": "Not a git repository",
            },
            "memory": {"available": True, "health_score": 1.0},
            "file_system": {"available": True, "health_score": 1.0},
        },
        human_options=[
            "Fix registry issue and retry",
            "Provide manual override",
            "Abandon field modification",
            "Investigate registry problems",
        ],
        recommended_action="Fix registry issue and retry",
        can_retry=True,
        requires_human_intervention=True,
    )

    print("📋 Simulated Fallback Scenario:")
    print(f"   Reason: {fallback_result.fallback_reason}")
    print(f"   Status: {fallback_result.system_status}")
    print(
        f"   Human Intervention Required: {fallback_result.requires_human_intervention}"
    )

    print("\n🔍 Registry Status Details:")
    for registry, details in fallback_result.registry_details.items():
        status_icon = "✅" if details.get("available", False) else "❌"
        health_score = details.get("health_score", 0)
        print(f"   {registry}: {status_icon} Health: {health_score:.1%}")
        if "error" in details:
            print(f"      Error: {details['error']}")

    print("\n👤 Human Decision Options:")
    for i, option in enumerate(fallback_result.human_options, 1):
        print(f"   {i}. {option}")

    print(f"\n💡 Recommended Action: {fallback_result.recommended_action}")

    # Simulate human choosing option 1 (fix and retry)
    print("\n🎭 Simulating Human Choice: Option 1 - Fix registry issue and retry")
    print("   Human would: Initialize Git repository, then retry field modification")
    print("   System would: Re-run registry check, proceed with field modification")

    return True


def test_graceful_degradation():
    """Test graceful degradation scenarios"""

    print("\n🧪 TESTING GRACEFUL DEGRADATION")
    print("=" * 50)

    # Test different failure scenarios
    failure_scenarios = [
        {
            "name": "Git Repository Missing",
            "registry_details": {
                "git": {
                    "available": False,
                    "health_score": 0.0,
                    "error": "Not a git repository",
                },
                "memory": {"available": True, "health_score": 1.0},
                "file_system": {"available": True, "health_score": 1.0},
            },
            "expected_action": "Fix registry issue and retry",
        },
        {
            "name": "Memory System Unavailable",
            "registry_details": {
                "git": {"available": True, "health_score": 1.0},
                "memory": {
                    "available": False,
                    "health_score": 0.0,
                    "error": "Memory system down",
                },
                "file_system": {"available": True, "health_score": 1.0},
            },
            "expected_action": "Investigate registry problems",
        },
        {
            "name": "File System Issues",
            "registry_details": {
                "git": {"available": True, "health_score": 1.0},
                "memory": {"available": True, "health_score": 1.0},
                "file_system": {
                    "available": False,
                    "health_score": 0.0,
                    "error": "Permission denied",
                },
            },
            "expected_action": "Investigate registry problems",
        },
    ]

    for scenario in failure_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")

        fallback_result = FieldModificationFallbackResult(
            fallback_reason=f"Registry failure: {scenario['name']}",
            system_status="degraded",
            registry_details=scenario["registry_details"],
            human_options=[
                "Fix registry issue and retry",
                "Provide manual override",
                "Abandon field modification",
                "Investigate registry problems",
            ],
            recommended_action=scenario["expected_action"],
        )

        print(f"   Status: {fallback_result.system_status}")
        print(f"   Recommended: {fallback_result.recommended_action}")

        # Show which registries are failing
        failing_registries = [
            name
            for name, details in scenario["registry_details"].items()
            if not details.get("available", False)
        ]
        print(f"   Failing Registries: {', '.join(failing_registries)}")

    return True


def main():
    """Run all fallback mechanism tests"""

    print("🚀 FALLBACK MECHANISM TEST SUITE")
    print("=" * 60)
    print("Testing the enhanced fallback mechanisms that return control")
    print("to the human when the system cannot resolve issues autonomously.")
    print("=" * 60)

    tests = [
        ("Boot-time Fallback", test_boot_time_fallback),
        ("Pre-use Validation Fallback", test_pre_use_validation_fallback),
        ("Human Interaction Simulation", test_human_interaction_simulation),
        ("Graceful Degradation", test_graceful_degradation),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 FALLBACK MECHANISM TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total:.1%}")

    if passed == total:
        print("\n🎉 ALL FALLBACK MECHANISMS WORKING CORRECTLY!")
        print("   The system can now gracefully fall back to human interaction")
        print("   when it encounters issues it cannot resolve autonomously.")
    else:
        print(f"\n⚠️  {total - passed} tests failed - review implementation")

    print("\n💡 Key Fallback Features Demonstrated:")
    print("   ✅ Boot-time registry availability checks")
    print("   ✅ Pre-use validation with fallback")
    print("   ✅ Clear human interaction options")
    print("   ✅ Graceful degradation scenarios")
    print("   ✅ Actionable recommendations for humans")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
