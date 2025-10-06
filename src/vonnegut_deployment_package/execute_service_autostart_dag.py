#!/usr/bin/env python3
"""
Service Auto-Start Governance DAG Executor

Orchestrates the execution of Service Auto-Start Governance implementation tasks
based on the DAG execution plan defined in .kiro/specs/service-auto-start-governance/

Usage:
    python scripts/execute_service_autostart_dag.py --phase [mvp|full|all]
    python scripts/execute_service_autostart_dag.py --task 1.0
    python scripts/execute_service_autostart_dag.py --validate
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Task priority levels."""
    P0 = 0  # Critical - MVP
    P1 = 1  # High - Full production
    P2 = 2  # Medium - Enhancements
    P3 = 3  # Low - Nice to have
    P4 = 4  # Future - Long-term


@dataclass
class Task:
    """Represents a single DAG task."""

    id: str
    name: str
    description: str
    priority: TaskPriority
    estimated_hours: float
    dependencies: List[str] = field(default_factory=list)
    phase: str = "Phase 1"
    status: TaskStatus = TaskStatus.PENDING
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)

    def can_execute(self, completed_tasks: Set[str]) -> bool:
        """Check if all dependencies are met."""
        return all(dep in completed_tasks for dep in self.dependencies)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.name,
            "estimated_hours": self.estimated_hours,
            "dependencies": self.dependencies,
            "phase": self.phase,
            "status": self.status.value,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "acceptance_criteria": self.acceptance_criteria
        }


class ServiceAutoStartDAG:
    """DAG executor for Service Auto-Start Governance implementation."""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.spec_dir = project_root / ".kiro/specs/service-auto-start-governance"
        self.status_file = project_root / "SERVICE_AUTOSTART_DAG_STATUS.json"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('service-autostart-dag-execution.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        self._initialize_tasks()
        self._load_status()

    def _initialize_tasks(self):
        """Initialize all tasks from the DAG execution plan."""

        # Phase 1: Foundation
        self.tasks["1.0"] = Task(
            id="1.0",
            name="Platform Detection and Abstraction Layer",
            description="Create platform adapter infrastructure for macOS, Linux, Docker",
            priority=TaskPriority.P0,
            estimated_hours=4.0,
            phase="Phase 1",
            dependencies=[],
            files_created=[
                "src/system_architecture/autostart/__init__.py",
                "src/system_architecture/autostart/platform_adapter.py",
                "src/system_architecture/autostart/platforms/__init__.py",
                "src/system_architecture/autostart/platforms/macos.py",
                "src/system_architecture/autostart/platforms/linux.py",
                "src/system_architecture/autostart/platforms/docker.py",
                "tests/unit/system_architecture/autostart/test_platforms.py"
            ],
            acceptance_criteria=[
                "All platform adapters pass unit tests",
                "Platform detection correctly identifies macOS/Linux/Docker",
                "Each adapter can generate, install, and verify configurations"
            ]
        )

        self.tasks["1.1"] = Task(
            id="1.1",
            name="Service Definition Schema and Registry",
            description="Define service schema and implement central registry",
            priority=TaskPriority.P0,
            estimated_hours=3.0,
            phase="Phase 1",
            dependencies=["1.0"],
            files_created=[
                "src/system_architecture/autostart/models.py",
                "src/system_architecture/autostart/service_registry.py",
                "tests/unit/system_architecture/autostart/test_service_registry.py"
            ],
            acceptance_criteria=[
                "ServiceDefinition includes all required fields",
                "ServiceRegistry can register and retrieve services",
                "Dependency resolution produces correct startup order",
                "Validation catches incomplete service definitions"
            ]
        )

        self.tasks["1.2"] = Task(
            id="1.2",
            name="Health Check Standardization System",
            description="Standardize health checks with container-native tools",
            priority=TaskPriority.P0,
            estimated_hours=4.0,
            phase="Phase 1",
            dependencies=["1.0"],
            files_created=[
                "src/system_architecture/autostart/health_check.py",
                "src/system_architecture/autostart/health_templates.py",
                "tests/integration/system_architecture/autostart/test_health_checks.py"
            ],
            acceptance_criteria=[
                "Tool detection works for common container images",
                "Health checks generated with appropriate tool fallbacks",
                "Health check validation catches misconfigurations",
                "IPv6/IPv4 compatibility issues prevented"
            ]
        )

        self.tasks["1.3"] = Task(
            id="1.3",
            name="Auto-Start Configuration Manager",
            description="Implement configuration generation and management",
            priority=TaskPriority.P0,
            estimated_hours=5.0,
            phase="Phase 1",
            dependencies=["1.0", "1.1", "1.2"],
            files_created=[
                "src/system_architecture/autostart/config_manager.py",
                "tests/integration/system_architecture/autostart/test_config_manager.py"
            ],
            acceptance_criteria=[
                "Can generate configs for macOS, Linux, Docker",
                "Configuration installation succeeds on target platform",
                "Verification confirms auto-start will work",
                "Rollback restores previous state on failure"
            ]
        )

        # Phase 2: Testing & Resilience
        self.tasks["2.0"] = Task(
            id="2.0",
            name="Boot Simulation Testing System",
            description="Implement boot simulation and testing framework",
            priority=TaskPriority.P1,
            estimated_hours=6.0,
            phase="Phase 2",
            dependencies=["1.3"],
            files_created=[
                "src/system_architecture/autostart/boot_simulator.py",
                "src/system_architecture/autostart/test_scenarios.py",
                "tests/integration/system_architecture/autostart/test_boot_simulation.py"
            ],
            acceptance_criteria=[
                "Boot simulation stops and restarts all services correctly",
                "Dependency ordering verified",
                "Failure scenarios tested (5+ scenarios)",
                "Reports include timing and success metrics"
            ]
        )

        self.tasks["2.1"] = Task(
            id="2.1",
            name="Failure Recovery and Resilience",
            description="Implement retry logic and failure recovery mechanisms",
            priority=TaskPriority.P1,
            estimated_hours=5.0,
            phase="Phase 2",
            dependencies=["1.3"],
            files_created=[
                "src/system_architecture/autostart/recovery_manager.py",
                "src/system_architecture/autostart/retry_policies.py",
                "tests/unit/system_architecture/autostart/test_recovery.py"
            ],
            acceptance_criteria=[
                "Retry logic uses exponential backoff (1s, 2s, 4s...)",
                "Dependency waiting times out appropriately",
                "Resource constraints handled gracefully",
                "Maintenance mode activated after retry limits"
            ]
        )

        self.tasks["2.2"] = Task(
            id="2.2",
            name="Startup Metrics and Monitoring",
            description="Implement Prometheus metrics and log aggregation",
            priority=TaskPriority.P1,
            estimated_hours=4.0,
            phase="Phase 2",
            dependencies=["1.3"],
            files_created=[
                "src/system_architecture/autostart/metrics_collector.py",
                "src/system_architecture/autostart/log_aggregator.py",
                "tests/unit/system_architecture/autostart/test_metrics.py"
            ],
            acceptance_criteria=[
                "Metrics exported to Prometheus",
                "Logs aggregated from all platforms",
                "Pattern analysis identifies issues",
                "Alerts triggered on failures"
            ]
        )

        # Phase 3: Governance & Documentation
        self.tasks["3.0"] = Task(
            id="3.0",
            name="Requirements Specification Governance",
            description="Implement requirements validation and governance",
            priority=TaskPriority.P2,
            estimated_hours=4.0,
            phase="Phase 3",
            dependencies=["1.3"],
            files_created=[
                "src/system_architecture/autostart/requirements_validator.py",
                "src/system_architecture/autostart/requirements_templates.py",
                "tests/unit/system_architecture/autostart/test_requirements.py"
            ],
            acceptance_criteria=[
                "Passive voice flagged in requirements",
                "WHO/WHEN/HOW/WHAT completeness verified",
                "Templates generate proper requirements",
                "Acceptance tests auto-generated"
            ]
        )

        self.tasks["3.1"] = Task(
            id="3.1",
            name="Deployment Integration and Verification",
            description="Integrate with deployment process and generate automation",
            priority=TaskPriority.P1,
            estimated_hours=5.0,
            phase="Phase 3",
            dependencies=["1.3"],
            files_created=[
                "src/system_architecture/autostart/deployment_integrator.py",
                "src/system_architecture/autostart/makefile_generator.py",
                "tests/integration/system_architecture/autostart/test_deployment.py"
            ],
            acceptance_criteria=[
                "Checklists include auto-start verification",
                "Makefile targets work (start/stop/status/logs)",
                "Deployment verification catches issues",
                "Documentation accurate and complete"
            ]
        )

        self.tasks["3.2"] = Task(
            id="3.2",
            name="Comprehensive Documentation System",
            description="Generate platform-specific documentation and runbooks",
            priority=TaskPriority.P2,
            estimated_hours=4.0,
            phase="Phase 3",
            dependencies=["1.3"],
            files_created=[
                "src/system_architecture/autostart/doc_generator.py",
                "src/system_architecture/autostart/templates/",
                "tests/unit/system_architecture/autostart/test_documentation.py"
            ],
            acceptance_criteria=[
                "Setup docs accurate for each platform",
                "Troubleshooting covers common issues",
                "Dependencies clearly documented",
                "Runbooks provide step-by-step procedures"
            ]
        )

        # Phase 4: Integration & Validation
        self.tasks["4.0"] = Task(
            id="4.0",
            name="Integrate with CMS Service (Validation)",
            description="Apply framework to Directus CMS as proof of concept",
            priority=TaskPriority.P0,
            estimated_hours=6.0,
            phase="Phase 4",
            dependencies=["2.0", "2.1", "2.2", "3.0", "3.1", "3.2"],
            files_modified=[
                "docker-compose.directus-fixed.yml"
            ],
            files_created=[
                "config/autostart/directus-cms.json",
                "~/Library/LaunchAgents/com.beastmode.directus-cms.plist"
            ],
            acceptance_criteria=[
                "CMS auto-starts on system boot",
                "Health check uses 127.0.0.1 not localhost",
                "Boot simulation passes",
                "Metrics collected properly"
            ]
        )

        self.tasks["4.1"] = Task(
            id="4.1",
            name="Extend to All Docker Compose Services",
            description="Apply framework to all 11 Docker services",
            priority=TaskPriority.P1,
            estimated_hours=8.0,
            phase="Phase 4",
            dependencies=["4.0"],
            acceptance_criteria=[
                "All services registered in registry",
                "Auto-start configs generated for all",
                "Multi-service boot simulation passes",
                "Dashboard shows all service status"
            ]
        )

        self.tasks["4.2"] = Task(
            id="4.2",
            name="Cross-Platform Support and Migration",
            description="Add Kubernetes and Docker Swarm support",
            priority=TaskPriority.P2,
            estimated_hours=10.0,
            phase="Phase 4",
            dependencies=["4.1"],
            files_created=[
                "src/system_architecture/autostart/platforms/kubernetes.py",
                "src/system_architecture/autostart/platforms/swarm.py",
                "src/system_architecture/autostart/migration_tools.py"
            ],
            acceptance_criteria=[
                "Kubernetes deployments generated",
                "Docker Swarm configs generated",
                "Migration tools work between platforms",
                "Feature detection handles differences"
            ]
        )

    def _load_status(self):
        """Load execution status from file."""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    status_data = json.load(f)
                    self.completed_tasks = set(status_data.get('completed_tasks', []))
                    self.failed_tasks = set(status_data.get('failed_tasks', []))

                    # Update task statuses
                    for task_id, task_status in status_data.get('task_statuses', {}).items():
                        if task_id in self.tasks:
                            self.tasks[task_id].status = TaskStatus(task_status)

                    self.logger.info(f"Loaded status: {len(self.completed_tasks)} completed, {len(self.failed_tasks)} failed")
            except Exception as e:
                self.logger.error(f"Error loading status: {e}")

    def _save_status(self):
        """Save execution status to file."""
        try:
            status_data = {
                'completed_tasks': list(self.completed_tasks),
                'failed_tasks': list(self.failed_tasks),
                'task_statuses': {tid: t.status.value for tid, t in self.tasks.items()},
                'last_updated': datetime.now().isoformat()
            }

            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)

            self.logger.info(f"Status saved to {self.status_file}")
        except Exception as e:
            self.logger.error(f"Error saving status: {e}")

    def get_executable_tasks(self, filter_priority: Optional[TaskPriority] = None) -> List[Task]:
        """Get tasks that can be executed now (dependencies met)."""
        executable = []

        for task in self.tasks.values():
            # Skip completed or failed tasks
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                continue

            # Check priority filter
            if filter_priority and task.priority.value > filter_priority.value:
                continue

            # Check dependencies
            if task.can_execute(self.completed_tasks):
                executable.append(task)

        return sorted(executable, key=lambda t: (t.priority.value, t.id))

    def execute_task(self, task_id: str, dry_run: bool = False) -> bool:
        """Execute a single task."""
        if task_id not in self.tasks:
            self.logger.error(f"Task {task_id} not found")
            return False

        task = self.tasks[task_id]

        # Check dependencies
        if not task.can_execute(self.completed_tasks):
            missing = [d for d in task.dependencies if d not in self.completed_tasks]
            self.logger.error(f"Cannot execute {task_id}: missing dependencies {missing}")
            return False

        self.logger.info(f"{'[DRY RUN] ' if dry_run else ''}Executing task {task_id}: {task.name}")
        task.status = TaskStatus.IN_PROGRESS

        if dry_run:
            self.logger.info(f"  Priority: {task.priority.name}")
            self.logger.info(f"  Estimated: {task.estimated_hours} hours")
            self.logger.info(f"  Files to create: {len(task.files_created)}")
            self.logger.info(f"  Acceptance criteria: {len(task.acceptance_criteria)}")
            task.status = TaskStatus.COMPLETED
            self.completed_tasks.add(task_id)
            return True

        # In real execution, this would:
        # 1. Create necessary directories
        # 2. Generate boilerplate code
        # 3. Run tests
        # 4. Validate acceptance criteria

        # For now, mark as requiring manual implementation
        self.logger.info(f"Task {task_id} ready for implementation:")
        self.logger.info(f"  Files to create:")
        for f in task.files_created:
            self.logger.info(f"    - {f}")
        if task.files_modified:
            self.logger.info(f"  Files to modify:")
            for f in task.files_modified:
                self.logger.info(f"    - {f}")
        self.logger.info(f"  Acceptance criteria:")
        for i, ac in enumerate(task.acceptance_criteria, 1):
            self.logger.info(f"    {i}. {ac}")

        # Mark as pending implementation
        self.logger.warning(f"Task {task_id} requires manual implementation")

        return True

    def execute_phase(self, phase_name: str, dry_run: bool = False) -> bool:
        """Execute all tasks in a phase."""
        phase_tasks = [t for t in self.tasks.values() if t.phase == phase_name]

        if not phase_tasks:
            self.logger.error(f"No tasks found for phase {phase_name}")
            return False

        self.logger.info(f"{'[DRY RUN] ' if dry_run else ''}Executing {phase_name}: {len(phase_tasks)} tasks")

        success_count = 0
        for task in sorted(phase_tasks, key=lambda t: t.id):
            if self.execute_task(task.id, dry_run):
                success_count += 1

        self.logger.info(f"{phase_name} completed: {success_count}/{len(phase_tasks)} tasks successful")
        self._save_status()

        return success_count == len(phase_tasks)

    def execute_mvp(self, dry_run: bool = False) -> bool:
        """Execute MVP tasks (Phase 1 + Task 4.0 + Task 2.2 + Task 3.1)."""
        mvp_tasks = ["1.0", "1.1", "1.2", "1.3", "4.0", "2.2", "3.1"]

        self.logger.info(f"{'[DRY RUN] ' if dry_run else ''}Executing MVP: {len(mvp_tasks)} tasks")

        success_count = 0
        for task_id in mvp_tasks:
            if self.execute_task(task_id, dry_run):
                success_count += 1
            else:
                self.logger.error(f"MVP execution failed at task {task_id}")
                break

        self._save_status()
        return success_count == len(mvp_tasks)

    def validate_dag(self) -> bool:
        """Validate DAG structure for cycles and missing dependencies."""
        self.logger.info("Validating DAG structure...")

        errors = []

        # Check for missing dependencies
        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    errors.append(f"Task {task_id} depends on non-existent task {dep}")

        # Check for cycles (simple DFS-based detection)
        def has_cycle(task_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            for dep in self.tasks[task_id].dependencies:
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    errors.append(f"Cycle detected involving task {task_id} and {dep}")
                    return True

            rec_stack.remove(task_id)
            return False

        visited = set()
        for task_id in self.tasks:
            if task_id not in visited:
                has_cycle(task_id, visited, set())

        if errors:
            for error in errors:
                self.logger.error(error)
            return False

        self.logger.info("✓ DAG structure valid")
        return True

    def generate_execution_report(self) -> str:
        """Generate execution status report."""
        report = []
        report.append("=" * 80)
        report.append("Service Auto-Start Governance - DAG Execution Status")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary
        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)

        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Tasks:    {total_tasks}")
        report.append(f"Completed:      {completed} ({completed/total_tasks*100:.1f}%)")
        report.append(f"In Progress:    {in_progress}")
        report.append(f"Failed:         {failed}")
        report.append(f"Pending:        {pending}")
        report.append("")

        # Executable tasks
        executable = self.get_executable_tasks()
        report.append(f"READY TO EXECUTE ({len(executable)} tasks)")
        report.append("-" * 80)
        for task in executable[:5]:  # Show top 5
            report.append(f"  {task.id}: {task.name} ({task.priority.name}, {task.estimated_hours}h)")
        if len(executable) > 5:
            report.append(f"  ... and {len(executable) - 5} more")
        report.append("")

        # Phase breakdown
        report.append("PROGRESS BY PHASE")
        report.append("-" * 80)
        phases = sorted(set(t.phase for t in self.tasks.values()))
        for phase in phases:
            phase_tasks = [t for t in self.tasks.values() if t.phase == phase]
            phase_completed = sum(1 for t in phase_tasks if t.status == TaskStatus.COMPLETED)
            report.append(f"{phase}: {phase_completed}/{len(phase_tasks)} completed")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Service Auto-Start Governance DAG Executor"
    )
    parser.add_argument(
        "--phase",
        choices=["mvp", "full", "all", "1", "2", "3", "4"],
        help="Execute specific phase"
    )
    parser.add_argument(
        "--task",
        help="Execute specific task (e.g., 1.0, 1.1)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate DAG structure"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show execution status"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (no actual execution)"
    )

    args = parser.parse_args()

    dag = ServiceAutoStartDAG()

    # Validate DAG
    if args.validate or not any([args.phase, args.task, args.status]):
        if not dag.validate_dag():
            sys.exit(1)
        print("\n✓ DAG validation passed")
        print(f"\nTotal tasks: {len(dag.tasks)}")
        print(f"Executable now: {len(dag.get_executable_tasks())}")

    # Show status
    if args.status or not any([args.phase, args.task]):
        print("\n" + dag.generate_execution_report())

    # Execute phase
    if args.phase:
        if args.phase == "mvp":
            success = dag.execute_mvp(dry_run=args.dry_run)
        elif args.phase == "full":
            phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
            success = all(dag.execute_phase(p, dry_run=args.dry_run) for p in phases)
        elif args.phase == "all":
            phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5", "Phase 6"]
            success = all(dag.execute_phase(p, dry_run=args.dry_run) for p in phases)
        else:
            success = dag.execute_phase(f"Phase {args.phase}", dry_run=args.dry_run)

        sys.exit(0 if success else 1)

    # Execute specific task
    if args.task:
        success = dag.execute_task(args.task, dry_run=args.dry_run)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
