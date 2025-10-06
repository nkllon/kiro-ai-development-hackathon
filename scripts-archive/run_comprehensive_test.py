#!/usr/bin/env python3
"""
Run Comprehensive Test - Safe Shell Command
==========================================

Uses the safe shell command system to test the consolidated navigator.
"""

import sys
sys.path.append('.')

from src.shell_command_fix import safe_shell_command

def run_test():
    """Run the comprehensive test safely."""
    print("🚨 RUNNING COMPREHENSIVE CONSOLIDATED NAVIGATOR TEST")
    print("=" * 60)
    
    # Test command
    test_command = "python3 test_consolidated_navigator.py"
    
    print(f"Executing: {test_command}")
    print()
    
    # Execute safely
    success, stdout, stderr = safe_shell_command(test_command)
    
    if success:
        print("✅ TEST EXECUTION SUCCESSFUL")
        print("=" * 40)
        print(stdout)
        return True
    else:
        print("❌ TEST EXECUTION FAILED")
        print("=" * 40)
        print(f"STDERR: {stderr}")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
