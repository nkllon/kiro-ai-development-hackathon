#!/usr/bin/env python3
"""
Remove Duplicate ReflectiveModule Implementations
================================================

This script removes all duplicate ReflectiveModule class definitions,
keeping only the canonical base_reflective_module.py implementation.

Author: Beast Mode Framework
Date: 2025-09-16
Purpose: Fix RM-DDD base class compliance
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def find_duplicate_reflective_modules(project_root: str) -> List[Tuple[str, int]]:
    """Find all files with duplicate ReflectiveModule classes"""
    duplicates = []
    project_path = Path(project_root)
    
    for py_file in project_path.rglob("src/**/*.py"):
        if "base_reflective_module.py" in str(py_file):
            continue  # Skip the canonical base class
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    if re.search(r'class ReflectiveModule\s*\(', line):
                        duplicates.append((str(py_file), i + 1))
                        break
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return duplicates

def remove_reflective_module_class(file_path: str, line_number: int) -> bool:
    """Remove the ReflectiveModule class from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the class definition and remove it
        start_line = line_number - 1  # Convert to 0-based index
        
        # Find the end of the class (look for next class or end of file)
        end_line = start_line
        indent_level = None
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            
            # Determine indentation level of the class
            if i == start_line:
                indent_level = len(line) - len(line.lstrip())
                continue
            
            # Check if we've reached the end of the class
            if line.strip() and not line.startswith(' ' * (indent_level + 1)) and not line.startswith('\t'):
                end_line = i
                break
        else:
            end_line = len(lines)
        
        # Remove the class definition
        new_lines = lines[:start_line] + lines[end_line:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return True
        
    except Exception as e:
        print(f"Error removing ReflectiveModule from {file_path}: {e}")
        return False

def add_import_statement(file_path: str) -> bool:
    """Add import statement for the canonical ReflectiveModule"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if import already exists
        if 'from src.rm_ddd.core.base_reflective_module import ReflectiveModule' in content:
            return True
        
        # Add import at the top
        lines = content.split('\n')
        
        # Find the right place to insert the import
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_index = i + 1
            elif line.strip() and not line.startswith('#'):
                break
        
        # Insert the import
        import_line = 'from src.rm_ddd.core.base_reflective_module import ReflectiveModule'
        lines.insert(insert_index, import_line)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
        
    except Exception as e:
        print(f"Error adding import to {file_path}: {e}")
        return False

def main():
    """Main function to remove duplicate ReflectiveModule classes"""
    print("🔍 Finding duplicate ReflectiveModule classes...")
    
    duplicates = find_duplicate_reflective_modules(".")
    print(f"📊 Found {len(duplicates)} duplicate ReflectiveModule classes")
    
    if not duplicates:
        print("✅ No duplicates found!")
        return
    
    print("\n🚀 Removing duplicate ReflectiveModule classes...")
    
    success_count = 0
    error_count = 0
    
    for file_path, line_number in duplicates:
        print(f"   Processing: {file_path}:{line_number}")
        
        # Remove the duplicate class
        if remove_reflective_module_class(file_path, line_number):
            # Add import for canonical ReflectiveModule
            if add_import_statement(file_path):
                success_count += 1
                print(f"   ✅ Successfully cleaned {file_path}")
            else:
                error_count += 1
                print(f"   ❌ Failed to add import to {file_path}")
        else:
            error_count += 1
            print(f"   ❌ Failed to clean {file_path}")
    
    print(f"\n📊 Cleanup Results:")
    print(f"   ✅ Successfully cleaned: {success_count}")
    print(f"   ❌ Failed: {error_count}")
    print(f"   📁 Total files processed: {len(duplicates)}")
    
    if success_count > 0:
        print("\n✅ Duplicate ReflectiveModule classes removed!")
        print("   All files now use the canonical base_reflective_module.py")
    else:
        print("\n❌ No files were successfully cleaned")

if __name__ == "__main__":
    main()
