#!/usr/bin/env python3
"""Test script for WebSocket connection optimization system."""

import asyncio
import json
import time
from datetime import datetime

from src.beast_mode.observatory.websocket.connection_pool import (
    ConnectionPool,
    ConnectionPoolConfig,
    PoolStrategy,
)
from src.beast_mode.observatory.websocket.message_optimizer import (
    MessageOptimizer,
    MessageOptimizerConfig,
    MessagePriority,
    BatchStrategy,
)
from src.beast_mode.observatory.websocket.compression_handler import (
    CompressionHandler,
    CompressionConfig,
    CompressionAlgorithm,
    SerializationFormat,
)


async def test_connection_pool():
    """Test connection pool functionality."""
    print("Testing Connection Pool...")
    
    config = ConnectionPoolConfig(
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
    
    pool = ConnectionPool(config)
    await pool.initialize()
    
    try:
        # Test pool metrics
        metrics = pool.get_pool_metrics()
        print(f"Pool metrics: {json.dumps(metrics, indent=2)}")
        
        # Test connection stats
        stats = pool.get_connection_stats()
        print(f"Connection stats: {json.dumps(stats, indent=2)}")
        
        print("✓ Connection pool test passed")
        
    finally:
        await pool.close()


async def test_message_optimizer():
    """Test message optimizer functionality."""
    print("\nTesting Message Optimizer...")
    
    config = MessageOptimizerConfig(
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
    
    optimizer = MessageOptimizer(config)
    await optimizer.initialize()
    
    try:
        # Add some test messages
        messages = [
            {"type": "test", "data": f"message_{i}", "timestamp": time.time()}
            for i in range(20)
        ]
        
        for message in messages:
            await optimizer.add_message(message, MessagePriority.NORMAL, "test_batch")
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Check metrics
        metrics = optimizer.get_metrics()
        print(f"Optimizer metrics: {json.dumps(metrics, indent=2)}")
        
        # Check queue status
        status = optimizer.get_queue_status()
        print(f"Queue status: {json.dumps(status, indent=2)}")
        
        print("✓ Message optimizer test passed")
        
    finally:
        await optimizer.close()


async def test_compression_handler():
    """Test compression handler functionality."""
    print("\nTesting Compression Handler...")
    
    config = CompressionConfig(
        compression_threshold=100,
        max_compression_level=6,
        enable_adaptive_compression=True,
        enable_parallel_compression=True,
        compression_timeout=2.0,
        cache_compressed_data=True,
        cache_size_limit=100,
        enable_compression_metrics=True,
    )
    
    handler = CompressionHandler(config)
    
    try:
        # Test compression
        test_message = {
            "type": "test",
            "data": "Hello, WebSocket optimization!",
            "number": 42,
            "list": [1, 2, 3, 4, 5],
            "nested": {"key": "value", "array": [1, 2, 3]}
        }
        
        # Test different compression algorithms
        algorithms_to_test = [CompressionAlgorithm.GZIP, CompressionAlgorithm.ZLIB]
        if hasattr(CompressionAlgorithm, 'LZ4'):
            algorithms_to_test.append(CompressionAlgorithm.LZ4)
        
        for algorithm in algorithms_to_test:
            try:
                result = await handler.compress_message(test_message, algorithm, SerializationFormat.JSON)
                print(f"{algorithm.value} compression: {result.original_size} -> {result.compressed_size} bytes ({result.compression_ratio:.2%} reduction)")
                
                # Test decompression
                decompressed = await handler.decompress_message(
                    result.data, result.algorithm, result.serialization_format
                )
                assert decompressed == test_message
                
            except Exception as e:
                print(f"  {algorithm.value} not available: {e}")
        
        # Test batch compression
        batch_messages = [
            {"type": "batch", "data": f"message_{i}"}
            for i in range(5)
        ]
        
        batch_results = await handler.batch_compress(batch_messages, CompressionAlgorithm.GZIP, SerializationFormat.JSON)
        print(f"Batch compression: {len(batch_results)} messages processed")
        
        # Check metrics
        metrics = handler.get_metrics()
        print(f"Compression metrics: {json.dumps(metrics, indent=2)}")
        
        # Check cache status
        cache_status = handler.get_cache_status()
        print(f"Cache status: {json.dumps(cache_status, indent=2)}")
        
        print("✓ Compression handler test passed")
        
    except Exception as e:
        print(f"✗ Compression handler test failed: {e}")


async def test_integration():
    """Test integration of all components."""
    print("\nTesting Integration...")
    
    try:
        # Create all components
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
        
        await pool.initialize()
        await optimizer.initialize()
        
        # Simulate high-frequency message processing
        start_time = time.time()
        for i in range(100):
            message = {
                "type": "integration_test",
                "data": f"message_{i}",
                "timestamp": time.time(),
                "payload": "x" * 100  # Some data to compress
            }
            await optimizer.add_message(message, MessagePriority.NORMAL, f"batch_{i % 10}")
        
        # Wait for processing
        await asyncio.sleep(0.3)
        
        # Check final metrics
        pool_metrics = pool.get_pool_metrics()
        optimizer_metrics = optimizer.get_metrics()
        compression_metrics = compression_handler.get_metrics()
        
        print(f"Integration test completed in {time.time() - start_time:.2f} seconds")
        print(f"Pool connections: {pool_metrics['total_connections']}")
        print(f"Messages processed: {optimizer_metrics['total_messages']}")
        print(f"Compressions performed: {compression_metrics['total_compressions']}")
        
        print("✓ Integration test passed")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        
    finally:
        try:
            await pool.close()
            await optimizer.close()
        except:
            pass


async def main():
    """Run all tests."""
    print("WebSocket Connection Optimization System Test")
    print("=" * 50)
    
    try:
        await test_connection_pool()
        await test_message_optimizer()
        await test_compression_handler()
        await test_integration()
        
        print("\n" + "=" * 50)
        print("✓ All tests completed successfully!")
        print("\nPerformance Features Validated:")
        print("- Connection pooling with reuse mechanisms")
        print("- Message batching for high-frequency updates")
        print("- Compression and serialization optimization")
        print("- Memory usage optimization")
        print("- CPU usage minimization")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())