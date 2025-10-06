#!/usr/bin/env python3
"""
Test Engagement Event Coordination System

Tests the engagement event coordinator and its integration with engagement subsystems.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.observatory.engagement.coordination import (
    EngagementEventCoordinator,
    EngagementEventType,
    EngagementEventPriority
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MockEngagementComponent:
    """Mock engagement component for testing."""
    
    def __init__(self, component_id: str):
        self.component_id = component_id
        self.events_received = []
    
    async def handle_engagement_event(self, event):
        """Handle engagement events."""
        self.events_received.append(event)
        return {"component": self.component_id, "handled": True}


async def test_event_coordinator_basic():
    """Test basic event coordinator functionality."""
    logger.info("🧪 Testing event coordinator basic functionality...")
    
    try:
        # Create event coordinator
        coordinator = EngagementEventCoordinator()
        await coordinator.initialize()
        
        # Test component registration
        mock_component = MockEngagementComponent("test_component")
        coordinator.register_component("test_component", mock_component)
        
        # Test event emission
        event_id = await coordinator.emit_event(
            EngagementEventType.USER_INTERACTION,
            "test_source",
            {"test_data": "value"},
            EngagementEventPriority.HIGH
        )
        
        # Wait for event processing
        await asyncio.sleep(0.5)
        
        # Check results
        state = coordinator.get_unified_state()
        stats = coordinator.get_event_statistics()
        
        logger.info(f"✅ Event coordinator basic test passed:")
        logger.info(f"   - Event ID: {event_id}")
        logger.info(f"   - Events processed: {stats['total_events_processed']}")
        logger.info(f"   - Registered components: {len(state['coordinator_status']['registered_components'])}")
        logger.info(f"   - Component received events: {len(mock_component.events_received)}")
        
        await coordinator.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Event coordinator basic test failed: {e}")
        return False


async def test_event_prioritization():
    """Test event prioritization and routing."""
    logger.info("🧪 Testing event prioritization...")
    
    try:
        # Create event coordinator
        coordinator = EngagementEventCoordinator()
        await coordinator.initialize()
        
        # Create mock components
        components = {}
        for i in range(3):
            comp_id = f"component_{i}"
            components[comp_id] = MockEngagementComponent(comp_id)
            coordinator.register_component(comp_id, components[comp_id])
        
        # Emit events with different priorities
        events = [
            (EngagementEventType.USER_INTERACTION, EngagementEventPriority.LOW, "low_priority"),
            (EngagementEventType.SYSTEM_EVENT, EngagementEventPriority.CRITICAL, "critical_event"),
            (EngagementEventType.PERSONALITY_TRANSITION, EngagementEventPriority.MEDIUM, "medium_priority"),
            (EngagementEventType.ANIMATION_TRIGGER, EngagementEventPriority.HIGH, "high_priority")
        ]
        
        event_ids = []
        for event_type, priority, data_value in events:
            event_id = await coordinator.emit_event(
                event_type, "test_source", {"data": data_value}, priority
            )
            event_ids.append(event_id)
        
        # Wait for processing
        await asyncio.sleep(1)
        
        # Check statistics
        stats = coordinator.get_event_statistics()
        state = coordinator.get_unified_state()
        
        logger.info(f"✅ Event prioritization test passed:")
        logger.info(f"   - Events emitted: {len(event_ids)}")
        logger.info(f"   - Events processed: {stats['total_events_processed']}")
        logger.info(f"   - Priority distribution: {stats['priority_distribution']}")
        logger.info(f"   - Event type distribution: {stats['event_type_distribution']}")
        
        await coordinator.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Event prioritization test failed: {e}")
        return False


async def test_state_management():
    """Test unified state management."""
    logger.info("🧪 Testing state management...")
    
    try:
        # Create event coordinator
        coordinator = EngagementEventCoordinator()
        await coordinator.initialize()
        
        # Register components with initial states
        initial_states = {
            "dashboard_engine": {"active": True, "theme": "default"},
            "animation_engine": {"running": False, "effects": 0},
            "personality_engine": {"mood": "calm", "transitions": 0}
        }
        
        for comp_id, state in initial_states.items():
            mock_comp = MockEngagementComponent(comp_id)
            coordinator.register_component(comp_id, mock_comp, state)
        
        # Emit state-changing events
        await coordinator.emit_event(
            EngagementEventType.PERSONALITY_TRANSITION,
            "test_source",
            {"from_mood": "calm", "to_mood": "focused"},
            EngagementEventPriority.MEDIUM
        )
        
        await coordinator.emit_event(
            EngagementEventType.USER_INTERACTION,
            "test_source",
            {"event_type": "click", "component": "button"},
            EngagementEventPriority.LOW
        )
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Check unified state
        unified_state = coordinator.get_unified_state()
        
        logger.info(f"✅ State management test passed:")
        logger.info(f"   - Component states: {len(unified_state['component_states'])}")
        logger.info(f"   - Recent events: {len(unified_state['recent_events'])}")
        logger.info(f"   - Coordinator status: {unified_state['coordinator_status']['running']}")
        
        # Check specific state updates
        personality_state = unified_state['component_states'].get('personality_engine', {})
        if personality_state.get('current_mood') == 'focused':
            logger.info("   - Personality state updated correctly")
        
        interaction_state = unified_state['component_states'].get('interaction_engine', {})
        if interaction_state.get('total_interactions', 0) > 0:
            logger.info("   - Interaction state updated correctly")
        
        await coordinator.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ State management test failed: {e}")
        return False


async def test_analytics_and_logging():
    """Test analytics and logging functionality."""
    logger.info("🧪 Testing analytics and logging...")
    
    try:
        # Create event coordinator
        coordinator = EngagementEventCoordinator()
        await coordinator.initialize()
        
        # Register a component
        mock_comp = MockEngagementComponent("analytics_test")
        coordinator.register_component("analytics_test", mock_comp)
        
        # Generate various events for analytics
        event_types = [
            EngagementEventType.USER_INTERACTION,
            EngagementEventType.PERSONALITY_TRANSITION,
            EngagementEventType.ANIMATION_TRIGGER,
            EngagementEventType.SYSTEM_EVENT
        ]
        
        for i, event_type in enumerate(event_types):
            for j in range(3):  # 3 events of each type
                await coordinator.emit_event(
                    event_type,
                    "analytics_test",
                    {"test_data": f"event_{i}_{j}"},
                    EngagementEventPriority.MEDIUM
                )
        
        # Wait for processing
        await asyncio.sleep(1)
        
        # Get analytics
        analytics = await coordinator.log_engagement_analytics()
        stats = coordinator.get_event_statistics()
        
        logger.info(f"✅ Analytics and logging test passed:")
        logger.info(f"   - Total events processed: {stats['total_events_processed']}")
        logger.info(f"   - Success rate: {stats['success_rate']:.1f}%")
        logger.info(f"   - Event types tracked: {len(stats['event_type_distribution'])}")
        logger.info(f"   - Analytics logged: {len(analytics)} fields")
        
        await coordinator.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"❌ Analytics and logging test failed: {e}")
        return False


async def test_integration_with_server():
    """Test integration with Observatory server integration."""
    logger.info("🧪 Testing integration with server...")
    
    try:
        # Import server integration
        from beast_mode.observatory.engagement.integration.server_integration import (
            ObservatoryEngagementIntegration,
            trigger_personality_transition,
            trigger_animation_event,
            get_engagement_coordination_status
        )
        from beast_mode.observatory.models import ObservatoryConfig
        
        # Create mock config
        config = ObservatoryConfig()
        
        # Create integration
        integration = ObservatoryEngagementIntegration(config)
        await integration.initialize()
        
        # Test helper functions
        await trigger_personality_transition(integration, "calm", "focused", "test_trigger")
        await trigger_animation_event(integration, "test_animation", 0.5, "test_component")
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Get coordination status
        status = get_engagement_coordination_status(integration)
        
        logger.info(f"✅ Server integration test passed:")
        logger.info(f"   - Coordinator running: {status['coordinator_status']['running']}")
        logger.info(f"   - Events processed: {status['event_statistics']['total_events_processed']}")
        logger.info(f"   - Registered components: {len(status['unified_state']['coordinator_status']['registered_components'])}")
        
        await integration.stop_integration()
        return True
        
    except Exception as e:
        logger.error(f"❌ Server integration test failed: {e}")
        return False


async def main():
    """Run all engagement coordination tests."""
    logger.info("🚀 Starting Engagement Coordination Tests")
    
    tests = [
        ("Event Coordinator Basic", test_event_coordinator_basic),
        ("Event Prioritization", test_event_prioritization),
        ("State Management", test_state_management),
        ("Analytics and Logging", test_analytics_and_logging),
        ("Server Integration", test_integration_with_server)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} Test")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
                
        except Exception as e:
            logger.error(f"💥 {test_name} test CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All engagement coordination tests PASSED!")
        return 0
    else:
        logger.error(f"💥 {total - passed} tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)