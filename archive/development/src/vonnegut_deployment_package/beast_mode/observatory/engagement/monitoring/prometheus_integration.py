"""
Prometheus Integration for Engagement Metrics

Integrates engagement metrics with Observatory's existing Prometheus monitoring system.
Provides seamless integration with existing metrics collection and health monitoring.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .engagement_metrics import EngagementMetricsCollector

logger = logging.getLogger(__name__)


class EngagementPrometheusIntegration(ReflectiveModule):
    """
    Integrates engagement metrics with Observatory's Prometheus monitoring system.
    
    Provides seamless integration with existing metrics collection, health monitoring,
    and adds engagement-specific metrics to the Observatory monitoring stack.
    """
    
    def __init__(self, metrics_collector: EngagementMetricsCollector):
        super().__init__()
        self.module_id = "engagement_prometheus_integration"
        
        self.metrics_collector = metrics_collector
        
        # Integration state
        self.running = False
        self.prometheus_registered = False
        
        # Metrics tracking
        self.metrics_exported = 0
        self.last_export = datetime.now()
        self.export_errors = 0
        
        logger.info("🔗 Engagement Prometheus Integration initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Prometheus integration."""
        try:
            # Register with Prometheus if available
            await self._register_with_prometheus()
            
            self.running = True
            logger.info("✅ Engagement Prometheus Integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Engagement Prometheus Integration: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the Prometheus integration."""
        logger.info("🛑 Shutting down Engagement Prometheus Integration...")
        
        self.running = False
        
        # Unregister from Prometheus if needed
        await self._unregister_from_prometheus()
        
        logger.info("✅ Engagement Prometheus Integration shutdown complete")
    
    async def _register_with_prometheus(self):
        """Register engagement metrics with Prometheus."""
        try:
            # Try to register with prometheus_client if available
            try:
                from prometheus_client import CollectorRegistry, REGISTRY, Gauge, Counter, Histogram
                
                # Create engagement-specific metrics
                self._create_prometheus_metrics()
                self.prometheus_registered = True
                
                logger.info("📊 Registered engagement metrics with Prometheus client")
                
            except ImportError:
                logger.info("📊 Prometheus client not available, using fallback metrics export")
                self.prometheus_registered = False
                
        except Exception as e:
            logger.error(f"Failed to register with Prometheus: {e}")
            self.prometheus_registered = False
    
    def _create_prometheus_metrics(self):
        """Create Prometheus metric objects for engagement data."""
        try:
            from prometheus_client import Gauge, Counter, Histogram, CollectorRegistry, REGISTRY
            
            # Check if metrics already exist to avoid duplicates
            existing_metrics = set()
            for collector in REGISTRY._collector_to_names.values():
                existing_metrics.update(collector)
            
            # Attention metrics
            if 'engagement_attention_sessions_active' not in existing_metrics:
                self.attention_sessions_active = Gauge(
                    'engagement_attention_sessions_active',
                    'Number of active attention tracking sessions',
                    ['user_type']
                )
            else:
                self.attention_sessions_active = None
            
            self.attention_session_duration = Histogram(
                'engagement_attention_session_duration_seconds',
                'Duration of attention sessions in seconds',
                ['user_id'],
                buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600]
            )
            
            self.attention_sessions_completed = Counter(
                'engagement_attention_sessions_completed_total',
                'Total number of completed attention sessions',
                ['user_id']
            )
            
            # Interaction metrics
            self.interactions_total = Counter(
                'engagement_interactions_total',
                'Total number of user interactions',
                ['user_id', 'event_type', 'component']
            )
            
            self.interaction_duration = Histogram(
                'engagement_interaction_duration_seconds',
                'Duration of user interactions in seconds',
                ['event_type', 'component'],
                buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
            )
            
            # Focus events
            self.focus_events = Counter(
                'engagement_focus_events_total',
                'Total number of focus/blur events',
                ['user_id', 'event_type']
            )
            
            self.page_views = Counter(
                'engagement_page_views_total',
                'Total number of page views',
                ['user_id', 'page']
            )
            
            # Animation metrics
            self.animations_total = Counter(
                'engagement_animations_total',
                'Total number of animations triggered',
                ['animation_type']
            )
            
            self.animation_duration = Histogram(
                'engagement_animation_duration_seconds',
                'Duration of animations in seconds',
                ['animation_type'],
                buckets=[0.1, 0.5, 1, 2, 5, 10]
            )
            
            self.animation_performance = Gauge(
                'engagement_animation_performance_score',
                'Animation performance score (0-1)',
                ['animation_type']
            )
            
            # Personality metrics
            self.personality_transitions = Counter(
                'engagement_personality_transitions_total',
                'Total number of personality mood transitions',
                ['from_mood', 'to_mood', 'trigger']
            )
            
            # Attention manager metrics
            self.attention_events = Counter(
                'engagement_attention_events_total',
                'Total number of attention priority events',
                ['priority']
            )
            
            self.attention_processing_time = Histogram(
                'engagement_attention_processing_seconds',
                'Time to process attention events',
                ['priority'],
                buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
            )
            
            # Learning metrics
            self.learning_optimizations = Counter(
                'engagement_learning_optimizations_total',
                'Total number of learning optimizations',
                ['optimization_type']
            )
            
            self.learning_improvement = Gauge(
                'engagement_learning_improvement_score',
                'Learning improvement score',
                ['optimization_type']
            )
            
            # System metrics
            self.metrics_collected = Counter(
                'engagement_metrics_collected_total',
                'Total number of engagement metrics collected'
            )
            
            self.system_health = Gauge(
                'engagement_system_health_score',
                'Overall engagement system health score (0-1)'
            )
            
            logger.info("📊 Created Prometheus metric objects for engagement data")
            
        except Exception as e:
            logger.error(f"Failed to create Prometheus metrics: {e}")
            raise
    
    async def update_prometheus_metrics(self):
        """Update Prometheus metrics with current engagement data."""
        if not self.prometheus_registered:
            return
        
        try:
            # Get current engagement summary
            summary = self.metrics_collector.get_engagement_summary()
            
            # Update system metrics
            self.attention_sessions_active.labels(user_type='all').set(
                summary.get('active_attention_sessions', 0)
            )
            
            self.metrics_collected.inc(
                summary.get('metrics_collected', 0) - self.metrics_exported
            )
            
            # Calculate health score based on engagement activity
            health_score = self._calculate_engagement_health_score(summary)
            self.system_health.set(health_score)
            
            # Update tracking
            self.metrics_exported = summary.get('metrics_collected', 0)
            self.last_export = datetime.now()
            
            logger.debug("📊 Updated Prometheus metrics with engagement data")
            
        except Exception as e:
            self.export_errors += 1
            logger.error(f"Failed to update Prometheus metrics: {e}")
    
    def _calculate_engagement_health_score(self, summary: Dict[str, Any]) -> float:
        """Calculate overall engagement system health score."""
        try:
            score = 1.0
            
            # Reduce score if no active sessions
            if summary.get('active_attention_sessions', 0) == 0:
                score *= 0.8
            
            # Reduce score if interaction rate is very low
            interaction_rate = summary.get('recent_interaction_rate_per_minute', 0)
            if interaction_rate < 0.1:
                score *= 0.9
            
            # Reduce score if average session duration is very short
            avg_duration = summary.get('average_session_duration_seconds', 0)
            if avg_duration < 10:
                score *= 0.9
            
            # Boost score for healthy activity
            if interaction_rate > 1.0 and avg_duration > 60:
                score = min(1.0, score * 1.1)
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating engagement health score: {e}")
            return 0.5
    
    def get_prometheus_metrics_text(self) -> str:
        """Get engagement metrics in Prometheus text format."""
        try:
            if self.prometheus_registered:
                # Use prometheus_client to generate metrics
                from prometheus_client import generate_latest, REGISTRY
                return generate_latest(REGISTRY).decode('utf-8')
            else:
                # Use fallback metrics from collector
                return self.metrics_collector.get_prometheus_metrics()
                
        except Exception as e:
            logger.error(f"Failed to get Prometheus metrics text: {e}")
            return f"# Error generating engagement metrics: {e}\n"
    
    async def inject_into_observatory_metrics(self, observatory_metrics: Dict[str, Any]):
        """Inject engagement metrics into Observatory's metrics endpoint."""
        try:
            # Get engagement summary
            summary = self.metrics_collector.get_engagement_summary()
            
            # Add engagement metrics to Observatory metrics
            observatory_metrics.update({
                "engagement_active_sessions": summary.get('active_attention_sessions', 0),
                "engagement_completed_sessions": summary.get('completed_sessions', 0),
                "engagement_total_interactions": summary.get('total_interactions', 0),
                "engagement_interaction_rate_per_minute": summary.get('recent_interaction_rate_per_minute', 0),
                "engagement_avg_session_duration_seconds": summary.get('average_session_duration_seconds', 0),
                "engagement_metrics_collected": summary.get('metrics_collected', 0),
                "engagement_system_health_score": self._calculate_engagement_health_score(summary)
            })
            
            logger.debug("📊 Injected engagement metrics into Observatory metrics")
            
        except Exception as e:
            logger.error(f"Failed to inject engagement metrics: {e}")
    
    async def _unregister_from_prometheus(self):
        """Unregister from Prometheus if needed."""
        try:
            if self.prometheus_registered:
                # Clean up Prometheus metrics if needed
                logger.info("📊 Unregistered engagement metrics from Prometheus")
                
        except Exception as e:
            logger.error(f"Failed to unregister from Prometheus: {e}")
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Prometheus integration capabilities."""
        return [
            "prometheus_metrics_export",
            "observatory_metrics_injection",
            "health_score_calculation",
            "real_time_metrics_update",
            "fallback_metrics_export"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Prometheus integration health status."""
        return {
            "status": "healthy" if self.running else "stopped",
            "prometheus_registered": self.prometheus_registered,
            "metrics_exported": self.metrics_exported,
            "last_export": self.last_export.isoformat(),
            "export_errors": self.export_errors,
            "integration_running": self.running
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Prometheus integration module information."""
        return {
            "module_id": self.module_id,
            "name": "Engagement Prometheus Integration",
            "version": "1.0.0",
            "description": "Integrates engagement metrics with Observatory's Prometheus monitoring"
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation when errors occur."""
        try:
            logger.warning(f"Engagement Prometheus Integration entering degradation mode due to: {error}")
            
            # Fall back to basic metrics export if Prometheus fails
            if self.prometheus_registered:
                self.prometheus_registered = False
                logger.info("Switched to fallback metrics export mode")
            
            # Reset error counter if it gets too high
            if self.export_errors > 10:
                self.export_errors = 0
                logger.info("Reset export error counter")
            
            logger.info("Degradation applied: using fallback metrics export")
            return True
            
        except Exception as degradation_error:
            logger.error(f"Failed to apply graceful degradation: {degradation_error}")
            return False


# Helper functions for Observatory integration

async def create_engagement_prometheus_integration(
    metrics_collector: EngagementMetricsCollector
) -> EngagementPrometheusIntegration:
    """Create and initialize engagement Prometheus integration."""
    integration = EngagementPrometheusIntegration(metrics_collector)
    await integration.initialize()
    return integration


async def inject_engagement_metrics_into_observatory(
    integration: EngagementPrometheusIntegration,
    observatory_metrics: Dict[str, Any]
) -> None:
    """Inject engagement metrics into Observatory's metrics endpoint."""
    await integration.inject_into_observatory_metrics(observatory_metrics)


def get_engagement_prometheus_metrics(
    integration: EngagementPrometheusIntegration
) -> str:
    """Get engagement metrics in Prometheus format."""
    return integration.get_prometheus_metrics_text()