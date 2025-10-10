#!/usr/bin/env python3
"""
CMS Task Audit System - Comprehensive Task Status Analysis

Analyzes all CMS tasks, calculates audit sample sizes, and generates
confusion matrices for task completion verification.
"""

import re
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class TaskInfo:
    """Information about a single task."""
    id: str
    title: str
    phase: str
    priority: str
    estimated_effort: str
    dependencies: List[str]
    assignee: str
    acceptance_criteria: List[str]
    completed_criteria: int
    total_criteria: int
    completion_percentage: float
    status: str  # 'completed', 'in_progress', 'not_started'


class CMSTaskAuditor:
    """Comprehensive CMS task auditing system."""
    
    def __init__(self):
        self.tasks: List[TaskInfo] = []
        self.task_stats = defaultdict(int)
        
    def parse_cms_tasks(self, tasks_file: str = ".kiro/specs/cms-architecture/tasks.md") -> List[TaskInfo]:
        """Parse CMS tasks from the tasks.md file."""
        try:
            with open(tasks_file, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ Tasks file not found: {tasks_file}")
            return []
        
        tasks = []
        current_phase = ""
        
        # Find all task sections using regex
        task_pattern = r'### (Task \d+\.\d+: .+?)\n(.*?)(?=### Task \d+\.\d+:|## Phase \d+:|$)'
        phase_pattern = r'## (Phase \d+: .+?)\n'
        
        # Extract phases
        phases = re.findall(phase_pattern, content)
        phase_map = {}
        
        # Map tasks to phases by position
        phase_positions = [(m.start(), m.group(1)) for m in re.finditer(phase_pattern, content)]
        
        # Find all tasks
        task_matches = re.finditer(task_pattern, content, re.DOTALL)
        
        for match in task_matches:
            header = match.group(1)
            section_content = match.group(2)
            
            # Find which phase this task belongs to
            task_position = match.start()
            current_phase = "Unknown Phase"
            
            for phase_pos, phase_name in reversed(phase_positions):
                if task_position > phase_pos:
                    current_phase = phase_name
                    break
            
            task = self._parse_task_section(header, section_content, current_phase)
            if task:
                tasks.append(task)
        
        self.tasks = tasks
        return tasks
    
    def _parse_task_section(self, header: str, content: str, phase: str) -> TaskInfo:
        """Parse a single task section."""
        # Extract task ID and title
        task_match = re.match(r'Task (\d+\.\d+): (.+)', header)
        if not task_match:
            print(f"Warning: Could not parse task header: {header}")
            return None
        
        task_id = task_match.group(1)
        title = task_match.group(2)
        
        # Extract metadata
        priority_match = re.search(r'\*\*Priority:\*\* (\w+)', content)
        priority = priority_match.group(1) if priority_match else "UNKNOWN"
        
        effort_match = re.search(r'\*\*Estimated Effort:\*\* (.+)', content)
        effort = effort_match.group(1) if effort_match else "Unknown"
        
        assignee_match = re.search(r'\*\*Assignee:\*\* (.+)', content)
        assignee = assignee_match.group(1) if assignee_match else "Unassigned"
        
        dependencies_match = re.search(r'\*\*Dependencies:\*\* (.+)', content)
        dependencies = []
        if dependencies_match:
            dep_text = dependencies_match.group(1)
            if dep_text != "None":
                dependencies = [d.strip() for d in dep_text.split(',')]
        
        # Extract acceptance criteria
        criteria_section = re.search(r'\*\*Acceptance Criteria:\*\*\s*\n(.*?)\n\n', content, re.DOTALL)
        acceptance_criteria = []
        completed_count = 0
        
        if criteria_section:
            criteria_text = criteria_section.group(1)
            criteria_lines = [line.strip() for line in criteria_text.split('\n') if line.strip()]
            
            for line in criteria_lines:
                if line.startswith('- ['):
                    acceptance_criteria.append(line)
                    if line.startswith('- [x]') or line.startswith('- [X]'):
                        completed_count += 1
        
        total_criteria = len(acceptance_criteria)
        completion_percentage = (completed_count / total_criteria * 100) if total_criteria > 0 else 0
        
        # Determine status
        if completion_percentage == 100:
            status = "completed"
        elif completion_percentage > 0:
            status = "in_progress"
        else:
            status = "not_started"
        
        return TaskInfo(
            id=task_id,
            title=title,
            phase=phase,
            priority=priority,
            estimated_effort=effort,
            dependencies=dependencies,
            assignee=assignee,
            acceptance_criteria=acceptance_criteria,
            completed_criteria=completed_count,
            total_criteria=total_criteria,
            completion_percentage=completion_percentage,
            status=status
        )
    
    def calculate_task_statistics(self) -> Dict[str, Any]:
        """Calculate comprehensive task statistics."""
        stats = {
            "total_tasks": len(self.tasks),
            "by_status": defaultdict(int),
            "by_phase": defaultdict(int),
            "by_priority": defaultdict(int),
            "by_assignee": defaultdict(int),
            "completion_distribution": defaultdict(int),
            "criteria_stats": {
                "total_criteria": 0,
                "completed_criteria": 0,
                "completion_rate": 0
            }
        }
        
        total_criteria = 0
        completed_criteria = 0
        
        for task in self.tasks:
            stats["by_status"][task.status] += 1
            stats["by_phase"][task.phase] += 1
            stats["by_priority"][task.priority] += 1
            stats["by_assignee"][task.assignee] += 1
            
            # Completion percentage buckets
            if task.completion_percentage == 100:
                bucket = "100%"
            elif task.completion_percentage >= 75:
                bucket = "75-99%"
            elif task.completion_percentage >= 50:
                bucket = "50-74%"
            elif task.completion_percentage >= 25:
                bucket = "25-49%"
            elif task.completion_percentage > 0:
                bucket = "1-24%"
            else:
                bucket = "0%"
            
            stats["completion_distribution"][bucket] += 1
            
            total_criteria += task.total_criteria
            completed_criteria += task.completed_criteria
        
        stats["criteria_stats"]["total_criteria"] = total_criteria
        stats["criteria_stats"]["completed_criteria"] = completed_criteria
        stats["criteria_stats"]["completion_rate"] = (completed_criteria / total_criteria * 100) if total_criteria > 0 else 0
        
        return stats
    
    def calculate_audit_requirements(self, status_filter: str = "completed") -> Dict[str, Any]:
        """Calculate audit requirements for tasks with specific status."""
        filtered_tasks = [task for task in self.tasks if task.status == status_filter]
        total_filtered = len(filtered_tasks)
        
        if total_filtered == 0:
            return {
                "status_filter": status_filter,
                "total_tasks": 0,
                "audit_required": 0,
                "audit_percentage": 0,
                "recommendation": "NO_AUDIT_NEEDED",
                "reason": f"No tasks found with status '{status_filter}'"
            }
        
        # Calculate audit sample size for 99% confidence, 1% error
        z_score = 2.576  # 99% confidence
        margin_of_error = 0.01
        expected_accuracy = 0.95
        
        p = expected_accuracy
        n_infinite = (z_score**2 * p * (1 - p)) / (margin_of_error**2)
        n_corrected = n_infinite / (1 + (n_infinite - 1) / total_filtered)
        sample_size = min(math.ceil(n_corrected), total_filtered)
        
        percentage = (sample_size / total_filtered) * 100
        
        if percentage >= 90:
            recommendation = "FULL_AUDIT"
            reason = "Sample size approaches population size"
        elif percentage >= 50:
            recommendation = "LARGE_SAMPLE"
            reason = "Large sample needed for high confidence"
        else:
            recommendation = "STATISTICAL_SAMPLE"
            reason = "Statistical sampling sufficient"
        
        return {
            "status_filter": status_filter,
            "total_tasks": total_filtered,
            "audit_required": sample_size,
            "audit_percentage": percentage,
            "recommendation": recommendation,
            "reason": reason,
            "confidence_level": "99%",
            "max_error_rate": "1%",
            "tasks_to_audit": [task.id for task in filtered_tasks[:sample_size]]
        }
    
    def generate_confusion_matrix_analysis(self) -> Dict[str, Any]:
        """Generate confusion matrix analysis for all task statuses."""
        
        # For demonstration, we'll simulate actual vs. reported status
        # In real implementation, this would come from actual audit results
        
        confusion_matrices = {}
        
        for status in ["completed", "in_progress", "not_started"]:
            tasks_with_status = [task for task in self.tasks if task.status == status]
            total = len(tasks_with_status)
            
            if total == 0:
                continue
            
            # Simulate audit results (in real implementation, this would be actual audit data)
            if status == "completed":
                # Assume 95% of "completed" tasks are actually completed
                true_positives = int(total * 0.95)
                false_positives = total - true_positives
                true_negatives = 0  # Not applicable for this analysis
                false_negatives = 0  # Not applicable for this analysis
            elif status == "in_progress":
                # Assume 90% of "in_progress" tasks are actually in progress
                true_positives = int(total * 0.90)
                false_positives = total - true_positives
                true_negatives = 0
                false_negatives = 0
            else:  # not_started
                # Assume 98% of "not_started" tasks are actually not started
                true_positives = int(total * 0.98)
                false_positives = total - true_positives
                true_negatives = 0
                false_negatives = 0
            
            confusion_matrices[status] = {
                "total_tasks": total,
                "true_positives": true_positives,
                "false_positives": false_positives,
                "true_negatives": true_negatives,
                "false_negatives": false_negatives,
                "accuracy": true_positives / total if total > 0 else 0,
                "precision": true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0,
                "recall": true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            }
        
        return confusion_matrices
    
    def print_comprehensive_audit_report(self):
        """Print comprehensive audit report."""
        print("🔍 CMS TASK AUDIT SYSTEM - COMPREHENSIVE ANALYSIS")
        print("=" * 70)
        print()
        
        # Parse tasks
        tasks = self.parse_cms_tasks()
        if not tasks:
            print("❌ No tasks found to analyze")
            return
        
        # Calculate statistics
        stats = self.calculate_task_statistics()
        
        print(f"📊 TASK OVERVIEW")
        print(f"Total Tasks: {stats['total_tasks']}")
        print(f"Total Acceptance Criteria: {stats['criteria_stats']['total_criteria']}")
        print(f"Completed Criteria: {stats['criteria_stats']['completed_criteria']}")
        print(f"Overall Completion Rate: {stats['criteria_stats']['completion_rate']:.1f}%")
        print()
        
        print(f"📈 TASK STATUS DISTRIBUTION")
        for status, count in stats['by_status'].items():
            percentage = (count / stats['total_tasks']) * 100
            print(f"  {status.replace('_', ' ').title()}: {count} tasks ({percentage:.1f}%)")
        print()
        
        print(f"🎯 COMPLETION DISTRIBUTION")
        for bucket, count in stats['completion_distribution'].items():
            percentage = (count / stats['total_tasks']) * 100
            print(f"  {bucket}: {count} tasks ({percentage:.1f}%)")
        print()
        
        print(f"📋 BY PHASE")
        for phase, count in stats['by_phase'].items():
            percentage = (count / stats['total_tasks']) * 100
            print(f"  {phase}: {count} tasks ({percentage:.1f}%)")
        print()
        
        print(f"⚡ BY PRIORITY")
        for priority, count in stats['by_priority'].items():
            percentage = (count / stats['total_tasks']) * 100
            print(f"  {priority}: {count} tasks ({percentage:.1f}%)")
        print()
        
        # Audit requirements for each status
        print(f"🔍 AUDIT REQUIREMENTS BY STATUS")
        print("=" * 50)
        
        for status in ["completed", "in_progress", "not_started"]:
            audit_req = self.calculate_audit_requirements(status)
            if audit_req['total_tasks'] > 0:
                print(f"\n📊 {status.replace('_', ' ').upper()} TASKS AUDIT")
                print(f"Total tasks: {audit_req['total_tasks']}")
                print(f"Audit required: {audit_req['audit_required']} tasks")
                print(f"Audit percentage: {audit_req['audit_percentage']:.1f}%")
                print(f"Recommendation: {audit_req['recommendation']}")
                print(f"Reason: {audit_req['reason']}")
                print(f"Confidence: {audit_req['confidence_level']}")
                print(f"Max error rate: {audit_req['max_error_rate']}")
        
        # Confusion matrix analysis
        print(f"\n🎯 CONFUSION MATRIX ANALYSIS")
        print("=" * 50)
        
        confusion_matrices = self.generate_confusion_matrix_analysis()
        
        for status, matrix in confusion_matrices.items():
            print(f"\n📈 {status.replace('_', ' ').upper()} TASKS CONFUSION MATRIX")
            print(f"                    ACTUAL STATUS")
            print(f"                 {status.title()} | Other")
            print(f"REPORTED {status.title():>8}    {matrix['true_positives']:>3}   |   {matrix['false_positives']:>3}")
            print(f"         Other    {matrix['false_negatives']:>3}   |   {matrix['true_negatives']:>3}")
            print(f"")
            print(f"Accuracy: {matrix['accuracy']:.1%}")
            print(f"Precision: {matrix['precision']:.1%}")
            print(f"Expected False Positives: {matrix['false_positives']} tasks")
        
        print(f"\n💡 PRACTICAL RECOMMENDATIONS")
        print("=" * 50)
        
        completed_audit = self.calculate_audit_requirements("completed")
        if completed_audit['total_tasks'] > 0:
            print(f"✅ COMPLETED TASKS:")
            print(f"   • Audit {completed_audit['audit_required']} out of {completed_audit['total_tasks']} completed tasks")
            print(f"   • Focus on verifying acceptance criteria are actually met")
            print(f"   • Check for false positives (tasks marked complete but not actually done)")
        
        in_progress_audit = self.calculate_audit_requirements("in_progress")
        if in_progress_audit['total_tasks'] > 0:
            print(f"🔄 IN PROGRESS TASKS:")
            print(f"   • Review {in_progress_audit['audit_required']} out of {in_progress_audit['total_tasks']} in-progress tasks")
            print(f"   • Verify actual progress matches reported progress")
            print(f"   • Identify tasks that may be stalled or blocked")
        
        not_started_audit = self.calculate_audit_requirements("not_started")
        if not_started_audit['total_tasks'] > 0:
            print(f"⏳ NOT STARTED TASKS:")
            print(f"   • Sample {not_started_audit['audit_required']} out of {not_started_audit['total_tasks']} not-started tasks")
            print(f"   • Check for tasks that may have actually begun")
            print(f"   • Verify dependencies are properly tracked")
        
        print(f"\n🎯 AUDIT FOCUS AREAS")
        print("=" * 30)
        print("1. **False Positives**: Tasks marked complete but not actually done")
        print("2. **Progress Accuracy**: Verify completion percentages are realistic")
        print("3. **Dependency Validation**: Ensure prerequisite tasks are actually complete")
        print("4. **Acceptance Criteria**: Verify criteria are measurable and met")
        print("5. **Resource Allocation**: Confirm assignees are actually working on tasks")


def main():
    """Main execution function."""
    auditor = CMSTaskAuditor()
    auditor.print_comprehensive_audit_report()


if __name__ == "__main__":
    main()