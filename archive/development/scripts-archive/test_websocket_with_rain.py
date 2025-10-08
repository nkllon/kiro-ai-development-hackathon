#!/usr/bin/env python3
"""
Test WebSocket integration with actual emoji rain.
"""

import asyncio
import json
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from beast_mode.observatory.emoji_rain import EmojiRainEngine, EmojiRainWebSocketHandler
from beast_mode.observatory.models import CoordinationEvent, CoordinationEventType

class MockWebSocket:
    """Mock WebSocket for testing."""
    
    def __init__(self, name: str):
        self.name = name
        self.messages = []
        self.particle_frames = []
    
    async def send(self, message: str):
        """Mock send method."""
        self.messages.append(message)
        data = json.loads(message)
        if data.get('type') == 'emoji_rain_frame' and data.get('data', {}).get('total_particles', 0) > 0:
            self.particle_frames.append(data)
            print(f"🎊 {self.name} received frame with {data['data']['total_particles']} particles!")

async def test_websocket_with_rain():
    """Test WebSocket integration with actual emoji rain."""
    print("🚀 Starting WebSocket + emoji rain test")
    
    # Create engine and WebSocket handler
    engine = EmojiRainEngine()
    ws_handler = EmojiRainWebSocketHandler(engine)
    
    # Create mock WebSocket client
    client = MockWebSocket("test_client")
    await ws_handler.add_client(client)
    
    # Start animation loop
    await engine.start_animation_loop()
    await asyncio.sleep(0.1)
    
    # Trigger emoji rain
    test_event = CoordinationEvent(
        event_type=CoordinationEventType.ACHIEVEMENT_UNLOCKED,  # This should be intense!
        source_component="test"
    )
    
    print("🏆 Triggering ACHIEVEMENT_UNLOCKED emoji rain...")
    effect_id = await engine.trigger_event_rain(test_event)
    print(f"✨ Created effect: {effect_id}")
    
    # Let it run and collect frames
    print("⏱️ Collecting frames for 3 seconds...")
    for i in range(30):  # 3 seconds
        await asyncio.sleep(0.1)
        if i % 10 == 0:
            stats = engine.get_performance_stats()
            print(f"📈 Second {i//10}: {stats['total_particles']} particles, {len(client.particle_frames)} frames with particles")
    
    # Stop the engine
    await engine.stop_animation_loop()
    
    # Report results
    print(f"\n🎯 RESULTS:")
    print(f"📨 Total messages: {len(client.messages)}")
    print(f"🎊 Frames with particles: {len(client.particle_frames)}")
    
    if client.particle_frames:
        sample_frame = client.particle_frames[0]
        particles = sample_frame['data']['effects'][0]['particles'][:3]  # First 3 particles
        print(f"🎨 Sample particles: {particles}")
        print("✅ SUCCESS: WebSocket is receiving emoji rain frames!")
    else:
        print("❌ FAILED: No particle frames received")

if __name__ == "__main__":
    asyncio.run(test_websocket_with_rain())