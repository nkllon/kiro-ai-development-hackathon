#!/usr/bin/env python3
"""
Test TRUE circular dependency (A -> B -> A)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rm_ddd.core.beast_mode_registry import beast_mode_registry, InterfaceType

def test_true_circular_dependency():
    """Test actual circular dependency A -> B -> A."""
    print("🧪 TRUE CIRCULAR DEPENDENCY TEST")
    print("=" * 50)
    
    # Step 1: Register module A
    print("\n1. Registering module A...")
    a_success = beast_mode_registry.register_module(
        module_id="module_a",
        class_name="ModuleA",
        file_path="test.py",
        line_number=1,
        interface_type=InterfaceType.REFLECTIVE_MODULE,
        dependencies=[],
        capabilities=["data_processing"],
        requirements=["process_data"]
    )
    print(f"Module A registration: {'✅' if a_success else '❌'}")
    
    # Step 2: Register module B that depends on A
    print("\n2. Registering module B (depends on A)...")
    b_success = beast_mode_registry.register_module(
        module_id="module_b",
        class_name="ModuleB", 
        file_path="test.py",
        line_number=1,
        interface_type=InterfaceType.REFLECTIVE_MODULE,
        dependencies=["module_a"],
        capabilities=["api_service"],
        requirements=["use_a"]
    )
    print(f"Module B registration: {'✅' if b_success else '❌'}")
    
    # Step 3: Try to register module C that depends on B, but would make A depend on C
    print("\n3. Registering module C (depends on B)...")
    c_success = beast_mode_registry.register_module(
        module_id="module_c",
        class_name="ModuleC",
        file_path="test.py",
        line_number=1,
        interface_type=InterfaceType.REFLECTIVE_MODULE, 
        dependencies=["module_b"],
        capabilities=["validation"],
        requirements=["use_b"]
    )
    print(f"Module C registration: {'✅' if c_success else '❌'}")
    
    # Step 4: Try to make A depend on C (this would create A -> C -> B -> A)
    print("\n4. Testing circular dependency (A -> C -> B -> A)...")
    print("Attempting to register module D that depends on C, then make A depend on D...")
    
    # Register module D that depends on C
    d_success = beast_mode_registry.register_module(
        module_id="module_d",
        class_name="ModuleD",
        file_path="test.py",
        line_number=1,
        interface_type=InterfaceType.REFLECTIVE_MODULE,
        dependencies=["module_c"],
        capabilities=["monitoring"],
        requirements=["use_c"]
    )
    print(f"Module D registration: {'✅' if d_success else '❌'}")
    
    # Now try to make A depend on D (this should create A -> D -> C -> B -> A)
    print("\n5. Testing if A can depend on D (would create cycle)...")
    # We need to test if we can update A to depend on D
    # This should be prevented by the circular dependency check
    
    # Check current dependency chain
    print("\n6. Current dependency chain:")
    print("A -> (nothing)")
    print("B -> A") 
    print("C -> B")
    print("D -> C")
    print("Chain: D -> C -> B -> A")
    
    # Test if A can depend on D
    would_create_circular = beast_mode_registry._would_create_circular_dependency("module_a", ["module_d"])
    print(f"\nWould A depending on D create circular dependency: {would_create_circular}")
    
    if would_create_circular:
        print("✅ Circular dependency correctly detected!")
    else:
        print("❌ Circular dependency NOT detected - this is a bug!")
    
    # Check final state
    print("\n7. Final registry state:")
    stats = beast_mode_registry.get_registry_stats()
    print(f"Total modules: {stats['total_modules']}")
    print(f"Total dependencies: {stats['total_dependencies']}")
    
    print("\n🎯 TRUE CIRCULAR DEPENDENCY TEST COMPLETE!")

if __name__ == "__main__":
    test_true_circular_dependency()
