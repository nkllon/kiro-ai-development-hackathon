#!/usr/bin/env python3
"""
Task Execution Engine with Recursive Descent Dependency Resolution
Automatically issues independent tasks to agents when dependencies are met
"""

import asyncio
import json
import subprocess
import uuid
import sys
import time
from pathlib import Path
from typing import Dict, List, Set, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

# Add src to Python path for ReflectiveModule import
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from beast_mode.core.reflective_module import ReflectiveModule, HealthStatus, HealthIndicator

class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class Task:
    id: str
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.NOT_STARTED
    assigned_agent: Optional[str] = None
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    estimated_duration_hours: float = 4.0
    priority: int = 1  # 1=highest, 10=lowest
    requirements: List[str] = field(default_factory=list)

@dataclass
class Agent:
    id: str
    name: str
    is_available: bool = True
    current_task: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 1

@dataclass
class GitSession:
    session_id: str
    branch_name: str
    original_branch: str
    created_at: datetime
    is_active: bool = True
    changes_made: bool = False

class TaskExecutionEngine(ReflectiveModule):
    """
    Recursive descent task execution engine with dependency resolution
    Implements RM interface compliance for Beast Mode Framework
    """
    
    def __init__(self, branch_name: Optional[str] = None):
        super().__init__("task_execution_engine")
        
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.execution_log: List[Dict] = []
        
        # Git session management
        self.git_session: Optional[GitSession] = None
        self.specified_branch = branch_name
        self.auto_merge = True
        self.auto_revert_on_failure = True
        
        # RM compliance - health indicators
        self._update_health_indicator(
            "engine_status",
            HealthStatus.HEALTHY,
            "initialized",
            "Task execution engine initialized successfully"
        )
        
        # Initialize task definitions
        self._initialize_tasks()
        self._initialize_agents()
        
        self._update_health_indicator(
            "task_definitions",
            HealthStatus.HEALTHY,
            len(self.tasks),
            f"Loaded {len(self.tasks)} task definitions"
        )
        
        self._update_health_indicator(
            "agent_pool",
            HealthStatus.HEALTHY,
            len(self.agents),
            f"Initialized {len(self.agents)} agents"
        )
    
    def _initialize_tasks(self):
        """Initialize all tasks with their dependencies"""
        
        # Tier 0 - Foundation Tasks (No dependencies)
        foundation_tasks = [
            Task("2.1", "Implement Logging Issue Detection and Repair", 
                 "Create TestInfrastructureRepair class for automated infrastructure fixes", 
                 [], TaskStatus.NOT_STARTED, None, None, None, 3.0, 1, ["1.1", "1.4"]),
            
            Task("2.2", "Create Robust Test Logging System",
                 "Implement LoggingManager class with fallback mechanisms for failed log writes",
                 [], TaskStatus.NOT_STARTED, None, None, None, 4.0, 1, ["1.1", "1.4", "6.4"]),
            
            Task("3.1", "Add Missing Optimization Methods",
                 "Implement _improve_tool_compliance and _optimize_tool_performance methods",
                 [], TaskStatus.NOT_STARTED, None, None, None, 3.5, 2, ["3.1", "3.2"]),
            
            Task("3.2", "Implement Comprehensive Analytics Methods", 
                 "Add failure_pattern_analysis method with frequency metrics and analysis",
                 [], TaskStatus.NOT_STARTED, None, None, None, 4.0, 2, ["3.3", "3.4", "3.5"]),
            
            Task("3.3", "Fix Tool Execution Behavior Validation",
                 "Correct tool execution output validation to match actual vs expected results",
                 [], TaskStatus.NOT_STARTED, None, None, None, 3.0, 1, ["2.1", "2.2", "2.3", "2.4"]),
            
            Task("4.1", "Implement Accurate Health State Tracking",
                 "Create HealthStateManager class for centralized health monitoring",
                 [], TaskStatus.NOT_STARTED, None, None, None, 3.5, 2, ["1.3", "1.5"]),
            
            Task("1.1", "Implement Enhanced RCA Engine Core",
                 "Create EnhancedRCAEngine class extending existing RCAEngine",
                 [], TaskStatus.NOT_STARTED, None, None, None, 5.0, 1, ["4.1", "4.2"])
        ]
        
        # Tier 1 - First Level Dependencies
        tier1_tasks = [
            Task("1.2", "Add Failure Pattern Recognition System",
                 "Create FailurePatternAnalyzer class for pattern-based failure analysis",
                 ["1.1"], TaskStatus.NOT_STARTED, None, None, None, 4.5, 1, ["4.3", "5.2", "5.3"]),
            
            Task("1.3", "Implement Context-Aware Analysis",
                 "Create ContextAwareAnalyzer class for environmental and system state analysis",
                 ["1.1"], TaskStatus.NOT_STARTED, None, None, None, 4.0, 2, ["4.1", "4.4", "5.1"]),
            
            Task("4.2", "Fix Component Health Check Methods",
                 "Update all component health check methods to return accurate status",
                 ["4.1"], TaskStatus.NOT_STARTED, None, None, None, 3.0, 2, ["1.3", "2.5"]),
            
            Task("2", "Fix Test Infrastructure Logging Issues",
                 "Resolve logging permission errors and path issues in test execution",
                 ["2.1", "2.2"], TaskStatus.NOT_STARTED, None, None, None, 1.0, 1, ["1.1", "1.4", "1.5"]),
            
            Task("3", "Implement Missing Tool Orchestration Methods",
                 "Add missing methods to ToolOrchestrator class that are referenced in tests",
                 ["3.1", "3.2", "3.3"], TaskStatus.NOT_STARTED, None, None, None, 1.0, 1, ["2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4", "3.5"]),
            
            Task("4", "Enhance Health Check Accuracy",
                 "Fix health check methods to accurately reflect actual component state",
                 ["4.1", "4.2"], TaskStatus.NOT_STARTED, None, None, None, 1.0, 1, ["1.3", "1.5", "2.5"])
        ]
        
        # Tier 2 - Second Level Dependencies
        tier2_tasks = [
            Task("1", "Enhance RCA Engine with Intelligent Analysis",
                 "Extend existing RCA engine with comprehensive failure analysis capabilities",
                 ["1.1", "1.2", "1.3"], TaskStatus.NOT_STARTED, None, None, None, 1.0, 1, ["4.1", "4.2", "4.3", "4.4", "4.5"]),
            
            Task("5.1", "Implement Automated RCA Triggering",
                 "Create TestFailureMonitor class that automatically detects test failures",
                 ["1"], TaskStatus.NOT_STARTED, None, None, None, 3.5, 1, ["5.1", "5.2"]),
            
            Task("5.2", "Create Failure Categorization System",
                 "Implement FailureCategorizer class for automatic failure type classification",
                 ["1.2"], TaskStatus.NOT_STARTED, None, None, None, 4.0, 1, ["5.2", "5.3"])
        ]
        
        # Continue with remaining tiers...
        tier3_tasks = [
            Task("5.3", "Build Remediation Suggestion Engine",
                 "Create RemediationEngine class for generating actionable fix suggestions",
                 ["5.1", "5.2"], TaskStatus.NOT_STARTED, None, None, None, 4.5, 1, ["5.4", "5.5"]),
            
            Task("6.1", "Create Test Infrastructure Integration Layer",
                 "Implement TestInfrastructureIntegrator class for seamless system integration",
                 ["2", "3", "4"], TaskStatus.NOT_STARTED, None, None, None, 4.0, 2, ["6.1", "6.2", "6.3"])
        ]
        
        tier4_tasks = [
            Task("5", "Create Automated Test Failure Analysis System",
                 "Implement automated RCA triggering on test failures",
                 ["5.1", "5.2", "5.3"], TaskStatus.NOT_STARTED, None, None, None, 1.0, 1, ["5.1", "5.2", "5.3", "5.4", "5.5"]),
            
            Task("6.2", "Enhance Test Validation Suite Integration",
                 "Extend existing test_validation_suite.py with RCA analysis capabilities",
                 ["5", "6.1"], TaskStatus.NOT_STARTED, None, None, None, 3.0, 2, ["6.1", "6.4"]),
            
            Task("7.1", "Create Failure Prevention Rule Engine",
                 "Implement PreventionRuleEngine class for proactive failure prevention",
                 ["5.2"], TaskStatus.NOT_STARTED, None, None, None, 4.0, 2, ["7.1", "7.2"])
        ]
        
        # Add all tasks to the main dictionary
        all_tasks = foundation_tasks + tier1_tasks + tier2_tasks + tier3_tasks + tier4_tasks
        
        for task in all_tasks:
            self.tasks[task.id] = task
    
    def _initialize_agents(self):
        """Initialize available agents"""
        agents = [
            Agent("agent_1", "RCA Specialist", True, None, ["rca", "analysis", "pattern_recognition"], 1),
            Agent("agent_2", "Infrastructure Engineer", True, None, ["logging", "infrastructure", "health_checks"], 1),
            Agent("agent_3", "Tool Orchestration Expert", True, None, ["orchestration", "optimization", "analytics"], 1),
            Agent("agent_4", "Test Framework Developer", True, None, ["testing", "validation", "integration"], 1),
            Agent("agent_5", "System Integration Specialist", True, None, ["integration", "reporting", "deployment"], 1),
            Agent("agent_6", "Quality Assurance Engineer", True, None, ["testing", "validation", "documentation"], 1),
            Agent("agent_7", "DevOps Engineer", True, None, ["deployment", "monitoring", "infrastructure"], 1)
        ]
        
        for agent in agents:
            self.agents[agent.id] = agent
    
    def get_ready_tasks(self) -> List[Task]:
        """Get all tasks that are ready to execute (dependencies met)"""
        ready_tasks = []
        
        for task in self.tasks.values():
            if (task.status == TaskStatus.NOT_STARTED and 
                self._dependencies_met(task)):
                ready_tasks.append(task)
        
        # Sort by priority (1 = highest priority)
        ready_tasks.sort(key=lambda t: (t.priority, -t.estimated_duration_hours))
        return ready_tasks
    
    def _dependencies_met(self, task: Task) -> bool:
        """Check if all dependencies for a task are completed"""
        return all(dep_id in self.completed_tasks for dep_id in task.dependencies)
    
    def _run_git_command(self, command: List[str]) -> tuple[bool, str]:
        """Execute git command and return success status and output"""
        try:
            result = subprocess.run(
                ['git'] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: git {' '.join(command)}")
            self.logger.error(f"Error: {e.stderr}")
            return False, e.stderr.strip()
    
    def _get_current_branch(self) -> Optional[str]:
        """Get the current git branch"""
        success, output = self._run_git_command(['branch', '--show-current'])
        return output if success else None
    
    def _generate_session_branch_name(self) -> str:
        """Generate a unique session branch name"""
        if self.specified_branch:
            return self.specified_branch
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        session_id = str(uuid.uuid4())[:8]
        return f"task-session-{timestamp}-{session_id}"
    
    def _create_session_branch(self) -> bool:
        """Create and switch to a new session branch"""
        try:
            # Get current branch
            original_branch = self._get_current_branch()
            if not original_branch:
                self.logger.error("Could not determine current branch")
                return False
            
            # Generate branch name
            branch_name = self._generate_session_branch_name()
            
            # Pull latest changes on current branch
            self.logger.info(f"Pulling latest changes on {original_branch}")
            success, _ = self._run_git_command(['pull', 'origin', original_branch])
            if not success:
                self.logger.warning("Failed to pull latest changes, continuing anyway")
            
            # Create new branch
            self.logger.info(f"Creating session branch: {branch_name}")
            success, _ = self._run_git_command(['checkout', '-b', branch_name])
            if not success:
                return False
            
            # Create git session
            self.git_session = GitSession(
                session_id=str(uuid.uuid4()),
                branch_name=branch_name,
                original_branch=original_branch,
                created_at=datetime.now()
            )
            
            # Update health indicators
            self._update_health_indicator(
                "git_session",
                HealthStatus.HEALTHY,
                branch_name,
                f"Git session created on branch: {branch_name}"
            )
            
            self.execution_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'session_branch_created',
                'branch_name': branch_name,
                'original_branch': original_branch
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create session branch: {e}")
            return False
    
    def _commit_changes(self, message: str) -> bool:
        """Commit current changes"""
        try:
            # Check if there are changes to commit
            success, output = self._run_git_command(['status', '--porcelain'])
            if not success or not output.strip():
                self.logger.info("No changes to commit")
                return True
            
            # Add all changes
            success, _ = self._run_git_command(['add', '.'])
            if not success:
                return False
            
            # Commit changes
            success, _ = self._run_git_command(['commit', '-m', message])
            if success and self.git_session:
                self.git_session.changes_made = True
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to commit changes: {e}")
            return False
    
    def _push_session_branch(self) -> bool:
        """Push session branch to remote"""
        if not self.git_session:
            return False
        
        try:
            success, _ = self._run_git_command(['push', 'origin', self.git_session.branch_name])
            if success:
                self.execution_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'session_branch_pushed',
                    'branch_name': self.git_session.branch_name
                })
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to push session branch: {e}")
            return False
    
    def _merge_session_branch(self) -> bool:
        """Merge session branch back to original branch"""
        if not self.git_session or not self.git_session.changes_made:
            self.logger.info("No changes to merge")
            return True
        
        try:
            # Switch back to original branch
            success, _ = self._run_git_command(['checkout', self.git_session.original_branch])
            if not success:
                return False
            
            # Pull latest changes
            success, _ = self._run_git_command(['pull', 'origin', self.git_session.original_branch])
            if not success:
                self.logger.warning("Failed to pull latest changes before merge")
            
            # Merge session branch
            success, _ = self._run_git_command(['merge', self.git_session.branch_name])
            if not success:
                self.logger.error("Merge failed - manual intervention required")
                return False
            
            # Push merged changes
            success, _ = self._run_git_command(['push', 'origin', self.git_session.original_branch])
            if success:
                self.execution_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'session_branch_merged',
                    'branch_name': self.git_session.branch_name,
                    'target_branch': self.git_session.original_branch
                })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to merge session branch: {e}")
            return False
    
    def _cleanup_session_branch(self) -> bool:
        """Delete the session branch after successful merge"""
        if not self.git_session:
            return True
        
        try:
            # Delete local branch
            success, _ = self._run_git_command(['branch', '-d', self.git_session.branch_name])
            if not success:
                self.logger.warning(f"Failed to delete local branch {self.git_session.branch_name}")
            
            # Delete remote branch
            success, _ = self._run_git_command(['push', 'origin', '--delete', self.git_session.branch_name])
            if not success:
                self.logger.warning(f"Failed to delete remote branch {self.git_session.branch_name}")
            
            self.execution_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'session_branch_cleaned_up',
                'branch_name': self.git_session.branch_name
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup session branch: {e}")
            return False
    
    def _revert_session_changes(self) -> bool:
        """Revert all changes and return to original branch"""
        if not self.git_session:
            return True
        
        try:
            # Switch back to original branch
            success, _ = self._run_git_command(['checkout', self.git_session.original_branch])
            if not success:
                return False
            
            # Delete session branch (force delete to discard changes)
            success, _ = self._run_git_command(['branch', '-D', self.git_session.branch_name])
            if not success:
                self.logger.warning(f"Failed to force delete branch {self.git_session.branch_name}")
            
            # Delete remote branch if it was pushed
            if self.git_session.changes_made:
                success, _ = self._run_git_command(['push', 'origin', '--delete', self.git_session.branch_name])
                if not success:
                    self.logger.warning(f"Failed to delete remote branch {self.git_session.branch_name}")
            
            self.execution_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'session_changes_reverted',
                'branch_name': self.git_session.branch_name
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revert session changes: {e}")
            return False
    
    def get_available_agents(self) -> List[Agent]:
        """Get all available agents"""
        return [agent for agent in self.agents.values() if agent.is_available]
    
    def assign_task_to_agent(self, task: Task, agent: Agent) -> bool:
        """Assign a task to an agent"""
        if not agent.is_available:
            return False
        
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_agent = agent.id
        task.start_time = datetime.now()
        
        agent.is_available = False
        agent.current_task = task.id
        
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "task_assigned",
            "task_id": task.id,
            "task_name": task.name,
            "agent_id": agent.id,
            "agent_name": agent.name
        })
        
        self.logger.info(f"Assigned task {task.id} ({task.name}) to agent {agent.id} ({agent.name})")
        return True
    
    def complete_task(self, task_id: str, success: bool = True) -> bool:
        """Mark a task as completed and free up the agent"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        agent_id = task.assigned_agent
        
        if success:
            task.status = TaskStatus.COMPLETED
            task.completion_time = datetime.now()
            self.completed_tasks.add(task_id)
            
            # Update health indicators
            completion_rate = len(self.completed_tasks) / len(self.tasks) * 100
            self._update_health_indicator(
                "task_completion",
                HealthStatus.HEALTHY if completion_rate > 80 else HealthStatus.DEGRADED,
                completion_rate,
                f"Task completion rate: {completion_rate:.1f}%"
            )
            
            # Commit changes for completed task
            commit_msg = f"Complete task {task_id}: {task.name}"
            if self._commit_changes(commit_msg):
                self.logger.info(f"Committed changes for task {task_id}")
            
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": "task_completed",
                "task_id": task.id,
                "task_name": task.name,
                "agent_id": agent_id,
                "duration_hours": (task.completion_time - task.start_time).total_seconds() / 3600
            })
            
            self.logger.info(f"Task {task_id} ({task.name}) completed successfully")
        else:
            task.status = TaskStatus.FAILED
            self.failed_tasks.add(task_id)
            
            # Update health indicators for failures
            failure_rate = len(self.failed_tasks) / len(self.tasks) * 100
            self._update_health_indicator(
                "task_failures",
                HealthStatus.UNHEALTHY if failure_rate > 20 else HealthStatus.DEGRADED,
                failure_rate,
                f"Task failure rate: {failure_rate:.1f}%"
            )
            
            # Commit failed state for tracking
            commit_msg = f"Task {task_id} failed: {task.name}"
            if self._commit_changes(commit_msg):
                self.logger.info(f"Committed failed state for task {task_id}")
            
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": "task_failed",
                "task_id": task.id,
                "task_name": task.name,
                "agent_id": agent_id
            })
            
            self.logger.error(f"Task {task_id} ({task.name}) failed")
        
        # Free up the agent
        if agent_id and agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.is_available = True
            agent.current_task = None
        
        return True
    
    def recursive_task_execution(self) -> Dict:
        """
        Recursive descent task execution with dependency resolution
        Returns execution summary
        """
        execution_start = datetime.now()
        iteration = 0
        
        # Initialize Git session
        if not self._create_session_branch():
            return {
                "error": "Failed to create session branch",
                "execution_start": execution_start.isoformat(),
                "execution_end": datetime.now().isoformat(),
                "success": False
            }
        
        self.logger.info(f"Starting recursive task execution in branch: {self.git_session.branch_name}")
        
        try:
            while True:
                iteration += 1
                self.logger.info(f"Execution iteration {iteration}")
                
                # Get tasks ready for execution
                ready_tasks = self.get_ready_tasks()
                available_agents = self.get_available_agents()
                
                if not ready_tasks:
                    # Check if we're done or blocked
                    remaining_tasks = [t for t in self.tasks.values() 
                                     if t.status in [TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS]]
                    
                    if not remaining_tasks:
                        self.logger.info("All tasks completed!")
                        break
                    elif not any(t.status == TaskStatus.IN_PROGRESS for t in remaining_tasks):
                        self.logger.warning("No ready tasks and no tasks in progress - possible deadlock")
                        break
                    else:
                        self.logger.info("Waiting for in-progress tasks to complete...")
                        # In a real implementation, this would wait for task completion events
                        break
                
                if not available_agents:
                    self.logger.info("No available agents - waiting for task completions")
                    break
                
                # Assign tasks to agents
                assignments_made = 0
                for task in ready_tasks:
                    if not available_agents:
                        break
                    
                    # Find best agent for this task (simple capability matching)
                    best_agent = self._find_best_agent(task, available_agents)
                    
                    if best_agent and self.assign_task_to_agent(task, best_agent):
                        available_agents.remove(best_agent)
                        assignments_made += 1
                
                if assignments_made == 0:
                    self.logger.info("No task assignments made this iteration")
                    break
                
                self.logger.info(f"Made {assignments_made} task assignments in iteration {iteration}")
        
        except Exception as e:
            self.logger.error(f"Error during task execution: {e}")
            execution_end = datetime.now()
            return {
                "error": str(e),
                "execution_start": execution_start.isoformat(),
                "execution_end": execution_end.isoformat(),
                "success": False
            }
        
        # Generate execution summary
        execution_end = datetime.now()
        total_duration = (execution_end - execution_start).total_seconds()
        
        # Commit final changes
        if self.git_session and self.git_session.changes_made:
            commit_msg = f"Task execution session completed - {len(self.completed_tasks)}/{len(self.tasks)} tasks completed"
            self._commit_changes(commit_msg)
            self._push_session_branch()
        
        # Determine if execution was successful
        success_rate = len(self.completed_tasks) / len(self.tasks) * 100
        execution_successful = success_rate >= 80  # Consider 80%+ completion as success
        
        # Handle Git session cleanup
        if self.auto_merge and execution_successful:
            merge_success = self._merge_session_branch()
            if merge_success:
                self._cleanup_session_branch()
                git_status = "merged_and_cleaned"
            else:
                git_status = "merge_failed"
        elif self.auto_revert_on_failure and not execution_successful:
            self._revert_session_changes()
            git_status = "reverted"
        else:
            git_status = "branch_preserved"
            
        summary = {
            "execution_start": execution_start.isoformat(),
            "execution_end": execution_end.isoformat(),
            "total_duration_seconds": total_duration,
            "iterations": iteration,
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "in_progress_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            "not_started_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.NOT_STARTED]),
            "completion_rate": success_rate,
            "execution_successful": execution_successful,
            "git_session": {
                "branch_name": self.git_session.branch_name if self.git_session else None,
                "original_branch": self.git_session.original_branch if self.git_session else None,
                "status": git_status,
                "changes_made": self.git_session.changes_made if self.git_session else False
            },
            "execution_log": self.execution_log
        }
        
        return summary
    
    def _find_best_agent(self, task: Task, available_agents: List[Agent]) -> Optional[Agent]:
        """Find the best agent for a task based on capabilities"""
        if not available_agents:
            return None
        
        # Simple scoring based on capability match
        scored_agents = []
        
        for agent in available_agents:
            score = 0
            
            # Check capability matches (this is a simplified example)
            task_keywords = task.name.lower().split()
            for capability in agent.capabilities:
                if any(keyword in capability.lower() or capability.lower() in keyword 
                       for keyword in task_keywords):
                    score += 1
            
            scored_agents.append((agent, score))
        
        # Sort by score (highest first), then by agent availability
        scored_agents.sort(key=lambda x: (-x[1], x[0].id))
        
        return scored_agents[0][0] if scored_agents else available_agents[0]
    
    def get_execution_status(self) -> Dict:
        """Get current execution status"""
        return {
            "total_tasks": len(self.tasks),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "in_progress": len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            "not_started": len([t for t in self.tasks.values() if t.status == TaskStatus.NOT_STARTED]),
            "blocked": len([t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED]),
            "ready_tasks": len(self.get_ready_tasks()),
            "available_agents": len(self.get_available_agents())
        }
    
    def print_execution_plan(self):
        """Print the current execution plan"""
        print("\n🚀 TASK EXECUTION PLAN")
        print("=" * 50)
        
        # Group tasks by tier based on dependency depth
        tiers = self._calculate_task_tiers()
        
        for tier_num in sorted(tiers.keys()):
            print(f"\n📋 TIER {tier_num} - {len(tiers[tier_num])} tasks")
            print("-" * 30)
            
            for task_id in tiers[tier_num]:
                task = self.tasks[task_id]
                deps_str = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else " (no dependencies)"
                print(f"  • {task.id}: {task.name}{deps_str}")
        
        print(f"\n📊 EXECUTION SUMMARY")
        print("-" * 30)
        status = self.get_execution_status()
        for key, value in status.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    def _calculate_task_tiers(self) -> Dict[int, List[str]]:
        """Calculate task tiers based on dependency depth"""
        tiers = {}
        visited = set()
        
        def get_tier(task_id: str) -> int:
            if task_id in visited:
                return 0  # Avoid cycles
            
            visited.add(task_id)
            task = self.tasks[task_id]
            
            if not task.dependencies:
                return 0
            
            max_dep_tier = max(get_tier(dep_id) for dep_id in task.dependencies)
            return max_dep_tier + 1
        
        for task_id in self.tasks:
            visited.clear()
            tier = get_tier(task_id)
            
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(task_id)
        
        return tiers
    
    # RM Interface Implementation (Required for Beast Mode Framework compliance)
    
    def get_module_status(self) -> Dict[str, Any]:
        """
        Operational visibility - external status reporting for GKE queries
        Required by R6.4 - external systems get accurate operational information
        """
        execution_status = self.get_execution_status()
        
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "task_execution": execution_status,
            "git_session": {
                "active": self.git_session is not None,
                "branch_name": self.git_session.branch_name if self.git_session else None,
                "changes_made": self.git_session.changes_made if self.git_session else False
            },
            "agent_pool": {
                "total_agents": len(self.agents),
                "available_agents": len(self.get_available_agents()),
                "busy_agents": len([a for a in self.agents.values() if not a.is_available])
            },
            "health_indicators": {name: indicator.status.value for name, indicator in self._health_indicators.items()},
            "last_updated": datetime.now().isoformat()
        }
    
    def is_healthy(self) -> bool:
        """
        Self-monitoring - accurate health assessment
        Required by R6.2 - components report health status accurately
        """
        # Check if any critical health indicators are unhealthy
        critical_indicators = ["engine_status", "task_definitions", "agent_pool"]
        
        for indicator_name in critical_indicators:
            if indicator_name in self._health_indicators:
                indicator = self._health_indicators[indicator_name]
                if indicator.status in [HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]:
                    return False
        
        # Check for execution errors
        if len(self.failed_tasks) > len(self.completed_tasks):
            return False
        
        # Check Git session health if active
        if self.git_session and not self.git_session.is_active:
            return False
        
        return True
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """
        Self-reporting - detailed health metrics for operational visibility
        Required by R6.2 - components report health status accurately
        """
        indicators = {}
        
        for name, indicator in self._health_indicators.items():
            indicators[name] = {
                "status": indicator.status.value,
                "value": indicator.value,
                "message": indicator.message,
                "timestamp": indicator.timestamp
            }
        
        # Add dynamic health metrics
        indicators["execution_health"] = {
            "status": "healthy" if len(self.failed_tasks) == 0 else "degraded",
            "value": {
                "success_rate": len(self.completed_tasks) / max(len(self.tasks), 1) * 100,
                "failure_rate": len(self.failed_tasks) / max(len(self.tasks), 1) * 100,
                "completion_rate": (len(self.completed_tasks) + len(self.failed_tasks)) / max(len(self.tasks), 1) * 100
            },
            "message": f"Completed: {len(self.completed_tasks)}, Failed: {len(self.failed_tasks)}, Total: {len(self.tasks)}",
            "timestamp": time.time()
        }
        
        indicators["git_session_health"] = {
            "status": "healthy" if not self.git_session or self.git_session.is_active else "degraded",
            "value": {
                "session_active": self.git_session is not None,
                "branch_name": self.git_session.branch_name if self.git_session else None,
                "changes_made": self.git_session.changes_made if self.git_session else False
            },
            "message": "Git session operational" if not self.git_session or self.git_session.is_active else "Git session inactive",
            "timestamp": time.time()
        }
        
        return indicators
    
    def _get_primary_responsibility(self) -> str:
        """
        Define the single primary responsibility of this module
        Required by RM interface for single responsibility validation
        """
        return "Recursive descent task execution with dependency resolution and Git branch management"
    
    def _update_health_indicator(self, name: str, status: HealthStatus, value: Any, message: str):
        """Update a health indicator with current status"""
        import time
        self._health_indicators[name] = HealthIndicator(
            name=name,
            status=status,
            value=value,
            message=message,
            timestamp=time.time()
        )

def main():
    """Main execution function with CLI arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Task Execution Engine with Recursive Descent Dependency Resolution')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze dependencies, don\'t execute')
    parser.add_argument('--execute', action='store_true', help='Execute tasks with dependency resolution')
    parser.add_argument('--output-json', help='Output execution results to JSON file')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create the task execution engine
    engine = TaskExecutionEngine()
    
    if args.analyze_only:
        print("\n🔍 DEPENDENCY ANALYSIS MODE")
        print("=" * 50)
        engine.print_execution_plan()
        
        # Save dependency analysis to file
        tiers = engine._calculate_task_tiers()
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(engine.tasks),
            "tier_count": len(tiers),
            "tiers": {str(k): v for k, v in tiers.items()},
            "critical_path_length": max(tiers.keys()) if tiers else 0,
            "max_parallelism": max(len(tasks) for tasks in tiers.values()) if tiers else 0
        }
        
        with open('task-dependency-analysis.json', 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\n💾 Dependency analysis saved to: task-dependency-analysis.json")
        return
    
    # Print the execution plan
    engine.print_execution_plan()
    
    if args.execute:
        print("\n🎯 STARTING TASK EXECUTION")
        print("=" * 50)
        
        # Execute tasks with dependency resolution
        summary = engine.recursive_task_execution()
        
        print(f"\n📈 EXECUTION RESULTS")
        print("-" * 30)
        print(f"Total Duration: {summary['total_duration_seconds']:.2f} seconds")
        print(f"Iterations: {summary['iterations']}")
        print(f"Completion Rate: {summary['completion_rate']:.1f}%")
        print(f"Tasks Assigned: {len([log for log in summary['execution_log'] if log['action'] == 'task_assigned'])}")
        
        # Show current status
        print(f"\n📊 CURRENT STATUS")
        print("-" * 30)
        status = engine.get_execution_status()
        for key, value in status.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Save execution results
        output_file = args.output_json or f"execution-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n💾 Execution results saved to: {output_file}")
    else:
        print("\n💡 Use --execute to run task execution or --analyze-only for dependency analysis")
        print("   Example: make execute-tasks")

if __name__ == "__main__":
    main()