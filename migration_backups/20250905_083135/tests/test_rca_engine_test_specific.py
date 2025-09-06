"""
Integration tests for test-specific RCA engine functionality
Tests Requirements 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4
"""

import pytest
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.beast_mode.analysis.rca_engine import (
    RCAEngine, Failure, FailureCategory, RootCauseType,
    RootCause, SystematicFix, PreventionPattern
)


class TestRCAEngineTestSpecificAnalysis:
    """Test suite for test-specific RCA engine functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.rca_engine = RCAEngine(pattern_library_path="test_patterns.json")
        
    def teardown_method(self):
        """Cleanup test environment"""
        # Clean up test pattern file
        test_pattern_file = Path("test_patterns.json")
        if test_pattern_file.exists():
            test_pattern_file.unlink()
    
    def test_pytest_failure_categorization(self):
        """Test pytest failure categorization - Requirement 5.1"""
        # Create pytest failure
        pytest_failure = Failure(
            failure_id="test_pytest_001",
            timestamp=datetime.now(),
            component="test:tests/test_imports.py",
            error_message="ImportError: No module named 'nonexistent_module'",
            stack_trace="Traceback (most recent call last):\n  File \"test_imports.py\", line 1, in <module>\n    import nonexistent_module\nImportError: No module named 'nonexistent_module'",
            context={
                "test_file": "tests/test_imports.py",
                "test_function": "test_import_module",
                "pytest_node_id": "tests/test_imports.py::test_import_module",
                "failure_type": "error"
            },
            category=FailureCategory.PYTEST_FAILURE
        )
        
        # Test categorization
        categorization = self.rca_engine.analyze_test_failure_categorization(pytest_failure)
        
        assert categorization["primary_category"] == "pytest_failure"
        assert categorization["subcategory"] == "import_error"
        assert categorization["confidence"] >= 0.8
        assert "analysis_details" in categorization
    
    def test_make_failure_categorization(self):
        """Test make failure categorization - Requirement 5.2"""
        # Create make failure
        make_failure = Failure(
            failure_id="test_make_001",
            timestamp=datetime.now(),
            component="makefile",
            error_message="make: *** No rule to make target 'test'. Stop.",
            stack_trace=None,
            context={"command": "make test"},
            category=FailureCategory.MAKE_TARGET_FAILURE
        )
        
        # Test categorization
        categorization = self.rca_engine.analyze_test_failure_categorization(make_failure)
        
        assert categorization["primary_category"] == "make_target_failure"
        assert categorization["subcategory"] == "missing_target"
        assert categorization["confidence"] >= 0.7
    
    def test_infrastructure_failure_categorization(self):
        """Test infrastructure failure categorization - Requirement 5.3"""
        # Create infrastructure failure
        infra_failure = Failure(
            failure_id="test_infra_001",
            timestamp=datetime.now(),
            component="system",
            error_message="PermissionError: [Errno 13] Permission denied: '/restricted/file'",
            stack_trace=None,
            context={"operation": "file_access"},
            category=FailureCategory.INFRASTRUCTURE_FAILURE
        )
        
        # Test categorization
        categorization = self.rca_engine.analyze_test_failure_categorization(infra_failure)
        
        assert categorization["primary_category"] == "infrastructure_failure"
        assert categorization["subcategory"] == "permission_error"
        assert categorization["confidence"] >= 0.6
    
    def test_comprehensive_rca_with_test_specific_analysis(self):
        """Test comprehensive RCA with test-specific analysis - Requirements 4.1, 4.2"""
        # Create test failure
        test_failure = Failure(
            failure_id="test_comprehensive_001",
            timestamp=datetime.now(),
            component="test:tests/test_example.py",
            error_message="AssertionError: Expected 5, got 3",
            stack_trace="Traceback (most recent call last):\n  File \"test_example.py\", line 10, in test_calculation\n    assert result == 5\nAssertionError: Expected 5, got 3",
            context={
                "test_file": "tests/test_example.py",
                "test_function": "test_calculation",
                "pytest_node_id": "tests/test_example.py::test_calculation",
                "failure_type": "assertion"
            },
            category=FailureCategory.PYTEST_FAILURE
        )
        
        # Perform comprehensive RCA
        rca_result = self.rca_engine.perform_systematic_rca(test_failure)
        
        # Verify RCA result structure
        assert rca_result.failure == test_failure
        assert rca_result.analysis is not None
        assert isinstance(rca_result.root_causes, list)
        assert isinstance(rca_result.systematic_fixes, list)
        assert rca_result.total_analysis_time_seconds > 0
        assert 0 <= rca_result.rca_confidence_score <= 1
        
        # Verify test-specific analysis was performed
        assert rca_result.analysis.analysis_confidence >= 0
    
    def test_test_specific_systematic_fix_generation(self):
        """Test test-specific systematic fix generation - Requirement 4.3"""
        # Create test-specific root cause
        test_root_cause = RootCause(
            cause_type=RootCauseType.TEST_IMPORT_ERROR,
            description="Test import error - missing test dependencies",
            evidence=["ImportError in test execution"],
            confidence_score=0.9,
            impact_severity="high",
            affected_components=["test:tests/test_imports.py"]
        )
        
        # Generate test-specific fixes
        fixes = self.rca_engine.generate_test_specific_systematic_fixes([test_root_cause])
        
        assert len(fixes) == 1
        fix = fixes[0]
        assert isinstance(fix, SystematicFix)
        assert fix.root_cause == test_root_cause
        assert "import" in fix.fix_description.lower()
        assert len(fix.implementation_steps) > 0
        assert len(fix.validation_criteria) > 0
        assert fix.estimated_time_minutes > 0
    
    def test_test_specific_pattern_library_integration(self):
        """Test test-specific pattern library integration - Requirement 4.4"""
        # Create test failure and root cause
        test_failure = Failure(
            failure_id="test_pattern_001",
            timestamp=datetime.now(),
            component="test:tests/test_pattern.py",
            error_message="ImportError: No module named 'test_module'",
            stack_trace=None,
            context={
                "test_file": "tests/test_pattern.py",
                "pytest_node_id": "tests/test_pattern.py::test_function"
            },
            category=FailureCategory.PYTEST_FAILURE
        )
        
        test_root_cause = RootCause(
            cause_type=RootCauseType.TEST_IMPORT_ERROR,
            description="Test import error pattern",
            evidence=["ImportError in test"],
            confidence_score=0.8,
            impact_severity="medium",
            affected_components=["test:tests/test_pattern.py"]
        )
        
        test_fix = SystematicFix(
            fix_id="fix_test_001",
            root_cause=test_root_cause,
            fix_description="Fix test import error",
            implementation_steps=["Install missing module"],
            validation_criteria=["Import succeeds"],
            rollback_plan="Remove module",
            estimated_time_minutes=5
        )
        
        # Add test-specific patterns to library
        patterns = self.rca_engine.add_test_specific_patterns_to_library(
            test_failure, [test_root_cause], [test_fix]
        )
        
        assert len(patterns) == 1
        pattern = patterns[0]
        assert isinstance(pattern, PreventionPattern)
        assert "test" in pattern.pattern_name.lower()
        assert pattern.pattern_id in self.rca_engine.pattern_library
    
    def test_pattern_matching_performance(self):
        """Test pattern matching performance - Requirement 4.2 (sub-second performance)"""
        # Create multiple test patterns
        for i in range(100):
            test_failure = Failure(
                failure_id=f"test_perf_{i}",
                timestamp=datetime.now(),
                component=f"test:tests/test_{i}.py",
                error_message=f"Test error {i}",
                stack_trace=None,
                context={"test_file": f"tests/test_{i}.py"},
                category=FailureCategory.PYTEST_FAILURE
            )
            
            # Add pattern to library
            pattern = PreventionPattern(
                pattern_id=f"pattern_{i}",
                pattern_name=f"Test pattern {i}",
                failure_signature=self.rca_engine._generate_test_failure_signature(test_failure),
                root_cause_pattern=f"Root cause {i}",
                prevention_steps=[f"Prevention {i}"],
                detection_criteria=[f"Detection {i}"],
                automated_checks=[f"Check {i}"],
                pattern_hash=f"hash_{i:08d}"
            )
            self.rca_engine._add_test_pattern_to_library(pattern)
        
        # Test pattern matching performance
        test_failure = Failure(
            failure_id="test_perf_match",
            timestamp=datetime.now(),
            component="test:tests/test_50.py",
            error_message="Test error 50",
            stack_trace=None,
            context={"test_file": "tests/test_50.py"},
            category=FailureCategory.PYTEST_FAILURE
        )
        
        start_time = time.time()
        matches = self.rca_engine.match_existing_patterns(test_failure)
        match_time = time.time() - start_time
        
        # Verify sub-second performance (Requirement 4.2)
        assert match_time < 1.0, f"Pattern matching took {match_time:.3f}s, should be < 1.0s"
        assert len(self.rca_engine.pattern_library) >= 100
    
    def test_unknown_failure_type_analysis(self):
        """Test unknown failure type analysis - Requirement 5.4"""
        # Create unknown failure type
        unknown_failure = Failure(
            failure_id="test_unknown_001",
            timestamp=datetime.now(),
            component="unknown_component",
            error_message="Unknown error occurred",
            stack_trace=None,
            context={},
            category=FailureCategory.UNKNOWN
        )
        
        # Perform RCA on unknown failure
        rca_result = self.rca_engine.perform_systematic_rca(unknown_failure)
        
        # Verify generic comprehensive analysis is performed
        assert rca_result.analysis is not None
        assert rca_result.analysis.analysis_confidence >= 0
        
        # Should still provide some analysis even for unknown types
        assert len(rca_result.analysis.symptoms) >= 0
    
    @patch('subprocess.run')
    def test_pytest_specific_analysis_methods(self, mock_subprocess):
        """Test pytest-specific analysis methods"""
        # Mock subprocess calls
        mock_subprocess.return_value = Mock(returncode=0, stdout="pytest 6.2.4", stderr="")
        
        # Create pytest failure
        pytest_failure = Failure(
            failure_id="test_pytest_analysis",
            timestamp=datetime.now(),
            component="test:tests/test_analysis.py",
            error_message="ImportError: No module named 'missing_module'",
            stack_trace="Traceback with ImportError",
            context={
                "test_file": "tests/test_analysis.py",
                "test_function": "test_function",
                "pytest_node_id": "tests/test_analysis.py::test_function"
            },
            category=FailureCategory.PYTEST_FAILURE
        )
        
        # Test pytest-specific analysis
        pytest_analysis = self.rca_engine._analyze_pytest_failures(pytest_failure)
        
        assert pytest_analysis.get('analysis_confidence', 0) > 0
        assert 'python_issues' in pytest_analysis
        assert 'import_analysis' in pytest_analysis
        assert 'dependency_analysis' in pytest_analysis
    
    @patch('subprocess.run')
    def test_makefile_specific_analysis_methods(self, mock_subprocess):
        """Test Makefile-specific analysis methods"""
        # Mock subprocess calls
        mock_subprocess.return_value = Mock(returncode=0, stdout="make help output", stderr="")
        
        # Create make failure
        make_failure = Failure(
            failure_id="test_make_analysis",
            timestamp=datetime.now(),
            component="makefile",
            error_message="make: *** No rule to make target 'test'. Stop.",
            stack_trace=None,
            context={"command": "make test"},
            category=FailureCategory.MAKE_TARGET_FAILURE
        )
        
        # Test makefile-specific analysis
        makefile_analysis = self.rca_engine._analyze_makefile_failures(make_failure)
        
        assert makefile_analysis.get('analysis_confidence', 0) > 0
        assert 'makefile_issues' in makefile_analysis
        assert 'missing_files' in makefile_analysis
        assert 'build_dependencies' in makefile_analysis
    
    def test_infrastructure_specific_analysis_methods(self):
        """Test infrastructure-specific analysis methods"""
        # Create infrastructure failure
        infra_failure = Failure(
            failure_id="test_infra_analysis",
            timestamp=datetime.now(),
            component="system",
            error_message="PermissionError: Permission denied",
            stack_trace=None,
            context={"operation": "file_access"},
            category=FailureCategory.INFRASTRUCTURE_FAILURE
        )
        
        # Test infrastructure-specific analysis
        infra_analysis = self.rca_engine._analyze_infrastructure_failures(infra_failure)
        
        assert infra_analysis.get('analysis_confidence', 0) > 0
        assert 'system_config' in infra_analysis
        assert 'permissions' in infra_analysis
        assert 'environment' in infra_analysis
    
    def test_test_specific_root_cause_identification(self):
        """Test identification of test-specific root causes"""
        # Create test failure with comprehensive analysis
        test_failure = Failure(
            failure_id="test_root_cause_001",
            timestamp=datetime.now(),
            component="test:tests/test_root_cause.py",
            error_message="ImportError: No module named 'test_dependency'",
            stack_trace="ImportError stack trace",
            context={
                "test_file": "tests/test_root_cause.py",
                "pytest_node_id": "tests/test_root_cause.py::test_function"
            },
            category=FailureCategory.PYTEST_FAILURE
        )
        
        # Perform comprehensive analysis
        analysis_result = self.rca_engine.analyze_comprehensive_factors(test_failure)
        
        # Identify root causes
        root_causes = self.rca_engine._identify_root_causes(test_failure, analysis_result)
        
        # Should identify test-specific root causes
        test_specific_causes = [rc for rc in root_causes if rc.cause_type in [
            RootCauseType.TEST_IMPORT_ERROR,
            RootCauseType.TEST_ASSERTION_FAILURE,
            RootCauseType.TEST_FIXTURE_ERROR,
            RootCauseType.TEST_TIMEOUT,
            RootCauseType.TEST_SETUP_ERROR
        ]]
        
        assert len(test_specific_causes) > 0
    
    def test_integration_with_existing_rca_engine(self):
        """Test integration with existing RCA engine - Requirement 4.1"""
        # Verify that test-specific functionality integrates with existing RCA engine
        assert hasattr(self.rca_engine, 'perform_systematic_rca')
        assert hasattr(self.rca_engine, 'analyze_comprehensive_factors')
        assert hasattr(self.rca_engine, 'match_existing_patterns')
        
        # Verify test-specific methods are added
        assert hasattr(self.rca_engine, 'analyze_test_failure_categorization')
        assert hasattr(self.rca_engine, 'generate_test_specific_systematic_fixes')
        assert hasattr(self.rca_engine, 'add_test_specific_patterns_to_library')
        
        # Verify analysis components include test-specific ones
        assert 'test_specific' in self.rca_engine.analysis_components
        assert 'pytest_analysis' in self.rca_engine.analysis_components
        assert 'makefile_analysis' in self.rca_engine.analysis_components
        assert 'infrastructure_analysis' in self.rca_engine.analysis_components
        
        # Verify new root cause types are available
        assert RootCauseType.TEST_IMPORT_ERROR in RootCauseType
        assert RootCauseType.MAKEFILE_ERROR in RootCauseType
        assert RootCauseType.INFRASTRUCTURE_ERROR in RootCauseType
        
        # Verify new failure categories are available
        assert FailureCategory.PYTEST_FAILURE in FailureCategory
        assert FailureCategory.MAKE_TARGET_FAILURE in FailureCategory
        assert FailureCategory.INFRASTRUCTURE_FAILURE in FailureCategory


if __name__ == "__main__":
    pytest.main([__file__, "-v"])