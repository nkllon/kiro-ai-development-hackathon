#!/usr/bin/env python3
"""
Observatory Cloudflare Infrastructure Governance Orchestrator

This script provides systematic orchestration of the infrastructure governance
implementation tasks, with dependency management, progress tracking, and
automated validation.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Task:
    id: str
    name: str
    description: str
    dependencies: List[str]
    make_target: str
    requirements: List[str]
    estimated_duration: int  # minutes
    priority: TaskPriority
    phase: int
    status: TaskStatus = TaskStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

@dataclass
class OrchestrationState:
    current_phase: int
    total_phases: int
    completed_tasks: int
    total_tasks: int
    start_time: datetime
    estimated_completion: Optional[datetime]
    current_task: Optional[str]

class InfrastructureGovernanceOrchestrator:
    def __init__(self):
        self.tasks = self._define_tasks()
        self.state_file = Path(".make-tasks/infra-governance/orchestration_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()
        
    def _define_tasks(self) -> Dict[str, Task]:
        """Define all infrastructure governance tasks with dependencies and metadata."""
        tasks = {
            # Phase 1: Service Management Foundation
            "1": Task(
                id="1",
                name="Service Management Foundation",
                description="Set up unified service management foundation",
                dependencies=[],
                make_target="infra-task-1",
                requirements=["5.1", "5.2", "5.3"],
                estimated_duration=30,
                priority=TaskPriority.CRITICAL,
                phase=1
            ),
            "2.1": Task(
                id="2.1",
                name="UnifiedServiceManager Lifecycle",
                description="Create UnifiedServiceManager class with lifecycle operations",
                dependencies=["1"],
                make_target="infra-task-2.1",
                requirements=["5.1", "5.2", "5.4"],
                estimated_duration=45,
                priority=TaskPriority.CRITICAL,
                phase=1
            ),
            "2.2": Task(
                id="2.2",
                name="Service Health Monitoring",
                description="Implement service health checking and monitoring",
                dependencies=["2.1"],
                make_target="infra-task-2.2",
                requirements=["5.7", "7.1", "7.2"],
                estimated_duration=40,
                priority=TaskPriority.HIGH,
                phase=1
            ),
            "2.3": Task(
                id="2.3",
                name="Configuration Management",
                description="Add service configuration validation and management",
                dependencies=["2.2"],
                make_target="infra-task-2.3",
                requirements=["6.1", "6.2", "6.5"],
                estimated_duration=35,
                priority=TaskPriority.HIGH,
                phase=1
            ),
            
            # Phase 2: Tunnel Management
            "3.1": Task(
                id="3.1",
                name="TunnelConfigurationManager",
                description="Implement TunnelConfigurationManager with multi-service support",
                dependencies=["2.3"],
                make_target="infra-task-3.1",
                requirements=["1.1", "1.2", "1.3", "1.4"],
                estimated_duration=50,
                priority=TaskPriority.CRITICAL,
                phase=2
            ),
            "3.2": Task(
                id="3.2",
                name="Tunnel Deployment",
                description="Add tunnel deployment and rollback capabilities",
                dependencies=["3.1"],
                make_target="infra-task-3.2",
                requirements=["1.6", "1.7", "6.3", "6.4"],
                estimated_duration=40,
                priority=TaskPriority.HIGH,
                phase=2
            ),
            "3.3": Task(
                id="3.3",
                name="Tunnel Health Monitoring",
                description="Implement tunnel health monitoring and diagnostics",
                dependencies=["3.2"],
                make_target="infra-task-3.3",
                requirements=["7.1", "7.2", "7.3"],
                estimated_duration=35,
                priority=TaskPriority.HIGH,
                phase=2
            ),
            
            # Phase 3: WebSocket Monitoring
            "4.1": Task(
                id="4.1",
                name="WebSocketHealthMonitor",
                description="Create WebSocketHealthMonitor with endpoint testing",
                dependencies=["3.3"],
                make_target="infra-task-4.1",
                requirements=["2.1", "2.2", "2.6"],
                estimated_duration=45,
                priority=TaskPriority.CRITICAL,
                phase=3
            ),
            "4.2": Task(
                id="4.2",
                name="HTTP Polling Fallback",
                description="Implement intelligent HTTP polling fallback system",
                dependencies=["4.1"],
                make_target="infra-task-4.2",
                requirements=["2.3", "2.4", "2.5"],
                estimated_duration=40,
                priority=TaskPriority.HIGH,
                phase=3
            ),
            "4.3": Task(
                id="4.3",
                name="WebSocket Recovery",
                description="Add WebSocket recovery and reconnection logic",
                dependencies=["4.2"],
                make_target="infra-task-4.3",
                requirements=["2.5", "2.6", "2.7"],
                estimated_duration=35,
                priority=TaskPriority.HIGH,
                phase=3
            )
        }
        return tasks
    
    def _load_state(self) -> OrchestrationState:
        """Load orchestration state from file or create new state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return OrchestrationState(
                        current_phase=data.get('current_phase', 1),
                        total_phases=data.get('total_phases', 3),
                        completed_tasks=data.get('completed_tasks', 0),
                        total_tasks=data.get('total_tasks', len(self.tasks)),
                        start_time=datetime.fromisoformat(data['start_time']),
                        estimated_completion=datetime.fromisoformat(data['estimated_completion']) if data.get('estimated_completion') else None,
                        current_task=data.get('current_task')
                    )
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
        
        return OrchestrationState(
            current_phase=1,
            total_phases=3,
            completed_tasks=0,
            total_tasks=len(self.tasks),
            start_time=datetime.now(timezone.utc),
            estimated_completion=None,
            current_task=None
        )
    
    def _save_state(self):
        """Save current orchestration state to file."""
        state_data = {
            'current_phase': self.state.current_phase,
            'total_phases': self.state.total_phases,
            'completed_tasks': self.state.completed_tasks,
            'total_tasks': self.state.total_tasks,
            'start_time': self.state.start_time.isoformat(),
            'estimated_completion': self.state.estimated_completion.isoformat() if self.state.estimated_completion else None,
            'current_task': self.state.current_task
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (dependencies satisfied)."""
        ready_tasks = []
        
        for task in self.tasks.values():
            if task.status != TaskStatus.NOT_STARTED:
                continue
                
            # Check if all dependencies are completed
            dependencies_satisfied = all(
                self.tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
                if dep_id in self.tasks
            )
            
            if dependencies_satisfied:
                ready_tasks.append(task)
        
        # Sort by priority and phase
        ready_tasks.sort(key=lambda t: (t.phase, t.priority.value, t.id))
        return ready_tasks
    
    def execute_task(self, task: Task) -> bool:
        """Execute a single task using Make."""
        print(f"\n🚀 Executing Task {task.id}: {task.name}")
        print(f"📝 Description: {task.description}")
        print(f"🎯 Requirements: {', '.join(task.requirements)}")
        print(f"⏱️  Estimated Duration: {task.estimated_duration} minutes")
        
        task.status = TaskStatus.IN_PROGRESS
        task.start_time = datetime.now(timezone.utc)
        self.state.current_task = task.id
        self._save_state()
        
        try:
            # Execute the Make target
            result = subprocess.run(
                ["make", task.make_target],
                capture_output=True,
                text=True,
                timeout=task.estimated_duration * 60 * 2  # 2x estimated duration timeout
            )
            
            if result.returncode == 0:
                task.status = TaskStatus.COMPLETED
                task.end_time = datetime.now(timezone.utc)
                self.state.completed_tasks += 1
                
                duration = (task.end_time - task.start_time).total_seconds() / 60
                print(f"✅ Task {task.id} completed successfully in {duration:.1f} minutes")
                
                # Update phase if all tasks in current phase are complete
                self._update_phase_progress()
                
                return True
            else:
                task.status = TaskStatus.FAILED
                task.error_message = result.stderr
                print(f"❌ Task {task.id} failed:")
                print(f"   Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            task.status = TaskStatus.FAILED
            task.error_message = f"Task timed out after {task.estimated_duration * 2} minutes"
            print(f"⏰ Task {task.id} timed out")
            return False
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            print(f"💥 Task {task.id} failed with exception: {e}")
            return False
        finally:
            self.state.current_task = None
            self._save_state()
    
    def _update_phase_progress(self):
        """Update current phase based on completed tasks."""
        phase_tasks = {phase: [] for phase in range(1, self.state.total_phases + 1)}
        
        for task in self.tasks.values():
            phase_tasks[task.phase].append(task)
        
        for phase in range(1, self.state.total_phases + 1):
            tasks_in_phase = phase_tasks[phase]
            completed_in_phase = [t for t in tasks_in_phase if t.status == TaskStatus.COMPLETED]
            
            if len(completed_in_phase) == len(tasks_in_phase) and phase > self.state.current_phase:
                self.state.current_phase = phase
                print(f"🎉 Phase {phase} completed! Moving to next phase.")
    
    def estimate_completion_time(self) -> Optional[datetime]:
        """Estimate completion time based on remaining tasks."""
        remaining_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.NOT_STARTED]
        if not remaining_tasks:
            return datetime.now(timezone.utc)
        
        total_remaining_minutes = sum(t.estimated_duration for t in remaining_tasks)
        return datetime.now(timezone.utc) + timedelta(minutes=total_remaining_minutes)
    
    def print_status(self):
        """Print current orchestration status."""
        print("\n" + "="*80)
        print("🏗️  OBSERVATORY CLOUDFLARE INFRASTRUCTURE GOVERNANCE ORCHESTRATION")
        print("="*80)
        
        progress_percentage = (self.state.completed_tasks / self.state.total_tasks) * 100
        print(f"📊 Overall Progress: {self.state.completed_tasks}/{self.state.total_tasks} tasks ({progress_percentage:.1f}%)")
        print(f"🔄 Current Phase: {self.state.current_phase}/{self.state.total_phases}")
        
        if self.state.current_task:
            current_task = self.tasks[self.state.current_task]
            print(f"⚡ Current Task: {current_task.id} - {current_task.name}")
        
        # Show phase breakdown
        phase_tasks = {phase: [] for phase in range(1, self.state.total_phases + 1)}
        for task in self.tasks.values():
            phase_tasks[task.phase].append(task)
        
        print(f"\n📋 Phase Breakdown:")
        for phase in range(1, self.state.total_phases + 1):
            tasks_in_phase = phase_tasks[phase]
            completed_in_phase = [t for t in tasks_in_phase if t.status == TaskStatus.COMPLETED]
            phase_progress = len(completed_in_phase) / len(tasks_in_phase) * 100
            
            phase_names = {
                1: "Service Management Foundation",
                2: "Tunnel Management", 
                3: "WebSocket Monitoring"
            }
            
            status_emoji = "✅" if phase_progress == 100 else "🔄" if phase_progress > 0 else "⏳"
            print(f"  {status_emoji} Phase {phase}: {phase_names.get(phase, f'Phase {phase}')} ({len(completed_in_phase)}/{len(tasks_in_phase)} tasks, {phase_progress:.0f}%)")
        
        # Show ready tasks
        ready_tasks = self.get_ready_tasks()
        if ready_tasks:
            print(f"\n🎯 Ready to Execute ({len(ready_tasks)} tasks):")
            for task in ready_tasks[:5]:  # Show first 5 ready tasks
                print(f"  • Task {task.id}: {task.name} ({task.estimated_duration}min, {task.priority.value})")
            if len(ready_tasks) > 5:
                print(f"  ... and {len(ready_tasks) - 5} more tasks")
        
        # Show failed tasks
        failed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
        if failed_tasks:
            print(f"\n❌ Failed Tasks ({len(failed_tasks)}):")
            for task in failed_tasks:
                print(f"  • Task {task.id}: {task.name}")
                if task.error_message:
                    print(f"    Error: {task.error_message[:100]}...")
        
        print("="*80)
    
    def execute_next_ready_task(self) -> bool:
        """Execute the next ready task."""
        ready_tasks = self.get_ready_tasks()
        if not ready_tasks:
            return False
        
        next_task = ready_tasks[0]  # Highest priority ready task
        return self.execute_task(next_task)
    
    def execute_all_ready_tasks(self):
        """Execute all ready tasks in sequence."""
        while True:
            ready_tasks = self.get_ready_tasks()
            if not ready_tasks:
                break
            
            success = self.execute_next_ready_task()
            if not success:
                print("❌ Task execution failed. Stopping orchestration.")
                break
            
            time.sleep(2)  # Brief pause between tasks
    
    def execute_phase(self, phase_number: int):
        """Execute all tasks in a specific phase."""
        phase_tasks = [t for t in self.tasks.values() if t.phase == phase_number]
        print(f"\n🚀 Executing Phase {phase_number} ({len(phase_tasks)} tasks)")
        
        while True:
            ready_tasks = [t for t in self.get_ready_tasks() if t.phase == phase_number]
            if not ready_tasks:
                break
            
            success = self.execute_task(ready_tasks[0])
            if not success:
                print(f"❌ Phase {phase_number} execution failed.")
                return False
            
            time.sleep(2)
        
        print(f"✅ Phase {phase_number} completed successfully!")
        return True
    
    def reset_task(self, task_id: str):
        """Reset a specific task to not started."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.NOT_STARTED
            task.start_time = None
            task.end_time = None
            task.error_message = None
            
            # Also reset dependent tasks
            dependent_tasks = [t for t in self.tasks.values() if task_id in t.dependencies]
            for dep_task in dependent_tasks:
                self.reset_task(dep_task.id)
            
            print(f"🔄 Task {task_id} reset to not started")
            self._save_state()
        else:
            print(f"❌ Task {task_id} not found")

def main():
    """Main orchestration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Observatory Infrastructure Governance Orchestrator")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--execute-next", action="store_true", help="Execute next ready task")
    parser.add_argument("--execute-all", action="store_true", help="Execute all ready tasks")
    parser.add_argument("--execute-phase", type=int, help="Execute specific phase")
    parser.add_argument("--reset-task", type=str, help="Reset specific task")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    orchestrator = InfrastructureGovernanceOrchestrator()
    
    if args.status:
        orchestrator.print_status()
    elif args.execute_next:
        orchestrator.execute_next_ready_task()
    elif args.execute_all:
        orchestrator.execute_all_ready_tasks()
    elif args.execute_phase:
        orchestrator.execute_phase(args.execute_phase)
    elif args.reset_task:
        orchestrator.reset_task(args.reset_task)
    elif args.interactive:
        # Interactive mode
        while True:
            orchestrator.print_status()
            print("\nOptions:")
            print("1. Execute next ready task")
            print("2. Execute all ready tasks")
            print("3. Execute specific phase")
            print("4. Reset task")
            print("5. Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                orchestrator.execute_next_ready_task()
            elif choice == "2":
                orchestrator.execute_all_ready_tasks()
            elif choice == "3":
                phase = input("Enter phase number (1-3): ").strip()
                try:
                    orchestrator.execute_phase(int(phase))
                except ValueError:
                    print("Invalid phase number")
            elif choice == "4":
                task_id = input("Enter task ID to reset: ").strip()
                orchestrator.reset_task(task_id)
            elif choice == "5":
                break
            else:
                print("Invalid choice")
    else:
        orchestrator.print_status()

if __name__ == "__main__":
    main()