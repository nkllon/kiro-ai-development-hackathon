#!/usr/bin/env python3
"""
Direct git operations - NO SHELL COMMANDS
"""
import subprocess
import sys
import os

def safe_git_commit():
    """Commit changes safely using subprocess"""
    try:
        print("🚨 PHASE 1 GIT SYNC - EMERGENCY FIXES")
        print("=====================================")
        
        # Add all changes
        result = subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
            
        print("✅ All changes added")
        
        # Commit with descriptive message
        commit_msg = """🚨 PHASE 1 EMERGENCY: Fix circular dependencies and deploy DAG registry

- BREAKING: Fixed circular dependency in reflective_module_methods.py
- NEW: Deployed DAG registry with cycle detection
- NEW: Implemented CLI safety system
- FIX: System now functional with proper DAG structure
- STATUS: Phase 1 emergency fixes complete"""
        
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            return False
            
        print("✅ Changes committed")
        
        # Push to GitHub
        result = subprocess.run(
            ["git", "push", "origin", "release/rc0-competitive-launch"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False
            
        print("✅ PHASE 1 CHANGES SYNCHRONIZED TO GITHUB")
        print("✅ Emergency fixes deployed")
        print("✅ Ready to proceed to Phase 2")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Git operation timed out")
        return False
    except Exception as e:
        print(f"❌ Git operation failed: {e}")
        return False

if __name__ == "__main__":
    success = safe_git_commit()
    sys.exit(0 if success else 1)
