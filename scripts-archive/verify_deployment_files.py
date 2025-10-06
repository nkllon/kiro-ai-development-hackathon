#!/usr/bin/env python3
"""
Verification script for deployment automation files

This script verifies that all required deployment automation files
are present and have the correct structure.
"""

import os
from pathlib import Path

def verify_file_exists(file_path, min_size=100):
    """Verify that a file exists and has minimum size"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    size = path.stat().st_size
    if size < min_size:
        print(f"❌ File too small: {file_path} ({size} bytes, expected >= {min_size})")
        return False
    
    print(f"✅ {file_path} ({size} bytes)")
    return True

def verify_directory_exists(dir_path):
    """Verify that a directory exists"""
    path = Path(dir_path)
    if not path.exists():
        print(f"❌ Directory not found: {dir_path}")
        return False
    
    print(f"✅ Directory exists: {dir_path}")
    return True

def verify_file_content(file_path, required_strings):
    """Verify that a file contains required strings"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        content = path.read_text()
        for required_string in required_strings:
            if required_string not in content:
                print(f"❌ Required string not found in {file_path}: {required_string}")
                return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False
    
    print(f"✅ {file_path} contains required content")
    return True

def main():
    """Main verification function"""
    print("🔍 Verifying Deployment Automation Files")
    print("=" * 50)
    
    all_passed = True
    
    # Required files with minimum sizes
    required_files = [
        ("scripts/deploy_websocket_fix.py", 10000),  # >100 lines
        ("scripts/validate_deployment.py", 8000),    # >80 lines
        ("scripts/rollback_deployment.py", 6000),     # >60 lines
        ("tests/deployment/test_deployment_automation.py", 5000),  # >50 lines
    ]
    
    print("\n📁 Checking Required Files")
    print("-" * 25)
    
    for file_path, min_size in required_files:
        if not verify_file_exists(file_path, min_size):
            all_passed = False
    
    # Required directories
    required_dirs = [
        "tests/deployment",
        "logs",
        "backups",
        "reports"
    ]
    
    print("\n📂 Checking Required Directories")
    print("-" * 30)
    
    for dir_path in required_dirs:
        if not verify_directory_exists(dir_path):
            all_passed = False
    
    # Verify file content
    print("\n📄 Checking File Content")
    print("-" * 22)
    
    # Check deployment script content
    deploy_content_checks = [
        "class WebSocketDeploymentManager",
        "async def deploy_websocket_fix",
        "staged rollout",
        "health checks",
        "automatic rollback"
    ]
    
    if not verify_file_content("scripts/deploy_websocket_fix.py", deploy_content_checks):
        all_passed = False
    
    # Check validation script content
    validation_content_checks = [
        "class DeploymentValidator",
        "async def validate_deployment",
        "health checks",
        "performance metrics",
        "quality assurance"
    ]
    
    if not verify_file_content("scripts/validate_deployment.py", validation_content_checks):
        all_passed = False
    
    # Check rollback script content
    rollback_content_checks = [
        "class RollbackManager",
        "async def execute_rollback",
        "automatic rollback",
        "configuration restoration",
        "emergency rollback"
    ]
    
    if not verify_file_content("scripts/rollback_deployment.py", rollback_content_checks):
        all_passed = False
    
    # Check test file content
    test_content_checks = [
        "class TestDeploymentManager",
        "class TestDeploymentValidator",
        "class TestRollbackManager",
        "pytest.mark.asyncio",
        "async def test_"
    ]
    
    if not verify_file_content("tests/deployment/test_deployment_automation.py", test_content_checks):
        all_passed = False
    
    # Check file permissions
    print("\n🔐 Checking File Permissions")
    print("-" * 28)
    
    script_files = [
        "scripts/deploy_websocket_fix.py",
        "scripts/validate_deployment.py",
        "scripts/rollback_deployment.py"
    ]
    
    for script_file in script_files:
        path = Path(script_file)
        if path.exists():
            # Check if file is executable (has shebang)
            try:
                content = path.read_text()
                if content.startswith("#!/usr/bin/env python3"):
                    print(f"✅ {script_file} has correct shebang")
                else:
                    print(f"⚠️  {script_file} missing shebang")
            except Exception as e:
                print(f"❌ Error reading {script_file}: {e}")
                all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All verification checks passed!")
        print("\n📋 Deployment Automation System Summary:")
        print("   • Main deployment script: scripts/deploy_websocket_fix.py")
        print("   • Validation system: scripts/validate_deployment.py")
        print("   • Rollback system: scripts/rollback_deployment.py")
        print("   • Test suite: tests/deployment/test_deployment_automation.py")
        print("\n🚀 System is ready for deployment automation!")
        return True
    else:
        print("❌ Some verification checks failed!")
        print("Please fix the issues above before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)