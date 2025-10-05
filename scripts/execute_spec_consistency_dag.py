#!/usr/bin/env python3
"""
Spec Consistency Governance DAG Executor

Orchestrates the execution of Spec Consistency Governance implementation tasks
based on the DAG execution plan defined in .kiro/specs/spec-consistency-governance/

Usage:
    python scripts/execute_spec_consistency_dag.py --phase [1|2|3|4|5|all]
    python scripts/execute_spec_consistency_dag.py --task 1.1
    python scripts/execute_spec_consistency_dag.py --validate
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
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


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


class SpecConsistencyDAG:
    """DAG executor for Spec Consistency Governance implementation."""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.spec_dir = project_root / ".kiro/specs/spec-consistency-governance"
        self.status_file = project_root / "SPEC_CONSISTENCY_DAG_STATUS.json"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('spec-consistency-dag-execution.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        self._initialize_tasks()
        self._load_status()

    def _initialize_tasks(self):
        """Initialize all tasks from the DAG execution plan."""

        # Phase 1: Critical Infrastructure (Week 1) - 25 hours
        self.tasks["1.1"] = Task(
            id="1.1",
            name="Core Module Structure",
            description="Create src/spec_governance/ directory structure and package setup",
            priority=TaskPriority.CRITICAL,
            estimated_hours=2.0,
            phase="Phase 1",
            dependencies=[],
            files_created=[
                "src/spec_governance/__init__.py",
                "src/spec_governance/models.py",
                "tests/unit/spec_governance/__init__.py"
            ],
            acceptance_criteria=[
                "Directory structure matches design.md",
                "Package imports successfully",
                "pytest discovers test structure"
            ]
        )

        self.tasks["1.2"] = Task(
            id="1.2",
            name="SpecValidator Core",
            description="Implement core validation logic for spec structure",
            priority=TaskPriority.CRITICAL,
            estimated_hours=8.0,
            phase="Phase 1",
            dependencies=["1.1"],
            files_created=[
                "src/spec_governance/validator.py",
                "tests/unit/spec_governance/test_validator.py"
            ],
            acceptance_criteria=[
                "Detects all 23 incomplete specs from analysis",
                "Identifies all 16 specs with extra files",
                "Unit tests achieve >90% coverage",
                "Validation runs in <5 seconds for all 105 specs"
            ]
        )

        self.tasks["1.3"] = Task(
            id="1.3",
            name="SpecReporter",
            description="Generate comprehensive markdown and JSON reports",
            priority=TaskPriority.CRITICAL,
            estimated_hours=6.0,
            phase="Phase 1",
            dependencies=["1.1"],
            files_created=[
                "src/spec_governance/reporter.py",
                "tests/unit/spec_governance/test_reporter.py"
            ],
            acceptance_criteria=[
                "Generates readable markdown report",
                "Includes all metrics from design.md",
                "JSON export valid and complete",
                "Report matches manual analysis findings"
            ]
        )

        self.tasks["1.4"] = Task(
            id="1.4",
            name="CLI Interface",
            description="Create Click-based CLI for validation and reporting",
            priority=TaskPriority.CRITICAL,
            estimated_hours=6.0,
            phase="Phase 1",
            dependencies=["1.2", "1.3"],
            files_created=[
                "src/spec_governance/cli.py",
                "tests/integration/spec_governance/test_cli.py"
            ],
            acceptance_criteria=[
                "spec-governance --help shows all commands",
                "Validate command runs successfully",
                "CI mode outputs parseable format",
                "Exit codes correct for pass/fail"
            ]
        )

        self.tasks["1.5"] = Task(
            id="1.5",
            name="Remove Empty Directory",
            description="Remove .kiro/specs/output/ empty directory",
            priority=TaskPriority.HIGH,
            estimated_hours=1.0,
            phase="Phase 1",
            dependencies=[],
            acceptance_criteria=[
                "Empty directory removed",
                "Git history checked for safety",
                "Commit message clear"
            ]
        )

        self.tasks["1.6"] = Task(
            id="1.6",
            name="Makefile Targets",
            description="Add spec-validate and spec-report targets",
            priority=TaskPriority.HIGH,
            estimated_hours=2.0,
            phase="Phase 1",
            dependencies=["1.4"],
            files_modified=["Makefile"],
            acceptance_criteria=[
                "make spec-validate works",
                "make spec-report generates report",
                "Targets documented in make help"
            ]
        )

        # Phase 2: Governance & Prevention (Week 2) - 38 hours
        self.tasks["2.1"] = Task(
            id="2.1",
            name="Spec Registry",
            description="Build JSON registry of all specs with metadata",
            priority=TaskPriority.CRITICAL,
            estimated_hours=8.0,
            phase="Phase 2",
            dependencies=["1.2"],
            files_created=[
                "src/spec_governance/registry.py",
                ".kiro/spec-registry.json",
                "tests/unit/spec_governance/test_registry.py"
            ],
            acceptance_criteria=[
                "All 105 specs indexed",
                "Registry includes name, path, completeness",
                "Fast lookup (<100ms)",
                "JSON format valid"
            ]
        )

        self.tasks["2.2"] = Task(
            id="2.2",
            name="Lifecycle Tracking",
            description="Implement .spec-state files for lifecycle management",
            priority=TaskPriority.HIGH,
            estimated_hours=6.0,
            phase="Phase 2",
            dependencies=["2.1"],
            files_created=[
                "src/spec_governance/lifecycle.py",
                "tests/unit/spec_governance/test_lifecycle.py"
            ],
            acceptance_criteria=[
                "States persist correctly",
                "Transitions validated",
                "Timestamps accurate",
                "YAML format correct"
            ]
        )

        self.tasks["2.3"] = Task(
            id="2.3",
            name="Remediator Foundation",
            description="Build auto-fix framework with dry-run support",
            priority=TaskPriority.CRITICAL,
            estimated_hours=8.0,
            phase="Phase 2",
            dependencies=["1.2"],
            files_created=[
                "src/spec_governance/remediator.py",
                "tests/unit/spec_governance/test_remediator.py"
            ],
            acceptance_criteria=[
                "Dry-run mode works",
                "Rollback capability",
                "Safe file operations",
                "Comprehensive logging"
            ]
        )

        self.tasks["2.4"] = Task(
            id="2.4",
            name="Extra File Management",
            description="Automatically move execution artifacts and backups",
            priority=TaskPriority.HIGH,
            estimated_hours=6.0,
            phase="Phase 2",
            dependencies=["2.3"],
            acceptance_criteria=[
                "Artifacts moved to .kiro/execution-logs/",
                "Backups moved to .kiro/archive/",
                "Timestamps preserved",
                "Original locations cleaned"
            ]
        )

        self.tasks["2.5"] = Task(
            id="2.5",
            name="Git Pre-commit Hook",
            description="Prevent incomplete specs from being committed",
            priority=TaskPriority.HIGH,
            estimated_hours=6.0,
            phase="Phase 2",
            dependencies=["2.2"],
            files_created=[
                ".git/hooks/pre-commit-spec-governance",
                "scripts/install_spec_governance_hooks.sh"
            ],
            acceptance_criteria=[
                "Hook prevents incomplete commits",
                "Clear error messages",
                "Can be bypassed with flag",
                "Install script works"
            ]
        )

        self.tasks["2.6"] = Task(
            id="2.6",
            name="Document Standards",
            description="Create comprehensive governance documentation",
            priority=TaskPriority.MEDIUM,
            estimated_hours=4.0,
            phase="Phase 2",
            dependencies=[],
            files_created=[
                "docs/spec-governance/standards.md",
                "docs/spec-governance/workflow.md"
            ],
            acceptance_criteria=[
                "Standards clear and complete",
                "Examples provided",
                "Workflow documented",
                "FAQ included"
            ]
        )

        # Phase 3: Quality & Automation (Week 3) - 28 hours
        self.tasks["3.1"] = Task(
            id="3.1",
            name="Template Generator",
            description="Generate starter templates for new specs",
            priority=TaskPriority.MEDIUM,
            estimated_hours=8.0,
            phase="Phase 3",
            dependencies=["2.1"],
            files_created=[
                "src/spec_governance/templates.py",
                "templates/spec-template/requirements.md.j2",
                "templates/spec-template/design.md.j2",
                "templates/spec-template/tasks.md.j2"
            ],
            acceptance_criteria=[
                "Templates comprehensive",
                "Customizable variables",
                "CLI integration works",
                "Output validates correctly"
            ]
        )

        self.tasks["3.2"] = Task(
            id="3.2",
            name="Automated Stubs",
            description="Auto-generate stub files for incomplete specs",
            priority=TaskPriority.HIGH,
            estimated_hours=6.0,
            phase="Phase 3",
            dependencies=["3.1", "2.3"],
            acceptance_criteria=[
                "Stubs contain proper structure",
                "Metadata preserved",
                "Safe creation (no overwrite)",
                "Logged for review"
            ]
        )

        self.tasks["3.3"] = Task(
            id="3.3",
            name="File Naming Fixes",
            description="Automatically rename non-standard filenames",
            priority=TaskPriority.MEDIUM,
            estimated_hours=4.0,
            phase="Phase 3",
            dependencies=["2.3"],
            acceptance_criteria=[
                "Case variants normalized",
                "Git history preserved",
                "Dry-run available",
                "Report generated"
            ]
        )

        self.tasks["3.4"] = Task(
            id="3.4",
            name="Enhanced Reporting",
            description="Add trend analysis and visualizations",
            priority=TaskPriority.MEDIUM,
            estimated_hours=10.0,
            phase="Phase 3",
            dependencies=["1.3", "2.1"],
            acceptance_criteria=[
                "Quality trends over time",
                "Visualization data export",
                "Dashboard integration ready",
                "Metrics comprehensive"
            ]
        )

        # Phase 4: Advanced Features (Week 4) - 42 hours
        self.tasks["4.1"] = Task(
            id="4.1",
            name="Similarity Detection",
            description="Detect duplicate and similar specs",
            priority=TaskPriority.MEDIUM,
            estimated_hours=12.0,
            phase="Phase 4",
            dependencies=["2.1"],
            files_created=[
                "src/spec_governance/similarity.py",
                "tests/unit/spec_governance/test_similarity.py"
            ],
            acceptance_criteria=[
                "Levenshtein distance computed",
                "Content similarity analyzed",
                "Threshold configurable",
                "Report includes pairs"
            ]
        )

        self.tasks["4.2"] = Task(
            id="4.2",
            name="Consolidation Workflow",
            description="Generate merge scripts for duplicate specs",
            priority=TaskPriority.MEDIUM,
            estimated_hours=10.0,
            phase="Phase 4",
            dependencies=["4.1"],
            acceptance_criteria=[
                "Merge script generated",
                "Preview available",
                "Rollback possible",
                "Traceability maintained"
            ]
        )

        self.tasks["4.3"] = Task(
            id="4.3",
            name="Pilot Consolidation",
            description="Test consolidation on spec-framework/spec-mode-framework pair",
            priority=TaskPriority.MEDIUM,
            estimated_hours=8.0,
            phase="Phase 4",
            dependencies=["4.2"],
            acceptance_criteria=[
                "Successful merge",
                "No data loss",
                "Tests pass",
                "Documentation updated"
            ]
        )

        self.tasks["4.4"] = Task(
            id="4.4",
            name="CI Integration",
            description="Add GitHub Actions workflow for validation",
            priority=TaskPriority.HIGH,
            estimated_hours=6.0,
            phase="Phase 4",
            dependencies=["1.4"],
            files_created=[
                ".github/workflows/spec-governance.yml"
            ],
            acceptance_criteria=[
                "Workflow runs on PR",
                "Fails on incomplete specs",
                "Report posted as comment",
                "Status badge available"
            ]
        )

        self.tasks["4.5"] = Task(
            id="4.5",
            name="Performance Optimization",
            description="Optimize validation for large spec sets",
            priority=TaskPriority.LOW,
            estimated_hours=6.0,
            phase="Phase 4",
            dependencies=["1.2"],
            acceptance_criteria=[
                "Validation <3s for 105 specs",
                "Parallel processing used",
                "Memory efficient",
                "Cached where possible"
            ]
        )

        # Phase 5: Rollout & Remediation (Week 5) - 32 hours
        self.tasks["5.1"] = Task(
            id="5.1",
            name="Fix Incomplete Specs",
            description="Generate and review stubs for 23 incomplete specs",
            priority=TaskPriority.CRITICAL,
            estimated_hours=16.0,
            phase="Phase 5",
            dependencies=["3.2"],
            acceptance_criteria=[
                "All 23 specs have required files",
                "Stubs reviewed and customized",
                "Validation passes",
                "Committed to repo"
            ]
        )

        self.tasks["5.2"] = Task(
            id="5.2",
            name="Clean Extra Files",
            description="Move/archive 16 specs with extra files",
            priority=TaskPriority.HIGH,
            estimated_hours=8.0,
            phase="Phase 5",
            dependencies=["2.4"],
            acceptance_criteria=[
                "Extra files moved correctly",
                "Logs preserved",
                "Specs cleaner",
                "Documentation updated"
            ]
        )

        self.tasks["5.3"] = Task(
            id="5.3",
            name="Complete Documentation",
            description="Finalize all governance documentation",
            priority=TaskPriority.MEDIUM,
            estimated_hours=4.0,
            phase="Phase 5",
            dependencies=["2.6"],
            acceptance_criteria=[
                "All docs complete",
                "Examples current",
                "README updated",
                "Links valid"
            ]
        )

        self.tasks["5.4"] = Task(
            id="5.4",
            name="Team Training",
            description="Conduct training on spec governance",
            priority=TaskPriority.MEDIUM,
            estimated_hours=4.0,
            phase="Phase 5",
            dependencies=["5.1", "5.2", "5.3"],
            acceptance_criteria=[
                "Training materials prepared",
                "Session conducted",
                "Feedback collected",
                "Q&A documented"
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
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                continue

            if filter_priority and task.priority.value > filter_priority.value:
                continue

            if task.can_execute(self.completed_tasks):
                executable.append(task)

        return sorted(executable, key=lambda t: (t.priority.value, t.id))

    def execute_task(self, task_id: str, dry_run: bool = False) -> bool:
        """Execute a single task."""
        if task_id not in self.tasks:
            self.logger.error(f"Task {task_id} not found")
            return False

        task = self.tasks[task_id]

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
            task.status = TaskStatus.COMPLETED
            self.completed_tasks.add(task_id)
            return True

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

    def validate_dag(self) -> bool:
        """Validate DAG structure for cycles and missing dependencies."""
        self.logger.info("Validating DAG structure...")

        errors = []

        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    errors.append(f"Task {task_id} depends on non-existent task {dep}")

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
        report.append("Spec Consistency Governance - DAG Execution Status")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

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

        executable = self.get_executable_tasks()
        report.append(f"READY TO EXECUTE ({len(executable)} tasks)")
        report.append("-" * 80)
        for task in executable[:5]:
            report.append(f"  {task.id}: {task.name} ({task.priority.name}, {task.estimated_hours}h)")
        if len(executable) > 5:
            report.append(f"  ... and {len(executable) - 5} more")
        report.append("")

        phases = sorted(set(t.phase for t in self.tasks.values()))
        report.append("PROGRESS BY PHASE")
        report.append("-" * 80)
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
        description="Spec Consistency Governance DAG Executor"
    )
    parser.add_argument(
        "--phase",
        choices=["1", "2", "3", "4", "5", "all"],
        help="Execute specific phase"
    )
    parser.add_argument(
        "--task",
        help="Execute specific task (e.g., 1.1, 1.2)"
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

    dag = SpecConsistencyDAG()

    if args.validate or not any([args.phase, args.task, args.status]):
        if not dag.validate_dag():
            sys.exit(1)
        print("\n✓ DAG validation passed")
        print(f"\nTotal tasks: {len(dag.tasks)}")
        print(f"Executable now: {len(dag.get_executable_tasks())}")

    if args.status or not any([args.phase, args.task]):
        print("\n" + dag.generate_execution_report())

    if args.phase:
        if args.phase == "all":
            phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"]
            success = all(dag.execute_phase(p, dry_run=args.dry_run) for p in phases)
        else:
            success = dag.execute_phase(f"Phase {args.phase}", dry_run=args.dry_run)
        sys.exit(0 if success else 1)

    if args.task:
        success = dag.execute_task(args.task, dry_run=args.dry_run)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
