"""
Performance Optimization Module for Spec Framework
=================================================

Provides comprehensive performance optimization capabilities including:
- Intelligent caching with LRU eviction
- Parallel processing for large specifications
- Performance monitoring and metrics
- Memory optimization
- Graceful degradation

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

from .performance_optimizer import (
    PerformanceOptimizer,
    PerformanceMetrics,
    CacheEntry,
    get_performance_optimizer,
    performance_monitor,
    cached_operation,
    parallel_process
)

__all__ = [
    'PerformanceOptimizer',
    'PerformanceMetrics', 
    'CacheEntry',
    'get_performance_optimizer',
    'performance_monitor',
    'cached_operation',
    'parallel_process'
]