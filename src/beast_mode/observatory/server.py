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
from datetime import datetime
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
from .observation_handler import ObservationHandler, set_global_observation_handler
from .models import (
    ObservatoryConfig,
    CoordinationEvent,
    CoordinationEventType,
    Achievement,
)
from .config import load_observatory_config

# Import engagement integration
try:
    from .engagement.integration.server_integration import (
        ObservatoryEngagementIntegration,
        add_engagement_websocket_to_server,
        inject_observatory_metrics,
        inject_observatory_health,
        inject_observatory_costs
    )
    ENGAGEMENT_AVAILABLE = True
except ImportError:
    ENGAGEMENT_AVAILABLE = False

# Import tracing
try:
    from src.beast_mode.tracing.tracer import get_tracer
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False


logger = logging.getLogger(__name__)


class ObservatoryServer:
    """Production-ready FastAPI server for the Beast Mode Coordination Observatory."""
    
    def __init__(self, config: ObservatoryConfig):
        self.config = config
        self.emoji_engine = EmojiRainEngine()
        self.observatory_core = ObservatoryCoreEngine(config)
        self.emoji_ws_handler = EmojiRainWebSocketHandler(self.emoji_engine)
        self.observation_handler = ObservationHandler()
        
        # Initialize engagement integration if available with comprehensive error handling
        self.engagement_integration = None
        self.engagement_available = False
        
        if ENGAGEMENT_AVAILABLE:
            try:
                self.engagement_integration = ObservatoryEngagementIntegration(config)
                self.engagement_available = True
                logger.info("🎯 Engagement integration initialized")
            except ImportError as e:
                logger.warning(f"Engagement integration not available due to import error: {e}")
                self.engagement_integration = None
                self.engagement_available = False
            except Exception as e:
                logger.error(f"Failed to initialize engagement integration: {e}")
                # Continue without engagement features
                self.engagement_integration = None
                self.engagement_available = False
        else:
            logger.info("Engagement integration not available - missing dependencies")
        
        # Set as global handler for ReflectiveModules to use
        set_global_observation_handler(self.observation_handler)
        
        # Initialize distributed tracing
        if TRACING_AVAILABLE:
            self.tracer = get_tracer("observatory-server")
            logger.info("🔍 Distributed tracing initialized for Observatory")
        else:
            self.tracer = None
        
        # Create FastAPI app with lifespan
        self.app = FastAPI(
            title=config.web_interface_config.title,
            description="Real-time coordination monitoring with delightful emoji rain",
            version="1.0.0",
            lifespan=self.lifespan
        )
        
        # Instrument FastAPI for tracing
        if self.tracer and self.tracer.is_available():
            self.tracer.instrument_fastapi(self.app)
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        self._setup_websockets()
        self._setup_engagement_features()
        self._setup_static_files()
        
        logger.info(f"🌐 Observatory Server initialized on port {config.websocket_config.port}")
        
        # Engagement integration already initialized above if available
    
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manage server lifespan - startup and shutdown."""
        # Startup
        logger.info("🚀 Starting Observatory Server...")
        
        # Start Observatory core
        await self.observatory_core.start_observatory()
        
        # Start emoji rain engine
        await self.emoji_engine.start_animation_loop()
        
        # Start engagement integration if available with error handling
        if self.engagement_integration:
            try:
                initialization_success = await self.engagement_integration.initialize()
                if initialization_success:
                    start_success = await self.engagement_integration.start_integration()
                    if start_success:
                        logger.info("🎯 Engagement integration started successfully")
                    else:
                        logger.warning("🎯 Engagement integration started with degraded functionality")
                        # Keep integration but mark as degraded
                else:
                    logger.error("🎯 Engagement integration initialization failed")
                    # Disable engagement integration but continue server startup
                    self.engagement_integration = None
                    self.engagement_available = False
            except Exception as e:
                logger.error(f"Failed to start engagement integration: {e}")
                # Continue server startup without engagement features
                self.engagement_integration = None
                self.engagement_available = False
                logger.info("🎯 Observatory server continuing without engagement features")
        
        logger.info("✅ Observatory Server started successfully")
        
        yield
        
        # Shutdown
        logger.info("🛑 Shutting down Observatory Server...")
        
        # Stop engagement integration with error handling
        if self.engagement_integration:
            try:
                await self.engagement_integration.stop_integration()
                logger.info("🎯 Engagement integration stopped")
            except Exception as e:
                logger.error(f"Error stopping engagement integration: {e}")
                # Continue shutdown process even if engagement stop fails
        
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
            """Health check endpoint with engagement system status."""
            observatory_health = self.observatory_core.get_health_status()
            emoji_stats = self.emoji_engine.get_performance_stats()
            
            health_data = {
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
            
            # Add engagement system status with comprehensive error handling (Requirement 28.1)
            if self.engagement_integration and self.engagement_available:
                try:
                    engagement_health = self.engagement_integration.get_health_status()
                    
                    # Get error handler statistics if available
                    error_stats = {}
                    resilience_status = {}
                    
                    if hasattr(self.engagement_integration, 'error_handler') and self.engagement_integration.error_handler:
                        try:
                            error_stats = self.engagement_integration.error_handler.get_error_statistics()
                        except Exception as e:
                            logger.debug(f"Could not get error statistics: {e}")
                    
                    if hasattr(self.engagement_integration, 'resilience_manager') and self.engagement_integration.resilience_manager:
                        try:
                            resilience_status = self.engagement_integration.resilience_manager.get_resilience_status()
                        except Exception as e:
                            logger.debug(f"Could not get resilience status: {e}")
                    
                    health_data["engagement"] = {
                        "status": engagement_health.get("status", "unknown"),
                        "integration_running": engagement_health.get("integration_running", False),
                        "active_websockets": engagement_health.get("active_websockets", 0),
                        "insights_broadcasted": engagement_health.get("insights_broadcasted", 0),
                        "storyteller_healthy": engagement_health.get("storyteller_healthy", False),
                        "data_bridge_running": engagement_health.get("data_bridge_running", False),
                        "monitoring": engagement_health.get("monitoring", {}),
                        "metrics": engagement_health.get("metrics", {}),
                        "error_handling": {
                            "total_errors": error_stats.get("total_errors", 0),
                            "recent_errors": error_stats.get("recent_errors", 0),
                            "system_degraded": error_stats.get("system_degraded", False),
                            "recovery_success_rate": error_stats.get("recovery_success_rate", 0.0)
                        },
                        "resilience": {
                            "current_strategy": resilience_status.get("current_strategy", "unknown"),
                            "system_health": resilience_status.get("system_health", 0.0),
                            "components_healthy": resilience_status.get("components_healthy", 0),
                            "components_degraded": resilience_status.get("components_degraded", 0),
                            "components_failed": resilience_status.get("components_failed", 0)
                        },
                        "component_health": {
                            "dashboard_engine": "implemented",
                            "data_storyteller": "implemented", 
                            "animation_engine": "placeholder",
                            "personality_engine": "placeholder",
                            "attention_manager": "placeholder",
                            "interaction_engine": "placeholder",
                            "learning_engine": "placeholder",
                            "error_handler": "implemented",
                            "resilience_manager": "implemented",
                            "error_recovery": "implemented"
                        }
                    }
                    
                    # Inject comprehensive engagement health into Observatory health
                    try:
                        from .engagement.integration.server_integration import inject_engagement_health_into_observatory_endpoint
                        await inject_engagement_health_into_observatory_endpoint(
                            self.engagement_integration, health_data
                        )
                    except Exception as e:
                        logger.debug(f"Could not inject engagement health: {e}")
                    
                    # Inject health data into engagement system
                    try:
                        await inject_observatory_health(self.engagement_integration, {
                            "health_score": observatory_health.health_score,
                            "status": observatory_health.status.value,
                            "uptime_seconds": observatory_health.uptime_seconds
                        })
                    except Exception as e:
                        logger.debug(f"Could not inject Observatory health: {e}")
                        
                except Exception as e:
                    logger.warning(f"Error adding engagement health data: {e}")
                    health_data["engagement"] = {
                        "status": "error",
                        "error": str(e),
                        "message": "Engagement system encountered an error but Observatory continues to function",
                        "component_health": {
                            "dashboard_engine": "error",
                            "data_storyteller": "error",
                            "animation_engine": "error",
                            "personality_engine": "error", 
                            "attention_manager": "error",
                            "interaction_engine": "error",
                            "learning_engine": "error",
                            "error_handler": "error",
                            "resilience_manager": "error",
                            "error_recovery": "error"
                        }
                    }
            else:
                # Engagement system not available or disabled
                reason = "not available" if not ENGAGEMENT_AVAILABLE else "disabled due to initialization failure"
                health_data["engagement"] = {
                    "status": "disabled",
                    "message": f"Engagement integration {reason}",
                    "observatory_core_functional": True,
                    "component_health": {
                        "dashboard_engine": "not_available",
                        "data_storyteller": "not_available",
                        "animation_engine": "not_available",
                        "personality_engine": "not_available",
                        "attention_manager": "not_available", 
                        "interaction_engine": "not_available",
                        "learning_engine": "not_available",
                        "error_handler": "not_available",
                        "resilience_manager": "not_available",
                        "error_recovery": "not_available"
                    }
                }
            
            return health_data
        
        @self.app.get("/healthemoji-rain")
        async def health_emoji_rain():
            """Combined health check with emoji rain celebration."""
            observatory_health = self.observatory_core.get_health_status()
            emoji_stats = self.emoji_engine.get_performance_stats()
            
            # Trigger a small celebration if system is healthy
            if observatory_health.health_score > 0.8:
                try:
                    # Create a health check celebration event
                    from .models import CoordinationEvent, CoordinationEventType
                    health_event = CoordinationEvent(
                        event_type=CoordinationEventType.SYSTEM_HEALTH_CHECK,
                        source_component="health_endpoint",
                        event_data={"health_score": observatory_health.health_score},
                        user_id="system"
                    )
                    
                    # Trigger a small emoji rain celebration
                    effect_id = await self.emoji_engine.trigger_event_rain(health_event)
                    celebration_triggered = True
                except Exception as e:
                    logger.warning(f"Failed to trigger health celebration: {e}")
                    celebration_triggered = False
                    effect_id = None
            else:
                celebration_triggered = False
                effect_id = None
            
            return {
                "status": "healthy" if observatory_health.health_score > 0.5 else "degraded",
                "timestamp": observatory_health.last_check.isoformat(),
                "health_score": observatory_health.health_score,
                "celebration_triggered": celebration_triggered,
                "effect_id": effect_id,
                "observatory": {
                    "status": observatory_health.status.value,
                    "health_score": observatory_health.health_score,
                    "uptime_seconds": observatory_health.uptime_seconds,
                    "error_count": observatory_health.error_count,
                    "warning_count": observatory_health.warning_count
                },
                "emoji_rain": {
                    "active": emoji_stats["animation_running"],
                    "active_effects": emoji_stats["active_effects"],
                    "total_particles": emoji_stats["total_particles"],
                    "connected_clients": len(self.emoji_ws_handler.connected_clients),
                    "frame_rate": emoji_stats.get("frame_rate", 60)
                }
            }
        
        @self.app.get("/ready")
        async def readiness_check():
            """Readiness check endpoint with engagement component health."""
            observatory_health = self.observatory_core.get_health_status()
            
            # Base readiness criteria
            ready = observatory_health.health_score > 0.5
            
            readiness_data = {
                "ready": ready,
                "timestamp": observatory_health.last_check.isoformat(),
                "observatory": {
                    "ready": ready,
                    "health_score": observatory_health.health_score,
                    "status": observatory_health.status.value
                },
                "emoji_rain": {
                    "ready": self.emoji_engine._running,
                    "animation_running": self.emoji_engine._running
                }
            }
            
            # Add engagement component readiness (Requirement 28.2)
            if self.engagement_integration:
                try:
                    engagement_health = self.engagement_integration.get_health_status()
                    engagement_ready = (
                        engagement_health.get("integration_running", False) and
                        engagement_health.get("storyteller_healthy", False)
                    )
                    
                    readiness_data["engagement"] = {
                        "ready": engagement_ready,
                        "integration_running": engagement_health.get("integration_running", False),
                        "storyteller_healthy": engagement_health.get("storyteller_healthy", False),
                        "data_bridge_running": engagement_health.get("data_bridge_running", False),
                        "components": {
                            "dashboard_engine": "ready",
                            "data_storyteller": "ready" if engagement_health.get("storyteller_healthy") else "not_ready",
                            "animation_engine": "placeholder",
                            "personality_engine": "placeholder",
                            "attention_manager": "placeholder",
                            "interaction_engine": "placeholder", 
                            "learning_engine": "placeholder"
                        }
                    }
                    
                    # Overall readiness includes engagement
                    readiness_data["ready"] = ready and engagement_ready
                    
                except Exception as e:
                    logger.warning(f"Error checking engagement readiness: {e}")
                    readiness_data["engagement"] = {
                        "ready": False,
                        "error": str(e),
                        "components": {
                            "dashboard_engine": "error",
                            "data_storyteller": "error",
                            "animation_engine": "placeholder",
                            "personality_engine": "placeholder",
                            "attention_manager": "placeholder",
                            "interaction_engine": "placeholder",
                            "learning_engine": "placeholder"
                        }
                    }
                    readiness_data["ready"] = False
            else:
                readiness_data["engagement"] = {
                    "ready": False,
                    "message": "Engagement integration not available",
                    "components": {
                        "dashboard_engine": "not_available",
                        "data_storyteller": "not_available", 
                        "animation_engine": "not_available",
                        "personality_engine": "not_available",
                        "attention_manager": "not_available",
                        "interaction_engine": "not_available",
                        "learning_engine": "not_available"
                    }
                }
            
            return readiness_data
        
        @self.app.get("/metrics")
        async def prometheus_metrics():
            """Prometheus metrics endpoint."""
            try:
                # Try to get metrics from prometheus_client if available
                try:
                    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
                    from prometheus_client import CollectorRegistry, REGISTRY
                    
                    # Generate metrics in Prometheus format
                    metrics_output = generate_latest(REGISTRY).decode('utf-8')
                    
                    # Add engagement metrics if available (Requirement 28.3)
                    if self.engagement_integration:
                        try:
                            from .engagement.integration.server_integration import get_engagement_prometheus_metrics_text
                            engagement_metrics = get_engagement_prometheus_metrics_text(self.engagement_integration)
                            metrics_output += "\n" + engagement_metrics
                            
                            # Add basic engagement component metrics
                            engagement_health = self.engagement_integration.get_health_status()
                            metrics_output += f"\n# HELP engagement_integration_running Engagement integration status\n"
                            metrics_output += f"# TYPE engagement_integration_running gauge\n"
                            metrics_output += f"engagement_integration_running {1 if engagement_health.get('integration_running') else 0}\n"
                            
                            metrics_output += f"# HELP engagement_active_websockets Active engagement WebSocket connections\n"
                            metrics_output += f"# TYPE engagement_active_websockets gauge\n"
                            metrics_output += f"engagement_active_websockets {engagement_health.get('active_websockets', 0)}\n"
                            
                            metrics_output += f"# HELP engagement_insights_broadcasted Total insights broadcasted\n"
                            metrics_output += f"# TYPE engagement_insights_broadcasted counter\n"
                            metrics_output += f"engagement_insights_broadcasted {engagement_health.get('insights_broadcasted', 0)}\n"
                            
                        except Exception as e:
                            logger.warning(f"Failed to add engagement metrics: {e}")
                            # Add error metric
                            metrics_output += f"\n# HELP engagement_metrics_error Engagement metrics collection error\n"
                            metrics_output += f"# TYPE engagement_metrics_error gauge\n"
                            metrics_output += f"engagement_metrics_error 1\n"
                    
                    from fastapi import Response
                    return Response(
                        content=metrics_output,
                        media_type=CONTENT_TYPE_LATEST
                    )
                except ImportError:
                    # Fallback to basic metrics if prometheus_client not available
                    observatory_health = self.observatory_core.get_health_status()
                    emoji_stats = self.emoji_engine.get_performance_stats()
                    
                    # Basic Prometheus format metrics
                    metrics_lines = [
                        f"# HELP observatory_health_score Observatory health score",
                        f"# TYPE observatory_health_score gauge",
                        f"observatory_health_score {observatory_health.health_score}",
                        f"# HELP observatory_uptime_seconds Observatory uptime in seconds",
                        f"# TYPE observatory_uptime_seconds counter",
                        f"observatory_uptime_seconds {observatory_health.uptime_seconds}",
                        f"# HELP observatory_error_count Total error count",
                        f"# TYPE observatory_error_count counter",
                        f"observatory_error_count {observatory_health.error_count}",
                        f"# HELP emoji_rain_active_effects Active emoji rain effects",
                        f"# TYPE emoji_rain_active_effects gauge",
                        f"emoji_rain_active_effects {emoji_stats.get('active_effects', 0)}",
                        f"# HELP emoji_rain_connected_clients Connected WebSocket clients",
                        f"# TYPE emoji_rain_connected_clients gauge",
                        f"emoji_rain_connected_clients {len(self.emoji_ws_handler.connected_clients)}",
                    ]
                    
                    # Add engagement metrics if available (Requirement 28.3)
                    if self.engagement_integration:
                        try:
                            from .engagement.integration.server_integration import get_engagement_prometheus_metrics_text
                            engagement_metrics = get_engagement_prometheus_metrics_text(self.engagement_integration)
                            metrics_lines.append(engagement_metrics.rstrip())
                            
                            # Add basic engagement component metrics
                            engagement_health = self.engagement_integration.get_health_status()
                            metrics_lines.extend([
                                f"# HELP engagement_integration_running Engagement integration status",
                                f"# TYPE engagement_integration_running gauge", 
                                f"engagement_integration_running {1 if engagement_health.get('integration_running') else 0}",
                                f"# HELP engagement_active_websockets Active engagement WebSocket connections",
                                f"# TYPE engagement_active_websockets gauge",
                                f"engagement_active_websockets {engagement_health.get('active_websockets', 0)}",
                                f"# HELP engagement_insights_broadcasted Total insights broadcasted",
                                f"# TYPE engagement_insights_broadcasted counter", 
                                f"engagement_insights_broadcasted {engagement_health.get('insights_broadcasted', 0)}"
                            ])
                            
                        except Exception as e:
                            logger.warning(f"Failed to add engagement metrics: {e}")
                            # Add error metric
                            metrics_lines.extend([
                                f"# HELP engagement_metrics_error Engagement metrics collection error",
                                f"# TYPE engagement_metrics_error gauge",
                                f"engagement_metrics_error 1"
                            ])
                    
                    from fastapi import Response
                    return Response(
                        content="\n".join(metrics_lines) + "\n",
                        media_type="text/plain; version=0.0.4; charset=utf-8"
                    )
                    
            except Exception as e:
                logger.error(f"Failed to generate Prometheus metrics: {e}")
                from fastapi import Response
                return Response(
                    content=f"# Error generating metrics: {e}\n",
                    media_type="text/plain; version=0.0.4; charset=utf-8",
                    status_code=500
                )
        
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
        
        @self.app.get("/api/doctor/status")
        async def doctor_status():
            """Get AI consultation doctor status."""
            try:
                from .ai_consultation.doctor_status_indicator import get_doctor_status_indicator
                indicator = get_doctor_status_indicator()
                return indicator.get_status_for_ui()
            except ImportError:
                # AI consultation module not available
                return {
                    "enabled": False,
                    "message": "AI consultation feature is not available"
                }
        
        @self.app.post("/api/doctor/toggle")
        async def toggle_doctor_status(request_data: Dict[str, Any]):
            """Toggle doctor availability status."""
            try:
                from .ai_consultation.doctor_status_indicator import get_doctor_status_indicator
                indicator = get_doctor_status_indicator()
                
                is_available = request_data.get("is_available", False)
                reason = request_data.get("reason", "")
                
                new_status = indicator.set_status(is_available, reason)
                
                # Broadcast status update via WebSocket
                await self._broadcast_doctor_status_update(indicator)
                
                return indicator.get_status_for_ui()
            except ImportError:
                raise HTTPException(
                    status_code=503,
                    detail="AI consultation feature is not available"
                )
        
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
        
        @self.app.get("/api/engagement/status")
        async def engagement_status():
            """Get engagement system status and component health."""
            if not self.engagement_integration:
                return {
                    "status": "disabled",
                    "message": "Engagement integration not available",
                    "components": {},
                    "timestamp": datetime.now().isoformat()
                }
            
            try:
                engagement_health = self.engagement_integration.get_health_status()
                coordination_status = {}
                
                # Get coordination status if available
                try:
                    from .engagement.integration.server_integration import get_engagement_coordination_status
                    coordination_status = get_engagement_coordination_status(self.engagement_integration)
                except Exception as e:
                    logger.warning(f"Failed to get coordination status: {e}")
                
                return {
                    "status": engagement_health.get("status", "unknown"),
                    "timestamp": datetime.now().isoformat(),
                    "integration": {
                        "running": engagement_health.get("integration_running", False),
                        "insights_broadcasted": engagement_health.get("insights_broadcasted", 0),
                        "last_broadcast": engagement_health.get("last_broadcast"),
                        "active_websockets": engagement_health.get("active_websockets", 0)
                    },
                    "components": {
                        "dashboard_engine": {
                            "status": "implemented",
                            "health": "healthy",
                            "description": "Core dashboard rendering with real-time data integration"
                        },
                        "data_storyteller": {
                            "status": "implemented", 
                            "health": "healthy" if engagement_health.get("storyteller_healthy") else "degraded",
                            "description": "Intelligent narrative generation from data patterns"
                        },
                        "animation_engine": {
                            "status": "placeholder",
                            "health": "placeholder",
                            "description": "GPU-accelerated animations (placeholder implementation)"
                        },
                        "personality_engine": {
                            "status": "placeholder",
                            "health": "placeholder", 
                            "description": "Adaptive dashboard personality (placeholder implementation)"
                        },
                        "attention_manager": {
                            "status": "placeholder",
                            "health": "placeholder",
                            "description": "Intelligent attention prioritization (placeholder implementation)"
                        },
                        "interaction_engine": {
                            "status": "placeholder",
                            "health": "placeholder",
                            "description": "Multi-modal user interaction (placeholder implementation)"
                        },
                        "learning_engine": {
                            "status": "placeholder", 
                            "health": "placeholder",
                            "description": "Continuous improvement through user behavior analysis (placeholder implementation)"
                        }
                    },
                    "monitoring": engagement_health.get("monitoring", {}),
                    "metrics": engagement_health.get("metrics", {}),
                    "coordination": coordination_status
                }
                
            except Exception as e:
                logger.error(f"Error getting engagement status: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "components": {}
                }
        
        @self.app.get("/api/engagement/config")
        async def engagement_config():
            """Get basic engagement system configuration."""
            if not self.engagement_integration:
                return {
                    "enabled": False,
                    "message": "Engagement integration not available",
                    "config": {},
                    "timestamp": datetime.now().isoformat()
                }
            
            try:
                # Get current configuration from engagement system
                config_data = {
                    "enabled": True,
                    "timestamp": datetime.now().isoformat(),
                    "features": {
                        "real_time_insights": True,
                        "websocket_broadcasting": True,
                        "data_storytelling": True,
                        "pattern_discovery": True,
                        "observatory_integration": True,
                        "live_data_streaming": True,
                        "gpu_animations": False,  # Placeholder
                        "adaptive_personality": False,  # Placeholder
                        "attention_management": False,  # Placeholder
                        "multi_modal_interaction": False,  # Placeholder
                        "continuous_learning": False  # Placeholder
                    },
                    "settings": {
                        "broadcast_interval_seconds": 30,
                        "max_websocket_connections": 100,
                        "insight_retention_hours": 24,
                        "pattern_detection_threshold": 0.7,
                        "health_check_interval_seconds": 60
                    },
                    "component_config": {
                        "dashboard_engine": {
                            "enabled": True,
                            "contextual_layering": True,
                            "engagement_analytics": True,
                            "performance_monitoring": True
                        },
                        "data_storyteller": {
                            "enabled": True,
                            "pattern_detection": True,
                            "narrative_generation": True,
                            "correlation_analysis": True,
                            "background_analysis_interval": 60
                        },
                        "animation_engine": {
                            "enabled": False,
                            "implementation": "placeholder",
                            "gpu_acceleration": False,
                            "target_fps": 60
                        },
                        "personality_engine": {
                            "enabled": False,
                            "implementation": "placeholder",
                            "mood_transitions": False,
                            "context_analysis": False
                        },
                        "attention_manager": {
                            "enabled": False,
                            "implementation": "placeholder",
                            "event_prioritization": False,
                            "focus_control": False
                        },
                        "interaction_engine": {
                            "enabled": False,
                            "implementation": "placeholder",
                            "multi_modal_support": False,
                            "accessibility_features": False
                        },
                        "learning_engine": {
                            "enabled": False,
                            "implementation": "placeholder",
                            "behavior_analysis": False,
                            "ab_testing": False
                        }
                    }
                }
                
                return config_data
                
            except Exception as e:
                logger.error(f"Error getting engagement config: {e}")
                return {
                    "enabled": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "config": {}
                }
        
        @self.app.get("/api/engagement/analytics")
        async def engagement_analytics():
            """Get basic engagement metrics and analytics."""
            if not self.engagement_integration:
                return {
                    "available": False,
                    "message": "Engagement integration not available",
                    "analytics": {},
                    "timestamp": datetime.now().isoformat()
                }
            
            try:
                engagement_health = self.engagement_integration.get_health_status()
                
                # Get WebSocket connection stats
                websocket_stats = {}
                if hasattr(self.engagement_integration, 'websocket_manager'):
                    websocket_stats = self.engagement_integration.websocket_manager.get_connection_stats()
                
                # Get storyteller metrics if available
                storyteller_metrics = {}
                if hasattr(self.engagement_integration, 'storyteller'):
                    try:
                        storyteller_health = self.engagement_integration.storyteller.get_health_status()
                        storyteller_metrics = {
                            "patterns_detected": storyteller_health.get("patterns_detected", 0),
                            "insights_generated": storyteller_health.get("insights_generated", 0),
                            "data_points_processed": storyteller_health.get("data_points_processed", 0),
                            "analysis_cycles": storyteller_health.get("analysis_cycles", 0)
                        }
                    except Exception as e:
                        logger.warning(f"Failed to get storyteller metrics: {e}")
                
                analytics_data = {
                    "available": True,
                    "timestamp": datetime.now().isoformat(),
                    "summary": {
                        "integration_running": engagement_health.get("integration_running", False),
                        "insights_broadcasted": engagement_health.get("insights_broadcasted", 0),
                        "active_websockets": engagement_health.get("active_websockets", 0),
                        "storyteller_healthy": engagement_health.get("storyteller_healthy", False)
                    },
                    "websocket_analytics": {
                        "active_connections": websocket_stats.get("active_connections", 0),
                        "total_messages_sent": websocket_stats.get("total_messages_sent", 0),
                        "connection_metadata": websocket_stats.get("connection_metadata", {})
                    },
                    "storyteller_analytics": storyteller_metrics,
                    "engagement_metrics": engagement_health.get("metrics", {}),
                    "component_analytics": {
                        "dashboard_engine": {
                            "status": "active",
                            "interactions": 0,  # Placeholder
                            "render_time_ms": 0  # Placeholder
                        },
                        "data_storyteller": {
                            "status": "active" if engagement_health.get("storyteller_healthy") else "inactive",
                            "patterns_detected": storyteller_metrics.get("patterns_detected", 0),
                            "insights_generated": storyteller_metrics.get("insights_generated", 0)
                        },
                        "animation_engine": {
                            "status": "placeholder",
                            "animations_triggered": 0,
                            "average_fps": 0
                        },
                        "personality_engine": {
                            "status": "placeholder",
                            "mood_transitions": 0,
                            "current_mood": "neutral"
                        },
                        "attention_manager": {
                            "status": "placeholder",
                            "events_prioritized": 0,
                            "attention_budget_used": 0
                        },
                        "interaction_engine": {
                            "status": "placeholder",
                            "interactions_processed": 0,
                            "accessibility_requests": 0
                        },
                        "learning_engine": {
                            "status": "placeholder",
                            "patterns_learned": 0,
                            "optimizations_applied": 0
                        }
                    },
                    "performance": {
                        "last_broadcast": engagement_health.get("last_broadcast"),
                        "broadcast_frequency": "30 seconds",
                        "average_response_time_ms": 0,  # Placeholder
                        "error_rate": 0  # Placeholder
                    }
                }
                
                return analytics_data
                
            except Exception as e:
                logger.error(f"Error getting engagement analytics: {e}")
                return {
                    "available": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "analytics": {}
                }
        
        @self.app.get("/api/observations/recent")
        async def get_recent_observations():
            """Get recent system observations from Beastly Modules."""
            try:
                # Get recent observations from the observation handler
                observations = self.observation_handler.get_recent_observations(limit=20)
                
                # If no observations yet, provide some sample data
                if not observations:
                    observations = [
                        {
                            "timestamp": datetime.now().isoformat(),
                            "module": "ObservatoryServer",
                            "event_type": "info",
                            "message": "Observatory observation system initialized 🎬",
                            "emoji": "🎬",
                            "severity": "info",
                            "context": {
                                "connected_clients": len(self.observation_handler.connected_clients),
                                "correlation_id": f"init_{datetime.now().timestamp()}"
                            }
                        }
                    ]
                
                return observations
                
            except Exception as e:
                logger.error(f"Failed to get observations: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/observations")
        async def post_observation(request: Request):
            """Post a new observation to the Observatory system."""
            try:
                observation_data = await request.json()
                
                # Validate required fields
                required_fields = ["message", "module"]
                for field in required_fields:
                    if field not in observation_data:
                        raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
                
                # Add timestamp if not provided
                if "timestamp" not in observation_data:
                    observation_data["timestamp"] = datetime.now().isoformat()
                
                # Set defaults for optional fields
                observation_data.setdefault("event_type", "info")
                observation_data.setdefault("emoji", "📰")
                observation_data.setdefault("severity", "info")
                observation_data.setdefault("context", {})
                
                # Broadcast the observation
                await self.observation_handler.broadcast_observation(observation_data)
                
                logger.info(f"📰 Received external observation: {observation_data['message']}")
                
                return {"status": "success", "message": "Observation posted successfully"}
                
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in request body")
            except Exception as e:
                logger.error(f"Failed to post observation: {e}")
                raise HTTPException(status_code=500, detail=str(e))

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

        @self.app.get("/api/dashboard/all-data")
        async def consolidated_dashboard_data():
            """
            Consolidated API endpoint for all chart data.
            Single endpoint to replace multiple API calls and prevent recursive updates.
            Required by the new clean chart architecture.
            """
            try:
                # Ensure observatory core is initialized
                if not hasattr(self, 'observatory_core') or not self.observatory_core:
                    logger.warning("Observatory core not initialized, returning fallback data")
                    return {
                        "analytics": {"healthScore": 0.7, "componentCount": 1},
                        "costs": {"totalCost": 0.0, "apiCalls": 0, "providers": {}},
                        "metrics": {"responseTime": 200.0, "errorRate": 0.0, "throughput": 100.0},
                        "agents": {"active": 1, "tasks": 0, "coordination": 0.5},
                        "timestamp": datetime.now().isoformat(),
                        "status": "initializing"
                    }
                # Gather all data in parallel to minimize latency
                import asyncio

                async def safe_get_analytics():
                    try:
                        # Get real Observatory health data
                        health = self.observatory_core.get_health_status()
                        metrics = await self.observatory_core.get_metrics()
                        
                        return {
                            "healthScore": health.health_score,
                            "componentCount": metrics.get("components_discovered", 0),
                            "uptime": health.uptime_seconds,
                            "errorCount": health.error_count,
                            "warningCount": health.warning_count
                        }
                    except Exception as e:
                        logger.warning(f"Analytics data unavailable: {e}")
                    return {"healthScore": 0.8, "componentCount": 0}

                async def safe_get_costs():
                    try:
                        if self.observatory_core._cost_tracker:
                            stats = self.observatory_core._cost_tracker.get_tracking_stats()
                            
                            # Calculate token statistics from recent API calls
                            input_tokens = 0
                            output_tokens = 0
                            total_tokens = 0
                            
                            # Get recent API calls for token data
                            if hasattr(self.observatory_core._cost_tracker, '_api_calls'):
                                recent_calls = self.observatory_core._cost_tracker._api_calls[-10:]  # Last 10 calls
                                for call in recent_calls:
                                    input_tokens += getattr(call, 'input_tokens', 0)
                                    output_tokens += getattr(call, 'output_tokens', 0)
                                    total_tokens += getattr(call, 'total_tokens', 0)
                            
                            return {
                                "totalCost": stats.get("total_cost_today", 0.0),
                                "apiCalls": stats.get("calls_tracked", 0),
                                "providers": stats.get("provider_costs", {}),
                                # Token metrics for chart visualization
                                "inputTokens": input_tokens,
                                "outputTokens": output_tokens,
                                "totalTokens": total_tokens,
                                "tokenRate": total_tokens / 60.0 if total_tokens > 0 else 0.0  # Tokens per minute estimate
                            }
                    except Exception as e:
                        logger.warning(f"Cost data unavailable: {e}")
                    return {
                        "totalCost": 0.0, 
                        "apiCalls": 0, 
                        "providers": {},
                        "inputTokens": 0,
                        "outputTokens": 0, 
                        "totalTokens": 0,
                        "tokenRate": 0.0
                    }

                async def safe_get_metrics():
                    try:
                        # Get real Observatory metrics
                        observatory_metrics = await self.observatory_core.get_metrics()
                        health = self.observatory_core.get_health_status()
                        
                        # Calculate real performance metrics
                        collection_rate = observatory_metrics.get("collection_rate_per_second", 0.0)
                        events_processed = observatory_metrics.get("events_processed_total", 0)
                        
                        return {
                            "responseTime": 200.0 if health.health_score > 0.8 else 500.0,  # Still estimated
                            "errorRate": max(0, 100 * (1 - health.health_score)),
                            "throughput": collection_rate,  # Real collection rate
                            "eventsProcessed": events_processed,
                            "componentsDiscovered": observatory_metrics.get("components_discovered", 0)
                        }
                    except Exception as e:
                        logger.warning(f"Metrics data unavailable: {e}")
                    return {"responseTime": 300.0, "errorRate": 5.0, "throughput": 100.0}

                async def safe_get_agents():
                    try:
                        observatory_metrics = await self.observatory_core.get_metrics()
                        components = observatory_metrics.get("components_discovered", 0)
                        events_processed = observatory_metrics.get("events_processed_total", 0)
                        
                        return {
                            "active": max(1, components),  # Real component count
                            "tasks": events_processed,     # Real events processed
                            "coordination": min(1.0, components / 10.0),  # Coordination based on components
                            "componentsDiscovered": components,
                            "collectionRate": observatory_metrics.get("collection_rate_per_second", 0.0)
                        }
                    except Exception as e:
                        logger.warning(f"Agent data unavailable: {e}")
                    return {"active": 1, "tasks": 5, "coordination": 0.5}

                # Fetch all data concurrently
                analytics, costs, metrics, agents = await asyncio.gather(
                    safe_get_analytics(),
                    safe_get_costs(),
                    safe_get_metrics(),
                    safe_get_agents(),
                    return_exceptions=True
                )

                # Handle any exceptions in the results
                if isinstance(analytics, Exception):
                    analytics = {"healthScore": 0.8, "componentCount": 0}
                if isinstance(costs, Exception):
                    costs = {"totalCost": 0.0, "apiCalls": 0, "providers": {}}
                if isinstance(metrics, Exception):
                    metrics = {"responseTime": 300.0, "errorRate": 5.0, "throughput": 100.0}
                if isinstance(agents, Exception):
                    agents = {"active": 1, "tasks": 5, "coordination": 0.5}

                # Return consolidated data structure expected by DataAggregator
                return {
                    "analytics": analytics,
                    "costs": costs,
                    "metrics": metrics,
                    "agents": agents,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }

            except Exception as e:
                logger.error(f"Failed to fetch consolidated dashboard data: {e}")
                # Return fallback data structure to prevent chart failures
                return {
                    "analytics": {"healthScore": 0.5, "componentCount": 0},
                    "costs": {"totalCost": 0.0, "apiCalls": 0, "providers": {}},
                    "metrics": {"responseTime": 500.0, "errorRate": 10.0, "throughput": 50.0},
                    "agents": {"active": 0, "tasks": 0, "coordination": 0.0},
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "error": str(e)
                }
    
    def _setup_engagement_integration(self):
        """Setup engagement integration if available."""
        try:
            from .engagement.integration.server_integration import ObservatoryEngagementIntegration
            
            # Initialize engagement integration
            self.engagement_integration = ObservatoryEngagementIntegration(self.config)
            
            # Add engagement WebSocket endpoint
            @self.app.websocket("/ws/engagement")
            async def engagement_websocket(websocket: WebSocket):
                """WebSocket endpoint for real-time engagement updates."""
                if self.engagement_integration:
                    await self.engagement_integration.handle_websocket_connection(websocket)
                else:
                    await websocket.close(code=1000, reason="Engagement system not available")
            
            # Add engagement API endpoints
            @self.app.get("/api/engagement/insights")
            async def get_engagement_insights():
                """Get current data insights from engagement system."""
                if self.engagement_integration:
                    insights = await self.engagement_integration.data_bridge.get_recent_insights()
                    return {
                        "status": "success",
                        "data": insights,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Engagement system not available",
                        "timestamp": datetime.now().isoformat()
                    }
            
            @self.app.get("/api/engagement/status")
            async def get_engagement_status():
                """Get engagement system status."""
                if self.engagement_integration:
                    status = await self.engagement_integration._get_system_status()
                    return {
                        "status": "success",
                        "data": status,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Engagement system not available",
                        "timestamp": datetime.now().isoformat()
                    }
            
            logger.info("🎯 Engagement integration setup complete")
            
        except ImportError as e:
            logger.info("🎯 Engagement system not available - continuing without engagement features")
            self.engagement_integration = None
        except Exception as e:
            logger.error(f"Failed to setup engagement integration: {e}")
            self.engagement_integration = None
    
    async def _inject_live_data_to_engagement(self):
        """Inject live Observatory data into the engagement system."""
        if not self.engagement_integration:
            return
        
        try:
            # Get current Observatory data
            dashboard_data = await self._get_consolidated_dashboard_data()
            
            # Inject metrics data
            if "metrics" in dashboard_data:
                await self.engagement_integration.inject_observatory_data("metrics", dashboard_data["metrics"])
            
            # Inject analytics data as health
            if "analytics" in dashboard_data:
                await self.engagement_integration.inject_observatory_data("health", dashboard_data["analytics"])
            
            # Inject cost data
            if "costs" in dashboard_data:
                await self.engagement_integration.inject_observatory_data("costs", dashboard_data["costs"])
            
        except Exception as e:
            logger.debug(f"Error injecting data to engagement system: {e}")

    def _setup_websockets(self):
        """Setup WebSocket endpoints with explicit registration."""
        logger.info("🔌 Setting up WebSocket endpoints...")
        
        # Initialize engagement integration if available
        self._setup_engagement_integration()
        
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
                        # Handle WebSocket message
                        if data.get("type") == "trigger_emoji_rain":
                            await self.emoji_engine.trigger_effect(data.get("effect_type", "celebration"))
                        elif data.get("type") == "trigger_test_rain":
                            # Trigger test emoji rain
                            event_type_name = data.get("event_type", "TASK_COMPLETED")
                            try:
                                from .models import CoordinationEventType, CoordinationEvent
                                event_type = CoordinationEventType[event_type_name]
                                
                                event = CoordinationEvent(
                                    event_type=event_type,
                                    source_component="websocket_test",
                                    event_data=data.get("data", {})
                                )
                                
                                effect_id = await self.emoji_engine.trigger_event_rain(event)
                                
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
                                    "data": {
                                        "success": False,
                                        "error": str(e)
                                    }
                                }
                                await websocket.send_text(json.dumps(response))
                        elif data.get("type") == "ping":
                            await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
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
                    
                    # Inject data into engagement system
                    await self._inject_live_data_to_engagement()
                    
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
                logger.error(f"Anomalies WebSocket error: {e}")

        @self.app.websocket("/ws/doctor-status")
        async def doctor_status_websocket(websocket: WebSocket):
            """WebSocket endpoint for doctor status updates."""
            await websocket.accept()

            try:
                while True:
                    # Send doctor status every 3 seconds
                    doctor_data = {
                        "type": "doctor_status",
                        "data": {
                            "status": "healthy",
                            "checks_performed": 42,
                            "last_check": datetime.now().isoformat(),
                            "system_health": self.observatory_core.get_health_status().health_score
                        }
                    }
                    
                    await websocket.send_text(json.dumps(doctor_data))
                    await asyncio.sleep(3)
                    
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"Doctor status WebSocket error: {e}")
        
        @self.app.websocket("/ws/observations")
        async def observations_websocket(websocket: WebSocket):
            """WebSocket endpoint for real-time observation events from Beastly Modules."""
            await websocket.accept()
            await self.observation_handler.add_client(websocket)
            
            try:
                # Keep connection alive and handle ping/pong
                while True:
                    try:
                        # Wait for messages from client (ping, etc.)
                        message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                        data = json.loads(message)
                        
                        if data.get('type') == 'ping':
                            await websocket.send_text(json.dumps({'type': 'pong'}))
                        
                    except asyncio.TimeoutError:
                        # Send periodic heartbeat
                        await websocket.send_text(json.dumps({
                            'type': 'heartbeat',
                            'timestamp': datetime.now().isoformat()
                        }))
                    
            except WebSocketDisconnect:
                await self.observation_handler.remove_client(websocket)
            except Exception as e:
                logger.error(f"Observations WebSocket error: {e}")
                await self.observation_handler.remove_client(websocket)
        
        # WebSocket endpoints are now registered using decorators above
        
        logger.info("✅ WebSocket endpoints registered successfully")
        logger.info(f"📊 Registered {len(['/ws/emoji-rain', '/ws/observatory', '/ws/anomalies', '/ws/doctor-status', '/ws/observations'])} WebSocket endpoints")
    
    def _setup_engagement_features(self):
        """Setup engagement features and WebSocket endpoints with error handling."""
        if not self.engagement_integration or not self.engagement_available:
            logger.info("🎯 Engagement features not available")
            return
        
        logger.info("🎯 Setting up engagement features...")
        
        try:
            # Add engagement WebSocket endpoint with error handling
            @self.app.websocket("/ws/engagement")
            async def engagement_websocket(websocket: WebSocket):
                """WebSocket endpoint for real-time engagement updates and data insights."""
                try:
                    await self.engagement_integration.handle_websocket_connection(websocket)
                except Exception as e:
                    logger.error(f"Error in engagement WebSocket connection: {e}")
                    try:
                        await websocket.close(code=1011, reason="Internal server error")
                    except Exception:
                        pass  # Connection might already be closed
        except Exception as e:
            logger.error(f"Failed to setup engagement WebSocket endpoint: {e}")
            self.engagement_available = False
        
        # Add engagement API endpoints with comprehensive error handling
        try:
            @self.app.get("/api/engagement/insights")
            async def get_engagement_insights():
                """Get current engagement insights and discovered patterns."""
                if not self.engagement_integration or not self.engagement_available:
                    raise HTTPException(status_code=503, detail="Engagement system not available")
                
                try:
                    insights = await self.engagement_integration.data_bridge.get_recent_insights()
                    return insights
                except Exception as e:
                    logger.error(f"Error getting engagement insights: {e}")
                    # Return degraded response instead of failing completely
                    return {
                        "patterns": [],
                        "insights": [],
                        "status": "degraded",
                        "error": "Failed to get insights",
                        "timestamp": datetime.now().isoformat()
                    }
            
            @self.app.get("/api/engagement/status")
            async def get_engagement_status():
                """Get engagement system status."""
                if not self.engagement_integration or not self.engagement_available:
                    return {
                        "status": "disabled",
                        "message": "Engagement system not available",
                        "observatory_functional": True,
                        "timestamp": datetime.now().isoformat()
                    }
                
                try:
                    status = await self.engagement_integration._get_system_status()
                    return status
                except Exception as e:
                    logger.error(f"Error getting engagement status: {e}")
                    return {
                        "status": "error",
                        "error": str(e),
                        "observatory_functional": True,
                        "timestamp": datetime.now().isoformat()
                    }
            
            @self.app.post("/api/engagement/data")
            async def inject_engagement_data(data: dict):
                """Inject custom data into the engagement system."""
                if not self.engagement_integration or not self.engagement_available:
                    raise HTTPException(status_code=503, detail="Engagement system not available")
                
                try:
                    data_type = data.get("type", "metrics")
                    data_payload = data.get("data", {})
                    
                    await self.engagement_integration.inject_observatory_data(data_type, data_payload)
                    
                    return {
                        "status": "success",
                        "message": f"Injected {data_type} data",
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"Error injecting engagement data: {e}")
                    return {
                        "status": "error",
                        "message": f"Failed to inject data: {e}",
                        "timestamp": datetime.now().isoformat()
                    }
            
            logger.info("✅ Engagement API endpoints setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup engagement API endpoints: {e}")
            self.engagement_available = False
        
        logger.info("🎯 Engagement features setup complete")

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