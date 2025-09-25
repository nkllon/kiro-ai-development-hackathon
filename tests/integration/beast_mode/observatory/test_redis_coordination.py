"""
Integration tests for Observatory Redis coordination across Beast Mode systems.

Tests real Redis stream coordination, cross-system event propagation,
and distributed state management between Observatory and Beast Mode components.
"""

import asyncio
import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List

import redis.asyncio as redis

from src.beast_mode.observatory.redis_streams import ObservatoryRedisStreams
from src.beast_mode.observatory.models import (
    CoordinationEvent,
    CoordinationEventType,
    RedisConfig
)


@pytest.fixture
def test_redis_config():
    """Redis configuration for integration testing."""
    return RedisConfig(
        host="localhost",
        port=6379,
        stream_name="test_coordination_stream",
        connection_pool_size=5
    )


@pytest.fixture
async def real_redis_client(test_redis_config):
    """Real Redis client for integration testing."""
    try:
        client = redis.Redis(
            host=test_redis_config.host,
            port=test_redis_config.port,
            decode_responses=True
        )

        # Test connection
        await client.ping()
        yield client

        # Cleanup
        await client.flushdb()  # Clear test data
        await client.close()

    except Exception as e:
        pytest.skip(f"Redis not available for integration testing: {e}")


@pytest.fixture
async def observatory_streams(test_redis_config, real_redis_client):
    """Observatory Redis streams for integration testing."""
    streams = ObservatoryRedisStreams(test_redis_config)

    with patch('redis.asyncio.from_url', return_value=real_redis_client):
        initialized = await streams.initialize()
        if not initialized:
            pytest.skip("Failed to initialize Observatory Redis streams")

        yield streams
        await streams.close()


class TestRealRedisCoordination:
    """Test real Redis coordination functionality."""

    @pytest.mark.asyncio
    async def test_real_event_publishing_and_consuming(self, observatory_streams, real_redis_client):
        """Test real event publishing and consuming through Redis streams."""
        # Create test event
        test_event = CoordinationEvent(
            event_id="real_test_event",
            timestamp=datetime.now(),
            event_type=CoordinationEventType.TASK_COMPLETED,
            source_component="integration_test",
            event_data={"test_key": "test_value", "completion_time": 150}
        )

        # Publish event
        publish_success = await observatory_streams.publish_event(test_event)
        assert publish_success is True

        # Consume event
        consumed_events = []
        async for event in observatory_streams.consume_events():
            consumed_events.append(event)
            if len(consumed_events) >= 1:
                break

        assert len(consumed_events) == 1
        consumed_event = consumed_events[0]

        assert consumed_event.event_id == "real_test_event"
        assert consumed_event.event_type == CoordinationEventType.TASK_COMPLETED
        assert consumed_event.source_component == "integration_test"
        assert consumed_event.event_data["test_key"] == "test_value"

    @pytest.mark.asyncio
    async def test_cross_system_event_propagation(self, observatory_streams, real_redis_client):
        """Test event propagation across multiple simulated Beast Mode systems."""
        # Simulate events from different Beast Mode components
        beast_mode_events = [
            CoordinationEvent(
                event_id="task_queue_event",
                event_type=CoordinationEventType.TASK_STARTED,
                source_component="task_queue_manager",
                event_data={"task_id": "cross_system_task", "priority": "high"}
            ),
            CoordinationEvent(
                event_id="pdca_event",
                event_type=CoordinationEventType.COORDINATION_INITIATED,
                source_component="pdca_orchestrator",
                event_data={"coordination_id": "cross_coord_123", "participants": ["node_a", "node_b"]}
            ),
            CoordinationEvent(
                event_id="assessment_event",
                event_type=CoordinationEventType.ASSESSMENT_COMPLETED,
                source_component="readiness_assessor",
                event_data={"assessment_id": "cross_assessment", "score": 0.92}
            )
        ]

        # Publish all events
        publish_tasks = [
            observatory_streams.publish_event(event) for event in beast_mode_events
        ]
        publish_results = await asyncio.gather(*publish_tasks)

        # All publishes should succeed
        assert all(publish_results)

        # Consume all events
        consumed_events = []
        start_time = asyncio.get_event_loop().time()

        async for event in observatory_streams.consume_events():
            consumed_events.append(event)
            if len(consumed_events) >= 3:
                break
            # Safety timeout
            if asyncio.get_event_loop().time() - start_time > 5:
                break

        assert len(consumed_events) == 3

        # Verify all expected components are represented
        source_components = {event.source_component for event in consumed_events}
        expected_components = {"task_queue_manager", "pdca_orchestrator", "readiness_assessor"}
        assert source_components == expected_components

    @pytest.mark.asyncio
    async def test_high_volume_coordination_performance(self, observatory_streams, real_redis_client):
        """Test high-volume event coordination performance."""
        event_count = 500
        start_time = time.time()

        # Generate high-volume events
        events = []
        for i in range(event_count):
            event = CoordinationEvent(
                event_id=f"volume_test_event_{i}",
                event_type=CoordinationEventType.API_CALL_SUCCESS,
                source_component="performance_test",
                event_data={"sequence": i, "batch": "high_volume_test"}
            )
            events.append(event)

        # Publish events concurrently
        publish_tasks = [observatory_streams.publish_event(event) for event in events]
        publish_results = await asyncio.gather(*publish_tasks)

        publish_time = time.time() - start_time

        # All publishes should succeed
        assert all(publish_results)

        # Performance assertion: should publish 500 events in reasonable time
        assert publish_time < 10.0  # Less than 10 seconds for 500 events

        # Verify publish rate
        publish_rate = event_count / publish_time
        assert publish_rate > 25  # At least 25 events per second

        print(f"Published {event_count} events in {publish_time:.2f}s ({publish_rate:.1f} events/sec)")

    @pytest.mark.asyncio
    async def test_consumer_group_coordination(self, test_redis_config, real_redis_client):
        """Test coordination with multiple consumer groups."""
        # Create multiple consumer instances
        consumer_1 = ObservatoryRedisStreams(test_redis_config)
        consumer_2 = ObservatoryRedisStreams(test_redis_config)

        with patch('redis.asyncio.from_url', return_value=real_redis_client):
            await consumer_1.initialize()
            await consumer_2.initialize()

            try:
                # Publish test events
                test_events = []
                for i in range(10):
                    event = CoordinationEvent(
                        event_id=f"consumer_group_event_{i}",
                        event_type=CoordinationEventType.COORDINATION_MILESTONE,
                        source_component="consumer_group_test",
                        event_data={"event_number": i}
                    )
                    test_events.append(event)

                # Publish all events
                for event in test_events:
                    await consumer_1.publish_event(event)

                # Consume with multiple consumers (they should share the workload)
                consumer_1_events = []
                consumer_2_events = []

                async def consume_with_timeout(consumer, event_list, max_events=5):
                    start_time = asyncio.get_event_loop().time()
                    async for event in consumer.consume_events():
                        event_list.append(event)
                        if len(event_list) >= max_events or asyncio.get_event_loop().time() - start_time > 3:
                            break

                # Run both consumers concurrently
                await asyncio.gather(
                    consume_with_timeout(consumer_1, consumer_1_events),
                    consume_with_timeout(consumer_2, consumer_2_events)
                )

                # Verify events were distributed across consumers
                total_consumed = len(consumer_1_events) + len(consumer_2_events)
                assert total_consumed <= 10  # Should not exceed published events
                assert total_consumed > 0   # At least some events should be consumed

                # Verify no duplicate consumption (each event consumed once)
                all_consumed_ids = [e.event_id for e in consumer_1_events + consumer_2_events]
                assert len(all_consumed_ids) == len(set(all_consumed_ids))  # No duplicates

            finally:
                await consumer_1.close()
                await consumer_2.close()

    @pytest.mark.asyncio
    async def test_stream_persistence_and_recovery(self, observatory_streams, real_redis_client):
        """Test stream persistence and recovery scenarios."""
        # Publish events
        persistent_events = []
        for i in range(5):
            event = CoordinationEvent(
                event_id=f"persistent_event_{i}",
                event_type=CoordinationEventType.SYSTEM_STATUS_UPDATE,
                source_component="persistence_test",
                event_data={"persistence_test": True, "event_index": i}
            )
            persistent_events.append(event)
            await observatory_streams.publish_event(event)

        # Verify stream info
        stream_info = await observatory_streams.get_stream_info()
        assert stream_info["length"] >= 5

        # Simulate consumer disconnect and reconnect
        await observatory_streams.close()

        # Reconnect with new instance
        new_streams = ObservatoryRedisStreams(observatory_streams._config)
        with patch('redis.asyncio.from_url', return_value=real_redis_client):
            await new_streams.initialize()

            try:
                # Should be able to consume persisted events
                recovered_events = []
                start_time = asyncio.get_event_loop().time()

                async for event in new_streams.consume_events():
                    recovered_events.append(event)
                    if len(recovered_events) >= 5 or asyncio.get_event_loop().time() - start_time > 3:
                        break

                # Verify recovery
                assert len(recovered_events) > 0

                # Check that recovered events are from our test
                test_events = [e for e in recovered_events if e.source_component == "persistence_test"]
                assert len(test_events) > 0

            finally:
                await new_streams.close()


class TestDistributedStateCoordination:
    """Test distributed state coordination across Beast Mode systems."""

    @pytest.fixture
    async def multi_node_setup(self, test_redis_config, real_redis_client):
        """Setup multiple simulated Beast Mode nodes."""
        nodes = {}

        for node_id in ["node_a", "node_b", "node_c"]:
            config = RedisConfig(
                host=test_redis_config.host,
                port=test_redis_config.port,
                stream_name=f"node_{node_id}_stream",
                connection_pool_size=3
            )

            streams = ObservatoryRedisStreams(config)
            with patch('redis.asyncio.from_url', return_value=real_redis_client):
                await streams.initialize()

            nodes[node_id] = streams

        yield nodes

        # Cleanup
        for streams in nodes.values():
            await streams.close()

    @pytest.mark.asyncio
    async def test_distributed_task_coordination(self, multi_node_setup, real_redis_client):
        """Test coordination of distributed tasks across nodes."""
        nodes = multi_node_setup

        # Simulate distributed task execution
        distributed_task_id = "distributed_task_123"

        # Node A starts the task
        task_start_event = CoordinationEvent(
            event_id=f"{distributed_task_id}_start",
            event_type=CoordinationEventType.TASK_STARTED,
            source_component="node_a_task_manager",
            event_data={
                "distributed_task_id": distributed_task_id,
                "node": "node_a",
                "subtasks": ["subtask_1", "subtask_2", "subtask_3"]
            }
        )
        await nodes["node_a"].publish_event(task_start_event)

        # Nodes B and C coordinate to handle subtasks
        coordination_events = [
            CoordinationEvent(
                event_id=f"{distributed_task_id}_coord_b",
                event_type=CoordinationEventType.COORDINATION_INITIATED,
                source_component="node_b_coordinator",
                event_data={
                    "distributed_task_id": distributed_task_id,
                    "node": "node_b",
                    "assigned_subtask": "subtask_1"
                }
            ),
            CoordinationEvent(
                event_id=f"{distributed_task_id}_coord_c",
                event_type=CoordinationEventType.COORDINATION_INITIATED,
                source_component="node_c_coordinator",
                event_data={
                    "distributed_task_id": distributed_task_id,
                    "node": "node_c",
                    "assigned_subtask": "subtask_2"
                }
            )
        ]

        for event in coordination_events:
            if "node_b" in event.source_component:
                await nodes["node_b"].publish_event(event)
            else:
                await nodes["node_c"].publish_event(event)

        # Node A completes coordination
        task_complete_event = CoordinationEvent(
            event_id=f"{distributed_task_id}_complete",
            event_type=CoordinationEventType.TASK_COMPLETED,
            source_component="node_a_task_manager",
            event_data={
                "distributed_task_id": distributed_task_id,
                "result": "success",
                "coordinated_nodes": ["node_b", "node_c"]
            }
        )
        await nodes["node_a"].publish_event(task_complete_event)

        # Verify all events were published successfully by checking stream info
        for node_id, streams in nodes.items():
            stream_info = await streams.get_stream_info()
            assert stream_info["length"] > 0

    @pytest.mark.asyncio
    async def test_cross_node_event_propagation(self, multi_node_setup, real_redis_client):
        """Test event propagation and coordination across multiple nodes."""
        nodes = multi_node_setup

        # Create a coordination scenario involving all nodes
        coordination_id = "multi_node_coordination_456"

        # Each node publishes coordination events
        node_events = {
            "node_a": CoordinationEvent(
                event_type=CoordinationEventType.COORDINATION_INITIATED,
                source_component="node_a_coordinator",
                event_data={"coordination_id": coordination_id, "role": "leader"}
            ),
            "node_b": CoordinationEvent(
                event_type=CoordinationEventType.COORDINATION_ACKNOWLEDGED,
                source_component="node_b_coordinator",
                event_data={"coordination_id": coordination_id, "role": "follower"}
            ),
            "node_c": CoordinationEvent(
                event_type=CoordinationEventType.COORDINATION_ACKNOWLEDGED,
                source_component="node_c_coordinator",
                event_data={"coordination_id": coordination_id, "role": "follower"}
            )
        }

        # Publish events from their respective nodes
        publish_tasks = []
        for node_id, event in node_events.items():
            publish_tasks.append(nodes[node_id].publish_event(event))

        publish_results = await asyncio.gather(*publish_tasks)
        assert all(publish_results)

        # Each node should be able to consume from its own stream
        # (In a real scenario, nodes would cross-subscribe to coordinate)
        for node_id, streams in nodes.items():
            stream_info = await streams.get_stream_info()
            assert stream_info["length"] >= 1


class TestErrorRecoveryAndResilience:
    """Test error recovery and resilience in distributed coordination."""

    @pytest.mark.asyncio
    async def test_network_partition_recovery(self, observatory_streams, real_redis_client):
        """Test recovery from simulated network partition."""
        # Publish events before partition
        pre_partition_events = []
        for i in range(3):
            event = CoordinationEvent(
                event_id=f"pre_partition_{i}",
                event_type=CoordinationEventType.SYSTEM_STATUS_UPDATE,
                source_component="partition_test",
                event_data={"phase": "pre_partition", "sequence": i}
            )
            pre_partition_events.append(event)
            await observatory_streams.publish_event(event)

        # Simulate network partition by closing connection
        await observatory_streams.close()

        # Wait briefly to simulate partition duration
        await asyncio.sleep(0.1)

        # Reconnect (simulate partition recovery)
        with patch('redis.asyncio.from_url', return_value=real_redis_client):
            recovery_success = await observatory_streams.initialize()
            assert recovery_success is True

            # Publish post-recovery events
            post_recovery_events = []
            for i in range(3):
                event = CoordinationEvent(
                    event_id=f"post_recovery_{i}",
                    event_type=CoordinationEventType.SYSTEM_STATUS_UPDATE,
                    source_component="partition_test",
                    event_data={"phase": "post_recovery", "sequence": i}
                )
                post_recovery_events.append(event)
                await observatory_streams.publish_event(event)

            # Verify stream continuity
            stream_info = await observatory_streams.get_stream_info()
            assert stream_info["length"] >= 6  # Pre + post events

    @pytest.mark.asyncio
    async def test_consumer_failure_and_recovery(self, test_redis_config, real_redis_client):
        """Test consumer failure and recovery scenarios."""
        # Create primary consumer
        primary_consumer = ObservatoryRedisStreams(test_redis_config)

        with patch('redis.asyncio.from_url', return_value=real_redis_client):
            await primary_consumer.initialize()

            try:
                # Publish some events
                for i in range(5):
                    event = CoordinationEvent(
                        event_id=f"consumer_recovery_test_{i}",
                        event_type=CoordinationEventType.API_CALL_SUCCESS,
                        source_component="recovery_test",
                        event_data={"recovery_test": True, "sequence": i}
                    )
                    await primary_consumer.publish_event(event)

                # Start consuming
                consumed_before_failure = []
                count = 0
                async for event in primary_consumer.consume_events():
                    consumed_before_failure.append(event)
                    count += 1
                    if count >= 2:  # Consume some events before simulated failure
                        break

                # Simulate consumer failure
                await primary_consumer.close()

                # Create recovery consumer (new consumer in same group)
                recovery_consumer = ObservatoryRedisStreams(test_redis_config)
                await recovery_consumer.initialize()

                try:
                    # Recovery consumer should be able to continue from where primary left off
                    consumed_after_recovery = []
                    start_time = asyncio.get_event_loop().time()

                    async for event in recovery_consumer.consume_events():
                        consumed_after_recovery.append(event)
                        if len(consumed_after_recovery) >= 3 or asyncio.get_event_loop().time() - start_time > 3:
                            break

                    # Verify recovery
                    total_consumed = len(consumed_before_failure) + len(consumed_after_recovery)
                    assert total_consumed <= 5  # Should not exceed published events
                    assert len(consumed_after_recovery) > 0  # Should consume some events after recovery

                finally:
                    await recovery_consumer.close()

            finally:
                await primary_consumer.close()


class TestStreamManagementAndCleanup:
    """Test stream management and cleanup operations."""

    @pytest.mark.asyncio
    async def test_stream_cleanup_operations(self, observatory_streams, real_redis_client):
        """Test stream cleanup and maintenance operations."""
        # Publish many events to test cleanup
        cleanup_events = []
        for i in range(20):
            event = CoordinationEvent(
                event_id=f"cleanup_test_{i}",
                event_type=CoordinationEventType.METRICS_COLLECTED,
                source_component="cleanup_test",
                event_data={"cleanup_test": True, "sequence": i}
            )
            cleanup_events.append(event)
            await observatory_streams.publish_event(event)

        # Verify events were added
        stream_info_before = await observatory_streams.get_stream_info()
        assert stream_info_before["length"] >= 20

        # Perform cleanup (limit to 10 events)
        cleanup_success = await observatory_streams.cleanup_old_messages(max_length=10)
        assert cleanup_success is True

        # Verify cleanup occurred
        stream_info_after = await observatory_streams.get_stream_info()
        assert stream_info_after["length"] <= 10

    @pytest.mark.asyncio
    async def test_stream_info_accuracy(self, observatory_streams, real_redis_client):
        """Test accuracy of stream information reporting."""
        # Get initial stream info
        initial_info = await observatory_streams.get_stream_info()
        initial_length = initial_info["length"]

        # Add known number of events
        test_event_count = 7
        for i in range(test_event_count):
            event = CoordinationEvent(
                event_id=f"info_test_{i}",
                event_type=CoordinationEventType.ACHIEVEMENT_UNLOCKED,
                source_component="info_test",
                event_data={"info_test": True, "index": i}
            )
            await observatory_streams.publish_event(event)

        # Verify stream info reflects the additions
        updated_info = await observatory_streams.get_stream_info()
        assert updated_info["length"] >= initial_length + test_event_count

        # Verify other stream info fields
        assert "first_entry" in updated_info
        assert "last_entry" in updated_info
        assert "consumer_groups" in updated_info