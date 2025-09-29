#!/usr/bin/env python3
"""
Test runner for Directus CMS tests

Executes all unit and integration tests for the Directus CMS system
with comprehensive reporting and validation.
"""

import unittest
import sys
import os
import time
from pathlib import Path
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_test_suite():
    """Run the complete Directus CMS test suite"""
    print("🧪 Directus CMS Test Suite")
    print("=" * 50)
    
    # Discover and run unit tests
    print("\n📋 Running Unit Tests...")
    unit_loader = unittest.TestLoader()
    unit_suite = unit_loader.discover('tests/unit/directus_cms', pattern='test_*.py')
    
    unit_runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    unit_result = unit_runner.run(unit_suite)
    
    # Discover and run integration tests
    print("\n🔗 Running Integration Tests...")
    integration_loader = unittest.TestLoader()
    integration_suite = integration_loader.discover('tests/integration/directus_cms', pattern='test_*.py')
    
    integration_runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    integration_result = integration_runner.run(integration_suite)
    
    # Generate summary report
    print("\n📊 Test Summary Report")
    print("-" * 30)
    
    total_tests = unit_result.testsRun + integration_result.testsRun
    total_failures = len(unit_result.failures) + len(integration_result.failures)
    total_errors = len(unit_result.errors) + len(integration_result.errors)
    total_skipped = len(unit_result.skipped) + len(integration_result.skipped)
    
    print(f"Total Tests Run: {total_tests}")
    print(f"✅ Passed: {total_tests - total_failures - total_errors - total_skipped}")
    print(f"❌ Failed: {total_failures}")
    print(f"💥 Errors: {total_errors}")
    print(f"⏭️  Skipped: {total_skipped}")
    
    # Calculate success rate
    if total_tests > 0:
        success_rate = ((total_tests - total_failures - total_errors) / total_tests) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Print detailed failure information
    if total_failures > 0 or total_errors > 0:
        print("\n🔍 Failure Details:")
        print("-" * 20)
        
        for test, traceback in unit_result.failures + integration_result.failures:
            print(f"❌ FAIL: {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip()}")
        
        for test, traceback in unit_result.errors + integration_result.errors:
            print(f"💥 ERROR: {test}")
            print(f"   {traceback.split('Exception:')[-1].strip()}")
    
    # Return overall success
    return total_failures == 0 and total_errors == 0

def run_specific_test(test_name):
    """Run a specific test by name"""
    print(f"🎯 Running specific test: {test_name}")
    
    # Try to find and run the specific test
    loader = unittest.TestLoader()
    
    # Look in unit tests
    try:
        suite = loader.loadTestsFromName(f'tests.unit.directus_cms.{test_name}')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except:
        pass
    
    # Look in integration tests
    try:
        suite = loader.loadTestsFromName(f'tests.integration.directus_cms.{test_name}')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except:
        pass
    
    print(f"❌ Test '{test_name}' not found")
    return False

def validate_test_environment():
    """Validate that the test environment is properly set up"""
    print("🔍 Validating test environment...")
    
    # Check required directories exist
    required_dirs = [
        'tests/unit/directus_cms',
        'tests/integration/directus_cms',
        'src/beast_mode/directus_cms'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Missing directory: {dir_path}")
            return False
        print(f"✅ Found: {dir_path}")
    
    # Check required test files exist
    required_files = [
        'tests/unit/directus_cms/test_schema_manager.py',
        'tests/unit/directus_cms/test_data_populator.py',
        'tests/integration/directus_cms/test_complete_workflow.py'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing test file: {file_path}")
            return False
        print(f"✅ Found: {file_path}")
    
    # Check source files exist
    source_files = [
        'src/beast_mode/directus_cms/schema_manager.py',
        'src/beast_mode/directus_cms/data_populator.py',
        'src/beast_mode/directus_cms/orchestrator.py'
    ]
    
    for file_path in source_files:
        if not os.path.exists(file_path):
            print(f"⚠️  Missing source file: {file_path}")
            # Don't fail validation for missing source files
        else:
            print(f"✅ Found: {file_path}")
    
    print("✅ Test environment validation complete")
    return True

def main():
    """Main test runner function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--validate':
            # Validate test environment
            success = validate_test_environment()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--test':
            # Run specific test
            if len(sys.argv) > 2:
                success = run_specific_test(sys.argv[2])
                sys.exit(0 if success else 1)
            else:
                print("❌ Please specify a test name")
                sys.exit(1)
        else:
            print("❌ Unknown option. Use --validate or --test <test_name>")
            sys.exit(1)
    else:
        # Run full test suite
        start_time = time.time()
        
        # Validate environment first
        if not validate_test_environment():
            print("❌ Test environment validation failed")
            sys.exit(1)
        
        # Run tests
        success = run_test_suite()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  Total execution time: {duration:.2f} seconds")
        
        if success:
            print("🎉 All tests passed!")
            sys.exit(0)
        else:
            print("💥 Some tests failed!")
            sys.exit(1)

if __name__ == '__main__':
    main()