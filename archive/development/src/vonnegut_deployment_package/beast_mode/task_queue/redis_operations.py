"""
Redis task queue operations using Redis Streams.

This module implements Redis-based task queue operations including
enqueue, dequeue, peek operations with task validation and security.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import asdict
import re

from .models import (
    TaskContext,
    TaskState,
    QueueConfig,
    SecuritySettings,
    TaskResult,
    TaskFailure,
)


class TaskValidationError(Exception):
    """Raised when task validation fails."""
    pass


class RedisTaskQueueOperations:
    """Redis-based task queue operations using Redis Streams."""
    
    def __init__(self, redis_client, security_settings: SecuritySettings):
        self.redis = redis_client
        self.security = security_settings
        self._logger = logging.getLogger(f"{__name__}.RedisTaskQueueOperations")
        
        # Task validation patterns
        self._dangerous_patterns = [re.compile(pattern) for pattern in security_settings.dangerous_patterns]
    
    async def enqueue_task(self, queue_name: str, task: TaskContext) -> bool:
        """Enqueue a task to the specified Redis Stream queue."""
        try:
            # Validate task before enqueuing
            if not await self._validate_task_security(task):
                raise TaskValidationError(f"Task {task.task_id} failed security validation")
            
            # Prepare task data for Redis Stream
            task_data = self._serialize_task(task)
            
            # Add to Redis Stream
            stream_key = f"task_queue:{queue_name}"
            message_id = await self.redis.xadd(stream_key, task_data)
            
            # Update task metadata
            task.task_metadata["redis_message_id"] = message_id.decode() if isinstance(message_id, bytes) else str(message_id)
            task.task_metadata["queue_name"] = queue_name
            task.task_metadata["enqueued_at"] = datetime.now().isoformat()
            
            self._logger.info(
                f"Task enqueued successfully: {task.task_id}",
                extra={
                    "task_id": task.task_id,
                    "queue_name": queue_name,
                    "message_id": task.task_metadata["redis_message_id"]
                }
            )
            
            return True
            
        except Exception as e:
            self._logger.error(
                f"Failed to enqueue task {task.task_id}: {e}",
                extra={
                    "task_id": task.task_id,
                    "queue_name": queue_name
                }
            )
            return False
    
    async def dequeue_task(self, queue_name: str, consumer_group: str, consumer_name: str, timeout_ms: int = 1000) -> Optional[TaskContext]:
        """Dequeue a task from the specified Redis Stream queue."""
        try:
            stream_key = f"task_queue:{queue_name}"
            
            # Ensure consumer group exists
            await self._ensure_consumer_group(stream_key, consumer_group)
            
            # Read from stream using consumer group
            messages = await self.redis.xreadgroup(
                consumer_group,
                consumer_name,
                {stream_key: '>'},
                count=1,
                block=timeout_ms
            )
            
            if not messages or not messages[0][1]:
                return None
            
            # Extract message data
            stream_name, message_list = messages[0]
            message_id, fields = message_list[0]
            
            # Deserialize task
            task = self._deserialize_task(fields)
            task.task_metadata["redis_message_id"] = message_id.decode() if isinstance(message_id, bytes) else str(message_id)
            task.task_metadata["consumer_group"] = consumer_group
            task.task_metadata["consumer_name"] = consumer_name
            task.task_metadata["dequeued_at"] = datetime.now().isoformat()
            
            # Update task state
            task.task_state = TaskState.CLAIMED
            task.claimed_at = datetime.now()
            
            self._logger.info(
                f"Task dequeued successfully: {task.task_id}",
                extra={
                    "task_id": task.task_id,
                    "queue_name": queue_name,
                    "consumer_group": consumer_group,
                    "consumer_name": consumer_name,
                    "message_id": task.task_metadata["redis_message_id"]
                }
            )
            
            return task
            
        except Exception as e:
            self._logger.error(
                f"Failed to dequeue task from {queue_name}: {e}",
                extra={
                    "queue_name": queue_name,
                    "consumer_group": consumer_group,
                    "consumer_name": consumer_name
                }
            )
            return None
    
    async def peek_queue(self, queue_name: str, count: int = 10) -> List[TaskContext]:
        """Peek at tasks in the queue without removing them."""
        try:
            stream_key = f"task_queue:{queue_name}"
            
            # Read latest messages without consuming
            messages = await self.redis.xrevrange(stream_key, count=count)
            
            tasks = []
            for message_id, fields in messages:
                try:
                    task = self._deserialize_task(fields)
                    task.task_metadata["redis_message_id"] = message_id.decode() if isinstance(message_id, bytes) else str(message_id)
                    tasks.append(task)
                except Exception as e:
                    self._logger.warning(f"Failed to deserialize task from message {message_id}: {e}")
            
            self._logger.debug(
                f"Peeked at {len(tasks)} tasks in queue {queue_name}",
                extra={"queue_name": queue_name, "task_count": len(tasks)}
            )
            
            return tasks
            
        except Exception as e:
            self._logger.error(
                f"Failed to peek queue {queue_name}: {e}",
                extra={"queue_name": queue_name}
            )
            return []
    
    async def acknowledge_task(self, queue_name: str, consumer_group: str, message_id: str) -> bool:
        """Acknowledge task completion and remove from pending list."""
        try:
            stream_key = f"task_queue:{queue_name}"
            
            # Acknowledge the message
            result = await self.redis.xack(stream_key, consumer_group, message_id)
            
            if result > 0:
                self._logger.info(
                    f"Task acknowledged successfully",
                    extra={
                        "queue_name": queue_name,
                        "consumer_group": consumer_group,
                        "message_id": message_id
                    }
                )
                return True
            else:
                self._logger.warning(
                    f"Task acknowledgment failed - message not found",
                    extra={
                        "queue_name": queue_name,
                        "consumer_group": consumer_group,
                        "message_id": message_id
                    }
                )
                return False
                
        except Exception as e:
            self._logger.error(
                f"Failed to acknowledge task: {e}",
                extra={
                    "queue_name": queue_name,
                    "consumer_group": consumer_group,
                    "message_id": message_id
                }
            )
            return False
    
    async def get_queue_info(self, queue_name: str) -> Dict[str, Any]:
        """Get information about the queue."""
        try:
            stream_key = f"task_queue:{queue_name}"
            
            # Get stream info
            stream_info = await self.redis.xinfo_stream(stream_key)
            
            # Get consumer group info
            try:
                groups_info = await self.redis.xinfo_groups(stream_key)
            except Exception:
                groups_info = []
            
            queue_info = {
                "queue_name": queue_name,
                "stream_key": stream_key,
                "length": stream_info.get(b'length', 0),
                "first_entry_id": stream_info.get(b'first-entry', [b'0-0'])[0].decode() if stream_info.get(b'first-entry') else None,
                "last_entry_id": stream_info.get(b'last-entry', [b'0-0'])[0].decode() if stream_info.get(b'last-entry') else None,
                "consumer_groups": []
            }
            
            # Process consumer groups
            for group_info in groups_info:
                group_data = {
                    "name": group_info.get(b'name', b'').decode(),
                    "consumers": group_info.get(b'consumers', 0),
                    "pending": group_info.get(b'pending', 0),
                    "last_delivered_id": group_info.get(b'last-delivered-id', b'0-0').decode()
                }
                queue_info["consumer_groups"].append(group_data)
            
            return queue_info
            
        except Exception as e:
            self._logger.error(f"Failed to get queue info for {queue_name}: {e}")
            return {
                "queue_name": queue_name,
                "error": str(e),
                "length": 0,
                "consumer_groups": []
            }
    
    async def get_pending_tasks(self, queue_name: str, consumer_group: str, consumer_name: str = None) -> List[Dict[str, Any]]:
        """Get pending tasks for a consumer group or specific consumer."""
        try:
            stream_key = f"task_queue:{queue_name}"
            
            if consumer_name:
                # Get pending tasks for specific consumer
                pending_info = await self.redis.xpending_range(
                    stream_key, consumer_group, '-', '+', 100, consumer_name
                )
            else:
                # Get pending tasks for entire consumer group
                pending_info = await self.redis.xpending_range(
                    stream_key, consumer_group, '-', '+', 100
                )
            
            pending_tasks = []
            for info in pending_info:
                task_info = {
                    "message_id": info[0].decode() if isinstance(info[0], bytes) else str(info[0]),
                    "consumer": info[1].decode() if isinstance(info[1], bytes) else str(info[1]),
                    "idle_time_ms": info[2],
                    "delivery_count": info[3]
                }
                pending_tasks.append(task_info)
            
            return pending_tasks
            
        except Exception as e:
            self._logger.error(
                f"Failed to get pending tasks for {queue_name}: {e}",
                extra={
                    "queue_name": queue_name,
                    "consumer_group": consumer_group,
                    "consumer_name": consumer_name
                }
            )
            return []
    
    async def claim_abandoned_tasks(self, queue_name: str, consumer_group: str, consumer_name: str, min_idle_time_ms: int = 60000) -> List[TaskContext]:
        """Claim tasks that have been abandoned by other consumers."""
        try:
            stream_key = f"task_queue:{queue_name}"
            
            # Get pending tasks that are idle for too long
            pending_tasks = await self.get_pending_tasks(queue_name, consumer_group)
            abandoned_tasks = [
                task for task in pending_tasks 
                if task["idle_time_ms"] > min_idle_time_ms
            ]
            
            claimed_tasks = []
            for task_info in abandoned_tasks:
                try:
                    # Claim the message
                    messages = await self.redis.xclaim(
                        stream_key,
                        consumer_group,
                        consumer_name,
                        min_idle_time_ms,
                        task_info["message_id"]
                    )
                    
                    if messages:
                        message_id, fields = messages[0]
                        task = self._deserialize_task(fields)
                        task.task_metadata["redis_message_id"] = message_id.decode() if isinstance(message_id, bytes) else str(message_id)
                        task.task_metadata["claimed_from_abandoned"] = True
                        task.task_metadata["original_consumer"] = task_info["consumer"]
                        task.task_metadata["reclaimed_at"] = datetime.now().isoformat()
                        
                        claimed_tasks.append(task)
                        
                        self._logger.info(
                            f"Claimed abandoned task: {task.task_id}",
                            extra={
                                "task_id": task.task_id,
                                "original_consumer": task_info["consumer"],
                                "idle_time_ms": task_info["idle_time_ms"]
                            }
                        )
                        
                except Exception as e:
                    self._logger.warning(f"Failed to claim abandoned task {task_info['message_id']}: {e}")
            
            return claimed_tasks
            
        except Exception as e:
            self._logger.error(f"Failed to claim abandoned tasks: {e}")
            return []
    
    async def _validate_task_security(self, task: TaskContext) -> bool:
        """Validate task security according to security settings."""
        try:
            # Check task type allowlist
            if self.security.allowed_task_types and task.task_type not in self.security.allowed_task_types:
                self._logger.warning(
                    f"Task type not allowed: {task.task_type}",
                    extra={"task_id": task.task_id, "task_type": task.task_type}
                )
                return False
            
            # Check payload size
            task_size = len(json.dumps(asdict(task), default=str).encode())
            if task_size > self.security.max_payload_size_bytes:
                self._logger.warning(
                    f"Task payload too large: {task_size} bytes",
                    extra={"task_id": task.task_id, "payload_size": task_size}
                )
                return False
            
            # Scan for dangerous patterns
            if self.security.validate_task_content:
                content_to_check = f"{task.task_content} {json.dumps(task.task_parameters, default=str)}"
                
                for pattern in self._dangerous_patterns:
                    if pattern.search(content_to_check):
                        self._logger.warning(
                            f"Dangerous pattern detected in task: {pattern.pattern}",
                            extra={"task_id": task.task_id, "pattern": pattern.pattern}
                        )
                        return False
            
            # Sanitize inputs if enabled
            if self.security.sanitize_inputs:
                task.task_content = self._sanitize_content(task.task_content)
                task.task_parameters = self._sanitize_parameters(task.task_parameters)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error during task security validation: {e}")
            return False
    
    def _sanitize_content(self, content: str) -> str:
        """Sanitize task content to prevent injection attacks."""
        if not content:
            return content
        
        # Remove or escape dangerous characters
        sanitized = content.replace('<script>', '&lt;script&gt;')
        sanitized = sanitized.replace('</script>', '&lt;/script&gt;')
        sanitized = sanitized.replace('javascript:', 'javascript_')
        sanitized = sanitized.replace('eval(', 'eval_')
        sanitized = sanitized.replace('exec(', 'exec_')
        
        return sanitized
    
    def _sanitize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize task parameters."""
        if not parameters:
            return parameters
        
        sanitized = {}
        for key, value in parameters.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_content(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_parameters(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _serialize_task(self, task: TaskContext) -> Dict[str, str]:
        """Serialize task for Redis Stream storage."""
        task_dict = asdict(task)
        
        # Convert complex fields to JSON strings
        serialized = {}
        for key, value in task_dict.items():
            if value is None:
                serialized[key] = ""
            elif isinstance(value, (dict, list)):
                serialized[key] = json.dumps(value, default=str)
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            else:
                serialized[key] = str(value)
        
        return serialized
    
    def _deserialize_task(self, fields: Dict[bytes, bytes]) -> TaskContext:
        """Deserialize task from Redis Stream fields."""
        # Convert bytes to strings and parse JSON fields
        task_data = {}
        for key, value in fields.items():
            key_str = key.decode() if isinstance(key, bytes) else str(key)
            value_str = value.decode() if isinstance(value, bytes) else str(value)
            
            if key_str in ['task_parameters', 'task_metadata', 'state_history']:
                try:
                    task_data[key_str] = json.loads(value_str) if value_str else {}
                except json.JSONDecodeError:
                    task_data[key_str] = {}
            elif key_str in ['created_at', 'claimed_at', 'execution_start', 'execution_end']:
                try:
                    task_data[key_str] = datetime.fromisoformat(value_str) if value_str else None
                except ValueError:
                    task_data[key_str] = None
            elif key_str == 'task_state':
                try:
                    task_data[key_str] = TaskState[value_str] if value_str else TaskState.QUEUED
                except KeyError:
                    task_data[key_str] = TaskState.QUEUED
            else:
                task_data[key_str] = value_str if value_str else None
        
        return TaskContext(**task_data)
    
    async def _ensure_consumer_group(self, stream_key: str, consumer_group: str):
        """Ensure consumer group exists for the stream."""
        try:
            await self.redis.xgroup_create(stream_key, consumer_group, id='0', mkstream=True)
        except Exception as e:
            # Group might already exist, which is fine
            if "BUSYGROUP" not in str(e):
                self._logger.debug(f"Consumer group creation result: {e}")


class TaskQueuePriorityManager:
    """Manages task priority across multiple queues."""
    
    def __init__(self, redis_operations: RedisTaskQueueOperations):
        self.redis_ops = redis_operations
        self._logger = logging.getLogger(f"{__name__}.TaskQueuePriorityManager")
    
    async def dequeue_by_priority(
        self, 
        queue_configs: List[QueueConfig], 
        consumer_group: str, 
        consumer_name: str,
        timeout_ms: int = 1000
    ) -> Optional[Tuple[TaskContext, str]]:
        """Dequeue task from highest priority queue with available tasks."""
        # Sort queues by priority (lower number = higher priority)
        sorted_queues = sorted(queue_configs, key=lambda q: q.priority)
        
        for queue_config in sorted_queues:
            try:
                task = await self.redis_ops.dequeue_task(
                    queue_config.name, 
                    consumer_group, 
                    consumer_name, 
                    timeout_ms=100  # Short timeout for priority checking
                )
                
                if task:
                    self._logger.info(
                        f"Dequeued task from priority queue: {queue_config.name}",
                        extra={
                            "task_id": task.task_id,
                            "queue_name": queue_config.name,
                            "priority": queue_config.priority
                        }
                    )
                    return task, queue_config.name
                    
            except Exception as e:
                self._logger.warning(f"Error checking queue {queue_config.name}: {e}")
        
        return None
    
    async def boost_aged_tasks(self, queue_configs: List[QueueConfig], age_threshold_minutes: int = 30):
        """Boost priority of tasks that have been waiting too long."""
        try:
            current_time = datetime.now()
            
            for queue_config in queue_configs:
                # Get tasks from queue
                tasks = await self.redis_ops.peek_queue(queue_config.name, count=100)
                
                for task in tasks:
                    task_age = (current_time - task.created_at).total_seconds() / 60
                    
                    if task_age > age_threshold_minutes:
                        # Move task to higher priority queue if available
                        higher_priority_queue = self._find_higher_priority_queue(queue_config, queue_configs)
                        
                        if higher_priority_queue:
                            # This would involve removing from current queue and adding to higher priority queue
                            # Implementation would depend on specific requirements
                            self._logger.info(
                                f"Task {task.task_id} eligible for priority boost",
                                extra={
                                    "task_id": task.task_id,
                                    "current_queue": queue_config.name,
                                    "target_queue": higher_priority_queue.name,
                                    "age_minutes": task_age
                                }
                            )
                            
        except Exception as e:
            self._logger.error(f"Error boosting aged tasks: {e}")
    
    def _find_higher_priority_queue(self, current_queue: QueueConfig, all_queues: List[QueueConfig]) -> Optional[QueueConfig]:
        """Find a queue with higher priority than the current queue."""
        for queue in all_queues:
            if queue.priority < current_queue.priority:  # Lower number = higher priority
                return queue
        return None