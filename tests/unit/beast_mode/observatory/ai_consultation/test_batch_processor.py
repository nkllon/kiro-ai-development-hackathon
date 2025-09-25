"""
Unit tests for Batch Query Processor
Tests batch processing, cost optimization, deduplication, and failure handling.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from src.beast_mode.observatory.ai_consultation.batch_processor import (
    BatchQueryProcessor, BatchStatus, BatchConfiguration, BatchMetrics, get_batch_processor
)
from src.beast_mode.observatory.ai_consultation.query_queue import QueuedQuery, QueueStatus
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, ConsultationResult, QueryPriority
)
from src.beast_mode.observatory.ai_consultation.exceptions import ProcessingError


class TestBatchConfiguration:
    """Test BatchConfiguration functionality"""
    
    def test_batch_configuration_defaults(self):
        """Test default batch configuration"""
        config = BatchConfiguration()
        
        assert config.max_batch_size == 10
        assert config.min_batch_size == 1
        assert config.max_cost_per_batch == 5.0
        assert config.deduplication_enabled is True
        assert config.cost_optimization_enabled is True
        assert config.parallel_processing is True
        assert config.max_concurrent_queries == 5
    
    def test_batch_configuration_custom(self):
        """Test custom batch configuration"""
        config = BatchConfiguration(
            max_batch_size=20,
            min_batch_size=3,
            max_cost_per_batch=10.0,
            deduplication_enabled=False,
            parallel_processing=False
        )
        
        assert config.max_batch_size == 20
        assert config.min_batch_size == 3
        assert config.max_cost_per_batch == 10.0
        assert config.deduplication_enabled is False
        assert config.parallel_processing is False
    
    def test_batch_configuration_to_dict(self):
        """Test converting configuration to dictionary"""
        config = BatchConfiguration(
            max_batch_size=15,
            max_cost_per_batch=7.5
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['max_batch_size'] == 15
        assert config_dict['max_cost_per_batch'] == 7.5
        assert 'deduplication_enabled' in config_dict
        assert 'parallel_processing' in config_dict


class TestBatchMetrics:
    """Test BatchMetrics functionality"""
    
    def test_batch_metrics_creation(self):
        """Test creating batch metrics"""
        start_time = datetime.utcnow()
        
        metrics = BatchMetrics(
            batch_id="test-batch-123",
            start_time=start_time,
            end_time=None,
            queries_processed=5,
            queries_successful=4,
            queries_failed=1,
            queries_deduplicated=2,
            total_cost=1.25,
            total_processing_time=15.5,
            batch_size=5,
            cost_per_query_avg=0.25,
            processing_time_avg=3.1
        )
        
        assert metrics.batch_id == "test-batch-123"
        assert metrics.start_time == start_time
        assert metrics.queries_processed == 5
        assert metrics.queries_successful == 4
        assert metrics.queries_failed == 1
        assert metrics.queries_deduplicated == 2
        assert metrics.total_cost == 1.25
        assert metrics.cost_per_query_avg == 0.25
    
    def test_batch_metrics_to_dict(self):
        """Test converting batch metrics to dictionary"""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=5)
        
        metrics = BatchMetrics(
            batch_id="test-batch-456",
            start_time=start_time,
            end_time=end_time,
            queries_processed=3,
            queries_successful=3,
            queries_failed=0,
            queries_deduplicated=1,
            total_cost=0.75,
            total_processing_time=8.2,
            batch_size=3,
            cost_per_query_avg=0.25,
            processing_time_avg=2.73
        )
        
        metrics_dict = metrics.to_dict()
        
        assert metrics_dict['batch_id'] == "test-batch-456"
        assert metrics_dict['queries_processed'] == 3
        assert metrics_dict['queries_successful'] == 3
        assert metrics_dict['queries_failed'] == 0
        assert metrics_dict['total_cost'] == 0.75
        assert metrics_dict['start_time'] == start_time.isoformat()
        assert metrics_dict['end_time'] == end_time.isoformat()


class TestBatchQueryProcessor:
    """Test BatchQueryProcessor functionality"""
    
    @pytest.fixture
    async def batch_processor(self):
        """Create batch processor for testing"""
        config = BatchConfiguration(
            max_batch_size=5,
            min_batch_size=1,
            max_cost_per_batch=2.0,
            deduplication_enabled=True,
            parallel_processing=False,  # Easier to test sequentially
            max_concurrent_queries=2,
            batch_timeout=timedelta(minutes=1)
        )
        
        processor = BatchQueryProcessor(
            config=config,
            processing_interval=1.0,  # Fast for testing
            max_idle_time=timedelta(minutes=1)
        )
        
        return processor
    
    @pytest.fixture
    def sample_queued_query(self):
        """Create sample queued query"""
        query = ConsultationQuery(
            query_id="test-query-123",
            user_id="test-user",
            query_text="What is the system status?",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        return QueuedQuery(
            queue_id="queued-123",
            original_query=query,
            priority=QueryPriority.NORMAL,
            status=QueueStatus.PROCESSING,
            queued_at=datetime.utcnow(),
            estimated_processing_time=timedelta(minutes=2),
            estimated_cost=0.15,
            retry_count=0,
            max_retries=3,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            metadata={}
        )
    
    async def test_processor_initialization(self, batch_processor):
        """Test processor initializes correctly"""
        assert batch_processor.status == BatchStatus.IDLE
        assert batch_processor.config.max_batch_size == 5
        assert batch_processor.config.min_batch_size == 1
        assert batch_processor.stats['batches_processed'] == 0
        assert len(batch_processor.query_cache) == 0
    
    def test_query_hash_generation(self, batch_processor):
        """Test query hash generation for deduplication"""
        query1 = ConsultationQuery(
            query_id="q1",
            user_id="user1",
            query_text="What is the system status?",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        query2 = ConsultationQuery(
            query_id="q2",
            user_id="user1",
            query_text="What is the system status?",  # Same text
            priority=QueryPriority.HIGH,  # Different priority
            timestamp=datetime.utcnow()
        )
        
        query3 = ConsultationQuery(
            query_id="q3",
            user_id="user2",
            query_text="What is the system status?",  # Same text, different user
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        hash1 = batch_processor._get_query_hash(query1)
        hash2 = batch_processor._get_query_hash(query2)
        hash3 = batch_processor._get_query_hash(query3)
        
        # Same user, same text should have same hash
        assert hash1 == hash2
        
        # Different user should have different hash
        assert hash1 != hash3
        
        # All hashes should be strings
        assert isinstance(hash1, str)
        assert isinstance(hash2, str)
        assert isinstance(hash3, str)
    
    def test_cache_cleanup(self, batch_processor):
        """Test cache cleanup functionality"""
        # Add some cache entries
        old_time = datetime.utcnow() - timedelta(hours=2)
        recent_time = datetime.utcnow() - timedelta(minutes=30)
        
        batch_processor.query_cache = {
            "old_hash": (old_time, "old result"),
            "recent_hash": (recent_time, "recent result")
        }
        
        # Run cleanup
        batch_processor._cleanup_cache()
        
        # Old entry should be removed, recent should remain
        assert "old_hash" not in batch_processor.query_cache
        assert "recent_hash" in batch_processor.query_cache
    
    async def test_processor_stats(self, batch_processor):
        """Test getting processor statistics"""
        # Set some test statistics
        batch_processor.stats['batches_processed'] = 5
        batch_processor.stats['total_queries_processed'] = 25
        batch_processor.stats['total_cost'] = 2.50
        
        stats = await batch_processor.get_processor_stats()
        
        assert 'batch_processor_stats' in stats
        assert 'current_status' in stats
        assert 'configuration' in stats
        assert 'cache_stats' in stats
        
        assert stats['batch_processor_stats']['batches_processed'] == 5
        assert stats['batch_processor_stats']['total_queries_processed'] == 25
        assert stats['batch_processor_stats']['total_cost'] == 2.50
        assert stats['current_status'] == BatchStatus.IDLE.value
    
    async def test_pause_resume_processing(self, batch_processor):
        """Test pausing and resuming processing"""
        # Initially idle
        assert batch_processor.status == BatchStatus.IDLE
        
        # Can't pause when idle
        paused = await batch_processor.pause_processing()
        assert not paused
        
        # Set to processing
        batch_processor.status = BatchStatus.PROCESSING
        
        # Should be able to pause
        paused = await batch_processor.pause_processing()
        assert paused
        assert batch_processor.status == BatchStatus.PAUSED
        
        # Should be able to resume
        resumed = await batch_processor.resume_processing()
        assert resumed
        assert batch_processor.status == BatchStatus.IDLE
    
    async def test_health_status_healthy(self, batch_processor):
        """Test health status when processor is healthy"""
        # Set good statistics
        batch_processor.stats['batches_processed'] = 10
        batch_processor.stats['batches_successful'] = 9
        batch_processor.stats['batches_failed'] = 1
        
        health = await batch_processor.get_health_status()
        
        assert health.component == "batch_query_processor"
        assert health.status == "healthy"
        assert health.error_message is None
        assert health.metadata['success_rate'] == 0.9
    
    async def test_health_status_degraded(self, batch_processor):
        """Test health status when processor is degraded"""
        # Set poor statistics
        batch_processor.stats['batches_processed'] = 10
        batch_processor.stats['batches_successful'] = 5
        batch_processor.stats['batches_failed'] = 5
        
        health = await batch_processor.get_health_status()
        
        assert health.component == "batch_query_processor"
        assert health.status == "degraded"
        assert "success rate" in health.error_message.lower()
    
    async def test_health_status_critical(self, batch_processor):
        """Test health status when processor is in error state"""
        batch_processor.status = BatchStatus.ERROR
        
        health = await batch_processor.get_health_status()
        
        assert health.component == "batch_query_processor"
        assert health.status == "critical"
        assert "error state" in health.error_message.lower()
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    async def test_build_batch_empty_queue(self, mock_flags, mock_get_queue, batch_processor):
        """Test building batch from empty queue"""
        mock_flags.is_enabled.return_value = True
        
        # Mock empty queue
        mock_queue = AsyncMock()
        mock_queue.dequeue.return_value = None
        mock_get_queue.return_value = mock_queue
        
        batch = await batch_processor._build_batch(mock_queue)
        
        assert len(batch) == 0
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    async def test_build_batch_with_queries(self, mock_flags, mock_get_queue, batch_processor, sample_queued_query):
        """Test building batch with available queries"""
        mock_flags.is_enabled.return_value = True
        
        # Mock queue with queries
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = [sample_queued_query, None]  # One query then empty
        mock_get_queue.return_value = mock_queue
        
        batch = await batch_processor._build_batch(mock_queue)
        
        assert len(batch) == 1
        assert batch[0] == sample_queued_query
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    async def test_build_batch_cost_limit(self, mock_flags, mock_get_queue, batch_processor):
        """Test batch building respects cost limits"""
        mock_flags.is_enabled.return_value = True
        
        # Create expensive queries
        expensive_query = QueuedQuery(
            queue_id="expensive-1",
            original_query=MagicMock(),
            priority=QueryPriority.NORMAL,
            status=QueueStatus.PROCESSING,
            queued_at=datetime.utcnow(),
            estimated_processing_time=None,
            estimated_cost=1.5,  # High cost
            retry_count=0,
            max_retries=3,
            expires_at=None,
            metadata={}
        )
        
        very_expensive_query = QueuedQuery(
            queue_id="expensive-2",
            original_query=MagicMock(),
            priority=QueryPriority.NORMAL,
            status=QueueStatus.PROCESSING,
            queued_at=datetime.utcnow(),
            estimated_processing_time=None,
            estimated_cost=1.0,  # Would exceed batch limit of 2.0
            retry_count=0,
            max_retries=3,
            expires_at=None,
            metadata={}
        )
        
        # Mock queue
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = [expensive_query, very_expensive_query, None]
        mock_get_queue.return_value = mock_queue
        
        batch = await batch_processor._build_batch(mock_queue)
        
        # Should only include first query due to cost limit
        assert len(batch) == 1
        assert batch[0] == expensive_query
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_request_processor')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_llm_service')
    async def test_process_single_query_success(self, mock_get_llm, mock_get_processor, batch_processor, sample_queued_query):
        """Test successful processing of single query"""
        # Mock processors
        mock_processor = AsyncMock()
        mock_processed_request = MagicMock()
        mock_processed_request.original_query = sample_queued_query.original_query
        mock_processor.process_request.return_value = mock_processed_request
        mock_get_processor.return_value = mock_processor
        
        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "System is healthy"
        mock_response.cost.total_cost = 0.12
        mock_response.provider.value = "mock"
        mock_response.model.value = "mock-model"
        mock_response.usage.total_tokens = 50
        mock_llm.generate_response.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Mock queue
        mock_queue = AsyncMock()
        
        # Initialize metrics
        batch_processor.current_metrics = BatchMetrics(
            batch_id="test-batch",
            start_time=datetime.utcnow(),
            end_time=None,
            queries_processed=0,
            queries_successful=0,
            queries_failed=0,
            queries_deduplicated=0,
            total_cost=0.0,
            total_processing_time=0.0,
            batch_size=1,
            cost_per_query_avg=0.0,
            processing_time_avg=0.0
        )
        
        # Process query
        await batch_processor._process_single_query(sample_queued_query, mock_queue)
        
        # Verify processing
        mock_processor.process_request.assert_called_once()
        mock_llm.generate_response.assert_called_once()
        mock_queue.complete_query.assert_called_once()
        
        # Verify metrics updated
        assert batch_processor.current_metrics.queries_processed == 1
        assert batch_processor.current_metrics.queries_successful == 1
        assert batch_processor.current_metrics.total_cost == 0.12
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_request_processor')
    async def test_process_single_query_failure(self, mock_get_processor, batch_processor, sample_queued_query):
        """Test handling of query processing failure"""
        # Mock processor to fail
        mock_processor = AsyncMock()
        mock_processor.process_request.side_effect = Exception("Processing failed")
        mock_get_processor.return_value = mock_processor
        
        # Mock queue
        mock_queue = AsyncMock()
        
        # Initialize metrics
        batch_processor.current_metrics = BatchMetrics(
            batch_id="test-batch",
            start_time=datetime.utcnow(),
            end_time=None,
            queries_processed=0,
            queries_successful=0,
            queries_failed=0,
            queries_deduplicated=0,
            total_cost=0.0,
            total_processing_time=0.0,
            batch_size=1,
            cost_per_query_avg=0.0,
            processing_time_avg=0.0
        )
        
        # Process query (should handle failure)
        await batch_processor._process_single_query(sample_queued_query, mock_queue)
        
        # Verify failure handling
        mock_queue.fail_query.assert_called_once()
        
        # Verify metrics updated
        assert batch_processor.current_metrics.queries_processed == 1
        assert batch_processor.current_metrics.queries_failed == 1
    
    async def test_use_cached_result(self, batch_processor, sample_queued_query):
        """Test using cached result for deduplicated query"""
        mock_queue = AsyncMock()
        cached_result = "Cached system status response"
        
        # Initialize metrics
        batch_processor.current_metrics = BatchMetrics(
            batch_id="test-batch",
            start_time=datetime.utcnow(),
            end_time=None,
            queries_processed=0,
            queries_successful=0,
            queries_failed=0,
            queries_deduplicated=0,
            total_cost=0.0,
            total_processing_time=0.0,
            batch_size=1,
            cost_per_query_avg=0.0,
            processing_time_avg=0.0
        )
        
        # Use cached result
        await batch_processor._use_cached_result(sample_queued_query, cached_result, mock_queue)
        
        # Verify cached result was used
        mock_queue.complete_query.assert_called_once()
        
        # Get the result that was passed to complete_query
        call_args = mock_queue.complete_query.call_args
        result = call_args[0][1]  # Second argument is the result
        
        assert result.response_text == cached_result
        assert result.cost == 0.0  # Cached results have no cost
        assert result.metadata['cached_result'] is True
    
    def test_finalize_batch_metrics(self, batch_processor):
        """Test finalizing batch metrics"""
        # Create metrics with some data
        batch_processor.current_metrics = BatchMetrics(
            batch_id="test-batch",
            start_time=datetime.utcnow(),
            end_time=None,
            queries_processed=4,
            queries_successful=3,
            queries_failed=1,
            queries_deduplicated=0,
            total_cost=1.20,
            total_processing_time=8.0,
            batch_size=4,
            cost_per_query_avg=0.0,
            processing_time_avg=0.0
        )
        
        # Finalize metrics
        batch_processor._finalize_batch_metrics()
        
        # Check calculations
        assert batch_processor.current_metrics.end_time is not None
        assert batch_processor.current_metrics.cost_per_query_avg == 0.30  # 1.20 / 4
        assert batch_processor.current_metrics.processing_time_avg == 2.0   # 8.0 / 4
    
    def test_update_stats(self, batch_processor):
        """Test updating processor statistics"""
        # Create completed metrics
        batch_processor.current_metrics = BatchMetrics(
            batch_id="test-batch",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            queries_processed=3,
            queries_successful=2,
            queries_failed=1,
            queries_deduplicated=1,
            total_cost=0.75,
            total_processing_time=6.0,
            batch_size=3,
            cost_per_query_avg=0.25,
            processing_time_avg=2.0
        )
        
        initial_batches = batch_processor.stats['batches_processed']
        
        # Update stats
        batch_processor._update_stats()
        
        # Verify updates
        assert batch_processor.stats['batches_processed'] == initial_batches + 1
        assert batch_processor.stats['total_queries_processed'] == 3
        assert batch_processor.stats['total_queries_successful'] == 2
        assert batch_processor.stats['total_queries_failed'] == 1
        assert batch_processor.stats['total_queries_deduplicated'] == 1
        assert batch_processor.stats['total_cost'] == 0.75
        assert batch_processor.stats['total_processing_time'] == 6.0
    
    async def test_shutdown(self, batch_processor):
        """Test processor shutdown"""
        # Start a mock processing task
        batch_processor.processing_task = asyncio.create_task(asyncio.sleep(10))
        
        # Shutdown
        await batch_processor.shutdown()
        
        # Verify shutdown
        assert batch_processor.stop_requested is True
        assert batch_processor.status == BatchStatus.STOPPED
        assert batch_processor.processing_task.cancelled()


class TestGlobalBatchProcessor:
    """Test global batch processor functions"""
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor._batch_processor', None)
    async def test_get_batch_processor(self):
        """Test getting global batch processor instance"""
        with patch('src.beast_mode.observatory.ai_consultation.batch_processor.BatchQueryProcessor') as MockProcessor:
            mock_instance = AsyncMock()
            MockProcessor.return_value = mock_instance
            
            processor1 = await get_batch_processor()
            processor2 = await get_batch_processor()
            
            assert processor1 is processor2  # Should be singleton
            mock_instance.initialize.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])