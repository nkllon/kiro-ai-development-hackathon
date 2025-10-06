#!/usr/bin/env python3
"""
Execute Comprehensive Tests - Master Test Runner
==============================================

Executes all comprehensive tests in sequence using safe shell commands.
"""

import sys
sys.path.append('.')

from src.shell_command_fix import safe_shell_command

def run_test(test_name, command):
    """Run a single test safely."""
    print(f"\n🚨 RUNNING {test_name}")
    print("=" * 50)
    print(f"Command: {command}")
    print()
    
    success, stdout, stderr = safe_shell_command(command)
    
    if success:
        print(f"✅ {test_name}: SUCCESS")
        print("-" * 30)
        print(stdout)
        return True
    else:
        print(f"❌ {test_name}: FAILED")
        print("-" * 30)
        print(f"STDERR: {stderr}")
        return False

def main():
    """Execute all comprehensive tests."""
    print("🚨 COMPREHENSIVE TEST EXECUTION")
    print("=" * 50)
    print("Testing RDI and RM-DDD compliance for all touched systems")
    print()
    
    tests = [
        ("DIRECT RDI TEST", "python3 direct_rdi_test.py"),
        ("CONSOLIDATED NAVIGATOR TEST", "python3 test_consolidated_navigator.py"),
        ("COMPREHENSIVE RDI ANALYSIS", "python3 comprehensive_rdi_analysis.py")
    ]
    
    results = []
    
    for test_name, command in tests:
        result = run_test(test_name, command)
        results.append((test_name, result))
    
    print("\n📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("✅ RDI compliance: VERIFIED")
        print("✅ RM-DDD compliance: VERIFIED")
        print("✅ System functionality: PRESERVED")
        print("✅ Architecture: SOUND")
    else:
        print("⚠️ SOME TESTS FAILED - REVIEW REQUIRED")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
