#!/usr/bin/env python3
"""
Clean Observatory Startup
=========================

Start Observatory with clean configuration, suppressed warnings, and WebSocket support.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Suppress the annoying Prometheus warnings
logging.getLogger('prometheus_exporter').setLevel(logging.ERROR)

async def start_clean_observatory():
    """Start Observatory with clean configuration and WebSocket support."""
    print("🚀 Starting Clean Observatory with WebSocket support...")
    
    # Set clean environment variables
    os.environ.update({
        'OBSERVATORY_HOST': '0.0.0.0',
        'OBSERVATORY_PORT': '8888',
        'LOG_LEVEL': 'INFO',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'PROMETHEUS_URL': 'http://localhost:9090',
        'DISABLE_PROMETHEUS_LEGACY': 'true',
        'PROMETHEUS_ENABLED': 'true',
        'MONITORING_DAEMON_ENABLED': 'false',  # Disable daemon to suppress warnings
        'METRICS_EXPORT_ENABLED': 'true',
        'WEBSOCKET_ENABLED': 'true',
        'EMOJI_RAIN_ENABLED': 'true',
        'ENGAGEMENT_ENABLED': 'true'
    })
    
    try:
        # Import Observatory components
        from beast_mode.observatory.models import ObservatoryConfig, WebSocketConfig
        from beast_mode.observatory.server import ObservatoryServer
        
        print("✅ Observatory modules imported successfully")
        
        # Create configuration with WebSocket support
        config = ObservatoryConfig()
        config.websocket_config = WebSocketConfig(
            host="0.0.0.0",
            port=8888,
            max_connections=100,
            heartbeat_interval=30
        )
        
        # Create and configure server
        server = ObservatoryServer(config)
        print("✅ Observatory server created with WebSocket support")
        
        # Start the server
        print("🌐 Starting Observatory on http://0.0.0.0:8888")
        print("🔌 WebSocket endpoints available:")
        print("   • /ws/emoji-rain - Emoji rain effects")
        print("   • /ws/engagement - Real-time engagement updates")
        print("   • /ws/observatory - General Observatory updates")
        print("Press Ctrl+C to stop...")
        
        await server.run_server(host="0.0.0.0", port=8888)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔄 Trying fallback FastAPI server with WebSocket support...")
        
        # Fallback: Create minimal FastAPI server with WebSocket
        try:
            from fastapi import FastAPI, WebSocket, WebSocketDisconnect
            from fastapi.responses import JSONResponse
            import uvicorn
            import json
            from typing import List
            
            app = FastAPI(title="Observatory Clean")
            
            # WebSocket connection manager
            class ConnectionManager:
                def __init__(self):
                    self.active_connections: List[WebSocket] = []
                
                async def connect(self, websocket: WebSocket):
                    await websocket.accept()
                    self.active_connections.append(websocket)
                    print(f"🔌 WebSocket connected. Total connections: {len(self.active_connections)}")
                
                def disconnect(self, websocket: WebSocket):
                    self.active_connections.remove(websocket)
                    print(f"🔌 WebSocket disconnected. Total connections: {len(self.active_connections)}")
                
                async def broadcast(self, message: dict):
                    for connection in self.active_connections:
                        try:
                            await connection.send_text(json.dumps(message))
                        except:
                            pass
            
            manager = ConnectionManager()
            
            @app.get("/health")
            async def health():
                return JSONResponse({
                    "status": "ok", 
                    "mode": "clean",
                    "websocket_connections": len(manager.active_connections),
                    "features": ["websockets", "real_time_updates"]
                })
            
            @app.get("/ready")
            async def ready():
                return JSONResponse({
                    "status": "ready", 
                    "mode": "clean",
                    "websocket_support": True
                })
            
            @app.get("/metrics")
            async def metrics():
                return f"""# Observatory clean metrics
observatory_status 1
observatory_websocket_connections {len(manager.active_connections)}
observatory_mode_clean 1
"""
            
            @app.get("/")
            async def dashboard():
                return JSONResponse({
                    "message": "Observatory Clean Dashboard", 
                    "status": "running",
                    "websocket_endpoints": [
                        "/ws/observatory",
                        "/ws/emoji-rain", 
                        "/ws/engagement"
                    ],
                    "active_connections": len(manager.active_connections)
                })
            
            @app.websocket("/ws/observatory")
            async def websocket_observatory(websocket: WebSocket):
                await manager.connect(websocket)
                try:
                    # Send welcome message
                    await websocket.send_text(json.dumps({
                        "type": "welcome",
                        "message": "Connected to Observatory WebSocket",
                        "timestamp": str(asyncio.get_event_loop().time())
                    }))
                    
                    # Keep connection alive and handle messages
                    while True:
                        data = await websocket.receive_text()
                        message = json.loads(data)
                        
                        # Echo back with timestamp
                        response = {
                            "type": "echo",
                            "original": message,
                            "timestamp": str(asyncio.get_event_loop().time()),
                            "connection_id": id(websocket)
                        }
                        await websocket.send_text(json.dumps(response))
                        
                except WebSocketDisconnect:
                    manager.disconnect(websocket)
            
            @app.websocket("/ws/emoji-rain")
            async def websocket_emoji_rain(websocket: WebSocket):
                await manager.connect(websocket)
                try:
                    # Send emoji rain updates
                    import random
                    emojis = ["🌟", "⭐", "✨", "💫", "🎉", "🎊", "🚀", "🔥"]
                    
                    await websocket.send_text(json.dumps({
                        "type": "emoji_rain_start",
                        "message": "Emoji rain WebSocket connected"
                    }))
                    
                    while True:
                        data = await websocket.receive_text()
                        # Send random emoji
                        response = {
                            "type": "emoji_rain",
                            "emoji": random.choice(emojis),
                            "x": random.randint(0, 100),
                            "y": random.randint(0, 100),
                            "timestamp": str(asyncio.get_event_loop().time())
                        }
                        await websocket.send_text(json.dumps(response))
                        
                except WebSocketDisconnect:
                    manager.disconnect(websocket)
            
            @app.websocket("/ws/engagement")
            async def websocket_engagement(websocket: WebSocket):
                await manager.connect(websocket)
                try:
                    await websocket.send_text(json.dumps({
                        "type": "engagement_start",
                        "message": "Engagement WebSocket connected",
                        "features": ["real_time_insights", "pattern_discovery"]
                    }))
                    
                    while True:
                        data = await websocket.receive_text()
                        # Send engagement update
                        response = {
                            "type": "engagement_update",
                            "insight": "WebSocket communication is working perfectly!",
                            "confidence": 0.95,
                            "timestamp": str(asyncio.get_event_loop().time())
                        }
                        await websocket.send_text(json.dumps(response))
                        
                except WebSocketDisconnect:
                    manager.disconnect(websocket)
            
            print("✅ Clean FastAPI server with WebSocket support created")
            print("🌐 Starting clean server on http://0.0.0.0:8888")
            print("🔌 WebSocket endpoints ready for real-time communication")
            
            # Run the server
            config = uvicorn.Config(app, host="0.0.0.0", port=8888, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            print(f"❌ Fallback server failed: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Observatory startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        asyncio.run(start_clean_observatory())
    except KeyboardInterrupt:
        print("\n🛑 Observatory stopped gracefully")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)