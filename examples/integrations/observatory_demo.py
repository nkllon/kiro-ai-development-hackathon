#!/usr/bin/env python3
"""
Beast Mode Coordination Observatory Demo

This script demonstrates the basic Observatory functionality including:
- Configuration loading
- Core engine initialization
- Event processing
- Health monitoring
- Graceful shutdown
"""

import asyncio
import logging
from pathlib import Path

from src.beast_mode.observatory import (
    ObservatoryCoreEngine,
    load_observatory_config,
    CoordinationEvent,
    CoordinationEventType,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main demo function."""
    logger.info("🚀 Starting Beast Mode Coordination Observatory Demo")
    
    try:
        # Load configuration
        config_path = Path(__file__).parent.parent / "config" / "observatory.yaml"
        config = load_observatory_config(str(config_path))
        logger.info(f"✅ Configuration loaded from {config_path}")
        
        # Create Observatory instance
        observatory = ObservatoryCoreEngine(config)
        logger.info("✅ Observatory Core Engine created")
        
        # Check initial health status
        health = observatory.get_health_status()
        logger.info(f"📊 Initial health status: {health.status.value} (score: {health.health_score})")
        
        # Get module info
        module_info = observatory.get_module_info()
        logger.info(f"ℹ️  Module: {module_info['name']} v{module_info['version']}")
        
        # Start Observatory
        logger.info("🔄 Starting Observatory...")
        success = await observatory.start_observatory()
        if success:
            logger.info("✅ Observatory started successfully!")
        else:
            logger.error("❌ Failed to start Observatory")
            return
        
        # Check health after startup
        health = observatory.get_health_status()
        logger.info(f"📊 Running health status: {health.status.value} (score: {health.health_score})")
        
        # Simulate some coordination events
        logger.info("📡 Simulating coordination events...")
        
        events = [
            CoordinationEvent(
                event_type=CoordinationEventType.TASK_COMPLETED,
                source_component="demo_task_queue",
                event_data={"task_id": "demo-001", "duration_ms": 1500}
            ),
            CoordinationEvent(
                event_type=CoordinationEventType.API_CALL_SUCCESS,
                source_component="demo_llm_api",
                event_data={"provider": "openai", "model": "gpt-4", "tokens": 150}
            ),
            CoordinationEvent(
                event_type=CoordinationEventType.COORDINATION_MILESTONE,
                source_component="demo_gamification",
                event_data={"milestone": "first_demo", "achievement_unlocked": True}
            ),
        ]
        
        for event in events:
            await observatory.process_coordination_event(event)
            logger.info(f"📨 Processed event: {event.event_type.name} from {event.source_component}")
            await asyncio.sleep(0.5)  # Small delay between events
        
        # Generate insights
        logger.info("🧠 Generating real-time insights...")
        insights = await observatory.generate_real_time_insights()
        logger.info(f"💡 Generated insights at {insights.timestamp}")
        logger.info(f"   Coordination health: {insights.coordination_health.overall_score}")
        logger.info(f"   Active anomalies: {len(insights.active_anomalies)}")
        logger.info(f"   Recent achievements: {len(insights.recent_achievements)}")
        
        # Get performance metrics
        metrics = await observatory.get_metrics()
        logger.info(f"📈 Performance metrics:")
        logger.info(f"   Uptime: {metrics['observatory_uptime_seconds']:.2f} seconds")
        logger.info(f"   Events processed: {metrics['events_processed_total']}")
        
        # Test graceful degradation
        logger.info("🔧 Testing graceful degradation...")
        degradation_result = observatory.graceful_degradation()
        if degradation_result.success:
            logger.info(f"✅ Graceful degradation successful")
            logger.info(f"   Remaining capabilities: {[cap.value for cap in degradation_result.remaining_capabilities]}")
        else:
            logger.warning(f"⚠️  Graceful degradation failed: {degradation_result.error_message}")
        
        # Let it run for a bit
        logger.info("⏱️  Running Observatory for 5 seconds...")
        await asyncio.sleep(5)
        
        # Final health check
        health = observatory.get_health_status()
        logger.info(f"📊 Final health status: {health.status.value} (uptime: {health.uptime_seconds:.2f}s)")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise
    
    finally:
        # Graceful shutdown
        logger.info("🛑 Shutting down Observatory...")
        await observatory.stop_observatory()
        logger.info("✅ Observatory stopped gracefully")
        logger.info("🎉 Demo completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Demo interrupted by user")
    except Exception as e:
        logger.error(f"💥 Demo crashed: {e}")
        exit(1)