"""
Domain Cache System

This module provides advanced caching capabilities for domain data,
including TTL management, invalidation strategies, and cache warming.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set, Callable
from collections import defaultdict
from dataclasses import dataclass

from .base import DomainSystemComponent
from .interfaces import CacheInterface
from .models import Domain, DomainCollection


@dataclass
class CacheEntry:
    """Individual cache entry with metadata"""
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int]
    tags: Set[str]
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl_seconds is None:
            return False
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl_seconds)
    
    def touch(self) -> None:
        """Update last accessed time and increment access count"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class DomainCache(DomainSystemComponent, CacheInterface):
    """
    Advanced caching system for domain data
    
    Features:
    - TTL-based expiration
    - Tag-based invalidation
    - LRU eviction policy
    - Cache warming
    - Statistics and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("domain_cache", config)
        
        # Cache configuration
        self.max_size = self.config.get('max_cache_size', 1000)
        self.default_ttl = self.config.get('default_ttl_seconds', 300)
        self.cleanup_interval = self.config.get('cleanup_interval_seconds', 60)
        self.enable_lru = self.config.get('enable_lru_eviction', True)
        
        # Cache storage
        self._cache: Dict[str, CacheEntry] = {}
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)
        self._lock = threading.RLock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.invalidations = 0
        
        # Background cleanup
        self._cleanup_timer = None
        self._start_cleanup_timer()
        
        self.logger.info(f"Initialized DomainCache with max_size={self.max_size}, default_ttl={self.default_ttl}s")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self.misses += 1
                return None
            
            if entry.is_expired():
                self._remove_entry(key)
                self.misses += 1
                return None
            
            entry.touch()
            self.hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tags: Optional[Set[str]] = None) -> bool:
        """Set value in cache with optional TTL and tags"""
        with self._lock:
            try:
                # Use default TTL if not specified
                if ttl_seconds is None:
                    ttl_seconds = self.default_ttl
                
                # Create cache entry
                entry = CacheEntry(
                    value=value,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    access_count=1,
                    ttl_seconds=ttl_seconds,
                    tags=tags or set()
                )
                
                # Check if we need to evict entries
                if len(self._cache) >= self.max_size and key not in self._cache:
                    self._evict_entries(1)
                
                # Remove existing entry if present
                if key in self._cache:
                    self._remove_entry(key)
                
                # Add new entry
                self._cache[key] = entry
                
                # Update tag index
                for tag in entry.tags:
                    self._tag_index[tag].add(key)
                
                return True
                
            except Exception as e:
                self._handle_error(e, "cache_set")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        with self._lock:
            try:
                self._cache.clear()
                self._tag_index.clear()
                self.hits = 0
                self.misses = 0
                self.evictions = 0
                self.invalidations = 0
                self.logger.info("Cache cleared")
                return True
            except Exception as e:
                self._handle_error(e, "cache_clear")
                return False
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all entries with a specific tag"""
        with self._lock:
            keys_to_remove = list(self._tag_index.get(tag, set()))
            
            for key in keys_to_remove:
                self._remove_entry(key)
            
            self.invalidations += len(keys_to_remove)
            self.logger.debug(f"Invalidated {len(keys_to_remove)} entries with tag '{tag}'")
            return len(keys_to_remove)
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate all entries matching a key pattern"""
        with self._lock:
            import fnmatch
            keys_to_remove = [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]
            
            for key in keys_to_remove:
                self._remove_entry(key)
            
            self.invalidations += len(keys_to_remove)
            self.logger.debug(f"Invalidated {len(keys_to_remove)} entries matching pattern '{pattern}'")
            return len(keys_to_remove)
    
    def warm_cache(self, warm_func: Callable[[str], Any], keys: List[str]) -> int:
        """Warm cache with data from a function"""
        warmed_count = 0
        
        for key in keys:
            try:
                if key not in self._cache:
                    value = warm_func(key)
                    if value is not None:
                        self.set(key, value)
                        warmed_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to warm cache for key '{key}': {e}")
        
        self.logger.info(f"Warmed cache with {warmed_count} entries")
        return warmed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
            
            # Calculate memory usage estimation
            memory_usage_bytes = sum(
                len(str(entry.value)) + len(str(key)) + 200  # Rough estimation
                for key, entry in self._cache.items()
            )
            
            # Age distribution
            now = datetime.now()
            age_buckets = {"<1min": 0, "1-5min": 0, "5-15min": 0, ">15min": 0}
            
            for entry in self._cache.values():
                age_seconds = (now - entry.created_at).total_seconds()
                if age_seconds < 60:
                    age_buckets["<1min"] += 1
                elif age_seconds < 300:
                    age_buckets["1-5min"] += 1
                elif age_seconds < 900:
                    age_buckets["5-15min"] += 1
                else:
                    age_buckets[">15min"] += 1
            
            return {
                "cache_size": len(self._cache),
                "max_size": self.max_size,
                "utilization": len(self._cache) / self.max_size if self.max_size > 0 else 0.0,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "evictions": self.evictions,
                "invalidations": self.invalidations,
                "memory_usage_bytes": memory_usage_bytes,
                "age_distribution": age_buckets,
                "tag_count": len(self._tag_index),
                "default_ttl_seconds": self.default_ttl
            }
    
    def get_keys_by_tag(self, tag: str) -> List[str]:
        """Get all cache keys with a specific tag"""
        with self._lock:
            return list(self._tag_index.get(tag, set()))
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a cache entry"""
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            
            return {
                "key": key,
                "created_at": entry.created_at.isoformat(),
                "last_accessed": entry.last_accessed.isoformat(),
                "access_count": entry.access_count,
                "ttl_seconds": entry.ttl_seconds,
                "is_expired": entry.is_expired(),
                "tags": list(entry.tags),
                "value_type": type(entry.value).__name__,
                "value_size_bytes": len(str(entry.value))
            }
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry and update tag index"""
        entry = self._cache.get(key)
        if entry:
            # Remove from tag index
            for tag in entry.tags:
                self._tag_index[tag].discard(key)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]
            
            # Remove from cache
            del self._cache[key]
    
    def _evict_entries(self, count: int) -> None:
        """Evict entries using LRU policy"""
        if not self.enable_lru or not self._cache:
            return
        
        # Sort by last accessed time (LRU)
        entries_by_access = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        evicted = 0
        for key, _ in entries_by_access:
            if evicted >= count:
                break
            
            self._remove_entry(key)
            evicted += 1
        
        self.evictions += evicted
        self.logger.debug(f"Evicted {evicted} entries using LRU policy")
    
    def _cleanup_expired_entries(self) -> None:
        """Clean up expired entries"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                self._remove_entry(key)
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
    
    def _start_cleanup_timer(self) -> None:
        """Start background cleanup timer"""
        def cleanup_task():
            try:
                self._cleanup_expired_entries()
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {e}")
            finally:
                # Schedule next cleanup
                self._cleanup_timer = threading.Timer(self.cleanup_interval, cleanup_task)
                self._cleanup_timer.daemon = True
                self._cleanup_timer.start()
        
        self._cleanup_timer = threading.Timer(self.cleanup_interval, cleanup_task)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def shutdown(self) -> None:
        """Shutdown cache and cleanup resources"""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        
        with self._lock:
            self._cache.clear()
            self._tag_index.clear()
        
        self.logger.info("DomainCache shutdown complete")


class DomainSpecificCache:
    """
    Domain-specific cache wrapper that provides domain-aware caching
    """
    
    def __init__(self, cache: DomainCache):
        self.cache = cache
    
    def cache_domain(self, domain: Domain, ttl_seconds: Optional[int] = None) -> bool:
        """Cache a domain with appropriate tags"""
        tags = {
            "domain",
            f"category:{domain.metadata.demo_role}",
            f"status:{domain.metadata.status}"
        }
        
        # Add pattern-based tags
        for pattern in domain.patterns:
            if "**" in pattern:
                tags.add("recursive_pattern")
            if ".py" in pattern:
                tags.add("python_domain")
        
        return self.cache.set(f"domain:{domain.name}", domain, ttl_seconds, tags)
    
    def get_domain(self, domain_name: str) -> Optional[Domain]:
        """Get cached domain"""
        return self.cache.get(f"domain:{domain_name}")
    
    def cache_domain_collection(self, domains: DomainCollection, ttl_seconds: Optional[int] = None) -> bool:
        """Cache a collection of domains"""
        tags = {"domain_collection", f"count:{len(domains)}"}
        return self.cache.set("all_domains", domains, ttl_seconds, tags)
    
    def get_domain_collection(self) -> Optional[DomainCollection]:
        """Get cached domain collection"""
        return self.cache.get("all_domains")
    
    def invalidate_domain(self, domain_name: str) -> bool:
        """Invalidate cached domain and related data"""
        # Remove specific domain
        self.cache.delete(f"domain:{domain_name}")
        
        # Invalidate collections that might contain this domain
        self.cache.invalidate_by_tag("domain_collection")
        
        # Invalidate search results that might contain this domain
        self.cache.invalidate_by_pattern("search:*")
        
        return True
    
    def invalidate_by_category(self, category: str) -> int:
        """Invalidate all domains in a category"""
        return self.cache.invalidate_by_tag(f"category:{category}")
    
    def warm_domains(self, domain_loader: Callable[[str], Optional[Domain]], domain_names: List[str]) -> int:
        """Warm cache with domain data"""
        def load_domain(key: str) -> Optional[Domain]:
            domain_name = key.replace("domain:", "")
            return domain_loader(domain_name)
        
        domain_keys = [f"domain:{name}" for name in domain_names]
        return self.cache.warm_cache(load_domain, domain_keys)