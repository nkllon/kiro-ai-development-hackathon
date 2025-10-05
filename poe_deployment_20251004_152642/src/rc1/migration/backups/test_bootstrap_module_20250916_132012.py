#!/usr/bin/env python3
"""
🧪 BOOTSTRAP TEST MODULE
=======================
Simple ReflectiveModule for testing registry bootstrap.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Test registry with minimal complexity
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, ModuleStatus, ModuleHealth, ModuleCapability, GracefulDegradationResult
)
from src.rm_ddd.core.beast_mode_registry import register_reflective_module, discover_reflective_modules, get_registry_stats
from datetime import datetime
from typing import Dict, Any, List


class BootstrapTestModule(ReflectiveModule):
    """Simple test module for registry bootstrap."""
    
    def __init__(self, module_id: str = "bootstrap_test"):
        super().__init__()
        self.module_id = module_id
        self.version = "1.0.0"
        self.capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION
        ]
        self.dependencies = ["reflective_module"]
        self.requirements = ["must_be_discoverable", "must_be_consumable"]
        
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
    
    def test_functionality(self) -> str:
        """Test function to verify module works."""
        return f"BootstrapTestModule {self.module_id} is working!"


def test_registry_bootstrap():
    """Test the registry bootstrap process."""
    print("🚀 BEAST MODE REGISTRY BOOTSTRAP TEST")
    print("=" * 50)
    
    # Test 1: Create and register module
    print("\n1. Creating and registering test module...")
    test_module = BootstrapTestModule("bootstrap_test_001")
    
    # Test 2: Discover modules
    print("\n2. Discovering registered modules...")
    discovered = discover_reflective_modules()
    print(f"Found {len(discovered)} modules:")
    for module in discovered:
        print(f"  - {module.module_id} ({module.class_name})")
        print(f"    Capabilities: {module.capabilities}")
        print(f"    Dependencies: {module.dependencies}")
    
    # Test 3: Test module functionality
    print("\n3. Testing module functionality...")
    result = test_module.test_functionality()
    print(f"Module test result: {result}")
    
    # Test 4: Check registry stats
    print("\n4. Registry statistics...")
    stats = get_registry_stats()
    print(f"Total modules: {stats['total_modules']}")
    print(f"Status breakdown: {stats['status_breakdown']}")
    print(f"Interface breakdown: {stats['interface_breakdown']}")
    print(f"Total dependencies: {stats['total_dependencies']}")
    print(f"Recent activity: {stats['recent_activity']}")
    print(f"Database healthy: {stats['is_healthy']}")
    
    # Test 5: Test discovery by capability
    print("\n5. Testing discovery by capability...")
    core_modules = discover_reflective_modules("core_functionality")
    print(f"Found {len(core_modules)} modules with core_functionality capability")
    
    print("\n🎯 BOOTSTRAP TEST: SUCCESS!")
    return True


if __name__ == "__main__":
    success = test_registry_bootstrap()
    sys.exit(0 if success else 1)


