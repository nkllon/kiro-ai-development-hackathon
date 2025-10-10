"""
Unit tests for Query Queue
Tests Redis-based queue management, priority handling, and brownfield safety.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from src.beast_mode.observatory.ai_consultation.query_queue import (
    QueryQueue, QueuedQuery, QueueStatus, get_query_queue
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, ConsultationResult, QueryPriority
)
from src.beast_mode.observatory.ai_consultation.exceptions import (
    ProcessingError, QueueFullError
)


class MockRedis:
    """Mock Redis for testing"""
    
    def __init__(self):
        self.data = {}
        self.lists = {}
        self.hashes = {}
        self.connected = True
    
    async def ping(self):
        """Mock ping"""
        if not self.connected:
            raise Exception("Redis connection failed")
        return True
    
    async def lpush(self, key: str, value: str):
        """Mock lpush"""
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key].insert(0, value)
        return len(self.lists[key])
    
    async def brpop(self, key: str, timeout: float = 1.0):
        """Mock brpop"""
        if key in self.lists and self.lists[key]:
            value = self.lists[key].pop()
            return (key, value)
        return None
    
    async def llen(self, key: str):
        """Mock llen"""
        return len(self.lists.get(key, []))
    
    async def lrange(self, key: str, start: int, end: int):
        """Mock lrange"""
        items = self.lists.get(key, [])
        if end == -1:
            return items[start:]
        return items[start:end+1]
    
    async def lrem(self, key: str, count: int, value: str):
        """Mock lrem"""
        if key in self.lists:
            try:
                self.lists[key].remove(value)
                return 1
            except ValueError:
                return 0
        return 0
    
    async def hset(self, key: str, field: str = None, value: str = None, mapping: Dict = None):
        """Mock hset"""
        if key not in self.hashes:
            self.hashes[key] = {}
        
        if mapping:
            self.hashes[key].update(mapping)
        elif field and value:
            self.hashes[key][field] = value
        
        return 1
    
    async def hget(self, key: str, field: str):
        """Mock hget"""
        return self.hashes.get(key, {}).get(field)
    
    async def hgetall(self, key: str):
        """Mock hgetall"""
        return self.hashes.get(key, {})
    
    async def hdel(self, key: str, field: str):
        """Mock hdel"""
        if key in self.hashes and field in self.hashes[key]:
            del self.hashes[key][field]
            return 1
        return 0
    
    async def hlen(self, key: str):
        """Mock hlen"""
        return len(self.hashes.get(key, {}))
    
    async def expire(self, key: str, seconds: int):
        """Mock expire"""
        return True
    
    async def close(self):
        """Mock close"""
        self.connected = False


class TestQueuedQuery:
    """Test QueuedQuery functionality"""
    
    def test_queued_query_creation(self):
        """Test creating a queued query"""
        query = ConsultationQuery(
            query_id="test-query",
            user_id="test-user",
            query_text="Test query",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        queued_query = QueuedQuery(
            queue_id="queue-123",
            original_query=query,
            priority=QueryPriority.HIGH,
            status=QueueStatus.PENDING,
            queued_at=datetime.utcnow(),
            estimated_processing_time=timedelta(minutes=5),
            estimated_cost=0.25,
            retry_count=0,
            max_retries=3,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            metadata={"test": "data"}
        )
        
        assert queued_query.queue_id == "queue-123"
        assert queued_query.original_query == query
        assert queued_query.priority == QueryPriority.HIGH
        assert queued_query.status == QueueStatus.PENDING
        assert queued_query.estimated_cost == 0.25
        assert queued_query.retry_count == 0
        assert queued_query.metadata["test"] == "data"
    
    def test_queued_query_to_dict(self):
        """Test converting queued query to dictionary"""
        query = ConsultationQuery(
            query_id="test-query",
            user_id="test-user",
            query_text="Test query",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        queued_at = datetime.utcnow()
        expires_at = queued_at + timedelta(hours=1)
        
        queued_query = QueuedQuery(
            queue_id="queue-123",
            original_query=query,
            priority=QueryPriority.HIGH,
            status=QueueStatus.PENDING,
            queued_at=queued_at,
            estimated_processing_time=timedelta(minutes=5),
            estimated_cost=0.25,
            retry_count=0,
            max_retries=3,
            expires_at=expires_at,
            metadata={"test": "data"}
        )
        
        data = queued_query.to_dict()
        
        assert data['queue_id'] == "queue-123"
        assert data['priority'] == "high"
        assert data['status'] == "pending"
        assert data['estimated_cost'] == 0.25
        assert data['retry_count'] == 0
        assert data['metadata']['test'] == "data"
        assert 'original_query' in data
        assert data['original_query']['query_id'] == "test-query"
    
    def test_queued_query_from_dict(self):
        """Test creating queued query from dictionary"""
        data = {
            'queue_id': "queue-123",
            'original_query': {
                'query_id': "test-query",
                'user_id': "test-user",
                'query_text': "Test query",
                'priority': "normal",
                'timestamp': datetime.utcnow().isoformat()
            },
            'priority': "high",
            'status': "pending",
            'queued_at': datetime.utcnow().isoformat(),
            'estimated_processing_time': 300.0,  # 5 minutes
            'estimated_cost': 0.25,
            'retry_count': 0,
            'max_retries': 3,
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'metadata': {"test": "data"}
        }
        
        queued_query = QueuedQuery.from_dict(data)
        
        assert queued_query.queue_id == "queue-123"
        assert queued_query.priority == QueryPriority.HIGH
        assert queued_query.status == QueueStatus.PENDING
        assert queued_query.estimated_cost == 0.25
        assert queued_query.retry_count == 0
        assert queued_query.metadata["test"] == "data"
        assert queued_query.original_query.query_id == "test-query"


class TestQueryQueue:
    """Test QueryQueue functionality"""
    
    @pytest.fixture
    async def mock_redis(self):
        """Create mock Redis instance"""
        return MockRedis()
    
    @pytest.fixture
    async def query_queue(self, mock_redis):
        """Create query queue with mock Redis"""
        queue = QueryQueue(
            redis_url="redis://localhost:6379",
            redis_db=2,
            max_queue_size=100,
            max_processing_time=timedelta(minutes=30),
            cleanup_interval=60,
            max_retries=2
        )
        
        # Replace Redis with mock
        queue.redis = mock_redis
        
        return queue
    
    @pytest.fixture
    def sample_query(self):
        """Create sample consultation query"""
        return ConsultationQuery(
            query_id="test-query-123",
            user_id="test-user",
            query_text="What is the current system status?",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
    
    async def test_queue_initialization(self, query_queue):
        """Test queue initializes correctly"""
        assert query_queue.max_queue_size == 100
        assert query_queue.max_retries == 2
        assert query_queue.redis is not None
        assert len(query_queue.queue_keys) == 4  # One for each priority
        assert query_queue.stats['queries_queued'] == 0
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_enqueue_success(self, mock_flags, query_queue, sample_query):
        """Test successful query enqueuing"""
        mock_flags.is_enabled.return_value = True
        
        queued_query = await query_queue.enqueue(
            sample_query,
            estimated_cost=0.15,
            estimated_processing_time=timedelta(minutes=3)
        )
        
        assert isinstance(queued_query, QueuedQuery)
        assert queued_query.original_query == sample_query
        assert queued_query.priority == sample_query.priority
        assert queued_query.status == QueueStatus.PENDING
        assert queued_query.estimated_cost == 0.15
        assert queued_query.retry_count == 0
        
        # Check statistics updated
        assert query_queue.stats['queries_queued'] == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_enqueue_feature_disabled(self, mock_flags, query_queue, sample_query):
        """Test enqueue when feature is disabled"""
        mock_flags.is_enabled.return_value = False
        
        with pytest.raises(ProcessingError, match="Queue processing is disabled"):
            await query_queue.enqueue(sample_query)
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_enqueue_queue_full(self, mock_flags, query_queue, sample_query):
        """Test enqueue when queue is full"""
        mock_flags.is_enabled.return_value = True
        
        # Set small queue size
        query_queue.max_queue_size = 1
        
        # Fill queue
        await query_queue.enqueue(sample_query)
        
        # Next enqueue should fail
        with pytest.raises(QueueFullError, match="Queue is full"):
            await query_queue.enqueue(sample_query)
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_dequeue_priority_order(self, mock_flags, query_queue):
        """Test dequeue respects priority order"""
        mock_flags.is_enabled.return_value = True
        
        # Create queries with different priorities
        urgent_query = ConsultationQuery(
            query_id="urgent",
            user_id="user",
            query_text="Urgent query",
            priority=QueryPriority.URGENT,
            timestamp=datetime.utcnow()
        )
        
        normal_query = ConsultationQuery(
            query_id="normal",
            user_id="user",
            query_text="Normal query",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        # Enqueue in reverse priority order
        await query_queue.enqueue(normal_query)
        await query_queue.enqueue(urgent_query)
        
        # Dequeue should return urgent first
        dequeued = await query_queue.dequeue(timeout=0.1)
        assert dequeued is not None
        assert dequeued.original_query.query_id == "urgent"
        assert dequeued.status == QueueStatus.PROCESSING
        
        # Next should be normal
        dequeued = await query_queue.dequeue(timeout=0.1)
        assert dequeued is not None
        assert dequeued.original_query.query_id == "normal"
    
    async def test_dequeue_empty_queue(self, query_queue):
        """Test dequeue from empty queue"""
        dequeued = await query_queue.dequeue(timeout=0.1)
        assert dequeued is None
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_complete_query(self, mock_flags, query_queue, sample_query):
        """Test completing a query"""
        mock_flags.is_enabled.return_value = True
        
        # Enqueue and dequeue
        await query_queue.enqueue(sample_query)
        queued_query = await query_queue.dequeue(timeout=0.1)
        
        # Create result
        result = ConsultationResult(
            result_id="result-123",
            query_id=sample_query.query_id,
            response_text="System is healthy",
            processing_time=2.5,
            cost=0.15,
            timestamp=datetime.utcnow()
        )
        
        # Complete query
        success = await query_queue.complete_query(queued_query, result)
        assert success
        
        # Check statistics
        assert query_queue.stats['queries_processed'] == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_fail_query_with_retry(self, mock_flags, query_queue, sample_query):
        """Test failing a query with retry"""
        mock_flags.is_enabled.return_value = True
        
        # Enqueue and dequeue
        await query_queue.enqueue(sample_query)
        queued_query = await query_queue.dequeue(timeout=0.1)
        
        # Fail query (should retry)
        success = await query_queue.fail_query(queued_query, "Test error", retry=True)
        assert success
        assert queued_query.retry_count == 1
        
        # Should be re-queued
        # Note: In real implementation, there would be a delay
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_fail_query_max_retries(self, mock_flags, query_queue, sample_query):
        """Test failing a query that exceeds max retries"""
        mock_flags.is_enabled.return_value = True
        
        # Enqueue and dequeue
        await query_queue.enqueue(sample_query)
        queued_query = await query_queue.dequeue(timeout=0.1)
        
        # Set retry count to max
        queued_query.retry_count = query_queue.max_retries
        
        # Fail query (should not retry)
        success = await query_queue.fail_query(queued_query, "Final error", retry=True)
        assert success
        assert queued_query.status == QueueStatus.FAILED
        
        # Check statistics
        assert query_queue.stats['queries_failed'] == 1
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_cancel_query(self, mock_flags, query_queue, sample_query):
        """Test cancelling a queued query"""
        mock_flags.is_enabled.return_value = True
        
        # Enqueue query
        queued_query = await query_queue.enqueue(sample_query)
        
        # Cancel query
        success = await query_queue.cancel_query(queued_query.queue_id)
        assert success
        
        # Check statistics
        assert query_queue.stats['queries_cancelled'] == 1
        
        # Queue should be empty
        dequeued = await query_queue.dequeue(timeout=0.1)
        assert dequeued is None
    
    async def test_get_queue_status(self, query_queue):
        """Test getting queue status"""
        status = await query_queue.get_queue_status()
        
        assert 'queue_sizes' in status
        assert 'total_pending' in status
        assert 'processing_count' in status
        assert 'statistics' in status
        assert 'configuration' in status
        
        # Check queue sizes for all priorities
        for priority in QueryPriority:
            assert priority.value in status['queue_sizes']
        
        # Check configuration
        assert status['configuration']['max_queue_size'] == 100
        assert status['configuration']['max_retries'] == 2
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue.feature_flags')
    async def test_get_user_queries(self, mock_flags, query_queue):
        """Test getting queries for specific user"""
        mock_flags.is_enabled.return_value = True
        
        # Create queries for different users
        user1_query = ConsultationQuery(
            query_id="user1-query",
            user_id="user1",
            query_text="User 1 query",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        user2_query = ConsultationQuery(
            query_id="user2-query",
            user_id="user2",
            query_text="User 2 query",
            priority=QueryPriority.HIGH,
            timestamp=datetime.utcnow()
        )
        
        # Enqueue queries
        await query_queue.enqueue(user1_query)
        await query_queue.enqueue(user2_query)
        
        # Get queries for user1
        user1_queries = await query_queue.get_user_queries("user1")
        assert len(user1_queries) == 1
        assert user1_queries[0]['original_query']['user_id'] == "user1"
        
        # Get queries for user2
        user2_queries = await query_queue.get_user_queries("user2")
        assert len(user2_queries) == 1
        assert user2_queries[0]['original_query']['user_id'] == "user2"
    
    async def test_estimate_wait_time(self, query_queue):
        """Test wait time estimation"""
        # Mock some queue data
        query_queue.redis.lists = {
            query_queue.queue_keys[QueryPriority.URGENT]: ["query1", "query2"],
            query_queue.queue_keys[QueryPriority.HIGH]: ["query3"],
            query_queue.queue_keys[QueryPriority.NORMAL]: ["query4", "query5", "query6"]
        }
        
        query_queue.redis.hashes = {
            query_queue.processing_key: {"proc1": "processing_query"}
        }
        
        # Estimate wait time for normal priority
        wait_time = await query_queue.estimate_wait_time(QueryPriority.NORMAL)
        
        assert isinstance(wait_time, timedelta)
        assert wait_time.total_seconds() > 0
        
        # Urgent should have shorter wait time
        urgent_wait = await query_queue.estimate_wait_time(QueryPriority.URGENT)
        assert urgent_wait < wait_time
    
    async def test_health_status_healthy(self, query_queue):
        """Test health status when queue is healthy"""
        health = await query_queue.get_health_status()
        
        assert health.component == "query_queue"
        assert health.status == "healthy"
        assert health.error_message is None
        assert 'total_pending' in health.metadata
        assert 'processing_count' in health.metadata
    
    async def test_health_status_degraded(self, query_queue):
        """Test health status when queue is getting full"""
        # Fill queue to 80% capacity
        for i in range(80):
            query_queue.redis.lists[query_queue.queue_keys[QueryPriority.NORMAL]] = [f"query{i}" for i in range(80)]
        
        health = await query_queue.get_health_status()
        
        assert health.component == "query_queue"
        assert health.status == "degraded"
        assert "getting full" in health.error_message.lower()
    
    async def test_health_status_critical(self, query_queue):
        """Test health status when queue is nearly full"""
        # Fill queue to 95% capacity
        for i in range(95):
            query_queue.redis.lists[query_queue.queue_keys[QueryPriority.NORMAL]] = [f"query{i}" for i in range(95)]
        
        health = await query_queue.get_health_status()
        
        assert health.component == "query_queue"
        assert health.status == "critical"
        assert "nearly full" in health.error_message.lower()
    
    async def test_health_status_no_redis(self):
        """Test health status when Redis is not available"""
        queue = QueryQueue()
        # Don't initialize Redis
        
        health = await queue.get_health_status()
        
        assert health.component == "query_queue"
        assert health.status == "unhealthy"
        assert "Redis connection not available" in health.error_message
    
    async def test_cleanup_expired_queries(self, query_queue):
        """Test cleanup of expired queries"""
        # Create expired query data
        expired_time = datetime.utcnow() - timedelta(hours=2)
        expired_query_data = {
            'queue_id': 'expired-query',
            'expires_at': expired_time.isoformat(),
            'status': 'pending'
        }
        
        # Add to queue
        queue_key = query_queue.queue_keys[QueryPriority.NORMAL]
        query_queue.redis.lists[queue_key] = [json.dumps(expired_query_data)]
        
        # Run cleanup
        await query_queue._cleanup_expired_queries()
        
        # Expired query should be removed
        assert len(query_queue.redis.lists[queue_key]) == 0
        assert query_queue.stats['queries_expired'] > 0
    
    async def test_shutdown(self, query_queue):
        """Test queue shutdown"""
        # Start cleanup task
        query_queue.cleanup_task = asyncio.create_task(asyncio.sleep(10))
        
        # Shutdown
        await query_queue.shutdown()
        
        # Cleanup task should be cancelled
        assert query_queue.cleanup_task.cancelled()
        
        # Redis should be closed
        assert not query_queue.redis.connected


class TestGlobalQueryQueue:
    """Test global queue queue functions"""
    
    @patch('src.beast_mode.observatory.ai_consultation.query_queue._query_queue', None)
    async def test_get_query_queue(self):
        """Test getting global queue instance"""
        with patch('src.beast_mode.observatory.ai_consultation.query_queue.QueryQueue') as MockQueue:
            mock_instance = AsyncMock()
            MockQueue.return_value = mock_instance
            
            queue1 = await get_query_queue()
            queue2 = await get_query_queue()
            
            assert queue1 is queue2  # Should be singleton
            mock_instance.initialize.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])