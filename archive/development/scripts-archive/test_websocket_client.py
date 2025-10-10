#!/usr/bin/env python3
"""
Test WebSocket client to debug the frontend issue.
"""

import asyncio
import json
import websockets
from datetime import datetime

async def test_websocket_client():
    """Test WebSocket client that mimics the frontend."""
    uri = "ws://localhost:55857/ws/emoji-rain"
    
    try:
        print(f"🔌 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Send trigger message
            message = {
                "type": "trigger_test_rain",
                "event_type": "TASK_COMPLETED",
                "data": {
                    "source": "test_client",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            print(f"📤 Sending: {message}")
            await websocket.send(json.dumps(message))
            
            # Listen for responses
            print("👂 Listening for responses...")
            particle_frames = 0
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    msg_type = data.get('type', 'unknown')
                    
                    if msg_type == 'initial_state':
                        print(f"📊 Initial state: {data['data']['performance_stats']}")
                    elif msg_type == 'test_rain_triggered':
                        print(f"🌧️ Rain triggered: {data['data']}")
                    elif msg_type == 'emoji_rain_frame':
                        frame_data = data['data']
                        if frame_data['total_particles'] > 0:
                            particle_frames += 1
                            print(f"🎊 Frame {particle_frames}: {frame_data['total_particles']} particles, {frame_data['active_effects']} effects")
                            
                            # Show first particle details
                            if frame_data['effects'] and frame_data['effects'][0]['particles']:
                                first_particle = frame_data['effects'][0]['particles'][0]
                                print(f"   First particle: {first_particle['emoji']} at ({first_particle['x']:.2f}, {first_particle['y']:.2f})")
                        
                        # Stop after 50 frames or when no more particles
                        if particle_frames >= 50 or (particle_frames > 0 and frame_data['total_particles'] == 0):
                            print(f"🏁 Stopping after {particle_frames} particle frames")
                            break
                    else:
                        print(f"📨 Received: {msg_type}")
                        
            except websockets.exceptions.ConnectionClosed:
                print("🔌 Connection closed")
            
            print(f"✅ Test complete! Received {particle_frames} frames with particles")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_client())