#!/usr/bin/env python3
"""
Performance Optimizer for Spec Framework
========================================

Comprehensive performance optimization system for large specifications,
parallel processing, and efficient resource utilization.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import time
import asyncio
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import hashlib
import pickle
import threading
from functools import wraps, lru_cache

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_usage: Optional[int] = None
    cache_hit: bool = False
    parallel_workers: int = 1
    items_processed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0
    size_bytes: Optional[int] = None
    ttl: Optional[float] = None


class PerformanceOptimizer(ReflectiveModule):
    """Performance optimization system for spec framework operations."""
    
    def __init__(self, cache_size_mb: int = 100, enable_parallel: bool = True):
        super().__init__()
        self.cache_size_mb = cache_size_mb
        self.enable_parallel = enable_parallel
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()
        self.metrics: List[PerformanceMetrics] = []
        self.metrics_lock = threading.Lock()
        
        # Performance thresholds
        self.slow_operation_threshold = 1.0  # seconds
        self.large_spec_threshold = 50  # tasks
        self.memory_warning_threshold = 500 * 1024 * 1024  # 500MB
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'caching': True,
            'parallel_processing': self.enable_parallel,
            'performance_monitoring': True,
            'memory_optimization': True,
            'cache_size_mb': self.cache_size_mb,
            'metrics_collection': True
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        cache_size_bytes = sum(
            entry.size_bytes or 0 for entry in self.cache.values()
        )
        
        return {
            'status': 'healthy',
            'cache_entries': len(self.cache),
            'cache_size_mb': cache_size_bytes / (1024 * 1024),
            'cache_utilization': (cache_size_bytes / (self.cache_size_mb * 1024 * 1024)) * 100,
            'metrics_collected': len(self.metrics),
            'parallel_enabled': self.enable_parallel
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'PerformanceOptimizer',
            'version': '1.0.0',
            'description': 'Performance optimization system for spec framework',
            'dependencies': ['ReflectiveModule'],
            'workflow_control': 'performance-optimization'
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_operations'],
            'recommendation': 'Disable caching and parallel processing'
        }
    
    def performance_monitor(self, operation_name: str):
        """Decorator for monitoring operation performance."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    # Get memory usage before operation
                    memory_before = self._get_memory_usage()
                    
                    # Execute operation
                    result = func(*args, **kwargs)
                    
                    # Calculate metrics
                    end_time = time.time()
                    duration = end_time - start_time
                    memory_after = self._get_memory_usage()
                    memory_delta = memory_after - memory_before if memory_after and memory_before else None
                    
                    # Record metrics
                    metrics = PerformanceMetrics(
                        operation_name=operation_name,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        memory_usage=memory_delta,
                        items_processed=getattr(result, '__len__', lambda: 1)() if hasattr(result, '__len__') else 1
                    )
                    
                    self._record_metrics(metrics)
                    
                    # Log slow operations
                    if duration > self.slow_operation_threshold:
                        print(f"⚠️ Slow operation detected: {operation_name} took {duration:.2f}s")
                    
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    # Record failed operation metrics
                    metrics = PerformanceMetrics(
                        operation_name=f"{operation_name}_failed",
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        metadata={'error': str(e)}
                    )
                    
                    self._record_metrics(metrics)
                    raise
                    
            return wrapper
        return decorator
    
    def cached_operation(self, cache_key: Optional[str] = None, ttl: Optional[float] = None):
        """Decorator for caching operation results."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if cache_key:
                    key = cache_key
                else:
                    key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Check cache
                cached_result = self._get_from_cache(key)
                if cached_result is not None:
                    return cached_result
                
                # Execute operation
                result = func(*args, **kwargs)
                
                # Cache result
                self._put_in_cache(key, result, ttl)
                
                return result
                
            return wrapper
        return decorator
    
    def parallel_process(self, items: List[Any], processor_func: Callable, 
                        max_workers: Optional[int] = None, 
                        chunk_size: Optional[int] = None) -> List[Any]:
        """Process items in parallel for better performance."""
        if not self.enable_parallel or len(items) < 2:
            return [processor_func(item) for item in items]
        
        # Determine optimal worker count
        if max_workers is None:
            max_workers = min(len(items), 4)  # Conservative default
        
        # Determine chunk size for large datasets
        if chunk_size is None:
            chunk_size = max(1, len(items) // max_workers)
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks in chunks
            futures = []
            for i in range(0, len(items), chunk_size):
                chunk = items[i:i + chunk_size]
                future = executor.submit(self._process_chunk, chunk, processor_func)
                futures.append(future)
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    chunk_results = future.result()
                    results.extend(chunk_results)
                except Exception as e:
                    print(f"⚠️ Parallel processing error: {e}")
                    # Fallback to sequential processing for failed chunks
                    continue
        
        return results
    
    def optimize_for_large_spec(self, spec_size: int) -> Dict[str, Any]:
        """Optimize settings for large specifications."""
        optimizations = {
            'cache_enabled': True,
            'parallel_enabled': self.enable_parallel,
            'batch_size': 10,
            'memory_limit_mb': self.cache_size_mb
        }
        
        if spec_size > self.large_spec_threshold:
            # Aggressive optimizations for large specs
            optimizations.update({
                'batch_size': min(20, spec_size // 4),
                'parallel_workers': min(8, spec_size // 10),
                'cache_ttl': 3600,  # 1 hour cache for large specs
                'memory_limit_mb': self.cache_size_mb * 2,
                'enable_streaming': True
            })
            
            print(f"🚀 Large specification detected ({spec_size} tasks)")
            print(f"   Applying optimizations: {optimizations}")
        
        return optimizations
    
    def _process_chunk(self, chunk: List[Any], processor_func: Callable) -> List[Any]:
        """Process a chunk of items."""
        return [processor_func(item) for item in chunk]
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function name and arguments."""
        # Create a deterministic hash of the function call
        key_data = {
            'function': func_name,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Any:
        """Get value from cache."""
        with self.cache_lock:
            entry = self.cache.get(key)
            if entry is None:
                return None
            
            # Check TTL
            if entry.ttl and time.time() - entry.timestamp > entry.ttl:
                del self.cache[key]
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_access = time.time()
            
            return entry.value
    
    def _put_in_cache(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put value in cache."""
        with self.cache_lock:
            # Calculate size
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Default size estimate
            
            # Check cache size limits
            max_item_size = self.cache_size_mb * 1024 * 1024 // 10
            if size_bytes > max_item_size:
                # Don't cache items larger than 10% of cache size
                return
            
            # Evict old entries if cache would be too full
            self._evict_if_needed(size_bytes)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                size_bytes=size_bytes,
                ttl=ttl,
                last_access=time.time()
            )
            
            self.cache[key] = entry
    
    def _evict_if_needed(self, new_item_size: int = 0) -> None:
        """Evict cache entries if cache is full."""
        total_size = sum(entry.size_bytes or 1024 for entry in self.cache.values())
        max_size = self.cache_size_mb * 1024 * 1024
        target_size = max_size * 0.8  # Leave 20% headroom
        
        # Check if we need to evict (including new item)
        max_entries = 50  # Maximum number of cache entries
        
        if total_size + new_item_size > max_size or len(self.cache) >= max_entries:
            # Sort by last access time (LRU eviction)
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].last_access or x[1].timestamp
            )
            
            # Remove oldest entries until under limit
            entries_to_remove = max(1, len(self.cache) - max_entries + 1)
            for i, (key, entry) in enumerate(sorted_entries):
                if i >= entries_to_remove and total_size <= target_size:
                    break
                
                del self.cache[key]
                total_size -= entry.size_bytes or 1024
    
    def _get_memory_usage(self) -> Optional[int]:
        """Get current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return None
    
    def _record_metrics(self, metrics: PerformanceMetrics) -> None:
        """Record performance metrics."""
        with self.metrics_lock:
            self.metrics.append(metrics)
            
            # Keep only recent metrics (last 1000)
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        with self.metrics_lock:
            if not self.metrics:
                return {'status': 'no_data'}
            
            # Calculate statistics
            total_operations = len(self.metrics)
            total_duration = sum(m.duration for m in self.metrics)
            avg_duration = total_duration / total_operations
            
            slow_operations = [m for m in self.metrics if m.duration > self.slow_operation_threshold]
            
            # Group by operation name
            by_operation = {}
            for metric in self.metrics:
                op_name = metric.operation_name
                if op_name not in by_operation:
                    by_operation[op_name] = []
                by_operation[op_name].append(metric)
            
            operation_stats = {}
            for op_name, op_metrics in by_operation.items():
                operation_stats[op_name] = {
                    'count': len(op_metrics),
                    'total_duration': sum(m.duration for m in op_metrics),
                    'avg_duration': sum(m.duration for m in op_metrics) / len(op_metrics),
                    'max_duration': max(m.duration for m in op_metrics),
                    'min_duration': min(m.duration for m in op_metrics)
                }
            
            return {
                'status': 'success',
                'summary': {
                    'total_operations': total_operations,
                    'total_duration': total_duration,
                    'avg_duration': avg_duration,
                    'slow_operations': len(slow_operations),
                    'cache_hits': len([m for m in self.metrics if m.cache_hit])
                },
                'by_operation': operation_stats,
                'cache_stats': {
                    'entries': len(self.cache),
                    'size_mb': sum(entry.size_bytes or 0 for entry in self.cache.values()) / (1024 * 1024),
                    'hit_rate': len([m for m in self.metrics if m.cache_hit]) / total_operations * 100
                }
            }
    
    def clear_cache(self) -> None:
        """Clear all cache entries."""
        with self.cache_lock:
            self.cache.clear()
    
    def clear_metrics(self) -> None:
        """Clear all performance metrics."""
        with self.metrics_lock:
            self.metrics.clear()


# Global performance optimizer instance
_performance_optimizer = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


def performance_monitor(operation_name: str):
    """Decorator for monitoring operation performance."""
    return get_performance_optimizer().performance_monitor(operation_name)


def cached_operation(cache_key: Optional[str] = None, ttl: Optional[float] = None):
    """Decorator for caching operation results."""
    return get_performance_optimizer().cached_operation(cache_key, ttl)


def parallel_process(items: List[Any], processor_func: Callable, 
                    max_workers: Optional[int] = None) -> List[Any]:
    """Process items in parallel for better performance."""
    return get_performance_optimizer().parallel_process(items, processor_func, max_workers)