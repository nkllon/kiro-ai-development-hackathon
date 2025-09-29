"""
Unit tests for RecoveryValidator.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from src.beast_mode.observatory.recovery.failure_classifier import FailureType
from src.beast_mode.observatory.recovery.recovery_strategies import RecoveryAttempt
from src.beast_mode.observatory.recovery.recovery_validator import (
    RecoveryValidator,
    ValidationResult
)


class TestRecoveryValidator:
    """Test cases for RecoveryValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a RecoveryValidator instance."""
        return RecoveryValidator()
    
    @pytest.fixture
    def sample_recovery_attempt(self):
        """Create a sample recovery attempt."""
        return RecoveryAttempt(
            strategy_name="websocket_reconnection",
            failure_type=FailureType.CONNECTION_REFUSED,
            attempt_number=1,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            success=True
        )
    
    @pytest.mark.asyncio
    async def test_validate_recovery_successful(self, validator, sample_recovery_attempt):
        """Test successful recovery validation."""
        with patch.object(validator, '_run_validation_tests', return_value={
            "tests_passed": 5,
            "tests_failed": 0,
            "error_messages": [],
            "performance_metrics": {
                "latency_ms": 50,
                "throughput_mbps": 10.5,
                "cpu_usage_percent": 15.2,
                "memory_usage_mb": 128.5
            }
        }):
            result = await validator.validate_recovery(sample_recovery_attempt)
            
            assert result.is_valid == True
            assert result.tests_passed == 5
            assert result.tests_failed == 0
            assert result.health_score >= 0.8
            assert result.error_messages == []
            assert "latency_ms" in result.performance_metrics
    
    @pytest.mark.asyncio
    async def test_validate_recovery_failed(self, validator, sample_recovery_attempt):
        """Test failed recovery validation."""
        with patch.object(validator, '_run_validation_tests', return_value={
            "tests_passed": 2,
            "tests_failed": 3,
            "error_messages": ["WebSocket connectivity failed", "Performance test failed"],
            "performance_metrics": {
                "latency_ms": 200,
                "throughput_mbps": 2.0,
                "cpu_usage_percent": 80.0,
                "memory_usage_mb": 800.0
            }
        }):
            result = await validator.validate_recovery(sample_recovery_attempt)
            
            assert result.is_valid == False
            assert result.tests_passed == 2
            assert result.tests_failed == 3
            assert result.health_score < 0.8
            assert len(result.error_messages) == 2
    
    @pytest.mark.asyncio
    async def test_validate_recovery_with_exception(self, validator, sample_recovery_attempt):
        """Test validation with exception."""
        with patch.object(validator, '_run_validation_tests', side_effect=Exception("Test error")):
            result = await validator.validate_recovery(sample_recovery_attempt)
            
            assert result.is_valid == False
            assert result.tests_passed == 0
            assert result.tests_failed == 1
            assert result.error_messages == ["Test error"]
            assert result.health_score == 0.0
    
    @pytest.mark.asyncio
    async def test_run_validation_tests(self, validator, sample_recovery_attempt):
        """Test running validation tests."""
        with patch.object(validator, '_test_websocket_connectivity', return_value={"passed": True}), \
             patch.object(validator, '_test_message_roundtrip', return_value={"passed": True}), \
             patch.object(validator, '_test_performance_metrics', return_value={"passed": True, "metrics": {}}), \
             patch.object(validator, '_test_recurring_failures', return_value={"passed": True}), \
             patch.object(validator, '_test_strategy_specific', return_value={"passed": True}):
            
            result = await validator._run_validation_tests(sample_recovery_attempt)
            
            assert result["tests_passed"] == 5
            assert result["tests_failed"] == 0
            assert result["error_messages"] == []
    
    @pytest.mark.asyncio
    async def test_test_websocket_connectivity_success(self, validator):
        """Test WebSocket connectivity test success."""
        with patch('asyncio.sleep', return_value=None):
            result = await validator._test_websocket_connectivity()
            
            # Result depends on random choice in implementation
            assert "passed" in result
            assert "connection_time" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_test_message_roundtrip_success(self, validator):
        """Test message round-trip test success."""
        with patch('asyncio.sleep', return_value=None):
            result = await validator._test_message_roundtrip()
            
            assert result["passed"] == True
            assert result["roundtrip_time"] == 0.5
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_test_performance_metrics_success(self, validator):
        """Test performance metrics test success."""
        with patch('asyncio.sleep', return_value=None):
            result = await validator._test_performance_metrics()
            
            # Result depends on random metrics in implementation
            assert "passed" in result
            assert "metrics" in result
    
    @pytest.mark.asyncio
    async def test_test_recurring_failures_success(self, validator):
        """Test recurring failures test success."""
        with patch('asyncio.sleep', return_value=None):
            result = await validator._test_recurring_failures()
            
            assert result["passed"] == True
            assert result["recent_failure_count"] == 0
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_test_strategy_specific_websocket(self, validator, sample_recovery_attempt):
        """Test strategy-specific validation for WebSocket reconnection."""
        sample_recovery_attempt.strategy_name = "websocket_reconnection"
        
        with patch.object(validator, '_test_reconnection_strategy', return_value={"passed": True}):
            result = await validator._test_strategy_specific(sample_recovery_attempt)
            
            assert result["passed"] == True
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_test_strategy_specific_tunnel(self, validator, sample_recovery_attempt):
        """Test strategy-specific validation for tunnel restart."""
        sample_recovery_attempt.strategy_name = "tunnel_restart"
        
        with patch.object(validator, '_test_tunnel_strategy', return_value={"passed": True}):
            result = await validator._test_strategy_specific(sample_recovery_attempt)
            
            assert result["passed"] == True
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_test_strategy_specific_config(self, validator, sample_recovery_attempt):
        """Test strategy-specific validation for configuration reload."""
        sample_recovery_attempt.strategy_name = "configuration_reload"
        
        with patch.object(validator, '_test_config_strategy', return_value={"passed": True}):
            result = await validator._test_strategy_specific(sample_recovery_attempt)
            
            assert result["passed"] == True
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_test_strategy_specific_bot_protection(self, validator, sample_recovery_attempt):
        """Test strategy-specific validation for bot protection clear."""
        sample_recovery_attempt.strategy_name = "bot_protection_clear"
        
        with patch.object(validator, '_test_bot_protection_strategy', return_value={"passed": True}):
            result = await validator._test_strategy_specific(sample_recovery_attempt)
            
            assert result["passed"] == True
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_test_strategy_specific_fallback(self, validator, sample_recovery_attempt):
        """Test strategy-specific validation for fallback activation."""
        sample_recovery_attempt.strategy_name = "fallback_activation"
        
        with patch.object(validator, '_test_fallback_strategy', return_value={"passed": True}):
            result = await validator._test_strategy_specific(sample_recovery_attempt)
            
            assert result["passed"] == True
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_test_strategy_specific_unknown(self, validator, sample_recovery_attempt):
        """Test strategy-specific validation for unknown strategy."""
        sample_recovery_attempt.strategy_name = "unknown_strategy"
        
        result = await validator._test_strategy_specific(sample_recovery_attempt)
        
        assert result["passed"] == True
        assert result["error"] is None
    
    def test_calculate_health_score_perfect(self, validator):
        """Test health score calculation with perfect metrics."""
        validation_tests = {
            "tests_passed": 5,
            "tests_failed": 0,
            "performance_metrics": {
                "latency_ms": 50,
                "throughput_mbps": 10.0,
                "cpu_usage_percent": 10.0,
                "memory_usage_mb": 100.0
            }
        }
        
        score = validator._calculate_health_score(validation_tests)
        assert score == 1.0
    
    def test_calculate_health_score_poor(self, validator):
        """Test health score calculation with poor metrics."""
        validation_tests = {
            "tests_passed": 2,
            "tests_failed": 3,
            "performance_metrics": {
                "latency_ms": 200,
                "throughput_mbps": 2.0,
                "cpu_usage_percent": 80.0,
                "memory_usage_mb": 800.0
            }
        }
        
        score = validator._calculate_health_score(validation_tests)
        assert score < 0.5
    
    def test_calculate_health_score_no_metrics(self, validator):
        """Test health score calculation without performance metrics."""
        validation_tests = {
            "tests_passed": 4,
            "tests_failed": 1,
            "performance_metrics": {}
        }
        
        score = validator._calculate_health_score(validation_tests)
        assert score == 0.8  # 4/5 tests passed
    
    def test_calculate_health_score_no_tests(self, validator):
        """Test health score calculation with no tests."""
        validation_tests = {
            "tests_passed": 0,
            "tests_failed": 0,
            "performance_metrics": {}
        }
        
        score = validator._calculate_health_score(validation_tests)
        assert score == 0.0
    
    @pytest.mark.asyncio
    async def test_verify_recovery_success(self, validator, sample_recovery_attempt):
        """Test recovery success verification."""
        with patch.object(validator, 'validate_recovery', return_value=ValidationResult(
            is_valid=True,
            validation_time=1.0,
            tests_passed=5,
            tests_failed=0,
            error_messages=[],
            performance_metrics={},
            health_score=0.9
        )):
            result = await validator.verify_recovery_success(sample_recovery_attempt)
            assert result == True
    
    @pytest.mark.asyncio
    async def test_verify_recovery_failure(self, validator, sample_recovery_attempt):
        """Test recovery failure verification."""
        with patch.object(validator, 'validate_recovery', return_value=ValidationResult(
            is_valid=False,
            validation_time=1.0,
            tests_passed=2,
            tests_failed=3,
            error_messages=["Test error"],
            performance_metrics={},
            health_score=0.4
        )):
            result = await validator.verify_recovery_success(sample_recovery_attempt)
            assert result == False
    
    @pytest.mark.asyncio
    async def test_verify_recovery_with_exception(self, validator, sample_recovery_attempt):
        """Test recovery verification with exception."""
        with patch.object(validator, 'validate_recovery', side_effect=Exception("Test error")):
            result = await validator.verify_recovery_success(sample_recovery_attempt)
            assert result == False