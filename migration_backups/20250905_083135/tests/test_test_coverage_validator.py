"""
Unit tests for TestCoverageValidator class.

Tests test coverage validation functionality.
"""

import pytest
import tempfile
import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.beast_mode.compliance.rdi.test_coverage_validator import (
    TestCoverageValidator,
    TestFile,
    FailingTest,
    CoverageReport,
    TestType,
    TestCoverageResult
)
from src.beast_mode.compliance.models import ComplianceIssueType, IssueSeverity


class TestTestCoverageValidator:
    """Test cases for TestCoverageValidator class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            
            # Create source files
            (repo_path / "src").mkdir()
            (repo_path / "src" / "module1.py").write_text("""
def function1():
    '''Function 1'''
    return True

def function2():
    '''Function 2'''
    return False

class Class1:
    def method1(self):
        return "method1"
    
    def method2(self):
        return "method2"
""")
            
            (repo_path / "src" / "module2.py").write_text("""
def uncovered_function():
    '''This function has no tests'''
    return "uncovered"
""")
            
            # Create test files
            (repo_path / "tests").mkdir()
            (repo_path / "tests" / "test_module1.py").write_text("""
import pytest
from src.module1 import function1, Class1

def test_function1():
    '''Test function1'''
    assert function1() is True

class TestClass1:
    def test_method1(self):
        '''Test method1'''
        obj = Class1()
        assert obj.method1() == "method1"
    
    def test_method2(self):
        '''Test method2'''
        obj = Class1()
        assert obj.method2() == "method2"

def test_failing_test():
    '''This test should fail'''
    assert False, "Intentional failure"
""")
            
            # Create integration test directory and file
            (repo_path / "tests" / "integration").mkdir(parents=True)
            (repo_path / "tests" / "integration" / "test_integration.py").write_text("""
def test_integration_scenario():
    '''Integration test'''
    assert True
""")
            
            yield repo_path
    
    @pytest.fixture
    def validator(self, temp_repo):
        """Create TestCoverageValidator instance for testing."""
        return TestCoverageValidator(str(temp_repo), baseline_coverage=80.0)
    
    def test_init(self, temp_repo):
        """Test TestCoverageValidator initialization."""
        validator = TestCoverageValidator(str(temp_repo), baseline_coverage=85.0)
        
        assert validator.repository_path == Path(temp_repo)
        assert validator.baseline_coverage == 85.0
        assert validator.coverage_cache is None
        assert len(validator.known_failing_tests) > 0
    
    def test_get_validator_name(self, validator):
        """Test validator name retrieval."""
        assert validator.get_validator_name() == "TestCoverageValidator"
    
    def test_find_test_files(self, validator, temp_repo):
        """Test finding and analyzing test files."""
        test_files = validator._find_test_files(temp_repo)
        
        assert len(test_files) >= 2
        
        # Check test file details
        test_file_names = [Path(tf.file_path).name for tf in test_files]
        assert "test_module1.py" in test_file_names
        assert "test_integration.py" in test_file_names
        
        # Check test functions are extracted
        module1_test = next(tf for tf in test_files if "test_module1.py" in tf.file_path)
        assert len(module1_test.test_functions) >= 3
        assert "test_function1" in module1_test.test_functions
        assert "TestClass1.test_method1" in module1_test.test_functions
    
    def test_extract_test_functions(self, validator, temp_repo):
        """Test extracting test function names from test files."""
        test_file = temp_repo / "tests" / "test_module1.py"
        test_functions = validator._extract_test_functions(test_file)
        
        assert len(test_functions) >= 4
        assert "test_function1" in test_functions
        assert "test_failing_test" in test_functions
        assert "TestClass1.test_method1" in test_functions
        assert "TestClass1.test_method2" in test_functions
    
    def test_determine_test_type(self, validator, temp_repo):
        """Test determining test type from file path."""
        unit_test = temp_repo / "tests" / "test_module1.py"
        assert validator._determine_test_type(unit_test) == TestType.UNIT
        
        integration_test = temp_repo / "tests" / "integration" / "test_integration.py"
        assert validator._determine_test_type(integration_test) == TestType.INTEGRATION
    
    def test_has_corresponding_test_file(self, validator, temp_repo):
        """Test checking if source files have corresponding test files."""
        src_files = list((temp_repo / "src").glob("*.py"))
        test_files = list((temp_repo / "tests").glob("**/*.py"))
        
        module1 = temp_repo / "src" / "module1.py"
        module2 = temp_repo / "src" / "module2.py"
        
        assert validator._has_corresponding_test_file(module1, test_files) is True
        assert validator._has_corresponding_test_file(module2, test_files) is False
    
    def test_find_missing_test_files(self, validator, temp_repo):
        """Test finding source files without test coverage."""
        missing_files = validator._find_missing_test_files(temp_repo)
        
        assert len(missing_files) >= 1
        assert any("module2.py" in file for file in missing_files)
    
    def test_manual_coverage_analysis(self, validator, temp_repo):
        """Test manual coverage analysis fallback."""
        coverage_data = validator._manual_coverage_analysis(temp_repo)
        
        assert 'overall_coverage' in coverage_data
        assert 'total_lines' in coverage_data
        assert 'covered_lines' in coverage_data
        assert 'file_coverage' in coverage_data
        
        assert coverage_data['overall_coverage'] >= 0
        assert coverage_data['total_lines'] > 0
        assert coverage_data['covered_lines'] >= 0
    
    @patch('subprocess.run')
    def test_run_coverage_analysis_success(self, mock_run, validator, temp_repo):
        """Test successful coverage analysis with subprocess."""
        # Mock successful subprocess run
        mock_run.return_value = MagicMock(returncode=0)
        
        # Create mock coverage.json
        coverage_data = {
            "totals": {
                "percent_covered": 85.5,
                "num_statements": 100,
                "covered_lines": 85
            },
            "files": {
                "src/module1.py": {
                    "total_lines": 50,
                    "covered_lines": 45,
                    "coverage_percent": 90.0
                }
            }
        }
        
        coverage_json_path = temp_repo / "coverage.json"
        with open(coverage_json_path, 'w') as f:
            json.dump(coverage_data, f)
        
        result = validator._run_coverage_analysis(temp_repo)
        
        assert result['overall_coverage'] == 85.5
        assert result['total_lines'] == 100
        assert result['covered_lines'] == 85
        assert 'src/module1.py' in result['file_coverage']
    
    @patch('subprocess.run')
    def test_run_coverage_analysis_failure(self, mock_run, validator, temp_repo):
        """Test coverage analysis fallback when subprocess fails."""
        # Mock subprocess failure
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pytest')
        
        result = validator._run_coverage_analysis(temp_repo)
        
        # Should fallback to manual analysis
        assert 'overall_coverage' in result
        assert result['overall_coverage'] >= 0
    
    @patch('subprocess.run')
    def test_identify_failing_tests_success(self, mock_run, validator, temp_repo):
        """Test identifying failing tests with subprocess."""
        # Mock successful test run with failures
        mock_run.return_value = MagicMock(returncode=1)  # Tests failed
        
        # Create mock test report
        test_report = {
            "tests": [
                {
                    "nodeid": "tests/test_module1.py::test_failing_test",
                    "file": "tests/test_module1.py",
                    "outcome": "failed",
                    "call": {
                        "longrepr": "AssertionError: Intentional failure"
                    }
                },
                {
                    "nodeid": "tests/test_module1.py::test_function1",
                    "file": "tests/test_module1.py",
                    "outcome": "passed"
                }
            ]
        }
        
        report_path = temp_repo / "test_report.json"
        with open(report_path, 'w') as f:
            json.dump(test_report, f)
        
        failing_tests = validator._identify_failing_tests(temp_repo)
        
        assert len(failing_tests) >= 1
        assert any("test_failing_test" in test.test_name for test in failing_tests)
    
    @patch('subprocess.run')
    def test_identify_failing_tests_fallback(self, mock_run, validator, temp_repo):
        """Test fallback to known failing tests when subprocess fails."""
        # Mock subprocess failure
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pytest')
        
        failing_tests = validator._identify_failing_tests(temp_repo)
        
        # Should use known failing tests
        assert len(failing_tests) == len(validator.known_failing_tests)
        failing_test_names = [test.test_name for test in failing_tests]
        assert "test_advanced_query_engine" in failing_test_names
    
    def test_find_uncovered_modules(self, validator, temp_repo):
        """Test finding modules with low coverage."""
        coverage_data = {
            'file_coverage': {
                'src/module1.py': {'coverage_percent': 85.0},
                'src/module2.py': {'coverage_percent': 30.0},  # Low coverage
                'src/module3.py': {'coverage_percent': 95.0}
            }
        }
        
        uncovered = validator._find_uncovered_modules(temp_repo, coverage_data)
        
        assert len(uncovered) >= 1
        assert 'src/module2.py' in uncovered
        assert 'src/module1.py' not in uncovered
    
    def test_generate_coverage_report(self, validator, temp_repo):
        """Test generating comprehensive coverage report."""
        with patch.object(validator, '_run_coverage_analysis') as mock_coverage:
            mock_coverage.return_value = {
                'overall_coverage': 75.0,
                'total_lines': 100,
                'covered_lines': 75,
                'file_coverage': {}
            }
            
            report = validator._generate_coverage_report(temp_repo)
            
            assert isinstance(report, CoverageReport)
            assert report.overall_coverage == 75.0
            assert report.baseline_coverage == 80.0
            assert report.coverage_adequate is False  # 75% < 80%
            assert len(report.test_files) >= 2
            assert len(report.missing_test_files) >= 1
    
    def test_analyze_coverage(self, validator):
        """Test coverage analysis and issue generation."""
        # Create mock coverage report
        validator.coverage_cache = CoverageReport(
            overall_coverage=70.0,
            baseline_coverage=80.0,
            coverage_adequate=False,
            total_lines=100,
            covered_lines=70,
            test_files=[],
            failing_tests=[
                FailingTest(
                    test_name="test_failing",
                    test_file="test_file.py",
                    error_message="Test failed",
                    error_type="assertion_error",
                    stack_trace=None,
                    requirements_covered=[]
                )
            ],
            missing_test_files=["src/uncovered.py"],
            uncovered_modules=["src/low_coverage.py"]
        )
        
        result = validator._analyze_coverage()
        
        assert isinstance(result, TestCoverageResult)
        assert result.meets_baseline is False
        assert result.coverage_gap == 10.0
        assert len(result.issues) >= 4  # Coverage, failing tests, missing files, uncovered modules
    
    def test_generate_coverage_issues(self, validator):
        """Test generation of coverage compliance issues."""
        report = CoverageReport(
            overall_coverage=60.0,
            baseline_coverage=80.0,
            coverage_adequate=False,
            total_lines=100,
            covered_lines=60,
            test_files=[],
            failing_tests=[
                FailingTest("test1", "file1.py", "error", "type", None, []),
                FailingTest("test2", "file2.py", "error", "type", None, [])
            ],
            missing_test_files=["src/file1.py", "src/file2.py"],
            uncovered_modules=["src/file3.py"]
        )
        
        issues = validator._generate_coverage_issues(report, False, 20.0)
        
        assert len(issues) == 4  # Coverage, failing tests, missing files, uncovered modules
        
        # Check issue types
        issue_types = [issue.issue_type for issue in issues]
        assert all(issue_type == ComplianceIssueType.TEST_FAILURE for issue_type in issue_types)
        
        # Check severities
        severities = [issue.severity for issue in issues]
        assert IssueSeverity.HIGH in severities
    
    def test_validate_method(self, validator, temp_repo):
        """Test the main validate method."""
        with patch.object(validator, '_generate_coverage_report') as mock_report:
            mock_report.return_value = CoverageReport(
                overall_coverage=85.0,
                baseline_coverage=80.0,
                coverage_adequate=True,
                total_lines=100,
                covered_lines=85,
                test_files=[],
                failing_tests=[],
                missing_test_files=[],
                uncovered_modules=[]
            )
            
            issues = validator.validate(str(temp_repo))
            
            assert isinstance(issues, list)
            # Should have minimal issues for good coverage
            
            # Check issue structure
            for issue in issues:
                assert hasattr(issue, 'issue_type')
                assert hasattr(issue, 'severity')
                assert hasattr(issue, 'description')
                assert hasattr(issue, 'remediation_steps')
    
    def test_analyze_coverage_method(self, validator, temp_repo):
        """Test the analyze_coverage method."""
        with patch.object(validator, '_generate_coverage_report') as mock_report:
            mock_report.return_value = CoverageReport(
                overall_coverage=90.0,
                baseline_coverage=80.0,
                coverage_adequate=True,
                total_lines=100,
                covered_lines=90,
                test_files=[],
                failing_tests=[],
                missing_test_files=[],
                uncovered_modules=[]
            )
            
            result = validator.analyze_coverage(str(temp_repo))
            
            assert isinstance(result, TestCoverageResult)
            assert result.meets_baseline is True
            assert result.coverage_gap == 0.0
            assert len(result.issues) == 0  # No issues for good coverage
    
    def test_empty_repository(self):
        """Test behavior with empty repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = TestCoverageValidator(temp_dir)
            
            with patch.object(validator, '_run_coverage_analysis') as mock_coverage:
                mock_coverage.return_value = {
                    'overall_coverage': 0.0,
                    'total_lines': 0,
                    'covered_lines': 0,
                    'file_coverage': {}
                }
                
                report = validator._generate_coverage_report(Path(temp_dir))
                
                assert report.overall_coverage == 0.0
                assert len(report.test_files) == 0
                assert len(report.missing_test_files) == 0
    
    def test_high_coverage_scenario(self, validator, temp_repo):
        """Test scenario with high coverage meeting baseline."""
        with patch.object(validator, '_run_coverage_analysis') as mock_coverage:
            mock_coverage.return_value = {
                'overall_coverage': 95.0,
                'total_lines': 100,
                'covered_lines': 95,
                'file_coverage': {
                    'src/module1.py': {'coverage_percent': 95.0}
                }
            }
            
            validator.coverage_cache = None  # Reset cache
            result = validator.analyze_coverage(str(temp_repo))
            
            assert result.meets_baseline is True
            assert result.coverage_gap == 0.0
            # Should have minimal issues
    
    def test_custom_baseline_coverage(self, temp_repo):
        """Test validator with custom baseline coverage."""
        validator = TestCoverageValidator(str(temp_repo), baseline_coverage=95.0)
        
        assert validator.baseline_coverage == 95.0
        
        # Test with coverage below custom baseline
        validator.coverage_cache = CoverageReport(
            overall_coverage=90.0,
            baseline_coverage=95.0,
            coverage_adequate=False,
            total_lines=100,
            covered_lines=90,
            test_files=[],
            failing_tests=[],
            missing_test_files=[],
            uncovered_modules=[]
        )
        
        result = validator._analyze_coverage()
        assert result.meets_baseline is False
        assert result.coverage_gap == 5.0


if __name__ == "__main__":
    pytest.main([__file__])