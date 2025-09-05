"""
Tests for Domain Cache System

This module tests the DomainCache and DomainSpecificCache classes,
including TTL management, invalidation strategies, and performance.
"""

import pytest
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.beast_mode.domain_index.domain_cache import DomainCache, DomainSpecificCache, CacheEntry
from src.beast_mode.domain_index.models import (
    Domain, DomainTools, DomainMetadata, PackagePotential
)


class TestCacheEntry:
    """Test CacheEntry functionality"""
    
    def test_cache_entry_creation(self):
        """Test cache entry creation"""
        entry = CacheEntry(
            value="test_value",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            ttl_seconds=300,
            tags={"test", "cache"}
        )
        
        assert entry.value == "test_value"
        assert entry.access_count == 1
        assert entry.ttl_seconds == 300
        assert "test" in entry.tags
        assert "cache" in entry.tags
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration logic"""
        # Non-expiring entry
        entry = CacheEntry(
            value="test",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            ttl_seconds=None,
            tags=set()
        )
        assert not entry.is_expired()
        
        # Expired entry
        old_time = datetime.now() - timedelta(seconds=400)
        entry = CacheEntry(
            value="test",
            created_at=old_time,
            last_accessed=old_time,
            access_count=1,
            ttl_seconds=300,
            tags=set()
        )
        assert entry.is_expired()
        
        # Non-expired entry
        recent_time = datetime.now() - timedelta(seconds=100)
        entry = CacheEntry(
            value="test",
            created_at=recent_time,
            last_accessed=recent_time,
            access_count=1,
            ttl_seconds=300,
            tags=set()
        )
        assert not entry.is_expired()
    
    def test_cache_entry_touch(self):
        """Test cache entry touch functionality"""
        entry = CacheEntry(
            value="test",
            created_at=datetime.now(),
            last_accessed=datetime.now() - timedelta(seconds=100),
            access_count=1,
            ttl_seconds=300,
            tags=set()
        )
        
        old_access_time = entry.last_accessed
        old_count = entry.access_count
        
        entry.touch()
        
        assert entry.last_accessed > old_access_time
        assert entry.access_count == old_count + 1


class TestDomainCache:
    """Test DomainCache functionality"""
    
    @pytest.fixture
    def cache(self):
        """Create a test cache instance"""
        config = {
            'max_cache_size': 100,
            'default_ttl_seconds': 300,
            'cleanup_interval_seconds': 60,
            'enable_lru_eviction': True
        }
        cache = DomainCache(config)
        yield cache
        cache.shutdown()
    
    def test_cache_initialization(self, cache):
        """Test cache initialization"""
        assert cache.max_size == 100
        assert cache.default_ttl == 300
        assert cache.cleanup_interval == 60
        assert cache.enable_lru is True
        assert cache.hits == 0
        assert cache.misses == 0
    
    def test_basic_cache_operations(self, cache):
        """Test basic cache get/set operations"""
        # Test cache miss
        result = cache.get("nonexistent")
        assert result is None
        assert cache.misses == 1
        
        # Test cache set and hit
        assert cache.set("test_key", "test_value")
        result = cache.get("test_key")
        assert result == "test_value"
        assert cache.hits == 1
        
        # Test cache delete
        assert cache.delete("test_key")
        result = cache.get("test_key")
        assert result is None
        assert cache.misses == 2
    
    def test_cache_ttl_expiration(self, cache):
        """Test TTL-based cache expiration"""
        # Set with short TTL
        cache.set("short_ttl", "value", ttl_seconds=1)
        
        # Should be available immediately
        assert cache.get("short_ttl") == "value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get("short_ttl") is None
    
    def test_cache_with_tags(self, cache):
        """Test cache operations with tags"""
        tags1 = {"tag1", "common"}
        tags2 = {"tag2", "common"}
        
        cache.set("key1", "value1", tags=tags1)
        cache.set("key2", "value2", tags=tags2)
        cache.set("key3", "value3", tags={"tag3"})
        
        # Test tag-based invalidation
        invalidated = cache.invalidate_by_tag("common")
        assert invalidated == 2
        
        # Check that tagged items are gone
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
    
    def test_cache_pattern_invalidation(self, cache):
        """Test pattern-based cache invalidation"""
        cache.set("domain:user", "user_domain")
        cache.set("domain:auth", "auth_domain")
        cache.set("search:user", "user_search")
        cache.set("other:key", "other_value")
        
        # Invalidate all domain keys
        invalidated = cache.invalidate_by_pattern("domain:*")
        assert invalidated == 2
        
        # Check results
        assert cache.get("domain:user") is None
        assert cache.get("domain:auth") is None
        assert cache.get("search:user") == "user_search"
        assert cache.get("other:key") == "other_value"
    
    def test_cache_lru_eviction(self, cache):
        """Test LRU eviction policy"""
        # Set small cache size for testing
        cache.max_size = 3
        
        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Access key1 to make it recently used
        cache.get("key1")
        
        # Add new item, should evict key2 (least recently used)
        cache.set("key4", "value4")
        
        assert cache.get("key1") == "value1"  # Should still be there
        assert cache.get("key2") is None      # Should be evicted
        assert cache.get("key3") == "value3"  # Should still be there
        assert cache.get("key4") == "value4"  # Should be there
    
    def test_cache_warming(self, cache):
        """Test cache warming functionality"""
        def warm_func(key: str) -> str:
            return f"warmed_{key}"
        
        keys = ["key1", "key2", "key3"]
        warmed_count = cache.warm_cache(warm_func, keys)
        
        assert warmed_count == 3
        assert cache.get("key1") == "warmed_key1"
        assert cache.get("key2") == "warmed_key2"
        assert cache.get("key3") == "warmed_key3"
    
    def test_cache_statistics(self, cache):
        """Test cache statistics"""
        # Perform some operations
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # hit
        cache.get("nonexistent")  # miss
        
        stats = cache.get_stats()
        
        assert stats["cache_size"] == 2
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["max_size"] == 100
        assert "memory_usage_bytes" in stats
        assert "age_distribution" in stats
    
    def test_cache_clear(self, cache):
        """Test cache clearing"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert cache.get("key1") == "value1"
        assert cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        
        stats = cache.get_stats()
        assert stats["cache_size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
    
    def test_cache_entry_info(self, cache):
        """Test detailed cache entry information"""
        tags = {"test", "info"}
        cache.set("test_key", "test_value", tags=tags)
        
        info = cache.get_entry_info("test_key")
        
        assert info is not None
        assert info["key"] == "test_key"
        assert info["value_type"] == "str"
        assert info["tags"] == ["test", "info"]
        assert "created_at" in info
        assert "last_accessed" in info
        assert "access_count" in info
    
    def test_cache_thread_safety(self, cache):
        """Test cache thread safety"""
        def worker(thread_id: int):
            for i in range(10):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                cache.set(key, value)
                retrieved = cache.get(key)
                assert retrieved == value
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify cache integrity
        stats = cache.get_stats()
        assert stats["cache_size"] == 50  # 5 threads * 10 keys each


class TestDomainSpecificCache:
    """Test DomainSpecificCache functionality"""
    
    @pytest.fixture
    def domain_cache(self):
        """Create a test domain-specific cache"""
        cache = DomainCache()
        domain_cache = DomainSpecificCache(cache)
        yield domain_cache
        cache.shutdown()
    
    @pytest.fixture
    def sample_domain(self):
        """Create a sample domain for testing"""
        tools = DomainTools(
            linter="pylint",
            formatter="black",
            validator="mypy"
        )
        
        package_potential = PackagePotential(
            score=0.8,
            reasons=["Well-defined interface"],
            dependencies=["requests"],
            estimated_effort="medium",
            blockers=[]
        )
        
        metadata = DomainMetadata(
            demo_role="core",
            extraction_candidate="yes",
            package_potential=package_potential,
            status="active",
            tags=["python", "core"]
        )
        
        return Domain(
            name="test_domain",
            description="Test domain for caching",
            patterns=["src/test/**/*.py"],
            content_indicators=["test", "domain"],
            requirements=["python>=3.8"],
            dependencies=["base_domain"],
            tools=tools,
            metadata=metadata
        )
    
    def test_domain_caching(self, domain_cache, sample_domain):
        """Test domain-specific caching"""
        # Cache domain
        assert domain_cache.cache_domain(sample_domain)
        
        # Retrieve domain
        cached_domain = domain_cache.get_domain("test_domain")
        assert cached_domain is not None
        assert cached_domain.name == "test_domain"
        assert cached_domain.description == "Test domain for caching"
    
    def test_domain_collection_caching(self, domain_cache, sample_domain):
        """Test domain collection caching"""
        domains = {"test_domain": sample_domain}
        
        # Cache collection
        assert domain_cache.cache_domain_collection(domains)
        
        # Retrieve collection
        cached_collection = domain_cache.get_domain_collection()
        assert cached_collection is not None
        assert "test_domain" in cached_collection
        assert cached_collection["test_domain"].name == "test_domain"
    
    def test_domain_invalidation(self, domain_cache, sample_domain):
        """Test domain-specific invalidation"""
        # Cache domain and collection
        domain_cache.cache_domain(sample_domain)
        domain_cache.cache_domain_collection({"test_domain": sample_domain})
        
        # Verify cached
        assert domain_cache.get_domain("test_domain") is not None
        assert domain_cache.get_domain_collection() is not None
        
        # Invalidate domain
        assert domain_cache.invalidate_domain("test_domain")
        
        # Verify invalidated
        assert domain_cache.get_domain("test_domain") is None
        assert domain_cache.get_domain_collection() is None
    
    def test_category_invalidation(self, domain_cache, sample_domain):
        """Test category-based invalidation"""
        # Cache domain
        domain_cache.cache_domain(sample_domain)
        
        # Verify cached
        assert domain_cache.get_domain("test_domain") is not None
        
        # Invalidate by category
        invalidated = domain_cache.invalidate_by_category("core")
        assert invalidated >= 1
        
        # Verify invalidated
        assert domain_cache.get_domain("test_domain") is None
    
    def test_domain_cache_warming(self, domain_cache, sample_domain):
        """Test domain cache warming"""
        def domain_loader(domain_name: str):
            if domain_name == "test_domain":
                return sample_domain
            return None
        
        # Warm cache
        warmed_count = domain_cache.warm_domains(domain_loader, ["test_domain", "nonexistent"])
        assert warmed_count == 1
        
        # Verify warmed
        cached_domain = domain_cache.get_domain("test_domain")
        assert cached_domain is not None
        assert cached_domain.name == "test_domain"


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for cache system"""
    
    def test_cache_with_registry_manager(self):
        """Test cache integration with registry manager"""
        # This would test the full integration with DomainRegistryManager
        # For now, we'll create a mock test
        
        cache = DomainCache()
        domain_cache = DomainSpecificCache(cache)
        
        # Mock domain
        tools = DomainTools("pylint", "black", "mypy")
        metadata = DomainMetadata(
            "core", "yes", 
            PackagePotential(0.8, [], [], "medium", []),
            tags=["test"]
        )
        domain = Domain(
            "integration_test", "Integration test domain",
            ["src/**/*.py"], ["test"], [], [], tools, metadata
        )
        
        # Test caching workflow
        assert domain_cache.cache_domain(domain)
        cached = domain_cache.get_domain("integration_test")
        assert cached is not None
        assert cached.name == "integration_test"
        
        cache.shutdown()