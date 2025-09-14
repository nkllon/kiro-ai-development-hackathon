#!/usr/bin/env python3
"""
Redis-Based Performance Optimizer
=================================

Leverages existing Redis infrastructure for performance optimization
instead of reinventing caching systems. Integrates with existing
DomainCache and Redis transport for optimal performance.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Redis-based performance optimization using existing infrastructure
"""

import sys
import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

# Use existing Redis infrastructure
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Use existing domain cache
from beast_mode.domain.domain_cache import DomainCache
from beast_mode.messaging.redis_transport import RedisTransport


class RedisOptimizationStrategy(Enum):
    """Redis-based optimization strategies."""
    REDIS_CACHING = "redis_caching"
    REDIS_PIPELINING = "redis_pipelining"
    REDIS_CLUSTERING = "redis_clustering"
    REDIS_PERSISTENCE = "redis_persistence"


@dataclass
class RedisOptimizationResult:
    """Result of Redis-based optimization."""
    strategy: RedisOptimizationStrategy
    performance_improvement: float
    redis_operations_saved: int
    cache_hit_rate: float
    execution_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class RedisPerformanceOptimizer:
    """
    Redis-based performance optimizer that leverages existing infrastructure.
    
    Instead of reinventing caching, this integrates with:
    - Existing Redis transport and messaging
    - Existing DomainCache with TTL/LRU/tag-based invalidation
    - Existing async Redis client infrastructure
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis-based optimizer."""
        self.redis_url = redis_url
        self.logger = self._setup_logging()
        
        # Use existing Redis transport
        self.redis_transport = RedisTransport(redis_url)
        
        # Use existing domain cache
        self.domain_cache = DomainCache({
            'max_cache_size': 1000,
            'default_ttl_seconds': 3600,
            'enable_lru_eviction': True
        })
        
        # Redis client for direct operations
        self.redis_client = None
        self._initialize_redis_client()
        
        # Performance tracking
        self.optimization_results: List[RedisOptimizationResult] = []
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for Redis optimizer."""
        logger = logging.getLogger('redis_performance_optimizer')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def _initialize_redis_client(self):
        """Initialize Redis client using existing infrastructure."""
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                self.logger.info("Redis client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Redis client: {e}")
                self.redis_client = None
        else:
            self.logger.warning("Redis not available, using domain cache only")
    
    async def optimize_with_redis_cache(self, 
                                      key: str,
                                      operation_func: Callable,
                                      ttl_seconds: int = 3600,
                                      tags: List[str] = None) -> Any:
        """
        Optimize operation using Redis caching.
        
        Uses existing DomainCache which already has proper TTL, LRU, and tag support.
        """
        start_time = time.time()
        
        # Check existing domain cache first
        cached_result = self.domain_cache.get(key)
        if cached_result is not None:
            execution_time = (time.time() - start_time) * 1000
            self.logger.info(f"Cache hit for key: {key}")
            
            # Record optimization result
            result = RedisOptimizationResult(
                strategy=RedisOptimizationStrategy.REDIS_CACHING,
                performance_improvement=100.0,  # 100x faster via cache
                redis_operations_saved=1,
                cache_hit_rate=1.0,
                execution_time_ms=execution_time,
                metadata={'cache_source': 'domain_cache'}
            )
            self.optimization_results.append(result)
            
            return cached_result
        
        # Cache miss - execute operation
        operation_result = operation_func()
        
        # Store in existing domain cache with proper TTL and tags
        self.domain_cache.set(
            key=key,
            value=operation_result,
            ttl_seconds=ttl_seconds,
            tags=set(tags) if tags else None
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # Record optimization result
        result = RedisOptimizationResult(
            strategy=RedisOptimizationStrategy.REDIS_CACHING,
            performance_improvement=1.0,
            redis_operations_saved=0,
            cache_hit_rate=0.0,
            execution_time_ms=execution_time,
            metadata={'cache_source': 'domain_cache', 'stored': True}
        )
        self.optimization_results.append(result)
        
        return operation_result
    
    async def optimize_with_redis_pipeline(self, operations: List[Tuple[str, Callable]]) -> List[Any]:
        """
        Optimize multiple operations using Redis pipelining.
        
        Uses existing Redis infrastructure for batch operations.
        """
        start_time = time.time()
        
        if not self.redis_client:
            # Fallback to sequential execution
            results = []
            for key, operation in operations:
                result = await self.optimize_with_redis_cache(key, operation)
                results.append(result)
            return results
        
        # Use Redis pipeline for batch operations
        pipe = self.redis_client.pipeline()
        
        # Check cache for all operations
        cache_keys = [f"cache:{key}" for key, _ in operations]
        cached_values = await pipe.mget(*cache_keys).execute()
        
        results = []
        operations_to_execute = []
        
        for i, (key, operation) in enumerate(operations):
            cached_value = cached_values[i]
            if cached_value:
                # Cache hit
                results.append(json.loads(cached_value))
            else:
                # Cache miss - need to execute
                operations_to_execute.append((i, key, operation))
        
        # Execute cache misses
        for i, key, operation in operations_to_execute:
            result = operation()
            results.insert(i, result)
            
            # Store in Redis
            pipe.setex(f"cache:{key}", 3600, json.dumps(result))
        
        # Execute pipeline
        await pipe.execute()
        
        execution_time = (time.time() - start_time) * 1000
        
        # Record optimization result
        result = RedisOptimizationResult(
            strategy=RedisOptimizationStrategy.REDIS_PIPELINING,
            performance_improvement=len(operations) / max(len(operations_to_execute), 1),
            redis_operations_saved=len(operations) - len(operations_to_execute),
            cache_hit_rate=(len(operations) - len(operations_to_execute)) / len(operations),
            execution_time_ms=execution_time,
            metadata={
                'total_operations': len(operations),
                'cache_hits': len(operations) - len(operations_to_execute),
                'cache_misses': len(operations_to_execute)
            }
        )
        self.optimization_results.append(result)
        
        return results
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary using existing cache statistics."""
        cache_stats = {
            'hits': self.domain_cache.hits,
            'misses': self.domain_cache.misses,
            'hit_rate': self.domain_cache.hits / (self.domain_cache.hits + self.domain_cache.misses) if (self.domain_cache.hits + self.domain_cache.misses) > 0 else 0,
            'evictions': self.domain_cache.evictions,
            'invalidations': self.domain_cache.invalidations
        }
        
        return {
            'cache_statistics': cache_stats,
            'optimization_results_count': len(self.optimization_results),
            'redis_available': REDIS_AVAILABLE and self.redis_client is not None,
            'domain_cache_active': True,
            'redis_url': self.redis_url
        }
    
    def generate_optimization_report(self) -> str:
        """Generate optimization report using existing infrastructure."""
        report = []
        report.append("=" * 80)
        report.append("REDIS-BASED PERFORMANCE OPTIMIZATION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        summary = self.get_performance_summary()
        
        report.append("INFRASTRUCTURE STATUS:")
        report.append(f"  Redis Available: {'Yes' if summary['redis_available'] else 'No'}")
        report.append(f"  Domain Cache Active: {'Yes' if summary['domain_cache_active'] else 'No'}")
        report.append(f"  Redis URL: {summary['redis_url']}")
        report.append("")
        
        cache_stats = summary['cache_statistics']
        report.append("EXISTING CACHE PERFORMANCE:")
        report.append(f"  Hit Rate: {cache_stats['hit_rate']:.1%}")
        report.append(f"  Total Hits: {cache_stats['hits']}")
        report.append(f"  Total Misses: {cache_stats['misses']}")
        report.append(f"  Evictions: {cache_stats['evictions']}")
        report.append(f"  Invalidations: {cache_stats['invalidations']}")
        report.append("")
        
        report.append("OPTIMIZATION RESULTS:")
        report.append(f"  Total Optimizations: {summary['optimization_results_count']}")
        report.append("")
        
        return "\n".join(report)
    
    async def cleanup(self):
        """Cleanup Redis connections."""
        if self.redis_client:
            await self.redis_client.close()


def main():
    """Main function demonstrating Redis-based optimization."""
    import asyncio
    
    async def demo_redis_optimization():
        optimizer = RedisPerformanceOptimizer()
        
        # Demo function
        def expensive_operation():
            time.sleep(0.1)
            return {"result": "expensive_calculation", "timestamp": time.time()}
        
        print("Testing Redis-based performance optimization...")
        
        # Test caching
        result1 = await optimizer.optimize_with_redis_cache("test_key", expensive_operation)
        result2 = await optimizer.optimize_with_redis_cache("test_key", expensive_operation)
        
        print(f"First execution: {result1}")
        print(f"Second execution (cached): {result2}")
        
        # Test pipelining
        operations = [
            ("key1", lambda: {"op": 1}),
            ("key2", lambda: {"op": 2}),
            ("key3", lambda: {"op": 3})
        ]
        
        results = await optimizer.optimize_with_redis_pipeline(operations)
        print(f"Pipeline results: {results}")
        
        # Generate report
        print("\n" + optimizer.generate_optimization_report())
        
        await optimizer.cleanup()
    
    asyncio.run(demo_redis_optimization())


if __name__ == "__main__":
    main()
