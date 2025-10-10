"""
Comprehensive unit tests for the Observatory Redis Streams system.

Tests Redis stream management, event publishing/consuming, and error handling
for real-time metrics distribution across Observatory components.
"""

import asyncio
import json
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from typing import AsyncGenerator

from src.beast_mode.observatory.redis_streams import ObservatoryRedisStreams
from src.beast_mode.observatory.models import (
    CoordinationEvent,
    CoordinationEventType,
    RedisConfig
)


@pytest.fixture
def redis_config():
    """Sample Redis configuration."""
    return RedisConfig(
        host='localhost',
        port=6379,
        password='test-password',
        ssl=False,
        connection_pool_size=10,
        stream_name='test_observatory_metrics'
    )


@pytest.fixture
def mock_redis_client():
    """Mock Redis client with all necessary methods."""
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    mock_client.xgroup_create = AsyncMock()
    mock_client.xadd = AsyncMock(return_value='1234567890-0')
    mock_client.xreadgroup = AsyncMock(return_value=[])
    mock_client.xack = AsyncMock()
    mock_client.xinfo_stream = AsyncMock(return_value={'length': 0})
    mock_client.xtrim = AsyncMock()
    mock_client.close = AsyncMock()
    return mock_client


@pytest.fixture
def sample_coordination_event():
    """Sample coordination event for testing."""
    return CoordinationEvent(
        event_id='test-event-123',
        timestamp=datetime.now(),
        event_type=CoordinationEventType.COMPONENT_STARTED,
        source_component='test_component',
        event_data={'key': 'value', 'number': 42},
        correlation_id='corr-456',
        user_id='user-789'
    )


@pytest.fixture
async def redis_streams(redis_config, mock_redis_client):
    """Create ObservatoryRedisStreams instance with mocked Redis."""
    streams = ObservatoryRedisStreams(redis_config)

    with patch('redis.asyncio.from_url', return_value=mock_redis_client):
        await streams.initialize()
        yield streams
        await streams.close()


class TestObservatoryRedisStreamsInitialization:
    """Test ObservatoryRedisStreams initialization."""

    def test_redis_streams_creation(self, redis_config):
        """Test ObservatoryRedisStreams creation."""
        streams = ObservatoryRedisStreams(redis_config)

        assert streams._config == redis_config
        assert streams._stream_name == redis_config.stream_name
        assert streams._consumer_group == "observatory_consumers"
        assert streams._consumer_name.startswith("observatory_")
        assert streams._redis_client is None

    @pytest.mark.asyncio
    async def test_initialize_success(self, redis_config, mock_redis_client):
        """Test successful Redis streams initialization."""
        streams = ObservatoryRedisStreams(redis_config)

        with patch('redis.asyncio.from_url', return_value=mock_redis_client):
            result = await streams.initialize()

            assert result is True
            mock_redis_client.ping.assert_called_once()
            mock_redis_client.xgroup_create.assert_called_once_with(
                redis_config.stream_name,
                "observatory_consumers",
                id='0',
                mkstream=True
            )

    @pytest.mark.asyncio
    async def test_initialize_consumer_group_exists(self, redis_config, mock_redis_client):
        """Test initialization when consumer group already exists."""
        streams = ObservatoryRedisStreams(redis_config)

        # Mock BUSYGROUP error (group exists)
        import redis as redis_lib
        mock_redis_client.xgroup_create.side_effect = redis_lib.ResponseError("BUSYGROUP Consumer Group name already exists")

        with patch('redis.asyncio.from_url', return_value=mock_redis_client):
            result = await streams.initialize()

            assert result is True
            mock_redis_client.ping.assert_called_once()
            mock_redis_client.xgroup_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_redis_connection_failure(self, redis_config):
        """Test initialization with Redis connection failure."""
        streams = ObservatoryRedisStreams(redis_config)

        mock_failing_client = AsyncMock()
        mock_failing_client.ping.side_effect = Exception("Connection failed")

        with patch('redis.asyncio.from_url', return_value=mock_failing_client):
            result = await streams.initialize()

            assert result is False

    @pytest.mark.asyncio
    async def test_initialize_consumer_group_error(self, redis_config, mock_redis_client):
        """Test initialization with consumer group creation error."""
        streams = ObservatoryRedisStreams(redis_config)

        import redis as redis_lib
        mock_redis_client.xgroup_create.side_effect = redis_lib.ResponseError("Some other error")

        with patch('redis.asyncio.from_url', return_value=mock_redis_client):
            result = await streams.initialize()

            assert result is False


class TestEventPublishing:
    """Test event publishing functionality."""

    @pytest.mark.asyncio
    async def test_publish_event_success(self, redis_streams, sample_coordination_event):
        """Test successful event publishing."""
        result = await redis_streams.publish_event(sample_coordination_event)

        assert result is True
        redis_streams._redis_client.xadd.assert_called_once()

        # Check the call arguments
        call_args = redis_streams._redis_client.xadd.call_args
        stream_name = call_args[0][0]
        event_data = call_args[0][1]

        assert stream_name == 'test_observatory_metrics'
        assert event_data['event_id'] == 'test-event-123'
        assert event_data['event_type'] == 'COMPONENT_STARTED'
        assert event_data['source_component'] == 'test_component'
        assert event_data['correlation_id'] == 'corr-456'
        assert event_data['user_id'] == 'user-789'

        # Check that event_data is JSON serialized
        parsed_data = json.loads(event_data['event_data'])
        assert parsed_data == {'key': 'value', 'number': 42}

    @pytest.mark.asyncio
    async def test_publish_event_with_empty_optional_fields(self, redis_streams):
        """Test publishing event with empty optional fields."""
        event = CoordinationEvent(
            event_id='minimal-event',
            timestamp=datetime.now(),
            event_type=CoordinationEventType.API_CALL_SUCCESS,
            source_component='minimal_component',
            event_data={},
            correlation_id=None,
            user_id=None
        )

        result = await redis_streams.publish_event(event)

        assert result is True

        call_args = redis_streams._redis_client.xadd.call_args
        event_data = call_args[0][1]

        assert event_data['correlation_id'] == ''
        assert event_data['user_id'] == ''
        assert event_data['event_data'] == '{}'

    @pytest.mark.asyncio
    async def test_publish_event_redis_not_initialized(self, redis_config, sample_coordination_event):
        """Test publishing when Redis client is not initialized."""
        streams = ObservatoryRedisStreams(redis_config)
        # Don't call initialize()

        result = await streams.publish_event(sample_coordination_event)

        assert result is False

    @pytest.mark.asyncio
    async def test_publish_event_redis_error(self, redis_streams, sample_coordination_event):
        """Test publishing event with Redis error."""
        redis_streams._redis_client.xadd.side_effect = Exception("Redis error")

        result = await redis_streams.publish_event(sample_coordination_event)

        assert result is False

    @pytest.mark.asyncio
    async def test_publish_event_complex_data(self, redis_streams):
        """Test publishing event with complex data structures."""
        complex_event = CoordinationEvent(
            event_id='complex-event',
            timestamp=datetime.now(),
            event_type=CoordinationEventType.METRICS_COLLECTED,
            source_component='complex_component',
            event_data={
                'nested': {
                    'dict': {'value': 123}
                },
                'list': [1, 2, 3, {'key': 'value'}],
                'float': 3.14159,
                'boolean': True,
                'null_value': None
            }
        )

        result = await redis_streams.publish_event(complex_event)

        assert result is True

        call_args = redis_streams._redis_client.xadd.call_args
        event_data = call_args[0][1]

        # Verify complex data is properly JSON serialized
        parsed_data = json.loads(event_data['event_data'])
        assert parsed_data['nested']['dict']['value'] == 123
        assert parsed_data['list'] == [1, 2, 3, {'key': 'value'}]
        assert parsed_data['float'] == 3.14159
        assert parsed_data['boolean'] is True
        assert parsed_data['null_value'] is None


class TestEventConsuming:
    """Test event consuming functionality."""

    @pytest.mark.asyncio
    async def test_consume_events_single_event(self, redis_streams):
        """Test consuming a single event from the stream."""
        # Mock Redis response with one message
        mock_message = ('1234567890-0', {
            'event_id': 'consumed-event',
            'timestamp': datetime.now().isoformat(),
            'event_type': 'COMPONENT_STARTED',
            'source_component': 'test_consumer',
            'event_data': '{"test": "data"}',
            'correlation_id': 'test-corr',
            'user_id': 'test-user'
        })

        redis_streams._redis_client.xreadgroup.return_value = [
            ('test_observatory_metrics', [mock_message])
        ]

        # Consume events (just get the first one)
        events = []
        async for event in redis_streams.consume_events():
            events.append(event)
            break  # Just get the first event for testing

        assert len(events) == 1
        event = events[0]

        assert event.event_id == 'consumed-event'
        assert event.event_type == CoordinationEventType.COMPONENT_STARTED
        assert event.source_component == 'test_consumer'
        assert event.event_data == {'test': 'data'}
        assert event.correlation_id == 'test-corr'
        assert event.user_id == 'test-user'

        # Verify message was acknowledged
        redis_streams._redis_client.xack.assert_called_with(
            'test_observatory_metrics',
            'observatory_consumers',
            '1234567890-0'
        )

    @pytest.mark.asyncio
    async def test_consume_events_multiple_messages(self, redis_streams):
        """Test consuming multiple events from the stream."""
        # Mock Redis response with multiple messages
        mock_messages = [
            ('1234567890-0', {
                'event_id': 'event-1',
                'timestamp': datetime.now().isoformat(),
                'event_type': 'COMPONENT_STARTED',
                'source_component': 'comp1',
                'event_data': '{}',
                'correlation_id': '',
                'user_id': ''
            }),
            ('1234567890-1', {
                'event_id': 'event-2',
                'timestamp': datetime.now().isoformat(),
                'event_type': 'COMPONENT_STOPPED',
                'source_component': 'comp2',
                'event_data': '{}',
                'correlation_id': '',
                'user_id': ''
            })
        ]

        redis_streams._redis_client.xreadgroup.return_value = [
            ('test_observatory_metrics', mock_messages)
        ]

        # Consume events
        events = []
        async for event in redis_streams.consume_events():
            events.append(event)
            if len(events) >= 2:
                break

        assert len(events) == 2
        assert events[0].event_id == 'event-1'
        assert events[0].event_type == CoordinationEventType.COMPONENT_STARTED
        assert events[1].event_id == 'event-2'
        assert events[1].event_type == CoordinationEventType.COMPONENT_STOPPED

        # Verify both messages were acknowledged
        assert redis_streams._redis_client.xack.call_count == 2

    @pytest.mark.asyncio
    async def test_consume_events_redis_not_initialized(self, redis_config):
        """Test consuming events when Redis client is not initialized."""
        streams = ObservatoryRedisStreams(redis_config)
        # Don't call initialize()

        events = []
        async for event in streams.consume_events():
            events.append(event)
            break  # Should not yield any events

        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_consume_events_deserialization_error(self, redis_streams):
        """Test handling of event deserialization errors."""
        # Mock Redis response with invalid message data
        mock_message = ('1234567890-0', {
            'event_id': 'invalid-event',
            'timestamp': 'invalid-timestamp',  # Invalid ISO format
            'event_type': 'INVALID_TYPE',  # Invalid enum value
            'source_component': 'test_consumer',
            'event_data': 'invalid-json',  # Invalid JSON
            'correlation_id': '',
            'user_id': ''
        })

        redis_streams._redis_client.xreadgroup.return_value = [
            ('test_observatory_metrics', [mock_message])
        ]

        # Consume events - should handle error gracefully
        events = []
        async for event in redis_streams.consume_events():
            events.append(event)
            break

        # Should not yield any events due to deserialization error
        assert len(events) == 0

        # Message should still be acknowledged (to prevent reprocessing)
        redis_streams._redis_client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_events_no_consumer_group_error(self, redis_streams):
        """Test handling of missing consumer group error."""
        import redis as redis_lib

        # First call fails with NOGROUP, second succeeds
        redis_streams._redis_client.xreadgroup.side_effect = [
            redis_lib.ResponseError("NOGROUP No such consumer group"),
            [('test_observatory_metrics', [])]
        ]

        # Mock initialize to succeed on retry
        with patch.object(redis_streams, 'initialize', return_value=True):
            events = []
            count = 0
            async for event in redis_streams.consume_events():
                events.append(event)
                count += 1
                if count > 2:  # Prevent infinite loop
                    break

        # Should recover from NOGROUP error
        assert redis_streams._redis_client.xreadgroup.call_count >= 2

    @pytest.mark.asyncio
    async def test_consume_events_generic_redis_error(self, redis_streams):
        """Test handling of generic Redis errors."""
        redis_streams._redis_client.xreadgroup.side_effect = Exception("Generic Redis error")

        # Should handle error gracefully and continue
        events = []
        start_time = asyncio.get_event_loop().time()

        async for event in redis_streams.consume_events():
            events.append(event)
            # Break after a short time to avoid infinite loop in test
            if asyncio.get_event_loop().time() - start_time > 0.1:
                break

        # Should not yield events but also not crash
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_consume_events_cancellation(self, redis_streams):
        """Test proper handling of task cancellation."""
        redis_streams._redis_client.xreadgroup.return_value = [
            ('test_observatory_metrics', [])
        ]

        # Start consuming and then cancel
        consume_task = asyncio.create_task(
            redis_streams.consume_events().__anext__()
        )

        # Give it a moment to start
        await asyncio.sleep(0.001)

        # Cancel the task
        consume_task.cancel()

        try:
            await consume_task
        except asyncio.CancelledError:
            pass  # Expected


class TestEventDeserialization:
    """Test event deserialization functionality."""

    def test_deserialize_event_complete(self, redis_streams):
        """Test deserializing a complete event."""
        fields = {
            'event_id': 'test-deserialize',
            'timestamp': '2024-01-15T10:30:45.123456',
            'event_type': 'METRICS_COLLECTED',
            'source_component': 'deserialize_component',
            'event_data': '{"metric": "value", "count": 42}',
            'correlation_id': 'corr-deserialize',
            'user_id': 'user-deserialize'
        }

        event = redis_streams._deserialize_event(fields)

        assert event is not None
        assert event.event_id == 'test-deserialize'
        assert event.timestamp == datetime.fromisoformat('2024-01-15T10:30:45.123456')
        assert event.event_type == CoordinationEventType.METRICS_COLLECTED
        assert event.source_component == 'deserialize_component'
        assert event.event_data == {'metric': 'value', 'count': 42}
        assert event.correlation_id == 'corr-deserialize'
        assert event.user_id == 'user-deserialize'

    def test_deserialize_event_empty_optional_fields(self, redis_streams):
        """Test deserializing event with empty optional fields."""
        fields = {
            'event_id': 'test-minimal',
            'timestamp': '2024-01-15T10:30:45',
            'event_type': 'API_CALL_SUCCESS',
            'source_component': 'minimal_component',
            'event_data': '',  # Empty JSON
            'correlation_id': '',  # Empty string
            'user_id': ''  # Empty string
        }

        event = redis_streams._deserialize_event(fields)

        assert event is not None
        assert event.event_data == {}
        assert event.correlation_id is None
        assert event.user_id is None

    def test_deserialize_event_invalid_timestamp(self, redis_streams):
        """Test deserializing event with invalid timestamp."""
        fields = {
            'event_id': 'test-invalid-time',
            'timestamp': 'not-a-timestamp',
            'event_type': 'COMPONENT_STARTED',
            'source_component': 'test_component',
            'event_data': '{}',
            'correlation_id': '',
            'user_id': ''
        }

        event = redis_streams._deserialize_event(fields)

        assert event is None  # Should fail gracefully

    def test_deserialize_event_invalid_event_type(self, redis_streams):
        """Test deserializing event with invalid event type."""
        fields = {
            'event_id': 'test-invalid-type',
            'timestamp': '2024-01-15T10:30:45',
            'event_type': 'INVALID_EVENT_TYPE',
            'source_component': 'test_component',
            'event_data': '{}',
            'correlation_id': '',
            'user_id': ''
        }

        event = redis_streams._deserialize_event(fields)

        assert event is None  # Should fail gracefully

    def test_deserialize_event_invalid_json_data(self, redis_streams):
        """Test deserializing event with invalid JSON data."""
        fields = {
            'event_id': 'test-invalid-json',
            'timestamp': '2024-01-15T10:30:45',
            'event_type': 'METRICS_COLLECTED',
            'source_component': 'test_component',
            'event_data': 'invalid-json-string',
            'correlation_id': '',
            'user_id': ''
        }

        event = redis_streams._deserialize_event(fields)

        assert event is None  # Should fail gracefully


class TestStreamManagement:
    """Test stream management functionality."""

    @pytest.mark.asyncio
    async def test_get_stream_info_success(self, redis_streams):
        """Test getting stream information."""
        mock_stream_info = {
            'length': 42,
            'first-entry': ['1234567890-0', ['field1', 'value1']],
            'last-entry': ['1234567890-41', ['field2', 'value2']],
            'groups': 2
        }

        redis_streams._redis_client.xinfo_stream.return_value = mock_stream_info

        info = await redis_streams.get_stream_info()

        assert info['length'] == 42
        assert info['first_entry'] == ['1234567890-0', ['field1', 'value1']]
        assert info['last_entry'] == ['1234567890-41', ['field2', 'value2']]
        assert info['consumer_groups'] == 2

        redis_streams._redis_client.xinfo_stream.assert_called_once_with('test_observatory_metrics')

    @pytest.mark.asyncio
    async def test_get_stream_info_redis_not_initialized(self, redis_config):
        """Test getting stream info when Redis is not initialized."""
        streams = ObservatoryRedisStreams(redis_config)

        info = await streams.get_stream_info()

        assert info == {}

    @pytest.mark.asyncio
    async def test_get_stream_info_redis_error(self, redis_streams):
        """Test getting stream info with Redis error."""
        redis_streams._redis_client.xinfo_stream.side_effect = Exception("Redis error")

        info = await redis_streams.get_stream_info()

        assert info == {}

    @pytest.mark.asyncio
    async def test_cleanup_old_messages_success(self, redis_streams):
        """Test successful cleanup of old messages."""
        result = await redis_streams.cleanup_old_messages(max_length=5000)

        assert result is True
        redis_streams._redis_client.xtrim.assert_called_once_with(
            'test_observatory_metrics',
            maxlen=5000,
            approximate=True
        )

    @pytest.mark.asyncio
    async def test_cleanup_old_messages_default_length(self, redis_streams):
        """Test cleanup with default max length."""
        result = await redis_streams.cleanup_old_messages()

        assert result is True
        redis_streams._redis_client.xtrim.assert_called_once_with(
            'test_observatory_metrics',
            maxlen=10000,
            approximate=True
        )

    @pytest.mark.asyncio
    async def test_cleanup_old_messages_redis_not_initialized(self, redis_config):
        """Test cleanup when Redis is not initialized."""
        streams = ObservatoryRedisStreams(redis_config)

        result = await streams.cleanup_old_messages()

        assert result is False

    @pytest.mark.asyncio
    async def test_cleanup_old_messages_redis_error(self, redis_streams):
        """Test cleanup with Redis error."""
        redis_streams._redis_client.xtrim.side_effect = Exception("Redis error")

        result = await redis_streams.cleanup_old_messages()

        assert result is False


class TestConnectionManagement:
    """Test connection management functionality."""

    @pytest.mark.asyncio
    async def test_close_connection(self, redis_streams):
        """Test closing Redis connection."""
        await redis_streams.close()

        redis_streams._redis_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_connection_no_client(self, redis_config):
        """Test closing when no Redis client exists."""
        streams = ObservatoryRedisStreams(redis_config)

        # Should not raise exception
        await streams.close()


class TestIntegrationScenarios:
    """Test integration scenarios and complex workflows."""

    @pytest.mark.asyncio
    async def test_publish_consume_roundtrip(self, redis_config):
        """Test complete publish-consume roundtrip scenario."""
        # Create separate instances for publisher and consumer
        publisher = ObservatoryRedisStreams(redis_config)
        consumer = ObservatoryRedisStreams(redis_config)

        # Mock Redis client for both
        mock_pub_client = AsyncMock()
        mock_pub_client.ping.return_value = True
        mock_pub_client.xgroup_create.return_value = None
        mock_pub_client.xadd.return_value = '1234567890-0'
        mock_pub_client.close = AsyncMock()

        mock_con_client = AsyncMock()
        mock_con_client.ping.return_value = True
        mock_con_client.xgroup_create.return_value = None
        mock_con_client.close = AsyncMock()

        # Test event
        test_event = CoordinationEvent(
            event_id='roundtrip-test',
            timestamp=datetime.now(),
            event_type=CoordinationEventType.METRICS_COLLECTED,
            source_component='roundtrip_component',
            event_data={'test': 'roundtrip'},
            correlation_id='roundtrip-corr'
        )

        try:
            # Initialize both
            with patch('redis.asyncio.from_url', return_value=mock_pub_client):
                await publisher.initialize()

            with patch('redis.asyncio.from_url', return_value=mock_con_client):
                await consumer.initialize()

            # Publish event
            pub_result = await publisher.publish_event(test_event)
            assert pub_result is True

            # Verify publish call
            mock_pub_client.xadd.assert_called_once()
            call_args = mock_pub_client.xadd.call_args
            published_data = call_args[0][1]

            assert published_data['event_id'] == 'roundtrip-test'
            assert published_data['event_type'] == 'METRICS_COLLECTED'
            assert published_data['correlation_id'] == 'roundtrip-corr'

        finally:
            await publisher.close()
            await consumer.close()

    @pytest.mark.asyncio
    async def test_high_volume_event_publishing(self, redis_streams):
        """Test publishing high volume of events."""
        events = []
        for i in range(100):
            event = CoordinationEvent(
                event_id=f'bulk-event-{i}',
                timestamp=datetime.now(),
                event_type=CoordinationEventType.METRICS_COLLECTED,
                source_component=f'bulk_component_{i % 10}',
                event_data={'index': i, 'batch': 'high_volume'},
                correlation_id=f'bulk-corr-{i}'
            )
            events.append(event)

        # Publish all events
        results = []
        for event in events:
            result = await redis_streams.publish_event(event)
            results.append(result)

        # All should succeed
        assert all(results)
        assert redis_streams._redis_client.xadd.call_count == 100

    @pytest.mark.asyncio
    async def test_concurrent_publish_consume(self, redis_config):
        """Test concurrent publishing and consuming."""
        streams = ObservatoryRedisStreams(redis_config)

        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        mock_client.xgroup_create.return_value = None
        mock_client.xadd.return_value = '1234567890-0'
        mock_client.xreadgroup.return_value = []
        mock_client.close = AsyncMock()

        try:
            with patch('redis.asyncio.from_url', return_value=mock_client):
                await streams.initialize()

            # Create concurrent tasks
            async def publisher_task():
                for i in range(10):
                    event = CoordinationEvent(
                        event_id=f'concurrent-{i}',
                        timestamp=datetime.now(),
                        event_type=CoordinationEventType.COMPONENT_STARTED,
                        source_component='concurrent_component',
                        event_data={'concurrent_index': i}
                    )
                    await streams.publish_event(event)
                    await asyncio.sleep(0.001)  # Small delay

            async def consumer_task():
                count = 0
                async for event in streams.consume_events():
                    count += 1
                    if count >= 5:  # Stop after processing some events
                        break

            # Run tasks concurrently
            publisher = asyncio.create_task(publisher_task())
            consumer = asyncio.create_task(consumer_task())

            # Wait for publisher to complete
            await publisher

            # Cancel consumer after a moment
            await asyncio.sleep(0.01)
            consumer.cancel()

            try:
                await consumer
            except asyncio.CancelledError:
                pass

            # Verify some publishing occurred
            assert mock_client.xadd.call_count > 0

        finally:
            await streams.close()

    @pytest.mark.asyncio
    async def test_error_recovery_scenarios(self, redis_streams):
        """Test various error recovery scenarios."""
        # Test recovery from temporary Redis failures
        redis_streams._redis_client.xadd.side_effect = [
            Exception("Temporary failure"),
            '1234567890-0'  # Success on retry
        ]

        test_event = CoordinationEvent(
            event_id='recovery-test',
            timestamp=datetime.now(),
            event_type=CoordinationEventType.API_CALL_SUCCESS,
            source_component='recovery_component',
            event_data={'recovery': True}
        )

        # First call should fail
        result1 = await redis_streams.publish_event(test_event)
        assert result1 is False

        # Second call should succeed
        result2 = await redis_streams.publish_event(test_event)
        assert result2 is True

        assert redis_streams._redis_client.xadd.call_count == 2