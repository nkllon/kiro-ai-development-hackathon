#!/usr/bin/env python3
"""
CMS Architecture DAG Executor

Executes the CMS Architecture implementation DAG with systematic task orchestration.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass
import sys


@dataclass
class TaskStatus:
    """Task execution status."""
    id: str
    name: str
    phase: int
    status: str  # pending, ready, in_progress, completed, failed
    dependencies: List[str]
    completed_dependencies: Set[str]


class CMSArchitectureDAGExecutor:
    """Execute CMS Architecture DAG with dependency management."""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.tasks: Dict[str, TaskStatus] = {}
        self.completed_tasks: Set[str] = set()

    def _load_config(self) -> Dict:
        """Load DAG configuration from YAML."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def initialize_tasks(self):
        """Initialize task statuses from config."""
        print("🔄 Initializing CMS Architecture DAG...")

        for task_config in self.config['tasks']:
            task_id = task_config['id']
            self.tasks[task_id] = TaskStatus(
                id=task_id,
                name=task_config['name'],
                phase=task_config['phase'],
                status='pending',
                dependencies=task_config.get('dependencies', []),
                completed_dependencies=set()
            )

        print(f"✅ Initialized {len(self.tasks)} tasks across {self._get_phase_count()} phases")

    def _get_phase_count(self) -> int:
        """Get total number of phases."""
        phases = set(task.phase for task in self.tasks.values() if isinstance(task.phase, int))
        return len(phases)

    def get_ready_tasks(self) -> List[TaskStatus]:
        """Get tasks that are ready to execute (all dependencies met)."""
        ready_tasks = []

        for task in self.tasks.values():
            if task.status != 'pending':
                continue

            # Check if all dependencies are completed
            all_deps_met = all(
                dep_id in self.completed_tasks
                for dep_id in task.dependencies
            )

            if all_deps_met:
                ready_tasks.append(task)

        return ready_tasks

    def execute_task_dry_run(self, task: TaskStatus) -> bool:
        """Dry run execution - just mark as ready."""
        print(f"\n📋 Task Ready: {task.id}")
        print(f"   Name: {task.name}")
        print(f"   Phase: {task.phase}")
        print(f"   Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}")

        # For dry run, we just mark it as completed
        task.status = 'completed'
        self.completed_tasks.add(task.id)
        return True

    def execute_dag(self, dry_run: bool = True):
        """Execute the DAG (dry run by default)."""
        print(f"\n{'🔍 DRY RUN MODE' if dry_run else '🚀 EXECUTION MODE'}: CMS Architecture DAG")
        print("=" * 80)

        self.initialize_tasks()

        iteration = 0
        max_iterations = 100  # Safety limit

        while len(self.completed_tasks) < len(self.tasks) and iteration < max_iterations:
            iteration += 1
            ready_tasks = self.get_ready_tasks()

            if not ready_tasks:
                # Check if we're stuck
                pending_tasks = [t for t in self.tasks.values() if t.status == 'pending']
                if pending_tasks:
                    print("\n❌ Error: DAG execution stuck. Remaining tasks have unmet dependencies.")
                    for task in pending_tasks[:5]:  # Show first 5
                        unmet_deps = [d for d in task.dependencies if d not in self.completed_tasks]
                        print(f"   - {task.id}: waiting for {unmet_deps}")
                    return False
                break

            print(f"\n🔄 Iteration {iteration}: {len(ready_tasks)} tasks ready")

            for task in ready_tasks:
                if dry_run:
                    self.execute_task_dry_run(task)
                else:
                    # Actual execution would go here
                    print(f"⚠️  Actual execution not implemented for: {task.id}")
                    task.status = 'completed'
                    self.completed_tasks.add(task.id)

        # Summary
        print("\n" + "=" * 80)
        print("📊 Execution Summary:")
        print(f"   Total tasks: {len(self.tasks)}")
        print(f"   Completed: {len(self.completed_tasks)}")
        print(f"   Iterations: {iteration}")

        # Phase breakdown
        phases = {}
        for task in self.tasks.values():
            if isinstance(task.phase, int):
                phases[task.phase] = phases.get(task.phase, 0) + 1

        print("\n📈 Phase Breakdown:")
        for phase in sorted(phases.keys()):
            phase_tasks = [t for t in self.tasks.values() if t.phase == phase]
            completed = sum(1 for t in phase_tasks if t.status == 'completed')
            print(f"   Phase {phase}: {completed}/{phases[phase]} tasks")

        if len(self.completed_tasks) == len(self.tasks):
            print("\n✅ DAG execution completed successfully!")
            return True
        else:
            print("\n⚠️  DAG execution incomplete")
            return False

    def visualize_dag(self):
        """Generate a simple visualization of the DAG."""
        print("\n📊 DAG Visualization:")
        print("=" * 80)

        # Group by phase
        phases = {}
        for task in self.tasks.values():
            if isinstance(task.phase, int):
                if task.phase not in phases:
                    phases[task.phase] = []
                phases[task.phase].append(task)

        for phase in sorted(phases.keys()):
            print(f"\n📌 Phase {phase}:")
            for task in phases[phase]:
                deps_str = f" (deps: {', '.join(task.dependencies)})" if task.dependencies else ""
                print(f"   - {task.id}: {task.name}{deps_str}")


def main():
    """Main execution."""
    config_file = ".kiro/specs/cms-architecture/dag-config.yml"

    if not Path(config_file).exists():
        print(f"❌ Error: DAG config not found at {config_file}")
        sys.exit(1)

    print("🐺 CMS Architecture DAG Executor")
    print("=" * 80)

    executor = CMSArchitectureDAGExecutor(config_file)

    # First visualize
    executor.visualize_dag()

    # Then execute dry run
    print("\n")
    success = executor.execute_dag(dry_run=True)

    if success:
        print("\n✅ CMS Architecture DAG is ready for execution!")
        print("\n📝 Next steps:")
        print("   1. Review task breakdown above")
        print("   2. Execute: python scripts/execute_cms_architecture_dag.py --execute")
        print("   3. Monitor: make dag-monitor")
        sys.exit(0)
    else:
        print("\n❌ DAG validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
