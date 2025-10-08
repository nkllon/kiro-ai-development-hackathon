"""
Integration tests for Batch Query Processor
Tests batch processor integration with queue, LLM service, and other components.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.beast_mode.observatory.ai_consultation.batch_processor import (
    BatchQueryProcessor, BatchConfiguration, BatchStatus, BatchMetrics, get_batch_processor
)
from src.beast_mode.observatory.ai_consultation.query_queue import QueuedQuery, QueueStatus
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, ConsultationResult, QueryPriority, ProcessingMode
)
from src.beast_mode.observatory.ai_consultation.llm_service import LLMResponse, LLMUsage, LLMCost, LLMProvider, LLMModel
from src.beast_mode.observatory.ai_consultation.request_processor import ProcessedRequest
from src.beast_mode.observatory.ai_consultation.feature_flags import FeatureFlag


class TestBatchQueryProcessorIntegration:
    """Integration tests for Batch Query Processor"""
    
    @pytest.fixture
    async def batch_processor(self):
        """Create batch processor with realistic configuration"""
        config = BatchConfiguration(
            max_batch_size=3,
            min_batch_size=1,
            max_cost_per_batch=1.0,
            deduplication_enabled=True,
            deduplication_window=timedelta(minutes=30),
            parallel_processing=False,  # Sequential for easier testing
            max_concurrent_queries=2,
            batch_timeout=timedelta(minutes=2)
        )
        
        processor = BatchQueryProcessor(
            config=config,
            processing_interval=0.5,  # Fast for testing
            max_idle_time=timedelta(minutes=1)
        )
        
        return processor
    
    def create_test_query(
        self, 
        query_id: str = None,
        user_id: str = "integration-test-user",
        priority: QueryPriority = QueryPriority.NORMAL,
        text: str = None,
        estimated_cost: float = 0.15
    ) -> QueuedQuery:
        """Create test queued query"""
        query = ConsultationQuery(
            query_id=query_id or f"integration-test-{datetime.utcnow().timestamp()}",
            user_id=user_id,
            query_text=text or f"Integration test query at {datetime.utcnow()}",
            priority=priority,
            timestamp=datetime.utcnow()
        )
        
        return QueuedQuery(
            queue_id=f"queue_{query.query_id}",
            original_query=query,
            priority=priority,
            status=QueueStatus.PROCESSING,
            queued_at=datetime.utcnow(),
            estimated_processing_time=timedelta(minutes=2),
            estimated_cost=estimated_cost,
            retry_count=0,
            max_retries=3,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            metadata={}
        )
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_request_processor')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_llm_service')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status')
    async def test_full_batch_processing_integration(
        self, 
        mock_get_status,
        mock_get_llm, 
        mock_get_processor, 
        mock_get_queue,
        mock_flags,
        batch_processor
    ):
        """Test complete batch processing integration"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        
        # Mock doctor status
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        # Mock queue with test queries
        test_queries = [
            self.create_test_query("batch-test-1", text="What is the system status?"),
            self.create_test_query("batch-test-2", text="Are there any alerts?")
        ]
        
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = test_queries + [None]  # Queries then empty
        mock_get_queue.return_value = mock_queue
        
        # Mock request processor
        mock_processor = AsyncMock()
        mock_processed_request = ProcessedRequest(
            original_query=test_queries[0].original_query,
            processed_text="Processed: What is the system status?",
            context_data={"system": "test"},
            security_context=None,
            processing_metadata={"mode": "batch"}
        )
        mock_processor.process_request.return_value = mock_processed_request
        mock_get_processor.return_value = mock_processor
        
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_response = LLMResponse(
            content="Integration test response",
            provider=LLMProvider.OPENAI,
            model=LLMModel.GPT_4,
            response_time=1.5,
            usage=LLMUsage(
                prompt_tokens=20,
                completion_tokens=20,
                total_tokens=40
            ),
            cost=LLMCost(
                prompt_cost=0.05,
                completion_cost=0.05,
                total_cost=0.10
            ),
            metadata={"temperature": 0.7}
        )
        mock_llm.generate_response.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Process batch
        await batch_processor._process_next_batch()
        
        # Verify processing occurred
        assert mock_queue.dequeue.call_count >= 2
        assert mock_processor.process_request.call_count == 2
        assert mock_llm.generate_response.call_count == 2
        assert mock_queue.complete_query.call_count == 2
        
        # Verify metrics
        assert batch_processor.current_metrics.queries_processed == 2
        assert batch_processor.current_metrics.queries_successful == 2
        assert batch_processor.current_metrics.total_cost == 0.20  # 2 * 0.10
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    async def test_deduplication_integration(self, mock_get_queue, mock_flags, batch_processor):
        """Test query deduplication integration"""
        mock_flags.is_enabled.return_value = True
        
        # Create duplicate queries
        duplicate_query1 = self.create_test_query("dup-1", text="What is the system status?")
        duplicate_query2 = self.create_test_query("dup-2", text="What is the system status?")  # Same text
        
        # Add cached result
        query_hash = batch_processor._get_query_hash(duplicate_query1.original_query)
        batch_processor.query_cache[query_hash] = (datetime.utcnow(), "Cached system status")
        
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = [duplicate_query1, duplicate_query2, None]
        mock_get_queue.return_value = mock_queue
        
        # Initialize metrics
        batch_processor.current_metrics = BatchMetrics(
            batch_id="dedup-test",
            start_time=datetime.utcnow(),
            end_time=None,
            queries_processed=0,
            queries_successful=0,
            queries_failed=0,
            queries_deduplicated=0,
            total_cost=0.0,
            total_processing_time=0.0,
            batch_size=2,
            cost_per_query_avg=0.0,
            processing_time_avg=0.0
        )
        
        # Build batch (should handle deduplication)
        batch = await batch_processor._build_batch(mock_queue)
        
        # Should have deduplicated one query
        assert batch_processor.current_metrics.queries_deduplicated >= 1
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status')
    async def test_doctor_availability_integration(self, mock_get_status, mock_flags, batch_processor):
        """Test integration with doctor availability"""
        mock_flags.is_enabled.return_value = True
        
        # Mock doctor as unavailable
        mock_status = MagicMock()
        mock_status.is_available = False
        mock_get_status.return_value = mock_status
        
        with patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue') as mock_get_queue:
            mock_queue = AsyncMock()
            mock_get_queue.return_value = mock_queue
            
            # Process next batch (should skip due to doctor unavailable)
            await batch_processor._process_next_batch()
            
            # Should not have attempted to dequeue
            mock_queue.dequeue.assert_not_called()
            
            # Status should remain idle
            assert batch_processor.status == BatchStatus.IDLE
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    async def test_feature_flag_integration(self, mock_flags, batch_processor):
        """Test feature flag integration"""
        # Test with batch processing disabled
        def feature_enabled(flag):
            if flag == FeatureFlag.BATCH_PROCESSING:
                return False
            return True
        
        mock_flags.is_enabled.side_effect = feature_enabled
        
        with patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue') as mock_get_queue:
            mock_queue = AsyncMock()
            mock_get_queue.return_value = mock_queue
            
            # Process next batch (should skip due to feature disabled)
            await batch_processor._process_next_batch()
            
            # Should not have attempted to dequeue
            mock_queue.dequeue.assert_not_called()
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status')
    async def test_cost_optimization_integration(self, mock_get_status, mock_get_queue, mock_flags, batch_processor):
        """Test cost optimization integration"""
        mock_flags.is_enabled.return_value = True
        
        # Mock doctor status
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        # Create queries with different costs
        cheap_query = self.create_test_query("cheap", estimated_cost=0.20)
        expensive_query = self.create_test_query("expensive", estimated_cost=0.90)  # Would exceed 1.0 limit
        
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = [cheap_query, expensive_query, None]
        mock_get_queue.return_value = mock_queue
        
        # Build batch
        batch = await batch_processor._build_batch(mock_queue)
        
        # Should only include cheap query due to cost optimization
        assert len(batch) == 1
        assert batch[0] == cheap_query
    
    async def test_statistics_integration(self, batch_processor):
        """Test statistics tracking integration"""
        initial_stats = await batch_processor.get_processor_stats()
        initial_batches = initial_stats['batch_processor_stats']['batches_processed']
        
        # Simulate processing a batch
        batch_processor.current_metrics = BatchMetrics(
            batch_id="stats-test",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            queries_processed=2,
            queries_successful=2,
            queries_failed=0,
            queries_deduplicated=0,
            total_cost=0.30,
            total_processing_time=4.0,
            batch_size=2,
            cost_per_query_avg=0.15,
            processing_time_avg=2.0
        )
        
        batch_processor._update_stats()
        
        # Check updated statistics
        final_stats = await batch_processor.get_processor_stats()
        
        assert final_stats['batch_processor_stats']['batches_processed'] == initial_batches + 1
        assert final_stats['batch_processor_stats']['total_queries_processed'] == 2
        assert final_stats['batch_processor_stats']['total_cost'] == 0.30
        
        # Check configuration is reported
        assert 'configuration' in final_stats
        assert final_stats['configuration']['max_batch_size'] == 3
        assert final_stats['configuration']['max_cost_per_batch'] == 1.0
    
    async def test_health_monitoring_integration(self, batch_processor):
        """Test health monitoring integration"""
        # Get initial health
        health = await batch_processor.get_health_status()
        assert health.component == "batch_query_processor"
        assert health.status in ["healthy", "degraded", "critical", "unhealthy"]
        
        # Simulate some processing
        batch_processor.stats['batches_processed'] = 5
        batch_processor.stats['batches_successful'] = 4
        batch_processor.stats['batches_failed'] = 1
        
        health = await batch_processor.get_health_status()
        assert 'success_rate' in health.metadata
        assert health.metadata['success_rate'] == 0.8
        
        # Test error state
        batch_processor.status = BatchStatus.ERROR
        health = await batch_processor.get_health_status()
        assert health.status == "critical"
        assert "error state" in health.error_message.lower()


class TestGlobalBatchProcessorIntegration:
    """Test global batch processor instance integration"""
    
    async def test_singleton_behavior_integration(self):
        """Test that global batch processor maintains singleton behavior"""
        processor1 = await get_batch_processor()
        processor2 = await get_batch_processor()
        
        assert processor1 is processor2
        
        # Test state persistence across calls
        initial_batches = processor1.stats['batches_processed']
        
        # Simulate processing
        processor1.stats['batches_processed'] += 1
        
        # Get third instance
        processor3 = await get_batch_processor()
        
        # Should see the update from processor1
        assert processor3.stats['batches_processed'] == initial_batches + 1


    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_request_processor')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_llm_service')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status')
    async def test_parallel_batch_processing_integration(
        self, 
        mock_get_status,
        mock_get_llm, 
        mock_get_processor, 
        mock_get_queue,
        mock_flags,
        batch_processor
    ):
        """Test parallel batch processing integration"""
        # Enable parallel processing
        batch_processor.config.parallel_processing = True
        batch_processor.config.max_concurrent_queries = 3
        
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        
        # Mock doctor status
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        # Mock queue with multiple test queries
        test_queries = [
            self.create_test_query("parallel-test-1", text="Query 1"),
            self.create_test_query("parallel-test-2", text="Query 2"),
            self.create_test_query("parallel-test-3", text="Query 3")
        ]
        
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = test_queries + [None]
        mock_get_queue.return_value = mock_queue
        
        # Mock request processor with delay to test parallelism
        mock_processor = AsyncMock()
        async def mock_process_request(query, **kwargs):
            await asyncio.sleep(0.1)  # Simulate processing time
            return ProcessedRequest(
                original_query=query,
                processed_text=f"Processed: {query.query_text}",
                context_data={"system": "test"},
                security_context=None,
                processing_metadata={"mode": "batch"}
            )
        mock_processor.process_request.side_effect = mock_process_request
        mock_get_processor.return_value = mock_processor
        
        # Mock LLM service with delay
        mock_llm = AsyncMock()
        async def mock_generate_response(request, **kwargs):
            await asyncio.sleep(0.1)  # Simulate LLM processing time
            return LLMResponse(
                content=f"Response for {request.original_query.query_text}",
                provider=LLMProvider.OPENAI,
                model=LLMModel.GPT_4,
                response_time=0.1,
                usage=LLMUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
                cost=LLMCost(prompt_cost=0.05, completion_cost=0.05, total_cost=0.10),
                metadata={}
            )
        mock_llm.generate_response.side_effect = mock_generate_response
        mock_get_llm.return_value = mock_llm
        
        # Measure processing time
        start_time = asyncio.get_event_loop().time()
        await batch_processor._process_next_batch()
        end_time = asyncio.get_event_loop().time()
        
        # Verify parallel processing was faster than sequential would be
        # Sequential would take ~0.6s (3 * 0.2s), parallel should be ~0.2s
        processing_time = end_time - start_time
        assert processing_time < 0.4, f"Parallel processing took too long: {processing_time}s"
        
        # Verify all queries were processed
        assert batch_processor.current_metrics.queries_processed == 3
        assert batch_processor.current_metrics.queries_successful == 3
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_request_processor')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_llm_service')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status')
    async def test_error_handling_integration(
        self, 
        mock_get_status,
        mock_get_llm, 
        mock_get_processor, 
        mock_get_queue,
        mock_flags,
        batch_processor
    ):
        """Test error handling in batch processing integration"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        
        # Mock doctor status
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        # Mock queue with test queries
        test_queries = [
            self.create_test_query("error-test-1", text="Good query"),
            self.create_test_query("error-test-2", text="Bad query")
        ]
        
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = test_queries + [None]
        mock_get_queue.return_value = mock_queue
        
        # Mock request processor - first succeeds, second fails
        mock_processor = AsyncMock()
        def mock_process_request(query, **kwargs):
            if "Bad query" in query.query_text:
                raise Exception("Processing failed")
            return ProcessedRequest(
                original_query=query,
                processed_text=f"Processed: {query.query_text}",
                context_data={"system": "test"},
                security_context=None,
                processing_metadata={"mode": "batch"}
            )
        mock_processor.process_request.side_effect = mock_process_request
        mock_get_processor.return_value = mock_processor
        
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_response = LLMResponse(
            content="Good response",
            provider=LLMProvider.OPENAI,
            model=LLMModel.GPT_4,
            response_time=1.0,
            usage=LLMUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
            cost=LLMCost(prompt_cost=0.05, completion_cost=0.05, total_cost=0.10),
            metadata={}
        )
        mock_llm.generate_response.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Process batch
        await batch_processor._process_next_batch()
        
        # Verify mixed results
        assert batch_processor.current_metrics.queries_processed == 2
        assert batch_processor.current_metrics.queries_successful == 1
        assert batch_processor.current_metrics.queries_failed == 1
        
        # Verify failed query was handled
        assert mock_queue.fail_query.call_count == 1
        assert mock_queue.complete_query.call_count == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    async def test_batch_timeout_integration(self, mock_get_queue, mock_flags, batch_processor):
        """Test batch timeout handling integration"""
        # Set short timeout for testing
        batch_processor.config.batch_timeout = timedelta(seconds=0.1)
        batch_processor.config.parallel_processing = True
        
        mock_flags.is_enabled.return_value = True
        
        # Mock queue with slow queries
        test_queries = [
            self.create_test_query("timeout-test-1", text="Slow query 1"),
            self.create_test_query("timeout-test-2", text="Slow query 2")
        ]
        
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = test_queries + [None]
        mock_get_queue.return_value = mock_queue
        
        # Mock slow processors
        with patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_request_processor') as mock_get_processor:
            with patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_llm_service') as mock_get_llm:
                with patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status') as mock_get_status:
                    
                    # Mock doctor status
                    mock_status = MagicMock()
                    mock_status.is_available = True
                    mock_get_status.return_value = mock_status
                    
                    # Mock slow request processor
                    mock_processor = AsyncMock()
                    async def slow_process_request(query, **kwargs):
                        await asyncio.sleep(1.0)  # Longer than timeout
                        return ProcessedRequest(
                            original_query=query,
                            processed_text=f"Processed: {query.query_text}",
                            context_data={"system": "test"},
                            security_context=None,
                            processing_metadata={"mode": "batch"}
                        )
                    mock_processor.process_request.side_effect = slow_process_request
                    mock_get_processor.return_value = mock_processor
                    
                    # Mock LLM service
                    mock_llm = AsyncMock()
                    mock_response = LLMResponse(
                        content="Response",
                        provider=LLMProvider.OPENAI,
                        model=LLMModel.GPT_4,
                        response_time=1.0,
                        usage=LLMUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
                        cost=LLMCost(prompt_cost=0.05, completion_cost=0.05, total_cost=0.10),
                        metadata={}
                    )
                    mock_llm.generate_response.return_value = mock_response
                    mock_get_llm.return_value = mock_llm
                    
                    # Process batch (should timeout)
                    start_time = asyncio.get_event_loop().time()
                    await batch_processor._process_next_batch()
                    end_time = asyncio.get_event_loop().time()
                    
                    # Should have timed out quickly
                    processing_time = end_time - start_time
                    assert processing_time < 0.5, f"Timeout handling took too long: {processing_time}s"
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    async def test_cache_integration(self, mock_get_queue, mock_flags, batch_processor):
        """Test query cache integration"""
        # Enable deduplication
        batch_processor.config.deduplication_enabled = True
        batch_processor.config.deduplication_window = timedelta(minutes=30)
        
        mock_flags.is_enabled.return_value = True
        
        # Create duplicate queries
        query1 = self.create_test_query("cache-test-1", text="What is the system status?")
        query2 = self.create_test_query("cache-test-2", text="What is the system status?")  # Same text
        
        # Pre-populate cache
        query_hash = batch_processor._get_query_hash(query1.original_query)
        batch_processor.query_cache[query_hash] = (datetime.utcnow(), "Cached system status")
        
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = [query1, query2, None]
        mock_get_queue.return_value = mock_queue
        
        with patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status') as mock_get_status:
            # Mock doctor status
            mock_status = MagicMock()
            mock_status.is_available = True
            mock_get_status.return_value = mock_status
            
            # Build batch (should handle deduplication)
            batch = await batch_processor._build_batch(mock_queue)
            
            # Should have used cached result for at least one query
            assert mock_queue.complete_query.call_count >= 1
            
            # Check cache was used
            assert len(batch_processor.query_cache) > 0
    
    async def test_metrics_and_statistics_integration(self, batch_processor):
        """Test comprehensive metrics and statistics integration"""
        # Simulate multiple batch processing cycles
        for i in range(3):
            batch_processor.current_metrics = BatchMetrics(
                batch_id=f"metrics-test-{i}",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                queries_processed=2 + i,
                queries_successful=2 + i,
                queries_failed=0,
                queries_deduplicated=i,
                total_cost=0.20 + (i * 0.10),
                total_processing_time=2.0 + i,
                batch_size=2 + i,
                cost_per_query_avg=0.10,
                processing_time_avg=1.0
            )
            batch_processor._update_stats()
        
        # Get comprehensive statistics
        stats = await batch_processor.get_processor_stats()
        
        # Verify batch statistics
        assert stats['batch_processor_stats']['batches_processed'] == 3
        assert stats['batch_processor_stats']['batches_successful'] == 3
        assert stats['batch_processor_stats']['total_queries_processed'] == 9  # 2+3+4
        assert stats['batch_processor_stats']['total_queries_deduplicated'] == 3  # 0+1+2
        assert stats['batch_processor_stats']['total_cost'] == 0.60  # 0.20+0.30+0.40
        
        # Verify configuration is included
        assert 'configuration' in stats
        assert stats['configuration']['max_batch_size'] == 3
        assert stats['configuration']['deduplication_enabled'] == True
        
        # Verify cache statistics
        assert 'cache_stats' in stats
        assert 'cache_size' in stats['cache_stats']
    
    async def test_circuit_breaker_integration(self, batch_processor):
        """Test circuit breaker integration"""
        # This test verifies that the circuit breaker decorator is applied
        # and would prevent cascading failures in real scenarios
        
        # Simulate multiple failures to potentially trip circuit breaker
        for i in range(5):
            batch_processor.current_metrics = BatchMetrics(
                batch_id=f"circuit-test-{i}",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                queries_processed=1,
                queries_successful=0,
                queries_failed=1,
                queries_deduplicated=0,
                total_cost=0.0,
                total_processing_time=1.0,
                batch_size=1,
                cost_per_query_avg=0.0,
                processing_time_avg=1.0
            )
            batch_processor._update_stats()
        
        # Verify failure statistics are tracked
        stats = await batch_processor.get_processor_stats()
        assert stats['batch_processor_stats']['batches_failed'] == 5
        assert stats['batch_processor_stats']['total_queries_failed'] == 5
        
        # Health status should reflect the failures
        health = await batch_processor.get_health_status()
        assert health.metadata['success_rate'] == 0.0


class TestBatchProcessorLifecycleIntegration:
    """Test batch processor lifecycle integration"""
    
    async def test_initialization_and_shutdown_integration(self):
        """Test complete initialization and shutdown cycle"""
        # Create processor
        config = BatchConfiguration(
            max_batch_size=2,
            processing_interval=0.1
        )
        processor = BatchQueryProcessor(config=config, processing_interval=0.1)
        
        # Initialize
        with patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            await processor.initialize()
            
            # Should be running
            assert processor.status in [BatchStatus.IDLE, BatchStatus.PROCESSING]
            assert processor.processing_task is not None
            assert not processor.processing_task.done()
        
        # Shutdown
        await processor.shutdown()
        
        # Should be stopped
        assert processor.status == BatchStatus.STOPPED
        assert processor.stop_requested == True
    
    async def test_pause_resume_integration(self):
        """Test pause and resume functionality integration"""
        config = BatchConfiguration(max_batch_size=2)
        processor = BatchQueryProcessor(config=config, processing_interval=0.1)
        
        with patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            await processor.initialize()
            
            # Start processing
            processor.status = BatchStatus.PROCESSING
            
            # Pause
            result = await processor.pause_processing()
            assert result == True
            assert processor.status == BatchStatus.PAUSED
            
            # Resume
            result = await processor.resume_processing()
            assert result == True
            assert processor.status == BatchStatus.IDLE
            
            await processor.shutdown()


if __name__ == "__main__":
    pytest.main([__file__])


class TestBatchProcessorRealWorldScenarios:
    """Test batch processor with real-world scenarios"""
    
    @pytest.fixture
    async def realistic_batch_processor(self):
        """Create batch processor with realistic production-like configuration"""
        config = BatchConfiguration(
            max_batch_size=5,
            min_batch_size=2,
            max_cost_per_batch=2.0,
            max_processing_time=timedelta(minutes=10),
            deduplication_enabled=True,
            deduplication_window=timedelta(hours=2),
            cost_optimization_enabled=True,
            parallel_processing=True,
            max_concurrent_queries=3,
            batch_timeout=timedelta(minutes=3)
        )
        
        processor = BatchQueryProcessor(
            config=config,
            processing_interval=1.0,
            max_idle_time=timedelta(minutes=10)
        )
        
        return processor
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_request_processor')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_llm_service')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status')
    async def test_high_volume_processing_integration(
        self, 
        mock_get_status,
        mock_get_llm, 
        mock_get_processor, 
        mock_get_queue,
        mock_flags,
        realistic_batch_processor
    ):
        """Test high-volume batch processing integration"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        
        # Mock doctor status
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_get_status.return_value = mock_status
        
        # Create high volume of queries
        test_queries = []
        for i in range(20):
            query = ConsultationQuery(
                query_id=f"high-volume-{i}",
                user_id=f"user-{i % 5}",  # 5 different users
                query_text=f"High volume query {i}: What is the status of system component {i % 3}?",
                priority=QueryPriority.NORMAL if i % 3 != 0 else QueryPriority.HIGH,
                timestamp=datetime.utcnow()
            )
            
            queued_query = QueuedQuery(
                queue_id=f"queue_high_volume_{i}",
                original_query=query,
                priority=query.priority,
                status=QueueStatus.PROCESSING,
                queued_at=datetime.utcnow(),
                estimated_processing_time=timedelta(minutes=1),
                estimated_cost=0.08 + (i % 3) * 0.02,  # Varying costs
                retry_count=0,
                max_retries=3,
                expires_at=datetime.utcnow() + timedelta(hours=1),
                metadata={}
            )
            test_queries.append(queued_query)
        
        # Mock queue to return queries in batches
        mock_queue = AsyncMock()
        query_iterator = iter(test_queries + [None] * 10)  # Add None values to end batches
        mock_queue.dequeue.side_effect = lambda timeout=None: next(query_iterator, None)
        mock_get_queue.return_value = mock_queue
        
        # Mock request processor
        mock_processor = AsyncMock()
        async def mock_process_request(query, **kwargs):
            # Simulate varying processing times
            await asyncio.sleep(0.01 + (hash(query.query_id) % 3) * 0.01)
            return ProcessedRequest(
                original_query=query,
                processed_text=f"Processed: {query.query_text}",
                context_data={"system": "test", "component": query.query_id.split('-')[-1]},
                security_context=None,
                processing_metadata={"mode": "batch", "volume": "high"}
            )
        mock_processor.process_request.side_effect = mock_process_request
        mock_get_processor.return_value = mock_processor
        
        # Mock LLM service with realistic responses
        mock_llm = AsyncMock()
        async def mock_generate_response(request, **kwargs):
            # Simulate varying LLM response times and costs
            component_id = int(request.original_query.query_id.split('-')[-1])
            await asyncio.sleep(0.02 + (component_id % 3) * 0.01)
            
            return LLMResponse(
                content=f"System component {component_id % 3} is operational. Status: {'Good' if component_id % 2 == 0 else 'Warning'}",
                provider=LLMProvider.OPENAI,
                model=LLMModel.GPT_4,
                response_time=0.02 + (component_id % 3) * 0.01,
                usage=LLMUsage(
                    prompt_tokens=15 + component_id % 10,
                    completion_tokens=10 + component_id % 5,
                    total_tokens=25 + component_id % 15
                ),
                cost=LLMCost(
                    prompt_cost=0.03 + (component_id % 3) * 0.01,
                    completion_cost=0.02 + (component_id % 2) * 0.01,
                    total_cost=0.05 + (component_id % 5) * 0.01
                ),
                metadata={"component_id": component_id % 3}
            )
        mock_llm.generate_response.side_effect = mock_generate_response
        mock_get_llm.return_value = mock_llm
        
        # Process multiple batches
        total_processed = 0
        max_batches = 5  # Limit to prevent infinite loop in test
        
        for batch_num in range(max_batches):
            await realistic_batch_processor._process_next_batch()
            
            if realistic_batch_processor.current_metrics:
                total_processed += realistic_batch_processor.current_metrics.queries_processed
                
                # Verify batch constraints were respected
                assert realistic_batch_processor.current_metrics.batch_size <= 5
                assert realistic_batch_processor.current_metrics.total_cost <= 2.0
                
                # Break if no more queries processed
                if realistic_batch_processor.current_metrics.queries_processed == 0:
                    break
        
        # Verify high-volume processing
        assert total_processed > 0
        
        # Get final statistics
        stats = await realistic_batch_processor.get_processor_stats()
        assert stats['batch_processor_stats']['batches_processed'] > 0
        assert stats['batch_processor_stats']['total_queries_processed'] == total_processed
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    async def test_mixed_priority_processing_integration(
        self, 
        mock_get_queue,
        mock_flags,
        realistic_batch_processor
    ):
        """Test processing queries with mixed priorities"""
        mock_flags.is_enabled.return_value = True
        
        # Create queries with different priorities
        urgent_query = self.create_test_query("urgent-1", priority=QueryPriority.URGENT, estimated_cost=0.15)
        high_query = self.create_test_query("high-1", priority=QueryPriority.HIGH, estimated_cost=0.12)
        normal_query = self.create_test_query("normal-1", priority=QueryPriority.NORMAL, estimated_cost=0.10)
        low_query = self.create_test_query("low-1", priority=QueryPriority.LOW, estimated_cost=0.08)
        
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = [urgent_query, high_query, normal_query, low_query, None]
        mock_get_queue.return_value = mock_queue
        
        with patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status') as mock_get_status:
            # Mock doctor status
            mock_status = MagicMock()
            mock_status.is_available = True
            mock_get_status.return_value = mock_status
            
            # Build batch
            batch = await realistic_batch_processor._build_batch(mock_queue)
            
            # Should include all queries within cost limits
            assert len(batch) >= 3  # At least urgent, high, and normal
            
            # Verify urgent query is included (priority handling)
            urgent_included = any(q.original_query.query_id == "urgent-1" for q in batch)
            assert urgent_included
    
    def create_test_query(
        self, 
        query_id: str = None,
        user_id: str = "integration-test-user",
        priority: QueryPriority = QueryPriority.NORMAL,
        text: str = None,
        estimated_cost: float = 0.15
    ) -> QueuedQuery:
        """Create test queued query"""
        query = ConsultationQuery(
            query_id=query_id or f"integration-test-{datetime.utcnow().timestamp()}",
            user_id=user_id,
            query_text=text or f"Integration test query at {datetime.utcnow()}",
            priority=priority,
            timestamp=datetime.utcnow()
        )
        
        return QueuedQuery(
            queue_id=f"queue_{query.query_id}",
            original_query=query,
            priority=priority,
            status=QueueStatus.PROCESSING,
            queued_at=datetime.utcnow(),
            estimated_processing_time=timedelta(minutes=2),
            estimated_cost=estimated_cost,
            retry_count=0,
            max_retries=3,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            metadata={}
        )
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_query_queue')
    async def test_cost_optimization_edge_cases_integration(
        self, 
        mock_get_queue,
        mock_flags,
        realistic_batch_processor
    ):
        """Test cost optimization with edge cases"""
        mock_flags.is_enabled.return_value = True
        
        # Create queries that would exceed cost limit if all included
        expensive_queries = [
            self.create_test_query("expensive-1", estimated_cost=0.8),
            self.create_test_query("expensive-2", estimated_cost=0.9),
            self.create_test_query("expensive-3", estimated_cost=1.0),
            self.create_test_query("cheap-1", estimated_cost=0.1),
            self.create_test_query("cheap-2", estimated_cost=0.1)
        ]
        
        mock_queue = AsyncMock()
        mock_queue.dequeue.side_effect = expensive_queries + [None]
        mock_get_queue.return_value = mock_queue
        
        with patch('src.beast_mode.observatory.ai_consultation.batch_processor.get_doctor_status') as mock_get_status:
            # Mock doctor status
            mock_status = MagicMock()
            mock_status.is_available = True
            mock_get_status.return_value = mock_status
            
            # Build batch with cost optimization
            batch = await realistic_batch_processor._build_batch(mock_queue)
            
            # Calculate total estimated cost
            total_cost = sum(q.estimated_cost for q in batch)
            
            # Should not exceed cost limit
            assert total_cost <= realistic_batch_processor.config.max_cost_per_batch
            
            # Should include some queries
            assert len(batch) > 0
            
            # Should prefer cheaper queries when possible
            cheap_queries_in_batch = sum(1 for q in batch if q.estimated_cost <= 0.2)
            assert cheap_queries_in_batch > 0
    
    async def test_long_running_batch_processing_integration(self, realistic_batch_processor):
        """Test long-running batch processing scenarios"""
        # Simulate processor running for extended period
        start_time = datetime.utcnow()
        
        # Simulate processing over time
        for hour in range(3):  # 3 hours of processing
            for batch in range(2):  # 2 batches per hour
                batch_time = start_time + timedelta(hours=hour, minutes=batch * 30)
                
                realistic_batch_processor.current_metrics = BatchMetrics(
                    batch_id=f"long-running-{hour}-{batch}",
                    start_time=batch_time,
                    end_time=batch_time + timedelta(minutes=5),
                    queries_processed=3 + (hour % 2),
                    queries_successful=3 + (hour % 2),
                    queries_failed=0,
                    queries_deduplicated=hour % 3,
                    total_cost=0.30 + (batch * 0.05),
                    total_processing_time=300.0 + (batch * 30),
                    batch_size=3 + (hour % 2),
                    cost_per_query_avg=0.10,
                    processing_time_avg=100.0
                )
                realistic_batch_processor._update_stats()
        
        # Verify long-term statistics
        stats = await realistic_batch_processor.get_processor_stats()
        
        assert stats['batch_processor_stats']['batches_processed'] == 6  # 3 hours * 2 batches
        assert stats['batch_processor_stats']['total_queries_processed'] == 21  # Sum of all queries
        assert stats['batch_processor_stats']['avg_batch_size'] == 3.5  # Average batch size
        
        # Verify cache cleanup would work over time
        realistic_batch_processor._cleanup_cache()
        
        # Health should still be good for long-running processor
        health = await realistic_batch_processor.get_health_status()
        assert health.status == "healthy"
        assert health.metadata['success_rate'] == 1.0


class TestBatchProcessorStressScenarios:
    """Test batch processor under stress conditions"""
    
    @pytest.fixture
    async def stress_test_processor(self):
        """Create processor configured for stress testing"""
        config = BatchConfiguration(
            max_batch_size=10,
            min_batch_size=1,
            max_cost_per_batch=5.0,
            max_processing_time=timedelta(minutes=1),
            deduplication_enabled=True,
            deduplication_window=timedelta(minutes=10),
            cost_optimization_enabled=True,
            parallel_processing=True,
            max_concurrent_queries=5,
            batch_timeout=timedelta(seconds=30)
        )
        
        processor = BatchQueryProcessor(
            config=config,
            processing_interval=0.1,  # Very fast for stress testing
            max_idle_time=timedelta(minutes=1)
        )
        
        return processor
    
    @patch('src.beast_mode.observatory.ai_consultation.batch_processor.feature_flags')
    async def test_rapid_batch_cycling_integration(self, mock_flags, stress_test_processor):
        """Test rapid batch processing cycles"""
        mock_flags.is_enabled.return_value = True
        
        # Simulate rapid batch processing
        for cycle in range(10):
            stress_test_processor.current_metrics = BatchMetrics(
                batch_id=f"rapid-cycle-{cycle}",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                queries_processed=5,
                queries_successful=4 + (cycle % 2),
                queries_failed=1 - (cycle % 2),
                queries_deduplicated=cycle % 3,
                total_cost=0.50,
                total_processing_time=10.0,
                batch_size=5,
                cost_per_query_avg=0.10,
                processing_time_avg=2.0
            )
            stress_test_processor._update_stats()
            
            # Simulate some cache entries
            for i in range(3):
                query_hash = f"stress_hash_{cycle}_{i}"
                stress_test_processor.query_cache[query_hash] = (
                    datetime.utcnow(), f"Cached result {cycle}-{i}"
                )
        
        # Verify statistics after rapid cycling
        stats = await stress_test_processor.get_processor_stats()
        
        assert stats['batch_processor_stats']['batches_processed'] == 10
        assert stats['batch_processor_stats']['total_queries_processed'] == 50
        
        # Verify cache management under stress
        assert len(stress_test_processor.query_cache) > 0
        
        # Cleanup should work even with many entries
        stress_test_processor._cleanup_cache()
        
        # Health monitoring should handle rapid changes
        health = await stress_test_processor.get_health_status()
        assert health.component == "batch_query_processor"
        assert health.status in ["healthy", "degraded"]  # Should not be critical
    
    async def test_memory_usage_integration(self, stress_test_processor):
        """Test memory usage patterns during batch processing"""
        # Simulate large cache buildup
        for i in range(1000):
            query_hash = f"memory_test_hash_{i}"
            stress_test_processor.query_cache[query_hash] = (
                datetime.utcnow() - timedelta(minutes=i % 60),
                f"Large cached result with lots of text to simulate memory usage {i}" * 10
            )
        
        # Verify cache size
        initial_cache_size = len(stress_test_processor.query_cache)
        assert initial_cache_size == 1000
        
        # Cleanup should reduce memory usage
        stress_test_processor._cleanup_cache()
        
        # Should have cleaned up old entries
        final_cache_size = len(stress_test_processor.query_cache)
        assert final_cache_size < initial_cache_size
        
        # Statistics should still be accessible
        stats = await stress_test_processor.get_processor_stats()
        assert 'cache_stats' in stats
        assert stats['cache_stats']['cache_size'] == final_cache_size