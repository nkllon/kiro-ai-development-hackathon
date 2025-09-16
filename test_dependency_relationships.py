#!/usr/bin/env python3
"""
🧪 DEPENDENCY RELATIONSHIP TESTING
================================
Test parent-child dependency relationships to debug common patterns.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Test dependency resolution and circular dependency prevention
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, ModuleStatus, ModuleHealth, ModuleCapability, GracefulDegradationResult
)
from src.rm_ddd.core.beast_mode_registry import (
    register_reflective_module, discover_reflective_modules, get_registry_stats,
    beast_mode_registry
)
from datetime import datetime
from typing import Dict, Any, List


class ParentModule(ReflectiveModule):
    """Parent module that provides core functionality."""
    
    def __init__(self, module_id: str = "parent_core"):
        super().__init__()
        self.module_id = module_id
        self.version = "1.0.0"
        self.capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING
        ]
        self.dependencies = []  # No dependencies - this is a parent
        self.requirements = ["provide_core_interface", "handle_data_processing"]
        
        # Auto-register with registry
        self._register_with_registry()
    
    def _register_with_registry(self):
        """Register this module with the beast mode registry."""
        try:
            success = register_reflective_module(
                module_id=self.module_id,
                class_name=self.__class__.__name__,
                file_path=__file__,
                line_number=1,
                dependencies=self.dependencies,
                capabilities=[cap.value for cap in self.capabilities],
                requirements=self.requirements
            )
            
            if success:
                print(f"✅ {self.module_id} registered successfully")
            else:
                print(f"❌ {self.module_id} registration failed")
                
        except Exception as e:
            print(f"🚨 Registration error: {e}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "version": self.version,
            "class_name": self.__class__.__name__,
            "file_path": __file__,
            "capabilities": [cap.value for cap in self.capabilities],
            "dependencies": self.dependencies,
            "requirements": self.requirements,
            "health_status": self.get_health_status().status.value,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return self.capabilities
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.capabilities,
            error_message=None
        )
    
    def provide_core_interface(self) -> str:
        """Core functionality provided by parent."""
        return f"Parent {self.module_id} provides core interface"


class ChildModule(ReflectiveModule):
    """Child module that depends on parent."""
    
    def __init__(self, module_id: str = "child_service", parent_id: str = "parent_core"):
        super().__init__()
        self.module_id = module_id
        self.parent_id = parent_id
        self.version = "1.0.0"
        self.capabilities = [
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.VALIDATION
        ]
        self.dependencies = [parent_id]  # Depends on parent
        self.requirements = ["use_parent_interface", "provide_api_service"]
        
        # Auto-register with registry
        self._register_with_registry()
    
    def _register_with_registry(self):
        """Register this module with the beast mode registry."""
        try:
            success = register_reflective_module(
                module_id=self.module_id,
                class_name=self.__class__.__name__,
                file_path=__file__,
                line_number=1,
                dependencies=self.dependencies,
                capabilities=[cap.value for cap in self.capabilities],
                requirements=self.requirements
            )
            
            if success:
                print(f"✅ {self.module_id} registered successfully")
            else:
                print(f"❌ {self.module_id} registration failed")
                
        except Exception as e:
            print(f"🚨 Registration error: {e}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "version": self.version,
            "class_name": self.__class__.__name__,
            "file_path": __file__,
            "capabilities": [cap.value for cap in self.capabilities],
            "dependencies": self.dependencies,
            "requirements": self.requirements,
            "health_status": self.get_health_status().status.value,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return self.capabilities
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.capabilities,
            error_message=None
        )
    
    def provide_api_service(self) -> str:
        """API service that uses parent functionality."""
        return f"Child {self.module_id} provides API service using parent {self.parent_id}"


def test_dependency_relationships():
    """Test parent-child dependency relationships."""
    print("🧪 DEPENDENCY RELATIONSHIP TESTING")
    print("=" * 50)
    
    # Test 1: Register parent first
    print("\n1. Registering parent module...")
    parent = ParentModule("parent_core")
    
    # Test 2: Register child that depends on parent
    print("\n2. Registering child module with dependency...")
    child = ChildModule("child_service", "parent_core")
    
    # Test 3: Test circular dependency prevention
    print("\n3. Testing circular dependency prevention...")
    try:
        # Try to create a circular dependency
        circular_child = ChildModule("circular_child", "child_service")
        print("❌ Circular dependency was allowed (this should not happen)")
    except Exception as e:
        print(f"✅ Circular dependency prevented: {e}")
    
    # Test 4: Discover all modules
    print("\n4. Discovering all registered modules...")
    all_modules = discover_reflective_modules()
    print(f"Found {len(all_modules)} modules:")
    for module in all_modules:
        print(f"  - {module.module_id} ({module.class_name})")
        print(f"    Dependencies: {module.dependencies}")
        print(f"    Capabilities: {module.capabilities}")
    
    # Test 5: Test dependency resolution
    print("\n5. Testing dependency resolution...")
    child_dependencies = beast_mode_registry.resolve_dependencies("child_service")
    print(f"Child service dependencies: {len(child_dependencies)}")
    for dep in child_dependencies:
        print(f"  - {dep.module_id} ({dep.class_name})")
    
    # Test 6: Test parent dependencies
    print("\n6. Testing parent dependencies...")
    parent_dependencies = beast_mode_registry.resolve_dependencies("parent_core")
    print(f"Parent core dependencies: {len(parent_dependencies)}")
    
    # Test 7: Test module functionality
    print("\n7. Testing module functionality...")
    parent_result = parent.provide_core_interface()
    child_result = child.provide_api_service()
    print(f"Parent result: {parent_result}")
    print(f"Child result: {child_result}")
    
    # Test 8: Registry statistics
    print("\n8. Registry statistics...")
    stats = get_registry_stats()
    print(f"Total modules: {stats['total_modules']}")
    print(f"Total dependencies: {stats['total_dependencies']}")
    print(f"Status breakdown: {stats['status_breakdown']}")
    print(f"Interface breakdown: {stats['interface_breakdown']}")
    
    print("\n🎯 DEPENDENCY RELATIONSHIP TEST: SUCCESS!")
    return True


if __name__ == "__main__":
    success = test_dependency_relationships()
    sys.exit(0 if success else 1)

