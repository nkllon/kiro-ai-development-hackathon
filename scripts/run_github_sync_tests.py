#!/usr/bin/env python3
"""
Test runner for GitHub synchronization system.

This script runs all tests for the GitHub sync system including unit tests,
integration tests, and end-to-end tests with proper environment setup.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import json


def setup_test_environment():
    """Set up test environment variables and dependencies."""
    print("Setting up test environment...")
    
    # Load environment variables from ~/.env if it exists (like our config does)
    home_env = Path.home() / ".env"
    if home_env.exists():
        with open(home_env, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip().strip('"').strip("'")
    
    # Ensure required environment variables are set
    required_env_vars = {
        'GITHUB_TOKEN': 'GitHub personal access token for testing',
        'TEST_REPO_OWNER': 'GitHub repository owner for testing (default: octocat)',
        'TEST_REPO_NAME': 'GitHub repository name for testing (default: Hello-World)'
    }
    
    missing_vars = []
    for var, description in required_env_vars.items():
        if not os.getenv(var):
            if var in ['TEST_REPO_OWNER', 'TEST_REPO_NAME']:
                # Set defaults for test repo
                if var == 'TEST_REPO_OWNER':
                    os.environ[var] = 'octocat'
                elif var == 'TEST_REPO_NAME':
                    os.environ[var] = 'Hello-World'
            else:
                missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        print("WARNING: Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nSome tests may be skipped without proper environment setup.")
        print("To run all tests, set the GITHUB_TOKEN environment variable or in ~/.env file.")
    else:
        print("✓ All required environment variables are available")
        github_token = os.getenv('GITHUB_TOKEN', '')
        if github_token:
            print(f"✓ GitHub token found: {github_token[:10]}...")
    
    # Set test-specific environment variables
    os.environ['PYTHONPATH'] = str(Path.cwd())
    
    return len(missing_vars) == 0


def run_unit_tests() -> Dict[str, Any]:
    """Run unit tests."""
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/test_github_sync_basic.py',
            'tests/test_github_sync_comprehensive.py',
            '-v',
            '--tb=short',
            '--no-header',
            '--disable-warnings'
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except Exception as e:
        print(f"Error running unit tests: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_integration_tests() -> Dict[str, Any]:
    """Run integration tests."""
    print("\n" + "="*60)
    print("RUNNING INTEGRATION TESTS")
    print("="*60)
    
    if not os.getenv('GITHUB_TOKEN'):
        print("SKIPPING: Integration tests require GITHUB_TOKEN environment variable")
        return {
            'success': True,
            'skipped': True,
            'reason': 'GITHUB_TOKEN not set'
        }
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/test_github_sync_integration.py',
            '-v',
            '-m', 'integration',
            '--tb=short',
            '--no-header',
            '--disable-warnings'
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except Exception as e:
        print(f"Error running integration tests: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_e2e_tests() -> Dict[str, Any]:
    """Run end-to-end tests."""
    print("\n" + "="*60)
    print("RUNNING END-TO-END TESTS")
    print("="*60)
    
    if not os.getenv('GITHUB_TOKEN'):
        print("SKIPPING: End-to-end tests require GITHUB_TOKEN environment variable")
        return {
            'success': True,
            'skipped': True,
            'reason': 'GITHUB_TOKEN not set'
        }
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/test_github_sync_e2e.py',
            '-v',
            '-m', 'e2e',
            '--tb=short',
            '--no-header',
            '--disable-warnings',
            '-s'  # Don't capture output for e2e tests
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except Exception as e:
        print(f"Error running end-to-end tests: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_security_validation() -> Dict[str, Any]:
    """Run security validation checks."""
    print("\n" + "="*60)
    print("RUNNING SECURITY VALIDATION")
    print("="*60)
    
    try:
        # Check for hardcoded credentials
        src_dir = Path('src/github_sync')
        violations = []
        
        if src_dir.exists():
            import re
            
            # Patterns that might indicate hardcoded credentials
            forbidden_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'key\s*=\s*["\'][^"\']+["\']',
            ]
            
            for py_file in src_dir.glob('*.py'):
                content = py_file.read_text()
                
                for pattern in forbidden_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Filter out test/example values
                        real_violations = [
                            match for match in matches
                            if not any(test_val in match.lower() for test_val in [
                                'test', 'example', 'placeholder', 'your_', 'dummy'
                            ])
                        ]
                        if real_violations:
                            violations.append(f"{py_file}: {real_violations}")
        
        if violations:
            print("SECURITY VIOLATIONS FOUND:")
            for violation in violations:
                print(f"  - {violation}")
            return {
                'success': False,
                'violations': violations
            }
        else:
            print("✓ No hardcoded credentials found")
            print("✓ Security validation passed")
            return {
                'success': True,
                'message': 'Security validation passed'
            }
        
    except Exception as e:
        print(f"Error running security validation: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_syntax_validation() -> Dict[str, Any]:
    """Run syntax validation on all Python files."""
    print("\n" + "="*60)
    print("RUNNING SYNTAX VALIDATION")
    print("="*60)
    
    try:
        src_dir = Path('src/github_sync')
        test_dir = Path('tests')
        
        syntax_errors = []
        
        # Check source files
        for py_file in src_dir.glob('*.py'):
            try:
                with open(py_file, 'r') as f:
                    compile(f.read(), py_file, 'exec')
                print(f"✓ {py_file}")
            except SyntaxError as e:
                syntax_errors.append(f"{py_file}: {e}")
                print(f"✗ {py_file}: {e}")
        
        # Check test files
        for py_file in test_dir.glob('test_github_sync*.py'):
            try:
                with open(py_file, 'r') as f:
                    compile(f.read(), py_file, 'exec')
                print(f"✓ {py_file}")
            except SyntaxError as e:
                syntax_errors.append(f"{py_file}: {e}")
                print(f"✗ {py_file}: {e}")
        
        if syntax_errors:
            return {
                'success': False,
                'errors': syntax_errors
            }
        else:
            print("✓ All Python files have valid syntax")
            return {
                'success': True,
                'message': 'Syntax validation passed'
            }
        
    except Exception as e:
        print(f"Error running syntax validation: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def generate_test_report(results: Dict[str, Any]) -> str:
    """Generate a comprehensive test report."""
    report_lines = [
        "="*80,
        "GITHUB SYNCHRONIZATION SYSTEM - TEST REPORT",
        "="*80,
        f"Test Run Date: {os.popen('date').read().strip()}",
        f"Environment: {os.getenv('GITHUB_TOKEN', 'Not Set')[:10]}..." if os.getenv('GITHUB_TOKEN') else "Environment: No GITHUB_TOKEN",
        ""
    ]
    
    # Summary
    total_categories = len(results)
    passed_categories = sum(1 for result in results.values() if result.get('success', False))
    
    report_lines.extend([
        "SUMMARY:",
        f"  Test Categories: {passed_categories}/{total_categories} passed",
        f"  Overall Status: {'PASS' if passed_categories == total_categories else 'FAIL'}",
        ""
    ])
    
    # Detailed results
    for category, result in results.items():
        status = "PASS" if result.get('success', False) else "FAIL"
        if result.get('skipped'):
            status = "SKIP"
        
        report_lines.extend([
            f"{category.upper()}: {status}",
            f"  {result.get('message', result.get('reason', 'No details'))}"
        ])
        
        if 'violations' in result:
            report_lines.append(f"  Violations: {len(result['violations'])}")
        
        if 'errors' in result:
            report_lines.append(f"  Errors: {len(result['errors'])}")
        
        report_lines.append("")
    
    return "\n".join(report_lines)


def main():
    """Main test runner function."""
    print("GitHub Synchronization System - Test Runner")
    print("="*60)
    
    # Set up environment
    env_ready = setup_test_environment()
    
    # Run all test categories
    test_results = {}
    
    # 1. Syntax validation (always run)
    test_results['syntax_validation'] = run_syntax_validation()
    
    # 2. Security validation (always run)
    test_results['security_validation'] = run_security_validation()
    
    # 3. Unit tests (always run)
    test_results['unit_tests'] = run_unit_tests()
    
    # 4. Integration tests (requires GITHUB_TOKEN)
    test_results['integration_tests'] = run_integration_tests()
    
    # 5. End-to-end tests (requires GITHUB_TOKEN)
    test_results['e2e_tests'] = run_e2e_tests()
    
    # Generate and display report
    report = generate_test_report(test_results)
    print("\n" + report)
    
    # Save report to file
    report_file = Path('github_sync_test_report.txt')
    report_file.write_text(report)
    print(f"\nTest report saved to: {report_file}")
    
    # Determine overall success
    critical_tests = ['syntax_validation', 'security_validation', 'unit_tests']
    critical_passed = all(
        test_results[test].get('success', False) 
        for test in critical_tests
    )
    
    if critical_passed:
        print("\n✓ All critical tests passed!")
        if not env_ready:
            print("  Note: Some tests were skipped due to missing environment variables")
        return 0
    else:
        print("\n✗ Critical tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())