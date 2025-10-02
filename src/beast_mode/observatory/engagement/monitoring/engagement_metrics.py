"""
Engagement Metrics Integration

Integrates engagement-specific metrics with Observatory's Prometheus monitoring system.
Provides comprehensive metrics for attention time, interaction rates, and engagement analytics.
"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import json
import logging

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

logger = logging.getLogger(__name__)


@dataclass
class EngagementMetric:
    """Represents an engagement-specific metric."""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metric_type: str = "gauge"  # gauge, counter, histogram


@dataclass
class AttentionSession:
    """Tracks user attention session data."""
    user_id: str
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    interactions: int = 0
    focus_events: int = 0
    blur_events: int = 0
    page_views: List[str] = field(default_factory=list)


@dataclass
class InteractionEvent:
    """Represents a user interaction event."""
    user_id: str
    event_type: str  # click, hover, scroll, keyboard, etc.
    component: str
    timestamp: float
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EngagementMetricsCollector(ReflectiveModule):
    """
    Collects and manages engagement-specific metrics for Observatory integration.
    
    Tracks attention time, interaction rates, engagement patterns, and provides
    Prometheus-compatible metrics for monitoring and alerting.
    """
    
    def __init__(self, max_session_history: int = 1000):
        super().__init__()
        self.module_id = "engagement_metrics_collector"
        
        # Configuration
        self.max_session_history = max_session_history
        
        # Metrics storage
        self._engagement_metrics: Dict[str, EngagementMetric] = {}
        self._attention_sessions: Dict[str, AttentionSession] = {}
        self._interaction_events: deque = deque(maxlen=10000)
        self._session_history: deque = deque(maxlen=max_session_history)
        
        # Aggregated metrics
        self._hourly_stats: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._daily_stats: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Performance tracking
        self._metrics_collected = 0
        self._last_cleanup = time.time()
        self._collection_start_time = time.time()
        
        # Background tasks
        self._running = False
        self._aggregation_task: Optional[asyncio.Task] = None
        
        logger.info("🎯 Engagement Metrics Collector initialized")
    
    async def initialize(self) -> bool:
        """Initialize the metrics collector."""
        try:
            # Start background aggregation
            self._running = True
            self._aggregation_task = asyncio.create_task(self._aggregation_loop())
            
            logger.info("✅ Engagement Metrics Collector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Engagement Metrics Collector: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the metrics collector."""
        logger.info("🛑 Shutting down Engagement Metrics Collector...")
        
        self._running = False
        
        if self._aggregation_task and not self._aggregation_task.done():
            self._aggregation_task.cancel()
            try:
                await self._aggregation_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Engagement Metrics Collector shutdown complete")
    
    # Attention Metrics
    
    async def start_attention_session(self, user_id: str, session_id: str, 
                                    page_view: str = None) -> None:
        """Start tracking an attention session."""
        session = AttentionSession(
            user_id=user_id,
            session_id=session_id,
            start_time=time.time(),
            page_views=[page_view] if page_view else []
        )
        
        self._attention_sessions[session_id] = session
        
        # Update metrics
        await self._update_metric("engagement_active_sessions", 
                                len(self._attention_sessions), 
                                {"type": "attention"})
        
        logger.debug(f"Started attention session: {session_id} for user {user_id}")
    
    async def end_attention_session(self, session_id: str) -> Optional[float]:
        """End an attention session and return duration."""
        if session_id not in self._attention_sessions:
            logger.warning(f"Attempted to end unknown session: {session_id}")
            return None
        
        session = self._attention_sessions[session_id]
        session.end_time = time.time()
        duration = session.end_time - session.start_time
        
        # Move to history
        self._session_history.append(session)
        del self._attention_sessions[session_id]
        
        # Update metrics
        await self._update_metric("engagement_session_duration_seconds", 
                                duration, 
                                {"user_id": session.user_id}, 
                                "histogram")
        
        await self._update_metric("engagement_active_sessions", 
                                len(self._attention_sessions), 
                                {"type": "attention"})
        
        await self._update_metric("engagement_sessions_completed_total", 
                                1, 
                                {"user_id": session.user_id}, 
                                "counter")
        
        logger.debug(f"Ended attention session: {session_id}, duration: {duration:.2f}s")
        return duration
    
    async def record_focus_event(self, session_id: str, event_type: str = "focus") -> None:
        """Record a focus/blur event for a session."""
        if session_id not in self._attention_sessions:
            return
        
        session = self._attention_sessions[session_id]
        
        if event_type == "focus":
            session.focus_events += 1
        elif event_type == "blur":
            session.blur_events += 1
        
        # Update metrics
        await self._update_metric(f"engagement_{event_type}_events_total", 
                                1, 
                                {"user_id": session.user_id}, 
                                "counter")
    
    async def record_page_view(self, session_id: str, page_view: str) -> None:
        """Record a page view for a session."""
        if session_id not in self._attention_sessions:
            return
        
        session = self._attention_sessions[session_id]
        session.page_views.append(page_view)
        
        # Update metrics
        await self._update_metric("engagement_page_views_total", 
                                1, 
                                {"user_id": session.user_id, "page": page_view}, 
                                "counter")
    
    # Interaction Metrics
    
    async def record_interaction(self, user_id: str, event_type: str, 
                               component: str, duration: float = None,
                               metadata: Dict[str, Any] = None) -> None:
        """Record a user interaction event."""
        interaction = InteractionEvent(
            user_id=user_id,
            event_type=event_type,
            component=component,
            timestamp=time.time(),
            duration=duration,
            metadata=metadata or {}
        )
        
        self._interaction_events.append(interaction)
        
        # Update session if active
        for session in self._attention_sessions.values():
            if session.user_id == user_id:
                session.interactions += 1
                break
        
        # Update metrics
        await self._update_metric("engagement_interactions_total", 
                                1, 
                                {
                                    "user_id": user_id, 
                                    "event_type": event_type,
                                    "component": component
                                }, 
                                "counter")
        
        if duration is not None:
            await self._update_metric("engagement_interaction_duration_seconds", 
                                    duration, 
                                    {
                                        "event_type": event_type,
                                        "component": component
                                    }, 
                                    "histogram")
        
        self._metrics_collected += 1
        logger.debug(f"Recorded interaction: {event_type} on {component} by {user_id}")
    
    async def record_animation_event(self, animation_type: str, duration: float,
                                   performance_score: float = None) -> None:
        """Record animation performance metrics."""
        await self._update_metric("engagement_animations_total", 
                                1, 
                                {"animation_type": animation_type}, 
                                "counter")
        
        await self._update_metric("engagement_animation_duration_seconds", 
                                duration, 
                                {"animation_type": animation_type}, 
                                "histogram")
        
        if performance_score is not None:
            await self._update_metric("engagement_animation_performance_score", 
                                    performance_score, 
                                    {"animation_type": animation_type})
    
    async def record_personality_transition(self, from_mood: str, to_mood: str,
                                          trigger: str) -> None:
        """Record personality engine mood transitions."""
        await self._update_metric("engagement_personality_transitions_total", 
                                1, 
                                {
                                    "from_mood": from_mood,
                                    "to_mood": to_mood,
                                    "trigger": trigger
                                }, 
                                "counter")
    
    async def record_attention_priority_event(self, event_priority: str, 
                                            processing_time: float) -> None:
        """Record attention manager priority events."""
        await self._update_metric("engagement_attention_events_total", 
                                1, 
                                {"priority": event_priority}, 
                                "counter")
        
        await self._update_metric("engagement_attention_processing_seconds", 
                                processing_time, 
                                {"priority": event_priority}, 
                                "histogram")
    
    async def record_learning_optimization(self, optimization_type: str,
                                         improvement_score: float) -> None:
        """Record learning engine optimizations."""
        await self._update_metric("engagement_learning_optimizations_total", 
                                1, 
                                {"optimization_type": optimization_type}, 
                                "counter")
        
        await self._update_metric("engagement_learning_improvement_score", 
                                improvement_score, 
                                {"optimization_type": optimization_type})
    
    # Metrics Management
    
    async def _update_metric(self, name: str, value: float, 
                           labels: Dict[str, str] = None,
                           metric_type: str = "gauge") -> None:
        """Update or create a metric."""
        labels = labels or {}
        
        # Create metric key with labels
        label_key = self._create_label_key(labels)
        full_name = f"{name}{label_key}"
        
        # Handle different metric types
        if metric_type == "counter":
            if full_name in self._engagement_metrics:
                self._engagement_metrics[full_name].value += value
            else:
                self._engagement_metrics[full_name] = EngagementMetric(
                    name=name, value=value, labels=labels, metric_type=metric_type
                )
            # Update timestamp
            self._engagement_metrics[full_name].timestamp = time.time()
            
        elif metric_type == "histogram":
            # For histograms, we'll store individual observations
            # and calculate statistics during export
            hist_key = f"{name}_observations{label_key}"
            if hist_key not in self._engagement_metrics:
                self._engagement_metrics[hist_key] = EngagementMetric(
                    name=f"{name}_observations", 
                    value=0, 
                    labels=labels, 
                    metric_type="histogram"
                )
            
            # Store observation (simplified - in production would use proper histogram)
            self._engagement_metrics[hist_key].value += 1
            self._engagement_metrics[hist_key].timestamp = time.time()
            
            # Also store sum for average calculation
            sum_key = f"{name}_sum{label_key}"
            if sum_key not in self._engagement_metrics:
                self._engagement_metrics[sum_key] = EngagementMetric(
                    name=f"{name}_sum", 
                    value=0, 
                    labels=labels, 
                    metric_type="histogram_sum"
                )
            self._engagement_metrics[sum_key].value += value
            self._engagement_metrics[sum_key].timestamp = time.time()
            
        else:  # gauge
            self._engagement_metrics[full_name] = EngagementMetric(
                name=name, value=value, labels=labels, metric_type=metric_type
            )
            self._engagement_metrics[full_name].timestamp = time.time()
    
    def _create_label_key(self, labels: Dict[str, str]) -> str:
        """Create a key from labels for metric identification."""
        if not labels:
            return ""
        
        sorted_labels = sorted(labels.items())
        return "{" + ",".join(f"{k}={v}" for k, v in sorted_labels) + "}"
    
    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # Group metrics by base name
        metric_groups = defaultdict(list)
        for full_name, metric in self._engagement_metrics.items():
            base_name = metric.name.replace("_observations", "").replace("_sum", "")
            metric_groups[base_name].append((full_name, metric))
        
        for base_name, metrics in metric_groups.items():
            # Add TYPE comment
            metric_type = metrics[0][1].metric_type
            if metric_type == "counter":
                lines.append(f"# TYPE {base_name} counter")
            elif metric_type in ["histogram", "histogram_sum"]:
                lines.append(f"# TYPE {base_name} histogram")
            else:
                lines.append(f"# TYPE {base_name} gauge")
            
            # Add metrics
            for full_name, metric in metrics:
                label_str = ""
                if metric.labels:
                    label_str = "{" + ",".join(f'{k}="{v}"' for k, v in metric.labels.items()) + "}"
                
                # Use the base name for output, not the internal storage name
                output_name = base_name
                if "_observations" in metric.name:
                    output_name = f"{base_name}_count"
                elif "_sum" in metric.name:
                    output_name = f"{base_name}_sum"
                
                lines.append(f"{output_name}{label_str} {metric.value}")
        
        return "\n".join(lines) + "\n"
    
    def get_engagement_summary(self) -> Dict[str, Any]:
        """Get a summary of engagement metrics."""
        active_sessions = len(self._attention_sessions)
        total_interactions = len(self._interaction_events)
        completed_sessions = len(self._session_history)
        
        # Calculate average session duration
        avg_session_duration = 0.0
        if self._session_history:
            durations = [
                (s.end_time - s.start_time) for s in self._session_history 
                if s.end_time is not None
            ]
            if durations:
                avg_session_duration = sum(durations) / len(durations)
        
        # Calculate interaction rate (interactions per minute)
        current_time = time.time()
        recent_interactions = [
            e for e in self._interaction_events 
            if current_time - e.timestamp < 300  # Last 5 minutes
        ]
        interaction_rate = len(recent_interactions) / 5.0  # per minute
        
        return {
            "active_attention_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "total_interactions": total_interactions,
            "recent_interaction_rate_per_minute": interaction_rate,
            "average_session_duration_seconds": avg_session_duration,
            "metrics_collected": self._metrics_collected,
            "uptime_seconds": current_time - self._collection_start_time,
            "total_engagement_metrics": len(self._engagement_metrics)
        }
    
    async def _aggregation_loop(self):
        """Background loop for metric aggregation and cleanup."""
        logger.info("📊 Starting engagement metrics aggregation loop")
        
        while self._running:
            try:
                await self._perform_aggregation()
                await self._cleanup_old_data()
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Error in metrics aggregation loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_aggregation(self):
        """Perform hourly and daily metric aggregation."""
        current_time = time.time()
        current_hour = int(current_time // 3600)
        current_day = int(current_time // 86400)
        
        # Aggregate hourly stats
        if current_hour not in self._hourly_stats:
            self._hourly_stats[current_hour] = self._calculate_period_stats(3600)
        
        # Aggregate daily stats
        if current_day not in self._daily_stats:
            self._daily_stats[current_day] = self._calculate_period_stats(86400)
    
    def _calculate_period_stats(self, period_seconds: int) -> Dict[str, float]:
        """Calculate statistics for a time period."""
        current_time = time.time()
        period_start = current_time - period_seconds
        
        # Filter events in period
        period_interactions = [
            e for e in self._interaction_events 
            if e.timestamp >= period_start
        ]
        
        period_sessions = [
            s for s in self._session_history 
            if s.start_time >= period_start
        ]
        
        return {
            "interactions": len(period_interactions),
            "sessions": len(period_sessions),
            "avg_session_duration": sum(
                (s.end_time - s.start_time) for s in period_sessions 
                if s.end_time is not None
            ) / max(len(period_sessions), 1),
            "unique_users": len(set(e.user_id for e in period_interactions))
        }
    
    async def _cleanup_old_data(self):
        """Clean up old data to prevent memory leaks."""
        current_time = time.time()
        
        # Only cleanup every hour
        if current_time - self._last_cleanup < 3600:
            return
        
        # Clean up old hourly stats (keep 7 days)
        cutoff_hour = int((current_time - 7 * 86400) // 3600)
        self._hourly_stats = {
            hour: stats for hour, stats in self._hourly_stats.items() 
            if hour > cutoff_hour
        }
        
        # Clean up old daily stats (keep 30 days)
        cutoff_day = int((current_time - 30 * 86400) // 86400)
        self._daily_stats = {
            day: stats for day, stats in self._daily_stats.items() 
            if day > cutoff_day
        }
        
        self._last_cleanup = current_time
        logger.debug("Performed engagement metrics cleanup")
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get engagement metrics collector capabilities."""
        return [
            "attention_tracking",
            "interaction_metrics",
            "engagement_analytics",
            "prometheus_export",
            "real_time_aggregation",
            "session_management"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get engagement metrics collector health status."""
        return {
            "status": "healthy" if self._running else "stopped",
            "metrics_collected": self._metrics_collected,
            "active_sessions": len(self._attention_sessions),
            "total_metrics": len(self._engagement_metrics),
            "aggregation_running": self._aggregation_task is not None and not self._aggregation_task.done(),
            "uptime_seconds": time.time() - self._collection_start_time
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get engagement metrics collector module information."""
        return {
            "module_id": self.module_id,
            "name": "Engagement Metrics Collector",
            "version": "1.0.0",
            "description": "Collects and manages engagement-specific metrics for Observatory monitoring"
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation when errors occur."""
        try:
            logger.warning(f"Engagement Metrics Collector entering degradation mode due to: {error}")
            
            # Reduce collection frequency by stopping aggregation temporarily
            if self._aggregation_task and not self._aggregation_task.done():
                self._aggregation_task.cancel()
                self._aggregation_task = None
            
            # Clear some memory by removing old metrics
            await self._cleanup_old_data()
            
            logger.info("Degradation applied: stopped aggregation and cleaned up data")
            return True
            
        except Exception as degradation_error:
            logger.error(f"Failed to apply graceful degradation: {degradation_error}")
            return False