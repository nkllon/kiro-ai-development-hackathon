"""
Main execution engine that orchestrates task execution.
"""
from datetime import datetime
from typing import Dict, List, Optional
import logging

from .task_manager import TaskManager, Task, TaskStatus
from .agent_manager import AgentManager, Agent
from .git_session import GitSession

class ExecutionEngine:
    """Main engine for orchestrating task execution."""
    
    def __init__(self, auto_merge: bool = False, auto_revert_on_failure: bool = False):
        self.task_manager = TaskManager()
        self.agent_manager = AgentManager()
        self.git_session: Optional[GitSession] = None
        self.auto_merge = auto_merge
        self.auto_revert_on_failure = auto_revert_on_failure
        self.logger = logging.getLogger(__name__)
    
    def add_task(self, task: Task) -> None:
        """Add a task to the execution queue."""
        self.task_manager.add_task(task)
    
    def register_agent(self, agent: Agent) -> None:
        """Register an agent for task execution."""
        self.agent_manager.register_agent(agent)
    
    def execute_tasks(self) -> Dict:
        """Execute all tasks in the queue."""
        execution_start = datetime.now()
        
        # Initialize Git session
        self.git_session = GitSession()
        if not self.git_session.create_session_branch():
            return {
                "error": "Failed to create session branch",
                "execution_start": execution_start.isoformat(),
                "execution_end": datetime.now().isoformat(),
                "success": False
            }
        
        self.logger.info(f"Starting task execution in branch: {self.git_session.branch_name}")
        
        try:
            iteration = 0
            while True:
                iteration += 1
                self.logger.info(f"Execution iteration {iteration}")
                
                # Get tasks ready for execution
                ready_tasks = self.task_manager.get_ready_tasks()
                available_agents = self.agent_manager.get_available_agents()
                
                if not ready_tasks:
                    if self._all_tasks_completed():
                        self.logger.info("All tasks completed!")
                        break
                    elif self._has_deadlock():
                        self.logger.warning("Possible deadlock detected")
                        break
                    else:
                        self.logger.info("Waiting for in-progress tasks...")
                        break
                
                if not available_agents:
                    self.logger.info("No available agents")
                    break
                
                # Assign tasks to agents
                assignments_made = self._assign_tasks(ready_tasks, available_agents)
                
                if assignments_made == 0:
                    self.logger.info("No task assignments made")
                    break
                
                self.logger.info(f"Made {assignments_made} assignments in iteration {iteration}")
        
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
            return self._create_error_summary(execution_start, str(e))
        
        return self._create_execution_summary(execution_start, iteration)
    
    def _all_tasks_completed(self) -> bool:
        """Check if all tasks are completed."""
        stats = self.task_manager.get_task_stats()
        total_tasks = sum(stats.values())
        return stats[TaskStatus.COMPLETED.value] == total_tasks
    
    def _has_deadlock(self) -> bool:
        """Check for potential deadlock situation."""
        stats = self.task_manager.get_task_stats()
        return (stats[TaskStatus.IN_PROGRESS.value] == 0 and 
                stats[TaskStatus.NOT_STARTED.value] > 0)
    
    def _assign_tasks(self, ready_tasks: List[Task], available_agents: List[Agent]) -> int:
        """Assign ready tasks to available agents."""
        assignments_made = 0
        
        for task in ready_tasks:
            if not available_agents:
                break
            
            best_agent = self.agent_manager.find_best_agent(task, available_agents)
            
            if best_agent:
                if self.agent_manager.assign_task(best_agent.id, task.id):
                    # Start the task
                    self.task_manager.start_task(task.id, best_agent.id)
                    
                    # Execute the task immediately (simulated)
                    success = self.task_manager.execute_task(task.id)
                    
                    # Release the agent
                    self.agent_manager.release_agent(best_agent.id)
                    
                    available_agents.remove(best_agent)
                    assignments_made += 1
                    
                    self.logger.info(f"Task {task.id} {'completed' if success else 'failed'}")
        
        return assignments_made
    
    def _create_error_summary(self, execution_start: datetime, error: str) -> Dict:
        """Create error summary."""
        return {
            "error": error,
            "execution_start": execution_start.isoformat(),
            "execution_end": datetime.now().isoformat(),
            "success": False
        }
    
    def _create_execution_summary(self, execution_start: datetime, iterations: int) -> Dict:
        """Create execution summary."""
        execution_end = datetime.now()
        total_duration = (execution_end - execution_start).total_seconds()
        stats = self.task_manager.get_task_stats()
        
        # Handle Git operations
        git_status = "branch_preserved"
        if self.git_session and self.git_session.changes_made:
            commit_msg = f"Task execution completed - {stats[TaskStatus.COMPLETED.value]} tasks"
            self.git_session.commit_changes(commit_msg)
            self.git_session.push_branch()
            
            success_rate = stats[TaskStatus.COMPLETED.value] / sum(stats.values()) * 100
            
            if self.auto_merge and success_rate >= 80:
                if self.git_session.merge_to_base():
                    self.git_session.cleanup_branch()
                    git_status = "merged_and_cleaned"
                else:
                    git_status = "merge_failed"
        
        return {
            "execution_start": execution_start.isoformat(),
            "execution_end": execution_end.isoformat(),
            "total_duration_seconds": total_duration,
            "iterations": iterations,
            "task_stats": stats,
            "git_status": git_status,
            "success": stats[TaskStatus.COMPLETED.value] > 0
        }