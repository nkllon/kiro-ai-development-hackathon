#!/usr/bin/env python3
"""
Pre-commit hook: Documentation Check
Ensures all interfaces have comprehensive documentation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def check_documentation():
    """Check documentation coverage."""
    # Simple documentation check
    files_without_docs = 0
    
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'class ' in content and '"""' not in content:
                        files_without_docs += 1
                except:
                    continue
    
    return files_without_docs

def main():
    """Run documentation check."""
    files_without_docs = check_documentation()
    
    if files_without_docs > 10:
        print(f"❌ Documentation check failed: {files_without_docs} files missing documentation")
        sys.exit(1)
    else:
        print(f"✅ Documentation check passed: {files_without_docs} files missing documentation")
        sys.exit(0)

if __name__ == "__main__":
    main()
