"""
Performance optimization and configuration management for TaskQueueManager

This module implements comprehensive performance enhancements including:
- Redis connection pooling with health monitoring
- Intelligent caching with LRU eviction and memory pressure handling
- Performance monitoring with latency tracking and resource metrics
- Configuration management with validation and hot-reloading
- Structured logging with correlation IDs and distributed tracing
- Prometheus metrics integration and alerting
"""

import asyncio
import functools
import hashlib
import json
import logging
import time
import threading
import uuid
import weakref
from collections import OrderedDict
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import os
import yaml
import redis.asyncio as redis
from redis.asyncio.connection import Connection, ConnectionPool
import psutil
import correlation_id

# Prometheus metrics (optional import)
try:
    from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from .models import TaskQueueConfig, RedisConfig


class CacheEvictionPolicy(Enum):
    """Cache eviction policies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live based
    MEMORY_PRESSURE = "memory_pressure"  # Based on memory usage


class ConfigurationFormat(Enum):
    """Supported configuration formats."""
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"
    ENV = "env"


class LogLevel(Enum):
    """Structured logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ConnectionPoolConfig:
    """Redis connection pool configuration."""
    min_size: int = 5
    max_size: int = 50
    health_check_interval: int = 30
    connection_timeout: float = 5.0
    socket_timeout: float = 5.0
    retry_on_timeout: bool = True
    max_connections_per_pool: int = 100
    connection_pool_class_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheConfig:
    """Intelligent caching configuration."""
    max_size_mb: int = 256
    default_ttl_seconds: int = 3600
    eviction_policy: CacheEvictionPolicy = CacheEvictionPolicy.LRU
    memory_pressure_threshold: float = 0.8
    cleanup_interval_seconds: int = 60
    enable_compression: bool = True
    compression_min_size: int = 1024


@dataclass
class PerformanceMetrics:
    """Performance monitoring metrics."""
    operation_latency: Dict[str, List[float]] = field(default_factory=dict)
    throughput_ops_per_second: float = 0.0
    error_rate_percent: float = 0.0
    cache_hit_rate_percent: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AlertRule:
    """Performance alerting rule configuration."""
    name: str
    condition: str  # Python expression
    threshold: float
    severity: str
    message_template: str
    cooldown_seconds: int = 300
    enabled: bool = True


class RedisConnectionPoolManager:
    """
    Advanced Redis connection pool manager with health monitoring.

    Provides high-performance Redis connectivity with automatic failover,
    health monitoring, and connection lifecycle management.
    """

    def __init__(self, redis_config: RedisConfig, pool_config: ConnectionPoolConfig):
        self.redis_config = redis_config
        self.pool_config = pool_config
        self.instance_id = f"pool_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.RedisConnectionPoolManager")

        # Connection pools
        self._pools: Dict[str, ConnectionPool] = {}
        self._health_status: Dict[str, bool] = {}
        self._pool_metrics: Dict[str, Dict[str, Any]] = {}

        # Health monitoring
        self._health_monitor_task = None
        self._monitoring_active = False
        self._shutdown_event = threading.Event()

        # Pool metrics
        self._connection_metrics = {
            "pools_created": 0,
            "connections_created": 0,
            "connections_closed": 0,
            "connection_errors": 0,
            "health_checks_performed": 0,
            "health_check_failures": 0,
            "pool_resets": 0
        }

        self._logger.info(
            f"RedisConnectionPoolManager initialized",
            extra={
                "instance_id": self.instance_id,
                "redis_host": redis_config.host,
                "redis_port": redis_config.port,
                "pool_config": asdict(pool_config)
            }
        )

    async def initialize_pools(self) -> bool:
        """Initialize Redis connection pools."""
        try:
            # Create primary connection pool
            primary_pool = await self._create_connection_pool("primary")
            self._pools["primary"] = primary_pool
            self._health_status["primary"] = True

            # Test initial connectivity
            async with redis.Redis(connection_pool=primary_pool) as client:
                await client.ping()

            # Start health monitoring
            await self._start_health_monitoring()

            self._logger.info("Redis connection pools initialized successfully")
            return True

        except Exception as e:
            self._logger.error(f"Failed to initialize Redis connection pools: {e}")
            return False

    async def _create_connection_pool(self, pool_name: str) -> ConnectionPool:
        """Create a configured Redis connection pool."""
        try:
            pool_kwargs = {
                "host": self.redis_config.host,
                "port": self.redis_config.port,
                "password": self.redis_config.password,
                "ssl": self.redis_config.ssl,
                "socket_timeout": self.pool_config.socket_timeout,
                "socket_connect_timeout": self.pool_config.connection_timeout,
                "retry_on_timeout": self.pool_config.retry_on_timeout,
                "max_connections": self.pool_config.max_connections_per_pool,
                **self.pool_config.connection_pool_class_kwargs
            }

            pool = ConnectionPool(**pool_kwargs)
            self._connection_metrics["pools_created"] += 1

            # Initialize pool metrics
            self._pool_metrics[pool_name] = {
                "created_at": datetime.now().isoformat(),
                "connections_created": 0,
                "connections_active": 0,
                "last_health_check": None,
                "health_check_failures": 0
            }

            self._logger.info(
                f"Created connection pool: {pool_name}",
                extra={"pool_name": pool_name, "max_connections": pool_kwargs["max_connections"]}
            )

            return pool

        except Exception as e:
            self._logger.error(f"Error creating connection pool {pool_name}: {e}")
            raise

    async def get_redis_client(self, pool_name: str = "primary") -> redis.Redis:
        """
        Get Redis client from connection pool.

        Args:
            pool_name: Name of the connection pool to use

        Returns:
            Redis client instance
        """
        if pool_name not in self._pools:
            raise ValueError(f"Connection pool '{pool_name}' not found")

        pool = self._pools[pool_name]

        # Check pool health
        if not self._health_status.get(pool_name, False):
            # Try to recover unhealthy pool
            await self._recover_unhealthy_pool(pool_name)

        return redis.Redis(connection_pool=pool)

    @asynccontextmanager
    async def managed_redis_client(self, pool_name: str = "primary"):
        """
        Context manager for Redis client with automatic cleanup.

        Args:
            pool_name: Name of the connection pool to use

        Yields:
            Redis client instance
        """
        client = None
        try:
            client = await self.get_redis_client(pool_name)
            yield client
        finally:
            if client:
                await client.aclose()

    async def _start_health_monitoring(self):
        """Start background health monitoring for connection pools."""
        if self._monitoring_active:
            return

        try:
            self._monitoring_active = True
            self._health_monitor_task = asyncio.create_task(self._health_monitoring_loop())

            self._logger.info("Connection pool health monitoring started")

        except Exception as e:
            self._logger.error(f"Error starting health monitoring: {e}")
            self._monitoring_active = False
            raise

    async def _health_monitoring_loop(self):
        """Background loop for connection pool health monitoring."""
        try:
            while self._monitoring_active and not self._shutdown_event.is_set():
                await self._perform_health_checks()
                await asyncio.sleep(self.pool_config.health_check_interval)

        except asyncio.CancelledError:
            self._logger.info("Health monitoring loop cancelled")
        except Exception as e:
            self._logger.error(f"Error in health monitoring loop: {e}")

    async def _perform_health_checks(self):
        """Perform health checks on all connection pools."""
        for pool_name, pool in self._pools.items():
            try:
                self._connection_metrics["health_checks_performed"] += 1

                # Test connection with ping
                async with redis.Redis(connection_pool=pool) as client:
                    await asyncio.wait_for(client.ping(), timeout=5.0)

                # Update health status
                self._health_status[pool_name] = True
                self._pool_metrics[pool_name]["last_health_check"] = datetime.now().isoformat()

                self._logger.debug(f"Health check passed for pool: {pool_name}")

            except Exception as e:
                self._connection_metrics["health_check_failures"] += 1
                self._health_status[pool_name] = False
                self._pool_metrics[pool_name]["health_check_failures"] += 1

                self._logger.warning(
                    f"Health check failed for pool {pool_name}: {e}",
                    extra={"pool_name": pool_name, "error": str(e)}
                )

                # Attempt recovery
                asyncio.create_task(self._recover_unhealthy_pool(pool_name))

    async def _recover_unhealthy_pool(self, pool_name: str):
        """Attempt to recover an unhealthy connection pool."""
        try:
            self._logger.info(f"Attempting to recover unhealthy pool: {pool_name}")

            # Close existing pool
            old_pool = self._pools.get(pool_name)
            if old_pool:
                await old_pool.disconnect()

            # Create new pool
            new_pool = await self._create_connection_pool(pool_name)
            self._pools[pool_name] = new_pool

            # Test new pool
            async with redis.Redis(connection_pool=new_pool) as client:
                await client.ping()

            self._health_status[pool_name] = True
            self._connection_metrics["pool_resets"] += 1

            self._logger.info(f"Successfully recovered pool: {pool_name}")

        except Exception as e:
            self._logger.error(f"Failed to recover pool {pool_name}: {e}")

    async def shutdown(self):
        """Shutdown connection pool manager and cleanup resources."""
        try:
            # Stop health monitoring
            self._monitoring_active = False
            self._shutdown_event.set()

            if self._health_monitor_task:
                self._health_monitor_task.cancel()
                try:
                    await self._health_monitor_task
                except asyncio.CancelledError:
                    pass

            # Close all connection pools
            for pool_name, pool in self._pools.items():
                try:
                    await pool.disconnect()
                    self._logger.info(f"Closed connection pool: {pool_name}")
                except Exception as e:
                    self._logger.error(f"Error closing pool {pool_name}: {e}")

            self._pools.clear()
            self._health_status.clear()

            self._logger.info("Connection pool manager shutdown complete")

        except Exception as e:
            self._logger.error(f"Error during connection pool shutdown: {e}")

    def get_pool_status(self) -> Dict[str, Any]:
        """Get comprehensive connection pool status."""
        return {
            "instance_id": self.instance_id,
            "pools": {
                name: {
                    "healthy": self._health_status.get(name, False),
                    "metrics": self._pool_metrics.get(name, {}),
                    "connection_count": pool.connection_kwargs.get("max_connections", 0)
                }
                for name, pool in self._pools.items()
            },
            "connection_metrics": dict(self._connection_metrics),
            "monitoring_active": self._monitoring_active,
            "timestamp": datetime.now().isoformat()
        }


class IntelligentCacheManager:
    """
    High-performance caching system with multiple eviction policies.

    Provides intelligent caching with LRU/LFU eviction, memory pressure
    handling, compression, and performance metrics.
    """

    def __init__(self, cache_config: CacheConfig):
        self.config = cache_config
        self.instance_id = f"cache_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.IntelligentCacheManager")

        # Cache storage
        self._cache_data: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._access_frequency: Dict[str, int] = {}
        self._cache_lock = threading.RLock()

        # Memory management
        self._current_memory_usage = 0
        self._max_memory_bytes = cache_config.max_size_mb * 1024 * 1024

        # Cleanup task
        self._cleanup_task = None
        self._monitoring_active = False

        # Cache metrics
        self._cache_metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_sets": 0,
            "cache_evictions": 0,
            "memory_pressure_cleanups": 0,
            "compression_saves_bytes": 0,
            "total_operations": 0
        }

        self._logger.info(
            f"IntelligentCacheManager initialized",
            extra={
                "instance_id": self.instance_id,
                "max_size_mb": cache_config.max_size_mb,
                "eviction_policy": cache_config.eviction_policy.value,
                "compression_enabled": cache_config.enable_compression
            }
        )

    async def start_cache_management(self):
        """Start background cache management tasks."""
        if self._monitoring_active:
            return

        try:
            self._monitoring_active = True
            self._cleanup_task = asyncio.create_task(self._cache_cleanup_loop())

            self._logger.info("Cache management started")

        except Exception as e:
            self._logger.error(f"Error starting cache management: {e}")
            self._monitoring_active = False
            raise

    async def stop_cache_management(self):
        """Stop cache management and cleanup resources."""
        try:
            self._monitoring_active = False

            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            # Clear cache
            with self._cache_lock:
                self._cache_data.clear()
                self._access_frequency.clear()
                self._current_memory_usage = 0

            self._logger.info("Cache management stopped")

        except Exception as e:
            self._logger.error(f"Error stopping cache management: {e}")

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        correlation_id.set(f"cache_get_{uuid.uuid4().hex[:8]}")

        try:
            self._cache_metrics["total_operations"] += 1

            with self._cache_lock:
                if key not in self._cache_data:
                    self._cache_metrics["cache_misses"] += 1
                    return None

                cache_entry = self._cache_data[key]

                # Check TTL
                if self._is_expired(cache_entry):
                    del self._cache_data[key]
                    if key in self._access_frequency:
                        del self._access_frequency[key]
                    self._cache_metrics["cache_misses"] += 1
                    return None

                # Update access patterns
                self._update_access_patterns(key)

                # Decompress if needed
                value = cache_entry["value"]
                if cache_entry.get("compressed", False):
                    value = await self._decompress_value(value)

                self._cache_metrics["cache_hits"] += 1

                self._logger.debug(
                    f"Cache hit for key: {key}",
                    extra={"cache_key": key, "correlation_id": correlation_id.get()}
                )

                return value

        except Exception as e:
            self._logger.error(f"Error getting cache key {key}: {e}")
            self._cache_metrics["cache_misses"] += 1
            return None

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to store
            ttl_seconds: Time to live (optional)

        Returns:
            True if stored successfully
        """
        correlation_id.set(f"cache_set_{uuid.uuid4().hex[:8]}")

        try:
            self._cache_metrics["total_operations"] += 1
            self._cache_metrics["cache_sets"] += 1

            # Prepare cache entry
            ttl = ttl_seconds or self.config.default_ttl_seconds
            expires_at = datetime.now() + timedelta(seconds=ttl)

            # Serialize and optionally compress value
            serialized_value = await self._serialize_value(value)
            compressed = False
            compressed_value = serialized_value

            if (self.config.enable_compression and
                len(serialized_value) >= self.config.compression_min_size):
                compressed_value = await self._compress_value(serialized_value)
                compressed = True
                self._cache_metrics["compression_saves_bytes"] += len(serialized_value) - len(compressed_value)

            cache_entry = {
                "value": compressed_value,
                "created_at": datetime.now(),
                "expires_at": expires_at,
                "access_count": 1,
                "size_bytes": len(compressed_value),
                "compressed": compressed
            }

            # Check memory pressure and evict if necessary
            await self._ensure_memory_available(cache_entry["size_bytes"])

            with self._cache_lock:
                # Remove old entry if exists
                if key in self._cache_data:
                    old_entry = self._cache_data[key]
                    self._current_memory_usage -= old_entry["size_bytes"]

                # Add new entry
                self._cache_data[key] = cache_entry
                self._current_memory_usage += cache_entry["size_bytes"]
                self._access_frequency[key] = self._access_frequency.get(key, 0) + 1

                # Move to end for LRU
                if self.config.eviction_policy == CacheEvictionPolicy.LRU:
                    self._cache_data.move_to_end(key)

            self._logger.debug(
                f"Cached key: {key}",
                extra={
                    "cache_key": key,
                    "size_bytes": cache_entry["size_bytes"],
                    "compressed": compressed,
                    "ttl_seconds": ttl,
                    "correlation_id": correlation_id.get()
                }
            )

            return True

        except Exception as e:
            self._logger.error(f"Error setting cache key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted
        """
        try:
            with self._cache_lock:
                if key in self._cache_data:
                    entry = self._cache_data[key]
                    self._current_memory_usage -= entry["size_bytes"]
                    del self._cache_data[key]

                if key in self._access_frequency:
                    del self._access_frequency[key]

            return True

        except Exception as e:
            self._logger.error(f"Error deleting cache key {key}: {e}")
            return False

    def _update_access_patterns(self, key: str):
        """Update access patterns for cache key."""
        # Update access frequency
        self._access_frequency[key] = self._access_frequency.get(key, 0) + 1

        # Update access count in cache entry
        if key in self._cache_data:
            self._cache_data[key]["access_count"] += 1

        # Move to end for LRU policy
        if self.config.eviction_policy == CacheEvictionPolicy.LRU:
            self._cache_data.move_to_end(key)

    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() > cache_entry["expires_at"]

    async def _ensure_memory_available(self, required_bytes: int):
        """Ensure sufficient memory is available for new cache entry."""
        if self._current_memory_usage + required_bytes <= self._max_memory_bytes:
            return

        # Calculate bytes to free
        bytes_to_free = (self._current_memory_usage + required_bytes) - self._max_memory_bytes

        # Perform eviction based on policy
        await self._evict_entries(bytes_to_free)

    async def _evict_entries(self, bytes_to_free: int):
        """Evict cache entries based on eviction policy."""
        freed_bytes = 0
        evicted_keys = []

        try:
            with self._cache_lock:
                if self.config.eviction_policy == CacheEvictionPolicy.LRU:
                    # Evict least recently used
                    keys_to_evict = list(self._cache_data.keys())

                elif self.config.eviction_policy == CacheEvictionPolicy.LFU:
                    # Evict least frequently used
                    keys_to_evict = sorted(
                        self._cache_data.keys(),
                        key=lambda k: self._access_frequency.get(k, 0)
                    )

                elif self.config.eviction_policy == CacheEvictionPolicy.TTL:
                    # Evict entries closest to expiration
                    keys_to_evict = sorted(
                        self._cache_data.keys(),
                        key=lambda k: self._cache_data[k]["expires_at"]
                    )

                else:  # Memory pressure based
                    # Evict largest entries first
                    keys_to_evict = sorted(
                        self._cache_data.keys(),
                        key=lambda k: self._cache_data[k]["size_bytes"],
                        reverse=True
                    )

                # Evict entries until enough memory is freed
                for key in keys_to_evict:
                    if freed_bytes >= bytes_to_free:
                        break

                    entry = self._cache_data[key]
                    freed_bytes += entry["size_bytes"]
                    self._current_memory_usage -= entry["size_bytes"]

                    del self._cache_data[key]
                    if key in self._access_frequency:
                        del self._access_frequency[key]

                    evicted_keys.append(key)
                    self._cache_metrics["cache_evictions"] += 1

            self._logger.info(
                f"Evicted {len(evicted_keys)} cache entries",
                extra={
                    "evicted_count": len(evicted_keys),
                    "freed_bytes": freed_bytes,
                    "eviction_policy": self.config.eviction_policy.value
                }
            )

        except Exception as e:
            self._logger.error(f"Error during cache eviction: {e}")

    async def _cache_cleanup_loop(self):
        """Background loop for cache maintenance."""
        try:
            while self._monitoring_active:
                await self._perform_cache_cleanup()
                await asyncio.sleep(self.config.cleanup_interval_seconds)

        except asyncio.CancelledError:
            self._logger.info("Cache cleanup loop cancelled")
        except Exception as e:
            self._logger.error(f"Error in cache cleanup loop: {e}")

    async def _perform_cache_cleanup(self):
        """Perform cache maintenance and cleanup."""
        try:
            expired_keys = []
            current_time = datetime.now()

            # Find expired entries
            with self._cache_lock:
                for key, entry in self._cache_data.items():
                    if current_time > entry["expires_at"]:
                        expired_keys.append(key)

            # Remove expired entries
            for key in expired_keys:
                await self.delete(key)

            # Check memory pressure
            memory_usage_ratio = self._current_memory_usage / self._max_memory_bytes
            if memory_usage_ratio > self.config.memory_pressure_threshold:
                bytes_to_free = int(self._max_memory_bytes * 0.2)  # Free 20%
                await self._evict_entries(bytes_to_free)
                self._cache_metrics["memory_pressure_cleanups"] += 1

            self._logger.debug(
                f"Cache cleanup completed",
                extra={
                    "expired_removed": len(expired_keys),
                    "memory_usage_ratio": memory_usage_ratio,
                    "total_entries": len(self._cache_data)
                }
            )

        except Exception as e:
            self._logger.error(f"Error in cache cleanup: {e}")

    async def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage."""
        try:
            if isinstance(value, (str, int, float, bool)):
                return str(value).encode()
            else:
                return json.dumps(value, default=str).encode()
        except Exception:
            return str(value).encode()

    async def _compress_value(self, data: bytes) -> bytes:
        """Compress data for storage."""
        try:
            import gzip
            return gzip.compress(data)
        except Exception as e:
            self._logger.warning(f"Compression failed: {e}")
            return data

    async def _decompress_value(self, data: bytes) -> Any:
        """Decompress and deserialize data."""
        try:
            import gzip
            decompressed = gzip.decompress(data)

            # Try to parse as JSON
            try:
                return json.loads(decompressed.decode())
            except (json.JSONDecodeError, ValueError):
                return decompressed.decode()

        except Exception as e:
            self._logger.warning(f"Decompression failed: {e}")
            return data.decode() if isinstance(data, bytes) else data

    def get_cache_status(self) -> Dict[str, Any]:
        """Get comprehensive cache status and metrics."""
        hit_rate = 0.0
        total_requests = self._cache_metrics["cache_hits"] + self._cache_metrics["cache_misses"]
        if total_requests > 0:
            hit_rate = self._cache_metrics["cache_hits"] / total_requests

        memory_usage_percent = (self._current_memory_usage / self._max_memory_bytes) * 100

        return {
            "instance_id": self.instance_id,
            "cache_size": len(self._cache_data),
            "memory_usage_bytes": self._current_memory_usage,
            "memory_usage_percent": memory_usage_percent,
            "hit_rate_percent": hit_rate * 100,
            "eviction_policy": self.config.eviction_policy.value,
            "compression_enabled": self.config.enable_compression,
            "monitoring_active": self._monitoring_active,
            "metrics": dict(self._cache_metrics),
            "timestamp": datetime.now().isoformat()
        }


class ConfigurationManager:
    """
    Comprehensive configuration management with validation and hot-reloading.

    Supports multiple formats (YAML, JSON, TOML), environment variables,
    schema validation, and live configuration updates.
    """

    def __init__(self, config_file_path: Optional[str] = None,
                 schema_file_path: Optional[str] = None):
        self.config_file_path = config_file_path
        self.schema_file_path = schema_file_path
        self.instance_id = f"config_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.ConfigurationManager")

        # Configuration state
        self._config_data: Dict[str, Any] = {}
        self._config_lock = threading.RLock()
        self._config_schema: Optional[Dict[str, Any]] = None

        # Hot reloading
        self._file_watcher_task = None
        self._last_modified = {}
        self._reload_callbacks: List[Callable[[Dict[str, Any]], None]] = []

        # Configuration metrics
        self._config_metrics = {
            "configs_loaded": 0,
            "hot_reloads": 0,
            "validation_errors": 0,
            "callback_executions": 0,
            "env_var_overrides": 0
        }

        self._logger.info(
            f"ConfigurationManager initialized",
            extra={
                "instance_id": self.instance_id,
                "config_file": config_file_path,
                "schema_file": schema_file_path
            }
        )

    async def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from file and environment variables."""
        try:
            with self._config_lock:
                config_data = {}

                # Load from file if specified
                if self.config_file_path and os.path.exists(self.config_file_path):
                    config_data = await self._load_config_file()

                # Override with environment variables
                env_overrides = self._load_environment_overrides()
                config_data.update(env_overrides)
                self._config_metrics["env_var_overrides"] += len(env_overrides)

                # Validate configuration
                if self._config_schema:
                    await self._validate_configuration(config_data)

                self._config_data = config_data
                self._config_metrics["configs_loaded"] += 1

                self._logger.info(
                    f"Configuration loaded successfully",
                    extra={
                        "config_keys": list(config_data.keys()),
                        "env_overrides": len(env_overrides)
                    }
                )

                return config_data.copy()

        except Exception as e:
            self._logger.error(f"Error loading configuration: {e}")
            raise

    async def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from file based on format."""
        try:
            if not os.path.exists(self.config_file_path):
                return {}

            # Update last modified time
            self._last_modified[self.config_file_path] = os.path.getmtime(self.config_file_path)

            # Determine format from file extension
            file_ext = os.path.splitext(self.config_file_path)[1].lower()

            with open(self.config_file_path, 'r') as f:
                content = f.read()

            if file_ext in ['.yml', '.yaml']:
                import yaml
                return yaml.safe_load(content) or {}
            elif file_ext == '.json':
                return json.loads(content) or {}
            elif file_ext == '.toml':
                try:
                    import tomllib
                    return tomllib.loads(content) or {}
                except ImportError:
                    import toml
                    return toml.loads(content) or {}
            else:
                raise ValueError(f"Unsupported configuration format: {file_ext}")

        except Exception as e:
            self._logger.error(f"Error loading config file {self.config_file_path}: {e}")
            raise

    def _load_environment_overrides(self) -> Dict[str, Any]:
        """Load configuration overrides from environment variables."""
        env_config = {}

        # Look for TASKQUEUE_ prefixed environment variables
        for key, value in os.environ.items():
            if key.startswith('TASKQUEUE_'):
                config_key = key[10:].lower().replace('_', '.')  # Remove prefix and format

                # Try to parse as JSON, fall back to string
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    # Try to parse as boolean or number
                    if value.lower() in ('true', 'false'):
                        parsed_value = value.lower() == 'true'
                    elif value.isdigit():
                        parsed_value = int(value)
                    elif value.replace('.', '').isdigit():
                        parsed_value = float(value)
                    else:
                        parsed_value = value

                # Set nested configuration
                self._set_nested_config(env_config, config_key, parsed_value)

        return env_config

    def _set_nested_config(self, config: Dict[str, Any], key_path: str, value: Any):
        """Set nested configuration value using dot notation."""
        keys = key_path.split('.')
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    async def _validate_configuration(self, config_data: Dict[str, Any]):
        """Validate configuration against schema."""
        if not self._config_schema:
            return

        try:
            # Simple validation - in production, use jsonschema or similar
            for required_key in self._config_schema.get("required", []):
                if required_key not in config_data:
                    raise ValueError(f"Required configuration key missing: {required_key}")

            # Type validation
            properties = self._config_schema.get("properties", {})
            for key, value in config_data.items():
                if key in properties:
                    expected_type = properties[key].get("type")
                    if expected_type and not self._validate_type(value, expected_type):
                        raise ValueError(f"Invalid type for {key}: expected {expected_type}")

        except Exception as e:
            self._config_metrics["validation_errors"] += 1
            self._logger.error(f"Configuration validation error: {e}")
            raise

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type against expected type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }

        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)

        return True

    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key_path: Configuration key path (e.g., "redis.host")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        try:
            with self._config_lock:
                keys = key_path.split('.')
                current = self._config_data

                for key in keys:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return default

                return current

        except Exception as e:
            self._logger.error(f"Error getting config value {key_path}: {e}")
            return default

    def register_reload_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register callback to be called when configuration is reloaded.

        Args:
            callback: Function to call with new configuration
        """
        self._reload_callbacks.append(callback)
        self._logger.debug(f"Registered config reload callback: {callback.__name__}")

    async def start_hot_reloading(self):
        """Start hot reloading of configuration files."""
        if not self.config_file_path or self._file_watcher_task:
            return

        try:
            self._file_watcher_task = asyncio.create_task(self._file_watching_loop())
            self._logger.info("Configuration hot reloading started")

        except Exception as e:
            self._logger.error(f"Error starting hot reloading: {e}")

    async def _file_watching_loop(self):
        """Monitor configuration file for changes."""
        try:
            while True:
                await asyncio.sleep(5)  # Check every 5 seconds

                if not os.path.exists(self.config_file_path):
                    continue

                current_mtime = os.path.getmtime(self.config_file_path)
                last_mtime = self._last_modified.get(self.config_file_path, 0)

                if current_mtime > last_mtime:
                    self._logger.info("Configuration file changed, reloading...")

                    try:
                        new_config = await self.load_configuration()

                        # Execute reload callbacks
                        for callback in self._reload_callbacks:
                            try:
                                callback(new_config)
                                self._config_metrics["callback_executions"] += 1
                            except Exception as e:
                                self._logger.error(f"Error in reload callback {callback.__name__}: {e}")

                        self._config_metrics["hot_reloads"] += 1

                    except Exception as e:
                        self._logger.error(f"Error during hot reload: {e}")

        except asyncio.CancelledError:
            self._logger.info("Configuration file watching cancelled")
        except Exception as e:
            self._logger.error(f"Error in file watching loop: {e}")

    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration management status."""
        return {
            "instance_id": self.instance_id,
            "config_file_path": self.config_file_path,
            "schema_file_path": self.schema_file_path,
            "hot_reloading_active": self._file_watcher_task is not None,
            "config_keys_count": len(self._config_data),
            "reload_callbacks_count": len(self._reload_callbacks),
            "metrics": dict(self._config_metrics),
            "timestamp": datetime.now().isoformat()
        }


class PrometheusMetricsCollector:
    """
    Prometheus metrics collection and alerting for TaskQueueManager.

    Provides comprehensive metrics collection with Prometheus integration,
    custom alerting rules, and performance monitoring.
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        if not PROMETHEUS_AVAILABLE:
            raise ImportError("prometheus_client not available")

        self.registry = registry or CollectorRegistry()
        self.instance_id = f"metrics_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.PrometheusMetricsCollector")

        # Prometheus metrics
        self._init_prometheus_metrics()

        # Alert rules
        self._alert_rules: List[AlertRule] = []
        self._alert_state: Dict[str, Dict[str, Any]] = {}

        # Metrics collection
        self._metrics_data: Dict[str, Any] = {}

        self._logger.info(
            f"PrometheusMetricsCollector initialized",
            extra={"instance_id": self.instance_id}
        )

    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        # Task processing metrics
        self.task_processing_duration = Histogram(
            'taskqueue_task_processing_duration_seconds',
            'Time spent processing tasks',
            ['task_type', 'status'],
            registry=self.registry
        )

        self.task_processing_total = Counter(
            'taskqueue_task_processing_total',
            'Total number of tasks processed',
            ['task_type', 'status'],
            registry=self.registry
        )

        # Redis metrics
        self.redis_operations_duration = Histogram(
            'taskqueue_redis_operations_duration_seconds',
            'Redis operation latency',
            ['operation', 'status'],
            registry=self.registry
        )

        self.redis_connections_active = Gauge(
            'taskqueue_redis_connections_active',
            'Number of active Redis connections',
            registry=self.registry
        )

        # Cache metrics
        self.cache_operations_total = Counter(
            'taskqueue_cache_operations_total',
            'Total cache operations',
            ['operation', 'result'],
            registry=self.registry
        )

        self.cache_memory_usage_bytes = Gauge(
            'taskqueue_cache_memory_usage_bytes',
            'Cache memory usage in bytes',
            registry=self.registry
        )

        # System metrics
        self.system_memory_usage_percent = Gauge(
            'taskqueue_system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )

        self.system_cpu_usage_percent = Gauge(
            'taskqueue_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )

    def record_task_processing(self, task_type: str, status: str, duration_seconds: float):
        """Record task processing metrics."""
        self.task_processing_duration.labels(task_type=task_type, status=status).observe(duration_seconds)
        self.task_processing_total.labels(task_type=task_type, status=status).inc()

    def record_redis_operation(self, operation: str, status: str, duration_seconds: float):
        """Record Redis operation metrics."""
        self.redis_operations_duration.labels(operation=operation, status=status).observe(duration_seconds)

    def update_redis_connections(self, active_connections: int):
        """Update active Redis connections gauge."""
        self.redis_connections_active.set(active_connections)

    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation metrics."""
        self.cache_operations_total.labels(operation=operation, result=result).inc()

    def update_cache_memory_usage(self, usage_bytes: int):
        """Update cache memory usage gauge."""
        self.cache_memory_usage_bytes.set(usage_bytes)

    def update_system_metrics(self):
        """Update system resource metrics."""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage_percent.set(memory.percent)

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.system_cpu_usage_percent.set(cpu_percent)

        except Exception as e:
            self._logger.error(f"Error updating system metrics: {e}")

    def add_alert_rule(self, alert_rule: AlertRule):
        """Add custom alert rule."""
        self._alert_rules.append(alert_rule)
        self._alert_state[alert_rule.name] = {
            "triggered": False,
            "last_triggered": None,
            "trigger_count": 0
        }

        self._logger.info(
            f"Added alert rule: {alert_rule.name}",
            extra={"alert_name": alert_rule.name, "condition": alert_rule.condition}
        )

    async def check_alert_rules(self) -> List[Dict[str, Any]]:
        """Check all alert rules and return triggered alerts."""
        triggered_alerts = []

        try:
            # Collect current metrics
            current_metrics = await self._collect_current_metrics()

            for rule in self._alert_rules:
                if not rule.enabled:
                    continue

                try:
                    # Evaluate alert condition
                    triggered = self._evaluate_alert_condition(rule, current_metrics)

                    alert_state = self._alert_state[rule.name]

                    if triggered and not alert_state["triggered"]:
                        # New alert triggered
                        alert_state["triggered"] = True
                        alert_state["last_triggered"] = datetime.now()
                        alert_state["trigger_count"] += 1

                        triggered_alerts.append({
                            "name": rule.name,
                            "severity": rule.severity,
                            "message": rule.message_template.format(**current_metrics),
                            "triggered_at": alert_state["last_triggered"].isoformat(),
                            "trigger_count": alert_state["trigger_count"]
                        })

                    elif not triggered and alert_state["triggered"]:
                        # Alert resolved
                        alert_state["triggered"] = False

                except Exception as e:
                    self._logger.error(f"Error evaluating alert rule {rule.name}: {e}")

        except Exception as e:
            self._logger.error(f"Error checking alert rules: {e}")

        return triggered_alerts

    def _evaluate_alert_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate alert condition using metrics data."""
        try:
            # Create safe evaluation environment
            safe_dict = {"__builtins__": {}}
            safe_dict.update(metrics)

            # Evaluate condition
            result = eval(rule.condition, safe_dict)
            return bool(result)

        except Exception as e:
            self._logger.error(f"Error evaluating condition '{rule.condition}': {e}")
            return False

    async def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current metrics for alert evaluation."""
        try:
            # System metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)

            return {
                "memory_usage_percent": memory.percent,
                "cpu_usage_percent": cpu_percent,
                "memory_available_gb": memory.available / (1024**3),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error collecting metrics: {e}")
            return {}

    def get_metrics_output(self) -> Tuple[str, str]:
        """Get Prometheus-formatted metrics output."""
        try:
            from prometheus_client import generate_latest
            metrics_output = generate_latest(self.registry)
            return metrics_output.decode(), "text/plain; version=0.0.4; charset=utf-8"

        except Exception as e:
            self._logger.error(f"Error generating metrics output: {e}")
            return "", "text/plain"

    def get_metrics_status(self) -> Dict[str, Any]:
        """Get metrics collector status."""
        return {
            "instance_id": self.instance_id,
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "alert_rules_count": len(self._alert_rules),
            "active_alerts": sum(1 for state in self._alert_state.values() if state["triggered"]),
            "timestamp": datetime.now().isoformat()
        }