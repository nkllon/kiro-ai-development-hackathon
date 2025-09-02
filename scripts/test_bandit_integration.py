#!/usr/bin/env python3
"""
Test script for Bandit integration

This script tests the Bandit security integration to ensure it works correctly
with our model-driven security system.
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def test_bandit_import():
    """Test that Bandit can be imported"""
    try:
        # Import to test availability
        from bandit_integration import BanditSecurityScanner, ModelDrivenSecurityScanner

        print("✅ Bandit integration imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Bandit integration: {e}")
        return False


def test_bandit_availability():
    """Test that Bandit is available in the environment"""
    try:
        import bandit

        print(f"✅ Bandit {bandit.__version__} is available")
        return True
    except ImportError:
        print("❌ Bandit is not installed. Install with: uv add bandit")
        return False


def test_scanner_creation():
    """Test that security scanner can be created"""
    try:
        from bandit_integration import BanditSecurityScanner

        _ = BanditSecurityScanner()  # Create scanner to test
        print("✅ Bandit security scanner created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create security scanner: {e}")
        return False


def test_model_scanner_creation():
    """Test that model-driven scanner can be created"""
    try:
        from bandit_integration import ModelDrivenSecurityScanner

        _ = ModelDrivenSecurityScanner()  # Create scanner to test
        print("✅ Model-driven security scanner created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create model-driven scanner: {e}")
        return False


def test_file_scan():
    """Test scanning a simple Python file"""
    try:
        from bandit_integration import BanditSecurityScanner

        # Create a simple test file with a security issue
        test_file = "test_security_issue.py"
        with open(test_file, "w") as f:
            f.write(
                """#!/usr/bin/env python3
# Test file with security issues for Bandit testing

import hashlib
import os

# This should trigger a Bandit warning
password = "hardcoded_password_123"

# This should also trigger a warning
hashlib.md5("test".encode()).hexdigest()

# This should be fine
hashlib.sha256("test".encode()).hexdigest()

print("Test file created for security scanning")
"""
            )

        # Scan the file
        scanner = BanditSecurityScanner()
        result = scanner.scan_file(test_file)

        print(f"✅ File scan completed:")
        print(f"   Files scanned: {result.files_scanned}")
        print(f"   Issues found: {result.issues_found}")
        print(f"   Success: {result.success}")

        if result.issues:
            print("   Issues found:")
            for issue in result.issues[:3]:  # Show first 3 issues
                print(f"     - {issue.issue_type}: {issue.message}")
                print(f"       File: {issue.filename}:{issue.line_number}")

        # Clean up test file
        os.remove(test_file)
        return True

    except Exception as e:
        print(f"❌ File scan test failed: {e}")
        # Clean up test file if it exists
        if os.path.exists("test_security_issue.py"):
            os.remove("test_security_issue.py")
        return False


def main():
    """Run all tests"""
    print("🔒 Testing Bandit Security Integration")
    print("=" * 50)

    tests = [
        ("Bandit Import", test_bandit_import),
        ("Bandit Availability", test_bandit_availability),
        ("Scanner Creation", test_scanner_creation),
        ("Model Scanner Creation", test_model_scanner_creation),
        ("File Scanning", test_file_scan),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 30)

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Bandit integration is working correctly.")
        return 0
    print("⚠️  Some tests failed. Check the output above for details.")
    return 1


if __name__ == "__main__":
    exit(main())
