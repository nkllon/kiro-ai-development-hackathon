"""
Comprehensive unit tests for Observatory Metrics Collector

Tests metrics collection, aggregation, storage, and real-time streaming
for production reliability with high-volume scenarios.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
import json

from src.beast_mode.observatory.metrics_collector import (
    MetricsCollector,
    MetricsAggregator,
    MetricsBuffer,
    MetricsStorage,
    RealTimeMetricsStreamer,
    MetricsValidator,
    MetricsCompressor,
    PerformanceMetrics,
)
from src.beast_mode.observatory.models import (
    CoordinationEvent,
    CoordinationEventType,
    CoordinationMetrics,
    LLMMetrics,
    CostMetrics,
    HealthScore,
    ObservatoryConfig,
)


class TestMetricsBuffer:
    """Test suite for MetricsBuffer component."""

    @pytest.fixture
    def buffer(self):
        """Create MetricsBuffer instance for testing."""
        return MetricsBuffer(
            max_size=100,
            flush_interval_seconds=5,
            compression_enabled=True
        )

    @pytest.fixture
    def sample_metrics(self):
        """Create sample coordination metrics."""
        return CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=25,
            api_calls_count=500,
            total_cost=Decimal("25.50"),
            health_score=0.95,
            event_id="test_metric_1"
        )

    def test_buffer_initialization(self, buffer):
        """Test MetricsBuffer initialization."""
        assert buffer is not None
        assert buffer.max_size == 100
        assert buffer.flush_interval_seconds == 5
        assert buffer.compression_enabled is True
        assert len(buffer) == 0

    def test_add_single_metric(self, buffer, sample_metrics):
        """Test adding a single metric to buffer."""
        buffer.add(sample_metrics)

        assert len(buffer) == 1
        assert buffer.is_empty() is False

    def test_add_multiple_metrics(self, buffer, sample_metrics):
        """Test adding multiple metrics to buffer."""
        for i in range(10):
            metric = CoordinationMetrics(
                timestamp=datetime.now() - timedelta(minutes=i),
                active_tasks=50 + i,
                completed_tasks=1000 + i*10,
                failed_tasks=10 + i,
                queue_depth=25 + i,
                api_calls_count=500 + i*5,
                total_cost=Decimal(f"{25.50 + i:.2f}"),
                health_score=0.95 - i*0.01,
                event_id=f"test_metric_{i}"
            )
            buffer.add(metric)

        assert len(buffer) == 10

    def test_buffer_overflow_handling(self, buffer, sample_metrics):
        """Test buffer behavior when max size is exceeded."""
        # Fill buffer beyond max size
        for i in range(150):  # More than max_size of 100
            metric = CoordinationMetrics(
                timestamp=datetime.now() - timedelta(seconds=i),
                active_tasks=50,
                completed_tasks=1000,
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal("25.50"),
                health_score=0.95,
                event_id=f"overflow_metric_{i}"
            )
            buffer.add(metric)

        # Buffer should maintain max_size (oldest items removed)
        assert len(buffer) == 100

    def test_flush_buffer(self, buffer, sample_metrics):
        """Test flushing buffer contents."""
        # Add metrics to buffer
        for i in range(5):
            buffer.add(sample_metrics)

        # Flush buffer
        flushed_metrics = buffer.flush()

        assert len(flushed_metrics) == 5
        assert len(buffer) == 0
        assert buffer.is_empty() is True

    def test_peek_buffer_contents(self, buffer, sample_metrics):
        """Test peeking at buffer contents without flushing."""
        buffer.add(sample_metrics)

        peeked = buffer.peek()
        assert len(peeked) == 1
        assert len(buffer) == 1  # Buffer should not be empty after peek

    @pytest.mark.asyncio
    async def test_auto_flush_on_interval(self, buffer, sample_metrics):
        """Test automatic flush based on time interval."""
        with patch.object(buffer, '_auto_flush_callback') as mock_callback:
            # Add metric and start auto-flush
            buffer.add(sample_metrics)
            await buffer.start_auto_flush()

            # Wait for flush interval
            await asyncio.sleep(buffer.flush_interval_seconds + 0.1)

            # Should have triggered flush
            mock_callback.assert_called()

            await buffer.stop_auto_flush()

    def test_buffer_statistics(self, buffer):
        """Test buffer statistics collection."""
        # Add various metrics
        for i in range(20):
            metric = CoordinationMetrics(
                timestamp=datetime.now() - timedelta(seconds=i),
                active_tasks=50 + i,
                completed_tasks=1000,
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal("25.50"),
                health_score=0.95,
                event_id=f"stats_metric_{i}"
            )
            buffer.add(metric)

        stats = buffer.get_statistics()

        assert stats['current_size'] == 20
        assert stats['total_added'] == 20
        assert stats['total_flushed'] == 0
        assert 'oldest_timestamp' in stats
        assert 'newest_timestamp' in stats


class TestMetricsAggregator:
    """Test suite for MetricsAggregator component."""

    @pytest.fixture
    def aggregator(self):
        """Create MetricsAggregator instance for testing."""
        return MetricsAggregator(
            aggregation_windows=[60, 300, 900],  # 1min, 5min, 15min
            aggregation_functions=['avg', 'sum', 'max', 'min', 'count']
        )

    @pytest.fixture
    def time_series_metrics(self):
        """Create time series metrics for aggregation testing."""
        base_time = datetime.now()
        return [
            CoordinationMetrics(
                timestamp=base_time - timedelta(seconds=i*30),  # Every 30 seconds
                active_tasks=100 + i*5,
                completed_tasks=1000 + i*20,
                failed_tasks=10 + i,
                queue_depth=50 - i*2,
                api_calls_count=500 + i*10,
                total_cost=Decimal(f"{25.00 + i*0.50:.2f}"),
                health_score=0.95 - i*0.01,
                event_id=f"ts_metric_{i}"
            )
            for i in range(30)  # 15 minutes of data
        ]

    def test_aggregator_initialization(self, aggregator):
        """Test MetricsAggregator initialization."""
        assert aggregator is not None
        assert len(aggregator.aggregation_windows) == 3
        assert 'avg' in aggregator.aggregation_functions

    def test_aggregate_single_window(self, aggregator, time_series_metrics):
        """Test aggregation for a single time window."""
        # Aggregate for 5-minute window
        aggregated = aggregator.aggregate_metrics(
            time_series_metrics,
            window_seconds=300
        )

        assert aggregated is not None
        assert 'avg' in aggregated
        assert 'sum' in aggregated
        assert 'max' in aggregated
        assert 'min' in aggregated
        assert 'count' in aggregated

        # Should have aggregated multiple metrics
        assert aggregated['count']['active_tasks'] == len(time_series_metrics)

    def test_aggregate_multiple_windows(self, aggregator, time_series_metrics):
        """Test aggregation across multiple time windows."""
        aggregated = aggregator.aggregate_all_windows(time_series_metrics)

        assert len(aggregated) == 3  # Three aggregation windows

        # Each window should have all aggregation functions
        for window_result in aggregated.values():
            assert 'avg' in window_result
            assert 'sum' in window_result
            assert 'max' in window_result
            assert 'min' in window_result

    def test_rolling_aggregation(self, aggregator):
        """Test rolling aggregation with sliding windows."""
        # Create hourly data
        hourly_metrics = []
        base_time = datetime.now()

        for hour in range(24):  # 24 hours
            for minute in range(0, 60, 10):  # Every 10 minutes
                metric = CoordinationMetrics(
                    timestamp=base_time - timedelta(hours=hour, minutes=minute),
                    active_tasks=100 + hour*2,
                    completed_tasks=1000,
                    failed_tasks=5,
                    queue_depth=25,
                    api_calls_count=500,
                    total_cost=Decimal("25.50"),
                    health_score=0.95,
                    event_id=f"hourly_{hour}_{minute}"
                )
                hourly_metrics.append(metric)

        rolling_agg = aggregator.rolling_aggregation(
            hourly_metrics,
            window_seconds=3600,  # 1 hour rolling window
            step_seconds=1800     # 30 minute steps
        )

        assert len(rolling_agg) > 0
        # Should have multiple rolling windows
        assert len(rolling_agg) >= 24  # At least 24 hours worth

    def test_weighted_aggregation(self, aggregator, time_series_metrics):
        """Test weighted aggregation based on recency."""
        # More recent metrics should have higher weight
        weighted_agg = aggregator.weighted_aggregation(
            time_series_metrics,
            weight_function='exponential_decay',
            decay_factor=0.1
        )

        # Compare with simple average
        simple_agg = aggregator.aggregate_metrics(time_series_metrics, window_seconds=900)

        # Results should be different due to weighting
        assert weighted_agg['avg']['active_tasks'] != simple_agg['avg']['active_tasks']

    def test_aggregation_with_missing_data(self, aggregator):
        """Test aggregation handling with missing/sparse data."""
        sparse_metrics = [
            CoordinationMetrics(
                timestamp=datetime.now() - timedelta(minutes=10),
                active_tasks=100,
                completed_tasks=1000,
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal("25.50"),
                health_score=0.95,
                event_id="sparse_1"
            ),
            # Large gap in data
            CoordinationMetrics(
                timestamp=datetime.now() - timedelta(minutes=1),
                active_tasks=120,
                completed_tasks=1100,
                failed_tasks=12,
                queue_depth=30,
                api_calls_count=550,
                total_cost=Decimal("28.00"),
                health_score=0.93,
                event_id="sparse_2"
            )
        ]

        aggregated = aggregator.aggregate_metrics(sparse_metrics, window_seconds=900)

        # Should still produce valid aggregation
        assert aggregated is not None
        assert aggregated['count']['active_tasks'] == 2


class TestMetricsStorage:
    """Test suite for MetricsStorage component."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ObservatoryConfig(
            redis_host="localhost",
            redis_port=6379,
            metrics_retention_hours=168,  # 7 days
            enable_compression=True
        )

    @pytest.fixture
    def storage(self, config):
        """Create MetricsStorage instance for testing."""
        return MetricsStorage(config)

    @pytest.fixture
    def sample_metrics_batch(self):
        """Create batch of sample metrics."""
        base_time = datetime.now()
        return [
            CoordinationMetrics(
                timestamp=base_time - timedelta(minutes=i),
                active_tasks=100 + i,
                completed_tasks=1000 + i*10,
                failed_tasks=10 + i,
                queue_depth=50 - i,
                api_calls_count=500 + i*5,
                total_cost=Decimal(f"{25.00 + i*0.25:.2f}"),
                health_score=0.95 - i*0.005,
                event_id=f"batch_metric_{i}"
            )
            for i in range(50)
        ]

    def test_storage_initialization(self, storage):
        """Test MetricsStorage initialization."""
        assert storage is not None
        assert hasattr(storage, 'store_metrics')
        assert hasattr(storage, 'retrieve_metrics')

    @pytest.mark.asyncio
    async def test_store_single_metric(self, storage, sample_metrics_batch):
        """Test storing a single metric."""
        metric = sample_metrics_batch[0]

        with patch.object(storage, '_redis_client') as mock_redis:
            mock_redis.hset = AsyncMock(return_value=True)
            mock_redis.zadd = AsyncMock(return_value=1)

            result = await storage.store_metric(metric)

            assert result is True
            mock_redis.hset.assert_called_once()
            mock_redis.zadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_metrics_batch(self, storage, sample_metrics_batch):
        """Test storing a batch of metrics."""
        with patch.object(storage, '_redis_client') as mock_redis:
            mock_redis.pipeline = MagicMock()
            mock_pipe = mock_redis.pipeline.return_value.__aenter__.return_value
            mock_pipe.hset = AsyncMock()
            mock_pipe.zadd = AsyncMock()
            mock_pipe.execute = AsyncMock(return_value=[True] * len(sample_metrics_batch))

            result = await storage.store_metrics_batch(sample_metrics_batch)

            assert result is True
            assert mock_pipe.hset.call_count == len(sample_metrics_batch)

    @pytest.mark.asyncio
    async def test_retrieve_metrics_by_time_range(self, storage):
        """Test retrieving metrics by time range."""
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        with patch.object(storage, '_redis_client') as mock_redis:
            # Mock Redis responses
            mock_redis.zrangebyscore = AsyncMock(return_value=[
                'metric_1', 'metric_2', 'metric_3'
            ])
            mock_redis.hmget = AsyncMock(return_value=[
                json.dumps({
                    'timestamp': start_time.isoformat(),
                    'active_tasks': 100,
                    'completed_tasks': 1000,
                    'failed_tasks': 10,
                    'queue_depth': 25,
                    'api_calls_count': 500,
                    'total_cost': '25.50',
                    'health_score': 0.95,
                    'event_id': 'retrieved_metric'
                }).encode()
            ])

            metrics = await storage.retrieve_metrics(start_time, end_time)

            assert len(metrics) > 0
            mock_redis.zrangebyscore.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_aggregated_metrics(self, storage):
        """Test retrieving pre-aggregated metrics."""
        with patch.object(storage, '_redis_client') as mock_redis:
            mock_redis.hget = AsyncMock(return_value=json.dumps({
                'avg': {'active_tasks': 125.5},
                'sum': {'completed_tasks': 50000},
                'max': {'health_score': 0.98},
                'min': {'failed_tasks': 5},
                'count': {'api_calls_count': 100}
            }).encode())

            aggregated = await storage.retrieve_aggregated_metrics(
                'hourly',
                datetime.now() - timedelta(hours=1),
                datetime.now()
            )

            assert aggregated is not None
            assert 'avg' in aggregated
            mock_redis.hget.assert_called()

    @pytest.mark.asyncio
    async def test_cleanup_expired_metrics(self, storage):
        """Test cleanup of expired metrics."""
        cutoff_time = datetime.now() - timedelta(hours=168)  # 7 days ago

        with patch.object(storage, '_redis_client') as mock_redis:
            mock_redis.zremrangebyscore = AsyncMock(return_value=25)  # 25 expired metrics
            mock_redis.scan_iter = AsyncMock(return_value=['expired_key_1', 'expired_key_2'])
            mock_redis.delete = AsyncMock(return_value=2)

            cleaned_count = await storage.cleanup_expired_metrics()

            assert cleaned_count > 0
            mock_redis.zremrangebyscore.assert_called()

    def test_metrics_compression(self, storage, sample_metrics_batch):
        """Test metrics compression functionality."""
        metric = sample_metrics_batch[0]

        # Test compression
        compressed = storage.compress_metric(metric)
        assert len(compressed) < len(str(metric))

        # Test decompression
        decompressed = storage.decompress_metric(compressed)
        assert decompressed.event_id == metric.event_id
        assert decompressed.active_tasks == metric.active_tasks

    @pytest.mark.asyncio
    async def test_storage_performance_metrics(self, storage):
        """Test storage performance tracking."""
        # Mock some storage operations
        with patch.object(storage, 'store_metric') as mock_store:
            mock_store.return_value = True

            # Simulate high-volume storage
            start_time = datetime.now()
            for i in range(1000):
                await storage.store_metric(MagicMock())

            perf_metrics = storage.get_performance_metrics()

            assert perf_metrics is not None
            assert 'operations_per_second' in perf_metrics
            assert 'average_operation_time' in perf_metrics
            assert 'total_operations' in perf_metrics


class TestRealTimeMetricsStreamer:
    """Test suite for RealTimeMetricsStreamer component."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ObservatoryConfig(
            redis_host="localhost",
            redis_port=6379,
            enable_real_time=True,
            stream_buffer_size=100
        )

    @pytest.fixture
    def streamer(self, config):
        """Create RealTimeMetricsStreamer instance for testing."""
        return RealTimeMetricsStreamer(config)

    def test_streamer_initialization(self, streamer):
        """Test RealTimeMetricsStreamer initialization."""
        assert streamer is not None
        assert hasattr(streamer, 'publish_metric')
        assert hasattr(streamer, 'subscribe_to_stream')

    @pytest.mark.asyncio
    async def test_publish_single_metric(self, streamer):
        """Test publishing a single metric to stream."""
        metric = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=100,
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=25,
            api_calls_count=500,
            total_cost=Decimal("25.50"),
            health_score=0.95,
            event_id="stream_test_1"
        )

        with patch.object(streamer, '_redis_client') as mock_redis:
            mock_redis.xadd = AsyncMock(return_value=b'stream_id_123')

            result = await streamer.publish_metric(metric)

            assert result is not None
            mock_redis.xadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_metrics_batch(self, streamer):
        """Test publishing batch of metrics to stream."""
        metrics = [
            CoordinationMetrics(
                timestamp=datetime.now() - timedelta(seconds=i),
                active_tasks=100 + i,
                completed_tasks=1000,
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal("25.50"),
                health_score=0.95,
                event_id=f"batch_stream_{i}"
            )
            for i in range(10)
        ]

        with patch.object(streamer, '_redis_client') as mock_redis:
            mock_redis.pipeline = MagicMock()
            mock_pipe = mock_redis.pipeline.return_value.__aenter__.return_value
            mock_pipe.xadd = AsyncMock()
            mock_pipe.execute = AsyncMock(return_value=[b'id_1', b'id_2'] * 5)

            results = await streamer.publish_metrics_batch(metrics)

            assert len(results) == 10
            assert mock_pipe.xadd.call_count == 10

    @pytest.mark.asyncio
    async def test_subscribe_to_metric_stream(self, streamer):
        """Test subscribing to metric stream."""
        callback_results = []

        async def test_callback(metric):
            callback_results.append(metric)

        with patch.object(streamer, '_redis_client') as mock_redis:
            # Mock Redis stream read
            mock_redis.xread = AsyncMock(return_value=[
                [b'metrics_stream', [
                    [b'123-0', {
                        b'data': json.dumps({
                            'timestamp': datetime.now().isoformat(),
                            'active_tasks': 100,
                            'event_id': 'streamed_metric'
                        }).encode()
                    }]
                ]]
            ])

            # Start subscription (run briefly)
            subscription_task = asyncio.create_task(
                streamer.subscribe_to_stream('metrics_stream', test_callback)
            )

            # Let it run briefly then cancel
            await asyncio.sleep(0.1)
            subscription_task.cancel()

            # Should have processed the mocked stream data
            assert len(callback_results) > 0 or mock_redis.xread.called

    @pytest.mark.asyncio
    async def test_stream_consumer_group(self, streamer):
        """Test Redis stream consumer group functionality."""
        group_name = "observatory_consumers"
        consumer_name = "consumer_1"

        with patch.object(streamer, '_redis_client') as mock_redis:
            mock_redis.xgroup_create = AsyncMock(return_value=True)
            mock_redis.xreadgroup = AsyncMock(return_value=[])

            await streamer.create_consumer_group(
                'metrics_stream',
                group_name,
                consumer_name
            )

            mock_redis.xgroup_create.assert_called_once()

    def test_stream_buffer_management(self, streamer):
        """Test stream buffer management."""
        # Fill buffer with metrics
        for i in range(150):  # More than buffer size
            metric = CoordinationMetrics(
                timestamp=datetime.now() - timedelta(seconds=i),
                active_tasks=100,
                completed_tasks=1000,
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal("25.50"),
                health_score=0.95,
                event_id=f"buffer_test_{i}"
            )
            streamer.add_to_buffer(metric)

        # Buffer should maintain its maximum size
        assert len(streamer.buffer) <= streamer.buffer_size

    @pytest.mark.asyncio
    async def test_stream_error_handling(self, streamer):
        """Test error handling in streaming operations."""
        metric = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=100,
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=25,
            api_calls_count=500,
            total_cost=Decimal("25.50"),
            health_score=0.95,
            event_id="error_test"
        )

        with patch.object(streamer, '_redis_client') as mock_redis:
            mock_redis.xadd = AsyncMock(side_effect=Exception("Redis connection failed"))

            # Should handle error gracefully
            result = await streamer.publish_metric(metric)
            assert result is None  # Should return None on error


class TestMetricsValidator:
    """Test suite for MetricsValidator component."""

    @pytest.fixture
    def validator(self):
        """Create MetricsValidator instance for testing."""
        return MetricsValidator(
            enable_strict_validation=True,
            auto_correct_errors=True
        )

    def test_validator_initialization(self, validator):
        """Test MetricsValidator initialization."""
        assert validator is not None
        assert validator.enable_strict_validation is True
        assert validator.auto_correct_errors is True

    def test_validate_valid_metric(self, validator):
        """Test validation of valid metric."""
        valid_metric = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=25,
            api_calls_count=500,
            total_cost=Decimal("25.50"),
            health_score=0.95,
            event_id="valid_metric"
        )

        result = validator.validate_metric(valid_metric)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_invalid_metric_values(self, validator):
        """Test validation of metric with invalid values."""
        invalid_metric = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=-10,  # Invalid: negative
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=25,
            api_calls_count=500,
            total_cost=Decimal("-5.00"),  # Invalid: negative cost
            health_score=1.5,  # Invalid: > 1.0
            event_id="invalid_metric"
        )

        result = validator.validate_metric(invalid_metric)

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Should detect negative active_tasks, negative cost, invalid health_score
        error_types = [error.error_type for error in result.errors]
        assert 'invalid_range' in error_types

    def test_validate_missing_required_fields(self, validator):
        """Test validation with missing required fields."""
        # Create metric with None timestamp
        incomplete_metric = CoordinationMetrics(
            timestamp=None,  # Required field missing
            active_tasks=50,
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=25,
            api_calls_count=500,
            total_cost=Decimal("25.50"),
            health_score=0.95,
            event_id="incomplete_metric"
        )

        result = validator.validate_metric(incomplete_metric)

        assert result.is_valid is False
        assert any(error.error_type == 'missing_required' for error in result.errors)

    def test_auto_correction(self, validator):
        """Test auto-correction of correctable errors."""
        correctable_metric = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=25,
            api_calls_count=500,
            total_cost=Decimal("25.50"),
            health_score=1.2,  # Will be corrected to 1.0
            event_id="correctable_metric"
        )

        result = validator.validate_metric(correctable_metric)

        if validator.auto_correct_errors:
            # Should auto-correct health_score to valid range
            assert result.corrected_metric.health_score <= 1.0

    def test_validate_business_rules(self, validator):
        """Test validation of business logic rules."""
        # Create metric that violates business rules
        business_rule_violation = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=900,
            failed_tasks=200,  # High failure rate (18%)
            queue_depth=25,
            api_calls_count=500,
            total_cost=Decimal("25.50"),
            health_score=0.95,  # High health score despite high failures
            event_id="business_rule_test"
        )

        result = validator.validate_metric(business_rule_violation)

        # Should detect inconsistency between high failure rate and high health score
        assert len(result.warnings) > 0
        assert any('inconsistent' in warning.message.lower() for warning in result.warnings)

    def test_validate_temporal_consistency(self, validator):
        """Test validation of temporal consistency."""
        base_time = datetime.now()

        # Create sequence of metrics with temporal issues
        metrics = [
            CoordinationMetrics(
                timestamp=base_time,
                active_tasks=100,
                completed_tasks=1000,
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal("25.50"),
                health_score=0.95,
                event_id="temporal_1"
            ),
            CoordinationMetrics(
                timestamp=base_time + timedelta(minutes=5),
                active_tasks=90,
                completed_tasks=800,  # Decreased completed tasks (impossible)
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal("25.50"),
                health_score=0.95,
                event_id="temporal_2"
            )
        ]

        result = validator.validate_temporal_consistency(metrics)

        assert len(result.errors) > 0
        assert any('temporal' in error.error_type for error in result.errors)

    def test_batch_validation(self, validator):
        """Test batch validation of multiple metrics."""
        metrics_batch = []
        base_time = datetime.now()

        # Create mix of valid and invalid metrics
        for i in range(20):
            metric = CoordinationMetrics(
                timestamp=base_time - timedelta(minutes=i),
                active_tasks=50 if i % 2 == 0 else -10,  # Every other invalid
                completed_tasks=1000 + i*10,
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal(f"{25.00 + i:.2f}"),
                health_score=0.95,
                event_id=f"batch_metric_{i}"
            )
            metrics_batch.append(metric)

        results = validator.validate_metrics_batch(metrics_batch)

        assert len(results) == 20

        # Should have mix of valid and invalid results
        valid_count = sum(1 for r in results if r.is_valid)
        invalid_count = sum(1 for r in results if not r.is_valid)

        assert valid_count > 0
        assert invalid_count > 0


class TestMetricsCollectorIntegration:
    """Integration tests for the complete metrics collection system."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ObservatoryConfig(
            redis_host="localhost",
            redis_port=6379,
            enable_real_time=True,
            metrics_retention_hours=24,
            enable_compression=True
        )

    @pytest.fixture
    def collector(self, config):
        """Create MetricsCollector instance for testing."""
        return MetricsCollector(config)

    @pytest.mark.asyncio
    async def test_end_to_end_collection_pipeline(self, collector):
        """Test end-to-end metrics collection pipeline."""
        # Create test metrics
        test_metrics = [
            CoordinationMetrics(
                timestamp=datetime.now() - timedelta(seconds=i*30),
                active_tasks=100 + i,
                completed_tasks=1000 + i*10,
                failed_tasks=5 + i,
                queue_depth=50 - i,
                api_calls_count=500 + i*5,
                total_cost=Decimal(f"{25.00 + i*0.25:.2f}"),
                health_score=0.95 - i*0.005,
                event_id=f"e2e_metric_{i}"
            )
            for i in range(20)
        ]

        with patch.object(collector.storage, 'store_metrics_batch') as mock_store:
            with patch.object(collector.streamer, 'publish_metrics_batch') as mock_stream:
                mock_store.return_value = True
                mock_stream.return_value = [f'stream_id_{i}' for i in range(20)]

                # Process through complete pipeline
                result = await collector.collect_metrics_batch(test_metrics)

                assert result['processed'] == 20
                assert result['stored'] == 20
                assert result['streamed'] == 20
                assert result['errors'] == 0

                mock_store.assert_called_once()
                mock_stream.assert_called_once()

    @pytest.mark.asyncio
    async def test_high_volume_performance(self, collector):
        """Test performance with high-volume metrics."""
        # Generate large batch of metrics
        large_batch = []
        base_time = datetime.now()

        for i in range(10000):  # 10K metrics
            metric = CoordinationMetrics(
                timestamp=base_time - timedelta(seconds=i),
                active_tasks=100,
                completed_tasks=1000,
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal("25.50"),
                health_score=0.95,
                event_id=f"perf_test_{i}"
            )
            large_batch.append(metric)

        # Mock storage and streaming for performance test
        with patch.object(collector.storage, 'store_metrics_batch') as mock_store:
            with patch.object(collector.streamer, 'publish_metrics_batch') as mock_stream:
                mock_store.return_value = True
                mock_stream.return_value = [f'id_{i}' for i in range(10000)]

                start_time = datetime.now()
                result = await collector.collect_metrics_batch(large_batch)
                end_time = datetime.now()

                processing_time = (end_time - start_time).total_seconds()

                # Should process 10K metrics in reasonable time (< 10 seconds)
                assert processing_time < 10.0
                assert result['processed'] == 10000

                # Check performance metrics
                perf_metrics = collector.get_performance_metrics()
                assert perf_metrics['throughput_metrics_per_second'] > 1000

    @pytest.mark.asyncio
    async def test_error_recovery_and_resilience(self, collector):
        """Test error recovery and system resilience."""
        test_metrics = [
            CoordinationMetrics(
                timestamp=datetime.now(),
                active_tasks=100,
                completed_tasks=1000,
                failed_tasks=10,
                queue_depth=25,
                api_calls_count=500,
                total_cost=Decimal("25.50"),
                health_score=0.95,
                event_id=f"resilience_test_{i}"
            )
            for i in range(50)
        ]

        # Simulate storage failure
        with patch.object(collector.storage, 'store_metrics_batch') as mock_store:
            with patch.object(collector.streamer, 'publish_metrics_batch') as mock_stream:
                mock_store.side_effect = Exception("Storage temporarily unavailable")
                mock_stream.return_value = [f'id_{i}' for i in range(50)]

                # Should handle storage failure gracefully
                result = await collector.collect_metrics_batch(test_metrics)

                # Should still succeed in streaming even if storage fails
                assert result['processed'] == 50
                assert result['streamed'] == 50
                assert result['storage_errors'] > 0

    def test_get_collector_status(self, collector):
        """Test metrics collector status reporting."""
        status = collector.get_collector_status()

        assert status is not None
        assert 'buffer_status' in status
        assert 'storage_status' in status
        assert 'stream_status' in status
        assert 'validator_status' in status
        assert 'performance_metrics' in status

    @pytest.mark.asyncio
    async def test_concurrent_collection_operations(self, collector):
        """Test concurrent metrics collection operations."""
        # Create multiple concurrent collection tasks
        tasks = []

        for batch_id in range(10):
            batch_metrics = [
                CoordinationMetrics(
                    timestamp=datetime.now() - timedelta(seconds=i),
                    active_tasks=100,
                    completed_tasks=1000,
                    failed_tasks=10,
                    queue_depth=25,
                    api_calls_count=500,
                    total_cost=Decimal("25.50"),
                    health_score=0.95,
                    event_id=f"concurrent_{batch_id}_{i}"
                )
                for i in range(100)
            ]

            task = collector.collect_metrics_batch(batch_metrics)
            tasks.append(task)

        # Execute all concurrently
        with patch.object(collector.storage, 'store_metrics_batch') as mock_store:
            with patch.object(collector.streamer, 'publish_metrics_batch') as mock_stream:
                mock_store.return_value = True
                mock_stream.return_value = ['id'] * 100

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # All should complete successfully
                assert len(results) == 10
                assert all(not isinstance(r, Exception) for r in results)

                # Should have processed all batches
                total_processed = sum(r['processed'] for r in results if isinstance(r, dict))
                assert total_processed == 1000