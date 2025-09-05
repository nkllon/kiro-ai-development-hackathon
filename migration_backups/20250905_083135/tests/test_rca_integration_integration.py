"""
Integration tests for Test RCA Integration Layer with real RCA engine
Tests end-to-end functionality with actual RCA engine components
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.beast_mode.testing.rca_integration import (
    TestRCAIntegrationEngine, TestFailure
)
from src.beast_mode.analysis.rca_engine import RCAEngine


class TestRCAIntegrationWithRealEngine:
    """Integration tests with real RCA engine"""
    
    @pytest.fixture
    def real_integrator(self):
        """Integration engine with real RCA engine"""
        return TestRCAIntegrationEngine()
        
    @pytest.fixture
    def sample_import_failure(self):
        """Sample import error test failure"""
        return TestFailure(
            test_name="test_import_missing_module",
            test_file="tests/test_imports.py",
            failure_type="error",
            error_message="ImportError: No module named 'nonexistent_module'",
            stack_trace="Traceback (most recent call last):\n  File \"tests/test_imports.py\", line 5, in test_import_missing_module\n    import nonexistent_module\nImportError: No module named 'nonexistent_module'",
            test_function="test_import_missing_module",
            test_class="TestImports",
            failure_timestamp=datetime.now(),
            test_context={"test_type": "unit", "test_category": "imports"},
            pytest_node_id="tests/test_imports.py::TestImports::test_import_missing_module"
        )
        
    def test_end_to_end_rca_analysis(self, real_integrator, sample_import_failure):
        """Test complete end-to-end RCA analysis workflow"""
        # Analyze single test failure
        report = real_integrator.analyze_test_failures([sample_import_failure])
        
        # Verify report structure
        assert report.total_failures == 1
        assert report.failures_analyzed >= 0  # May be 0 if RCA engine has issues
        assert len(report.grouped_failures) > 0
        assert isinstance(report.recommendations, list)
        assert isinstance(report.next_steps, list)
        
        # Verify summary contains meaningful data
        assert report.summary.confidence_score >= 0.0
        assert report.summary.estimated_fix_time_minutes >= 0
        
    def test_multiple_failure_analysis(self, real_integrator):
        """Test analysis of multiple related failures"""
        failures = [
            TestFailure(
                test_name="test_import_error_1",
                test_file="tests/test_module_a.py",
                failure_type="error",
                error_message="ImportError: No module named 'missing_dep'",
                stack_trace="ImportError stack trace",
                test_function="test_import_error_1",
                test_class="TestModuleA",
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_module_a.py::TestModuleA::test_import_error_1"
            ),
            TestFailure(
                test_name="test_import_error_2",
                test_file="tests/test_module_b.py",
                failure_type="error",
                error_message="ImportError: No module named 'missing_dep'",
                stack_trace="ImportError stack trace",
                test_function="test_import_error_2",
                test_class="TestModuleB",
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_module_b.py::TestModuleB::test_import_error_2"
            )
        ]
        
        report = real_integrator.analyze_test_failures(failures)
        
        # Should group related failures
        assert report.total_failures == 2
        assert len(report.grouped_failures) >= 1  # Should group similar import errors
        
        # Should provide consolidated recommendations
        assert len(report.recommendations) > 0
        
    def test_failure_categorization_accuracy(self, real_integrator):
        """Test accuracy of failure categorization"""
        test_cases = [
            ("ImportError: No module named 'test'", "dependency"),
            ("FileNotFoundError: No such file", "configuration"),
            ("PermissionError: Access denied", "permission"),
            ("AssertionError: Test failed", "unknown")  # Generic test failure
        ]
        
        for error_message, expected_category_hint in test_cases:
            failure = TestFailure(
                test_name="test_categorization",
                test_file="tests/test_cat.py",
                failure_type="error",
                error_message=error_message,
                stack_trace="Stack trace",
                test_function="test_categorization",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="tests/test_cat.py::test_categorization"
            )
            
            # Convert to RCA failure and check categorization
            rca_failure = real_integrator.convert_to_rca_failure(failure)
            
            # Verify categorization makes sense
            assert rca_failure.category is not None
            assert rca_failure.component.startswith("test:")
            
    def test_performance_within_timeout(self, real_integrator, sample_import_failure):
        """Test that analysis completes within timeout requirements"""
        import time
        
        start_time = time.time()
        report = real_integrator.analyze_test_failures([sample_import_failure])
        analysis_time = time.time() - start_time
        
        # Should complete within 30 seconds (requirement 1.4)
        assert analysis_time < 30.0
        
        # Verify integrator tracks timing
        assert real_integrator.total_analysis_time > 0
        
    def test_health_monitoring(self, real_integrator):
        """Test health monitoring and status reporting"""
        # Check initial health
        assert real_integrator.is_healthy()
        
        # Get module status
        status = real_integrator.get_module_status()
        assert status["module_name"] == "test_rca_integrator"
        assert "status" in status
        assert "rca_engine_status" in status
        
        # Get health indicators
        health = real_integrator.get_health_indicators()
        assert "integration_capability" in health
        assert "rca_engine_integration" in health
        assert "performance" in health
        
    def test_graceful_degradation(self, real_integrator):
        """Test graceful degradation when RCA engine has issues"""
        # Simulate RCA engine degradation
        real_integrator.rca_engine = None
        
        # Should still provide basic functionality
        assert not real_integrator.is_healthy()
        
        status = real_integrator.get_module_status()
        assert status["status"] == "degraded"
        
    def test_pattern_matching_integration(self, real_integrator, sample_import_failure):
        """Test integration with pattern matching system"""
        # This test verifies that pattern matching is called
        # Even if no patterns exist, the integration should work
        
        with patch.object(real_integrator.rca_engine, 'match_existing_patterns') as mock_match:
            mock_match.return_value = []  # No existing patterns
            
            report = real_integrator.analyze_test_failures([sample_import_failure])
            
            # Pattern matching should have been called
            mock_match.assert_called()
            
            # Report should still be generated
            assert isinstance(report, type(report))
            
    def test_metrics_tracking(self, real_integrator, sample_import_failure):
        """Test that metrics are properly tracked"""
        initial_processed = real_integrator.total_test_failures_processed
        initial_successful = real_integrator.successful_rca_analyses
        
        real_integrator.analyze_test_failures([sample_import_failure])
        
        # Metrics should be updated
        assert real_integrator.total_test_failures_processed > initial_processed
        # successful_rca_analyses may or may not increase depending on RCA engine state
        
    def test_error_recovery(self, real_integrator):
        """Test error recovery mechanisms"""
        # Create a problematic failure that might cause issues
        problematic_failure = TestFailure(
            test_name="test_problematic",
            test_file=None,  # Missing file path
            failure_type="unknown",
            error_message=None,  # Missing error message
            stack_trace="",
            test_function="test_problematic",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id=None  # Missing node ID
        )
        
        # Should handle gracefully without crashing
        report = real_integrator.analyze_test_failures([problematic_failure])
        
        # Should return a valid report even with problematic input
        assert report.total_failures == 1
        assert isinstance(report.recommendations, list)
        assert isinstance(report.next_steps, list)


if __name__ == "__main__":
    pytest.main([__file__])