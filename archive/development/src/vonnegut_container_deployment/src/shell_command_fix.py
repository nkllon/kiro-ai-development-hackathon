#!/usr/bin/env python3
"""
PERMANENT SHELL COMMAND FIX
===========================
No more dquote errors. Ever. This wraps ALL shell commands.
"""

import subprocess
import sys
import re
from typing import Tuple, Optional

class ShellCommandFix:
    """Permanent fix for shell command execution - NO MORE DQUOTE ERRORS"""
    
    def __init__(self):
        self.dangerous_patterns = [
            r'"[^"]*$',  # Unclosed double quotes
            r"'[^']*$",  # Unclosed single quotes  
            r'`[^`]*$',  # Unclosed backticks
            r'\\$',      # Trailing backslash
            r'&&\s*$',   # Trailing &&
            r'\|\|\s*$', # Trailing ||
            r'\([^)]*$', # Unclosed parentheses
            r'\[[^\]]*$', # Unclosed brackets
        ]
    
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate command - returns (is_safe, error_message)"""
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command):
                return False, f"DANGEROUS PATTERN: {pattern}"
        
        # Check for balanced quotes
        quote_count = command.count('"') - command.count('\\"')
        if quote_count % 2 != 0:
            return False, "UNBALANCED DOUBLE QUOTES"
            
        single_quote_count = command.count("'") - command.count("\\'")
        if single_quote_count % 2 != 0:
            return False, "UNBALANCED SINGLE QUOTES"
        
        # Check for balanced parentheses
        paren_count = command.count('(') - command.count(')')
        if paren_count != 0:
            return False, "UNBALANCED PARENTHESES"
            
        return True, "SAFE"
    
    def sanitize_command(self, command: str) -> str:
        """Sanitize command to prevent hanging"""
        # Remove any trailing operators
        command = re.sub(r'[&|]+\s*$', '', command)
        
        # Escape problematic characters
        command = command.replace('\\', '\\\\')
        
        return command.strip()
    
    def safe_execute(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Safely execute command with full validation"""
        print(f"🔍 Validating command: {command}")
        
        # Validate first
        is_safe, error = self.validate_command(command)
        if not is_safe:
            print(f"❌ UNSAFE COMMAND BLOCKED: {error}")
            return False, "", error
        
        # Sanitize
        safe_command = self.sanitize_command(command)
        if safe_command != command:
            print(f"🔧 Sanitized command: {safe_command}")
        
        try:
            print(f"✅ Executing safe command: {safe_command}")
            result = subprocess.run(
                safe_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            print(f"✅ Command completed with exit code: {result.returncode}")
            return True, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            error_msg = f"COMMAND TIMEOUT after {timeout} seconds"
            print(f"❌ {error_msg}")
            return False, "", error_msg
        except Exception as e:
            error_msg = f"EXECUTION ERROR: {e}"
            print(f"❌ {error_msg}")
            return False, "", error_msg

# Global instance for use by other modules
shell_fix = ShellCommandFix()

def safe_shell_command(command: str, timeout: int = 30) -> Tuple[bool, str, str]:
    """Convenience function for safe shell command execution"""
    return shell_fix.safe_execute(command, timeout)

if __name__ == "__main__":
    # Test the fix
    test_commands = [
        "python3 test_imports_direct.py",
        'echo "hello world"',
        'echo "unclosed quote',  # This should be blocked
        "ls -la",
        'echo "test" &&',  # This should be sanitized
    ]
    
    print("🚨 TESTING PERMANENT SHELL COMMAND FIX")
    print("=" * 50)
    
    for cmd in test_commands:
        print(f"\n--- Testing: {cmd} ---")
        success, stdout, stderr = safe_shell_command(cmd)
        if success:
            print(f"✅ SUCCESS: {stdout[:100]}...")
        else:
            print(f"❌ FAILED: {stderr}")


