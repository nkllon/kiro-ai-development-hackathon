"""
Test coverage validation for RDI compliance.

This module implements test coverage analysis against the 96.7% baseline
and specific analysis for failing tests identified in Phase 2.
"""

import re
import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity
from ...utils.path_normalizer import safe_relative_to


class TestType(Enum):
    """Types of tests that can be analyzed."""
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    SYSTEM = "system"


@dataclass
class TestFile:
    """Represents a test file and its metadata."""
    file_path: str
    test_functions: List[str]
    test_type: TestType
    coverage_percentage: float
    lines_covered: int
    lines_total: int
    missing_lines: List[int]


@dataclass
class FailingTest:
    """Represents a failing test with details."""
    test_name: str
    test_file: str
    error_message: str
    error_type: str
    stack_trace: Optional[str]
    requirements_covered: List[str]


@dataclass
class CoverageReport:
    """Comprehensive test coverage report."""
    overall_coverage: float
    baseline_coverage: float
    coverage_adequate: bool
    total_lines: int
    covered_lines: int
    test_files: List[TestFile]
    failing_tests: List[FailingTest]
    missing_test_files: List[str]
    uncovered_modules: List[str]


@dataclass
class TestCoverageResult:
    """Results of test coverage validation."""
    coverage_report: CoverageReport
    meets_baseline: bool
    coverage_gap: float
    issues: List[ComplianceIssue]


class TestCoverageValidator(ComplianceValidator):
    """
    Validates test coverage against baseline and identifies failing tests.
    
    This class validates that:
    1. Test coverage meets the 96.7% baseline
    2. All failing tests are identified and analyzed
    3. Test coverage is adequate for requirements
    4. Missing test files are identified
    """
    
    def __init__(self, repository_path: str, baseline_coverage: float = 96.7):
        """
        Initialize the TestCoverageValidator.
        
        Args:
            repository_path: Path to the repository root
            baseline_coverage: Baseline coverage percentage to validate against
        """
        self.repository_path = Path(repository_path)
        self.baseline_coverage = baseline_coverage
        self.coverage_cache: Optional[CoverageReport] = None
        
        # Known failing tests from Phase 2 lessons learned
        self.known_failing_tests = [
            "test_advanced_query_engine",
            "test_registry_manager", 
            "test_infrastructure",
            "test_mpm_dashboard_fixed",
            "test_rm_rdi_analysis_basic",
            "test_task17_components",
            "test_final_validation_assessment"
        ]
    
    def validate(self, target: str) -> List[ComplianceIssue]:
        """
        Validate test coverage for the given target.
        
        Args:
            target: Path to analyze (file or directory)
            
        Returns:
            List of compliance issues found
        """
        target_path = Path(target) if isinstance(target, str) else target
        
        # Generate coverage report if not cached
        if self.coverage_cache is None:
            self.coverage_cache = self._generate_coverage_report(target_path)
        
        # Analyze coverage
        coverage_result = self._analyze_coverage()
        
        return coverage_result.issues
    
    def get_validator_name(self) -> str:
        """Get the name of this validator."""
        return "TestCoverageValidator"
    
    def analyze_coverage(self, target_path: Optional[str] = None) -> TestCoverageResult:
        """
        Perform comprehensive test coverage analysis.
        
        Args:
            target_path: Specific path to analyze, or None for full repository
            
        Returns:
            Detailed coverage analysis results
        """
        analysis_path = Path(target_path) if target_path else self.repository_path
        
        if self.coverage_cache is None:
            self.coverage_cache = self._generate_coverage_report(analysis_path)
        
        return self._analyze_coverage()
    
    def _generate_coverage_report(self, target_path: Path) -> CoverageReport:
        """
        Generate comprehensive coverage report.
        
        Args:
            target_path: Path to analyze for coverage
            
        Returns:
            Comprehensive coverage report
        """
        # Try to run coverage analysis
        coverage_data = self._run_coverage_analysis(target_path)
        
        # Find test files
        test_files = self._find_test_files(target_path)
        
        # Identify failing tests
        failing_tests = self._identify_failing_tests(target_path)
        
        # Find missing test files
        missing_test_files = self._find_missing_test_files(target_path)
        
        # Find uncovered modules
        uncovered_modules = self._find_uncovered_modules(target_path, coverage_data)
        
        # Calculate overall coverage
        overall_coverage = coverage_data.get('overall_coverage', 0.0)
        total_lines = coverage_data.get('total_lines', 0)
        covered_lines = coverage_data.get('covered_lines', 0)
        
        return CoverageReport(
            overall_coverage=overall_coverage,
            baseline_coverage=self.baseline_coverage,
            coverage_adequate=overall_coverage >= self.baseline_coverage,
            total_lines=total_lines,
            covered_lines=covered_lines,
            test_files=test_files,
            failing_tests=failing_tests,
            missing_test_files=missing_test_files,
            uncovered_modules=uncovered_modules
        )
    
    def _run_coverage_analysis(self, target_path: Path) -> Dict[str, Any]:
        """
        Run coverage analysis using pytest-cov or coverage.py.
        
        Args:
            target_path: Path to analyze
            
        Returns:
            Coverage data dictionary
        """
        coverage_data = {
            'overall_coverage': 0.0,
            'total_lines': 0,
            'covered_lines': 0,
            'file_coverage': {}
        }
        
        try:
            # Try to run pytest with coverage
            result = subprocess.run([
                'python', '-m', 'pytest', 
                '--cov=src',
                '--cov-report=json',
                '--cov-report=term-missing',
                str(target_path / 'tests') if (target_path / 'tests').exists() else 'tests'
            ], 
            capture_output=True, 
            text=True, 
            cwd=self.repository_path,
            timeout=300
            )
            
            # Look for coverage.json file
            coverage_json_path = self.repository_path / 'coverage.json'
            if coverage_json_path.exists():
                with open(coverage_json_path, 'r') as f:
                    coverage_json = json.load(f)
                    
                coverage_data['overall_coverage'] = coverage_json.get('totals', {}).get('percent_covered', 0.0)
                coverage_data['total_lines'] = coverage_json.get('totals', {}).get('num_statements', 0)
                coverage_data['covered_lines'] = coverage_json.get('totals', {}).get('covered_lines', 0)
                coverage_data['file_coverage'] = coverage_json.get('files', {})
                
                # Clean up the coverage file
                coverage_json_path.unlink()
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            # Fallback to manual analysis if coverage tools fail
            print(f"Coverage analysis failed: {e}")
            coverage_data = self._manual_coverage_analysis(target_path)
        
        return coverage_data
    
    def _manual_coverage_analysis(self, target_path: Path) -> Dict[str, Any]:
        """
        Perform manual coverage analysis when automated tools fail.
        
        Args:
            target_path: Path to analyze
            
        Returns:
            Coverage data dictionary
        """
        # Find all Python source files
        src_files = list(self.repository_path.glob('src/**/*.py'))
        test_files = list(self.repository_path.glob('tests/**/*.py'))
        
        total_lines = 0
        covered_lines = 0
        file_coverage = {}
        
        for src_file in src_files:
            try:
                with open(src_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Count non-empty, non-comment lines
                code_lines = [
                    line for line in lines 
                    if line.strip() and not line.strip().startswith('#')
                ]
                
                file_total = len(code_lines)
                total_lines += file_total
                
                # Estimate coverage based on test file existence
                relative_path = safe_relative_to(src_file, self.repository_path)
                if relative_path is None:
                    continue  # Skip files that can't be made relative
                test_file_exists = self._has_corresponding_test_file(src_file, test_files)
                
                if test_file_exists:
                    # Assume 80% coverage if test file exists
                    file_covered = int(file_total * 0.8)
                else:
                    # Assume 20% coverage if no test file
                    file_covered = int(file_total * 0.2)
                
                covered_lines += file_covered
                file_coverage[str(relative_path)] = {
                    'total_lines': file_total,
                    'covered_lines': file_covered,
                    'coverage_percent': (file_covered / file_total * 100) if file_total > 0 else 0
                }
                
            except Exception as e:
                print(f"Error analyzing {src_file}: {e}")
        
        overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        
        return {
            'overall_coverage': overall_coverage,
            'total_lines': total_lines,
            'covered_lines': covered_lines,
            'file_coverage': file_coverage
        }
    
    def _has_corresponding_test_file(self, src_file: Path, test_files: List[Path]) -> bool:
        """
        Check if a source file has a corresponding test file.
        
        Args:
            src_file: Source file to check
            test_files: List of test files
            
        Returns:
            True if corresponding test file exists
        """
        src_name = src_file.stem
        
        # Look for test files that might test this source file
        for test_file in test_files:
            test_name = test_file.stem
            if (src_name in test_name or 
                test_name.replace('test_', '') == src_name or
                test_name == f'test_{src_name}'):
                return True
        
        return False
    
    def _find_test_files(self, target_path: Path) -> List[TestFile]:
        """
        Find and analyze all test files.
        
        Args:
            target_path: Path to search for test files
            
        Returns:
            List of test files with metadata
        """
        test_files = []
        
        # Find test files
        test_patterns = ['**/test_*.py', '**/tests.py', '**/*_test.py']
        found_files = []
        
        for pattern in test_patterns:
            found_files.extend(self.repository_path.glob(pattern))
        
        for test_file in found_files:
            try:
                test_functions = self._extract_test_functions(test_file)
                test_type = self._determine_test_type(test_file)
                
                test_files.append(TestFile(
                    file_path=str(test_file),
                    test_functions=test_functions,
                    test_type=test_type,
                    coverage_percentage=0.0,  # Will be filled by coverage analysis
                    lines_covered=0,
                    lines_total=0,
                    missing_lines=[]
                ))
                
            except Exception as e:
                print(f"Error analyzing test file {test_file}: {e}")
        
        return test_files
    
    def _extract_test_functions(self, test_file: Path) -> List[str]:
        """
        Extract test function names from a test file.
        
        Args:
            test_file: Path to the test file
            
        Returns:
            List of test function names
        """
        test_functions = []
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find test functions
            test_matches = re.findall(r'def\s+(test_\w+)', content)
            test_functions.extend(test_matches)
            
            # Also find test methods in test classes
            class_matches = re.findall(r'class\s+(Test\w+)', content)
            for class_name in class_matches:
                # Find methods in test classes
                class_pattern = rf'class\s+{class_name}.*?(?=class|\Z)'
                class_match = re.search(class_pattern, content, re.DOTALL)
                if class_match:
                    class_content = class_match.group(0)
                    method_matches = re.findall(r'def\s+(test_\w+)', class_content)
                    test_functions.extend([f"{class_name}.{method}" for method in method_matches])
            
        except Exception as e:
            print(f"Error extracting test functions from {test_file}: {e}")
        
        return test_functions
    
    def _determine_test_type(self, test_file: Path) -> TestType:
        """
        Determine the type of test based on file path and content.
        
        Args:
            test_file: Path to the test file
            
        Returns:
            Test type classification
        """
        file_path_str = str(test_file).lower()
        
        if 'integration' in file_path_str:
            return TestType.INTEGRATION
        elif 'functional' in file_path_str:
            return TestType.FUNCTIONAL
        elif 'system' in file_path_str:
            return TestType.SYSTEM
        else:
            return TestType.UNIT
    
    def _identify_failing_tests(self, target_path: Path) -> List[FailingTest]:
        """
        Identify failing tests by running the test suite.
        
        Args:
            target_path: Path to analyze
            
        Returns:
            List of failing tests with details
        """
        failing_tests = []
        
        try:
            # Run pytest to identify failing tests
            result = subprocess.run([
                'python', '-m', 'pytest', 
                '--tb=short',
                '--json-report',
                '--json-report-file=test_report.json',
                str(target_path / 'tests') if (target_path / 'tests').exists() else 'tests'
            ], 
            capture_output=True, 
            text=True, 
            cwd=self.repository_path,
            timeout=300
            )
            
            # Parse test report
            report_path = self.repository_path / 'test_report.json'
            if report_path.exists():
                with open(report_path, 'r') as f:
                    test_report = json.load(f)
                
                # Extract failing tests
                for test in test_report.get('tests', []):
                    if test.get('outcome') == 'failed':
                        failing_tests.append(FailingTest(
                            test_name=test.get('nodeid', ''),
                            test_file=test.get('file', ''),
                            error_message=test.get('call', {}).get('longrepr', ''),
                            error_type='test_failure',
                            stack_trace=test.get('call', {}).get('longrepr', ''),
                            requirements_covered=[]  # Would need to be extracted from test
                        ))
                
                # Clean up report file
                report_path.unlink()
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            # Fallback to known failing tests
            print(f"Test execution failed: {e}")
            for test_name in self.known_failing_tests:
                failing_tests.append(FailingTest(
                    test_name=test_name,
                    test_file=f"tests/{test_name}.py",
                    error_message="Known failing test from Phase 2",
                    error_type="known_failure",
                    stack_trace=None,
                    requirements_covered=[]
                ))
        
        return failing_tests
    
    def _find_missing_test_files(self, target_path: Path) -> List[str]:
        """
        Find source files that don't have corresponding test files.
        
        Args:
            target_path: Path to analyze
            
        Returns:
            List of source files missing test coverage
        """
        missing_test_files = []
        
        # Find all source files
        src_files = list(self.repository_path.glob('src/**/*.py'))
        test_files = list(self.repository_path.glob('tests/**/*.py'))
        
        for src_file in src_files:
            # Skip __init__.py files
            if src_file.name == '__init__.py':
                continue
            
            if not self._has_corresponding_test_file(src_file, test_files):
                relative_path = safe_relative_to(src_file, self.repository_path)
                if relative_path is not None:
                    missing_test_files.append(str(relative_path))
        
        return missing_test_files
    
    def _find_uncovered_modules(self, target_path: Path, coverage_data: Dict[str, Any]) -> List[str]:
        """
        Find modules with low or no test coverage.
        
        Args:
            target_path: Path to analyze
            coverage_data: Coverage analysis data
            
        Returns:
            List of uncovered modules
        """
        uncovered_modules = []
        
        file_coverage = coverage_data.get('file_coverage', {})
        
        for file_path, coverage_info in file_coverage.items():
            coverage_percent = coverage_info.get('coverage_percent', 0)
            if coverage_percent < 50.0:  # Consider <50% as uncovered
                uncovered_modules.append(file_path)
        
        return uncovered_modules
    
    def _analyze_coverage(self) -> TestCoverageResult:
        """
        Analyze coverage report and generate compliance issues.
        
        Returns:
            Test coverage analysis results
        """
        if not self.coverage_cache:
            raise ValueError("Coverage report not generated")
        
        report = self.coverage_cache
        meets_baseline = report.overall_coverage >= self.baseline_coverage
        coverage_gap = max(0, self.baseline_coverage - report.overall_coverage)
        
        # Generate compliance issues
        issues = self._generate_coverage_issues(report, meets_baseline, coverage_gap)
        
        return TestCoverageResult(
            coverage_report=report,
            meets_baseline=meets_baseline,
            coverage_gap=coverage_gap,
            issues=issues
        )
    
    def _generate_coverage_issues(
        self, 
        report: CoverageReport, 
        meets_baseline: bool, 
        coverage_gap: float
    ) -> List[ComplianceIssue]:
        """
        Generate compliance issues based on coverage analysis.
        
        Args:
            report: Coverage report
            meets_baseline: Whether coverage meets baseline
            coverage_gap: Gap between current and baseline coverage
            
        Returns:
            List of compliance issues
        """
        issues = []
        
        # Issue for not meeting baseline coverage
        if not meets_baseline:
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.TEST_FAILURE,
                severity=IssueSeverity.HIGH if coverage_gap > 10 else IssueSeverity.MEDIUM,
                description=f"Test coverage {report.overall_coverage:.1f}% below baseline {self.baseline_coverage}%",
                affected_files=[],
                remediation_steps=[
                    f"Increase test coverage by {coverage_gap:.1f}% to meet baseline",
                    "Add tests for uncovered modules and functions",
                    "Focus on critical path testing",
                    f"Target: Achieve {self.baseline_coverage}% coverage (currently {report.overall_coverage:.1f}%)"
                ],
                estimated_effort="High",
                blocking_merge=coverage_gap > 10,
                metadata={
                    "current_coverage": report.overall_coverage,
                    "baseline_coverage": self.baseline_coverage,
                    "coverage_gap": coverage_gap
                }
            ))
        
        # Issue for failing tests
        if report.failing_tests:
            failing_test_names = [test.test_name for test in report.failing_tests]
            
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.TEST_FAILURE,
                severity=IssueSeverity.HIGH,
                description=f"Found {len(report.failing_tests)} failing tests",
                affected_files=list(set(test.test_file for test in report.failing_tests)),
                remediation_steps=[
                    f"Fix failing tests: {', '.join(failing_test_names[:5])}{'...' if len(failing_test_names) > 5 else ''}",
                    "Investigate test failures and fix underlying issues",
                    "Update tests if requirements have changed",
                    "Ensure all tests pass before merging"
                ],
                estimated_effort="High",
                blocking_merge=True,
                metadata={
                    "failing_tests": failing_test_names,
                    "count": len(report.failing_tests)
                }
            ))
        
        # Issue for missing test files
        if report.missing_test_files:
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.TEST_FAILURE,
                severity=IssueSeverity.MEDIUM,
                description=f"Found {len(report.missing_test_files)} source files without test coverage",
                affected_files=report.missing_test_files,
                remediation_steps=[
                    f"Create test files for uncovered modules: {', '.join(report.missing_test_files[:3])}{'...' if len(report.missing_test_files) > 3 else ''}",
                    "Implement comprehensive test suites for new modules",
                    "Follow test-driven development practices"
                ],
                estimated_effort="Medium",
                blocking_merge=len(report.missing_test_files) > 10,
                metadata={
                    "missing_test_files": report.missing_test_files,
                    "count": len(report.missing_test_files)
                }
            ))
        
        # Issue for uncovered modules
        if report.uncovered_modules:
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.TEST_FAILURE,
                severity=IssueSeverity.MEDIUM,
                description=f"Found {len(report.uncovered_modules)} modules with low test coverage (<50%)",
                affected_files=report.uncovered_modules,
                remediation_steps=[
                    f"Improve test coverage for modules: {', '.join(report.uncovered_modules[:3])}{'...' if len(report.uncovered_modules) > 3 else ''}",
                    "Add unit tests for uncovered functions and methods",
                    "Focus on edge cases and error conditions"
                ],
                estimated_effort="Medium",
                blocking_merge=False,
                metadata={
                    "uncovered_modules": report.uncovered_modules,
                    "count": len(report.uncovered_modules)
                }
            ))
        
        return issues