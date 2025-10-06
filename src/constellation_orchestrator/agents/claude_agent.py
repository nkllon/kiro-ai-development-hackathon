"""Claude CLI agent wrapper for Constellation Orchestrator."""

import asyncio
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import structlog

from ..models.execution_state import ExecutionResult
from ..models.task_definition import TaskStatus, TaskDefinition


class ClaudeAgent:
    """Wrapper for Claude CLI agent communication."""
    
    def __init__(self, agent_id: str, claude_cli_path: str = "claude", timeout: int = 300):
        """Initialize Claude agent."""
        self.agent_id = agent_id
        self.claude_cli_path = claude_cli_path
        self.timeout = timeout
        self.logger = structlog.get_logger(__name__)
        
        # Agent state
        self.is_busy = False
        self.current_task_id: Optional[str] = None
        self.process: Optional[asyncio.subprocess.Process] = None
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        
        # Performance tracking
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_execution_time = 0.0
        
        self.logger.info(
            "claude_agent_created",
            agent_id=self.agent_id,
            claude_cli_path=self.claude_cli_path,
            timeout=self.timeout
        )
    
    async def execute_prompt(self, task: TaskDefinition) -> ExecutionResult:
        """Execute prompt via Claude CLI and capture output."""
        if self.is_busy:
            raise RuntimeError(f"Agent {self.agent_id} is already busy")
        
        self.is_busy = True
        self.current_task_id = task.task_id
        start_time = time.time()
        
        try:
            self.logger.info(
                "claude_agent_executing_task",
                agent_id=self.agent_id,
                task_id=task.task_id,
                prompt_length=len(task.prompt)
            )
            
            # Create execution result
            result = ExecutionResult(
                task_id=task.task_id,
                status=TaskStatus.RUNNING,
                start_time=datetime.utcnow(),
                agent_id=self.agent_id
            )
            
            # Execute Claude CLI command
            try:
                # Create the command
                cmd = [self.claude_cli_path, "-"]
                
                # Start the process
                self.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                # Send prompt and wait for response
                stdout, stderr = await asyncio.wait_for(
                    self.process.communicate(input=task.prompt.encode('utf-8')),
                    timeout=task.timeout or self.timeout
                )
                
                # Process results
                result.end_time = datetime.utcnow()
                result.duration = time.time() - start_time
                result.exit_code = self.process.returncode
                
                if self.process.returncode == 0:
                    result.status = TaskStatus.COMPLETED
                    result.output = stdout.decode('utf-8').strip()
                    self.tasks_completed += 1
                    
                    self.logger.info(
                        "claude_agent_task_completed",
                        agent_id=self.agent_id,
                        task_id=task.task_id,
                        duration=result.duration,
                        output_length=len(result.output) if result.output else 0
                    )
                else:
                    result.status = TaskStatus.FAILED
                    result.error = stderr.decode('utf-8').strip() if stderr else "Process failed with no error output"
                    self.tasks_failed += 1
                    
                    self.logger.error(
                        "claude_agent_task_failed",
                        agent_id=self.agent_id,
                        task_id=task.task_id,
                        exit_code=self.process.returncode,
                        error=result.error
                    )
                
            except asyncio.TimeoutError:
                result.status = TaskStatus.FAILED
                result.error = f"Task timed out after {task.timeout or self.timeout} seconds"
                result.end_time = datetime.utcnow()
                result.duration = time.time() - start_time
                self.tasks_failed += 1
                
                # Kill the process if it's still running
                if self.process and self.process.returncode is None:
                    try:
                        self.process.kill()
                        await self.process.wait()
                    except Exception as kill_error:
                        self.logger.warning(
                            "claude_agent_process_kill_failed",
                            agent_id=self.agent_id,
                            task_id=task.task_id,
                            error=str(kill_error)
                        )
                
                self.logger.error(
                    "claude_agent_task_timeout",
                    agent_id=self.agent_id,
                    task_id=task.task_id,
                    timeout=task.timeout or self.timeout
                )
            
            except Exception as exec_error:
                result.status = TaskStatus.FAILED
                result.error = f"Execution error: {str(exec_error)}"
                result.end_time = datetime.utcnow()
                result.duration = time.time() - start_time
                self.tasks_failed += 1
                
                self.logger.error(
                    "claude_agent_execution_error",
                    agent_id=self.agent_id,
                    task_id=task.task_id,
                    error=str(exec_error),
                    error_type=type(exec_error).__name__
                )
            
            # Update performance tracking
            self.total_execution_time += result.duration or 0
            self.last_activity = datetime.utcnow()
            
            return result
            
        finally:
            # Clean up
            self.is_busy = False
            self.current_task_id = None
            self.process = None
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        return not self.is_busy
    
    async def health_check(self) -> bool:
        """Verify agent is responsive and healthy."""
        try:
            if self.is_busy:
                # Agent is busy, consider it healthy if it's not stuck
                time_since_activity = (datetime.utcnow() - self.last_activity).total_seconds()
                return time_since_activity < (self.timeout * 2)  # Allow 2x timeout for stuck detection
            
            # Test with a simple prompt
            test_task = TaskDefinition(
                task_id=f"health_check_{uuid.uuid4().hex[:8]}",
                prompt="Hello, respond with 'OK'",
                timeout=10
            )
            
            result = await self.execute_prompt(test_task)
            
            is_healthy = result.status == TaskStatus.COMPLETED
            
            self.logger.debug(
                "claude_agent_health_check",
                agent_id=self.agent_id,
                is_healthy=is_healthy,
                test_result_status=result.status.value
            )
            
            return is_healthy
            
        except Exception as e:
            self.logger.error(
                "claude_agent_health_check_failed",
                agent_id=self.agent_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = (datetime.utcnow() - self.created_at).total_seconds()
        
        return {
            'agent_id': self.agent_id,
            'is_available': self.is_available(),
            'is_busy': self.is_busy,
            'current_task_id': self.current_task_id,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_execution_time': self.total_execution_time,
            'uptime_seconds': uptime,
            'last_activity': self.last_activity.isoformat(),
            'success_rate': self.tasks_completed / (self.tasks_completed + self.tasks_failed) if (self.tasks_completed + self.tasks_failed) > 0 else 0.0,
            'average_execution_time': self.total_execution_time / self.tasks_completed if self.tasks_completed > 0 else 0.0
        }
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for this agent."""
        total_tasks = self.tasks_completed + self.tasks_failed
        
        return {
            'success_rate': self.tasks_completed / total_tasks if total_tasks > 0 else 0.0,
            'failure_rate': self.tasks_failed / total_tasks if total_tasks > 0 else 0.0,
            'average_execution_time': self.total_execution_time / self.tasks_completed if self.tasks_completed > 0 else 0.0,
            'tasks_per_hour': total_tasks / ((datetime.utcnow() - self.created_at).total_seconds() / 3600) if total_tasks > 0 else 0.0,
            'utilization': self.total_execution_time / (datetime.utcnow() - self.created_at).total_seconds() if (datetime.utcnow() - self.created_at).total_seconds() > 0 else 0.0
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        try:
            self.logger.info(
                "claude_agent_shutting_down",
                agent_id=self.agent_id,
                tasks_completed=self.tasks_completed,
                tasks_failed=self.tasks_failed
            )
            
            # If agent is busy, wait a bit for current task to complete
            if self.is_busy and self.process:
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    # Force kill if it doesn't complete
                    if self.process.returncode is None:
                        self.process.kill()
                        await self.process.wait()
            
            self.is_busy = False
            self.current_task_id = None
            self.process = None
            
            self.logger.info(
                "claude_agent_shutdown_complete",
                agent_id=self.agent_id
            )
            
        except Exception as e:
            self.logger.error(
                "claude_agent_shutdown_error",
                agent_id=self.agent_id,
                error=str(e),
                error_type=type(e).__name__
            )