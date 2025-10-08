#!/usr/bin/env python3
"""
Test WebSocket message handling to debug the frontend issue.
"""

import asyncio
import json
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from beast_mode.observatory.server import ObservatoryServer
from beast_mode.observatory.config import load_observatory_config

class MockWebSocket:
    """Mock WebSocket for testing message handling."""
    
    def __init__(self):
        self.sent_messages = []
        self.received_messages = []
    
    async def accept(self):
        """Mock accept method."""
        pass
    
    async def send_text(self, message: str):
        """Mock send_text method."""
        self.sent_messages.append(message)
        print(f"📤 Server sent: {message[:100]}...")
    
    async def receive_text(self):
        """Mock receive_text method."""
        if self.received_messages:
            return self.received_messages.pop(0)
        else:
            # Simulate WebSocketDisconnect after processing messages
            from fastapi import WebSocketDisconnect
            raise WebSocketDisconnect()
    
    def queue_message(self, message: dict):
        """Queue a message to be received."""
        self.received_messages.append(json.dumps(message))

async def test_websocket_message_handling():
    """Test WebSocket message handling."""
    print("🚀 Testing WebSocket message handling")
    
    # Create server
    config = load_observatory_config()
    server = ObservatoryServer(config)
    
    # Start the server components
    await server.emoji_engine.start_animation_loop()
    await server.observatory_core.start_observatory()
    
    # Create mock WebSocket
    mock_ws = MockWebSocket()
    
    # Test message that frontend would send
    test_message = {
        "type": "trigger_test_rain",
        "event_type": "TASK_COMPLETED",
        "data": {
            "source": "test",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    print(f"📨 Queuing test message: {test_message}")
    mock_ws.queue_message(test_message)
    
    # Test the message handling directly
    try:
        await server._handle_websocket_message(mock_ws, test_message)
        print("✅ Message handled successfully")
        
        # Check if emoji rain was triggered
        active_effects = server.emoji_engine.get_active_effects()
        stats = server.emoji_engine.get_performance_stats()
        
        print(f"📊 Active effects: {len(active_effects)}")
        print(f"📊 Total particles: {stats['total_particles']}")
        print(f"📊 Animation running: {stats['animation_running']}")
        
        if len(active_effects) > 0:
            print("🎉 SUCCESS: Emoji rain was triggered!")
            print(f"🎨 Effect details: {active_effects}")
        else:
            print("❌ FAILED: No emoji rain effects created")
        
        # Check sent messages
        print(f"📤 Server sent {len(mock_ws.sent_messages)} messages")
        for i, msg in enumerate(mock_ws.sent_messages):
            data = json.loads(msg)
            print(f"  {i+1}. {data.get('type', 'unknown')}: {data}")
        
    except Exception as e:
        print(f"❌ Error handling message: {e}")
        import traceback
        traceback.print_exc()
    
    # Stop server components
    await server.emoji_engine.stop_animation_loop()
    await server.observatory_core.stop_observatory()

if __name__ == "__main__":
    asyncio.run(test_websocket_message_handling())