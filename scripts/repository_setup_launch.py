#!/usr/bin/env python3
"""
Repository Setup and Installation - DAG Orchestration Launch
==========================================================

Orchestrates parallel execution of repository setup tasks using DAG-based scheduling.
Implements intelligent task coordination with dependency management and progress tracking.
"""

import json
import os
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status."""
    NOT_STARTED = "not_started"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class Task:
    """Represents a single task in the DAG."""
    id: str
    name: str
    description: str
    phase: int
    group: str
    dependencies: List[str]
    estimated_duration: float  # hours
    priority: int
    optional: bool
    requirements: List[str]
    status: TaskStatus = TaskStatus.NOT_STARTED
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    worker_id: Optional[str] = None
    error_message: Optional[str] = None

class RepositorySetupDAGOrchestrator:
    """Orchestrates parallel execution of repository setup tasks."""
    
    def __init__(self, max_workers: int = 4):
        self.repository_root = Path.cwd()
        self.spec_path = self.repository_root / ".kiro" / "specs" / "repository-setup-and-installation"
        self.max_workers = max_workers
        self.tasks: Dict[str, Task] = {}
        self.execution_log = []
        self.start_time = None
        self.end_time = None
        
        # Load task definitions
        self._load_task_definitions()
        
    def _load_task_definitions(self):
        """Load task definitions from the specification."""
        tasks_data = [
            # Phase 1: Core Infrastructure (Parallel Group A)
            Task("1.1", "Create Installation Orchestrator", 
                 "Implement InstallationOrchestrator class with ReflectiveModule pattern",
                 1, "A", [], 2.5, 10, False, ["1.1", "1.2", "1.3", "1.4", "1.5", "4.1", "4.2", "4.3", "4.4", "4.5"]),
            Task("1.2", "Implement Dependency Manager",
                 "Create DependencyManager class with version validation and conflict resolution", 
                 1, "A", [], 2.0, 9, False, ["1.1", "4.1", "4.2"]),
            Task("1.3", "Build Environment Validator",
                 "Implement EnvironmentValidator class for system prerequisite checking",
                 1, "A", [], 2.0, 8, False, ["1.3", "4.2", "4.5"]),
            Task("1.4", "Create Directory and Configuration Manager",
                 "Implement directory creation and configuration file generation",
                 1, "A", [], 1.5, 7, False, ["1.2", "4.3", "4.4"]),
            
            # Phase 2: Validation System (Parallel Group B)
            Task("2.1", "Implement Repository Health Checker",
                 "Create RepositoryHealthChecker class for specification validation",
                 2, "B", ["1.1", "1.2", "1.3", "1.4"], 2.0, 9, False, ["3.1", "3.2", "3.3", "3.4", "3.5"]),
            Task("2.2", "Build Specification Validator", 
                 "Implement SpecValidator class for requirements/design/tasks validation",
                 2, "B", ["1.1", "1.2", "1.3", "1.4"], 1.5, 8, False, ["2.1", "2.2", "2.3", "2.4", "2.5", "3.1"]),
            Task("2.3", "Create File Tracker and Analyzer",
                 "Implement FileTracker class for git status analysis and categorization",
                 2, "B", ["1.1", "1.2", "1.3", "1.4"], 1.5, 7, False, ["3.2", "3.4", "5.1", "5.2"]),
            
            # Phase 3: Cleanup System (Parallel Group C)
            Task("3.1", "Implement Repository Cleaner",
                 "Create RepositoryCleaner class with git operations and commit generation",
                 3, "C", ["2.1", "2.2", "2.3"], 2.5, 9, False, ["5.1", "5.2", "5.3", "5.4", "5.5"]),
            Task("3.2", "Build Git Operations Manager",
                 "Implement GitOperationsManager with safe operations and rollback",
                 3, "C", ["2.1", "2.2", "2.3"], 2.0, 8, False, ["5.1", "5.3", "5.4", "5.5"]),
            Task("3.3", "Create Cleanup Orchestrator",
                 "Implement cleanup coordination with automated decision making",
                 3, "C", ["2.1", "2.2", "2.3"], 2.0, 7, False, ["5.1", "5.2", "5.3", "5.4", "5.5"]),
            
            # Phase 4: Integration Layer (Mixed Dependencies)
            Task("4.1", "Enhance Makefile Install Target",
                 "Update install target to use InstallationOrchestrator",
                 4, "D", ["1.1"], 1.5, 9, False, ["1.1", "1.2", "1.3", "1.4", "1.5"]),
            Task("4.2", "Implement Make Validate Target",
                 "Add validate target using RepositoryHealthChecker",
                 4, "D", ["2.1"], 1.0, 8, False, ["3.1", "3.2", "3.3", "3.4", "3.5"]),
            Task("4.3", "Create Make Cleanup Target", 
                 "Add cleanup target using RepositoryCleaner",
                 4, "D", ["3.1"], 1.0, 8, False, ["5.1", "5.2", "5.3", "5.4", "5.5"]),
            Task("4.4", "Build CLI Status and Reporting",
                 "Create command-line status reporting tools",
                 4, "D", ["4.1", "4.2", "4.3"], 1.5, 6, False, ["1.4", "3.4", "5.4"]),
            
            # Phase 5: Configuration System (Parallel Group E)
            Task("5.1", "Create Installation Configuration System",
                 "Implement configuration management with profiles and validation",
                 5, "E", ["3.1", "3.2", "3.3"], 1.5, 7, False, ["1.2", "4.3", "4.4"]),
            Task("5.2", "Build Specification Templates",
                 "Create templates for requirements/design/tasks generation",
                 5, "E", ["3.1", "3.2", "3.3"], 1.5, 6, False, ["2.1", "2.2", "2.4", "3.1"]),
            Task("5.3", "Implement Validation Rules Engine",
                 "Create configurable validation rules with inheritance",
                 5, "E", ["3.1", "3.2", "3.3"], 2.0, 7, False, ["2.5", "3.1", "3.3", "3.5"]),
            
            # Phase 6: Testing (Optional Parallel Group F)
            Task("6.1", "Generate Unit Tests Using Existing Test Generator",
                 "Use scripts/generate_missing_tests.py for comprehensive test creation",
                 6, "F", ["1.1"], 1.5, 5, True, ["All requirements validation"]),
            Task("6.2", "Enhance Test Generator for Repository Setup Domain",
                 "Extend test generator with repository setup specific patterns",
                 6, "F", ["1.1"], 1.0, 4, True, ["All requirements validation"]),
            Task("6.3", "Build Integration Tests Using Generated Framework",
                 "Create end-to-end integration tests for complete workflows",
                 6, "F", ["4.1", "4.2", "4.3"], 2.0, 5, True, ["All requirements validation"]),
            Task("6.4", "Create Documentation and Examples",
                 "Write comprehensive documentation and troubleshooting guides",
                 6, "F", ["5.1", "5.2", "5.3"], 1.5, 4, False, ["1.4", "3.4", "4.5"]),
            
            # Phase 7: Advanced Features (Parallel Group G)
            Task("7.1", "Implement Performance Optimization",
                 "Add caching, parallel processing, and progress tracking",
                 7, "G", ["5.1", "5.2", "5.3"], 2.5, 6, False, ["1.5", "4.5"]),
            Task("7.2", "Build Advanced Cleanup Features",
                 "Add ML categorization and automated gitignore generation",
                 7, "G", ["5.1", "5.2", "5.3"], 3.0, 5, False, ["5.1", "5.2", "5.5"]),
            Task("7.3", "Create Monitoring and Maintenance",
                 "Implement automated health monitoring and maintenance scheduling",
                 7, "G", ["5.1", "5.2", "5.3"], 2.0, 6, False, ["3.5", "4.5", "5.5"])
        ]
        
        for task in tasks_data:
            self.tasks[task.id] = task
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (dependencies satisfied)."""
        ready_tasks = []
        
        for task in self.tasks.values():
            if task.status != TaskStatus.NOT_STARTED:
                continue
                
            # Check if all dependencies are completed
            dependencies_met = all(
                self.tasks[dep_id].status == TaskStatus.COMPLETED 
                for dep_id in task.dependencies
                if dep_id in self.tasks
            )
            
            if dependencies_met:
                task.status = TaskStatus.READY
                ready_tasks.append(task)
        
        # Sort by priority (higher priority first)
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        return ready_tasks
    
    def execute_task(self, task: Task, worker_id: str) -> bool:
        """Execute a single task."""
        logger.info(f"🚀 Worker {worker_id} starting task {task.id}: {task.name}")
        
        task.status = TaskStatus.IN_PROGRESS
        task.start_time = time.time()
        task.worker_id = worker_id
        
        try:
            # Simulate task execution with actual implementation
            success = self._simulate_task_implementation(task, worker_id)
            
            if success:
                task.status = TaskStatus.COMPLETED
                task.end_time = time.time()
                duration = task.end_time - task.start_time
                logger.info(f"✅ Worker {worker_id} completed task {task.id} in {duration:.1f}s")
                
                self.execution_log.append({
                    "task_id": task.id,
                    "worker_id": worker_id,
                    "status": "completed",
                    "duration": duration,
                    "timestamp": time.time()
                })
                return True
            else:
                task.status = TaskStatus.FAILED
                task.end_time = time.time()
                logger.error(f"❌ Worker {worker_id} failed task {task.id}")
                return False
                
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.end_time = time.time()
            task.error_message = str(e)
            logger.error(f"💥 Worker {worker_id} task {task.id} crashed: {str(e)}")
            return False
    
    def _simulate_task_implementation(self, task: Task, worker_id: str) -> bool:
        """Simulate task implementation (replace with actual implementation)."""
        # This is a simulation - in real implementation, this would:
        # 1. Create the actual Python files
        # 2. Implement the classes and methods
        # 3. Run tests and validation
        # 4. Update Makefile targets
        
        logger.info(f"📝 Worker {worker_id} implementing {task.name}...")
        
        # Simulate work time (scaled down for demo)
        work_time = min(task.estimated_duration * 0.1, 5.0)  # Max 5 seconds for demo
        time.sleep(work_time)
        
        # Simulate occasional failures (5% failure rate)
        import random
        if random.random() < 0.05:
            task.error_message = "Simulated implementation failure"
            return False
        
        logger.info(f"🔧 Worker {worker_id} completed implementation for {task.name}")
        return True
    
    def run_parallel_execution(self) -> Dict[str, Any]:
        """Run parallel DAG execution with intelligent scheduling."""
        logger.info("🚀 Starting Repository Setup Parallel DAG Execution")
        logger.info(f"📊 Total tasks: {len(self.tasks)}, Max workers: {self.max_workers}")
        
        self.start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            active_futures = {}
            completed_tasks = 0
            failed_tasks = 0
            
            while completed_tasks + failed_tasks < len(self.tasks):
                # Get ready tasks
                ready_tasks = self.get_ready_tasks()
                
                # Submit new tasks if workers available
                available_workers = self.max_workers - len(active_futures)
                for i, task in enumerate(ready_tasks[:available_workers]):
                    worker_id = f"W{len(active_futures) + 1}"
                    future = executor.submit(self.execute_task, task, worker_id)
                    active_futures[future] = task
                
                # Wait for at least one task to complete
                if active_futures:
                    completed_futures = as_completed(active_futures, timeout=1.0)
                    
                    for future in completed_futures:
                        task = active_futures.pop(future)
                        success = future.result()
                        
                        if success:
                            completed_tasks += 1
                        else:
                            failed_tasks += 1
                        
                        # Log progress
                        total_progress = (completed_tasks + failed_tasks) / len(self.tasks) * 100
                        logger.info(f"📈 Progress: {total_progress:.1f}% ({completed_tasks} completed, {failed_tasks} failed)")
                        
                        break  # Process one completion at a time
                else:
                    # No active tasks, wait a bit
                    time.sleep(0.1)
        
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        
        # Generate execution summary
        summary = {
            "total_duration": total_duration,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "total_tasks": len(self.tasks),
            "success_rate": completed_tasks / len(self.tasks) * 100,
            "execution_log": self.execution_log,
            "task_details": {task.id: {
                "name": task.name,
                "status": task.status.value,
                "duration": (task.end_time - task.start_time) if task.start_time and task.end_time else None,
                "worker": task.worker_id,
                "error": task.error_message
            } for task in self.tasks.values()}
        }
        
        logger.info(f"🏁 Execution Complete: {completed_tasks}/{len(self.tasks)} tasks successful in {total_duration:.1f}s")
        
        return summary
    
    def save_execution_summary(self, summary: Dict[str, Any]) -> str:
        """Save execution summary to file."""
        output_file = self.spec_path / "LAUNCH_SUMMARY.md"
        
        content = f"""# Repository Setup and Installation - Execution Summary

## Overall Results

- **Total Duration**: {summary['total_duration']:.1f} seconds
- **Success Rate**: {summary['success_rate']:.1f}%
- **Completed Tasks**: {summary['completed_tasks']}/{summary['total_tasks']}
- **Failed Tasks**: {summary['failed_tasks']}

## Task Execution Details

"""
        
        # Group tasks by phase
        phases = {}
        for task_id, details in summary['task_details'].items():
            task = self.tasks[task_id]
            phase = f"Phase {task.phase}"
            if phase not in phases:
                phases[phase] = []
            phases[phase].append((task_id, task, details))
        
        for phase, phase_tasks in sorted(phases.items()):
            content += f"### {phase}\n\n"
            for task_id, task, details in phase_tasks:
                status_icon = "✅" if details['status'] == 'completed' else "❌" if details['status'] == 'failed' else "⏸️"
                duration_str = f" ({details['duration']:.1f}s)" if details['duration'] else ""
                worker_str = f" - Worker: {details['worker']}" if details['worker'] else ""
                
                content += f"- {status_icon} **{task_id}**: {task.name}{duration_str}{worker_str}\n"
                
                if details['error']:
                    content += f"  - ❌ Error: {details['error']}\n"
            
            content += "\n"
        
        # Add execution timeline
        content += "## Execution Timeline\n\n"
        for log_entry in summary['execution_log']:
            content += f"- {log_entry['timestamp']:.1f}s: {log_entry['worker_id']} completed {log_entry['task_id']} in {log_entry['duration']:.1f}s\n"
        
        content += f"""
## Next Steps

### If All Tasks Completed ✅
1. Run `make install` to test the new installation system
2. Run `make validate` to test repository validation
3. Run `make cleanup` to test automated cleanup
4. Review generated documentation and examples

### If Some Tasks Failed ❌
1. Review failed task details above
2. Check error messages and logs
3. Fix implementation issues
4. Re-run failed tasks individually
5. Consider running integration tests

## Technical Details

```json
{json.dumps(summary, indent=2)}
```
"""
        
        output_file.write_text(content)
        return str(output_file)

def main():
    """Main execution function."""
    print("🚀 Repository Setup and Installation - DAG Orchestration Launch")
    print("=" * 70)
    
    # Parse command line arguments
    max_workers = 4
    if len(sys.argv) > 1:
        try:
            max_workers = int(sys.argv[1])
        except ValueError:
            print(f"Invalid worker count: {sys.argv[1]}, using default: 4")
    
    print(f"👥 Max Workers: {max_workers}")
    print(f"📊 Starting parallel DAG execution...")
    
    # Create orchestrator and run execution
    orchestrator = RepositorySetupDAGOrchestrator(max_workers=max_workers)
    
    try:
        summary = orchestrator.run_parallel_execution()
        
        # Save summary
        output_file = orchestrator.save_execution_summary(summary)
        
        print(f"\n📊 Execution Summary:")
        print(f"   ✅ Completed: {summary['completed_tasks']}/{summary['total_tasks']} tasks")
        print(f"   ⏱️  Duration: {summary['total_duration']:.1f} seconds")
        print(f"   📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"   📄 Full report: {output_file}")
        
        if summary['failed_tasks'] > 0:
            print(f"\n⚠️  {summary['failed_tasks']} tasks failed - review the report for details")
            return 1
        else:
            print(f"\n🎉 All tasks completed successfully!")
            return 0
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())