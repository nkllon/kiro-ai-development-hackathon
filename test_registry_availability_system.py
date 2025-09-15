#!/usr/bin/env python3
"""
Test Registry Availability System
=================================

Test the critical derived requirement: Synchronous availability of the registry
is required for any field modifications to work. Without it, the system is
"dead in the water" and cannot fix itself.
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


def create_test_environment():
    """Create a test environment for registry availability testing"""

    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="registry_availability_test_")
    test_path = Path(test_dir)

    # Create a simple test file
    test_file = test_path / "test_component.py"
    test_file.write_text(
        '''
#!/usr/bin/env python3
"""
Test Component for Registry Availability Testing
===============================================
"""

def test_function():
    """Test function for registry availability"""
    return "Registry availability test"
'''
    )

    print(f"🧪 Created test environment: {test_dir}")
    return test_dir, test_path


def test_git_registry_checker():
    """Test Git registry availability checker"""

    print("🔍 TESTING GIT REGISTRY CHECKER")
    print("=" * 40)

    # Create test environment
    test_dir, test_path = create_test_environment()

    try:
        # Create Git registry checker
        git_checker = GitRegistryChecker(str(test_path))

        # Check availability
        status = git_checker.check_availability()

        print(f"Git Registry Status:")
        print(f"   Available: {'✅' if status.is_available else '❌'}")
        print(f"   Health Score: {status.health_score:.1%}")
        print(f"   Response Time: {status.response_time_ms:.1f}ms")
        print(f"   Error Message: {status.error_message or 'None'}")
        print(f"   Failure Reason: {status.failure_reason or 'None'}")

        # Check critical dependencies
        dependencies = git_checker.get_critical_dependencies()
        print(f"   Critical Dependencies: {dependencies}")

        return status.is_available

    finally:
        # Clean up test environment
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test environment")


def test_memory_registry_checker():
    """Test memory registry availability checker"""

    print("\n🧠 TESTING MEMORY REGISTRY CHECKER")
    print("=" * 40)

    # Create test environment
    test_dir, test_path = create_test_environment()

    try:
        # Create memory manager
        memory_manager = PlanningMemoryManager(test_dir)

        # Create memory registry checker
        memory_checker = MemoryRegistryChecker(memory_manager)

        # Check availability
        status = memory_checker.check_availability()

        print(f"Memory Registry Status:")
        print(f"   Available: {'✅' if status.is_available else '❌'}")
        print(f"   Health Score: {status.health_score:.1%}")
        print(f"   Response Time: {status.response_time_ms:.1f}ms")
        print(f"   Error Message: {status.error_message or 'None'}")
        print(f"   Failure Reason: {status.failure_reason or 'None'}")

        # Check critical dependencies
        dependencies = memory_checker.get_critical_dependencies()
        print(f"   Critical Dependencies: {dependencies}")

        return status.is_available

    finally:
        # Clean up test environment
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test environment")


def test_file_system_registry_checker():
    """Test file system registry availability checker"""

    print("\n💾 TESTING FILE SYSTEM REGISTRY CHECKER")
    print("=" * 40)

    # Create test environment
    test_dir, test_path = create_test_environment()

    try:
        # Create file system registry checker
        fs_checker = FileSystemRegistryChecker(str(test_path))

        # Check availability
        status = fs_checker.check_availability()

        print(f"File System Registry Status:")
        print(f"   Available: {'✅' if status.is_available else '❌'}")
        print(f"   Health Score: {status.health_score:.1%}")
        print(f"   Response Time: {status.response_time_ms:.1f}ms")
        print(f"   Error Message: {status.error_message or 'None'}")
        print(f"   Failure Reason: {status.failure_reason or 'None'}")

        # Check critical dependencies
        dependencies = fs_checker.get_critical_dependencies()
        print(f"   Critical Dependencies: {dependencies}")

        return status.is_available

    finally:
        # Clean up test environment
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test environment")


def test_boot_time_registry_check():
    """Test boot-time registry availability check"""

    print("\n🚀 TESTING BOOT TIME REGISTRY CHECK")
    print("=" * 40)

    # Create test environment
    test_dir, test_path = create_test_environment()

    try:
        # Create memory manager
        memory_manager = PlanningMemoryManager(test_dir)

        # Perform boot-time registry check
        results = perform_boot_time_registry_check(test_dir, memory_manager)

        print(f"Boot Time Registry Check Results:")
        print(f"   Overall Health: {results['overall_health']:.1%}")
        print(f"   System Status: {results['system_status']}")
        print(
            f"   Can Perform Field Modifications: {results['can_perform_field_modifications']}"
        )
        print(f"   Graceful Shutdown Required: {results['graceful_shutdown_required']}")

        print(f"\nCritical Registries:")
        for registry_name, registry_info in results["critical_registries"].items():
            status_icon = "✅" if registry_info["available"] else "❌"
            print(
                f"   {status_icon} {registry_name}: {registry_info['health_score']:.1%}"
            )
            if registry_info["error_message"]:
                print(f"      Error: {registry_info['error_message']}")

        if results["recommendations"]:
            print(f"\nRecommendations:")
            for rec in results["recommendations"]:
                print(f"   • {rec}")

        return results["can_perform_field_modifications"]

    finally:
        # Clean up test environment
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test environment")


def test_pre_use_registry_validation():
    """Test pre-use registry validation"""

    print("\n🔧 TESTING PRE-USE REGISTRY VALIDATION")
    print("=" * 40)

    # Create test environment
    test_dir, test_path = create_test_environment()

    try:
        # Create memory manager
        memory_manager = PlanningMemoryManager(test_dir)

        # Perform pre-use registry validation
        is_safe = perform_pre_use_registry_validation(test_dir, memory_manager)

        print(f"Pre-Use Registry Validation:")
        print(f"   Field Modifications Safe: {'✅' if is_safe else '❌'}")

        if not is_safe:
            print("   I can't fix myself. I'm dead in the water here.")

        return is_safe

    finally:
        # Clean up test environment
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test environment")


def test_field_modification_with_registry_check():
    """Test field modification with registry availability check"""

    print("\n🔧 TESTING FIELD MODIFICATION WITH REGISTRY CHECK")
    print("=" * 50)

    # Create test environment
    test_dir, test_path = create_test_environment()

    try:
        # Create memory manager
        memory_manager = PlanningMemoryManager(test_dir)

        # Create field modification system (includes boot-time registry check)
        print("Creating field modification system...")
        field_system = create_field_modification_system(test_dir, memory_manager)

        # Create test file
        test_file = test_path / "test_component.py"

        # Create field modification request
        request = FieldModificationRequest(
            modification_id="registry_test_001",
            component_name="test_component",
            modification_type="enhancement",
            description="Test field modification with registry availability check",
            code_changes={
                str(
                    test_file
                ): '''
#!/usr/bin/env python3
"""
Test Component (Enhanced with Registry Check)
============================================
"""

def test_function():
    """Enhanced test function with registry availability check"""
    return "Registry availability verified - enhancement applied"

def new_registry_aware_function():
    """New function created with registry awareness"""
    return "Registry-aware functionality"
'''
            },
            safety_level="medium",
            git_sync_required=True,
            short_term_memory_impact=True,
            permanent_persistence=True,
            created_at=datetime.now(),
            requested_by="registry_test",
        )

        # Process the field modification request
        print("Processing field modification request...")
        result = field_system.request_field_modification(request)

        # Display results
        print(f"\nField Modification Results:")
        print(f"   Success: {'✅' if result.success else '❌'}")
        print(f"   Registry Check Passed: {'✅' if result.success else '❌'}")
        print(f"   Error Message: {result.error_message or 'None'}")

        if result.success:
            print(
                "✅ Field modification completed successfully with registry availability check"
            )
        else:
            print(
                "❌ Field modification failed - registry availability check prevented unsafe operation"
            )

        return result.success

    finally:
        # Clean up test environment
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test environment")


def test_graceful_shutdown_scenario():
    """Test graceful shutdown scenario when registry is unavailable"""

    print("\n🚨 TESTING GRACEFUL SHUTDOWN SCENARIO")
    print("=" * 40)

    # Create test environment with restricted permissions
    test_dir = tempfile.mkdtemp(prefix="registry_failure_test_")
    test_path = Path(test_dir)

    try:
        # Create memory manager
        memory_manager = PlanningMemoryManager(test_dir)

        # Create registry health monitor
        from registry_availability_system import create_registry_health_monitor

        monitor = create_registry_health_monitor(test_dir, memory_manager)

        # Check registry health
        health_report = monitor.check_registry_health()

        print(f"Registry Health Report:")
        print(f"   Overall Health: {health_report.overall_health:.1%}")
        print(f"   System Status: {health_report.system_status}")
        print(
            f"   Can Perform Field Modifications: {health_report.can_perform_field_modifications}"
        )
        print(
            f"   Graceful Shutdown Required: {health_report.graceful_shutdown_required}"
        )

        if health_report.graceful_shutdown_required:
            print(f"\n🚨 GRACEFUL SHUTDOWN REQUIRED!")
            print(f"   {monitor.get_graceful_shutdown_message()}")
            print("   I can't fix myself. I'm dead in the water here.")
        else:
            print(f"\n✅ Registry health is sufficient for field modifications")

        return health_report.graceful_shutdown_required

    finally:
        # Clean up test environment
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test environment")


def demonstrate_registry_availability_benefits():
    """Demonstrate the benefits of registry availability checking"""

    print("\n🌟 REGISTRY AVAILABILITY SYSTEM BENEFITS")
    print("=" * 60)

    benefits = [
        {
            "benefit": "Boot-Time Registry Validation",
            "description": "Check registry availability when system boots",
            "example": "Prevent system startup if critical registries are unavailable",
        },
        {
            "benefit": "Pre-Use Registry Validation",
            "description": "Validate registry availability before field modifications",
            "example": "Ensure Git, memory, and file system are available before making changes",
        },
        {
            "benefit": "Graceful Failure Handling",
            "description": "Graceful shutdown when registry is unavailable",
            "example": "I can't fix myself. I'm dead in the water here.",
        },
        {
            "benefit": "Critical Dependency Tracking",
            "description": "Track critical dependencies for each registry",
            "example": "Git registry requires git_executable, git_repository, remote_origin, etc.",
        },
        {
            "benefit": "Health Score Monitoring",
            "description": "Continuous health score monitoring for all registries",
            "example": "0.0 to 1.0 health score with detailed failure reasons",
        },
        {
            "benefit": "Synchronous Availability Requirement",
            "description": "Ensure synchronous availability before field modifications",
            "example": "Cannot perform field modifications without registry availability",
        },
    ]

    for i, benefit in enumerate(benefits, 1):
        print(f"\n{i}. {benefit['benefit']}")
        print(f"   {benefit['description']}")
        print(f"   Example: {benefit['example']}")

    print(f"\n🎯 KEY INSIGHT: Registry availability is a critical derived requirement!")
    print("   🚀 Boot-time validation prevents unsafe system startup")
    print("   🔧 Pre-use validation prevents unsafe field modifications")
    print("   🚨 Graceful shutdown when registry is unavailable")
    print("   📊 Health score monitoring for all critical registries")
    print("   🔍 Critical dependency tracking and validation")
    print("   ⚡ Synchronous availability requirement for field modifications")

    return benefits


def main():
    """Main test function"""

    print("🔍 TESTING REGISTRY AVAILABILITY SYSTEM")
    print("=" * 70)
    print("Critical derived requirement: Synchronous availability of the registry")
    print("is required for any field modifications to work. Without it, the system")
    print("is 'dead in the water' and cannot fix itself.")
    print("=" * 70)

    try:
        # Test individual registry checkers
        git_available = test_git_registry_checker()
        memory_available = test_memory_registry_checker()
        filesystem_available = test_file_system_registry_checker()

        # Test boot-time registry check
        boot_time_safe = test_boot_time_registry_check()

        # Test pre-use registry validation
        pre_use_safe = test_pre_use_registry_validation()

        # Test field modification with registry check
        field_mod_safe = test_field_modification_with_registry_check()

        # Test graceful shutdown scenario
        graceful_shutdown_required = test_graceful_shutdown_scenario()

        # Demonstrate benefits
        benefits = demonstrate_registry_availability_benefits()

        # Summary
        print(f"\n🎉 REGISTRY AVAILABILITY SYSTEM TEST COMPLETED")
        print("=" * 60)

        print(f"Individual Registry Checkers:")
        print(f"   Git Registry: {'✅' if git_available else '❌'}")
        print(f"   Memory Registry: {'✅' if memory_available else '❌'}")
        print(f"   File System Registry: {'✅' if filesystem_available else '❌'}")

        print(f"\nSystem-Level Checks:")
        print(f"   Boot Time Registry Check: {'✅' if boot_time_safe else '❌'}")
        print(f"   Pre-Use Registry Validation: {'✅' if pre_use_safe else '❌'}")
        print(
            f"   Field Modification with Registry Check: {'✅' if field_mod_safe else '❌'}"
        )
        print(
            f"   Graceful Shutdown Required: {'🚨' if graceful_shutdown_required else '✅'}"
        )

        overall_success = (
            git_available
            and memory_available
            and filesystem_available
            and boot_time_safe
            and pre_use_safe
            and field_mod_safe
            and not graceful_shutdown_required
        )

        if overall_success:
            print(f"\n✅ ALL REGISTRY AVAILABILITY SYSTEMS OPERATIONAL!")
            print("🚀 Boot-time registry validation: ACTIVE")
            print("🔧 Pre-use registry validation: ACTIVE")
            print("🚨 Graceful failure handling: ACTIVE")
            print("📊 Health score monitoring: ACTIVE")
            print("🔍 Critical dependency tracking: ACTIVE")
            print("⚡ Synchronous availability requirement: ENFORCED")
            return True
        else:
            print(f"\n❌ SOME REGISTRY AVAILABILITY SYSTEMS NEED ATTENTION")
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
