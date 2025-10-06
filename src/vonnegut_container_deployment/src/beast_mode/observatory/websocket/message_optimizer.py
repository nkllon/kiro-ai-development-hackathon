"""Message batching and optimization for high-frequency WebSocket updates."""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
import heapq

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class BatchStrategy(Enum):
    """Message batching strategies."""
    TIME_BASED = "time_based"
    SIZE_BASED = "size_based"
    COUNT_BASED = "count_based"
    PRIORITY_BASED = "priority_based"
    HYBRID = "hybrid"


@dataclass
class MessageBatch:
    """A batch of messages for optimization."""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: MessagePriority = MessagePriority.NORMAL
    batch_id: str = ""
    total_size: int = 0
    compression_ratio: float = 0.0
    processing_time: float = 0.0

    def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message to the batch."""
        self.messages.append(message)
        self.total_size += len(json.dumps(message))
    
    def get_batch_data(self) -> Dict[str, Any]:
        """Get the batch as a single message."""
        return {
            'batch_id': self.batch_id,
            'message_count': len(self.messages),
            'created_at': self.created_at.isoformat(),
            'priority': self.priority.value,
            'messages': self.messages,
            'total_size': self.total_size,
            'compression_ratio': self.compression_ratio,
        }


@dataclass
class OptimizationMetrics:
    """Message optimization performance metrics."""
    total_messages: int = 0
    batched_messages: int = 0
    compression_savings: float = 0.0
    avg_batch_size: float = 0.0
    avg_processing_time: float = 0.0
    messages_per_second: float = 0.0
    peak_throughput: float = 0.0
    dropped_messages: int = 0
    duplicate_messages: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'total_messages': self.total_messages,
            'batched_messages': self.batched_messages,
            'compression_savings': self.compression_savings,
            'avg_batch_size': self.avg_batch_size,
            'avg_processing_time': self.avg_processing_time,
            'messages_per_second': self.messages_per_second,
            'peak_throughput': self.peak_throughput,
            'dropped_messages': self.dropped_messages,
            'duplicate_messages': self.duplicate_messages,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
        }


@dataclass
class MessageOptimizerConfig:
    """Configuration for message optimization."""
    batch_timeout: float = 0.1  # seconds
    max_batch_size: int = 8192  # bytes
    max_batch_count: int = 100
    enable_compression: bool = True
    enable_deduplication: bool = True
    enable_prioritization: bool = True
    batch_strategy: BatchStrategy = BatchStrategy.HYBRID
    priority_threshold: int = 100  # messages per second
    drop_threshold: float = 0.95  # drop messages when queue is 95% full
    max_queue_size: int = 10000
    compression_threshold: int = 1024  # bytes


class MessageOptimizer:
    """High-performance message batching and optimization system."""

    def __init__(self, config: MessageOptimizerConfig):
        self.config = config
        self._message_queue: List[Tuple[MessagePriority, float, Dict[str, Any]]] = []
        self._batch_queue: List[MessageBatch] = []
        self._active_batches: Dict[str, MessageBatch] = {}
        self._metrics = OptimizationMetrics()
        self._lock = asyncio.Lock()
        self._processing_task: Optional[asyncio.Task] = None
        self._batch_processor_task: Optional[asyncio.Task] = None
        self._message_cache: Dict[str, Any] = {}  # For deduplication
        self._cache_timestamps: Dict[str, datetime] = {}
        self._throughput_history: deque = deque(maxlen=100)
        self._start_time = time.time()
        self._message_counter = 0

    async def initialize(self) -> None:
        """Initialize the message optimizer."""
        async with self._lock:
            # Start background processing tasks
            self._processing_task = asyncio.create_task(self._process_messages())
            self._batch_processor_task = asyncio.create_task(self._process_batches())
            
            logger.info("Message optimizer initialized")

    async def add_message(
        self, 
        message: Dict[str, Any], 
        priority: MessagePriority = MessagePriority.NORMAL,
        batch_key: Optional[str] = None
    ) -> str:
        """Add a message for optimization."""
        message_id = f"msg_{self._message_counter}_{int(time.time() * 1000)}"
        self._message_counter += 1
        
        async with self._lock:
            # Check queue capacity
            if len(self._message_queue) >= self.config.max_queue_size * self.config.drop_threshold:
                self._metrics.dropped_messages += 1
                logger.warning(f"Dropping message due to queue capacity: {message_id}")
                return message_id
            
            # Deduplication check
            if self.config.enable_deduplication:
                message_hash = self._get_message_hash(message)
                if message_hash in self._message_cache:
                    self._metrics.duplicate_messages += 1
                    logger.debug(f"Duplicate message detected: {message_id}")
                    return message_id
                
                self._message_cache[message_hash] = message
                self._cache_timestamps[message_hash] = datetime.utcnow()
            
            # Add to priority queue
            timestamp = time.time()
            heapq.heappush(self._message_queue, (priority, timestamp, message))
            
            # Create or update batch
            if batch_key:
                await self._add_to_batch(batch_key, message, priority)
            
            self._metrics.total_messages += 1
            self._update_throughput_metrics()
            
        return message_id

    async def _add_to_batch(self, batch_key: str, message: Dict[str, Any], priority: MessagePriority) -> None:
        """Add message to a specific batch."""
        if batch_key not in self._active_batches:
            batch = MessageBatch(
                batch_id=batch_key,
                priority=priority,
                created_at=datetime.utcnow()
            )
            self._active_batches[batch_key] = batch
        
        batch = self._active_batches[batch_key]
        batch.add_message(message)
        
        # Check if batch should be processed
        if self._should_process_batch(batch):
            await self._finalize_batch(batch_key)

    def _should_process_batch(self, batch: MessageBatch) -> bool:
        """Determine if a batch should be processed."""
        if self.config.batch_strategy == BatchStrategy.TIME_BASED:
            age = (datetime.utcnow() - batch.created_at).total_seconds()
            return age >= self.config.batch_timeout
        
        elif self.config.batch_strategy == BatchStrategy.SIZE_BASED:
            return batch.total_size >= self.config.max_batch_size
        
        elif self.config.batch_strategy == BatchStrategy.COUNT_BASED:
            return len(batch.messages) >= self.config.max_batch_count
        
        elif self.config.batch_strategy == BatchStrategy.PRIORITY_BASED:
            return batch.priority == MessagePriority.CRITICAL
        
        elif self.config.batch_strategy == BatchStrategy.HYBRID:
            age = (datetime.utcnow() - batch.created_at).total_seconds()
            return (
                age >= self.config.batch_timeout or
                batch.total_size >= self.config.max_batch_size or
                len(batch.messages) >= self.config.max_batch_count or
                batch.priority == MessagePriority.CRITICAL
            )
        
        return False

    async def _finalize_batch(self, batch_key: str) -> None:
        """Finalize and queue a batch for processing."""
        if batch_key not in self._active_batches:
            return
        
        batch = self._active_batches.pop(batch_key)
        batch.processing_time = time.time()
        
        # Apply compression if enabled and beneficial
        if self.config.enable_compression and batch.total_size >= self.config.compression_threshold:
            batch.compression_ratio = await self._calculate_compression_ratio(batch)
        
        self._batch_queue.append(batch)
        self._metrics.batched_messages += len(batch.messages)

    async def _calculate_compression_ratio(self, batch: MessageBatch) -> float:
        """Calculate potential compression ratio for a batch."""
        # Simulate compression ratio calculation
        # In a real implementation, this would use actual compression
        original_size = batch.total_size
        compressed_size = original_size * 0.6  # Assume 40% compression
        return (original_size - compressed_size) / original_size

    async def _process_messages(self) -> None:
        """Background task to process incoming messages."""
        while True:
            try:
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
                async with self._lock:
                    if not self._message_queue:
                        continue
                    
                    # Process high-priority messages immediately
                    high_priority_messages = []
                    normal_messages = []
                    
                    while self._message_queue:
                        priority, timestamp, message = heapq.heappop(self._message_queue)
                        if priority == MessagePriority.CRITICAL:
                            high_priority_messages.append(message)
                        else:
                            normal_messages.append(message)
                    
                    # Process high-priority messages immediately
                    for message in high_priority_messages:
                        await self._process_single_message(message)
                    
                    # Batch normal messages
                    if normal_messages:
                        await self._create_auto_batch(normal_messages)
                
            except Exception as e:
                logger.error(f"Error processing messages: {e}")

    async def _process_single_message(self, message: Dict[str, Any]) -> None:
        """Process a single message immediately."""
        # This would typically send the message directly
        logger.debug(f"Processing single message: {message}")

    async def _create_auto_batch(self, messages: List[Dict[str, Any]]) -> None:
        """Create an automatic batch from messages."""
        batch = MessageBatch(
            batch_id=f"auto_{int(time.time() * 1000)}",
            created_at=datetime.utcnow(),
            priority=MessagePriority.NORMAL
        )
        
        for message in messages:
            batch.add_message(message)
        
        batch.processing_time = time.time()
        self._batch_queue.append(batch)
        self._metrics.batched_messages += len(batch.messages)

    async def _process_batches(self) -> None:
        """Background task to process completed batches."""
        while True:
            try:
                await asyncio.sleep(0.05)  # Process batches every 50ms
                
                async with self._lock:
                    if not self._batch_queue:
                        continue
                    
                    # Process batches in priority order
                    batches_to_process = []
                    while self._batch_queue:
                        batch = self._batch_queue.pop(0)
                        batches_to_process.append(batch)
                    
                    # Sort by priority and process
                    batches_to_process.sort(key=lambda b: b.priority.value, reverse=True)
                    
                    for batch in batches_to_process:
                        await self._process_batch(batch)
                
            except Exception as e:
                logger.error(f"Error processing batches: {e}")

    async def _process_batch(self, batch: MessageBatch) -> None:
        """Process a completed batch."""
        start_time = time.time()
        
        try:
            # Apply optimizations
            optimized_batch = await self._optimize_batch(batch)
            
            # Send the batch (this would integrate with the connection pool)
            await self._send_batch(optimized_batch)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_batch_metrics(batch, processing_time)
            
        except Exception as e:
            logger.error(f"Error processing batch {batch.batch_id}: {e}")

    async def _optimize_batch(self, batch: MessageBatch) -> MessageBatch:
        """Apply various optimizations to a batch."""
        # Message deduplication within batch
        if self.config.enable_deduplication:
            unique_messages = []
            seen_hashes = set()
            
            for message in batch.messages:
                message_hash = self._get_message_hash(message)
                if message_hash not in seen_hashes:
                    unique_messages.append(message)
                    seen_hashes.add(message_hash)
            
            batch.messages = unique_messages
        
        # Message compression
        if self.config.enable_compression and batch.total_size >= self.config.compression_threshold:
            batch.compression_ratio = await self._calculate_compression_ratio(batch)
        
        return batch

    async def _send_batch(self, batch: MessageBatch) -> None:
        """Send a batch through the WebSocket connection."""
        # This would integrate with the connection pool
        batch_data = batch.get_batch_data()
        logger.debug(f"Sending batch {batch.batch_id} with {len(batch.messages)} messages")

    def _get_message_hash(self, message: Dict[str, Any]) -> str:
        """Generate a hash for message deduplication."""
        # Simple hash based on message content
        message_str = json.dumps(message, sort_keys=True)
        return str(hash(message_str))

    def _update_throughput_metrics(self) -> None:
        """Update throughput metrics."""
        current_time = time.time()
        elapsed_time = current_time - self._start_time
        
        if elapsed_time > 0:
            current_throughput = self._metrics.total_messages / elapsed_time
            self._throughput_history.append(current_throughput)
            self._metrics.messages_per_second = current_throughput
            self._metrics.peak_throughput = max(self._throughput_history) if self._throughput_history else 0

    def _update_batch_metrics(self, batch: MessageBatch, processing_time: float) -> None:
        """Update batch processing metrics."""
        self._metrics.avg_batch_size = (
            (self._metrics.avg_batch_size * (self._metrics.batched_messages - len(batch.messages)) + 
             len(batch.messages)) / self._metrics.batched_messages
        )
        
        self._metrics.avg_processing_time = (
            (self._metrics.avg_processing_time * (self._metrics.batched_messages - len(batch.messages)) + 
             processing_time) / self._metrics.batched_messages
        )
        
        if batch.compression_ratio > 0:
            self._metrics.compression_savings += batch.compression_ratio * batch.total_size

    async def cleanup_cache(self) -> None:
        """Clean up old cache entries."""
        current_time = datetime.utcnow()
        cache_timeout = timedelta(minutes=5)
        
        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if (current_time - timestamp) > cache_timeout
        ]
        
        for key in expired_keys:
            self._message_cache.pop(key, None)
            self._cache_timestamps.pop(key, None)

    async def close(self) -> None:
        """Close the message optimizer and process remaining messages."""
        async with self._lock:
            # Cancel background tasks
            if self._processing_task:
                self._processing_task.cancel()
            if self._batch_processor_task:
                self._batch_processor_task.cancel()
            
            # Process remaining messages
            remaining_messages = []
            while self._message_queue:
                _, _, message = heapq.heappop(self._message_queue)
                remaining_messages.append(message)
            
            if remaining_messages:
                await self._create_auto_batch(remaining_messages)
            
            # Process remaining batches
            while self._batch_queue:
                batch = self._batch_queue.pop(0)
                await self._process_batch(batch)
            
            # Clean up
            self._message_cache.clear()
            self._cache_timestamps.clear()
            self._active_batches.clear()
            
            logger.info("Message optimizer closed")

    def get_metrics(self) -> Dict[str, Any]:
        """Get optimization metrics."""
        self._metrics.last_updated = datetime.utcnow()
        return self._metrics.to_dict()

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            'message_queue_size': len(self._message_queue),
            'batch_queue_size': len(self._batch_queue),
            'active_batches': len(self._active_batches),
            'cache_size': len(self._message_cache),
            'throughput_mps': self._metrics.messages_per_second,
            'peak_throughput_mps': self._metrics.peak_throughput,
        }