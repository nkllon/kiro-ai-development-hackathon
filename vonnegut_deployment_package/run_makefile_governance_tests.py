#!/usr/bin/env python3
"""
Test runner for makefile governance system.

Runs comprehensive tests for syntax validation, governance engine,
and health monitoring components.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all makefile governance tests."""
    print("🧪 Running Makefile Governance System Tests")
    print("=" * 50)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    
    # Test commands to run
    test_commands = [
        # Unit tests
        ["python", "-m", "pytest", "tests/unit/makefile_governance/", "-v", "--tb=short"],
        
        # Integration tests
        ["python", "-m", "pytest", "tests/integration/makefile_governance/", "-v", "--tb=short"],
        
        # All makefile governance tests with coverage
        ["python", "-m", "pytest", "tests/", "-k", "makefile_governance", "-v", "--cov=src/makefile_governance", "--cov-report=term-missing"],
    ]
    
    success_count = 0
    total_count = len(test_commands)
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n📋 Running test suite {i}/{total_count}: {' '.join(cmd[3:])}")
        print("-" * 40)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Test suite {i} passed")
                success_count += 1
            else:
                print(f"❌ Test suite {i} failed with return code {result.returncode}")
                
        except Exception as e:
            print(f"❌ Test suite {i} failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results Summary:")
    print(f"   Passed: {success_count}/{total_count}")
    print(f"   Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All test suites passed!")
        return 0
    else:
        print("💥 Some test suites failed!")
        return 1


def run_specific_tests():
    """Run specific test categories."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run specific makefile governance tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if args.unit:
        cmd.append("tests/unit/makefile_governance/")
    elif args.integration:
        cmd.append("tests/integration/makefile_governance/")
    else:
        cmd.extend(["tests/", "-k", "makefile_governance"])
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=src/makefile_governance", "--cov-report=term-missing", "--cov-report=html"])
    
    cmd.append("--tb=short")
    
    print(f"🧪 Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        exit_code = run_specific_tests()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)