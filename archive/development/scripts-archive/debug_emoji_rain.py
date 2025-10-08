#!/usr/bin/env python3
"""
Debug script to test emoji rain WebSocket broadcasting.
"""

import asyncio
import json
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.DEBUG)

from src.beast_mode.observatory.emoji_rain import EmojiRainEngine, EmojiRainWebSocketHandler
from src.beast_mode.observatory.models import CoordinationEvent, CoordinationEventType


async def debug_emoji_rain():
    """Debug the emoji rain WebSocket broadcasting."""
    print("🔍 Starting emoji rain debug...")
    
    # Create emoji engine
    emoji_engine = EmojiRainEngine()
    
    # Create WebSocket handler
    ws_handler = EmojiRainWebSocketHandler(emoji_engine)
    
    # Create a mock WebSocket client
    class MockWebSocket:
        def __init__(self):
            self.messages = []
        
        async def send(self, message):
            self.messages.append(message)
            print(f"📨 WebSocket would send: {message}")
    
    mock_client = MockWebSocket()
    await ws_handler.add_client(mock_client)
    
    # Start animation loop
    await emoji_engine.start_animation_loop()
    print("✅ Animation loop started")
    
    # Trigger some rain
    event = CoordinationEvent(
        event_type=CoordinationEventType.ACHIEVEMENT_UNLOCKED,
        source_component="debug_test"
    )
    
    effect_id = await emoji_engine.trigger_event_rain(event)
    print(f"🌧️ Triggered rain: {effect_id}")
    
    # Check active effects
    effects = emoji_engine.get_active_effects()
    print(f"📊 Active effects: {len(effects)}")
    for effect_id, effect_info in effects.items():
        print(f"   {effect_id}: {effect_info['particle_count']} particles")
    
    # Wait for a few animation frames
    print("⏱️ Waiting for animation frames...")
    await asyncio.sleep(2)
    
    # Check if WebSocket received any messages
    print(f"📨 WebSocket received {len(mock_client.messages)} messages")
    for i, message in enumerate(mock_client.messages):
        data = json.loads(message)
        print(f"   Message {i}: {data['type']}")
        if data['type'] == 'emoji_rain_frame':
            print(f"      Effects: {data['data']['active_effects']}, Particles: {data['data']['total_particles']}")
    
    # Stop animation
    await emoji_engine.stop_animation_loop()
    print("✅ Debug complete")


if __name__ == "__main__":
    asyncio.run(debug_emoji_rain())