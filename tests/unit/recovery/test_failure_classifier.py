"""
Unit tests for FailureClassifier.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from src.beast_mode.observatory.recovery.failure_classifier import (
    FailureClassifier,
    FailureType,
    FailureData
)


class TestFailureClassifier:
    """Test cases for FailureClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create a FailureClassifier instance."""
        return FailureClassifier()
    
    @pytest.fixture
    def sample_failure_data(self):
        """Create sample failure data."""
        return FailureData(
            error_code=1033,
            error_message="Cloudflare bot protection triggered",
            http_status=403,
            response_headers={"cf-ray": "1234567890"},
            connection_attempts=5,
            symptoms=["connection refused", "timeout"]
        )
    
    @pytest.mark.asyncio
    async def test_classify_bot_protection_failure(self, classifier, sample_failure_data):
        """Test classification of bot protection failure."""
        failure_type = await classifier.classify_failure(sample_failure_data)
        assert failure_type == FailureType.BOT_PROTECTION_TRIGGERED
    
    @pytest.mark.asyncio
    async def test_classify_connection_refused(self, classifier):
        """Test classification of connection refused failure."""
        failure_data = FailureData(
            error_message="Connection refused",
            http_status=502,
            symptoms=["connection refused"]
        )
        
        failure_type = await classifier.classify_failure(failure_data)
        assert failure_type == FailureType.CONNECTION_REFUSED
    
    @pytest.mark.asyncio
    async def test_classify_timeout_failure(self, classifier):
        """Test classification of timeout failure."""
        failure_data = FailureData(
            error_message="Connection timed out",
            symptoms=["timeout"]
        )
        
        failure_type = await classifier.classify_failure(failure_data)
        assert failure_type == FailureType.TIMEOUT
    
    @pytest.mark.asyncio
    async def test_classify_rate_limited(self, classifier):
        """Test classification of rate limited failure."""
        failure_data = FailureData(
            http_status=429,
            error_message="Too many requests",
            connection_attempts=15
        )
        
        failure_type = await classifier.classify_failure(failure_data)
        assert failure_type == FailureType.RATE_LIMITED
    
    @pytest.mark.asyncio
    async def test_classify_authentication_failed(self, classifier):
        """Test classification of authentication failure."""
        failure_data = FailureData(
            http_status=401,
            error_message="Authentication failed"
        )
        
        failure_type = await classifier.classify_failure(failure_data)
        assert failure_type == FailureType.AUTHENTICATION_FAILED
    
    @pytest.mark.asyncio
    async def test_classify_upgrade_failed(self, classifier):
        """Test classification of upgrade failed."""
        failure_data = FailureData(
            error_message="WebSocket upgrade failed"
        )
        
        failure_type = await classifier.classify_failure(failure_data)
        assert failure_type == FailureType.UPGRADE_FAILED
    
    @pytest.mark.asyncio
    async def test_classify_unknown_failure(self, classifier):
        """Test classification of unknown failure."""
        failure_data = FailureData(
            error_message="Some random error"
        )
        
        failure_type = await classifier.classify_failure(failure_data)
        assert failure_type == FailureType.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_detect_failure_from_symptoms(self, classifier):
        """Test failure detection from symptoms."""
        symptoms = ["connection refused", "timeout"]
        failure_type = await classifier.detect_failure_from_symptoms(symptoms)
        assert failure_type == FailureType.CONNECTION_REFUSED
    
    def test_get_recovery_priority(self, classifier):
        """Test recovery priority calculation."""
        assert classifier.get_recovery_priority(FailureType.CONNECTION_REFUSED) == 1
        assert classifier.get_recovery_priority(FailureType.UPGRADE_FAILED) == 2
        assert classifier.get_recovery_priority(FailureType.TIMEOUT) == 2
        assert classifier.get_recovery_priority(FailureType.AUTHENTICATION_FAILED) == 3
        assert classifier.get_recovery_priority(FailureType.RATE_LIMITED) == 4
        assert classifier.get_recovery_priority(FailureType.BOT_PROTECTION_TRIGGERED) == 5
        assert classifier.get_recovery_priority(FailureType.UNKNOWN) == 3
    
    def test_get_estimated_recovery_time(self, classifier):
        """Test estimated recovery time calculation."""
        assert classifier.get_estimated_recovery_time(FailureType.CONNECTION_REFUSED) == 30
        assert classifier.get_estimated_recovery_time(FailureType.UPGRADE_FAILED) == 45
        assert classifier.get_estimated_recovery_time(FailureType.TIMEOUT) == 60
        assert classifier.get_estimated_recovery_time(FailureType.AUTHENTICATION_FAILED) == 30
        assert classifier.get_estimated_recovery_time(FailureType.RATE_LIMITED) == 120
        assert classifier.get_estimated_recovery_time(FailureType.BOT_PROTECTION_TRIGGERED) == 300
        assert classifier.get_estimated_recovery_time(FailureType.UNKNOWN) == 60
    
    @pytest.mark.asyncio
    async def test_classify_failure_with_exception(self, classifier):
        """Test classification when an exception occurs."""
        with patch.object(classifier, '_analyze_failure', side_effect=Exception("Test error")):
            failure_data = FailureData(error_message="test")
            failure_type = await classifier.classify_failure(failure_data)
            assert failure_type == FailureType.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_classify_failure_with_cloudflare_headers(self, classifier):
        """Test classification with Cloudflare headers."""
        failure_data = FailureData(
            response_headers={
                "cf-ray": "1234567890",
                "cf-cache-status": "MISS"
            }
        )
        
        failure_type = await classifier.classify_failure(failure_data)
        assert failure_type == FailureType.BOT_PROTECTION_TRIGGERED
    
    @pytest.mark.asyncio
    async def test_classify_failure_with_high_connection_attempts(self, classifier):
        """Test classification with high connection attempts."""
        failure_data = FailureData(
            connection_attempts=15,
            error_message="Connection failed"
        )
        
        failure_type = await classifier.classify_failure(failure_data)
        assert failure_type == FailureType.RATE_LIMITED