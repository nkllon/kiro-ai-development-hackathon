"""
Unit tests for Test RCA Integration Layer
Tests failure grouping, prioritization, and RCA integration functionality
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from typing import List, Dict, Any

from src.beast_mode.testing.rca_integration import (
    TestRCAIntegrationEngine, TestFailure, TestRCAReport, TestRCASummary,
    TestFailurePriority
)
from src.beast_mode.analysis.rca_engine import (
    RCAEngine, Failure, FailureCategory, RCAResult, RootCause, 
    RootCauseType, SystematicFix, ValidationResult, PreventionPattern,
    ComprehensiveAnalysisResult
)


class TestTestRCAIntegrationEngine:
    """Test suite for TestRCAIntegrationEngine class"""
    
    @pytest.fixture
    def mock_rca_engine(self):
        """Mock RCA engine for testing"""
        engine = Mock(spec=RCAEngine)
        engine.is_healthy.return_value = True
        engine.get_module_status.return_value = {"status": "operational"}
        return engine
        
    @pytest.fixture
    def integrator(self, mock_rca_engine):
        """Test RCA integrator instance"""
        return TestRCAIntegrationEngine(rca_engine=mock_rca_engine)
        
    @pytest.fixture
    def sample_test_failures(self):
        """Sample test failures for testing"""
        base_time = datetime.now()
        
        return [
            TestFailure(
                test_name="test_import_error",
                test_file="tests/test_module.py",
                failure_type="error",
                error_message="ImportError: No module named 'missing_module'",
                stack_trace="Traceback...\nImportError: No module named 'missing_module'",
                test_function="test_import_error",
                test_class="TestModule",
                failure_timestamp=base_time,
                test_context={"test_type": "unit"},
                pytest_node_id="tests/test_module.py::TestModule::test_import_error"
            ),
            TestFailure(
                test_name="test_assertion_error",
                test_file="tests/test_logic.py",
                failure_type="assertion",
                error_message="AssertionError: Expected 5, got 3",
                stack_trace="Traceback...\nAssertionError: Expected 5, got 3",
                test_function="test_assertion_error",
                test_class="TestLogic",
                failure_timestamp=base_time - timedelta(minutes=5),
                test_context={"test_type": "unit"},
                pytest_node_id="tests/test_logic.py::TestLogic::test_assertion_error"
            ),
            TestFailure(
                test_name="test_file_not_found",
                test_file="tests/test_files.py",
                failure_type="error",
                error_message="FileNotFoundError: No such file or directory: 'missing.txt'",
                stack_trace="Traceback...\nFileNotFoundError: No such file or directory",
                test_function="test_file_not_found",
                test_class=None,
                failure_timestamp=base_time - timedelta(minutes=10),
                test_context={"test_type": "integration"},
                pytest_node_id="tests/test_files.py::test_file_not_found"
            )
        ]
        
    @pytest.fixture
    def sample_rca_result(self):
        """Sample RCA result for testing"""
        failure = Failure(
            failure_id="test_failure_1",
            timestamp=datetime.now(),
            component="test:tests/test_module.py",
            error_message="ImportError: No module named 'missing_module'",
            stack_trace="Traceback...",
            context={},
            category=FailureCategory.DEPENDENCY_ISSUE
        )
        
        root_cause = RootCause(
            cause_type=RootCauseType.BROKEN_DEPENDENCIES,
            description="Missing Python module dependency",
            evidence=["ImportError in stack trace"],
            confidence_score=0.9,
            impact_severity="high",
            affected_components=["test:tests/test_module.py"]
        )
        
        systematic_fix = SystematicFix(
            fix_id="fix_dependency_1",
            root_cause=root_cause,
            fix_description="Install missing Python module",
            implementation_steps=["pip install missing_module"],
            validation_criteria=["Import succeeds"],
            rollback_plan="Uninstall module",
            estimated_time_minutes=5
        )
        
        return RCAResult(
            failure=failure,
            analysis=ComprehensiveAnalysisResult([], {}, {}, {}, {}, {}, 0.8),
            root_causes=[root_cause],
            systematic_fixes=[systematic_fix],
            validation_results=[],
            prevention_patterns=[],
            total_analysis_time_seconds=2.5,
            rca_confidence_score=0.85
        )
        
    def test_initialization(self, mock_rca_engine):
        """Test TestRCAIntegrationEngine initialization"""
        integrator = TestRCAIntegrationEngine(rca_engine=mock_rca_engine)
        
        assert integrator.module_name == "test_rca_integrator"
        assert integrator.rca_engine == mock_rca_engine
        assert integrator.total_test_failures_processed == 0
        assert integrator.successful_rca_analyses == 0
        assert integrator.is_healthy()
        
    def test_initialization_without_rca_engine(self):
        """Test initialization creates default RCA engine"""
        with patch('src.beast_mode.testing.rca_integration.RCAEngine') as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            
            integrator = TestRCAIntegrationEngine()
            
            assert integrator.rca_engine == mock_engine
            mock_engine_class.assert_called_once()
            
    def test_get_module_status(self, integrator, mock_rca_engine):
        """Test module status reporting"""
        integrator.total_test_failures_processed = 10
        integrator.successful_rca_analyses = 8
        integrator.total_analysis_time = 20.0
        
        status = integrator.get_module_status()
        
        assert status["module_name"] == "test_rca_integrator"
        assert status["status"] == "operational"
        assert status["test_failures_processed"] == 10
        assert status["successful_rca_analyses"] == 8
        assert status["average_analysis_time"] == 2.5
        assert "rca_engine_status" in status
        
    def test_is_healthy(self, integrator, mock_rca_engine):
        """Test health assessment"""
        mock_rca_engine.is_healthy.return_value = True
        assert integrator.is_healthy()
        
        mock_rca_engine.is_healthy.return_value = False
        assert not integrator.is_healthy()
        
        integrator._degradation_active = True
        assert not integrator.is_healthy()
        
    def test_group_related_failures(self, integrator, sample_test_failures):
        """Test failure grouping functionality"""
        grouped = integrator.group_related_failures(sample_test_failures)
        
        # Should group failures by test file and error type
        assert isinstance(grouped, dict)
        assert len(grouped) > 0
        
        # All failures should be grouped
        total_grouped = sum(len(failures) for failures in grouped.values())
        assert total_grouped == len(sample_test_failures)
        
    def test_group_related_failures_with_overflow(self, integrator):
        """Test failure grouping with overflow handling"""
        # Create many similar failures
        failures = []
        for i in range(15):  # More than max_failures_per_group (10)
            failures.append(TestFailure(
                test_name=f"test_{i}",
                test_file="tests/test_same.py",
                failure_type="error",
                error_message="ImportError: Same error",
                stack_trace="Same stack trace",
                test_function=f"test_{i}",
                test_class="TestSame",
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id=f"tests/test_same.py::TestSame::test_{i}"
            ))
            
        grouped = integrator.group_related_failures(failures)
        
        # Should create overflow groups
        assert len(grouped) > 1
        
        # No group should exceed max size
        for group_failures in grouped.values():
            assert len(group_failures) <= integrator.max_failures_per_group
            
    def test_prioritize_failures(self, integrator, sample_test_failures):
        """Test failure prioritization"""
        prioritized = integrator.prioritize_failures(sample_test_failures)
        
        assert len(prioritized) == len(sample_test_failures)
        assert all(failure in prioritized for failure in sample_test_failures)
        
        # ImportError should be prioritized higher than AssertionError
        import_failure = next(f for f in prioritized if "ImportError" in f.error_message)
        assertion_failure = next(f for f in prioritized if "AssertionError" in f.error_message)
        
        import_index = prioritized.index(import_failure)
        assertion_index = prioritized.index(assertion_failure)
        
        assert import_index < assertion_index  # ImportError comes first (higher priority)
        
    def test_convert_to_rca_failure(self, integrator, sample_test_failures):
        """Test conversion of TestFailure to RCA Failure"""
        test_failure = sample_test_failures[0]  # ImportError failure
        
        rca_failure = integrator.convert_to_rca_failure(test_failure)
        
        assert isinstance(rca_failure, Failure)
        assert rca_failure.component == f"test:{test_failure.test_file}"
        assert rca_failure.error_message == test_failure.error_message
        assert rca_failure.stack_trace == test_failure.stack_trace
        assert rca_failure.category == FailureCategory.DEPENDENCY_ISSUE
        
        # Check context preservation
        assert rca_failure.context["test_file"] == test_failure.test_file
        assert rca_failure.context["test_function"] == test_failure.test_function
        assert rca_failure.context["pytest_node_id"] == test_failure.pytest_node_id
        
    def test_convert_to_rca_failure_categorization(self, integrator):
        """Test failure categorization during conversion"""
        test_cases = [
            ("ImportError: No module", FailureCategory.DEPENDENCY_ISSUE),
            ("PermissionError: Access denied", FailureCategory.PERMISSION_ISSUE),
            ("FileNotFoundError: No such file", FailureCategory.CONFIGURATION_ERROR),
            ("ConnectionError: Network unreachable", FailureCategory.NETWORK_CONNECTIVITY),
            ("MemoryError: Out of memory", FailureCategory.RESOURCE_EXHAUSTION),
            ("Unknown error", FailureCategory.UNKNOWN)
        ]
        
        for error_message, expected_category in test_cases:
            test_failure = TestFailure(
                test_name="test_case",
                test_file="tests/test.py",
                failure_type="error",
                error_message=error_message,
                stack_trace="",
                test_function="test_case",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test.py::test_case"
            )
            
            rca_failure = integrator.convert_to_rca_failure(test_failure)
            assert rca_failure.category == expected_category
            
    def test_analyze_test_failures_success(self, integrator, mock_rca_engine, sample_test_failures, sample_rca_result):
        """Test successful test failure analysis"""
        # Mock RCA engine responses
        mock_rca_engine.match_existing_patterns.return_value = []
        mock_rca_engine.perform_systematic_rca.return_value = sample_rca_result
        
        report = integrator.analyze_test_failures(sample_test_failures)
        
        assert isinstance(report, TestRCAReport)
        assert report.total_failures == len(sample_test_failures)
        assert report.failures_analyzed > 0
        assert len(report.rca_results) > 0
        assert isinstance(report.summary, TestRCASummary)
        assert len(report.recommendations) > 0
        
        # Check metrics updated
        assert integrator.total_test_failures_processed == len(sample_test_failures)
        assert integrator.successful_rca_analyses > 0
        
    def test_analyze_test_failures_with_patterns(self, integrator, mock_rca_engine, sample_test_failures, sample_rca_result):
        """Test analysis with existing pattern matches"""
        # Mock pattern matches
        pattern = PreventionPattern(
            pattern_id="pattern_1",
            pattern_name="Import Error Pattern",
            failure_signature="import_error_signature",
            root_cause_pattern="missing_dependency",
            prevention_steps=["Install dependencies"],
            detection_criteria=["ImportError in message"],
            automated_checks=["pip check"],
            pattern_hash="abc123"
        )
        
        mock_rca_engine.match_existing_patterns.return_value = [pattern]
        mock_rca_engine.perform_systematic_rca.return_value = sample_rca_result
        
        report = integrator.analyze_test_failures(sample_test_failures)
        
        assert integrator.pattern_matches_found > 0
        assert len(report.prevention_patterns) > 0
        
    def test_analyze_test_failures_timeout_handling(self, integrator, mock_rca_engine, sample_test_failures):
        """Test timeout handling during analysis"""
        # Set very short timeout
        integrator.analysis_timeout_seconds = 0.1
        
        # Mock slow RCA analysis
        def slow_rca(*args, **kwargs):
            time.sleep(0.2)  # Longer than timeout
            return sample_rca_result
            
        mock_rca_engine.match_existing_patterns.return_value = []
        mock_rca_engine.perform_systematic_rca.side_effect = slow_rca
        
        report = integrator.analyze_test_failures(sample_test_failures)
        
        # Should still return a report, but may have fewer results due to timeout
        assert isinstance(report, TestRCAReport)
        assert report.total_failures == len(sample_test_failures)
        
    def test_analyze_test_failures_rca_engine_failure(self, integrator, mock_rca_engine, sample_test_failures):
        """Test handling of RCA engine failures"""
        mock_rca_engine.match_existing_patterns.side_effect = Exception("RCA engine failed")
        mock_rca_engine.perform_systematic_rca.side_effect = Exception("RCA analysis failed")
        
        report = integrator.analyze_test_failures(sample_test_failures)
        
        # Should return minimal report on failure
        assert isinstance(report, TestRCAReport)
        assert report.total_failures == len(sample_test_failures)
        assert report.failures_analyzed == 0
        # The report should contain error information and fallback recommendations
        assert len(report.recommendations) > 0
        # Check for fallback recommendations when no systematic fixes are available
        assert any("review test failures manually" in rec.lower() for rec in report.recommendations)
        
    def test_generate_failure_group_key(self, integrator):
        """Test failure group key generation"""
        test_failure = TestFailure(
            test_name="test_import",
            test_file="tests/test_module.py",
            failure_type="error",
            error_message="ImportError: No module named 'test'",
            stack_trace="",
            test_function="test_import",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test_module.py::test_import"
        )
        
        group_key = integrator._generate_failure_group_key(test_failure)
        
        assert "test_module" in group_key
        assert "error" in group_key
        assert "import_error" in group_key
        
    def test_calculate_failure_priority_score(self, integrator):
        """Test failure priority score calculation"""
        # Critical error should get high score
        critical_failure = TestFailure(
            test_name="test_critical",
            test_file="tests/test.py",
            failure_type="error",
            error_message="CRITICAL: System failure",
            stack_trace="",
            test_function="test_critical",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test.py::test_critical"
        )
        
        # Regular assertion error should get lower score
        regular_failure = TestFailure(
            test_name="test_regular",
            test_file="tests/test.py",
            failure_type="assertion",
            error_message="AssertionError: Test failed",
            stack_trace="",
            test_function="test_regular",
            test_class=None,
            failure_timestamp=datetime.now() - timedelta(hours=1),
            test_context={},
            pytest_node_id="tests/test.py::test_regular"
        )
        
        critical_score = integrator._calculate_failure_priority_score(critical_failure)
        regular_score = integrator._calculate_failure_priority_score(regular_failure)
        
        assert critical_score > regular_score
        
    def test_get_failure_priority(self, integrator):
        """Test failure priority level assignment"""
        # Test different priority levels
        priorities = [
            ("CRITICAL: System failure", TestFailurePriority.CRITICAL),
            ("ImportError: Missing module", TestFailurePriority.HIGH),
            ("ConfigurationError: Bad config", TestFailurePriority.MEDIUM),
            ("AssertionError: Test failed", TestFailurePriority.LOW)
        ]
        
        for error_message, expected_priority in priorities:
            test_failure = TestFailure(
                test_name="test_priority",
                test_file="tests/test.py",
                failure_type="error",
                error_message=error_message,
                stack_trace="",
                test_function="test_priority",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test.py::test_priority"
            )
            
            priority = integrator._get_failure_priority(test_failure)
            assert priority == expected_priority
            
    def test_generate_rca_summary(self, integrator, sample_rca_result):
        """Test RCA summary generation"""
        rca_results = [sample_rca_result]
        pattern_matches = []
        
        summary = integrator._generate_rca_summary(rca_results, pattern_matches)
        
        assert isinstance(summary, TestRCASummary)
        assert len(summary.most_common_root_causes) > 0
        assert summary.systematic_fixes_available > 0
        assert summary.confidence_score > 0
        
    def test_generate_recommendations(self, integrator, sample_rca_result):
        """Test recommendation generation"""
        rca_results = [sample_rca_result]
        
        recommendations = integrator._generate_recommendations(rca_results)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)
        
    def test_generate_next_steps(self, integrator):
        """Test next steps generation"""
        summary = TestRCASummary(
            most_common_root_causes=[(RootCauseType.BROKEN_DEPENDENCIES, 2)],
            systematic_fixes_available=3,
            pattern_matches_found=1,
            estimated_fix_time_minutes=15,
            confidence_score=0.8,
            critical_issues=["Critical dependency issue"]
        )
        
        next_steps = integrator._generate_next_steps([], summary)
        
        assert isinstance(next_steps, list)
        assert len(next_steps) > 0
        assert any("critical" in step.lower() for step in next_steps)
        
    def test_error_handling_in_grouping(self, integrator):
        """Test error handling in failure grouping"""
        # Create failure that might cause grouping issues
        problematic_failure = TestFailure(
            test_name="test_problematic",
            test_file=None,  # This might cause issues
            failure_type="error",
            error_message="Error message",
            stack_trace="",
            test_function="test_problematic",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test.py::test_problematic"
        )
        
        # Should handle gracefully and return fallback grouping
        grouped = integrator.group_related_failures([problematic_failure])
        
        assert isinstance(grouped, dict)
        assert len(grouped) > 0
        
    def test_error_handling_in_prioritization(self, integrator):
        """Test error handling in failure prioritization"""
        # Create failure that might cause prioritization issues
        problematic_failure = TestFailure(
            test_name="test_problematic",
            test_file="tests/test.py",
            failure_type="error",
            error_message=None,  # This might cause issues
            stack_trace="",
            test_function="test_problematic",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test.py::test_problematic"
        )
        
        # Should handle gracefully and return original order
        prioritized = integrator.prioritize_failures([problematic_failure])
        
        assert isinstance(prioritized, list)
        assert len(prioritized) == 1
        
    def test_error_handling_in_conversion(self, integrator):
        """Test error handling in TestFailure to RCA Failure conversion"""
        # Create failure that might cause conversion issues
        problematic_failure = TestFailure(
            test_name="test_problematic",
            test_file="tests/test.py",
            failure_type="error",
            error_message="Error message",
            stack_trace="",
            test_function="test_problematic",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id=None  # This might cause issues
        )
        
        # Should handle gracefully and return minimal failure object
        rca_failure = integrator.convert_to_rca_failure(problematic_failure)
        
        assert isinstance(rca_failure, Failure)
        assert rca_failure.component == "test:unknown" or "conversion_failed" in rca_failure.failure_id


if __name__ == "__main__":
    pytest.main([__file__])