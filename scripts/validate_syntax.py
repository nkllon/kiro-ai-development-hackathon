#!/usr/bin/env python3
"""
Syntax validation gate for automated scripts
"""
import ast
import sys
from pathlib import Path

def validate_python_syntax(file_path):
    """Validate Python syntax of a file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def validate_all_python_files(directory="src"):
    """Validate all Python files in directory"""
    errors = []
    total_files = 0
    
    for py_file in Path(directory).rglob("*.py"):
        total_files += 1
        is_valid, error = validate_python_syntax(py_file)
        if not is_valid:
            errors.append({
                'file': str(py_file),
                'error': error
            })
    
    return errors, total_files

if __name__ == "__main__":
    errors, total = validate_all_python_files()
    if errors:
        print(f"❌ Found {len(errors)} syntax errors in {total} files")
        for error in errors[:5]:  # Show first 5
            print(f"   {error['file']}: {error['error']}")
        sys.exit(1)
    else:
        print(f"✅ All {total} Python files have valid syntax")
        sys.exit(0)
