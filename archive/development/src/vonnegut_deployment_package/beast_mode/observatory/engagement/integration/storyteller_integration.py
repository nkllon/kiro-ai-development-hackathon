"""
Data Storyteller Integration - Observatory Dashboard Integration
==============================================================

Integrates the Data Storyteller Engine with the existing Observatory dashboard
to provide real-time data insights and pattern discovery.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..intelligence.data_storyteller import DataStorytellerEngine, DataPoint
from ..core.dashboard_engine import DashboardEngine

logger = logging.getLogger(__name__)


class StorytellerIntegration(ReflectiveModule):
    """Integrates Data Storyteller with Observatory dashboard."""
    
    def __init__(self, dashboard_engine: DashboardEngine):
        super().__init__()
        self.module_id = "storyteller_integration"
        
        self.dashboard_engine = dashboard_engine
        self.storyteller = DataStorytellerEngine()
        
        # Integration state
        self.active_insights: Dict[str, Any] = {}
        self.last_update: Optional[datetime] = None
        
        logger.info("Storyteller Integration initialized")
    
    async def initialize(self) -> bool:
        """Initialize the integration."""
        try:
            # Initialize the storyteller engine
            await self.storyteller.initialize()
            
            # Register with dashboard engine for data updates
            await self._register_data_callbacks()
            
            # Start insight broadcasting
            asyncio.create_task(self._insight_broadcast_loop())
            
            logger.info("Storyteller Integration initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Storyteller Integration initialization failed: {e}")
            return False
    
    async def process_observatory_data(self, data: Dict[str, Any]) -> None:
        """Process incoming Observatory data for pattern analysis."""
        try:
            timestamp = datetime.now()
            
            # Convert Observatory data to DataPoints
            data_points = []
            
            # Process different types of Observatory data
            if "metrics" in data:
                for metric_name, value in data["metrics"].items():
                    if isinstance(value, (int, float)):
                        data_point = DataPoint(
                            timestamp=timestamp,
                            value=float(value),
                            metric_name=metric_name,
                            source="observatory",
                            quality_score=1.0,
                            metadata={"raw_data": data}
                        )
                        data_points.append(data_point)
            
            # Process health data
            if "health" in data:
                health_score = self._calculate_health_score(data["health"])
                data_point = DataPoint(
                    timestamp=timestamp,
                    value=health_score,
                    metric_name="system_health",
                    source="observatory",
                    quality_score=1.0,
                    metadata={"health_data": data["health"]}
                )
                data_points.append(data_point)
            
            # Process performance data
            if "performance" in data:
                for perf_metric, value in data["performance"].items():
                    if isinstance(value, (int, float)):
                        data_point = DataPoint(
                            timestamp=timestamp,
                            value=float(value),
                            metric_name=f"performance_{perf_metric}",
                            source="observatory",
                            quality_score=0.9,  # Slightly lower quality for derived metrics
                            metadata={"performance_data": data["performance"]}
                        )
                        data_points.append(data_point)
            
            # Add data points to storyteller
            if data_points:
                await self.storyteller.add_data_points(data_points)
                logger.debug(f"Added {len(data_points)} data points to storyteller")
            
        except Exception as e:
            logger.error(f"Error processing Observatory data: {e}")
    
    async def get_current_insights(self) -> Dict[str, Any]:
        """Get current data insights for dashboard display."""
        try:
            insights = await self.storyteller.get_current_insights()
            
            # Enhance insights with dashboard-specific formatting
            enhanced_insights = {
                "summary": insights["summary"],
                "patterns": [],
                "recommendations": [],
                "visual_updates": [],
                "timestamp": insights["analysis_timestamp"]
            }
            
            # Process patterns for dashboard display
            for pattern in insights["patterns"]:
                dashboard_pattern = {
                    "id": pattern["id"],
                    "title": self._generate_pattern_title(pattern),
                    "description": pattern["narrative"],
                    "interest_level": pattern["interest_level"],
                    "confidence": pattern["confidence"],
                    "affected_metrics": pattern["affected_metrics"],
                    "visual_suggestion": pattern["visual_suggestion"],
                    "timestamp": pattern["timestamp"]
                }
                enhanced_insights["patterns"].append(dashboard_pattern)
                
                # Generate visual updates for dashboard
                visual_update = self._create_visual_update(pattern)
                if visual_update:
                    enhanced_insights["visual_updates"].append(visual_update)
                
                # Generate recommendations
                recommendation = self._generate_recommendation(pattern)
                if recommendation:
                    enhanced_insights["recommendations"].append(recommendation)
            
            self.active_insights = enhanced_insights
            self.last_update = datetime.now()
            
            return enhanced_insights
            
        except Exception as e:
            logger.error(f"Error getting current insights: {e}")
            return {
                "summary": "Unable to generate insights at this time",
                "patterns": [],
                "recommendations": [],
                "visual_updates": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _register_data_callbacks(self) -> None:
        """Register callbacks to receive data from dashboard engine."""
        # This would integrate with the dashboard engine's data subscription system
        # For now, we'll create a placeholder that can be connected later
        logger.info("Data callbacks registered with dashboard engine")
    
    async def _insight_broadcast_loop(self) -> None:
        """Background loop that broadcasts insights to the dashboard."""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                insights = await self.get_current_insights()
                
                # Broadcast insights via WebSocket if available
                await self._broadcast_insights(insights)
                
            except Exception as e:
                logger.error(f"Error in insight broadcast loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _broadcast_insights(self, insights: Dict[str, Any]) -> None:
        """Broadcast insights to connected dashboard clients."""
        try:
            # Create WebSocket message
            message = {
                "type": "data_insights",
                "data": insights,
                "timestamp": datetime.now().isoformat()
            }
            
            # This would integrate with Observatory's WebSocket system
            # For now, we'll log the insights
            logger.info(f"Broadcasting insights: {insights['summary']}")
            
            # Update dashboard components with visual suggestions
            for visual_update in insights.get("visual_updates", []):
                await self._apply_visual_update(visual_update)
            
        except Exception as e:
            logger.error(f"Error broadcasting insights: {e}")
    
    async def _apply_visual_update(self, visual_update: Dict[str, Any]) -> None:
        """Apply visual updates to dashboard components."""
        try:
            # This would integrate with the dashboard engine's rendering system
            component_id = visual_update.get("component_id")
            if component_id and self.dashboard_engine:
                # Update component engagement level based on pattern interest
                interest_level = visual_update.get("interest_level", "medium")
                engagement_level = self._map_interest_to_engagement(interest_level)
                
                await self.dashboard_engine.update_component_engagement(
                    component_id, engagement_level
                )
            
        except Exception as e:
            logger.error(f"Error applying visual update: {e}")
    
    def _calculate_health_score(self, health_data: Dict[str, Any]) -> float:
        """Calculate a numeric health score from health data."""
        try:
            # Simple health scoring algorithm
            if isinstance(health_data, dict):
                if "status" in health_data:
                    status = health_data["status"].lower()
                    if status == "healthy":
                        return 1.0
                    elif status == "degraded":
                        return 0.7
                    elif status == "unhealthy":
                        return 0.3
                    else:
                        return 0.5
                else:
                    # Calculate based on available metrics
                    scores = []
                    for key, value in health_data.items():
                        if isinstance(value, (int, float)):
                            # Normalize to 0-1 range (assuming higher is better)
                            normalized = min(max(float(value) / 100.0, 0.0), 1.0)
                            scores.append(normalized)
                    
                    return sum(scores) / len(scores) if scores else 0.5
            
            return 0.5  # Default neutral score
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 0.5
    
    def _generate_pattern_title(self, pattern: Dict[str, Any]) -> str:
        """Generate a user-friendly title for a pattern."""
        pattern_type = pattern.get("type", "unknown")
        metrics = pattern.get("affected_metrics", [])
        
        if pattern_type == "trend_increasing":
            return f"📈 {metrics[0]} Trending Up" if metrics else "📈 Upward Trend"
        elif pattern_type == "trend_decreasing":
            return f"📉 {metrics[0]} Trending Down" if metrics else "📉 Downward Trend"
        elif pattern_type == "anomaly_spike":
            return f"⚡ {metrics[0]} Spike Detected" if metrics else "⚡ Anomaly Spike"
        elif pattern_type == "anomaly_drop":
            return f"⚠️ {metrics[0]} Drop Detected" if metrics else "⚠️ Anomaly Drop"
        elif pattern_type == "correlation_positive":
            return f"🔗 {' & '.join(metrics[:2])} Correlated" if len(metrics) >= 2 else "🔗 Positive Correlation"
        elif pattern_type == "correlation_negative":
            return f"🔄 {' & '.join(metrics[:2])} Inversely Related" if len(metrics) >= 2 else "🔄 Negative Correlation"
        else:
            return f"🔍 Pattern in {metrics[0]}" if metrics else "🔍 Data Pattern"
    
    def _create_visual_update(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create visual update instructions for a pattern."""
        try:
            visual_suggestion = pattern.get("visual_suggestion", {})
            affected_metrics = pattern.get("affected_metrics", [])
            
            if not affected_metrics:
                return None
            
            # Map metric names to component IDs (this would be configurable)
            component_mapping = {
                "system_health": "healthTrendChart",
                "performance_response_time": "performanceChart",
                "performance_cpu_usage": "performanceChart",
                "error_rate": "healthTrendChart"
            }
            
            component_id = component_mapping.get(affected_metrics[0])
            if not component_id:
                return None
            
            return {
                "component_id": component_id,
                "animation_type": visual_suggestion.get("animation_type", "highlight"),
                "color": visual_suggestion.get("color", "#3498db"),
                "intensity": visual_suggestion.get("intensity", 0.5),
                "interest_level": pattern.get("interest_level", "medium"),
                "duration": 3000  # 3 seconds
            }
            
        except Exception as e:
            logger.error(f"Error creating visual update: {e}")
            return None
    
    def _generate_recommendation(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate actionable recommendations based on patterns."""
        try:
            pattern_type = pattern.get("type")
            interest_level = pattern.get("interest_level")
            metrics = pattern.get("affected_metrics", [])
            
            if interest_level in ["critical", "high"]:
                if pattern_type == "anomaly_spike":
                    return {
                        "type": "investigation",
                        "priority": "high",
                        "title": "Investigate Anomaly",
                        "description": f"Unusual spike in {metrics[0]} requires investigation",
                        "actions": [
                            "Check system logs for errors",
                            "Review recent deployments",
                            "Monitor for continued anomalies"
                        ]
                    }
                elif pattern_type == "trend_decreasing" and "performance" in metrics[0]:
                    return {
                        "type": "optimization",
                        "priority": "medium",
                        "title": "Performance Optimization",
                        "description": f"Declining {metrics[0]} may need attention",
                        "actions": [
                            "Review system resources",
                            "Check for bottlenecks",
                            "Consider scaling options"
                        ]
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return None
    
    def _map_interest_to_engagement(self, interest_level: str) -> str:
        """Map pattern interest level to dashboard engagement level."""
        mapping = {
            "critical": "immersive",
            "high": "active", 
            "medium": "active",
            "low": "passive"
        }
        return mapping.get(interest_level, "passive")
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Storyteller Integration capabilities."""
        return [
            "data_integration",
            "pattern_broadcasting",
            "visual_updates",
            "insight_generation",
            "recommendation_engine"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Storyteller Integration health status."""
        return {
            "status": "healthy",
            "storyteller_active": self.storyteller is not None,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "active_insights": len(self.active_insights.get("patterns", [])),
            "dashboard_connected": self.dashboard_engine is not None
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Storyteller Integration module information."""
        return {
            "module_id": self.module_id,
            "name": "Storyteller Integration",
            "version": "1.0.0",
            "description": "Integrates Data Storyteller with Observatory dashboard"
        }


# Quick demo function to test the integration
async def demo_storyteller_integration():
    """Demo function to show the storyteller in action."""
    print("🎯 Starting Data Storyteller Demo...")
    
    # Create storyteller
    storyteller = DataStorytellerEngine()
    await storyteller.initialize()
    
    # Generate some sample data
    import random
    from datetime import datetime, timedelta
    
    base_time = datetime.now() - timedelta(hours=1)
    
    # Create trending data
    for i in range(60):
        timestamp = base_time + timedelta(minutes=i)
        
        # CPU usage with upward trend + noise
        cpu_value = 30 + (i * 0.5) + random.gauss(0, 5)
        cpu_point = DataPoint(
            timestamp=timestamp,
            value=max(0, min(100, cpu_value)),
            metric_name="cpu_usage",
            source="demo",
            quality_score=0.95
        )
        await storyteller.add_data_point(cpu_point)
        
        # Response time with some anomalies
        base_response = 200 + random.gauss(0, 20)
        if i in [25, 45]:  # Add anomalies
            base_response *= 3
        
        response_point = DataPoint(
            timestamp=timestamp,
            value=max(0, base_response),
            metric_name="response_time",
            source="demo",
            quality_score=0.9
        )
        await storyteller.add_data_point(response_point)
    
    # Wait for analysis
    await asyncio.sleep(2)
    
    # Get insights
    insights = await storyteller.get_current_insights()
    
    print(f"\n📊 Analysis Results:")
    print(f"Summary: {insights['summary']}")
    print(f"\n🔍 Discovered Patterns:")
    
    for pattern in insights['patterns']:
        print(f"  • {pattern['narrative']}")
        print(f"    Interest: {pattern['interest_level']}, Confidence: {pattern['confidence']:.2f}")
    
    print(f"\n📈 Analyzed {insights['metrics_analyzed']} metrics with {insights['total_data_points']} data points")
    
    return insights


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_storyteller_integration())