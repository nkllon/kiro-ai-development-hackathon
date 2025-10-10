#!/usr/bin/env python3
"""
Debug circular dependency detection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rm_ddd.core.beast_mode_registry import beast_mode_registry

def debug_circular_dependency():
    """Debug why circular dependency detection isn't working."""
    print("🔍 DEBUGGING CIRCULAR DEPENDENCY DETECTION")
    print("=" * 50)
    
    # Check current state
    print("\n1. Current registry state:")
    stats = beast_mode_registry.get_registry_stats()
    print(f"Total modules: {stats['total_modules']}")
    
    # Check if child_service exists
    child_module = beast_mode_registry.get_module("child_service")
    if child_module:
        print(f"child_service found: {child_module.dependencies}")
    else:
        print("child_service not found")
    
    # Test circular dependency detection
    print("\n2. Testing circular dependency detection:")
    print("Testing: circular_child depends on child_service")
    
    # Check if there's a path from child_service to circular_child
    has_path = beast_mode_registry._has_dependency_path("child_service", "circular_child")
    print(f"Has dependency path from child_service to circular_child: {has_path}")
    
    # Check if there's a path from circular_child to child_service (this would be circular)
    has_reverse_path = beast_mode_registry._has_dependency_path("circular_child", "child_service")
    print(f"Has dependency path from circular_child to child_service: {has_reverse_path}")
    
    # Test the full circular dependency check
    would_create_circular = beast_mode_registry._would_create_circular_dependency("circular_child", ["child_service"])
    print(f"Would create circular dependency: {would_create_circular}")
    
    # Check the dependency chain
    print("\n3. Checking dependency chain:")
    child_deps = beast_mode_registry.resolve_dependencies("child_service")
    print(f"child_service dependencies: {[d.module_id for d in child_deps]}")
    
    # Check if child_service depends on anything that would create a cycle
    print("\n4. Checking for existing cycles:")
    for dep in child_deps:
        dep_deps = beast_mode_registry.resolve_dependencies(dep.module_id)
        print(f"{dep.module_id} depends on: {[d.module_id for d in dep_deps]}")
        if "circular_child" in [d.module_id for d in dep_deps]:
            print(f"  ⚠️  {dep.module_id} already depends on circular_child!")

if __name__ == "__main__":
    debug_circular_dependency()


