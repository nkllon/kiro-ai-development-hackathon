#!/usr/bin/env python3
"""
Emoji Rain Demo - Make it rain emojis!

This script demonstrates the delightful emoji rain system that transforms
coordination events into beautiful, cascading visual celebrations.
"""

import asyncio
import logging
from pathlib import Path

from src.beast_mode.observatory import (
    EmojiRainEngine,
    CoordinationEvent,
    CoordinationEventType,
    Achievement,
    load_observatory_config,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_emoji_rain():
    """Demonstrate the emoji rain system."""
    logger.info("🌧️ Starting Emoji Rain Demo - Let's make it rain!")
    
    try:
        # Create emoji rain engine
        emoji_engine = EmojiRainEngine()
        logger.info("✅ Emoji Rain Engine created")
        
        # Start animation loop
        await emoji_engine.start_animation_loop()
        logger.info("🎬 Animation loop started at 60 FPS")
        
        # Register a callback to log frame updates
        frame_count = 0
        
        def log_frame_update(frame_data):
            nonlocal frame_count
            frame_count += 1
            if frame_count % 60 == 0:  # Log every second
                logger.info(f"📊 Frame {frame_count}: {frame_data['active_effects']} effects, {frame_data['total_particles']} particles")
        
        emoji_engine.register_animation_callback(log_frame_update)
        
        # Demo different coordination events
        events_to_demo = [
            (CoordinationEventType.TASK_COMPLETED, "Task completed successfully! 🎉"),
            (CoordinationEventType.API_CALL_SUCCESS, "API call blazing fast! ⚡"),
            (CoordinationEventType.COORDINATION_MILESTONE, "Team coordination milestone! 🎯"),
            (CoordinationEventType.ACHIEVEMENT_UNLOCKED, "Achievement unlocked! 🏆"),
            (CoordinationEventType.COST_THRESHOLD_REACHED, "Cost optimization achieved! 💰"),
            (CoordinationEventType.SYSTEM_HEALTH_CHANGE, "System health improved! 💚"),
        ]
        
        logger.info("🎭 Demonstrating different coordination events...")
        
        for event_type, description in events_to_demo:
            logger.info(f"🎪 {description}")
            
            # Create coordination event
            event = CoordinationEvent(
                event_type=event_type,
                source_component="emoji_rain_demo",
                event_data={
                    "description": description,
                    "demo": True,
                    "timestamp": asyncio.get_event_loop().time()
                }
            )
            
            # Trigger emoji rain
            effect_id = await emoji_engine.trigger_event_rain(event)
            logger.info(f"🌧️ Triggered {event_type.name} rain (Effect ID: {effect_id})")
            
            # Show active effects
            active_effects = emoji_engine.get_active_effects()
            logger.info(f"📈 Active effects: {len(active_effects)}")
            
            # Wait a bit between events
            await asyncio.sleep(2.0)
        
        # Demo special achievement celebration
        logger.info("🏆 Demonstrating special achievement celebration...")
        
        achievement = Achievement(
            name="Emoji Rain Master",
            description="Successfully demonstrated the emoji rain system",
            icon_emoji="🌧️",
            user_id="demo-user"
        )
        
        celebration_id = await emoji_engine.create_achievement_celebration(achievement)
        logger.info(f"🎊 Created achievement celebration (Effect ID: {celebration_id})")
        
        # Let the celebration run
        await asyncio.sleep(3.0)
        
        # Show performance stats
        stats = emoji_engine.get_performance_stats()
        logger.info("📊 Performance Statistics:")
        logger.info(f"   Active effects: {stats['active_effects']}")
        logger.info(f"   Total particles: {stats['total_particles']}")
        logger.info(f"   Target FPS: {stats['target_fps']}")
        logger.info(f"   Canvas size: {stats['canvas_size']}")
        logger.info(f"   Animation running: {stats['animation_running']}")
        logger.info(f"   Registered callbacks: {stats['registered_callbacks']}")
        
        # Demo rapid-fire events (stress test)
        logger.info("🚀 Stress testing with rapid-fire events...")
        
        for i in range(10):
            event = CoordinationEvent(
                event_type=CoordinationEventType.TASK_COMPLETED,
                source_component=f"stress_test_{i}",
                event_data={"iteration": i}
            )
            
            await emoji_engine.trigger_event_rain(event)
            await asyncio.sleep(0.2)  # 5 events per second
        
        logger.info("💥 Stress test complete!")
        
        # Let effects finish
        logger.info("⏱️ Letting effects finish...")
        await asyncio.sleep(5.0)
        
        # Final stats
        final_stats = emoji_engine.get_performance_stats()
        logger.info(f"🏁 Final stats: {final_stats['active_effects']} effects, {final_stats['total_particles']} particles")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise
    
    finally:
        # Stop animation loop
        logger.info("🛑 Stopping emoji rain engine...")
        await emoji_engine.stop_animation_loop()
        logger.info("✅ Emoji rain engine stopped")
        logger.info("🎉 Emoji Rain Demo completed!")


async def demo_web_interface():
    """Demonstrate the web interface with emoji rain."""
    logger.info("🌐 Starting Web Interface Demo...")
    
    try:
        # Load configuration
        config_path = Path(__file__).parent.parent / "config" / "observatory.yaml"
        config = load_observatory_config(str(config_path))
        
        # Create emoji engine and web interface
        emoji_engine = EmojiRainEngine()
        from src.beast_mode.observatory import ObservatoryWebInterface
        web_interface = ObservatoryWebInterface(config, emoji_engine)
        
        logger.info(f"🌐 Web interface created on port {config.websocket_config.port}")
        logger.info("🌧️ Visit http://localhost:8080 to see the emoji rain in action!")
        logger.info("🎮 Click the buttons to trigger different emoji rain effects")
        logger.info("⏹️ Press Ctrl+C to stop the demo")
        
        # Start the web interface
        await web_interface.start_server()
        
        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("👋 Demo interrupted by user")
        
    except Exception as e:
        logger.error(f"❌ Web interface demo failed: {e}")
        raise
    
    finally:
        # Stop web interface
        if 'web_interface' in locals():
            await web_interface.stop_server()
        logger.info("🛑 Web interface demo stopped")


async def main():
    """Main demo function."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        await demo_web_interface()
    else:
        await demo_emoji_rain()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Demo interrupted by user")
    except Exception as e:
        logger.error(f"💥 Demo crashed: {e}")
        exit(1)