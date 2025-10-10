"""Redis-based state storage for Constellation Orchestrator."""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
import structlog

from ..models.execution_state import ExecutionState, ExecutionResult
from ..models.task_definition import TaskStatus


class RedisStateStore:
    """Redis-based persistent state management for orchestrator execution."""
    
    def __init__(self, redis_url: str, password: Optional[str] = None):
        """Initialize Redis state store."""
        self.redis_url = redis_url
        self.password = password
        self.redis_client: Optional[redis.Redis] = None
        self.logger = structlog.get_logger(__name__)
        
        # Key prefixes for different data types
        self.EXECUTION_PREFIX = "constellation:execution:"
        self.TASK_RESULT_PREFIX = "constellation:task_result:"
        self.TASK_STATUS_PREFIX = "constellation:task_status:"
        self.METRICS_PREFIX = "constellation:metrics:"
        
        # Default expiration times
        self.EXECUTION_TTL = 86400 * 7  # 7 days
        self.TASK_RESULT_TTL = 86400 * 3  # 3 days
        self.METRICS_TTL = 86400 * 1  # 1 day
    
    async def initialize(self) -> bool:
        """Initialize Redis connection."""
        try:
            # Create Redis connection
            connection_kwargs = {
                'decode_responses': True,
                'socket_connect_timeout': 5,
                'socket_timeout': 5,
                'retry_on_timeout': True,
                'health_check_interval': 30
            }
            
            if self.password:
                connection_kwargs['password'] = self.password
            
            self.redis_client = redis.from_url(self.redis_url, **connection_kwargs)
            
            # Test connection
            await self.redis_client.ping()
            
            self.logger.info(
                "redis_state_store_initialized",
                redis_url=self.redis_url.split('@')[-1] if '@' in self.redis_url else self.redis_url
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "redis_state_store_initialization_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            if not self.redis_client:
                return False
            
            await self.redis_client.ping()
            return True
            
        except Exception as e:
            self.logger.error(
                "redis_health_check_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def save_execution_state(self, execution_id: str, state: ExecutionState) -> bool:
        """Save execution state to Redis with expiration."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            key = f"{self.EXECUTION_PREFIX}{execution_id}"
            state_json = state.json()
            
            # Save with expiration
            await self.redis_client.setex(key, self.EXECUTION_TTL, state_json)
            
            self.logger.debug(
                "execution_state_saved",
                execution_id=execution_id,
                state_size=len(state_json)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "execution_state_save_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def load_execution_state(self, execution_id: str) -> Optional[ExecutionState]:
        """Load execution state from Redis."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            key = f"{self.EXECUTION_PREFIX}{execution_id}"
            state_json = await self.redis_client.get(key)
            
            if not state_json:
                self.logger.debug(
                    "execution_state_not_found",
                    execution_id=execution_id
                )
                return None
            
            state = ExecutionState.parse_raw(state_json)
            
            self.logger.debug(
                "execution_state_loaded",
                execution_id=execution_id,
                task_count=len(state.task_states)
            )
            
            return state
            
        except Exception as e:
            self.logger.error(
                "execution_state_load_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return None
    
    async def save_task_result(self, execution_id: str, task_id: str, result: ExecutionResult) -> bool:
        """Save individual task result for recovery."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            # Save task result
            result_key = f"{self.TASK_RESULT_PREFIX}{execution_id}:{task_id}"
            result_json = result.json()
            await self.redis_client.setex(result_key, self.TASK_RESULT_TTL, result_json)
            
            # Update task status
            status_key = f"{self.TASK_STATUS_PREFIX}{execution_id}"
            await self.redis_client.hset(status_key, task_id, result.status.value)
            await self.redis_client.expire(status_key, self.TASK_RESULT_TTL)
            
            self.logger.debug(
                "task_result_saved",
                execution_id=execution_id,
                task_id=task_id,
                status=result.status.value
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "task_result_save_failed",
                execution_id=execution_id,
                task_id=task_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def get_task_results(self, execution_id: str) -> Dict[str, ExecutionResult]:
        """Get all task results for an execution."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            # Get all task result keys for this execution
            pattern = f"{self.TASK_RESULT_PREFIX}{execution_id}:*"
            keys = await self.redis_client.keys(pattern)
            
            results = {}
            
            if keys:
                # Get all results in batch
                values = await self.redis_client.mget(keys)
                
                for key, value in zip(keys, values):
                    if value:
                        # Extract task_id from key
                        task_id = key.split(':')[-1]
                        try:
                            result = ExecutionResult.parse_raw(value)
                            results[task_id] = result
                        except Exception as parse_error:
                            self.logger.warning(
                                "task_result_parse_failed",
                                execution_id=execution_id,
                                task_id=task_id,
                                error=str(parse_error)
                            )
            
            self.logger.debug(
                "task_results_loaded",
                execution_id=execution_id,
                result_count=len(results)
            )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "task_results_load_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return {}
    
    async def get_task_statuses(self, execution_id: str) -> Dict[str, TaskStatus]:
        """Get all task statuses for an execution."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            status_key = f"{self.TASK_STATUS_PREFIX}{execution_id}"
            status_data = await self.redis_client.hgetall(status_key)
            
            statuses = {}
            for task_id, status_str in status_data.items():
                try:
                    statuses[task_id] = TaskStatus(status_str)
                except ValueError:
                    self.logger.warning(
                        "invalid_task_status",
                        execution_id=execution_id,
                        task_id=task_id,
                        status=status_str
                    )
            
            return statuses
            
        except Exception as e:
            self.logger.error(
                "task_statuses_load_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return {}
    
    async def update_task_status(self, execution_id: str, task_id: str, status: TaskStatus) -> bool:
        """Update individual task status."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            status_key = f"{self.TASK_STATUS_PREFIX}{execution_id}"
            await self.redis_client.hset(status_key, task_id, status.value)
            await self.redis_client.expire(status_key, self.TASK_RESULT_TTL)
            
            return True
            
        except Exception as e:
            self.logger.error(
                "task_status_update_failed",
                execution_id=execution_id,
                task_id=task_id,
                status=status.value,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def save_metrics(self, execution_id: str, metrics: Dict[str, Any]) -> bool:
        """Save execution metrics."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            metrics_key = f"{self.METRICS_PREFIX}{execution_id}"
            metrics_json = json.dumps(metrics, default=str)
            
            await self.redis_client.setex(metrics_key, self.METRICS_TTL, metrics_json)
            
            return True
            
        except Exception as e:
            self.logger.error(
                "metrics_save_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def get_active_executions(self) -> List[str]:
        """Get list of active execution IDs."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            pattern = f"{self.EXECUTION_PREFIX}*"
            keys = await self.redis_client.keys(pattern)
            
            # Extract execution IDs from keys
            execution_ids = []
            for key in keys:
                execution_id = key.replace(self.EXECUTION_PREFIX, '')
                execution_ids.append(execution_id)
            
            return execution_ids
            
        except Exception as e:
            self.logger.error(
                "active_executions_load_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return []
    
    async def cleanup_expired_data(self) -> int:
        """Clean up expired data and return count of cleaned items."""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            cleaned_count = 0
            
            # Get all constellation keys
            patterns = [
                f"{self.EXECUTION_PREFIX}*",
                f"{self.TASK_RESULT_PREFIX}*",
                f"{self.TASK_STATUS_PREFIX}*",
                f"{self.METRICS_PREFIX}*"
            ]
            
            for pattern in patterns:
                keys = await self.redis_client.keys(pattern)
                for key in keys:
                    ttl = await self.redis_client.ttl(key)
                    if ttl == -1:  # No expiration set
                        # Set appropriate expiration based on key type
                        if self.EXECUTION_PREFIX in key:
                            await self.redis_client.expire(key, self.EXECUTION_TTL)
                        elif self.TASK_RESULT_PREFIX in key or self.TASK_STATUS_PREFIX in key:
                            await self.redis_client.expire(key, self.TASK_RESULT_TTL)
                        elif self.METRICS_PREFIX in key:
                            await self.redis_client.expire(key, self.METRICS_TTL)
                        cleaned_count += 1
            
            if cleaned_count > 0:
                self.logger.info(
                    "redis_cleanup_completed",
                    cleaned_count=cleaned_count
                )
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(
                "redis_cleanup_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return 0
    
    async def shutdown(self) -> None:
        """Shutdown Redis connection."""
        try:
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None
                
                self.logger.info("redis_state_store_shutdown_complete")
                
        except Exception as e:
            self.logger.error(
                "redis_state_store_shutdown_error",
                error=str(e),
                error_type=type(e).__name__
            )