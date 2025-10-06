"""Status management for Constellation Orchestrator."""

from datetime import datetime
from typing import Dict, Optional, Any, List
import structlog

from ..core.config import ConstellationConfig
from ..models.execution_state import ExecutionState, ExecutionResult, ExecutionMetrics
from ..models.task_definition import TaskStatus
from ..storage.redis_store import RedisStateStore


class StatusManager:
    """Manages execution state persistence and recovery."""
    
    def __init__(self, config: ConstellationConfig):
        """Initialize status manager."""
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Storage
        self.redis_store = RedisStateStore(
            redis_url=config.redis_url,
            password=config.redis_password
        )
        
        # Current execution state
        self.current_execution: Optional[ExecutionState] = None
        
        self.logger.info("status_manager_initialized")
    
    async def initialize(self) -> bool:
        """Initialize status manager."""
        try:
            self.logger.info("status_manager_initializing")
            
            # Initialize Redis store
            success = await self.redis_store.initialize()
            if not success:
                self.logger.error("status_manager_redis_initialization_failed")
                return False
            
            self.logger.info("status_manager_initialized_successfully")
            return True
            
        except Exception as e:
            self.logger.error(
                "status_manager_initialization_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def initialize_execution(self, execution_id: str, task_count: int) -> bool:
        """Initialize execution tracking state."""
        try:
            self.logger.info(
                "status_initializing_execution",
                execution_id=execution_id,
                task_count=task_count
            )
            
            # Create new execution state
            metrics = ExecutionMetrics(
                total_tasks=task_count,
                pending_tasks=task_count,
                start_time=datetime.utcnow()
            )
            
            execution_state = ExecutionState(
                execution_id=execution_id,
                status="initializing",
                metrics=metrics,
                max_concurrent_agents=self.config.max_concurrent_agents
            )
            
            # Save to Redis
            success = await self.redis_store.save_execution_state(execution_id, execution_state)
            if not success:
                self.logger.error(
                    "status_execution_initialization_save_failed",
                    execution_id=execution_id
                )
                return False
            
            # Set as current execution
            self.current_execution = execution_state
            
            self.logger.info(
                "status_execution_initialized",
                execution_id=execution_id,
                task_count=task_count
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "status_execution_initialization_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def update_task_status(self, task_id: str, status: TaskStatus, result: Optional[ExecutionResult] = None) -> bool:
        """Update individual task status and persist state."""
        try:
            if not self.current_execution:
                self.logger.error(
                    "status_update_no_current_execution",
                    task_id=task_id,
                    status=status.value
                )
                return False
            
            # Update execution state
            self.current_execution.update_task_state(task_id, status, result)
            
            # Save to Redis
            success = await self.redis_store.save_execution_state(
                self.current_execution.execution_id,
                self.current_execution
            )
            
            if not success:
                self.logger.error(
                    "status_task_update_save_failed",
                    execution_id=self.current_execution.execution_id,
                    task_id=task_id,
                    status=status.value
                )
                return False
            
            # Save task result if provided
            if result:
                await self.redis_store.save_task_result(
                    self.current_execution.execution_id,
                    task_id,
                    result
                )
            
            self.logger.debug(
                "status_task_updated",
                execution_id=self.current_execution.execution_id,
                task_id=task_id,
                status=status.value,
                has_result=result is not None
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "status_task_update_failed",
                task_id=task_id,
                status=status.value,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def get_execution_state(self, execution_id: str) -> Optional[ExecutionState]:
        """Get current execution state."""
        try:
            # Check if it's the current execution
            if self.current_execution and self.current_execution.execution_id == execution_id:
                return self.current_execution
            
            # Load from Redis
            execution_state = await self.redis_store.load_execution_state(execution_id)
            
            if execution_state:
                self.logger.debug(
                    "status_execution_state_loaded",
                    execution_id=execution_id,
                    status=execution_state.status,
                    task_count=execution_state.metrics.total_tasks
                )
            else:
                self.logger.debug(
                    "status_execution_state_not_found",
                    execution_id=execution_id
                )
            
            return execution_state
            
        except Exception as e:
            self.logger.error(
                "status_execution_state_load_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return None
    
    async def can_resume(self, execution_id: str) -> bool:
        """Check if execution can be resumed from saved state."""
        try:
            execution_state = await self.get_execution_state(execution_id)
            
            if not execution_state:
                return False
            
            can_resume = execution_state.can_resume()
            
            self.logger.debug(
                "status_resume_check",
                execution_id=execution_id,
                can_resume=can_resume,
                status=execution_state.status,
                remaining_tasks=execution_state.metrics.get_remaining_tasks()
            )
            
            return can_resume
            
        except Exception as e:
            self.logger.error(
                "status_resume_check_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def resume_execution(self, execution_id: str) -> Optional[Dict[str, TaskStatus]]:
        """Resume execution and return task states."""
        try:
            self.logger.info(
                "status_resuming_execution",
                execution_id=execution_id
            )
            
            # Load execution state
            execution_state = await self.get_execution_state(execution_id)
            
            if not execution_state:
                self.logger.error(
                    "status_resume_state_not_found",
                    execution_id=execution_id
                )
                return None
            
            if not execution_state.can_resume():
                self.logger.error(
                    "status_resume_not_allowed",
                    execution_id=execution_id,
                    status=execution_state.status
                )
                return None
            
            # Set as current execution
            self.current_execution = execution_state
            self.current_execution.status = "running"
            self.current_execution.add_execution_event("execution_resumed", {
                "resumed_at": datetime.utcnow().isoformat()
            })
            
            # Save updated state
            await self.redis_store.save_execution_state(execution_id, execution_state)
            
            self.logger.info(
                "status_execution_resumed",
                execution_id=execution_id,
                total_tasks=execution_state.metrics.total_tasks,
                completed_tasks=execution_state.metrics.completed_tasks,
                remaining_tasks=execution_state.metrics.get_remaining_tasks()
            )
            
            return execution_state.task_states
            
        except Exception as e:
            self.logger.error(
                "status_resume_execution_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return None
    
    async def complete_execution(self, execution_id: Optional[str] = None) -> bool:
        """Mark execution as completed."""
        try:
            target_execution_id = execution_id or (self.current_execution.execution_id if self.current_execution else None)
            
            if not target_execution_id:
                self.logger.error("status_complete_no_execution_id")
                return False
            
            execution_state = await self.get_execution_state(target_execution_id)
            if not execution_state:
                self.logger.error(
                    "status_complete_state_not_found",
                    execution_id=target_execution_id
                )
                return False
            
            # Update status
            execution_state.status = "completed"
            execution_state.metrics.last_update = datetime.utcnow()
            execution_state.add_execution_event("execution_completed", {
                "completed_at": datetime.utcnow().isoformat(),
                "final_metrics": execution_state.metrics.dict()
            })
            
            # Save final state
            success = await self.redis_store.save_execution_state(target_execution_id, execution_state)
            
            if success:
                self.logger.info(
                    "status_execution_completed",
                    execution_id=target_execution_id,
                    total_tasks=execution_state.metrics.total_tasks,
                    completed_tasks=execution_state.metrics.completed_tasks,
                    failed_tasks=execution_state.metrics.failed_tasks,
                    success_rate=execution_state.metrics.get_success_rate()
                )
            
            return success
            
        except Exception as e:
            self.logger.error(
                "status_complete_execution_failed",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def fail_execution(self, execution_id: str, error_message: str) -> bool:
        """Mark execution as failed."""
        try:
            execution_state = await self.get_execution_state(execution_id)
            if not execution_state:
                self.logger.error(
                    "status_fail_state_not_found",
                    execution_id=execution_id
                )
                return False
            
            # Update status
            execution_state.status = "failed"
            execution_state.metrics.last_update = datetime.utcnow()
            execution_state.add_execution_event("execution_failed", {
                "failed_at": datetime.utcnow().isoformat(),
                "error_message": error_message,
                "final_metrics": execution_state.metrics.dict()
            })
            
            # Save final state
            success = await self.redis_store.save_execution_state(execution_id, execution_state)
            
            if success:
                self.logger.error(
                    "status_execution_failed",
                    execution_id=execution_id,
                    error_message=error_message,
                    completed_tasks=execution_state.metrics.completed_tasks,
                    failed_tasks=execution_state.metrics.failed_tasks
                )
            
            return success
            
        except Exception as e:
            self.logger.error(
                "status_fail_execution_error",
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def get_active_executions(self) -> List[str]:
        """Get list of active execution IDs."""
        try:
            return await self.redis_store.get_active_executions()
        except Exception as e:
            self.logger.error(
                "status_get_active_executions_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return []
    
    async def cleanup_old_executions(self, max_age_hours: int = 168) -> int:
        """Clean up old execution data."""
        try:
            return await self.redis_store.cleanup_expired_data()
        except Exception as e:
            self.logger.error(
                "status_cleanup_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return 0
    
    async def health_check(self) -> bool:
        """Health check for status manager."""
        try:
            # Check Redis connection
            redis_healthy = await self.redis_store.health_check()
            
            if not redis_healthy:
                self.logger.warning("status_health_check_redis_unhealthy")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(
                "status_health_check_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def shutdown(self) -> None:
        """Shutdown status manager."""
        try:
            self.logger.info("status_manager_shutting_down")
            
            # Save current execution state if exists
            if self.current_execution:
                await self.redis_store.save_execution_state(
                    self.current_execution.execution_id,
                    self.current_execution
                )
            
            # Shutdown Redis store
            await self.redis_store.shutdown()
            
            self.current_execution = None
            
            self.logger.info("status_manager_shutdown_complete")
            
        except Exception as e:
            self.logger.error(
                "status_manager_shutdown_error",
                error=str(e),
                error_type=type(e).__name__
            )