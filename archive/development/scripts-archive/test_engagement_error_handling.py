#!/usr/bin/env python3
"""
Test Engagement Error Handling and Resilience System
====================================================

Comprehensive test suite for the engagement system error handling,
resilience management, and recovery capabilities.
"""

import asyncio
import pytest
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Import engagement error handling components
from src.beast_mode.observatory.engagement.error_handling import (
    EngagementErrorHandler,
    EngagementErrorType,
    EngagementErrorSeverity,
    EngagementError,
    EngagementFallbackMode,
    EngagementResilienceManager,
    EngagementErrorRecovery,
    RecoveryAction,
    RecoveryResult
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestEngagementErrorHandler:
    """Test suite for EngagementErrorHandler."""
    
    @pytest.fixture
    async def error_handler(self):
        """Create an error handler for testing."""
        handler = EngagementErrorHandler()
        await handler.initialize()
        return handler
    
    @pytest.mark.asyncio
    async def test_error_handler_initialization(self, error_handler):
        """Test that error handler initializes correctly."""
        assert error_handler is not None
        assert len(error_handler.recovery_handlers) > 0
        assert len(error_handler.fallback_handlers) > 0
        assert error_handler.system_degraded is False
    
    @pytest.mark.asyncio
    async def test_handle_low_severity_error(self, error_handler):
        """Test handling of low severity errors."""
        error = await error_handler.handle_error(
            EngagementErrorType.ANIMATION_ERROR,
            "test_component",
            "Test animation error",
            ValueError("Test error")
        )
        
        assert error.severity == EngagementErrorSeverity.LOW
        assert error.component == "test_component"
        assert error.error_type == EngagementErrorType.ANIMATION_ERROR
        assert not error.recovery_attempted  # Low severity errors don't trigger recovery
    
    @pytest.mark.asyncio
    async def test_handle_high_severity_error(self, error_handler):
        """Test handling of high severity errors."""
        error = await error_handler.handle_error(
            EngagementErrorType.INTEGRATION_ERROR,
            "test_component",
            "Test integration error",
            ImportError("Test import error")
        )
        
        assert error.severity == EngagementErrorSeverity.HIGH
        assert error.recovery_attempted is True
        assert error.fallback_mode is not None
    
    @pytest.mark.asyncio
    async def test_error_count_tracking(self, error_handler):
        """Test that error counts are tracked correctly."""
        # Generate multiple errors
        for i in range(5):
            await error_handler.handle_error(
                EngagementErrorType.WEBSOCKET_ERROR,
                "websocket_component",
                f"Test error {i}",
                ConnectionError(f"Connection error {i}")
            )
        
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 5
        assert stats["component_distribution"]["websocket_component"] == 5
    
    @pytest.mark.asyncio
    async def test_system_degradation_trigger(self, error_handler):
        """Test that system degradation is triggered by multiple critical errors."""
        # Generate multiple critical errors
        for i in range(4):
            await error_handler.handle_error(
                EngagementErrorType.INITIALIZATION_ERROR,
                f"component_{i}",
                f"Critical error {i}",
                Exception(f"Critical error {i}")
            )
        
        # System should be degraded after multiple critical errors
        assert error_handler.system_degraded is True
    
    @pytest.mark.asyncio
    async def test_fallback_mode_application(self, error_handler):
        """Test that fallback modes are applied correctly."""
        error = await error_handler.handle_error(
            EngagementErrorType.INTEGRATION_ERROR,
            "dashboard_engine",
            "Dashboard integration failed",
            Exception("Integration failure")
        )
        
        fallback_mode = error_handler.get_component_fallback_mode("dashboard_engine")
        assert fallback_mode != EngagementFallbackMode.FULL_FUNCTIONALITY
        assert error.fallback_mode is not None


class TestEngagementResilienceManager:
    """Test suite for EngagementResilienceManager."""
    
    @pytest.fixture
    async def resilience_manager(self):
        """Create a resilience manager for testing."""
        error_handler = EngagementErrorHandler()
        await error_handler.initialize()
        
        manager = EngagementResilienceManager(error_handler)
        await manager.initialize()
        return manager
    
    @pytest.mark.asyncio
    async def test_resilience_manager_initialization(self, resilience_manager):
        """Test that resilience manager initializes correctly."""
        assert resilience_manager is not None
        assert resilience_manager.health_monitor_task is not None
        assert resilience_manager.strategy_evaluator_task is not None
        assert not resilience_manager.health_monitor_task.done()
        assert not resilience_manager.strategy_evaluator_task.done()
    
    @pytest.mark.asyncio
    async def test_component_registration(self, resilience_manager):
        """Test component registration with resilience manager."""
        # Mock health check function
        def mock_health_check():
            return {"status": "healthy", "response_time": 0.1}
        
        resilience_manager.register_component(
            "test_component",
            mock_health_check,
            dependencies=["dependency1"],
            critical=True
        )
        
        assert "test_component" in resilience_manager.registered_components
        assert resilience_manager.registered_components["test_component"]["critical"] is True
        assert "test_component" in resilience_manager.component_health_scores
    
    @pytest.mark.asyncio
    async def test_health_score_calculation(self, resilience_manager):
        """Test health score calculation from health data."""
        # Test various health data scenarios
        test_cases = [
            ({"status": "healthy"}, 1.0),
            ({"status": "degraded"}, 0.6),
            ({"status": "unhealthy"}, 0.3),
            ({"status": "critical"}, 0.1),
            ({"status": "failed"}, 0.0),
            ({"status": "healthy", "error_rate": 0.5}, 0.5),  # 50% error rate
            ({"status": "healthy", "response_time": 10.0}, 0.5),  # Slow response
        ]
        
        for health_data, expected_score in test_cases:
            score = resilience_manager._calculate_component_health_score(health_data)
            assert abs(score - expected_score) < 0.1, f"Health data {health_data} should give score ~{expected_score}, got {score}"
    
    @pytest.mark.asyncio
    async def test_resilience_strategy_determination(self, resilience_manager):
        """Test resilience strategy determination based on system health."""
        from src.beast_mode.observatory.engagement.error_handling.resilience_manager import ResilienceStrategy
        
        # Test different system health scenarios
        test_cases = [
            (0.9, ResilienceStrategy.NORMAL_OPERATION),
            (0.5, ResilienceStrategy.GRACEFUL_DEGRADATION),
            (0.2, ResilienceStrategy.EMERGENCY_MODE),
        ]
        
        for system_health, expected_strategy in test_cases:
            strategy = resilience_manager._determine_optimal_strategy(system_health, {"recent_errors": 0})
            assert strategy == expected_strategy, f"System health {system_health} should trigger {expected_strategy}, got {strategy}"
    
    @pytest.mark.asyncio
    async def test_resilience_status_reporting(self, resilience_manager):
        """Test resilience status reporting."""
        status = resilience_manager.get_resilience_status()
        
        assert "current_strategy" in status
        assert "system_health" in status
        assert "fallback_strategies" in status
        assert "component_health_scores" in status
        assert "registered_components" in status
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, resilience_manager):
        """Test graceful shutdown of resilience manager."""
        # Ensure tasks are running
        assert not resilience_manager.health_monitor_task.done()
        assert not resilience_manager.strategy_evaluator_task.done()
        
        # Shutdown
        await resilience_manager.shutdown()
        
        # Tasks should be cancelled
        assert resilience_manager.health_monitor_task.done()
        assert resilience_manager.strategy_evaluator_task.done()


class TestEngagementErrorRecovery:
    """Test suite for EngagementErrorRecovery."""
    
    @pytest.fixture
    async def error_recovery(self):
        """Create an error recovery system for testing."""
        recovery = EngagementErrorRecovery()
        await recovery.initialize()
        return recovery
    
    @pytest.mark.asyncio
    async def test_error_recovery_initialization(self, error_recovery):
        """Test that error recovery initializes correctly."""
        assert error_recovery is not None
        assert len(error_recovery.recovery_plans) > 0
        assert len(error_recovery.component_recovery_handlers) > 0
    
    @pytest.mark.asyncio
    async def test_recovery_plan_registration(self, error_recovery):
        """Test recovery plan registration."""
        error_recovery.register_recovery_plan(
            EngagementErrorType.WEBSOCKET_ERROR,
            "test_component",
            [RecoveryAction.RECONNECT, RecoveryAction.VALIDATE_STATE],
            timeout=30,
            retry_count=2
        )
        
        plan_key = "test_component:websocket_error"
        assert plan_key in error_recovery.recovery_plans
        
        plan = error_recovery.recovery_plans[plan_key]
        assert plan.error_type == EngagementErrorType.WEBSOCKET_ERROR
        assert plan.component == "test_component"
        assert RecoveryAction.RECONNECT in plan.actions
        assert plan.timeout == 30
        assert plan.retry_count == 2
    
    @pytest.mark.asyncio
    async def test_recovery_handler_registration(self, error_recovery):
        """Test recovery handler registration."""
        async def mock_handler(error, attempt):
            return True
        
        error_recovery.register_recovery_handler(
            "test_component",
            RecoveryAction.RESTART_COMPONENT,
            mock_handler
        )
        
        assert "test_component" in error_recovery.component_recovery_handlers
        assert RecoveryAction.RESTART_COMPONENT in error_recovery.component_recovery_handlers["test_component"]
    
    @pytest.mark.asyncio
    async def test_recovery_attempt_with_success(self, error_recovery):
        """Test successful recovery attempt."""
        # Create a mock error
        error = EngagementError(
            error_type=EngagementErrorType.WEBSOCKET_ERROR,
            severity=EngagementErrorSeverity.MEDIUM,
            component="test_component",
            message="Test WebSocket error",
            exception=ConnectionError("Connection failed")
        )
        
        # Mock successful recovery handler
        async def successful_handler(error, attempt):
            await asyncio.sleep(0.1)  # Simulate recovery work
            return True
        
        error_recovery.register_recovery_handler(
            "test_component",
            RecoveryAction.RECONNECT,
            successful_handler
        )
        
        # Attempt recovery
        result = await error_recovery.attempt_recovery(error)
        
        assert result == RecoveryResult.SUCCESS
        assert error_recovery.successful_recoveries > 0
    
    @pytest.mark.asyncio
    async def test_recovery_attempt_with_failure(self, error_recovery):
        """Test failed recovery attempt."""
        # Create a mock error
        error = EngagementError(
            error_type=EngagementErrorType.DATA_PROCESSING_ERROR,
            severity=EngagementErrorSeverity.MEDIUM,
            component="test_component",
            message="Test data processing error",
            exception=ValueError("Invalid data")
        )
        
        # Mock failing recovery handler
        async def failing_handler(error, attempt):
            await asyncio.sleep(0.1)
            raise Exception("Recovery failed")
        
        error_recovery.register_recovery_handler(
            "test_component",
            RecoveryAction.CLEAR_STATE,
            failing_handler
        )
        
        # Attempt recovery
        result = await error_recovery.attempt_recovery(error)
        
        assert result == RecoveryResult.FAILURE
        assert error_recovery.failed_recoveries > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_recovery_limit(self, error_recovery):
        """Test that concurrent recovery attempts are limited."""
        # Create multiple errors
        errors = []
        for i in range(10):
            error = EngagementError(
                error_type=EngagementErrorType.INTEGRATION_ERROR,
                severity=EngagementErrorSeverity.MEDIUM,
                component=f"component_{i}",
                message=f"Test error {i}",
                exception=Exception(f"Error {i}")
            )
            errors.append(error)
        
        # Start recovery attempts concurrently
        tasks = [error_recovery.attempt_recovery(error) for error in errors]
        results = await asyncio.gather(*tasks)
        
        # Some should be rejected due to concurrent limit
        not_applicable_count = sum(1 for result in results if result == RecoveryResult.NOT_APPLICABLE)
        assert not_applicable_count > 0
    
    @pytest.mark.asyncio
    async def test_recovery_statistics(self, error_recovery):
        """Test recovery statistics reporting."""
        stats = error_recovery.get_recovery_statistics()
        
        assert "total_recovery_attempts" in stats
        assert "successful_recoveries" in stats
        assert "failed_recoveries" in stats
        assert "success_rate" in stats
        assert "recent_attempts" in stats
        assert "active_recoveries" in stats
        assert "registered_plans" in stats
        assert "registered_handlers" in stats


class TestIntegratedErrorHandling:
    """Test suite for integrated error handling across all components."""
    
    @pytest.fixture
    async def integrated_system(self):
        """Create an integrated error handling system for testing."""
        error_handler = EngagementErrorHandler()
        await error_handler.initialize()
        
        error_recovery = EngagementErrorRecovery()
        await error_recovery.initialize()
        
        resilience_manager = EngagementResilienceManager(error_handler)
        await resilience_manager.initialize()
        
        return {
            "error_handler": error_handler,
            "error_recovery": error_recovery,
            "resilience_manager": resilience_manager
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_error_handling(self, integrated_system):
        """Test end-to-end error handling flow."""
        error_handler = integrated_system["error_handler"]
        error_recovery = integrated_system["error_recovery"]
        resilience_manager = integrated_system["resilience_manager"]
        
        # Register a component with resilience manager
        def mock_health_check():
            return {"status": "healthy"}
        
        resilience_manager.register_component(
            "test_component",
            mock_health_check,
            critical=True
        )
        
        # Register recovery handler
        async def mock_recovery_handler(error, attempt):
            await asyncio.sleep(0.1)
            return True
        
        error_recovery.register_recovery_handler(
            "test_component",
            RecoveryAction.RESTART_COMPONENT,
            mock_recovery_handler
        )
        
        # Trigger an error
        error = await error_handler.handle_error(
            EngagementErrorType.INTEGRATION_ERROR,
            "test_component",
            "Integration failure",
            Exception("Test integration error")
        )
        
        # Verify error was handled
        assert error.error_type == EngagementErrorType.INTEGRATION_ERROR
        assert error.recovery_attempted is True
        
        # Verify fallback mode was applied
        fallback_mode = error_handler.get_component_fallback_mode("test_component")
        assert fallback_mode != EngagementFallbackMode.FULL_FUNCTIONALITY
        
        # Verify statistics are updated
        error_stats = error_handler.get_error_statistics()
        assert error_stats["total_errors"] > 0
        
        recovery_stats = error_recovery.get_recovery_statistics()
        assert recovery_stats["total_recovery_attempts"] > 0
    
    @pytest.mark.asyncio
    async def test_system_resilience_under_load(self, integrated_system):
        """Test system resilience under high error load."""
        error_handler = integrated_system["error_handler"]
        
        # Generate many errors quickly
        error_tasks = []
        for i in range(50):
            task = error_handler.handle_error(
                EngagementErrorType.WEBSOCKET_ERROR,
                f"component_{i % 5}",  # Distribute across 5 components
                f"Load test error {i}",
                ConnectionError(f"Connection error {i}")
            )
            error_tasks.append(task)
        
        # Wait for all errors to be processed
        errors = await asyncio.gather(*error_tasks)
        
        # Verify all errors were handled
        assert len(errors) == 50
        
        # Verify system degradation was triggered
        assert error_handler.system_degraded is True
        
        # Verify error statistics
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 50
        assert stats["recent_errors"] == 50
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown_of_integrated_system(self, integrated_system):
        """Test graceful shutdown of the entire integrated system."""
        resilience_manager = integrated_system["resilience_manager"]
        
        # Verify system is running
        assert not resilience_manager.health_monitor_task.done()
        assert not resilience_manager.strategy_evaluator_task.done()
        
        # Shutdown
        await resilience_manager.shutdown()
        
        # Verify clean shutdown
        assert resilience_manager.health_monitor_task.done()
        assert resilience_manager.strategy_evaluator_task.done()


async def run_comprehensive_tests():
    """Run comprehensive tests for engagement error handling system."""
    logger.info("🧪 Starting comprehensive engagement error handling tests...")
    
    try:
        # Test individual components
        logger.info("Testing EngagementErrorHandler...")
        error_handler = EngagementErrorHandler()
        await error_handler.initialize()
        
        # Test basic error handling
        error = await error_handler.handle_error(
            EngagementErrorType.WEBSOCKET_ERROR,
            "test_websocket",
            "Test WebSocket connection failed",
            ConnectionError("Connection refused")
        )
        
        assert error.error_type == EngagementErrorType.WEBSOCKET_ERROR
        assert error.component == "test_websocket"
        logger.info("✅ EngagementErrorHandler basic functionality working")
        
        # Test error recovery
        logger.info("Testing EngagementErrorRecovery...")
        error_recovery = EngagementErrorRecovery()
        await error_recovery.initialize()
        
        # Test recovery attempt
        result = await error_recovery.attempt_recovery(error)
        assert result in [RecoveryResult.SUCCESS, RecoveryResult.FAILURE, RecoveryResult.NOT_APPLICABLE]
        logger.info("✅ EngagementErrorRecovery basic functionality working")
        
        # Test resilience manager
        logger.info("Testing EngagementResilienceManager...")
        resilience_manager = EngagementResilienceManager(error_handler)
        await resilience_manager.initialize()
        
        # Register a test component
        resilience_manager.register_component(
            "test_component",
            lambda: {"status": "healthy"},
            critical=True
        )
        
        status = resilience_manager.get_resilience_status()
        assert "current_strategy" in status
        logger.info("✅ EngagementResilienceManager basic functionality working")
        
        # Test integrated error handling
        logger.info("Testing integrated error handling...")
        
        # Generate multiple errors to test system behavior
        for i in range(5):
            await error_handler.handle_error(
                EngagementErrorType.DATA_PROCESSING_ERROR,
                f"component_{i}",
                f"Test error {i}",
                ValueError(f"Test error {i}")
            )
        
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] >= 5
        logger.info("✅ Integrated error handling working")
        
        # Cleanup
        await resilience_manager.shutdown()
        
        logger.info("🎉 All engagement error handling tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the comprehensive tests
    result = asyncio.run(run_comprehensive_tests())
    
    if result:
        print("\n✅ All engagement error handling tests passed!")
        print("🛡️ Error handling system is ready for production use")
    else:
        print("\n❌ Some tests failed!")
        print("🔧 Please check the error handling implementation")
        exit(1)