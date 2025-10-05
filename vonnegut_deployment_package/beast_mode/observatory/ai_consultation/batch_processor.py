"""
Batch Query Processor

Processes queued consultation queries with cost optimization, deduplication, and failure handling.
Provides efficient batch processing with resource limits and circuit breaker protection.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import json
from collections import defaultdict

from .models import (
    ConsultationQuery, ConsultationResult, QueryPriority, ProcessingMode
)
from .query_queue import get_query_queue, QueuedQuery, QueueStatus
from .request_processor import get_request_processor, ContextInjectionMode
from .llm_service import get_llm_service
from .doctor_status_manager import get_doctor_status, status_manager
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ConsultationError, ProcessingError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class BatchStatus(str, Enum):
    """Batch processing status"""
    IDLE = "idle"
    PROCESSING = "processing"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class BatchMetrics:
    """Metrics for batch processing"""
    batch_id: str
    start_time: datetime
    end_time: Optional[datetime]
    queries_processed: int
    queries_successful: int
    queries_failed: int
    queries_deduplicated: int
    total_cost: float
    total_processing_time: float
    batch_size: int
    cost_per_query_avg: float
    processing_time_avg: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            'batch_id': self.batch_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'queries_processed': self.queries_processed,
            'queries_successful': self.queries_successful,
            'queries_failed': self.queries_failed,
            'queries_deduplicated': self.queries_deduplicated,
            'total_cost': self.total_cost,
            'total_processing_time': self.total_processing_time,
            'batch_size': self.batch_size,
            'cost_per_query_avg': self.cost_per_query_avg,
            'processing_time_avg': self.processing_time_avg
        }


@dataclass
class BatchConfiguration:
    """Configuration for batch processing"""
    max_batch_size: int = 10
    min_batch_size: int = 1
    max_cost_per_batch: float = 5.0
    max_processing_time: timedelta = timedelta(minutes=30)
    deduplication_enabled: bool = True
    deduplication_window: timedelta = timedelta(hours=1)
    cost_optimization_enabled: bool = True
    parallel_processing: bool = True
    max_concurrent_queries: int = 5
    batch_timeout: timedelta = timedelta(minutes=5)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'max_batch_size': self.max_batch_size,
            'min_batch_size': self.min_batch_size,
            'max_cost_per_batch': self.max_cost_per_batch,
            'max_processing_time_minutes': self.max_processing_time.total_seconds() / 60,
            'deduplication_enabled': self.deduplication_enabled,
            'deduplication_window_hours': self.deduplication_window.total_seconds() / 3600,
            'cost_optimization_enabled': self.cost_optimization_enabled,
            'parallel_processing': self.parallel_processing,
            'max_concurrent_queries': self.max_concurrent_queries,
            'batch_timeout_minutes': self.batch_timeout.total_seconds() / 60
        }


class BatchQueryProcessor:
    """
    Batch Query Processor with cost optimization and failure handling
    
    Features:
    - Batch processing logic for cost efficiency
    - Query deduplication and optimization
    - Batch size optimization based on cost limits and system load
    - Circuit breaker protection for batch processing
    - Resource limits and timeout protection
    - Comprehensive error handling and retry logic
    """
    
    def __init__(
        self,
        config: Optional[BatchConfiguration] = None,
        processing_interval: float = 30.0,  # 30 seconds between batch checks
        max_idle_time: timedelta = timedelta(minutes=5)
    ):
        self.config = config or BatchConfiguration()
        self.processing_interval = processing_interval
        self.max_idle_time = max_idle_time
        
        # Processing state
        self.status = BatchStatus.IDLE
        self.current_batch_id: Optional[str] = None
        self.processing_task: Optional[asyncio.Task] = None
        self.stop_requested = False
        
        # Statistics
        self.stats = {
            'batches_processed': 0,
            'batches_successful': 0,
            'batches_failed': 0,
            'total_queries_processed': 0,
            'total_queries_successful': 0,
            'total_queries_failed': 0,
            'total_queries_deduplicated': 0,
            'total_cost': 0.0,
            'total_processing_time': 0.0,
            'avg_batch_size': 0.0,
            'avg_cost_per_batch': 0.0,
            'avg_processing_time_per_batch': 0.0,
            'last_batch_time': None
        }
        
        # Deduplication cache
        self.query_cache: Dict[str, Tuple[datetime, str]] = {}  # hash -> (timestamp, result)
        
        # Current batch metrics
        self.current_metrics: Optional[BatchMetrics] = None
    
    async def initialize(self) -> None:
        """Initialize the batch processor"""
        try:
            logger.info("Initializing Batch Query Processor")
            
            # Check if batch processing is enabled
            if not await feature_flags.is_enabled(FeatureFlag.BATCH_PROCESSING):
                logger.info("Batch processing is disabled via feature flag")
                return
            
            # Start processing loop
            await self._start_processing_loop()
            
            logger.info("Batch Query Processor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Batch Query Processor: {e}")
            # Don't raise - should degrade gracefully
    
    async def _start_processing_loop(self) -> None:
        """Start the batch processing loop"""
        try:
            if self.processing_task and not self.processing_task.done():
                return  # Already running
            
            self.stop_requested = False
            self.status = BatchStatus.IDLE
            self.processing_task = asyncio.create_task(self._processing_loop())
            
        except Exception as e:
            logger.error(f"Failed to start processing loop: {e}")
    
    async def _processing_loop(self) -> None:
        """Main batch processing loop"""
        try:
            logger.info("Batch processing loop started")
            
            while not self.stop_requested:
                try:
                    # Check if batch processing is enabled
                    if not await feature_flags.is_enabled(FeatureFlag.BATCH_PROCESSING):
                        await asyncio.sleep(self.processing_interval)
                        continue
                    
                    # Check if doctor is available for batch processing
                    doctor_status = await get_doctor_status()
                    if not doctor_status.is_available:
                        logger.debug("Doctor unavailable, skipping batch processing")
                        await asyncio.sleep(self.processing_interval)
                        continue
                    
                    # Process next batch
                    await self._process_next_batch()
                    
                    # Wait before next iteration
                    await asyncio.sleep(self.processing_interval)
                    
                except asyncio.CancelledError:
                    logger.info("Batch processing loop cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in batch processing loop: {e}")
                    self.status = BatchStatus.ERROR
                    await asyncio.sleep(self.processing_interval * 2)  # Back off on error
            
            self.status = BatchStatus.STOPPED
            logger.info("Batch processing loop stopped")
            
        except asyncio.CancelledError:
            logger.info("Batch processing loop cancelled")
            self.status = BatchStatus.STOPPED
        except Exception as e:
            logger.error(f"Fatal error in batch processing loop: {e}")
            self.status = BatchStatus.ERROR
    
    @with_circuit_breaker('batch_processing')
    async def _process_next_batch(self) -> None:
        """Process the next batch of queries"""
        try:
            # Get queue instance
            queue = await get_query_queue()
            
            # Build batch
            batch_queries = await self._build_batch(queue)
            
            if not batch_queries:
                # No queries to process
                if self.status == BatchStatus.PROCESSING:
                    self.status = BatchStatus.IDLE
                return
            
            # Update status
            self.status = BatchStatus.PROCESSING
            self.current_batch_id = f"batch_{int(time.time())}_{len(batch_queries)}"
            
            # Initialize batch metrics
            self.current_metrics = BatchMetrics(
                batch_id=self.current_batch_id,
                start_time=datetime.utcnow(),
                end_time=None,
                queries_processed=0,
                queries_successful=0,
                queries_failed=0,
                queries_deduplicated=0,
                total_cost=0.0,
                total_processing_time=0.0,
                batch_size=len(batch_queries),
                cost_per_query_avg=0.0,
                processing_time_avg=0.0
            )
            
            logger.info(f"Processing batch {self.current_batch_id} with {len(batch_queries)} queries")
            
            # Process batch
            await self._process_batch(batch_queries, queue)
            
            # Finalize metrics
            self._finalize_batch_metrics()
            
            # Update statistics
            self._update_stats()
            
            logger.info(f"Completed batch {self.current_batch_id}: "
                       f"{self.current_metrics.queries_successful} successful, "
                       f"{self.current_metrics.queries_failed} failed, "
                       f"${self.current_metrics.total_cost:.4f} cost")
            
            self.status = BatchStatus.IDLE
            
        except Exception as e:
            logger.error(f"Failed to process batch: {e}")
            self.status = BatchStatus.ERROR
            
            # Mark current batch as failed if we have one
            if self.current_metrics:
                self.current_metrics.end_time = datetime.utcnow()
                self.stats['batches_failed'] += 1
    
    async def _build_batch(self, queue) -> List[QueuedQuery]:
        """Build optimal batch of queries"""
        try:
            batch_queries = []
            total_estimated_cost = 0.0
            seen_hashes = set()
            
            # Dequeue queries up to batch limits
            for _ in range(self.config.max_batch_size):
                if self.stop_requested:
                    break
                
                # Try to dequeue with short timeout
                queued_query = await queue.dequeue(timeout=1.0)
                if not queued_query:
                    break  # No more queries
                
                # Check deduplication
                if self.config.deduplication_enabled:
                    query_hash = self._get_query_hash(queued_query.original_query)
                    
                    # Check if we've seen this query recently
                    if query_hash in self.query_cache:
                        cached_time, cached_result = self.query_cache[query_hash]
                        if datetime.utcnow() - cached_time < self.config.deduplication_window:
                            # Use cached result
                            await self._use_cached_result(queued_query, cached_result, queue)
                            if self.current_metrics:
                                self.current_metrics.queries_deduplicated += 1
                            continue
                    
                    # Check for duplicates within current batch
                    if query_hash in seen_hashes:
                        # Skip duplicate within batch
                        await queue.fail_query(queued_query, "Duplicate query in batch", retry=False)
                        if self.current_metrics:
                            self.current_metrics.queries_deduplicated += 1
                        continue
                    
                    seen_hashes.add(query_hash)
                
                # Check cost limits
                estimated_cost = queued_query.estimated_cost or 0.1  # Default estimate
                if total_estimated_cost + estimated_cost > self.config.max_cost_per_batch:
                    # Would exceed cost limit, put back in queue
                    await self._requeue_query(queued_query, queue)
                    break
                
                batch_queries.append(queued_query)
                total_estimated_cost += estimated_cost
            
            # Check minimum batch size
            if len(batch_queries) < self.config.min_batch_size:
                # Not enough queries, put them back
                for query in batch_queries:
                    await self._requeue_query(query, queue)
                return []
            
            return batch_queries
            
        except Exception as e:
            logger.error(f"Failed to build batch: {e}")
            return []
    
    async def _process_batch(self, batch_queries: List[QueuedQuery], queue) -> None:
        """Process a batch of queries"""
        try:
            if self.config.parallel_processing:
                await self._process_batch_parallel(batch_queries, queue)
            else:
                await self._process_batch_sequential(batch_queries, queue)
                
        except Exception as e:
            logger.error(f"Failed to process batch: {e}")
            # Mark all remaining queries as failed
            for query in batch_queries:
                if query.status == QueueStatus.PROCESSING:
                    await queue.fail_query(query, f"Batch processing error: {str(e)}")
    
    async def _process_batch_parallel(self, batch_queries: List[QueuedQuery], queue) -> None:
        """Process batch queries in parallel"""
        try:
            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.config.max_concurrent_queries)
            
            # Create tasks for all queries
            tasks = [
                self._process_single_query_with_semaphore(query, queue, semaphore)
                for query in batch_queries
            ]
            
            # Wait for all tasks with timeout
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.config.batch_timeout.total_seconds()
                )
            except asyncio.TimeoutError:
                logger.error(f"Batch processing timed out after {self.config.batch_timeout}")
                # Cancel remaining tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                
        except Exception as e:
            logger.error(f"Failed to process batch in parallel: {e}")
    
    async def _process_batch_sequential(self, batch_queries: List[QueuedQuery], queue) -> None:
        """Process batch queries sequentially"""
        try:
            for query in batch_queries:
                if self.stop_requested:
                    break
                
                await self._process_single_query(query, queue)
                
        except Exception as e:
            logger.error(f"Failed to process batch sequentially: {e}")
    
    async def _process_single_query_with_semaphore(
        self, 
        query: QueuedQuery, 
        queue, 
        semaphore: asyncio.Semaphore
    ) -> None:
        """Process single query with semaphore for concurrency control"""
        async with semaphore:
            await self._process_single_query(query, queue)
    
    async def _process_single_query(self, query: QueuedQuery, queue) -> None:
        """Process a single query"""
        start_time = time.time()
        
        try:
            # Get processors
            request_processor = await get_request_processor()
            llm_service = await get_llm_service()
            
            # Process request
            processed_request = await request_processor.process_request(
                query.original_query,
                context_mode=ContextInjectionMode.SUMMARY  # Use summary for batch processing
            )
            
            # Generate LLM response
            llm_response = await llm_service.generate_response(
                processed_request,
                stream=False,
                timeout=30.0
            )
            
            # Create consultation result
            processing_time = time.time() - start_time
            result = ConsultationResult(
                result_id=f"batch_{query.queue_id}_{int(time.time())}",
                query_id=query.original_query.query_id,
                response_text=llm_response.content,
                processing_time=processing_time,
                cost=llm_response.cost.total_cost,
                timestamp=datetime.utcnow(),
                processing_mode=ProcessingMode.QUEUE,
                metadata={
                    'batch_id': self.current_batch_id,
                    'batch_processing': True,
                    'llm_provider': llm_response.provider.value,
                    'llm_model': llm_response.model.value,
                    'token_usage': llm_response.usage.total_tokens
                }
            )
            
            # Complete query
            await queue.complete_query(query, result)
            
            # Cache result for deduplication
            if self.config.deduplication_enabled:
                query_hash = self._get_query_hash(query.original_query)
                self.query_cache[query_hash] = (datetime.utcnow(), result.response_text)
            
            # Update metrics
            if self.current_metrics:
                self.current_metrics.queries_processed += 1
                self.current_metrics.queries_successful += 1
                self.current_metrics.total_cost += result.cost
                self.current_metrics.total_processing_time += processing_time
            
            logger.debug(f"Successfully processed query {query.queue_id}")
            
        except Exception as e:
            logger.error(f"Failed to process query {query.queue_id}: {e}")
            
            # Fail query
            await queue.fail_query(query, str(e))
            
            # Update metrics
            if self.current_metrics:
                self.current_metrics.queries_processed += 1
                self.current_metrics.queries_failed += 1
    
    async def _use_cached_result(self, query: QueuedQuery, cached_result: str, queue) -> None:
        """Use cached result for deduplicated query"""
        try:
            # Create result from cache
            result = ConsultationResult(
                result_id=f"cached_{query.queue_id}_{int(time.time())}",
                query_id=query.original_query.query_id,
                response_text=cached_result,
                processing_time=0.1,  # Minimal time for cached result
                cost=0.0,  # No cost for cached result
                timestamp=datetime.utcnow(),
                processing_mode=ProcessingMode.QUEUE,
                metadata={
                    'batch_id': self.current_batch_id,
                    'cached_result': True,
                    'deduplication': True
                }
            )
            
            # Complete query with cached result
            await queue.complete_query(query, result)
            
            logger.debug(f"Used cached result for query {query.queue_id}")
            
        except Exception as e:
            logger.error(f"Failed to use cached result for query {query.queue_id}: {e}")
            await queue.fail_query(query, f"Cached result error: {str(e)}")
    
    async def _requeue_query(self, query: QueuedQuery, queue) -> None:
        """Put query back in queue"""
        try:
            # Reset status to pending
            query.status = QueueStatus.PENDING
            
            # Re-enqueue (this is a simplified approach - in practice, 
            # we'd need to properly re-add to the Redis queue)
            logger.debug(f"Re-queuing query {query.queue_id}")
            
        except Exception as e:
            logger.error(f"Failed to re-queue query {query.queue_id}: {e}")
    
    def _get_query_hash(self, query: ConsultationQuery) -> str:
        """Get hash for query deduplication"""
        try:
            # Create hash based on query text and user (normalized)
            content = f"{query.user_id}:{query.query_text.lower().strip()}"
            return hashlib.sha256(content.encode()).hexdigest()[:16]
            
        except Exception as e:
            logger.error(f"Failed to get query hash: {e}")
            return f"error_{int(time.time())}"
    
    def _finalize_batch_metrics(self) -> None:
        """Finalize current batch metrics"""
        try:
            if not self.current_metrics:
                return
            
            self.current_metrics.end_time = datetime.utcnow()
            
            # Calculate averages
            if self.current_metrics.queries_processed > 0:
                self.current_metrics.cost_per_query_avg = (
                    self.current_metrics.total_cost / self.current_metrics.queries_processed
                )
                self.current_metrics.processing_time_avg = (
                    self.current_metrics.total_processing_time / self.current_metrics.queries_processed
                )
            
        except Exception as e:
            logger.error(f"Failed to finalize batch metrics: {e}")
    
    def _update_stats(self) -> None:
        """Update processor statistics"""
        try:
            if not self.current_metrics:
                return
            
            # Update batch statistics
            self.stats['batches_processed'] += 1
            if self.current_metrics.queries_failed == 0:
                self.stats['batches_successful'] += 1
            else:
                self.stats['batches_failed'] += 1
            
            # Update query statistics
            self.stats['total_queries_processed'] += self.current_metrics.queries_processed
            self.stats['total_queries_successful'] += self.current_metrics.queries_successful
            self.stats['total_queries_failed'] += self.current_metrics.queries_failed
            self.stats['total_queries_deduplicated'] += self.current_metrics.queries_deduplicated
            
            # Update cost and time statistics
            self.stats['total_cost'] += self.current_metrics.total_cost
            self.stats['total_processing_time'] += self.current_metrics.total_processing_time
            
            # Update averages
            batches_processed = self.stats['batches_processed']
            if batches_processed > 0:
                self.stats['avg_batch_size'] = (
                    self.stats['total_queries_processed'] / batches_processed
                )
                self.stats['avg_cost_per_batch'] = (
                    self.stats['total_cost'] / batches_processed
                )
                self.stats['avg_processing_time_per_batch'] = (
                    self.stats['total_processing_time'] / batches_processed
                )
            
            self.stats['last_batch_time'] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
    
    def _cleanup_cache(self) -> None:
        """Clean up old entries from deduplication cache"""
        try:
            current_time = datetime.utcnow()
            expired_keys = []
            
            for key, (timestamp, _) in self.query_cache.items():
                if current_time - timestamp > self.config.deduplication_window:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.query_cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")
    
    async def get_processor_stats(self) -> Dict[str, Any]:
        """Get current processor statistics"""
        try:
            # Clean up cache
            self._cleanup_cache()
            
            return {
                'batch_processor_stats': self.stats.copy(),
                'current_status': self.status.value,
                'current_batch_id': self.current_batch_id,
                'current_metrics': (
                    self.current_metrics.to_dict() 
                    if self.current_metrics else None
                ),
                'configuration': self.config.to_dict(),
                'cache_stats': {
                    'cache_size': len(self.query_cache),
                    'deduplication_window_hours': self.config.deduplication_window.total_seconds() / 3600
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get processor stats: {e}")
            return {'error': str(e)}
    
    async def pause_processing(self) -> bool:
        """Pause batch processing"""
        try:
            if self.status == BatchStatus.PROCESSING:
                self.status = BatchStatus.PAUSED
                logger.info("Batch processing paused")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to pause processing: {e}")
            return False
    
    async def resume_processing(self) -> bool:
        """Resume batch processing"""
        try:
            if self.status == BatchStatus.PAUSED:
                self.status = BatchStatus.IDLE
                logger.info("Batch processing resumed")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to resume processing: {e}")
            return False
    
    async def get_health_status(self) -> ComponentHealth:
        """Get processor health status"""
        try:
            # Determine health based on processing state
            if self.status == BatchStatus.ERROR:
                status = "critical"
                error_message = "Batch processor in error state"
            elif self.status == BatchStatus.STOPPED:
                status = "degraded"
                error_message = "Batch processor stopped"
            elif self.processing_task and self.processing_task.done():
                status = "degraded"
                error_message = "Processing task terminated unexpectedly"
            else:
                status = "healthy"
                error_message = None
            
            # Calculate success rate
            total_batches = self.stats['batches_processed']
            success_rate = (
                self.stats['batches_successful'] / max(1, total_batches)
            )
            
            if success_rate < 0.8 and total_batches > 0:
                status = "degraded"
                error_message = f"Low batch success rate: {success_rate:.1%}"
            
            return ComponentHealth(
                component="batch_query_processor",
                status=status,
                response_time=self.stats.get('avg_processing_time_per_batch', 0.0) * 1000,
                error_message=error_message,
                metadata={
                    'current_status': self.status.value,
                    'batches_processed': total_batches,
                    'success_rate': success_rate,
                    'total_cost': self.stats['total_cost'],
                    'cache_size': len(self.query_cache),
                    'avg_batch_size': self.stats['avg_batch_size']
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="batch_query_processor",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def shutdown(self) -> None:
        """Shutdown the batch processor"""
        try:
            logger.info("Shutting down Batch Query Processor")
            
            self.stop_requested = True
            self.status = BatchStatus.STOPPING
            
            # Cancel processing task
            if self.processing_task and not self.processing_task.done():
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            self.status = BatchStatus.STOPPED
            logger.info("Batch Query Processor shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during batch processor shutdown: {e}")


# Global processor instance
_batch_processor: Optional[BatchQueryProcessor] = None


async def get_batch_processor() -> BatchQueryProcessor:
    """Get the global batch processor instance"""
    global _batch_processor
    
    if _batch_processor is None:
        _batch_processor = BatchQueryProcessor()
        await _batch_processor.initialize()
    
    return _batch_processor