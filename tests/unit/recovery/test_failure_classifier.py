"""
Unit tests for FailureClassifier
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.beast_mode.observatory.recovery.failure_classifier import (
    FailureClassifier, FailureType, FailureContext
)


class TestFailureClassifier:
    """Test cases for FailureClassifier"""
    
    @pytest.fixture
    def classifier(self):
        """Create failure classifier instance for testing"""
        return FailureClassifier()
    
    @pytest.fixture
    def sample_context(self):
        """Create sample failure context for testing"""
        return FailureContext(
            error_message="Connection refused",
            error_code=1033,
            http_status=403,
            response_headers={"cf-ray": "12345"},
            timestamp=datetime.utcnow(),
            retry_count=2,
            connection_duration=1.5,
            last_successful_connection=datetime.utcnow() - timedelta(minutes=30)
        )
    
    @pytest.mark.asyncio
    async def test_classify_failure_by_error_code(self, classifier, sample_context):
        """Test failure classification by error code"""
        sample_context.error_code = 1033
        
        failure_type = await classifier.classify_failure(sample_context)
        
        assert failure_type == FailureType.BOT_PROTECTION_TRIGGERED
    
    @pytest.mark.asyncio
    async def test_classify_failure_by_message_pattern(self, classifier):
        """Test failure classification by message pattern"""
        context = FailureContext(error_message="Connection refused by server")
        
        failure_type = await classifier.classify_failure(context)
        
        assert failure_type == FailureType.CONNECTION_REFUSED
    
    @pytest.mark.asyncio
    async def test_classify_failure_by_http_status(self, classifier):
        """Test failure classification by HTTP status"""
        context = FailureContext(
            error_message="Some error",
            http_status=429
        )
        
        failure_type = await classifier.classify_failure(context)
        
        assert failure_type == FailureType.RATE_LIMITED
    
    @pytest.mark.asyncio
    async def test_classify_failure_by_context_analysis(self, classifier):
        """Test failure classification by context analysis"""
        context = FailureContext(
            error_message="Some unknown error",
            retry_count=10,  # High retry count
            connection_duration=0.5,  # Short connection duration
            last_successful_connection=datetime.utcnow() - timedelta(hours=2)
        )
        
        failure_type = await classifier.classify_failure(context)
        
        # Should classify as rate limited due to high retry count
        assert failure_type == FailureType.RATE_LIMITED
    
    @pytest.mark.asyncio
    async def test_classify_failure_unknown(self, classifier):
        """Test failure classification for unknown errors"""
        context = FailureContext(error_message="Completely unknown error")
        
        failure_type = await classifier.classify_failure(context)
        
        assert failure_type == FailureType.NETWORK_ERROR  # Default fallback
    
    @pytest.mark.asyncio
    async def test_detect_failure_symptoms(self, classifier):
        """Test failure detection from symptoms list"""
        symptoms = ["connection refused", "timeout occurred", "network error"]
        
        failure_type = await classifier.detect_failure_symptoms(symptoms)
        
        # Should detect connection refused from first symptom
        assert failure_type == FailureType.CONNECTION_REFUSED
    
    @pytest.mark.asyncio
    async def test_detect_failure_symptoms_empty(self, classifier):
        """Test failure detection with empty symptoms"""
        symptoms = []
        
        failure_type = await classifier.detect_failure_symptoms(symptoms)
        
        assert failure_type == FailureType.NETWORK_ERROR  # Default fallback
    
    def test_get_recovery_priority(self, classifier):
        """Test getting recovery priority for failure types"""
        # Test high priority failure
        priority = classifier.get_recovery_priority(FailureType.CONNECTION_REFUSED)
        assert priority == 1
        
        # Test low priority failure
        priority = classifier.get_recovery_priority(FailureType.BOT_PROTECTION_TRIGGERED)
        assert priority == 8
        
        # Test unknown failure
        priority = classifier.get_recovery_priority(FailureType.UNKNOWN)
        assert priority == 9
    
    def test_is_recoverable(self, classifier):
        """Test recoverability check for failure types"""
        # All failure types should be recoverable
        for failure_type in FailureType:
            assert classifier.is_recoverable(failure_type) is True
    
    @pytest.mark.asyncio
    async def test_classify_failure_exception_handling(self, classifier):
        """Test exception handling in classification"""
        # Create context that might cause issues
        context = FailureContext(error_message=None)
        
        failure_type = await classifier.classify_failure(context)
        
        # Should return UNKNOWN on exception
        assert failure_type == FailureType.UNKNOWN
    
    def test_failure_patterns_coverage(self, classifier):
        """Test that all failure types have patterns"""
        for failure_type in FailureType:
            if failure_type != FailureType.UNKNOWN:
                assert failure_type in classifier.failure_patterns
                assert len(classifier.failure_patterns[failure_type]) > 0
    
    @pytest.mark.asyncio
    async def test_classify_failure_multiple_matches(self, classifier):
        """Test classification when multiple patterns match"""
        context = FailureContext(
            error_message="Connection refused and timeout occurred"
        )
        
        failure_type = await classifier.classify_failure(context)
        
        # Should return the first matching failure type
        assert failure_type in [FailureType.CONNECTION_REFUSED, FailureType.TIMEOUT]


class TestFailureContext:
    """Test cases for FailureContext dataclass"""
    
    def test_failure_context_creation(self):
        """Test creating failure context"""
        context = FailureContext(
            error_message="Test error",
            error_code=500,
            http_status=500,
            retry_count=3
        )
        
        assert context.error_message == "Test error"
        assert context.error_code == 500
        assert context.http_status == 500
        assert context.retry_count == 3
        assert context.response_headers is None
        assert context.timestamp is None
        assert context.connection_duration is None
        assert context.last_successful_connection is None
    
    def test_failure_context_defaults(self):
        """Test failure context with defaults"""
        context = FailureContext(error_message="Test error")
        
        assert context.error_message == "Test error"
        assert context.error_code is None
        assert context.http_status is None
        assert context.response_headers is None
        assert context.timestamp is None
        assert context.retry_count == 0
        assert context.connection_duration is None
        assert context.last_successful_connection is None


class TestFailureType:
    """Test cases for FailureType enum"""
    
    def test_failure_type_values(self):
        """Test failure type enum values"""
        assert FailureType.CONNECTION_REFUSED.value == "connection_refused"
        assert FailureType.UPGRADE_FAILED.value == "upgrade_failed"
        assert FailureType.TIMEOUT.value == "timeout"
        assert FailureType.AUTHENTICATION_FAILED.value == "authentication_failed"
        assert FailureType.RATE_LIMITED.value == "rate_limited"
        assert FailureType.BOT_PROTECTION_TRIGGERED.value == "bot_protection_triggered"
        assert FailureType.NETWORK_ERROR.value == "network_error"
        assert FailureType.CONFIGURATION_ERROR.value == "configuration_error"
        assert FailureType.UNKNOWN.value == "unknown"
    
    def test_failure_type_members(self):
        """Test failure type enum members"""
        expected_members = {
            "CONNECTION_REFUSED", "UPGRADE_FAILED", "TIMEOUT",
            "AUTHENTICATION_FAILED", "RATE_LIMITED", "BOT_PROTECTION_TRIGGERED",
            "NETWORK_ERROR", "CONFIGURATION_ERROR", "UNKNOWN"
        }
        
        actual_members = {member.name for member in FailureType}
        assert actual_members == expected_members