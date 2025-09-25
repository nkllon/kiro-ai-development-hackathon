"""
Integration tests for Observatory with Beast Mode components.

Tests the Observatory's integration with core Beast Mode framework components
including TaskQueueManager, ReflectiveModules, and cross-system coordination.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from src.beast_mode.observatory.core_engine import ObservatoryCoreEngine
from src.beast_mode.observatory.models import (
    ObservatoryConfig,
    CoordinationEvent,
    CoordinationEventType,
    CoordinationMetrics,
    RedisConfig,
    MetricsConfig
)

# Mock Beast Mode components for integration testing
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability
)


@pytest.fixture
def mock_task_queue_manager():
    """Mock TaskQueueManager for integration testing."""
    mock_manager = AsyncMock()
    mock_manager.module_id = "task_queue_manager"
    mock_manager.get_health_status.return_value = ModuleHealth(
        module_id="task_queue_manager",
        status=ModuleStatus.HEALTHY,
        health_score=0.95,
        issues=[],
        last_check=datetime.now(),
        uptime_seconds=3600.0,
        error_count=0,
        warning_count=0
    )
    mock_manager.get_capabilities.return_value = [
        ModuleCapability.TASK_PROCESSING,
        ModuleCapability.COORDINATION
    ]
    mock_manager.get_module_info.return_value = {
        "module_id": "task_queue_manager",
        "name": "Task Queue Manager",
        "version": "1.0.0",
        "description": "Redis-backed task queue management"
    }
    return mock_manager


@pytest.fixture
def mock_redis_operations():
    """Mock Redis operations for testing."""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.xadd.return_value = "1234567890-0"
    mock_redis.xreadgroup.return_value = []
    mock_redis.close.return_value = None
    return mock_redis


@pytest.fixture
def integration_config():
    """Configuration for integration testing."""
    return ObservatoryConfig(
        redis_config=RedisConfig(
            host="localhost",
            port=6379,
            stream_name="integration_test_metrics"
        ),
        metrics_config=MetricsConfig(
            collection_interval_seconds=1,
            component_discovery_enabled=True
        )
    )


@pytest.fixture
async def observatory_with_beast_mode(integration_config, mock_task_queue_manager, mock_redis_operations):
    """Observatory engine integrated with Beast Mode components."""
    with patch('redis.asyncio.Redis', return_value=mock_redis_operations):
        observatory = ObservatoryCoreEngine(integration_config)

        # Register Beast Mode components
        await observatory.register_beast_mode_component(mock_task_queue_manager)

        # Initialize
        await observatory.initialize()

        yield observatory

        # Cleanup
        await observatory.shutdown()


class TestObservatoryBeastModeIntegration:
    """Test Observatory integration with Beast Mode framework."""

    @pytest.mark.asyncio
    async def test_beast_mode_component_registration(self, observatory_with_beast_mode, mock_task_queue_manager):
        """Test registering Beast Mode components with Observatory."""
        observatory = observatory_with_beast_mode

        # Verify component was registered
        registered_components = observatory.get_registered_components()
        assert "task_queue_manager" in registered_components

        # Verify component health is tracked
        health_status = await observatory.get_component_health("task_queue_manager")
        assert health_status is not None
        assert health_status.status == ModuleStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_cross_system_event_coordination(self, observatory_with_beast_mode, mock_task_queue_manager):
        """Test event coordination between Observatory and Beast Mode systems."""
        observatory = observatory_with_beast_mode

        # Simulate task queue event
        task_event = CoordinationEvent(
            event_type=CoordinationEventType.TASK_STARTED,
            source_component="task_queue_manager",
            event_data={
                "task_id": "task_123",
                "conversation_id": "conv_456",
                "priority": "high"
            }
        )

        # Process event through Observatory
        await observatory.process_coordination_event(task_event)

        # Verify Observatory tracked the event
        recent_events = observatory.get_recent_events(limit=1)
        assert len(recent_events) == 1
        assert recent_events[0].source_component == "task_queue_manager"
        assert recent_events[0].event_data["task_id"] == "task_123"

    @pytest.mark.asyncio
    async def test_beast_mode_metrics_collection(self, observatory_with_beast_mode, mock_task_queue_manager):
        """Test collecting metrics from Beast Mode components."""
        observatory = observatory_with_beast_mode

        # Mock task queue manager metrics
        mock_task_queue_manager.get_metrics.return_value = {
            "active_tasks": 15,
            "completed_tasks_today": 42,
            "error_rate": 0.02,
            "average_processing_time_ms": 150.5,
            "queue_depth": 8
        }

        # Trigger metrics collection
        await observatory._collect_beast_mode_metrics()

        # Verify metrics were collected
        latest_metrics = observatory.get_latest_coordination_metrics()
        assert latest_metrics is not None

        # Check that Beast Mode component metrics are included
        component_metrics = latest_metrics.component_metrics.get("task_queue_manager")
        assert component_metrics is not None
        assert component_metrics["active_tasks"] == 15
        assert component_metrics["completed_tasks_today"] == 42

    @pytest.mark.asyncio
    async def test_health_monitoring_integration(self, observatory_with_beast_mode, mock_task_queue_manager):
        """Test health monitoring integration with Beast Mode components."""
        observatory = observatory_with_beast_mode

        # Simulate component health degradation
        degraded_health = ModuleHealth(
            module_id="task_queue_manager",
            status=ModuleStatus.WARNING,
            health_score=0.65,
            issues=["High memory usage", "Slow Redis connection"],
            last_check=datetime.now(),
            uptime_seconds=3600.0,
            error_count=2,
            warning_count=1
        )
        mock_task_queue_manager.get_health_status.return_value = degraded_health

        # Trigger health check
        await observatory._perform_health_checks()

        # Verify Observatory detected health issues
        system_health = observatory.get_system_health()
        component_health = system_health.component_health.get("task_queue_manager")

        assert component_health is not None
        assert component_health.status == ModuleStatus.WARNING
        assert component_health.health_score == 0.65
        assert len(component_health.issues) == 2

    @pytest.mark.asyncio
    async def test_error_propagation_and_recovery(self, observatory_with_beast_mode, mock_task_queue_manager):
        """Test error propagation and recovery between systems."""
        observatory = observatory_with_beast_mode

        # Simulate error in Beast Mode component
        mock_task_queue_manager.get_health_status.side_effect = Exception("Component error")

        # Observatory should handle the error gracefully
        await observatory._perform_health_checks()

        # Verify Observatory tracked the error
        system_health = observatory.get_system_health()
        assert system_health.overall_status in [ModuleStatus.WARNING, ModuleStatus.ERROR]

        # Simulate recovery
        mock_task_queue_manager.get_health_status.side_effect = None
        mock_task_queue_manager.get_health_status.return_value = ModuleHealth(
            module_id="task_queue_manager",
            status=ModuleStatus.HEALTHY,
            health_score=0.95,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=3600.0,
            error_count=0,
            warning_count=0
        )

        # Trigger another health check
        await observatory._perform_health_checks()

        # Verify recovery was detected
        system_health = observatory.get_system_health()
        component_health = system_health.component_health.get("task_queue_manager")
        assert component_health.status == ModuleStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_distributed_coordination_scenarios(self, observatory_with_beast_mode, mock_task_queue_manager):
        """Test distributed coordination scenarios across Beast Mode components."""
        observatory = observatory_with_beast_mode

        # Simulate distributed task execution
        coordination_events = [
            CoordinationEvent(
                event_type=CoordinationEventType.TASK_STARTED,
                source_component="task_queue_manager",
                event_data={"task_id": "distributed_task_1", "node": "node_a"}
            ),
            CoordinationEvent(
                event_type=CoordinationEventType.COORDINATION_INITIATED,
                source_component="pdca_orchestrator",
                event_data={"coordination_id": "coord_123", "participants": ["node_a", "node_b"]}
            ),
            CoordinationEvent(
                event_type=CoordinationEventType.TASK_COMPLETED,
                source_component="task_queue_manager",
                event_data={"task_id": "distributed_task_1", "result": "success", "node": "node_a"}
            )
        ]

        # Process coordination events
        for event in coordination_events:
            await observatory.process_coordination_event(event)

        # Verify coordination pattern detection
        coordination_patterns = observatory.analyze_coordination_patterns()
        assert len(coordination_patterns) > 0

        # Should detect distributed execution pattern
        distributed_pattern = next(
            (p for p in coordination_patterns if "distributed" in p.pattern_type.lower()),
            None
        )
        assert distributed_pattern is not None

    @pytest.mark.asyncio
    async def test_performance_impact_monitoring(self, observatory_with_beast_mode, mock_task_queue_manager):
        """Test monitoring performance impact of Observatory on Beast Mode components."""
        observatory = observatory_with_beast_mode

        # Measure baseline performance
        start_time = time.time()

        # Simulate high-frequency coordination events
        events = []
        for i in range(100):
            event = CoordinationEvent(
                event_type=CoordinationEventType.API_CALL_SUCCESS,
                source_component="task_queue_manager",
                event_data={"request_id": f"req_{i}", "latency_ms": 50 + i}
            )
            events.append(observatory.process_coordination_event(event))

        # Process all events
        await asyncio.gather(*events)

        processing_time = time.time() - start_time

        # Verify performance is within acceptable limits
        assert processing_time < 5.0  # Should process 100 events in under 5 seconds

        # Verify Observatory didn't significantly impact component performance
        component_metrics = await observatory.get_performance_impact_metrics()
        task_queue_impact = component_metrics.get("task_queue_manager", {})

        # Observatory should have minimal performance impact
        assert task_queue_impact.get("cpu_overhead_percent", 0) < 5.0
        assert task_queue_impact.get("memory_overhead_mb", 0) < 50.0


class TestObservatoryTaskQueueIntegration:
    """Test specific integration with Beast Mode TaskQueueManager."""

    @pytest.fixture
    def mock_task_queue_with_metrics(self):
        """Mock TaskQueueManager with detailed metrics."""
        mock_manager = AsyncMock()
        mock_manager.module_id = "task_queue_manager"

        # Detailed metrics response
        mock_manager.get_metrics.return_value = {
            "queue_metrics": {
                "total_tasks_queued": 1250,
                "active_tasks": 8,
                "completed_tasks": 1200,
                "failed_tasks": 42,
                "average_queue_time_ms": 125.5,
                "average_processing_time_ms": 2150.8
            },
            "coordination_metrics": {
                "active_conversations": 15,
                "coordination_events_processed": 8420,
                "cross_conversation_coordination": 245,
                "coordination_success_rate": 0.987
            },
            "health_metrics": {
                "redis_connection_healthy": True,
                "error_rate_last_hour": 0.003,
                "memory_usage_mb": 234.5,
                "cpu_usage_percent": 12.8
            }
        }

        return mock_manager

    @pytest.mark.asyncio
    async def test_task_lifecycle_monitoring(self, integration_config, mock_task_queue_with_metrics):
        """Test monitoring complete task lifecycle through Observatory."""
        with patch('redis.asyncio.Redis', return_value=AsyncMock()):
            observatory = ObservatoryCoreEngine(integration_config)
            await observatory.register_beast_mode_component(mock_task_queue_with_metrics)
            await observatory.initialize()

            try:
                # Simulate complete task lifecycle
                task_lifecycle_events = [
                    CoordinationEvent(
                        event_type=CoordinationEventType.TASK_QUEUED,
                        source_component="task_queue_manager",
                        event_data={"task_id": "lifecycle_task_1", "priority": "normal"}
                    ),
                    CoordinationEvent(
                        event_type=CoordinationEventType.TASK_STARTED,
                        source_component="task_queue_manager",
                        event_data={"task_id": "lifecycle_task_1", "worker_id": "worker_001"}
                    ),
                    CoordinationEvent(
                        event_type=CoordinationEventType.COORDINATION_INITIATED,
                        source_component="task_queue_manager",
                        event_data={"task_id": "lifecycle_task_1", "coordination_type": "resource_allocation"}
                    ),
                    CoordinationEvent(
                        event_type=CoordinationEventType.TASK_COMPLETED,
                        source_component="task_queue_manager",
                        event_data={"task_id": "lifecycle_task_1", "duration_ms": 2500, "result": "success"}
                    )
                ]

                # Process lifecycle events
                for event in task_lifecycle_events:
                    await observatory.process_coordination_event(event)

                # Analyze task lifecycle
                task_analytics = observatory.analyze_task_lifecycle("lifecycle_task_1")

                assert task_analytics is not None
                assert task_analytics.total_duration_ms >= 2500
                assert task_analytics.coordination_events_count >= 1
                assert task_analytics.final_status == "success"

            finally:
                await observatory.shutdown()

    @pytest.mark.asyncio
    async def test_queue_performance_monitoring(self, integration_config, mock_task_queue_with_metrics):
        """Test monitoring task queue performance through Observatory."""
        with patch('redis.asyncio.Redis', return_value=AsyncMock()):
            observatory = ObservatoryCoreEngine(integration_config)
            await observatory.register_beast_mode_component(mock_task_queue_with_metrics)
            await observatory.initialize()

            try:
                # Collect metrics multiple times to establish trends
                for i in range(5):
                    await observatory._collect_beast_mode_metrics()
                    await asyncio.sleep(0.1)  # Small delay between collections

                # Analyze queue performance trends
                queue_trends = observatory.analyze_queue_performance_trends()

                assert queue_trends is not None
                assert "task_queue_manager" in queue_trends

                manager_trends = queue_trends["task_queue_manager"]
                assert "queue_depth_trend" in manager_trends
                assert "processing_time_trend" in manager_trends
                assert "error_rate_trend" in manager_trends

            finally:
                await observatory.shutdown()


class TestObservatoryPDCAIntegration:
    """Test integration with Beast Mode PDCA orchestration."""

    @pytest.fixture
    def mock_pdca_orchestrator(self):
        """Mock PDCA orchestrator for testing."""
        mock_orchestrator = AsyncMock()
        mock_orchestrator.module_id = "pdca_orchestrator"
        mock_orchestrator.get_health_status.return_value = ModuleHealth(
            module_id="pdca_orchestrator",
            status=ModuleStatus.HEALTHY,
            health_score=0.92,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=7200.0,
            error_count=0,
            warning_count=0
        )
        mock_orchestrator.get_metrics.return_value = {
            "active_cycles": 3,
            "completed_cycles_today": 12,
            "average_cycle_duration_minutes": 45.2,
            "coordination_effectiveness_score": 0.89
        }
        return mock_orchestrator

    @pytest.mark.asyncio
    async def test_pdca_cycle_monitoring(self, integration_config, mock_pdca_orchestrator):
        """Test monitoring PDCA cycles through Observatory."""
        with patch('redis.asyncio.Redis', return_value=AsyncMock()):
            observatory = ObservatoryCoreEngine(integration_config)
            await observatory.register_beast_mode_component(mock_pdca_orchestrator)
            await observatory.initialize()

            try:
                # Simulate PDCA cycle events
                pdca_events = [
                    CoordinationEvent(
                        event_type=CoordinationEventType.PDCA_CYCLE_STARTED,
                        source_component="pdca_orchestrator",
                        event_data={"cycle_id": "cycle_001", "phase": "plan", "objective": "improve_coordination"}
                    ),
                    CoordinationEvent(
                        event_type=CoordinationEventType.COORDINATION_MILESTONE,
                        source_component="pdca_orchestrator",
                        event_data={"cycle_id": "cycle_001", "phase": "do", "milestone": "implementation_50_percent"}
                    ),
                    CoordinationEvent(
                        event_type=CoordinationEventType.PDCA_CYCLE_COMPLETED,
                        source_component="pdca_orchestrator",
                        event_data={"cycle_id": "cycle_001", "outcome": "success", "effectiveness_score": 0.91}
                    )
                ]

                # Process PDCA events
                for event in pdca_events:
                    await observatory.process_coordination_event(event)

                # Analyze PDCA effectiveness
                pdca_analysis = observatory.analyze_pdca_effectiveness()

                assert pdca_analysis is not None
                assert pdca_analysis.cycles_analyzed >= 1
                assert pdca_analysis.average_effectiveness_score > 0.8

            finally:
                await observatory.shutdown()


class TestObservatoryEmojiRainIntegration:
    """Test integration of emoji rain with Beast Mode coordination events."""

    @pytest.fixture
    def mock_emoji_engine(self):
        """Mock emoji rain engine."""
        mock_engine = AsyncMock()
        mock_engine.trigger_event_rain.return_value = "effect_123"
        mock_engine.get_active_effects.return_value = []
        mock_engine.get_performance_stats.return_value = {
            "active_effects": 0,
            "total_particles": 0,
            "target_fps": 60
        }
        return mock_engine

    @pytest.mark.asyncio
    async def test_beast_mode_event_emoji_triggering(self, integration_config, mock_emoji_engine, mock_task_queue_manager):
        """Test that Beast Mode events trigger appropriate emoji rain effects."""
        with patch('redis.asyncio.Redis', return_value=AsyncMock()):
            observatory = ObservatoryCoreEngine(integration_config)

            # Integrate emoji engine
            observatory.emoji_engine = mock_emoji_engine

            # Register Beast Mode component
            await observatory.register_beast_mode_component(mock_task_queue_manager)
            await observatory.initialize()

            try:
                # Simulate significant Beast Mode achievement
                achievement_event = CoordinationEvent(
                    event_type=CoordinationEventType.ACHIEVEMENT_UNLOCKED,
                    source_component="task_queue_manager",
                    event_data={
                        "achievement": "coordination_mastery",
                        "participant": "user_alice",
                        "significance": "epic"
                    }
                )

                # Process event
                await observatory.process_coordination_event(achievement_event)

                # Verify emoji rain was triggered
                mock_emoji_engine.trigger_event_rain.assert_called_once()
                call_args = mock_emoji_engine.trigger_event_rain.call_args[0][0]
                assert call_args.event_type == CoordinationEventType.ACHIEVEMENT_UNLOCKED

            finally:
                await observatory.shutdown()


class TestObservatoryResilience:
    """Test Observatory resilience with Beast Mode component failures."""

    @pytest.mark.asyncio
    async def test_component_failure_handling(self, integration_config):
        """Test Observatory handling of Beast Mode component failures."""
        # Create a mock component that will fail
        failing_component = AsyncMock()
        failing_component.module_id = "failing_component"
        failing_component.get_health_status.side_effect = Exception("Component crashed")
        failing_component.get_metrics.side_effect = Exception("Metrics unavailable")

        with patch('redis.asyncio.Redis', return_value=AsyncMock()):
            observatory = ObservatoryCoreEngine(integration_config)
            await observatory.register_beast_mode_component(failing_component)
            await observatory.initialize()

            try:
                # Observatory should handle component failures gracefully
                await observatory._perform_health_checks()
                await observatory._collect_beast_mode_metrics()

                # Observatory should still be functional
                system_health = observatory.get_system_health()
                assert system_health is not None

                # Should indicate degraded state but continue operating
                assert system_health.overall_status in [ModuleStatus.WARNING, ModuleStatus.ERROR]

            finally:
                await observatory.shutdown()

    @pytest.mark.asyncio
    async def test_partial_component_recovery(self, integration_config):
        """Test Observatory handling partial component recovery."""
        # Create component that recovers partially
        recovering_component = AsyncMock()
        recovering_component.module_id = "recovering_component"

        # Initially healthy
        recovering_component.get_health_status.return_value = ModuleHealth(
            module_id="recovering_component",
            status=ModuleStatus.HEALTHY,
            health_score=0.95,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=3600.0,
            error_count=0,
            warning_count=0
        )

        with patch('redis.asyncio.Redis', return_value=AsyncMock()):
            observatory = ObservatoryCoreEngine(integration_config)
            await observatory.register_beast_mode_component(recovering_component)
            await observatory.initialize()

            try:
                # Initial healthy state
                await observatory._perform_health_checks()
                initial_health = observatory.get_system_health()
                assert initial_health.overall_status == ModuleStatus.HEALTHY

                # Simulate partial failure (metrics fail but health check works)
                recovering_component.get_metrics.side_effect = Exception("Metrics service down")

                await observatory._collect_beast_mode_metrics()
                await observatory._perform_health_checks()

                partial_failure_health = observatory.get_system_health()

                # Should detect partial failure but maintain some functionality
                component_health = partial_failure_health.component_health.get("recovering_component")
                assert component_health is not None

            finally:
                await observatory.shutdown()


class TestObservatoryScalability:
    """Test Observatory scalability with multiple Beast Mode components."""

    @pytest.mark.asyncio
    async def test_multiple_component_coordination(self, integration_config):
        """Test Observatory coordinating multiple Beast Mode components."""
        # Create multiple mock components
        components = []
        for i in range(10):
            component = AsyncMock()
            component.module_id = f"beast_component_{i}"
            component.get_health_status.return_value = ModuleHealth(
                module_id=f"beast_component_{i}",
                status=ModuleStatus.HEALTHY,
                health_score=0.9 + (i * 0.01),
                issues=[],
                last_check=datetime.now(),
                uptime_seconds=3600.0,
                error_count=0,
                warning_count=0
            )
            component.get_metrics.return_value = {
                "component_specific_metric": i * 10,
                "shared_metric": 100 - i
            }
            components.append(component)

        with patch('redis.asyncio.Redis', return_value=AsyncMock()):
            observatory = ObservatoryCoreEngine(integration_config)

            # Register all components
            for component in components:
                await observatory.register_beast_mode_component(component)

            await observatory.initialize()

            try:
                # Perform system-wide operations
                await observatory._perform_health_checks()
                await observatory._collect_beast_mode_metrics()

                # Verify all components are tracked
                system_health = observatory.get_system_health()
                assert len(system_health.component_health) == 10

                # Verify metrics from all components
                latest_metrics = observatory.get_latest_coordination_metrics()
                assert len(latest_metrics.component_metrics) == 10

                # Test coordinated event processing
                events = []
                for i in range(10):
                    event = CoordinationEvent(
                        event_type=CoordinationEventType.COORDINATION_INITIATED,
                        source_component=f"beast_component_{i}",
                        event_data={"coordination_id": f"coord_{i}"}
                    )
                    events.append(observatory.process_coordination_event(event))

                await asyncio.gather(*events)

                # Verify coordination patterns across components
                coordination_patterns = observatory.analyze_coordination_patterns()
                assert len(coordination_patterns) > 0

            finally:
                await observatory.shutdown()

    @pytest.mark.asyncio
    async def test_high_frequency_event_processing(self, integration_config, mock_task_queue_manager):
        """Test Observatory handling high-frequency events from Beast Mode."""
        with patch('redis.asyncio.Redis', return_value=AsyncMock()):
            observatory = ObservatoryCoreEngine(integration_config)
            await observatory.register_beast_mode_component(mock_task_queue_manager)
            await observatory.initialize()

            try:
                # Generate high-frequency events
                start_time = time.time()
                event_tasks = []

                for i in range(1000):
                    event = CoordinationEvent(
                        event_type=CoordinationEventType.API_CALL_SUCCESS,
                        source_component="task_queue_manager",
                        event_data={"request_id": f"high_freq_{i}", "latency_ms": 50}
                    )
                    event_tasks.append(observatory.process_coordination_event(event))

                # Process all events concurrently
                await asyncio.gather(*event_tasks)

                processing_time = time.time() - start_time

                # Verify performance is acceptable
                assert processing_time < 10.0  # Process 1000 events in under 10 seconds

                # Verify Observatory maintained data integrity
                recent_events = observatory.get_recent_events(limit=1000)
                assert len(recent_events) >= 900  # Allow for some sampling/cleanup

            finally:
                await observatory.shutdown()