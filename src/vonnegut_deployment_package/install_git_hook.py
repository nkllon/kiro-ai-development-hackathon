#!/usr/bin/env python3
"""
Install pre-commit hook for deployment data governance.

This script installs a git pre-commit hook that automatically scans
for deployment data violations before allowing commits.
"""

import os
import sys
import stat
from pathlib import Path


def install_pre_commit_hook():
    """Install the pre-commit hook."""
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository. Run this from the project root.")
        return False
    
    # Create the hook content
    hook_content = '''#!/bin/sh
# Deployment Data Governance Pre-commit Hook
# Automatically installed by install_git_hook.py

echo "🔍 Checking for deployment data governance violations..."

# Run the auditor on staged files
python scripts/deployment_auditor_scan.py deployment/ --quiet

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Deployment data governance violations found!"
    echo ""
    echo "To fix:"
    echo "1. Review the violations above"
    echo "2. Remove the files from git: git rm --cached <file>"
    echo "3. Add patterns to .gitignore"
    echo "4. Try committing again"
    echo ""
    echo "To bypass this check (NOT RECOMMENDED):"
    echo "git commit --no-verify"
    echo ""
    exit 1
fi

echo "✅ No deployment data violations found. Commit allowed."
'''
    
    # Write the hook file
    hook_path = Path('.git/hooks/pre-commit')
    
    # Backup existing hook if it exists
    if hook_path.exists():
        backup_path = Path('.git/hooks/pre-commit.backup')
        print(f"📋 Backing up existing pre-commit hook to {backup_path}")
        hook_path.rename(backup_path)
    
    # Write new hook
    with open(hook_path, 'w') as f:
        f.write(hook_content)
    
    # Make it executable
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
    
    print(f"✅ Pre-commit hook installed: {hook_path}")
    print("   This will automatically check for violations before each commit.")
    
    return True


def uninstall_pre_commit_hook():
    """Remove the pre-commit hook."""
    hook_path = Path('.git/hooks/pre-commit')
    backup_path = Path('.git/hooks/pre-commit.backup')
    
    if hook_path.exists():
        hook_path.unlink()
        print(f"✅ Pre-commit hook removed: {hook_path}")
        
        # Restore backup if it exists
        if backup_path.exists():
            backup_path.rename(hook_path)
            print(f"📋 Restored backup hook from {backup_path}")
    else:
        print("ℹ️  No pre-commit hook found to remove.")


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == 'uninstall':
        uninstall_pre_commit_hook()
    else:
        print("🔧 Installing Deployment Data Governance Pre-commit Hook")
        print("=" * 55)
        
        if install_pre_commit_hook():
            print("")
            print("🎯 What happens now:")
            print("   • Every git commit will be automatically scanned")
            print("   • Commits with violations will be blocked")
            print("   • You'll get specific remediation instructions")
            print("")
            print("🧪 Test it:")
            print("   1. Create a test violation: touch deployment/test.db")
            print("   2. Try to commit: git add . && git commit -m 'test'")
            print("   3. Should be blocked with violation details")
            print("")
            print("🚨 To bypass (emergency only): git commit --no-verify")
            print("")
            print("🗑️  To remove: python scripts/install_git_hook.py uninstall")


if __name__ == '__main__':
    main()