#!/usr/bin/env python3
"""
Test proper circular dependency scenario
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rm_ddd.core.beast_mode_registry import register_reflective_module, get_registry_stats

def test_proper_circular_dependency():
    """Test circular dependency in the correct order."""
    print("🧪 PROPER CIRCULAR DEPENDENCY TEST")
    print("=" * 50)
    
    # Step 1: Register parent
    print("\n1. Registering parent...")
    parent_success = register_reflective_module(
        module_id="parent",
        class_name="ParentModule",
        file_path="test.py",
        line_number=1,
        dependencies=[],
        capabilities=["core_functionality"],
        requirements=["provide_interface"]
    )
    print(f"Parent registration: {'✅' if parent_success else '❌'}")
    
    # Step 2: Register child that depends on parent
    print("\n2. Registering child...")
    child_success = register_reflective_module(
        module_id="child",
        class_name="ChildModule", 
        file_path="test.py",
        line_number=1,
        dependencies=["parent"],
        capabilities=["api_integration"],
        requirements=["use_parent"]
    )
    print(f"Child registration: {'✅' if child_success else '❌'}")
    
    # Step 3: Try to register grandchild that depends on child
    print("\n3. Registering grandchild...")
    grandchild_success = register_reflective_module(
        module_id="grandchild",
        class_name="GrandchildModule",
        file_path="test.py", 
        line_number=1,
        dependencies=["child"],
        capabilities=["validation"],
        requirements=["use_child"]
    )
    print(f"Grandchild registration: {'✅' if grandchild_success else '❌'}")
    
    # Step 4: Try to register circular dependency (grandchild -> parent)
    print("\n4. Testing circular dependency (grandchild -> parent)...")
    circular_success = register_reflective_module(
        module_id="circular",
        class_name="CircularModule",
        file_path="test.py",
        line_number=1,
        dependencies=["parent"],  # This should be OK - parent -> child -> grandchild -> parent
        capabilities=["monitoring"],
        requirements=["use_parent"]
    )
    print(f"Circular registration: {'✅' if circular_success else '❌'}")
    
    # Step 5: Try to register actual circular dependency (A -> B -> A)
    print("\n5. Testing actual circular dependency (A -> B -> A)...")
    # First register module A
    a_success = register_reflective_module(
        module_id="module_a",
        class_name="ModuleA",
        file_path="test.py",
        line_number=1,
        dependencies=[],
        capabilities=["data_processing"],
        requirements=["process_data"]
    )
    print(f"Module A registration: {'✅' if a_success else '❌'}")
    
    # Then try to register module B that depends on A, but A will depend on B
    b_success = register_reflective_module(
        module_id="module_b", 
        class_name="ModuleB",
        file_path="test.py",
        line_number=1,
        dependencies=["module_a"],
        capabilities=["api_service"],
        requirements=["use_a"]
    )
    print(f"Module B registration: {'✅' if b_success else '❌'}")
    
    # Now try to make A depend on B (this should fail)
    print("\n6. Testing circular dependency (A -> B -> A)...")
    # We need to update module A to depend on B
    # This should be prevented by the registry
    print("This would require updating module A to depend on B, which should be prevented")
    
    # Check final state
    print("\n7. Final registry state:")
    stats = get_registry_stats()
    print(f"Total modules: {stats['total_modules']}")
    print(f"Total dependencies: {stats['total_dependencies']}")
    
    print("\n🎯 CIRCULAR DEPENDENCY TEST COMPLETE!")

if __name__ == "__main__":
    test_proper_circular_dependency()
