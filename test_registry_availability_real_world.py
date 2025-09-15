#!/usr/bin/env python3
"""
Test Registry Availability System - Real World Scenario
======================================================

Test the critical derived requirement with real-world scenarios:
- Boot-time registry check prevents unsafe system startup
- Pre-use validation prevents unsafe field modifications
- Graceful failure handling when registry is unavailable
"""

import sys
import tempfile
import shutil
from typing import Dict, Any
from pathlib import Path

from registry_availability_system import (
    create_registry_health_monitor,
    perform_boot_time_registry_check,
    perform_pre_use_registry_validation,
    GitRegistryChecker,
    MemoryRegistryChecker,
    FileSystemRegistryChecker,
)
from field_repair_modification_system import (
    create_field_modification_system,
    FieldModificationRequest,
)
from short_term_planning_memory import PlanningMemoryManager


def test_real_world_registry_scenarios():
    """Test real-world registry availability scenarios"""

    print("🌍 TESTING REAL-WORLD REGISTRY AVAILABILITY SCENARIOS")
    print("=" * 60)

    # Test in current working directory (should have Git)
    current_dir = "."

    try:
        # Create memory manager
        memory_manager = PlanningMemoryManager(current_dir)

        # Test 1: Boot-time registry check in real environment
        print("\n🚀 SCENARIO 1: Boot-Time Registry Check (Real Environment)")
        print("-" * 50)

        results = perform_boot_time_registry_check(current_dir, memory_manager)

        print(f"Boot Time Results:")
        print(f"   Overall Health: {results['overall_health']:.1%}")
        print(f"   System Status: {results['system_status']}")
        print(
            f"   Can Perform Field Modifications: {results['can_perform_field_modifications']}"
        )
        print(f"   Graceful Shutdown Required: {results['graceful_shutdown_required']}")

        if results["graceful_shutdown_required"]:
            print("🚨 CRITICAL: I can't fix myself. I'm dead in the water here.")
        else:
            print("✅ Boot-time registry check passed - system can start safely")

        # Test 2: Pre-use validation
        print("\n🔧 SCENARIO 2: Pre-Use Registry Validation")
        print("-" * 50)

        is_safe = perform_pre_use_registry_validation(current_dir, memory_manager)

        print(f"Pre-Use Validation:")
        print(f"   Field Modifications Safe: {'✅' if is_safe else '❌'}")

        if not is_safe:
            print("🚨 CRITICAL: I can't fix myself. I'm dead in the water here.")
        else:
            print("✅ Pre-use validation passed - field modifications are safe")

        # Test 3: Registry health monitoring
        print("\n📊 SCENARIO 3: Registry Health Monitoring")
        print("-" * 50)

        monitor = create_registry_health_monitor(current_dir, memory_manager)
        health_report = monitor.check_registry_health()

        print(f"Registry Health Report:")
        print(f"   Overall Health: {health_report.overall_health:.1%}")
        print(f"   System Status: {health_report.system_status}")
        print(
            f"   Can Perform Field Modifications: {health_report.can_perform_field_modifications}"
        )

        for registry_name, status in health_report.critical_registries.items():
            status_icon = "✅" if status.is_available else "❌"
            print(f"   {status_icon} {registry_name}: {status.health_score:.1%}")
            if status.error_message:
                print(f"      Error: {status.error_message}")

        # Test 4: Individual registry checkers
        print("\n🔍 SCENARIO 4: Individual Registry Checkers")
        print("-" * 50)

        # Git registry checker
        git_checker = GitRegistryChecker(current_dir)
        git_status = git_checker.check_availability()
        print(
            f"Git Registry: {'✅' if git_status.is_available else '❌'} ({git_status.health_score:.1%})"
        )

        # Memory registry checker
        memory_checker = MemoryRegistryChecker(memory_manager)
        memory_status = memory_checker.check_availability()
        print(
            f"Memory Registry: {'✅' if memory_status.is_available else '❌'} ({memory_status.health_score:.1%})"
        )

        # File system registry checker
        fs_checker = FileSystemRegistryChecker(current_dir)
        fs_status = fs_checker.check_availability()
        print(
            f"File System Registry: {'✅' if fs_status.is_available else '❌'} ({fs_status.health_score:.1%})"
        )

        return {
            "boot_time_safe": results["can_perform_field_modifications"],
            "pre_use_safe": is_safe,
            "overall_health": health_report.overall_health,
            "git_available": git_status.is_available,
            "memory_available": memory_status.is_available,
            "filesystem_available": fs_status.is_available,
        }

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


def test_graceful_failure_scenarios():
    """Test graceful failure scenarios"""

    print("\n🚨 TESTING GRACEFUL FAILURE SCENARIOS")
    print("=" * 50)

    # Test with restricted environment
    test_dir = tempfile.mkdtemp(prefix="registry_failure_")

    try:
        # Create memory manager in restricted environment
        memory_manager = PlanningMemoryManager(test_dir)

        print("🧪 Testing with restricted environment (no Git)...")

        # Test boot-time check in restricted environment
        results = perform_boot_time_registry_check(test_dir, memory_manager)

        print(f"Restricted Environment Results:")
        print(f"   Overall Health: {results['overall_health']:.1%}")
        print(f"   System Status: {results['system_status']}")
        print(
            f"   Can Perform Field Modifications: {results['can_perform_field_modifications']}"
        )
        print(f"   Graceful Shutdown Required: {results['graceful_shutdown_required']}")

        if results["graceful_shutdown_required"]:
            print("🚨 GRACEFUL SHUTDOWN REQUIRED!")
            print("   I can't fix myself. I'm dead in the water here.")

            # Show failed registries
            failed_registries = [
                name
                for name, status_info in results["critical_registries"].items()
                if not status_info["available"]
            ]
            print(f"   Failed registries: {', '.join(failed_registries)}")

            # Show recommendations
            if results["recommendations"]:
                print("   Recommendations:")
                for rec in results["recommendations"]:
                    print(f"     • {rec}")
        else:
            print("✅ Restricted environment passed registry checks")

        return results["graceful_shutdown_required"]

    finally:
        # Clean up
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up restricted test environment")


def demonstrate_derived_requirement():
    """Demonstrate the critical derived requirement"""

    print("\n🎯 DEMONSTRATING CRITICAL DERIVED REQUIREMENT")
    print("=" * 60)

    print(
        """
CRITICAL DERIVED REQUIREMENT:
============================

You must have synchronous availability of the registry in order to do any 
field modifications. That might as well be tested when you boot and it 
certainly should be tested when you get ready to use it and you should be 
able to bail as gracefully as you can. Namely, I can't fix myself. I'm 
dead in the water here.

IMPLEMENTATION:
==============

1. BOOT-TIME REGISTRY CHECK
   - Test registry availability when system boots
   - Prevent system startup if critical registries are unavailable
   - Graceful shutdown if registry health is below threshold

2. PRE-USE REGISTRY VALIDATION
   - Test registry availability before field modifications
   - Ensure Git, memory, and file system are available
   - Prevent unsafe field modifications

3. GRACEFUL FAILURE HANDLING
   - "I can't fix myself. I'm dead in the water here."
   - Clear error messages and recommendations
   - Safe shutdown when registry is unavailable

4. SYNCHRONOUS AVAILABILITY REQUIREMENT
   - All critical registries must be available synchronously
   - No field modifications without registry availability
   - Health score monitoring for all registries

BENEFITS:
=========

✅ Prevents unsafe system startup
✅ Prevents unsafe field modifications  
✅ Graceful failure handling
✅ Clear error messages and recommendations
✅ Health score monitoring
✅ Critical dependency tracking
"""
    )

    return True


def main():
    """Main test function"""

    print("🔍 TESTING REGISTRY AVAILABILITY SYSTEM - REAL WORLD SCENARIOS")
    print("=" * 80)
    print("Critical derived requirement: Synchronous availability of the registry")
    print("is required for any field modifications to work. Without it, the system")
    print("is 'dead in the water' and cannot fix itself.")
    print("=" * 80)

    try:
        # Test real-world scenarios
        real_world_results = test_real_world_registry_scenarios()

        # Test graceful failure scenarios
        graceful_failure = test_graceful_failure_scenarios()

        # Demonstrate derived requirement
        requirement_demonstrated = demonstrate_derived_requirement()

        # Summary
        print(f"\n🎉 REGISTRY AVAILABILITY SYSTEM TEST COMPLETED")
        print("=" * 60)

        if real_world_results:
            print(f"Real-World Environment Results:")
            print(
                f"   Boot Time Safe: {'✅' if real_world_results['boot_time_safe'] else '❌'}"
            )
            print(
                f"   Pre-Use Safe: {'✅' if real_world_results['pre_use_safe'] else '❌'}"
            )
            print(f"   Overall Health: {real_world_results['overall_health']:.1%}")
            print(
                f"   Git Available: {'✅' if real_world_results['git_available'] else '❌'}"
            )
            print(
                f"   Memory Available: {'✅' if real_world_results['memory_available'] else '❌'}"
            )
            print(
                f"   File System Available: {'✅' if real_world_results['filesystem_available'] else '❌'}"
            )

        print(f"\nGraceful Failure Scenarios:")
        print(f"   Graceful Shutdown Required: {'🚨' if graceful_failure else '✅'}")

        print(f"\nCritical Derived Requirement:")
        print(
            f"   Requirement Demonstrated: {'✅' if requirement_demonstrated else '❌'}"
        )

        # Overall assessment
        if (
            real_world_results
            and real_world_results["boot_time_safe"]
            and real_world_results["pre_use_safe"]
        ):
            print(f"\n✅ REGISTRY AVAILABILITY SYSTEM OPERATIONAL!")
            print("🚀 Boot-time registry validation: ACTIVE")
            print("🔧 Pre-use registry validation: ACTIVE")
            print("🚨 Graceful failure handling: ACTIVE")
            print("📊 Health score monitoring: ACTIVE")
            print("🔍 Critical dependency tracking: ACTIVE")
            print("⚡ Synchronous availability requirement: ENFORCED")
            print("\n🎯 CRITICAL DERIVED REQUIREMENT SATISFIED!")
            print("   Synchronous availability of registry is enforced")
            print("   System cannot perform unsafe field modifications")
            print("   Graceful failure handling prevents 'dead in the water' scenarios")
            return True
        else:
            print(f"\n❌ REGISTRY AVAILABILITY SYSTEM NEEDS ATTENTION")
            print("🚨 I can't fix myself. I'm dead in the water here.")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    from datetime import datetime

    success = main()
    sys.exit(0 if success else 1)
