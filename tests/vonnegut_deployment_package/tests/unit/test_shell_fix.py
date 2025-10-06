#!/usr/bin/env python3
"""
Test the permanent shell command fix
"""
import sys
sys.path.append('.')

from src.shell_command_fix import safe_shell_command

def test_shell_fix():
    """Test the shell command fix"""
    print("🚨 TESTING PERMANENT SHELL COMMAND FIX")
    print("=" * 50)
    
    # Test safe command
    print("\n1. Testing safe command:")
    success, stdout, stderr = safe_shell_command("python3 test_imports_direct.py")
    if success:
        print("✅ Safe command executed successfully")
        print(f"Output: {stdout[:200]}...")
    else:
        print(f"❌ Safe command failed: {stderr}")
    
    # Test dangerous command (should be blocked)
    print("\n2. Testing dangerous command (should be blocked):")
    success, stdout, stderr = safe_shell_command('echo "unclosed quote')
    if not success:
        print("✅ Dangerous command correctly blocked")
        print(f"Error: {stderr}")
    else:
        print("❌ Dangerous command was not blocked!")
    
    # Test command with trailing operator (should be sanitized)
    print("\n3. Testing command with trailing operator:")
    success, stdout, stderr = safe_shell_command('echo "hello" &&')
    if success:
        print("✅ Command with trailing operator sanitized and executed")
        print(f"Output: {stdout}")
    else:
        print(f"❌ Command failed: {stderr}")
    
    print("\n🎯 SHELL COMMAND FIX: TEST COMPLETE")
    return True

if __name__ == "__main__":
    test_shell_fix()


