#!/usr/bin/env python3
"""
Debug script for emoji rain system with detailed logging.
"""

import asyncio
import logging
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from beast_mode.observatory.emoji_rain import EmojiRainEngine, EmojiRainWebSocketHandler
from beast_mode.observatory.models import CoordinationEvent, CoordinationEventType

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('emoji_rain_debug.log')
    ]
)

logger = logging.getLogger(__name__)

class MockWebSocket:
    """Mock WebSocket for testing."""
    
    def __init__(self, name: str):
        self.name = name
        self.messages = []
    
    async def send(self, message: str):
        """Mock send method."""
        self.messages.append(message)
        logger.info(f"📨 MockWebSocket {self.name} received: {message[:100]}...")

async def test_emoji_rain_with_websocket():
    """Test emoji rain engine with WebSocket handler."""
    logger.info("🚀 Starting detailed emoji rain debug test")
    
    # Create engine
    engine = EmojiRainEngine()
    
    # Create WebSocket handler
    ws_handler = EmojiRainWebSocketHandler(engine)
    
    # Create mock WebSocket clients
    client1 = MockWebSocket("client1")
    client2 = MockWebSocket("client2")
    
    # Add clients to handler
    await ws_handler.add_client(client1)
    await ws_handler.add_client(client2)
    
    logger.info(f"📊 Engine stats before starting: {engine.get_performance_stats()}")
    
    # Start animation loop
    await engine.start_animation_loop()
    
    # Wait a moment for loop to start
    await asyncio.sleep(0.1)
    
    # Create a test event
    test_event = CoordinationEvent(
        event_id="test-123",
        event_type=CoordinationEventType.TASK_COMPLETED,
        timestamp=datetime.now(),
        source_component="debug_test",
        event_data={"task": "test_task", "success": True}
    )
    
    logger.info("🎯 Triggering emoji rain...")
    effect_id = await engine.trigger_event_rain(test_event)
    logger.info(f"✨ Created effect: {effect_id}")
    
    # Let it run for a few seconds to see frame updates
    logger.info("⏱️ Running for 5 seconds to observe frame updates...")
    for i in range(50):  # 5 seconds at ~10 checks per second
        await asyncio.sleep(0.1)
        
        if i % 10 == 0:  # Log every second
            stats = engine.get_performance_stats()
            active_effects = engine.get_active_effects()
            logger.info(f"📊 Second {i//10}: {stats['total_particles']} particles, {len(active_effects)} effects")
            
            # Check if clients received messages
            logger.info(f"📨 Client1 messages: {len(client1.messages)}, Client2 messages: {len(client2.messages)}")
    
    # Stop the engine
    await engine.stop_animation_loop()
    
    # Final report
    logger.info(f"🏁 Final client1 message count: {len(client1.messages)}")
    logger.info(f"🏁 Final client2 message count: {len(client2.messages)}")
    
    if client1.messages:
        logger.info(f"📄 Sample message: {client1.messages[0][:200]}...")
    else:
        logger.error("❌ No messages received by clients!")

if __name__ == "__main__":
    asyncio.run(test_emoji_rain_with_websocket())