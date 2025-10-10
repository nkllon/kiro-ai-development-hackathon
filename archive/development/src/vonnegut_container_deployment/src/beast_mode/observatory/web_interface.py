"""
Observatory Web Interface - Serves the delightful emoji rain dashboard.

This module provides the FastAPI web server and WebSocket endpoints for
real-time emoji rain visualization and Observatory monitoring.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from .emoji_rain import EmojiRainEngine, EmojiRainWebSocketHandler
from .models import ObservatoryConfig, CoordinationEvent


logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Create dummy classes for type annotations
    class FastAPI: pass
    class WebSocket: pass
    class WebSocketDisconnect(Exception): pass
    class Request: pass
    class HTMLResponse: pass
    class FileResponse: pass
    class StaticFiles: pass
    class Jinja2Templates: pass
    logger.warning("FastAPI not available. Web interface will not work. Install with: pip install fastapi uvicorn")


class ObservatoryWebInterface:
    """Web interface for the Beast Mode Coordination Observatory."""
    
    def __init__(self, config: ObservatoryConfig, emoji_engine: EmojiRainEngine):
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for web interface. Install with: pip install fastapi uvicorn")
        
        self.config = config
        self.emoji_engine = emoji_engine
        self.app = FastAPI(
            title=config.web_interface_config.title,
            description="Real-time coordination monitoring with delightful emoji rain",
            version="1.0.0"
        )
        
        # WebSocket handler for emoji rain
        self.emoji_ws_handler = EmojiRainWebSocketHandler(emoji_engine)
        
        # Setup routes
        self._setup_routes()
        self._setup_websockets()
        
        # Templates and static files
        self.templates_dir = Path(__file__).parent / "templates"
        self.static_dir = Path(__file__).parent / "static"
        
        # Create directories if they don't exist
        self.templates_dir.mkdir(exist_ok=True)
        self.static_dir.mkdir(exist_ok=True)
        
        # Setup Jinja2 templates
        self.templates = Jinja2Templates(directory=str(self.templates_dir))
        
        # Mount static files
        self.app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")
        
        logger.info(f"🌐 Observatory Web Interface initialized on port {config.websocket_config.port}")
    
    def _setup_routes(self) -> None:
        """Setup HTTP routes for the web interface."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Serve the main Observatory dashboard."""
            return self.templates.TemplateResponse("dashboard.html", {
                "request": request,
                "title": self.config.web_interface_config.title,
                "theme": self.config.web_interface_config.theme,
                "refresh_rate": self.config.web_interface_config.refresh_rate_ms,
                "emoji_rain_enabled": self.config.gamification_config.emoji_rain_enabled
            })
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "emoji_rain_active": self.emoji_engine._running,
                "active_effects": len(self.emoji_engine._active_effects),
                "connected_clients": len(self.emoji_ws_handler.connected_clients)
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
                # Create a test coordination event
                from .models import CoordinationEventType
                
                event_type_name = event_data.get("event_type", "TASK_COMPLETED")
                event_type = CoordinationEventType[event_type_name]
                
                event = CoordinationEvent(
                    event_type=event_type,
                    source_component="web_interface_test",
                    event_data=event_data.get("data", {})
                )
                
                effect_id = await self.emoji_engine.trigger_event_rain(event)
                
                return {
                    "success": True,
                    "effect_id": effect_id,
                    "event_type": event_type_name
                }
                
            except Exception as e:
                logger.error(f"Failed to trigger emoji rain: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def _setup_websockets(self) -> None:
        """Setup WebSocket endpoints for real-time updates."""
        
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
                        "performance_stats": self.emoji_engine.get_performance_stats()
                    }
                }
                await websocket.send_text(json.dumps(initial_data))
                
                # Keep connection alive and handle incoming messages
                while True:
                    try:
                        # Wait for messages from client
                        message = await websocket.receive_text()
                        data = json.loads(message)
                        
                        # Handle client messages
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
    
    async def _handle_websocket_message(self, websocket: WebSocket, data: Dict[str, Any]) -> None:
        """Handle incoming WebSocket messages from clients."""
        message_type = data.get("type")
        
        if message_type == "ping":
            # Respond to ping with pong
            await websocket.send_text(json.dumps({"type": "pong"}))
            
        elif message_type == "trigger_test_rain":
            # Trigger test emoji rain
            event_type_name = data.get("event_type", "TASK_COMPLETED")
            try:
                from .models import CoordinationEventType
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
        
        elif message_type == "set_canvas_size":
            # Update canvas dimensions
            width = data.get("width", 1920)
            height = data.get("height", 1080)
            self.emoji_engine.set_canvas_size(width, height)
            
        else:
            logger.warning(f"Unknown WebSocket message type: {message_type}")
    
    async def start_server(self) -> None:
        """Start the web server and emoji rain engine."""
        # Start emoji rain animation loop
        await self.emoji_engine.start_animation_loop()
        
        logger.info(f"🚀 Observatory web interface ready at http://localhost:{self.config.websocket_config.port}")
        logger.info("🌧️ Emoji rain engine is running - ready to make it rain!")
    
    async def stop_server(self) -> None:
        """Stop the web server and emoji rain engine."""
        await self.emoji_engine.stop_animation_loop()
        logger.info("🛑 Observatory web interface stopped")


def create_dashboard_html() -> str:
    """Create the HTML template for the Observatory dashboard."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: {% if theme == 'dark' %}#1a1a1a{% else %}#f5f5f5{% endif %};
            color: {% if theme == 'dark' %}#ffffff{% else %}#333333{% endif %};
            overflow: hidden;
        }
        
        #emoji-rain-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 1000;
        }
        
        .dashboard-container {
            position: relative;
            z-index: 1;
            padding: 20px;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
        }
        
        .btn-secondary {
            background: linear-gradient(45deg, #45b7d1, #96ceb4);
            color: white;
        }
        
        .btn-success {
            background: linear-gradient(45deg, #2ecc71, #27ae60);
            color: white;
        }
        
        .btn-warning {
            background: linear-gradient(45deg, #f39c12, #e67e22);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: {% if theme == 'dark' %}rgba(255,255,255,0.1){% else %}rgba(0,0,0,0.05){% endif %};
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid {% if theme == 'dark' %}rgba(255,255,255,0.2){% else %}rgba(0,0,0,0.1){% endif %};
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            opacity: 0.8;
            font-size: 0.9em;
        }
        
        .emoji-particle {
            position: absolute;
            font-size: 24px;
            pointer-events: none;
            user-select: none;
            z-index: 1000;
        }
        
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            z-index: 1001;
        }
        
        .connected {
            background: #2ecc71;
            color: white;
        }
        
        .disconnected {
            background: #e74c3c;
            color: white;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .dashboard-container > * {
            animation: fadeInUp 0.6s ease-out;
        }
    </style>
</head>
<body>
    <canvas id="emoji-rain-canvas"></canvas>
    
    <div class="connection-status" id="connectionStatus">
        🔌 Connecting...
    </div>
    
    <div class="dashboard-container">
        <div class="header">
            <h1>🌧️ {{ title }} 🌧️</h1>
            <p>Making systematic coordination delightfully engaging</p>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="triggerRain('TASK_COMPLETED')">
                ✅ Task Completed
            </button>
            <button class="btn btn-secondary" onclick="triggerRain('API_CALL_SUCCESS')">
                ⚡ API Success
            </button>
            <button class="btn btn-success" onclick="triggerRain('ACHIEVEMENT_UNLOCKED')">
                🏆 Achievement
            </button>
            <button class="btn btn-warning" onclick="triggerRain('COORDINATION_MILESTONE')">
                🎯 Milestone
            </button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="activeEffects">0</div>
                <div class="stat-label">Active Effects</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalParticles">0</div>
                <div class="stat-label">Total Particles</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="connectedClients">0</div>
                <div class="stat-label">Connected Clients</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="frameRate">60</div>
                <div class="stat-label">Target FPS</div>
            </div>
        </div>
    </div>
    
    <script>
        class EmojiRainRenderer {
            constructor() {
                this.canvas = document.getElementById('emoji-rain-canvas');
                this.ctx = this.canvas.getContext('2d');
                this.particles = [];
                this.websocket = null;
                this.connected = false;
                
                this.setupCanvas();
                this.connectWebSocket();
                this.startRenderLoop();
            }
            
            setupCanvas() {
                this.resizeCanvas();
                window.addEventListener('resize', () => this.resizeCanvas());
            }
            
            resizeCanvas() {
                this.canvas.width = window.innerWidth;
                this.canvas.height = window.innerHeight;
                
                // Notify server of canvas size change
                if (this.websocket && this.connected) {
                    this.websocket.send(JSON.stringify({
                        type: 'set_canvas_size',
                        width: this.canvas.width,
                        height: this.canvas.height
                    }));
                }
            }
            
            connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/emoji-rain`;
                
                this.websocket = new WebSocket(wsUrl);
                
                this.websocket.onopen = () => {
                    this.connected = true;
                    this.updateConnectionStatus(true);
                    console.log('🌧️ Connected to emoji rain WebSocket');
                };
                
                this.websocket.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                };
                
                this.websocket.onclose = () => {
                    this.connected = false;
                    this.updateConnectionStatus(false);
                    console.log('🌧️ Disconnected from emoji rain WebSocket');
                    
                    // Reconnect after 3 seconds
                    setTimeout(() => this.connectWebSocket(), 3000);
                };
                
                this.websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }
            
            handleWebSocketMessage(message) {
                switch (message.type) {
                    case 'emoji_rain_frame':
                        this.updateParticles(message.data);
                        break;
                    case 'initial_state':
                        this.updateStats(message.data.performance_stats);
                        break;
                    case 'test_rain_triggered':
                        console.log('Test rain triggered:', message.data);
                        break;
                }
            }
            
            updateParticles(frameData) {
                this.particles = [];
                
                frameData.effects.forEach(effect => {
                    effect.particles.forEach(particle => {
                        this.particles.push({
                            emoji: particle.emoji,
                            x: particle.x * this.canvas.width,
                            y: particle.y * this.canvas.height,
                            rotation: particle.rotation,
                            scale: particle.scale,
                            opacity: particle.opacity
                        });
                    });
                });
                
                // Update stats
                document.getElementById('activeEffects').textContent = frameData.active_effects;
                document.getElementById('totalParticles').textContent = frameData.total_particles;
            }
            
            updateStats(stats) {
                if (stats.active_effects !== undefined) {
                    document.getElementById('activeEffects').textContent = stats.active_effects;
                }
                if (stats.total_particles !== undefined) {
                    document.getElementById('totalParticles').textContent = stats.total_particles;
                }
                if (stats.target_fps !== undefined) {
                    document.getElementById('frameRate').textContent = stats.target_fps;
                }
            }
            
            updateConnectionStatus(connected) {
                const status = document.getElementById('connectionStatus');
                if (connected) {
                    status.textContent = '🟢 Connected';
                    status.className = 'connection-status connected';
                } else {
                    status.textContent = '🔴 Disconnected';
                    status.className = 'connection-status disconnected';
                }
            }
            
            startRenderLoop() {
                const render = () => {
                    this.renderFrame();
                    requestAnimationFrame(render);
                };
                render();
            }
            
            renderFrame() {
                // Clear canvas
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Render particles
                this.particles.forEach(particle => {
                    this.ctx.save();
                    
                    // Apply transformations
                    this.ctx.translate(particle.x, particle.y);
                    this.ctx.rotate(particle.rotation * Math.PI / 180);
                    this.ctx.scale(particle.scale, particle.scale);
                    this.ctx.globalAlpha = particle.opacity;
                    
                    // Draw emoji
                    this.ctx.font = '24px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.textBaseline = 'middle';
                    this.ctx.fillText(particle.emoji, 0, 0);
                    
                    this.ctx.restore();
                });
            }
        }
        
        // Global functions
        function triggerRain(eventType) {
            if (window.emojiRenderer && window.emojiRenderer.websocket && window.emojiRenderer.connected) {
                window.emojiRenderer.websocket.send(JSON.stringify({
                    type: 'trigger_test_rain',
                    event_type: eventType,
                    data: {
                        source: 'dashboard_button',
                        timestamp: new Date().toISOString()
                    }
                }));
            } else {
                console.warn('WebSocket not connected');
            }
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', () => {
            window.emojiRenderer = new EmojiRainRenderer();
        });
    </script>
</body>
</html>
    """