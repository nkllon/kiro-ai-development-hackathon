#!/usr/bin/env python3
"""
Fix Redis Hardcoded Credentials
===============================

Systematically replaces hardcoded Redis passwords with secure credential calls.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


class RedisCredentialFixer:
    """Fixes hardcoded Redis credentials in Python files."""
    
    def __init__(self):
        self.fixes_applied = []
        
        # Patterns to find and replace
        self.hardcoded_patterns = [
            # Direct password assignment
            (r'REDIS_PASSWORD\s*=\s*["\']beastmode2025["\']', 
             'REDIS_PASSWORD = get_redis_password()'),
            
            # Redis connection strings
            (r'redis\.from_url\(["\']redis://:beastmode2025@([^"\']+)["\']', 
             r'redis.from_url(f"redis://:{get_redis_password()}@\1"'),
            
            # Redis client password parameter
            (r'password\s*=\s*["\']beastmode2025["\']',
             'password=get_redis_password()'),
            
            # Redis client constructor with password
            (r'redis\.Redis\(([^)]*?)password=["\']beastmode2025["\']([^)]*?)\)',
             r'redis.Redis(\1password=get_redis_password()\2)'),
        ]
        
        # Import statement to add
        self.import_statement = "from src.security.secure_credentials import get_redis_password"
    
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
            if needs_import and 'get_redis_password' not in content:
                # Find where to insert import - after sys.path.append if present
                lines = content.split('\n')
                insert_line = 0
                
                # Look for sys.path.append first, then other imports
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
            if any(skip in str(file_path) for skip in ['/tests/', '/test_', '_test.py', 'credential_scanner', 'fix_redis_credentials']):
                continue
            
            self.fix_file(file_path)
    
    def generate_report(self) -> None:
        """Generate a report of fixes applied."""
        print(f"\n📊 REDIS CREDENTIAL FIX REPORT")
        print("=" * 45)
        
        if not self.fixes_applied:
            print("✅ No hardcoded Redis credentials found!")
            return
        
        print(f"🔧 Fixed {len(self.fixes_applied)} files:")
        for file_path in self.fixes_applied:
            print(f"  • {file_path}")
        
        print(f"\n🚨 IMPORTANT: Add to ~/.env file:")
        print("REDIS_PASSWORD=beastmode2025")
        print("REDIS_HOST=192.168.1.119")
        print("REDIS_PORT=6379")


def main():
    """Main function to fix Redis credentials."""
    fixer = RedisCredentialFixer()
    
    print("🔍 Scanning for hardcoded Redis credentials...")
    
    # Fix current directory
    fixer.fix_directory(Path.cwd())
    
    # Generate report
    fixer.generate_report()


if __name__ == "__main__":
    main()