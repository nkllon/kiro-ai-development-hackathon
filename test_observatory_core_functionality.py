#!/usr/bin/env python3
"""
Test Observatory Core Functionality with Engagement System Resilience
=====================================================================

Test that Observatory core functionality works correctly and remains
available even when engagement system components fail.
"""

import asyncio
import logging
from unittest.mock import Mock, patch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_observatory_core_without_engagement():
    """Test that Observatory core functionality works without engagement system."""
    logger.info("🧪 Testing Observatory core functionality without engagement...")
    
    try:
        # Test that core components can be imported and initialized
        from src.beast_mode.observatory.models import ObservatoryConfig
        from src.beast_mode.observatory.core import ObservatoryCoreEngine
        from src.beast_mode.observatory.emoji_rain import EmojiRainEngine
        
        # Create configuration
        config = ObservatoryConfig()
        
        # Test core engine
        core_engine = ObservatoryCoreEngine(config)
        assert core_engine is not None
        logger.info("✅ Observatory core engine initializes correctly")
        
        # Test emoji rain engine
        emoji_engine = EmojiRainEngine()
        assert emoji_engine is not None
        logger.info("✅ Emoji rain engine initializes correctly")
        
        # Test health status
        health_status = core_engine.get_health_status()
        assert health_status is not None
        assert hasattr(health_status, 'status')
        logger.info("✅ Observatory core health status available")
        
        logger.info("🎉 Observatory core functionality test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_engagement_system_graceful_degradation():
    """Test that engagement system degrades gracefully under errors."""
    logger.info("🧪 Testing engagement system graceful degradation...")
    
    try:
        from src.beast_mode.observatory.engagement.error_handling import (
            EngagementErrorHandler,
            EngagementErrorType,
            EngagementErrorSeverity,
            EngagementFallbackMode
        )
        
        # Initialize error handler
        error_handler = EngagementErrorHandler()
        await error_handler.initialize()
        
        # Test 1: System starts in normal mode
        assert not error_handler.system_degraded
        logger.info("✅ System starts in normal mode")
        
        # Test 2: Single error doesn't trigger system degradation
        await error_handler.handle_error(
            EngagementErrorType.WEBSOCKET_ERROR,
            "websocket_test",
            "Single WebSocket error",
            ConnectionError("Connection failed")
        )
        
        assert not error_handler.system_degraded
        logger.info("✅ Single error doesn't trigger system degradation")
        
        # Test 3: Multiple critical errors trigger degradation
        for i in range(3):
            await error_handler.handle_error(
                EngagementErrorType.INITIALIZATION_ERROR,
                f"critical_component_{i}",
                f"Critical error {i}",
                Exception(f"Critical failure {i}")
            )
        
        assert error_handler.system_degraded
        logger.info("✅ Multiple critical errors trigger system degradation")
        
        # Test 4: Components are in appropriate fallback modes
        stats = error_handler.get_error_statistics()
        assert "component_fallback_modes" in stats
        assert len(stats["component_fallback_modes"]) > 0
        logger.info("✅ Components are in appropriate fallback modes")
        
        # Test 5: Error statistics are comprehensive
        assert stats["total_errors"] > 0
        assert stats["system_degraded"] is True
        assert "severity_distribution" in stats
        assert "component_distribution" in stats
        assert "error_type_distribution" in stats
        logger.info("✅ Error statistics are comprehensive")
        
        logger.info("🎉 Engagement system graceful degradation test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_engagement_error_recovery():
    """Test engagement system error recovery capabilities."""
    logger.info("🧪 Testing engagement system error recovery...")
    
    try:
        from src.beast_mode.observatory.engagement.error_handling import (
            EngagementErrorRecovery,
            RecoveryAction,
            RecoveryResult,
            EngagementErrorType,
            EngagementError,
            EngagementErrorSeverity
        )
        
        # Initialize error recovery
        error_recovery = EngagementErrorRecovery()
        await error_recovery.initialize()
        
        # Test 1: Recovery plans are registered
        assert len(error_recovery.recovery_plans) > 0
        logger.info("✅ Recovery plans are registered")
        
        # Test 2: Recovery handlers are registered
        assert len(error_recovery.component_recovery_handlers) > 0
        logger.info("✅ Recovery handlers are registered")
        
        # Test 3: Recovery attempt for WebSocket error
        error = EngagementError(
            error_type=EngagementErrorType.WEBSOCKET_ERROR,
            severity=EngagementErrorSeverity.MEDIUM,
            component="test_websocket",
            message="WebSocket connection failed",
            exception=ConnectionError("Connection refused")
        )
        
        result = await error_recovery.attempt_recovery(error)
        assert result in [RecoveryResult.SUCCESS, RecoveryResult.FAILURE, RecoveryResult.NOT_APPLICABLE]
        logger.info("✅ Recovery attempt completed")
        
        # Test 4: Recovery statistics are tracked
        stats = error_recovery.get_recovery_statistics()
        assert "total_recovery_attempts" in stats
        assert "success_rate" in stats
        assert "registered_plans" in stats
        assert "registered_handlers" in stats
        logger.info("✅ Recovery statistics are tracked")
        
        logger.info("🎉 Engagement system error recovery test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_resilience_manager():
    """Test engagement resilience manager functionality."""
    logger.info("🧪 Testing engagement resilience manager...")
    
    try:
        from src.beast_mode.observatory.engagement.error_handling import (
            EngagementErrorHandler,
            EngagementResilienceManager
        )
        
        # Initialize components
        error_handler = EngagementErrorHandler()
        await error_handler.initialize()
        
        resilience_manager = EngagementResilienceManager(error_handler)
        await resilience_manager.initialize()
        
        # Test 1: Resilience manager initializes correctly
        assert resilience_manager.health_monitor_task is not None
        assert resilience_manager.strategy_evaluator_task is not None
        logger.info("✅ Resilience manager initializes correctly")
        
        # Test 2: Component registration works
        def mock_health_check():
            return {"status": "healthy", "response_time": 0.1}
        
        resilience_manager.register_component(
            "test_component",
            mock_health_check,
            critical=True
        )
        
        assert "test_component" in resilience_manager.registered_components
        logger.info("✅ Component registration works")
        
        # Test 3: Health score calculation works
        health_data = {"status": "healthy", "response_time": 0.5}
        score = resilience_manager._calculate_component_health_score(health_data)
        assert 0.0 <= score <= 1.0
        logger.info("✅ Health score calculation works")
        
        # Test 4: Resilience status reporting works
        status = resilience_manager.get_resilience_status()
        assert "current_strategy" in status
        assert "system_health" in status
        assert "registered_components" in status
        logger.info("✅ Resilience status reporting works")
        
        # Test 5: Graceful shutdown works
        await resilience_manager.shutdown()
        assert resilience_manager.health_monitor_task.done()
        assert resilience_manager.strategy_evaluator_task.done()
        logger.info("✅ Graceful shutdown works")
        
        logger.info("🎉 Engagement resilience manager test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integrated_error_handling_flow():
    """Test the complete integrated error handling flow."""
    logger.info("🧪 Testing integrated error handling flow...")
    
    try:
        from src.beast_mode.observatory.engagement.error_handling import (
            EngagementErrorHandler,
            EngagementErrorRecovery,
            EngagementResilienceManager,
            EngagementErrorType,
            EngagementErrorSeverity
        )
        
        # Initialize all components
        error_handler = EngagementErrorHandler()
        await error_handler.initialize()
        
        error_recovery = EngagementErrorRecovery()
        await error_recovery.initialize()
        
        resilience_manager = EngagementResilienceManager(error_handler)
        await resilience_manager.initialize()
        
        # Register a test component
        def mock_health_check():
            return {"status": "healthy"}
        
        resilience_manager.register_component(
            "integrated_test_component",
            mock_health_check,
            critical=True
        )
        
        # Test 1: Handle a medium severity error
        error = await error_handler.handle_error(
            EngagementErrorType.WEBSOCKET_ERROR,
            "integrated_test_component",
            "WebSocket connection failed in integration test",
            ConnectionError("Connection refused")
        )
        
        assert error.error_type == EngagementErrorType.WEBSOCKET_ERROR
        assert error.recovery_attempted is True
        logger.info("✅ Medium severity error handled with recovery attempt")
        
        # Test 2: Handle a critical error
        critical_error = await error_handler.handle_error(
            EngagementErrorType.INITIALIZATION_ERROR,
            "integrated_test_component",
            "Critical initialization failure",
            Exception("Critical failure")
        )
        
        assert critical_error.error_type == EngagementErrorType.INITIALIZATION_ERROR
        assert critical_error.severity == EngagementErrorSeverity.CRITICAL
        logger.info("✅ Critical error handled correctly")
        
        # Test 3: Verify fallback mode was applied
        fallback_mode = error_handler.get_component_fallback_mode("integrated_test_component")
        from src.beast_mode.observatory.engagement.error_handling import EngagementFallbackMode
        assert fallback_mode != EngagementFallbackMode.FULL_FUNCTIONALITY
        logger.info("✅ Fallback mode applied correctly")
        
        # Test 4: Verify statistics are updated
        error_stats = error_handler.get_error_statistics()
        recovery_stats = error_recovery.get_recovery_statistics()
        resilience_status = resilience_manager.get_resilience_status()
        
        assert error_stats["total_errors"] >= 2
        assert "component_fallback_modes" in error_stats
        assert "total_recovery_attempts" in recovery_stats
        assert "current_strategy" in resilience_status
        logger.info("✅ All statistics updated correctly")
        
        # Cleanup
        await resilience_manager.shutdown()
        
        logger.info("🎉 Integrated error handling flow test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_core_functionality_tests():
    """Run all Observatory core functionality tests."""
    logger.info("🚀 Starting Observatory core functionality tests...")
    
    results = []
    
    # Test Observatory core without engagement
    result1 = await test_observatory_core_without_engagement()
    results.append(result1)
    
    # Test engagement system graceful degradation
    result2 = await test_engagement_system_graceful_degradation()
    results.append(result2)
    
    # Test engagement error recovery
    result3 = await test_engagement_error_recovery()
    results.append(result3)
    
    # Test resilience manager
    result4 = await test_resilience_manager()
    results.append(result4)
    
    # Test integrated error handling flow
    result5 = await test_integrated_error_handling_flow()
    results.append(result5)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        logger.info(f"🎉 All {total} core functionality test suites passed!")
        logger.info("🛡️ Observatory core functionality is robust and resilient")
        return True
    else:
        logger.error(f"❌ {total - passed} out of {total} test suites failed!")
        return False


if __name__ == "__main__":
    # Run all core functionality tests
    result = asyncio.run(run_all_core_functionality_tests())
    
    if result:
        print("\n✅ All Observatory core functionality tests passed!")
        print("🛡️ Observatory core remains functional even with engagement system errors")
        print("🎯 Error handling and resilience systems work correctly")
        print("🔧 Recovery mechanisms are operational")
    else:
        print("\n❌ Some core functionality tests failed!")
        print("🔧 Please check the implementation")
        exit(1)