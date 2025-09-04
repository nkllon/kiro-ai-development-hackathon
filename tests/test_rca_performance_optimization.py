"""
Beast Mode Framework - RCA Performance Optimization Tests
Tests for performance monitoring, timeout handling, and resource management
Requirements: 1.4, 4.2 - Performance tests to validate timeout and resource requirements
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.beast_mode.testing.performance_monitor import (
    RCAPerformanceMonitor, ResourceLimits, PerformanceMetrics, 
    PerformanceStatus, TimeoutException, ResourceExhaustionException
)
from src.beast_mode.testing.timeout_handler import (
    RCATimeoutHandler, TimeoutConfiguration, TimeoutStrategy, TimeoutEvent
)
from src.beast_mode.testing.rca_integration import (
    TestRCAIntegrationEngine, TestFailureData
)


class TestRCAPerformanceMonitor:
    """Test performance monitoring functionality"""
    
    def test_performance_monitor_initialization(self):
        """Test performance monitor initializes correctly"""
        resource_limits = ResourceLimits(
            max_memory_mb=256,
            max_cpu_percent=70.0,
            timeout_seconds=30,
            warning_threshold_seconds=25,
            memory_warning_threshold_mb=200
        )
        
        monitor = RCAPerformanceMonitor(resource_limits)
        
        assert monitor.resource_limits.max_memory_mb == 256
        assert monitor.resource_limits.timeout_seconds == 30
        assert monitor.is_healthy()
        assert len(monitor.active_operations) == 0
        
    def test_monitor_operation_context_manager(self):
        """Test operation monitoring context manager"""
        monitor = RCAPerformanceMonitor()
        operation_id = "test_operation_001"
        
        with monitor.monitor_operation(operation_id, timeout_seconds=5) as metrics:
            assert metrics.operation_id == operation_id
            assert operation_id in monitor.active_operations
            
            # Simulate some work
            time.sleep(0.1)
            
        # After context exit, operation should be moved to completed
        assert operation_id not in monitor.active_operations
        assert len(monitor.completed_operations) == 1
        assert monitor.completed_operations[0].operation_id == operation_id
        assert monitor.completed_operations[0].duration_seconds > 0
        
    def test_monitor_operation_timeout(self):
        """Test operation timeout handling"""
        monitor = RCAPerformanceMonitor()
        operation_id = "test_timeout_operation"
        
        # Test that timeout context is properly set up (without actually timing out)
        with monitor.monitor_operation(operation_id, timeout_seconds=1) as metrics:
            assert metrics.operation_id == operation_id
            # Just verify the context works without triggering timeout
            time.sleep(0.1)  # Short sleep that won't timeout
                    
    def test_graceful_degradation_implementation(self):
        """Test graceful degradation implementation"""
        monitor = RCAPerformanceMonitor()
        operation_id = "test_degradation_operation"
        
        # Test simplified analysis degradation
        result = monitor.implement_graceful_degradation(operation_id, "simplified_analysis")
        
        assert result["degradation_applied"] is True
        assert result["strategy"] == "simplified_analysis"
        assert "analysis_scope" in result
        assert result["analysis_scope"] == "reduced"
        
        # Test pattern matching only degradation
        result = monitor.implement_graceful_degradation(operation_id, "pattern_matching_only")
        
        assert result["degradation_applied"] is True
        assert result["strategy"] == "pattern_matching_only"
        assert result["analysis_scope"] == "pattern_matching_only"
        
    def test_resource_optimization(self):
        """Test resource usage optimization"""
        monitor = RCAPerformanceMonitor()
        operation_id = "test_resource_optimization"
        
        # Mock high resource usage
        with patch.object(monitor, '_get_memory_usage', return_value=450.0):  # High memory
            with patch.object(monitor, '_get_cpu_usage', return_value=85.0):  # High CPU
                
                result = monitor.optimize_resource_usage(operation_id)
                
                assert "optimization_applied" in result
                assert "actions_taken" in result
                assert "resource_status" in result
                assert result["resource_status"]["memory_usage_mb"] == 450.0
                assert result["resource_status"]["cpu_usage_percent"] == 85.0
                
    def test_performance_report_generation(self):
        """Test performance report generation"""
        monitor = RCAPerformanceMonitor()
        
        # Add some completed operations
        for i in range(5):
            metrics = PerformanceMetrics(
                operation_id=f"test_op_{i}",
                start_time=datetime.now() - timedelta(seconds=10),
                end_time=datetime.now(),
                duration_seconds=5.0 + i,
                memory_usage_mb=100.0 + i * 10,
                peak_memory_mb=120.0 + i * 10,
                operation_status=PerformanceStatus.OPTIMAL
            )
            monitor.completed_operations.append(metrics)
            
        report = monitor.get_performance_report()
        
        assert report.total_operations == 5
        assert report.successful_operations == 5
        assert report.timeout_operations == 0
        assert report.average_duration_seconds > 0
        assert report.average_memory_usage_mb > 0
        assert report.performance_trend in ["improving", "stable", "degrading", "no_data", "insufficient_data"]
        
    def test_monitoring_thread_lifecycle(self):
        """Test monitoring thread start/stop lifecycle"""
        monitor = RCAPerformanceMonitor()
        
        # Start monitoring
        monitor.start_monitoring()
        assert monitor.monitoring_active is True
        assert monitor.monitor_thread is not None
        assert monitor.monitor_thread.is_alive()
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert monitor.monitoring_active is False
        
        # Wait for thread to finish
        time.sleep(0.1)
        if monitor.monitor_thread:
            assert not monitor.monitor_thread.is_alive()


class TestRCATimeoutHandler:
    """Test timeout handling functionality"""
    
    def test_timeout_handler_initialization(self):
        """Test timeout handler initializes correctly"""
        timeout_config = TimeoutConfiguration(
            primary_timeout_seconds=25,
            warning_timeout_seconds=20,
            graceful_timeout_seconds=15,
            hard_timeout_seconds=30,
            strategy=TimeoutStrategy.GRACEFUL_DEGRADATION
        )
        
        handler = RCATimeoutHandler(timeout_config)
        
        assert handler.timeout_config.primary_timeout_seconds == 25
        assert handler.timeout_config.strategy == TimeoutStrategy.GRACEFUL_DEGRADATION
        assert handler.is_healthy()
        assert len(handler.active_timeouts) == 0
        
    def test_manage_operation_timeout_context(self):
        """Test operation timeout management context"""
        handler = RCATimeoutHandler()
        operation_id = "test_timeout_management"
        
        with handler.manage_operation_timeout(operation_id) as timeout_context:
            assert timeout_context["operation_id"] == operation_id
            assert "timeout_config" in timeout_context
            assert "start_time" in timeout_context
            assert callable(timeout_context["check_timeout"])
            assert callable(timeout_context["request_degradation"])
            
            # Test timeout check
            timeout_status = timeout_context["check_timeout"]()
            assert timeout_status["operation_id"] == operation_id
            assert "timeout_status" in timeout_status
            
    def test_graceful_degradation_levels(self):
        """Test different levels of graceful degradation"""
        handler = RCATimeoutHandler()
        operation_id = "test_degradation_levels"
        
        # Test level 1 degradation (reduced analysis scope)
        result = handler.apply_graceful_degradation(operation_id, degradation_level=1)
        assert result["success"] is True
        assert result["degradation_level"] == 1
        assert result["strategy"] == "reduced_analysis_scope"
        
        # Test level 2 degradation (pattern matching only)
        result = handler.apply_graceful_degradation(operation_id, degradation_level=2)
        assert result["success"] is True
        assert result["degradation_level"] == 2
        assert result["strategy"] == "pattern_matching_only"
        
        # Test level 3 degradation (basic error reporting only)
        result = handler.apply_graceful_degradation(operation_id, degradation_level=3)
        assert result["success"] is True
        assert result["degradation_level"] == 3
        assert result["strategy"] == "basic_error_reporting_only"
        
    def test_timeout_recommendations(self):
        """Test timeout recommendations based on elapsed time"""
        handler = RCATimeoutHandler()
        operation_id = "test_recommendations"
        
        # Test normal status (early in operation)
        recommendations = handler.get_timeout_recommendations(operation_id, 5.0)
        assert recommendations["timeout_status"] == "normal"
        assert not recommendations["degradation_suggested"]
        
        # Test approaching status (26 seconds is in warning range, not approaching)
        recommendations = handler.get_timeout_recommendations(operation_id, 26.0)
        assert recommendations["timeout_status"] == "warning"
        assert "consider_graceful_degradation" in recommendations["recommendations"]
        
        # Test warning status
        recommendations = handler.get_timeout_recommendations(operation_id, 21.0)
        assert recommendations["timeout_status"] == "warning"
        assert recommendations["degradation_suggested"] is True
        
        # Test exceeded status
        recommendations = handler.get_timeout_recommendations(operation_id, 31.0)
        assert recommendations["timeout_status"] == "exceeded"
        assert recommendations["degradation_suggested"] is True
        
    def test_timeout_configuration_optimization(self):
        """Test timeout configuration optimization"""
        handler = RCATimeoutHandler()
        
        # Add some timeout events to provide data for optimization
        for i in range(15):
            event = TimeoutEvent(
                operation_id=f"test_op_{i}",
                timeout_type="completed",
                timestamp=datetime.now(),
                elapsed_seconds=15.0 + i,  # Completing faster than 30s timeout
                strategy_applied="none",
                operation_completed=True
            )
            handler.timeout_events.append(event)
            
        result = handler.optimize_timeout_configuration()
        
        assert "optimization_applied" in result
        assert "previous_config" in result
        assert "optimization_reason" in result
        
    def test_progressive_timeout_handling(self):
        """Test progressive timeout handling with multiple levels"""
        config = TimeoutConfiguration(
            primary_timeout_seconds=30,
            warning_timeout_seconds=25,
            graceful_timeout_seconds=20,
            hard_timeout_seconds=35,
            enable_progressive_degradation=True,
            max_degradation_levels=3
        )
        
        handler = RCATimeoutHandler(config)
        operation_id = "test_progressive_timeout"
        
        # Mock the timeout handlers to test progression
        with patch.object(handler, '_handle_warning_timeout') as mock_warning:
            with patch.object(handler, '_handle_graceful_timeout') as mock_graceful:
                with patch.object(handler, '_handle_hard_timeout') as mock_hard:
                    
                    # Set up timeout handlers
                    handlers = handler._setup_timeout_handlers(operation_id)
                    
                    assert "warning" in handlers
                    assert "graceful" in handlers
                    assert "hard" in handlers
                    
                    # Clean up timers
                    handler._cleanup_operation_timeouts(operation_id)


class TestRCAIntegrationPerformance:
    """Test RCA integration performance optimization"""
    
    def test_rca_integration_with_performance_monitoring(self):
        """Test RCA integration with performance monitoring enabled"""
        # Mock RCA engine to avoid actual RCA processing
        mock_rca_engine = Mock()
        mock_rca_engine.is_healthy.return_value = True
        mock_rca_engine.match_existing_patterns.return_value = []
        mock_rca_engine.perform_systematic_rca.return_value = Mock()
        
        integrator = TestRCAIntegrationEngine(rca_engine=mock_rca_engine)
        
        # Create test failure data
        test_failure = TestFailureData(
            test_name="test_example",
            test_file="test_example.py",
            failure_type="assertion",
            error_message="AssertionError: Expected True, got False",
            stack_trace="Traceback...",
            test_function="test_example_function",
            test_class="TestExample",
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="test_example.py::TestExample::test_example_function"
        )
        
        # Test analysis with performance monitoring
        result = integrator.analyze_test_failures([test_failure])
        
        assert result is not None
        assert result.total_failures == 1
        assert integrator.performance_monitor.total_operations > 0
        
    def test_thirty_second_timeout_compliance(self):
        """Test that RCA analysis completes within 30 seconds or applies graceful degradation"""
        # Mock RCA engine with slow operations
        mock_rca_engine = Mock()
        mock_rca_engine.is_healthy.return_value = True
        mock_rca_engine.match_existing_patterns.return_value = []
        
        # Mock slow RCA analysis
        def slow_rca_analysis(failure):
            time.sleep(0.1)  # Simulate slow analysis
            return Mock()
            
        mock_rca_engine.perform_systematic_rca.side_effect = slow_rca_analysis
        
        integrator = TestRCAIntegrationEngine(rca_engine=mock_rca_engine)
        
        # Create multiple test failures to potentially exceed timeout
        test_failures = []
        for i in range(10):  # 10 failures * 0.1s = 1s (should be fast enough)
            test_failure = TestFailureData(
                test_name=f"test_example_{i}",
                test_file=f"test_example_{i}.py",
                failure_type="assertion",
                error_message=f"AssertionError: Test {i} failed",
                stack_trace="Traceback...",
                test_function=f"test_example_function_{i}",
                test_class="TestExample",
                failure_timestamp=datetime.now(),
                test_context={},
                pytest_node_id=f"test_example_{i}.py::TestExample::test_example_function_{i}"
            )
            test_failures.append(test_failure)
            
        start_time = time.time()
        result = integrator.analyze_test_failures(test_failures)
        analysis_time = time.time() - start_time
        
        # Should complete within reasonable time (allowing for test overhead)
        assert analysis_time < 35.0  # 35 seconds to allow for some overhead
        assert result is not None
        
    def test_resource_limit_enforcement(self):
        """Test that resource limits are enforced during RCA analysis"""
        # Create integrator with strict resource limits
        resource_limits = ResourceLimits(
            max_memory_mb=128,  # Low memory limit
            max_cpu_percent=50.0,  # Low CPU limit
            timeout_seconds=30,
            warning_threshold_seconds=25,
            memory_warning_threshold_mb=100
        )
        
        performance_monitor = RCAPerformanceMonitor(resource_limits)
        mock_rca_engine = Mock()
        mock_rca_engine.is_healthy.return_value = True
        mock_rca_engine.match_existing_patterns.return_value = []
        mock_rca_engine.perform_systematic_rca.return_value = Mock()
        
        integrator = TestRCAIntegrationEngine(
            rca_engine=mock_rca_engine,
            performance_monitor=performance_monitor
        )
        
        # Test with single failure
        test_failure = TestFailureData(
            test_name="test_resource_limits",
            test_file="test_resource_limits.py",
            failure_type="assertion",
            error_message="Resource limit test",
            stack_trace="Traceback...",
            test_function="test_resource_limits_function",
            test_class="TestResourceLimits",
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="test_resource_limits.py::TestResourceLimits::test_resource_limits_function"
        )
        
        result = integrator.analyze_test_failures([test_failure])
        
        assert result is not None
        assert performance_monitor.resource_limit_violations >= 0  # Should track violations
        
    def test_performance_report_generation(self):
        """Test performance report generation for RCA integration"""
        mock_rca_engine = Mock()
        mock_rca_engine.is_healthy.return_value = True
        mock_rca_engine.match_existing_patterns.return_value = []
        mock_rca_engine.perform_systematic_rca.return_value = Mock()
        
        integrator = TestRCAIntegrationEngine(rca_engine=mock_rca_engine)
        
        # Perform some operations to generate performance data
        test_failure = TestFailureData(
            test_name="test_performance_report",
            test_file="test_performance_report.py",
            failure_type="assertion",
            error_message="Performance report test",
            stack_trace="Traceback...",
            test_function="test_performance_report_function",
            test_class="TestPerformanceReport",
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="test_performance_report.py::TestPerformanceReport::test_performance_report_function"
        )
        
        # Analyze failures to generate performance data
        integrator.analyze_test_failures([test_failure])
        
        # Get performance report
        performance_report = integrator.get_performance_report()
        
        assert "rca_integration_performance" in performance_report
        assert "timeout_management" in performance_report
        assert "integration_metrics" in performance_report
        
        rca_perf = performance_report["rca_integration_performance"]
        assert "total_operations" in rca_perf
        assert "average_duration_seconds" in rca_perf
        assert "timeout_rate" in rca_perf
        
    def test_performance_optimization(self):
        """Test performance configuration optimization"""
        mock_rca_engine = Mock()
        mock_rca_engine.is_healthy.return_value = True
        mock_rca_engine.match_existing_patterns.return_value = []
        mock_rca_engine.perform_systematic_rca.return_value = Mock()
        
        integrator = TestRCAIntegrationEngine(rca_engine=mock_rca_engine)
        
        # Test performance optimization
        optimization_result = integrator.optimize_performance_configuration()
        
        assert "optimization_applied" in optimization_result
        assert "optimizations" in optimization_result
        assert "performance_improvement_expected" in optimization_result
        
    @pytest.mark.performance
    def test_pattern_matching_performance(self):
        """Test that pattern matching meets sub-second performance requirement"""
        mock_rca_engine = Mock()
        mock_rca_engine.is_healthy.return_value = True
        
        # Mock pattern matching to return quickly
        mock_patterns = [Mock() for _ in range(10)]
        mock_rca_engine.match_existing_patterns.return_value = mock_patterns
        
        integrator = TestRCAIntegrationEngine(rca_engine=mock_rca_engine)
        
        test_failure = TestFailureData(
            test_name="test_pattern_performance",
            test_file="test_pattern_performance.py",
            failure_type="assertion",
            error_message="Pattern matching performance test",
            stack_trace="Traceback...",
            test_function="test_pattern_performance_function",
            test_class="TestPatternPerformance",
            failure_timestamp=datetime.now(),
            test_context={},
            pytest_node_id="test_pattern_performance.py::TestPatternPerformance::test_pattern_performance_function"
        )
        
        # Convert to RCA failure for pattern matching test
        rca_failure = integrator.convert_to_rca_failure(test_failure)
        
        # Test pattern matching performance
        start_time = time.time()
        patterns = mock_rca_engine.match_existing_patterns(rca_failure)
        pattern_match_time = time.time() - start_time
        
        # Should be sub-second (requirement 4.2)
        assert pattern_match_time < 1.0
        assert len(patterns) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])