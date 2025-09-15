#!/usr/bin/env python3
"""
Test safe shell wrapper
"""
import sys
sys.path.append('.')
from src.safe_shell_wrapper import safe_run

# Test safe command
success, stdout, stderr = safe_run("echo 'test'")
print(f"Safe command result: {success}")
print(f"Output: {stdout}")

# Test dangerous command (should be rejected)
success, stdout, stderr = safe_run('echo "unclosed quote')
print(f"Dangerous command result: {success}")
print(f"Error: {stderr}")
