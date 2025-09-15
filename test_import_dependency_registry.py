#!/usr/bin/env python3
"""
Test Import Dependency Registry
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rm_ddd.core.import_dependency_registry import (
    register_module_imports, validate_no_circular_imports,
    get_import_dependencies, get_importers_of, get_import_registry_stats
)

def test_import_dependency_registry():
    """Test the import dependency registry."""
    print("🧪 IMPORT DEPENDENCY REGISTRY TEST")
    print("=" * 50)
    
    # Test 1: Register imports for existing modules
    print("\n1. Registering imports for existing modules...")
    
    # Test with some actual Python files
    test_files = [
        "src/rm_ddd/core/unified_reflective_module.py",
        "src/rm_ddd/core/beast_mode_registry.py",
        "test_bootstrap_module.py"
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"Scanning {file_path}...")
            success = register_module_imports(file_path)
            print(f"  {'✅' if success else '❌'} {file_path}")
        else:
            print(f"  ⚠️  {file_path} not found")
    
    # Test 2: Check for circular imports
    print("\n2. Checking for circular imports...")
    has_circular = not validate_no_circular_imports()
    print(f"Has circular imports: {'❌ YES' if has_circular else '✅ NO'}")
    
    # Test 3: Get import dependencies
    print("\n3. Import dependencies:")
    for file_path in test_files:
        if Path(file_path).exists():
            deps = get_import_dependencies(file_path)
            print(f"\n{file_path} imports:")
            for dep in deps[:5]:  # Show first 5
                print(f"  - {dep.imported_module} ({dep.import_type})")
            if len(deps) > 5:
                print(f"  ... and {len(deps) - 5} more")
    
    # Test 4: Get importers
    print("\n4. Modules that import unified_reflective_module:")
    importers = get_importers_of("src.rm_ddd.core.unified_reflective_module")
    for importer in importers:
        print(f"  - {importer}")
    
    # Test 5: Registry statistics
    print("\n5. Registry statistics:")
    stats = get_import_registry_stats()
    print(f"Total imports: {stats['total_imports']}")
    print(f"Total modules: {stats['total_modules']}")
    print(f"Has circular imports: {stats['has_circular_imports']}")
    print(f"Registry healthy: {stats['is_healthy']}")
    
    print("\n🎯 IMPORT DEPENDENCY REGISTRY TEST COMPLETE!")

if __name__ == "__main__":
    test_import_dependency_registry()
