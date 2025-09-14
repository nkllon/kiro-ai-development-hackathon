"""
Comprehensive Performance Tests

This module provides comprehensive performance tests for the Beast Mode framework,
including load testing, stress testing, and performance benchmarking.
"""

import pytest
import asyncio
import time
import psutil
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import gc
import tracemalloc

from tests.test_utilities import (
    TestConfig, TestEnvironment, TestDataFactory, PerformanceMonitor,
    TestAssertions, performance_test, slow_test, requires_dependency
)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import core modules
try:
    from beast_mode.core.reflective_module import ReflectiveModule, HealthStatus
    from beast_mode.core.model_registry import ModelRegistry
    from beast_mode.core.pdca_models import PDCACycle, PDCAPhase
except ImportError as e:
    pytest.skip(f"Core modules not available: {e}", allow_module_level=True)


class PerformanceMetrics:
    """Collect and analyze performance metrics."""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        self.memory_snapshots = []
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        if operation not in self.start_times:
            return 0.0
        
        duration = time.time() - self.start_times[operation]
        self.metrics[operation] = duration
        return duration
    
    def record_memory_snapshot(self, label: str):
        """Record a memory snapshot."""
        process = psutil.Process(os.getpid())
        memory_info = {
            "label": label,
            "timestamp": time.time(),
            "rss_mb": process.memory_info().rss / 1024 / 1024,
            "vms_mb": process.memory_info().vms / 1024 / 1024,
            "percent": process.memory_percent()
        }
        self.memory_snapshots.append(memory_info)
        return memory_info
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {"error": "No metrics recorded"}
        
        durations = list(self.metrics.values())
        return {
            "total_operations": len(self.metrics),
            "total_time": sum(durations),
            "average_time": statistics.mean(durations),
            "median_time": statistics.median(durations),
            "min_time": min(durations),
            "max_time": max(durations),
            "std_deviation": statistics.stdev(durations) if len(durations) > 1 else 0,
            "operations_per_second": len(durations) / sum(durations) if sum(durations) > 0 else 0
        }


class TestModelRegistryPerformance:
    """Test Model Registry performance."""
    
    @performance_test
    def test_large_scale_model_registration(self):
        """Test performance with large-scale model registration."""
        registry = ModelRegistry()
        metrics = PerformanceMetrics()
        
        # Test with different scales
        scales = [100, 500, 1000, 2000]
        
        for scale in scales:
            metrics.start_timer(f"register_{scale}_models")
            
            for i in range(scale):
                registry.register_model(
                    f"model_{i}",
                    "classification",
                    "1.0.0",
                    {
                        "index": i,
                        "data": "x" * 100,  # 100 bytes per model
                        "features": [f"feature_{j}" for j in range(10)]
                    }
                )
            
            duration = metrics.end_timer(f"register_{scale}_models")
            
            # Performance assertions
            models_per_second = scale / duration
            assert models_per_second > 100, f"Registration too slow: {models_per_second:.2f} models/sec"
            
            # Memory usage check
            memory_snapshot = metrics.record_memory_snapshot(f"after_{scale}_models")
            assert memory_snapshot["rss_mb"] < 500, f"Memory usage too high: {memory_snapshot['rss_mb']:.2f} MB"
    
    @performance_test
    def test_model_retrieval_performance(self):
        """Test model retrieval performance."""
        registry = ModelRegistry()
        
        # Register test models
        for i in range(1000):
            registry.register_model(
                f"model_{i}",
                "classification",
                "1.0.0",
                {"index": i}
            )
        
        metrics = PerformanceMetrics()
        
        # Test retrieval performance
        metrics.start_timer("retrieve_100_models")
        for i in range(100):
            registry.get_model(f"model_{i}")
        duration = metrics.end_timer("retrieve_100_models")
        
        # Performance assertions
        retrievals_per_second = 100 / duration
        assert retrievals_per_second > 1000, f"Retrieval too slow: {retrievals_per_second:.2f} retrievals/sec"
    
    @performance_test
    def test_concurrent_model_operations(self):
        """Test concurrent model operations."""
        registry = ModelRegistry()
        
        async def register_models(start_idx, count):
            """Register models concurrently."""
            for i in range(start_idx, start_idx + count):
                registry.register_model(
                    f"concurrent_model_{i}",
                    "classification",
                    "1.0.0",
                    {"index": i}
                )
        
        async def retrieve_models(start_idx, count):
            """Retrieve models concurrently."""
            for i in range(start_idx, start_idx + count):
                registry.get_model(f"concurrent_model_{i}")
        
        async def test_concurrent_operations():
            """Test concurrent operations."""
            # Register models concurrently
            register_tasks = [
                register_models(i * 100, 100) for i in range(10)
            ]
            await asyncio.gather(*register_tasks)
            
            # Retrieve models concurrently
            retrieve_tasks = [
                retrieve_models(i * 100, 100) for i in range(10)
            ]
            await asyncio.gather(*retrieve_tasks)
        
        # Run concurrent test
        start_time = time.time()
        asyncio.run(test_concurrent_operations())
        total_time = time.time() - start_time
        
        # Performance assertions
        assert total_time < 5.0, f"Concurrent operations too slow: {total_time:.2f}s"
        assert len(registry.models) == 1000, "Not all models registered"


class TestReflectiveModulePerformance:
    """Test ReflectiveModule performance."""
    
    @performance_test
    def test_module_creation_performance(self):
        """Test module creation performance."""
        metrics = PerformanceMetrics()
        
        # Test module creation at different scales
        scales = [100, 500, 1000]
        
        for scale in scales:
            modules = []
            metrics.start_timer(f"create_{scale}_modules")
            
            for i in range(scale):
                module = ReflectiveModule(
                    f"module_{i}",
                    "1.0.0",
                    f"Test module {i}"
                )
                modules.append(module)
            
            duration = metrics.end_timer(f"create_{scale}_modules")
            
            # Performance assertions
            modules_per_second = scale / duration
            assert modules_per_second > 1000, f"Module creation too slow: {modules_per_second:.2f} modules/sec"
            
            # Memory usage check
            memory_snapshot = metrics.record_memory_snapshot(f"after_{scale}_modules")
            assert memory_snapshot["rss_mb"] < 200, f"Memory usage too high: {memory_snapshot['rss_mb']:.2f} MB"
    
    @performance_test
    def test_capability_management_performance(self):
        """Test capability management performance."""
        module = ReflectiveModule("test_module", "1.0.0")
        metrics = PerformanceMetrics()
        
        # Test capability registration
        metrics.start_timer("register_1000_capabilities")
        for i in range(1000):
            module.register_capability(
                f"capability_{i}",
                {
                    "description": f"Test capability {i}",
                    "data": "x" * 100
                }
            )
        duration = metrics.end_timer("register_1000_capabilities")
        
        # Performance assertions
        capabilities_per_second = 1000 / duration
        assert capabilities_per_second > 500, f"Capability registration too slow: {capabilities_per_second:.2f} capabilities/sec"
        
        # Test capability retrieval
        metrics.start_timer("retrieve_100_capabilities")
        for i in range(100):
            module.get_capability(f"capability_{i}")
        duration = metrics.end_timer("retrieve_100_capabilities")
        
        # Performance assertions
        retrievals_per_second = 100 / duration
        assert retrievals_per_second > 1000, f"Capability retrieval too slow: {retrievals_per_second:.2f} retrievals/sec"
    
    @performance_test
    def test_health_status_updates_performance(self):
        """Test health status updates performance."""
        module = ReflectiveModule("test_module", "1.0.0")
        metrics = PerformanceMetrics()
        
        # Test health status updates
        metrics.start_timer("1000_health_updates")
        for i in range(1000):
            status = HealthStatus.HEALTHY if i % 2 == 0 else HealthStatus.DEGRADED
            module.update_health_status(status)
        duration = metrics.end_timer("1000_health_updates")
        
        # Performance assertions
        updates_per_second = 1000 / duration
        assert updates_per_second > 2000, f"Health updates too slow: {updates_per_second:.2f} updates/sec"


class TestPDCAPerformance:
    """Test PDCA performance."""
    
    @performance_test
    def test_pdca_cycle_creation_performance(self):
        """Test PDCA cycle creation performance."""
        metrics = PerformanceMetrics()
        
        # Test cycle creation at different scales
        scales = [100, 500, 1000]
        
        for scale in scales:
            cycles = []
            metrics.start_timer(f"create_{scale}_cycles")
            
            for i in range(scale):
                cycle = PDCACycle(
                    f"cycle_{i}",
                    f"Test objective {i}",
                    created_at=datetime.now()
                )
                cycles.append(cycle)
            
            duration = metrics.end_timer(f"create_{scale}_cycles")
            
            # Performance assertions
            cycles_per_second = scale / duration
            assert cycles_per_second > 1000, f"Cycle creation too slow: {cycles_per_second:.2f} cycles/sec"
    
    @performance_test
    def test_pdca_phase_transitions_performance(self):
        """Test PDCA phase transitions performance."""
        cycle = PDCACycle("test_cycle", "test_objective")
        metrics = PerformanceMetrics()
        
        # Test phase transitions
        metrics.start_timer("1000_phase_transitions")
        for i in range(1000):
            phase = PDCAPhase.PLAN if i % 4 == 0 else \
                   PDCAPhase.DO if i % 4 == 1 else \
                   PDCAPhase.CHECK if i % 4 == 2 else \
                   PDCAPhase.ACT
            cycle.transition_to_phase(phase)
        duration = metrics.end_timer("1000_phase_transitions")
        
        # Performance assertions
        transitions_per_second = 1000 / duration
        assert transitions_per_second > 2000, f"Phase transitions too slow: {transitions_per_second:.2f} transitions/sec"
    
    @performance_test
    def test_pdca_validation_performance(self):
        """Test PDCA validation performance."""
        cycle = PDCACycle("test_cycle", "test_objective")
        metrics = PerformanceMetrics()
        
        # Add validation criteria
        criteria = [f"criterion_{i}" for i in range(100)]
        cycle.add_validation_criteria(criteria)
        
        # Test validation performance
        metrics.start_timer("1000_validations")
        for i in range(1000):
            validation_results = {
                criterion: i % 2 == 0 for criterion in criteria
            }
            cycle.validate_criteria(validation_results)
        duration = metrics.end_timer("1000_validations")
        
        # Performance assertions
        validations_per_second = 1000 / duration
        assert validations_per_second > 500, f"Validations too slow: {validations_per_second:.2f} validations/sec"


class TestMemoryPerformance:
    """Test memory performance and usage."""
    
    @slow_test
    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        metrics = PerformanceMetrics()
        
        # Record initial memory
        initial_memory = metrics.record_memory_snapshot("initial")
        
        # Create large number of objects
        modules = []
        registry = ModelRegistry()
        cycles = []
        
        for i in range(10000):
            # Create module
            module = ReflectiveModule(f"load_module_{i}", "1.0.0")
            module.register_capability("load_capability", {"data": "x" * 1000})
            modules.append(module)
            
            # Register model
            registry.register_model(
                f"load_model_{i}",
                "classification",
                "1.0.0",
                {"data": "x" * 2000}
            )
            
            # Create cycle
            cycle = PDCACycle(f"load_cycle_{i}", f"Load objective {i}")
            cycle.add_validation_criteria([f"criterion_{j}" for j in range(10)])
            cycles.append(cycle)
        
        # Record peak memory
        peak_memory = metrics.record_memory_snapshot("peak")
        
        # Calculate memory increase
        memory_increase = peak_memory["rss_mb"] - initial_memory["rss_mb"]
        
        # Memory usage should be reasonable
        assert memory_increase < 1000, f"Memory usage too high: {memory_increase:.2f} MB increase"
        
        # Test memory cleanup
        del modules
        del registry
        del cycles
        gc.collect()
        
        # Record memory after cleanup
        cleanup_memory = metrics.record_memory_snapshot("cleanup")
        memory_after_cleanup = cleanup_memory["rss_mb"] - initial_memory["rss_mb"]
        
        # Memory should be mostly cleaned up
        assert memory_after_cleanup < 200, f"Memory not properly cleaned up: {memory_after_cleanup:.2f} MB remaining"
    
    @slow_test
    def test_memory_leak_detection(self):
        """Test for memory leaks."""
        tracemalloc.start()
        
        # Record initial memory
        initial_snapshot = tracemalloc.take_snapshot()
        
        # Perform operations that might cause leaks
        for iteration in range(100):
            modules = []
            registry = ModelRegistry()
            
            # Create and destroy objects
            for i in range(1000):
                module = ReflectiveModule(f"leak_test_{iteration}_{i}", "1.0.0")
                module.register_capability("test_capability", {"data": "x" * 100})
                modules.append(module)
                
                registry.register_model(
                    f"leak_model_{iteration}_{i}",
                    "classification",
                    "1.0.0",
                    {"data": "x" * 100}
                )
            
            # Clean up
            del modules
            del registry
            gc.collect()
        
        # Record final memory
        final_snapshot = tracemalloc.take_snapshot()
        
        # Calculate memory difference
        top_stats = final_snapshot.compare_to(initial_snapshot, 'lineno')
        
        # Check for significant memory leaks
        total_memory_diff = sum(stat.size_diff for stat in top_stats)
        memory_diff_mb = total_memory_diff / 1024 / 1024
        
        # Memory difference should be small
        assert memory_diff_mb < 50, f"Potential memory leak detected: {memory_diff_mb:.2f} MB difference"
        
        tracemalloc.stop()


class TestConcurrencyPerformance:
    """Test concurrency and threading performance."""
    
    @performance_test
    def test_threading_performance(self):
        """Test threading performance."""
        registry = ModelRegistry()
        metrics = PerformanceMetrics()
        
        def register_models(start_idx, count):
            """Register models in thread."""
            for i in range(start_idx, start_idx + count):
                registry.register_model(
                    f"thread_model_{i}",
                    "classification",
                    "1.0.0",
                    {"index": i}
                )
        
        def retrieve_models(start_idx, count):
            """Retrieve models in thread."""
            for i in range(start_idx, start_idx + count):
                registry.get_model(f"thread_model_{i}")
        
        # Test threading performance
        metrics.start_timer("threading_test")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit registration tasks
            registration_futures = [
                executor.submit(register_models, i * 100, 100)
                for i in range(10)
            ]
            
            # Wait for completion
            for future in registration_futures:
                future.result()
            
            # Submit retrieval tasks
            retrieval_futures = [
                executor.submit(retrieve_models, i * 100, 100)
                for i in range(10)
            ]
            
            # Wait for completion
            for future in retrieval_futures:
                future.result()
        
        duration = metrics.end_timer("threading_test")
        
        # Performance assertions
        operations_per_second = 2000 / duration  # 1000 registrations + 1000 retrievals
        assert operations_per_second > 500, f"Threading performance too slow: {operations_per_second:.2f} ops/sec"
    
    @performance_test
    def test_asyncio_performance(self):
        """Test asyncio performance."""
        registry = ModelRegistry()
        metrics = PerformanceMetrics()
        
        async def register_models_async(start_idx, count):
            """Register models asynchronously."""
            for i in range(start_idx, start_idx + count):
                registry.register_model(
                    f"async_model_{i}",
                    "classification",
                    "1.0.0",
                    {"index": i}
                )
                await asyncio.sleep(0)  # Yield control
        
        async def retrieve_models_async(start_idx, count):
            """Retrieve models asynchronously."""
            for i in range(start_idx, start_idx + count):
                registry.get_model(f"async_model_{i}")
                await asyncio.sleep(0)  # Yield control
        
        async def test_asyncio_performance():
            """Test asyncio performance."""
            # Register models concurrently
            registration_tasks = [
                register_models_async(i * 100, 100)
                for i in range(10)
            ]
            await asyncio.gather(*registration_tasks)
            
            # Retrieve models concurrently
            retrieval_tasks = [
                retrieve_models_async(i * 100, 100)
                for i in range(10)
            ]
            await asyncio.gather(*retrieval_tasks)
        
        # Run asyncio test
        metrics.start_timer("asyncio_test")
        asyncio.run(test_asyncio_performance())
        duration = metrics.end_timer("asyncio_test")
        
        # Performance assertions
        operations_per_second = 2000 / duration
        assert operations_per_second > 300, f"Asyncio performance too slow: {operations_per_second:.2f} ops/sec"


class TestScalabilityLimits:
    """Test scalability limits and boundaries."""
    
    @slow_test
    def test_maximum_module_capacity(self):
        """Test maximum module capacity."""
        modules = []
        metrics = PerformanceMetrics()
        
        try:
            # Try to create maximum number of modules
            for i in range(50000):  # 50K modules
                module = ReflectiveModule(f"max_module_{i}", "1.0.0")
                modules.append(module)
                
                if i % 10000 == 0:
                    memory_snapshot = metrics.record_memory_snapshot(f"at_{i}_modules")
                    if memory_snapshot["rss_mb"] > 2000:  # 2GB limit
                        break
            
            # Should be able to create at least 10K modules
            assert len(modules) >= 10000, f"Could only create {len(modules)} modules"
            
        except MemoryError:
            # Memory error is acceptable at high limits
            assert len(modules) >= 1000, f"Memory error too early: only {len(modules)} modules"
    
    @slow_test
    def test_maximum_model_capacity(self):
        """Test maximum model capacity."""
        registry = ModelRegistry()
        metrics = PerformanceMetrics()
        
        try:
            # Try to register maximum number of models
            for i in range(100000):  # 100K models
                registry.register_model(
                    f"max_model_{i}",
                    "classification",
                    "1.0.0",
                    {"index": i, "data": "x" * 100}
                )
                
                if i % 20000 == 0:
                    memory_snapshot = metrics.record_memory_snapshot(f"at_{i}_models")
                    if memory_snapshot["rss_mb"] > 2000:  # 2GB limit
                        break
            
            # Should be able to register at least 20K models
            assert len(registry.models) >= 20000, f"Could only register {len(registry.models)} models"
            
        except MemoryError:
            # Memory error is acceptable at high limits
            assert len(registry.models) >= 5000, f"Memory error too early: only {len(registry.models)} models"


class TestPerformanceRegression:
    """Test for performance regressions."""
    
    @performance_test
    def test_benchmark_regression(self):
        """Test for performance regressions against benchmarks."""
        # Define performance benchmarks
        benchmarks = {
            "model_registration": 1000,  # models per second
            "model_retrieval": 5000,    # retrievals per second
            "module_creation": 2000,    # modules per second
            "capability_registration": 1000,  # capabilities per second
            "health_updates": 5000,     # updates per second
        }
        
        metrics = PerformanceMetrics()
        results = {}
        
        # Test model registration
        registry = ModelRegistry()
        metrics.start_timer("benchmark_model_registration")
        for i in range(1000):
            registry.register_model(f"benchmark_model_{i}", "classification", "1.0.0")
        duration = metrics.end_timer("benchmark_model_registration")
        results["model_registration"] = 1000 / duration
        
        # Test model retrieval
        metrics.start_timer("benchmark_model_retrieval")
        for i in range(1000):
            registry.get_model(f"benchmark_model_{i}")
        duration = metrics.end_timer("benchmark_model_retrieval")
        results["model_retrieval"] = 1000 / duration
        
        # Test module creation
        modules = []
        metrics.start_timer("benchmark_module_creation")
        for i in range(1000):
            module = ReflectiveModule(f"benchmark_module_{i}", "1.0.0")
            modules.append(module)
        duration = metrics.end_timer("benchmark_module_creation")
        results["module_creation"] = 1000 / duration
        
        # Test capability registration
        module = ReflectiveModule("benchmark_module", "1.0.0")
        metrics.start_timer("benchmark_capability_registration")
        for i in range(1000):
            module.register_capability(f"benchmark_capability_{i}", {"data": "test"})
        duration = metrics.end_timer("benchmark_capability_registration")
        results["capability_registration"] = 1000 / duration
        
        # Test health updates
        metrics.start_timer("benchmark_health_updates")
        for i in range(1000):
            module.update_health_status(HealthStatus.HEALTHY)
        duration = metrics.end_timer("benchmark_health_updates")
        results["health_updates"] = 1000 / duration
        
        # Check against benchmarks
        for operation, benchmark in benchmarks.items():
            actual = results[operation]
            assert actual >= benchmark * 0.8, f"{operation} performance regression: {actual:.2f} < {benchmark * 0.8:.2f}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
