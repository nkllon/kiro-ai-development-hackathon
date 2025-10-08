#!/usr/bin/env python3
"""
Fix Directus Hardcoded Credentials
=================================

Systematically replaces hardcoded Directus passwords with secure credential calls.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


class DirectusCredentialFixer:
    """Fixes hardcoded Directus credentials in Python files."""
    
    def __init__(self):
        self.fixes_applied = []
        
        # Patterns to find and replace
        self.hardcoded_patterns = [
            # Direct password assignment
            (r'ADMIN_PASSWORD\s*=\s*["\']d1r3ctu5["\']', 
             'ADMIN_PASSWORD = get_directus_password()'),
            
            # Self assignment in classes
            (r'self\.admin_password\s*=\s*["\']d1r3ctu5["\']',
             'self.admin_password = get_directus_password()'),
            
            # Other variations
            (r'admin_password\s*=\s*["\']d1r3ctu5["\']',
             'admin_password = get_directus_password()'),
        ]
        
        # Import statement to add
        self.import_statement = "from src.security.secure_credentials import get_directus_password"
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix hardcoded credentials in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            needs_import = False
            
            # Apply pattern replacements
            for pattern, replacement in self.hardcoded_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    needs_import = True
            
            # Add import if needed and not already present
            if needs_import and 'get_directus_password' not in content:
                # Find where to insert import - after sys.path.append if present
                lines = content.split('\n')
                insert_line = 0
                
                # Look for sys.path.append first
                for i, line in enumerate(lines):
                    if 'sys.path.append' in line:
                        insert_line = i + 1
                        break
                    elif line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_line = i + 1
                
                # Insert import with blank line
                lines.insert(insert_line, "")
                lines.insert(insert_line + 1, self.import_statement)
                content = '\n'.join(lines)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixes_applied.append(str(file_path))
                print(f"✅ Fixed: {file_path}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
            return False
    
    def fix_directory(self, directory: Path) -> None:
        """Fix all Python files in directory recursively."""
        for file_path in directory.rglob("*.py"):
            # Skip test files and scanner scripts
            if any(skip in str(file_path) for skip in ['/tests/', '/test_', '_test.py', 'credential_scanner']):
                continue
            
            self.fix_file(file_path)
    
    def generate_report(self) -> None:
        """Generate a report of fixes applied."""
        print(f"\n📊 DIRECTUS CREDENTIAL FIX REPORT")
        print("=" * 45)
        
        if not self.fixes_applied:
            print("✅ No hardcoded Directus credentials found!")
            return
        
        print(f"🔧 Fixed {len(self.fixes_applied)} files:")
        for file_path in self.fixes_applied:
            print(f"  • {file_path}")
        
        print(f"\n🚨 IMPORTANT: Add to ~/.env file:")
        print("DIRECTUS_ADMIN_PASSWORD=d1r3ctu5")
        print("DIRECTUS_URL=http://localhost:8055")
        print("DIRECTUS_ADMIN_EMAIL=admin@example.com")


def main():
    """Main function to fix Directus credentials."""
    fixer = DirectusCredentialFixer()
    
    print("🔍 Scanning for hardcoded Directus credentials...")
    
    # Fix current directory
    fixer.fix_directory(Path.cwd())
    
    # Generate report
    fixer.generate_report()


if __name__ == "__main__":
    main()