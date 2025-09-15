#!/usr/bin/env python3
"""
Intelligent Cache Manager
========================

Advanced intelligent caching system for the Beast Mode framework.
Provides predictive caching, adaptive TTL, and intelligent cache
eviction strategies for optimal performance.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Intelligent caching for performance optimization
"""

import sys
import os
import time
import json
import logging
import threading
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import weakref
from pathlib import Path


class CacheStrategy(Enum):
    """Cache eviction strategies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on usage patterns


class CacheLevel(Enum):
    """Cache levels for hierarchical caching."""

    L1 = "l1"  # In-memory cache
    L2 = "l2"  # Disk cache
    L3 = "l3"  # Network cache


@dataclass
class CacheEntry:
    """Enhanced cache entry with intelligent metadata."""

    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: int = 3600
    priority: int = 1
    hit_rate: float = 0.0
    access_pattern: List[datetime] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class CacheStats:
    """Cache performance statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    hit_rate: float = 0.0
    average_access_time_ms: float = 0.0
    cache_efficiency: float = 0.0


class IntelligentCacheManager:
    """
    Intelligent cache manager with predictive caching and adaptive strategies.

    Provides advanced caching capabilities including:
    - Predictive caching based on usage patterns
    - Adaptive TTL based on access frequency
    - Intelligent eviction strategies
    - Hierarchical caching (L1, L2, L3)
    - Cache dependency tracking
    """

    def __init__(
        self,
        max_size_mb: int = 200,
        strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
        enable_disk_cache: bool = True,
        enable_network_cache: bool = False,
    ):
        """Initialize the intelligent cache manager."""
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.strategy = strategy
        self.enable_disk_cache = enable_disk_cache
        self.enable_network_cache = enable_network_cache

        self.logger = self._setup_logging()

        # Cache storage
        self.l1_cache: Dict[str, CacheEntry] = {}  # In-memory
        self.l2_cache: Dict[str, CacheEntry] = {}  # Disk
        self.l3_cache: Dict[str, CacheEntry] = {}  # Network

        # Statistics
        self.stats = CacheStats()

        # Threading
        self.cache_lock = threading.RLock()
        self.cleanup_thread = None
        self.cleanup_active = False

        # Cache directories
        self.cache_dir = Path(".cache/beast_mode")
        if self.enable_disk_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Access pattern tracking
        self.access_patterns: Dict[str, List[datetime]] = {}
        self.prediction_model = self._initialize_prediction_model()

        # Start cleanup thread
        self.start_cleanup_thread()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for cache manager."""
        logger = logging.getLogger("intelligent_cache_manager")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_prediction_model(self) -> Dict[str, Any]:
        """Initialize predictive caching model."""
        return {
            "access_frequency": {},
            "temporal_patterns": {},
            "dependency_graph": {},
            "hit_rate_history": [],
            "eviction_patterns": {},
        }

    def start_cleanup_thread(self):
        """Start cache cleanup thread."""
        if not self.cleanup_active:
            self.cleanup_active = True
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_loop, daemon=True
            )
            self.cleanup_thread.start()
            self.logger.info("Cache cleanup thread started")

    def stop_cleanup_thread(self):
        """Stop cache cleanup thread."""
        self.cleanup_active = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        self.logger.info("Cache cleanup thread stopped")

    def _cleanup_loop(self):
        """Cache cleanup loop."""
        while self.cleanup_active:
            try:
                self._cleanup_expired_entries()
                self._optimize_cache_size()
                self._update_prediction_model()
                time.sleep(30)  # Cleanup every 30 seconds
            except Exception as e:
                self.logger.error(f"Cache cleanup error: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with intelligent retrieval."""
        start_time = time.time()

        with self.cache_lock:
            # Try L1 cache first (in-memory)
            entry = self._get_from_level(key, CacheLevel.L1)
            if entry:
                self._update_access_stats(entry, start_time)
                return entry.value

            # Try L2 cache (disk)
            if self.enable_disk_cache:
                entry = self._get_from_level(key, CacheLevel.L2)
                if entry:
                    # Promote to L1 cache
                    self._promote_to_l1(entry)
                    self._update_access_stats(entry, start_time)
                    return entry.value

            # Try L3 cache (network)
            if self.enable_network_cache:
                entry = self._get_from_level(key, CacheLevel.L3)
                if entry:
                    # Promote to L1 and L2
                    self._promote_to_l1(entry)
                    if self.enable_disk_cache:
                        self._promote_to_l2(entry)
                    self._update_access_stats(entry, start_time)
                    return entry.value

            # Cache miss
            self.stats.misses += 1
            self._record_access_pattern(key, start_time)
            return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        priority: int = 1,
        tags: List[str] = None,
        dependencies: List[str] = None,
    ):
        """Set value in cache with intelligent storage."""
        start_time = time.time()

        with self.cache_lock:
            # Calculate size
            size_bytes = sys.getsizeof(value)

            # Determine TTL if not provided
            if ttl is None:
                ttl = self._calculate_adaptive_ttl(key, value)

            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                size_bytes=size_bytes,
                ttl_seconds=ttl,
                priority=priority,
                tags=tags or [],
                dependencies=dependencies or [],
            )

            # Store in appropriate cache level
            self._store_in_cache(entry)

            self.logger.debug(
                f"Cached entry: {key} (size: {size_bytes} bytes, TTL: {ttl}s)"
            )

    def _get_from_level(self, key: str, level: CacheLevel) -> Optional[CacheEntry]:
        """Get entry from specific cache level."""
        cache_map = {
            CacheLevel.L1: self.l1_cache,
            CacheLevel.L2: self.l2_cache,
            CacheLevel.L3: self.l3_cache,
        }

        cache = cache_map[level]

        if key in cache:
            entry = cache[key]

            # Check if expired
            if self._is_expired(entry):
                del cache[key]
                return None

            # Update access time
            entry.last_accessed = datetime.now()
            entry.access_count += 1

            return entry

        return None

    def _store_in_cache(self, entry: CacheEntry):
        """Store entry in appropriate cache level."""
        # Always store in L1 cache
        self.l1_cache[entry.key] = entry

        # Store in L2 cache if enabled and meets criteria
        if self.enable_disk_cache and self._should_store_in_l2(entry):
            self._store_in_l2(entry)

        # Store in L3 cache if enabled and meets criteria
        if self.enable_network_cache and self._should_store_in_l3(entry):
            self._store_in_l3(entry)

        # Update total size
        self.stats.total_size_bytes += entry.size_bytes

        # Check if we need to evict
        if self.stats.total_size_bytes > self.max_size_bytes:
            self._evict_entries()

    def _should_store_in_l2(self, entry: CacheEntry) -> bool:
        """Determine if entry should be stored in L2 cache."""
        # Store in L2 if:
        # - High priority
        # - Large size
        # - Frequently accessed
        return (
            entry.priority <= 2
            or entry.size_bytes > 1024 * 1024  # > 1MB
            or entry.access_count > 5
        )

    def _should_store_in_l3(self, entry: CacheEntry) -> bool:
        """Determine if entry should be stored in L3 cache."""
        # Store in L3 if:
        # - Critical priority
        # - Very large size
        # - High access frequency
        return entry.priority == 1 and (
            entry.size_bytes > 10 * 1024 * 1024 or entry.access_count > 20  # > 10MB
        )

    def _store_in_l2(self, entry: CacheEntry):
        """Store entry in L2 cache (disk)."""
        try:
            cache_file = self.cache_dir / f"{entry.key}.cache"

            # Serialize entry
            entry_data = {
                "value": entry.value,
                "created_at": entry.created_at.isoformat(),
                "last_accessed": entry.last_accessed.isoformat(),
                "access_count": entry.access_count,
                "size_bytes": entry.size_bytes,
                "ttl_seconds": entry.ttl_seconds,
                "priority": entry.priority,
                "tags": entry.tags,
                "dependencies": entry.dependencies,
            }

            with open(cache_file, "wb") as f:
                pickle.dump(entry_data, f)

            self.l2_cache[entry.key] = entry

        except Exception as e:
            self.logger.error(f"Failed to store in L2 cache: {e}")

    def _store_in_l3(self, entry: CacheEntry):
        """Store entry in L3 cache (network)."""
        # For now, just store in memory as L3
        # In a real implementation, this would use network storage
        self.l3_cache[entry.key] = entry

    def _promote_to_l1(self, entry: CacheEntry):
        """Promote entry to L1 cache."""
        self.l1_cache[entry.key] = entry

    def _promote_to_l2(self, entry: CacheEntry):
        """Promote entry to L2 cache."""
        if self.enable_disk_cache:
            self._store_in_l2(entry)

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        current_time = datetime.now()
        age_seconds = (current_time - entry.created_at).total_seconds()
        return age_seconds > entry.ttl_seconds

    def _calculate_adaptive_ttl(self, key: str, value: Any) -> int:
        """Calculate adaptive TTL based on usage patterns."""
        base_ttl = 3600  # 1 hour default

        # Adjust based on key patterns
        if "analysis" in key.lower():
            return base_ttl * 4  # Analysis results are stable
        elif "validation" in key.lower():
            return base_ttl // 2  # Validation results change more frequently
        elif "health" in key.lower():
            return base_ttl // 4  # Health checks change frequently

        # Adjust based on value type
        if isinstance(value, (dict, list)) and len(str(value)) > 10000:
            return base_ttl * 2  # Large data structures are expensive to compute

        # Adjust based on historical access patterns
        if key in self.prediction_model["access_frequency"]:
            frequency = self.prediction_model["access_frequency"][key]
            if frequency > 10:  # Frequently accessed
                return base_ttl * 2
            elif frequency < 2:  # Rarely accessed
                return base_ttl // 2

        return base_ttl

    def _update_access_stats(self, entry: CacheEntry, start_time: float):
        """Update access statistics."""
        access_time = (time.time() - start_time) * 1000  # Convert to ms

        self.stats.hits += 1
        self.stats.average_access_time_ms = (
            self.stats.average_access_time_ms * (self.stats.hits - 1) + access_time
        ) / self.stats.hits

        # Update hit rate
        total_requests = self.stats.hits + self.stats.misses
        self.stats.hit_rate = (
            (self.stats.hits / total_requests * 100) if total_requests > 0 else 0
        )

        # Record access pattern
        entry.access_pattern.append(datetime.now())
        if len(entry.access_pattern) > 100:  # Keep only last 100 accesses
            entry.access_pattern = entry.access_pattern[-100:]

    def _record_access_pattern(self, key: str, start_time: float):
        """Record access pattern for cache misses."""
        if key not in self.access_patterns:
            self.access_patterns[key] = []

        self.access_patterns[key].append(datetime.now())

        # Keep only recent patterns
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.access_patterns[key] = [
            t for t in self.access_patterns[key] if t > cutoff_time
        ]

    def _cleanup_expired_entries(self):
        """Clean up expired cache entries."""
        current_time = datetime.now()

        for cache_name, cache in [
            ("L1", self.l1_cache),
            ("L2", self.l2_cache),
            ("L3", self.l3_cache),
        ]:
            expired_keys = []

            for key, entry in cache.items():
                if self._is_expired(entry):
                    expired_keys.append(key)

            for key in expired_keys:
                entry = cache[key]
                self.stats.total_size_bytes -= entry.size_bytes
                del cache[key]

                # Remove from disk if L2
                if cache_name == "L2" and self.enable_disk_cache:
                    cache_file = self.cache_dir / f"{key}.cache"
                    if cache_file.exists():
                        cache_file.unlink()

            if expired_keys:
                self.logger.info(
                    f"Cleaned up {len(expired_keys)} expired entries from {cache_name} cache"
                )

    def _optimize_cache_size(self):
        """Optimize cache size using intelligent eviction."""
        if self.stats.total_size_bytes <= self.max_size_bytes:
            return

        # Calculate how much to evict (20% of max size)
        target_reduction = self.max_size_bytes * 0.2
        current_reduction = 0

        # Sort entries by eviction score
        all_entries = []
        for cache_name, cache in [
            ("L1", self.l1_cache),
            ("L2", self.l2_cache),
            ("L3", self.l3_cache),
        ]:
            for key, entry in cache.items():
                eviction_score = self._calculate_eviction_score(entry)
                all_entries.append((cache_name, key, entry, eviction_score))

        # Sort by eviction score (highest first = most likely to evict)
        all_entries.sort(key=lambda x: x[3], reverse=True)

        # Evict entries until we reach target reduction
        for cache_name, key, entry, score in all_entries:
            if current_reduction >= target_reduction:
                break

            self._evict_entry(cache_name, key, entry)
            current_reduction += entry.size_bytes
            self.stats.evictions += 1

        self.logger.info(
            f"Evicted entries to reduce cache size by {current_reduction / (1024*1024):.1f}MB"
        )

    def _calculate_eviction_score(self, entry: CacheEntry) -> float:
        """Calculate eviction score for intelligent eviction."""
        current_time = datetime.now()

        # Base score from strategy
        if self.strategy == CacheStrategy.LRU:
            # Lower score = more recently used = less likely to evict
            age_seconds = (current_time - entry.last_accessed).total_seconds()
            base_score = 1.0 / (age_seconds + 1)
        elif self.strategy == CacheStrategy.LFU:
            # Lower score = more frequently used = less likely to evict
            base_score = 1.0 / (entry.access_count + 1)
        elif self.strategy == CacheStrategy.TTL:
            # Lower score = more time remaining = less likely to evict
            age_seconds = (current_time - entry.created_at).total_seconds()
            remaining_seconds = entry.ttl_seconds - age_seconds
            base_score = 1.0 / (remaining_seconds + 1)
        else:  # ADAPTIVE
            # Combine multiple factors
            age_seconds = (current_time - entry.last_accessed).total_seconds()
            frequency_score = 1.0 / (entry.access_count + 1)
            recency_score = 1.0 / (age_seconds + 1)
            priority_score = entry.priority
            base_score = (frequency_score + recency_score + priority_score) / 3

        # Adjust by size (larger entries are more expensive to evict)
        size_factor = entry.size_bytes / (1024 * 1024)  # Size in MB
        size_adjustment = 1.0 / (size_factor + 1)

        # Adjust by hit rate
        hit_rate_adjustment = 1.0 / (entry.hit_rate + 0.1)

        return base_score * size_adjustment * hit_rate_adjustment

    def _evict_entry(self, cache_name: str, key: str, entry: CacheEntry):
        """Evict a specific cache entry."""
        cache_map = {"L1": self.l1_cache, "L2": self.l2_cache, "L3": self.l3_cache}

        cache = cache_map[cache_name]

        if key in cache:
            del cache[key]
            self.stats.total_size_bytes -= entry.size_bytes

            # Remove from disk if L2
            if cache_name == "L2" and self.enable_disk_cache:
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    cache_file.unlink()

    def _evict_entries(self):
        """Evict entries using current strategy."""
        self._optimize_cache_size()

    def _update_prediction_model(self):
        """Update predictive caching model."""
        # Update access frequency
        for key, patterns in self.access_patterns.items():
            frequency = len(patterns)
            self.prediction_model["access_frequency"][key] = frequency

        # Update hit rate history
        self.prediction_model["hit_rate_history"].append(self.stats.hit_rate)
        if len(self.prediction_model["hit_rate_history"]) > 100:
            self.prediction_model["hit_rate_history"] = self.prediction_model[
                "hit_rate_history"
            ][-100:]

    def clear(self):
        """Clear all cache levels."""
        with self.cache_lock:
            self.l1_cache.clear()
            self.l2_cache.clear()
            self.l3_cache.clear()

            # Clear disk cache
            if self.enable_disk_cache and self.cache_dir.exists():
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()

            # Reset stats
            self.stats.total_size_bytes = 0
            self.logger.info("All cache levels cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get comprehensive cache information."""
        return {
            "cache_levels": {
                "L1_entries": len(self.l1_cache),
                "L2_entries": len(self.l2_cache),
                "L3_entries": len(self.l3_cache),
            },
            "statistics": {
                "hits": self.stats.hits,
                "misses": self.stats.misses,
                "hit_rate_percent": self.stats.hit_rate,
                "evictions": self.stats.evictions,
                "total_size_mb": self.stats.total_size_bytes / (1024 * 1024),
                "average_access_time_ms": self.stats.average_access_time_ms,
            },
            "configuration": {
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "strategy": self.strategy.value,
                "disk_cache_enabled": self.enable_disk_cache,
                "network_cache_enabled": self.enable_network_cache,
            },
            "prediction_model": {
                "tracked_keys": len(self.prediction_model["access_frequency"]),
                "hit_rate_history_length": len(
                    self.prediction_model["hit_rate_history"]
                ),
            },
        }

    def generate_cache_report(self) -> str:
        """Generate detailed cache performance report."""
        report = []
        report.append("=" * 80)
        report.append("INTELLIGENT CACHE MANAGER REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        cache_info = self.get_cache_info()

        report.append("CACHE LEVELS:")
        levels = cache_info["cache_levels"]
        report.append(f"  L1 Cache (Memory): {levels['L1_entries']} entries")
        report.append(f"  L2 Cache (Disk): {levels['L2_entries']} entries")
        report.append(f"  L3 Cache (Network): {levels['L3_entries']} entries")
        report.append("")

        stats = cache_info["statistics"]
        report.append("PERFORMANCE STATISTICS:")
        report.append(f"  Hit Rate: {stats['hit_rate_percent']:.1f}%")
        report.append(f"  Total Hits: {stats['hits']}")
        report.append(f"  Total Misses: {stats['misses']}")
        report.append(f"  Evictions: {stats['evictions']}")
        report.append(f"  Cache Size: {stats['total_size_mb']:.1f}MB")
        report.append(f"  Average Access Time: {stats['average_access_time_ms']:.2f}ms")
        report.append("")

        config = cache_info["configuration"]
        report.append("CONFIGURATION:")
        report.append(f"  Max Size: {config['max_size_mb']:.1f}MB")
        report.append(f"  Strategy: {config['strategy']}")
        report.append(
            f"  Disk Cache: {'Enabled' if config['disk_cache_enabled'] else 'Disabled'}"
        )
        report.append(
            f"  Network Cache: {'Enabled' if config['network_cache_enabled'] else 'Disabled'}"
        )
        report.append("")

        prediction = cache_info["prediction_model"]
        report.append("PREDICTIVE MODEL:")
        report.append(f"  Tracked Keys: {prediction['tracked_keys']}")
        report.append(
            f"  Hit Rate History: {prediction['hit_rate_history_length']} samples"
        )
        report.append("")

        return "\n".join(report)

    def __del__(self):
        """Cleanup on destruction."""
        self.stop_cleanup_thread()


def main():
    """Main function for testing the intelligent cache manager."""
    cache = IntelligentCacheManager(
        max_size_mb=50, strategy=CacheStrategy.ADAPTIVE, enable_disk_cache=True
    )

    print("Testing Intelligent Cache Manager...")

    # Test basic operations
    print("\nTesting basic operations...")
    cache.set("test_key", "test_value", ttl=60)
    value = cache.get("test_key")
    print(f"Stored and retrieved: {value}")

    # Test TTL expiration
    print("\nTesting TTL expiration...")
    cache.set("expire_key", "expire_value", ttl=1)
    time.sleep(2)
    expired_value = cache.get("expire_key")
    print(f"Expired value: {expired_value}")

    # Test cache statistics
    print("\nTesting cache statistics...")
    for i in range(10):
        cache.set(f"key_{i}", f"value_{i}", priority=1 if i < 5 else 3)

    # Access some keys multiple times
    for i in range(5):
        cache.get("key_0")  # High access count

    # Generate report
    print("\n" + cache.generate_cache_report())


if __name__ == "__main__":
    main()
