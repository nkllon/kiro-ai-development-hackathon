from src.beast_mode.observability.metrics import Metric, MetricType
"""
Performance test module for PerformanceMonitorCoreValidation.

Priority: CRITICAL
Module: beast_mode.testing.performance_monitor_core_validation
Phase 2: Performance Testing
"""

import pytest
import time
import psutil
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.beast_mode.testing.performance_monitor_core_validation import PerformanceMonitorCoreValidation


class TestPerformanceMonitorCoreValidationPerformance:
    """Performance tests for PerformanceMonitorCoreValidation."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        self.instance = PerformanceMonitorCoreValidation()
        self.performance_metrics = {}
    
    def test_response_time(self):
        """Test response time performance."""
        start_time = time.time()
        
        # Execute performance-critical operation
        result = self.instance.perform_operation()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Assert response time is within acceptable limits
        assert response_time < 1.0  # 1 second threshold
        self.performance_metrics['response_time'] = response_time
    
    def test_memory_usage(self):
        """Test memory usage performance."""
        initial_memory = psutil.Process().memory_info().rss
        
        # Execute memory-intensive operation
        result = self.instance.memory_intensive_operation()
        
        final_memory = psutil.Process().memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Assert memory usage is within acceptable limits
        assert memory_increase < 100 * 1024 * 1024  # 100MB threshold
        self.performance_metrics['memory_usage'] = memory_increase
    
    def test_concurrent_load(self):
        """Test performance under concurrent load."""
        def worker():
            return self.instance.handle_concurrent_request()
        
        # Create multiple threads
        threads = []
        results = []
        
        for _ in range(10):
            thread = threading.Thread(target=lambda: results.append(worker()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert all operations completed successfully
        assert len(results) == 10
        assert all(result is not None for result in results)
    
    def test_stress_performance(self):
        """Test performance under stress conditions."""
        stress_results = []
        
        for i in range(100):
            start_time = time.time()
            result = self.instance.stress_test_operation()
            end_time = time.time()
            
            stress_results.append({
                'iteration': i,
                'result': result,
                'duration': end_time - start_time
            })
        
        # Assert consistent performance under stress
        avg_duration = sum(r['duration'] for r in stress_results) / len(stress_results)
        assert avg_duration < 0.1  # 100ms average threshold
        
        # Assert no failures under stress
        assert all(r['result'] is not None for r in stress_results)
    
    def test_scalability(self):
        """Test scalability performance."""
        scalability_results = []
        
        for scale in [1, 10, 100, 1000]:
            start_time = time.time()
            result = self.instance.scale_operation(scale)
            end_time = time.time()
            
            scalability_results.append({
                'scale': scale,
                'result': result,
                'duration': end_time - start_time
            })
        
        # Assert scalability characteristics
        assert len(scalability_results) == 4
        assert all(r['result'] is not None for r in scalability_results)
    
    def teardown_method(self):
        """Clean up performance test resources."""
        # Log performance metrics
        print(f"Performance Metrics: {self.performance_metrics}")
