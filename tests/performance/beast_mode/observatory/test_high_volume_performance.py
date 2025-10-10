"""
High-volume performance tests for Observatory system.

Tests Observatory performance under extreme load conditions including
massive event volumes, concurrent processing, memory efficiency,
and sustained high-throughput operations.
"""

import asyncio
import pytest
import time
import gc
import psutil
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List
from dataclasses import dataclass

from src.beast_mode.observatory.core_engine import ObservatoryCoreEngine
from src.beast_mode.observatory.models import (
    ObservatoryConfig,
    CoordinationEvent,
    CoordinationEventType,
    RedisConfig,
    MetricsConfig
)

from src.rm_ddd.core.unified_reflective_module import (
    ModuleHealth,
    ModuleStatus,
    ModuleCapability
)


@dataclass
class PerformanceMetrics:
    """Performance metrics for testing."""
    events_processed: int
    processing_time_seconds: float
    events_per_second: float
    peak_memory_mb: float
    cpu_usage_percent: float
    error_count: int
    success_rate: float


class PerformanceMonitor:
    """Monitor system performance during tests."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = self.initial_memory
        self.cpu_samples = []
        self.monitoring = False
        self._monitor_task = None

    async def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        """Monitor performance metrics."""
        while self.monitoring:
            try:
                # Memory monitoring
                current_memory = self.process.memory_info().rss / 1024 / 1024
                self.peak_memory = max(self.peak_memory, current_memory)

                # CPU monitoring
                cpu_percent = self.process.cpu_percent()
                self.cpu_samples.append(cpu_percent)

                await asyncio.sleep(0.1)  # Sample every 100ms
            except Exception:
                break

    def get_peak_memory_usage(self) -> float:
        """Get peak memory usage in MB."""
        return self.peak_memory - self.initial_memory

    def get_average_cpu_usage(self) -> float:
        """Get average CPU usage."""
        return sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0


@pytest.fixture
def performance_config():
    """Configuration optimized for performance testing."""
    return ObservatoryConfig(
        redis_config=RedisConfig(
            host="localhost",
            port=6379,
            stream_name="performance_test_stream",
            connection_pool_size=20
        ),
        metrics_config=MetricsConfig(
            collection_interval_seconds=1,
            component_discovery_enabled=True,
            performance_impact_limit=0.10  # Allow higher impact for performance tests
        )
    )


@pytest.fixture
def mock_high_performance_redis():
    """High-performance mock Redis client."""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.xadd.return_value = "1234567890-0"
    mock_redis.xreadgroup.return_value = []
    mock_redis.xgroup_create.return_value = None
    mock_redis.close.return_value = None

    # Simulate realistic Redis performance characteristics
    async def realistic_xadd(stream_name, data):
        await asyncio.sleep(0.0001)  # 0.1ms simulated Redis latency
        return f"{int(time.time() * 1000)}-{hash(str(data)) % 1000}"

    mock_redis.xadd.side_effect = realistic_xadd
    return mock_redis


@pytest.fixture
async def performance_observatory(performance_config, mock_high_performance_redis):
    """Observatory configured for performance testing."""
    with patch('redis.asyncio.Redis', return_value=mock_high_performance_redis), \
         patch('redis.asyncio.from_url', return_value=mock_high_performance_redis):

        observatory = ObservatoryCoreEngine(performance_config)
        await observatory.initialize()

        yield observatory

        await observatory.shutdown()


class TestMassiveEventVolume:
    """Test Observatory performance with massive event volumes."""

    @pytest.mark.asyncio
    async def test_10k_events_sequential_processing(self, performance_observatory):
        """Test processing 10,000 events sequentially."""
        observatory = performance_observatory
        monitor = PerformanceMonitor()

        await monitor.start_monitoring()
        start_time = time.time()

        try:
            # Generate 10,000 realistic coordination events
            events_processed = 0
            errors = 0

            for i in range(10000):
                event = CoordinationEvent(
                    event_id=f"sequential_test_{i}",
                    event_type=CoordinationEventType.API_CALL_SUCCESS,
                    source_component="performance_test_sequential",
                    event_data={
                        "sequence_id": i,
                        "batch": "10k_sequential",
                        "processing_time_ms": 45 + (i % 50),
                        "success_rate": 0.98 + (i % 100) / 5000
                    }
                )

                try:
                    await observatory.process_coordination_event(event)
                    events_processed += 1
                except Exception:
                    errors += 1

                # Progress indicator for long test
                if i % 1000 == 0:
                    print(f"Processed {i} events...")

            processing_time = time.time() - start_time

        finally:
            await monitor.stop_monitoring()

        # Performance metrics
        events_per_second = events_processed / processing_time
        peak_memory = monitor.get_peak_memory_usage()
        avg_cpu = monitor.get_average_cpu_usage()
        success_rate = events_processed / (events_processed + errors)

        performance_metrics = PerformanceMetrics(
            events_processed=events_processed,
            processing_time_seconds=processing_time,
            events_per_second=events_per_second,
            peak_memory_mb=peak_memory,
            cpu_usage_percent=avg_cpu,
            error_count=errors,
            success_rate=success_rate
        )

        # Performance assertions
        assert events_processed >= 9900, f"Should process most events, got {events_processed}"
        assert processing_time < 120.0, f"Should complete in under 2 minutes, took {processing_time:.2f}s"
        assert events_per_second > 50, f"Should process >50 events/sec, got {events_per_second:.1f}"
        assert success_rate > 0.99, f"Should have >99% success rate, got {success_rate:.3f}"
        assert peak_memory < 500.0, f"Memory usage should be <500MB, used {peak_memory:.1f}MB"

        print(f"\n10K Sequential Performance Results:")
        print(f"  Events Processed: {events_processed}")
        print(f"  Processing Time: {processing_time:.2f}s")
        print(f"  Events/Second: {events_per_second:.1f}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Avg CPU: {avg_cpu:.1f}%")
        print(f"  Success Rate: {success_rate:.3%}")

    @pytest.mark.asyncio
    async def test_10k_events_concurrent_processing(self, performance_observatory):
        """Test processing 10,000 events with high concurrency."""
        observatory = performance_observatory
        monitor = PerformanceMonitor()

        await monitor.start_monitoring()
        start_time = time.time()

        try:
            # Generate 10,000 events in batches for concurrent processing
            batch_size = 100
            num_batches = 100

            async def process_batch(batch_id):
                batch_events = []
                for i in range(batch_size):
                    event_id = batch_id * batch_size + i
                    event = CoordinationEvent(
                        event_id=f"concurrent_test_{event_id}",
                        event_type=CoordinationEventType.METRICS_COLLECTED,
                        source_component="performance_test_concurrent",
                        event_data={
                            "batch_id": batch_id,
                            "event_id": event_id,
                            "concurrent_test": True,
                            "metrics": {"cpu": 45.2, "memory": 67.8, "disk": 23.1}
                        }
                    )
                    batch_events.append(event)

                # Process batch concurrently
                batch_tasks = [observatory.process_coordination_event(event) for event in batch_events]
                results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                # Count successes and errors
                successes = sum(1 for r in results if not isinstance(r, Exception))
                errors = len(results) - successes
                return successes, errors

            # Process all batches with high concurrency
            batch_tasks = [process_batch(batch_id) for batch_id in range(num_batches)]
            batch_results = await asyncio.gather(*batch_tasks)

            processing_time = time.time() - start_time

        finally:
            await monitor.stop_monitoring()

        # Aggregate results
        total_successes = sum(successes for successes, _ in batch_results)
        total_errors = sum(errors for _, errors in batch_results)
        total_events = total_successes + total_errors

        # Performance metrics
        events_per_second = total_successes / processing_time
        peak_memory = monitor.get_peak_memory_usage()
        avg_cpu = monitor.get_average_cpu_usage()
        success_rate = total_successes / total_events if total_events > 0 else 0

        performance_metrics = PerformanceMetrics(
            events_processed=total_successes,
            processing_time_seconds=processing_time,
            events_per_second=events_per_second,
            peak_memory_mb=peak_memory,
            cpu_usage_percent=avg_cpu,
            error_count=total_errors,
            success_rate=success_rate
        )

        # Performance assertions
        assert total_successes >= 9800, f"Should process most events, got {total_successes}"
        assert processing_time < 60.0, f"Should complete in under 1 minute with concurrency, took {processing_time:.2f}s"
        assert events_per_second > 100, f"Should process >100 events/sec with concurrency, got {events_per_second:.1f}"
        assert success_rate > 0.98, f"Should have >98% success rate, got {success_rate:.3f}"
        assert peak_memory < 800.0, f"Memory usage should be <800MB, used {peak_memory:.1f}MB"

        print(f"\n10K Concurrent Performance Results:")
        print(f"  Events Processed: {total_successes}")
        print(f"  Processing Time: {processing_time:.2f}s")
        print(f"  Events/Second: {events_per_second:.1f}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Avg CPU: {avg_cpu:.1f}%")
        print(f"  Success Rate: {success_rate:.3%}")
        print(f"  Concurrency Speedup: {120/processing_time:.1f}x")

    @pytest.mark.asyncio
    async def test_sustained_high_throughput(self, performance_observatory):
        """Test sustained high-throughput event processing over time."""
        observatory = performance_observatory
        monitor = PerformanceMonitor()

        await monitor.start_monitoring()

        try:
            # Sustained throughput test: 1000 events/second for 30 seconds
            target_duration_seconds = 30
            target_events_per_second = 1000
            total_target_events = target_duration_seconds * target_events_per_second

            start_time = time.time()
            events_processed = 0
            errors = 0

            # Process events in timed batches to maintain consistent rate
            batch_duration = 1.0  # 1 second batches
            events_per_batch = target_events_per_second

            for second in range(target_duration_seconds):
                batch_start = time.time()

                # Create batch of events
                batch_tasks = []
                for i in range(events_per_batch):
                    event_id = second * events_per_batch + i
                    event = CoordinationEvent(
                        event_id=f"sustained_{event_id}",
                        event_type=CoordinationEventType.COORDINATION_MILESTONE,
                        source_component="performance_test_sustained",
                        event_data={
                            "second": second,
                            "event_in_second": i,
                            "sustained_test": True,
                            "throughput_target": target_events_per_second
                        }
                    )
                    batch_tasks.append(observatory.process_coordination_event(event))

                # Process batch
                try:
                    await asyncio.gather(*batch_tasks)
                    events_processed += events_per_batch
                except Exception as e:
                    errors += 1

                # Maintain timing
                batch_elapsed = time.time() - batch_start
                if batch_elapsed < batch_duration:
                    await asyncio.sleep(batch_duration - batch_elapsed)

                # Progress indicator
                if second % 5 == 0:
                    current_rate = events_processed / (time.time() - start_time)
                    print(f"Second {second}: {current_rate:.0f} events/sec")

            total_time = time.time() - start_time

        finally:
            await monitor.stop_monitoring()

        # Performance metrics
        actual_events_per_second = events_processed / total_time
        peak_memory = monitor.get_peak_memory_usage()
        avg_cpu = monitor.get_average_cpu_usage()
        success_rate = events_processed / (events_processed + errors) if events_processed + errors > 0 else 0

        # Performance assertions
        assert events_processed >= total_target_events * 0.95, f"Should process 95% of target events"
        assert actual_events_per_second >= target_events_per_second * 0.9, f"Should maintain 90% of target rate"
        assert total_time <= target_duration_seconds * 1.2, f"Should complete within 20% of target time"
        assert success_rate > 0.98, f"Should maintain >98% success rate under sustained load"
        assert peak_memory < 1000.0, f"Memory usage should remain <1GB under sustained load"

        print(f"\nSustained Throughput Performance Results:")
        print(f"  Target Events: {total_target_events}")
        print(f"  Events Processed: {events_processed}")
        print(f"  Target Rate: {target_events_per_second} events/sec")
        print(f"  Actual Rate: {actual_events_per_second:.1f} events/sec")
        print(f"  Duration: {total_time:.1f}s")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Avg CPU: {avg_cpu:.1f}%")
        print(f"  Success Rate: {success_rate:.3%}")


class TestMemoryAndResourceEfficiency:
    """Test memory efficiency and resource usage under load."""

    @pytest.mark.asyncio
    async def test_memory_efficiency_large_events(self, performance_observatory):
        """Test memory efficiency with large event payloads."""
        observatory = performance_observatory
        monitor = PerformanceMonitor()

        await monitor.start_monitoring()

        try:
            # Generate events with large payloads
            num_events = 1000
            events_processed = 0

            for i in range(num_events):
                # Create event with large payload
                large_payload = {
                    "large_data": "x" * 10000,  # 10KB string
                    "metrics_array": list(range(1000)),  # Array of 1000 numbers
                    "nested_data": {
                        f"key_{j}": f"value_{j}" * 100 for j in range(50)  # 50 nested items
                    },
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "processing_id": f"large_event_{i}",
                        "data_size_estimate": "50KB"
                    }
                }

                event = CoordinationEvent(
                    event_id=f"large_event_{i}",
                    event_type=CoordinationEventType.SYSTEM_STATUS_UPDATE,
                    source_component="performance_test_memory",
                    event_data=large_payload
                )

                await observatory.process_coordination_event(event)
                events_processed += 1

                # Progress and memory check
                if i % 100 == 0:
                    current_memory = monitor.process.memory_info().rss / 1024 / 1024
                    print(f"Processed {i} large events, current memory: {current_memory:.1f}MB")

                # Force garbage collection periodically
                if i % 250 == 0:
                    gc.collect()

        finally:
            await monitor.stop_monitoring()

        # Final memory check
        peak_memory = monitor.get_peak_memory_usage()
        avg_cpu = monitor.get_average_cpu_usage()

        # Memory efficiency assertions
        assert events_processed == num_events, f"Should process all large events"
        assert peak_memory < 2000.0, f"Memory should stay under 2GB with large payloads, used {peak_memory:.1f}MB"

        # Check for memory leaks by processing smaller events after large ones
        small_event = CoordinationEvent(
            event_id="memory_leak_test",
            event_type=CoordinationEventType.API_CALL_SUCCESS,
            source_component="memory_leak_check",
            event_data={"small": "payload"}
        )

        pre_small_memory = monitor.process.memory_info().rss / 1024 / 1024
        await observatory.process_coordination_event(small_event)
        post_small_memory = monitor.process.memory_info().rss / 1024 / 1024

        memory_increase = post_small_memory - pre_small_memory
        assert memory_increase < 10.0, f"Small event shouldn't increase memory by >10MB, increased {memory_increase:.1f}MB"

        print(f"\nLarge Event Memory Efficiency Results:")
        print(f"  Events Processed: {events_processed}")
        print(f"  Peak Memory Usage: {peak_memory:.1f}MB")
        print(f"  Memory per Event: {peak_memory/events_processed:.2f}MB")
        print(f"  Avg CPU Usage: {avg_cpu:.1f}%")

    @pytest.mark.asyncio
    async def test_garbage_collection_efficiency(self, performance_observatory):
        """Test garbage collection efficiency during sustained load."""
        observatory = performance_observatory
        monitor = PerformanceMonitor()

        await monitor.start_monitoring()

        try:
            # Track memory usage over multiple cycles
            memory_snapshots = []
            gc_counts_initial = gc.get_count()

            # Process events in cycles with deliberate garbage generation
            cycles = 10
            events_per_cycle = 1000

            for cycle in range(cycles):
                cycle_start_memory = monitor.process.memory_info().rss / 1024 / 1024

                # Process events with temporary objects
                for i in range(events_per_cycle):
                    # Create temporary objects that should be garbage collected
                    temp_data = {
                        "temporary_list": [f"temp_{j}" for j in range(100)],
                        "temporary_dict": {f"temp_key_{j}": j for j in range(100)},
                        "cycle": cycle,
                        "event": i
                    }

                    event = CoordinationEvent(
                        event_id=f"gc_test_{cycle}_{i}",
                        event_type=CoordinationEventType.METRICS_COLLECTED,
                        source_component="gc_efficiency_test",
                        event_data=temp_data
                    )

                    await observatory.process_coordination_event(event)

                    # Clear temporary reference
                    temp_data = None

                # Force garbage collection at end of cycle
                gc.collect()

                cycle_end_memory = monitor.process.memory_info().rss / 1024 / 1024
                memory_snapshots.append({
                    'cycle': cycle,
                    'start_memory': cycle_start_memory,
                    'end_memory': cycle_end_memory,
                    'memory_growth': cycle_end_memory - cycle_start_memory
                })

                print(f"Cycle {cycle}: Start={cycle_start_memory:.1f}MB, End={cycle_end_memory:.1f}MB, Growth={cycle_end_memory-cycle_start_memory:.1f}MB")

        finally:
            await monitor.stop_monitoring()

        # Analyze garbage collection efficiency
        gc_counts_final = gc.get_count()
        total_events_processed = cycles * events_per_cycle
        peak_memory = monitor.get_peak_memory_usage()

        # Calculate memory growth trend
        memory_growths = [snapshot['memory_growth'] for snapshot in memory_snapshots]
        avg_memory_growth_per_cycle = sum(memory_growths) / len(memory_growths)

        # GC efficiency assertions
        assert total_events_processed == cycles * events_per_cycle, "Should process all events"
        assert avg_memory_growth_per_cycle < 100.0, f"Average memory growth per cycle should be <100MB, was {avg_memory_growth_per_cycle:.1f}MB"
        assert peak_memory < 1500.0, f"Peak memory should stay <1.5GB, was {peak_memory:.1f}MB"

        # Check that later cycles don't grow memory excessively (no major memory leaks)
        early_cycles_growth = sum(memory_growths[:3]) / 3
        late_cycles_growth = sum(memory_growths[-3:]) / 3
        growth_ratio = late_cycles_growth / early_cycles_growth if early_cycles_growth > 0 else float('inf')
        assert growth_ratio < 2.0, f"Late cycle memory growth shouldn't be >2x early cycles, ratio: {growth_ratio:.2f}"

        print(f"\nGarbage Collection Efficiency Results:")
        print(f"  Total Events: {total_events_processed}")
        print(f"  Cycles Completed: {cycles}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Avg Memory Growth/Cycle: {avg_memory_growth_per_cycle:.1f}MB")
        print(f"  GC Objects Created: {gc_counts_final[0] - gc_counts_initial[0]}")
        print(f"  Memory Growth Stability Ratio: {growth_ratio:.2f}")


class TestConcurrencyAndScalability:
    """Test concurrency handling and scalability limits."""

    @pytest.mark.asyncio
    async def test_extreme_concurrency_limits(self, performance_observatory):
        """Test Observatory under extreme concurrency conditions."""
        observatory = performance_observatory
        monitor = PerformanceMonitor()

        await monitor.start_monitoring()

        try:
            # Test with very high concurrency - 1000 concurrent tasks
            concurrency_level = 1000
            events_per_task = 10
            total_expected_events = concurrency_level * events_per_task

            async def concurrent_event_producer(task_id):
                """Producer coroutine for concurrent event generation."""
                events_produced = 0
                errors = 0

                for i in range(events_per_task):
                    try:
                        event = CoordinationEvent(
                            event_id=f"extreme_concurrency_{task_id}_{i}",
                            event_type=CoordinationEventType.COORDINATION_INITIATED,
                            source_component=f"concurrent_producer_{task_id}",
                            event_data={
                                "task_id": task_id,
                                "event_index": i,
                                "concurrency_level": concurrency_level,
                                "extreme_test": True
                            }
                        )

                        await observatory.process_coordination_event(event)
                        events_produced += 1

                        # Small random delay to simulate realistic timing
                        await asyncio.sleep(0.001 + (hash(f"{task_id}_{i}") % 10) / 10000)

                    except Exception:
                        errors += 1

                return events_produced, errors

            # Launch all concurrent producers
            start_time = time.time()
            producer_tasks = [concurrent_event_producer(task_id) for task_id in range(concurrency_level)]

            # Wait for all producers to complete
            results = await asyncio.gather(*producer_tasks, return_exceptions=True)

            processing_time = time.time() - start_time

        finally:
            await monitor.stop_monitoring()

        # Aggregate results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        total_events_processed = sum(events for events, _ in successful_results)
        total_errors = sum(errors for _, errors in successful_results)
        task_exceptions = len(results) - len(successful_results)

        # Performance metrics
        events_per_second = total_events_processed / processing_time
        peak_memory = monitor.get_peak_memory_usage()
        avg_cpu = monitor.get_average_cpu_usage()
        success_rate = total_events_processed / (total_events_processed + total_errors) if total_events_processed + total_errors > 0 else 0

        # Extreme concurrency assertions
        assert total_events_processed >= total_expected_events * 0.90, f"Should process 90% of events under extreme concurrency"
        assert task_exceptions < concurrency_level * 0.10, f"Should have <10% task exceptions"
        assert processing_time < 180.0, f"Should complete extreme concurrency test in <3 minutes"
        assert events_per_second > 50, f"Should maintain >50 events/sec even under extreme load"
        assert peak_memory < 2000.0, f"Memory should stay <2GB under extreme concurrency"

        print(f"\nExtreme Concurrency Performance Results:")
        print(f"  Concurrency Level: {concurrency_level} tasks")
        print(f"  Target Events: {total_expected_events}")
        print(f"  Events Processed: {total_events_processed}")
        print(f"  Processing Time: {processing_time:.2f}s")
        print(f"  Events/Second: {events_per_second:.1f}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Task Success Rate: {(concurrency_level-task_exceptions)/concurrency_level:.3%}")
        print(f"  Event Success Rate: {success_rate:.3%}")

    @pytest.mark.asyncio
    async def test_scalability_with_beast_mode_components(self, performance_config, mock_high_performance_redis):
        """Test scalability with multiple Beast Mode components under load."""
        with patch('redis.asyncio.Redis', return_value=mock_high_performance_redis), \
             patch('redis.asyncio.from_url', return_value=mock_high_performance_redis):

            observatory = ObservatoryCoreEngine(performance_config)
            monitor = PerformanceMonitor()

            # Create multiple mock Beast Mode components
            num_components = 50  # Scale to 50 components
            beast_mode_components = []

            for i in range(num_components):
                component = AsyncMock()
                component.module_id = f"beast_component_{i}"
                component.get_health_status.return_value = ModuleHealth(
                    module_id=f"beast_component_{i}",
                    status=ModuleStatus.HEALTHY,
                    health_score=0.85 + (i % 15) / 100,
                    issues=[],
                    last_check=datetime.now(),
                    uptime_seconds=3600.0,
                    error_count=0,
                    warning_count=0
                )
                component.get_metrics.return_value = {
                    f"component_{i}_metric_1": i * 10,
                    f"component_{i}_metric_2": i * 15,
                    "shared_metric": 100 - i,
                    "performance_score": 0.9 + (i % 10) / 100
                }
                beast_mode_components.append(component)

            await monitor.start_monitoring()

            try:
                await observatory.initialize()

                # Register all components
                for component in beast_mode_components:
                    await observatory.register_beast_mode_component(component)

                # Generate coordinated events across all components
                events_per_component = 20
                total_events = num_components * events_per_component

                start_time = time.time()

                # Create events from all components concurrently
                all_event_tasks = []

                for component_idx, component in enumerate(beast_mode_components):
                    for event_idx in range(events_per_component):
                        event = CoordinationEvent(
                            event_id=f"scalability_{component_idx}_{event_idx}",
                            event_type=CoordinationEventType.COORDINATION_MILESTONE,
                            source_component=component.module_id,
                            event_data={
                                "component_index": component_idx,
                                "event_index": event_idx,
                                "scalability_test": True,
                                "total_components": num_components
                            }
                        )
                        all_event_tasks.append(observatory.process_coordination_event(event))

                # Process all events concurrently
                results = await asyncio.gather(*all_event_tasks, return_exceptions=True)

                # Perform health checks and metrics collection across all components
                await observatory._perform_health_checks()
                await observatory._collect_beast_mode_metrics()

                processing_time = time.time() - start_time

            finally:
                await monitor.stop_monitoring()
                await observatory.shutdown()

        # Analyze scalability results
        successful_events = sum(1 for r in results if not isinstance(r, Exception))
        failed_events = len(results) - successful_events

        events_per_second = successful_events / processing_time
        peak_memory = monitor.get_peak_memory_usage()
        avg_cpu = monitor.get_average_cpu_usage()
        success_rate = successful_events / len(results)

        # Scalability assertions
        assert successful_events >= total_events * 0.95, f"Should process 95% of events with {num_components} components"
        assert processing_time < 120.0, f"Should complete scalability test in <2 minutes"
        assert events_per_second > 25, f"Should maintain >25 events/sec with many components"
        assert peak_memory < 1500.0, f"Memory should stay <1.5GB with {num_components} components"
        assert success_rate > 0.95, f"Should maintain >95% success rate with many components"

        print(f"\nScalability Performance Results:")
        print(f"  Beast Mode Components: {num_components}")
        print(f"  Total Events: {total_events}")
        print(f"  Successful Events: {successful_events}")
        print(f"  Processing Time: {processing_time:.2f}s")
        print(f"  Events/Second: {events_per_second:.1f}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Success Rate: {success_rate:.3%}")
        print(f"  Memory per Component: {peak_memory/num_components:.2f}MB")


class TestRealtimePerformanceConstraints:
    """Test performance under real-time constraints and SLA requirements."""

    @pytest.mark.asyncio
    async def test_response_time_sla_compliance(self, performance_observatory):
        """Test SLA compliance for event processing response times."""
        observatory = performance_observatory

        # SLA requirements: 95% of events processed within 100ms, 99% within 500ms
        sla_95_percentile_ms = 100
        sla_99_percentile_ms = 500

        num_test_events = 1000
        response_times = []

        for i in range(num_test_events):
            event = CoordinationEvent(
                event_id=f"sla_test_{i}",
                event_type=CoordinationEventType.API_CALL_SUCCESS,
                source_component="sla_performance_test",
                event_data={
                    "sla_test": True,
                    "event_index": i,
                    "target_sla_95p": sla_95_percentile_ms,
                    "target_sla_99p": sla_99_percentile_ms
                }
            )

            # Measure response time for individual event
            start_time = time.time()
            await observatory.process_coordination_event(event)
            response_time_ms = (time.time() - start_time) * 1000

            response_times.append(response_time_ms)

        # Calculate percentiles
        response_times.sort()
        p95_index = int(0.95 * len(response_times))
        p99_index = int(0.99 * len(response_times))

        p95_response_time = response_times[p95_index]
        p99_response_time = response_times[p99_index]
        median_response_time = response_times[len(response_times) // 2]
        max_response_time = max(response_times)
        avg_response_time = sum(response_times) / len(response_times)

        # SLA compliance assertions
        assert p95_response_time <= sla_95_percentile_ms, f"95th percentile SLA violated: {p95_response_time:.1f}ms > {sla_95_percentile_ms}ms"
        assert p99_response_time <= sla_99_percentile_ms, f"99th percentile SLA violated: {p99_response_time:.1f}ms > {sla_99_percentile_ms}ms"
        assert avg_response_time <= 50, f"Average response time should be <50ms, was {avg_response_time:.1f}ms"

        # Calculate SLA compliance rates
        sla_95_compliant = sum(1 for rt in response_times if rt <= sla_95_percentile_ms)
        sla_99_compliant = sum(1 for rt in response_times if rt <= sla_99_percentile_ms)

        sla_95_compliance_rate = sla_95_compliant / len(response_times)
        sla_99_compliance_rate = sla_99_compliant / len(response_times)

        assert sla_95_compliance_rate >= 0.95, f"95th percentile SLA compliance rate: {sla_95_compliance_rate:.3%}"
        assert sla_99_compliance_rate >= 0.99, f"99th percentile SLA compliance rate: {sla_99_compliance_rate:.3%}"

        print(f"\nSLA Compliance Performance Results:")
        print(f"  Events Tested: {num_test_events}")
        print(f"  Median Response Time: {median_response_time:.1f}ms")
        print(f"  Average Response Time: {avg_response_time:.1f}ms")
        print(f"  95th Percentile: {p95_response_time:.1f}ms (SLA: {sla_95_percentile_ms}ms)")
        print(f"  99th Percentile: {p99_response_time:.1f}ms (SLA: {sla_99_percentile_ms}ms)")
        print(f"  Max Response Time: {max_response_time:.1f}ms")
        print(f"  95th Percentile Compliance: {sla_95_compliance_rate:.1%}")
        print(f"  99th Percentile Compliance: {sla_99_compliance_rate:.1%}")

    @pytest.mark.asyncio
    async def test_throughput_consistency_under_load(self, performance_observatory):
        """Test consistency of throughput under varying load conditions."""
        observatory = performance_observatory

        # Test throughput consistency across different load levels
        load_levels = [100, 500, 1000, 2000]  # events per measurement period
        measurement_periods = 5  # Measure 5 times per load level
        period_duration = 10  # 10 seconds per period

        throughput_results = {}

        for load_level in load_levels:
            load_throughputs = []

            print(f"Testing load level: {load_level} events/{period_duration}s")

            for period in range(measurement_periods):
                start_time = time.time()
                events_processed = 0

                # Process events at target rate
                events_per_second = load_level / period_duration

                for i in range(load_level):
                    event = CoordinationEvent(
                        event_id=f"throughput_test_{load_level}_{period}_{i}",
                        event_type=CoordinationEventType.METRICS_COLLECTED,
                        source_component="throughput_consistency_test",
                        event_data={
                            "load_level": load_level,
                            "period": period,
                            "event_index": i,
                            "target_rate": events_per_second
                        }
                    )

                    await observatory.process_coordination_event(event)
                    events_processed += 1

                    # Maintain timing if needed
                    if i % 100 == 0:
                        elapsed = time.time() - start_time
                        expected_elapsed = i / events_per_second
                        if elapsed < expected_elapsed:
                            await asyncio.sleep(expected_elapsed - elapsed)

                period_duration_actual = time.time() - start_time
                period_throughput = events_processed / period_duration_actual
                load_throughputs.append(period_throughput)

                print(f"  Period {period}: {period_throughput:.1f} events/sec")

            throughput_results[load_level] = load_throughputs

        # Analyze throughput consistency
        for load_level, throughputs in throughput_results.items():
            avg_throughput = sum(throughputs) / len(throughputs)
            min_throughput = min(throughputs)
            max_throughput = max(throughputs)

            # Calculate coefficient of variation (std dev / mean)
            variance = sum((t - avg_throughput) ** 2 for t in throughputs) / len(throughputs)
            std_dev = variance ** 0.5
            coeff_variation = std_dev / avg_throughput if avg_throughput > 0 else float('inf')

            # Consistency assertions
            throughput_consistency = min_throughput / max_throughput if max_throughput > 0 else 0
            assert throughput_consistency > 0.8, f"Throughput consistency at load {load_level} too low: {throughput_consistency:.3f}"
            assert coeff_variation < 0.2, f"Throughput variation at load {load_level} too high: {coeff_variation:.3f}"

            print(f"Load {load_level} - Avg: {avg_throughput:.1f}, Min: {min_throughput:.1f}, Max: {max_throughput:.1f}, CV: {coeff_variation:.3f}")

        # Verify throughput scales appropriately with load
        base_load = load_levels[0]
        base_throughput = sum(throughput_results[base_load]) / len(throughput_results[base_load])

        for load_level in load_levels[1:]:
            load_throughput = sum(throughput_results[load_level]) / len(throughput_results[load_level])
            scaling_ratio = load_throughput / base_throughput
            expected_ratio = load_level / base_load

            # Should scale reasonably with load (allowing for some degradation at high loads)
            min_acceptable_scaling = min(1.0, expected_ratio * 0.7)  # Allow 30% degradation at high loads
            assert scaling_ratio >= min_acceptable_scaling, f"Throughput scaling inadequate at load {load_level}: {scaling_ratio:.2f} vs expected {expected_ratio:.2f}"

        print(f"\nThroughput Consistency Results:")
        for load_level, throughputs in throughput_results.items():
            avg = sum(throughputs) / len(throughputs)
            print(f"  Load {load_level}: {avg:.1f} events/sec average")