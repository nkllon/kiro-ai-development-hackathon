#!/usr/bin/env python3
"""
Test Suite Validation Script

Validates that the comprehensive integration test suite is properly configured
and can be executed. This script performs basic validation without running
the full test suite.
"""

import sys
import importlib.util
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def validate_test_file(test_file_path: Path) -> Dict[str, Any]:
    """Validate a single test file"""
    
    result = {
        "file": str(test_file_path),
        "exists": False,
        "importable": False,
        "test_classes": [],
        "test_methods": [],
        "errors": []
    }
    
    # Check if file exists
    if not test_file_path.exists():
        result["errors"].append(f"File does not exist: {test_file_path}")
        return result
    
    result["exists"] = True
    
    # Try to import the module
    try:
        spec = importlib.util.spec_from_file_location("test_module", test_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result["importable"] = True
        
        # Find test classes and methods
        for name in dir(module):
            obj = getattr(module, name)
            
            if isinstance(obj, type) and name.startswith("Test"):
                result["test_classes"].append(name)
                
                # Find test methods in class
                for method_name in dir(obj):
                    if method_name.startswith("test_"):
                        result["test_methods"].append(f"{name}.{method_name}")
        
    except Exception as e:
        result["errors"].append(f"Import error: {str(e)}")
    
    return result


def validate_comprehensive_test_suite() -> Dict[str, Any]:
    """Validate the comprehensive integration test suite"""
    
    print("🔍 Validating Beast Mode Comprehensive Integration Test Suite")
    print("=" * 60)
    
    # Define test files to validate
    test_files = [
        "tests/integration/test_comprehensive_beast_mode_integration.py",
        "tests/integration/test_performance_benchmarks.py", 
        "tests/integration/test_cross_platform_compatibility.py",
        "tests/integration/run_comprehensive_tests.py"
    ]
    
    # Existing integration tests
    existing_test_files = [
        "tests/integration/test_bus_client.py",
        "tests/integration/test_agent_discovery.py",
        "tests/integration/test_help_system_integration.py",
        "tests/integration/test_mailbox_logger_integration.py",
        "tests/integration/test_message_routing.py",
        "tests/integration/test_spore_management_integration.py"
    ]
    
    validation_results = {
        "comprehensive_tests": {},
        "existing_tests": {},
        "summary": {
            "total_files": 0,
            "files_exist": 0,
            "files_importable": 0,
            "total_test_classes": 0,
            "total_test_methods": 0,
            "validation_passed": False
        },
        "errors": []
    }
    
    # Validate comprehensive test files
    print("\n📋 Validating Comprehensive Test Files:")
    for test_file in test_files:
        test_path = Path(test_file)
        result = validate_test_file(test_path)
        validation_results["comprehensive_tests"][test_file] = result
        
        status = "✅" if result["importable"] else "❌"
        print(f"  {status} {test_file}")
        
        if result["errors"]:
            for error in result["errors"]:
                print(f"    ⚠️  {error}")
                validation_results["errors"].append(f"{test_file}: {error}")
        else:
            print(f"    📊 {len(result['test_classes'])} test classes, {len(result['test_methods'])} test methods")
    
    # Validate existing test files
    print("\n📋 Validating Existing Integration Test Files:")
    for test_file in existing_test_files:
        test_path = Path(test_file)
        result = validate_test_file(test_path)
        validation_results["existing_tests"][test_file] = result
        
        status = "✅" if result["importable"] else "❌"
        print(f"  {status} {test_file}")
        
        if result["errors"]:
            for error in result["errors"]:
                print(f"    ⚠️  {error}")
                validation_results["errors"].append(f"{test_file}: {error}")
        else:
            print(f"    📊 {len(result['test_classes'])} test classes, {len(result['test_methods'])} test methods")
    
    # Calculate summary statistics
    all_results = list(validation_results["comprehensive_tests"].values()) + \
                  list(validation_results["existing_tests"].values())
    
    validation_results["summary"]["total_files"] = len(all_results)
    validation_results["summary"]["files_exist"] = sum(1 for r in all_results if r["exists"])
    validation_results["summary"]["files_importable"] = sum(1 for r in all_results if r["importable"])
    validation_results["summary"]["total_test_classes"] = sum(len(r["test_classes"]) for r in all_results)
    validation_results["summary"]["total_test_methods"] = sum(len(r["test_methods"]) for r in all_results)
    validation_results["summary"]["validation_passed"] = len(validation_results["errors"]) == 0
    
    return validation_results


def validate_task_13_requirements(validation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that task 13 requirements are covered by test classes"""
    
    print("\n🎯 Validating Task 13 Requirements Coverage:")
    
    # Required test coverage for task 13
    required_coverage = {
        "multi_agent_collaboration_scenarios": False,
        "end_to_end_message_flow_validation": False,
        "performance_throughput_testing": False,
        "performance_latency_testing": False,
        "stress_testing_high_volume": False,
        "compatibility_testing_platforms": False,
        "success_criteria_validation": False
    }
    
    # Check comprehensive test files for required coverage
    comprehensive_results = validation_results["comprehensive_tests"]
    
    for test_file, result in comprehensive_results.items():
        if not result["importable"]:
            continue
            
        test_classes = result["test_classes"]
        
        # Check for multi-agent collaboration
        if any("MultiAgent" in cls or "Collaboration" in cls for cls in test_classes):
            required_coverage["multi_agent_collaboration_scenarios"] = True
            print("  ✅ Multi-agent collaboration scenarios")
        
        # Check for end-to-end message flow
        if any("EndToEnd" in cls or "MessageFlow" in cls for cls in test_classes):
            required_coverage["end_to_end_message_flow_validation"] = True
            print("  ✅ End-to-end message flow validation")
        
        # Check for performance testing
        if any("Performance" in cls or "Throughput" in cls for cls in test_classes):
            required_coverage["performance_throughput_testing"] = True
            print("  ✅ Performance throughput testing")
        
        # Check for latency testing
        if any("Latency" in cls for cls in test_classes):
            required_coverage["performance_latency_testing"] = True
            print("  ✅ Performance latency testing")
        
        # Check for stress testing
        if any("Stress" in cls or "Volume" in cls or "Scalability" in cls for cls in test_classes):
            required_coverage["stress_testing_high_volume"] = True
            print("  ✅ Stress testing for high-volume scenarios")
        
        # Check for compatibility testing
        if any("Compatibility" in cls or "Platform" in cls for cls in test_classes):
            required_coverage["compatibility_testing_platforms"] = True
            print("  ✅ Compatibility testing across platforms")
        
        # Check for success criteria validation
        if any("Success" in cls or "Criteria" in cls or "Validation" in cls for cls in test_classes):
            required_coverage["success_criteria_validation"] = True
            print("  ✅ Success criteria validation")
    
    # Check for missing coverage
    missing_coverage = [req for req, covered in required_coverage.items() if not covered]
    
    if missing_coverage:
        print("\n  ⚠️  Missing coverage for:")
        for missing in missing_coverage:
            print(f"    - {missing.replace('_', ' ').title()}")
    
    coverage_result = {
        "required_coverage": required_coverage,
        "missing_coverage": missing_coverage,
        "coverage_complete": len(missing_coverage) == 0
    }
    
    return coverage_result


def validate_dependencies() -> Dict[str, Any]:
    """Validate that required dependencies are available"""
    
    print("\n📦 Validating Dependencies:")
    
    required_modules = [
        "pytest",
        "asyncio", 
        "json",
        "redis",
        "pydantic",
        "pathlib",
        "datetime",
        "uuid",
        "statistics",
        "tempfile",
        "unittest.mock"
    ]
    
    optional_modules = [
        "psutil",  # For performance monitoring
        "platform"  # For platform detection
    ]
    
    dependency_results = {
        "required_available": [],
        "required_missing": [],
        "optional_available": [],
        "optional_missing": [],
        "all_required_available": False
    }
    
    # Check required modules
    for module_name in required_modules:
        try:
            __import__(module_name)
            dependency_results["required_available"].append(module_name)
            print(f"  ✅ {module_name}")
        except ImportError:
            dependency_results["required_missing"].append(module_name)
            print(f"  ❌ {module_name} (REQUIRED)")
    
    # Check optional modules
    for module_name in optional_modules:
        try:
            __import__(module_name)
            dependency_results["optional_available"].append(module_name)
            print(f"  ✅ {module_name} (optional)")
        except ImportError:
            dependency_results["optional_missing"].append(module_name)
            print(f"  ⚠️  {module_name} (optional, recommended for full functionality)")
    
    dependency_results["all_required_available"] = len(dependency_results["required_missing"]) == 0
    
    return dependency_results


def main():
    """Main validation function"""
    
    print("🚀 Beast Mode Agent Collaboration Network")
    print("   Comprehensive Integration Test Suite Validation")
    print("=" * 60)
    
    # Validate test suite
    validation_results = validate_comprehensive_test_suite()
    
    # Validate task 13 requirements coverage
    coverage_results = validate_task_13_requirements(validation_results)
    
    # Validate dependencies
    dependency_results = validate_dependencies()
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    summary = validation_results["summary"]
    print(f"\n📁 Test Files:")
    print(f"  Total files: {summary['total_files']}")
    print(f"  Files exist: {summary['files_exist']}")
    print(f"  Files importable: {summary['files_importable']}")
    print(f"  Test classes: {summary['total_test_classes']}")
    print(f"  Test methods: {summary['total_test_methods']}")
    
    print(f"\n🎯 Task 13 Requirements:")
    print(f"  Coverage complete: {'✅ YES' if coverage_results['coverage_complete'] else '❌ NO'}")
    if not coverage_results['coverage_complete']:
        print(f"  Missing: {len(coverage_results['missing_coverage'])} requirements")
    
    print(f"\n📦 Dependencies:")
    print(f"  Required available: {len(dependency_results['required_available'])}/{len(dependency_results['required_available']) + len(dependency_results['required_missing'])}")
    print(f"  All required available: {'✅ YES' if dependency_results['all_required_available'] else '❌ NO'}")
    
    # Overall validation status
    overall_success = (
        validation_results["summary"]["validation_passed"] and
        coverage_results["coverage_complete"] and
        dependency_results["all_required_available"]
    )
    
    print(f"\n🏁 Overall Validation: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    
    if overall_success:
        print("\n🎉 Comprehensive Integration Test Suite is ready!")
        print("   You can now run the full test suite with:")
        print("   python tests/integration/run_comprehensive_tests.py")
    else:
        print("\n⚠️  Please address the issues above before running the test suite.")
        
        if validation_results["errors"]:
            print("\n🔧 Errors to fix:")
            for error in validation_results["errors"][:5]:  # Show first 5 errors
                print(f"  - {error}")
    
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()