"""Unit tests for Google Calendar MCP profiling functionality."""

import time
import unittest
from datetime import datetime
from unittest.mock import patch

from src.beast_mode.mcp_integrations.google_calendar.profiling import (
    PerformanceProfiler,
    PerformanceMetrics,
    AggregatedMetrics,
    get_profiler,
    profile,
    profile_block
)


class TestPerformanceMetrics(unittest.TestCase):
    """Test cases for PerformanceMetrics."""
    
    def test_performance_metrics_creation(self):
        """Test creating performance metrics."""
        start_time = datetime.utcnow()
        end_time = datetime.utcnow()
        
        metrics = PerformanceMetrics(
            operation_name="test_operation",
            start_time=start_time,
            end_time=end_time,
            duration_ms=100.0,
            memory_peak_mb=50.0,
            memory_current_mb=40.0,
            cpu_time_ms=80.0
        )
        
        self.assertEqual(metrics.operation_name, "test_operation")
        self.assertEqual(metrics.duration_ms, 100.0)
        self.assertEqual(metrics.duration_seconds, 0.1)
        self.assertEqual(metrics.success_rate, 100.0)
    
    def test_success_rate_calculation(self):
        """Test success rate calculation with errors."""
        metrics = PerformanceMetrics(
            operation_name="test_operation",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_ms=100.0,
            memory_peak_mb=50.0,
            memory_current_mb=40.0,
            cpu_time_ms=80.0,
            call_count=10,
            error_count=2
        )
        
        self.assertEqual(metrics.success_rate, 80.0)


class TestAggregatedMetrics(unittest.TestCase):
    """Test cases for AggregatedMetrics."""
    
    def test_aggregated_metrics_creation(self):
        """Test creating aggregated metrics."""
        aggregated = AggregatedMetrics("test_operation")
        
        self.assertEqual(aggregated.operation_name, "test_operation")
        self.assertEqual(aggregated.total_calls, 0)
        self.assertEqual(aggregated.total_errors, 0)
    
    def test_add_measurement(self):
        """Test adding measurements to aggregated metrics."""
        aggregated = AggregatedMetrics("test_operation")
        
        metrics1 = PerformanceMetrics(
            operation_name="test_operation",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_ms=100.0,
            memory_peak_mb=50.0,
            memory_current_mb=40.0,
            cpu_time_ms=80.0,
            call_count=1,
            error_count=0
        )
        
        metrics2 = PerformanceMetrics(
            operation_name="test_operation",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_ms=200.0,
            memory_peak_mb=60.0,
            memory_current_mb=45.0,
            cpu_time_ms=150.0,
            call_count=1,
            error_count=1
        )
        
        aggregated.add_measurement(metrics1)
        aggregated.add_measurement(metrics2)
        
        self.assertEqual(aggregated.total_calls, 2)
        self.assertEqual(aggregated.total_errors, 1)
        self.assertEqual(aggregated.total_duration_ms, 300.0)
        self.assertEqual(aggregated.avg_duration_ms, 150.0)
        self.assertEqual(aggregated.min_duration_ms, 100.0)
        self.assertEqual(aggregated.max_duration_ms, 200.0)
        self.assertEqual(aggregated.peak_memory_mb, 60.0)


class TestPerformanceProfiler(unittest.TestCase):
    """Test cases for PerformanceProfiler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.profiler = PerformanceProfiler(enable_memory_tracking=False)
    
    def test_profiler_initialization(self):
        """Test profiler initialization."""
        self.assertFalse(self.profiler.enable_memory_tracking)
        self.assertEqual(len(self.profiler.metrics_history), 0)
        self.assertEqual(len(self.profiler.aggregated_metrics), 0)
    
    def test_profile_context(self):
        """Test profiling context manager."""
        with self.profiler.profile_context("test_operation") as metrics:
            time.sleep(0.01)  # Small delay to measure
            self.assertEqual(metrics.operation_name, "test_operation")
        
        # Check that metrics were recorded
        self.assertEqual(len(self.profiler.metrics_history), 1)
        recorded_metrics = self.profiler.metrics_history[0]
        self.assertEqual(recorded_metrics.operation_name, "test_operation")
        self.assertGreater(recorded_metrics.duration_ms, 0)
    
    def test_profile_decorator(self):
        """Test profiling decorator."""
        @self.profiler.profile_operation("decorated_function")
        def test_function():
            time.sleep(0.01)
            return "result"
        
        result = test_function()
        
        self.assertEqual(result, "result")
        self.assertEqual(len(self.profiler.metrics_history), 1)
        self.assertEqual(self.profiler.metrics_history[0].operation_name, "decorated_function")
    
    def test_profile_decorator_with_exception(self):
        """Test profiling decorator with exception."""
        @self.profiler.profile_operation("failing_function")
        def failing_function():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            failing_function()
        
        # Check that error was recorded
        self.assertEqual(len(self.profiler.metrics_history), 1)
        metrics = self.profiler.metrics_history[0]
        self.assertEqual(metrics.error_count, 1)
    
    def test_get_operation_metrics(self):
        """Test getting metrics for specific operation."""
        with self.profiler.profile_context("test_op"):
            pass
        
        metrics = self.profiler.get_operation_metrics("test_op")
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.operation_name, "test_op")
        self.assertEqual(metrics.total_calls, 1)
        
        # Test non-existent operation
        missing_metrics = self.profiler.get_operation_metrics("missing_op")
        self.assertIsNone(missing_metrics)
    
    def test_get_slow_operations(self):
        """Test getting slow operations."""
        # Create fast operation
        with self.profiler.profile_context("fast_op"):
            pass
        
        # Create slow operation (simulate by modifying metrics)
        with self.profiler.profile_context("slow_op"):
            pass
        
        # Manually set duration to make it slow
        self.profiler.metrics_history[1].duration_ms = 2000.0
        
        slow_ops = self.profiler.get_slow_operations(1000.0)
        self.assertEqual(len(slow_ops), 1)
        self.assertEqual(slow_ops[0].operation_name, "slow_op")
    
    def test_generate_performance_report(self):
        """Test generating performance report."""
        # Add some test metrics
        with self.profiler.profile_context("op1"):
            pass
        with self.profiler.profile_context("op2"):
            pass
        
        report = self.profiler.generate_performance_report()
        
        self.assertIn("summary", report)
        self.assertIn("bottlenecks", report)
        self.assertIn("operations", report)
        
        summary = report["summary"]
        self.assertEqual(summary["total_operations"], 2)
        self.assertEqual(summary["total_errors"], 0)
        self.assertEqual(summary["error_rate_percent"], 0.0)
    
    def test_clear_metrics(self):
        """Test clearing metrics."""
        with self.profiler.profile_context("test_op"):
            pass
        
        self.assertEqual(len(self.profiler.metrics_history), 1)
        
        self.profiler.clear_metrics()
        
        self.assertEqual(len(self.profiler.metrics_history), 0)
        self.assertEqual(len(self.profiler.aggregated_metrics), 0)
    
    @patch('builtins.open', create=True)
    def test_export_metrics_csv(self, mock_open):
        """Test exporting metrics to CSV."""
        with self.profiler.profile_context("test_op"):
            pass
        
        mock_file = mock_open.return_value.__enter__.return_value
        
        self.profiler.export_metrics_csv("test.csv")
        
        mock_open.assert_called_once_with("test.csv", 'w', newline='')
        # Verify that write operations were called
        self.assertTrue(mock_file.write.called)


class TestGlobalProfiler(unittest.TestCase):
    """Test cases for global profiler functions."""
    
    def test_get_profiler(self):
        """Test getting global profiler instance."""
        profiler1 = get_profiler()
        profiler2 = get_profiler()
        
        # Should return the same instance
        self.assertIs(profiler1, profiler2)
    
    def test_profile_decorator(self):
        """Test global profile decorator."""
        @profile("global_test")
        def test_function():
            return "success"
        
        result = test_function()
        
        self.assertEqual(result, "success")
        
        # Check that metrics were recorded in global profiler
        profiler = get_profiler()
        self.assertGreater(len(profiler.metrics_history), 0)
    
    def test_profile_block_context(self):
        """Test global profile block context manager."""
        with profile_block("block_test") as metrics:
            self.assertEqual(metrics.operation_name, "block_test")
        
        # Check that metrics were recorded
        profiler = get_profiler()
        self.assertGreater(len(profiler.metrics_history), 0)


class TestDetailedProfiling(unittest.TestCase):
    """Test cases for detailed CPU profiling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.profiler = PerformanceProfiler(enable_memory_tracking=False)
    
    def test_detailed_profiling(self):
        """Test detailed CPU profiling."""
        # Start profiling
        profile_id = self.profiler.start_detailed_profiling("detailed_test")
        
        # Do some work
        def test_work():
            sum(range(1000))
        
        test_work()
        
        # Stop profiling and get results
        results = self.profiler.stop_detailed_profiling(profile_id)
        
        self.assertIsInstance(results, str)
        self.assertIn("function calls", results.lower())
    
    def test_stop_nonexistent_profile(self):
        """Test stopping non-existent profile."""
        result = self.profiler.stop_detailed_profiling("nonexistent")
        self.assertEqual(result, "Profile ID not found")


if __name__ == "__main__":
    unittest.main()