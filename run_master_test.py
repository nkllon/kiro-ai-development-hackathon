#!/usr/bin/env python3
"""
Run Master Test - Safe Execution
===============================

Uses safe shell command system to run the master test suite.
"""

import sys
sys.path.append('.')

from src.shell_command_fix import safe_shell_command

def run_master_test():
    """Run the master test suite safely."""
    print("🚨 RUNNING MASTER COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    # Master test command
    master_command = "python3 execute_comprehensive_tests.py"
    
    print(f"Executing: {master_command}")
    print()
    
    # Execute safely
    success, stdout, stderr = safe_shell_command(master_command)
    
    if success:
        print("✅ MASTER TEST SUITE EXECUTION SUCCESSFUL")
        print("=" * 50)
        print(stdout)
        return True
    else:
        print("❌ MASTER TEST SUITE EXECUTION FAILED")
        print("=" * 45)
        print(f"STDERR: {stderr}")
        return False

if __name__ == "__main__":
    success = run_master_test()
    sys.exit(0 if success else 1)
