#!/usr/bin/env python3
"""
SAFE SHELL WRAPPER - NO MORE DQUOTE ISSUES
=========================================
Wrapper that uses EmergencyCLIFix to prevent shell hanging.
"""

import subprocess
import sys
from src.emergency_cli_fix import EmergencyCLIFix

class SafeShellWrapper:
    """Safe shell wrapper that prevents dquote issues"""
    
    def __init__(self):
        self.cli_fix = EmergencyCLIFix()
    
    def safe_execute(self, command: str) -> tuple[bool, str, str]:
        """Safely execute command with validation"""
        # Validate first
        is_safe, error = self.cli_fix.validate_command(command)
        if not is_safe:
            return False, f"COMMAND REJECTED: {error}", ""
        
        # Sanitize if needed
        safe_command = self.cli_fix.sanitize_command(command)
        
        try:
            result = subprocess.run(
                safe_command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            return True, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "COMMAND TIMEOUT", ""
        except Exception as e:
            return False, f"EXECUTION ERROR: {e}", ""

# Global safe shell instance
safe_shell = SafeShellWrapper()

def safe_run(command: str) -> tuple[bool, str, str]:
    """Safe run command - no dquote issues"""
    return safe_shell.safe_execute(command)


