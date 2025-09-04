#!/usr/bin/env python3
"""
Task Execution Engine with Recursive Descent Dependency Resolution
Automatically issues independent tasks to agents when dependencies are met
"""

import asyncio
import json
from typing import Dict, List, Set, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

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

class TaskExecutionEngine:
    """
    Recursive descent task execution engine with dependency resolution
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.execution_log: List[Dict] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize task definitions
        self._initialize_tasks()
        self._initialize_agents()
    
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
        
        self.logger.info("Starting recursive task execution...")
        
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
        
        # Generate execution summary
        execution_end = datetime.now()
        total_duration = (execution_end - execution_start).total_seconds()
        
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
            "completion_rate": len(self.completed_tasks) / len(self.tasks) * 100,
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