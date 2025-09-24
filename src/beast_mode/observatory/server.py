"""
Observatory FastAPI Server - The web server that makes emoji rain accessible to the world.

This module provides a production-ready FastAPI server with WebSocket support,
real-time emoji rain streaming, and comprehensive API endpoints.
"""

import asyncio
import json
import logging
import signal
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .emoji_rain import EmojiRainEngine, EmojiRainWebSocketHandler
from .core import ObservatoryCoreEngine
from .models import (
    ObservatoryConfig,
    CoordinationEvent,
    CoordinationEventType,
    Achievement,
)
from .config import load_observatory_config


logger = logging.getLogger(__name__)


class ObservatoryServer:
    """Production-ready FastAPI server for the Beast Mode Coordination Observatory."""
    
    def __init__(self, config: ObservatoryConfig):
        self.config = config
        self.emoji_engine = EmojiRainEngine()
        self.observatory_core = ObservatoryCoreEngine(config)
        self.emoji_ws_handler = EmojiRainWebSocketHandler(self.emoji_engine)
        
        # Create FastAPI app with lifespan
        self.app = FastAPI(
            title=config.web_interface_config.title,
            description="Real-time coordination monitoring with delightful emoji rain",
            version="1.0.0",
            lifespan=self.lifespan
        )
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        self._setup_websockets()
        self._setup_static_files()
        
        logger.info(f"🌐 Observatory Server initialized on port {config.websocket_config.port}")
    
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manage server lifespan - startup and shutdown."""
        # Startup
        logger.info("🚀 Starting Observatory Server...")
        
        # Start Observatory core
        await self.observatory_core.start_observatory()
        
        # Start emoji rain engine
        await self.emoji_engine.start_animation_loop()
        
        logger.info("✅ Observatory Server started successfully")
        
        yield
        
        # Shutdown
        logger.info("🛑 Shutting down Observatory Server...")
        
        # Stop emoji rain engine
        await self.emoji_engine.stop_animation_loop()
        
        # Stop Observatory core
        await self.observatory_core.stop_observatory()
        
        logger.info("✅ Observatory Server stopped gracefully")
    
    def _setup_middleware(self):
        """Setup FastAPI middleware."""
        # CORS middleware for cross-origin requests
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup HTTP routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        @self.app.head("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Serve the main Observatory dashboard."""
            templates_dir = Path(__file__).parent / "templates"
            templates = Jinja2Templates(directory=str(templates_dir))
            
            return templates.TemplateResponse(request, "dashboard.html", {
                "title": self.config.web_interface_config.title,
                "theme": self.config.web_interface_config.theme,
                "refresh_rate": self.config.web_interface_config.refresh_rate_ms,
                "emoji_rain_enabled": self.config.gamification_config.emoji_rain_enabled
            })
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            observatory_health = self.observatory_core.get_health_status()
            emoji_stats = self.emoji_engine.get_performance_stats()
            
            return {
                "status": "healthy",
                "timestamp": observatory_health.last_check.isoformat(),
                "observatory": {
                    "status": observatory_health.status.value,
                    "health_score": observatory_health.health_score,
                    "uptime_seconds": observatory_health.uptime_seconds
                },
                "emoji_rain": {
                    "active": emoji_stats["animation_running"],
                    "active_effects": emoji_stats["active_effects"],
                    "total_particles": emoji_stats["total_particles"],
                    "connected_clients": len(self.emoji_ws_handler.connected_clients)
                }
            }
        
        @self.app.get("/api/observatory/status")
        async def observatory_status():
            """Get Observatory status and metrics."""
            health = self.observatory_core.get_health_status()
            metrics = await self.observatory_core.get_metrics()
            module_info = self.observatory_core.get_module_info()
            
            return {
                "health": {
                    "status": health.status.value,
                    "health_score": health.health_score,
                    "uptime_seconds": health.uptime_seconds,
                    "error_count": health.error_count,
                    "warning_count": health.warning_count,
                    "issues": health.issues
                },
                "metrics": metrics,
                "module_info": module_info
            }
        
        @self.app.get("/api/emoji-rain/stats")
        async def emoji_rain_stats():
            """Get emoji rain performance statistics."""
            return self.emoji_engine.get_performance_stats()
        
        @self.app.get("/api/emoji-rain/effects")
        async def active_effects():
            """Get currently active emoji rain effects."""
            return self.emoji_engine.get_active_effects()
        
        @self.app.post("/api/emoji-rain/trigger")
        async def trigger_emoji_rain(event_data: Dict[str, Any]):
            """Manually trigger emoji rain for testing."""
            try:
                event_type_name = event_data.get("event_type", "TASK_COMPLETED")
                
                # Validate event type
                try:
                    event_type = CoordinationEventType[event_type_name]
                except KeyError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid event type: {event_type_name}. Valid types: {[e.name for e in CoordinationEventType]}"
                    )
                
                # Create coordination event
                event = CoordinationEvent(
                    event_type=event_type,
                    source_component="api_trigger",
                    event_data=event_data.get("data", {}),
                    user_id=event_data.get("user_id")
                )
                
                # Trigger emoji rain
                effect_id = await self.emoji_engine.trigger_event_rain(event)
                
                # Also process through Observatory core
                await self.observatory_core.process_coordination_event(event)
                
                return {
                    "success": True,
                    "effect_id": effect_id,
                    "event_type": event_type_name,
                    "event_id": event.event_id
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to trigger emoji rain: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/emoji-rain/achievement")
        async def trigger_achievement_celebration(achievement_data: Dict[str, Any]):
            """Trigger special achievement celebration."""
            try:
                achievement = Achievement(
                    name=achievement_data.get("name", "API Achievement"),
                    description=achievement_data.get("description", "Achievement triggered via API"),
                    icon_emoji=achievement_data.get("icon_emoji", "🏆"),
                    user_id=achievement_data.get("user_id", "api_user")
                )
                
                effect_id = await self.emoji_engine.create_achievement_celebration(achievement)
                
                return {
                    "success": True,
                    "effect_id": effect_id,
                    "achievement": {
                        "name": achievement.name,
                        "description": achievement.description,
                        "icon_emoji": achievement.icon_emoji
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to trigger achievement celebration: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/emoji-rain/event-types")
        async def get_event_types():
            """Get available coordination event types for triggering."""
            return {
                "event_types": [
                    {
                        "name": event_type.name,
                        "description": f"Trigger {event_type.name.lower().replace('_', ' ')} emoji rain"
                    }
                    for event_type in CoordinationEventType
                ]
            }
        
        @self.app.get("/api/debug/emoji-engine")
        async def debug_emoji_engine():
            """Debug endpoint to check emoji engine state."""
            return {
                "animation_running": self.emoji_engine._running,
                "active_effects": len(self.emoji_engine._active_effects),
                "animation_task_exists": self.emoji_engine._animation_task is not None,
                "animation_task_done": self.emoji_engine._animation_task.done() if self.emoji_engine._animation_task else None,
                "connected_clients": len(self.emoji_ws_handler.connected_clients),
                "frame_rate": self.emoji_engine._frame_rate,
                "canvas_size": f"{self.emoji_engine._canvas_width}x{self.emoji_engine._canvas_height}"
            }
        
        @self.app.get("/api/metrics/components")
        async def discovered_components():
            """Get discovered Beast Mode components and their metrics."""
            if not self.observatory_core._metrics_collector:
                return {"error": "MetricsCollector not initialized"}
            
            return {
                "discovered_components": self.observatory_core._metrics_collector.get_discovered_components(),
                "collection_stats": self.observatory_core._metrics_collector.get_collection_stats()
            }
        
        @self.app.get("/api/metrics/collection-stats")
        async def collection_statistics():
            """Get metrics collection performance statistics."""
            if not self.observatory_core._metrics_collector:
                return {"error": "MetricsCollector not initialized"}
            
            return self.observatory_core._metrics_collector.get_collection_stats()
        
        @self.app.get("/api/costs/overview")
        async def cost_overview():
            """Get LLM cost overview and metrics."""
            if not self.observatory_core._cost_tracker:
                return {"error": "LLMCostTracker not initialized"}
            
            cost_metrics = self.observatory_core._cost_tracker.get_cost_metrics()
            tracking_stats = self.observatory_core._cost_tracker.get_tracking_stats()
            
            return {
                "cost_metrics": {
                    "total_cost_today": float(cost_metrics.total_cost_today),
                    "projected_monthly_cost": float(cost_metrics.projected_monthly_cost),
                    "cost_trend": cost_metrics.cost_trend.name,
                    "cost_by_provider": {k: float(v) for k, v in cost_metrics.cost_by_provider.items()},
                    "cost_by_model": {k: float(v) for k, v in cost_metrics.cost_by_model.items()}
                },
                "tracking_stats": tracking_stats
            }
        
        @self.app.post("/api/costs/track-call")
        async def track_llm_call(call_data: Dict[str, Any]):
            """Track an LLM API call for cost monitoring."""
            if not self.observatory_core._cost_tracker:
                return {"error": "LLMCostTracker not initialized"}
            
            try:
                api_call = await self.observatory_core._cost_tracker.track_api_call(
                    provider=call_data.get("provider", "openai"),
                    model=call_data.get("model", "gpt-3.5-turbo"),
                    input_tokens=call_data.get("input_tokens", 0),
                    output_tokens=call_data.get("output_tokens", 0),
                    response_time_ms=call_data.get("response_time_ms", 0.0),
                    success=call_data.get("success", True),
                    error_type=call_data.get("error_type"),
                    user_id=call_data.get("user_id"),
                    correlation_id=call_data.get("correlation_id")
                )
                
                return {
                    "success": True,
                    "call_id": api_call.call_id,
                    "estimated_cost": float(api_call.estimated_cost),
                    "total_tokens": api_call.total_tokens
                }
                
            except Exception as e:
                logger.error(f"Failed to track LLM call: {e}")
                return {"error": str(e)}
        
        @self.app.get("/api/costs/providers")
        async def supported_providers():
            """Get supported LLM providers and their pricing models."""
            if not self.observatory_core._cost_tracker:
                return {"error": "LLMCostTracker not initialized"}
            
            return {
                "supported_providers": ["openai", "anthropic", "google", "cohere", "huggingface", "azure_openai"],
                "pricing_models": self.observatory_core._cost_tracker.get_tracking_stats()["pricing_models"]
            }
        
        @self.app.get("/api/analytics/current")
        async def current_analytics():
            """Get current real-time analytics and insights."""
            if not self.observatory_core._analytics_engine:
                return {"error": "RealTimeAnalyticsEngine not initialized"}
            return self.observatory_core._analytics_engine.get_current_analytics()
        
        @self.app.get("/api/analytics/stats")
        async def analytics_statistics():
            """Get analytics engine performance statistics."""
            if not self.observatory_core._analytics_engine:
                return {"error": "RealTimeAnalyticsEngine not initialized"}
            return self.observatory_core._analytics_engine.get_analytics_stats()
        
        @self.app.get("/api/analytics/health")
        async def analytics_health():
            """Get analytics engine health status."""
            if not self.observatory_core._analytics_engine:
                return {"error": "RealTimeAnalyticsEngine not initialized"}
            health = self.observatory_core._analytics_engine.get_health_status()
            return {
                "status": health.status.value,
                "health_score": health.health_score,
                "issues": health.issues,
                "uptime_seconds": health.uptime_seconds,
                "error_count": health.error_count,
                "warning_count": health.warning_count
            }

        @self.app.get("/api/anomalies/active")
        async def active_anomalies():
            """Get currently active anomalies."""
            if not self.observatory_core._anomaly_detector:
                return {"error": "AnomalyDetectionEngine not initialized"}
            return {
                "active_anomalies": self.observatory_core._anomaly_detector.get_active_anomalies(),
                "anomaly_stats": self.observatory_core._anomaly_detector.get_anomaly_stats()
            }

        @self.app.get("/api/anomalies/stats")
        async def anomaly_statistics():
            """Get anomaly detection statistics."""
            if not self.observatory_core._anomaly_detector:
                return {"error": "AnomalyDetectionEngine not initialized"}
            return self.observatory_core._anomaly_detector.get_anomaly_stats()

        @self.app.get("/api/anomalies/health")
        async def anomaly_detection_health():
            """Get anomaly detection engine health status."""
            if not self.observatory_core._anomaly_detector:
                return {"error": "AnomalyDetectionEngine not initialized"}
            health = self.observatory_core._anomaly_detector.get_health_status()
            return {
                "status": health.status.value,
                "health_score": health.health_score,
                "issues": health.issues,
                "uptime_seconds": health.uptime_seconds,
                "error_count": health.error_count,
                "warning_count": health.warning_count
            }

        @self.app.post("/api/anomalies/resolve/{anomaly_id}")
        async def resolve_anomaly(anomaly_id: str):
            """Manually resolve an anomaly."""
            if not self.observatory_core._anomaly_detector:
                return {"error": "AnomalyDetectionEngine not initialized"}

            try:
                # Find the anomaly in active anomalies
                active_anomalies = self.observatory_core._anomaly_detector._active_anomalies
                for i, anomaly in enumerate(active_anomalies):
                    if anomaly.anomaly_id == anomaly_id:
                        # Move to resolved
                        resolved_anomaly = active_anomalies[i]
                        resolved_anomaly.auto_resolved = False  # Manually resolved
                        self.observatory_core._anomaly_detector._resolved_anomalies.append(resolved_anomaly)
                        del active_anomalies[i]

                        logger.info(f"✅ Manually resolved anomaly: {anomaly_id}")
                        return {"success": True, "message": f"Anomaly {anomaly_id} resolved"}

                return {"error": f"Anomaly {anomaly_id} not found in active anomalies"}

            except Exception as e:
                logger.error(f"Failed to resolve anomaly {anomaly_id}: {e}")
                return {"error": str(e)}

        @self.app.post("/api/anomalies/false-positive/{anomaly_id}")
        async def mark_false_positive(anomaly_id: str):
            """Mark an anomaly as a false positive for ML training."""
            if not self.observatory_core._anomaly_detector:
                return {"error": "AnomalyDetectionEngine not initialized"}

            try:
                # Find and remove the anomaly
                active_anomalies = self.observatory_core._anomaly_detector._active_anomalies
                for i, anomaly in enumerate(active_anomalies):
                    if anomaly.anomaly_id == anomaly_id:
                        del active_anomalies[i]
                        self.observatory_core._anomaly_detector._false_positives += 1

                        logger.info(f"🎯 Marked anomaly as false positive: {anomaly_id}")
                        return {"success": True, "message": f"Anomaly {anomaly_id} marked as false positive"}

                return {"error": f"Anomaly {anomaly_id} not found in active anomalies"}

            except Exception as e:
                logger.error(f"Failed to mark false positive {anomaly_id}: {e}")
                return {"error": str(e)}
    
    def _setup_websockets(self):
        """Setup WebSocket endpoints."""
        
        @self.app.websocket("/ws/emoji-rain")
        async def emoji_rain_websocket(websocket: WebSocket):
            """WebSocket endpoint for real-time emoji rain updates."""
            await websocket.accept()
            await self.emoji_ws_handler.add_client(websocket)
            
            try:
                # Send initial state
                initial_data = {
                    "type": "initial_state",
                    "data": {
                        "active_effects": self.emoji_engine.get_active_effects(),
                        "performance_stats": self.emoji_engine.get_performance_stats(),
                        "observatory_status": {
                            "health_score": self.observatory_core.get_health_status().health_score,
                            "uptime": self.observatory_core.get_health_status().uptime_seconds
                        }
                    }
                }
                await websocket.send_text(json.dumps(initial_data))
                
                # Handle incoming messages
                while True:
                    try:
                        message = await websocket.receive_text()
                        data = json.loads(message)
                        await self._handle_websocket_message(websocket, data)
                    except WebSocketDisconnect:
                        break
                    except Exception as e:
                        logger.error(f"WebSocket error: {e}")
                        break
                        
            except WebSocketDisconnect:
                pass
            finally:
                await self.emoji_ws_handler.remove_client(websocket)
        
        @self.app.websocket("/ws/observatory")
        async def observatory_websocket(websocket: WebSocket):
            """WebSocket endpoint for Observatory status updates."""
            await websocket.accept()
            
            try:
                while True:
                    # Send Observatory status every 5 seconds
                    health = self.observatory_core.get_health_status()
                    metrics = await self.observatory_core.get_metrics()

                    # Get anomaly data if available
                    anomalies = []
                    if self.observatory_core._anomaly_detector:
                        anomalies = self.observatory_core._anomaly_detector.get_active_anomalies()

                    status_data = {
                        "type": "observatory_status",
                        "data": {
                            "health": {
                                "status": health.status.value,
                                "health_score": health.health_score,
                                "uptime_seconds": health.uptime_seconds
                            },
                            "metrics": metrics,
                            "anomalies": anomalies,
                            "timestamp": health.last_check.isoformat()
                        }
                    }
                    
                    await websocket.send_text(json.dumps(status_data))
                    await asyncio.sleep(5)
                    
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"Observatory WebSocket error: {e}")

        @self.app.websocket("/ws/anomalies")
        async def anomalies_websocket(websocket: WebSocket):
            """WebSocket endpoint for real-time anomaly alerts."""
            await websocket.accept()

            try:
                while True:
                    if self.observatory_core._anomaly_detector:
                        # Send anomaly updates every 10 seconds
                        active_anomalies = self.observatory_core._anomaly_detector.get_active_anomalies()
                        anomaly_stats = self.observatory_core._anomaly_detector.get_anomaly_stats()

                        anomaly_data = {
                            "type": "anomaly_update",
                            "data": {
                                "active_anomalies": active_anomalies,
                                "stats": anomaly_stats,
                                "timestamp": datetime.now().isoformat()
                            }
                        }

                        await websocket.send_text(json.dumps(anomaly_data))

                    await asyncio.sleep(10)

            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"Anomaly WebSocket error: {e}")
    
    async def _handle_websocket_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle incoming WebSocket messages."""
        message_type = data.get("type")
        
        if message_type == "ping":
            await websocket.send_text(json.dumps({"type": "pong"}))
            
        elif message_type == "trigger_test_rain":
            try:
                event_type_name = data.get("event_type", "TASK_COMPLETED")
                event_type = CoordinationEventType[event_type_name]

                event = CoordinationEvent(
                    event_type=event_type,
                    source_component="websocket_test",
                    event_data=data.get("data", {})
                )

                effect_id = await self.emoji_engine.trigger_event_rain(event)
                await self.observatory_core.process_coordination_event(event)

                response = {
                    "type": "test_rain_triggered",
                    "data": {
                        "success": True,
                        "effect_id": effect_id,
                        "event_type": event_type_name
                    }
                }
                await websocket.send_text(json.dumps(response))
                
            except Exception as e:
                logger.error(f"Failed to trigger test rain: {e}")
                response = {
                    "type": "test_rain_triggered",
                    "data": {"success": False, "error": str(e)}
                }
                await websocket.send_text(json.dumps(response))
        
        elif message_type == "set_canvas_size":
            width = data.get("width", 1920)
            height = data.get("height", 1080)
            self.emoji_engine.set_canvas_size(width, height)
            
        else:
            logger.warning(f"Unknown WebSocket message type: {message_type}")
    
    def _setup_static_files(self):
        """Setup static file serving."""
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        
        # Mount static files
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    async def run_server(self, host: str = "0.0.0.0", port: Optional[int] = None):
        """Run the server with uvicorn."""
        if port is None:
            port = self.config.websocket_config.port
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            server.should_exit = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info(f"🚀 Starting Observatory Server on http://{host}:{port}")
        logger.info("🌧️ Emoji rain is ready - visit the dashboard to see the magic!")
        
        await server.serve()


def create_server(config_path: Optional[str] = None) -> ObservatoryServer:
    """Create an Observatory server instance."""
    config = load_observatory_config(config_path)
    return ObservatoryServer(config)


async def main():
    """Main entry point for running the Observatory server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Beast Mode Coordination Observatory Server")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, help="Port to bind to")
    
    args = parser.parse_args()
    
    try:
        server = create_server(args.config)
        await server.run_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("👋 Server interrupted by user")
    except Exception as e:
        logger.error(f"💥 Server crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())