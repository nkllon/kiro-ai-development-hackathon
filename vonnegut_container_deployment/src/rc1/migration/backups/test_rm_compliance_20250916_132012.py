#!/usr/bin/env python3
"""
Test RM compliance for Task Execution Engine
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from beast_mode.compliance.rm.rm_validator import RMValidator
from task_execution_engine import TaskExecutionEngine


def test_rm_compliance():
    """Test RM compliance of the Task Execution Engine"""
    print("🧪 Testing RM Compliance for Task Execution Engine")
    print("=" * 60)

    # Test 1: Check if TaskExecutionEngine implements ReflectiveModule
    print("\n1. Testing ReflectiveModule Implementation...")
    engine = TaskExecutionEngine()

    # Check required methods
    required_methods = ["get_module_status", "is_healthy", "get_health_indicators"]
    missing_methods = []

    for method in required_methods:
        if not hasattr(engine, method):
            missing_methods.append(method)

    if missing_methods:
        print(f"❌ Missing required RM methods: {missing_methods}")
        return False
    else:
        print("✅ All required RM methods implemented")

    # Test 2: Test method functionality
    print("\n2. Testing RM Method Functionality...")

    try:
        # Test get_module_status
        status = engine.get_module_status()
        if not isinstance(status, dict) or "module_name" not in status:
            print("❌ get_module_status() doesn't return proper dict")
            return False
        print(f"✅ get_module_status() returns: {status['module_name']}")

        # Test is_healthy
        healthy = engine.is_healthy()
        if not isinstance(healthy, bool):
            print("❌ is_healthy() doesn't return boolean")
            return False
        print(f"✅ is_healthy() returns: {healthy}")

        # Test get_health_indicators
        indicators = engine.get_health_indicators()
        if not isinstance(indicators, dict):
            print("❌ get_health_indicators() doesn't return dict")
            return False
        print(f"✅ get_health_indicators() returns {len(indicators)} indicators")

    except Exception as e:
        print(f"❌ Error testing RM methods: {e}")
        return False

    # Test 3: Use RM Validator to check compliance
    print("\n3. Running RM Validator...")

    try:
        validator = RMValidator()
        result = validator.validate_rm_compliance("task-execution-engine.py")

        print(f"Interface Implemented: {result.interface_implemented}")
        print(f"Size Constraints Met: {result.size_constraints_met}")
        print(f"Health Monitoring Present: {result.health_monitoring_present}")
        print(f"Registry Integrated: {result.registry_integrated}")
        print(f"Overall Compliance Score: {result.compliance_score:.2f}")

        if result.issues:
            print(f"\n⚠️  Found {len(result.issues)} compliance issues:")
            for issue in result.issues[:3]:  # Show first 3 issues
                print(f"  - {issue.severity.value}: {issue.description}")

        if result.compliance_score >= 0.8:
            print("✅ RM compliance score acceptable (≥0.8)")
        else:
            print(f"❌ RM compliance score too low: {result.compliance_score:.2f}")
            return False

    except Exception as e:
        print(f"❌ Error running RM validator: {e}")
        return False

    print("\n✅ RM Compliance Test Completed Successfully!")
    print("\nTask Execution Engine now implements:")
    print("- ReflectiveModule interface")
    print("- Health monitoring with indicators")
    print("- Module status reporting")
    print("- Single responsibility principle")

    return True


if __name__ == "__main__":
    success = test_rm_compliance()
    sys.exit(0 if success else 1)
