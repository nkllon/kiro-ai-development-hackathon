"""Comprehensive tests for WebSocket connection optimization features."""

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
    """Test connection pooling functionality."""

    @pytest.fixture
    def pool_config(self):
        """Create a test pool configuration."""
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
    async def connection_pool(self, pool_config):
        """Create a test connection pool."""
        pool = ConnectionPool(pool_config)
        await pool.initialize()
        yield pool
        await pool.close()

    @pytest.mark.asyncio
    async def test_pool_initialization(self, connection_pool):
        """Test connection pool initialization."""
        assert connection_pool.config.max_connections == 10
        assert connection_pool.config.min_connections == 2
        assert connection_pool.config.pool_strategy == PoolStrategy.LEAST_CONNECTIONS
        
        metrics = connection_pool.get_pool_metrics()
        assert 'total_connections' in metrics
        assert 'active_connections' in metrics
        assert 'idle_connections' in metrics

    @pytest.mark.asyncio
    async def test_connection_creation_and_reuse(self, connection_pool):
        """Test connection creation and reuse."""
        endpoint = "ws://test.example.com/ws"
        
        # Mock WebSocket connection
        with patch('src.beast_mode.observatory.websocket.connection_pool.WebSocketConnection') as mock_conn_class:
            mock_connection = AsyncMock()
            mock_connection.endpoint = endpoint
            mock_connection.is_connected.return_value = True
            mock_connection.connect = AsyncMock()
            mock_connection.disconnect = AsyncMock()
            mock_conn_class.return_value = mock_connection
            
            # Get first connection
            conn1 = await connection_pool.get_connection(endpoint)
            assert conn1 is not None
            
            # Return connection to pool
            await connection_pool.return_connection(conn1)
            
            # Get second connection (should reuse)
            conn2 = await connection_pool.get_connection(endpoint)
            assert conn2 is not None
            
            # Verify connection was reused
            assert conn1 == conn2

    @pytest.mark.asyncio
    async def test_pool_strategies(self, pool_config):
        """Test different pool strategies."""
        strategies = [
            PoolStrategy.ROUND_ROBIN,
            PoolStrategy.LEAST_CONNECTIONS,
            PoolStrategy.LEAST_LATENCY,
            PoolStrategy.STICKY_SESSION,
        ]
        
        for strategy in strategies:
            config = ConnectionPoolConfig(
                max_connections=5,
                min_connections=1,
                pool_strategy=strategy,
            )
            pool = ConnectionPool(config)
            await pool.initialize()
            
            # Test that strategy is set correctly
            assert pool.config.pool_strategy == strategy
            
            await pool.close()

    @pytest.mark.asyncio
    async def test_connection_health_checks(self, connection_pool):
        """Test connection health checking."""
        endpoint = "ws://test.example.com/ws"
        
        with patch('src.beast_mode.observatory.websocket.connection_pool.WebSocketConnection') as mock_conn_class:
            mock_connection = AsyncMock()
            mock_connection.endpoint = endpoint
            mock_connection.is_connected.return_value = False  # Simulate failed connection
            mock_connection.connect = AsyncMock()
            mock_connection.disconnect = AsyncMock()
            mock_conn_class.return_value = mock_connection
            
            # Add a connection to the pool
            conn = await connection_pool.get_connection(endpoint)
            await connection_pool.return_connection(conn)
            
            # Simulate health check
            await connection_pool._perform_health_checks()
            
            # Verify unhealthy connection was removed
            stats = connection_pool.get_connection_stats()
            assert stats['total_connections'] == 0

    @pytest.mark.asyncio
    async def test_pool_metrics_tracking(self, connection_pool):
        """Test pool metrics tracking."""
        endpoint = "ws://test.example.com/ws"
        
        with patch('src.beast_mode.observatory.websocket.connection_pool.WebSocketConnection') as mock_conn_class:
            mock_connection = AsyncMock()
            mock_connection.endpoint = endpoint
            mock_connection.is_connected.return_value = True
            mock_connection.connect = AsyncMock()
            mock_connection.disconnect = AsyncMock()
            mock_conn_class.return_value = mock_connection
            
            # Get and return connections multiple times
            for _ in range(5):
                conn = await connection_pool.get_connection(endpoint)
                await connection_pool.return_connection(conn)
            
            metrics = connection_pool.get_pool_metrics()
            assert metrics['total_requests'] >= 5
            assert metrics['successful_requests'] >= 5

    @pytest.mark.asyncio
    async def test_pool_exhaustion_handling(self, pool_config):
        """Test handling when pool is exhausted."""
        config = ConnectionPoolConfig(max_connections=1, min_connections=0)
        pool = ConnectionPool(config)
        await pool.initialize()
        
        endpoint = "ws://test.example.com/ws"
        
        with patch('src.beast_mode.observatory.websocket.connection_pool.WebSocketConnection') as mock_conn_class:
            mock_connection = AsyncMock()
            mock_connection.endpoint = endpoint
            mock_connection.is_connected.return_value = True
            mock_connection.connect = AsyncMock()
            mock_connection.disconnect = AsyncMock()
            mock_conn_class.return_value = mock_connection
            
            # Get first connection
            conn1 = await pool.get_connection(endpoint)
            
            # Try to get second connection (should fail)
            with pytest.raises(ConnectionFailedError):
                await pool.get_connection(endpoint)
            
            await pool.close()


class TestMessageOptimizer:
    """Test message optimization functionality."""

    @pytest.fixture
    def optimizer_config(self):
        """Create a test optimizer configuration."""
        return MessageOptimizerConfig(
            batch_timeout=0.1,
            max_batch_size=1024,
            max_batch_count=10,
            enable_compression=True,
            enable_deduplication=True,
            enable_prioritization=True,
            batch_strategy=BatchStrategy.HYBRID,
            priority_threshold=100,
            drop_threshold=0.9,
            max_queue_size=1000,
            compression_threshold=512,
        )

    @pytest.fixture
    async def message_optimizer(self, optimizer_config):
        """Create a test message optimizer."""
        optimizer = MessageOptimizer(optimizer_config)
        await optimizer.initialize()
        yield optimizer
        await optimizer.close()

    @pytest.mark.asyncio
    async def test_message_batching(self, message_optimizer):
        """Test message batching functionality."""
        messages = [
            {"type": "test", "data": f"message_{i}"}
            for i in range(5)
        ]
        
        # Add messages to optimizer
        for message in messages:
            await message_optimizer.add_message(message)
        
        # Wait for batch processing
        await asyncio.sleep(0.2)
        
        metrics = message_optimizer.get_metrics()
        assert metrics['total_messages'] == 5
        assert metrics['batched_messages'] >= 5

    @pytest.mark.asyncio
    async def test_message_prioritization(self, message_optimizer):
        """Test message prioritization."""
        # Add low priority message
        await message_optimizer.add_message(
            {"type": "low_priority", "data": "test"},
            priority=MessagePriority.LOW
        )
        
        # Add critical priority message
        await message_optimizer.add_message(
            {"type": "critical", "data": "urgent"},
            priority=MessagePriority.CRITICAL
        )
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        metrics = message_optimizer.get_metrics()
        assert metrics['total_messages'] == 2

    @pytest.mark.asyncio
    async def test_message_deduplication(self, message_optimizer):
        """Test message deduplication."""
        message = {"type": "duplicate", "data": "test_data"}
        
        # Add same message multiple times
        for _ in range(3):
            await message_optimizer.add_message(message)
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        metrics = message_optimizer.get_metrics()
        assert metrics['total_messages'] == 3
        assert metrics['duplicate_messages'] >= 2

    @pytest.mark.asyncio
    async def test_batch_strategies(self, optimizer_config):
        """Test different batch strategies."""
        strategies = [
            BatchStrategy.TIME_BASED,
            BatchStrategy.SIZE_BASED,
            BatchStrategy.COUNT_BASED,
            BatchStrategy.PRIORITY_BASED,
            BatchStrategy.HYBRID,
        ]
        
        for strategy in strategies:
            config = MessageOptimizerConfig(
                batch_timeout=0.1,
                max_batch_size=1024,
                max_batch_count=10,
                batch_strategy=strategy,
            )
            optimizer = MessageOptimizer(config)
            await optimizer.initialize()
            
            # Test that strategy is set correctly
            assert optimizer.config.batch_strategy == strategy
            
            await optimizer.close()

    @pytest.mark.asyncio
    async def test_queue_capacity_handling(self, optimizer_config):
        """Test handling when queue capacity is exceeded."""
        config = MessageOptimizerConfig(
            max_queue_size=5,
            drop_threshold=0.8,  # Drop when 80% full
        )
        optimizer = MessageOptimizer(config)
        await optimizer.initialize()
        
        # Fill queue beyond threshold
        for i in range(10):
            await optimizer.add_message({"type": "test", "data": f"message_{i}"})
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        metrics = optimizer.get_metrics()
        assert metrics['dropped_messages'] > 0

    @pytest.mark.asyncio
    async def test_optimization_metrics(self, message_optimizer):
        """Test optimization metrics collection."""
        # Add various messages
        for i in range(10):
            await message_optimizer.add_message({
                "type": "test",
                "data": f"message_{i}",
                "timestamp": time.time()
            })
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        metrics = message_optimizer.get_metrics()
        assert 'total_messages' in metrics
        assert 'batched_messages' in metrics
        assert 'avg_batch_size' in metrics
        assert 'messages_per_second' in metrics


class TestCompressionHandler:
    """Test compression and serialization functionality."""

    @pytest.fixture
    def compression_config(self):
        """Create a test compression configuration."""
        return CompressionConfig(
            default_algorithm=CompressionAlgorithm.LZ4,
            default_format=SerializationFormat.MSGPACK,
            compression_threshold=1024,
            max_compression_level=9,
            enable_adaptive_compression=True,
            enable_parallel_compression=True,
            compression_timeout=5.0,
            cache_compressed_data=True,
            cache_size_limit=100,
            enable_compression_metrics=True,
        )

    @pytest.fixture
    def compression_handler(self, compression_config):
        """Create a test compression handler."""
        return CompressionHandler(compression_config)

    @pytest.mark.asyncio
    async def test_message_compression(self, compression_handler):
        """Test message compression."""
        message = {
            "type": "test",
            "data": "This is a test message with some content to compress",
            "metadata": {"timestamp": time.time(), "id": "test_123"},
            "nested": {"level1": {"level2": "deep_value"}}
        }
        
        # Compress message
        result = await compression_handler.compress_message(message)
        
        assert isinstance(result, CompressionResult)
        assert result.original_size > 0
        assert result.compressed_size > 0
        assert result.compression_ratio >= 0
        assert result.algorithm in CompressionAlgorithm
        assert result.serialization_format in SerializationFormat

    @pytest.mark.asyncio
    async def test_message_decompression(self, compression_handler):
        """Test message decompression."""
        original_message = {
            "type": "test",
            "data": "This is a test message for decompression",
            "metadata": {"timestamp": time.time()}
        }
        
        # Compress message
        compressed_result = await compression_handler.compress_message(original_message)
        
        # Decompress message
        decompressed_message = await compression_handler.decompress_message(
            compressed_result.data,
            compressed_result.algorithm,
            compressed_result.serialization_format
        )
        
        assert decompressed_message == original_message

    @pytest.mark.asyncio
    async def test_compression_algorithms(self, compression_handler):
        """Test different compression algorithms."""
        message = {"data": "Test message for algorithm comparison" * 10}
        
        algorithms = [
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.ZLIB,
            CompressionAlgorithm.LZ4,
        ]
        
        results = {}
        for algorithm in algorithms:
            result = await compression_handler.compress_message(message, algorithm=algorithm)
            results[algorithm.value] = result
        
        # Verify all algorithms produced results
        assert len(results) == len(algorithms)
        
        # Verify compression ratios are reasonable
        for algorithm, result in results.items():
            assert result.compression_ratio >= 0
            assert result.compression_ratio <= 1

    @pytest.mark.asyncio
    async def test_serialization_formats(self, compression_handler):
        """Test different serialization formats."""
        message = {
            "string": "test",
            "number": 123,
            "boolean": True,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }
        
        formats = [
            SerializationFormat.JSON,
            SerializationFormat.MSGPACK,
            SerializationFormat.PICKLE,
        ]
        
        results = {}
        for format_type in formats:
            result = await compression_handler.compress_message(message, format_type=format_type)
            results[format_type.value] = result
        
        # Verify all formats produced results
        assert len(results) == len(formats)
        
        # Verify decompression works for all formats
        for format_type, result in results.items():
            decompressed = await compression_handler.decompress_message(
                result.data,
                result.algorithm,
                result.serialization_format
            )
            assert decompressed == message

    @pytest.mark.asyncio
    async def test_batch_compression(self, compression_handler):
        """Test batch compression functionality."""
        messages = [
            {"type": "test", "data": f"message_{i}"}
            for i in range(5)
        ]
        
        # Compress batch
        results = await compression_handler.batch_compress(messages)
        
        assert len(results) == len(messages)
        
        # Verify all results are valid
        for result in results:
            assert isinstance(result, CompressionResult)
            assert result.original_size > 0
            assert result.compressed_size > 0

    @pytest.mark.asyncio
    async def test_compression_threshold(self, compression_config):
        """Test compression threshold behavior."""
        config = CompressionConfig(compression_threshold=1000)
        handler = CompressionHandler(config)
        
        # Small message (below threshold)
        small_message = {"data": "small"}
        small_result = await handler.compress_message(small_message)
        assert small_result.algorithm == CompressionAlgorithm.NONE
        
        # Large message (above threshold)
        large_message = {"data": "large " * 200}  # Make it large
        large_result = await handler.compress_message(large_message)
        assert large_result.algorithm != CompressionAlgorithm.NONE

    @pytest.mark.asyncio
    async def test_compression_metrics(self, compression_handler):
        """Test compression metrics collection."""
        messages = [
            {"type": "test", "data": f"message_{i}"}
            for i in range(10)
        ]
        
        # Compress multiple messages
        for message in messages:
            await compression_handler.compress_message(message)
        
        metrics = compression_handler.get_metrics()
        assert metrics['total_compressions'] == 10
        assert 'avg_compression_ratio' in metrics
        assert 'avg_processing_time' in metrics
        assert 'algorithm_usage' in metrics
        assert 'format_usage' in metrics

    @pytest.mark.asyncio
    async def test_adaptive_compression(self, compression_handler):
        """Test adaptive compression algorithm selection."""
        # Test with different data sizes
        small_data = {"data": "small"}
        large_data = {"data": "large " * 100}
        
        small_result = await compression_handler.compress_message(small_data)
        large_result = await compression_handler.compress_message(large_data)
        
        # Both should have valid results
        assert small_result.compression_ratio >= 0
        assert large_result.compression_ratio >= 0
        
        # Large data should benefit more from compression
        assert large_result.compression_ratio > small_result.compression_ratio

    @pytest.mark.asyncio
    async def test_compression_cache(self, compression_handler):
        """Test compression caching functionality."""
        message = {"data": "test message for caching"}
        
        # First compression (cache miss)
        result1 = await compression_handler.compress_message(message)
        assert result1.metadata.get('cache_hit', True) == False
        
        # Second compression (cache hit)
        result2 = await compression_handler.compress_message(message)
        assert result2.metadata.get('cache_hit', True) == True
        
        # Results should be identical
        assert result1.data == result2.data
        assert result1.compression_ratio == result2.compression_ratio


class TestIntegration:
    """Integration tests for the complete optimization system."""

    @pytest.mark.asyncio
    async def test_end_to_end_optimization(self):
        """Test end-to-end optimization workflow."""
        # Create all components
        pool_config = ConnectionPoolConfig(max_connections=5, min_connections=1)
        optimizer_config = MessageOptimizerConfig(batch_timeout=0.1, max_batch_count=5)
        compression_config = CompressionConfig(compression_threshold=100)
        
        pool = ConnectionPool(pool_config)
        optimizer = MessageOptimizer(optimizer_config)
        compression_handler = CompressionHandler(compression_config)
        
        await pool.initialize()
        await optimizer.initialize()
        
        try:
            # Simulate message flow
            messages = [
                {"type": "data", "payload": f"message_{i}", "timestamp": time.time()}
                for i in range(10)
            ]
            
            # Add messages to optimizer
            for message in messages:
                await optimizer.add_message(message)
            
            # Wait for processing
            await asyncio.sleep(0.2)
            
            # Verify metrics
            pool_metrics = pool.get_pool_metrics()
            optimizer_metrics = optimizer.get_metrics()
            compression_metrics = compression_handler.get_metrics()
            
            assert pool_metrics['total_requests'] >= 0
            assert optimizer_metrics['total_messages'] == 10
            assert compression_metrics['total_compressions'] >= 0
            
        finally:
            await pool.close()
            await optimizer.close()

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test performance under high message load."""
        optimizer_config = MessageOptimizerConfig(
            batch_timeout=0.05,
            max_batch_count=20,
            max_queue_size=1000,
        )
        optimizer = MessageOptimizer(optimizer_config)
        await optimizer.initialize()
        
        try:
            # Send many messages quickly
            start_time = time.time()
            for i in range(100):
                await optimizer.add_message({
                    "type": "load_test",
                    "data": f"message_{i}",
                    "timestamp": time.time()
                })
            
            # Wait for processing
            await asyncio.sleep(0.5)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            metrics = optimizer.get_metrics()
            
            # Verify performance
            assert metrics['total_messages'] == 100
            assert processing_time < 2.0  # Should process quickly
            assert metrics['messages_per_second'] > 50  # Should handle high throughput
            
        finally:
            await optimizer.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])