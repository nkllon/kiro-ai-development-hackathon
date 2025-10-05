#!/usr/bin/env python3
"""
Performance Monitoring and Optimization - Phase 5 Task 5.4

Monitors documentation generation performance, implements optimization strategies,
creates benchmarks, and provides caching for frequently accessed documentation.
"""

import asyncio
import psutil
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
import hashlib
import pickle
import gzip
from collections import defaultdict, deque

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    component: str
    operation: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceBenchmark:
    """Performance benchmark definition."""
    benchmark_id: str
    name: str
    description: str
    target_value: float
    warning_threshold: float
    critical_threshold: float
    unit: str
    component: str
    enabled: bool = True


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation."""
    recommendation_id: str
    component: str
    issue_type: str
    severity: str  # low, medium, high, critical
    description: str
    recommended_action: str
    estimated_impact: str
    implementation_effort: str
    created_at: datetime


@dataclass
class CacheEntry:
    """Cache entry for documentation content."""
    key: str
    content: Any
    content_hash: str
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: int
    compressed: bool = False


class PerformanceMonitor(ReflectiveModule):
    """
    Performance monitoring and optimization system for documentation generation
    with caching, benchmarking, and automated optimization recommendations.
    """
    
    def __init__(self):
        super().__init__()
        self.metrics_history: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self.benchmarks: Dict[str, PerformanceBenchmark] = {}
        self.cache: Dict[str, CacheEntry] = {}
        self.optimization_recommendations: List[OptimizationRecommendation] = []
        self.performance_alerts: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.operation_timings: Dict[str, List[float]] = defaultdict(list)
        self.resource_usage_history: deque = deque(maxlen=1000)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_size_bytes': 0,
            'max_size_bytes': 100 * 1024 * 1024  # 100MB default cache limit
        }
        
        # Configuration
        self.monitoring_interval = 30  # seconds
        self.cache_cleanup_interval = 300  # 5 minutes
        self.benchmark_check_interval = 60  # 1 minute
        self.optimization_analysis_interval = 900  # 15 minutes
        
        # Initialize metrics
        self.metrics.update({
            'cpu_usage_percent': 0.0,
            'memory_usage_mb': 0.0,
            'memory_usage_percent': 0.0,
            'disk_io_read_mb': 0.0,
            'disk_io_write_mb': 0.0,
            'network_io_mb': 0.0,
            'cache_hit_rate': 0.0,
            'cache_size_mb': 0.0,
            'avg_operation_time_ms': 0.0,
            'active_operations': 0,
            'benchmark_violations': 0,
            'optimization_recommendations': 0
        })
        
        self.logger.info("PerformanceMonitor initialized")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the performance monitoring system."""
        correlation_id = self.generate_correlation_id()
        
        try:
            # Initialize benchmarks
            await self._initialize_performance_benchmarks()
            
            # Start monitoring loops
            asyncio.create_task(self._performance_monitoring_loop())
            asyncio.create_task(self._cache_cleanup_loop())
            asyncio.create_task(self._benchmark_monitoring_loop())
            asyncio.create_task(self._optimization_analysis_loop())
            
            self.logger.info("PerformanceMonitor initialized successfully",
                           extra={"correlation_id": correlation_id})
            
            return {
                "status": "initialized",
                "benchmarks_loaded": len(self.benchmarks),
                "cache_max_size_mb": self.cache_stats['max_size_bytes'] / (1024 * 1024),
                "monitoring_interval": self.monitoring_interval,
                "correlation_id": correlation_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PerformanceMonitor: {e}",
                            extra={"correlation_id": correlation_id})
            return {
                "status": "failed",
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    async def _initialize_performance_benchmarks(self):
        """Initialize performance benchmarks."""
        benchmarks = [
            # System Resource Benchmarks
            PerformanceBenchmark(
                benchmark_id="cpu_usage",
                name="CPU Usage",
                description="System CPU usage percentage",
                target_value=50.0,
                warning_threshold=70.0,
                critical_threshold=90.0,
                unit="percent",
                component="system"
            ),
            PerformanceBenchmark(
                benchmark_id="memory_usage",
                name="Memory Usage",
                description="System memory usage percentage",
                target_value=60.0,
                warning_threshold=80.0,
                critical_threshold=95.0,
                unit="percent",
                component="system"
            ),
            
            # Documentation Generation Benchmarks
            PerformanceBenchmark(
                benchmark_id="discovery_time",
                name="Infrastructure Discovery Time",
                description="Time to complete infrastructure discovery",
                target_value=30.0,
                warning_threshold=60.0,
                critical_threshold=120.0,
                unit="seconds",
                component="discovery"
            ),
            PerformanceBenchmark(
                benchmark_id="analysis_time",
                name="Relationship Analysis Time",
                description="Time to complete relationship analysis",
                target_value=20.0,
                warning_threshold=45.0,
                critical_threshold=90.0,
                unit="seconds",
                component="analysis"
            ),
            PerformanceBenchmark(
                benchmark_id="generation_time",
                name="Documentation Generation Time",
                description="Time to generate documentation",
                target_value=15.0,
                warning_threshold=30.0,
                critical_threshold=60.0,
                unit="seconds",
                component="generation"
            ),
            
            # Cache Performance Benchmarks
            PerformanceBenchmark(
                benchmark_id="cache_hit_rate",
                name="Cache Hit Rate",
                description="Percentage of cache hits vs total requests",
                target_value=80.0,
                warning_threshold=60.0,
                critical_threshold=40.0,
                unit="percent",
                component="cache"
            ),
            
            # Network Performance Benchmarks
            PerformanceBenchmark(
                benchmark_id="websocket_response_time",
                name="WebSocket Response Time",
                description="Average WebSocket response time",
                target_value=100.0,
                warning_threshold=500.0,
                critical_threshold=1000.0,
                unit="milliseconds",
                component="websocket"
            )
        ]
        
        for benchmark in benchmarks:
            self.benchmarks[benchmark.benchmark_id] = benchmark
        
        self.logger.info(f"Initialized {len(self.benchmarks)} performance benchmarks")
    
    async def record_performance_metric(self, metric_name: str, value: float, 
                                      unit: str, component: str, operation: str,
                                      metadata: Dict[str, Any] = None) -> None:
        """Record a performance metric."""
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            component=component,
            operation=operation,
            metadata=metadata or {}
        )
        
        self.metrics_history.append(metric)
        
        # Update operation timings for analysis
        if unit in ['seconds', 'milliseconds']:
            timing_key = f"{component}_{operation}"
            timing_value = value if unit == 'seconds' else value / 1000
            self.operation_timings[timing_key].append(timing_value)
            
            # Keep only recent timings (last 100 per operation)
            if len(self.operation_timings[timing_key]) > 100:
                self.operation_timings[timing_key] = self.operation_timings[timing_key][-100:]
    
    async def start_operation_timing(self, component: str, operation: str) -> str:
        """Start timing an operation."""
        timing_id = f"{component}_{operation}_{int(time.time() * 1000)}"
        
        # Store start time in metadata
        if not hasattr(self, '_operation_start_times'):
            self._operation_start_times = {}
        
        self._operation_start_times[timing_id] = time.time()
        
        # Update active operations count
        self.metrics['active_operations'] += 1
        
        return timing_id
    
    async def end_operation_timing(self, timing_id: str, 
                                 metadata: Dict[str, Any] = None) -> float:
        """End timing an operation and record the metric."""
        if not hasattr(self, '_operation_start_times'):
            return 0.0
        
        start_time = self._operation_start_times.pop(timing_id, None)
        if not start_time:
            return 0.0
        
        duration = time.time() - start_time
        
        # Parse component and operation from timing_id
        parts = timing_id.split('_')
        if len(parts) >= 2:
            component = parts[0]
            operation = parts[1]
            
            await self.record_performance_metric(
                metric_name=f"{operation}_duration",
                value=duration,
                unit="seconds",
                component=component,
                operation=operation,
                metadata=metadata
            )
        
        # Update active operations count
        self.metrics['active_operations'] = max(0, self.metrics['active_operations'] - 1)
        
        return duration
    
    async def _performance_monitoring_loop(self):
        """Background loop for system performance monitoring."""
        while True:
            try:
                await self._collect_system_metrics()
                await self._update_performance_metrics()
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_performance_metric(
                "cpu_usage", cpu_percent, "percent", "system", "monitoring"
            )
            self.metrics['cpu_usage_percent'] = cpu_percent
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)
            await self.record_performance_metric(
                "memory_usage", memory_mb, "megabytes", "system", "monitoring"
            )
            await self.record_performance_metric(
                "memory_usage_percent", memory.percent, "percent", "system", "monitoring"
            )
            self.metrics['memory_usage_mb'] = memory_mb
            self.metrics['memory_usage_percent'] = memory.percent
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                read_mb = disk_io.read_bytes / (1024 * 1024)
                write_mb = disk_io.write_bytes / (1024 * 1024)
                await self.record_performance_metric(
                    "disk_read", read_mb, "megabytes", "system", "monitoring"
                )
                await self.record_performance_metric(
                    "disk_write", write_mb, "megabytes", "system", "monitoring"
                )
                self.metrics['disk_io_read_mb'] = read_mb
                self.metrics['disk_io_write_mb'] = write_mb
            
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io:
                network_mb = (network_io.bytes_sent + network_io.bytes_recv) / (1024 * 1024)
                await self.record_performance_metric(
                    "network_io", network_mb, "megabytes", "system", "monitoring"
                )
                self.metrics['network_io_mb'] = network_mb
            
            # Store resource usage for trend analysis
            resource_snapshot = {
                'timestamp': datetime.utcnow(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_mb': memory_mb
            }
            self.resource_usage_history.append(resource_snapshot)
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    async def _update_performance_metrics(self):
        """Update calculated performance metrics."""
        # Calculate average operation times
        if self.operation_timings:
            all_timings = []
            for timings in self.operation_timings.values():
                all_timings.extend(timings)
            
            if all_timings:
                avg_time_ms = (sum(all_timings) / len(all_timings)) * 1000
                self.metrics['avg_operation_time_ms'] = avg_time_ms
        
        # Update cache metrics
        if self.cache:
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            if total_requests > 0:
                hit_rate = (self.cache_stats['hits'] / total_requests) * 100
                self.metrics['cache_hit_rate'] = hit_rate
            
            cache_size_mb = self.cache_stats['total_size_bytes'] / (1024 * 1024)
            self.metrics['cache_size_mb'] = cache_size_mb
    
    # Cache Management Methods
    
    def _generate_cache_key(self, component: str, operation: str, 
                          parameters: Dict[str, Any]) -> str:
        """Generate a cache key for the given parameters."""
        key_data = {
            'component': component,
            'operation': operation,
            'parameters': parameters
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _calculate_content_hash(self, content: Any) -> str:
        """Calculate hash of content for cache validation."""
        content_bytes = pickle.dumps(content)
        return hashlib.sha256(content_bytes).hexdigest()
    
    async def cache_get(self, component: str, operation: str, 
                       parameters: Dict[str, Any]) -> Optional[Any]:
        """Get content from cache."""
        cache_key = self._generate_cache_key(component, operation, parameters)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            # Check TTL
            if (datetime.utcnow() - entry.created_at).total_seconds() > entry.ttl_seconds:
                # Expired, remove from cache
                await self._remove_cache_entry(cache_key)
                self.cache_stats['misses'] += 1
                return None
            
            # Update access statistics
            entry.last_accessed = datetime.utcnow()
            entry.access_count += 1
            
            self.cache_stats['hits'] += 1
            
            # Decompress if needed
            content = entry.content
            if entry.compressed:
                content = pickle.loads(gzip.decompress(content))
            
            return content
        else:
            self.cache_stats['misses'] += 1
            return None
    
    async def cache_set(self, component: str, operation: str, 
                       parameters: Dict[str, Any], content: Any,
                       ttl_seconds: int = 3600) -> bool:
        """Set content in cache."""
        cache_key = self._generate_cache_key(component, operation, parameters)
        content_hash = self._calculate_content_hash(content)
        
        # Serialize content
        content_bytes = pickle.dumps(content)
        content_size = len(content_bytes)
        
        # Compress if content is large
        compressed = False
        if content_size > 1024:  # Compress if > 1KB
            compressed_bytes = gzip.compress(content_bytes)
            if len(compressed_bytes) < content_size * 0.8:  # Only if compression saves 20%+
                content_bytes = compressed_bytes
                content_size = len(compressed_bytes)
                compressed = True
        
        # Check if we need to make space
        await self._ensure_cache_space(content_size)
        
        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            content=content_bytes,
            content_hash=content_hash,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=0,
            size_bytes=content_size,
            ttl_seconds=ttl_seconds,
            compressed=compressed
        )
        
        self.cache[cache_key] = entry
        self.cache_stats['total_size_bytes'] += content_size
        
        return True
    
    async def _ensure_cache_space(self, required_bytes: int):
        """Ensure there's enough space in cache for new content."""
        max_size = self.cache_stats['max_size_bytes']
        current_size = self.cache_stats['total_size_bytes']
        
        if current_size + required_bytes <= max_size:
            return  # Enough space
        
        # Need to evict entries - use LRU strategy
        entries_by_access = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        bytes_to_free = (current_size + required_bytes) - max_size
        bytes_freed = 0
        
        for cache_key, entry in entries_by_access:
            if bytes_freed >= bytes_to_free:
                break
            
            await self._remove_cache_entry(cache_key)
            bytes_freed += entry.size_bytes
            self.cache_stats['evictions'] += 1
    
    async def _remove_cache_entry(self, cache_key: str):
        """Remove an entry from cache."""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            self.cache_stats['total_size_bytes'] -= entry.size_bytes
            del self.cache[cache_key]
    
    async def _cache_cleanup_loop(self):
        """Background loop for cache cleanup."""
        while True:
            try:
                await self._cleanup_expired_cache_entries()
                await asyncio.sleep(self.cache_cleanup_interval)
                
            except Exception as e:
                self.logger.error(f"Error in cache cleanup loop: {e}")
                await asyncio.sleep(self.cache_cleanup_interval)
    
    async def _cleanup_expired_cache_entries(self):
        """Remove expired cache entries."""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for cache_key, entry in self.cache.items():
            if (current_time - entry.created_at).total_seconds() > entry.ttl_seconds:
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            await self._remove_cache_entry(cache_key)
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    # Benchmark Monitoring
    
    async def _benchmark_monitoring_loop(self):
        """Background loop for benchmark monitoring."""
        while True:
            try:
                await self._check_performance_benchmarks()
                await asyncio.sleep(self.benchmark_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in benchmark monitoring loop: {e}")
                await asyncio.sleep(self.benchmark_check_interval)
    
    async def _check_performance_benchmarks(self):
        """Check current performance against benchmarks."""
        violations = 0
        
        for benchmark in self.benchmarks.values():
            if not benchmark.enabled:
                continue
            
            current_value = await self._get_current_benchmark_value(benchmark)
            if current_value is None:
                continue
            
            severity = self._evaluate_benchmark_violation(benchmark, current_value)
            
            if severity:
                violations += 1
                await self._handle_benchmark_violation(benchmark, current_value, severity)
        
        self.metrics['benchmark_violations'] = violations
    
    async def _get_current_benchmark_value(self, benchmark: PerformanceBenchmark) -> Optional[float]:
        """Get current value for a benchmark."""
        if benchmark.benchmark_id == "cpu_usage":
            return self.metrics.get('cpu_usage_percent')
        elif benchmark.benchmark_id == "memory_usage":
            return self.metrics.get('memory_usage_percent')
        elif benchmark.benchmark_id == "cache_hit_rate":
            return self.metrics.get('cache_hit_rate')
        elif benchmark.benchmark_id in ["discovery_time", "analysis_time", "generation_time"]:
            # Get average time for this operation
            operation_key = f"{benchmark.component}_operation"
            if operation_key in self.operation_timings:
                timings = self.operation_timings[operation_key]
                return sum(timings) / len(timings) if timings else None
        
        return None
    
    def _evaluate_benchmark_violation(self, benchmark: PerformanceBenchmark, 
                                    current_value: float) -> Optional[str]:
        """Evaluate if current value violates benchmark thresholds."""
        if current_value >= benchmark.critical_threshold:
            return "critical"
        elif current_value >= benchmark.warning_threshold:
            return "warning"
        elif current_value > benchmark.target_value:
            return "target_exceeded"
        
        return None
    
    async def _handle_benchmark_violation(self, benchmark: PerformanceBenchmark,
                                        current_value: float, severity: str):
        """Handle a benchmark violation."""
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "benchmark_id": benchmark.benchmark_id,
            "benchmark_name": benchmark.name,
            "current_value": current_value,
            "target_value": benchmark.target_value,
            "threshold_violated": benchmark.warning_threshold if severity == "warning" else benchmark.critical_threshold,
            "severity": severity,
            "component": benchmark.component,
            "unit": benchmark.unit
        }
        
        self.performance_alerts.append(alert)
        
        # Keep only recent alerts (last 100)
        if len(self.performance_alerts) > 100:
            self.performance_alerts = self.performance_alerts[-100:]
        
        self.logger.warning(f"Performance benchmark violation: {benchmark.name}",
                          extra={
                              "benchmark_id": benchmark.benchmark_id,
                              "current_value": current_value,
                              "threshold": benchmark.warning_threshold if severity == "warning" else benchmark.critical_threshold,
                              "severity": severity
                          })
    
    # Optimization Analysis
    
    async def _optimization_analysis_loop(self):
        """Background loop for optimization analysis."""
        while True:
            try:
                await self._analyze_performance_trends()
                await self._generate_optimization_recommendations()
                await asyncio.sleep(self.optimization_analysis_interval)
                
            except Exception as e:
                self.logger.error(f"Error in optimization analysis loop: {e}")
                await asyncio.sleep(self.optimization_analysis_interval)
    
    async def _analyze_performance_trends(self):
        """Analyze performance trends and identify optimization opportunities."""
        if len(self.resource_usage_history) < 10:
            return  # Need more data points
        
        # Analyze CPU usage trend
        recent_cpu = [snapshot['cpu_percent'] for snapshot in list(self.resource_usage_history)[-10:]]
        cpu_trend = self._calculate_trend(recent_cpu)
        
        if cpu_trend > 5.0:  # CPU usage increasing by >5% per measurement
            await self._create_optimization_recommendation(
                "cpu_usage_trend",
                "system",
                "performance_degradation",
                "medium",
                f"CPU usage trending upward ({cpu_trend:.1f}% increase per measurement)",
                "Investigate CPU-intensive operations and consider optimization or scaling",
                "Reduced system responsiveness and increased resource costs",
                "Medium - requires performance profiling and optimization"
            )
        
        # Analyze memory usage trend
        recent_memory = [snapshot['memory_percent'] for snapshot in list(self.resource_usage_history)[-10:]]
        memory_trend = self._calculate_trend(recent_memory)
        
        if memory_trend > 3.0:  # Memory usage increasing by >3% per measurement
            await self._create_optimization_recommendation(
                "memory_usage_trend",
                "system",
                "memory_leak",
                "high",
                f"Memory usage trending upward ({memory_trend:.1f}% increase per measurement)",
                "Investigate potential memory leaks and implement memory optimization",
                "System instability and potential out-of-memory errors",
                "High - requires immediate investigation"
            )
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (slope) of values over time."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        # Linear regression slope
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    async def _generate_optimization_recommendations(self):
        """Generate optimization recommendations based on current performance."""
        # Cache optimization recommendations
        hit_rate = self.metrics.get('cache_hit_rate', 0)
        if hit_rate < 60:
            await self._create_optimization_recommendation(
                "low_cache_hit_rate",
                "cache",
                "cache_efficiency",
                "medium",
                f"Cache hit rate is low ({hit_rate:.1f}%)",
                "Analyze cache usage patterns and adjust TTL values or cache size",
                "Improved response times and reduced computation overhead",
                "Low - configuration adjustment"
            )
        
        # Operation timing recommendations
        avg_time = self.metrics.get('avg_operation_time_ms', 0)
        if avg_time > 5000:  # > 5 seconds average
            await self._create_optimization_recommendation(
                "slow_operations",
                "operations",
                "performance_optimization",
                "high",
                f"Average operation time is high ({avg_time:.0f}ms)",
                "Profile slow operations and implement performance optimizations",
                "Significantly improved user experience and system throughput",
                "Medium - requires code optimization"
            )
    
    async def _create_optimization_recommendation(self, rec_id: str, component: str,
                                               issue_type: str, severity: str,
                                               description: str, recommended_action: str,
                                               estimated_impact: str, implementation_effort: str):
        """Create an optimization recommendation."""
        # Check if recommendation already exists
        existing = next((r for r in self.optimization_recommendations 
                        if r.recommendation_id == rec_id), None)
        
        if existing:
            return  # Don't duplicate recommendations
        
        recommendation = OptimizationRecommendation(
            recommendation_id=rec_id,
            component=component,
            issue_type=issue_type,
            severity=severity,
            description=description,
            recommended_action=recommended_action,
            estimated_impact=estimated_impact,
            implementation_effort=implementation_effort,
            created_at=datetime.utcnow()
        )
        
        self.optimization_recommendations.append(recommendation)
        self.metrics['optimization_recommendations'] = len(self.optimization_recommendations)
        
        self.logger.info(f"Created optimization recommendation: {rec_id}",
                        extra={
                            "component": component,
                            "severity": severity,
                            "issue_type": issue_type
                        })
    
    # Public API Methods
    
    async def get_performance_status(self) -> Dict[str, Any]:
        """Get current performance status."""
        return {
            "system_metrics": {
                "cpu_usage_percent": self.metrics['cpu_usage_percent'],
                "memory_usage_percent": self.metrics['memory_usage_percent'],
                "memory_usage_mb": self.metrics['memory_usage_mb'],
                "avg_operation_time_ms": self.metrics['avg_operation_time_ms'],
                "active_operations": self.metrics['active_operations']
            },
            "cache_metrics": {
                "hit_rate_percent": self.metrics['cache_hit_rate'],
                "size_mb": self.metrics['cache_size_mb'],
                "total_entries": len(self.cache),
                "hits": self.cache_stats['hits'],
                "misses": self.cache_stats['misses'],
                "evictions": self.cache_stats['evictions']
            },
            "benchmark_status": {
                "total_benchmarks": len(self.benchmarks),
                "active_violations": self.metrics['benchmark_violations'],
                "recent_alerts": len(self.performance_alerts)
            },
            "optimization_status": {
                "active_recommendations": len(self.optimization_recommendations),
                "by_severity": self._count_recommendations_by_severity()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _count_recommendations_by_severity(self) -> Dict[str, int]:
        """Count optimization recommendations by severity."""
        counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for rec in self.optimization_recommendations:
            counts[rec.severity] = counts.get(rec.severity, 0) + 1
        return counts
    
    async def get_performance_history(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance history for the specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]
        recent_alerts = [a for a in self.performance_alerts 
                        if datetime.fromisoformat(a['timestamp']) > cutoff_time]
        
        return {
            "time_period_hours": hours,
            "metrics_count": len(recent_metrics),
            "alerts_count": len(recent_alerts),
            "metrics_by_component": self._group_metrics_by_component(recent_metrics),
            "alerts_by_severity": self._group_alerts_by_severity(recent_alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _group_metrics_by_component(self, metrics: List[PerformanceMetric]) -> Dict[str, int]:
        """Group metrics by component."""
        groups = defaultdict(int)
        for metric in metrics:
            groups[metric.component] += 1
        return dict(groups)
    
    def _group_alerts_by_severity(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group alerts by severity."""
        groups = defaultdict(int)
        for alert in alerts:
            groups[alert['severity']] += 1
        return dict(groups)
    
    async def clear_cache(self, component: str = None) -> Dict[str, Any]:
        """Clear cache entries, optionally filtered by component."""
        cleared_count = 0
        cleared_size = 0
        
        if component:
            # Clear cache entries for specific component
            keys_to_remove = []
            for cache_key, entry in self.cache.items():
                # Check if cache key contains component name
                if component in cache_key:
                    keys_to_remove.append(cache_key)
                    cleared_size += entry.size_bytes
            
            for cache_key in keys_to_remove:
                await self._remove_cache_entry(cache_key)
                cleared_count += 1
        else:
            # Clear all cache
            cleared_count = len(self.cache)
            cleared_size = self.cache_stats['total_size_bytes']
            self.cache.clear()
            self.cache_stats['total_size_bytes'] = 0
        
        self.logger.info(f"Cleared {cleared_count} cache entries ({cleared_size / (1024*1024):.1f}MB)",
                        extra={"component": component or "all"})
        
        return {
            "cleared_entries": cleared_count,
            "cleared_size_mb": cleared_size / (1024 * 1024),
            "remaining_entries": len(self.cache),
            "component": component or "all"
        }


if __name__ == "__main__":
    async def main():
        monitor = PerformanceMonitor()
        await monitor.initialize()
        
        # Test performance monitoring
        timing_id = await monitor.start_operation_timing("test", "operation")
        await asyncio.sleep(0.1)  # Simulate work
        duration = await monitor.end_operation_timing(timing_id)
        print(f"Operation took {duration:.3f} seconds")
        
        # Test caching
        await monitor.cache_set("test", "operation", {"param": "value"}, {"result": "data"})
        cached_result = await monitor.cache_get("test", "operation", {"param": "value"})
        print(f"Cached result: {cached_result}")
        
        # Get status
        status = await monitor.get_performance_status()
        print(f"Performance Status: {json.dumps(status, indent=2)}")
    
    asyncio.run(main())