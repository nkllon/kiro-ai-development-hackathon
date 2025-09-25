"""
Query Queue Management

Provides Redis-based query queue management with brownfield safety for batch processing.
Handles priority-based queuing, overflow protection, and resource limits.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import redis.asyncio as redis
from redis.asyncio import Redis

from .models import (
    ConsultationQuery, ConsultationResult, QueryPriority, ProcessingMode
)
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ConsultationError, ProcessingError, QueueFullError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class QueueStatus(str, Enum):
    """Queue status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class QueuedQuery:
    """Queued consultation query with metadata"""
    queue_id: str
    original_query: ConsultationQuery
    priority: QueryPriority
    status: QueueStatus
    queued_at: datetime
    estimated_processing_time: Optional[timedelta]
    estimated_cost: Optional[float]
    retry_count: int
    max_retries: int
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        return {
            'queue_id': self.queue_id,
            'original_query': {
                'query_id': self.original_query.query_id,
                'user_id': self.original_query.user_id,
                'query_text': self.original_query.query_text,
                'priority': self.original_query.priority.value,
                'timestamp': self.original_query.timestamp.isoformat()
            },
            'priority': self.priority.value,
            'status': self.status.value,
            'queued_at': self.queued_at.isoformat(),
            'estimated_processing_time': (
                self.estimated_processing_time.total_seconds() 
                if self.estimated_processing_time else None
            ),
            'estimated_cost': self.estimated_cost,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueuedQuery':
        """Create from dictionary loaded from Redis"""
        query_data = data['original_query']
        original_query = ConsultationQuery(
            query_id=query_data['query_id'],
            user_id=query_data['user_id'],
            query_text=query_data['query_text'],
            priority=QueryPriority(query_data['priority']),
            timestamp=datetime.fromisoformat(query_data['timestamp'])
        )
        
        return cls(
            queue_id=data['queue_id'],
            original_query=original_query,
            priority=QueryPriority(data['priority']),
            status=QueueStatus(data['status']),
            queued_at=datetime.fromisoformat(data['queued_at']),
            estimated_processing_time=(
                timedelta(seconds=data['estimated_processing_time'])
                if data['estimated_processing_time'] else None
            ),
            estimated_cost=data['estimated_cost'],
            retry_count=data['retry_count'],
            max_retries=data['max_retries'],
            expires_at=(
                datetime.fromisoformat(data['expires_at'])
                if data['expires_at'] else None
            ),
            metadata=data['metadata']
        )


class QueryQueue:
    """
    Redis-based query queue management with brownfield safety
    
    Features:
    - Priority-based queue management
    - Overflow protection and resource limits
    - Circuit breaker integration
    - Brownfield safety with Observatory Redis
    - Queue statistics and monitoring
    - Automatic cleanup of expired queries
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        redis_db: int = 2,  # Use separate DB to avoid Observatory conflicts
        key_prefix: str = "ai_consultation:",
        max_queue_size: int = 1000,
        max_processing_time: timedelta = timedelta(hours=1),
        cleanup_interval: int = 300,  # 5 minutes
        max_retries: int = 3
    ):
        self.redis_url = redis_url
        self.redis_db = redis_db
        self.key_prefix = key_prefix
        self.max_queue_size = max_queue_size
        self.max_processing_time = max_processing_time
        self.cleanup_interval = cleanup_interval
        self.max_retries = max_retries
        
        # Redis connection
        self.redis: Optional[Redis] = None
        
        # Queue keys
        self.queue_keys = {
            QueryPriority.URGENT: f"{key_prefix}queue:urgent",
            QueryPriority.HIGH: f"{key_prefix}queue:high", 
            QueryPriority.NORMAL: f"{key_prefix}queue:normal",
            QueryPriority.LOW: f"{key_prefix}queue:low"
        }
        
        self.processing_key = f"{key_prefix}processing"
        self.completed_key = f"{key_prefix}completed"
        self.failed_key = f"{key_prefix}failed"
        self.stats_key = f"{key_prefix}stats"
        
        # Statistics
        self.stats = {
            'queries_queued': 0,
            'queries_processed': 0,
            'queries_failed': 0,
            'queries_expired': 0,
            'queries_cancelled': 0,
            'current_queue_size': 0,
            'processing_count': 0,
            'avg_wait_time_seconds': 0.0,
            'avg_processing_time_seconds': 0.0
        }
        
        # Background cleanup task
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> None:
        """Initialize the query queue"""
        try:
            logger.info("Initializing Query Queue")
            
            # Check if queue processing is enabled
            if not await feature_flags.is_enabled(FeatureFlag.QUEUE_PROCESSING):
                logger.info("Queue processing is disabled via feature flag")
                return
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Load existing statistics
            await self._load_stats()
            
            # Start background cleanup
            await self._start_cleanup_task()
            
            logger.info("Query Queue initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Query Queue: {e}")
            # Don't raise - should degrade gracefully
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection with brownfield safety"""
        try:
            # Create Redis connection with separate database
            self.redis = redis.from_url(
                self.redis_url,
                db=self.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis.ping()
            
            logger.info(f"Connected to Redis DB {self.redis_db} for query queue")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ProcessingError(f"Redis connection failed: {e}")
    
    async def _load_stats(self) -> None:
        """Load statistics from Redis"""
        try:
            if not self.redis:
                return
            
            stats_data = await self.redis.hgetall(self.stats_key)
            if stats_data:
                for key, value in stats_data.items():
                    if key in self.stats:
                        try:
                            self.stats[key] = float(value) if '.' in str(value) else int(value)
                        except (ValueError, TypeError):
                            pass
            
        except Exception as e:
            logger.warning(f"Failed to load stats from Redis: {e}")
    
    async def _save_stats(self) -> None:
        """Save statistics to Redis"""
        try:
            if not self.redis:
                return
            
            await self.redis.hset(self.stats_key, mapping=self.stats)
            
        except Exception as e:
            logger.warning(f"Failed to save stats to Redis: {e}")
    
    async def _start_cleanup_task(self) -> None:
        """Start background cleanup task"""
        try:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
        except Exception as e:
            logger.error(f"Failed to start cleanup task: {e}")
    
    @with_circuit_breaker('query_queue')
    async def enqueue(
        self,
        query: ConsultationQuery,
        estimated_cost: Optional[float] = None,
        estimated_processing_time: Optional[timedelta] = None,
        expires_in: Optional[timedelta] = None
    ) -> QueuedQuery:
        """Add query to queue with priority handling"""
        try:
            # Check if queue processing is enabled
            if not await feature_flags.is_enabled(FeatureFlag.QUEUE_PROCESSING):
                raise ProcessingError("Queue processing is disabled")
            
            if not self.redis:
                raise ProcessingError("Redis connection not available")
            
            # Check queue capacity
            current_size = await self._get_total_queue_size()
            if current_size >= self.max_queue_size:
                raise QueueFullError(f"Queue is full: {current_size}/{self.max_queue_size}")
            
            # Create queued query
            queue_id = f"queue_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            expires_at = None
            if expires_in:
                expires_at = datetime.utcnow() + expires_in
            elif self.max_processing_time:
                expires_at = datetime.utcnow() + self.max_processing_time
            
            queued_query = QueuedQuery(
                queue_id=queue_id,
                original_query=query,
                priority=query.priority,
                status=QueueStatus.PENDING,
                queued_at=datetime.utcnow(),
                estimated_processing_time=estimated_processing_time,
                estimated_cost=estimated_cost,
                retry_count=0,
                max_retries=self.max_retries,
                expires_at=expires_at,
                metadata={}
            )
            
            # Add to appropriate priority queue
            queue_key = self.queue_keys[query.priority]
            query_data = json.dumps(queued_query.to_dict())
            
            # Use Redis list for FIFO within priority
            await self.redis.lpush(queue_key, query_data)
            
            # Update statistics
            self.stats['queries_queued'] += 1
            self.stats['current_queue_size'] = await self._get_total_queue_size()
            await self._save_stats()
            
            logger.info(f"Queued query {queue_id} with priority {query.priority.value}")
            
            return queued_query
            
        except Exception as e:
            logger.error(f"Failed to enqueue query: {e}")
            raise
    
    async def dequeue(self, timeout: float = 1.0) -> Optional[QueuedQuery]:
        """Dequeue next query based on priority"""
        try:
            if not self.redis:
                return None
            
            # Check queues in priority order
            for priority in [QueryPriority.URGENT, QueryPriority.HIGH, QueryPriority.NORMAL, QueryPriority.LOW]:
                queue_key = self.queue_keys[priority]
                
                # Use blocking pop with timeout
                result = await self.redis.brpop(queue_key, timeout=timeout)
                if result:
                    _, query_data = result
                    
                    try:
                        data = json.loads(query_data)
                        queued_query = QueuedQuery.from_dict(data)
                        
                        # Check if expired
                        if queued_query.expires_at and datetime.utcnow() > queued_query.expires_at:
                            await self._mark_expired(queued_query)
                            continue
                        
                        # Move to processing
                        await self._mark_processing(queued_query)
                        
                        return queued_query
                        
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.error(f"Failed to parse queued query: {e}")
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue query: {e}")
            return None
    
    async def complete_query(
        self,
        queued_query: QueuedQuery,
        result: ConsultationResult
    ) -> bool:
        """Mark query as completed"""
        try:
            if not self.redis:
                return False
            
            # Update query status
            queued_query.status = QueueStatus.COMPLETED
            queued_query.metadata['completed_at'] = datetime.utcnow().isoformat()
            queued_query.metadata['result'] = {
                'result_id': result.result_id,
                'response_text': result.response_text[:500],  # Truncate for storage
                'processing_time': result.processing_time,
                'cost': result.cost
            }
            
            # Remove from processing
            await self.redis.hdel(self.processing_key, queued_query.queue_id)
            
            # Add to completed (with TTL for cleanup)
            completed_data = json.dumps(queued_query.to_dict())
            await self.redis.hset(self.completed_key, queued_query.queue_id, completed_data)
            await self.redis.expire(self.completed_key, 86400)  # 24 hours
            
            # Update statistics
            self.stats['queries_processed'] += 1
            self.stats['processing_count'] = await self.redis.hlen(self.processing_key)
            
            # Update wait time statistics
            wait_time = (datetime.utcnow() - queued_query.queued_at).total_seconds()
            await self._update_avg_wait_time(wait_time)
            
            await self._save_stats()
            
            logger.info(f"Completed query {queued_query.queue_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete query {queued_query.queue_id}: {e}")
            return False
    
    async def fail_query(
        self,
        queued_query: QueuedQuery,
        error: str,
        retry: bool = True
    ) -> bool:
        """Mark query as failed and optionally retry"""
        try:
            if not self.redis:
                return False
            
            queued_query.retry_count += 1
            queued_query.metadata['last_error'] = error
            queued_query.metadata['failed_at'] = datetime.utcnow().isoformat()
            
            # Remove from processing
            await self.redis.hdel(self.processing_key, queued_query.queue_id)
            
            # Retry if under limit
            if retry and queued_query.retry_count <= queued_query.max_retries:
                queued_query.status = QueueStatus.PENDING
                
                # Re-queue with exponential backoff delay
                delay = min(300, 30 * (2 ** (queued_query.retry_count - 1)))  # Max 5 minutes
                await asyncio.sleep(delay)
                
                queue_key = self.queue_keys[queued_query.priority]
                query_data = json.dumps(queued_query.to_dict())
                await self.redis.lpush(queue_key, query_data)
                
                logger.info(f"Retrying query {queued_query.queue_id} (attempt {queued_query.retry_count})")
                
            else:
                # Mark as permanently failed
                queued_query.status = QueueStatus.FAILED
                
                failed_data = json.dumps(queued_query.to_dict())
                await self.redis.hset(self.failed_key, queued_query.queue_id, failed_data)
                await self.redis.expire(self.failed_key, 86400)  # 24 hours
                
                self.stats['queries_failed'] += 1
                
                logger.error(f"Query {queued_query.queue_id} failed permanently: {error}")
            
            self.stats['processing_count'] = await self.redis.hlen(self.processing_key)
            await self._save_stats()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle query failure {queued_query.queue_id}: {e}")
            return False 
   
    async def cancel_query(self, queue_id: str) -> bool:
        """Cancel a queued query"""
        try:
            if not self.redis:
                return False
            
            # Check all queues for the query
            for priority in QueryPriority:
                queue_key = self.queue_keys[priority]
                
                # Get all items from queue
                items = await self.redis.lrange(queue_key, 0, -1)
                
                for i, item in enumerate(items):
                    try:
                        data = json.loads(item)
                        if data.get('queue_id') == queue_id:
                            # Remove from queue
                            await self.redis.lrem(queue_key, 1, item)
                            
                            # Mark as cancelled
                            queued_query = QueuedQuery.from_dict(data)
                            queued_query.status = QueueStatus.CANCELLED
                            queued_query.metadata['cancelled_at'] = datetime.utcnow().isoformat()
                            
                            self.stats['queries_cancelled'] += 1
                            await self._save_stats()
                            
                            logger.info(f"Cancelled query {queue_id}")
                            return True
                            
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            # Check processing queue
            processing_data = await self.redis.hget(self.processing_key, queue_id)
            if processing_data:
                await self.redis.hdel(self.processing_key, queue_id)
                self.stats['queries_cancelled'] += 1
                self.stats['processing_count'] = await self.redis.hlen(self.processing_key)
                await self._save_stats()
                
                logger.info(f"Cancelled processing query {queue_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel query {queue_id}: {e}")
            return False
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status and statistics"""
        try:
            if not self.redis:
                return {'error': 'Redis connection not available'}
            
            # Get queue sizes by priority
            queue_sizes = {}
            total_pending = 0
            
            for priority in QueryPriority:
                queue_key = self.queue_keys[priority]
                size = await self.redis.llen(queue_key)
                queue_sizes[priority.value] = size
                total_pending += size
            
            # Get processing count
            processing_count = await self.redis.hlen(self.processing_key)
            
            # Update current stats
            self.stats['current_queue_size'] = total_pending
            self.stats['processing_count'] = processing_count
            
            return {
                'queue_sizes': queue_sizes,
                'total_pending': total_pending,
                'processing_count': processing_count,
                'statistics': self.stats.copy(),
                'configuration': {
                    'max_queue_size': self.max_queue_size,
                    'max_processing_time_hours': self.max_processing_time.total_seconds() / 3600,
                    'max_retries': self.max_retries,
                    'cleanup_interval_minutes': self.cleanup_interval / 60
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {'error': str(e)}
    
    async def get_user_queries(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all queries for a specific user"""
        try:
            if not self.redis:
                return []
            
            user_queries = []
            
            # Check all priority queues
            for priority in QueryPriority:
                queue_key = self.queue_keys[priority]
                items = await self.redis.lrange(queue_key, 0, -1)
                
                for item in items:
                    try:
                        data = json.loads(item)
                        if data.get('original_query', {}).get('user_id') == user_id:
                            user_queries.append(data)
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            # Check processing queue
            processing_items = await self.redis.hgetall(self.processing_key)
            for queue_id, item in processing_items.items():
                try:
                    data = json.loads(item)
                    if data.get('original_query', {}).get('user_id') == user_id:
                        user_queries.append(data)
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Sort by queued_at timestamp
            user_queries.sort(key=lambda x: x.get('queued_at', ''))
            
            return user_queries
            
        except Exception as e:
            logger.error(f"Failed to get user queries for {user_id}: {e}")
            return []
    
    async def estimate_wait_time(self, priority: QueryPriority) -> timedelta:
        """Estimate wait time for a query with given priority"""
        try:
            if not self.redis:
                return timedelta(minutes=30)  # Default estimate
            
            # Count queries ahead in queue
            queries_ahead = 0
            
            # Count higher priority queries
            for p in QueryPriority:
                if p.value < priority.value:  # Higher priority (lower number)
                    queue_key = self.queue_keys[p]
                    queries_ahead += await self.redis.llen(queue_key)
                elif p == priority:
                    # Count queries in same priority queue
                    queue_key = self.queue_keys[p]
                    queries_ahead += await self.redis.llen(queue_key)
                    break
            
            # Add processing queries (they need to finish first)
            queries_ahead += await self.redis.hlen(self.processing_key)
            
            # Estimate based on average processing time
            avg_processing_time = self.stats.get('avg_processing_time_seconds', 120)  # 2 minutes default
            
            estimated_seconds = queries_ahead * avg_processing_time
            
            # Add some buffer
            estimated_seconds *= 1.2
            
            return timedelta(seconds=max(60, estimated_seconds))  # Minimum 1 minute
            
        except Exception as e:
            logger.error(f"Failed to estimate wait time: {e}")
            return timedelta(minutes=30)
    
    async def _mark_processing(self, queued_query: QueuedQuery) -> None:
        """Mark query as processing"""
        try:
            if not self.redis:
                return
            
            queued_query.status = QueueStatus.PROCESSING
            queued_query.metadata['processing_started_at'] = datetime.utcnow().isoformat()
            
            processing_data = json.dumps(queued_query.to_dict())
            await self.redis.hset(self.processing_key, queued_query.queue_id, processing_data)
            
            self.stats['processing_count'] = await self.redis.hlen(self.processing_key)
            
        except Exception as e:
            logger.error(f"Failed to mark query as processing: {e}")
    
    async def _mark_expired(self, queued_query: QueuedQuery) -> None:
        """Mark query as expired"""
        try:
            if not self.redis:
                return
            
            queued_query.status = QueueStatus.EXPIRED
            queued_query.metadata['expired_at'] = datetime.utcnow().isoformat()
            
            self.stats['queries_expired'] += 1
            await self._save_stats()
            
            logger.info(f"Query {queued_query.queue_id} expired")
            
        except Exception as e:
            logger.error(f"Failed to mark query as expired: {e}")
    
    async def _get_total_queue_size(self) -> int:
        """Get total number of queries in all queues"""
        try:
            if not self.redis:
                return 0
            
            total = 0
            for queue_key in self.queue_keys.values():
                total += await self.redis.llen(queue_key)
            
            return total
            
        except Exception as e:
            logger.error(f"Failed to get total queue size: {e}")
            return 0
    
    async def _update_avg_wait_time(self, wait_time_seconds: float) -> None:
        """Update average wait time statistics"""
        try:
            processed_count = self.stats['queries_processed']
            if processed_count > 1:
                current_avg = self.stats['avg_wait_time_seconds']
                self.stats['avg_wait_time_seconds'] = (
                    (current_avg * (processed_count - 1) + wait_time_seconds) / processed_count
                )
            else:
                self.stats['avg_wait_time_seconds'] = wait_time_seconds
                
        except Exception as e:
            logger.error(f"Failed to update average wait time: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_queries()
                
        except asyncio.CancelledError:
            logger.info("Queue cleanup loop cancelled")
        except Exception as e:
            logger.error(f"Queue cleanup loop error: {e}")
    
    async def _cleanup_expired_queries(self) -> None:
        """Clean up expired queries from all queues"""
        try:
            if not self.redis:
                return
            
            expired_count = 0
            current_time = datetime.utcnow()
            
            # Check all priority queues
            for priority in QueryPriority:
                queue_key = self.queue_keys[priority]
                items = await self.redis.lrange(queue_key, 0, -1)
                
                for item in items:
                    try:
                        data = json.loads(item)
                        expires_at_str = data.get('expires_at')
                        
                        if expires_at_str:
                            expires_at = datetime.fromisoformat(expires_at_str)
                            if current_time > expires_at:
                                # Remove expired query
                                await self.redis.lrem(queue_key, 1, item)
                                expired_count += 1
                                
                    except (json.JSONDecodeError, KeyError, ValueError):
                        # Remove malformed entries
                        await self.redis.lrem(queue_key, 1, item)
                        expired_count += 1
            
            # Check processing queue for stuck queries
            processing_items = await self.redis.hgetall(self.processing_key)
            for queue_id, item in processing_items.items():
                try:
                    data = json.loads(item)
                    processing_started = data.get('metadata', {}).get('processing_started_at')
                    
                    if processing_started:
                        started_at = datetime.fromisoformat(processing_started)
                        if current_time - started_at > self.max_processing_time:
                            # Remove stuck processing query
                            await self.redis.hdel(self.processing_key, queue_id)
                            expired_count += 1
                            
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Remove malformed entries
                    await self.redis.hdel(self.processing_key, queue_id)
                    expired_count += 1
            
            if expired_count > 0:
                self.stats['queries_expired'] += expired_count
                self.stats['current_queue_size'] = await self._get_total_queue_size()
                self.stats['processing_count'] = await self.redis.hlen(self.processing_key)
                await self._save_stats()
                
                logger.info(f"Cleaned up {expired_count} expired queries")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired queries: {e}")
    
    async def get_health_status(self) -> ComponentHealth:
        """Get queue health status"""
        try:
            if not self.redis:
                return ComponentHealth(
                    component="query_queue",
                    status="unhealthy",
                    response_time=0.0,
                    error_message="Redis connection not available",
                    metadata={},
                    last_check=datetime.utcnow()
                )
            
            # Test Redis connectivity
            start_time = time.time()
            await self.redis.ping()
            response_time = (time.time() - start_time) * 1000
            
            # Get current queue status
            queue_status = await self.get_queue_status()
            
            # Determine health based on queue state
            total_pending = queue_status.get('total_pending', 0)
            processing_count = queue_status.get('processing_count', 0)
            
            if total_pending >= self.max_queue_size * 0.9:
                status = "critical"
                error_message = f"Queue nearly full: {total_pending}/{self.max_queue_size}"
            elif total_pending >= self.max_queue_size * 0.7:
                status = "degraded"
                error_message = f"Queue getting full: {total_pending}/{self.max_queue_size}"
            elif processing_count > 10:  # Arbitrary threshold
                status = "degraded"
                error_message = f"High processing load: {processing_count} queries"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="query_queue",
                status=status,
                response_time=response_time,
                error_message=error_message,
                metadata={
                    'total_pending': total_pending,
                    'processing_count': processing_count,
                    'queue_utilization': total_pending / self.max_queue_size,
                    'queries_processed': self.stats['queries_processed'],
                    'queries_failed': self.stats['queries_failed']
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="query_queue",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def shutdown(self) -> None:
        """Shutdown the query queue"""
        try:
            logger.info("Shutting down Query Queue")
            
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Close Redis connection
            if self.redis:
                await self.redis.close()
            
            logger.info("Query Queue shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during queue shutdown: {e}")


# Global queue instance
_query_queue: Optional[QueryQueue] = None


async def get_query_queue() -> QueryQueue:
    """Get the global query queue instance"""
    global _query_queue
    
    if _query_queue is None:
        _query_queue = QueryQueue()
        await _query_queue.initialize()
    
    return _query_queue