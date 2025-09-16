#!/usr/bin/env python3
"""
🚀 SCALE UP REGISTRY - REGISTER ALL MODULES
==========================================
Register all Python modules in the repository with the import dependency registry.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Full repository registration
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rm_ddd.core.import_dependency_registry import (
    register_module_imports, validate_no_circular_imports,
    get_import_registry_stats
)

def find_python_files(directory: str = ".") -> list:
    """Find all Python files in the repository."""
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)
    
    return python_files

def register_all_modules():
    """Register all Python modules in the repository."""
    print("🚀 BEAST MODE SCALE-UP: REGISTERING ALL MODULES")
    print("=" * 60)
    
    # Find all Python files
    print("\n1. Scanning repository for Python files...")
    python_files = find_python_files()
    print(f"Found {len(python_files)} Python files")
    
    # Register each module
    print("\n2. Registering modules with import dependency registry...")
    successful = 0
    failed = 0
    circular_imports = []
    
    for i, file_path in enumerate(python_files, 1):
        print(f"[{i:3d}/{len(python_files)}] {file_path}...", end=" ")
        
        try:
            success = register_module_imports(file_path)
            if success:
                print("✅")
                successful += 1
            else:
                print("❌")
                failed += 1
                circular_imports.append(file_path)
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
            circular_imports.append(file_path)
    
    # Check for circular imports
    print("\n3. Validating no circular imports...")
    has_circular = not validate_no_circular_imports()
    
    if has_circular:
        print("❌ CIRCULAR IMPORTS DETECTED!")
    else:
        print("✅ NO CIRCULAR IMPORTS - SYSTEM HEALTHY!")
    
    # Get final statistics
    print("\n4. Final registry statistics...")
    stats = get_import_registry_stats()
    print(f"Total modules registered: {stats['total_modules']}")
    print(f"Total imports tracked: {stats['total_imports']}")
    print(f"Has circular imports: {stats['has_circular_imports']}")
    print(f"Registry healthy: {stats['is_healthy']}")
    
    # Summary
    print("\n5. SCALE-UP SUMMARY:")
    print(f"✅ Successfully registered: {successful} modules")
    print(f"❌ Failed to register: {failed} modules")
    print(f"🔄 Circular imports: {'YES' if has_circular else 'NO'}")
    print(f"🏥 System health: {'HEALTHY' if stats['is_healthy'] else 'UNHEALTHY'}")
    
    if circular_imports:
        print(f"\n⚠️  Modules with circular import issues:")
        for module in circular_imports[:10]:  # Show first 10
            print(f"  - {module}")
        if len(circular_imports) > 10:
            print(f"  ... and {len(circular_imports) - 10} more")
    
    print(f"\n🎯 BEAST MODE SCALE-UP: {'SUCCESS' if stats['is_healthy'] else 'ISSUES FOUND'}")
    return stats['is_healthy']

if __name__ == "__main__":
    success = register_all_modules()
    sys.exit(0 if success else 1)

