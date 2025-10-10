#!/usr/bin/env python3
"""
DevPost Integration Progress Tracker
Tracks implementation progress against the daily plan
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class Task:
    """Individual task tracking"""

    id: str
    name: str
    estimated_hours: float
    actual_hours: float = 0.0
    status: str = "not_started"  # not_started, in_progress, completed, blocked
    start_time: str = ""
    end_time: str = ""
    notes: str = ""
    blockers: List[str] = None

    def __post_init__(self):
        if self.blockers is None:
            self.blockers = []


@dataclass
class Milestone:
    """Milestone tracking"""

    name: str
    target_time: str
    criteria: str
    status: str = "not_started"  # not_started, in_progress, completed, at_risk
    completion_time: str = ""
    notes: str = ""


class DevPostProgressTracker:
    """Tracks DevPost integration implementation progress"""

    def __init__(self):
        self.tracker_file = Path("devpost_progress.json")
        self.tasks = self._initialize_tasks()
        self.milestones = self._initialize_milestones()
        self.daily_metrics = self._initialize_daily_metrics()

    def _initialize_tasks(self) -> List[Task]:
        """Initialize all tasks from the implementation plan"""
        return [
            # Phase 1: DevPost API Client
            Task("1.1", "Create DevpostAPIClient class with HTTP handling", 1.0),
            Task("1.2", "Implement project CRUD operations", 1.0),
            Task("1.3", "Add error handling and retry logic", 0.5),
            # Phase 2: Authentication Service
            Task("2.1", "Implement OAuth authentication flow", 0.75),
            Task("2.2", "Add API key authentication fallback", 0.5),
            Task("2.3", "Implement token storage and refresh", 0.25),
            # Phase 3: Project Manager Fixes
            Task("3.1", "Fix DevpostAPIClient import and integration", 0.5),
            Task("3.2", "Implement project connection logic", 0.75),
            Task("3.3", "Add project status tracking", 0.25),
            # Phase 4: Configuration System
            Task("4.1", "Fix DevpostConfig API mismatch", 0.5),
            Task("4.2", "Implement project connections support", 0.75),
            Task("4.3", "Add configuration validation", 0.25),
            # Phase 5: Testing and Validation
            Task("5.1", "Run unit tests and fix failures", 0.5),
            Task("5.2", "Create basic integration test", 0.33),
            Task("5.3", "Update documentation", 0.17),
        ]

    def _initialize_milestones(self) -> List[Milestone]:
        """Initialize milestones from the implementation plan"""
        return [
            Milestone(
                "API Client Complete",
                "End of morning session",
                "Can make authenticated API calls",
            ),
            Milestone(
                "Authentication Working",
                "End of morning session",
                "OAuth and API key auth both working",
            ),
            Milestone(
                "Project Manager Fixed",
                "Mid-afternoon",
                "No import errors, basic functionality",
            ),
            Milestone(
                "Configuration Fixed",
                "End of afternoon",
                "DevpostConfig works with tests",
            ),
            Milestone(
                "Integration Working", "End of day", "End-to-end workflow functional"
            ),
        ]

    def _initialize_daily_metrics(self) -> Dict[str, Any]:
        """Initialize daily metrics tracking"""
        return {
            "date": datetime.now().isoformat(),
            "total_tasks": len(self.tasks),
            "completed_tasks": 0,
            "in_progress_tasks": 0,
            "blocked_tasks": 0,
            "total_estimated_hours": sum(task.estimated_hours for task in self.tasks),
            "total_actual_hours": 0.0,
            "completion_percentage": 0.0,
            "tests_passing": 28,  # Current data model tests
            "integration_tests_passing": 0,
            "milestones_completed": 0,
            "risks_identified": [],
            "notes": [],
        }

    def start_task(self, task_id: str, notes: str = "") -> bool:
        """Start working on a task"""
        task = self._find_task(task_id)
        if not task:
            return False

        if task.status == "completed":
            print(f"⚠️ Task {task_id} is already completed")
            return False

        task.status = "in_progress"
        task.start_time = datetime.now().isoformat()
        task.notes = notes

        self._update_metrics()
        self._save_progress()
        print(f"🚀 Started task {task_id}: {task.name}")
        return True

    def complete_task(
        self, task_id: str, actual_hours: float = None, notes: str = ""
    ) -> bool:
        """Mark a task as completed"""
        task = self._find_task(task_id)
        if not task:
            return False

        task.status = "completed"
        task.end_time = datetime.now().isoformat()
        if actual_hours is not None:
            task.actual_hours = actual_hours
        task.notes = notes

        self._update_metrics()
        self._save_progress()
        print(f"✅ Completed task {task_id}: {task.name}")
        return True

    def block_task(self, task_id: str, blocker: str, notes: str = "") -> bool:
        """Mark a task as blocked"""
        task = self._find_task(task_id)
        if not task:
            return False

        task.status = "blocked"
        task.blockers.append(blocker)
        task.notes = notes

        self._update_metrics()
        self._save_progress()
        print(f"🚫 Blocked task {task_id}: {blocker}")
        return True

    def complete_milestone(self, milestone_name: str, notes: str = "") -> bool:
        """Mark a milestone as completed"""
        milestone = self._find_milestone(milestone_name)
        if not milestone:
            return False

        milestone.status = "completed"
        milestone.completion_time = datetime.now().isoformat()
        milestone.notes = notes

        self._update_metrics()
        self._save_progress()
        print(f"🎯 Completed milestone: {milestone_name}")
        return True

    def add_risk(self, risk: str, impact: str = "medium") -> None:
        """Add a risk to tracking"""
        self.daily_metrics["risks_identified"].append(
            {"risk": risk, "impact": impact, "timestamp": datetime.now().isoformat()}
        )
        self._save_progress()
        print(f"⚠️ Risk identified: {risk} (Impact: {impact})")

    def add_note(self, note: str) -> None:
        """Add a progress note"""
        self.daily_metrics["notes"].append(
            {"note": note, "timestamp": datetime.now().isoformat()}
        )
        self._save_progress()
        print(f"📝 Note added: {note}")

    def update_test_status(
        self, unit_tests: int = None, integration_tests: int = None
    ) -> None:
        """Update test passing status"""
        if unit_tests is not None:
            self.daily_metrics["tests_passing"] = unit_tests
        if integration_tests is not None:
            self.daily_metrics["integration_tests_passing"] = integration_tests

        self._save_progress()
        print(
            f"🧪 Test status updated: {unit_tests} unit, {integration_tests} integration"
        )

    def _find_task(self, task_id: str) -> Task:
        """Find task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def _find_milestone(self, name: str) -> Milestone:
        """Find milestone by name"""
        for milestone in self.milestones:
            if milestone.name == name:
                return milestone
        return None

    def _update_metrics(self) -> None:
        """Update daily metrics based on current task status"""
        completed = sum(1 for task in self.tasks if task.status == "completed")
        in_progress = sum(1 for task in self.tasks if task.status == "in_progress")
        blocked = sum(1 for task in self.tasks if task.status == "blocked")
        actual_hours = sum(task.actual_hours for task in self.tasks)

        self.daily_metrics["completed_tasks"] = completed
        self.daily_metrics["in_progress_tasks"] = in_progress
        self.daily_metrics["blocked_tasks"] = blocked
        self.daily_metrics["total_actual_hours"] = actual_hours
        self.daily_metrics["completion_percentage"] = (
            completed / len(self.tasks)
        ) * 100
        self.daily_metrics["milestones_completed"] = sum(
            1 for m in self.milestones if m.status == "completed"
        )

    def _save_progress(self) -> None:
        """Save progress to file"""
        data = {
            "tasks": [asdict(task) for task in self.tasks],
            "milestones": [asdict(milestone) for milestone in self.milestones],
            "daily_metrics": self.daily_metrics,
        }

        with open(self.tracker_file, "w") as f:
            json.dump(data, f, indent=2)

    def load_progress(self) -> None:
        """Load progress from file"""
        if not self.tracker_file.exists():
            return

        with open(self.tracker_file, "r") as f:
            data = json.load(f)

        # Load tasks
        self.tasks = [Task(**task_data) for task_data in data.get("tasks", [])]

        # Load milestones
        self.milestones = [
            Milestone(**milestone_data) for milestone_data in data.get("milestones", [])
        ]

        # Load daily metrics
        self.daily_metrics = data.get("daily_metrics", self._initialize_daily_metrics())

    def print_status(self) -> None:
        """Print current status"""
        print("\n" + "=" * 60)
        print("🚀 DEVPOST INTEGRATION PROGRESS STATUS")
        print("=" * 60)

        # Daily metrics
        metrics = self.daily_metrics
        print(f"📅 Date: {metrics['date']}")
        print(
            f"📊 Progress: {metrics['completed_tasks']}/{metrics['total_tasks']} tasks ({metrics['completion_percentage']:.1f}%)"
        )
        print(
            f"⏱️ Time: {metrics['total_actual_hours']:.1f}/{metrics['total_estimated_hours']:.1f} hours"
        )
        print(
            f"🧪 Tests: {metrics['tests_passing']} unit, {metrics['integration_tests_passing']} integration"
        )
        print(
            f"🎯 Milestones: {metrics['milestones_completed']}/{len(self.milestones)} completed"
        )

        # Current tasks
        print(f"\n🔄 In Progress ({metrics['in_progress_tasks']}):")
        for task in self.tasks:
            if task.status == "in_progress":
                print(f"   • {task.id}: {task.name}")

        # Blocked tasks
        if metrics["blocked_tasks"] > 0:
            print(f"\n🚫 Blocked ({metrics['blocked_tasks']}):")
            for task in self.tasks:
                if task.status == "blocked":
                    print(f"   • {task.id}: {task.name} - {', '.join(task.blockers)}")

        # Recent milestones
        print(f"\n🎯 Milestones:")
        for milestone in self.milestones:
            status_icon = "✅" if milestone.status == "completed" else "⏳"
            print(f"   {status_icon} {milestone.name}: {milestone.status}")

        # Risks
        if metrics["risks_identified"]:
            print(f"\n⚠️ Risks:")
            for risk in metrics["risks_identified"][-3:]:  # Show last 3
                print(f"   • {risk['risk']} ({risk['impact']})")

        print("=" * 60)


def main():
    """Main function for command-line usage"""
    tracker = DevPostProgressTracker()
    tracker.load_progress()
    tracker.print_status()


if __name__ == "__main__":
    main()
