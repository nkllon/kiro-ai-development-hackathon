"""
Stress and load testing for Observatory system.

Tests Observatory behavior under extreme stress conditions including
resource exhaustion, failure scenarios, recovery under load,
and breaking point determination.
"""

import asyncio
import pytest
import time
import gc
import psutil
import os
import random
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
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
class StressTestMetrics:
    """Metrics for stress testing."""
    test_duration_seconds: float
    events_attempted: int
    events_processed: int
    events_failed: int
    peak_memory_mb: float
    max_cpu_percent: float
    error_rate: float
    recovery_time_seconds: float
    breaking_point_reached: bool


class StressTestMonitor:
    """Monitor system behavior during stress tests."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = self.initial_memory
        self.max_cpu = 0.0
        self.memory_samples = []
        self.cpu_samples = []
        self.monitoring = False
        self._monitor_task = None

    async def start_monitoring(self):
        """Start stress test monitoring."""
        self.monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        """Stop stress test monitoring."""
        self.monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        """Monitor system resources during stress test."""
        while self.monitoring:
            try:
                # Memory monitoring
                current_memory = self.process.memory_info().rss / 1024 / 1024
                self.peak_memory = max(self.peak_memory, current_memory)
                self.memory_samples.append(current_memory)

                # CPU monitoring
                cpu_percent = self.process.cpu_percent()
                self.max_cpu = max(self.max_cpu, cpu_percent)
                self.cpu_samples.append(cpu_percent)

                await asyncio.sleep(0.05)  # Sample every 50ms for stress tests
            except Exception:
                break

    def get_peak_memory_usage(self) -> float:
        """Get peak memory usage above baseline."""
        return self.peak_memory - self.initial_memory

    def get_max_cpu_usage(self) -> float:
        """Get maximum CPU usage observed."""
        return self.max_cpu

    def is_resource_exhausted(self) -> bool:
        """Check if system resources appear exhausted."""
        current_memory = self.process.memory_info().rss / 1024 / 1024
        memory_exhausted = current_memory > 4096  # 4GB threshold
        cpu_exhausted = self.max_cpu > 95  # 95% CPU threshold
        return memory_exhausted or cpu_exhausted


@pytest.fixture
def stress_test_config():
    """Configuration for stress testing."""
    return ObservatoryConfig(
        redis_config=RedisConfig(
            host="localhost",
            port=6379,
            stream_name="stress_test_stream",
            connection_pool_size=50  # Increased pool for stress tests
        ),
        metrics_config=MetricsConfig(
            collection_interval_seconds=0.5,  # Faster collection for stress tests
            component_discovery_enabled=True,
            performance_impact_limit=0.25  # Allow higher impact during stress tests
        )
    )


@pytest.fixture
def mock_stress_redis():
    """Mock Redis client that can simulate failures under stress."""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.xgroup_create.return_value = None
    mock_redis.close.return_value = None

    # Simulate Redis under stress - occasional failures and increased latency
    async def stress_xadd(stream_name, data):
        # Simulate increasing latency under load
        stress_latency = random.uniform(0.001, 0.010)  # 1-10ms latency
        await asyncio.sleep(stress_latency)

        # Simulate occasional Redis failures (5% failure rate under stress)
        if random.random() < 0.05:
            raise Exception("Redis connection timeout under stress")

        return f"{int(time.time() * 1000)}-{hash(str(data)) % 10000}"

    mock_redis.xadd.side_effect = stress_xadd
    return mock_redis


@pytest.fixture
async def stress_test_observatory(stress_test_config, mock_stress_redis):
    """Observatory configured for stress testing."""
    with patch('redis.asyncio.Redis', return_value=mock_stress_redis), \
         patch('redis.asyncio.from_url', return_value=mock_stress_redis):

        observatory = ObservatoryCoreEngine(stress_test_config)
        await observatory.initialize()

        yield observatory

        await observatory.shutdown()


class TestResourceExhaustionScenarios:
    """Test Observatory behavior under resource exhaustion."""

    @pytest.mark.asyncio
    async def test_memory_exhaustion_handling(self, stress_test_observatory):
        """Test Observatory behavior approaching memory limits."""
        observatory = stress_test_observatory
        monitor = StressTestMonitor()

        await monitor.start_monitoring()
        start_time = time.time()

        try:
            # Gradually increase memory pressure
            memory_pressure_events = []
            events_processed = 0
            events_failed = 0

            # Start with reasonable payloads and increase size
            for round_num in range(10):
                payload_size_kb = 10 * (2 ** round_num)  # Exponentially increasing payload size
                events_in_round = max(1, 100 // (round_num + 1))  # Fewer events as size increases

                print(f"Memory stress round {round_num}: {payload_size_kb}KB payloads, {events_in_round} events")

                for i in range(events_in_round):
                    # Create increasingly large payloads
                    large_data = "x" * (payload_size_kb * 1024)  # Create large string
                    nested_data = {
                        f"large_field_{j}": large_data for j in range(min(10, payload_size_kb // 100))
                    }

                    event = CoordinationEvent(
                        event_id=f"memory_stress_{round_num}_{i}",
                        event_type=CoordinationEventType.SYSTEM_STATUS_UPDATE,
                        source_component="memory_exhaustion_test",
                        event_data={
                            "round": round_num,
                            "payload_size_kb": payload_size_kb,
                            "large_nested_data": nested_data,
                            "memory_stress_test": True
                        }
                    )

                    try:
                        await observatory.process_coordination_event(event)
                        events_processed += 1
                    except Exception as e:
                        events_failed += 1
                        print(f"Event failed at round {round_num}: {str(e)[:100]}")

                # Check if we've hit resource limits
                if monitor.is_resource_exhausted():
                    print(f"Resource exhaustion detected at round {round_num}")
                    break

                # Force garbage collection between rounds
                gc.collect()
                await asyncio.sleep(0.1)

            test_duration = time.time() - start_time

        finally:
            await monitor.stop_monitoring()

        # Analyze memory exhaustion behavior
        peak_memory = monitor.get_peak_memory_usage()
        max_cpu = monitor.get_max_cpu_usage()
        error_rate = events_failed / (events_processed + events_failed) if events_processed + events_failed > 0 else 0

        # Memory exhaustion handling assertions
        assert events_processed > 0, "Should process some events before exhaustion"
        assert peak_memory < 8192, f"Should not exceed 8GB memory usage, used {peak_memory:.1f}MB"

        # Observatory should handle memory pressure gracefully
        if error_rate > 0:
            assert error_rate < 0.5, f"Error rate under memory pressure should be <50%, was {error_rate:.3%}"

        print(f"\nMemory Exhaustion Test Results:")
        print(f"  Events Processed: {events_processed}")
        print(f"  Events Failed: {events_failed}")
        print(f"  Error Rate: {error_rate:.3%}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Max CPU: {max_cpu:.1f}%")
        print(f"  Test Duration: {test_duration:.1f}s")

    @pytest.mark.asyncio
    async def test_cpu_saturation_handling(self, stress_test_observatory):
        """Test Observatory behavior under CPU saturation."""
        observatory = stress_test_observatory
        monitor = StressTestMonitor()

        await monitor.start_monitoring()
        start_time = time.time()

        try:
            # Create CPU-intensive coordination events
            cpu_intensive_duration = 30  # 30 seconds of CPU stress
            events_per_second = 200
            total_events = cpu_intensive_duration * events_per_second

            async def cpu_intensive_event_processor(event_batch):
                """Process a batch of CPU-intensive events."""
                results = []
                for event in event_batch:
                    try:
                        # Add CPU-intensive processing to event data
                        event.event_data["cpu_intensive_hash"] = hash(str(event.event_data)) % 1000000

                        # Simulate computational coordination analysis
                        coordination_score = 0.0
                        for i in range(100):  # CPU-intensive loop
                            coordination_score += hash(f"{event.event_id}_{i}") % 1000 / 1000000

                        event.event_data["computed_coordination_score"] = coordination_score

                        await observatory.process_coordination_event(event)
                        results.append(True)
                    except Exception:
                        results.append(False)

                return results

            # Generate events in batches to saturate CPU
            batch_size = 50
            events_processed = 0
            events_failed = 0

            for second in range(cpu_intensive_duration):
                batch_events = []

                for i in range(events_per_second):
                    event = CoordinationEvent(
                        event_id=f"cpu_stress_{second}_{i}",
                        event_type=CoordinationEventType.COORDINATION_MILESTONE,
                        source_component="cpu_saturation_test",
                        event_data={
                            "second": second,
                            "event_index": i,
                            "cpu_intensive_data": list(range(100)),  # CPU load data
                            "complex_nested": {f"key_{j}": j**2 for j in range(50)}
                        }
                    )
                    batch_events.append(event)

                # Process batches concurrently to maximize CPU usage
                batch_tasks = []
                for i in range(0, len(batch_events), batch_size):
                    batch = batch_events[i:i + batch_size]
                    batch_tasks.append(cpu_intensive_event_processor(batch))

                # Wait for batch completion
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                # Count successes and failures
                for result in batch_results:
                    if isinstance(result, list):
                        events_processed += sum(1 for r in result if r)
                        events_failed += sum(1 for r in result if not r)
                    else:
                        events_failed += batch_size  # Entire batch failed

                # Progress indicator
                if second % 5 == 0:
                    current_cpu = monitor.process.cpu_percent()
                    print(f"CPU stress second {second}: {current_cpu:.1f}% CPU, {events_processed} processed")

            test_duration = time.time() - start_time

        finally:
            await monitor.stop_monitoring()

        # Analyze CPU saturation behavior
        peak_memory = monitor.get_peak_memory_usage()
        max_cpu = monitor.get_max_cpu_usage()
        error_rate = events_failed / (events_processed + events_failed) if events_processed + events_failed > 0 else 0
        events_per_second_actual = events_processed / test_duration

        # CPU saturation handling assertions
        assert events_processed >= total_events * 0.70, f"Should process 70% of events under CPU saturation"
        assert max_cpu > 50, f"Should achieve significant CPU usage, got {max_cpu:.1f}%"
        assert error_rate < 0.30, f"Error rate under CPU saturation should be <30%, was {error_rate:.3%}"
        assert events_per_second_actual > 50, f"Should maintain >50 events/sec under CPU stress"

        print(f"\nCPU Saturation Test Results:")
        print(f"  Target Events: {total_events}")
        print(f"  Events Processed: {events_processed}")
        print(f"  Events Failed: {events_failed}")
        print(f"  Error Rate: {error_rate:.3%}")
        print(f"  Events/Second: {events_per_second_actual:.1f}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Max CPU: {max_cpu:.1f}%")
        print(f"  Test Duration: {test_duration:.1f}s")


class TestFailureResilienceUnderLoad:
    """Test Observatory resilience to failures under high load."""

    @pytest.mark.asyncio
    async def test_redis_failures_under_load(self, stress_test_config):
        """Test Observatory behavior when Redis fails under high load."""
        # Create Redis mock that fails increasingly under load
        failure_redis = AsyncMock()
        failure_redis.ping.return_value = True
        failure_redis.xgroup_create.return_value = None
        failure_redis.close.return_value = None

        failure_count = 0
        total_calls = 0

        async def failing_xadd(stream_name, data):
            nonlocal failure_count, total_calls
            total_calls += 1

            # Increase failure rate as load increases
            failure_probability = min(0.5, total_calls / 10000)  # Up to 50% failure rate

            if random.random() < failure_probability:
                failure_count += 1
                raise Exception(f"Redis failure #{failure_count} under load")

            # Simulate latency increase under load
            latency = 0.001 + (total_calls / 100000) * 0.01  # Increasing latency
            await asyncio.sleep(latency)

            return f"{int(time.time() * 1000)}-{total_calls}"

        failure_redis.xadd.side_effect = failing_xadd

        with patch('redis.asyncio.Redis', return_value=failure_redis), \
             patch('redis.asyncio.from_url', return_value=failure_redis):

            observatory = ObservatoryCoreEngine(stress_test_config)
            monitor = StressTestMonitor()

            await monitor.start_monitoring()
            start_time = time.time()

            try:
                await observatory.initialize()

                # Generate high load with increasing Redis failures
                load_duration = 60  # 1 minute of load with failures
                events_per_second = 100
                total_target_events = load_duration * events_per_second

                events_attempted = 0
                events_processed = 0
                events_failed = 0

                for second in range(load_duration):
                    second_events = []

                    for i in range(events_per_second):
                        event = CoordinationEvent(
                            event_id=f"redis_failure_test_{second}_{i}",
                            event_type=CoordinationEventType.API_CALL_SUCCESS,
                            source_component="redis_failure_resilience_test",
                            event_data={
                                "second": second,
                                "event_index": i,
                                "load_test": True,
                                "expected_redis_failures": True
                            }
                        )
                        second_events.append(event)

                    # Process events concurrently
                    event_tasks = [observatory.process_coordination_event(event) for event in second_events]
                    results = await asyncio.gather(*event_tasks, return_exceptions=True)

                    # Count results
                    events_attempted += len(results)
                    second_successes = sum(1 for r in results if not isinstance(r, Exception))
                    second_failures = len(results) - second_successes

                    events_processed += second_successes
                    events_failed += second_failures

                    # Progress update
                    if second % 10 == 0:
                        current_failure_rate = events_failed / events_attempted if events_attempted > 0 else 0
                        print(f"Second {second}: {second_successes} successes, {second_failures} failures, overall failure rate: {current_failure_rate:.3%}")

                test_duration = time.time() - start_time

            finally:
                await monitor.stop_monitoring()
                await observatory.shutdown()

        # Analyze Redis failure resilience
        peak_memory = monitor.get_peak_memory_usage()
        max_cpu = monitor.get_max_cpu_usage()
        overall_error_rate = events_failed / events_attempted if events_attempted > 0 else 0
        redis_failure_rate = failure_count / total_calls if total_calls > 0 else 0

        # Failure resilience assertions
        assert events_processed > 0, "Should process some events despite Redis failures"
        assert events_attempted >= total_target_events * 0.90, "Should attempt most target events"

        # Observatory should be more resilient than underlying Redis
        resilience_improvement = redis_failure_rate - overall_error_rate
        assert resilience_improvement >= 0, f"Observatory should not make Redis failures worse"

        # System should remain stable despite failures
        assert peak_memory < 2000, f"Memory should stay reasonable despite failures, used {peak_memory:.1f}MB"

        print(f"\nRedis Failure Resilience Results:")
        print(f"  Target Events: {total_target_events}")
        print(f"  Events Attempted: {events_attempted}")
        print(f"  Events Processed: {events_processed}")
        print(f"  Events Failed: {events_failed}")
        print(f"  Overall Error Rate: {overall_error_rate:.3%}")
        print(f"  Redis Failure Rate: {redis_failure_rate:.3%}")
        print(f"  Resilience Improvement: {resilience_improvement:.3%}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Test Duration: {test_duration:.1f}s")

    @pytest.mark.asyncio
    async def test_component_failures_during_high_load(self, stress_test_observatory):
        """Test Observatory behavior when Beast Mode components fail during high load."""
        observatory = stress_test_observatory
        monitor = StressTestMonitor()

        # Create multiple mock components that will fail under load
        num_components = 20
        failing_components = []

        for i in range(num_components):
            component = AsyncMock()
            component.module_id = f"failing_component_{i}"

            # Components start healthy but degrade under load
            health_calls = 0

            def create_degrading_health(component_id, degradation_rate):
                def get_health():
                    nonlocal health_calls
                    health_calls += 1

                    # Health degrades with load
                    health_score = max(0.1, 1.0 - (health_calls * degradation_rate))

                    if health_score > 0.7:
                        status = ModuleStatus.HEALTHY
                        issues = []
                    elif health_score > 0.4:
                        status = ModuleStatus.WARNING
                        issues = ["Performance degradation under load"]
                    else:
                        status = ModuleStatus.ERROR
                        issues = ["Component failure under high load", "Resource exhaustion"]

                    return ModuleHealth(
                        module_id=component_id,
                        status=status,
                        health_score=health_score,
                        issues=issues,
                        last_check=datetime.now(),
                        uptime_seconds=3600.0,
                        error_count=max(0, int((1.0 - health_score) * 10)),
                        warning_count=1 if status == ModuleStatus.WARNING else 0
                    )
                return get_health

            component.get_health_status.side_effect = create_degrading_health(component.module_id, 0.001)

            # Metrics also degrade
            metrics_calls = 0

            def get_degrading_metrics():
                nonlocal metrics_calls
                metrics_calls += 1

                if metrics_calls > 50:  # Start failing metrics after 50 calls
                    raise Exception(f"Component {component.module_id} metrics service failed under load")

                return {
                    "load_metric": metrics_calls * 10,
                    "degradation_indicator": metrics_calls / 100,
                    "failure_imminent": metrics_calls > 40
                }

            component.get_metrics.side_effect = get_degrading_metrics
            failing_components.append(component)

        await monitor.start_monitoring()
        start_time = time.time()

        try:
            # Register all components
            for component in failing_components:
                await observatory.register_beast_mode_component(component)

            # Generate high load while components fail
            load_duration = 45  # 45 seconds of load with component failures
            events_per_second = 150

            events_processed = 0
            events_failed = 0
            health_checks_performed = 0
            metrics_collections_performed = 0

            for second in range(load_duration):
                # Generate events from various components
                second_events = []

                for i in range(events_per_second):
                    source_component = random.choice(failing_components).module_id

                    event = CoordinationEvent(
                        event_id=f"component_failure_test_{second}_{i}",
                        event_type=CoordinationEventType.COORDINATION_MILESTONE,
                        source_component=source_component,
                        event_data={
                            "second": second,
                            "event_index": i,
                            "source_component": source_component,
                            "component_failure_test": True
                        }
                    )
                    second_events.append(event)

                # Process events
                event_tasks = [observatory.process_coordination_event(event) for event in second_events]
                results = await asyncio.gather(*event_tasks, return_exceptions=True)

                events_processed += sum(1 for r in results if not isinstance(r, Exception))
                events_failed += sum(1 for r in results if isinstance(r, Exception))

                # Trigger health checks and metrics collection (this will cause failures)
                if second % 5 == 0:
                    try:
                        await observatory._perform_health_checks()
                        health_checks_performed += 1
                    except Exception:
                        pass

                if second % 3 == 0:
                    try:
                        await observatory._collect_beast_mode_metrics()
                        metrics_collections_performed += 1
                    except Exception:
                        pass

                # Progress update
                if second % 10 == 0:
                    error_rate = events_failed / (events_processed + events_failed) if events_processed + events_failed > 0 else 0
                    system_health = observatory.get_system_health()
                    healthy_components = sum(1 for h in system_health.component_health.values() if h.status == ModuleStatus.HEALTHY)

                    print(f"Second {second}: {events_processed} processed, {events_failed} failed, "
                          f"error rate: {error_rate:.3%}, healthy components: {healthy_components}/{num_components}")

            test_duration = time.time() - start_time

        finally:
            await monitor.stop_monitoring()

        # Analyze component failure resilience
        peak_memory = monitor.get_peak_memory_usage()
        max_cpu = monitor.get_max_cpu_usage()
        total_events = events_processed + events_failed
        error_rate = events_failed / total_events if total_events > 0 else 0

        # Get final system health
        final_system_health = observatory.get_system_health()
        healthy_components = sum(1 for h in final_system_health.component_health.values() if h.status == ModuleStatus.HEALTHY)
        degraded_components = num_components - healthy_components

        # Component failure resilience assertions
        assert events_processed > 0, "Should process some events despite component failures"
        assert error_rate < 0.40, f"Error rate should be <40% despite component failures, was {error_rate:.3%}"
        assert health_checks_performed > 0, "Should perform some health checks"
        assert peak_memory < 1500, f"Memory should stay reasonable despite component failures"

        # Observatory should continue functioning even with component failures
        assert final_system_health.overall_status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.ERROR], "System should maintain status"

        print(f"\nComponent Failure Resilience Results:")
        print(f"  Total Components: {num_components}")
        print(f"  Healthy Components (final): {healthy_components}")
        print(f"  Degraded Components: {degraded_components}")
        print(f"  Events Processed: {events_processed}")
        print(f"  Events Failed: {events_failed}")
        print(f"  Error Rate: {error_rate:.3%}")
        print(f"  Health Checks: {health_checks_performed}")
        print(f"  Metrics Collections: {metrics_collections_performed}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  System Status: {final_system_health.overall_status}")


class TestBreakingPointDetermination:
    """Determine Observatory system breaking points and limits."""

    @pytest.mark.asyncio
    async def test_find_maximum_event_throughput(self, stress_test_observatory):
        """Find the maximum sustainable event throughput."""
        observatory = stress_test_observatory
        monitor = StressTestMonitor()

        await monitor.start_monitoring()

        try:
            # Binary search for maximum throughput
            min_throughput = 100  # events per second
            max_throughput = 5000  # events per second
            test_duration = 30  # 30 seconds per test
            acceptable_error_rate = 0.05  # 5% error rate threshold

            max_sustainable_throughput = 0

            print("Finding maximum sustainable throughput...")

            while max_throughput - min_throughput > 50:
                target_throughput = (min_throughput + max_throughput) // 2
                total_events = target_throughput * test_duration

                print(f"Testing throughput: {target_throughput} events/sec")

                # Test this throughput level
                start_time = time.time()
                events_attempted = 0
                events_processed = 0
                events_failed = 0

                try:
                    for second in range(test_duration):
                        second_events = []

                        for i in range(target_throughput):
                            event = CoordinationEvent(
                                event_id=f"throughput_test_{target_throughput}_{second}_{i}",
                                event_type=CoordinationEventType.API_CALL_SUCCESS,
                                source_component="throughput_breaking_point_test",
                                event_data={
                                    "target_throughput": target_throughput,
                                    "second": second,
                                    "event_index": i
                                }
                            )
                            second_events.append(event)

                        # Process events concurrently
                        event_tasks = [observatory.process_coordination_event(event) for event in second_events]
                        results = await asyncio.gather(*event_tasks, return_exceptions=True)

                        events_attempted += len(results)
                        events_processed += sum(1 for r in results if not isinstance(r, Exception))
                        events_failed += sum(1 for r in results if isinstance(r, Exception))

                    actual_duration = time.time() - start_time
                    actual_throughput = events_processed / actual_duration
                    error_rate = events_failed / events_attempted if events_attempted > 0 else 0

                    print(f"  Results: {actual_throughput:.0f} events/sec actual, {error_rate:.3%} error rate")

                    # Check if this throughput level is sustainable
                    if error_rate <= acceptable_error_rate and actual_throughput >= target_throughput * 0.9:
                        # Throughput is sustainable
                        max_sustainable_throughput = target_throughput
                        min_throughput = target_throughput
                    else:
                        # Throughput exceeded limits
                        max_throughput = target_throughput

                except Exception as e:
                    print(f"  Failed at {target_throughput} events/sec: {str(e)[:100]}")
                    max_throughput = target_throughput

                # Reset memory between tests
                gc.collect()
                await asyncio.sleep(2)

        finally:
            await monitor.stop_monitoring()

        peak_memory = monitor.get_peak_memory_usage()
        max_cpu = monitor.get_max_cpu_usage()

        # Breaking point assertions
        assert max_sustainable_throughput > 0, "Should find some sustainable throughput level"
        assert max_sustainable_throughput >= 100, f"Should sustain at least 100 events/sec, found {max_sustainable_throughput}"

        print(f"\nMaximum Throughput Results:")
        print(f"  Maximum Sustainable Throughput: {max_sustainable_throughput} events/sec")
        print(f"  Peak Memory Usage: {peak_memory:.1f}MB")
        print(f"  Max CPU Usage: {max_cpu:.1f}%")
        print(f"  Error Rate Threshold: {acceptable_error_rate:.1%}")

    @pytest.mark.asyncio
    async def test_maximum_concurrent_connections(self, stress_test_config, mock_stress_redis):
        """Test maximum number of concurrent Beast Mode component connections."""
        with patch('redis.asyncio.Redis', return_value=mock_stress_redis), \
             patch('redis.asyncio.from_url', return_value=mock_stress_redis):

            monitor = StressTestMonitor()
            await monitor.start_monitoring()

            try:
                # Test increasing numbers of components until failure
                max_components_tested = 500
                components_step = 50
                max_successful_components = 0

                for num_components in range(components_step, max_components_tested + 1, components_step):
                    print(f"Testing {num_components} concurrent components...")

                    try:
                        observatory = ObservatoryCoreEngine(stress_test_config)
                        await observatory.initialize()

                        # Create and register components
                        components = []
                        for i in range(num_components):
                            component = AsyncMock()
                            component.module_id = f"concurrent_test_component_{i}"
                            component.get_health_status.return_value = ModuleHealth(
                                module_id=f"concurrent_test_component_{i}",
                                status=ModuleStatus.HEALTHY,
                                health_score=0.9,
                                issues=[],
                                last_check=datetime.now(),
                                uptime_seconds=3600.0,
                                error_count=0,
                                warning_count=0
                            )
                            component.get_metrics.return_value = {
                                f"component_{i}_metric": i,
                                "connection_test": True
                            }
                            components.append(component)

                        # Register all components
                        registration_start = time.time()
                        for component in components:
                            await observatory.register_beast_mode_component(component)

                        registration_time = time.time() - registration_start

                        # Test basic operations with all components
                        health_check_start = time.time()
                        await observatory._perform_health_checks()
                        health_check_time = time.time() - health_check_start

                        metrics_collection_start = time.time()
                        await observatory._collect_beast_mode_metrics()
                        metrics_collection_time = time.time() - metrics_collection_start

                        # Test event processing from all components
                        event_processing_start = time.time()
                        test_events = []
                        for i, component in enumerate(components[:min(100, num_components)]):  # Limit to 100 events
                            event = CoordinationEvent(
                                event_id=f"concurrent_component_test_{i}",
                                event_type=CoordinationEventType.COORDINATION_MILESTONE,
                                source_component=component.module_id,
                                event_data={"concurrent_test": True, "component_index": i}
                            )
                            test_events.append(observatory.process_coordination_event(event))

                        await asyncio.gather(*test_events)
                        event_processing_time = time.time() - event_processing_start

                        await observatory.shutdown()

                        # Success - record this as max successful
                        max_successful_components = num_components

                        print(f"  Success: {num_components} components")
                        print(f"    Registration time: {registration_time:.2f}s")
                        print(f"    Health check time: {health_check_time:.2f}s")
                        print(f"    Metrics collection time: {metrics_collection_time:.2f}s")
                        print(f"    Event processing time: {event_processing_time:.2f}s")

                        # Check if operations are becoming too slow (indicating limits)
                        if (registration_time > 30 or health_check_time > 10 or
                            metrics_collection_time > 10 or event_processing_time > 30):
                            print(f"  Operations too slow at {num_components} components, stopping test")
                            break

                    except Exception as e:
                        print(f"  Failed at {num_components} components: {str(e)[:100]}")
                        break

                    # Check memory usage
                    if monitor.is_resource_exhausted():
                        print(f"  Resource exhaustion at {num_components} components")
                        break

            finally:
                await monitor.stop_monitoring()

        peak_memory = monitor.get_peak_memory_usage()
        max_cpu = monitor.get_max_cpu_usage()

        # Concurrent connections assertions
        assert max_successful_components > 0, "Should handle at least some concurrent components"
        assert max_successful_components >= 50, f"Should handle at least 50 components, handled {max_successful_components}"

        print(f"\nMaximum Concurrent Connections Results:")
        print(f"  Maximum Successful Components: {max_successful_components}")
        print(f"  Peak Memory Usage: {peak_memory:.1f}MB")
        print(f"  Max CPU Usage: {max_cpu:.1f}%")

    @pytest.mark.asyncio
    async def test_sustained_load_endurance(self, stress_test_observatory):
        """Test Observatory endurance under sustained load over extended time."""
        observatory = stress_test_observatory
        monitor = StressTestMonitor()

        await monitor.start_monitoring()
        start_time = time.time()

        try:
            # Sustained load test - 10 minutes at moderate throughput
            endurance_duration_minutes = 10
            events_per_second = 200  # Moderate throughput for endurance
            total_duration_seconds = endurance_duration_minutes * 60

            events_processed = 0
            events_failed = 0
            memory_samples = []
            performance_samples = []

            print(f"Starting {endurance_duration_minutes}-minute endurance test at {events_per_second} events/sec...")

            for minute in range(endurance_duration_minutes):
                minute_start = time.time()
                minute_events_processed = 0
                minute_events_failed = 0

                for second in range(60):
                    second_events = []

                    for i in range(events_per_second):
                        event = CoordinationEvent(
                            event_id=f"endurance_test_{minute}_{second}_{i}",
                            event_type=CoordinationEventType.METRICS_COLLECTED,
                            source_component="endurance_test",
                            event_data={
                                "minute": minute,
                                "second": second,
                                "event_index": i,
                                "endurance_test": True,
                                "elapsed_seconds": minute * 60 + second
                            }
                        )
                        second_events.append(event)

                    # Process events
                    event_tasks = [observatory.process_coordination_event(event) for event in second_events]
                    results = await asyncio.gather(*event_tasks, return_exceptions=True)

                    second_successes = sum(1 for r in results if not isinstance(r, Exception))
                    second_failures = len(results) - second_successes

                    minute_events_processed += second_successes
                    minute_events_failed += second_failures

                minute_duration = time.time() - minute_start
                events_processed += minute_events_processed
                events_failed += minute_events_failed

                # Record performance sample
                current_memory = monitor.process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)

                minute_throughput = minute_events_processed / minute_duration
                performance_samples.append(minute_throughput)

                print(f"Minute {minute + 1}: {minute_events_processed} processed, "
                      f"{minute_throughput:.0f} events/sec, {current_memory:.0f}MB memory")

                # Force garbage collection every few minutes
                if minute % 3 == 0:
                    gc.collect()

            total_duration = time.time() - start_time

        finally:
            await monitor.stop_monitoring()

        # Analyze endurance results
        peak_memory = monitor.get_peak_memory_usage()
        max_cpu = monitor.get_max_cpu_usage()
        avg_throughput = events_processed / total_duration
        error_rate = events_failed / (events_processed + events_failed) if events_processed + events_failed > 0 else 0

        # Calculate performance stability
        performance_std_dev = (sum((p - avg_throughput) ** 2 for p in performance_samples) / len(performance_samples)) ** 0.5
        performance_coefficient_variation = performance_std_dev / avg_throughput if avg_throughput > 0 else float('inf')

        # Memory growth analysis
        initial_memory = memory_samples[0] if memory_samples else 0
        final_memory = memory_samples[-1] if memory_samples else 0
        memory_growth = final_memory - initial_memory

        # Endurance test assertions
        assert events_processed >= (endurance_duration_minutes * 60 * events_per_second * 0.90), "Should process 90% of target events"
        assert error_rate < 0.10, f"Error rate should be <10% during endurance test, was {error_rate:.3%}"
        assert performance_coefficient_variation < 0.3, f"Performance should be stable, CV: {performance_coefficient_variation:.3f}"
        assert memory_growth < 1000, f"Memory growth should be <1GB over {endurance_duration_minutes} minutes, was {memory_growth:.1f}MB"
        assert avg_throughput >= events_per_second * 0.85, f"Should maintain 85% of target throughput"

        print(f"\nEndurance Test Results ({endurance_duration_minutes} minutes):")
        print(f"  Target Events: {endurance_duration_minutes * 60 * events_per_second}")
        print(f"  Events Processed: {events_processed}")
        print(f"  Events Failed: {events_failed}")
        print(f"  Error Rate: {error_rate:.3%}")
        print(f"  Average Throughput: {avg_throughput:.1f} events/sec")
        print(f"  Performance Stability (CV): {performance_coefficient_variation:.3f}")
        print(f"  Peak Memory: {peak_memory:.1f}MB")
        print(f"  Memory Growth: {memory_growth:.1f}MB")
        print(f"  Test Duration: {total_duration/60:.1f} minutes")