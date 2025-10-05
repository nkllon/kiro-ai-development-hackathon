"""Compression and serialization optimization for WebSocket messages."""

import asyncio
import gzip
import json
import logging
import pickle
import time
import zlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False
    lz4 = None

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False
    msgpack = None

logger = logging.getLogger(__name__)


class CompressionAlgorithm(Enum):
    """Available compression algorithms."""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    LZ4 = "lz4"
    BROTLI = "brotli"


class SerializationFormat(Enum):
    """Available serialization formats."""
    JSON = "json"
    MSGPACK = "msgpack"
    PICKLE = "pickle"


@dataclass
class CompressionResult:
    """Result of compression operation."""
    data: bytes
    original_size: int
    compressed_size: int
    compression_ratio: float
    algorithm: CompressionAlgorithm
    serialization_format: SerializationFormat
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'original_size': self.original_size,
            'compressed_size': self.compressed_size,
            'compression_ratio': self.compression_ratio,
            'algorithm': self.algorithm.value,
            'serialization_format': self.serialization_format.value,
            'processing_time': self.processing_time,
            'metadata': self.metadata,
        }


@dataclass
class CompressionMetrics:
    """Compression performance metrics."""
    total_compressions: int = 0
    total_decompressions: int = 0
    total_bytes_saved: int = 0
    avg_compression_ratio: float = 0.0
    avg_processing_time: float = 0.0
    compression_success_rate: float = 0.0
    algorithm_usage: Dict[str, int] = field(default_factory=dict)
    format_usage: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'total_compressions': self.total_compressions,
            'total_decompressions': self.total_decompressions,
            'total_bytes_saved': self.total_bytes_saved,
            'avg_compression_ratio': self.avg_compression_ratio,
            'avg_processing_time': self.avg_processing_time,
            'compression_success_rate': self.compression_success_rate,
            'algorithm_usage': self.algorithm_usage,
            'format_usage': self.format_usage,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
        }


@dataclass
class CompressionConfig:
    """Configuration for compression and serialization."""
    default_algorithm: CompressionAlgorithm = CompressionAlgorithm.LZ4 if LZ4_AVAILABLE else CompressionAlgorithm.GZIP
    default_format: SerializationFormat = SerializationFormat.MSGPACK if MSGPACK_AVAILABLE else SerializationFormat.JSON
    compression_threshold: int = 1024  # bytes
    max_compression_level: int = 9
    enable_adaptive_compression: bool = True
    enable_parallel_compression: bool = True
    compression_timeout: float = 5.0
    cache_compressed_data: bool = True
    cache_size_limit: int = 1000
    enable_compression_metrics: bool = True


class CompressionHandler:
    """High-performance compression and serialization handler."""

    def __init__(self, config: CompressionConfig):
        self.config = config
        self._metrics = CompressionMetrics()
        self._compression_cache: Dict[str, CompressionResult] = {}
        self._cache_access_times: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()
        self._compression_stats: Dict[str, Dict[str, Any]] = {}
        self._adaptive_thresholds: Dict[str, int] = {}

    async def compress_message(
        self, 
        message: Union[Dict[str, Any], List[Any], str], 
        algorithm: Optional[CompressionAlgorithm] = None,
        format_type: Optional[SerializationFormat] = None
    ) -> CompressionResult:
        """Compress a message with optimal algorithm selection."""
        start_time = time.time()
        
        algorithm = algorithm or self.config.default_algorithm
        format_type = format_type or self.config.default_format
        
        # Check cache first
        if self.config.cache_compressed_data:
            cache_key = self._get_cache_key(message, algorithm, format_type)
            if cache_key in self._compression_cache:
                self._cache_access_times[cache_key] = datetime.utcnow()
                return self._compression_cache[cache_key]
        
        try:
            # Serialize the message
            serialized_data = await self._serialize_message(message, format_type)
            original_size = len(serialized_data)
            
            # Check if compression is beneficial
            if original_size < self.config.compression_threshold:
                algorithm = CompressionAlgorithm.NONE
            
            # Apply adaptive compression if enabled
            if self.config.enable_adaptive_compression:
                algorithm = await self._select_optimal_algorithm(serialized_data, algorithm)
            
            # Compress the data
            if algorithm == CompressionAlgorithm.NONE:
                compressed_data = serialized_data
            else:
                compressed_data = await self._compress_data(serialized_data, algorithm)
            
            compressed_size = len(compressed_data)
            compression_ratio = (original_size - compressed_size) / original_size if original_size > 0 else 0.0
            processing_time = time.time() - start_time
            
            result = CompressionResult(
                data=compressed_data,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                algorithm=algorithm,
                serialization_format=format_type,
                processing_time=processing_time,
                metadata={
                    'cache_hit': False,
                    'adaptive_selection': self.config.enable_adaptive_compression,
                }
            )
            
            # Cache the result
            if self.config.cache_compressed_data:
                await self._cache_result(cache_key, result)
            
            # Update metrics
            await self._update_compression_metrics(result, success=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            await self._update_compression_metrics(None, success=False)
            raise

    async def decompress_message(
        self, 
        compressed_data: bytes, 
        algorithm: CompressionAlgorithm,
        format_type: SerializationFormat
    ) -> Union[Dict[str, Any], List[Any], str]:
        """Decompress a message."""
        start_time = time.time()
        
        try:
            # Decompress the data
            if algorithm == CompressionAlgorithm.NONE:
                serialized_data = compressed_data
            else:
                serialized_data = await self._decompress_data(compressed_data, algorithm)
            
            # Deserialize the message
            message = await self._deserialize_message(serialized_data, format_type)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._metrics.total_decompressions += 1
            self._metrics.avg_processing_time = (
                (self._metrics.avg_processing_time * (self._metrics.total_decompressions - 1) + 
                 processing_time) / self._metrics.total_decompressions
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            raise

    async def _serialize_message(
        self, 
        message: Union[Dict[str, Any], List[Any], str], 
        format_type: SerializationFormat
    ) -> bytes:
        """Serialize a message to bytes."""
        if format_type == SerializationFormat.JSON:
            return json.dumps(message, separators=(',', ':')).encode('utf-8')
        elif format_type == SerializationFormat.MSGPACK:
            if not MSGPACK_AVAILABLE:
                raise ValueError("msgpack library not available")
            return msgpack.packb(message)
        elif format_type == SerializationFormat.PICKLE:
            return pickle.dumps(message, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            raise ValueError(f"Unsupported serialization format: {format_type}")

    async def _deserialize_message(
        self, 
        data: bytes, 
        format_type: SerializationFormat
    ) -> Union[Dict[str, Any], List[Any], str]:
        """Deserialize bytes to a message."""
        if format_type == SerializationFormat.JSON:
            return json.loads(data.decode('utf-8'))
        elif format_type == SerializationFormat.MSGPACK:
            if not MSGPACK_AVAILABLE:
                raise ValueError("msgpack library not available")
            return msgpack.unpackb(data)
        elif format_type == SerializationFormat.PICKLE:
            return pickle.loads(data)
        else:
            raise ValueError(f"Unsupported serialization format: {format_type}")

    async def _compress_data(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Compress data using the specified algorithm."""
        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.compress(data, compresslevel=self.config.max_compression_level)
        elif algorithm == CompressionAlgorithm.ZLIB:
            return zlib.compress(data, level=self.config.max_compression_level)
        elif algorithm == CompressionAlgorithm.LZ4:
            if not LZ4_AVAILABLE:
                raise ValueError("lz4 library not available")
            return lz4.frame.compress(data)
        elif algorithm == CompressionAlgorithm.BROTLI:
            # Brotli compression would require the brotli library
            # For now, fall back to gzip
            return gzip.compress(data, compresslevel=self.config.max_compression_level)
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")

    async def _decompress_data(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Decompress data using the specified algorithm."""
        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(data)
        elif algorithm == CompressionAlgorithm.ZLIB:
            return zlib.decompress(data)
        elif algorithm == CompressionAlgorithm.LZ4:
            if not LZ4_AVAILABLE:
                raise ValueError("lz4 library not available")
            return lz4.frame.decompress(data)
        elif algorithm == CompressionAlgorithm.BROTLI:
            # Brotli decompression would require the brotli library
            # For now, fall back to gzip
            return gzip.decompress(data)
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")

    async def _select_optimal_algorithm(
        self, 
        data: bytes, 
        default_algorithm: CompressionAlgorithm
    ) -> CompressionAlgorithm:
        """Select the optimal compression algorithm based on data characteristics."""
        if not self.config.enable_adaptive_compression:
            return default_algorithm
        
        data_size = len(data)
        
        # Use historical performance data if available
        if data_size in self._adaptive_thresholds:
            threshold = self._adaptive_thresholds[data_size]
            if data_size > threshold:
                return CompressionAlgorithm.LZ4
            else:
                return CompressionAlgorithm.GZIP
        
        # Quick compression test for small data
        if data_size < 4096:
            try:
                gzip_compressed = gzip.compress(data)
                
                if LZ4_AVAILABLE:
                    lz4_compressed = lz4.frame.compress(data)
                    gzip_ratio = len(gzip_compressed) / data_size
                    lz4_ratio = len(lz4_compressed) / data_size
                    
                    # Choose the better compression
                    if lz4_ratio < gzip_ratio:
                        return CompressionAlgorithm.LZ4
                    else:
                        return CompressionAlgorithm.GZIP
                else:
                    return CompressionAlgorithm.GZIP
            except Exception:
                return default_algorithm
        
        # For larger data, use LZ4 by default (faster) if available
        if LZ4_AVAILABLE:
            return CompressionAlgorithm.LZ4
        else:
            return CompressionAlgorithm.GZIP

    def _get_cache_key(
        self, 
        message: Union[Dict[str, Any], List[Any], str], 
        algorithm: CompressionAlgorithm,
        format_type: SerializationFormat
    ) -> str:
        """Generate a cache key for the message."""
        # Simple hash-based key generation
        message_str = str(message)
        return f"{hash(message_str)}_{algorithm.value}_{format_type.value}"

    async def _cache_result(self, cache_key: str, result: CompressionResult) -> None:
        """Cache a compression result."""
        async with self._lock:
            # Check cache size limit
            if len(self._compression_cache) >= self.config.cache_size_limit:
                # Remove oldest entry
                oldest_key = min(
                    self._cache_access_times.keys(),
                    key=lambda k: self._cache_access_times[k]
                )
                self._compression_cache.pop(oldest_key, None)
                self._cache_access_times.pop(oldest_key, None)
            
            self._compression_cache[cache_key] = result
            self._cache_access_times[cache_key] = datetime.utcnow()

    async def _update_compression_metrics(self, result: Optional[CompressionResult], success: bool) -> None:
        """Update compression metrics."""
        async with self._lock:
            if success and result:
                self._metrics.total_compressions += 1
                self._metrics.total_bytes_saved += result.original_size - result.compressed_size
                
                # Update average compression ratio
                self._metrics.avg_compression_ratio = (
                    (self._metrics.avg_compression_ratio * (self._metrics.total_compressions - 1) + 
                     result.compression_ratio) / self._metrics.total_compressions
                )
                
                # Update average processing time
                self._metrics.avg_processing_time = (
                    (self._metrics.avg_processing_time * (self._metrics.total_compressions - 1) + 
                     result.processing_time) / self._metrics.total_compressions
                )
                
                # Update algorithm usage
                algorithm_name = result.algorithm.value
                self._metrics.algorithm_usage[algorithm_name] = (
                    self._metrics.algorithm_usage.get(algorithm_name, 0) + 1
                )
                
                # Update format usage
                format_name = result.serialization_format.value
                self._metrics.format_usage[format_name] = (
                    self._metrics.format_usage.get(format_name, 0) + 1
                )
            
            # Update success rate
            total_attempts = self._metrics.total_compressions + (
                self._metrics.total_compressions / max(self._metrics.compression_success_rate, 0.01) - 
                self._metrics.total_compressions
            )
            self._metrics.compression_success_rate = (
                self._metrics.total_compressions / max(total_attempts, 1)
            )
            
            self._metrics.last_updated = datetime.utcnow()

    async def batch_compress(
        self, 
        messages: List[Union[Dict[str, Any], List[Any], str]], 
        algorithm: Optional[CompressionAlgorithm] = None,
        format_type: Optional[SerializationFormat] = None
    ) -> List[CompressionResult]:
        """Compress multiple messages in parallel."""
        if not self.config.enable_parallel_compression:
            # Sequential compression
            results = []
            for message in messages:
                result = await self.compress_message(message, algorithm, format_type)
                results.append(result)
            return results
        
        # Parallel compression
        tasks = [
            self.compress_message(message, algorithm, format_type)
            for message in messages
        ]
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.compression_timeout
            )
            
            # Filter out exceptions and log them
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Compression failed for message {i}: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except asyncio.TimeoutError:
            logger.error("Batch compression timed out")
            raise

    async def cleanup_cache(self) -> None:
        """Clean up old cache entries."""
        async with self._lock:
            current_time = datetime.utcnow()
            cache_timeout = datetime.utcnow() - datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            expired_keys = [
                key for key, timestamp in self._cache_access_times.items()
                if (current_time - timestamp) > cache_timeout
            ]
            
            for key in expired_keys:
                self._compression_cache.pop(key, None)
                self._cache_access_times.pop(key, None)

    def get_metrics(self) -> Dict[str, Any]:
        """Get compression metrics."""
        self._metrics.last_updated = datetime.utcnow()
        return self._metrics.to_dict()

    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status information."""
        return {
            'cache_size': len(self._compression_cache),
            'cache_limit': self.config.cache_size_limit,
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'memory_usage_estimate': len(self._compression_cache) * 1024,  # Rough estimate
        }

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        # This would need to track cache hits vs misses
        # For now, return a placeholder
        return 0.0

    async def benchmark_algorithms(
        self, 
        sample_data: List[Union[Dict[str, Any], List[Any], str]]
    ) -> Dict[str, Dict[str, Any]]:
        """Benchmark different compression algorithms."""
        results = {}
        
        for algorithm in CompressionAlgorithm:
            if algorithm == CompressionAlgorithm.NONE:
                continue
            
            algorithm_results = {
                'total_size': 0,
                'compressed_size': 0,
                'total_time': 0.0,
                'avg_ratio': 0.0,
                'success_count': 0,
            }
            
            for data in sample_data:
                try:
                    start_time = time.time()
                    result = await self.compress_message(data, algorithm)
                    processing_time = time.time() - start_time
                    
                    algorithm_results['total_size'] += result.original_size
                    algorithm_results['compressed_size'] += result.compressed_size
                    algorithm_results['total_time'] += processing_time
                    algorithm_results['success_count'] += 1
                    
                except Exception as e:
                    logger.error(f"Benchmark failed for {algorithm.value}: {e}")
            
            if algorithm_results['success_count'] > 0:
                algorithm_results['avg_ratio'] = (
                    algorithm_results['compressed_size'] / algorithm_results['total_size']
                )
            
            results[algorithm.value] = algorithm_results
        
        return results