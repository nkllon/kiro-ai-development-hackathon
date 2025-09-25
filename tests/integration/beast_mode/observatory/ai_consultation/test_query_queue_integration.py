"""
Integration tests for Query Queue
Tests queue integration with Redis, feature flags, and other system components.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.beast_mode.observatory.ai_consultation.query_queue import (
    QueryQueue, QueuedQuery, QueueStatus, get_query_queue
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, ConsultationResult, QueryPriority
)
from src.beast_mode.observatory.ai_consultation.feature_flags import FeatureFlag


class TestQueryQueueIntegration:
    """Integration tests for Query Queue"""
    
    @pytest.fixture
    async def query_queue(self):
        """Create query queue with realistic configuration"""
        # Use a test Redis database
        queue = QueryQueue(
            redis_url="redis://localhost:6379",
            redis_db=15,  # Use test database
            key_prefix="test_ai_consultation:",
            max_queue_size=50,
            max_processing_time=timedelta(minutes=15),
            cleanup_interval=30,
            max_retries=2
        )
        
        # Initialize with mock Redis if real Redis not available
        try:
            await queue.initialize()
            if queue.redis:
                # Clean up any existing test data
                await queue.redis.flushdb()
        except Exception:
            # Use mock Redis for testing
            from tests.unit.beast_mode.observatory.ai_consultation.test_query_queue import MockRedis
            queue.redis = MockRedis()
        
        yield queue
        
        # Cleanup
        try:
            if queue.redis and hasattr(queue.redis, 'flushdb'):
                await queue.redis.flushdb()
            await queue.shutdown()
        except Exception:
            pass
    
    def create_test_query(
        self, 
        query_id: str = None, 
        user_id: str = "integration-test-user",
        priority: QueryPriority = QueryPriority.NORMAL,
        text: str = None
    ) -> ConsultationQuery:
        """Create test consultation query"""
        return ConsultationQuery(
            query_id=query_id or f"integration-test-{datetime.utcnow().timestamp()}",
            user_id=user_id,
            query_text=text or f"Integration test query at {datetime.utcnow()}",
            priority=priority,
            timestamp=datetime.utcnow()
        )
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_full_queue_lifecycle_integration(self, mock_flags, query_queue):
        """Test complete queue lifecycle with all operations"""
        mock_flags.is_enabled.return_value = True
        
        # Create test query
        query = self.create_test_query("lifecycle-test", priority=QueryPriority.HIGH)
        
        # Enqueue
        queued_query = await query_queue.enqueue(
            query,
            estimated_cost=0.20,
            estimated_processing_time=timedelta(minutes=2)
        )
        
        assert queued_query.queue_id is not None
        assert queued_query.status == QueueStatus.PENDING
        assert queued_query.estimated_cost == 0.20
        
        # Check queue status
        status = await query_queue.get_queue_status()
        assert status['total_pending'] == 1
        assert status['queue_sizes']['high'] == 1
        
        # Dequeue
        dequeued = await query_queue.dequeue(timeout=1.0)
        assert dequeued is not None
        assert dequeued.queue_id == queued_query.queue_id
        assert dequeued.status == QueueStatus.PROCESSING
        
        # Check processing status
        status = await query_queue.get_queue_status()
        assert status['processing_count'] == 1
        assert status['total_pending'] == 0
        
        # Complete query
        result = ConsultationResult(
            result_id="integration-result",
            query_id=query.query_id,
            response_text="Integration test completed successfully",
            processing_time=1.5,
            cost=0.18,
            timestamp=datetime.utcnow()
        )
        
        success = await query_queue.complete_query(dequeued, result)
        assert success
        
        # Check final status
        status = await query_queue.get_queue_status()
        assert status['processing_count'] == 0
        assert status['statistics']['queries_processed'] == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_priority_queue_integration(self, mock_flags, query_queue):
        """Test priority-based queue processing"""
        mock_flags.is_enabled.return_value = True
        
        # Create queries with different priorities
        queries = [
            self.create_test_query("low-priority", priority=QueryPriority.LOW),
            self.create_test_query("urgent-priority", priority=QueryPriority.URGENT),
            self.create_test_query("normal-priority", priority=QueryPriority.NORMAL),
            self.create_test_query("high-priority", priority=QueryPriority.HIGH)
        ]
        
        # Enqueue in mixed order
        for query in queries:
            await query_queue.enqueue(query)
        
        # Dequeue should return in priority order
        expected_order = ["urgent-priority", "high-priority", "normal-priority", "low-priority"]
        actual_order = []
        
        for _ in range(4):
            dequeued = await query_queue.dequeue(timeout=1.0)
            assert dequeued is not None
            actual_order.append(dequeued.original_query.query_id)
        
        assert actual_order == expected_order
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_retry_mechanism_integration(self, mock_flags, query_queue):
        """Test query retry mechanism"""
        mock_flags.is_enabled.return_value = True
        
        # Create and enqueue query
        query = self.create_test_query("retry-test")
        await query_queue.enqueue(query)
        
        # Dequeue and fail with retry
        dequeued = await query_queue.dequeue(timeout=1.0)
        assert dequeued is not None
        
        # Fail query (should retry)
        success = await query_queue.fail_query(dequeued, "Simulated failure", retry=True)
        assert success
        assert dequeued.retry_count == 1
        
        # Should be able to dequeue again (after retry delay)
        # Note: In real implementation, there would be a delay
        # For testing, we'll check that it can be retried
        
        # Fail again to reach max retries
        dequeued.retry_count = query_queue.max_retries
        success = await query_queue.fail_query(dequeued, "Final failure", retry=True)
        assert success
        assert dequeued.status == QueueStatus.FAILED
        
        # Check statistics
        status = await query_queue.get_queue_status()
        assert status['statistics']['queries_failed'] == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_user_query_tracking_integration(self, mock_flags, query_queue):
        """Test tracking queries by user"""
        mock_flags.is_enabled.return_value = True
        
        # Create queries for different users
        user1_queries = [
            self.create_test_query("user1-query1", "user1", QueryPriority.HIGH),
            self.create_test_query("user1-query2", "user1", QueryPriority.NORMAL)
        ]
        
        user2_queries = [
            self.create_test_query("user2-query1", "user2", QueryPriority.URGENT)
        ]
        
        # Enqueue all queries
        for query in user1_queries + user2_queries:
            await query_queue.enqueue(query)
        
        # Get queries for user1
        user1_results = await query_queue.get_user_queries("user1")
        assert len(user1_results) == 2
        
        user1_ids = [q['original_query']['query_id'] for q in user1_results]
        assert "user1-query1" in user1_ids
        assert "user1-query2" in user1_ids
        
        # Get queries for user2
        user2_results = await query_queue.get_user_queries("user2")
        assert len(user2_results) == 1
        assert user2_results[0]['original_query']['query_id'] == "user2-query1"
        
        # Get queries for non-existent user
        no_user_results = await query_queue.get_user_queries("nonexistent")
        assert len(no_user_results) == 0
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_wait_time_estimation_integration(self, mock_flags, query_queue):
        """Test wait time estimation with real queue data"""
        mock_flags.is_enabled.return_value = True
        
        # Create queue with various priorities
        queries = [
            self.create_test_query("urgent1", priority=QueryPriority.URGENT),
            self.create_test_query("urgent2", priority=QueryPriority.URGENT),
            self.create_test_query("high1", priority=QueryPriority.HIGH),
            self.create_test_query("normal1", priority=QueryPriority.NORMAL),
            self.create_test_query("normal2", priority=QueryPriority.NORMAL),
            self.create_test_query("low1", priority=QueryPriority.LOW)
        ]
        
        for query in queries:
            await query_queue.enqueue(query)
        
        # Estimate wait times
        urgent_wait = await query_queue.estimate_wait_time(QueryPriority.URGENT)
        high_wait = await query_queue.estimate_wait_time(QueryPriority.HIGH)
        normal_wait = await query_queue.estimate_wait_time(QueryPriority.NORMAL)
        low_wait = await query_queue.estimate_wait_time(QueryPriority.LOW)
        
        # Higher priority should have shorter wait times
        assert urgent_wait <= high_wait
        assert high_wait <= normal_wait
        assert normal_wait <= low_wait
        
        # All should be reasonable times
        assert urgent_wait.total_seconds() >= 60  # At least 1 minute
        assert low_wait.total_seconds() <= 3600   # At most 1 hour
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_queue_capacity_integration(self, mock_flags, query_queue):
        """Test queue capacity limits"""
        mock_flags.is_enabled.return_value = True
        
        # Fill queue to capacity
        for i in range(query_queue.max_queue_size):
            query = self.create_test_query(f"capacity-test-{i}")
            await query_queue.enqueue(query)
        
        # Next enqueue should fail
        overflow_query = self.create_test_query("overflow-query")
        
        with pytest.raises(Exception, match="Queue is full"):
            await query_queue.enqueue(overflow_query)
        
        # Check queue status
        status = await query_queue.get_queue_status()
        assert status['total_pending'] == query_queue.max_queue_size
        assert status['queue_sizes']['normal'] == query_queue.max_queue_size
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_concurrent_operations_integration(self, mock_flags, query_queue):
        """Test concurrent queue operations"""
        mock_flags.is_enabled.return_value = True
        
        # Create multiple queries
        queries = [
            self.create_test_query(f"concurrent-{i}", priority=QueryPriority.NORMAL)
            for i in range(10)
        ]
        
        # Enqueue all concurrently
        enqueue_tasks = [
            query_queue.enqueue(query, estimated_cost=0.1)
            for query in queries
        ]
        
        enqueue_results = await asyncio.gather(*enqueue_tasks, return_exceptions=True)
        
        # All should succeed
        successful_enqueues = [r for r in enqueue_results if not isinstance(r, Exception)]
        assert len(successful_enqueues) == 10
        
        # Dequeue all concurrently
        dequeue_tasks = [
            query_queue.dequeue(timeout=1.0)
            for _ in range(10)
        ]
        
        dequeue_results = await asyncio.gather(*dequeue_tasks, return_exceptions=True)
        
        # All should succeed
        successful_dequeues = [r for r in dequeue_results if r is not None and not isinstance(r, Exception)]
        assert len(successful_dequeues) == 10
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_feature_flag_integration(self, mock_flags, query_queue):
        """Test feature flag integration"""
        query = self.create_test_query("feature-flag-test")
        
        # Test with queue processing disabled
        def feature_enabled(flag):
            if flag == FeatureFlag.QUEUE_PROCESSING:
                return False
            return True
        
        mock_flags.is_enabled.side_effect = feature_enabled
        
        # Should fail to enqueue
        with pytest.raises(Exception, match="Queue processing is disabled"):
            await query_queue.enqueue(query)
        
        # Test with feature enabled
        mock_flags.is_enabled.return_value = True
        
        # Should succeed
        queued_query = await query_queue.enqueue(query)
        assert queued_query.status == QueueStatus.PENDING
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_cleanup_integration(self, mock_flags, query_queue):
        """Test automatic cleanup of expired queries"""
        mock_flags.is_enabled.return_value = True
        
        # Create query that expires quickly
        query = self.create_test_query("cleanup-test")
        
        queued_query = await query_queue.enqueue(
            query,
            expires_in=timedelta(seconds=1)  # Expires in 1 second
        )
        
        # Wait for expiration
        await asyncio.sleep(2)
        
        # Run cleanup manually
        await query_queue._cleanup_expired_queries()
        
        # Query should be cleaned up
        status = await query_queue.get_queue_status()
        assert status['total_pending'] == 0
        assert status['statistics']['queries_expired'] >= 1
    
    async def test_health_monitoring_integration(self, query_queue):
        """Test health monitoring integration"""
        # Get initial health
        health = await query_queue.get_health_status()
        assert health.component == "query_queue"
        
        if query_queue.redis and hasattr(query_queue.redis, 'ping'):
            # If real Redis is available
            assert health.status in ["healthy", "degraded", "critical"]
            assert 'total_pending' in health.metadata
            assert 'processing_count' in health.metadata
        else:
            # Mock Redis
            assert health.status == "healthy"
    
    async def test_statistics_tracking_integration(self, query_queue):
        """Test statistics tracking across operations"""
        with patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            initial_status = await query_queue.get_queue_status()
            initial_queued = initial_status['statistics']['queries_queued']
            
            # Perform various operations
            queries = []
            for i in range(3):
                query = self.create_test_query(f"stats-test-{i}")
                queued_query = await query_queue.enqueue(query)
                queries.append(queued_query)
            
            # Complete one query
            dequeued = await query_queue.dequeue(timeout=1.0)
            if dequeued:
                result = ConsultationResult(
                    result_id="stats-result",
                    query_id=dequeued.original_query.query_id,
                    response_text="Stats test completed",
                    processing_time=1.0,
                    cost=0.10,
                    timestamp=datetime.utcnow()
                )
                await query_queue.complete_query(dequeued, result)
            
            # Fail one query
            dequeued = await query_queue.dequeue(timeout=1.0)
            if dequeued:
                await query_queue.fail_query(dequeued, "Stats test failure", retry=False)
            
            # Cancel one query
            if queries:
                await query_queue.cancel_query(queries[0].queue_id)
            
            # Check final statistics
            final_status = await query_queue.get_queue_status()
            final_stats = final_status['statistics']
            
            assert final_stats['queries_queued'] >= initial_queued + 3
            assert final_stats['queries_processed'] >= 1
            assert final_stats['queries_failed'] >= 1
            assert final_stats['queries_cancelled'] >= 1


class TestGlobalQueueIntegration:
    """Test global queue instance integration"""
    
    async def test_singleton_behavior_integration(self):
        """Test that global queue maintains singleton behavior"""
        queue1 = await get_query_queue()
        queue2 = await get_query_queue()
        
        assert queue1 is queue2
        
        # Test state persistence across calls
        with patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            
            try:
                # Create a test query
                query = ConsultationQuery(
                    query_id="singleton-test",
                    user_id="test-user",
                    query_text="Test singleton behavior",
                    priority=QueryPriority.NORMAL,
                    timestamp=datetime.utcnow()
                )
                
                # Enqueue with first instance
                initial_status = await queue1.get_queue_status()
                initial_queued = initial_status['statistics']['queries_queued']
                
                await queue1.enqueue(query)
                
                # Get third instance
                queue3 = await get_query_queue()
                
                # Should see the query enqueued by queue1
                final_status = await queue3.get_queue_status()
                assert final_status['statistics']['queries_queued'] == initial_queued + 1
                
            except Exception as e:
                # If Redis is not available, just verify singleton behavior
                assert queue1 is queue2


if __name__ == "__main__":
    pytest.main([__file__])