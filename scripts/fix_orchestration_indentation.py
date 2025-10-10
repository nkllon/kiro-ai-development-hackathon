#!/usr/bin/env python3
"""
Fix Orchestration Indentation Issue

Root Cause: Code generation created malformed indentation in test fixtures function
Fix: Repair indentation and validate syntax
"""

import ast
from pathlib import Path

def fix_orchestration_file():
    """Fix the indentation issue in orchestrate_makefile_unit_tests.py"""
    
    file_path = Path("scripts/orchestrate_makefile_unit_tests.py")
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find and fix the problematic section by looking for specific patterns
    # The issue is with indentation after triple quotes
    
    # Fix by correcting line indentation
        
        # Alternative fix - look for the specific line pattern
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'fixtures_file = self.fixtures_dir / "conftest.py"' in line:
                # Check if indentation is wrong (should be 8 spaces for method body)
                if not line.startswith('        '):
                    lines[i] = '        ' + line.lstrip()
                    print(f"✅ Fixed line {i+1} indentation")
                    
            if 'fixtures_file.write_text(fixtures_content)' in line:
                if not line.startswith('        '):
                    lines[i] = '        ' + line.lstrip()
                    print(f"✅ Fixed line {i+1} indentation")
                    
            if 'self._logger.info(f"Created test fixtures:' in line:
                if not line.startswith('        '):
                    lines[i] = '        ' + line.lstrip()
                    print(f"✅ Fixed line {i+1} indentation")
        
        content = '\n'.join(lines)
    
    # Validate syntax
    try:
        ast.parse(content)
        print("✅ Syntax validation passed")
    except SyntaxError as e:
        print(f"❌ Syntax error still exists: {e}")
        print(f"Line {e.lineno}: {e.text}")
        return False
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed orchestration file: {file_path}")
    return True

if __name__ == "__main__":
    success = fix_orchestration_file()
    if success:
        print("🎉 Orchestration file repair completed successfully")
    else:
        print("❌ Orchestration file repair failed")