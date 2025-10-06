"""
Dashboard Engine - Real-time Data Integration and Rendering
===========================================================

The Dashboard Engine provides the core functionality for real-time data integration,
contextual information layering, and dynamic dashboard rendering with seamless
integration to the existing Observatory WebSocket infrastructure.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .interfaces import (
    IDashboardRenderer, 
    IDataSubscriber, 
    EngagementContext, 
    EngagementLevel
)

logger = logging.getLogger(__name__)


@dataclass
class DashboardComponent:
    """Represents a dashboard component with engagement capabilities."""
    component_id: str
    component_type: str
    data_sources: List[str]
    engagement_level: EngagementLevel = EngagementLevel.PASSIVE
    last_updated: datetime = field(default_factory=datetime.now)
    interaction_count: int = 0
    context_layers: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataStream:
    """Represents a real-time data stream."""
    stream_id: str
    source: str
    update_frequency: float  # Hz
    last_update: datetime = field(default_factory=datetime.now)
    subscribers: List[Callable] = field(default_factory=list)
    data_buffer: List[Dict[str, Any]] = field(default_factory=list)


class DashboardRenderer(IDashboardRenderer):
    """Implementation of dashboard rendering with engagement features."""
    
    def __init__(self):
        self.active_components: Dict[str, DashboardComponent] = {}
        self.render_queue: asyncio.Queue = asyncio.Queue()
        self.theme_config: Dict[str, Any] = {}
        
    async def render_component(self, component_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Render a dashboard component with engagement enhancements."""
        try:
            component = self.active_components.get(component_id)
            if not component:
                logger.warning(f"Component {component_id} not found")
                return {"status": "error", "message": "Component not found"}
            
            # Apply contextual information layering
            enhanced_data = await self._apply_context_layers(component, data)
            
            # Generate engagement-aware rendering
            render_config = await self._generate_render_config(component, enhanced_data)
            
            # Update component state
            component.last_updated = datetime.now()
            component.interaction_count += 1
            
            return {
                "status": "success",
                "component_id": component_id,
                "render_config": render_config,
                "engagement_level": component.engagement_level.value,
                "context_layers": len(component.context_layers)
            }
            
        except Exception as e:
            logger.error(f"Error rendering component {component_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def update_layout(self, layout_config: Dict[str, Any]) -> bool:
        """Update dashboard layout with engagement considerations."""
        try:
            # Validate layout configuration
            if not self._validate_layout_config(layout_config):
                return False
            
            # Apply engagement-aware layout optimizations
            optimized_config = await self._optimize_layout_for_engagement(layout_config)
            
            # Update active components
            for component_id, config in optimized_config.get("components", {}).items():
                if component_id in self.active_components:
                    component = self.active_components[component_id]
                    component.engagement_level = EngagementLevel(
                        config.get("engagement_level", "passive")
                    )
            
            logger.info(f"Layout updated with {len(optimized_config.get('components', {}))} components")
            return True
            
        except Exception as e:
            logger.error(f"Error updating layout: {e}")
            return False
    
    async def apply_theme(self, theme_config: Dict[str, Any]) -> bool:
        """Apply visual theme with personality-driven adaptations."""
        try:
            self.theme_config = theme_config
            
            # Apply theme to all active components
            for component in self.active_components.values():
                await self._apply_theme_to_component(component, theme_config)
            
            logger.info(f"Theme applied: {theme_config.get('name', 'unnamed')}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying theme: {e}")
            return False
    
    async def _apply_context_layers(self, component: DashboardComponent, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply contextual information layers for progressive disclosure."""
        enhanced_data = data.copy()
        
        # Add engagement context
        enhanced_data["engagement_context"] = {
            "level": component.engagement_level.value,
            "interaction_count": component.interaction_count,
            "last_updated": component.last_updated.isoformat()
        }
        
        # Add contextual layers based on engagement level
        if component.engagement_level in [EngagementLevel.ACTIVE, EngagementLevel.IMMERSIVE]:
            enhanced_data["detailed_context"] = component.context_layers
        
        return enhanced_data
    
    async def _generate_render_config(self, component: DashboardComponent, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate engagement-aware rendering configuration."""
        base_config = {
            "component_type": component.component_type,
            "data": data,
            "theme": self.theme_config
        }
        
        # Add engagement-specific rendering options
        if component.engagement_level == EngagementLevel.IMMERSIVE:
            base_config["animations"] = {"enabled": True, "intensity": "high"}
            base_config["interactions"] = {"hover_effects": True, "click_handlers": True}
        elif component.engagement_level == EngagementLevel.ACTIVE:
            base_config["animations"] = {"enabled": True, "intensity": "medium"}
            base_config["interactions"] = {"hover_effects": True}
        
        return base_config
    
    def _validate_layout_config(self, config: Dict[str, Any]) -> bool:
        """Validate layout configuration."""
        required_fields = ["components", "layout_type"]
        return all(field in config for field in required_fields)
    
    async def _optimize_layout_for_engagement(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize layout for better engagement."""
        optimized = config.copy()
        
        # Add engagement-aware positioning
        components = optimized.get("components", {})
        for component_id, component_config in components.items():
            # Prioritize high-engagement components
            if component_config.get("engagement_level") == "immersive":
                component_config["priority"] = "high"
                component_config["position"] = "prominent"
        
        return optimized
    
    async def _apply_theme_to_component(self, component: DashboardComponent, theme: Dict[str, Any]) -> None:
        """Apply theme to individual component."""
        # Store theme preferences in component context
        component.context_layers["theme"] = {
            "name": theme.get("name"),
            "colors": theme.get("colors", {}),
            "typography": theme.get("typography", {}),
            "applied_at": datetime.now().isoformat()
        }


class DataSubscriber(IDataSubscriber):
    """Implementation of real-time data subscription with Observatory integration."""
    
    def __init__(self):
        self.active_streams: Dict[str, DataStream] = {}
        self.observatory_client = None  # Will be injected
        
    async def subscribe_to_data_stream(self, stream_id: str, callback: Callable) -> bool:
        """Subscribe to Observatory data stream."""
        try:
            if stream_id not in self.active_streams:
                # Create new data stream
                self.active_streams[stream_id] = DataStream(
                    stream_id=stream_id,
                    source="observatory",
                    update_frequency=1.0  # 1 Hz default
                )
            
            stream = self.active_streams[stream_id]
            if callback not in stream.subscribers:
                stream.subscribers.append(callback)
            
            logger.info(f"Subscribed to stream {stream_id}, {len(stream.subscribers)} subscribers")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to stream {stream_id}: {e}")
            return False
    
    async def unsubscribe_from_stream(self, stream_id: str) -> bool:
        """Unsubscribe from data stream."""
        try:
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
                logger.info(f"Unsubscribed from stream {stream_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error unsubscribing from stream {stream_id}: {e}")
            return False
    
    async def get_latest_data(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get latest data from stream."""
        try:
            stream = self.active_streams.get(stream_id)
            if stream and stream.data_buffer:
                return stream.data_buffer[-1]
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest data from stream {stream_id}: {e}")
            return None


class DashboardEngine(ReflectiveModule):
    """
    Main Dashboard Engine that orchestrates real-time data integration
    and contextual information layering for engaging dashboard experiences.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "dashboard_engine"
        
        # Core components
        self.renderer = DashboardRenderer()
        self.data_subscriber = DataSubscriber()
        
        # State management
        self.active_components: Dict[str, DashboardComponent] = {}
        self.engagement_contexts: Dict[str, EngagementContext] = {}
        
        # Integration with Observatory
        self.observatory_integration = None
        
        logger.info("Dashboard Engine initialized")
    
    async def initialize(self, observatory_client=None) -> bool:
        """Initialize the Dashboard Engine with Observatory integration."""
        try:
            if observatory_client:
                self.data_subscriber.observatory_client = observatory_client
                logger.info("Observatory integration established")
            
            # Register default data streams
            await self._register_default_streams()
            
            logger.info("Dashboard Engine initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Dashboard Engine initialization failed: {e}")
            return False
    
    async def register_component(self, component_config: Dict[str, Any]) -> str:
        """Register a new dashboard component."""
        try:
            component = DashboardComponent(
                component_id=component_config["component_id"],
                component_type=component_config["component_type"],
                data_sources=component_config.get("data_sources", []),
                engagement_level=EngagementLevel(
                    component_config.get("engagement_level", "passive")
                )
            )
            
            self.active_components[component.component_id] = component
            self.renderer.active_components[component.component_id] = component
            
            # Subscribe to required data streams
            for source in component.data_sources:
                await self.data_subscriber.subscribe_to_data_stream(
                    source, 
                    self._create_data_callback(component.component_id)
                )
            
            logger.info(f"Component registered: {component.component_id}")
            return component.component_id
            
        except Exception as e:
            logger.error(f"Error registering component: {e}")
            raise
    
    async def update_component_engagement(self, component_id: str, level: EngagementLevel) -> bool:
        """Update component engagement level."""
        try:
            if component_id in self.active_components:
                self.active_components[component_id].engagement_level = level
                logger.info(f"Component {component_id} engagement updated to {level.value}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating component engagement: {e}")
            return False
    
    async def get_engagement_analytics(self) -> Dict[str, Any]:
        """Get engagement analytics for all components."""
        try:
            analytics = {
                "total_components": len(self.active_components),
                "engagement_distribution": {},
                "interaction_stats": {},
                "performance_metrics": await self._get_performance_metrics()
            }
            
            # Calculate engagement distribution
            for level in EngagementLevel:
                count = sum(1 for c in self.active_components.values() 
                           if c.engagement_level == level)
                analytics["engagement_distribution"][level.value] = count
            
            # Calculate interaction stats
            total_interactions = sum(c.interaction_count for c in self.active_components.values())
            analytics["interaction_stats"] = {
                "total_interactions": total_interactions,
                "average_per_component": total_interactions / len(self.active_components) if self.active_components else 0
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting engagement analytics: {e}")
            return {}
    
    def _create_data_callback(self, component_id: str) -> Callable:
        """Create data callback for component updates."""
        async def callback(data: Dict[str, Any]):
            try:
                # Render component with new data
                result = await self.renderer.render_component(component_id, data)
                if result["status"] == "success":
                    # Broadcast update via WebSocket if available
                    await self._broadcast_component_update(component_id, result)
            except Exception as e:
                logger.error(f"Error in data callback for {component_id}: {e}")
        
        return callback
    
    async def _register_default_streams(self) -> None:
        """Register default Observatory data streams."""
        default_streams = [
            "observatory_metrics",
            "system_health", 
            "emoji_rain_events",
            "user_interactions"
        ]
        
        for stream_id in default_streams:
            await self.data_subscriber.subscribe_to_data_stream(
                stream_id,
                self._create_default_callback(stream_id)
            )
    
    def _create_default_callback(self, stream_id: str) -> Callable:
        """Create default callback for data streams."""
        async def callback(data: Dict[str, Any]):
            logger.debug(f"Received data from {stream_id}: {len(str(data))} bytes")
        
        return callback
    
    async def _broadcast_component_update(self, component_id: str, update_data: Dict[str, Any]) -> None:
        """Broadcast component update via WebSocket."""
        try:
            # This would integrate with Observatory's WebSocket system
            message = {
                "type": "dashboard_component_update",
                "component_id": component_id,
                "data": update_data,
                "timestamp": datetime.now().isoformat()
            }
            
            # TODO: Integrate with Observatory WebSocket handler
            logger.debug(f"Broadcasting update for component {component_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting component update: {e}")
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get Dashboard Engine performance metrics."""
        return {
            "active_components": len(self.active_components),
            "active_streams": len(self.data_subscriber.active_streams),
            "render_queue_size": self.renderer.render_queue.qsize(),
            "memory_usage": "N/A",  # TODO: Implement memory tracking
            "cpu_usage": "N/A"      # TODO: Implement CPU tracking
        }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Dashboard Engine capabilities."""
        return [
            "real_time_rendering",
            "contextual_layering", 
            "engagement_tracking",
            "observatory_integration",
            "performance_monitoring"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Dashboard Engine health status."""
        return {
            "status": "healthy",
            "active_components": len(self.active_components),
            "active_streams": len(self.data_subscriber.active_streams),
            "observatory_connected": self.data_subscriber.observatory_client is not None
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Dashboard Engine module information."""
        return {
            "module_id": self.module_id,
            "name": "Dashboard Engine",
            "version": "1.0.0",
            "description": "Real-time data integration and contextual dashboard rendering"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation when issues occur."""
        try:
            # Disable advanced features and fall back to basic functionality
            degradation_actions = []
            
            # Reduce engagement levels
            for component in self.active_components.values():
                if component.engagement_level != EngagementLevel.PASSIVE:
                    component.engagement_level = EngagementLevel.PASSIVE
                    degradation_actions.append(f"Reduced {component.component_id} to passive mode")
            
            # Clear complex context layers
            for component in self.active_components.values():
                if component.context_layers:
                    component.context_layers.clear()
                    degradation_actions.append(f"Cleared context layers for {component.component_id}")
            
            return {
                "status": "degraded",
                "actions_taken": degradation_actions,
                "functionality_level": "basic_rendering_only",
                "recovery_possible": True
            }
        except Exception as e:
            return {
                "status": "degradation_failed",
                "error": str(e),
                "functionality_level": "unknown",
                "recovery_possible": False
            }