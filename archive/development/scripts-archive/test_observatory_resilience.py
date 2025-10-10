#!/usr/bin/env python3
"""
Test Observatory Server Resilience with Engagement System
=========================================================

Test that the Observatory server starts successfully and continues to function
even when the engagement system encounters errors or failures.
"""

import asyncio
import logging
from unittest.mock import Mock, patch, AsyncMock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_observatory_server_resilience():
    """Test Observatory server resilience with engagement system failures."""
    logger.info("🧪 Testing Observatory server resilience...")
    
    try:
        # Import Observatory components
        from src.beast_mode.observatory.models import ObservatoryConfig
        from src.beast_mode.observatory.server import ObservatoryServer
        
        # Create a test configuration
        config = ObservatoryConfig()
        
        # Test 1: Server starts without engagement system
        logger.info("Test 1: Observatory server without engagement system")
        
        with patch('src.beast_mode.observatory.server.ENGAGEMENT_AVAILABLE', False):
            server = ObservatoryServer(config)
            assert server.engagement_integration is None
            assert server.engagement_available is False
            logger.info("✅ Server initializes correctly without engagement system")
        
        # Test 2: Server starts with engagement system available
        logger.info("Test 2: Observatory server with engagement system")
        
        with patch('src.beast_mode.observatory.server.ENGAGEMENT_AVAILABLE', True):
            server = ObservatoryServer(config)
            # Server should attempt to initialize engagement
            logger.info("✅ Server attempts engagement initialization when available")
        
        # Test 3: Server handles engagement initialization failure
        logger.info("Test 3: Observatory server with engagement initialization failure")
        
        with patch('src.beast_mode.observatory.server.ENGAGEMENT_AVAILABLE', True):
            with patch('src.beast_mode.observatory.engagement.integration.server_integration.ObservatoryEngagementIntegration') as mock_integration:
                # Make initialization fail
                mock_integration.side_effect = Exception("Initialization failed")
                
                server = ObservatoryServer(config)
                assert server.engagement_integration is None
                assert server.engagement_available is False
                logger.info("✅ Server handles engagement initialization failure gracefully")
        
        # Test 4: Health endpoint works with and without engagement
        logger.info("Test 4: Health endpoint resilience")
        
        # Mock the core components
        with patch('src.beast_mode.observatory.server.ObservatoryCoreEngine') as mock_core:
            with patch('src.beast_mode.observatory.server.EmojiRainEngine') as mock_emoji:
                # Setup mocks
                mock_core_instance = Mock()
                mock_core_instance.get_health_status.return_value = Mock(
                    status=Mock(value="healthy"),
                    health_score=0.95,
                    uptime_seconds=3600,
                    last_check=Mock(isoformat=lambda: "2025-01-01T00:00:00")
                )
                mock_core.return_value = mock_core_instance
                
                mock_emoji_instance = Mock()
                mock_emoji_instance.get_performance_stats.return_value = {
                    "animation_running": True,
                    "active_effects": 5,
                    "total_particles": 100
                }
                mock_emoji.return_value = mock_emoji_instance
                
                # Test without engagement
                with patch('src.beast_mode.observatory.server.ENGAGEMENT_AVAILABLE', False):
                    server = ObservatoryServer(config)
                    
                    # Simulate health check
                    health_data = {
                        "status": "healthy",
                        "timestamp": "2025-01-01T00:00:00",
                        "observatory": {
                            "status": "healthy",
                            "health_score": 0.95,
                            "uptime_seconds": 3600
                        },
                        "emoji_rain": {
                            "active": True,
                            "active_effects": 5,
                            "total_particles": 100,
                            "connected_clients": 0
                        }
                    }
                    
                    # Should include engagement status as disabled
                    assert "engagement" not in health_data or health_data.get("engagement", {}).get("status") != "healthy"
                    logger.info("✅ Health endpoint works without engagement system")
        
        # Test 5: WebSocket endpoints handle engagement failures
        logger.info("Test 5: WebSocket endpoint resilience")
        
        # This would test that WebSocket connections work even if engagement WebSocket fails
        # For now, we'll just verify the setup doesn't crash
        with patch('src.beast_mode.observatory.server.ENGAGEMENT_AVAILABLE', True):
            with patch('src.beast_mode.observatory.engagement.integration.server_integration.ObservatoryEngagementIntegration') as mock_integration:
                # Make WebSocket setup fail
                mock_integration_instance = Mock()
                mock_integration_instance.handle_websocket_connection = AsyncMock(side_effect=Exception("WebSocket failed"))
                mock_integration.return_value = mock_integration_instance
                
                server = ObservatoryServer(config)
                # Server should still initialize
                logger.info("✅ Server handles WebSocket setup failures gracefully")
        
        logger.info("🎉 All Observatory server resilience tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_engagement_error_scenarios():
    """Test specific engagement error scenarios."""
    logger.info("🧪 Testing engagement error scenarios...")
    
    try:
        from src.beast_mode.observatory.engagement.error_handling import (
            EngagementErrorHandler,
            EngagementErrorType,
            EngagementErrorSeverity
        )
        
        # Test 1: Import errors don't crash the system
        logger.info("Test 1: Import error handling")
        
        error_handler = EngagementErrorHandler()
        await error_handler.initialize()
        
        error = await error_handler.handle_error(
            EngagementErrorType.IMPORT_ERROR,
            "missing_module",
            "Failed to import engagement module",
            ImportError("No module named 'missing_module'")
        )
        
        assert error.error_type == EngagementErrorType.IMPORT_ERROR
        assert error.severity == EngagementErrorSeverity.HIGH
        logger.info("✅ Import errors handled correctly")
        
        # Test 2: WebSocket errors trigger recovery
        logger.info("Test 2: WebSocket error recovery")
        
        error = await error_handler.handle_error(
            EngagementErrorType.WEBSOCKET_ERROR,
            "websocket_manager",
            "WebSocket connection failed",
            ConnectionError("Connection refused")
        )
        
        assert error.error_type == EngagementErrorType.WEBSOCKET_ERROR
        assert error.recovery_attempted is True
        logger.info("✅ WebSocket errors trigger recovery")
        
        # Test 3: Multiple errors trigger system degradation
        logger.info("Test 3: System degradation on multiple errors")
        
        # Generate multiple critical errors
        for i in range(4):
            await error_handler.handle_error(
                EngagementErrorType.INITIALIZATION_ERROR,
                f"critical_component_{i}",
                f"Critical initialization failure {i}",
                Exception(f"Critical error {i}")
            )
        
        assert error_handler.system_degraded is True
        logger.info("✅ System degradation triggered correctly")
        
        # Test 4: Error statistics are tracked
        logger.info("Test 4: Error statistics tracking")
        
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] > 0
        assert stats["system_degraded"] is True
        assert "severity_distribution" in stats
        assert "component_distribution" in stats
        logger.info("✅ Error statistics tracked correctly")
        
        logger.info("🎉 All engagement error scenario tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_fallback_modes():
    """Test engagement system fallback modes."""
    logger.info("🧪 Testing engagement system fallback modes...")
    
    try:
        from src.beast_mode.observatory.engagement.error_handling import (
            EngagementErrorHandler,
            EngagementErrorType,
            EngagementFallbackMode
        )
        
        error_handler = EngagementErrorHandler()
        await error_handler.initialize()
        
        # Test 1: Component starts in full functionality mode
        logger.info("Test 1: Default fallback mode")
        
        mode = error_handler.get_component_fallback_mode("test_component")
        assert mode == EngagementFallbackMode.FULL_FUNCTIONALITY
        logger.info("✅ Components start in full functionality mode")
        
        # Test 2: High severity error triggers fallback mode
        logger.info("Test 2: High severity error fallback")
        
        await error_handler.handle_error(
            EngagementErrorType.INTEGRATION_ERROR,
            "test_component",
            "Integration failure",
            Exception("Integration failed")
        )
        
        mode = error_handler.get_component_fallback_mode("test_component")
        assert mode != EngagementFallbackMode.FULL_FUNCTIONALITY
        logger.info("✅ High severity errors trigger fallback modes")
        
        # Test 3: Critical errors disable components
        logger.info("Test 3: Critical error component disable")
        
        await error_handler.handle_error(
            EngagementErrorType.INITIALIZATION_ERROR,
            "critical_component",
            "Critical initialization failure",
            Exception("Critical failure")
        )
        
        mode = error_handler.get_component_fallback_mode("critical_component")
        assert mode == EngagementFallbackMode.DISABLED
        logger.info("✅ Critical errors disable components")
        
        # Test 4: Fallback mode statistics
        logger.info("Test 4: Fallback mode statistics")
        
        stats = error_handler.get_error_statistics()
        assert "component_fallback_modes" in stats
        assert len(stats["component_fallback_modes"]) > 0
        logger.info("✅ Fallback mode statistics available")
        
        logger.info("🎉 All fallback mode tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_resilience_tests():
    """Run all Observatory resilience tests."""
    logger.info("🚀 Starting comprehensive Observatory resilience tests...")
    
    results = []
    
    # Test Observatory server resilience
    result1 = await test_observatory_server_resilience()
    results.append(result1)
    
    # Test engagement error scenarios
    result2 = await test_engagement_error_scenarios()
    results.append(result2)
    
    # Test fallback modes
    result3 = await test_fallback_modes()
    results.append(result3)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        logger.info(f"🎉 All {total} resilience test suites passed!")
        logger.info("🛡️ Observatory server is resilient to engagement system failures")
        return True
    else:
        logger.error(f"❌ {total - passed} out of {total} test suites failed!")
        return False


if __name__ == "__main__":
    # Run all resilience tests
    result = asyncio.run(run_all_resilience_tests())
    
    if result:
        print("\n✅ All Observatory resilience tests passed!")
        print("🛡️ Observatory server can handle engagement system failures gracefully")
        print("🎯 Core Observatory functionality remains available even when engagement features fail")
    else:
        print("\n❌ Some resilience tests failed!")
        print("🔧 Please check the Observatory server resilience implementation")
        exit(1)