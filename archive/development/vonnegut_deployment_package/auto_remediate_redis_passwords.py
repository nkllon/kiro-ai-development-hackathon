#!/usr/bin/env python3
"""
Automated Redis Password Remediation
====================================

Automatically fix the most common hardcoded password patterns.
"""

import os
import re
from pathlib import Path


def remediate_file(file_path: str) -> bool:
    """Remediate a single file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: redis.from_url with hardcoded password
        content = re.sub(
            r'redis\.from_url\("redis://:beastmode2025@([^"]+)"\)',
            r'redis.from_url(f"redis://:{os.getenv(\'REDIS_PASSWORD\', \'\')}@\1")',
            content
        )
        
        # Pattern 2: Variable assignment
        content = re.sub(
            r'REDIS_PASSWORD = get_redis_password()',
            r'REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")',
            content
        )
        
        # Pattern 3: Redis constructor with password parameter
        content = re.sub(
            r'password=[\'"]beastmode2025[\'"]',
            r'password=os.getenv("REDIS_PASSWORD", "")',
            content
        )
        
        # Add import os if needed and not present
        if content != original_content and 'import os' not in content:
            if content.startswith('#!/usr/bin/env python3'):
                # Add after shebang and docstring
                lines = content.split('\n')
                insert_pos = 1
                # Skip docstring
                if len(lines) > 1 and '"""' in lines[1]:
                    for i, line in enumerate(lines[2:], 2):
                        if '"""' in line:
                            insert_pos = i + 1
                            break
                lines.insert(insert_pos, 'import os')
                content = '\n'.join(lines)
            else:
                content = 'import os\n' + content
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"❌ Failed to remediate {file_path}: {e}")
        return False


def main():
    """Main remediation function."""
    print("🔧 Automated Redis Password Remediation")
    print("=" * 50)
    
    # Priority files to remediate
    priority_files = [
        'src/execution_tracking/redis_execution_tracker.py',
        'src/dag_orchestration/infrastructure/precondition_validator.py',
        'scripts/configure_dag_coordination_mode.py'
    ]
    
    remediated_count = 0
    
    for file_path in priority_files:
        if os.path.exists(file_path):
            print(f"🔧 Remediating {file_path}...")
            if remediate_file(file_path):
                print(f"✅ Remediated {file_path}")
                remediated_count += 1
            else:
                print(f"ℹ️  No changes needed in {file_path}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n✅ Remediated {remediated_count} files")
    print("\n🚨 REMAINING WORK:")
    print("1. Manually review and fix the remaining 27 files")
    print("2. Test all Redis connections still work")
    print("3. Consider rotating the Redis password")
    print("4. Remove password from git history if needed")


if __name__ == "__main__":
    main()