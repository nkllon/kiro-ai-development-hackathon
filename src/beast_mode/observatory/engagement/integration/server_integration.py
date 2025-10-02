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
from typing import Dict, List, Any, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..intelligence.data_storyteller import DataStorytellerEngine, DataPoint
from .observatory_data_bridge import ObservatoryDataBridge
from ...models import ObservatoryConfig

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
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
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
        
        # Core components
        self.storyteller = DataStorytellerEngine()
        self.data_bridge = ObservatoryDataBridge(config, self.storyteller)
        self.websocket_manager = EngagementWebSocketManager()
        
        # State
        self.running = False
        self.broadcast_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.insights_broadcasted = 0
        self.last_broadcast = datetime.now()
        
        logger.info("🎯 Observatory Engagement Integration initialized")
    
    async def initialize(self) -> bool:
        """Initialize the engagement integration."""
        try:
            # Initialize storyteller
            await self.storyteller.initialize()
            
            # Initialize data bridge
            await self.data_bridge.initialize()
            
            logger.info("✅ Observatory Engagement Integration initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Observatory Engagement Integration initialization failed: {e}")
            return False
    
    async def start_integration(self) -> bool:
        """Start the engagement integration."""
        try:
            if self.running:
                logger.warning("Observatory Engagement Integration is already running")
                return True
            
            # Start data bridge
            await self.data_bridge.start_bridge()
            
            # Start insight broadcasting
            self.running = True
            self.broadcast_task = asyncio.create_task(self._insight_broadcast_loop())
            
            logger.info("🚀 Observatory Engagement Integration started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Observatory Engagement Integration: {e}")
            return False
    
    async def stop_integration(self) -> None:
        """Stop the engagement integration."""
        logger.info("🛑 Stopping Observatory Engagement Integration...")
        
        self.running = False
        
        # Stop broadcast task
        if self.broadcast_task and not self.broadcast_task.done():
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
        
        # Stop data bridge
        await self.data_bridge.stop_bridge()
        
        logger.info("✅ Observatory Engagement Integration stopped")
    
    async def handle_websocket_connection(self, websocket: WebSocket):
        """Handle a new engagement WebSocket connection."""
        await self.websocket_manager.connect(websocket, {
            "user_agent": websocket.headers.get("user-agent", "unknown"),
            "origin": websocket.headers.get("origin", "unknown")
        })
        
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
            await self.websocket_manager.disconnect(websocket)
    
    async def _handle_websocket_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle incoming WebSocket messages."""
        message_type = data.get("type")
        
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
        """Background loop that broadcasts insights to connected clients."""
        logger.info("📡 Starting insight broadcast loop")
        
        while self.running:
            try:
                # Get latest insights
                insights = await self.data_bridge.get_recent_insights()
                
                # Only broadcast if we have patterns
                if insights.get("patterns"):
                    await self.websocket_manager.broadcast({
                        "type": "insights_update",
                        "data": insights,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    self.insights_broadcasted += 1
                    self.last_broadcast = datetime.now()
                    
                    logger.debug(f"Broadcasted insights to {len(self.websocket_manager.active_connections)} clients")
                
                # Wait before next broadcast
                await asyncio.sleep(30)  # Broadcast every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in insight broadcast loop: {e}")
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
        return {
            "status": "healthy" if self.running else "stopped",
            "insights_broadcasted": self.insights_broadcasted,
            "last_broadcast": self.last_broadcast.isoformat(),
            "active_websockets": len(self.websocket_manager.active_connections),
            "storyteller_healthy": self.storyteller.get_health_status().get("status") == "healthy",
            "data_bridge_running": self.data_bridge.running
        }
    
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
            
            # Reduce broadcast frequency
            if self.broadcast_task:
                # The broadcast loop will automatically slow down on errors
                pass
            
            # Notify connected clients about degraded mode
            await self.websocket_manager.broadcast({
                "type": "system_status",
                "status": "degraded",
                "message": "System operating in degraded mode",
                "timestamp": datetime.now().isoformat()
            })
            
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