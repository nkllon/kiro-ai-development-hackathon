"""
Phase Optimizer Core Core

This module was extracted from phase_optimizer_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import math
from ..models.dag_models import (
    MVPPhase,
    TaskNode,
    ParallelGroup,
    ResourceRequirements,
    MVPRoute,
    RiskFactor,
)
from ..models.enums import TaskStatus, RiskType, RiskImpact


@dataclass
class PhaseOptimizationResult:
    """Result of phase optimization analysis."""

    optimized_phases: List[MVPPhase]
    total_timeline: int
    critical_path_phases: List[int]
    resource_requirements: Dict[int, ResourceRequirements]
    optimization_metrics: Dict[str, float]


@dataclass
class TimelineEstimation:
    """Timeline estimation with confidence intervals."""

    optimistic_weeks: int
    realistic_weeks: int
    pessimistic_weeks: int
    confidence_level: float
    risk_factors: List[str]


class PhaseOptimizer:
    """
    Systematic MVP phase optimizer with extreme prejudice.

    Creates optimal phases with clear deliverables, success criteria,
    and realistic timeline estimation that SLAYS complexity.
    """

    def __init__(self):
        self.working_hours_per_week = 40
        self.parallel_efficiency = 0.85
        self.phase_overhead = 0.15
        self.risk_buffer = 0.2
        self.max_phase_duration = 3
        self.min_parallel_tasks = 2
        self.complexity_threshold = 0.7

    def optimize_mvp_phases_with_extreme_prejudice(
        self, mvp_route: MVPRoute
    ) -> PhaseOptimizationResult:
        """
        Optimize MVP phases with BEASTMASTER systematic annihilation.

        Args:
            mvp_route: MVP route to optimize with extreme prejudice

        Returns:
            PhaseOptimizationResult: Systematically optimized phases
        """
        task_analysis = self._analyze_tasks_with_prejudice(mvp_route.critical_tasks)
        phase_groups = self._create_optimal_phase_groups(
            mvp_route.critical_tasks, task_analysis
        )
        optimized_phases = []
        resource_requirements = {}
        for i, (phase_name, tasks) in enumerate(phase_groups):
            phase_number = i + 1
            parallel_groups = self._create_high_velocity_parallel_groups(tasks)
            resources = self._calculate_systematic_resource_requirements(
                tasks, parallel_groups
            )
            resource_requirements[phase_number] = resources
            objectives = self._define_systematic_objectives(tasks, phase_number)
            deliverables = self._identify_systematic_deliverables(tasks)
            success_criteria = self._define_systematic_success_criteria(
                tasks, deliverables
            )
            timeline = self._calculate_phase_timeline_with_prejudice(
                parallel_groups, resources
            )
            dependencies = self._extract_phase_dependencies(tasks)
            optimized_phases.append(
                MVPPhase(
                    phase_name=phase_name,
                    phase_number=phase_number,
                    objectives=objectives,
                    tasks=tasks,
                    deliverables=deliverables,
                    estimated_duration=timeline,
                    parallel_groups=parallel_groups,
                    success_criteria=success_criteria,
                    dependencies_satisfied=dependencies,
                )
            )
        critical_path_phases = self._identify_critical_path_phases(optimized_phases)
        optimization_metrics = self._calculate_optimization_metrics(optimized_phases)
        total_timeline = sum((phase.estimated_duration for phase in optimized_phases))
        return PhaseOptimizationResult(
            optimized_phases=optimized_phases,
            total_timeline=total_timeline,
            critical_path_phases=critical_path_phases,
            resource_requirements=resource_requirements,
            optimization_metrics=optimization_metrics,
        )

    def estimate_timeline_with_systematic_precision(
        self,
        tasks: List[TaskNode],
        parallel_groups: List[ParallelGroup],
        resource_constraints: Optional[Dict] = None,
    ) -> TimelineEstimation:
        """
        Estimate timeline with systematic precision and confidence intervals.

        Args:
            tasks: Tasks to estimate
            parallel_groups: Parallel execution groups
            resource_constraints: Optional resource constraints

        Returns:
            TimelineEstimation: Precise timeline estimation with confidence
        """
        base_effort = sum((task.estimated_effort for task in tasks))
        if parallel_groups:
            max_parallel_effort = max(
                (
                    sum((task.estimated_effort for task in group.tasks))
                    for group in parallel_groups
                )
            )
            parallel_effort = max_parallel_effort * self.parallel_efficiency
        else:
            parallel_effort = base_effort
        base_weeks = parallel_effort / self.working_hours_per_week
        optimistic_weeks = max(1, int(base_weeks * 0.8))
        realistic_weeks = max(1, int(base_weeks * (1 + self.phase_overhead)))
        pessimistic_weeks = max(
            2, int(base_weeks * (1 + self.phase_overhead + self.risk_buffer))
        )
        confidence_level = self._calculate_timeline_confidence(tasks, parallel_groups)
        risk_factors = self._identify_timeline_risk_factors(tasks)
        return TimelineEstimation(
            optimistic_weeks=optimistic_weeks,
            realistic_weeks=realistic_weeks,
            pessimistic_weeks=pessimistic_weeks,
            confidence_level=confidence_level,
            risk_factors=risk_factors,
        )

    def calculate_resource_requirements_with_precision(
        self, phases: List[MVPPhase]
    ) -> Dict[int, ResourceRequirements]:
        """
        Calculate systematic resource requirements for each phase.

        Args:
            phases: MVP phases to analyze

        Returns:
            Dict[int, ResourceRequirements]: Phase number -> resource requirements
        """
        resource_requirements = {}
        for phase in phases:
            required_skills = self._analyze_required_skills(phase.tasks)
            total_effort = sum((task.estimated_effort for task in phase.tasks))
            phase_weeks = phase.estimated_duration
            if phase_weeks > 0:
                developers_needed = max(
                    1,
                    math.ceil(
                        total_effort / (self.working_hours_per_week * phase_weeks)
                    ),
                )
            else:
                developers_needed = 1
            tools_required = self._identify_required_tools(phase.tasks)
            resource_requirements[phase.phase_number] = ResourceRequirements(
                developers_needed=developers_needed,
                skill_requirements=required_skills,
                estimated_hours=total_effort,
                tools_required=tools_required,
            )
        return resource_requirements

    def _analyze_tasks_with_prejudice(self, tasks: List[TaskNode]) -> Dict[str, float]:
        """Analyze tasks with BEASTMASTER systematic prejudice."""
        analysis = {}
        for task in tasks:
            complexity_score = self._calculate_task_complexity(task)
            risk_score = self._calculate_task_risk(task)
            value_score = self._calculate_task_value(task)
            priority_score = 1.0 / max(task.priority, 1)
            analysis[task.task_id] = {
                "complexity": complexity_score,
                "risk": risk_score,
                "value": value_score,
                "priority": priority_score,
                "combined": value_score
                * priority_score
                / max(complexity_score * risk_score, 0.1),
            }
        return analysis

    def _create_optimal_phase_groups(
        self, tasks: List[TaskNode], analysis: Dict[str, float]
    ) -> List[Tuple[str, List[TaskNode]]]:
        """Create optimal phase groups with SYSTEMATIC PRECISION."""
        sorted_tasks = self._sort_tasks_systematically(tasks, analysis)
        phases = []
        current_phase_tasks = []
        current_phase_effort = 0
        phase_counter = 0
        max_phase_effort = self.max_phase_duration * self.working_hours_per_week
        for task in sorted_tasks:
            if (
                current_phase_effort + task.estimated_effort <= max_phase_effort
                and len(current_phase_tasks) < 8
            ):
                current_phase_tasks.append(task)
                current_phase_effort += task.estimated_effort
            else:
                if current_phase_tasks:
                    phase_counter += 1
                    phase_name = self._generate_phase_name(
                        current_phase_tasks, phase_counter
                    )
                    phases.append((phase_name, current_phase_tasks.copy()))
                current_phase_tasks = [task]
                current_phase_effort = task.estimated_effort
        if current_phase_tasks:
            phase_counter += 1
            phase_name = self._generate_phase_name(current_phase_tasks, phase_counter)
            phases.append((phase_name, current_phase_tasks))
        return phases

    def _create_high_velocity_parallel_groups(
        self, tasks: List[TaskNode]
    ) -> List[ParallelGroup]:
        """Create high-velocity parallel groups with EXTREME EFFICIENCY."""
        if len(tasks) < self.min_parallel_tasks:
            return [
                ParallelGroup(
                    group_id="single_group",
                    tasks=tasks,
                    estimated_duration=(
                        max((task.estimated_effort for task in tasks)) // 8
                        if tasks
                        else 1
                    ),
                    coordination_overhead=0.0,
                )
            ]
        groups = []
        remaining_tasks = tasks.copy()
        group_counter = 0
        while remaining_tasks:
            group_counter += 1
            current_group = [remaining_tasks.pop(0)]
            reference_effort = current_group[0].estimated_effort
            i = 0
            while i < len(remaining_tasks) and len(current_group) < 4:
                task = remaining_tasks[i]
                effort_ratio = abs(task.estimated_effort - reference_effort) / max(
                    reference_effort, 1
                )
                if effort_ratio <= 0.5:
                    current_group.append(remaining_tasks.pop(i))
                else:
                    i += 1
            max_effort = max((task.estimated_effort for task in current_group))
            estimated_duration = max(1, max_effort // 8)
            if len(current_group) > 1:
                coordination_overhead = 0.1 + (len(current_group) - 2) * 0.05
            else:
                coordination_overhead = 0.0
            groups.append(
                ParallelGroup(
                    group_id=f"parallel_group_{group_counter}",
                    tasks=current_group,
                    estimated_duration=estimated_duration,
                    coordination_overhead=coordination_overhead,
                )
            )
        return groups

    def _calculate_systematic_resource_requirements(
        self, tasks: List[TaskNode], parallel_groups: List[ParallelGroup]
    ) -> ResourceRequirements:
        """Calculate systematic resource requirements with PRECISION."""
        required_skills = self._analyze_required_skills(tasks)
        total_effort = sum((task.estimated_effort for task in tasks))
        max_concurrent_tasks = (
            max((len(group.tasks) for group in parallel_groups))
            if parallel_groups
            else 1
        )
        developers_needed = min(max_concurrent_tasks, max(1, total_effort // 40))
        tools_required = self._identify_required_tools(tasks)
        return ResourceRequirements(
            developers_needed=developers_needed,
            skill_requirements=required_skills,
            estimated_hours=total_effort,
            tools_required=tools_required,
        )

    def _define_systematic_objectives(
        self, tasks: List[TaskNode], phase_number: int
    ) -> List[str]:
        """Define systematic objectives with CLARITY."""
        objectives = []
        if phase_number == 1:
            objectives.append(
                "🚀 Establish systematic foundation and core infrastructure"
            )
        elif phase_number == 2:
            objectives.append(
                "⚡ Implement core systematic functionality with extreme efficiency"
            )
        elif phase_number == 3:
            objectives.append("🔗 Integrate components with systematic precision")
        else:
            objectives.append("🎯 Complete systematic implementation and validation")
        task_keywords = set()
        for task in tasks:
            words = task.task_name.lower().split()
            task_keywords.update(words)
        if "api" in task_keywords:
            objectives.append("📡 Deliver systematic API with complete functionality")
        if "test" in task_keywords:
            objectives.append(
                "🧪 Achieve systematic test coverage with quality validation"
            )
        if "framework" in task_keywords:
            objectives.append(
                "🏗️ Build systematic framework with extensible architecture"
            )
        if "integration" in task_keywords:
            objectives.append(
                "🔄 Complete systematic integration with dependency validation"
            )
        return objectives

    def _identify_systematic_deliverables(self, tasks: List[TaskNode]) -> List[str]:
        """Identify systematic deliverables with PRECISION."""
        deliverables = set()
        for task in tasks:
            task_text = f"{task.task_name} {task.description}".lower()
            if any(
                (keyword in task_text for keyword in ["api", "endpoint", "interface"])
            ):
                deliverables.add("🔌 Functional API with systematic validation")
            if any(
                (keyword in task_text for keyword in ["framework", "system", "engine"])
            ):
                deliverables.add("🏗️ Systematic framework implementation")
            if any(
                (keyword in task_text for keyword in ["test", "validation", "verify"])
            ):
                deliverables.add("🧪 Comprehensive test suite with systematic coverage")
            if any(
                (keyword in task_text for keyword in ["documentation", "docs", "guide"])
            ):
                deliverables.add("📚 Systematic documentation with examples")
            if any((keyword in task_text for keyword in ["example", "demo", "sample"])):
                deliverables.add("💡 Working examples with systematic validation")
            if any(
                (keyword in task_text for keyword in ["integration", "orchestration"])
            ):
                deliverables.add("🔗 Systematic integration with dependency management")
        return list(deliverables) if deliverables else ["✅ Systematic task completion"]

    def _define_systematic_success_criteria(
        self, tasks: List[TaskNode], deliverables: List[str]
    ) -> List[str]:
        """Define systematic success criteria with RIGOR."""
        criteria = []
        criteria.append(
            f"✅ All {len(tasks)} systematic tasks completed with validation"
        )
        for deliverable in deliverables:
            criteria.append(f"🎯 {deliverable} meets systematic quality standards")
        criteria.append("🛡️ Zero critical systematic violations detected")
        criteria.append("📊 Systematic quality score > 0.9 achieved")
        criteria.append("🔍 Code review and systematic validation completed")
        if len(tasks) > 1:
            criteria.append("🔗 All systematic dependencies validated and integrated")
        return criteria

    def _calculate_phase_timeline_with_prejudice(
        self, parallel_groups: List[ParallelGroup], resources: ResourceRequirements
    ) -> int:
        """Calculate phase timeline with BEASTMASTER PREJUDICE."""
        if not parallel_groups:
            return 1
        max_group_duration = max(
            (group.estimated_duration for group in parallel_groups)
        )
        total_overhead = sum((group.coordination_overhead for group in parallel_groups))
        overhead_days = max_group_duration * total_overhead
        if resources.developers_needed > 4:
            overhead_days += 1
        total_days = max_group_duration + overhead_days
        weeks = max(1, math.ceil(total_days / 5))
        return min(weeks, self.max_phase_duration)

    def _sort_tasks_systematically(
        self, tasks: List[TaskNode], analysis: Dict[str, float]
    ) -> List[TaskNode]:
        """Sort tasks systematically by dependencies and analysis scores."""
        task_lookup = {task.task_id: task for task in tasks}
        sorted_tasks = []
        processed = set()

        def process_task(task: TaskNode):
            if task.task_id in processed:
                return
            for dep_id in task.dependencies:
                if dep_id in task_lookup and dep_id not in processed:
                    process_task(task_lookup[dep_id])
            sorted_tasks.append(task)
            processed.add(task.task_id)

        for task in tasks:
            process_task(task)
        return sorted_tasks

    def _generate_phase_name(self, tasks: List[TaskNode], phase_number: int) -> str:
        """Generate systematic phase name."""
        task_keywords = []
        for task in tasks:
            words = task.task_name.lower().split()
            task_keywords.extend(words)
        keyword_counts = {}
        for keyword in task_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        if keyword_counts:
            dominant_keyword = max(keyword_counts.items(), key=lambda x: x[1])[0]
            if dominant_keyword in ["setup", "infrastructure", "core", "foundation"]:
                return f"Phase {phase_number}: Systematic Foundation"
            elif dominant_keyword in ["implement", "create", "build"]:
                return f"Phase {phase_number}: Systematic Implementation"
            elif dominant_keyword in ["integrate", "orchestration", "coordination"]:
                return f"Phase {phase_number}: Systematic Integration"
            elif dominant_keyword in ["test", "validation", "verify"]:
                return f"Phase {phase_number}: Systematic Validation"
            else:
                return f"Phase {phase_number}: Systematic {dominant_keyword.title()}"
        return f"Phase {phase_number}: Systematic Execution"

    def _calculate_task_complexity(self, task: TaskNode) -> float:
        """Calculate task complexity score."""
        complexity = 0.5
        if task.estimated_effort > 40:
            complexity += 0.3
        elif task.estimated_effort > 20:
            complexity += 0.2
        complex_keywords = [
            "complex",
            "advanced",
            "comprehensive",
            "integrate",
            "optimize",
            "framework",
            "system",
        ]
        task_text = f"{task.task_name} {task.description}".lower()
        for keyword in complex_keywords:
            if keyword in task_text:
                complexity += 0.1
        return min(1.0, complexity)

    def _calculate_task_risk(self, task: TaskNode) -> float:
        """Calculate task risk score."""
        risk = 0.2
        if task.completion_status == TaskStatus.BLOCKED:
            risk += 0.6
        elif task.completion_status == TaskStatus.FAILED:
            risk += 0.8
        elif task.completion_status == TaskStatus.IN_PROGRESS:
            risk += 0.1
        if len(task.dependencies) > 3:
            risk += 0.2
        return min(1.0, risk)

    def _calculate_task_value(self, task: TaskNode) -> float:
        """Calculate task value score."""
        value = 0.5
        high_value_keywords = ["api", "framework", "core", "integration", "system"]
        task_text = f"{task.task_name} {task.description}".lower()
        for keyword in high_value_keywords:
            if keyword in task_text:
                value += 0.2
        if task.completion_status == TaskStatus.COMPLETED:
            value += 0.3
        return min(1.0, value)

    def _analyze_required_skills(self, tasks: List[TaskNode]) -> List[str]:
        """Analyze required skills for tasks."""
        skills = set()
        for task in tasks:
            task_text = f"{task.task_name} {task.description}".lower()
            if any((keyword in task_text for keyword in ["python", "api", "backend"])):
                skills.add("Python Development")
            if any(
                (keyword in task_text for keyword in ["frontend", "ui", "interface"])
            ):
                skills.add("Frontend Development")
            if any(
                (keyword in task_text for keyword in ["test", "testing", "validation"])
            ):
                skills.add("Testing & QA")
            if any(
                (
                    keyword in task_text
                    for keyword in ["devops", "deployment", "infrastructure"]
                )
            ):
                skills.add("DevOps & Infrastructure")
            if any(
                (
                    keyword in task_text
                    for keyword in ["design", "architecture", "system"]
                )
            ):
                skills.add("System Architecture")
            if any((keyword in task_text for keyword in ["documentation", "docs"])):
                skills.add("Technical Writing")
        return list(skills) if skills else ["General Development"]

    def _identify_required_tools(self, tasks: List[TaskNode]) -> List[str]:
        """Identify required tools for tasks."""
        tools = set()
        for task in tasks:
            task_text = f"{task.task_name} {task.description}".lower()
            if any(
                (keyword in task_text for keyword in ["git", "version", "repository"])
            ):
                tools.add("Git")
            if any((keyword in task_text for keyword in ["docker", "container"])):
                tools.add("Docker")
            if any((keyword in task_text for keyword in ["kubernetes", "k8s"])):
                tools.add("Kubernetes")
            if any(
                (
                    keyword in task_text
                    for keyword in ["ci/cd", "pipeline", "deployment"]
                )
            ):
                tools.add("CI/CD Pipeline")
            if any((keyword in task_text for keyword in ["test", "pytest", "testing"])):
                tools.add("Testing Framework")
            if any((keyword in task_text for keyword in ["api", "rest", "endpoint"])):
                tools.add("API Development Tools")
        return list(tools) if tools else ["Standard Development Environment"]

    def _extract_phase_dependencies(self, tasks: List[TaskNode]) -> List[str]:
        """Extract dependencies satisfied by completing this phase."""
        dependencies = set()
        for task in tasks:
            dependencies.update(task.requirements_traced)
        return list(dependencies)

    def _identify_critical_path_phases(self, phases: List[MVPPhase]) -> List[int]:
        """Identify phases on the critical path."""
        critical_phases = []
        for phase in phases:
            total_effort = sum((task.estimated_effort for task in phase.tasks))
            total_dependencies = sum((len(task.dependencies) for task in phase.tasks))
            if total_effort > 80 or total_dependencies > 10:
                critical_phases.append(phase.phase_number)
        return critical_phases

    def _calculate_optimization_metrics(
        self, phases: List[MVPPhase]
    ) -> Dict[str, float]:
        """Calculate optimization metrics."""
        total_tasks = sum((len(phase.tasks) for phase in phases))
        total_effort = sum(
            (sum((task.estimated_effort for task in phase.tasks)) for phase in phases)
        )
        total_parallel_groups = sum((len(phase.parallel_groups) for phase in phases))
        return {
            "total_phases": len(phases),
            "total_tasks": total_tasks,
            "total_effort_hours": total_effort,
            "average_tasks_per_phase": total_tasks / len(phases) if phases else 0,
            "average_effort_per_phase": total_effort / len(phases) if phases else 0,
            "parallel_groups_total": total_parallel_groups,
            "parallelization_ratio": (
                total_parallel_groups / total_tasks if total_tasks > 0 else 0
            ),
        }

    def _calculate_timeline_confidence(
        self, tasks: List[TaskNode], parallel_groups: List[ParallelGroup]
    ) -> float:
        """Calculate timeline confidence level."""
        confidence = 0.8
        completed_tasks = sum(
            (1 for task in tasks if task.completion_status == TaskStatus.COMPLETED)
        )
        completion_ratio = completed_tasks / len(tasks) if tasks else 0
        confidence += completion_ratio * 0.2
        high_complexity_tasks = sum((1 for task in tasks if task.estimated_effort > 20))
        complexity_ratio = high_complexity_tasks / len(tasks) if tasks else 0
        confidence -= complexity_ratio * 0.3
        if parallel_groups and len(parallel_groups) > 1:
            confidence += 0.1
        return max(0.1, min(1.0, confidence))

    def _identify_timeline_risk_factors(self, tasks: List[TaskNode]) -> List[str]:
        """Identify timeline risk factors."""
        risk_factors = []
        high_effort_tasks = [task for task in tasks if task.estimated_effort > 40]
        if high_effort_tasks:
            risk_factors.append(
                f"{len(high_effort_tasks)} high-effort tasks (>40 hours)"
            )
        blocked_tasks = [
            task for task in tasks if task.completion_status == TaskStatus.BLOCKED
        ]
        if blocked_tasks:
            risk_factors.append(
                f"{len(blocked_tasks)} blocked tasks requiring resolution"
            )
        complex_deps = [task for task in tasks if len(task.dependencies) > 3]
        if complex_deps:
            risk_factors.append(f"{len(complex_deps)} tasks with complex dependencies")
        unknown_tasks = [
            task
            for task in tasks
            if task.completion_status == TaskStatus.NOT_STARTED
            and task.estimated_effort > 20
        ]
        if unknown_tasks:
            risk_factors.append(f"{len(unknown_tasks)} unstarted complex tasks")
        return (
            risk_factors
            if risk_factors
            else ["No significant timeline risks identified"]
        )


def __init__(self):
    self.working_hours_per_week = 40
    self.parallel_efficiency = 0.85
    self.phase_overhead = 0.15
    self.risk_buffer = 0.2
    self.max_phase_duration = 3
    self.min_parallel_tasks = 2
    self.complexity_threshold = 0.7


def optimize_mvp_phases_with_extreme_prejudice(
    self, mvp_route: MVPRoute
) -> PhaseOptimizationResult:
    """
    Optimize MVP phases with BEASTMASTER systematic annihilation.

    Args:
        mvp_route: MVP route to optimize with extreme prejudice

    Returns:
        PhaseOptimizationResult: Systematically optimized phases
    """
    task_analysis = self._analyze_tasks_with_prejudice(mvp_route.critical_tasks)
    phase_groups = self._create_optimal_phase_groups(
        mvp_route.critical_tasks, task_analysis
    )
    optimized_phases = []
    resource_requirements = {}
    for i, (phase_name, tasks) in enumerate(phase_groups):
        phase_number = i + 1
        parallel_groups = self._create_high_velocity_parallel_groups(tasks)
        resources = self._calculate_systematic_resource_requirements(
            tasks, parallel_groups
        )
        resource_requirements[phase_number] = resources
        objectives = self._define_systematic_objectives(tasks, phase_number)
        deliverables = self._identify_systematic_deliverables(tasks)
        success_criteria = self._define_systematic_success_criteria(tasks, deliverables)
        timeline = self._calculate_phase_timeline_with_prejudice(
            parallel_groups, resources
        )
        dependencies = self._extract_phase_dependencies(tasks)
        optimized_phases.append(
            MVPPhase(
                phase_name=phase_name,
                phase_number=phase_number,
                objectives=objectives,
                tasks=tasks,
                deliverables=deliverables,
                estimated_duration=timeline,
                parallel_groups=parallel_groups,
                success_criteria=success_criteria,
                dependencies_satisfied=dependencies,
            )
        )
    critical_path_phases = self._identify_critical_path_phases(optimized_phases)
    optimization_metrics = self._calculate_optimization_metrics(optimized_phases)
    total_timeline = sum((phase.estimated_duration for phase in optimized_phases))
    return PhaseOptimizationResult(
        optimized_phases=optimized_phases,
        total_timeline=total_timeline,
        critical_path_phases=critical_path_phases,
        resource_requirements=resource_requirements,
        optimization_metrics=optimization_metrics,
    )


def estimate_timeline_with_systematic_precision(
    self,
    tasks: List[TaskNode],
    parallel_groups: List[ParallelGroup],
    resource_constraints: Optional[Dict] = None,
) -> TimelineEstimation:
    """
    Estimate timeline with systematic precision and confidence intervals.

    Args:
        tasks: Tasks to estimate
        parallel_groups: Parallel execution groups
        resource_constraints: Optional resource constraints

    Returns:
        TimelineEstimation: Precise timeline estimation with confidence
    """
    base_effort = sum((task.estimated_effort for task in tasks))
    if parallel_groups:
        max_parallel_effort = max(
            (
                sum((task.estimated_effort for task in group.tasks))
                for group in parallel_groups
            )
        )
        parallel_effort = max_parallel_effort * self.parallel_efficiency
    else:
        parallel_effort = base_effort
    base_weeks = parallel_effort / self.working_hours_per_week
    optimistic_weeks = max(1, int(base_weeks * 0.8))
    realistic_weeks = max(1, int(base_weeks * (1 + self.phase_overhead)))
    pessimistic_weeks = max(
        2, int(base_weeks * (1 + self.phase_overhead + self.risk_buffer))
    )
    confidence_level = self._calculate_timeline_confidence(tasks, parallel_groups)
    risk_factors = self._identify_timeline_risk_factors(tasks)
    return TimelineEstimation(
        optimistic_weeks=optimistic_weeks,
        realistic_weeks=realistic_weeks,
        pessimistic_weeks=pessimistic_weeks,
        confidence_level=confidence_level,
        risk_factors=risk_factors,
    )


def calculate_resource_requirements_with_precision(
    self, phases: List[MVPPhase]
) -> Dict[int, ResourceRequirements]:
    """
    Calculate systematic resource requirements for each phase.

    Args:
        phases: MVP phases to analyze

    Returns:
        Dict[int, ResourceRequirements]: Phase number -> resource requirements
    """
    resource_requirements = {}
    for phase in phases:
        required_skills = self._analyze_required_skills(phase.tasks)
        total_effort = sum((task.estimated_effort for task in phase.tasks))
        phase_weeks = phase.estimated_duration
        if phase_weeks > 0:
            developers_needed = max(
                1, math.ceil(total_effort / (self.working_hours_per_week * phase_weeks))
            )
        else:
            developers_needed = 1
        tools_required = self._identify_required_tools(phase.tasks)
        resource_requirements[phase.phase_number] = ResourceRequirements(
            developers_needed=developers_needed,
            skill_requirements=required_skills,
            estimated_hours=total_effort,
            tools_required=tools_required,
        )
    return resource_requirements


def _analyze_tasks_with_prejudice(self, tasks: List[TaskNode]) -> Dict[str, float]:
    """Analyze tasks with BEASTMASTER systematic prejudice."""
    analysis = {}
    for task in tasks:
        complexity_score = self._calculate_task_complexity(task)
        risk_score = self._calculate_task_risk(task)
        value_score = self._calculate_task_value(task)
        priority_score = 1.0 / max(task.priority, 1)
        analysis[task.task_id] = {
            "complexity": complexity_score,
            "risk": risk_score,
            "value": value_score,
            "priority": priority_score,
            "combined": value_score
            * priority_score
            / max(complexity_score * risk_score, 0.1),
        }
    return analysis


def _create_optimal_phase_groups(
    self, tasks: List[TaskNode], analysis: Dict[str, float]
) -> List[Tuple[str, List[TaskNode]]]:
    """Create optimal phase groups with SYSTEMATIC PRECISION."""
    sorted_tasks = self._sort_tasks_systematically(tasks, analysis)
    phases = []
    current_phase_tasks = []
    current_phase_effort = 0
    phase_counter = 0
    max_phase_effort = self.max_phase_duration * self.working_hours_per_week
    for task in sorted_tasks:
        if (
            current_phase_effort + task.estimated_effort <= max_phase_effort
            and len(current_phase_tasks) < 8
        ):
            current_phase_tasks.append(task)
            current_phase_effort += task.estimated_effort
        else:
            if current_phase_tasks:
                phase_counter += 1
                phase_name = self._generate_phase_name(
                    current_phase_tasks, phase_counter
                )
                phases.append((phase_name, current_phase_tasks.copy()))
            current_phase_tasks = [task]
            current_phase_effort = task.estimated_effort
    if current_phase_tasks:
        phase_counter += 1
        phase_name = self._generate_phase_name(current_phase_tasks, phase_counter)
        phases.append((phase_name, current_phase_tasks))
    return phases


def _create_high_velocity_parallel_groups(
    self, tasks: List[TaskNode]
) -> List[ParallelGroup]:
    """Create high-velocity parallel groups with EXTREME EFFICIENCY."""
    if len(tasks) < self.min_parallel_tasks:
        return [
            ParallelGroup(
                group_id="single_group",
                tasks=tasks,
                estimated_duration=(
                    max((task.estimated_effort for task in tasks)) // 8 if tasks else 1
                ),
                coordination_overhead=0.0,
            )
        ]
    groups = []
    remaining_tasks = tasks.copy()
    group_counter = 0
    while remaining_tasks:
        group_counter += 1
        current_group = [remaining_tasks.pop(0)]
        reference_effort = current_group[0].estimated_effort
        i = 0
        while i < len(remaining_tasks) and len(current_group) < 4:
            task = remaining_tasks[i]
            effort_ratio = abs(task.estimated_effort - reference_effort) / max(
                reference_effort, 1
            )
            if effort_ratio <= 0.5:
                current_group.append(remaining_tasks.pop(i))
            else:
                i += 1
        max_effort = max((task.estimated_effort for task in current_group))
        estimated_duration = max(1, max_effort // 8)
        if len(current_group) > 1:
            coordination_overhead = 0.1 + (len(current_group) - 2) * 0.05
        else:
            coordination_overhead = 0.0
        groups.append(
            ParallelGroup(
                group_id=f"parallel_group_{group_counter}",
                tasks=current_group,
                estimated_duration=estimated_duration,
                coordination_overhead=coordination_overhead,
            )
        )
    return groups


def _calculate_systematic_resource_requirements(
    self, tasks: List[TaskNode], parallel_groups: List[ParallelGroup]
) -> ResourceRequirements:
    """Calculate systematic resource requirements with PRECISION."""
    required_skills = self._analyze_required_skills(tasks)
    total_effort = sum((task.estimated_effort for task in tasks))
    max_concurrent_tasks = (
        max((len(group.tasks) for group in parallel_groups)) if parallel_groups else 1
    )
    developers_needed = min(max_concurrent_tasks, max(1, total_effort // 40))
    tools_required = self._identify_required_tools(tasks)
    return ResourceRequirements(
        developers_needed=developers_needed,
        skill_requirements=required_skills,
        estimated_hours=total_effort,
        tools_required=tools_required,
    )


def _define_systematic_objectives(
    self, tasks: List[TaskNode], phase_number: int
) -> List[str]:
    """Define systematic objectives with CLARITY."""
    objectives = []
    if phase_number == 1:
        objectives.append("🚀 Establish systematic foundation and core infrastructure")
    elif phase_number == 2:
        objectives.append(
            "⚡ Implement core systematic functionality with extreme efficiency"
        )
    elif phase_number == 3:
        objectives.append("🔗 Integrate components with systematic precision")
    else:
        objectives.append("🎯 Complete systematic implementation and validation")
    task_keywords = set()
    for task in tasks:
        words = task.task_name.lower().split()
        task_keywords.update(words)
    if "api" in task_keywords:
        objectives.append("📡 Deliver systematic API with complete functionality")
    if "test" in task_keywords:
        objectives.append("🧪 Achieve systematic test coverage with quality validation")
    if "framework" in task_keywords:
        objectives.append("🏗️ Build systematic framework with extensible architecture")
    if "integration" in task_keywords:
        objectives.append(
            "🔄 Complete systematic integration with dependency validation"
        )
    return objectives


def _identify_systematic_deliverables(self, tasks: List[TaskNode]) -> List[str]:
    """Identify systematic deliverables with PRECISION."""
    deliverables = set()
    for task in tasks:
        task_text = f"{task.task_name} {task.description}".lower()
        if any((keyword in task_text for keyword in ["api", "endpoint", "interface"])):
            deliverables.add("🔌 Functional API with systematic validation")
        if any((keyword in task_text for keyword in ["framework", "system", "engine"])):
            deliverables.add("🏗️ Systematic framework implementation")
        if any((keyword in task_text for keyword in ["test", "validation", "verify"])):
            deliverables.add("🧪 Comprehensive test suite with systematic coverage")
        if any(
            (keyword in task_text for keyword in ["documentation", "docs", "guide"])
        ):
            deliverables.add("📚 Systematic documentation with examples")
        if any((keyword in task_text for keyword in ["example", "demo", "sample"])):
            deliverables.add("💡 Working examples with systematic validation")
        if any((keyword in task_text for keyword in ["integration", "orchestration"])):
            deliverables.add("🔗 Systematic integration with dependency management")
    return list(deliverables) if deliverables else ["✅ Systematic task completion"]


def _define_systematic_success_criteria(
    self, tasks: List[TaskNode], deliverables: List[str]
) -> List[str]:
    """Define systematic success criteria with RIGOR."""
    criteria = []
    criteria.append(f"✅ All {len(tasks)} systematic tasks completed with validation")
    for deliverable in deliverables:
        criteria.append(f"🎯 {deliverable} meets systematic quality standards")
    criteria.append("🛡️ Zero critical systematic violations detected")
    criteria.append("📊 Systematic quality score > 0.9 achieved")
    criteria.append("🔍 Code review and systematic validation completed")
    if len(tasks) > 1:
        criteria.append("🔗 All systematic dependencies validated and integrated")
    return criteria


def _calculate_phase_timeline_with_prejudice(
    self, parallel_groups: List[ParallelGroup], resources: ResourceRequirements
) -> int:
    """Calculate phase timeline with BEASTMASTER PREJUDICE."""
    if not parallel_groups:
        return 1
    max_group_duration = max((group.estimated_duration for group in parallel_groups))
    total_overhead = sum((group.coordination_overhead for group in parallel_groups))
    overhead_days = max_group_duration * total_overhead
    if resources.developers_needed > 4:
        overhead_days += 1
    total_days = max_group_duration + overhead_days
    weeks = max(1, math.ceil(total_days / 5))
    return min(weeks, self.max_phase_duration)


def _sort_tasks_systematically(
    self, tasks: List[TaskNode], analysis: Dict[str, float]
) -> List[TaskNode]:
    """Sort tasks systematically by dependencies and analysis scores."""
    task_lookup = {task.task_id: task for task in tasks}
    sorted_tasks = []
    processed = set()

    def process_task(task: TaskNode):
        if task.task_id in processed:
            return
        for dep_id in task.dependencies:
            if dep_id in task_lookup and dep_id not in processed:
                process_task(task_lookup[dep_id])
        sorted_tasks.append(task)
        processed.add(task.task_id)

    for task in tasks:
        process_task(task)
    return sorted_tasks


def _generate_phase_name(self, tasks: List[TaskNode], phase_number: int) -> str:
    """Generate systematic phase name."""
    task_keywords = []
    for task in tasks:
        words = task.task_name.lower().split()
        task_keywords.extend(words)
    keyword_counts = {}
    for keyword in task_keywords:
        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    if keyword_counts:
        dominant_keyword = max(keyword_counts.items(), key=lambda x: x[1])[0]
        if dominant_keyword in ["setup", "infrastructure", "core", "foundation"]:
            return f"Phase {phase_number}: Systematic Foundation"
        elif dominant_keyword in ["implement", "create", "build"]:
            return f"Phase {phase_number}: Systematic Implementation"
        elif dominant_keyword in ["integrate", "orchestration", "coordination"]:
            return f"Phase {phase_number}: Systematic Integration"
        elif dominant_keyword in ["test", "validation", "verify"]:
            return f"Phase {phase_number}: Systematic Validation"
        else:
            return f"Phase {phase_number}: Systematic {dominant_keyword.title()}"
    return f"Phase {phase_number}: Systematic Execution"


def _calculate_task_complexity(self, task: TaskNode) -> float:
    """Calculate task complexity score."""
    complexity = 0.5
    if task.estimated_effort > 40:
        complexity += 0.3
    elif task.estimated_effort > 20:
        complexity += 0.2
    complex_keywords = [
        "complex",
        "advanced",
        "comprehensive",
        "integrate",
        "optimize",
        "framework",
        "system",
    ]
    task_text = f"{task.task_name} {task.description}".lower()
    for keyword in complex_keywords:
        if keyword in task_text:
            complexity += 0.1
    return min(1.0, complexity)


def _calculate_task_risk(self, task: TaskNode) -> float:
    """Calculate task risk score."""
    risk = 0.2
    if task.completion_status == TaskStatus.BLOCKED:
        risk += 0.6
    elif task.completion_status == TaskStatus.FAILED:
        risk += 0.8
    elif task.completion_status == TaskStatus.IN_PROGRESS:
        risk += 0.1
    if len(task.dependencies) > 3:
        risk += 0.2
    return min(1.0, risk)


def _calculate_task_value(self, task: TaskNode) -> float:
    """Calculate task value score."""
    value = 0.5
    high_value_keywords = ["api", "framework", "core", "integration", "system"]
    task_text = f"{task.task_name} {task.description}".lower()
    for keyword in high_value_keywords:
        if keyword in task_text:
            value += 0.2
    if task.completion_status == TaskStatus.COMPLETED:
        value += 0.3
    return min(1.0, value)


def _analyze_required_skills(self, tasks: List[TaskNode]) -> List[str]:
    """Analyze required skills for tasks."""
    skills = set()
    for task in tasks:
        task_text = f"{task.task_name} {task.description}".lower()
        if any((keyword in task_text for keyword in ["python", "api", "backend"])):
            skills.add("Python Development")
        if any((keyword in task_text for keyword in ["frontend", "ui", "interface"])):
            skills.add("Frontend Development")
        if any((keyword in task_text for keyword in ["test", "testing", "validation"])):
            skills.add("Testing & QA")
        if any(
            (
                keyword in task_text
                for keyword in ["devops", "deployment", "infrastructure"]
            )
        ):
            skills.add("DevOps & Infrastructure")
        if any(
            (keyword in task_text for keyword in ["design", "architecture", "system"])
        ):
            skills.add("System Architecture")
        if any((keyword in task_text for keyword in ["documentation", "docs"])):
            skills.add("Technical Writing")
    return list(skills) if skills else ["General Development"]


def _extract_phase_dependencies(self, tasks: List[TaskNode]) -> List[str]:
    """Extract dependencies satisfied by completing this phase."""
    dependencies = set()
    for task in tasks:
        dependencies.update(task.requirements_traced)
    return list(dependencies)


def _identify_critical_path_phases(self, phases: List[MVPPhase]) -> List[int]:
    """Identify phases on the critical path."""
    critical_phases = []
    for phase in phases:
        total_effort = sum((task.estimated_effort for task in phase.tasks))
        total_dependencies = sum((len(task.dependencies) for task in phase.tasks))
        if total_effort > 80 or total_dependencies > 10:
            critical_phases.append(phase.phase_number)
    return critical_phases


def _calculate_optimization_metrics(self, phases: List[MVPPhase]) -> Dict[str, float]:
    """Calculate optimization metrics."""
    total_tasks = sum((len(phase.tasks) for phase in phases))
    total_effort = sum(
        (sum((task.estimated_effort for task in phase.tasks)) for phase in phases)
    )
    total_parallel_groups = sum((len(phase.parallel_groups) for phase in phases))
    return {
        "total_phases": len(phases),
        "total_tasks": total_tasks,
        "total_effort_hours": total_effort,
        "average_tasks_per_phase": total_tasks / len(phases) if phases else 0,
        "average_effort_per_phase": total_effort / len(phases) if phases else 0,
        "parallel_groups_total": total_parallel_groups,
        "parallelization_ratio": (
            total_parallel_groups / total_tasks if total_tasks > 0 else 0
        ),
    }


def _calculate_timeline_confidence(
    self, tasks: List[TaskNode], parallel_groups: List[ParallelGroup]
) -> float:
    """Calculate timeline confidence level."""
    confidence = 0.8
    completed_tasks = sum(
        (1 for task in tasks if task.completion_status == TaskStatus.COMPLETED)
    )
    completion_ratio = completed_tasks / len(tasks) if tasks else 0
    confidence += completion_ratio * 0.2
    high_complexity_tasks = sum((1 for task in tasks if task.estimated_effort > 20))
    complexity_ratio = high_complexity_tasks / len(tasks) if tasks else 0
    confidence -= complexity_ratio * 0.3
    if parallel_groups and len(parallel_groups) > 1:
        confidence += 0.1
    return max(0.1, min(1.0, confidence))


def _identify_timeline_risk_factors(self, tasks: List[TaskNode]) -> List[str]:
    """Identify timeline risk factors."""
    risk_factors = []
    high_effort_tasks = [task for task in tasks if task.estimated_effort > 40]
    if high_effort_tasks:
        risk_factors.append(f"{len(high_effort_tasks)} high-effort tasks (>40 hours)")
    blocked_tasks = [
        task for task in tasks if task.completion_status == TaskStatus.BLOCKED
    ]
    if blocked_tasks:
        risk_factors.append(f"{len(blocked_tasks)} blocked tasks requiring resolution")
    complex_deps = [task for task in tasks if len(task.dependencies) > 3]
    if complex_deps:
        risk_factors.append(f"{len(complex_deps)} tasks with complex dependencies")
    unknown_tasks = [
        task
        for task in tasks
        if task.completion_status == TaskStatus.NOT_STARTED
        and task.estimated_effort > 20
    ]
    if unknown_tasks:
        risk_factors.append(f"{len(unknown_tasks)} unstarted complex tasks")
    return (
        risk_factors if risk_factors else ["No significant timeline risks identified"]
    )


def __init__(self):
    self.working_hours_per_week = 40
    self.parallel_efficiency = 0.85
    self.phase_overhead = 0.15
    self.risk_buffer = 0.2
    self.max_phase_duration = 3
    self.min_parallel_tasks = 2
    self.complexity_threshold = 0.7


def optimize_mvp_phases_with_extreme_prejudice(
    self, mvp_route: MVPRoute
) -> PhaseOptimizationResult:
    """
    Optimize MVP phases with BEASTMASTER systematic annihilation.

    Args:
        mvp_route: MVP route to optimize with extreme prejudice

    Returns:
        PhaseOptimizationResult: Systematically optimized phases
    """
    task_analysis = self._analyze_tasks_with_prejudice(mvp_route.critical_tasks)
    phase_groups = self._create_optimal_phase_groups(
        mvp_route.critical_tasks, task_analysis
    )
    optimized_phases = []
    resource_requirements = {}
    for i, (phase_name, tasks) in enumerate(phase_groups):
        phase_number = i + 1
        parallel_groups = self._create_high_velocity_parallel_groups(tasks)
        resources = self._calculate_systematic_resource_requirements(
            tasks, parallel_groups
        )
        resource_requirements[phase_number] = resources
        objectives = self._define_systematic_objectives(tasks, phase_number)
        deliverables = self._identify_systematic_deliverables(tasks)
        success_criteria = self._define_systematic_success_criteria(tasks, deliverables)
        timeline = self._calculate_phase_timeline_with_prejudice(
            parallel_groups, resources
        )
        dependencies = self._extract_phase_dependencies(tasks)
        optimized_phases.append(
            MVPPhase(
                phase_name=phase_name,
                phase_number=phase_number,
                objectives=objectives,
                tasks=tasks,
                deliverables=deliverables,
                estimated_duration=timeline,
                parallel_groups=parallel_groups,
                success_criteria=success_criteria,
                dependencies_satisfied=dependencies,
            )
        )
    critical_path_phases = self._identify_critical_path_phases(optimized_phases)
    optimization_metrics = self._calculate_optimization_metrics(optimized_phases)
    total_timeline = sum((phase.estimated_duration for phase in optimized_phases))
    return PhaseOptimizationResult(
        optimized_phases=optimized_phases,
        total_timeline=total_timeline,
        critical_path_phases=critical_path_phases,
        resource_requirements=resource_requirements,
        optimization_metrics=optimization_metrics,
    )


def estimate_timeline_with_systematic_precision(
    self,
    tasks: List[TaskNode],
    parallel_groups: List[ParallelGroup],
    resource_constraints: Optional[Dict] = None,
) -> TimelineEstimation:
    """
    Estimate timeline with systematic precision and confidence intervals.

    Args:
        tasks: Tasks to estimate
        parallel_groups: Parallel execution groups
        resource_constraints: Optional resource constraints

    Returns:
        TimelineEstimation: Precise timeline estimation with confidence
    """
    base_effort = sum((task.estimated_effort for task in tasks))
    if parallel_groups:
        max_parallel_effort = max(
            (
                sum((task.estimated_effort for task in group.tasks))
                for group in parallel_groups
            )
        )
        parallel_effort = max_parallel_effort * self.parallel_efficiency
    else:
        parallel_effort = base_effort
    base_weeks = parallel_effort / self.working_hours_per_week
    optimistic_weeks = max(1, int(base_weeks * 0.8))
    realistic_weeks = max(1, int(base_weeks * (1 + self.phase_overhead)))
    pessimistic_weeks = max(
        2, int(base_weeks * (1 + self.phase_overhead + self.risk_buffer))
    )
    confidence_level = self._calculate_timeline_confidence(tasks, parallel_groups)
    risk_factors = self._identify_timeline_risk_factors(tasks)
    return TimelineEstimation(
        optimistic_weeks=optimistic_weeks,
        realistic_weeks=realistic_weeks,
        pessimistic_weeks=pessimistic_weeks,
        confidence_level=confidence_level,
        risk_factors=risk_factors,
    )


def calculate_resource_requirements_with_precision(
    self, phases: List[MVPPhase]
) -> Dict[int, ResourceRequirements]:
    """
    Calculate systematic resource requirements for each phase.

    Args:
        phases: MVP phases to analyze

    Returns:
        Dict[int, ResourceRequirements]: Phase number -> resource requirements
    """
    resource_requirements = {}
    for phase in phases:
        required_skills = self._analyze_required_skills(phase.tasks)
        total_effort = sum((task.estimated_effort for task in phase.tasks))
        phase_weeks = phase.estimated_duration
        if phase_weeks > 0:
            developers_needed = max(
                1, math.ceil(total_effort / (self.working_hours_per_week * phase_weeks))
            )
        else:
            developers_needed = 1
        tools_required = self._identify_required_tools(phase.tasks)
        resource_requirements[phase.phase_number] = ResourceRequirements(
            developers_needed=developers_needed,
            skill_requirements=required_skills,
            estimated_hours=total_effort,
            tools_required=tools_required,
        )
    return resource_requirements


def _analyze_tasks_with_prejudice(self, tasks: List[TaskNode]) -> Dict[str, float]:
    """Analyze tasks with BEASTMASTER systematic prejudice."""
    analysis = {}
    for task in tasks:
        complexity_score = self._calculate_task_complexity(task)
        risk_score = self._calculate_task_risk(task)
        value_score = self._calculate_task_value(task)
        priority_score = 1.0 / max(task.priority, 1)
        analysis[task.task_id] = {
            "complexity": complexity_score,
            "risk": risk_score,
            "value": value_score,
            "priority": priority_score,
            "combined": value_score
            * priority_score
            / max(complexity_score * risk_score, 0.1),
        }
    return analysis


def _create_optimal_phase_groups(
    self, tasks: List[TaskNode], analysis: Dict[str, float]
) -> List[Tuple[str, List[TaskNode]]]:
    """Create optimal phase groups with SYSTEMATIC PRECISION."""
    sorted_tasks = self._sort_tasks_systematically(tasks, analysis)
    phases = []
    current_phase_tasks = []
    current_phase_effort = 0
    phase_counter = 0
    max_phase_effort = self.max_phase_duration * self.working_hours_per_week
    for task in sorted_tasks:
        if (
            current_phase_effort + task.estimated_effort <= max_phase_effort
            and len(current_phase_tasks) < 8
        ):
            current_phase_tasks.append(task)
            current_phase_effort += task.estimated_effort
        else:
            if current_phase_tasks:
                phase_counter += 1
                phase_name = self._generate_phase_name(
                    current_phase_tasks, phase_counter
                )
                phases.append((phase_name, current_phase_tasks.copy()))
            current_phase_tasks = [task]
            current_phase_effort = task.estimated_effort
    if current_phase_tasks:
        phase_counter += 1
        phase_name = self._generate_phase_name(current_phase_tasks, phase_counter)
        phases.append((phase_name, current_phase_tasks))
    return phases


def _create_high_velocity_parallel_groups(
    self, tasks: List[TaskNode]
) -> List[ParallelGroup]:
    """Create high-velocity parallel groups with EXTREME EFFICIENCY."""
    if len(tasks) < self.min_parallel_tasks:
        return [
            ParallelGroup(
                group_id="single_group",
                tasks=tasks,
                estimated_duration=(
                    max((task.estimated_effort for task in tasks)) // 8 if tasks else 1
                ),
                coordination_overhead=0.0,
            )
        ]
    groups = []
    remaining_tasks = tasks.copy()
    group_counter = 0
    while remaining_tasks:
        group_counter += 1
        current_group = [remaining_tasks.pop(0)]
        reference_effort = current_group[0].estimated_effort
        i = 0
        while i < len(remaining_tasks) and len(current_group) < 4:
            task = remaining_tasks[i]
            effort_ratio = abs(task.estimated_effort - reference_effort) / max(
                reference_effort, 1
            )
            if effort_ratio <= 0.5:
                current_group.append(remaining_tasks.pop(i))
            else:
                i += 1
        max_effort = max((task.estimated_effort for task in current_group))
        estimated_duration = max(1, max_effort // 8)
        if len(current_group) > 1:
            coordination_overhead = 0.1 + (len(current_group) - 2) * 0.05
        else:
            coordination_overhead = 0.0
        groups.append(
            ParallelGroup(
                group_id=f"parallel_group_{group_counter}",
                tasks=current_group,
                estimated_duration=estimated_duration,
                coordination_overhead=coordination_overhead,
            )
        )
    return groups


def _calculate_systematic_resource_requirements(
    self, tasks: List[TaskNode], parallel_groups: List[ParallelGroup]
) -> ResourceRequirements:
    """Calculate systematic resource requirements with PRECISION."""
    required_skills = self._analyze_required_skills(tasks)
    total_effort = sum((task.estimated_effort for task in tasks))
    max_concurrent_tasks = (
        max((len(group.tasks) for group in parallel_groups)) if parallel_groups else 1
    )
    developers_needed = min(max_concurrent_tasks, max(1, total_effort // 40))
    tools_required = self._identify_required_tools(tasks)
    return ResourceRequirements(
        developers_needed=developers_needed,
        skill_requirements=required_skills,
        estimated_hours=total_effort,
        tools_required=tools_required,
    )


def _define_systematic_objectives(
    self, tasks: List[TaskNode], phase_number: int
) -> List[str]:
    """Define systematic objectives with CLARITY."""
    objectives = []
    if phase_number == 1:
        objectives.append("🚀 Establish systematic foundation and core infrastructure")
    elif phase_number == 2:
        objectives.append(
            "⚡ Implement core systematic functionality with extreme efficiency"
        )
    elif phase_number == 3:
        objectives.append("🔗 Integrate components with systematic precision")
    else:
        objectives.append("🎯 Complete systematic implementation and validation")
    task_keywords = set()
    for task in tasks:
        words = task.task_name.lower().split()
        task_keywords.update(words)
    if "api" in task_keywords:
        objectives.append("📡 Deliver systematic API with complete functionality")
    if "test" in task_keywords:
        objectives.append("🧪 Achieve systematic test coverage with quality validation")
    if "framework" in task_keywords:
        objectives.append("🏗️ Build systematic framework with extensible architecture")
    if "integration" in task_keywords:
        objectives.append(
            "🔄 Complete systematic integration with dependency validation"
        )
    return objectives


def _identify_systematic_deliverables(self, tasks: List[TaskNode]) -> List[str]:
    """Identify systematic deliverables with PRECISION."""
    deliverables = set()
    for task in tasks:
        task_text = f"{task.task_name} {task.description}".lower()
        if any((keyword in task_text for keyword in ["api", "endpoint", "interface"])):
            deliverables.add("🔌 Functional API with systematic validation")
        if any((keyword in task_text for keyword in ["framework", "system", "engine"])):
            deliverables.add("🏗️ Systematic framework implementation")
        if any((keyword in task_text for keyword in ["test", "validation", "verify"])):
            deliverables.add("🧪 Comprehensive test suite with systematic coverage")
        if any(
            (keyword in task_text for keyword in ["documentation", "docs", "guide"])
        ):
            deliverables.add("📚 Systematic documentation with examples")
        if any((keyword in task_text for keyword in ["example", "demo", "sample"])):
            deliverables.add("💡 Working examples with systematic validation")
        if any((keyword in task_text for keyword in ["integration", "orchestration"])):
            deliverables.add("🔗 Systematic integration with dependency management")
    return list(deliverables) if deliverables else ["✅ Systematic task completion"]


def _define_systematic_success_criteria(
    self, tasks: List[TaskNode], deliverables: List[str]
) -> List[str]:
    """Define systematic success criteria with RIGOR."""
    criteria = []
    criteria.append(f"✅ All {len(tasks)} systematic tasks completed with validation")
    for deliverable in deliverables:
        criteria.append(f"🎯 {deliverable} meets systematic quality standards")
    criteria.append("🛡️ Zero critical systematic violations detected")
    criteria.append("📊 Systematic quality score > 0.9 achieved")
    criteria.append("🔍 Code review and systematic validation completed")
    if len(tasks) > 1:
        criteria.append("🔗 All systematic dependencies validated and integrated")
    return criteria


def _calculate_phase_timeline_with_prejudice(
    self, parallel_groups: List[ParallelGroup], resources: ResourceRequirements
) -> int:
    """Calculate phase timeline with BEASTMASTER PREJUDICE."""
    if not parallel_groups:
        return 1
    max_group_duration = max((group.estimated_duration for group in parallel_groups))
    total_overhead = sum((group.coordination_overhead for group in parallel_groups))
    overhead_days = max_group_duration * total_overhead
    if resources.developers_needed > 4:
        overhead_days += 1
    total_days = max_group_duration + overhead_days
    weeks = max(1, math.ceil(total_days / 5))
    return min(weeks, self.max_phase_duration)


def _sort_tasks_systematically(
    self, tasks: List[TaskNode], analysis: Dict[str, float]
) -> List[TaskNode]:
    """Sort tasks systematically by dependencies and analysis scores."""
    task_lookup = {task.task_id: task for task in tasks}
    sorted_tasks = []
    processed = set()

    def process_task(task: TaskNode):
        if task.task_id in processed:
            return
        for dep_id in task.dependencies:
            if dep_id in task_lookup and dep_id not in processed:
                process_task(task_lookup[dep_id])
        sorted_tasks.append(task)
        processed.add(task.task_id)

    for task in tasks:
        process_task(task)
    return sorted_tasks


def _generate_phase_name(self, tasks: List[TaskNode], phase_number: int) -> str:
    """Generate systematic phase name."""
    task_keywords = []
    for task in tasks:
        words = task.task_name.lower().split()
        task_keywords.extend(words)
    keyword_counts = {}
    for keyword in task_keywords:
        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    if keyword_counts:
        dominant_keyword = max(keyword_counts.items(), key=lambda x: x[1])[0]
        if dominant_keyword in ["setup", "infrastructure", "core", "foundation"]:
            return f"Phase {phase_number}: Systematic Foundation"
        elif dominant_keyword in ["implement", "create", "build"]:
            return f"Phase {phase_number}: Systematic Implementation"
        elif dominant_keyword in ["integrate", "orchestration", "coordination"]:
            return f"Phase {phase_number}: Systematic Integration"
        elif dominant_keyword in ["test", "validation", "verify"]:
            return f"Phase {phase_number}: Systematic Validation"
        else:
            return f"Phase {phase_number}: Systematic {dominant_keyword.title()}"
    return f"Phase {phase_number}: Systematic Execution"


def _calculate_task_complexity(self, task: TaskNode) -> float:
    """Calculate task complexity score."""
    complexity = 0.5
    if task.estimated_effort > 40:
        complexity += 0.3
    elif task.estimated_effort > 20:
        complexity += 0.2
    complex_keywords = [
        "complex",
        "advanced",
        "comprehensive",
        "integrate",
        "optimize",
        "framework",
        "system",
    ]
    task_text = f"{task.task_name} {task.description}".lower()
    for keyword in complex_keywords:
        if keyword in task_text:
            complexity += 0.1
    return min(1.0, complexity)


def _calculate_task_risk(self, task: TaskNode) -> float:
    """Calculate task risk score."""
    risk = 0.2
    if task.completion_status == TaskStatus.BLOCKED:
        risk += 0.6
    elif task.completion_status == TaskStatus.FAILED:
        risk += 0.8
    elif task.completion_status == TaskStatus.IN_PROGRESS:
        risk += 0.1
    if len(task.dependencies) > 3:
        risk += 0.2
    return min(1.0, risk)


def _calculate_task_value(self, task: TaskNode) -> float:
    """Calculate task value score."""
    value = 0.5
    high_value_keywords = ["api", "framework", "core", "integration", "system"]
    task_text = f"{task.task_name} {task.description}".lower()
    for keyword in high_value_keywords:
        if keyword in task_text:
            value += 0.2
    if task.completion_status == TaskStatus.COMPLETED:
        value += 0.3
    return min(1.0, value)


def _analyze_required_skills(self, tasks: List[TaskNode]) -> List[str]:
    """Analyze required skills for tasks."""
    skills = set()
    for task in tasks:
        task_text = f"{task.task_name} {task.description}".lower()
        if any((keyword in task_text for keyword in ["python", "api", "backend"])):
            skills.add("Python Development")
        if any((keyword in task_text for keyword in ["frontend", "ui", "interface"])):
            skills.add("Frontend Development")
        if any((keyword in task_text for keyword in ["test", "testing", "validation"])):
            skills.add("Testing & QA")
        if any(
            (
                keyword in task_text
                for keyword in ["devops", "deployment", "infrastructure"]
            )
        ):
            skills.add("DevOps & Infrastructure")
        if any(
            (keyword in task_text for keyword in ["design", "architecture", "system"])
        ):
            skills.add("System Architecture")
        if any((keyword in task_text for keyword in ["documentation", "docs"])):
            skills.add("Technical Writing")
    return list(skills) if skills else ["General Development"]


def _extract_phase_dependencies(self, tasks: List[TaskNode]) -> List[str]:
    """Extract dependencies satisfied by completing this phase."""
    dependencies = set()
    for task in tasks:
        dependencies.update(task.requirements_traced)
    return list(dependencies)


def _identify_critical_path_phases(self, phases: List[MVPPhase]) -> List[int]:
    """Identify phases on the critical path."""
    critical_phases = []
    for phase in phases:
        total_effort = sum((task.estimated_effort for task in phase.tasks))
        total_dependencies = sum((len(task.dependencies) for task in phase.tasks))
        if total_effort > 80 or total_dependencies > 10:
            critical_phases.append(phase.phase_number)
    return critical_phases


def _calculate_optimization_metrics(self, phases: List[MVPPhase]) -> Dict[str, float]:
    """Calculate optimization metrics."""
    total_tasks = sum((len(phase.tasks) for phase in phases))
    total_effort = sum(
        (sum((task.estimated_effort for task in phase.tasks)) for phase in phases)
    )
    total_parallel_groups = sum((len(phase.parallel_groups) for phase in phases))
    return {
        "total_phases": len(phases),
        "total_tasks": total_tasks,
        "total_effort_hours": total_effort,
        "average_tasks_per_phase": total_tasks / len(phases) if phases else 0,
        "average_effort_per_phase": total_effort / len(phases) if phases else 0,
        "parallel_groups_total": total_parallel_groups,
        "parallelization_ratio": (
            total_parallel_groups / total_tasks if total_tasks > 0 else 0
        ),
    }


def _calculate_timeline_confidence(
    self, tasks: List[TaskNode], parallel_groups: List[ParallelGroup]
) -> float:
    """Calculate timeline confidence level."""
    confidence = 0.8
    completed_tasks = sum(
        (1 for task in tasks if task.completion_status == TaskStatus.COMPLETED)
    )
    completion_ratio = completed_tasks / len(tasks) if tasks else 0
    confidence += completion_ratio * 0.2
    high_complexity_tasks = sum((1 for task in tasks if task.estimated_effort > 20))
    complexity_ratio = high_complexity_tasks / len(tasks) if tasks else 0
    confidence -= complexity_ratio * 0.3
    if parallel_groups and len(parallel_groups) > 1:
        confidence += 0.1
    return max(0.1, min(1.0, confidence))


def _identify_timeline_risk_factors(self, tasks: List[TaskNode]) -> List[str]:
    """Identify timeline risk factors."""
    risk_factors = []
    high_effort_tasks = [task for task in tasks if task.estimated_effort > 40]
    if high_effort_tasks:
        risk_factors.append(f"{len(high_effort_tasks)} high-effort tasks (>40 hours)")
    blocked_tasks = [
        task for task in tasks if task.completion_status == TaskStatus.BLOCKED
    ]
    if blocked_tasks:
        risk_factors.append(f"{len(blocked_tasks)} blocked tasks requiring resolution")
    complex_deps = [task for task in tasks if len(task.dependencies) > 3]
    if complex_deps:
        risk_factors.append(f"{len(complex_deps)} tasks with complex dependencies")
    unknown_tasks = [
        task
        for task in tasks
        if task.completion_status == TaskStatus.NOT_STARTED
        and task.estimated_effort > 20
    ]
    if unknown_tasks:
        risk_factors.append(f"{len(unknown_tasks)} unstarted complex tasks")
    return (
        risk_factors if risk_factors else ["No significant timeline risks identified"]
    )
