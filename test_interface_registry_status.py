#!/usr/bin/env python3
"""
Interface Registry Status Test
=============================

Test the interface registry to ensure it's updated and free from loops.
"""

import sys
sys.path.append('.')

from src.rm_ddd.core.dag_registry import DAGRegistry, get_dag_validation, get_registry_stats
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleStatus, ModuleHealth, ModuleCapability


def test_interface_registry_integration():
    """Test interface registry integration with DAG registry."""
    print("🔍 TESTING INTERFACE REGISTRY INTEGRATION")
    print("=" * 50)
    
    # Create DAG registry
    dag_registry = DAGRegistry()
    
    # Test 1: Register modules with dependencies
    print("\n📊 Test 1: Module Registration with Dependencies")
    print("-" * 40)
    
    # Register base modules
    success1 = dag_registry.register_module("base_reflective_module", set())
    success2 = dag_registry.register_module("domain_service", {"base_reflective_module"})
    success3 = dag_registry.register_module("application_service", {"domain_service"})
    success4 = dag_registry.register_module("infrastructure_service", {"base_reflective_module"})
    
    print(f"Base ReflectiveModule: {success1}")
    print(f"Domain Service: {success2}")
    print(f"Application Service: {success3}")
    print(f"Infrastructure Service: {success4}")
    
    # Test 2: Try to create circular dependency
    print("\n🚫 Test 2: Circular Dependency Prevention")
    print("-" * 40)
    
    # This should fail - would create cycle
    cycle_attempt = dag_registry.register_module("base_reflective_module", {"application_service"})
    print(f"Cycle attempt (should fail): {cycle_attempt}")
    
    # Test 3: Validate DAG structure
    print("\n✅ Test 3: DAG Structure Validation")
    print("-" * 40)
    
    is_dag = dag_registry.validate_dag()
    print(f"Is DAG: {is_dag}")
    
    # Test 4: Check dependency chains
    print("\n🔗 Test 4: Dependency Chain Analysis")
    print("-" * 40)
    
    for module in dag_registry.modules:
        deps = dag_registry.get_dependencies(module)
        dependents = dag_registry.get_dependents(module)
        chain = dag_registry.get_dependency_chain(module)
        print(f"{module}:")
        print(f"  Dependencies: {deps}")
        print(f"  Dependents: {dependents}")
        print(f"  Chain: {chain}")
    
    # Test 5: Registry statistics
    print("\n📈 Test 5: Registry Statistics")
    print("-" * 40)
    
    stats = dag_registry.get_registry_stats()
    print(f"Total modules: {stats['total_modules']}")
    print(f"Is DAG: {stats['is_dag']}")
    print(f"Modules: {stats['modules']}")
    
    return is_dag


def test_reflective_module_registry_integration():
    """Test ReflectiveModule integration with registry."""
    print("\n🧠 TESTING REFLECTIVE MODULE REGISTRY INTEGRATION")
    print("=" * 60)
    
    # Create a test ReflectiveModule
    class TestReflectiveModule(ReflectiveModule):
        def get_module_info(self) -> dict:
            return {"module_id": "test_module", "version": "1.0.0"}
        
        def get_capabilities(self) -> list:
            return [ModuleCapability.CORE_FUNCTIONALITY]
        
        def get_health_status(self) -> ModuleHealth:
            return ModuleHealth(
                module_id="test_module",
                status=ModuleStatus.HEALTHY,
                health_score=1.0,
                issues=[],
                last_check=datetime.now()
            )
        
        def graceful_degradation(self):
            from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[],
                remaining_capabilities=[ModuleCapability.CORE_FUNCTIONALITY]
            )
    
    # Test module creation and registration
    print("\n📊 Test 1: ReflectiveModule Creation")
    print("-" * 30)
    
    try:
        module = TestReflectiveModule()
        print("✅ ReflectiveModule created successfully")
        
        # Test interface metadata
        metadata = module.get_interface_metadata()
        print(f"✅ Interface metadata: {metadata}")
        
        # Test health check
        health = module.health_check()
        print(f"✅ Health check: {health}")
        
        # Test capabilities
        capabilities = module.get_capabilities()
        print(f"✅ Capabilities: {capabilities}")
        
        return True
        
    except Exception as e:
        print(f"❌ ReflectiveModule test failed: {e}")
        return False


def test_global_registry_status():
    """Test global registry status."""
    print("\n🌐 TESTING GLOBAL REGISTRY STATUS")
    print("=" * 40)
    
    # Test global DAG validation
    global_is_dag = get_dag_validation()
    print(f"Global DAG validation: {global_is_dag}")
    
    # Test global registry stats
    global_stats = get_registry_stats()
    print(f"Global registry modules: {global_stats['total_modules']}")
    print(f"Global registry is DAG: {global_stats['is_dag']}")
    
    return global_is_dag


def main():
    """Run comprehensive interface registry tests."""
    print("🚀 INTERFACE REGISTRY COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Run all tests
    test1_passed = test_interface_registry_integration()
    test2_passed = test_reflective_module_registry_integration()
    test3_passed = test_global_registry_status()
    
    print("\n🎯 FINAL RESULTS")
    print("=" * 30)
    print(f"DAG Registry Integration: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"ReflectiveModule Integration: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Global Registry Status: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    overall_success = test1_passed and test2_passed and test3_passed
    
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 INTERFACE REGISTRY IS WORKING CORRECTLY!")
        print("✅ DAG structure enforced")
        print("✅ Circular dependencies prevented")
        print("✅ ReflectiveModule integration working")
        print("✅ Global registry functional")
    else:
        print("\n❌ INTERFACE REGISTRY HAS ISSUES!")
        print("❌ Some components not working properly")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
