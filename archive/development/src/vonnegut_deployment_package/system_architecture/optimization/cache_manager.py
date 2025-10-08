#!/usr/bin/env python3
"""
Cache Manager - Phase 5 Task 5.4 Component

Implements caching strategies for frequently accessed documentation
with intelligent cache invalidation and performance optimization.
"""

import asyncio
import json
import hashlib
import time
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class CacheStrategy(Enum):
    """Cache eviction strategies."""
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used
    TTL = "ttl"              # Time To Live
    ADAPTIVE = "adaptive"     # Adaptive based on access patterns


@dataclass
class CacheEntry:
    """Represents a cache entry."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = None


@dataclass
class CacheStats:
    """Cache performance statistics."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        return self.cache_hits / self.total_requests if self.total_requests > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        return self.cache_misses / self.total_requests if self.total_requests > 0 else 0.0


class CacheManager(ReflectiveModule):
    """
    Intelligent cache manager for documentation generation.
    
    Provides multiple caching strategies with automatic invalidation,
    performance monitoring, and optimization recommendations.
    """
    
    def __init__(self, max_size_mb: int = 1024, strategy: CacheStrategy = CacheStrategy.ADAPTIVE):
        super().__init__()
        self.max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
        self.strategy = strategy
        self.cache: Dict[str, CacheEntry] = {}
        self.stats = CacheStats()
        self.lock = threading.RLock()
        
        # Cache configuration
        self.default_ttl_seconds = 3600  # 1 hour
        self.cleanup_interval_seconds = 300  # 5 minutes
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Persistence
        self.persistent_cache_file = Path("cache/documentation_cache.pkl")
        self.persistent_cache_file.parent.mkdir(exist_ok=True)
        
        # Access pattern tracking for adaptive strategy
        self.access_patterns: Dict[str, List[datetime]] = {}
        self.invalidation_callbacks: List[Callable[[str], None]] = []
        
        # Load persistent cache
        self._load_persistent_cache()
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Register capabilities
        self.register_capability('cache_management', {
            'description': 'Intelligent caching for documentation generation',
            'max_size_mb': max_size_mb,
            'strategy': strategy.value,
            'persistent_cache': True
        })
    
    def _calculate_entry_size(self, value: Any) -> int:
        """Calculate the size of a cache entry in bytes."""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (dict, list)):
                return len(json.dumps(value, default=str).encode('utf-8'))
            elif isinstance(value, bytes):
                return len(value)
            else:
                # Use pickle to estimate size for other objects
                return len(pickle.dumps(value))
        except Exception:
            # Fallback estimation
            return 1024  # 1KB default
    
    def _generate_cache_key(self, namespace: str, identifier: str, 
                          parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a consistent cache key."""
        key_parts = [namespace, identifier]
        
        if parameters:
            # Sort parameters for consistent key generation
            param_str = json.dumps(parameters, sort_keys=True, default=str)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            key_parts.append(param_hash)
        
        return ":".join(key_parts)
    
    async def get(self, namespace: str, identifier: str, 
                 parameters: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Get value from cache."""
        key = self._generate_cache_key(namespace, identifier, parameters)
        
        with self.lock:
            self.stats.total_requests += 1
            
            if key not in self.cache:
                self.stats.cache_misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check TTL expiration
            if entry.ttl_seconds:
                age_seconds = (datetime.now() - entry.created_at).total_seconds()
                if age_seconds > entry.ttl_seconds:
                    # Entry expired
                    del self.cache[key]
                    self.stats.cache_misses += 1
                    self.stats.entry_count -= 1
                    self.stats.total_size_bytes -= entry.size_bytes
                    return None
            
            # Update access statistics
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            # Track access pattern for adaptive strategy
            if key not in self.access_patterns:
                self.access_patterns[key] = []
            self.access_patterns[key].append(datetime.now())
            
            # Keep only recent access history (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.access_patterns[key] = [
                access_time for access_time in self.access_patterns[key]
                if access_time > cutoff_time
            ]
            
            self.stats.cache_hits += 1
            
            self.logger.debug(f"Cache hit for key: {key}")
            return entry.value
    
    async def set(self, namespace: str, identifier: str, value: Any,
                 parameters: Optional[Dict[str, Any]] = None,
                 ttl_seconds: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Set value in cache."""
        key = self._generate_cache_key(namespace, identifier, parameters)
        
        with self.lock:
            # Calculate entry size
            size_bytes = self._calculate_entry_size(value)
            
            # Check if we need to make space
            if not await self._ensure_space(size_bytes):
                self.logger.warning(f"Could not make space for cache entry: {key}")
                return False
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds or self.default_ttl_seconds,
                metadata=metadata or {}
            )
            
            # Remove existing entry if present
            if key in self.cache:
                old_entry = self.cache[key]
                self.stats.total_size_bytes -= old_entry.size_bytes
                self.stats.entry_count -= 1
            
            # Add new entry
            self.cache[key] = entry
            self.stats.total_size_bytes += size_bytes
            self.stats.entry_count += 1
            
            self.logger.debug(f"Cache set for key: {key} (size: {size_bytes} bytes)")
            return True
    
    async def _ensure_space(self, required_bytes: int) -> bool:
        """Ensure there's enough space in the cache."""
        # Check if we have enough space
        if self.stats.total_size_bytes + required_bytes <= self.max_size_bytes:
            return True
        
        # Need to evict entries
        bytes_to_free = (self.stats.total_size_bytes + required_bytes) - self.max_size_bytes
        bytes_freed = 0
        
        # Get eviction candidates based on strategy
        candidates = self._get_eviction_candidates()
        
        for key in candidates:
            if bytes_freed >= bytes_to_free:
                break
            
            if key in self.cache:
                entry = self.cache[key]
                bytes_freed += entry.size_bytes
                
                # Remove from cache
                del self.cache[key]
                self.stats.total_size_bytes -= entry.size_bytes
                self.stats.entry_count -= 1
                self.stats.evictions += 1
                
                # Remove access pattern
                if key in self.access_patterns:
                    del self.access_patterns[key]
                
                self.logger.debug(f"Evicted cache entry: {key} (freed {entry.size_bytes} bytes)")
        
        return bytes_freed >= bytes_to_free
    
    def _get_eviction_candidates(self) -> List[str]:
        """Get list of cache keys to evict based on strategy."""
        if not self.cache:
            return []
        
        if self.strategy == CacheStrategy.LRU:
            # Least Recently Used
            return sorted(self.cache.keys(), 
                         key=lambda k: self.cache[k].last_accessed)
        
        elif self.strategy == CacheStrategy.LFU:
            # Least Frequently Used
            return sorted(self.cache.keys(), 
                         key=lambda k: self.cache[k].access_count)
        
        elif self.strategy == CacheStrategy.TTL:
            # Oldest entries first
            return sorted(self.cache.keys(), 
                         key=lambda k: self.cache[k].created_at)
        
        elif self.strategy == CacheStrategy.ADAPTIVE:
            # Adaptive strategy based on access patterns
            return self._get_adaptive_eviction_candidates()
        
        else:
            # Default to LRU
            return sorted(self.cache.keys(), 
                         key=lambda k: self.cache[k].last_accessed)
    
    def _get_adaptive_eviction_candidates(self) -> List[str]:
        """Get eviction candidates using adaptive strategy."""
        candidates = []
        
        for key, entry in self.cache.items():
            # Calculate adaptive score based on multiple factors
            score = 0.0
            
            # Factor 1: Recency (higher score = more recent)
            age_hours = (datetime.now() - entry.last_accessed).total_seconds() / 3600
            recency_score = max(0, 1.0 - (age_hours / 24.0))  # Decay over 24 hours
            
            # Factor 2: Frequency (higher score = more frequent)
            frequency_score = min(1.0, entry.access_count / 10.0)  # Normalize to 10 accesses
            
            # Factor 3: Access pattern (higher score = more regular access)
            pattern_score = 0.0
            if key in self.access_patterns and len(self.access_patterns[key]) > 1:
                # Calculate access regularity
                accesses = self.access_patterns[key]
                if len(accesses) >= 3:
                    intervals = []
                    for i in range(1, len(accesses)):
                        interval = (accesses[i] - accesses[i-1]).total_seconds()
                        intervals.append(interval)
                    
                    # Regular access patterns get higher scores
                    if intervals:
                        avg_interval = sum(intervals) / len(intervals)
                        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
                        regularity = 1.0 / (1.0 + variance / (avg_interval ** 2))
                        pattern_score = regularity
            
            # Factor 4: Size penalty (larger entries get lower scores)
            size_penalty = min(1.0, entry.size_bytes / (1024 * 1024))  # Penalty for entries > 1MB
            
            # Combine factors (higher score = keep in cache)
            adaptive_score = (recency_score * 0.4 + 
                            frequency_score * 0.3 + 
                            pattern_score * 0.2 - 
                            size_penalty * 0.1)
            
            candidates.append((key, adaptive_score))
        
        # Sort by score (lowest first for eviction)
        candidates.sort(key=lambda x: x[1])
        return [key for key, score in candidates]
    
    async def invalidate(self, namespace: str, identifier: str = None,
                        parameters: Optional[Dict[str, Any]] = None) -> int:
        """Invalidate cache entries."""
        with self.lock:
            if identifier:
                # Invalidate specific entry
                key = self._generate_cache_key(namespace, identifier, parameters)
                if key in self.cache:
                    entry = self.cache[key]
                    del self.cache[key]
                    self.stats.total_size_bytes -= entry.size_bytes
                    self.stats.entry_count -= 1
                    
                    if key in self.access_patterns:
                        del self.access_patterns[key]
                    
                    # Notify callbacks
                    for callback in self.invalidation_callbacks:
                        try:
                            callback(key)
                        except Exception as e:
                            self.logger.error(f"Error in invalidation callback: {e}")
                    
                    self.logger.debug(f"Invalidated cache entry: {key}")
                    return 1
                return 0
            else:
                # Invalidate all entries in namespace
                keys_to_remove = [key for key in self.cache.keys() if key.startswith(f"{namespace}:")]
                removed_count = 0
                
                for key in keys_to_remove:
                    entry = self.cache[key]
                    del self.cache[key]
                    self.stats.total_size_bytes -= entry.size_bytes
                    self.stats.entry_count -= 1
                    removed_count += 1
                    
                    if key in self.access_patterns:
                        del self.access_patterns[key]
                    
                    # Notify callbacks
                    for callback in self.invalidation_callbacks:
                        try:
                            callback(key)
                        except Exception as e:
                            self.logger.error(f"Error in invalidation callback: {e}")
                
                self.logger.info(f"Invalidated {removed_count} cache entries in namespace: {namespace}")
                return removed_count
    
    async def clear(self) -> int:
        """Clear all cache entries."""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            self.access_patterns.clear()
            self.stats = CacheStats()
            
            self.logger.info(f"Cleared all cache entries: {count}")
            return count
    
    async def _cleanup_loop(self):
        """Periodic cleanup of expired entries."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_seconds)
                await self._cleanup_expired_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cache cleanup loop: {e}")
    
    async def _cleanup_expired_entries(self):
        """Remove expired cache entries."""
        with self.lock:
            current_time = datetime.now()
            expired_keys = []
            
            for key, entry in self.cache.items():
                if entry.ttl_seconds:
                    age_seconds = (current_time - entry.created_at).total_seconds()
                    if age_seconds > entry.ttl_seconds:
                        expired_keys.append(key)
            
            # Remove expired entries
            for key in expired_keys:
                entry = self.cache[key]
                del self.cache[key]
                self.stats.total_size_bytes -= entry.size_bytes
                self.stats.entry_count -= 1
                
                if key in self.access_patterns:
                    del self.access_patterns[key]
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _load_persistent_cache(self):
        """Load cache from persistent storage."""
        try:
            if self.persistent_cache_file.exists():
                with open(self.persistent_cache_file, 'rb') as f:
                    data = pickle.load(f)
                    
                    # Restore cache entries that haven't expired
                    current_time = datetime.now()
                    loaded_count = 0
                    
                    for key, entry_data in data.get('cache', {}).items():
                        entry = CacheEntry(**entry_data)
                        
                        # Check if entry is still valid
                        if entry.ttl_seconds:
                            age_seconds = (current_time - entry.created_at).total_seconds()
                            if age_seconds > entry.ttl_seconds:
                                continue  # Skip expired entry
                        
                        self.cache[key] = entry
                        self.stats.total_size_bytes += entry.size_bytes
                        self.stats.entry_count += 1
                        loaded_count += 1
                    
                    # Restore access patterns
                    self.access_patterns = data.get('access_patterns', {})
                    
                    # Clean up old access patterns
                    cutoff_time = current_time - timedelta(hours=24)
                    for key in list(self.access_patterns.keys()):
                        self.access_patterns[key] = [
                            access_time for access_time in self.access_patterns[key]
                            if isinstance(access_time, datetime) and access_time > cutoff_time
                        ]
                        if not self.access_patterns[key]:
                            del self.access_patterns[key]
                    
                    self.logger.info(f"Loaded {loaded_count} cache entries from persistent storage")
        
        except Exception as e:
            self.logger.warning(f"Could not load persistent cache: {e}")
    
    async def save_persistent_cache(self):
        """Save cache to persistent storage."""
        try:
            # Prepare data for serialization
            cache_data = {}
            for key, entry in self.cache.items():
                cache_data[key] = asdict(entry)
            
            data = {
                'cache': cache_data,
                'access_patterns': self.access_patterns,
                'saved_at': datetime.now().isoformat()
            }
            
            # Save to file
            with open(self.persistent_cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            self.logger.debug(f"Saved {len(self.cache)} cache entries to persistent storage")
            
        except Exception as e:
            self.logger.error(f"Could not save persistent cache: {e}")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self.lock:
            # Calculate additional statistics
            if self.cache:
                entry_sizes = [entry.size_bytes for entry in self.cache.values()]
                access_counts = [entry.access_count for entry in self.cache.values()]
                ages = [(datetime.now() - entry.created_at).total_seconds() / 3600 
                       for entry in self.cache.values()]
                
                size_stats = {
                    'min_size_bytes': min(entry_sizes),
                    'max_size_bytes': max(entry_sizes),
                    'avg_size_bytes': sum(entry_sizes) / len(entry_sizes)
                }
                
                access_stats = {
                    'min_access_count': min(access_counts),
                    'max_access_count': max(access_counts),
                    'avg_access_count': sum(access_counts) / len(access_counts)
                }
                
                age_stats = {
                    'min_age_hours': min(ages),
                    'max_age_hours': max(ages),
                    'avg_age_hours': sum(ages) / len(ages)
                }
            else:
                size_stats = access_stats = age_stats = {}
            
            # Namespace breakdown
            namespace_stats = {}
            for key in self.cache.keys():
                namespace = key.split(':')[0]
                if namespace not in namespace_stats:
                    namespace_stats[namespace] = {'count': 0, 'size_bytes': 0}
                namespace_stats[namespace]['count'] += 1
                namespace_stats[namespace]['size_bytes'] += self.cache[key].size_bytes
            
            return {
                'basic_stats': asdict(self.stats),
                'size_stats': size_stats,
                'access_stats': access_stats,
                'age_stats': age_stats,
                'namespace_breakdown': namespace_stats,
                'cache_utilization': self.stats.total_size_bytes / self.max_size_bytes,
                'strategy': self.strategy.value,
                'cleanup_interval_seconds': self.cleanup_interval_seconds
            }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get cache optimization recommendations."""
        recommendations = []
        stats = self.get_cache_statistics()
        
        # Hit rate recommendations
        hit_rate = stats['basic_stats']['hit_rate']
        if hit_rate < 0.5:
            recommendations.append(f"Low cache hit rate ({hit_rate:.1%}). Consider increasing cache size or adjusting TTL.")
        elif hit_rate > 0.9:
            recommendations.append(f"Excellent cache hit rate ({hit_rate:.1%}). Cache is well-tuned.")
        
        # Size utilization recommendations
        utilization = stats['cache_utilization']
        if utilization > 0.9:
            recommendations.append(f"High cache utilization ({utilization:.1%}). Consider increasing cache size.")
        elif utilization < 0.3:
            recommendations.append(f"Low cache utilization ({utilization:.1%}). Cache size could be reduced.")
        
        # Eviction recommendations
        if stats['basic_stats']['evictions'] > stats['basic_stats']['cache_hits'] * 0.1:
            recommendations.append("High eviction rate. Consider increasing cache size or optimizing entry sizes.")
        
        # Strategy recommendations
        if self.strategy == CacheStrategy.LRU and len(self.access_patterns) > 100:
            recommendations.append("Consider switching to ADAPTIVE strategy for better performance with complex access patterns.")
        
        # Entry size recommendations
        if 'size_stats' in stats and stats['size_stats']:
            avg_size = stats['size_stats']['avg_size_bytes']
            if avg_size > 1024 * 1024:  # > 1MB
                recommendations.append(f"Large average entry size ({avg_size / (1024*1024):.1f}MB). Consider compressing large entries.")
        
        # TTL recommendations
        if 'age_stats' in stats and stats['age_stats']:
            avg_age = stats['age_stats']['avg_age_hours']
            if avg_age > 24:
                recommendations.append(f"Entries staying in cache for long time ({avg_age:.1f}h). Consider reducing TTL.")
        
        return recommendations
    
    def add_invalidation_callback(self, callback: Callable[[str], None]):
        """Add callback for cache invalidation events."""
        self.invalidation_callbacks.append(callback)
    
    def remove_invalidation_callback(self, callback: Callable[[str], None]):
        """Remove invalidation callback."""
        if callback in self.invalidation_callbacks:
            self.invalidation_callbacks.remove(callback)
    
    async def cleanup(self):
        """Cleanup cache manager resources."""
        try:
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Save persistent cache
            await self.save_persistent_cache()
            
            self.logger.info("Cache manager cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cache cleanup: {e}")
    
    # ReflectiveModule health endpoints
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        stats = self.get_cache_statistics()
        
        return {
            'status': 'healthy',
            'cache_entries': stats['basic_stats']['entry_count'],
            'cache_utilization': stats['cache_utilization'],
            'hit_rate': stats['basic_stats']['hit_rate'],
            'cleanup_task_running': self.cleanup_task is not None and not self.cleanup_task.done()
        }
    
    async def ready_check(self) -> Dict[str, Any]:
        """Readiness check endpoint."""
        return {
            'ready': True,
            'cache_initialized': True,
            'strategy_configured': self.strategy is not None
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache metrics."""
        stats = self.get_cache_statistics()
        
        return {
            'cache_manager_total_requests': stats['basic_stats']['total_requests'],
            'cache_manager_cache_hits': stats['basic_stats']['cache_hits'],
            'cache_manager_cache_misses': stats['basic_stats']['cache_misses'],
            'cache_manager_hit_rate': stats['basic_stats']['hit_rate'],
            'cache_manager_entry_count': stats['basic_stats']['entry_count'],
            'cache_manager_total_size_bytes': stats['basic_stats']['total_size_bytes'],
            'cache_manager_utilization': stats['cache_utilization'],
            'cache_manager_evictions': stats['basic_stats']['evictions']
        }


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Create cache manager
        cache = CacheManager(max_size_mb=10, strategy=CacheStrategy.ADAPTIVE)
        
        # Test caching
        await cache.set('docs', 'workflow1', {'content': 'Workflow documentation'}, ttl_seconds=300)
        await cache.set('diagrams', 'sequence1', {'svg': '<svg>...</svg>'}, ttl_seconds=600)
        
        # Test retrieval
        workflow = await cache.get('docs', 'workflow1')
        print(f"Retrieved workflow: {workflow}")
        
        # Test cache statistics
        stats = cache.get_cache_statistics()
        print(f"Cache stats: Hit rate={stats['basic_stats']['hit_rate']:.1%}, "
              f"Entries={stats['basic_stats']['entry_count']}")
        
        # Test optimization recommendations
        recommendations = cache.get_optimization_recommendations()
        print(f"Recommendations: {recommendations}")
        
        # Cleanup
        await cache.cleanup()
    
    asyncio.run(main())