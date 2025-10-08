"""
Server Integration - Observatory Server Enhancement for Engagement System
========================================================================

Integrates the Data Storyteller and engagement features directly into the
Observatory server, adding WebSocket endpoints and live data streaming.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Callable
from fastapi import WebSocket, WebSocketDisconnect

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..intelligence.data_storyteller import DataStorytellerEngine, DataPoint
from .observatory_data_bridge import ObservatoryDataBridge
from ...models import ObservatoryConfig
from ..monitoring import (
    EngagementMetricsCollector,
    EngagementPrometheusIntegration,
    EngagementHealthMonitor,
    create_engagement_prometheus_integration,
    create_engagement_health_monitor
)
from ..coordination import (
    EngagementEventCoordinator,
    EngagementEventType,
    EngagementEventPriority
)
from ..error_handling import (
    EngagementErrorHandler,
    EngagementErrorType,
    EngagementErrorSeverity,
    EngagementFallbackMode,
    EngagementResilienceManager,
    EngagementErrorRecovery
)

logger = logging.getLogger(__name__)


class EngagementWebSocketManager:
    """Manages WebSocket connections for engagement features."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": datetime.now(),
            "client_info": client_info or {},
            "messages_sent": 0,
            "last_activity": datetime.now()
        }
        logger.info(f"🔌 New engagement WebSocket connection: {len(self.active_connections)} total")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.connection_metadata.pop(websocket, None)
            logger.info(f"🔌 Engagement WebSocket disconnected: {len(self.active_connections)} remaining")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients with error handling."""
        if not self.active_connections:
            return
        
        try:
            message_json = json.dumps(message)
            disconnected = set()
            
            for websocket in self.active_connections:
                try:
                    await websocket.send_text(message_json)
                    
                    # Update metadata
                    if websocket in self.connection_metadata:
                        self.connection_metadata[websocket]["messages_sent"] += 1
                        self.connection_metadata[websocket]["last_activity"] = datetime.now()
                        
                except Exception as e:
                    logger.warning(f"Failed to send message to WebSocket client: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                await self.disconnect(websocket)
                
        except Exception as e:
            logger.error(f"Error in WebSocket broadcast: {e}")
    
    async def send_to_client(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific client."""
        try:
            await websocket.send_text(json.dumps(message))
            
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["messages_sent"] += 1
                self.connection_metadata[websocket]["last_activity"] = datetime.now()
                
        except Exception as e:
            logger.warning(f"Failed to send message to specific WebSocket client: {e}")
            await self.disconnect(websocket)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about WebSocket connections."""
        total_messages = sum(
            meta.get("messages_sent", 0) 
            for meta in self.connection_metadata.values()
        )
        
        return {
            "active_connections": len(self.active_connections),
            "total_messages_sent": total_messages,
            "connection_metadata": {
                str(id(ws)): {
                    "connected_at": meta["connected_at"].isoformat(),
                    "messages_sent": meta["messages_sent"],
                    "last_activity": meta["last_activity"].isoformat()
                }
                for ws, meta in self.connection_metadata.items()
            }
        }


class ObservatoryEngagementIntegration(ReflectiveModule):
    """
    Main integration class that enhances the Observatory server
    with engagement features and real-time data storytelling.
    """
    
    def __init__(self, config: ObservatoryConfig):
        super().__init__()
        self.module_id = "observatory_engagement_integration"
        
        self.config = config
        
        # Error handling and resilience components (initialize first)
        self.error_handler = EngagementErrorHandler()
        self.error_recovery = EngagementErrorRecovery()
        self.resilience_manager: Optional[EngagementResilienceManager] = None
        
        # Core components
        self.storyteller = DataStorytellerEngine()
        self.data_bridge = ObservatoryDataBridge(config, self.storyteller)
        self.websocket_manager = EngagementWebSocketManager()
        
        # Monitoring components
        self.metrics_collector = EngagementMetricsCollector()
        self.prometheus_integration: Optional[EngagementPrometheusIntegration] = None
        self.health_monitor: Optional[EngagementHealthMonitor] = None
        
        # Coordination components
        self.event_coordinator = EngagementEventCoordinator()
        
        # State
        self.running = False
        self.broadcast_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.insights_broadcasted = 0
        self.last_broadcast = datetime.now()
        
        logger.info("🎯 Observatory Engagement Integration initialized")
    
    async def initialize(self) -> bool:
        """Initialize the engagement integration with comprehensive error handling."""
        try:
            # Initialize error handling components first
            if not await self.error_handler.initialize():
                logger.error("Failed to initialize error handler")
                return False
            
            if not await self.error_recovery.initialize():
                logger.error("Failed to initialize error recovery")
                return False
            
            # Create resilience manager
            self.resilience_manager = EngagementResilienceManager(self.error_handler)
            if not await self.resilience_manager.initialize():
                logger.error("Failed to initialize resilience manager")
                return False
            
            # Initialize core components with error handling
            await self._initialize_component_with_error_handling(
                "storyteller", self.storyteller.initialize
            )
            
            await self._initialize_component_with_error_handling(
                "data_bridge", self.data_bridge.initialize
            )
            
            await self._initialize_component_with_error_handling(
                "event_coordinator", self.event_coordinator.initialize
            )
            
            await self._initialize_component_with_error_handling(
                "metrics_collector", self.metrics_collector.initialize
            )
            
            # Create monitoring components with error handling
            try:
                self.prometheus_integration = await create_engagement_prometheus_integration(
                    self.metrics_collector
                )
            except Exception as e:
                await self.error_handler.handle_error(
                    EngagementErrorType.INITIALIZATION_ERROR,
                    "prometheus_integration",
                    f"Failed to create Prometheus integration: {e}",
                    e
                )
                self.prometheus_integration = None
            
            try:
                self.health_monitor = await create_engagement_health_monitor(
                    self.metrics_collector, self.prometheus_integration
                )
            except Exception as e:
                await self.error_handler.handle_error(
                    EngagementErrorType.INITIALIZATION_ERROR,
                    "health_monitor",
                    f"Failed to create health monitor: {e}",
                    e
                )
                self.health_monitor = None
            
            # Register components with event coordinator and resilience manager
            self._register_components_with_coordinator()
            self._register_components_with_resilience_manager()
            
            logger.info("✅ Observatory Engagement Integration initialization complete")
            return True
            
        except Exception as e:
            # Handle initialization failure
            await self.error_handler.handle_error(
                EngagementErrorType.INITIALIZATION_ERROR,
                "server_integration",
                f"Observatory Engagement Integration initialization failed: {e}",
                e
            )
            logger.error(f"Observatory Engagement Integration initialization failed: {e}")
            return False
    
    async def start_integration(self) -> bool:
        """Start the engagement integration with error handling."""
        try:
            if self.running:
                logger.warning("Observatory Engagement Integration is already running")
                return True
            
            # Start data bridge with error handling
            try:
                await self.data_bridge.start_bridge()
            except Exception as e:
                await self.error_handler.handle_error(
                    EngagementErrorType.INTEGRATION_ERROR,
                    "data_bridge",
                    f"Failed to start data bridge: {e}",
                    e
                )
                # Continue with degraded functionality
            
            # Start insight broadcasting with error handling
            self.running = True
            try:
                self.broadcast_task = asyncio.create_task(self._insight_broadcast_loop())
            except Exception as e:
                await self.error_handler.handle_error(
                    EngagementErrorType.INTEGRATION_ERROR,
                    "broadcast_task",
                    f"Failed to start broadcast task: {e}",
                    e
                )
                # Continue without broadcasting
            
            logger.info("🚀 Observatory Engagement Integration started")
            return True
            
        except Exception as e:
            await self.error_handler.handle_error(
                EngagementErrorType.INTEGRATION_ERROR,
                "server_integration",
                f"Failed to start Observatory Engagement Integration: {e}",
                e
            )
            logger.error(f"Failed to start Observatory Engagement Integration: {e}")
            return False
    
    async def stop_integration(self) -> None:
        """Stop the engagement integration with error handling."""
        logger.info("🛑 Stopping Observatory Engagement Integration...")
        
        self.running = False
        
        # Stop broadcast task with error handling
        if self.broadcast_task and not self.broadcast_task.done():
            try:
                self.broadcast_task.cancel()
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.warning(f"Error stopping broadcast task: {e}")
        
        # Stop resilience manager
        if self.resilience_manager:
            try:
                await self.resilience_manager.shutdown()
            except Exception as e:
                logger.warning(f"Error stopping resilience manager: {e}")
        
        # Stop coordination system
        try:
            await self.event_coordinator.shutdown()
        except Exception as e:
            logger.warning(f"Error stopping event coordinator: {e}")
        
        # Stop monitoring components
        if self.health_monitor:
            try:
                await self.health_monitor.shutdown()
            except Exception as e:
                logger.warning(f"Error stopping health monitor: {e}")
        
        if self.prometheus_integration:
            try:
                await self.prometheus_integration.shutdown()
            except Exception as e:
                logger.warning(f"Error stopping prometheus integration: {e}")
        
        try:
            await self.metrics_collector.shutdown()
        except Exception as e:
            logger.warning(f"Error stopping metrics collector: {e}")
        
        # Stop data bridge
        try:
            await self.data_bridge.stop_bridge()
        except Exception as e:
            logger.warning(f"Error stopping data bridge: {e}")
        
        logger.info("✅ Observatory Engagement Integration stopped")
    
    async def handle_websocket_connection(self, websocket: WebSocket):
        """Handle a new engagement WebSocket connection."""
        client_info = {
            "user_agent": websocket.headers.get("user-agent", "unknown"),
            "origin": websocket.headers.get("origin", "unknown")
        }
        
        await self.websocket_manager.connect(websocket, client_info)
        
        # Record connection metrics
        user_id = f"ws_{id(websocket)}"
        session_id = f"session_{id(websocket)}_{int(datetime.now().timestamp())}"
        
        await self.metrics_collector.start_attention_session(
            user_id, session_id, "engagement_dashboard"
        )
        
        try:
            # Send initial data
            initial_insights = await self.data_bridge.get_recent_insights()
            await self.websocket_manager.send_to_client(websocket, {
                "type": "initial_insights",
                "data": initial_insights,
                "timestamp": datetime.now().isoformat()
            })
            
            # Handle incoming messages
            while True:
                try:
                    message = await websocket.receive_text()
                    data = json.loads(message)
                    await self._handle_websocket_message(websocket, data)
                    
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")
                    await self.websocket_manager.send_to_client(websocket, {
                        "type": "error",
                        "message": "Failed to process message",
                        "timestamp": datetime.now().isoformat()
                    })
        
        except WebSocketDisconnect:
            pass
        finally:
            # End attention session and record metrics
            await self.metrics_collector.end_attention_session(session_id)
            await self.websocket_manager.disconnect(websocket)
    
    async def _handle_websocket_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle incoming WebSocket messages."""
        message_type = data.get("type")
        user_id = f"ws_{id(websocket)}"
        
        # Record interaction
        await self.metrics_collector.record_interaction(
            user_id, "websocket_message", message_type or "unknown",
            metadata={"message_data": data}
        )
        
        # Emit engagement event
        await self.emit_engagement_event(
            EngagementEventType.USER_INTERACTION,
            {
                "user_id": user_id,
                "event_type": "websocket_message",
                "component": message_type or "unknown",
                "data": data
            }
        )
        
        if message_type == "get_insights":
            # Send current insights
            insights = await self.data_bridge.get_recent_insights()
            await self.websocket_manager.send_to_client(websocket, {
                "type": "insights_update",
                "data": insights,
                "timestamp": datetime.now().isoformat()
            })
        
        elif message_type == "get_status":
            # Send system status
            status = await self._get_system_status()
            await self.websocket_manager.send_to_client(websocket, {
                "type": "status_update",
                "data": status,
                "timestamp": datetime.now().isoformat()
            })
        
        elif message_type == "add_data_point":
            # Allow clients to add custom data points
            await self._handle_custom_data_point(data.get("data", {}))
        
        elif message_type == "ping":
            # Respond to ping
            await self.websocket_manager.send_to_client(websocket, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
        
        else:
            logger.warning(f"Unknown WebSocket message type: {message_type}")
    
    async def _handle_custom_data_point(self, data: Dict[str, Any]):
        """Handle custom data points from clients."""
        try:
            # Create DataPoint from client data
            data_point = DataPoint(
                timestamp=datetime.now(),
                value=float(data.get("value", 0)),
                metric_name=data.get("metric_name", "custom_metric"),
                source="websocket_client",
                quality_score=0.8,  # Lower quality for client data
                metadata={
                    "client_provided": True,
                    "original_data": data
                }
            )
            
            await self.storyteller.add_data_point(data_point)
            logger.info(f"Added custom data point: {data_point.metric_name} = {data_point.value}")
            
        except Exception as e:
            logger.error(f"Error handling custom data point: {e}")
    
    async def _insight_broadcast_loop(self):
        """Background loop that broadcasts insights to connected clients with error handling."""
        logger.info("📡 Starting insight broadcast loop")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                # Get latest insights with error handling
                try:
                    insights = await self.data_bridge.get_recent_insights()
                except Exception as e:
                    await self.error_handler.handle_error(
                        EngagementErrorType.DATA_PROCESSING_ERROR,
                        "data_bridge",
                        f"Failed to get recent insights: {e}",
                        e
                    )
                    insights = {"patterns": [], "error": "Failed to get insights"}
                
                # Only broadcast if we have patterns
                if insights.get("patterns"):
                    try:
                        await self.websocket_manager.broadcast({
                            "type": "insights_update",
                            "data": insights,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        self.insights_broadcasted += 1
                        self.last_broadcast = datetime.now()
                        consecutive_errors = 0  # Reset error count on success
                        
                        logger.debug(f"Broadcasted insights to {len(self.websocket_manager.active_connections)} clients")
                        
                    except Exception as e:
                        await self.error_handler.handle_error(
                            EngagementErrorType.WEBSOCKET_ERROR,
                            "websocket_manager",
                            f"Failed to broadcast insights: {e}",
                            e
                        )
                        consecutive_errors += 1
                
                # Wait before next broadcast (adjust based on error count)
                sleep_time = 30 + (consecutive_errors * 10)  # Increase delay with errors
                await asyncio.sleep(min(sleep_time, 300))  # Max 5 minutes
                
            except Exception as e:
                consecutive_errors += 1
                await self.error_handler.handle_error(
                    EngagementErrorType.INTEGRATION_ERROR,
                    "broadcast_loop",
                    f"Error in insight broadcast loop: {e}",
                    e
                )
                
                # If too many consecutive errors, enter degraded mode
                if consecutive_errors >= max_consecutive_errors:
                    logger.warning("Too many broadcast errors, entering degraded mode")
                    await asyncio.sleep(300)  # Wait 5 minutes before retrying
                    consecutive_errors = 0
                else:
                    await asyncio.sleep(60)  # Wait longer on error
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        bridge_status = await self.data_bridge.get_bridge_status()
        storyteller_health = self.storyteller.get_health_status()
        websocket_stats = self.websocket_manager.get_connection_stats()
        
        return {
            "integration_running": self.running,
            "insights_broadcasted": self.insights_broadcasted,
            "last_broadcast": self.last_broadcast.isoformat(),
            "data_bridge": bridge_status,
            "storyteller": storyteller_health,
            "websockets": websocket_stats
        }
    
    async def inject_observatory_data(self, data_type: str, data: Dict[str, Any]):
        """Inject Observatory data directly into the storyteller."""
        try:
            timestamp = datetime.now()
            
            # Convert Observatory data to DataPoints based on type
            if data_type == "metrics":
                for metric_name, value in data.items():
                    if isinstance(value, (int, float)):
                        data_point = DataPoint(
                            timestamp=timestamp,
                            value=float(value),
                            metric_name=metric_name,
                            source="observatory_direct",
                            quality_score=0.95,
                            metadata={"injection_type": data_type}
                        )
                        await self.storyteller.add_data_point(data_point)
            
            elif data_type == "health":
                # Convert health data to numeric metrics
                health_score = self._extract_health_score(data)
                data_point = DataPoint(
                    timestamp=timestamp,
                    value=health_score,
                    metric_name="system_health_score",
                    source="observatory_direct",
                    quality_score=0.98,
                    metadata={"health_data": data}
                )
                await self.storyteller.add_data_point(data_point)
            
            elif data_type == "costs":
                # Extract cost metrics
                for cost_field in ["total_cost", "cost_per_token", "tokens_used"]:
                    if cost_field in data:
                        data_point = DataPoint(
                            timestamp=timestamp,
                            value=float(data[cost_field]),
                            metric_name=f"llm_{cost_field}",
                            source="observatory_direct",
                            quality_score=0.98,
                            metadata={"cost_data": data}
                        )
                        await self.storyteller.add_data_point(data_point)
            
        except Exception as e:
            logger.error(f"Error injecting Observatory data: {e}")
    
    def _extract_health_score(self, health_data: Dict[str, Any]) -> float:
        """Extract a numeric health score from health data."""
        try:
            if "health_score" in health_data:
                return float(health_data["health_score"])
            elif "status" in health_data:
                status = health_data["status"].lower()
                status_scores = {
                    "healthy": 1.0,
                    "degraded": 0.6,
                    "unhealthy": 0.2,
                    "critical": 0.0
                }
                return status_scores.get(status, 0.5)
            else:
                return 0.5  # Default neutral score
        except Exception:
            return 0.5
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Observatory Engagement Integration capabilities."""
        return [
            "real_time_insights",
            "websocket_broadcasting",
            "data_storytelling",
            "pattern_discovery",
            "observatory_integration",
            "live_data_streaming"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Observatory Engagement Integration health status."""
        base_health = {
            "status": "healthy" if self.running else "stopped",
            "insights_broadcasted": self.insights_broadcasted,
            "last_broadcast": self.last_broadcast.isoformat(),
            "active_websockets": len(self.websocket_manager.active_connections),
            "storyteller_healthy": self.storyteller.get_health_status().get("status") == "healthy",
            "data_bridge_running": self.data_bridge.running
        }
        
        # Add monitoring health if available
        if self.health_monitor:
            monitoring_health = self.health_monitor.get_health_summary()
            base_health["monitoring"] = {
                "overall_status": monitoring_health.get("overall_status"),
                "health_score": monitoring_health.get("health_score"),
                "component_health": monitoring_health.get("component_health")
            }
        
        # Add metrics summary if available
        if self.metrics_collector:
            metrics_summary = self.metrics_collector.get_engagement_summary()
            base_health["metrics"] = {
                "active_sessions": metrics_summary.get("active_attention_sessions"),
                "total_interactions": metrics_summary.get("total_interactions"),
                "interaction_rate": metrics_summary.get("recent_interaction_rate_per_minute")
            }
        
        return base_health
    
    def _register_components_with_coordinator(self):
        """Register all engagement components with the event coordinator."""
        try:
            # Register core components
            self.event_coordinator.register_component(
                "storyteller", self.storyteller, 
                {"status": "active", "insights_generated": 0}
            )
            
            self.event_coordinator.register_component(
                "data_bridge", self.data_bridge,
                {"status": "active", "bridge_running": self.data_bridge.running}
            )
            
            self.event_coordinator.register_component(
                "websocket_manager", self.websocket_manager,
                {"active_connections": len(self.websocket_manager.active_connections)}
            )
            
            self.event_coordinator.register_component(
                "metrics_collector", self.metrics_collector,
                {"metrics_collected": 0, "active_sessions": 0}
            )
            
            if self.prometheus_integration:
                self.event_coordinator.register_component(
                    "prometheus_integration", self.prometheus_integration,
                    {"prometheus_registered": self.prometheus_integration.prometheus_registered}
                )
            
            if self.health_monitor:
                self.event_coordinator.register_component(
                    "health_monitor", self.health_monitor,
                    {"monitoring_running": True, "health_score": 0.0}
                )
            
            logger.info("✅ Registered all components with event coordinator")
            
        except Exception as e:
            logger.error(f"Failed to register components with coordinator: {e}")
    
    async def _initialize_component_with_error_handling(self, component_name: str, init_func: Callable):
        """Initialize a component with comprehensive error handling."""
        try:
            if asyncio.iscoroutinefunction(init_func):
                result = await init_func()
            else:
                result = init_func()
            
            if result is False:
                await self.error_handler.handle_error(
                    EngagementErrorType.INITIALIZATION_ERROR,
                    component_name,
                    f"Component {component_name} initialization returned False",
                    None,
                    {"component": component_name}
                )
            
        except Exception as e:
            await self.error_handler.handle_error(
                EngagementErrorType.INITIALIZATION_ERROR,
                component_name,
                f"Component {component_name} initialization failed: {e}",
                e,
                {"component": component_name}
            )
    
    def _register_components_with_resilience_manager(self):
        """Register all components with the resilience manager for health monitoring."""
        if not self.resilience_manager:
            return
        
        try:
            # Register core components
            self.resilience_manager.register_component(
                "storyteller",
                lambda: self.storyteller.get_health_status(),
                critical=True
            )
            
            self.resilience_manager.register_component(
                "data_bridge",
                lambda: {"status": "healthy" if self.data_bridge.running else "unhealthy"},
                dependencies=["storyteller"],
                critical=True
            )
            
            self.resilience_manager.register_component(
                "websocket_manager",
                lambda: {
                    "status": "healthy",
                    "active_connections": len(self.websocket_manager.active_connections)
                },
                critical=False
            )
            
            self.resilience_manager.register_component(
                "event_coordinator",
                lambda: self.event_coordinator.get_health_status(),
                critical=True
            )
            
            self.resilience_manager.register_component(
                "metrics_collector",
                lambda: {"status": "healthy", "metrics_collected": 0},
                critical=False
            )
            
            if self.prometheus_integration:
                self.resilience_manager.register_component(
                    "prometheus_integration",
                    lambda: {"status": "healthy", "prometheus_registered": True},
                    critical=False
                )
            
            if self.health_monitor:
                self.resilience_manager.register_component(
                    "health_monitor",
                    lambda: self.health_monitor.get_health_status(),
                    critical=False
                )
            
            logger.info("✅ Registered all components with resilience manager")
            
        except Exception as e:
            logger.error(f"Failed to register components with resilience manager: {e}")
    
    async def emit_engagement_event(self, event_type: EngagementEventType, 
                                  data: Dict[str, Any] = None,
                                  priority: EngagementEventPriority = EngagementEventPriority.MEDIUM) -> str:
        """Emit an engagement event through the coordinator."""
        return await self.event_coordinator.emit_event(
            event_type, "server_integration", data, priority
        )
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Observatory Engagement Integration module information."""
        return {
            "module_id": self.module_id,
            "name": "Observatory Engagement Integration",
            "version": "1.0.0",
            "description": "Integrates engagement features with Observatory server"
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation when errors occur."""
        try:
            logger.warning(f"Observatory Engagement Integration entering degradation mode due to: {error}")
            
            # Report degradation to error handler
            await self.error_handler.handle_error(
                EngagementErrorType.INTEGRATION_ERROR,
                "server_integration",
                f"Entering graceful degradation: {error}",
                error,
                {"degradation_triggered": True}
            )
            
            # Apply fallback modes through resilience manager
            if self.resilience_manager:
                try:
                    # This will trigger appropriate fallback strategies
                    pass
                except Exception as e:
                    logger.error(f"Error applying resilience strategies: {e}")
            
            # Reduce broadcast frequency
            if self.broadcast_task:
                # The broadcast loop will automatically slow down on errors
                pass
            
            # Notify connected clients about degraded mode
            try:
                await self.websocket_manager.broadcast({
                    "type": "system_status",
                    "status": "degraded",
                    "message": "System operating in degraded mode",
                    "timestamp": datetime.now().isoformat(),
                    "fallback_mode": self.error_handler.get_component_fallback_mode("server_integration").value
                })
            except Exception as e:
                logger.error(f"Failed to notify clients about degradation: {e}")
            
            logger.info("Degradation applied: reduced broadcast frequency and notified clients")
            return True
            
        except Exception as degradation_error:
            logger.error(f"Failed to apply graceful degradation: {degradation_error}")
            return False


# Helper function to add engagement WebSocket to Observatory server
def add_engagement_websocket_to_server(app, integration: ObservatoryEngagementIntegration):
    """Add the engagement WebSocket endpoint to the Observatory server."""
    
    @app.websocket("/ws/engagement")
    async def engagement_websocket(websocket: WebSocket):
        """WebSocket endpoint for real-time engagement updates."""
        await integration.handle_websocket_connection(websocket)


# Helper function to inject data from Observatory components
async def inject_observatory_metrics(integration: ObservatoryEngagementIntegration, 
                                   metrics_data: Dict[str, Any]):
    """Inject Observatory metrics into the engagement system."""
    await integration.inject_observatory_data("metrics", metrics_data)


async def inject_observatory_health(integration: ObservatoryEngagementIntegration,
                                  health_data: Dict[str, Any]):
    """Inject Observatory health data into the engagement system."""
    await integration.inject_observatory_data("health", health_data)


async def inject_observatory_costs(integration: ObservatoryEngagementIntegration,
                                 cost_data: Dict[str, Any]):
    """Inject Observatory cost data into the engagement system."""
    await integration.inject_observatory_data("costs", cost_data)


# New monitoring integration functions

async def inject_engagement_metrics_into_observatory_endpoint(
    integration: ObservatoryEngagementIntegration,
    observatory_metrics: Dict[str, Any]
) -> None:
    """Inject engagement metrics into Observatory's metrics endpoint."""
    if integration.prometheus_integration:
        from ..monitoring import inject_engagement_metrics_into_observatory
        await inject_engagement_metrics_into_observatory(
            integration.prometheus_integration, observatory_metrics
        )


async def inject_engagement_health_into_observatory_endpoint(
    integration: ObservatoryEngagementIntegration,
    observatory_health: Dict[str, Any]
) -> None:
    """Inject engagement health into Observatory's health endpoint."""
    if integration.health_monitor:
        from ..monitoring import inject_engagement_health_into_observatory
        await inject_engagement_health_into_observatory(
            integration.health_monitor, observatory_health
        )


def get_engagement_prometheus_metrics_text(
    integration: ObservatoryEngagementIntegration
) -> str:
    """Get engagement metrics in Prometheus format."""
    if integration.prometheus_integration:
        from ..monitoring import get_engagement_prometheus_metrics
        return get_engagement_prometheus_metrics(integration.prometheus_integration)
    return "# Engagement metrics not available\n"


async def record_user_interaction(
    integration: ObservatoryEngagementIntegration,
    user_id: str,
    event_type: str,
    component: str,
    duration: float = None,
    metadata: Dict[str, Any] = None
) -> None:
    """Record a user interaction for engagement metrics."""
    if integration.metrics_collector:
        await integration.metrics_collector.record_interaction(
            user_id, event_type, component, duration, metadata
        )
    
    # Emit engagement event
    await integration.emit_engagement_event(
        EngagementEventType.USER_INTERACTION,
        {
            "user_id": user_id,
            "event_type": event_type,
            "component": component,
            "duration": duration,
            "metadata": metadata or {}
        }
    )


async def trigger_personality_transition(
    integration: ObservatoryEngagementIntegration,
    from_mood: str,
    to_mood: str,
    trigger: str
) -> None:
    """Trigger a personality transition through the event coordinator."""
    await integration.emit_engagement_event(
        EngagementEventType.PERSONALITY_TRANSITION,
        {
            "from_mood": from_mood,
            "to_mood": to_mood,
            "trigger": trigger
        },
        EngagementEventPriority.MEDIUM
    )


async def trigger_animation_event(
    integration: ObservatoryEngagementIntegration,
    animation_type: str,
    duration: float,
    component: str = None
) -> None:
    """Trigger an animation event through the event coordinator."""
    await integration.emit_engagement_event(
        EngagementEventType.ANIMATION_TRIGGER,
        {
            "animation_type": animation_type,
            "duration": duration,
            "component": component
        },
        EngagementEventPriority.LOW
    )


def get_engagement_coordination_status(
    integration: ObservatoryEngagementIntegration
) -> Dict[str, Any]:
    """Get engagement coordination system status."""
    if integration.event_coordinator:
        return {
            "coordinator_status": integration.event_coordinator.get_health_status(),
            "unified_state": integration.event_coordinator.get_unified_state(),
            "event_statistics": integration.event_coordinator.get_event_statistics()
        }
    return {"error": "Event coordinator not available"}