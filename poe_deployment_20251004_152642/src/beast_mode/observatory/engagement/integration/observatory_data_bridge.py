"""
Observatory Data Bridge - Live Data Integration for Engagement System
====================================================================

Bridges the Observatory's live data streams with the Data Storyteller Engine
to provide real-time pattern discovery and narrative generation from actual
system metrics, costs, and analytics.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import deque
import redis

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..intelligence.data_storyteller import DataStorytellerEngine, DataPoint
from ...models import ObservatoryConfig, CoordinationEvent
from ...analytics_engine import RealTimeAnalyticsEngine

logger = logging.getLogger(__name__)


class ObservatoryDataBridge(ReflectiveModule):
    """
    Bridges Observatory data streams with the Data Storyteller Engine
    for real-time pattern discovery and narrative generation.
    """
    
    def __init__(self, config: ObservatoryConfig, storyteller: DataStorytellerEngine):
        super().__init__()
        self.module_id = "observatory_data_bridge"
        
        self.config = config
        self.storyteller = storyteller
        
        # Redis connection for stream processing
        self.redis_client: Optional[redis.Redis] = None
        
        # Data processing state
        self.running = False
        self.processing_tasks: List[asyncio.Task] = []
        
        # Metrics tracking
        self.metrics_processed = 0
        self.patterns_discovered = 0
        self.last_update = datetime.now()
        
        # Data buffers for correlation analysis
        self.recent_metrics: deque = deque(maxlen=500)
        self.recent_costs: deque = deque(maxlen=200)
        self.recent_events: deque = deque(maxlen=100)
        
        # Callbacks for real-time updates
        self.pattern_callbacks: List[Callable] = []
        
        logger.info("🌉 Observatory Data Bridge initialized")
    
    async def initialize(self) -> bool:
        """Initialize the data bridge and connect to Observatory streams."""
        try:
            # Connect to Redis
            await self._connect_redis()
            
            # Initialize storyteller if not already done
            if not hasattr(self.storyteller, '_running') or not self.storyteller._running:
                await self.storyteller.initialize()
            
            logger.info("✅ Observatory Data Bridge initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Observatory Data Bridge initialization failed: {e}")
            return False
    
    async def start_bridge(self) -> bool:
        """Start bridging Observatory data to the Data Storyteller."""
        try:
            if self.running:
                logger.warning("Observatory Data Bridge is already running")
                return True
            
            self.running = True
            
            # Start data stream processors
            metrics_task = asyncio.create_task(self._process_metrics_stream())
            costs_task = asyncio.create_task(self._process_cost_stream())
            events_task = asyncio.create_task(self._process_coordination_events())
            analytics_task = asyncio.create_task(self._process_analytics_data())
            
            self.processing_tasks = [metrics_task, costs_task, events_task, analytics_task]
            
            logger.info("🚀 Observatory Data Bridge started - streaming live data to storyteller")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Observatory Data Bridge: {e}")
            return False
    
    async def stop_bridge(self) -> None:
        """Stop the data bridge gracefully."""
        logger.info("🛑 Stopping Observatory Data Bridge...")
        
        self.running = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        self.processing_tasks.clear()
        
        # Close Redis connection
        if self.redis_client:
            try:
                self.redis_client.close()
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")
        
        logger.info("✅ Observatory Data Bridge stopped gracefully")
    
    async def _connect_redis(self) -> None:
        """Connect to Redis for stream processing."""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_config.host,
                port=self.config.redis_config.port,
                password=self.config.redis_config.password,
                ssl=self.config.redis_config.ssl,
                decode_responses=True
            )
            
            # Test connection
            try:
                self.redis_client.ping()
                logger.info("📡 Observatory Data Bridge connected to Redis")
            except Exception as e:
                logger.warning(f"Redis connection test failed, continuing without Redis: {e}")
                self.redis_client = None
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def _process_metrics_stream(self) -> None:
        """Process Observatory metrics stream and feed to Data Storyteller."""
        logger.info("📊 Starting metrics stream processing")
        
        while self.running:
            try:
                # Read from Observatory metrics stream
                stream_data = await self._read_redis_stream("observatory:metrics", count=10)
                
                for stream_id, fields in stream_data:
                    await self._process_metrics_entry(fields)
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"Error processing metrics stream: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _process_cost_stream(self) -> None:
        """Process Observatory cost stream and feed to Data Storyteller."""
        logger.info("💰 Starting cost stream processing")
        
        while self.running:
            try:
                # Read from Observatory cost stream
                stream_data = await self._read_redis_stream("observatory:costs", count=5)
                
                for stream_id, fields in stream_data:
                    await self._process_cost_entry(fields)
                
                await asyncio.sleep(2)  # Process every 2 seconds
                
            except Exception as e:
                logger.error(f"Error processing cost stream: {e}")
                await asyncio.sleep(5)
    
    async def _process_coordination_events(self) -> None:
        """Process Observatory coordination events."""
        logger.info("🎯 Starting coordination events processing")
        
        while self.running:
            try:
                # Read from Observatory events stream
                stream_data = await self._read_redis_stream("observatory:events", count=5)
                
                for stream_id, fields in stream_data:
                    await self._process_event_entry(fields)
                
                await asyncio.sleep(3)  # Process every 3 seconds
                
            except Exception as e:
                logger.error(f"Error processing events stream: {e}")
                await asyncio.sleep(5)
    
    async def _process_analytics_data(self) -> None:
        """Process Observatory analytics insights."""
        logger.info("🔍 Starting analytics data processing")
        
        while self.running:
            try:
                # Read from Observatory analytics stream
                stream_data = await self._read_redis_stream("observatory:analytics", count=3)
                
                for stream_id, fields in stream_data:
                    await self._process_analytics_entry(fields)
                
                await asyncio.sleep(5)  # Process every 5 seconds
                
            except Exception as e:
                logger.error(f"Error processing analytics stream: {e}")
                await asyncio.sleep(10)
    
    async def _read_redis_stream(self, stream_name: str, count: int = 10) -> List[tuple]:
        """Read data from a Redis stream."""
        try:
            if not self.redis_client:
                # Return empty list if no Redis connection
                return []
            
            # Use XREAD to get new entries from the stream
            # Note: Using synchronous Redis client, not async
            result = self.redis_client.xread({stream_name: '$'}, count=count, block=1000)
            
            if result:
                return result[0][1]  # Return the entries
            return []
            
        except Exception as e:
            logger.debug(f"No new data in stream {stream_name}: {e}")
            return []
    
    async def _process_metrics_entry(self, fields: Dict[str, str]) -> None:
        """Process a single metrics entry and convert to DataPoint."""
        try:
            timestamp = datetime.now()
            
            # Extract metrics from the fields
            for field_name, field_value in fields.items():
                if field_name in ['timestamp', 'source', 'metadata']:
                    continue
                
                try:
                    # Convert to numeric value
                    numeric_value = float(field_value)
                    
                    # Create DataPoint for the storyteller
                    data_point = DataPoint(
                        timestamp=timestamp,
                        value=numeric_value,
                        metric_name=field_name,
                        source="observatory_metrics",
                        quality_score=0.95,
                        metadata={
                            "stream_source": "redis",
                            "original_fields": fields
                        }
                    )
                    
                    # Add to storyteller
                    await self.storyteller.add_data_point(data_point)
                    
                    # Store in recent metrics for correlation
                    self.recent_metrics.append({
                        "timestamp": timestamp,
                        "metric": field_name,
                        "value": numeric_value,
                        "source": "metrics"
                    })
                    
                    self.metrics_processed += 1
                    
                except ValueError:
                    # Skip non-numeric values
                    continue
            
            self.last_update = timestamp
            
        except Exception as e:
            logger.error(f"Error processing metrics entry: {e}")
    
    async def _process_cost_entry(self, fields: Dict[str, str]) -> None:
        """Process a single cost entry and convert to DataPoint."""
        try:
            timestamp = datetime.now()
            
            # Extract cost metrics
            cost_fields = ['total_cost', 'cost_per_token', 'tokens_used', 'provider_cost']
            
            for field_name in cost_fields:
                if field_name in fields:
                    try:
                        cost_value = float(fields[field_name])
                        
                        data_point = DataPoint(
                            timestamp=timestamp,
                            value=cost_value,
                            metric_name=f"llm_{field_name}",
                            source="observatory_costs",
                            quality_score=0.98,  # Cost data is usually very accurate
                            metadata={
                                "provider": fields.get("provider", "unknown"),
                                "model": fields.get("model", "unknown"),
                                "operation": fields.get("operation", "unknown")
                            }
                        )
                        
                        await self.storyteller.add_data_point(data_point)
                        
                        # Store in recent costs
                        self.recent_costs.append({
                            "timestamp": timestamp,
                            "metric": field_name,
                            "value": cost_value,
                            "provider": fields.get("provider", "unknown"),
                            "source": "costs"
                        })
                        
                        self.metrics_processed += 1
                        
                    except ValueError:
                        continue
            
        except Exception as e:
            logger.error(f"Error processing cost entry: {e}")
    
    async def _process_event_entry(self, fields: Dict[str, str]) -> None:
        """Process a coordination event and extract metrics."""
        try:
            timestamp = datetime.now()
            
            # Extract event metrics
            event_type = fields.get("event_type", "unknown")
            source_component = fields.get("source_component", "unknown")
            
            # Create synthetic metrics from events
            event_metrics = {
                "event_frequency": 1.0,  # Each event contributes 1 to frequency
                "component_activity": 1.0,  # Activity indicator
                "coordination_health": self._calculate_event_health_score(fields)
            }
            
            for metric_name, value in event_metrics.items():
                data_point = DataPoint(
                    timestamp=timestamp,
                    value=value,
                    metric_name=metric_name,
                    source="observatory_events",
                    quality_score=0.85,
                    metadata={
                        "event_type": event_type,
                        "source_component": source_component,
                        "original_event": fields
                    }
                )
                
                await self.storyteller.add_data_point(data_point)
            
            # Store event for correlation analysis
            self.recent_events.append({
                "timestamp": timestamp,
                "event_type": event_type,
                "source_component": source_component,
                "fields": fields
            })
            
            self.metrics_processed += 1
            
        except Exception as e:
            logger.error(f"Error processing event entry: {e}")
    
    async def _process_analytics_entry(self, fields: Dict[str, str]) -> None:
        """Process analytics insights and convert to metrics."""
        try:
            timestamp = datetime.now()
            
            # Extract analytics metrics
            analytics_fields = ['health_score', 'trend_score', 'anomaly_score', 'coordination_efficiency']
            
            for field_name in analytics_fields:
                if field_name in fields:
                    try:
                        analytics_value = float(fields[field_name])
                        
                        data_point = DataPoint(
                            timestamp=timestamp,
                            value=analytics_value,
                            metric_name=f"analytics_{field_name}",
                            source="observatory_analytics",
                            quality_score=0.92,
                            metadata={
                                "insight_type": fields.get("insight_type", "unknown"),
                                "confidence": fields.get("confidence", "unknown"),
                                "original_analytics": fields
                            }
                        )
                        
                        await self.storyteller.add_data_point(data_point)
                        self.metrics_processed += 1
                        
                    except ValueError:
                        continue
            
        except Exception as e:
            logger.error(f"Error processing analytics entry: {e}")
    
    def _calculate_event_health_score(self, event_fields: Dict[str, str]) -> float:
        """Calculate a health score based on event characteristics."""
        try:
            event_type = event_fields.get("event_type", "").lower()
            
            # Score events based on their health implications
            health_scores = {
                "success": 1.0,
                "achievement": 0.9,
                "completion": 0.8,
                "warning": 0.4,
                "error": 0.2,
                "failure": 0.1,
                "critical": 0.0
            }
            
            for keyword, score in health_scores.items():
                if keyword in event_type:
                    return score
            
            return 0.5  # Neutral score for unknown events
            
        except Exception:
            return 0.5
    
    async def add_pattern_callback(self, callback: Callable) -> None:
        """Add a callback to be notified when new patterns are discovered."""
        self.pattern_callbacks.append(callback)
    
    async def get_bridge_status(self) -> Dict[str, Any]:
        """Get current status of the data bridge."""
        return {
            "running": self.running,
            "metrics_processed": self.metrics_processed,
            "patterns_discovered": self.patterns_discovered,
            "last_update": self.last_update.isoformat(),
            "recent_metrics_count": len(self.recent_metrics),
            "recent_costs_count": len(self.recent_costs),
            "recent_events_count": len(self.recent_events),
            "redis_connected": self.redis_client is not None,
            "storyteller_active": hasattr(self.storyteller, '_running') and self.storyteller._running
        }
    
    async def get_recent_insights(self) -> Dict[str, Any]:
        """Get recent insights from the Data Storyteller."""
        try:
            insights = await self.storyteller.get_current_insights()
            
            # Enhance insights with Observatory context
            enhanced_insights = {
                **insights,
                "bridge_status": await self.get_bridge_status(),
                "data_sources": {
                    "metrics": len(self.recent_metrics),
                    "costs": len(self.recent_costs),
                    "events": len(self.recent_events)
                }
            }
            
            return enhanced_insights
            
        except Exception as e:
            logger.error(f"Error getting recent insights: {e}")
            return {
                "summary": "Unable to retrieve insights",
                "patterns": [],
                "error": str(e)
            }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Observatory Data Bridge capabilities."""
        return [
            "live_data_streaming",
            "metrics_processing",
            "cost_analysis",
            "event_correlation",
            "analytics_integration",
            "pattern_discovery"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Observatory Data Bridge health status."""
        return {
            "status": "healthy" if self.running else "stopped",
            "metrics_processed": self.metrics_processed,
            "patterns_discovered": self.patterns_discovered,
            "last_update": self.last_update.isoformat(),
            "redis_connected": self.redis_client is not None,
            "processing_tasks": len([t for t in self.processing_tasks if not t.done()])
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Observatory Data Bridge module information."""
        return {
            "module_id": self.module_id,
            "name": "Observatory Data Bridge",
            "version": "1.0.0",
            "description": "Bridges Observatory live data streams with Data Storyteller Engine"
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation when errors occur."""
        try:
            logger.warning(f"Observatory Data Bridge entering degradation mode due to: {error}")
            
            # Reduce processing frequency
            for task in self.processing_tasks:
                if not task.done():
                    # Add delays to reduce load
                    await asyncio.sleep(2)
            
            # Clear old data to free memory
            if "memory" in str(error).lower():
                self.recent_metrics.clear()
                self.recent_costs.clear()
                self.recent_events.clear()
            
            logger.info("Degradation applied: reduced processing frequency and cleared buffers")
            return True
            
        except Exception as degradation_error:
            logger.error(f"Failed to apply graceful degradation: {degradation_error}")
            return False