"""
Unit tests for AI Consultation data models
"""

import pytest
from datetime import datetime, timedelta
from uuid import UUID

from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery,
    ConsultationResult,
    DoctorStatus,
    QueuedQuery,
    QueueStatus,
    BudgetStatus,
    ProcessingMode,
    QueryPriority,
    DoctorStatusReason
)


class TestConsultationQuery:
    """Test ConsultationQuery model"""
    
    def test_valid_query_creation(self):
        """Test creating a valid consultation query"""
        query = ConsultationQuery(
            user_id="test_user",
            query_text="What's causing the high CPU usage?"
        )
        
        assert query.user_id == "test_user"
        assert query.query_text == "What's causing the high CPU usage?"
        assert query.priority == QueryPriority.NORMAL
        assert query.email_notification is None
        assert isinstance(UUID(query.query_id), UUID)
    
    def test_query_with_email_notification(self):
        """Test query with valid email notification"""
        query = ConsultationQuery(
            user_id="test_user",
            query_text="Test query",
            email_notification="user@example.com"
        )
        
        assert query.email_notification == "user@example.com"
    
    def test_invalid_email_validation(self):
        """Test email validation"""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ConsultationQuery(
                user_id="test_user",
                query_text="Test query",
                email_notification="invalid-email"
            )
    
    def test_empty_query_text_validation(self):
        """Test empty query text validation"""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ConsultationQuery(
                user_id="test_user",
                query_text=""
            )
    
    def test_query_text_sanitization(self):
        """Test query text sanitization"""
        query = ConsultationQuery(
            user_id="test_user",
            query_text="<script>alert('xss')</script>What's the issue?"
        )
        
        assert "<script" not in query.query_text
        assert "&lt;script" in query.query_text


class TestConsultationResult:
    """Test ConsultationResult model"""
    
    def test_valid_result_creation(self):
        """Test creating a valid consultation result"""
        query = ConsultationQuery(
            user_id="test_user",
            query_text="Test query"
        )
        
        result = ConsultationResult(
            query_id=query.query_id,
            query=query,
            response="Test response",
            processing_mode=ProcessingMode.REAL_TIME,
            cost=0.05,
            tokens_used=100,
            processing_time=2.5
        )
        
        assert result.query_id == query.query_id
        assert result.response == "Test response"
        assert result.cost == 0.05
        assert result.tokens_used == 100
        assert result.processing_time == 2.5
        assert isinstance(UUID(result.result_id), UUID)
    
    def test_negative_cost_validation(self):
        """Test that negative costs are rejected"""
        from pydantic import ValidationError
        query = ConsultationQuery(user_id="test_user", query_text="Test")
        
        with pytest.raises(ValidationError):
            ConsultationResult(
                query_id=query.query_id,
                query=query,
                response="Test response",
                processing_mode=ProcessingMode.REAL_TIME,
                cost=-0.05,  # Negative cost should be rejected
                tokens_used=100,
                processing_time=2.5
            )


class TestDoctorStatus:
    """Test DoctorStatus model"""
    
    def test_valid_status_creation(self):
        """Test creating a valid doctor status"""
        status = DoctorStatus(
            is_available=True,
            reason=DoctorStatusReason.MANUAL,
            cost_budget_remaining=100.0,
            daily_usage=25.0,
            monthly_usage=500.0
        )
        
        assert status.is_available is True
        assert status.reason == DoctorStatusReason.MANUAL
        assert status.cost_budget_remaining == 100.0
        assert status.daily_usage == 25.0
        assert status.monthly_usage == 500.0
        assert status.active_sessions == 0
        assert status.queue_length == 0


class TestQueuedQuery:
    """Test QueuedQuery model"""
    
    def test_valid_queued_query_creation(self):
        """Test creating a valid queued query"""
        query = ConsultationQuery(
            user_id="test_user",
            query_text="Test query"
        )
        
        queued = QueuedQuery(
            query=query,
            priority=QueryPriority.HIGH,
            estimated_cost=0.10
        )
        
        assert queued.query == query
        assert queued.priority == QueryPriority.HIGH
        assert queued.estimated_cost == 0.10
        assert queued.retry_count == 0
        assert queued.can_retry is True
        assert isinstance(UUID(queued.queue_id), UUID)
    
    def test_expiry_check(self):
        """Test query expiry checking"""
        query = ConsultationQuery(user_id="test_user", query_text="Test")
        
        # Create query with old timestamp
        old_time = datetime.utcnow() - timedelta(hours=25)
        queued = QueuedQuery(
            query=query,
            queued_at=old_time
        )
        
        assert queued.is_expired is True
    
    def test_retry_limit(self):
        """Test retry limit checking"""
        query = ConsultationQuery(user_id="test_user", query_text="Test")
        
        queued = QueuedQuery(
            query=query,
            retry_count=3,
            max_retries=3
        )
        
        assert queued.can_retry is False


class TestQueueStatus:
    """Test QueueStatus model"""
    
    def test_valid_queue_status_creation(self):
        """Test creating a valid queue status"""
        status = QueueStatus(
            total_queued=50,
            processing=2,
            estimated_wait_time=timedelta(minutes=30),
            estimated_batch_cost=5.0,
            queue_capacity=1000
        )
        
        assert status.total_queued == 50
        assert status.processing == 2
        assert status.estimated_wait_time == timedelta(minutes=30)
        assert status.estimated_batch_cost == 5.0
        assert status.queue_capacity == 1000
        assert status.is_full is False
        assert status.utilization_percent == 5.0  # 50/1000 * 100
    
    def test_full_queue_detection(self):
        """Test full queue detection"""
        status = QueueStatus(
            total_queued=1000,
            processing=0,
            estimated_wait_time=timedelta(hours=1),
            estimated_batch_cost=50.0,
            queue_capacity=1000
        )
        
        assert status.is_full is True
        assert status.utilization_percent == 100.0


class TestBudgetStatus:
    """Test BudgetStatus model"""
    
    def test_valid_budget_status_creation(self):
        """Test creating a valid budget status"""
        status = BudgetStatus(
            daily_budget=100.0,
            monthly_budget=2000.0,
            daily_spent=25.0,
            monthly_spent=500.0
        )
        
        assert status.daily_budget == 100.0
        assert status.monthly_budget == 2000.0
        assert status.daily_spent == 25.0
        assert status.monthly_spent == 500.0
        assert status.daily_remaining == 75.0
        assert status.monthly_remaining == 1500.0
        assert status.is_daily_budget_exceeded is False
        assert status.is_monthly_budget_exceeded is False
        assert status.daily_utilization_percent == 25.0
        assert status.monthly_utilization_percent == 25.0
    
    def test_budget_exceeded_detection(self):
        """Test budget exceeded detection"""
        status = BudgetStatus(
            daily_budget=100.0,
            monthly_budget=2000.0,
            daily_spent=150.0,  # Exceeds daily budget
            monthly_spent=2500.0  # Exceeds monthly budget
        )
        
        assert status.is_daily_budget_exceeded is True
        assert status.is_monthly_budget_exceeded is True
        assert status.daily_remaining == 0.0  # Should not go negative
        assert status.monthly_remaining == 0.0  # Should not go negative


if __name__ == "__main__":
    pytest.main([__file__])