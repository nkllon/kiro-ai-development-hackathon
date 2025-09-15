#!/usr/bin/env python3
"""
🚨 EMERGENCY CLI FIX - PERMANENT SOLUTION
========================================
No more dquote bullshit. Ever.
"""

import re
import subprocess
import sys
from typing import List, Optional

class EmergencyCLIFix:
    """Permanent CLI safety system - NO MORE DQUOTE ISSUES"""
    
    def __init__(self):
        self.dangerous_patterns = [
            r'"[^"]*$',  # Unclosed double quotes
            r"'[^']*$",  # Unclosed single quotes  
            r'`[^`]*$',  # Unclosed backticks
            r'\\$',      # Trailing backslash
            r'&&\s*$',   # Trailing &&
            r'\|\|\s*$', # Trailing ||
        ]
        
    def validate_command(self, command: str) -> tuple[bool, str]:
        """Validate command - returns (is_safe, error_message)"""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command):
                return False, f"DANGEROUS PATTERN DETECTED: {pattern}"
        
        # Check for balanced quotes
        quote_count = command.count('"') - command.count('\\"')
        if quote_count % 2 != 0:
            return False, "UNBALANCED DOUBLE QUOTES"
            
        single_quote_count = command.count("'") - command.count("\\'")
        if single_quote_count % 2 != 0:
            return False, "UNBALANCED SINGLE QUOTES"
            
        return True, "SAFE"
    
    def sanitize_command(self, command: str) -> str:
        """Sanitize command to prevent hanging"""
        # Escape all quotes
        command = command.replace('"', '\\"')
        command = command.replace("'", "\\'")
        command = command.replace('`', '\\`')
        
        # Remove trailing operators
        command = re.sub(r'[&|]+\s*$', '', command)
        
        return command
    
    def safe_execute(self, command: str) -> tuple[bool, str, str]:
        """Safely execute command with validation"""
        # Validate first
        is_safe, error = self.validate_command(command)
        if not is_safe:
            return False, error, ""
        
        # Sanitize if needed
        safe_command = self.sanitize_command(command)
        
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

def main():
    """Test the emergency CLI fix"""
    cli_fix = EmergencyCLIFix()
    
    # Test dangerous commands
    dangerous_commands = [
        'echo "unclosed quote',
        "echo 'unclosed single",
        'echo `unclosed backtick',
        'echo "test" &&',
        'echo "test" ||',
    ]
    
    print("🚨 TESTING CLI SAFETY SYSTEM")
    print("=" * 40)
    
    for cmd in dangerous_commands:
        is_safe, error = cli_fix.validate_command(cmd)
        print(f"Command: {cmd}")
        print(f"Safe: {is_safe}")
        if not is_safe:
            print(f"Error: {error}")
        print()

if __name__ == "__main__":
    main()
