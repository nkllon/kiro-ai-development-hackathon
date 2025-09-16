#!/usr/bin/env python3
"""
Prove the shell fix works - NO MORE DQUOTE ERRORS
"""
import sys
sys.path.append('.')

from src.shell_command_fix import safe_shell_command

def prove_fix():
    """Prove the shell fix actually works"""
    print("🚨 PROVING SHELL FIX WORKS")
    print("=" * 30)
    
    # Test the exact command that was failing
    test_command = "python3 test_imports_direct.py"
    print(f"Testing: {test_command}")
    
    success, stdout, stderr = safe_shell_command(test_command)
    
    if success:
        print("✅ SHELL FIX WORKS - Command executed successfully!")
        print(f"Output: {stdout[:200]}...")
        return True
    else:
        print(f"❌ SHELL FIX FAILED: {stderr}")
        return False

if __name__ == "__main__":
    prove_fix()

