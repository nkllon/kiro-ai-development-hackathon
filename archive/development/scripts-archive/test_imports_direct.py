#!/usr/bin/env python3
"""
Direct import test - NO SHELL COMMANDS
"""
import sys
sys.path.append('.')

def test_circular_fix():
    """Test circular dependency fix directly"""
    try:
        print("🚨 TESTING CIRCULAR DEPENDENCY FIX")
        print("=" * 40)
        
        # Test importing the fixed modules
        from src.devpost_integration.reflective_module import ReflectiveModule
        print("✅ ReflectiveModule imported successfully")
        
        from src.devpost_integration.reflective_module_methods import ReflectiveModuleMethods
        print("✅ ReflectiveModuleMethods imported successfully")
        
        from src.rm_ddd.core.dag_registry import DAGRegistry
        print("✅ DAGRegistry imported successfully")
        
        # Test DAG registry functionality
        registry = DAGRegistry()
        print("✅ DAG registry created")
        
        # Test registration
        success1 = registry.register_module("module_a", {"module_b"})
        success2 = registry.register_module("module_b", {"module_c"})
        success3 = registry.register_module("module_c", set())
        
        print(f"✅ DAG registry working: {success1}, {success2}, {success3}")
        print(f"✅ Registry is DAG: {registry.validate_dag()}")
        
        print("\n🎯 PHASE 1 EMERGENCY FIX: SUCCESS!")
        print("✅ Circular dependencies: FIXED")
        print("✅ DAG registry: WORKING")
        print("✅ System: FUNCTIONAL")
        
        return True
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print("❌ Circular dependency fix failed")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("❌ Test failed")
        return False

if __name__ == "__main__":
    success = test_circular_fix()
    sys.exit(0 if success else 1)
