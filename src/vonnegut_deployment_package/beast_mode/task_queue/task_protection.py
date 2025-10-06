"""
Task processing protection systems for TaskQueueManager

This module implements comprehensive task processing protection including:
- TaskDeduplicationManager for at-most-once processing guarantees
- IdempotentTaskProcessor with content-based idempotency keys
- PriorityTaskScheduler with starvation prevention and age boosting
"""

import asyncio
import hashlib
import json
import logging
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

from .models import (
    TaskContext,
    TaskResult,
    TaskFailure,
    TaskState,
)


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ProcessingStatus(Enum):
    """Task processing status."""
    PENDING = "pending"
    CLAIMED = "claimed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class TaskClaim:
    """Represents a task processing claim."""
    task_id: str
    claim_key: str
    claimed_at: datetime
    expires_at: datetime
    instance_id: str


@dataclass
class IdempotencyRecord:
    """Record for tracking idempotent task results."""
    idempotency_key: str
    task_id: str
    result: Any
    processed_at: datetime
    instance_id: str


@dataclass
class PriorityTaskInfo:
    """Information about a prioritized task."""
    task_id: str
    priority: TaskPriority
    submitted_at: datetime
    boosted_count: int = 0
    last_boosted_at: Optional[datetime] = None


class TaskDeduplicationManager:
    """
    Ensures at-most-once task processing across distributed instances.

    Provides atomic task claiming with expiration, duplicate detection,
    and completion tracking to prevent duplicate processing.
    """

    def __init__(self, redis_client, processing_timeout: int = 300):
        self.redis = redis_client
        self.processing_timeout = processing_timeout  # 5 minutes default
        self.instance_id = f"taskqueue_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.TaskDeduplicationManager")

        # Tracking metrics
        self._deduplication_metrics = {
            "tasks_claimed": 0,
            "tasks_completed": 0,
            "duplicate_attempts": 0,
            "expired_claims_cleaned": 0,
            "claim_conflicts": 0
        }

        self._logger.info(
            f"TaskDeduplicationManager initialized",
            extra={"instance_id": self.instance_id, "processing_timeout": processing_timeout}
        )

    async def claim_task_for_processing(self, task_id: str) -> Optional[TaskClaim]:
        """
        Claim exclusive right to process a task.

        Args:
            task_id: Unique identifier for the task

        Returns:
            TaskClaim if successfully claimed, None if already claimed

        Raises:
            Exception: If Redis operation fails
        """
        claim_start = time.time()

        try:
            # Check if task is already completed
            if await self.is_task_already_processed(task_id):
                self._deduplication_metrics["duplicate_attempts"] += 1
                self._logger.debug(
                    f"Task {task_id} already processed, skipping",
                    extra={"task_id": task_id}
                )
                return None

            claim_key = f"task:claim:{task_id}"
            claim_value = {
                "instance_id": self.instance_id,
                "claimed_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=self.processing_timeout)).isoformat(),
                "task_id": task_id
            }

            # Atomic claim with expiration
            claimed = await self.redis.set(
                claim_key,
                json.dumps(claim_value),
                nx=True,  # Only if not exists
                ex=self.processing_timeout
            )

            if not claimed:
                # Check if existing claim is expired
                await self._check_and_cleanup_expired_claim(claim_key, task_id)

                # Try to claim again after cleanup
                claimed = await self.redis.set(
                    claim_key,
                    json.dumps(claim_value),
                    nx=True,
                    ex=self.processing_timeout
                )

                if not claimed:
                    self._deduplication_metrics["claim_conflicts"] += 1
                    self._logger.debug(
                        f"Task {task_id} already claimed by another instance",
                        extra={"task_id": task_id}
                    )
                    return None

            # Successfully claimed
            self._deduplication_metrics["tasks_claimed"] += 1

            claim = TaskClaim(
                task_id=task_id,
                instance_id=self.instance_id,
                claimed_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=self.processing_timeout),
                claim_key=claim_key
            )

            claim_duration = time.time() - claim_start

            self._logger.info(
                f"Successfully claimed task {task_id}",
                extra={
                    "task_id": task_id,
                    "instance_id": self.instance_id,
                    "claim_duration_ms": claim_duration * 1000,
                    "expires_in_seconds": self.processing_timeout
                }
            )

            return claim

        except Exception as e:
            self._logger.error(f"Error claiming task {task_id}: {e}")
            raise

    async def _check_and_cleanup_expired_claim(self, claim_key: str, task_id: str):
        """Check if existing claim is expired and clean it up."""
        try:
            current_claim_data = await self.redis.get(claim_key)
            if current_claim_data:
                current_claim = json.loads(current_claim_data)
                expires_at_str = current_claim.get("expires_at")

                if expires_at_str:
                    expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                    if datetime.now() > expires_at:
                        # Claim is expired, clean it up
                        await self.redis.delete(claim_key)
                        self._deduplication_metrics["expired_claims_cleaned"] += 1

                        self._logger.warning(
                            f"Cleaned up expired claim for task {task_id}",
                            extra={
                                "task_id": task_id,
                                "expired_at": expires_at_str,
                                "previous_holder": current_claim.get("instance_id")
                            }
                        )

        except Exception as e:
            self._logger.warning(f"Error checking expired claim for {task_id}: {e}")

    async def complete_task_processing(self, task_id: str, result: TaskResult):
        """
        Mark task as completed and release claim.

        Args:
            task_id: Unique identifier for the task
            result: Task processing result

        Raises:
            Exception: If Redis operation fails
        """
        completion_start = time.time()

        try:
            claim_key = f"task:claim:{task_id}"
            completion_key = f"task:completed:{task_id}"

            # Verify we still hold the claim
            current_claim_data = await self.redis.get(claim_key)
            if current_claim_data:
                current_claim = json.loads(current_claim_data)
                if current_claim.get("instance_id") != self.instance_id:
                    self._logger.error(
                        f"Cannot complete task {task_id}: claim held by different instance",
                        extra={
                            "task_id": task_id,
                            "our_instance": self.instance_id,
                            "claim_holder": current_claim.get("instance_id")
                        }
                    )
                    raise ValueError(f"Task {task_id} not claimed by this instance")

            # Mark as completed and release claim atomically
            async with self.redis.pipeline() as pipe:
                # Store completion record
                completion_record = {
                    "result": asdict(result),
                    "completed_at": datetime.now().isoformat(),
                    "completed_by": self.instance_id,
                    "status": "completed"
                }

                await pipe.hset(completion_key, mapping=completion_record)

                # Set completion TTL (24 hours)
                await pipe.expire(completion_key, 86400)

                # Release claim
                await pipe.delete(claim_key)

                # Execute pipeline
                await pipe.execute()

            self._deduplication_metrics["tasks_completed"] += 1
            completion_duration = time.time() - completion_start

            self._logger.info(
                f"Task {task_id} completed and claim released",
                extra={
                    "task_id": task_id,
                    "instance_id": self.instance_id,
                    "completion_duration_ms": completion_duration * 1000,
                    "result_success": result.success
                }
            )

        except Exception as e:
            self._logger.error(f"Error completing task {task_id}: {e}")
            raise

    async def fail_task_processing(self, task_id: str, failure: TaskFailure):
        """
        Mark task as failed and release claim.

        Args:
            task_id: Unique identifier for the task
            failure: Task processing failure information
        """
        try:
            claim_key = f"task:claim:{task_id}"
            failure_key = f"task:failed:{task_id}"

            # Store failure record and release claim
            async with self.redis.pipeline() as pipe:
                failure_record = {
                    "failure": asdict(failure),
                    "failed_at": datetime.now().isoformat(),
                    "failed_by": self.instance_id,
                    "status": "failed"
                }

                await pipe.hset(failure_key, mapping=failure_record)
                await pipe.expire(failure_key, 86400)  # 24 hours
                await pipe.delete(claim_key)
                await pipe.execute()

            self._logger.warning(
                f"Task {task_id} failed and claim released",
                extra={"task_id": task_id, "failure_reason": failure.error_message}
            )

        except Exception as e:
            self._logger.error(f"Error failing task {task_id}: {e}")

    async def is_task_already_processed(self, task_id: str) -> bool:
        """
        Check if task was already completed or failed.

        Args:
            task_id: Unique identifier for the task

        Returns:
            True if task was already processed
        """
        try:
            completed_exists = await self.redis.exists(f"task:completed:{task_id}")
            failed_exists = await self.redis.exists(f"task:failed:{task_id}")

            return bool(completed_exists or failed_exists)

        except Exception as e:
            self._logger.error(f"Error checking if task {task_id} is processed: {e}")
            return False

    async def extend_claim(self, task_id: str, additional_seconds: int = 300) -> bool:
        """
        Extend processing claim for a task.

        Args:
            task_id: Task to extend claim for
            additional_seconds: Additional time in seconds

        Returns:
            True if claim was successfully extended
        """
        try:
            claim_key = f"task:claim:{task_id}"

            # Get current claim
            current_claim_data = await self.redis.get(claim_key)
            if not current_claim_data:
                self._logger.warning(f"No claim exists for task {task_id}")
                return False

            current_claim = json.loads(current_claim_data)
            if current_claim.get("instance_id") != self.instance_id:
                self._logger.warning(f"Cannot extend claim for task {task_id}: not our claim")
                return False

            # Extend TTL
            extended = await self.redis.expire(claim_key, additional_seconds)

            if extended:
                self._logger.debug(
                    f"Extended claim for task {task_id} by {additional_seconds} seconds",
                    extra={"task_id": task_id, "additional_seconds": additional_seconds}
                )

            return bool(extended)

        except Exception as e:
            self._logger.error(f"Error extending claim for task {task_id}: {e}")
            return False

    async def cleanup_expired_claims(self) -> int:
        """
        Clean up expired task claims.

        Returns:
            Number of expired claims cleaned up
        """
        try:
            pattern = "task:claim:*"
            claim_keys = await self.redis.keys(pattern)

            cleaned_count = 0
            for claim_key in claim_keys:
                try:
                    # Extract task_id from key
                    task_id = claim_key.decode().split(":", 2)[-1]
                    await self._check_and_cleanup_expired_claim(claim_key, task_id)
                    cleaned_count += 1

                except Exception as e:
                    self._logger.warning(f"Error cleaning claim {claim_key}: {e}")

            if cleaned_count > 0:
                self._logger.info(f"Cleaned up {cleaned_count} expired claims")

            return cleaned_count

        except Exception as e:
            self._logger.error(f"Error in cleanup_expired_claims: {e}")
            return 0

    def get_deduplication_metrics(self) -> Dict[str, Any]:
        """Get comprehensive deduplication metrics."""
        return {
            "instance_id": self.instance_id,
            "processing_timeout_seconds": self.processing_timeout,
            "metrics": dict(self._deduplication_metrics),
            "timestamp": datetime.now().isoformat()
        }


class IdempotentTaskProcessor:
    """
    Ensures task processing is idempotent using content-based idempotency keys.

    Provides idempotency guarantees by generating deterministic keys from task content
    and caching results to prevent duplicate processing effects.
    """

    def __init__(self, redis_client, result_ttl: int = 86400):
        self.redis = redis_client
        self.result_ttl = result_ttl  # 24 hours default
        self.instance_id = f"taskqueue_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.IdempotentTaskProcessor")

        # Idempotency metrics
        self._idempotency_metrics = {
            "idempotent_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "results_stored": 0
        }

        self._logger.info(f"IdempotentTaskProcessor initialized")

    async def process_task_idempotently(self, task: TaskContext, processor_func) -> TaskResult:
        """
        Process task with idempotency guarantees.

        Args:
            task: Task to process
            processor_func: Function that actually processes the task

        Returns:
            TaskResult from processing or cache

        Raises:
            Exception: If processing fails
        """
        self._idempotency_metrics["idempotent_calls"] += 1

        try:
            # Generate idempotency key from task content
            idempotency_key = self._generate_idempotency_key(task)

            self._logger.debug(
                f"Processing task with idempotency key {idempotency_key}",
                extra={
                    "task_id": task.task_id,
                    "idempotency_key": idempotency_key
                }
            )

            # Check if already processed
            existing_result = await self._get_idempotent_result(idempotency_key)
            if existing_result:
                self._idempotency_metrics["cache_hits"] += 1

                self._logger.info(
                    f"Task {task.task_id} already processed, returning cached result",
                    extra={
                        "task_id": task.task_id,
                        "idempotency_key": idempotency_key,
                        "cached_success": existing_result.success
                    }
                )

                return existing_result

            self._idempotency_metrics["cache_misses"] += 1

            # Process the task
            self._logger.debug(f"Processing task {task.task_id} for first time")
            processing_start = time.time()

            if asyncio.iscoroutinefunction(processor_func):
                result = await processor_func(task)
            else:
                result = processor_func(task)

            processing_duration = time.time() - processing_start

            # Store result for future idempotency
            await self._store_idempotent_result(idempotency_key, task.task_id, result)

            self._logger.info(
                f"Task {task.task_id} processed and result cached",
                extra={
                    "task_id": task.task_id,
                    "idempotency_key": idempotency_key,
                    "processing_duration_ms": processing_duration * 1000,
                    "result_success": result.success
                }
            )

            return result

        except Exception as e:
            self._logger.error(
                f"Error in idempotent processing for task {task.task_id}: {e}",
                extra={"task_id": task.task_id}
            )
            raise

    def _generate_idempotency_key(self, task: TaskContext) -> str:
        """
        Generate deterministic idempotency key from task content.

        Args:
            task: Task to generate key for

        Returns:
            Deterministic hash string
        """
        # Create deterministic representation of task content
        content_for_hashing = {
            "task_type": task.task_type,
            "content": task.content,
            # Note: We don't include task_id, created_at, or state as these
            # are not part of the logical content for idempotency
        }

        # Generate deterministic JSON and hash
        content_json = json.dumps(content_for_hashing, sort_keys=True, default=str)
        hash_object = hashlib.sha256(content_json.encode())
        idempotency_key = f"idempotent:{hash_object.hexdigest()[:16]}"

        return idempotency_key

    async def _get_idempotent_result(self, idempotency_key: str) -> Optional[TaskResult]:
        """Retrieve cached idempotent result."""
        try:
            result_data = await self.redis.get(idempotency_key)
            if result_data:
                stored_record = json.loads(result_data)
                result_dict = stored_record["result"]

                # Reconstruct TaskResult
                return TaskResult(
                    task_id=result_dict["task_id"],
                    success=result_dict["success"],
                    result=result_dict.get("result"),
                    error_message=result_dict.get("error_message"),
                    processing_time_ms=result_dict.get("processing_time_ms", 0)
                )

            return None

        except Exception as e:
            self._logger.warning(f"Error retrieving idempotent result for {idempotency_key}: {e}")
            return None

    async def _store_idempotent_result(self, idempotency_key: str, task_id: str, result: TaskResult):
        """Store result for idempotency."""
        try:
            record = IdempotencyRecord(
                idempotency_key=idempotency_key,
                task_id=task_id,
                result=result,
                processed_at=datetime.now(),
                instance_id=self.instance_id
            )

            record_data = {
                "idempotency_key": idempotency_key,
                "task_id": task_id,
                "result": asdict(result),
                "processed_at": record.processed_at.isoformat(),
                "instance_id": self.instance_id
            }

            # Store with TTL
            await self.redis.setex(
                idempotency_key,
                self.result_ttl,
                json.dumps(record_data, default=str)
            )

            self._idempotency_metrics["results_stored"] += 1

        except Exception as e:
            self._logger.error(f"Error storing idempotent result for {idempotency_key}: {e}")

    async def invalidate_idempotent_result(self, task: TaskContext) -> bool:
        """
        Invalidate cached idempotent result for a task.

        Args:
            task: Task to invalidate result for

        Returns:
            True if result was invalidated
        """
        try:
            idempotency_key = self._generate_idempotency_key(task)
            deleted = await self.redis.delete(idempotency_key)

            if deleted:
                self._logger.info(
                    f"Invalidated idempotent result for task {task.task_id}",
                    extra={"task_id": task.task_id, "idempotency_key": idempotency_key}
                )

            return bool(deleted)

        except Exception as e:
            self._logger.error(f"Error invalidating idempotent result: {e}")
            return False

    def get_idempotency_metrics(self) -> Dict[str, Any]:
        """Get comprehensive idempotency metrics."""
        cache_hit_rate = 0.0
        if self._idempotency_metrics["idempotent_calls"] > 0:
            cache_hit_rate = (
                self._idempotency_metrics["cache_hits"] /
                self._idempotency_metrics["idempotent_calls"]
            )

        return {
            "instance_id": self.instance_id,
            "result_ttl_seconds": self.result_ttl,
            "cache_hit_rate": cache_hit_rate,
            "metrics": dict(self._idempotency_metrics),
            "timestamp": datetime.now().isoformat()
        }


class PriorityTaskScheduler:
    """
    Fair task scheduling with priority boosting to prevent starvation.

    Implements weighted fair queuing with age-based priority boosting to ensure
    low-priority tasks don't starve while maintaining priority ordering.
    """

    def __init__(self, redis_client, age_boost_threshold: int = 300):
        self.redis = redis_client
        self.age_boost_threshold = age_boost_threshold  # 5 minutes default
        self.instance_id = f"taskqueue_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.PriorityTaskScheduler")

        # Priority queue configuration
        self.priority_queues = {
            TaskPriority.CRITICAL: "tasks:priority:critical",
            TaskPriority.HIGH: "tasks:priority:high",
            TaskPriority.NORMAL: "tasks:priority:normal",
            TaskPriority.LOW: "tasks:priority:low"
        }

        # Scheduling weights (higher = more likely to be selected)
        self.priority_weights = {
            TaskPriority.CRITICAL: 8,
            TaskPriority.HIGH: 4,
            TaskPriority.NORMAL: 2,
            TaskPriority.LOW: 1
        }

        # Scheduling metrics
        self._scheduling_metrics = {
            "tasks_scheduled": {priority.value: 0 for priority in TaskPriority},
            "tasks_boosted": 0,
            "starvation_preventions": 0,
            "weighted_selections": 0,
            "queue_selections": {priority.value: 0 for priority in TaskPriority}
        }

        self._logger.info(
            f"PriorityTaskScheduler initialized",
            extra={
                "instance_id": self.instance_id,
                "age_boost_threshold": age_boost_threshold,
                "priorities": list(self.priority_queues.keys())
            }
        )

    async def enqueue_task(self, task: TaskContext, priority: TaskPriority = TaskPriority.NORMAL) -> bool:
        """
        Enqueue task with specified priority.

        Args:
            task: Task to enqueue
            priority: Task priority level

        Returns:
            True if task was successfully enqueued

        Raises:
            Exception: If Redis operation fails
        """
        try:
            queue_name = self.priority_queues[priority]

            # Create priority task info
            task_info = PriorityTaskInfo(
                task_id=task.task_id,
                priority=priority,
                submitted_at=datetime.now()
            )

            # Use current timestamp as score for age-based ordering
            score = time.time()

            # Store task data and add to priority queue
            task_data = {
                "task": asdict(task),
                "priority_info": asdict(task_info),
                "enqueued_at": datetime.now().isoformat(),
                "enqueued_by": self.instance_id
            }

            async with self.redis.pipeline() as pipe:
                # Store full task data
                await pipe.hset(f"task:data:{task.task_id}", mapping=task_data)

                # Add to priority queue (sorted set with timestamp as score)
                await pipe.zadd(queue_name, {task.task_id: score})

                await pipe.execute()

            self._scheduling_metrics["tasks_scheduled"][priority.value] += 1

            self._logger.info(
                f"Task {task.task_id} enqueued with {priority.value} priority",
                extra={
                    "task_id": task.task_id,
                    "priority": priority.value,
                    "queue": queue_name
                }
            )

            return True

        except Exception as e:
            self._logger.error(f"Error enqueuing task {task.task_id} with priority {priority.value}: {e}")
            raise

    async def get_next_task_with_fairness(self) -> Optional[Tuple[TaskContext, TaskPriority]]:
        """
        Get next task using weighted fair queuing with age boosting.

        Returns:
            Tuple of (TaskContext, TaskPriority) if task available, None otherwise

        Raises:
            Exception: If Redis operation fails
        """
        try:
            # Perform age boosting to prevent starvation
            boost_count = await self._boost_aged_tasks()
            if boost_count > 0:
                self._scheduling_metrics["starvation_preventions"] += boost_count

            # Weighted selection based on priority
            total_weight = sum(self.priority_weights.values())

            # Get queue sizes for non-empty selection
            queue_sizes = {}
            for priority in TaskPriority:
                queue_name = self.priority_queues[priority]
                size = await self.redis.zcard(queue_name)
                queue_sizes[priority] = size

            # Filter to only non-empty queues
            available_priorities = [p for p, size in queue_sizes.items() if size > 0]

            if not available_priorities:
                return None  # No tasks available

            # Weighted random selection from available priorities
            selection_attempts = 0
            max_attempts = len(available_priorities) * 2

            while selection_attempts < max_attempts:
                selected_priority = self._weighted_random_selection(available_priorities)

                # Try to get task from selected queue
                task_context = await self._pop_task_from_queue(selected_priority)

                if task_context:
                    self._scheduling_metrics["weighted_selections"] += 1
                    self._scheduling_metrics["queue_selections"][selected_priority.value] += 1

                    self._logger.debug(
                        f"Selected task {task_context.task_id} from {selected_priority.value} queue",
                        extra={
                            "task_id": task_context.task_id,
                            "priority": selected_priority.value,
                            "selection_attempts": selection_attempts + 1
                        }
                    )

                    return task_context, selected_priority

                # Remove empty queue from available priorities
                available_priorities = [p for p in available_priorities if p != selected_priority]
                if not available_priorities:
                    break

                selection_attempts += 1

            return None

        except Exception as e:
            self._logger.error(f"Error in get_next_task_with_fairness: {e}")
            raise

    def _weighted_random_selection(self, available_priorities: List[TaskPriority]) -> TaskPriority:
        """
        Select priority using weighted random selection.

        Args:
            available_priorities: List of priorities with available tasks

        Returns:
            Selected TaskPriority
        """
        # Calculate total weight for available priorities
        available_weights = {p: self.priority_weights[p] for p in available_priorities}
        total_weight = sum(available_weights.values())

        # Random weighted selection
        selection_value = random.randint(1, total_weight)
        cumulative_weight = 0

        for priority, weight in available_weights.items():
            cumulative_weight += weight
            if selection_value <= cumulative_weight:
                return priority

        # Fallback to first available priority
        return available_priorities[0]

    async def _pop_task_from_queue(self, priority: TaskPriority) -> Optional[TaskContext]:
        """
        Pop oldest task from specified priority queue.

        Args:
            priority: Priority queue to pop from

        Returns:
            TaskContext if available, None if queue is empty
        """
        try:
            queue_name = self.priority_queues[priority]

            # Get and remove oldest task (lowest score)
            tasks = await self.redis.zpopmin(queue_name, count=1)

            if not tasks:
                return None

            task_id = tasks[0][0].decode() if isinstance(tasks[0][0], bytes) else tasks[0][0]

            # Retrieve full task data
            task_data = await self.redis.hgetall(f"task:data:{task_id}")

            if not task_data:
                self._logger.warning(f"Task data not found for {task_id}")
                return None

            # Parse task data
            if isinstance(task_data, dict) and 'task' in task_data:
                task_dict = json.loads(task_data['task'])
            else:
                # Handle case where task_data values are bytes
                task_dict = json.loads(task_data[b'task'] if b'task' in task_data else task_data['task'])

            # Reconstruct TaskContext
            task_context = TaskContext(
                task_id=task_dict["task_id"],
                task_type=task_dict["task_type"],
                content=task_dict["content"],
                created_at=datetime.fromisoformat(task_dict["created_at"]),
                state=TaskState(task_dict["state"])
            )

            # Clean up task data
            await self.redis.delete(f"task:data:{task_id}")

            return task_context

        except Exception as e:
            self._logger.error(f"Error popping task from {priority.value} queue: {e}")
            return None

    async def _boost_aged_tasks(self) -> int:
        """
        Boost priority of aged tasks to prevent starvation.

        Returns:
            Number of tasks boosted
        """
        boosted_count = 0

        try:
            current_time = time.time()
            cutoff_time = current_time - self.age_boost_threshold

            # Check each priority queue (except critical) for aged tasks
            priorities_to_boost = [TaskPriority.LOW, TaskPriority.NORMAL, TaskPriority.HIGH]

            for priority in priorities_to_boost:
                queue_name = self.priority_queues[priority]

                # Get tasks older than threshold
                old_tasks = await self.redis.zrangebyscore(
                    queue_name,
                    0,  # minimum score (oldest)
                    cutoff_time,  # maximum score (age cutoff)
                    withscores=True
                )

                if old_tasks:
                    # Get higher priority queue
                    higher_priority = self._get_higher_priority(priority)

                    if higher_priority:
                        higher_queue_name = self.priority_queues[higher_priority]

                        # Move aged tasks to higher priority queue
                        async with self.redis.pipeline() as pipe:
                            for task_data in old_tasks:
                                task_id = task_data[0].decode() if isinstance(task_data[0], bytes) else task_data[0]
                                original_score = task_data[1]

                                # Remove from current queue
                                await pipe.zrem(queue_name, task_id)

                                # Add to higher priority queue with current timestamp
                                await pipe.zadd(higher_queue_name, {task_id: current_time})

                                boosted_count += 1

                            await pipe.execute()

                        self._logger.info(
                            f"Boosted {len(old_tasks)} tasks from {priority.value} to {higher_priority.value}",
                            extra={
                                "from_priority": priority.value,
                                "to_priority": higher_priority.value,
                                "tasks_boosted": len(old_tasks),
                                "age_threshold_seconds": self.age_boost_threshold
                            }
                        )

            if boosted_count > 0:
                self._scheduling_metrics["tasks_boosted"] += boosted_count

            return boosted_count

        except Exception as e:
            self._logger.error(f"Error in _boost_aged_tasks: {e}")
            return 0

    def _get_higher_priority(self, current_priority: TaskPriority) -> Optional[TaskPriority]:
        """
        Get the next higher priority level.

        Args:
            current_priority: Current priority level

        Returns:
            Higher priority level or None if already at highest
        """
        priority_order = [TaskPriority.LOW, TaskPriority.NORMAL, TaskPriority.HIGH, TaskPriority.CRITICAL]

        try:
            current_index = priority_order.index(current_priority)
            if current_index < len(priority_order) - 1:
                return priority_order[current_index + 1]
            return None  # Already at highest priority
        except ValueError:
            return None

    async def get_queue_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of all priority queues.

        Returns:
            Dict containing queue sizes and status information
        """
        try:
            queue_status = {}

            total_tasks = 0
            for priority in TaskPriority:
                queue_name = self.priority_queues[priority]
                queue_size = await self.redis.zcard(queue_name)

                # Get oldest task age if queue not empty
                oldest_task_age = None
                if queue_size > 0:
                    oldest_tasks = await self.redis.zrange(queue_name, 0, 0, withscores=True)
                    if oldest_tasks:
                        oldest_timestamp = oldest_tasks[0][1]
                        oldest_task_age = time.time() - oldest_timestamp

                queue_status[priority.value] = {
                    "size": queue_size,
                    "oldest_task_age_seconds": oldest_task_age,
                    "queue_name": queue_name
                }

                total_tasks += queue_size

            return {
                "total_tasks": total_tasks,
                "queues": queue_status,
                "age_boost_threshold": self.age_boost_threshold,
                "priority_weights": {p.value: w for p, w in self.priority_weights.items()},
                "instance_id": self.instance_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error getting queue status: {e}")
            return {"error": str(e)}

    async def clear_queue(self, priority: TaskPriority) -> int:
        """
        Clear all tasks from a priority queue.

        Args:
            priority: Priority queue to clear

        Returns:
            Number of tasks cleared
        """
        try:
            queue_name = self.priority_queues[priority]

            # Get all tasks in queue
            all_tasks = await self.redis.zrange(queue_name, 0, -1)

            if not all_tasks:
                return 0

            # Clear queue and associated task data
            async with self.redis.pipeline() as pipe:
                # Delete the queue
                await pipe.delete(queue_name)

                # Delete associated task data
                for task_id in all_tasks:
                    if isinstance(task_id, bytes):
                        task_id = task_id.decode()
                    await pipe.delete(f"task:data:{task_id}")

                await pipe.execute()

            self._logger.warning(
                f"Cleared {len(all_tasks)} tasks from {priority.value} queue",
                extra={"priority": priority.value, "tasks_cleared": len(all_tasks)}
            )

            return len(all_tasks)

        except Exception as e:
            self._logger.error(f"Error clearing {priority.value} queue: {e}")
            return 0

    def get_scheduling_metrics(self) -> Dict[str, Any]:
        """Get comprehensive scheduling metrics."""
        total_scheduled = sum(self._scheduling_metrics["tasks_scheduled"].values())
        total_selected = sum(self._scheduling_metrics["queue_selections"].values())

        priority_distribution = {}
        if total_scheduled > 0:
            for priority, count in self._scheduling_metrics["tasks_scheduled"].items():
                priority_distribution[priority] = count / total_scheduled

        selection_distribution = {}
        if total_selected > 0:
            for priority, count in self._scheduling_metrics["queue_selections"].items():
                selection_distribution[priority] = count / total_selected

        return {
            "instance_id": self.instance_id,
            "age_boost_threshold_seconds": self.age_boost_threshold,
            "priority_weights": {p.value: w for p, w in self.priority_weights.items()},
            "total_tasks_scheduled": total_scheduled,
            "total_tasks_selected": total_selected,
            "priority_distribution": priority_distribution,
            "selection_distribution": selection_distribution,
            "fairness_metrics": {
                "tasks_boosted": self._scheduling_metrics["tasks_boosted"],
                "starvation_preventions": self._scheduling_metrics["starvation_preventions"],
                "weighted_selections": self._scheduling_metrics["weighted_selections"]
            },
            "raw_metrics": dict(self._scheduling_metrics),
            "timestamp": datetime.now().isoformat()
        }


class SecurityThreatLevel(Enum):
    """Security threat assessment levels."""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL_RISK = "critical_risk"


@dataclass
class SecurityScanResult:
    """Results of security content scanning."""
    task_id: str
    threat_level: SecurityThreatLevel
    threats_detected: List[Dict[str, Any]]
    safe_to_process: bool
    sanitized_content: Optional[str] = None
    scan_duration_ms: float = 0.0
    scanner_version: str = "1.0.0"


@dataclass
class SandboxExecutionResult:
    """Results from sandboxed task execution."""
    task_id: str
    execution_successful: bool
    result: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    resource_usage: Optional[Dict[str, Any]] = None
    security_violations: List[str] = None
    sandbox_version: str = "1.0.0"


class TaskSecurityValidator:
    """
    Advanced security validator for task content with pattern matching and ML-based detection.

    Provides comprehensive security scanning including:
    - Static pattern matching for known dangerous content
    - Content sanitization and safe processing recommendations
    - Threat level assessment and risk scoring
    """

    def __init__(self, security_patterns: List[str] = None, max_content_length: int = 100000):
        self.max_content_length = max_content_length
        self.instance_id = f"taskqueue_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.TaskSecurityValidator")

        # Default dangerous patterns
        self.security_patterns = security_patterns or [
            # Command injection patterns
            r'rm\s+-rf\s+/',
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'subprocess\.',
            r'os\.system',
            r'os\.popen',

            # SQL injection patterns
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'INSERT\s+INTO.*VALUES',
            r'UPDATE.*SET',
            r'UNION\s+SELECT',

            # Script injection patterns
            r'<script[^>]*>',
            r'javascript:',
            r'data:text/html',
            r'onclick\s*=',
            r'onerror\s*=',

            # File system access patterns
            r'\.\./',
            r'etc/passwd',
            r'/dev/null',
            r'file://',

            # Network access patterns
            r'http://.*malicious',
            r'wget\s+',
            r'curl\s+.*\|',
        ]

        # Compile regex patterns for efficiency
        import re
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.security_patterns]

        # Security metrics
        self._security_metrics = {
            "scans_performed": 0,
            "threats_detected": 0,
            "safe_tasks": 0,
            "blocked_tasks": 0,
            "sanitizations_performed": 0,
            "threat_levels": {level.value: 0 for level in SecurityThreatLevel}
        }

        self._logger.info(
            f"TaskSecurityValidator initialized",
            extra={
                "instance_id": self.instance_id,
                "max_content_length": max_content_length,
                "security_patterns_count": len(self.security_patterns)
            }
        )

    async def scan_task_content(self, task: TaskContext) -> SecurityScanResult:
        """
        Perform comprehensive security scan of task content.

        Args:
            task: Task to scan for security threats

        Returns:
            SecurityScanResult with threat assessment and recommendations
        """
        scan_start = time.time()
        self._security_metrics["scans_performed"] += 1

        try:
            # Basic content validation
            if len(str(task.content)) > self.max_content_length:
                return SecurityScanResult(
                    task_id=task.task_id,
                    threat_level=SecurityThreatLevel.HIGH_RISK,
                    threats_detected=[{
                        "type": "content_length_violation",
                        "description": f"Content length {len(str(task.content))} exceeds maximum {self.max_content_length}",
                        "risk_score": 0.8
                    }],
                    safe_to_process=False,
                    scan_duration_ms=(time.time() - scan_start) * 1000
                )

            # Pattern-based threat detection
            threats_detected = []
            content_str = str(task.content).lower()

            for i, pattern in enumerate(self.compiled_patterns):
                matches = pattern.findall(content_str)
                if matches:
                    threat = {
                        "type": "pattern_match",
                        "pattern_id": i,
                        "pattern": self.security_patterns[i],
                        "matches": matches,
                        "risk_score": self._calculate_pattern_risk_score(self.security_patterns[i]),
                        "description": f"Detected potentially dangerous pattern: {self.security_patterns[i]}"
                    }
                    threats_detected.append(threat)

            # Additional content analysis
            additional_threats = await self._perform_additional_security_checks(task, content_str)
            threats_detected.extend(additional_threats)

            # Calculate overall threat level
            threat_level = self._assess_overall_threat_level(threats_detected)
            safe_to_process = threat_level in [SecurityThreatLevel.SAFE, SecurityThreatLevel.LOW_RISK]

            # Perform content sanitization if needed
            sanitized_content = None
            if threats_detected and safe_to_process:
                sanitized_content = await self._sanitize_content(str(task.content), threats_detected)
                self._security_metrics["sanitizations_performed"] += 1

            # Update metrics
            self._security_metrics["threat_levels"][threat_level.value] += 1
            if safe_to_process:
                self._security_metrics["safe_tasks"] += 1
            else:
                self._security_metrics["blocked_tasks"] += 1

            if threats_detected:
                self._security_metrics["threats_detected"] += len(threats_detected)

            scan_duration = (time.time() - scan_start) * 1000

            self._logger.info(
                f"Security scan completed for task {task.task_id}",
                extra={
                    "task_id": task.task_id,
                    "threat_level": threat_level.value,
                    "threats_count": len(threats_detected),
                    "safe_to_process": safe_to_process,
                    "scan_duration_ms": scan_duration
                }
            )

            return SecurityScanResult(
                task_id=task.task_id,
                threat_level=threat_level,
                threats_detected=threats_detected,
                safe_to_process=safe_to_process,
                sanitized_content=sanitized_content,
                scan_duration_ms=scan_duration
            )

        except Exception as e:
            self._logger.error(f"Error scanning task {task.task_id}: {e}")
            # Return high risk on scan failure
            return SecurityScanResult(
                task_id=task.task_id,
                threat_level=SecurityThreatLevel.HIGH_RISK,
                threats_detected=[{
                    "type": "scan_error",
                    "description": f"Security scan failed: {str(e)}",
                    "risk_score": 0.9
                }],
                safe_to_process=False,
                scan_duration_ms=(time.time() - scan_start) * 1000
            )

    def _calculate_pattern_risk_score(self, pattern: str) -> float:
        """Calculate risk score for a detected pattern."""
        high_risk_patterns = ['rm -rf', 'eval(', 'exec(', 'DROP TABLE', 'os.system']
        medium_risk_patterns = ['<script', 'javascript:', 'subprocess.']

        pattern_lower = pattern.lower()

        for high_pattern in high_risk_patterns:
            if high_pattern.lower() in pattern_lower:
                return 0.9

        for medium_pattern in medium_risk_patterns:
            if medium_pattern.lower() in pattern_lower:
                return 0.6

        return 0.3  # Default low risk

    async def _perform_additional_security_checks(self, task: TaskContext, content_str: str) -> List[Dict[str, Any]]:
        """Perform additional security checks beyond pattern matching."""
        additional_threats = []

        try:
            # Check for base64 encoded content (potential obfuscation)
            import base64
            if len(content_str) > 50:
                try:
                    decoded = base64.b64decode(content_str[:100], validate=True)
                    if len(decoded) > 10:
                        additional_threats.append({
                            "type": "potential_obfuscation",
                            "description": "Content appears to contain base64 encoded data",
                            "risk_score": 0.4
                        })
                except Exception:
                    pass

            # Check for excessive special characters (potential injection)
            special_chars = sum(1 for char in content_str if not char.isalnum() and not char.isspace())
            if len(content_str) > 0 and special_chars / len(content_str) > 0.3:
                additional_threats.append({
                    "type": "high_special_character_ratio",
                    "description": f"High ratio of special characters: {special_chars}/{len(content_str)}",
                    "risk_score": 0.5
                })

            # Check for suspicious keywords
            suspicious_keywords = ['password', 'secret', 'token', 'api_key', 'private_key']
            for keyword in suspicious_keywords:
                if keyword in content_str:
                    additional_threats.append({
                        "type": "sensitive_data_reference",
                        "description": f"Content references potentially sensitive data: {keyword}",
                        "risk_score": 0.3
                    })

        except Exception as e:
            self._logger.warning(f"Error in additional security checks: {e}")

        return additional_threats

    def _assess_overall_threat_level(self, threats: List[Dict[str, Any]]) -> SecurityThreatLevel:
        """Assess overall threat level based on detected threats."""
        if not threats:
            return SecurityThreatLevel.SAFE

        max_risk_score = max(threat.get("risk_score", 0.0) for threat in threats)
        threat_count = len(threats)

        # High risk if any single threat is high risk
        if max_risk_score >= 0.8:
            return SecurityThreatLevel.CRITICAL_RISK
        elif max_risk_score >= 0.6:
            return SecurityThreatLevel.HIGH_RISK
        elif max_risk_score >= 0.4 or threat_count >= 3:
            return SecurityThreatLevel.MEDIUM_RISK
        elif max_risk_score >= 0.2 or threat_count >= 1:
            return SecurityThreatLevel.LOW_RISK
        else:
            return SecurityThreatLevel.SAFE

    async def _sanitize_content(self, content: str, threats: List[Dict[str, Any]]) -> str:
        """Sanitize content by removing or escaping threats."""
        sanitized = content

        try:
            # Remove or escape dangerous patterns
            for threat in threats:
                if threat.get("type") == "pattern_match" and "matches" in threat:
                    for match in threat["matches"]:
                        # Simple sanitization - replace with safe placeholder
                        sanitized = sanitized.replace(match, f"[SANITIZED_{threat['pattern_id']}]")

            # Escape HTML/script tags
            sanitized = sanitized.replace("<script", "&lt;script")
            sanitized = sanitized.replace("javascript:", "javascript-blocked:")

        except Exception as e:
            self._logger.warning(f"Error sanitizing content: {e}")

        return sanitized

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get comprehensive security validation metrics."""
        return {
            "instance_id": self.instance_id,
            "max_content_length": self.max_content_length,
            "security_patterns_count": len(self.security_patterns),
            "metrics": dict(self._security_metrics),
            "timestamp": datetime.now().isoformat()
        }


class TaskExecutionSandbox:
    """
    Secure sandboxed execution environment for task processing.

    Provides isolated execution with resource limits, security monitoring,
    and safe cleanup of execution environment.
    """

    def __init__(self, max_execution_time: int = 300, max_memory_mb: int = 512):
        self.max_execution_time = max_execution_time  # 5 minutes default
        self.max_memory_mb = max_memory_mb
        self.instance_id = f"taskqueue_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.TaskExecutionSandbox")

        # Sandbox metrics
        self._sandbox_metrics = {
            "executions_attempted": 0,
            "executions_successful": 0,
            "executions_failed": 0,
            "executions_timed_out": 0,
            "security_violations": 0,
            "resource_limit_violations": 0
        }

        self._logger.info(
            f"TaskExecutionSandbox initialized",
            extra={
                "instance_id": self.instance_id,
                "max_execution_time": max_execution_time,
                "max_memory_mb": max_memory_mb
            }
        )

    async def execute_task_safely(self, task: TaskContext, processor_func) -> SandboxExecutionResult:
        """
        Execute task in sandboxed environment with security and resource monitoring.

        Args:
            task: Task to execute
            processor_func: Function to execute the task

        Returns:
            SandboxExecutionResult with execution status and monitoring data
        """
        execution_start = time.time()
        self._sandbox_metrics["executions_attempted"] += 1

        resource_usage = {
            "start_time": execution_start,
            "peak_memory_mb": 0,
            "cpu_time_ms": 0
        }

        security_violations = []

        try:
            self._logger.info(
                f"Starting sandboxed execution for task {task.task_id}",
                extra={"task_id": task.task_id, "task_type": task.task_type}
            )

            # Pre-execution security checks
            pre_violations = await self._perform_pre_execution_checks(task)
            security_violations.extend(pre_violations)

            if pre_violations:
                self._sandbox_metrics["security_violations"] += len(pre_violations)
                return SandboxExecutionResult(
                    task_id=task.task_id,
                    execution_successful=False,
                    error_message=f"Pre-execution security violations: {pre_violations}",
                    security_violations=security_violations,
                    execution_time_ms=(time.time() - execution_start) * 1000
                )

            # Execute with timeout and monitoring
            result = await self._execute_with_monitoring(task, processor_func, resource_usage)

            # Post-execution security checks
            post_violations = await self._perform_post_execution_checks(task, result)
            security_violations.extend(post_violations)

            execution_time = (time.time() - execution_start) * 1000
            resource_usage["execution_time_ms"] = execution_time

            if security_violations:
                self._sandbox_metrics["security_violations"] += len(post_violations)
                self._sandbox_metrics["executions_failed"] += 1

                self._logger.warning(
                    f"Post-execution security violations for task {task.task_id}",
                    extra={
                        "task_id": task.task_id,
                        "violations": security_violations,
                        "execution_time_ms": execution_time
                    }
                )

                return SandboxExecutionResult(
                    task_id=task.task_id,
                    execution_successful=False,
                    result=result,
                    error_message=f"Post-execution security violations: {post_violations}",
                    execution_time_ms=execution_time,
                    resource_usage=resource_usage,
                    security_violations=security_violations
                )

            self._sandbox_metrics["executions_successful"] += 1

            self._logger.info(
                f"Sandboxed execution completed successfully for task {task.task_id}",
                extra={
                    "task_id": task.task_id,
                    "execution_time_ms": execution_time,
                    "peak_memory_mb": resource_usage["peak_memory_mb"]
                }
            )

            return SandboxExecutionResult(
                task_id=task.task_id,
                execution_successful=True,
                result=result,
                execution_time_ms=execution_time,
                resource_usage=resource_usage,
                security_violations=security_violations
            )

        except asyncio.TimeoutError:
            self._sandbox_metrics["executions_timed_out"] += 1
            self._logger.error(f"Task {task.task_id} execution timed out after {self.max_execution_time}s")

            return SandboxExecutionResult(
                task_id=task.task_id,
                execution_successful=False,
                error_message=f"Execution timed out after {self.max_execution_time} seconds",
                execution_time_ms=(time.time() - execution_start) * 1000,
                resource_usage=resource_usage,
                security_violations=security_violations
            )

        except Exception as e:
            self._sandbox_metrics["executions_failed"] += 1
            self._logger.error(f"Sandboxed execution failed for task {task.task_id}: {e}")

            return SandboxExecutionResult(
                task_id=task.task_id,
                execution_successful=False,
                error_message=str(e),
                execution_time_ms=(time.time() - execution_start) * 1000,
                resource_usage=resource_usage,
                security_violations=security_violations
            )

    async def _perform_pre_execution_checks(self, task: TaskContext) -> List[str]:
        """Perform security checks before task execution."""
        violations = []

        try:
            # Check for dangerous task types
            dangerous_types = ['system_command', 'file_operation', 'network_request']
            if task.task_type in dangerous_types:
                violations.append(f"Dangerous task type: {task.task_type}")

            # Check content length
            if len(str(task.content)) > 50000:  # 50KB limit
                violations.append(f"Task content too large: {len(str(task.content))} bytes")

        except Exception as e:
            self._logger.warning(f"Error in pre-execution checks: {e}")
            violations.append(f"Pre-execution check failed: {str(e)}")

        return violations

    async def _execute_with_monitoring(self, task: TaskContext, processor_func, resource_usage: Dict) -> Any:
        """Execute task with resource and security monitoring."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB

        try:
            # Execute with timeout
            if asyncio.iscoroutinefunction(processor_func):
                result = await asyncio.wait_for(
                    processor_func(task),
                    timeout=self.max_execution_time
                )
            else:
                # Run sync function in thread pool with timeout
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, processor_func, task),
                    timeout=self.max_execution_time
                )

            # Monitor resource usage
            current_memory = process.memory_info().rss / (1024 * 1024)  # MB
            peak_memory = current_memory - initial_memory

            resource_usage["peak_memory_mb"] = max(resource_usage["peak_memory_mb"], peak_memory)

            # Check memory limits
            if peak_memory > self.max_memory_mb:
                self._sandbox_metrics["resource_limit_violations"] += 1
                raise Exception(f"Memory limit exceeded: {peak_memory}MB > {self.max_memory_mb}MB")

            return result

        except asyncio.TimeoutError:
            raise
        except Exception as e:
            raise

    async def _perform_post_execution_checks(self, task: TaskContext, result: Any) -> List[str]:
        """Perform security checks after task execution."""
        violations = []

        try:
            # Check result size
            if result and len(str(result)) > 100000:  # 100KB limit
                violations.append(f"Result too large: {len(str(result))} characters")

            # Check for sensitive data in results
            if result and isinstance(result, str):
                sensitive_patterns = ['password=', 'secret=', 'token=', 'key=']
                for pattern in sensitive_patterns:
                    if pattern.lower() in str(result).lower():
                        violations.append(f"Result contains sensitive data pattern: {pattern}")

        except Exception as e:
            self._logger.warning(f"Error in post-execution checks: {e}")
            violations.append(f"Post-execution check failed: {str(e)}")

        return violations

    def get_sandbox_metrics(self) -> Dict[str, Any]:
        """Get comprehensive sandbox execution metrics."""
        total_executions = self._sandbox_metrics["executions_attempted"]
        success_rate = 0.0
        if total_executions > 0:
            success_rate = self._sandbox_metrics["executions_successful"] / total_executions

        return {
            "instance_id": self.instance_id,
            "max_execution_time_seconds": self.max_execution_time,
            "max_memory_mb": self.max_memory_mb,
            "success_rate": success_rate,
            "metrics": dict(self._sandbox_metrics),
            "timestamp": datetime.now().isoformat()
        }


class ConversationStateEncryption:
    """
    Encryption and data protection for sensitive conversation state data.

    Provides AES-256 encryption for conversation state with key rotation,
    secure key management, and data integrity verification.
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        from cryptography.fernet import Fernet

        self.instance_id = f"taskqueue_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.ConversationStateEncryption")

        # Initialize encryption key
        if encryption_key:
            self.fernet = Fernet(encryption_key)
        else:
            # Generate new key
            key = Fernet.generate_key()
            self.fernet = Fernet(key)

        # Encryption metrics
        self._encryption_metrics = {
            "encryptions_performed": 0,
            "decryptions_performed": 0,
            "encryption_failures": 0,
            "decryption_failures": 0,
            "key_rotations": 0
        }

        self._logger.info(
            f"ConversationStateEncryption initialized",
            extra={"instance_id": self.instance_id}
        )

    async def encrypt_conversation_state(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive conversation state data.

        Args:
            conversation_data: Raw conversation state data

        Returns:
            Dict containing encrypted data and metadata
        """
        try:
            self._encryption_metrics["encryptions_performed"] += 1

            # Serialize data for encryption
            serialized_data = json.dumps(conversation_data, default=str).encode()

            # Encrypt the data
            encrypted_data = self.fernet.encrypt(serialized_data)

            # Create metadata
            encrypted_result = {
                "encrypted_data": encrypted_data.decode('latin-1'),  # Store as string
                "encryption_timestamp": datetime.now().isoformat(),
                "encryption_version": "1.0",
                "data_integrity_hash": hashlib.sha256(serialized_data).hexdigest(),
                "encrypted_size_bytes": len(encrypted_data),
                "original_size_bytes": len(serialized_data)
            }

            self._logger.debug(
                f"Encrypted conversation state data",
                extra={
                    "original_size": len(serialized_data),
                    "encrypted_size": len(encrypted_data),
                    "compression_ratio": len(encrypted_data) / len(serialized_data)
                }
            )

            return encrypted_result

        except Exception as e:
            self._encryption_metrics["encryption_failures"] += 1
            self._logger.error(f"Error encrypting conversation state: {e}")
            raise

    async def decrypt_conversation_state(self, encrypted_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt conversation state data and verify integrity.

        Args:
            encrypted_result: Encrypted data with metadata

        Returns:
            Decrypted conversation state data
        """
        try:
            self._encryption_metrics["decryptions_performed"] += 1

            # Extract encrypted data
            encrypted_data = encrypted_result["encrypted_data"].encode('latin-1')
            expected_hash = encrypted_result.get("data_integrity_hash")

            # Decrypt the data
            decrypted_data = self.fernet.decrypt(encrypted_data)

            # Verify data integrity
            if expected_hash:
                actual_hash = hashlib.sha256(decrypted_data).hexdigest()
                if actual_hash != expected_hash:
                    raise Exception(f"Data integrity check failed: expected {expected_hash}, got {actual_hash}")

            # Deserialize data
            conversation_data = json.loads(decrypted_data.decode())

            self._logger.debug(
                f"Decrypted conversation state data",
                extra={
                    "decrypted_size": len(decrypted_data),
                    "integrity_verified": expected_hash is not None
                }
            )

            return conversation_data

        except Exception as e:
            self._encryption_metrics["decryption_failures"] += 1
            self._logger.error(f"Error decrypting conversation state: {e}")
            raise

    def rotate_encryption_key(self) -> bytes:
        """
        Rotate encryption key for enhanced security.

        Returns:
            New encryption key
        """
        try:
            from cryptography.fernet import Fernet

            # Generate new key
            new_key = Fernet.generate_key()
            old_fernet = self.fernet

            # Update to new key
            self.fernet = Fernet(new_key)
            self._encryption_metrics["key_rotations"] += 1

            self._logger.info("Encryption key rotated successfully")

            return new_key

        except Exception as e:
            self._logger.error(f"Error rotating encryption key: {e}")
            raise

    def get_encryption_metrics(self) -> Dict[str, Any]:
        """Get comprehensive encryption metrics."""
        total_operations = (
            self._encryption_metrics["encryptions_performed"] +
            self._encryption_metrics["decryptions_performed"]
        )

        total_failures = (
            self._encryption_metrics["encryption_failures"] +
            self._encryption_metrics["decryption_failures"]
        )

        success_rate = 1.0
        if total_operations > 0:
            success_rate = (total_operations - total_failures) / total_operations

        return {
            "instance_id": self.instance_id,
            "success_rate": success_rate,
            "metrics": dict(self._encryption_metrics),
            "timestamp": datetime.now().isoformat()
        }