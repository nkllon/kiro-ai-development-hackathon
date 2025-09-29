#!/usr/bin/env python3
"""
Validate that all test imports work correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test ReflectiveModule import
        from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
        print("✅ ReflectiveModule imported successfully")
        
        # Test Directus CMS imports
        from src.beast_mode.directus_cms.schema_manager import SchemaManager
        print("✅ SchemaManager imported successfully")
        
        from src.beast_mode.directus_cms.data_populator import DataPopulator
        print("✅ DataPopulator imported successfully")
        
        # Test creating instances
        schema_manager = SchemaManager()
        print("✅ SchemaManager instance created")
        
        data_populator = DataPopulator(schema_manager)
        print("✅ DataPopulator instance created")
        
        # Test basic functionality
        schema_info = schema_manager.get_module_info()
        print(f"✅ SchemaManager module info: {schema_info['module_id']}")
        
        populator_info = data_populator.get_module_info()
        print(f"✅ DataPopulator module info: {populator_info['module_id']}")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)