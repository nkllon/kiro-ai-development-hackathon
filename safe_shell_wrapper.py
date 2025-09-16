#!/usr/bin/env python3
"""
SAFE SHELL WRAPPER - MANDATORY FOR ALL SHELL COMMANDS
=====================================================
This is the ONLY way to execute shell commands safely.
"""

import sys
import os
sys.path.append('.')

from src.shell_command_fix import safe_shell_command

def execute_safe_command(command: str, timeout: int = 30) -> bool:
    """Execute a shell command safely - returns True if successful"""
    print(f"🚨 EXECUTING SAFE COMMAND: {command}")
    
    success, stdout, stderr = safe_shell_command(command, timeout)
    
    if success:
        print("✅ COMMAND SUCCESSFUL")
        if stdout:
            print(f"OUTPUT:\n{stdout}")
        return True
    else:
        print("❌ COMMAND FAILED")
        if stderr:
            print(f"ERROR:\n{stderr}")
        return False

def main():
    """Test the safe shell wrapper"""
    if len(sys.argv) < 2:
        print("Usage: python3 safe_shell_wrapper.py 'command'")
        sys.exit(1)
    
    command = sys.argv[1]
    success = execute_safe_command(command)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

