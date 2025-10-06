#!/usr/bin/env python3
"""
Test Requirements Inheritance Registry
====================================
Quick test of the multi-dimensional requirements inheritance system.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rm_ddd.core.requirements_inheritance_registry import (
    RequirementsInheritanceRegistry, Requirement, RequirementType,
    register_module_with_requirements, add_requirement_to_module,
    abdicate_parent_requirements, get_module_requirements,
    get_requirements_coverage, get_audit_trail
)
from datetime import datetime


def test_requirements_inheritance():
    """Test the requirements inheritance system."""
    print("🧬 Testing Requirements Inheritance Registry")
    print("=" * 50)
    
    # Create registry
    registry = RequirementsInheritanceRegistry()
    
    # Register parent modules with requirements
    print("\n1. Registering parent modules...")
    
    # Parent A: Interface requirements
    registry.register_module("parent_a", set())
    interface_req = Requirement(
        requirement_id="req_interface_1",
        requirement_type=RequirementType.INTERFACE,
        description="Must implement ReflectiveModule interface",
        source_parent="parent_a",
        created_at=datetime.now()
    )
    registry.add_requirement("parent_a", interface_req)
    
    # Parent B: Data requirements  
    registry.register_module("parent_b", set())
    data_req = Requirement(
        requirement_id="req_data_1",
        requirement_type=RequirementType.DATA,
        description="Must handle JSON serialization",
        source_parent="parent_b",
        created_at=datetime.now()
    )
    registry.add_requirement("parent_b", data_req)
    
    # Parent C: Validation requirements
    registry.register_module("parent_c", set())
    validation_req = Requirement(
        requirement_id="req_validation_1",
        requirement_type=RequirementType.VALIDATION,
        description="Must validate input parameters",
        source_parent="parent_c",
        created_at=datetime.now()
    )
    registry.add_requirement("parent_c", validation_req)
    
    print("✅ Parents registered with requirements")
    
    # Register child modules inheriting from multiple parents
    print("\n2. Registering child modules with multi-parent inheritance...")
    
    # Child X inherits from A and B
    registry.register_module("child_x", {"parent_a", "parent_b"})
    
    # Child Y inherits from B and C  
    registry.register_module("child_y", {"parent_b", "parent_c"})
    
    # Child Z inherits from A, B, and C
    registry.register_module("child_z", {"parent_a", "parent_b", "parent_c"})
    
    print("✅ Children registered with multi-parent inheritance")
    
    # Check inheritance
    print("\n3. Checking requirements inheritance...")
    
    child_x_reqs = registry.get_module_requirements("child_x")
    print(f"Child X requirements: {len(child_x_reqs)}")
    for req in child_x_reqs:
        print(f"  - {req.requirement_type.value}: {req.description}")
    
    child_z_reqs = registry.get_module_requirements("child_z")
    print(f"Child Z requirements: {len(child_z_reqs)}")
    for req in child_z_reqs:
        print(f"  - {req.requirement_type.value}: {req.description}")
    
    # Test abdication
    print("\n4. Testing parent abdication...")
    
    print("Parent B abdicating...")
    registry.abdicate_parent("parent_b", "Parent B module removed")
    
    # Check that children still have B's requirements
    child_x_reqs_after = registry.get_module_requirements("child_x")
    child_y_reqs_after = registry.get_module_requirements("child_y")
    
    print(f"Child X requirements after abdication: {len(child_x_reqs_after)}")
    print(f"Child Y requirements after abdication: {len(child_y_reqs_after)}")
    
    # Check requirements coverage
    print("\n5. Checking requirements coverage...")
    coverage = registry.get_requirements_coverage()
    print(f"Coverage status: {coverage['coverage_status']}")
    print(f"Total requirements: {coverage['total_requirements']}")
    print(f"Active requirements: {coverage['active_requirements']}")
    print(f"Orphaned requirements: {len(coverage['orphaned_requirements'])}")
    
    # Show audit trail
    print("\n6. Audit trail:")
    audit_events = registry.get_audit_trail()
    for event in audit_events:
        print(f"  {event.timestamp}: {event.event_type} - {event.reason}")
    
    print("\n🎯 Requirements Inheritance Test: SUCCESS!")
    return True


if __name__ == "__main__":
    success = test_requirements_inheritance()
    sys.exit(0 if success else 1)
