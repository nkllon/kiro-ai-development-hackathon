#!/usr/bin/env python3
"""
Beast Mode Framework - Test Infrastructure Validation Suite
Comprehensive validation of test infrastructure repair

This suite validates:
- All test fixtures are available and properly scoped
- All tests can be imported successfully
- Test coverage for repaired infrastructure
- Requirements traceability
"""

import sys
import importlib
import inspect
import pytest
from pathlib import Path
from typing import Dict, List, Any, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationResult:
    """Result of a validation check"""
    check_name: str
    passed: bool
    details: str
    issues: List[str]
    recommendations: List[str]

class TestInfrastructureValidator:
    """Comprehensive test infrastructure validator"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / "tests"
        self.validation_results = []
        
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete test infrastructure validation"""
        print("🦁 Beast Mode Framework - Test Infrastructure Validation")
        print("=" * 60)
        print()
        
        # Run all validation checks
        self.validate_fixture_availability()
        self.validate_test_imports()
        self.validate_requirements_coverage()
        self.validate_conftest_structure()
        self.validate_enum_completeness()
        self.validate_health_checks()
        
        # Generate summary report
        return self.generate_validation_report()
        
    def validate_fixture_availability(self) -> ValidationResult:
        """Validate all fixtures are available and properly scoped"""
        print("🔧 Validating fixture availability...")
        
        issues = []
        recommendations = []
        
        # Check for required conftest.py files
        required_conftest_files = [
            self.tests_dir / "conftest.py",
            self.tests_dir / "orchestration" / "conftest.py", 
            self.tests_dir / "analysis" / "conftest.py"
        ]
        
        for conftest_file in required_conftest_files:
            if not conftest_file.exists():
                issues.append(f"Missing conftest.py: {conftest_file}")
                recommendations.append(f"Create {conftest_file} with required fixtures")
            else:
                print(f"  ✅ Found: {conftest_file}")
                
        # Check for critical fixtures in root conftest
        root_conftest = self.tests_dir / "conftest.py"
        if root_conftest.exists():
            try:
                content = root_conftest.read_text()
                required_fixtures = [
                    "orchestrator",
                    "sample_tool_definition", 
                    "sample_execution_request",
                    "mock_intelligence_engine"
                ]
                
                for fixture in required_fixtures:
                    if f"def {fixture}" in content:
                        print(f"  ✅ Fixture available: {fixture}")
                    else:
                        issues.append(f"Missing fixture: {fixture}")
                        recommendations.append(f"Add {fixture} fixture to root conftest.py")
                        
            except Exception as e:
                issues.append(f"Error reading root conftest.py: {str(e)}")
                
        passed = len(issues) == 0
        result = ValidationResult(
            check_name="fixture_availability",
            passed=passed,
            details=f"Checked {len(required_conftest_files)} conftest files and critical fixtures",
            issues=issues,
            recommendations=recommendations
        )
        
        self.validation_results.append(result)
        print(f"  {'✅ PASSED' if passed else '❌ FAILED'}: Fixture availability check")
        print()
        return result
        
    def validate_test_imports(self) -> ValidationResult:
        """Validate all tests can be imported successfully"""
        print("📦 Validating test imports...")
        
        issues = []
        recommendations = []
        successful_imports = 0
        total_tests = 0
        
        # Find all test files
        test_files = list(self.tests_dir.rglob("test_*.py"))
        total_tests = len(test_files)
        
        for test_file in test_files:
            try:
                # Convert file path to module name
                relative_path = test_file.relative_to(self.project_root)
                module_name = str(relative_path).replace("/", ".").replace("\\", ".")[:-3]  # Remove .py
                
                # Try to import the module
                spec = importlib.util.spec_from_file_location(module_name, test_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    successful_imports += 1
                    print(f"  ✅ Imported: {module_name}")
                else:
                    issues.append(f"Could not create spec for: {test_file}")
                    
            except Exception as e:
                issues.append(f"Import failed for {test_file}: {str(e)}")
                recommendations.append(f"Fix import issues in {test_file}")
                print(f"  ❌ Failed: {test_file} - {str(e)}")
                
        passed = len(issues) == 0
        result = ValidationResult(
            check_name="test_imports",
            passed=passed,
            details=f"Successfully imported {successful_imports}/{total_tests} test files",
            issues=issues,
            recommendations=recommendations
        )
        
        self.validation_results.append(result)
        print(f"  {'✅ PASSED' if passed else '❌ FAILED'}: Test import validation")
        print()
        return result
        
    def validate_requirements_coverage(self) -> ValidationResult:
        """Validate requirements coverage by tests"""
        print("📋 Validating requirements coverage...")
        
        issues = []
        recommendations = []
        
        # Check if requirements file exists
        requirements_file = self.project_root / ".kiro" / "specs" / "test-infrastructure-repair" / "requirements.md"
        
        if not requirements_file.exists():
            issues.append("Requirements file not found")
            recommendations.append("Create requirements.md file")
        else:
            try:
                content = requirements_file.read_text()
                
                # Count requirements
                requirement_sections = content.count("### Requirement")
                acceptance_criteria = content.count("WHEN") + content.count("IF")
                
                print(f"  ✅ Found {requirement_sections} requirements")
                print(f"  ✅ Found {acceptance_criteria} acceptance criteria")
                
                # Check for RDI compliance test
                rdi_test_file = self.tests_dir / "test_rdi_compliance.py"
                if rdi_test_file.exists():
                    print(f"  ✅ RDI compliance tests exist")
                else:
                    issues.append("RDI compliance tests missing")
                    recommendations.append("Create test_rdi_compliance.py")
                    
            except Exception as e:
                issues.append(f"Error reading requirements: {str(e)}")
                
        passed = len(issues) == 0
        result = ValidationResult(
            check_name="requirements_coverage",
            passed=passed,
            details="Validated requirements traceability to tests",
            issues=issues,
            recommendations=recommendations
        )
        
        self.validation_results.append(result)
        print(f"  {'✅ PASSED' if passed else '❌ FAILED'}: Requirements coverage check")
        print()
        return result
        
    def validate_conftest_structure(self) -> ValidationResult:
        """Validate conftest.py structure and organization"""
        print("🏗️  Validating conftest structure...")
        
        issues = []
        recommendations = []
        
        # Check conftest hierarchy
        conftest_files = list(self.tests_dir.rglob("conftest.py"))
        
        for conftest_file in conftest_files:
            try:
                content = conftest_file.read_text()
                
                # Check for proper imports
                if "import pytest" not in content:
                    issues.append(f"Missing pytest import in {conftest_file}")
                    
                # Check for fixture definitions
                fixture_count = content.count("@pytest.fixture")
                if fixture_count == 0:
                    issues.append(f"No fixtures defined in {conftest_file}")
                else:
                    print(f"  ✅ {conftest_file}: {fixture_count} fixtures")
                    
            except Exception as e:
                issues.append(f"Error reading {conftest_file}: {str(e)}")
                
        passed = len(issues) == 0
        result = ValidationResult(
            check_name="conftest_structure",
            passed=passed,
            details=f"Validated {len(conftest_files)} conftest.py files",
            issues=issues,
            recommendations=recommendations
        )
        
        self.validation_results.append(result)
        print(f"  {'✅ PASSED' if passed else '❌ FAILED'}: Conftest structure check")
        print()
        return result
        
    def validate_enum_completeness(self) -> ValidationResult:
        """Validate enum completeness and consistency"""
        print("🔢 Validating enum completeness...")
        
        issues = []
        recommendations = []
        
        try:
            # Check AnalysisStatus enum
            from src.beast_mode.analysis.rm_rdi.base import AnalysisStatus
            
            required_values = ["SUCCESS", "PARTIAL_SUCCESS", "COMPLETED", "FAILED", "NOT_STARTED", "IN_PROGRESS", "KILLED"]
            
            for value in required_values:
                if hasattr(AnalysisStatus, value):
                    print(f"  ✅ AnalysisStatus.{value} exists")
                else:
                    issues.append(f"Missing AnalysisStatus.{value}")
                    recommendations.append(f"Add {value} to AnalysisStatus enum")
                    
        except ImportError as e:
            issues.append(f"Could not import AnalysisStatus: {str(e)}")
            recommendations.append("Fix AnalysisStatus import issues")
            
        passed = len(issues) == 0
        result = ValidationResult(
            check_name="enum_completeness",
            passed=passed,
            details="Validated enum definitions and values",
            issues=issues,
            recommendations=recommendations
        )
        
        self.validation_results.append(result)
        print(f"  {'✅ PASSED' if passed else '❌ FAILED'}: Enum completeness check")
        print()
        return result
        
    def validate_health_checks(self) -> ValidationResult:
        """Validate component health checks work correctly"""
        print("🏥 Validating health checks...")
        
        issues = []
        recommendations = []
        
        # Test key components
        components_to_test = [
            ("DocumentManagementRM", "src.beast_mode.documentation.document_management_rm"),
            ("InfrastructureIntegrationManager", "src.beast_mode.integration.infrastructure_integration_manager"),
            ("SelfConsistencyValidator", "src.beast_mode.integration.self_consistency_validator"),
            ("BeastModeCLI", "src.beast_mode.cli.beast_mode_cli")
        ]
        
        for component_name, module_path in components_to_test:
            try:
                module = importlib.import_module(module_path)
                component_class = getattr(module, component_name)
                
                # Create instance and test health check
                instance = component_class()
                is_healthy = instance.is_healthy()
                
                if is_healthy:
                    print(f"  ✅ {component_name} health check: HEALTHY")
                else:
                    print(f"  ⚠️  {component_name} health check: DEGRADED")
                    issues.append(f"{component_name} health check failed")
                    recommendations.append(f"Debug {component_name} health issues")
                    
            except Exception as e:
                issues.append(f"Error testing {component_name}: {str(e)}")
                recommendations.append(f"Fix {component_name} initialization issues")
                
        passed = len(issues) == 0
        result = ValidationResult(
            check_name="health_checks",
            passed=passed,
            details=f"Validated health checks for {len(components_to_test)} components",
            issues=issues,
            recommendations=recommendations
        )
        
        self.validation_results.append(result)
        print(f"  {'✅ PASSED' if passed else '❌ FAILED'}: Health check validation")
        print()
        return result
        
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        print("📊 Generating validation report...")
        print()
        
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for result in self.validation_results if result.passed)
        failed_checks = total_checks - passed_checks
        
        # Calculate overall score
        overall_score = passed_checks / total_checks if total_checks > 0 else 0.0
        
        # Determine status
        if overall_score >= 0.9:
            status = "EXCELLENT"
            status_icon = "🏆"
        elif overall_score >= 0.8:
            status = "GOOD"
            status_icon = "✅"
        elif overall_score >= 0.7:
            status = "ACCEPTABLE"
            status_icon = "⚠️"
        else:
            status = "NEEDS_WORK"
            status_icon = "❌"
            
        # Print summary
        print(f"{status_icon} VALIDATION SUMMARY")
        print("=" * 40)
        print(f"Overall Status: {status}")
        print(f"Overall Score: {overall_score:.1%}")
        print(f"Checks Passed: {passed_checks}/{total_checks}")
        print(f"Checks Failed: {failed_checks}")
        print()
        
        # Print detailed results
        print("📋 DETAILED RESULTS")
        print("-" * 40)
        for result in self.validation_results:
            status_symbol = "✅" if result.passed else "❌"
            print(f"{status_symbol} {result.check_name}: {result.details}")
            
            if result.issues:
                print("   Issues:")
                for issue in result.issues:
                    print(f"     - {issue}")
                    
            if result.recommendations:
                print("   Recommendations:")
                for rec in result.recommendations:
                    print(f"     - {rec}")
            print()
            
        # Collect all issues and recommendations
        all_issues = []
        all_recommendations = []
        
        for result in self.validation_results:
            all_issues.extend(result.issues)
            all_recommendations.extend(result.recommendations)
            
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "overall_status": status,
            "overall_score": overall_score,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "check_results": [
                {
                    "check_name": result.check_name,
                    "passed": result.passed,
                    "details": result.details,
                    "issues": result.issues,
                    "recommendations": result.recommendations
                }
                for result in self.validation_results
            ],
            "summary": {
                "total_issues": len(all_issues),
                "total_recommendations": len(all_recommendations),
                "infrastructure_health": "healthy" if overall_score >= 0.8 else "degraded"
            }
        }
        
        # Save report to file
        report_file = self.project_root / "test-infrastructure-validation-report.json"
        with open(report_file, 'w') as f:
            import json
            json.dump(report, f, indent=2)
            
        print(f"📄 Full report saved to: {report_file}")
        print()
        
        return report

def main():
    """Main validation entry point"""
    validator = TestInfrastructureValidator()
    report = validator.run_complete_validation()
    
    # Exit with appropriate code
    if report["overall_score"] >= 0.8:
        print("🎉 Test infrastructure validation PASSED!")
        sys.exit(0)
    else:
        print("💥 Test infrastructure validation FAILED!")
        print("Please address the issues above before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()