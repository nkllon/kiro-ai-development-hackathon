#!/usr/bin/env python3
"""
Safe test using EmergencyCLIFix
"""
import sys
sys.path.append('.')

from src.emergency_cli_fix import EmergencyCLIFix

def safe_test():
    """Test using the CLI safety system"""
    cli_fix = EmergencyCLIFix()
    
    # Test the circular fix
    test_command = "python3 test_circular_fix.py"
    
    print("🚨 TESTING WITH CLI SAFETY SYSTEM")
    print("=" * 40)
    
    # Validate command first
    is_safe, error = cli_fix.validate_command(test_command)
    print(f"Command: {test_command}")
    print(f"Safe: {is_safe}")
    if not is_safe:
        print(f"Error: {error}")
        return False
    
    # Execute safely
    success, stdout, stderr = cli_fix.safe_execute(test_command)
    print(f"Execution success: {success}")
    if stdout:
        print(f"STDOUT:\n{stdout}")
    if stderr:
        print(f"STDERR:\n{stderr}")
    
    return success

if __name__ == "__main__":
    safe_test()
