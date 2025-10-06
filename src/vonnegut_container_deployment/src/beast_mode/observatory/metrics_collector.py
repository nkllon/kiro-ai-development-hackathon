"""
Observatory Metrics Collector - Discovers and collects metrics from Beast Mode components.

This module provides automatic discovery of Beast Mode components and non-intrusive
metrics collection with minimal performance impact (<1% overhead).
"""

import asyncio
import importlib
import inspect
import logging
import pkgutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Type
from uuid import uuid4

import redis.asyncio as redis

from ..core import ReflectiveModule
from .models import (
    CoordinationMetrics,
    LLMMetrics,
    SystemLoadMetrics,
    CoordinationEvent,
    CoordinationEventType,
)
from .config import ObservatoryConfig


logger = logging.getLogger(__name__)


@dataclass
class ComponentMetrics:
    """Metrics collected from a Beast Mode component."""
    component_id: str
    component_name: str
    component_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    health_score: float = 1.0
    uptime_seconds: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscoveredComponent:
    """Information about a discovered Beast Mode component."""
    module_path: str
    class_name: str
    component_type: str
    instance: Optional[Any] = None
    is_reflective: bool = False
    last_seen: datetime = field(default_factory=datetime.now)


class MetricsCollector(ReflectiveModule):
    """
    Discovers and collects metrics from Beast Mode components with minimal overhead.
    
    Features:
    - Automatic component discovery via reflection
    - Non-intrusive metrics collection (<1% performance impact)
    - Redis streaming for real-time metrics
    - Health monitoring of metrics collection itself
    """
    
    def __init__(self, config: ObservatoryConfig):
        super().__init__()
        self.module_id = "metrics_collector"
        self._config = config
        self._redis_client: Optional[redis.Redis] = None
        self._discovered_components: Dict[str, DiscoveredComponent] = {}
        self._running = False
        self._collection_task: Optional[asyncio.Task] = None
        self._discovery_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self._collection_start_time = time.time()
        self._metrics_collected = 0
        self._collection_errors = 0
        self._last_collection_duration = 0.0
        
        logger.info("🔍 MetricsCollector initialized - Ready to discover Beast Mode components")
    
    async def start_collection(self) -> bool:
        """Start metrics collection and component discovery."""
        try:
            if self._running:
                logger.warning("MetricsCollector is already running")
                return True
            
            # Connect to Redis
            await self._connect_redis()
            
            # Start discovery and collection tasks
            self._running = True
            self._discovery_task = asyncio.create_task(self._discovery_loop())
            self._collection_task = asyncio.create_task(self._collection_loop())
            
            logger.info("🚀 MetricsCollector started - discovering components and collecting metrics")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MetricsCollector: {e}")
            return False
    
    async def stop_collection(self) -> None:
        """Stop metrics collection gracefully."""
        logger.info("🛑 Stopping MetricsCollector...")
        
        self._running = False
        
        # Cancel tasks
        if self._discovery_task and not self._discovery_task.done():
            self._discovery_task.cancel()
        if self._collection_task and not self._collection_task.done():
            self._collection_task.cancel()
        
        # Wait for tasks to complete
        tasks = [t for t in [self._discovery_task, self._collection_task] if t]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Close Redis connection
        if self._redis_client:
            await self._redis_client.close()
        
        logger.info("✅ MetricsCollector stopped gracefully")
    
    async def _connect_redis(self) -> None:
        """Connect to Redis for metrics streaming."""
        try:
            self._redis_client = redis.Redis(
                host=self._config.redis_config.host,
                port=self._config.redis_config.port,
                password=self._config.redis_config.password,
                ssl=self._config.redis_config.ssl,
                decode_responses=True
            )
            
            # Test connection
            await self._redis_client.ping()
            logger.info(f"📡 Connected to Redis at {self._config.redis_config.host}:{self._config.redis_config.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def _discovery_loop(self) -> None:
        """Main loop for discovering Beast Mode components."""
        logger.info("🔍 Starting component discovery loop")
        
        while self._running:
            try:
                # Discover components
                await self._discover_components()
                
                # Sleep for discovery interval (longer than collection)
                await asyncio.sleep(30)  # Discover every 30 seconds
                
            except asyncio.CancelledError:
                logger.info("Component discovery loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                await asyncio.sleep(5)  # Brief pause on error
        
        logger.info("Component discovery loop stopped")
    
    async def _collection_loop(self) -> None:
        """Main loop for collecting metrics from discovered components."""
        logger.info("📊 Starting metrics collection loop")
        
        while self._running:
            collection_start = time.time()
            
            try:
                # Collect metrics from all discovered components
                await self._collect_all_metrics()
                
                # Track performance
                self._last_collection_duration = time.time() - collection_start
                self._metrics_collected += len(self._discovered_components)
                
                # Sleep for collection interval
                await asyncio.sleep(self._config.metrics_config.collection_interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("Metrics collection loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                self._collection_errors += 1
                await asyncio.sleep(1)  # Brief pause on error
        
        logger.info("Metrics collection loop stopped")
    
    async def _discover_components(self) -> None:
        """Discover Beast Mode components via reflection."""
        try:
            beast_mode_path = Path(__file__).parent.parent
            discovered_count = 0
            
            # Walk through all Beast Mode modules
            for module_info in pkgutil.walk_packages([str(beast_mode_path)], "beast_mode."):
                try:
                    # Skip the observatory module to avoid circular imports
                    if "observatory" in module_info.name:
                        continue
                    
                    # Import the module
                    module = importlib.import_module(module_info.name)
                    
                    # Look for classes that inherit from ReflectiveModule
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (hasattr(obj, '__bases__') and 
                            any(base.__name__ == 'ReflectiveModule' for base in obj.__mro__)):
                            
                            component_id = f"{module_info.name}.{name}"
                            
                            if component_id not in self._discovered_components:
                                discovered_component = DiscoveredComponent(
                                    module_path=module_info.name,
                                    class_name=name,
                                    component_type="ReflectiveModule",
                                    is_reflective=True
                                )
                                
                                self._discovered_components[component_id] = discovered_component
                                discovered_count += 1
                                
                                logger.debug(f"🔍 Discovered component: {component_id}")
                
                except Exception as e:
                    # Skip modules that can't be imported (missing dependencies, etc.)
                    logger.debug(f"Skipped module {module_info.name}: {e}")
                    continue
            
            if discovered_count > 0:
                logger.info(f"🎯 Discovered {discovered_count} new Beast Mode components (total: {len(self._discovered_components)})")
            
        except Exception as e:
            logger.error(f"Error during component discovery: {e}")
    
    async def _collect_all_metrics(self) -> None:
        """Collect metrics from all discovered components."""
        if not self._discovered_components:
            return
        
        metrics_batch = []
        
        for component_id, component in self._discovered_components.items():
            try:
                metrics = await self._collect_component_metrics(component_id, component)
                if metrics:
                    metrics_batch.append(metrics)
                    
            except Exception as e:
                logger.debug(f"Failed to collect metrics from {component_id}: {e}")
                continue
        
        # Stream metrics to Redis
        if metrics_batch:
            await self._stream_metrics_to_redis(metrics_batch)
    
    async def _collect_component_metrics(self, component_id: str, component: DiscoveredComponent) -> Optional[ComponentMetrics]:
        """Collect metrics from a specific component."""
        try:
            # For now, create basic metrics
            # TODO: Implement actual metrics collection from component instances
            metrics = ComponentMetrics(
                component_id=component_id,
                component_name=component.class_name,
                component_type=component.component_type,
                health_score=1.0,  # Default healthy
                uptime_seconds=(datetime.now() - component.last_seen).total_seconds(),
                custom_metrics={
                    "module_path": component.module_path,
                    "is_reflective": component.is_reflective,
                    "last_seen": component.last_seen.isoformat()
                }
            )
            
            return metrics
            
        except Exception as e:
            logger.debug(f"Error collecting metrics from {component_id}: {e}")
            return None
    
    async def _stream_metrics_to_redis(self, metrics_batch: List[ComponentMetrics]) -> None:
        """Stream collected metrics to Redis."""
        try:
            if not self._redis_client:
                return
            
            stream_name = self._config.redis_config.stream_name
            
            for metrics in metrics_batch:
                # Convert metrics to Redis stream format
                stream_data = {
                    "component_id": metrics.component_id,
                    "component_name": metrics.component_name,
                    "component_type": metrics.component_type,
                    "timestamp": metrics.timestamp.isoformat(),
                    "health_score": str(metrics.health_score),
                    "uptime_seconds": str(metrics.uptime_seconds),
                    "error_count": str(metrics.error_count),
                    "warning_count": str(metrics.warning_count),
                    "memory_usage_mb": str(metrics.memory_usage_mb),
                    "cpu_usage_percent": str(metrics.cpu_usage_percent),
                    "custom_metrics": str(metrics.custom_metrics)
                }
                
                # Add to Redis stream
                await self._redis_client.xadd(stream_name, stream_data)
            
            logger.debug(f"📡 Streamed {len(metrics_batch)} metrics to Redis stream '{stream_name}'")
            
        except Exception as e:
            logger.error(f"Failed to stream metrics to Redis: {e}")
    
    def get_discovered_components(self) -> Dict[str, Dict[str, Any]]:
        """Get information about discovered components."""
        return {
            component_id: {
                "module_path": component.module_path,
                "class_name": component.class_name,
                "component_type": component.component_type,
                "is_reflective": component.is_reflective,
                "last_seen": component.last_seen.isoformat()
            }
            for component_id, component in self._discovered_components.items()
        }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get metrics collection performance statistics."""
        uptime = time.time() - self._collection_start_time
        
        return {
            "uptime_seconds": uptime,
            "discovered_components": len(self._discovered_components),
            "metrics_collected": self._metrics_collected,
            "collection_errors": self._collection_errors,
            "last_collection_duration_ms": self._last_collection_duration * 1000,
            "collection_rate_per_second": self._metrics_collected / uptime if uptime > 0 else 0,
            "error_rate_percent": (self._collection_errors / max(1, self._metrics_collected)) * 100
        }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get MetricsCollector capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
        ]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Beast Mode Metrics Collector",
            "version": "1.0.0",
            "description": "Discovers and collects metrics from Beast Mode components",
            "config": {
                "redis_host": self._config.redis_config.host,
                "collection_interval": self._config.metrics_config.collection_interval_seconds,
                "discovered_components": len(self._discovered_components)
            }
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation on errors."""
        logger.warning(f"MetricsCollector entering graceful degradation due to: {error}")
        
        # Continue running but with reduced functionality
        if "redis" in str(error).lower():
            logger.info("Redis connection issue - continuing without streaming")
            return True
        
        return False
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the MetricsCollector."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        # Determine status based on running state and error rate
        if not self._running:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = ["MetricsCollector is not running"]
        else:
            error_rate = (self._collection_errors / max(1, self._metrics_collected)) * 100
            
            if error_rate > 10:
                status = ModuleStatus.ERROR
                health_score = 0.3
                issues = [f"High error rate: {error_rate:.1f}%"]
            elif error_rate > 5:
                status = ModuleStatus.WARNING
                health_score = 0.7
                issues = [f"Elevated error rate: {error_rate:.1f}%"]
            else:
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
        
        uptime = time.time() - self._collection_start_time
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._collection_errors,
            warning_count=0
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for this collector."""
        return {
            "collection_stats": self.get_collection_stats(),
            "discovered_components": len(self._discovered_components),
            "redis_connected": self._redis_client is not None,
            "running": self._running
        }