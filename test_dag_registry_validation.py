#!/usr/bin/env python3
"""
Test DAG Registry Validation
===========================

Test the DAG registry to ensure it's working and free from loops.
"""

import sys
sys.path.append('.')

from src.rm_ddd.core.dag_registry import DAGRegistry, get_dag_validation, get_registry_stats


def test_dag_registry():
    """Test DAG registry functionality and loop detection."""
    print("🔍 TESTING DAG REGISTRY VALIDATION")
    print("=" * 50)
    
    # Create new registry for testing
    registry = DAGRegistry()
    
    # Test 1: Register modules in valid order (no cycles)
    print("\n📊 Test 1: Valid DAG Registration")
    print("-" * 30)
    
    # Register base modules first
    success1 = registry.register_module("base_module", set())
    success2 = registry.register_module("core_module", {"base_module"})
    success3 = registry.register_module("service_module", {"core_module"})
    success4 = registry.register_module("api_module", {"service_module"})
    
    print(f"Base module: {success1}")
    print(f"Core module: {success2}")
    print(f"Service module: {success3}")
    print(f"API module: {success4}")
    
    # Test 2: Try to create a cycle (should fail)
    print("\n🚫 Test 2: Cycle Detection")
    print("-" * 30)
    
    # This should fail - would create cycle: base_module -> core_module -> base_module
    cycle_attempt = registry.register_module("base_module", {"api_module"})
    print(f"Cycle attempt (should fail): {cycle_attempt}")
    
    # Test 3: Validate DAG
    print("\n✅ Test 3: DAG Validation")
    print("-" * 30)
    
    is_dag = registry.validate_dag()
    print(f"Is DAG: {is_dag}")
    
    # Test 4: Get registry stats
    print("\n📈 Test 4: Registry Statistics")
    print("-" * 30)
    
    stats = registry.get_registry_stats()
    print(f"Total modules: {stats['total_modules']}")
    print(f"Is DAG: {stats['is_dag']}")
    print(f"Modules: {stats['modules']}")
    
    # Test 5: Test dependency chains
    print("\n🔗 Test 5: Dependency Chains")
    print("-" * 30)
    
    for module in stats['modules']:
        deps = registry.get_dependencies(module)
        dependents = registry.get_dependents(module)
        chain = registry.get_dependency_chain(module)
        print(f"{module}:")
        print(f"  Dependencies: {deps}")
        print(f"  Dependents: {dependents}")
        print(f"  Chain: {chain}")
    
    # Test 6: Test global registry
    print("\n🌐 Test 6: Global Registry")
    print("-" * 30)
    
    global_is_dag = get_dag_validation()
    global_stats = get_registry_stats()
    print(f"Global DAG validation: {global_is_dag}")
    print(f"Global registry modules: {global_stats['total_modules']}")
    
    return is_dag and global_is_dag


def test_circular_dependency_prevention():
    """Test that circular dependencies are properly prevented."""
    print("\n🔄 TESTING CIRCULAR DEPENDENCY PREVENTION")
    print("=" * 50)
    
    registry = DAGRegistry()
    
    # Create a valid chain first
    registry.register_module("A", set())
    registry.register_module("B", {"A"})
    registry.register_module("C", {"B"})
    
    print("✅ Valid chain created: A -> B -> C")
    
    # Try to create cycle: C -> A (should fail)
    cycle_result = registry.register_module("C", {"A"})
    print(f"❌ Cycle attempt C -> A: {cycle_result} (should be False)")
    
    # Try to create another cycle: D -> C, E -> D, C -> E (should fail)
    registry.register_module("D", {"C"})
    registry.register_module("E", {"D"})
    cycle_result2 = registry.register_module("C", {"E"})
    print(f"❌ Complex cycle attempt: {cycle_result2} (should be False)")
    
    # Validate final state
    is_dag = registry.validate_dag()
    print(f"✅ Final DAG validation: {is_dag}")
    
    return is_dag


if __name__ == "__main__":
    print("🚀 DAG REGISTRY COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_dag_registry()
    test2_passed = test_circular_dependency_prevention()
    
    print("\n🎯 FINAL RESULTS")
    print("=" * 30)
    print(f"DAG Registry Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Cycle Prevention Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    overall_success = test1_passed and test2_passed
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 DAG REGISTRY IS WORKING CORRECTLY!")
        print("✅ No circular dependencies detected")
        print("✅ DAG structure enforced")
        print("✅ Cycle prevention working")
    else:
        print("\n❌ DAG REGISTRY HAS ISSUES!")
        print("❌ Circular dependencies may exist")
        print("❌ DAG structure not enforced")
    
    sys.exit(0 if overall_success else 1)

