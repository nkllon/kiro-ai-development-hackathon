"""
Real-Time Analytics Engine - Processes streams of metrics to generate intelligent insights.

This module provides continuous analysis of coordination metrics, cost trends, and system health
to generate actionable insights and early warning signals for the Observatory dashboard.
"""

import asyncio
import json
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Deque
from uuid import uuid4

import redis.asyncio as redis

from ..core import ReflectiveModule
from .models import (
    CoordinationMetrics,
    HealthScore,
    CostTrend,
    CoordinationEvent,
    CoordinationEventType,
)
from .config import ObservatoryConfig


logger = logging.getLogger(__name__)


@dataclass
class TimeWindowMetrics:
    """Metrics aggregated over a time window."""
    window_start: datetime
    window_end: datetime
    window_duration_seconds: int
    
    # Component metrics
    component_count: int = 0
    healthy_components: int = 0
    warning_components: int = 0
    error_components: int = 0
    
    # Cost metrics
    total_cost: Decimal = field(default_factory=lambda: Decimal('0.00'))
    llm_calls: int = 0
    avg_cost_per_call: Decimal = field(default_factory=lambda: Decimal('0.00'))
    
    # Performance metrics
    avg_response_time_ms: float = 0.0
    error_rate_percent: float = 0.0
    
    # Coordination health
    coordination_health_score: float = 1.0


@dataclass
class TrendAnalysis:
    """Analysis of trends over multiple time windows."""
    metric_name: str
    current_value: float
    previous_value: float
    change_percent: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    confidence_score: float
    analysis_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CoordinationInsight:
    """Actionable insight generated from analytics."""
    insight_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    category: str = "general"  # "performance", "cost", "health", "coordination"
    severity: str = "info"  # "info", "warning", "critical"
    title: str = ""
    description: str = ""
    recommended_action: str = ""
    confidence_score: float = 0.8
    data_points: Dict[str, Any] = field(default_factory=dict)


class RealTimeAnalyticsEngine(ReflectiveModule):
    """
    Processes real-time streams of metrics to generate intelligent insights.
    
    Features:
    - Continuous stream processing from Redis
    - Time window aggregation and trend analysis
    - Coordination health calculation
    - Anomaly detection and alerting
    - Actionable insight generation
    """
    
    def __init__(self, config: ObservatoryConfig):
        super().__init__()
        self.module_id = "analytics_engine"
        self._config = config
        self._redis_client: Optional[redis.Redis] = None
        self._running = False
        self._processing_task: Optional[asyncio.Task] = None
        
        # Analytics configuration
        self._window_size_seconds = config.analytics_config.window_size_seconds
        self._trend_window_minutes = config.analytics_config.trend_analysis_window_minutes
        
        # Time series data storage
        self._time_windows: Deque[TimeWindowMetrics] = deque(maxlen=100)  # Keep last 100 windows
        self._recent_metrics: Deque[Dict[str, Any]] = deque(maxlen=1000)  # Keep last 1000 metrics
        self._recent_costs: Deque[Dict[str, Any]] = deque(maxlen=1000)  # Keep last 1000 cost events
        
        # Generated insights
        self._insights: Deque[CoordinationInsight] = deque(maxlen=50)  # Keep last 50 insights
        
        # Performance tracking
        self._start_time = time.time()
        self._metrics_processed = 0
        self._insights_generated = 0
        self._processing_errors = 0
        
        logger.info("📊 RealTimeAnalyticsEngine initialized - Ready for intelligent analysis")
    
    async def start_analytics(self) -> bool:
        """Start real-time analytics processing."""
        try:
            if self._running:
                logger.warning("RealTimeAnalyticsEngine is already running")
                return True
            
            # Connect to Redis
            await self._connect_redis()
            
            # Start processing task
            self._running = True
            self._processing_task = asyncio.create_task(self._analytics_loop())
            
            logger.info("🚀 RealTimeAnalyticsEngine started - processing streams")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start RealTimeAnalyticsEngine: {e}")
            return False
    
    async def stop_analytics(self) -> None:
        """Stop analytics processing gracefully."""
        logger.info("🛑 Stopping RealTimeAnalyticsEngine...")
        
        self._running = False
        
        # Cancel processing task
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        
        # Close Redis connection
        if self._redis_client:
            await self._redis_client.close()
        
        logger.info("✅ RealTimeAnalyticsEngine stopped gracefully")
    
    async def _connect_redis(self) -> None:
        """Connect to Redis for stream processing."""
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
            logger.info(f"📡 RealTimeAnalyticsEngine connected to Redis")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def _analytics_loop(self) -> None:
        """Main analytics processing loop."""
        logger.info("📊 Starting analytics processing loop")
        
        while self._running:
            try:
                # Process metrics streams
                await self._process_metrics_stream()
                
                # Process cost streams
                await self._process_cost_stream()
                
                # Generate time window analytics
                await self._generate_window_analytics()
                
                # Perform trend analysis
                await self._perform_trend_analysis()
                
                # Generate insights
                await self._generate_insights()
                
                # Sleep for processing interval
                await asyncio.sleep(5)  # Process every 5 seconds
                
            except asyncio.CancelledError:
                logger.info("Analytics processing loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in analytics loop: {e}")
                self._processing_errors += 1
                await asyncio.sleep(1)  # Brief pause on error
        
        logger.info("Analytics processing loop stopped")
    
    async def _process_metrics_stream(self) -> None:
        """Process metrics from Redis streams."""
        try:
            if not self._redis_client:
                return
            
            stream_name = self._config.redis_config.stream_name
            
            # Read recent entries from metrics stream
            try:
                entries = await self._redis_client.xread({stream_name: '$'}, count=10, block=100)
                
                for stream, messages in entries:
                    for message_id, fields in messages:
                        # Process each metrics message
                        await self._process_metrics_message(fields)
                        self._metrics_processed += 1
                        
            except Exception as e:
                # Stream might not exist yet or no new messages
                logger.debug(f"No new metrics in stream: {e}")
                
        except Exception as e:
            logger.error(f"Error processing metrics stream: {e}")
    
    async def _process_cost_stream(self) -> None:
        """Process cost data from Redis streams."""
        try:
            if not self._redis_client:
                return
            
            stream_name = f"{self._config.redis_config.stream_name}:llm_costs"
            
            # Read recent entries from cost stream
            try:
                entries = await self._redis_client.xread({stream_name: '$'}, count=10, block=100)
                
                for stream, messages in entries:
                    for message_id, fields in messages:
                        # Process each cost message
                        await self._process_cost_message(fields)
                        
            except Exception as e:
                # Stream might not exist yet or no new messages
                logger.debug(f"No new costs in stream: {e}")
                
        except Exception as e:
            logger.error(f"Error processing cost stream: {e}")
    
    async def _process_metrics_message(self, fields: Dict[str, str]) -> None:
        """Process a single metrics message."""
        try:
            # Convert Redis fields to structured data
            metrics_data = {
                "timestamp": datetime.fromisoformat(fields.get("timestamp", datetime.now().isoformat())),
                "component_id": fields.get("component_id", ""),
                "component_name": fields.get("component_name", ""),
                "health_score": float(fields.get("health_score", "1.0")),
                "uptime_seconds": float(fields.get("uptime_seconds", "0")),
                "error_count": int(fields.get("error_count", "0")),
                "warning_count": int(fields.get("warning_count", "0")),
            }
            
            # Add to recent metrics
            self._recent_metrics.append(metrics_data)
            
        except Exception as e:
            logger.error(f"Error processing metrics message: {e}")
    
    async def _process_cost_message(self, fields: Dict[str, str]) -> None:
        """Process a single cost message."""
        try:
            # Convert Redis fields to structured data
            cost_data = {
                "timestamp": datetime.fromisoformat(fields.get("timestamp", datetime.now().isoformat())),
                "provider": fields.get("provider", ""),
                "model": fields.get("model", ""),
                "estimated_cost": Decimal(fields.get("estimated_cost", "0.00")),
                "total_tokens": int(fields.get("total_tokens", "0")),
                "success": fields.get("success", "true").lower() == "true",
                "response_time_ms": float(fields.get("response_time_ms", "0")),
            }
            
            # Add to recent costs
            self._recent_costs.append(cost_data)
            
        except Exception as e:
            logger.error(f"Error processing cost message: {e}")
    
    async def _generate_window_analytics(self) -> None:
        """Generate analytics for the current time window."""
        try:
            now = datetime.now()
            window_start = now - timedelta(seconds=self._window_size_seconds)
            
            # Filter recent data to current window
            window_metrics = [m for m in self._recent_metrics if m["timestamp"] >= window_start]
            window_costs = [c for c in self._recent_costs if c["timestamp"] >= window_start]
            
            # Calculate component health
            component_count = len(set(m["component_id"] for m in window_metrics))
            healthy_components = len([m for m in window_metrics if m["health_score"] >= 0.8])
            warning_components = len([m for m in window_metrics if 0.5 <= m["health_score"] < 0.8])
            error_components = len([m for m in window_metrics if m["health_score"] < 0.5])
            
            # Calculate cost metrics
            total_cost = sum(c["estimated_cost"] for c in window_costs)
            llm_calls = len(window_costs)
            avg_cost_per_call = total_cost / llm_calls if llm_calls > 0 else Decimal('0.00')
            
            # Calculate performance metrics
            successful_calls = [c for c in window_costs if c["success"]]
            avg_response_time = statistics.mean([c["response_time_ms"] for c in successful_calls]) if successful_calls else 0.0
            error_rate = ((llm_calls - len(successful_calls)) / llm_calls * 100) if llm_calls > 0 else 0.0
            
            # Calculate coordination health score
            if component_count > 0:
                health_scores = [m["health_score"] for m in window_metrics]
                coordination_health = statistics.mean(health_scores)
            else:
                coordination_health = 1.0
            
            # Create time window metrics
            window_metrics_obj = TimeWindowMetrics(
                window_start=window_start,
                window_end=now,
                window_duration_seconds=self._window_size_seconds,
                component_count=component_count,
                healthy_components=healthy_components,
                warning_components=warning_components,
                error_components=error_components,
                total_cost=total_cost,
                llm_calls=llm_calls,
                avg_cost_per_call=avg_cost_per_call,
                avg_response_time_ms=avg_response_time,
                error_rate_percent=error_rate,
                coordination_health_score=coordination_health
            )
            
            # Add to time windows
            self._time_windows.append(window_metrics_obj)

            # Stream analytics data to Redis for anomaly detection
            await self._stream_analytics_data(window_metrics_obj)

            logger.debug(f"📊 Generated window analytics: {component_count} components, ${total_cost:.4f} cost, {coordination_health:.2f} health")
            
        except Exception as e:
            logger.error(f"Error generating window analytics: {e}")

    async def _stream_analytics_data(self, window_metrics: TimeWindowMetrics) -> None:
        """Stream analytics data to Redis for anomaly detection."""
        try:
            if not self._redis_client:
                return

            # Prepare analytics data for anomaly detection
            analytics_data = {
                "timestamp": window_metrics.window_end.isoformat(),
                "coordination_health_score": str(window_metrics.coordination_health_score),
                "component_count": str(window_metrics.component_count),
                "error_rate_percent": str(window_metrics.error_rate_percent),
                "avg_response_time_ms": str(window_metrics.avg_response_time_ms),
                "avg_cost_per_call": str(float(window_metrics.avg_cost_per_call)),
                "total_cost": str(float(window_metrics.total_cost)),
                "llm_calls": str(window_metrics.llm_calls),
                "healthy_components": str(window_metrics.healthy_components),
                "warning_components": str(window_metrics.warning_components),
                "error_components": str(window_metrics.error_components)
            }

            stream_name = f"{self._config.redis_config.stream_name}:analytics"
            await self._redis_client.xadd(stream_name, analytics_data)

        except Exception as e:
            logger.error(f"Error streaming analytics data: {e}")

    async def _perform_trend_analysis(self) -> None:
        """Perform trend analysis on time windows."""
        try:
            if len(self._time_windows) < 2:
                return  # Need at least 2 windows for trend analysis
            
            current_window = self._time_windows[-1]
            previous_window = self._time_windows[-2]
            
            # Analyze coordination health trend
            health_change = ((current_window.coordination_health_score - previous_window.coordination_health_score) 
                           / previous_window.coordination_health_score * 100)
            
            if abs(health_change) > 10:  # Significant change
                trend_direction = "increasing" if health_change > 0 else "decreasing"
                logger.info(f"📈 Coordination health trend: {trend_direction} by {abs(health_change):.1f}%")
            
            # Analyze cost trend
            if current_window.total_cost > 0 and previous_window.total_cost > 0:
                cost_change = ((float(current_window.total_cost) - float(previous_window.total_cost)) 
                             / float(previous_window.total_cost) * 100)
                
                if abs(cost_change) > 20:  # Significant cost change
                    trend_direction = "increasing" if cost_change > 0 else "decreasing"
                    logger.info(f"💰 Cost trend: {trend_direction} by {abs(cost_change):.1f}%")
            
        except Exception as e:
            logger.error(f"Error performing trend analysis: {e}")
    
    async def _generate_insights(self) -> None:
        """Generate actionable insights from analytics."""
        try:
            if not self._time_windows:
                return
            
            current_window = self._time_windows[-1]
            
            # Generate health insights
            if current_window.coordination_health_score < 0.7:
                insight = CoordinationInsight(
                    category="health",
                    severity="warning" if current_window.coordination_health_score > 0.5 else "critical",
                    title="Coordination Health Declining",
                    description=f"System health score is {current_window.coordination_health_score:.2f} with {current_window.error_components} components in error state",
                    recommended_action="Review component logs and address failing components",
                    confidence_score=0.9,
                    data_points={
                        "health_score": current_window.coordination_health_score,
                        "error_components": current_window.error_components,
                        "total_components": current_window.component_count
                    }
                )
                self._insights.append(insight)
                self._insights_generated += 1
                logger.warning(f"🚨 Generated health insight: {insight.title}")
            
            # Generate cost insights
            if current_window.avg_cost_per_call > Decimal('0.05'):  # $0.05 per call threshold
                insight = CoordinationInsight(
                    category="cost",
                    severity="warning",
                    title="High Average LLM Cost Per Call",
                    description=f"Average cost per LLM call is ${current_window.avg_cost_per_call:.4f}, consider optimizing model usage",
                    recommended_action="Review model selection and prompt efficiency",
                    confidence_score=0.8,
                    data_points={
                        "avg_cost_per_call": float(current_window.avg_cost_per_call),
                        "total_calls": current_window.llm_calls,
                        "total_cost": float(current_window.total_cost)
                    }
                )
                self._insights.append(insight)
                self._insights_generated += 1
                logger.warning(f"💸 Generated cost insight: {insight.title}")
            
            # Generate performance insights
            if current_window.error_rate_percent > 10:  # 10% error rate threshold
                insight = CoordinationInsight(
                    category="performance",
                    severity="warning",
                    title="High LLM API Error Rate",
                    description=f"LLM API error rate is {current_window.error_rate_percent:.1f}%, indicating potential service issues",
                    recommended_action="Check API status and implement retry logic",
                    confidence_score=0.9,
                    data_points={
                        "error_rate_percent": current_window.error_rate_percent,
                        "total_calls": current_window.llm_calls,
                        "avg_response_time": current_window.avg_response_time_ms
                    }
                )
                self._insights.append(insight)
                self._insights_generated += 1
                logger.warning(f"⚠️ Generated performance insight: {insight.title}")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
    
    def get_current_analytics(self) -> Dict[str, Any]:
        """Get current analytics and insights."""
        try:
            current_window = self._time_windows[-1] if self._time_windows else None
            recent_insights = list(self._insights)[-10:]  # Last 10 insights
            
            return {
                "current_window": {
                    "coordination_health_score": current_window.coordination_health_score if current_window else 1.0,
                    "component_count": current_window.component_count if current_window else 0,
                    "healthy_components": current_window.healthy_components if current_window else 0,
                    "warning_components": current_window.warning_components if current_window else 0,
                    "error_components": current_window.error_components if current_window else 0,
                    "total_cost": float(current_window.total_cost) if current_window else 0.0,
                    "llm_calls": current_window.llm_calls if current_window else 0,
                    "avg_cost_per_call": float(current_window.avg_cost_per_call) if current_window else 0.0,
                    "error_rate_percent": current_window.error_rate_percent if current_window else 0.0,
                    "avg_response_time_ms": current_window.avg_response_time_ms if current_window else 0.0,
                },
                "insights": [
                    {
                        "category": insight.category,
                        "severity": insight.severity,
                        "title": insight.title,
                        "description": insight.description,
                        "recommended_action": insight.recommended_action,
                        "confidence_score": insight.confidence_score,
                        "timestamp": insight.timestamp.isoformat()
                    }
                    for insight in recent_insights
                ],
                "analytics_stats": self.get_analytics_stats()
            }
            
        except Exception as e:
            logger.error(f"Error getting current analytics: {e}")
            return {"current_window": {}, "insights": [], "analytics_stats": {}}
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics processing statistics."""
        uptime = time.time() - self._start_time
        
        return {
            "uptime_seconds": uptime,
            "metrics_processed": self._metrics_processed,
            "insights_generated": self._insights_generated,
            "processing_errors": self._processing_errors,
            "processing_rate_per_second": self._metrics_processed / uptime if uptime > 0 else 0,
            "time_windows_stored": len(self._time_windows),
            "recent_metrics_count": len(self._recent_metrics),
            "recent_costs_count": len(self._recent_costs),
            "active_insights": len(self._insights)
        }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get RealTimeAnalyticsEngine capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.ANALYTICS,
        ]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Real-Time Analytics Engine",
            "version": "1.0.0",
            "description": "Processes streams of metrics to generate intelligent insights",
            "config": {
                "window_size_seconds": self._window_size_seconds,
                "trend_window_minutes": self._trend_window_minutes,
                "max_time_windows": 100,
                "max_insights": 50
            }
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation on errors."""
        logger.warning(f"RealTimeAnalyticsEngine entering graceful degradation due to: {error}")
        
        # Continue processing even if Redis streams are unavailable
        if "redis" in str(error).lower():
            logger.info("Redis connection issue - continuing analytics with cached data")
            return True
        
        return False
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the RealTimeAnalyticsEngine."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        if not self._running:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = ["RealTimeAnalyticsEngine is not running"]
        else:
            # Check processing health
            uptime = time.time() - self._start_time
            processing_rate = self._metrics_processed / uptime if uptime > 0 else 0
            error_rate = (self._processing_errors / max(1, self._metrics_processed)) * 100
            
            if error_rate > 10:
                status = ModuleStatus.ERROR
                health_score = 0.3
                issues = [f"High processing error rate: {error_rate:.1f}%"]
            elif error_rate > 5:
                status = ModuleStatus.WARNING
                health_score = 0.7
                issues = [f"Elevated processing error rate: {error_rate:.1f}%"]
            elif processing_rate > 0 or uptime < 60:  # Allow 1 minute warmup
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            else:
                status = ModuleStatus.WARNING
                health_score = 0.5
                issues = ["No metrics processed recently"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=time.time() - self._start_time,
            error_count=self._processing_errors,
            warning_count=len([i for i in self._insights if i.severity == "warning"])
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for this engine."""
        return {
            "analytics_stats": self.get_analytics_stats(),
            "current_analytics": self.get_current_analytics(),
            "running": self._running
        }