#!/usr/bin/env python3
"""
Simple test to trigger emoji rain and see if it works.
"""

import asyncio
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from beast_mode.observatory.emoji_rain import EmojiRainEngine, EmojiRainWebSocketHandler
from beast_mode.observatory.models import CoordinationEvent, CoordinationEventType

async def test_trigger_rain():
    """Test triggering emoji rain."""
    print("🚀 Starting emoji rain trigger test")
    
    # Create engine
    engine = EmojiRainEngine()
    
    # Start animation loop
    await engine.start_animation_loop()
    
    # Wait a moment for loop to start
    await asyncio.sleep(0.1)
    
    # Create a test event
    test_event = CoordinationEvent(
        event_type=CoordinationEventType.TASK_COMPLETED,
        source_component="test"
    )
    
    print("🎯 Triggering emoji rain...")
    effect_id = await engine.trigger_event_rain(test_event)
    print(f"✨ Created effect: {effect_id}")
    
    # Check active effects
    active_effects = engine.get_active_effects()
    print(f"📊 Active effects: {active_effects}")
    
    # Let it run for 2 seconds
    print("⏱️ Running for 2 seconds...")
    for i in range(20):
        await asyncio.sleep(0.1)
        if i % 10 == 0:
            stats = engine.get_performance_stats()
            print(f"📈 Particles: {stats['total_particles']}, Effects: {stats['active_effects']}")
    
    # Stop the engine
    await engine.stop_animation_loop()
    print("✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_trigger_rain())