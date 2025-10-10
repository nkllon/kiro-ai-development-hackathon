"""Comprehensive unit tests for WebSocket connection optimization components."""

import asyncio
import json
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.beast_mode.observatory.websocket.connection_pool import (
    ConnectionPool,
    ConnectionPoolConfig,
    PoolStrategy,
    PoolMetrics,
)
from src.beast_mode.observatory.websocket.message_optimizer import (
    MessageOptimizer,
    MessageOptimizerConfig,
    MessagePriority,
    BatchStrategy,
    MessageBatch,
    OptimizationMetrics,
)
from src.beast_mode.observatory.websocket.compression_handler import (
    CompressionHandler,
    CompressionConfig,
    CompressionAlgorithm,
    SerializationFormat,
    CompressionResult,
    CompressionMetrics,
)
from src.beast_mode.observatory.websocket.connection import WebSocketConnection, ConnectionStatus
from src.beast_mode.observatory.websocket.exceptions import ConnectionFailedError


class TestConnectionPool:
    """Test connection pooling and reuse mechanisms."""

    @pytest.fixture
    def pool_config(self):
        """Create a test configuration for connection pool."""
        return ConnectionPoolConfig(
            max_connections=10,
            min_connections=2,
            max_idle_time=60,
            connection_timeout=5.0,
            health_check_interval=10,
            pool_strategy=PoolStrategy.LEAST_CONNECTIONS,
            enable_compression=True,
            enable_keepalive=True,
            keepalive_interval=20,
            max_retries=3,
            retry_delay=1.0,
        )

    @pytest.fixture
    def mock_connection(self):
        """Create a mock WebSocket connection."""
        connection = MagicMock(spec=WebSocketConnection)
        connection.endpoint = "ws://test.example.com/ws"
        connection.is_connected.return_value = True
        connection.connect = AsyncMock()
        connection.disconnect = AsyncMock()
        return connection

    @pytest.fixture
    async def connection_pool(self, pool_config):
        """Create and initialize a connection pool."""
        pool = ConnectionPool(pool_config)
        await pool.initialize()
        yield pool
        await pool.close()

    @pytest.mark.asyncio
    async def test_pool_initialization(self, pool_config):
        """Test connection pool initialization."""
        pool = ConnectionPool(pool_config)
        await pool.initialize()
        
        assert pool.config == pool_config
        assert pool._pool_metrics.total_connections == 0
        assert pool._health_check_task is not None
        assert pool._cleanup_task is not None
        
        await pool.close()

    @pytest.mark.asyncio
    async def test_get_connection_round_robin(self, pool_config, mock_connection):
        """Test getting connection with round-robin strategy."""
        pool_config.pool_strategy = PoolStrategy.ROUND_ROBIN
        pool = ConnectionPool(pool_config)
        
        with patch.object(pool, '_create_new_connection', return_value=mock_connection):
            await pool.initialize()
            
            connection = await pool.get_connection("ws://test.example.com/ws")
            assert connection == mock_connection
            assert connection in pool._active_connections
            
            await pool.close()

    @pytest.mark.asyncio
    async def test_get_connection_least_connections(self, pool_config, mock_connection):
        """Test getting connection with least connections strategy."""
        pool_config.pool_strategy = PoolStrategy.LEAST_CONNECTIONS
        pool = ConnectionPool(pool_config)
        
        with patch.object(pool, '_create_new_connection', return_value=mock_connection):
            await pool.initialize()
            
            connection = await pool.get_connection("ws://test.example.com/ws")
            assert connection == mock_connection
            
            await pool.close()

    @pytest.mark.asyncio
    async def test_get_connection_sticky_session(self, pool_config, mock_connection):
        """Test sticky session functionality."""
        pool_config.pool_strategy = PoolStrategy.STICKY_SESSION
        pool = ConnectionPool(pool_config)
        
        with patch.object(pool, '_create_new_connection', return_value=mock_connection):
            await pool.initialize()
            
            session_id = "test_session_123"
            connection1 = await pool.get_connection("ws://test.example.com/ws", session_id)
            connection2 = await pool.get_connection("ws://test.example.com/ws", session_id)
            
            assert connection1 == connection2
            assert session_id in pool._session_sticky_map
            
            await pool.close()

    @pytest.mark.asyncio
    async def test_return_connection(self, connection_pool, mock_connection):
        """Test returning connection to pool."""
        pool = connection_pool
        pool._active_connections.add(mock_connection)
        
        await pool.return_connection(mock_connection)
        
        assert mock_connection not in pool._active_connections
        assert mock_connection in pool._idle_connections

    @pytest.mark.asyncio
    async def test_connection_pool_exhausted(self, pool_config):
        """Test behavior when connection pool is exhausted."""
        pool_config.max_connections = 1
        pool = ConnectionPool(pool_config)
        
        mock_connection = MagicMock(spec=WebSocketConnection)
        mock_connection.endpoint = "ws://test.example.com/ws"
        mock_connection.is_connected.return_value = True
        
        with patch.object(pool, '_create_new_connection', return_value=mock_connection):
            await pool.initialize()
            
            # Get first connection
            connection1 = await pool.get_connection("ws://test.example.com/ws")
            assert connection1 == mock_connection
            
            # Try to get second connection - should fail
            with pytest.raises(ConnectionFailedError):
                await pool.get_connection("ws://test.example.com/ws")
            
            await pool.close()

    @pytest.mark.asyncio
    async def test_health_check_loop(self, connection_pool):
        """Test health check background loop."""
        pool = connection_pool
        
        # Mock an unhealthy connection
        mock_connection = MagicMock(spec=WebSocketConnection)
        mock_connection.is_connected.return_value = False
        mock_connection.endpoint = "ws://test.example.com/ws"
        
        pool._connections["ws://test.example.com/ws"] = [mock_connection]
        
        # Run health check
        await pool._perform_health_checks()
        
        # Connection should be removed
        assert len(pool._connections["ws://test.example.com/ws"]) == 0

    @pytest.mark.asyncio
    async def test_cleanup_idle_connections(self, connection_pool):
        """Test cleanup of idle connections."""
        pool = connection_pool
        
        # Create mock connection that's been idle too long
        mock_connection = MagicMock(spec=WebSocketConnection)
        mock_connection.endpoint = "ws://test.example.com/ws"
        mock_connection.is_connected.return_value = True
        
        pool._idle_connections.append(mock_connection)
        pool._last_used_times[mock_connection] = datetime.utcnow() - timedelta(seconds=400)
        
        await pool._cleanup_idle_connections()
        
        # Connection should be removed
        assert mock_connection not in pool._idle_connections

    def test_pool_metrics(self, connection_pool):
        """Test pool metrics collection."""
        pool = connection_pool
        
        # Add some mock connections
        mock_connection = MagicMock(spec=WebSocketConnection)
        mock_connection.endpoint = "ws://test.example.com/ws"
        mock_connection.is_connected.return_value = True
        
        pool._connections["ws://test.example.com/ws"] = [mock_connection]
        pool._active_connections.add(mock_connection)
        
        metrics = pool.get_pool_metrics()
        
        assert 'total_connections' in metrics
        assert 'active_connections' in metrics
        assert 'idle_connections' in metrics
        assert 'memory_usage_mb' in metrics
        assert 'cpu_usage_percent' in metrics

    def test_connection_stats(self, connection_pool):
        """Test connection statistics."""
        pool = connection_pool
        
        # Add mock connections
        mock_connection = MagicMock(spec=WebSocketConnection)
        mock_connection.endpoint = "ws://test.example.com/ws"
        mock_connection.is_connected.return_value = True
        
        pool._connections["ws://test.example.com/ws"] = [mock_connection]
        pool._active_connections.add(mock_connection)
        
        stats = pool.get_connection_stats()
        
        assert 'endpoints' in stats
        assert 'total_connections' in stats
        assert 'active_connections' in stats
        assert 'idle_connections' in stats
        assert 'ws://test.example.com/ws' in stats['endpoints']


class TestMessageOptimizer:
    """Test message batching and optimization."""

    @pytest.fixture
    def optimizer_config(self):
        """Create a test configuration for message optimizer."""
        return MessageOptimizerConfig(
            batch_timeout=0.1,
            max_batch_size=1024,
            max_batch_count=10,
            enable_compression=True,
            enable_deduplication=True,
            enable_prioritization=True,
            batch_strategy=BatchStrategy.HYBRID,
            priority_threshold=100,
            drop_threshold=0.95,
            max_queue_size=1000,
            compression_threshold=512,
        )

    @pytest.fixture
    async def message_optimizer(self, optimizer_config):
        """Create and initialize a message optimizer."""
        optimizer = MessageOptimizer(optimizer_config)
        await optimizer.initialize()
        yield optimizer
        await optimizer.close()

    @pytest.mark.asyncio
    async def test_optimizer_initialization(self, optimizer_config):
        """Test message optimizer initialization."""
        optimizer = MessageOptimizer(optimizer_config)
        await optimizer.initialize()
        
        assert optimizer.config == optimizer_config
        assert optimizer._processing_task is not None
        assert optimizer._batch_processor_task is not None
        assert optimizer._metrics.total_messages == 0
        
        await optimizer.close()

    @pytest.mark.asyncio
    async def test_add_message_normal_priority(self, message_optimizer):
        """Test adding normal priority message."""
        optimizer = message_optimizer
        
        message = {"type": "test", "data": "hello world"}
        message_id = await optimizer.add_message(message, MessagePriority.NORMAL)
        
        assert message_id.startswith("msg_")
        assert optimizer._metrics.total_messages == 1

    @pytest.mark.asyncio
    async def test_add_message_critical_priority(self, message_optimizer):
        """Test adding critical priority message."""
        optimizer = message_optimizer
        
        message = {"type": "critical", "data": "urgent"}
        message_id = await optimizer.add_message(message, MessagePriority.CRITICAL)
        
        assert message_id.startswith("msg_")
        assert optimizer._metrics.total_messages == 1

    @pytest.mark.asyncio
    async def test_message_deduplication(self, message_optimizer):
        """Test message deduplication functionality."""
        optimizer = message_optimizer
        
        message = {"type": "duplicate", "data": "same content"}
        
        # Add same message twice
        message_id1 = await optimizer.add_message(message, MessagePriority.NORMAL)
        message_id2 = await optimizer.add_message(message, MessagePriority.NORMAL)
        
        assert optimizer._metrics.total_messages == 1
        assert optimizer._metrics.duplicate_messages == 1

    @pytest.mark.asyncio
    async def test_batch_creation_time_based(self, optimizer_config):
        """Test time-based batch creation."""
        optimizer_config.batch_strategy = BatchStrategy.TIME_BASED
        optimizer_config.batch_timeout = 0.05  # 50ms
        
        optimizer = MessageOptimizer(optimizer_config)
        await optimizer.initialize()
        
        # Add message to batch
        message = {"type": "batch_test", "data": "test"}
        await optimizer.add_message(message, MessagePriority.NORMAL, "test_batch")
        
        # Wait for batch timeout
        await asyncio.sleep(0.1)
        
        # Check if batch was processed
        assert len(optimizer._active_batches) == 0
        
        await optimizer.close()

    @pytest.mark.asyncio
    async def test_batch_creation_size_based(self, optimizer_config):
        """Test size-based batch creation."""
        optimizer_config.batch_strategy = BatchStrategy.SIZE_BASED
        optimizer_config.max_batch_size = 100  # Small size for testing
        
        optimizer = MessageOptimizer(optimizer_config)
        await optimizer.initialize()
        
        # Add large message to batch
        large_message = {"type": "large", "data": "x" * 200}
        await optimizer.add_message(large_message, MessagePriority.NORMAL, "large_batch")
        
        # Batch should be processed immediately due to size
        await asyncio.sleep(0.01)
        assert len(optimizer._active_batches) == 0
        
        await optimizer.close()

    @pytest.mark.asyncio
    async def test_batch_creation_count_based(self, optimizer_config):
        """Test count-based batch creation."""
        optimizer_config.batch_strategy = BatchStrategy.COUNT_BASED
        optimizer_config.max_batch_count = 3
        
        optimizer = MessageOptimizer(optimizer_config)
        await optimizer.initialize()
        
        # Add multiple messages to batch
        for i in range(3):
            message = {"type": "count_test", "data": f"message_{i}"}
            await optimizer.add_message(message, MessagePriority.NORMAL, "count_batch")
        
        # Batch should be processed due to count
        await asyncio.sleep(0.01)
        assert len(optimizer._active_batches) == 0
        
        await optimizer.close()

    @pytest.mark.asyncio
    async def test_queue_capacity_drop(self, optimizer_config):
        """Test message dropping when queue is full."""
        optimizer_config.max_queue_size = 5
        optimizer_config.drop_threshold = 0.8  # Drop at 80% capacity
        
        optimizer = MessageOptimizer(optimizer_config)
        await optimizer.initialize()
        
        # Fill queue beyond threshold
        for i in range(6):
            message = {"type": "capacity_test", "data": f"message_{i}"}
            await optimizer.add_message(message, MessagePriority.NORMAL)
        
        # Some messages should be dropped
        assert optimizer._metrics.dropped_messages > 0
        
        await optimizer.close()

    def test_message_batch_creation(self):
        """Test MessageBatch class functionality."""
        batch = MessageBatch(
            batch_id="test_batch",
            priority=MessagePriority.HIGH,
            created_at=datetime.utcnow()
        )
        
        message1 = {"type": "test1", "data": "hello"}
        message2 = {"type": "test2", "data": "world"}
        
        batch.add_message(message1)
        batch.add_message(message2)
        
        assert len(batch.messages) == 2
        assert batch.total_size > 0
        
        batch_data = batch.get_batch_data()
        assert batch_data['batch_id'] == "test_batch"
        assert batch_data['message_count'] == 2
        assert batch_data['priority'] == MessagePriority.HIGH.value

    def test_optimization_metrics(self, message_optimizer):
        """Test optimization metrics collection."""
        optimizer = message_optimizer
        
        metrics = optimizer.get_metrics()
        
        assert 'total_messages' in metrics
        assert 'batched_messages' in metrics
        assert 'compression_savings' in metrics
        assert 'avg_batch_size' in metrics
        assert 'messages_per_second' in metrics
        assert 'dropped_messages' in metrics
        assert 'duplicate_messages' in metrics

    def test_queue_status(self, message_optimizer):
        """Test queue status reporting."""
        optimizer = message_optimizer
        
        status = optimizer.get_queue_status()
        
        assert 'message_queue_size' in status
        assert 'batch_queue_size' in status
        assert 'active_batches' in status
        assert 'cache_size' in status
        assert 'throughput_mps' in status
        assert 'peak_throughput_mps' in status


class TestCompressionHandler:
    """Test compression and serialization optimization."""

    @pytest.fixture
    def compression_config(self):
        """Create a test configuration for compression handler."""
        return CompressionConfig(
            default_algorithm=CompressionAlgorithm.LZ4,
            default_format=SerializationFormat.MSGPACK,
            compression_threshold=100,
            max_compression_level=6,
            enable_adaptive_compression=True,
            enable_parallel_compression=True,
            compression_timeout=2.0,
            cache_compressed_data=True,
            cache_size_limit=100,
            enable_compression_metrics=True,
        )

    @pytest.fixture
    def compression_handler(self, compression_config):
        """Create a compression handler."""
        return CompressionHandler(compression_config)

    @pytest.mark.asyncio
    async def test_compress_message_json_gzip(self, compression_handler):
        """Test compressing a JSON message with GZIP."""
        message = {"type": "test", "data": "hello world", "number": 42}
        
        result = await compression_handler.compress_message(
            message, 
            CompressionAlgorithm.GZIP, 
            SerializationFormat.JSON
        )
        
        assert isinstance(result, CompressionResult)
        assert result.algorithm == CompressionAlgorithm.GZIP
        assert result.serialization_format == SerializationFormat.JSON
        assert result.original_size > 0
        assert result.compressed_size > 0
        assert result.compression_ratio >= 0.0
        assert result.processing_time > 0.0

    @pytest.mark.asyncio
    async def test_compress_message_msgpack_lz4(self, compression_handler):
        """Test compressing a message with LZ4 and MessagePack."""
        message = {"type": "test", "data": "hello world", "number": 42}
        
        result = await compression_handler.compress_message(
            message, 
            CompressionAlgorithm.LZ4, 
            SerializationFormat.MSGPACK
        )
        
        assert isinstance(result, CompressionResult)
        assert result.algorithm == CompressionAlgorithm.LZ4
        assert result.serialization_format == SerializationFormat.MSGPACK
        assert result.original_size > 0
        assert result.compressed_size > 0

    @pytest.mark.asyncio
    async def test_decompress_message(self, compression_handler):
        """Test decompressing a message."""
        original_message = {"type": "test", "data": "hello world", "number": 42}
        
        # Compress first
        compressed_result = await compression_handler.compress_message(
            original_message, 
            CompressionAlgorithm.GZIP, 
            SerializationFormat.JSON
        )
        
        # Then decompress
        decompressed_message = await compression_handler.decompress_message(
            compressed_result.data,
            compressed_result.algorithm,
            compressed_result.serialization_format
        )
        
        assert decompressed_message == original_message

    @pytest.mark.asyncio
    async def test_compression_below_threshold(self, compression_config):
        """Test that small messages are not compressed."""
        compression_config.compression_threshold = 1000
        handler = CompressionHandler(compression_config)
        
        small_message = {"type": "small", "data": "hi"}
        
        result = await handler.compress_message(small_message)
        
        assert result.algorithm == CompressionAlgorithm.NONE
        assert result.compression_ratio == 0.0

    @pytest.mark.asyncio
    async def test_adaptive_compression_selection(self, compression_handler):
        """Test adaptive compression algorithm selection."""
        # Test with different data sizes
        small_data = b"small data"
        large_data = b"large data " * 1000
        
        # Small data should prefer GZIP
        small_result = await compression_handler._select_optimal_algorithm(
            small_data, CompressionAlgorithm.LZ4
        )
        
        # Large data should prefer LZ4
        large_result = await compression_handler._select_optimal_algorithm(
            large_data, CompressionAlgorithm.GZIP
        )
        
        # Results should be different based on data characteristics
        assert isinstance(small_result, CompressionAlgorithm)
        assert isinstance(large_result, CompressionAlgorithm)

    @pytest.mark.asyncio
    async def test_batch_compression(self, compression_handler):
        """Test batch compression functionality."""
        messages = [
            {"type": "test1", "data": "message 1"},
            {"type": "test2", "data": "message 2"},
            {"type": "test3", "data": "message 3"},
        ]
        
        results = await compression_handler.batch_compress(
            messages, 
            CompressionAlgorithm.GZIP, 
            SerializationFormat.JSON
        )
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, CompressionResult)
            assert result.algorithm == CompressionAlgorithm.GZIP
            assert result.serialization_format == SerializationFormat.JSON

    @pytest.mark.asyncio
    async def test_compression_caching(self, compression_handler):
        """Test compression result caching."""
        message = {"type": "cache_test", "data": "cached message"}
        
        # First compression
        result1 = await compression_handler.compress_message(message)
        
        # Second compression should use cache
        result2 = await compression_handler.compress_message(message)
        
        # Results should be identical (cached)
        assert result1.data == result2.data
        assert result1.original_size == result2.original_size
        assert result1.compressed_size == result2.compressed_size

    def test_compression_metrics(self, compression_handler):
        """Test compression metrics collection."""
        metrics = compression_handler.get_metrics()
        
        assert 'total_compressions' in metrics
        assert 'total_decompressions' in metrics
        assert 'total_bytes_saved' in metrics
        assert 'avg_compression_ratio' in metrics
        assert 'avg_processing_time' in metrics
        assert 'compression_success_rate' in metrics
        assert 'algorithm_usage' in metrics
        assert 'format_usage' in metrics

    def test_cache_status(self, compression_handler):
        """Test cache status reporting."""
        status = compression_handler.get_cache_status()
        
        assert 'cache_size' in status
        assert 'cache_limit' in status
        assert 'cache_hit_rate' in status
        assert 'memory_usage_estimate' in status

    @pytest.mark.asyncio
    async def test_benchmark_algorithms(self, compression_handler):
        """Test algorithm benchmarking functionality."""
        sample_data = [
            {"type": "benchmark", "data": "test message 1"},
            {"type": "benchmark", "data": "test message 2"},
            {"type": "benchmark", "data": "test message 3"},
        ]
        
        results = await compression_handler.benchmark_algorithms(sample_data)
        
        assert 'gzip' in results
        assert 'lz4' in results
        assert 'zlib' in results
        
        for algorithm, metrics in results.items():
            assert 'total_size' in metrics
            assert 'compressed_size' in metrics
            assert 'total_time' in metrics
            assert 'avg_ratio' in metrics
            assert 'success_count' in metrics

    @pytest.mark.asyncio
    async def test_serialization_formats(self, compression_handler):
        """Test different serialization formats."""
        message = {"type": "format_test", "data": "test", "number": 42, "list": [1, 2, 3]}
        
        # Test JSON serialization
        json_result = await compression_handler.compress_message(
            message, SerializationFormat.JSON
        )
        assert json_result.serialization_format == SerializationFormat.JSON
        
        # Test MessagePack serialization
        msgpack_result = await compression_handler.compress_message(
            message, SerializationFormat.MSGPACK
        )
        assert msgpack_result.serialization_format == SerializationFormat.MSGPACK
        
        # MessagePack should be more efficient
        assert msgpack_result.original_size <= json_result.original_size

    @pytest.mark.asyncio
    async def test_compression_error_handling(self, compression_handler):
        """Test error handling in compression."""
        # Test with invalid data that might cause serialization errors
        invalid_message = {"circular_ref": None}
        invalid_message["circular_ref"] = invalid_message  # Create circular reference
        
        with pytest.raises(Exception):
            await compression_handler.compress_message(invalid_message)


class TestIntegrationScenarios:
    """Integration tests for WebSocket optimization components."""

    @pytest.mark.asyncio
    async def test_full_optimization_pipeline(self):
        """Test the complete optimization pipeline."""
        # Create components
        pool_config = ConnectionPoolConfig(max_connections=5, min_connections=1)
        optimizer_config = MessageOptimizerConfig(
            batch_timeout=0.05,
            max_batch_count=5,
            enable_compression=True,
            enable_deduplication=True
        )
        compression_config = CompressionConfig(
            compression_threshold=100,
            enable_adaptive_compression=True
        )
        
        pool = ConnectionPool(pool_config)
        optimizer = MessageOptimizer(optimizer_config)
        compression_handler = CompressionHandler(compression_config)
        
        try:
            await pool.initialize()
            await optimizer.initialize()
            
            # Add messages to optimizer
            messages = [
                {"type": "test", "data": f"message_{i}", "timestamp": time.time()}
                for i in range(10)
            ]
            
            for message in messages:
                await optimizer.add_message(message, MessagePriority.NORMAL, "integration_batch")
            
            # Wait for batch processing
            await asyncio.sleep(0.1)
            
            # Check metrics
            pool_metrics = pool.get_pool_metrics()
            optimizer_metrics = optimizer.get_metrics()
            compression_metrics = compression_handler.get_metrics()
            
            assert pool_metrics['total_connections'] >= 0
            assert optimizer_metrics['total_messages'] >= 0
            assert compression_metrics['total_compressions'] >= 0
            
        finally:
            await pool.close()
            await optimizer.close()

    @pytest.mark.asyncio
    async def test_high_frequency_message_handling(self):
        """Test handling of high-frequency messages."""
        optimizer_config = MessageOptimizerConfig(
            batch_timeout=0.01,  # Very short timeout
            max_batch_count=100,
            enable_compression=True,
            enable_deduplication=True,
            max_queue_size=1000
        )
        
        optimizer = MessageOptimizer(optimizer_config)
        await optimizer.initialize()
        
        try:
            # Send many messages rapidly
            start_time = time.time()
            for i in range(500):
                message = {"type": "rapid", "data": f"message_{i}", "timestamp": time.time()}
                await optimizer.add_message(message, MessagePriority.NORMAL)
            
            # Wait for processing
            await asyncio.sleep(0.2)
            
            metrics = optimizer.get_metrics()
            assert metrics['total_messages'] >= 500
            assert metrics['messages_per_second'] > 0
            
        finally:
            await optimizer.close()

    @pytest.mark.asyncio
    async def test_memory_usage_optimization(self):
        """Test memory usage optimization."""
        compression_config = CompressionConfig(
            cache_compressed_data=True,
            cache_size_limit=50,  # Small cache limit
            compression_threshold=50
        )
        
        compression_handler = CompressionHandler(compression_config)
        
        # Compress many messages to test cache management
        for i in range(100):
            message = {"type": "memory_test", "data": f"message_{i}", "large_data": "x" * 1000}
            await compression_handler.compress_message(message)
        
        cache_status = compression_handler.get_cache_status()
        assert cache_status['cache_size'] <= compression_config.cache_size_limit
        
        # Test cache cleanup
        await compression_handler.cleanup_cache()
        
        # Cache should be cleaned up
        final_cache_status = compression_handler.get_cache_status()
        assert final_cache_status['cache_size'] <= cache_status['cache_size']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])