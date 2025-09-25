"""
Unit tests for Repository Pattern
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

from src.beast_mode.observatory.ai_consultation.repository import (
    ConsultationRepository,
    DoctorStatusRepository,
    QueueRepository,
    RepositoryError,
    get_consultation_repository,
    get_doctor_status_repository,
    get_queue_repository
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery,
    ConsultationResult,
    DoctorStatus,
    QueuedQuery,
    ProcessingMode,
    QueryPriority,
    DoctorStatusReason
)


class TestConsultationRepository:
    """Test ConsultationRepository class"""
    
    @pytest.fixture
    def repository(self):
        """Create ConsultationRepository instance"""
        return ConsultationRepository()
    
    @pytest.fixture
    def sample_query(self):
        """Create sample consultation query"""
        return ConsultationQuery(
            user_id="test_user",
            query_text="What's causing the high CPU usage?",
            priority=QueryPriority.NORMAL
        )
    
    @pytest.fixture
    def sample_result(self, sample_query):
        """Create sample consultation result"""
        return ConsultationResult(
            query_id=sample_query.query_id,
            query=sample_query,
            response="The high CPU usage is caused by...",
            processing_mode=ProcessingMode.REAL_TIME,
            cost=0.05,
            tokens_used=100,
            processing_time=2.5
        )
    
    @pytest.mark.asyncio
    async def test_store_query_success(self, repository, sample_query):
        """Test successful query storage"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session_instance.add = MagicMock()
            mock_session_instance.commit = AsyncMock()
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await repository.store_query(sample_query)
            
            assert result == sample_query.query_id
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_query_duplicate(self, repository, sample_query):
        """Test storing duplicate query"""
        from sqlalchemy.exc import IntegrityError
        
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session_instance.add = MagicMock()
            mock_session_instance.commit = AsyncMock(side_effect=IntegrityError("", "", ""))
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            from src.beast_mode.observatory.ai_consultation.exceptions import ValidationError
            with pytest.raises(ValidationError):
                await repository.store_query(sample_query)
    
    @pytest.mark.asyncio
    async def test_get_query_found(self, repository, sample_query):
        """Test getting existing query"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            # Mock database query result
            mock_db_query = MagicMock()
            mock_db_query.query_id = sample_query.query_id
            mock_db_query.user_id = sample_query.user_id
            mock_db_query.query_text = sample_query.query_text
            mock_db_query.timestamp = sample_query.timestamp
            mock_db_query.email_notification = sample_query.email_notification
            mock_db_query.priority = sample_query.priority.value
            mock_db_query.processing_mode = None
            mock_db_query.session_id = sample_query.session_id
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_db_query
            
            mock_session_instance = AsyncMock()
            mock_session_instance.execute = AsyncMock(return_value=mock_result)
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await repository.get_query(sample_query.query_id)
            
            assert result is not None
            assert result.query_id == sample_query.query_id
            assert result.user_id == sample_query.user_id
            assert result.query_text == sample_query.query_text
    
    @pytest.mark.asyncio
    async def test_get_query_not_found(self, repository):
        """Test getting non-existent query"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            
            mock_session_instance = AsyncMock()
            mock_session_instance.execute = AsyncMock(return_value=mock_result)
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await repository.get_query("nonexistent")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_store_result_success(self, repository, sample_result):
        """Test successful result storage"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session_instance.add = MagicMock()
            mock_session_instance.commit = AsyncMock()
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await repository.store_result(sample_result)
            
            assert result == sample_result.result_id
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_results(self, repository):
        """Test searching consultation results"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            with patch.object(repository, 'get_query') as mock_get_query:
                # Mock query result
                mock_query = ConsultationQuery(
                    user_id="test_user",
                    query_text="test query"
                )
                mock_get_query.return_value = mock_query
                
                # Mock database result
                mock_db_result = MagicMock()
                mock_db_result.result_id = str(uuid4())
                mock_db_result.query_id = mock_query.query_id
                mock_db_result.response = "test response"
                mock_db_result.processing_mode = "real_time"
                mock_db_result.cost = 0.05
                mock_db_result.tokens_used = 100
                mock_db_result.processing_time = 2.5
                mock_db_result.timestamp = datetime.utcnow()
                mock_db_result.confidence_score = None
                mock_db_result.error_message = None
                mock_db_result.retry_count = 0
                
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = [mock_db_result]
                
                mock_session_instance = AsyncMock()
                mock_session_instance.execute = AsyncMock(return_value=mock_result)
                mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
                
                results = await repository.search_results("test_user", "test query")
                
                assert len(results) == 1
                assert results[0].query.user_id == "test_user"
    
    @pytest.mark.asyncio
    async def test_cleanup_old_results(self, repository):
        """Test cleaning up old results"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            mock_result1 = MagicMock()
            mock_result1.rowcount = 5
            mock_result2 = MagicMock()
            mock_result2.rowcount = 2
            
            mock_session_instance = AsyncMock()
            mock_session_instance.execute = AsyncMock(side_effect=[mock_result1, mock_result2])
            mock_session_instance.commit = AsyncMock()
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await repository.cleanup_old_results(30)
            
            assert result == 7  # 5 + 2
            assert mock_session_instance.execute.call_count == 2
            mock_session_instance.commit.assert_called_once()


class TestDoctorStatusRepository:
    """Test DoctorStatusRepository class"""
    
    @pytest.fixture
    def repository(self):
        """Create DoctorStatusRepository instance"""
        return DoctorStatusRepository()
    
    @pytest.fixture
    def sample_status(self):
        """Create sample doctor status"""
        return DoctorStatus(
            is_available=True,
            reason=DoctorStatusReason.MANUAL,
            cost_budget_remaining=100.0,
            daily_usage=25.0,
            monthly_usage=500.0
        )
    
    @pytest.mark.asyncio
    async def test_get_status_found(self, repository, sample_status):
        """Test getting existing doctor status"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            # Mock database status result
            mock_db_status = MagicMock()
            mock_db_status.is_available = sample_status.is_available
            mock_db_status.reason = sample_status.reason.value
            mock_db_status.cost_budget_remaining = sample_status.cost_budget_remaining
            mock_db_status.daily_usage = sample_status.daily_usage
            mock_db_status.monthly_usage = sample_status.monthly_usage
            mock_db_status.last_updated = sample_status.last_updated
            mock_db_status.next_budget_reset = sample_status.next_budget_reset
            mock_db_status.active_sessions = sample_status.active_sessions
            mock_db_status.queue_length = sample_status.queue_length
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_db_status
            
            mock_session_instance = AsyncMock()
            mock_session_instance.execute = AsyncMock(return_value=mock_result)
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await repository.get_status()
            
            assert result is not None
            assert result.is_available == sample_status.is_available
            assert result.cost_budget_remaining == sample_status.cost_budget_remaining
    
    @pytest.mark.asyncio
    async def test_get_status_not_found(self, repository):
        """Test getting non-existent doctor status"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            
            mock_session_instance = AsyncMock()
            mock_session_instance.execute = AsyncMock(return_value=mock_result)
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await repository.get_status()
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_update_status_existing(self, repository, sample_status):
        """Test updating existing doctor status"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            # Mock existing status
            mock_existing = MagicMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_existing
            
            mock_session_instance = AsyncMock()
            mock_session_instance.execute = AsyncMock(return_value=mock_result)
            mock_session_instance.commit = AsyncMock()
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            await repository.update_status(sample_status)
            
            # Should call execute twice (select and update)
            assert mock_session_instance.execute.call_count == 2
            mock_session_instance.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_status_new(self, repository, sample_status):
        """Test creating new doctor status"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            # Mock no existing status
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            
            mock_session_instance = AsyncMock()
            mock_session_instance.execute = AsyncMock(return_value=mock_result)
            mock_session_instance.add = MagicMock()
            mock_session_instance.commit = AsyncMock()
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            await repository.update_status(sample_status)
            
            mock_session_instance.execute.assert_called_once()
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()


class TestQueueRepository:
    """Test QueueRepository class"""
    
    @pytest.fixture
    def repository(self):
        """Create QueueRepository instance"""
        return QueueRepository()
    
    @pytest.fixture
    def sample_queued_query(self):
        """Create sample queued query"""
        query = ConsultationQuery(
            user_id="test_user",
            query_text="Test queued query"
        )
        return QueuedQuery(
            query=query,
            priority=QueryPriority.HIGH,
            estimated_cost=0.10
        )
    
    @pytest.mark.asyncio
    async def test_add_to_queue_success(self, repository, sample_queued_query):
        """Test successful queue addition"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            with patch('src.beast_mode.observatory.ai_consultation.repository.ConsultationRepository') as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.store_query = AsyncMock()
                mock_repo_class.return_value = mock_repo
                
                mock_session_instance = AsyncMock()
                mock_session_instance.add = MagicMock()
                mock_session_instance.commit = AsyncMock()
                mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
                
                result = await repository.add_to_queue(sample_queued_query)
                
                assert result == sample_queued_query.queue_id
                mock_repo.store_query.assert_called_once()
                mock_session_instance.add.assert_called_once()
                mock_session_instance.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_next_batch(self, repository):
        """Test getting next batch of queries"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            with patch('src.beast_mode.observatory.ai_consultation.repository.ConsultationRepository') as mock_repo_class:
                # Mock consultation repository
                mock_repo = AsyncMock()
                mock_query = ConsultationQuery(user_id="test_user", query_text="test")
                mock_repo.get_query = AsyncMock(return_value=mock_query)
                mock_repo_class.return_value = mock_repo
                
                # Mock database queued item
                mock_db_queued = MagicMock()
                mock_db_queued.queue_id = str(uuid4())
                mock_db_queued.query_id = mock_query.query_id
                mock_db_queued.queued_at = datetime.utcnow()
                mock_db_queued.priority = "high"
                mock_db_queued.estimated_cost = 0.10
                mock_db_queued.retry_count = 0
                mock_db_queued.max_retries = 3
                mock_db_queued.processing_started_at = None
                
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = [mock_db_queued]
                
                mock_session_instance = AsyncMock()
                mock_session_instance.execute = AsyncMock(return_value=mock_result)
                mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
                
                results = await repository.get_next_batch(5)
                
                assert len(results) == 1
                assert results[0].queue_id == mock_db_queued.queue_id
    
    @pytest.mark.asyncio
    async def test_get_queue_stats(self, repository):
        """Test getting queue statistics"""
        with patch('src.beast_mode.observatory.ai_consultation.repository.get_database_session') as mock_session:
            # Mock query results
            mock_results = [
                MagicMock(scalar=MagicMock(return_value=10)),  # total_queued
                MagicMock(scalar=MagicMock(return_value=3)),   # processing
                MagicMock(fetchall=MagicMock(return_value=[('high', 5), ('normal', 5)]))  # by_priority
            ]
            
            mock_session_instance = AsyncMock()
            mock_session_instance.execute = AsyncMock(side_effect=mock_results)
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            stats = await repository.get_queue_stats()
            
            assert stats['total_queued'] == 10
            assert stats['processing'] == 3
            assert stats['waiting'] == 7
            assert 'by_priority' in stats


class TestRepositoryIntegration:
    """Test repository integration functions"""
    
    @pytest.mark.asyncio
    async def test_get_consultation_repository(self):
        """Test getting consultation repository"""
        repo = await get_consultation_repository()
        assert isinstance(repo, ConsultationRepository)
    
    @pytest.mark.asyncio
    async def test_get_doctor_status_repository(self):
        """Test getting doctor status repository"""
        repo = await get_doctor_status_repository()
        assert isinstance(repo, DoctorStatusRepository)
    
    @pytest.mark.asyncio
    async def test_get_queue_repository(self):
        """Test getting queue repository"""
        repo = await get_queue_repository()
        assert isinstance(repo, QueueRepository)


class TestRepositoryError:
    """Test RepositoryError exception"""
    
    def test_repository_error_creation(self):
        """Test creating RepositoryError"""
        error = RepositoryError("Operation failed", "store_query")
        
        assert error.message == "Operation failed"
        assert error.error_code == "REPOSITORY_ERROR"
        assert error.details["operation"] == "store_query"
        assert error.retry_possible is True
    
    def test_repository_error_without_operation(self):
        """Test creating RepositoryError without operation"""
        error = RepositoryError("Operation failed")
        
        assert error.message == "Operation failed"
        assert error.details["operation"] is None


if __name__ == "__main__":
    pytest.main([__file__])