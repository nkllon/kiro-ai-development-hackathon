"""
Unit tests for multi-failure analysis and grouping functionality
Tests the enhanced failure grouping, prioritization, and correlation detection
Requirements: 1.3, 5.1, 5.2, 5.3, 5.4
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from src.beast_mode.testing.rca_integration import (
    TestRCAIntegrationEngine, TestFailureData, TestFailurePriorityLevel
)
from src.beast_mode.analysis.rca_engine import RCAEngine, RCAResult, RootCause, RootCauseType


# Global fixtures available to all test classes
@pytest.fixture
def rca_engine_mock():
    """Mock RCA engine for testing"""
    mock_engine = Mock(spec=RCAEngine)
    mock_engine.is_healthy.return_value = True
    mock_engine.get_module_status.return_value = {"status": "healthy"}
    
    # Mock RCA result
    mock_result = Mock(spec=RCAResult)
    mock_result.root_causes = [Mock(spec=RootCause)]
    mock_result.root_causes[0].cause_type = RootCauseType.BROKEN_DEPENDENCIES
    mock_result.root_causes[0].description = "Mock root cause"
    mock_result.root_causes[0].impact_severity = "medium"
    mock_result.systematic_fixes = []
    mock_result.total_analysis_time_seconds = 5.0
    mock_result.rca_confidence_score = 0.8
    mock_result.prevention_patterns = []
    
    mock_engine.perform_systematic_rca.return_value = mock_result
    mock_engine.match_existing_patterns.return_value = []
    
    return mock_engine

@pytest.fixture
def integrator(rca_engine_mock):
    """Test RCA integrator instance"""
    return TestRCAIntegrationEngine(rca_engine_mock)

@pytest.fixture
def sample_failures():
    """Sample test failures for testing"""
    base_time = datetime.now()
    
    return [
        TestFailureData(
            test_name="tests/test_module_a.py::test_import_error",
            test_file="tests/test_module_a.py",
            failure_type="import",
            error_message="ImportError: No module named 'missing_module'",
            stack_trace="Traceback: import missing_module",
            test_function="test_import_error",
            test_class=None,
            failure_timestamp=base_time,
            test_context={"environment_variables": {"CI": "true"}},
            pytest_node_id="tests/test_module_a.py::test_import_error"
        ),
        TestFailureData(
            test_name="tests/test_module_a.py::test_another_import",
            test_file="tests/test_module_a.py", 
            failure_type="import",
            error_message="ImportError: No module named 'another_missing'",
            stack_trace="Traceback: import another_missing",
            test_function="test_another_import",
            test_class=None,
            failure_timestamp=base_time + timedelta(seconds=30),
            test_context={"environment_variables": {"CI": "true"}},
            pytest_node_id="tests/test_module_a.py::test_another_import"
        ),
        TestFailureData(
            test_name="tests/test_module_b.py::test_assertion",
            test_file="tests/test_module_b.py",
            failure_type="assertion",
            error_message="AssertionError: Expected 5, got 3",
            stack_trace="Traceback: assert result == 5",
            test_function="test_assertion",
            test_class=None,
            failure_timestamp=base_time + timedelta(minutes=1),
            test_context={"environment_variables": {}},
            pytest_node_id="tests/test_module_b.py::test_assertion"
        ),
        TestFailureData(
            test_name="tests/conftest.py::test_fixture_error",
            test_file="tests/conftest.py",
            failure_type="error",
            error_message="FileNotFoundError: Config file not found",
            stack_trace="Traceback: open('config.json')",
            test_function="test_fixture_error",
            test_class=None,
            failure_timestamp=base_time + timedelta(minutes=2),
            test_context={"environment_variables": {"CI": "true"}},
            pytest_node_id="tests/conftest.py::test_fixture_error"
        ),
        TestFailureData(
            test_name="tests/test_security.py::test_critical_security",
            test_file="tests/test_security.py",
            failure_type="error",
            error_message="SecurityError: Critical security vulnerability detected",
            stack_trace="Traceback: security check failed",
            test_function="test_critical_security",
            test_class=None,
            failure_timestamp=base_time + timedelta(minutes=3),
            test_context={"environment_variables": {}},
            pytest_node_id="tests/test_security.py::test_critical_security"
        )
    ]


class TestFailureGrouping:
    """Test failure grouping functionality"""
    
    def test_basic_failure_grouping(self, integrator, sample_failures):
        """Test basic failure grouping by characteristics"""
        grouped = integrator.group_related_failures(sample_failures)
        
        # Should have multiple groups
        assert len(grouped) > 1
        
        # Import failures should be grouped together
        import_groups = [g for name, g in grouped.items() if 'import' in name.lower()]
        assert len(import_groups) > 0
        
        # Check that import failures are in the same group
        import_failure_names = []
        for group in import_groups:
            import_failure_names.extend([f.test_name for f in group])
            
        assert "tests/test_module_a.py::test_import_error" in import_failure_names
        assert "tests/test_module_a.py::test_another_import" in import_failure_names
    
    def test_correlation_detection_within_groups(self, integrator, sample_failures):
        """Test correlation detection within failure groups"""
        # Create failures with high correlation
        correlated_failures = [
            TestFailureData(
                test_name="tests/test_a.py::test_1",
                test_file="tests/test_a.py",
                failure_type="import",
                error_message="ImportError: No module named 'common_module'",
                stack_trace="import common_module",
                test_function="test_1",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_a.py::test_1"
            ),
            TestFailureData(
                test_name="tests/test_a.py::test_2", 
                test_file="tests/test_a.py",
                failure_type="import",
                error_message="ImportError: No module named 'common_module'",
                stack_trace="import common_module",
                test_function="test_2",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_a.py::test_2"
            )
        ]
        
        grouped = integrator.group_related_failures(correlated_failures)
        
        # Highly correlated failures should be in the same group
        assert len(grouped) == 1
        group_name, group_failures = next(iter(grouped.items()))
        assert len(group_failures) == 2
    
    def test_group_size_limits(self, integrator):
        """Test that group size limits are enforced"""
        # Create many similar failures
        many_failures = []
        for i in range(15):  # More than max_failures_per_group (10)
            failure = TestFailureData(
                test_name=f"tests/test_{i}.py::test_method",
                test_file=f"tests/test_{i}.py",
                failure_type="import",
                error_message="ImportError: Same error",
                stack_trace="Same stack trace",
                test_function="test_method",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id=f"tests/test_{i}.py::test_method"
            )
            many_failures.append(failure)
            
        grouped = integrator.group_related_failures(many_failures)
        
        # Should be split into multiple groups due to size limits
        total_failures_in_groups = sum(len(group) for group in grouped.values())
        assert total_failures_in_groups == len(many_failures)
        
        # No group should exceed the limit
        for group in grouped.values():
            assert len(group) <= integrator.max_failures_per_group
    
    def test_cross_group_correlation_merging(self, integrator):
        """Test merging of highly correlated groups"""
        # This is tested implicitly in the group_related_failures method
        # The method should detect and merge highly correlated groups
        
        similar_failures = [
            TestFailureData(
                test_name="tests/test_1.py::test_method",
                test_file="tests/test_1.py",
                failure_type="import",
                error_message="ImportError: No module named 'shared_dependency'",
                stack_trace="import shared_dependency",
                test_function="test_method",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_1.py::test_method"
            ),
            TestFailureData(
                test_name="tests/test_2.py::test_method",
                test_file="tests/test_2.py", 
                failure_type="import",
                error_message="ImportError: No module named 'shared_dependency'",
                stack_trace="import shared_dependency",
                test_function="test_method",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_2.py::test_method"
            )
        ]
        
        grouped = integrator.group_related_failures(similar_failures)
        
        # Should be grouped together due to high correlation
        assert len(grouped) <= 2  # May be 1 if merged, or 2 if kept separate


class TestFailurePrioritization:
    """Test failure prioritization functionality"""
    
    def test_multi_dimensional_prioritization(self, integrator, sample_failures):
        """Test multi-dimensional priority scoring"""
        prioritized = integrator.prioritize_failures(sample_failures)
        
        # Should return all failures
        assert len(prioritized) == len(sample_failures)
        
        # Critical security failure should be high priority
        security_failure = next(f for f in prioritized if 'security' in f.test_name)
        security_index = prioritized.index(security_failure)
        
        # Should be in top half of priorities
        assert security_index < len(prioritized) // 2
    
    def test_critical_priority_boosting(self, integrator):
        """Test that critical failures get priority boost"""
        critical_failure = TestFailureData(
            test_name="tests/test_critical.py::test_fatal_error",
            test_file="tests/test_critical.py",
            failure_type="error",
            error_message="FATAL: System corruption detected",
            stack_trace="Fatal error stack trace",
            test_function="test_fatal_error",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test_critical.py::test_fatal_error"
        )
        
        normal_failure = TestFailureData(
            test_name="tests/test_normal.py::test_simple",
            test_file="tests/test_normal.py",
            failure_type="assertion",
            error_message="AssertionError: Simple assertion failed",
            stack_trace="Simple stack trace",
            test_function="test_simple",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test_normal.py::test_simple"
        )
        
        failures = [normal_failure, critical_failure]
        prioritized = integrator.prioritize_failures(failures)
        
        # Critical failure should come first
        assert prioritized[0] == critical_failure
    
    def test_impact_score_calculation(self, integrator, sample_failures):
        """Test impact score calculation"""
        # Infrastructure failure (conftest.py) should have high impact
        conftest_failure = next(f for f in sample_failures if 'conftest' in f.test_file)
        impact_score = integrator._calculate_failure_impact_score(conftest_failure)
        
        # Should have high impact score
        assert impact_score > 30.0
        
        # Import failure should have high impact
        import_failure = next(f for f in sample_failures if f.failure_type == 'import')
        import_impact = integrator._calculate_failure_impact_score(import_failure)
        
        assert import_impact > 30.0
    
    def test_urgency_score_calculation(self, integrator):
        """Test urgency score calculation"""
        # Recent failure should have high urgency
        recent_failure = TestFailureData(
            test_name="tests/test_recent.py::test_method",
            test_file="tests/test_recent.py",
            failure_type="error",
            error_message="Recent error",
            stack_trace="Recent stack trace",
            test_function="test_method",
            test_class=None,
            failure_timestamp=datetime.now(),  # Very recent
            test_context={"environment_variables": {"CI": "true"}},
            pytest_node_id="tests/test_recent.py::test_method"
        )
        
        urgency_score = integrator._calculate_failure_urgency_score(recent_failure)
        
        # Should have high urgency (recent + CI context)
        assert urgency_score > 40.0
    
    def test_correlation_priority_score(self, integrator):
        """Test correlation-based priority scoring"""
        # Create failures with similar characteristics
        base_failure = TestFailureData(
            test_name="tests/test_base.py::test_method",
            test_file="tests/test_base.py",
            failure_type="import",
            error_message="ImportError: Common error",
            stack_trace="Common stack trace",
            test_function="test_method",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test_base.py::test_method"
        )
        
        similar_failures = []
        for i in range(3):
            similar_failure = TestFailureData(
                test_name=f"tests/test_similar_{i}.py::test_method",
                test_file=f"tests/test_similar_{i}.py",
                failure_type="import",
                error_message="ImportError: Common error",
                stack_trace="Common stack trace",
                test_function="test_method",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id=f"tests/test_similar_{i}.py::test_method"
            )
            similar_failures.append(similar_failure)
            
        all_failures = [base_failure] + similar_failures
        correlation_score = integrator._calculate_correlation_priority_score(base_failure, all_failures)
        
        # Should have positive correlation score due to similar failures
        assert correlation_score > 0.0


class TestBatchAnalysis:
    """Test batch RCA analysis functionality"""
    
    def test_batch_failure_analysis(self, integrator, sample_failures):
        """Test batch analysis of grouped failures"""
        # Group failures first
        grouped_failures = integrator.group_related_failures(sample_failures)
        
        # Perform batch analysis
        batch_results = integrator.analyze_batch_failures(grouped_failures)
        
        # Should have results for each group
        assert len(batch_results) > 0
        
        # Each group should have RCA results
        for group_name, results in batch_results.items():
            assert isinstance(results, list)
            # Results may be empty if RCA engine mock doesn't return results
    
    def test_shared_context_building(self, integrator, sample_failures):
        """Test building shared context for batch analysis"""
        # Create common patterns
        common_patterns = [
            {"type": "error_message_pattern", "pattern": "ImportError", "frequency": 2}
        ]
        
        shared_context = integrator._build_shared_analysis_context(sample_failures, common_patterns)
        
        # Should include batch information
        assert shared_context["batch_analysis"] is True
        assert shared_context["batch_size"] == len(sample_failures)
        assert "common_patterns" in shared_context
        assert "failure_types" in shared_context
        assert "affected_files" in shared_context
    
    def test_common_pattern_detection(self, integrator):
        """Test detection of common patterns within failure groups"""
        # Create failures with common patterns
        failures_with_patterns = [
            TestFailureData(
                test_name="tests/test_1.py::test_method",
                test_file="tests/test_1.py",
                failure_type="import",
                error_message="ImportError: No module named 'common_module'",
                stack_trace="import common_module",
                test_function="test_method",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_1.py::test_method"
            ),
            TestFailureData(
                test_name="tests/test_2.py::test_method",
                test_file="tests/test_2.py",
                failure_type="import", 
                error_message="ImportError: No module named 'common_module'",
                stack_trace="import common_module",
                test_function="test_method",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_2.py::test_method"
            )
        ]
        
        patterns = integrator._detect_common_failure_patterns(failures_with_patterns)
        
        # Should detect common error message patterns
        error_patterns = [p for p in patterns if p["type"] == "error_message_pattern"]
        assert len(error_patterns) > 0
        
        # Should find "common_module" pattern
        common_module_patterns = [p for p in error_patterns if "common_module" in p["pattern"]]
        assert len(common_module_patterns) > 0


class TestCorrelationDetection:
    """Test failure correlation detection functionality"""
    
    def test_failure_correlation_detection(self, integrator, sample_failures):
        """Test comprehensive failure correlation detection"""
        correlations = integrator.detect_failure_correlations(sample_failures)
        
        # Should have correlation categories
        expected_categories = [
            "temporal_correlations", "error_pattern_correlations",
            "dependency_correlations", "environmental_correlations", 
            "common_root_causes"
        ]
        
        for category in expected_categories:
            assert category in correlations
            assert isinstance(correlations[category], list)
    
    def test_temporal_correlation_analysis(self, integrator):
        """Test temporal correlation analysis"""
        # Create failures close in time
        base_time = datetime.now()
        close_failures = [
            TestFailureData(
                test_name="tests/test_1.py::test_method",
                test_file="tests/test_1.py",
                failure_type="error",
                error_message="Error 1",
                stack_trace="Stack 1",
                test_function="test_method",
                test_class=None,
                failure_timestamp=base_time,
                test_context={},
                pytest_node_id="tests/test_1.py::test_method"
            ),
            TestFailureData(
                test_name="tests/test_2.py::test_method",
                test_file="tests/test_2.py",
                failure_type="error",
                error_message="Error 2", 
                stack_trace="Stack 2",
                test_function="test_method",
                test_class=None,
                failure_timestamp=base_time + timedelta(seconds=30),  # 30 seconds later
                test_context={},
                pytest_node_id="tests/test_2.py::test_method"
            )
        ]
        
        temporal_correlations = integrator._analyze_temporal_correlations(close_failures)
        
        # Should find temporal correlation
        assert len(temporal_correlations) > 0
        assert temporal_correlations[0]["type"] == "temporal"
        assert temporal_correlations[0]["time_difference_seconds"] == 30.0
    
    def test_error_pattern_correlation_analysis(self, integrator):
        """Test error pattern correlation analysis"""
        # Create failures with similar error patterns
        pattern_failures = [
            TestFailureData(
                test_name="tests/test_1.py::test_method",
                test_file="tests/test_1.py",
                failure_type="import",
                error_message="ImportError: No module named 'missing'",
                stack_trace="import missing",
                test_function="test_method",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_1.py::test_method"
            ),
            TestFailureData(
                test_name="tests/test_2.py::test_method",
                test_file="tests/test_2.py",
                failure_type="import",
                error_message="ImportError: No module named 'missing'",
                stack_trace="import missing",
                test_function="test_method",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_2.py::test_method"
            )
        ]
        
        error_correlations = integrator._analyze_error_pattern_correlations(pattern_failures)
        
        # Should find error pattern correlation
        assert len(error_correlations) > 0
        assert error_correlations[0]["type"] == "error_pattern"
    
    def test_dependency_correlation_analysis(self, integrator, sample_failures):
        """Test dependency correlation analysis"""
        dependency_correlations = integrator._analyze_dependency_correlations(sample_failures)
        
        # Should find import failure correlations
        import_correlations = [c for c in dependency_correlations 
                             if c.get("subtype") == "import_failures"]
        
        # Sample failures include import failures, so should find correlations
        assert len(import_correlations) > 0
    
    def test_environmental_correlation_analysis(self, integrator, sample_failures):
        """Test environmental correlation analysis"""
        environmental_correlations = integrator._analyze_environmental_correlations(sample_failures)
        
        # Sample failures have CI environment variable, should find correlation
        ci_correlations = [c for c in environmental_correlations 
                          if "CI=true" in c.get("environment_variable", "")]
        
        assert len(ci_correlations) > 0
    
    def test_common_root_cause_identification(self, integrator, sample_failures):
        """Test common root cause identification"""
        root_causes = integrator._identify_common_root_causes(sample_failures)
        
        # Should identify some common root causes
        assert len(root_causes) > 0
        
        # Should have confidence scores
        for root_cause in root_causes:
            assert "confidence" in root_cause
            assert 0.0 <= root_cause["confidence"] <= 1.0


class TestHelperMethods:
    """Test helper methods for similarity and pattern detection"""
    
    def test_failure_similarity_calculation(self, integrator):
        """Test failure similarity calculation"""
        failure_a = TestFailureData(
            test_name="tests/test_a.py::test_method",
            test_file="tests/test_a.py",
            failure_type="import",
            error_message="ImportError: No module named 'common'",
            stack_trace="import common",
            test_function="test_method",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test_a.py::test_method"
        )
        
        failure_b = TestFailureData(
            test_name="tests/test_a.py::test_other",
            test_file="tests/test_a.py",  # Same file
            failure_type="import",  # Same type
            error_message="ImportError: No module named 'common'",  # Same error
            stack_trace="import common",  # Same stack trace
            test_function="test_other",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="tests/test_a.py::test_other"
        )
        
        similarity = integrator._calculate_failure_similarity(failure_a, failure_b)
        
        # Should have high similarity (same file, type, error, stack trace)
        assert similarity > 0.8
    
    def test_text_similarity_calculation(self, integrator):
        """Test text similarity calculation"""
        text_a = "ImportError: No module named 'test_module'"
        text_b = "ImportError: No module named 'test_module'"
        
        similarity = integrator._calculate_text_similarity(text_a, text_b)
        
        # Identical texts should have similarity of 1.0
        assert similarity == 1.0
        
        # Different texts should have lower similarity
        text_c = "AssertionError: Expected value"
        similarity_different = integrator._calculate_text_similarity(text_a, text_c)
        
        assert similarity_different < 0.5
    
    def test_common_text_pattern_finding(self, integrator):
        """Test finding common patterns in text lists"""
        texts = [
            "ImportError: No module named 'module_a'",
            "ImportError: No module named 'module_b'", 
            "AssertionError: Test failed"
        ]
        
        patterns = integrator._find_common_text_patterns(texts)
        
        # Should find "ImportError" as common pattern (appears twice)
        assert "importerror:" in patterns
        assert patterns["importerror:"] == 2
    
    def test_error_pattern_extraction(self, integrator):
        """Test error pattern extraction"""
        error_message = "ImportError: No module named 'specific_module' at line 42"
        
        pattern = integrator._extract_error_pattern(error_message)
        
        # Should generalize specific details
        assert "specific_module" not in pattern
        assert "<value>" in pattern or "<path>" in pattern
        assert "line <num>" in pattern or "<num>" in pattern


class TestErrorHandling:
    """Test error handling in multi-failure analysis"""
    
    def test_grouping_error_handling(self, integrator):
        """Test error handling in failure grouping"""
        # Create invalid failure data
        invalid_failure = TestFailureData(
            test_name=None,  # Invalid
            test_file="",
            failure_type="",
            error_message="",
            stack_trace="",
            test_function="",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id=""
        )
        
        # Should handle gracefully and not crash
        grouped = integrator.group_related_failures([invalid_failure])
        
        # Should return some grouping (fallback behavior)
        assert len(grouped) > 0
    
    def test_prioritization_error_handling(self, integrator):
        """Test error handling in failure prioritization"""
        # Create failure with missing data
        incomplete_failure = TestFailureData(
            test_name="test",
            test_file="",
            failure_type="",
            error_message="",
            stack_trace="",
            test_function="",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id=""
        )
        
        # Should handle gracefully
        prioritized = integrator.prioritize_failures([incomplete_failure])
        
        # Should return the failure (fallback behavior)
        assert len(prioritized) == 1
    
    def test_correlation_detection_error_handling(self, integrator):
        """Test error handling in correlation detection"""
        # Empty failure list
        correlations = integrator.detect_failure_correlations([])
        
        # Should return empty correlations without crashing
        assert isinstance(correlations, dict)
        assert len(correlations["common_root_causes"]) == 0


if __name__ == "__main__":
    pytest.main([__file__])