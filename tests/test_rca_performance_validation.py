"""
Performance Validation Tests for RCA Integration - Task 11
Tests 30-second analysis requirement and performance benchmarks
Requirements: 1.4, 4.2 - Performance requirements validation
"""

import pytest
import time
import threading
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None
import os
import sys
import gc
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from beast_mode.testing.test_failure_detector import TestFailureDetector
from beast_mode.testing.rca_integration import TestRCAIntegrationEngine, TestFailureData
from beast_mode.testing.rca_report_generator import RCAReportGenerator


class TestPerformanceBenchmarks:
    """Performance benchmark tests for RCA integration"""
    
    @pytest.fixture
    def performance_monitor(self):
        """Performance monitoring utilities"""
        class PerformanceMonitor:
            def __init__(self):
                if HAS_PSUTIL:
                    self.process = psutil.Process(os.getpid())
                else:
                    self.process = None
                self.start_time = None
                self.start_memory = None
                self.start_cpu = None
                
            def start_monitoring(self):
                self.start_time = time.time()
                if HAS_PSUTIL and self.process:
                    self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                    self.start_cpu = self.process.cpu_percent()
                else:
                    self.start_memory = 0
                    self.start_cpu = 0
                
            def get_metrics(self):
                end_time = time.time()
                if HAS_PSUTIL and self.process:
                    end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                    end_cpu = self.process.cpu_percent()
                else:
                    end_memory = 0
                    end_cpu = 0
                
                return {
                    'elapsed_time': end_time - self.start_time,
                    'memory_delta': end_memory - self.start_memory,
                    'cpu_usage': end_cpu,
                    'peak_memory': end_memory
                }
                
        return PerformanceMonitor()
        
    @pytest.fixture
    def large_failure_dataset(self):
        """Create large dataset of test failures for performance testing"""
        failures = []
        base_time = datetime.now()
        
        # Create 100 test failures with varied characteristics
        for i in range(100):
            failure_types = ["error", "assertion", "timeout"]
            error_messages = [
                f"ImportError: No module named 'module_{i}'",
                f"AssertionError: Expected {i}, got {i+1}",
                f"FileNotFoundError: File 'file_{i}.txt' not found",
                f"PermissionError: Access denied to resource_{i}",
                f"ConnectionError: Failed to connect to service_{i}"
            ]
            
            failures.append(TestFailureData(
                test_name=f"test_performance_{i}",
                test_file=f"tests/test_module_{i % 10}.py",  # Group into 10 files
                failure_type=failure_types[i % 3],
                error_message=error_messages[i % 5],
                stack_trace=f"Stack trace for test {i}\n" * (i % 5 + 1),  # Varying stack trace sizes
                test_function=f"test_performance_{i}",
                test_class=f"TestClass{i % 20}" if i % 3 == 0 else None,  # Some with classes
                failure_timestamp=base_time - timedelta(minutes=i),
                test_context={
                    "test_type": "performance",
                    "batch": i // 10,
                    "complexity": i % 5
                },
                pytest_node_id=f"tests/test_module_{i % 10}.py::TestClass{i % 20}::test_performance_{i}"
            ))
            
        return failures
        
    def test_30_second_analysis_requirement_validation(self, performance_monitor, large_failure_dataset):
        """
        Validate that RCA analysis completes within 30 seconds for large datasets
        Requirements: 1.4 - 30-second timeout requirement
        """
        integrator = TestRCAIntegrationEngine()
        
        # Test with different dataset sizes
        dataset_sizes = [10, 25, 50, 100]
        
        for size in dataset_sizes:
            test_failures = large_failure_dataset[:size]
            
            performance_monitor.start_monitoring()
            
            # Perform RCA analysis
            report = integrator.analyze_test_failures(test_failures)
            
            metrics = performance_monitor.get_metrics()
            
            # Validate 30-second requirement
            assert metrics['elapsed_time'] < 30.0, (
                f"Analysis of {size} failures took {metrics['elapsed_time']:.2f}s, "
                f"should be under 30s"
            )
            
            # Verify meaningful results were produced
            assert report.total_failures == size
            assert isinstance(report.summary.confidence_score, float)
            
            print(f"Dataset size {size}: {metrics['elapsed_time']:.2f}s, "
                  f"Memory: {metrics['memory_delta']:.1f}MB")
                  
    def test_pattern_matching_sub_second_performance(self, performance_monitor):
        """
        Test that pattern matching achieves sub-second performance
        Requirements: 4.2 - Sub-second performance for existing patterns
        """
        integrator = TestRCAIntegrationEngine()
        
        # Create test failures that should match common patterns
        pattern_test_failures = [
            TestFailureData(
                test_name="test_import_error",
                test_file="tests/test_imports.py",
                failure_type="error",
                error_message="ImportError: No module named 'requests'",
                stack_trace="ImportError stack trace",
                test_function="test_import_error",
                test_class="TestImports",
                failure_timestamp=datetime.now(),
                test_context={"test_type": "unit"},
                pytest_node_id="tests/test_imports.py::TestImports::test_import_error"
            ),
            TestFailureData(
                test_name="test_file_not_found",
                test_file="tests/test_files.py",
                failure_type="error",
                error_message="FileNotFoundError: [Errno 2] No such file or directory: 'config.json'",
                stack_trace="FileNotFoundError stack trace",
                test_function="test_file_not_found",
                test_class="TestFiles",
                failure_timestamp=datetime.now(),
                test_context={"test_type": "integration"},
                pytest_node_id="tests/test_files.py::TestFiles::test_file_not_found"
            )
        ]
        
        # Test individual pattern matching performance
        for failure in pattern_test_failures:
            performance_monitor.start_monitoring()
            
            # Convert to RCA failure (includes pattern matching logic)
            rca_failure = integrator.convert_to_rca_failure(failure)
            
            metrics = performance_monitor.get_metrics()
            
            # Should complete in sub-second time
            assert metrics['elapsed_time'] < 1.0, (
                f"Pattern matching for {failure.test_name} took {metrics['elapsed_time']:.3f}s, "
                f"should be under 1s"
            )
            
            # Verify conversion was successful
            assert rca_failure.component == f"test:{failure.test_file}"
            
    @pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not available")
    def test_memory_usage_efficiency(self, performance_monitor, large_failure_dataset):
        """
        Test memory usage efficiency during RCA analysis
        Requirements: 1.4 - Resource usage limits
        """
        integrator = TestRCAIntegrationEngine()
        
        # Force garbage collection before test
        gc.collect()
        
        performance_monitor.start_monitoring()
        
        # Analyze large dataset
        report = integrator.analyze_test_failures(large_failure_dataset)
        
        metrics = performance_monitor.get_metrics()
        
        # Memory usage should be reasonable (less than 200MB increase)
        assert metrics['memory_delta'] < 200, (
            f"Memory usage increased by {metrics['memory_delta']:.1f}MB, "
            f"should be under 200MB"
        )
        
        # Peak memory should be reasonable
        assert metrics['peak_memory'] < 1000, (
            f"Peak memory usage was {metrics['peak_memory']:.1f}MB, "
            f"should be under 1000MB"
        )
        
        # Verify analysis completed successfully
        assert report.total_failures == len(large_failure_dataset)
        
    def test_concurrent_analysis_performance(self, large_failure_dataset):
        """
        Test performance with concurrent RCA analysis requests
        Requirements: 1.4 - Performance under load
        """
        integrator = TestRCAIntegrationEngine()
        
        # Split dataset into chunks for concurrent processing
        chunk_size = 20
        chunks = [
            large_failure_dataset[i:i + chunk_size]
            for i in range(0, len(large_failure_dataset), chunk_size)
        ]
        
        results = []
        threads = []
        start_time = time.time()
        
        def analyze_chunk(chunk, result_list):
            """Analyze a chunk of failures"""
            report = integrator.analyze_test_failures(chunk)
            result_list.append(report)
            
        # Start concurrent analysis threads
        for chunk in chunks[:3]:  # Test with 3 concurrent threads
            thread = threading.Thread(
                target=analyze_chunk,
                args=(chunk, results)
            )
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        total_time = time.time() - start_time
        
        # Should complete concurrent analysis efficiently
        assert total_time < 45.0, (
            f"Concurrent analysis took {total_time:.2f}s, "
            f"should be under 45s"
        )
        
        # Verify all chunks were processed
        assert len(results) == 3
        for report in results:
            assert report.total_failures == chunk_size
            
    def test_scalability_with_increasing_load(self, performance_monitor):
        """
        Test scalability with increasing failure counts
        Requirements: 1.4 - Scalability requirements
        """
        integrator = TestRCAIntegrationEngine()
        
        # Test with increasing dataset sizes
        sizes = [5, 10, 20, 40, 80]
        performance_data = []
        
        for size in sizes:
            # Create dataset of specified size
            failures = []
            for i in range(size):
                failures.append(TestFailureData(
                    test_name=f"test_scale_{i}",
                    test_file=f"tests/test_scale_{i % 5}.py",
                    failure_type="error",
                    error_message=f"Error message {i}",
                    stack_trace=f"Stack trace {i}",
                    test_function=f"test_scale_{i}",
                    test_class=None,
                    failure_timestamp=datetime.now(),
                    test_context={"test_type": "scale"},
                    pytest_node_id=f"tests/test_scale_{i % 5}.py::test_scale_{i}"
                ))
                
            performance_monitor.start_monitoring()
            
            # Analyze failures
            report = integrator.analyze_test_failures(failures)
            
            metrics = performance_monitor.get_metrics()
            performance_data.append({
                'size': size,
                'time': metrics['elapsed_time'],
                'memory': metrics['memory_delta']
            })
            
            # Verify analysis completed
            assert report.total_failures == size
            
        # Analyze scalability trends
        # Time should scale reasonably (not exponentially)
        for i in range(1, len(performance_data)):
            prev_data = performance_data[i-1]
            curr_data = performance_data[i]
            
            size_ratio = curr_data['size'] / prev_data['size']
            time_ratio = curr_data['time'] / max(prev_data['time'], 0.001)  # Avoid division by zero
            
            # Time should not scale worse than quadratically
            assert time_ratio < size_ratio ** 2, (
                f"Performance degradation too severe: "
                f"size ratio {size_ratio:.1f}, time ratio {time_ratio:.1f}"
            )
            
    def test_timeout_mechanism_effectiveness(self):
        """
        Test effectiveness of timeout mechanisms
        Requirements: 1.4 - Timeout handling
        """
        integrator = TestRCAIntegrationEngine()
        
        # Set short timeout for testing
        original_timeout = integrator.analysis_timeout_seconds
        integrator.analysis_timeout_seconds = 2.0  # 2 second timeout
        
        try:
            # Create failure that might cause slow analysis
            slow_failure = TestFailureData(
                test_name="test_timeout",
                test_file="tests/test_timeout.py",
                failure_type="error",
                error_message="Complex error" * 1000,  # Large error message
                stack_trace="Very long stack trace\n" * 1000,  # Large stack trace
                test_function="test_timeout",
                test_class="TestTimeout",
                failure_timestamp=datetime.now(),
                test_context={"test_type": "timeout"},
                pytest_node_id="tests/test_timeout.py::TestTimeout::test_timeout"
            )
            
            start_time = time.time()
            
            # Mock RCA engine to simulate slow operation
            with patch.object(integrator, 'rca_engine') as mock_engine:
                def slow_analysis(*args, **kwargs):
                    time.sleep(5)  # Simulate 5-second analysis (longer than timeout)
                    return Mock()
                    
                mock_engine.match_existing_patterns.return_value = []
                mock_engine.perform_systematic_rca.side_effect = slow_analysis
                mock_engine.is_healthy.return_value = True
                
                report = integrator.analyze_test_failures([slow_failure])
                
            analysis_time = time.time() - start_time
            
            # Should respect timeout (with some overhead)
            assert analysis_time < 5.0, (
                f"Analysis took {analysis_time:.2f}s, "
                f"should timeout around {integrator.analysis_timeout_seconds}s"
            )
            
            # Should still return a report
            assert report.total_failures == 1
            
        finally:
            # Restore original timeout
            integrator.analysis_timeout_seconds = original_timeout
            
    def test_report_generation_performance(self, performance_monitor, large_failure_dataset):
        """
        Test report generation performance with large datasets
        Requirements: 2.2, 2.3, 2.4 - Report generation performance
        """
        integrator = TestRCAIntegrationEngine()
        generator = RCAReportGenerator()
        
        # Generate RCA report
        report = integrator.analyze_test_failures(large_failure_dataset[:50])
        
        # Test console report generation performance
        performance_monitor.start_monitoring()
        console_report = generator.format_for_console(report, use_colors=False)
        console_metrics = performance_monitor.get_metrics()
        
        assert console_metrics['elapsed_time'] < 5.0, (
            f"Console report generation took {console_metrics['elapsed_time']:.2f}s, "
            f"should be under 5s"
        )
        assert len(console_report) > 0
        
        # Test JSON report generation performance
        performance_monitor.start_monitoring()
        json_report = generator.generate_json_report(report)
        json_metrics = performance_monitor.get_metrics()
        
        assert json_metrics['elapsed_time'] < 2.0, (
            f"JSON report generation took {json_metrics['elapsed_time']:.2f}s, "
            f"should be under 2s"
        )
        assert isinstance(json_report, dict)
        
        # Test markdown report generation performance
        performance_monitor.start_monitoring()
        markdown_report = generator.generate_markdown_report(report)
        markdown_metrics = performance_monitor.get_metrics()
        
        assert markdown_metrics['elapsed_time'] < 3.0, (
            f"Markdown report generation took {markdown_metrics['elapsed_time']:.2f}s, "
            f"should be under 3s"
        )
        assert len(markdown_report) > 0


class TestResourceManagement:
    """Test resource management and limits"""
    
    @pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not available")
    def test_cpu_usage_limits(self, large_failure_dataset):
        """
        Test CPU usage stays within reasonable limits
        Requirements: 1.4 - Resource usage limits
        """
        integrator = TestRCAIntegrationEngine()
        
        # Monitor CPU usage during analysis
        process = psutil.Process(os.getpid())
        cpu_samples = []
        
        def monitor_cpu():
            """Monitor CPU usage in background"""
            for _ in range(10):  # Sample for 10 seconds
                cpu_samples.append(process.cpu_percent(interval=1))
                
        # Start CPU monitoring in background
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        # Perform analysis
        report = integrator.analyze_test_failures(large_failure_dataset[:30])
        
        # Wait for monitoring to complete
        monitor_thread.join()
        
        # Verify analysis completed
        assert report.total_failures == 30
        
        # Check CPU usage was reasonable
        if cpu_samples:
            avg_cpu = sum(cpu_samples) / len(cpu_samples)
            max_cpu = max(cpu_samples)
            
            # CPU usage should be reasonable (not pegging the CPU)
            assert avg_cpu < 80.0, f"Average CPU usage was {avg_cpu:.1f}%, should be under 80%"
            assert max_cpu < 95.0, f"Peak CPU usage was {max_cpu:.1f}%, should be under 95%"
            
    @pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not available")
    def test_memory_leak_detection(self):
        """
        Test for memory leaks during repeated analysis
        Requirements: 1.4 - Resource management
        """
        integrator = TestRCAIntegrationEngine()
        process = psutil.Process(os.getpid())
        
        # Create small test failure for repeated analysis
        test_failure = TestFailureData(
            test_name="test_memory_leak",
            test_file="tests/test_memory.py",
            failure_type="error",
            error_message="Test error for memory leak detection",
            stack_trace="Stack trace",
            test_function="test_memory_leak",
            test_class=None,
            failure_timestamp=datetime.now(),
            test_context={"test_type": "memory"},
            pytest_node_id="tests/test_memory.py::test_memory_leak"
        )
        
        # Get initial memory usage
        gc.collect()  # Force garbage collection
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform repeated analysis
        for i in range(20):
            report = integrator.analyze_test_failures([test_failure])
            assert report.total_failures == 1
            
            # Periodic garbage collection
            if i % 5 == 0:
                gc.collect()
                
        # Get final memory usage
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 50MB)
        assert memory_increase < 50, (
            f"Memory increased by {memory_increase:.1f}MB after 20 iterations, "
            f"possible memory leak"
        )
        
    @pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not available")
    def test_file_handle_management(self, large_failure_dataset):
        """
        Test proper file handle management
        Requirements: 1.4 - Resource management
        """
        integrator = TestRCAIntegrationEngine()
        generator = RCAReportGenerator()
        
        # Get initial file descriptor count
        process = psutil.Process(os.getpid())
        initial_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
        
        # Perform analysis and report generation
        report = integrator.analyze_test_failures(large_failure_dataset[:20])
        
        # Generate reports (which might create temporary files)
        console_report = generator.format_for_console(report, use_colors=False)
        json_report = generator.generate_json_report(report)
        markdown_report = generator.generate_markdown_report(report)
        
        # Verify reports were generated
        assert len(console_report) > 0
        assert isinstance(json_report, dict)
        assert len(markdown_report) > 0
        
        # Check file descriptor count hasn't increased significantly
        final_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
        
        if initial_fds > 0 and final_fds > 0:
            fd_increase = final_fds - initial_fds
            assert fd_increase < 10, (
                f"File descriptor count increased by {fd_increase}, "
                f"possible file handle leak"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])  # -s to see print output