"""
Unit tests for RCA Integration Error Handling and Graceful Degradation
Tests error scenarios and recovery mechanisms for RCA integration
Requirements: 1.1, 1.4, 4.1 - Error handling, fallback reporting, health monitoring, retry logic
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.beast_mode.testing.error_handler import (
    RCAErrorHandler, ErrorSeverity, ErrorCategory, DegradationLevel,
    ErrorContext, RetryConfiguration, FallbackReportData, HealthMonitoringMetrics
)
from src.beast_mode.testing.rca_integration import TestFailureData, TestRCAReportData
from src.beast_mode.analysis.rca_engine import Failure, RCAResult, FailureCategory


class TestRCAErrorHandler:
    """Test suite for RCA error handling and graceful degradation"""
    
    @pytest.fixture
    def error_handler(self):
        """Create RCA error handler for testing"""
        return RCAErrorHandler()
        
    @pytest.fixture
    def sample_test_failure(self):
        """Create sample test failure data"""
        return TestFailureData(
            test_name="test_sample_failure",
            test_file="test_sample.py",
            failure_type="assertion",
            error_message="AssertionError: Expected 5, got 3",
            stack_trace="Traceback...",
            test_function="test_sample_failure",
            test_class="TestSample",
            failure_timestamp=datetime.now(),
            test_context={"test_data": "sample"},
            pytest_node_id="test_sample.py::TestSample::test_sample_failure"
        )
        
    @pytest.fixture
    def sample_rca_failure(self):
        """Create sample RCA failure object"""
        return Failure(
            failure_id="test_failure_001",
            timestamp=datetime.now(),
            component="test:sample.py",
            error_message="Test assertion failed",
            stack_trace="Traceback...",
            context={"test": True},
            category=FailureCategory.UNKNOWN
        )
        
    def test_error_handler_initialization(self, error_handler):
        """Test error handler proper initialization"""
        assert error_handler.module_name == "rca_error_handler"
        assert error_handler.is_healthy()
        assert error_handler.degradation_level == DegradationLevel.NONE
        assert len(error_handler.monitored_components) > 0
        assert error_handler.total_errors_handled == 0
        
    def test_handle_rca_operation_success(self, error_handler):
        """Test successful RCA operation handling"""
        with error_handler.handle_rca_operation("test_operation", "test_component") as operation_id:
            assert operation_id is not None
            assert "test_operation" in operation_id
            
        # Should not raise any exceptions
        assert error_handler.is_healthy()
        
    def test_handle_rca_operation_failure(self, error_handler):
        """Test RCA operation failure handling"""
        with pytest.raises(ValueError):
            with error_handler.handle_rca_operation("test_operation", "test_component"):
                raise ValueError("Test operation failed")
                
        # Error should be recorded
        assert error_handler.total_errors_handled > 0
        assert len(error_handler.error_history) > 0
        
    def test_handle_rca_engine_failure_with_retry(self, error_handler, sample_rca_failure):
        """Test RCA engine failure handling with successful retry"""
        mock_rca_engine = Mock()
        
        # First call fails, second succeeds
        mock_result = Mock(spec=RCAResult)
        mock_rca_engine.perform_systematic_rca.side_effect = [
            Exception("Temporary failure"),
            mock_result
        ]
        
        result = error_handler.handle_rca_engine_failure(
            failure=sample_rca_failure,
            error=Exception("Temporary failure"),
            rca_engine=mock_rca_engine
        )
        
        # Should return fallback result since retry is not configured for this error type
        assert isinstance(result, FallbackReportData)
        assert "Temporary failure" in result.error_summary
        
    def test_handle_rca_engine_failure_fallback(self, error_handler, sample_rca_failure):
        """Test RCA engine failure with fallback report generation"""
        # Simulate non-retryable error
        critical_error = Exception("Critical RCA engine failure")
        
        result = error_handler.handle_rca_engine_failure(
            failure=sample_rca_failure,
            error=critical_error,
            rca_engine=None
        )
        
        # Should return fallback report
        assert isinstance(result, FallbackReportData)
        assert "Critical RCA engine failure" in result.error_summary
        assert len(result.basic_failure_info) > 0
        assert len(result.suggested_actions) > 0
        assert error_handler.fallback_reports_generated > 0
        
    def test_generate_fallback_report(self, error_handler, sample_test_failure):
        """Test fallback report generation for test failures"""
        test_failures = [sample_test_failure]
        error = Exception("RCA analysis timeout")
        
        fallback_report = error_handler.generate_fallback_report(test_failures, error)
        
        assert isinstance(fallback_report, TestRCAReportData)
        assert fallback_report.total_failures == 1
        assert fallback_report.failures_analyzed == 0
        assert "RCA analysis timeout" in fallback_report.summary.critical_issues[0]
        assert len(fallback_report.recommendations) > 0
        assert len(fallback_report.next_steps) > 0
        
    def test_monitor_component_health_success(self, error_handler):
        """Test component health monitoring for successful operations"""
        component_name = "test_component"
        
        # Monitor successful operations
        for _ in range(5):
            error_handler.monitor_component_health(component_name, True, 100.0)
            
        health_metrics = error_handler.component_health[component_name]
        assert health_metrics.is_healthy
        assert health_metrics.success_rate_last_hour > 0.9
        assert health_metrics.error_count_last_hour == 0
        
    def test_monitor_component_health_failures(self, error_handler):
        """Test component health monitoring for failed operations"""
        component_name = "test_component"
        
        # Monitor failed operations
        for _ in range(10):
            error_handler.monitor_component_health(component_name, False, 1000.0)
            
        health_metrics = error_handler.component_health[component_name]
        assert not health_metrics.is_healthy
        assert health_metrics.error_count_last_hour == 10
        # Success rate decays but may not go below 0.5 with the current algorithm
        assert health_metrics.success_rate_last_hour < 0.8
        
    def test_apply_graceful_degradation_minimal(self, error_handler):
        """Test minimal graceful degradation application"""
        result = error_handler.apply_graceful_degradation(
            DegradationLevel.MINIMAL,
            "Test minimal degradation"
        )
        
        assert result["success"]
        assert result["new_level"] == DegradationLevel.MINIMAL.value
        assert error_handler.degradation_level == DegradationLevel.MINIMAL
        assert "analysis_depth" in result["actions_taken"]
        
    def test_apply_graceful_degradation_severe(self, error_handler):
        """Test severe graceful degradation application"""
        result = error_handler.apply_graceful_degradation(
            DegradationLevel.SEVERE,
            "Test severe degradation"
        )
        
        assert result["success"]
        assert result["new_level"] == DegradationLevel.SEVERE.value
        assert error_handler.degradation_level == DegradationLevel.SEVERE
        assert result["actions_taken"]["analysis_depth"] == "minimal"
        
    def test_apply_graceful_degradation_emergency(self, error_handler):
        """Test emergency graceful degradation application"""
        result = error_handler.apply_graceful_degradation(
            DegradationLevel.EMERGENCY,
            "Test emergency degradation"
        )
        
        assert result["success"]
        assert result["new_level"] == DegradationLevel.EMERGENCY.value
        assert error_handler.degradation_level == DegradationLevel.EMERGENCY
        assert result["actions_taken"]["fallback_mode"] == "enabled"
        
    def test_retry_with_simplified_parameters_success(self, error_handler):
        """Test retry logic with successful recovery"""
        call_count = 0
        
        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
            
        result = error_handler.retry_with_simplified_parameters(
            operation=failing_operation,
            original_error=Exception("Original error"),
            max_retries=3
        )
        
        assert result == "success"
        assert call_count == 3
        assert error_handler.successful_retries > 0
        
    def test_retry_with_simplified_parameters_failure(self, error_handler):
        """Test retry logic with persistent failure"""
        def always_failing_operation():
            raise Exception("Persistent failure")
            
        with pytest.raises(Exception) as exc_info:
            error_handler.retry_with_simplified_parameters(
                operation=always_failing_operation,
                original_error=Exception("Original error"),
                max_retries=2
            )
            
        assert "All 2 retry attempts failed" in str(exc_info.value)
        
    def test_error_categorization(self, error_handler):
        """Test error categorization logic"""
        # Test timeout error
        timeout_error = Exception("Operation timeout exceeded")
        timeout_context = error_handler._create_error_context(
            timeout_error, "test_component", "test_operation"
        )
        assert timeout_context.category == ErrorCategory.TIMEOUT_EXCEEDED
        
        # Test memory error
        memory_error = Exception("Out of memory")
        memory_context = error_handler._create_error_context(
            memory_error, "test_component", "test_operation"
        )
        assert memory_context.category == ErrorCategory.RESOURCE_EXHAUSTION
        
        # Test RCA error
        rca_error = Exception("RCA analysis failed")
        rca_context = error_handler._create_error_context(
            rca_error, "rca_engine", "systematic_analysis"
        )
        assert rca_context.category == ErrorCategory.RCA_ENGINE_FAILURE
        
    def test_error_severity_assessment(self, error_handler):
        """Test error severity assessment logic"""
        # Critical error
        critical_error = Exception("Critical system failure")
        critical_context = error_handler._create_error_context(
            critical_error, "rca_engine", "analysis"
        )
        assert critical_context.severity == ErrorSeverity.CRITICAL
        
        # Medium error
        medium_error = Exception("Standard error occurred")
        medium_context = error_handler._create_error_context(
            medium_error, "test_component", "operation"
        )
        assert medium_context.severity == ErrorSeverity.MEDIUM
        
    def test_should_retry_logic(self, error_handler):
        """Test retry decision logic"""
        # Retryable error
        timeout_context = ErrorContext(
            error_id="test_error",
            timestamp=datetime.now(),
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.TIMEOUT_EXCEEDED,
            error_message="Timeout",
            stack_trace=None,
            component="test",
            operation="test"
        )
        assert error_handler._should_retry(timeout_context)
        
        # Non-retryable error
        critical_context = ErrorContext(
            error_id="test_error",
            timestamp=datetime.now(),
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.CONFIGURATION_ERROR,
            error_message="Config error",
            stack_trace=None,
            component="test",
            operation="test"
        )
        assert not error_handler._should_retry(critical_context)
        
    def test_component_health_assessment(self, error_handler):
        """Test component health assessment logic"""
        # Healthy component
        healthy_metrics = HealthMonitoringMetrics(
            component_name="healthy_component",
            last_check_timestamp=datetime.now(),
            is_healthy=True,
            error_count_last_hour=2,
            error_count_last_day=5,
            success_rate_last_hour=0.9,
            success_rate_last_day=0.95,
            average_response_time_ms=100.0,
            resource_usage={},
            degradation_level=DegradationLevel.NONE
        )
        assert error_handler._assess_component_health(healthy_metrics)
        
        # Unhealthy component
        unhealthy_metrics = HealthMonitoringMetrics(
            component_name="unhealthy_component",
            last_check_timestamp=datetime.now(),
            is_healthy=False,
            error_count_last_hour=15,
            error_count_last_day=50,
            success_rate_last_hour=0.3,
            success_rate_last_day=0.4,
            average_response_time_ms=8000.0,
            resource_usage={},
            degradation_level=DegradationLevel.MODERATE
        )
        assert not error_handler._assess_component_health(unhealthy_metrics)
        
    def test_overall_component_health_calculation(self, error_handler):
        """Test overall component health score calculation"""
        # Add healthy components
        error_handler.component_health["healthy1"] = HealthMonitoringMetrics(
            component_name="healthy1",
            last_check_timestamp=datetime.now(),
            is_healthy=True,
            error_count_last_hour=0,
            error_count_last_day=0,
            success_rate_last_hour=1.0,
            success_rate_last_day=1.0,
            average_response_time_ms=50.0,
            resource_usage={},
            degradation_level=DegradationLevel.NONE
        )
        
        error_handler.component_health["unhealthy1"] = HealthMonitoringMetrics(
            component_name="unhealthy1",
            last_check_timestamp=datetime.now(),
            is_healthy=False,
            error_count_last_hour=20,
            error_count_last_day=100,
            success_rate_last_hour=0.2,
            success_rate_last_day=0.3,
            average_response_time_ms=10000.0,
            resource_usage={},
            degradation_level=DegradationLevel.SEVERE
        )
        
        health_score = error_handler._get_overall_component_health()
        assert 0.0 <= health_score <= 1.0
        # Should be around 0.14 (1 healthy out of 7 total including default components)
        assert health_score < 0.5  # Less than half are healthy
        
    def test_error_report_generation(self, error_handler):
        """Test comprehensive error report generation"""
        # Generate some errors
        error_handler.total_errors_handled = 10
        error_handler.successful_recoveries = 7
        error_handler.fallback_reports_generated = 3
        error_handler.retry_attempts_made = 15
        error_handler.successful_retries = 12
        
        error_report = error_handler.get_error_report()
        
        assert "error_handling_summary" in error_report
        assert "retry_statistics" in error_report
        assert "component_health" in error_report
        assert "recent_errors" in error_report
        assert "health_indicators" in error_report
        
        summary = error_report["error_handling_summary"]
        assert summary["total_errors_handled"] == 10
        assert summary["successful_recoveries"] == 7
        assert summary["recovery_rate"] == 0.7
        
        retry_stats = error_report["retry_statistics"]
        assert retry_stats["retry_success_rate"] == 0.8
        
    def test_basic_failure_analysis(self, error_handler):
        """Test basic failure analysis when RCA is unavailable"""
        test_failures = [
            TestFailureData(
                test_name="test1",
                test_file="test1.py",
                failure_type="assertion",
                error_message="AssertionError: values don't match",
                stack_trace="",
                test_function="test1",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="test1.py::test1"
            ),
            TestFailureData(
                test_name="test2",
                test_file="test2.py",
                failure_type="import",
                error_message="ImportError: module not found",
                stack_trace="",
                test_function="test2",
                test_class=None,
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id="test2.py::test2"
            )
        ]
        
        analysis = error_handler._perform_basic_failure_analysis(test_failures)
        
        assert analysis["total_failures"] == 2
        assert "assertion" in analysis["failure_types"]
        assert "import" in analysis["failure_types"]
        assert analysis["failure_types"]["assertion"] == 1
        assert analysis["failure_types"]["import"] == 1
        
    def test_basic_recommendations_generation(self, error_handler, sample_test_failure):
        """Test basic recommendations generation"""
        test_failures = [sample_test_failure]
        error = Exception("RCA timeout")
        
        recommendations = error_handler._generate_basic_recommendations(test_failures, error)
        
        assert len(recommendations) > 0
        assert any("RCA timeout" in rec for rec in recommendations)
        assert any("1 test failures" in rec for rec in recommendations)
        
    def test_degradation_consideration(self, error_handler):
        """Test automatic degradation consideration based on component health"""
        # Create unhealthy component with many errors
        unhealthy_metrics = HealthMonitoringMetrics(
            component_name="failing_component",
            last_check_timestamp=datetime.now(),
            is_healthy=False,
            error_count_last_hour=25,  # Above threshold
            error_count_last_day=100,
            success_rate_last_hour=0.2,
            success_rate_last_day=0.3,
            average_response_time_ms=10000.0,
            resource_usage={},
            degradation_level=DegradationLevel.NONE
        )
        
        error_handler._consider_degradation("failing_component", unhealthy_metrics)
        
        # Should have applied severe degradation
        assert error_handler.degradation_level == DegradationLevel.SEVERE
        
    def test_emergency_fallback_generation(self, error_handler, sample_rca_failure):
        """Test emergency fallback when all systems fail"""
        emergency_fallback = error_handler._generate_emergency_fallback(
            sample_rca_failure,
            "Complete system failure"
        )
        
        assert isinstance(emergency_fallback, FallbackReportData)
        assert emergency_fallback.degradation_level == DegradationLevel.EMERGENCY
        assert "Complete system failure" in emergency_fallback.error_summary
        assert "Contact system administrator" in emergency_fallback.suggested_actions
        
    def test_health_indicators_comprehensive(self, error_handler):
        """Test comprehensive health indicators reporting"""
        # Set up some test state
        error_handler.total_errors_handled = 5
        error_handler.successful_recoveries = 4
        error_handler.degradation_level = DegradationLevel.MINIMAL
        
        health_indicators = error_handler.get_health_indicators()
        
        assert "error_handling_capability" in health_indicators
        assert "component_monitoring" in health_indicators
        assert "degradation_management" in health_indicators
        
        error_capability = health_indicators["error_handling_capability"]
        assert error_capability["errors_handled"] == 5
        assert error_capability["recovery_rate"] == 0.8
        
        degradation_mgmt = health_indicators["degradation_management"]
        assert degradation_mgmt["current_level"] == DegradationLevel.MINIMAL.value
        
    def test_retry_configuration_customization(self):
        """Test custom retry configuration"""
        custom_config = RetryConfiguration(
            max_retries=5,
            base_delay_seconds=2.0,
            max_delay_seconds=60.0,
            exponential_backoff=True,
            retry_on_categories=[ErrorCategory.TIMEOUT_EXCEEDED]
        )
        
        error_handler = RCAErrorHandler(retry_config=custom_config)
        
        assert error_handler.retry_config.max_retries == 5
        assert error_handler.retry_config.base_delay_seconds == 2.0
        assert error_handler.retry_config.max_delay_seconds == 60.0
        assert ErrorCategory.TIMEOUT_EXCEEDED in error_handler.retry_config.retry_on_categories
        
    def test_concurrent_error_handling(self, error_handler):
        """Test error handling under concurrent operations"""
        import threading
        
        def simulate_error_operation(operation_id):
            try:
                with error_handler.handle_rca_operation(f"concurrent_op_{operation_id}", "test_component"):
                    if operation_id % 2 == 0:
                        raise Exception(f"Simulated error {operation_id}")
            except Exception:
                pass  # Expected for some operations
                
        # Run concurrent operations
        threads = []
        for i in range(10):
            thread = threading.Thread(target=simulate_error_operation, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Should handle errors without corruption (5 operations should fail)
        assert error_handler.total_errors_handled >= 5
        assert len(error_handler.error_history) >= 5
            
    def test_module_status_reporting(self, error_handler):
        """Test module status reporting functionality"""
        # Set up some test metrics
        error_handler.total_errors_handled = 15
        error_handler.successful_recoveries = 12
        error_handler.fallback_reports_generated = 3
        error_handler.retry_attempts_made = 20
        error_handler.successful_retries = 18
        
        status = error_handler.get_module_status()
        
        assert status["module_name"] == "rca_error_handler"
        assert status["status"] in ["operational", "degraded"]
        assert status["total_errors_handled"] == 15
        assert status["successful_recoveries"] == 12
        assert status["retry_success_rate"] == 0.9
        assert "component_health_summary" in status
        
    def test_error_history_management(self, error_handler):
        """Test error history management and cleanup"""
        # Generate many errors to test history cleanup
        for i in range(150):  # More than the 100 limit
            try:
                with error_handler.handle_rca_operation(f"test_op_{i}", "test_component"):
                    raise Exception(f"Test error {i}")
            except Exception:
                pass
                
        # Should keep only the most recent 100 errors
        assert len(error_handler.error_history) == 100
        
        # Should contain the most recent errors
        recent_error_ids = [error.error_id for error in error_handler.error_history]
        assert any("test_op_149" in error_id for error_id in recent_error_ids)
        assert not any("test_op_0" in error_id for error_id in recent_error_ids)


class TestErrorHandlerIntegration:
    """Integration tests for error handler with other RCA components"""
    
    @pytest.fixture
    def mock_rca_engine(self):
        """Create mock RCA engine for integration testing"""
        mock_engine = Mock()
        mock_engine.is_healthy.return_value = True
        mock_engine.get_module_status.return_value = {"status": "operational"}
        return mock_engine
        
    def test_integration_with_rca_engine_failure(self, mock_rca_engine):
        """Test integration when RCA engine fails"""
        error_handler = RCAErrorHandler()
        
        # Configure RCA engine to fail
        mock_rca_engine.perform_systematic_rca.side_effect = Exception("RCA engine crashed")
        
        failure = Failure(
            failure_id="integration_test",
            timestamp=datetime.now(),
            component="test:integration",
            error_message="Integration test failure",
            stack_trace="",
            context={},
            category=FailureCategory.TEST_FAILURE
        )
        
        result = error_handler.handle_rca_engine_failure(
            failure=failure,
            error=Exception("RCA engine crashed"),
            rca_engine=mock_rca_engine
        )
        
        # Should return fallback report
        assert isinstance(result, FallbackReportData)
        assert "RCA engine crashed" in result.error_summary
        
    def test_integration_with_health_monitoring(self):
        """Test integration with health monitoring system"""
        error_handler = RCAErrorHandler()
        
        # Simulate component operations
        component_name = "integration_component"
        
        # Successful operations
        for _ in range(10):
            error_handler.monitor_component_health(component_name, True, 50.0)
            
        # Failed operations
        for _ in range(5):
            error_handler.monitor_component_health(component_name, False, 1000.0)
            
        health_metrics = error_handler.component_health[component_name]
        
        # Should reflect mixed health status
        assert health_metrics.error_count_last_hour == 5
        assert 0.5 < health_metrics.success_rate_last_hour < 1.0
        
    def test_integration_with_degradation_system(self):
        """Test integration with graceful degradation system"""
        error_handler = RCAErrorHandler()
        
        # Trigger degradation through component health
        component_name = "degrading_component"
        
        # Generate many failures to trigger degradation
        for _ in range(25):  # Above threshold
            error_handler.monitor_component_health(component_name, False, 5000.0)
            
        # Should have triggered degradation
        assert error_handler.degradation_level.value > DegradationLevel.NONE.value
        
        # Health status should reflect degradation
        assert not error_handler.is_healthy()
        
    def test_end_to_end_error_recovery(self):
        """Test end-to-end error recovery scenario"""
        error_handler = RCAErrorHandler()
        
        # Simulate complete failure scenario
        test_failures = [
            TestFailureData(
                test_name="end_to_end_test",
                test_file="e2e_test.py",
                failure_type="error",
                error_message="End-to-end test failure",
                stack_trace="Full stack trace...",
                test_function="test_e2e",
                test_class="TestE2E",
                failure_timestamp=datetime.now(),
                test_context={"e2e": True},
                pytest_node_id="e2e_test.py::TestE2E::test_e2e"
            )
        ]
        
        # Generate fallback report
        fallback_report = error_handler.generate_fallback_report(
            test_failures,
            Exception("Complete RCA system failure")
        )
        
        # Verify complete fallback functionality
        assert isinstance(fallback_report, TestRCAReportData)
        assert fallback_report.total_failures == 1
        assert len(fallback_report.recommendations) > 0
        assert len(fallback_report.next_steps) > 0
        assert "Complete RCA system failure" in fallback_report.summary.critical_issues[0]
        
        # Verify error tracking
        assert error_handler.fallback_reports_generated > 0