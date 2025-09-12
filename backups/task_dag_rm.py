"""
Beast Mode Framework - Task DAG Reflective Module
Standard RM for task dependency analysis and execution across all specs
"""

import json
import re
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

from ..core.reflective_module import ReflectiveModule, HealthStatus


class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskNode:
    """Represents a task in the DAG"""
    id: str
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    estimated_hours: float = 4.0
    priority: int = 1  # 1=highest, 10=lowest
    status: TaskStatus = TaskStatus.NOT_STARTED
    tier: int = 0  # Calculated dependency depth


@dataclass
class Agent:
    """Represents an available agent/worker"""
    id: str
    name: str
    capabilities: List[str] = field(default_factory=list)
    is_available: bool = True
    current_task: Optional[str] = None


@dataclass
class DAGAnalysis:
    """Results of DAG analysis"""
    total_tasks: int
    tier_count: int
    critical_path_length: int
    max_parallelism: int
    tiers: Dict[int, List[str]]
    ready_tasks: List[str]
    blocked_tasks: List[str]
    completion_rate: float


class TaskDAGRM(ReflectiveModule):
    """
    Reflective Module for Task DAG Discovery and Execution
    
    Provides standardized task dependency analysis and execution
    capabilities for any spec with a tasks.md file.
    """
    
    def __init__(self, spec_path: str = None):
        super().__init__("task_dag_rm")
        
        self.spec_path = Path(spec_path) if spec_path else Path(".")
        self.tasks: Dict[str, TaskNode] = {}
        self.agents: Dict[str, Agent] = {}
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.execution_log: List[Dict] = []
        
        # Initialize default agents
        self._initialize_default_agents()
        
        # Load tasks if spec path provided
        if spec_path:
            self.load_tasks_from_spec()
        
        self._update_health_indicator(
            "task_dag_rm",
            HealthStatus.HEALTHY,
            "operational",
            "Task DAG RM ready for dependency analysis and execution"
        )
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get task DAG RM operational status"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "spec_path": str(self.spec_path),
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "available_agents": len([a for a in self.agents.values() if a.is_available]),
            "ready_tasks": len(self.get_ready_tasks())
        }
    
    def is_healthy(self) -> bool:
        """Health assessment for task DAG RM"""
        return (
            len(self.tasks) > 0 and
            len(self.agents) > 0 and
            not self._degradation_active
        )
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for task DAG RM"""
        dag_analysis = self.analyze_dag()
        
        return {
            "task_analysis": {
                "total_tasks": dag_analysis.total_tasks,
                "tier_count": dag_analysis.tier_count,
                "critical_path_length": dag_analysis.critical_path_length,
                "max_parallelism": dag_analysis.max_parallelism,
                "completion_rate": dag_analysis.completion_rate
            },
            "execution_status": {
                "ready_tasks": len(dag_analysis.ready_tasks),
                "blocked_tasks": len(dag_analysis.blocked_tasks),
                "available_agents": len([a for a in self.agents.values() if a.is_available])
            },
            "system_health": {
                "spec_loaded": len(self.tasks) > 0,
                "agents_available": len(self.agents) > 0,
                "dag_valid": self._validate_dag()
            }
        }
    
    def _get_primary_responsibility(self) -> str:
        """Primary responsibility of this RM"""
        return "task_dependency_analysis_and_execution"
    
    def load_tasks_from_spec(self, spec_path: str = None) -> bool:
        """
        Load tasks from a spec's tasks.md file
        
        Args:
            spec_path: Path to spec directory (uses self.spec_path if None)
            
        Returns:
            bool: True if tasks loaded successfully
        """
        if spec_path:
            self.spec_path = Path(spec_path)
        
        tasks_file = self.spec_path / "tasks.md"
        
        if not tasks_file.exists():
            self.logger.error(f"Tasks file not found: {tasks_file}")
            return False
        
        try:
            content = tasks_file.read_text()
            self.tasks = self._parse_tasks_markdown(content)
            self._calculate_task_tiers()
            
            self.logger.info(f"Loaded {len(self.tasks)} tasks from {tasks_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load tasks from {tasks_file}: {e}")
            return False
    
    def _parse_tasks_markdown(self, content: str) -> Dict[str, TaskNode]:
        """
        Parse tasks from markdown content
        
        Expected format:
        - [ ] 1. Task Name
          - Description
          - _Requirements: req1, req2_
        
        - [ ] 1.1 Subtask Name
          - Subtask description
          - _Requirements: req3_
        """
        tasks = {}
        current_task = None
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Match task headers: - [ ] 1.1 Task Name
            task_match = re.match(r'^-\s*\[\s*[x\s]\s*\]\s*(\d+(?:\.\d+)*)\s+(.+)$', line)
            if task_match:
                task_id = task_match.group(1)
                task_name = task_match.group(2)
                
                current_task = TaskNode(
                    id=task_id,
                    name=task_name,
                    description="",
                    dependencies=self._extract_dependencies(task_id),
                    requirements=[],
                    estimated_hours=4.0,
                    priority=1
                )
                tasks[task_id] = current_task
                continue
            
            # Match requirements: _Requirements: req1, req2_
            req_match = re.match(r'^_Requirements:\s*(.+)_$', line)
            if req_match and current_task:
                reqs = [r.strip() for r in req_match.group(1).split(',')]
                current_task.requirements = reqs
                continue
            
            # Add description lines
            if current_task and line and not line.startswith('-') and not line.startswith('_'):
                if current_task.description:
                    current_task.description += " " + line
                else:
                    current_task.description = line
        
        return tasks
    
    def _extract_dependencies(self, task_id: str) -> List[str]:
        """
        Extract dependencies based on task ID hierarchy
        
        Examples:
        - 1.1 depends on 1
        - 2.3 depends on 2.1, 2.2 (if they exist)
        - 5 depends on 5.1, 5.2, 5.3 (if they exist)
        """
        dependencies = []
        
        # Handle hierarchical dependencies
        if '.' in task_id:
            # Subtask depends on parent
            parent_id = '.'.join(task_id.split('.')[:-1])
            dependencies.append(parent_id)
        else:
            # Parent task depends on all its subtasks
            # This will be resolved after all tasks are parsed
            pass
        
        return dependencies
    
    def _resolve_parent_dependencies(self):
        """Resolve parent task dependencies on their subtasks"""
        for task_id, task in self.tasks.items():
            if '.' not in task_id:  # Parent task
                subtasks = [tid for tid in self.tasks.keys() if tid.startswith(f"{task_id}.")]
                if subtasks:
                    task.dependencies = subtasks
    
    def _calculate_task_tiers(self):
        """Calculate tier (dependency depth) for each task"""
        # First resolve parent dependencies
        self._resolve_parent_dependencies()
        
        # Calculate tiers using topological sort
        visited = set()
        
        def calculate_tier(task_id: str) -> int:
            if task_id in visited:
                return 0  # Avoid cycles
            
            visited.add(task_id)
            
            if task_id not in self.tasks:
                return 0
            
            task = self.tasks[task_id]
            
            if not task.dependencies:
                task.tier = 0
                return 0
            
            max_dep_tier = 0
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    dep_tier = calculate_tier(dep_id)
                    max_dep_tier = max(max_dep_tier, dep_tier)
            
            task.tier = max_dep_tier + 1
            return task.tier
        
        for task_id in self.tasks:
            visited.clear()
            calculate_tier(task_id)
    
    def _initialize_default_agents(self):
        """Initialize default agents for task execution"""
        default_agents = [
            Agent("agent_1", "Full-Stack Developer", ["development", "testing", "integration"]),
            Agent("agent_2", "Infrastructure Engineer", ["infrastructure", "deployment", "monitoring"]),
            Agent("agent_3", "Quality Assurance Engineer", ["testing", "validation", "documentation"]),
            Agent("agent_4", "DevOps Specialist", ["automation", "deployment", "optimization"]),
            Agent("agent_5", "System Architect", ["design", "architecture", "integration"]),
        ]
        
        for agent in default_agents:
            self.agents[agent.id] = agent
    
    def analyze_dag(self) -> DAGAnalysis:
        """
        Analyze the task DAG and return comprehensive analysis
        
        Returns:
            DAGAnalysis: Complete analysis of the task dependency graph
        """
        if not self.tasks:
            return DAGAnalysis(0, 0, 0, 0, {}, [], [], 0.0)
        
        # Group tasks by tier
        tiers = {}
        for task in self.tasks.values():
            tier = task.tier
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(task.id)
        
        # Calculate metrics
        total_tasks = len(self.tasks)
        tier_count = len(tiers)
        critical_path_length = max(tiers.keys()) if tiers else 0
        max_parallelism = max(len(task_list) for task_list in tiers.values()) if tiers else 0
        
        # Get ready and blocked tasks
        ready_tasks = self.get_ready_tasks()
        blocked_tasks = self.get_blocked_tasks()
        
        # Calculate completion rate
        completion_rate = len(self.completed_tasks) / total_tasks * 100 if total_tasks > 0 else 0.0
        
        return DAGAnalysis(
            total_tasks=total_tasks,
            tier_count=tier_count,
            critical_path_length=critical_path_length,
            max_parallelism=max_parallelism,
            tiers=tiers,
            ready_tasks=[t.id for t in ready_tasks],
            blocked_tasks=blocked_tasks,
            completion_rate=completion_rate
        )
    
    def get_ready_tasks(self) -> List[TaskNode]:
        """Get all tasks that are ready to execute (dependencies met)"""
        ready_tasks = []
        
        for task in self.tasks.values():
            if (task.status == TaskStatus.NOT_STARTED and 
                self._dependencies_met(task)):
                ready_tasks.append(task)
        
        # Sort by priority and tier
        ready_tasks.sort(key=lambda t: (t.priority, t.tier, -t.estimated_hours))
        return ready_tasks
    
    def get_blocked_tasks(self) -> List[str]:
        """Get tasks that are blocked by failed dependencies"""
        blocked_tasks = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.NOT_STARTED:
                # Check if any dependencies failed
                for dep_id in task.dependencies:
                    if dep_id in self.failed_tasks:
                        blocked_tasks.append(task.id)
                        break
        
        return blocked_tasks
    
    def _dependencies_met(self, task: TaskNode) -> bool:
        """Check if all dependencies for a task are completed"""
        return all(dep_id in self.completed_tasks for dep_id in task.dependencies)
    
    def _validate_dag(self) -> bool:
        """Validate that the DAG has no cycles"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: str) -> bool:
            if task_id in rec_stack:
                return True
            if task_id in visited:
                return False
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            if task_id in self.tasks:
                for dep_id in self.tasks[task_id].dependencies:
                    if has_cycle(dep_id):
                        return True
            
            rec_stack.remove(task_id)
            return False
        
        for task_id in self.tasks:
            if task_id not in visited:
                if has_cycle(task_id):
                    return False
        
        return True
    
    def print_dag_analysis(self):
        """Print comprehensive DAG analysis"""
        analysis = self.analyze_dag()
        
        print("\n🚀 TASK DAG ANALYSIS")
        print("=" * 50)
        
        # Print tiers
        for tier_num in sorted(analysis.tiers.keys()):
            tasks_in_tier = analysis.tiers[tier_num]
            print(f"\n📋 TIER {tier_num} - {len(tasks_in_tier)} tasks")
            print("-" * 30)
            
            for task_id in tasks_in_tier:
                task = self.tasks[task_id]
                deps_str = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else " (no dependencies)"
                status_icon = self._get_status_icon(task.status)
                print(f"  {status_icon} {task.id}: {task.name}{deps_str}")
        
        # Print summary
        print(f"\n📊 DAG SUMMARY")
        print("-" * 30)
        print(f"  Total Tasks: {analysis.total_tasks}")
        print(f"  Tier Count: {analysis.tier_count}")
        print(f"  Critical Path Length: {analysis.critical_path_length}")
        print(f"  Max Parallelism: {analysis.max_parallelism}")
        print(f"  Completion Rate: {analysis.completion_rate:.1f}%")
        print(f"  Ready Tasks: {len(analysis.ready_tasks)}")
        print(f"  Blocked Tasks: {len(analysis.blocked_tasks)}")
    
    def _get_status_icon(self, status: TaskStatus) -> str:
        """Get icon for task status"""
        icons = {
            TaskStatus.NOT_STARTED: "⚪",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.BLOCKED: "🚫"
        }
        return icons.get(status, "❓")
    
    def execute_recursive_descent(self, simulate: bool = True) -> Dict[str, Any]:
        """
        Execute tasks using recursive descent with dependency resolution
        
        Args:
            simulate: If True, simulate task completion for demonstration
            
        Returns:
            Dict: Execution summary with results and metrics
        """
        execution_start = datetime.now()
        iteration = 0
        
        self.logger.info("Starting recursive descent task execution...")
        
        while True:
            iteration += 1
            self.logger.info(f"Execution iteration {iteration}")
            
            # Get tasks ready for execution
            ready_tasks = self.get_ready_tasks()
            available_agents = [a for a in self.agents.values() if a.is_available]
            
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
                    if simulate:
                        # In simulation, complete some in-progress tasks
                        self._simulate_task_completions()
                    break
            
            if not available_agents:
                self.logger.info("No available agents - waiting for task completions")
                if simulate:
                    self._simulate_task_completions()
                break
            
            # Assign tasks to agents
            assignments_made = 0
            for task in ready_tasks:
                if not available_agents:
                    break
                
                # Find best agent for this task
                best_agent = self._find_best_agent(task, available_agents)
                
                if best_agent and self._assign_task_to_agent(task, best_agent):
                    available_agents.remove(best_agent)
                    assignments_made += 1
            
            if assignments_made == 0:
                self.logger.info("No task assignments made this iteration")
                break
            
            self.logger.info(f"Made {assignments_made} task assignments in iteration {iteration}")
            
            # In simulation mode, complete tasks immediately
            if simulate:
                self._simulate_task_completions()
        
        # Generate execution summary
        execution_end = datetime.now()
        total_duration = (execution_end - execution_start).total_seconds()
        
        analysis = self.analyze_dag()
        
        summary = {
            "execution_start": execution_start.isoformat(),
            "execution_end": execution_end.isoformat(),
            "total_duration_seconds": total_duration,
            "iterations": iteration,
            "dag_analysis": {
                "total_tasks": analysis.total_tasks,
                "completed_tasks": len(self.completed_tasks),
                "failed_tasks": len(self.failed_tasks),
                "completion_rate": analysis.completion_rate,
                "critical_path_length": analysis.critical_path_length,
                "max_parallelism": analysis.max_parallelism
            },
            "execution_log": self.execution_log
        }
        
        return summary
    
    def _find_best_agent(self, task: TaskNode, available_agents: List[Agent]) -> Optional[Agent]:
        """Find the best agent for a task based on capabilities"""
        if not available_agents:
            return None
        
        # Simple scoring based on capability match
        scored_agents = []
        
        for agent in available_agents:
            score = 0
            
            # Check capability matches
            task_keywords = task.name.lower().split()
            for capability in agent.capabilities:
                if any(keyword in capability.lower() or capability.lower() in keyword 
                       for keyword in task_keywords):
                    score += 1
            
            scored_agents.append((agent, score))
        
        # Sort by score (highest first)
        scored_agents.sort(key=lambda x: (-x[1], x[0].id))
        
        return scored_agents[0][0] if scored_agents else available_agents[0]
    
    def _assign_task_to_agent(self, task: TaskNode, agent: Agent) -> bool:
        """Assign a task to an agent"""
        if not agent.is_available:
            return False
        
        task.status = TaskStatus.IN_PROGRESS
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
    
    def _simulate_task_completions(self):
        """Simulate completion of in-progress tasks"""
        import random
        
        in_progress_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
        
        if in_progress_tasks:
            # Randomly complete 1-3 tasks
            to_complete = random.sample(in_progress_tasks, min(3, len(in_progress_tasks)))
            
            for task in to_complete:
                self._complete_task(task.id, success=True)
    
    def _complete_task(self, task_id: str, success: bool = True):
        """Mark a task as completed and free up the agent"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if success:
            task.status = TaskStatus.COMPLETED
            self.completed_tasks.add(task_id)
            
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": "task_completed",
                "task_id": task.id,
                "task_name": task.name
            })
            
            self.logger.info(f"Task {task_id} ({task.name}) completed successfully")
        else:
            task.status = TaskStatus.FAILED
            self.failed_tasks.add(task_id)
            
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": "task_failed",
                "task_id": task.id,
                "task_name": task.name
            })
            
            self.logger.error(f"Task {task_id} ({task.name}) failed")
        
        # Free up the agent
        for agent in self.agents.values():
            if agent.current_task == task_id:
                agent.is_available = True
                agent.current_task = None
                break
        
        return True
    
    def export_dag_analysis(self, output_file: str = None) -> str:
        """
        Export DAG analysis to JSON file
        
        Args:
            output_file: Output file path (auto-generated if None)
            
        Returns:
            str: Path to exported file
        """
        analysis = self.analyze_dag()
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "spec_path": str(self.spec_path),
            "dag_analysis": {
                "total_tasks": analysis.total_tasks,
                "tier_count": analysis.tier_count,
                "critical_path_length": analysis.critical_path_length,
                "max_parallelism": analysis.max_parallelism,
                "completion_rate": analysis.completion_rate,
                "tiers": analysis.tiers,
                "ready_tasks": analysis.ready_tasks,
                "blocked_tasks": analysis.blocked_tasks
            },
            "tasks": {
                task_id: {
                    "name": task.name,
                    "description": task.description,
                    "dependencies": task.dependencies,
                    "requirements": task.requirements,
                    "estimated_hours": task.estimated_hours,
                    "priority": task.priority,
                    "status": task.status.value,
                    "tier": task.tier
                }
                for task_id, task in self.tasks.items()
            }
        }
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            output_file = f"dag-analysis-{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"DAG analysis exported to: {output_file}")
        return output_file