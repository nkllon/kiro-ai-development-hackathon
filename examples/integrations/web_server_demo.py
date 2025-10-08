#!/usr/bin/env python3
"""
Observatory Web Server Demo

This script demonstrates the full FastAPI web server with emoji rain,
WebSocket connections, and all API endpoints.
"""

import asyncio
import json
import logging
import time
from pathlib import Path

import httpx
import websockets

from src.beast_mode.observatory.server import create_server


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_api_endpoints():
    """Test all API endpoints."""
    base_url = "http://localhost:8080"
    
    async with httpx.AsyncClient() as client:
        logger.info("🧪 Testing API endpoints...")
        
        # Test health endpoint
        logger.info("📊 Testing health endpoint...")
        response = await client.get(f"{base_url}/health")
        assert response.status_code == 200
        health_data = response.json()
        logger.info(f"✅ Health: {health_data['status']} - Observatory: {health_data['observatory']['status']}")
        
        # Test Observatory status
        logger.info("🔍 Testing Observatory status...")
        response = await client.get(f"{base_url}/api/observatory/status")
        assert response.status_code == 200
        status_data = response.json()
        logger.info(f"✅ Observatory health score: {status_data['health']['health_score']}")
        
        # Test emoji rain stats
        logger.info("🌧️ Testing emoji rain stats...")
        response = await client.get(f"{base_url}/api/emoji-rain/stats")
        assert response.status_code == 200
        stats_data = response.json()
        logger.info(f"✅ Emoji rain: {stats_data['active_effects']} effects, {stats_data['total_particles']} particles")
        
        # Test event types
        logger.info("📋 Testing event types...")
        response = await client.get(f"{base_url}/api/emoji-rain/event-types")
        assert response.status_code == 200
        event_types = response.json()
        logger.info(f"✅ Available event types: {len(event_types['event_types'])}")
        
        # Test triggering emoji rain
        logger.info("🎉 Testing emoji rain triggers...")
        test_events = [
            {"event_type": "TASK_COMPLETED", "data": {"task": "demo_task_1"}},
            {"event_type": "API_CALL_SUCCESS", "data": {"api": "demo_api"}},
            {"event_type": "ACHIEVEMENT_UNLOCKED", "data": {"achievement": "demo_achievement"}},
        ]
        
        for event_data in test_events:
            response = await client.post(f"{base_url}/api/emoji-rain/trigger", json=event_data)
            assert response.status_code == 200
            result = response.json()
            logger.info(f"✅ Triggered {event_data['event_type']}: {result['effect_id']}")
            await asyncio.sleep(0.5)
        
        # Test achievement celebration
        logger.info("🏆 Testing achievement celebration...")
        achievement_data = {
            "name": "API Demo Master",
            "description": "Successfully tested all API endpoints",
            "icon_emoji": "🎯",
            "user_id": "demo_user"
        }
        
        response = await client.post(f"{base_url}/api/emoji-rain/achievement", json=achievement_data)
        assert response.status_code == 200
        result = response.json()
        logger.info(f"✅ Achievement celebration: {result['achievement']['name']}")
        
        logger.info("🎊 All API endpoints tested successfully!")


async def test_websocket_connection():
    """Test WebSocket connection and real-time updates."""
    ws_url = "ws://localhost:8080/ws/emoji-rain"
    
    logger.info("🔌 Testing WebSocket connection...")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            logger.info("✅ WebSocket connected!")
            
            # Wait for initial state message
            initial_message = await websocket.recv()
            initial_data = json.loads(initial_message)
            logger.info(f"📨 Received initial state: {initial_data['type']}")
            
            # Send ping
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            
            # Wait for pong
            pong_message = await websocket.recv()
            pong_data = json.loads(pong_message)
            assert pong_data["type"] == "pong"
            logger.info("✅ Ping/pong successful")
            
            # Trigger test rain via WebSocket
            test_rain_message = {
                "type": "trigger_test_rain",
                "event_type": "COORDINATION_MILESTONE",
                "data": {"websocket_test": True}
            }
            await websocket.send(json.dumps(test_rain_message))
            
            # Wait for response
            response_message = await websocket.recv()
            response_data = json.loads(response_message)
            assert response_data["type"] == "test_rain_triggered"
            assert response_data["data"]["success"] is True
            logger.info(f"✅ WebSocket rain trigger: {response_data['data']['effect_id']}")
            
            # Set canvas size
            canvas_message = {
                "type": "set_canvas_size",
                "width": 1600,
                "height": 900
            }
            await websocket.send(json.dumps(canvas_message))
            logger.info("✅ Canvas size updated via WebSocket")
            
            # Listen for a few frame updates
            logger.info("👂 Listening for frame updates...")
            frame_count = 0
            
            while frame_count < 5:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    
                    if data["type"] == "emoji_rain_frame":
                        frame_count += 1
                        frame_data = data["data"]
                        logger.info(f"🎬 Frame {frame_count}: {frame_data['active_effects']} effects, {frame_data['total_particles']} particles")
                    
                except asyncio.TimeoutError:
                    logger.info("⏰ No frame updates received (timeout)")
                    break
            
            logger.info("🎊 WebSocket testing completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")


async def run_demo_server():
    """Run the demo server for a short time."""
    logger.info("🚀 Starting Observatory Server Demo...")
    
    # Create server
    config_path = Path(__file__).parent.parent / "config" / "observatory.yaml"
    server = create_server(str(config_path))
    
    # Start server in background
    server_task = asyncio.create_task(
        server.run_server(host="127.0.0.1", port=8080)
    )
    
    # Wait a moment for server to start
    await asyncio.sleep(2)
    
    try:
        # Test API endpoints
        await test_api_endpoints()
        
        # Test WebSocket
        await test_websocket_connection()
        
        # Let the server run for a bit to see emoji rain
        logger.info("⏱️ Letting server run for 10 seconds to see emoji rain...")
        await asyncio.sleep(10)
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
    
    finally:
        # Stop server
        logger.info("🛑 Stopping demo server...")
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
        
        logger.info("✅ Demo completed!")


async def interactive_demo():
    """Run an interactive demo where user can trigger events."""
    logger.info("🎮 Starting Interactive Observatory Demo...")
    logger.info("🌐 Visit http://localhost:8080 to see the web interface!")
    logger.info("🎯 Use the buttons on the web page to trigger emoji rain")
    logger.info("⏹️ Press Ctrl+C to stop the demo")
    
    # Create and run server
    config_path = Path(__file__).parent.parent / "config" / "observatory.yaml"
    server = create_server(str(config_path))
    
    try:
        await server.run_server(host="0.0.0.0", port=8080)
    except KeyboardInterrupt:
        logger.info("👋 Demo stopped by user")


async def main():
    """Main demo function."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        await interactive_demo()
    else:
        await run_demo_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Demo interrupted by user")
    except Exception as e:
        logger.error(f"💥 Demo crashed: {e}")
        exit(1)