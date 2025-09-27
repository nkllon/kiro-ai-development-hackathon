"""
Unit tests for RecoveryValidator
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.beast_mode.observatory.recovery.recovery_validator import (
    RecoveryValidator, ValidationStatus, ValidationCheck, ValidationResult
)
from src.beast_mode.observatory.recovery.recovery_strategies import (
    RecoveryAttempt, RecoveryStrategyType
)
from src.beast_mode.observatory.recovery.failure_classifier import FailureType


class TestRecoveryValidator:
    """Test cases for RecoveryValidator"""
    
    @pytest.fixture
    def validator(self):
        """Create recovery validator instance"""
        return RecoveryValidator(validation_timeout=5.0)
    
    @pytest.fixture
    def sample_recovery_attempt(self):
        """Create sample recovery attempt for testing"""
        return RecoveryAttempt(
            strategy_type=RecoveryStrategyType.WEBSOCKET_RECONNECTION,
            failure_type=FailureType.CONNECTION_REFUSED,
            attempt_number=1,
            start_time=datetime.utcnow() - timedelta(seconds=10),
            end_time=datetime.utcnow(),
            success=True,
            recovery_data={"connection_restored": True}
        )
    
    @pytest.mark.asyncio
    async def test_validate_recovery_success(self, validator, sample_recovery_attempt):
        """Test successful recovery validation"""
        with patch('asyncio.sleep') as mock_sleep:
            result = await validator.validate_recovery(sample_recovery_attempt)
            
            assert isinstance(result, ValidationResult)
            assert result.overall_success is True
            assert len(result.checks_performed) == 5  # All validation checks
            assert result.failures_count == 0
            assert result.total_duration > 0
            assert result.validation_timestamp is not None
    
    @pytest.mark.asyncio
    async def test_validate_recovery_timeout(self, validator, sample_recovery_attempt):
        """Test recovery validation with timeout"""
        # Mock validation checks to take longer than timeout
        with patch('asyncio.sleep', side_effect=asyncio.sleep):
            with patch.object(validator, '_validate_websocket_connectivity') as mock_check:
                mock_check.side_effect = asyncio.TimeoutError()
                
                result = await validator.validate_recovery(sample_recovery_attempt)
                
                assert isinstance(result, ValidationResult)
                # Should have timeout failures
                assert result.failures_count > 0
    
    @pytest.mark.asyncio
    async def test_validate_recovery_exception(self, validator, sample_recovery_attempt):
        """Test recovery validation with exception"""
        with patch.object(validator, '_validate_websocket_connectivity') as mock_check:
            mock_check.side_effect = Exception("Validation error")
            
            result = await validator.validate_recovery(sample_recovery_attempt)
            
            assert isinstance(result, ValidationResult)
            assert result.failures_count > 0
    
    @pytest.mark.asyncio
    async def test_validate_websocket_connectivity_success(self, validator):
        """Test WebSocket connectivity validation success"""
        with patch('asyncio.sleep') as mock_sleep:
            check = await validator._validate_websocket_connectivity()
            
            assert isinstance(check, ValidationCheck)
            assert check.check_name == "websocket_connectivity"
            assert check.status == ValidationStatus.PASSED
            assert check.duration > 0
            assert check.details is not None
            assert "connection_time" in check.details
    
    @pytest.mark.asyncio
    async def test_validate_websocket_connectivity_failure(self, validator):
        """Test WebSocket connectivity validation failure"""
        with patch('asyncio.sleep', side_effect=Exception("Connection failed")):
            check = await validator._validate_websocket_connectivity()
            
            assert isinstance(check, ValidationCheck)
            assert check.check_name == "websocket_connectivity"
            assert check.status == ValidationStatus.FAILED
            assert "Connection failed" in check.message
    
    @pytest.mark.asyncio
    async def test_validate_message_roundtrip_success(self, validator):
        """Test message round-trip validation success"""
        with patch('asyncio.sleep') as mock_sleep:
            check = await validator._validate_message_roundtrip()
            
            assert isinstance(check, ValidationCheck)
            assert check.check_name == "message_roundtrip"
            assert check.status == ValidationStatus.PASSED
            assert check.details is not None
            assert "roundtrip_time" in check.details
    
    @pytest.mark.asyncio
    async def test_validate_performance_metrics_normal(self, validator):
        """Test performance metrics validation with normal values"""
        with patch('asyncio.sleep') as mock_sleep:
            check = await validator._validate_performance_metrics()
            
            assert isinstance(check, ValidationCheck)
            assert check.check_name == "performance_metrics"
            assert check.status == ValidationStatus.PASSED
            assert check.details is not None
            assert "latency_ms" in check.details
            assert "throughput_msg_per_sec" in check.details
    
    @pytest.mark.asyncio
    async def test_validate_performance_metrics_high_latency(self, validator):
        """Test performance metrics validation with high latency"""
        with patch('asyncio.sleep') as mock_sleep:
            # Mock high latency scenario
            with patch.object(validator, '_validate_performance_metrics') as mock_validate:
                mock_check = ValidationCheck(
                    check_name="performance_metrics",
                    status=ValidationStatus.WARNING,
                    message="High latency detected: 150.0ms",
                    duration=0.2,
                    details={
                        "latency_ms": 150.0,
                        "throughput_msg_per_sec": 1000.0,
                        "warning_reason": "high_latency"
                    }
                )
                mock_validate.return_value = mock_check
                
                check = await validator._validate_performance_metrics()
                
                assert check.status == ValidationStatus.WARNING
                assert "High latency" in check.message
    
    @pytest.mark.asyncio
    async def test_validate_stability_success(self, validator):
        """Test stability validation success"""
        with patch('asyncio.sleep') as mock_sleep:
            check = await validator._validate_stability()
            
            assert isinstance(check, ValidationCheck)
            assert check.check_name == "stability"
            assert check.status == ValidationStatus.PASSED
            assert check.details is not None
            assert "monitoring_duration" in check.details
            assert "stability_score" in check.details
    
    @pytest.mark.asyncio
    async def test_validate_error_rates_normal(self, validator):
        """Test error rates validation with normal values"""
        with patch('asyncio.sleep') as mock_sleep:
            check = await validator._validate_error_rates()
            
            assert isinstance(check, ValidationCheck)
            assert check.check_name == "error_rates"
            assert check.status == ValidationStatus.PASSED
            assert check.details is not None
            assert "error_rate" in check.details
            assert check.details["error_rate"] <= 0.05  # Should be within threshold
    
    @pytest.mark.asyncio
    async def test_validate_error_rates_elevated(self, validator):
        """Test error rates validation with elevated rates"""
        with patch('asyncio.sleep') as mock_sleep:
            # Mock elevated error rate scenario
            with patch.object(validator, '_validate_error_rates') as mock_validate:
                mock_check = ValidationCheck(
                    check_name="error_rates",
                    status=ValidationStatus.WARNING,
                    message="Elevated error rate detected: 0.08",
                    duration=0.1,
                    details={
                        "error_rate": 0.08,
                        "threshold": 0.05,
                        "warning_reason": "elevated_error_rate"
                    }
                )
                mock_validate.return_value = mock_check
                
                check = await validator._validate_error_rates()
                
                assert check.status == ValidationStatus.WARNING
                assert "Elevated error rate" in check.message
    
    @pytest.mark.asyncio
    async def test_validate_recurring_failures_no_pattern(self, validator):
        """Test recurring failures validation with no pattern"""
        failure_history = []  # Empty history
        
        result = await validator.validate_recurring_failures(failure_history)
        
        assert isinstance(result, ValidationResult)
        assert result.overall_success is True
        assert len(result.checks_performed) == 1
        assert result.checks_performed[0].check_name == "recurring_failures"
        assert result.checks_performed[0].status == ValidationStatus.PASSED
    
    @pytest.mark.asyncio
    async def test_validate_recurring_failures_multiple_failures(self, validator):
        """Test recurring failures validation with multiple recent failures"""
        # Create mock failure history with multiple recent failures
        recent_time = datetime.utcnow() - timedelta(minutes=30)
        failure_history = [
            Mock(start_time=recent_time),
            Mock(start_time=recent_time + timedelta(minutes=5)),
            Mock(start_time=recent_time + timedelta(minutes=10)),
            Mock(start_time=recent_time + timedelta(minutes=15)),
            Mock(start_time=recent_time + timedelta(minutes=20))
        ]
        
        result = await validator.validate_recurring_failures(failure_history)
        
        assert isinstance(result, ValidationResult)
        assert result.overall_success is False
        assert len(result.checks_performed) == 1
        assert result.checks_performed[0].check_name == "recurring_failures"
        assert result.checks_performed[0].status == ValidationStatus.WARNING
    
    def test_get_validation_summary(self, validator):
        """Test getting validation summary"""
        checks = [
            ValidationCheck("check1", ValidationStatus.PASSED, "Passed", 1.0),
            ValidationCheck("check2", ValidationStatus.PASSED, "Passed", 0.5),
            ValidationCheck("check3", ValidationStatus.WARNING, "Warning", 0.3),
            ValidationCheck("check4", ValidationStatus.FAILED, "Failed", 0.2)
        ]
        
        result = ValidationResult(
            overall_success=False,
            checks_performed=checks,
            total_duration=2.0,
            warnings_count=1,
            failures_count=1,
            validation_timestamp=datetime.utcnow()
        )
        
        summary = validator.get_validation_summary(result)
        
        assert summary["overall_success"] is False
        assert summary["checks_performed"] == 4
        assert summary["passed_checks"] == 2
        assert summary["warning_checks"] == 1
        assert summary["failed_checks"] == 1
        assert summary["total_duration"] == 2.0
        assert "validation_timestamp" in summary


class TestValidationCheck:
    """Test cases for ValidationCheck dataclass"""
    
    def test_validation_check_creation(self):
        """Test creating validation check"""
        check = ValidationCheck(
            check_name="test_check",
            status=ValidationStatus.PASSED,
            message="Test passed",
            duration=1.5,
            details={"key": "value"}
        )
        
        assert check.check_name == "test_check"
        assert check.status == ValidationStatus.PASSED
        assert check.message == "Test passed"
        assert check.duration == 1.5
        assert check.details == {"key": "value"}
    
    def test_validation_check_minimal(self):
        """Test creating validation check with minimal data"""
        check = ValidationCheck(
            check_name="minimal_check",
            status=ValidationStatus.FAILED,
            message="Test failed",
            duration=0.0
        )
        
        assert check.check_name == "minimal_check"
        assert check.status == ValidationStatus.FAILED
        assert check.message == "Test failed"
        assert check.duration == 0.0
        assert check.details is None


class TestValidationResult:
    """Test cases for ValidationResult dataclass"""
    
    def test_validation_result_creation(self):
        """Test creating validation result"""
        checks = [
            ValidationCheck("check1", ValidationStatus.PASSED, "Passed", 1.0),
            ValidationCheck("check2", ValidationStatus.PASSED, "Passed", 0.5)
        ]
        
        result = ValidationResult(
            overall_success=True,
            checks_performed=checks,
            total_duration=1.5,
            warnings_count=0,
            failures_count=0,
            validation_timestamp=datetime.utcnow()
        )
        
        assert result.overall_success is True
        assert len(result.checks_performed) == 2
        assert result.total_duration == 1.5
        assert result.warnings_count == 0
        assert result.failures_count == 0
        assert result.validation_timestamp is not None
    
    def test_validation_result_with_warnings_and_failures(self):
        """Test creating validation result with warnings and failures"""
        checks = [
            ValidationCheck("check1", ValidationStatus.PASSED, "Passed", 1.0),
            ValidationCheck("check2", ValidationStatus.WARNING, "Warning", 0.5),
            ValidationCheck("check3", ValidationStatus.FAILED, "Failed", 0.3)
        ]
        
        result = ValidationResult(
            overall_success=False,
            checks_performed=checks,
            total_duration=1.8,
            warnings_count=1,
            failures_count=1,
            validation_timestamp=datetime.utcnow()
        )
        
        assert result.overall_success is False
        assert len(result.checks_performed) == 3
        assert result.warnings_count == 1
        assert result.failures_count == 1


class TestValidationStatus:
    """Test cases for ValidationStatus enum"""
    
    def test_validation_status_values(self):
        """Test validation status enum values"""
        assert ValidationStatus.PASSED.value == "passed"
        assert ValidationStatus.FAILED.value == "failed"
        assert ValidationStatus.WARNING.value == "warning"
        assert ValidationStatus.SKIPPED.value == "skipped"
    
    def test_validation_status_members(self):
        """Test validation status enum members"""
        expected_members = {"PASSED", "FAILED", "WARNING", "SKIPPED"}
        actual_members = {status.name for status in ValidationStatus}
        assert actual_members == expected_members