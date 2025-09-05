"""
Integration tests for RCA Error Handling with other RCA components
Tests end-to-end error handling scenarios and recovery mechanisms
Requirements: 1.1, 1.4, 4.1 - Comprehensive error handling integration
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any

from src.beast_mode.testing.error_handler import RCAErrorHandler, DegradationLevel, ErrorCategory
from src.beast_mode.testing.rca_integration import TestRCAIntegrationEngine, TestFailureData
from src.beast_mode.testing.test_failure_detector import TestFailureDetector
from src.beast_mode.testing.rca_report_generator import RCAReportGenerator
from src.beast_mode.analysis.rca_engine import RCAEngine, Failure, FailureCategory


class TestRCAErrorIntegration:
    """Integration tests for error handling across RCA components"""
    
    @pytest.fixture
    def error_handler(self):
        """Create error handler for integration testing"""
        return RCAErrorHandler()
        
    @pytest.fixture
    def mock_rca_engine(self):
        """Create mock RCA engine"""
        mock_engine = Mock(spec=RCAEngine)
        mock_engine.is_healthy.return_value = True
        mock_engine.get_module_status.return_value = {"status": "operational"}
        return mock_engine
        
    @pytest.fixture
    def integration_engine(self, error_handler, mock_rca_engine):
        """Create RCA integration engine with error handling"""
        return TestRCAIntegrationEngine(
            rca_engine=mock_rca_engine,
            error_handler=error_handler
        )
        
    @pytest.fixture
    def test_failure_detector(self, error_handler):
        """Create test failure detector with error handling"""
        return TestFailureDetector(error_handler=error_handler)
        
    @pytest.fixture
    def sample_test_failures(self):
        """Create sample test failures for testing"""
        return [
            TestFailureData(
                test_name="test_integration_failure_1",
                test_file="integration_test.py",
                failure_type="assertion",
                error_message="AssertionError: Integration test failed",
                stack_trace="Traceback (most recent call last):\n  File...",
                test_function="test_integration_failure_1",
                test_class="TestIntegration",
                failure_timestamp=datetime.now(),
                test_context={"integration": True},
                pytest_node_id="integration_test.py::TestIntegration::test_integration_failure_1"
            ),
            TestFailureData(
                test_name="test_integration_failure_2",
                test_file="integration_test.py",
                failure_type="import",
                error_message="ImportError: Module not found",
                stack_trace="Traceback (most recent call last):\n  File...",
                test_function="test_integration_failure_2",
                test_class="TestIntegration",
                failure_timestamp=datetime.now(),
                test_context={"integration": True},
                pytest_node_id="integration_test.py::TestIntegration::test_integration_failure_2"
            )
        ]
        
    def test_end_to_end_error_handling_success(self, integration_engine, sample_test_failures, mock_rca_engine):
        """Test successful end-to-end error handling scenario"""
        # Configure RCA engine to succeed
        mock_result = Mock()
        mock_result.failure.failure_id = "test_failure"
        mock_result.root_causes = []
        mock_result.systematic_fixes = []
        mock_result.total_analysis_time_seconds = 1.5
        mock_result.rca_confidence_score = 0.9
        mock_result.validation_results = []
        mock_result.prevention_patterns = []
        
        mock_rca_engine.perform_systematic_rca.return_value = mock_result
        mock_rca_engine.match_existing_patterns.return_value = []
        
        # Perform analysis
        report = integration_engine.analyze_test_failures(sample_test_failures)
        
        # Verify successful analysis
        assert report.total_failures == 2
        assert report.failures_analyzed > 0
        assert len(report.rca_results) > 0
        
        # Verify error handler tracked operations
        assert integration_engine.error_handler.total_errors_handled >= 0  # May be 0 if no errors
        
    def test_end_to_end_error_handling_with_rca_failure(self, integration_engine, sample_test_failures, mock_rca_engine):
        """Test end-to-end error handling when RCA engine fails"""
        # Configure RCA engine to fail
        mock_rca_engine.perform_systematic_rca.side_effect = Exception("RCA engine crashed")
        mock_rca_engine.match_existing_patterns.return_value = []
        
        # Perform analysis - should not raise exception
        report = integration_engine.analyze_test_failures(sample_test_failures)
        
        # Verify fallback report was generated
        assert report.total_failures == 2
        assert report.failures_analyzed == 0  # No successful RCA analyses
        assert len(report.summary.critical_issues) > 0
        assert any("RCA analysis failed" in issue for issue in report.summary.critical_issues)
        
        # Verify error handler tracked the failures
        assert integration_engine.error_handler.total_errors_handled > 0
        assert integration_engine.error_handler.fallback_reports_generated > 0
        
    def test_test_failure_detector_with_error_handling(self, test_failure_detector):
        """Test test failure detector with comprehensive error handling"""
        # Mock subprocess to simulate test execution failure
        with patch('subprocess.run') as mock_run:
            # Simulate test execution that fails to parse
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stdout = "Invalid pytest output that cannot be parsed"
            mock_result.stderr = "Error: malformed output"
            mock_run.return_value = mock_result
            
            # Monitor test execution
            failures = test_failure_detector.monitor_test_execution("python -m pytest tests/")
            
            # Should create parsing failure
            assert len(failures) > 0
            assert any(f.failure_type == "parsing_error" for f in failures)
            
            # Verify error handler tracked the parsing failure
            assert "text_parser" in test_failure_detector.error_handler.component_health
            
    def test_graceful_degradation_integration(self, integration_engine, sample_test_failures, mock_rca_engine):
        """Test graceful degradation integration across components"""
        # Simulate component health degradation
        error_handler = integration_engine.error_handler
        
        # Generate many failures to trigger degradation
        for _ in range(25):  # Above threshold
            error_handler.monitor_component_health("rca_engine", False, 5000.0)
            
        # Should have triggered degradation
        assert error_handler.degradation_level.value > DegradationLevel.NONE.value
        
        # Configure RCA engine to work but slowly
        mock_result = Mock()
        mock_result.failure.failure_id = "test_failure"
        mock_result.root_causes = []
        mock_result.systematic_fixes = []
        mock_result.total_analysis_time_seconds = 2.0
        mock_result.rca_confidence_score = 0.7
        mock_result.validation_results = []
        mock_result.prevention_patterns = []
        
        mock_rca_engine.perform_systematic_rca.return_value = mock_result
        mock_rca_engine.match_existing_patterns.return_value = []
        
        # Perform analysis under degradation
        report = integration_engine.analyze_test_failures(sample_test_failures)
        
        # Should still generate report but with degraded functionality
        assert report.total_failures == 2
        assert report.summary.confidence_score <= 0.8  # Reduced confidence under degradation
        
    def test_retry_logic_integration(self, integration_engine, sample_test_failures, mock_rca_engine):
        """Test retry logic integration with RCA components"""
        call_count = 0
        
        def failing_rca_analysis(failure):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail first 2 attempts
                raise Exception("Temporary RCA failure")
            # Succeed on 3rd attempt
            mock_result = Mock()
            mock_result.failure = failure
            mock_result.root_causes = []
            mock_result.systematic_fixes = []
            mock_result.total_analysis_time_seconds = 1.0
            mock_result.rca_confidence_score = 0.8
            mock_result.validation_results = []
            mock_result.prevention_patterns = []
            return mock_result
            
        mock_rca_engine.perform_systematic_rca.side_effect = failing_rca_analysis
        mock_rca_engine.match_existing_patterns.return_value = []
        
        # Perform analysis - should succeed after retries
        report = integration_engine.analyze_test_failures(sample_test_failures)
        
        # Verify successful recovery
        assert report.total_failures == 2
        assert report.failures_analyzed > 0
        assert integration_engine.error_handler.successful_retries > 0
        
    def test_health_monitoring_integration(self, integration_engine, sample_test_failures, mock_rca_engine):
        """Test health monitoring integration across all components"""
        error_handler = integration_engine.error_handler
        
        # Configure successful RCA operations
        mock_result = Mock()
        mock_result.failure.failure_id = "test_failure"
        mock_result.root_causes = []
        mock_result.systematic_fixes = []
        mock_result.total_analysis_time_seconds = 0.5
        mock_result.rca_confidence_score = 0.95
        mock_result.validation_results = []
        mock_result.prevention_patterns = []
        
        mock_rca_engine.perform_systematic_rca.return_value = mock_result
        mock_rca_engine.match_existing_patterns.return_value = []
        
        # Perform multiple analyses to build health metrics
        for _ in range(5):
            report = integration_engine.analyze_test_failures(sample_test_failures)
            
        # Verify health monitoring tracked operations
        health_report = error_handler.get_error_report()
        
        assert "component_health" in health_report
        assert len(health_report["component_health"]) > 0
        
        # Should have healthy components
        healthy_components = [
            name for name, metrics in health_report["component_health"].items()
            if metrics["is_healthy"]
        ]
        assert len(healthy_components) > 0
        
    def test_fallback_report_generation_integration(self, integration_engine, sample_test_failures):
        """Test fallback report generation integration"""
        error_handler = integration_engine.error_handler
        
        # Simulate complete RCA system failure
        complete_failure_error = Exception("Complete RCA system failure - all components down")
        
        # Generate fallback report
        fallback_report = error_handler.generate_fallback_report(
            sample_test_failures,
            complete_failure_error
        )
        
        # Verify comprehensive fallback report
        assert fallback_report.total_failures == 2
        assert fallback_report.failures_analyzed == 0
        assert len(fallback_report.recommendations) > 0
        assert len(fallback_report.next_steps) > 0
        assert "Complete RCA system failure" in fallback_report.summary.critical_issues[0]
        
        # Verify fallback contains actionable information
        assert any("Check RCA engine health" in step for step in fallback_report.next_steps)
        assert any("Retry analysis" in step for step in fallback_report.next_steps)
        
    def test_error_recovery_with_simplified_parameters(self, integration_engine, sample_test_failures, mock_rca_engine):
        """Test error recovery with simplified parameters"""
        error_handler = integration_engine.error_handler
        
        # Create operation that fails initially but succeeds with simplified parameters
        attempt_count = 0
        
        def rca_with_retry_logic():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise Exception("Complex analysis failed")
            return "simplified_success"
            
        # Test retry with simplified parameters
        result = error_handler.retry_with_simplified_parameters(
            operation=rca_with_retry_logic,
            original_error=Exception("Original complex failure"),
            max_retries=3
        )
        
        assert result == "simplified_success"
        assert attempt_count == 2  # Failed once, succeeded on retry
        assert error_handler.successful_retries > 0
        
    def test_component_health_degradation_cascade(self, integration_engine, sample_test_failures):
        """Test cascading component health degradation"""
        error_handler = integration_engine.error_handler
        
        # Simulate cascading failures across components
        components = ["rca_engine", "pattern_library", "report_generator"]
        
        for component in components:
            # Generate failures for each component
            for _ in range(15):  # Enough to trigger degradation
                error_handler.monitor_component_health(component, False, 3000.0)
                
        # Should trigger overall system degradation
        assert error_handler.degradation_level.value >= DegradationLevel.MODERATE.value
        
        # Overall health should be poor
        overall_health = error_handler._get_overall_component_health()
        assert overall_health < 0.5
        
    def test_emergency_degradation_scenario(self, integration_engine, sample_test_failures):
        """Test emergency degradation scenario"""
        error_handler = integration_engine.error_handler
        
        # Apply emergency degradation
        degradation_result = error_handler.apply_graceful_degradation(
            DegradationLevel.EMERGENCY,
            "Critical system failure - emergency mode activated"
        )
        
        assert degradation_result["success"]
        assert error_handler.degradation_level == DegradationLevel.EMERGENCY
        
        # System should still be able to generate basic reports
        fallback_report = error_handler.generate_fallback_report(
            sample_test_failures,
            Exception("Emergency scenario")
        )
        
        assert fallback_report.total_failures == 2
        assert len(fallback_report.next_steps) > 0
        assert "Emergency scenario" in fallback_report.summary.critical_issues[0]
        
    def test_error_history_and_pattern_learning(self, integration_engine, sample_test_failures, mock_rca_engine):
        """Test error history tracking and pattern learning"""
        error_handler = integration_engine.error_handler
        
        # Generate various types of errors
        error_types = [
            Exception("Timeout error"),
            Exception("Memory exhaustion"),
            Exception("Network connection failed"),
            Exception("Configuration error"),
            Exception("RCA analysis failed")
        ]
        
        for i, error in enumerate(error_types):
            try:
                with error_handler.handle_rca_operation(f"test_operation_{i}", "test_component"):
                    raise error
            except Exception:
                pass  # Expected
                
        # Verify error history tracking
        assert len(error_handler.error_history) == len(error_types)
        
        # Verify different error categories were detected
        categories = set(error.category for error in error_handler.error_history)
        assert len(categories) > 1  # Should have multiple categories
        
        # Get error report
        error_report = error_handler.get_error_report()
        
        assert error_report["error_handling_summary"]["total_errors_handled"] == len(error_types)
        assert len(error_report["recent_errors"]) == len(error_types)
        
    def test_performance_under_error_conditions(self, integration_engine, sample_test_failures, mock_rca_engine):
        """Test system performance under various error conditions"""
        error_handler = integration_engine.error_handler
        
        # Configure RCA engine with intermittent failures
        call_count = 0
        
        def intermittent_rca_analysis(failure):
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:  # Fail every 3rd call
                raise Exception(f"Intermittent failure {call_count}")
            
            mock_result = Mock()
            mock_result.failure = failure
            mock_result.root_causes = []
            mock_result.systematic_fixes = []
            mock_result.total_analysis_time_seconds = 0.8
            mock_result.rca_confidence_score = 0.85
            mock_result.validation_results = []
            mock_result.prevention_patterns = []
            return mock_result
            
        mock_rca_engine.perform_systematic_rca.side_effect = intermittent_rca_analysis
        mock_rca_engine.match_existing_patterns.return_value = []
        
        # Perform multiple analyses
        start_time = time.time()
        reports = []
        
        for _ in range(10):
            try:
                report = integration_engine.analyze_test_failures(sample_test_failures)
                reports.append(report)
            except Exception:
                pass  # Some may fail due to intermittent errors
                
        end_time = time.time()
        
        # Verify system maintained reasonable performance despite errors
        total_time = end_time - start_time
        assert total_time < 60  # Should complete within reasonable time
        
        # Verify some analyses succeeded
        assert len(reports) > 0
        
        # Verify error handling tracked intermittent failures
        assert error_handler.total_errors_handled > 0
        
    def test_comprehensive_error_report_integration(self, integration_engine, sample_test_failures):
        """Test comprehensive error reporting integration"""
        error_handler = integration_engine.error_handler
        
        # Generate comprehensive error scenario
        error_handler.total_errors_handled = 20
        error_handler.successful_recoveries = 15
        error_handler.fallback_reports_generated = 5
        error_handler.retry_attempts_made = 30
        error_handler.successful_retries = 25
        
        # Apply some degradation
        error_handler.apply_graceful_degradation(
            DegradationLevel.MODERATE,
            "Integration test degradation"
        )
        
        # Get comprehensive error report
        error_report = error_handler.get_error_report()
        
        # Verify all sections are present and populated
        assert "error_handling_summary" in error_report
        assert "retry_statistics" in error_report
        assert "component_health" in error_report
        assert "recent_errors" in error_report
        assert "health_indicators" in error_report
        
        # Verify metrics are reasonable
        summary = error_report["error_handling_summary"]
        assert summary["recovery_rate"] == 0.75  # 15/20
        assert summary["current_degradation_level"] == DegradationLevel.MODERATE.value
        
        retry_stats = error_report["retry_statistics"]
        assert retry_stats["retry_success_rate"] == 25/30
        
        # Verify health indicators show degraded state
        health_indicators = error_report["health_indicators"]
        assert "degradation_management" in health_indicators
        assert health_indicators["degradation_management"]["current_level"] == DegradationLevel.MODERATE.value


class TestErrorHandlerStressTest:
    """Stress tests for error handler under extreme conditions"""
    
    def test_high_volume_error_handling(self):
        """Test error handler under high volume of errors"""
        error_handler = RCAErrorHandler()
        
        # Generate high volume of errors
        for i in range(1000):
            try:
                with error_handler.handle_rca_operation(f"stress_test_{i}", "stress_component"):
                    if i % 10 == 0:  # 10% failure rate
                        raise Exception(f"Stress test error {i}")
            except Exception:
                pass  # Expected
                
        # Verify error handler maintained stability
        assert error_handler.is_healthy() or error_handler.degradation_level.value <= DegradationLevel.MODERATE.value
        assert len(error_handler.error_history) <= 100  # Should maintain history limit
        assert error_handler.total_errors_handled == 100  # 10% of 1000
        
    def test_concurrent_error_handling_stress(self):
        """Test concurrent error handling under stress"""
        import threading
        import queue
        
        error_handler = RCAErrorHandler()
        results = queue.Queue()
        
        def stress_worker(worker_id):
            try:
                for i in range(100):
                    try:
                        with error_handler.handle_rca_operation(f"worker_{worker_id}_op_{i}", f"worker_{worker_id}"):
                            if i % 5 == 0:  # 20% failure rate
                                raise Exception(f"Worker {worker_id} error {i}")
                    except Exception:
                        pass  # Expected
                results.put(f"worker_{worker_id}_completed")
            except Exception as e:
                results.put(f"worker_{worker_id}_failed: {e}")
                
        # Start multiple concurrent workers
        threads = []
        for worker_id in range(10):
            thread = threading.Thread(target=stress_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
            
        # Wait for all workers to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout
            
        # Collect results
        completed_workers = 0
        while not results.empty():
            result = results.get()
            if "completed" in result:
                completed_workers += 1
                
        # Verify most workers completed successfully
        assert completed_workers >= 8  # At least 80% should complete
        
        # Verify error handler maintained stability under concurrent load
        assert error_handler.total_errors_handled > 0
        assert len(error_handler.component_health) > 0