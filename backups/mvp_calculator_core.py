"""
Mvp Calculator Core

This module was extracted from mvp_calculator.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import heapq
from ..models.dag_models import EcosystemDAG, TaskNode, MVPRoute, MVPPhase, RiskFactor, ParallelGroup, ResourceRequirements
from ..models.enums import TaskStatus, RiskType, RiskImpact
from ..analysis.dependency_mapper import ConstraintGraph
from datetime import datetime

@dataclass
class MVPCriteria:
    """Systematic MVP success criteria."""
    required_deliverables: List[str]
    success_metrics: Dict[str, float]
    maximum_timeline: int
    maximum_effort: int
    minimum_value_demonstration: List[str]
    quality_gates: Dict[str, float]
    risk_tolerance: RiskImpact

@dataclass
class RouteOption:
    """Potential MVP route option."""
    route_id: str
    tasks: List[TaskNode]
    estimated_effort: int
    estimated_timeline: int
    value_score: float
    risk_score: float
    deliverables: List[str]
    dependencies_satisfied: bool

class MVPRouteCalculator:
    """
    Systematic MVP route calculator for DAG orchestration.
    
    Identifies shortest paths to demonstrable systematic value
    while maintaining systematic quality and dependency compliance.
    """

    def __init__(self):
        self.working_hours_per_week = 40
        self.parallel_efficiency = 0.85
        self.phase_overhead = 0.1
        self.deliverable_weights = {'framework': 0.9, 'api': 0.8, 'integration': 0.7, 'documentation': 0.5, 'testing': 0.6, 'example': 0.4, 'prototype': 0.8}

    async def calculate_mvp_route(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> MVPRoute:
        """
        Calculate optimal route to MVP delivery.
        
        Args:
            ecosystem_dag: Complete ecosystem dependency graph
            mvp_criteria: Systematic criteria for MVP success
            
        Returns:
            MVPRoute: Optimal path with phases and deliverables
        """
        route_options = self._generate_route_options(ecosystem_dag, mvp_criteria)
        best_route = self._select_best_route(route_options, mvp_criteria)
        if not best_route:
            raise ValueError('No viable MVP route found within criteria constraints')
        mvp_route = await self._create_detailed_mvp_route(best_route, ecosystem_dag, mvp_criteria)
        return mvp_route

    async def optimize_mvp_phases(self, mvp_route: MVPRoute) -> List[MVPPhase]:
        """
        Optimize MVP route into systematic phases with clear deliverables.
        
        Args:
            mvp_route: MVP route to optimize
            
        Returns:
            List[MVPPhase]: Systematic phases with parallel execution plans
        """
        phase_groups = self._group_tasks_into_phases(mvp_route.critical_tasks)
        optimized_phases = []
        for i, (phase_name, tasks) in enumerate(phase_groups):
            parallel_groups = self._create_parallel_groups(tasks)
            objectives = self._define_phase_objectives(tasks, i + 1)
            deliverables = self._identify_phase_deliverables(tasks)
            success_criteria = self._define_success_criteria(tasks, deliverables)
            estimated_duration = self._calculate_phase_duration(parallel_groups)
            optimized_phases.append(MVPPhase(phase_name=phase_name, phase_number=i + 1, objectives=objectives, tasks=tasks, deliverables=deliverables, estimated_duration=estimated_duration, parallel_groups=parallel_groups, success_criteria=success_criteria, dependencies_satisfied=self._get_phase_dependencies(tasks)))
        return optimized_phases

    async def calculate_success_probability(self, mvp_route: MVPRoute) -> float:
        """
        Calculate systematic success probability for MVP route.
        
        Args:
            mvp_route: MVP route to analyze
            
        Returns:
            float: Risk-adjusted success probability (0.0 to 1.0)
        """
        base_probability = 0.8
        risk_adjustment = 0.0
        for risk in mvp_route.risk_factors:
            if risk.impact == RiskImpact.CRITICAL:
                risk_adjustment -= 0.3 * risk.probability
            elif risk.impact == RiskImpact.HIGH:
                risk_adjustment -= 0.2 * risk.probability
            elif risk.impact == RiskImpact.MEDIUM:
                risk_adjustment -= 0.1 * risk.probability
            else:
                risk_adjustment -= 0.05 * risk.probability
        if mvp_route.estimated_timeline > 12:
            risk_adjustment -= 0.1
        elif mvp_route.estimated_timeline > 8:
            risk_adjustment -= 0.05
        if mvp_route.total_estimated_effort > 1000:
            risk_adjustment -= 0.1
        elif mvp_route.total_estimated_effort > 500:
            risk_adjustment -= 0.05
        if len(mvp_route.phases) > 5:
            risk_adjustment -= 0.05
        success_probability = max(0.1, min(1.0, base_probability + risk_adjustment))
        return success_probability

    def _generate_route_options(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[RouteOption]:
        """Generate multiple route options for evaluation."""
        route_options = []
        min_viable_tasks = self._find_minimum_viable_tasks(ecosystem_dag, mvp_criteria)
        if min_viable_tasks:
            route_options.append(self._create_route_option('minimum_viable', min_viable_tasks, ecosystem_dag))
        value_optimized_tasks = self._find_value_optimized_tasks(ecosystem_dag, mvp_criteria)
        if value_optimized_tasks:
            route_options.append(self._create_route_option('value_optimized', value_optimized_tasks, ecosystem_dag))
        risk_minimized_tasks = self._find_risk_minimized_tasks(ecosystem_dag, mvp_criteria)
        if risk_minimized_tasks:
            route_options.append(self._create_route_option('risk_minimized', risk_minimized_tasks, ecosystem_dag))
        balanced_tasks = self._find_balanced_tasks(ecosystem_dag, mvp_criteria)
        if balanced_tasks:
            route_options.append(self._create_route_option('balanced', balanced_tasks, ecosystem_dag))
        return route_options

    def _find_minimum_viable_tasks(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[TaskNode]:
        """Find minimum set of tasks for viable MVP."""
        required_tasks = set()
        for deliverable in mvp_criteria.required_deliverables:
            tasks = self._find_tasks_for_deliverable(ecosystem_dag.tasks, deliverable)
            required_tasks.update(tasks)
        all_tasks = self._add_task_dependencies(list(required_tasks), ecosystem_dag.tasks)
        all_tasks.sort(key=lambda t: t.estimated_effort)
        return all_tasks

    def _find_value_optimized_tasks(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[TaskNode]:
        """Find tasks that maximize value demonstration."""
        task_scores = {}
        for task in ecosystem_dag.tasks:
            score = self._calculate_task_value_score(task, mvp_criteria)
            task_scores[task.task_id] = score
        selected_tasks = []
        total_effort = 0
        sorted_tasks = sorted(ecosystem_dag.tasks, key=lambda t: task_scores.get(t.task_id, 0), reverse=True)
        for task in sorted_tasks:
            if total_effort + task.estimated_effort <= mvp_criteria.maximum_effort:
                selected_tasks.append(task)
                total_effort += task.estimated_effort
        return self._add_task_dependencies(selected_tasks, ecosystem_dag.tasks)

    def _find_risk_minimized_tasks(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[TaskNode]:
        """Find tasks that minimize risk."""
        low_risk_tasks = []
        for task in ecosystem_dag.tasks:
            risk_score = self._calculate_task_risk_score(task)
            if risk_score < 0.5:
                if self._task_contributes_to_mvp(task, mvp_criteria):
                    low_risk_tasks.append(task)
        return self._add_minimal_dependencies(low_risk_tasks, ecosystem_dag.tasks)

    def _find_balanced_tasks(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[TaskNode]:
        """Find balanced set of tasks optimizing multiple factors."""
        task_scores = {}
        for task in ecosystem_dag.tasks:
            value_score = self._calculate_task_value_score(task, mvp_criteria)
            risk_score = self._calculate_task_risk_score(task)
            effort_score = 1.0 - task.estimated_effort / 40.0
            combined_score = 0.4 * value_score + 0.3 * (1.0 - risk_score) + 0.3 * effort_score
            task_scores[task.task_id] = combined_score
        selected_tasks = []
        total_effort = 0
        sorted_tasks = sorted(ecosystem_dag.tasks, key=lambda t: task_scores.get(t.task_id, 0), reverse=True)
        for task in sorted_tasks:
            if total_effort + task.estimated_effort <= mvp_criteria.maximum_effort:
                selected_tasks.append(task)
                total_effort += task.estimated_effort
        return self._add_task_dependencies(selected_tasks, ecosystem_dag.tasks)

    def _create_route_option(self, route_id: str, tasks: List[TaskNode], ecosystem_dag: EcosystemDAG) -> RouteOption:
        """Create a route option from selected tasks."""
        total_effort = sum((task.estimated_effort for task in tasks))
        estimated_timeline = self._estimate_timeline(tasks)
        value_score = self._calculate_route_value_score(tasks)
        risk_score = self._calculate_route_risk_score(tasks)
        deliverables = self._identify_route_deliverables(tasks)
        dependencies_satisfied = self._check_dependencies_satisfied(tasks, ecosystem_dag.tasks)
        return RouteOption(route_id=route_id, tasks=tasks, estimated_effort=total_effort, estimated_timeline=estimated_timeline, value_score=value_score, risk_score=risk_score, deliverables=deliverables, dependencies_satisfied=dependencies_satisfied)

    def _select_best_route(self, route_options: List[RouteOption], mvp_criteria: MVPCriteria) -> Optional[RouteOption]:
        """Select the best route option based on criteria."""
        viable_routes = []
        for route in route_options:
            if route.estimated_timeline <= mvp_criteria.maximum_timeline and route.estimated_effort <= mvp_criteria.maximum_effort and route.dependencies_satisfied and self._meets_minimum_deliverables(route, mvp_criteria):
                viable_routes.append(route)
        if not viable_routes:
            return None
        best_route = None
        best_score = -1
        for route in viable_routes:
            score = 0.4 * route.value_score + 0.3 * (1.0 - route.risk_score) + 0.2 * (1.0 - route.estimated_timeline / mvp_criteria.maximum_timeline) + 0.1 * (1.0 - route.estimated_effort / mvp_criteria.maximum_effort)
            if score > best_score:
                best_score = score
                best_route = route
        return best_route

    async def _create_detailed_mvp_route(self, route_option: RouteOption, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> MVPRoute:
        """Create detailed MVP route from selected option."""
        from datetime import datetime
        phases = await self.optimize_mvp_phases(MVPRoute(route_id=route_option.route_id, phases=[], critical_tasks=route_option.tasks, total_estimated_effort=route_option.estimated_effort, estimated_timeline=route_option.estimated_timeline, success_probability=0.0, risk_factors=[]))
        risk_factors = self._identify_risk_factors(route_option.tasks, mvp_criteria)
        mvp_route = MVPRoute(route_id=route_option.route_id, phases=phases, critical_tasks=route_option.tasks, total_estimated_effort=route_option.estimated_effort, estimated_timeline=route_option.estimated_timeline, success_probability=0.0, risk_factors=risk_factors)
        mvp_route.success_probability = await self.calculate_success_probability(mvp_route)
        return mvp_route

    def _find_tasks_for_deliverable(self, tasks: List[TaskNode], deliverable: str) -> List[TaskNode]:
        """Find tasks that contribute to a specific deliverable."""
        matching_tasks = []
        deliverable_lower = deliverable.lower()
        for task in tasks:
            task_desc_lower = task.description.lower()
            task_name_lower = task.task_name.lower()
            if deliverable_lower in task_desc_lower or deliverable_lower in task_name_lower or any((keyword in task_desc_lower for keyword in deliverable_lower.split())):
                matching_tasks.append(task)
        return matching_tasks

    def _calculate_task_value_score(self, task: TaskNode, mvp_criteria: MVPCriteria) -> float:
        """Calculate value score for a task."""
        score = 0.0
        for deliverable in mvp_criteria.required_deliverables:
            if deliverable.lower() in task.description.lower():
                for deliverable_type, weight in self.deliverable_weights.items():
                    if deliverable_type in deliverable.lower():
                        score += weight
                        break
                else:
                    score += 0.5
        if task.completion_status == TaskStatus.COMPLETED:
            score += 0.2
        if task.estimated_effort > 20:
            score -= 0.1
        return min(1.0, max(0.0, score))

    def _calculate_task_risk_score(self, task: TaskNode) -> float:
        """Calculate risk score for a task (0.0 = low risk, 1.0 = high risk)."""
        risk_score = 0.0
        if task.completion_status == TaskStatus.COMPLETED:
            risk_score += 0.0
        elif task.completion_status == TaskStatus.IN_PROGRESS:
            risk_score += 0.2
        elif task.completion_status == TaskStatus.BLOCKED:
            risk_score += 0.8
        elif task.completion_status == TaskStatus.FAILED:
            risk_score += 0.9
        else:
            risk_score += 0.4
        if task.estimated_effort > 40:
            risk_score += 0.3
        elif task.estimated_effort > 20:
            risk_score += 0.1
        complexity_keywords = ['complex', 'advanced', 'comprehensive', 'integrate', 'optimize']
        task_text = f'{task.task_name} {task.description}'.lower()
        for keyword in complexity_keywords:
            if keyword in task_text:
                risk_score += 0.1
        return min(1.0, risk_score)

    def _add_task_dependencies(self, selected_tasks: List[TaskNode], all_tasks: List[TaskNode]) -> List[TaskNode]:
        """Add all dependencies for selected tasks."""
        task_lookup = {task.task_id: task for task in all_tasks}
        result_tasks = set((task.task_id for task in selected_tasks))

        def add_deps(task_id: str):
            if task_id not in task_lookup:
                return
            task = task_lookup[task_id]
            for dep_id in task.dependencies:
                if dep_id not in result_tasks and dep_id in task_lookup:
                    result_tasks.add(dep_id)
                    add_deps(dep_id)
        for task in selected_tasks:
            add_deps(task.task_id)
        return [task_lookup[task_id] for task_id in result_tasks if task_id in task_lookup]

    def _group_tasks_into_phases(self, tasks: List[TaskNode]) -> List[Tuple[str, List[TaskNode]]]:
        """Group tasks into logical phases."""
        phases = []
        foundation_tasks = [task for task in tasks if any((keyword in task.task_name.lower() for keyword in ['setup', 'infrastructure', 'foundation', 'core', 'base']))]
        if foundation_tasks:
            phases.append(('Foundation Setup', foundation_tasks))
        core_tasks = [task for task in tasks if task not in foundation_tasks and any((keyword in task.task_name.lower() for keyword in ['implement', 'create', 'build', 'develop']))]
        if core_tasks:
            phases.append(('Core Implementation', core_tasks))
        integration_tasks = [task for task in tasks if task not in foundation_tasks and task not in core_tasks and any((keyword in task.task_name.lower() for keyword in ['integrate', 'test', 'validate', 'verify']))]
        if integration_tasks:
            phases.append(('Integration & Testing', integration_tasks))
        remaining_tasks = [task for task in tasks if task not in foundation_tasks and task not in core_tasks and (task not in integration_tasks)]
        if remaining_tasks:
            phases.append(('Finalization', remaining_tasks))
        return phases

    def _create_parallel_groups(self, tasks: List[TaskNode]) -> List[ParallelGroup]:
        """Create parallel groups from tasks."""
        groups = []
        remaining_tasks = tasks.copy()
        group_id = 0
        while remaining_tasks:
            group_id += 1
            current_group = [remaining_tasks.pop(0)]
            current_effort = current_group[0].estimated_effort
            i = 0
            while i < len(remaining_tasks):
                task = remaining_tasks[i]
                if abs(task.estimated_effort - current_effort) <= 8:
                    current_group.append(remaining_tasks.pop(i))
                else:
                    i += 1
            max_effort = max((task.estimated_effort for task in current_group))
            estimated_duration = max_effort // 8
            groups.append(ParallelGroup(group_id=f'group_{group_id}', tasks=current_group, estimated_duration=estimated_duration, coordination_overhead=0.1 if len(current_group) > 1 else 0.0))
        return groups

    def _define_phase_objectives(self, tasks: List[TaskNode], phase_number: int) -> List[str]:
        """Define objectives for a phase."""
        objectives = []
        if phase_number == 1:
            objectives.append('Establish foundational infrastructure and core interfaces')
        elif phase_number == 2:
            objectives.append('Implement core functionality and business logic')
        elif phase_number == 3:
            objectives.append('Integrate components and validate system behavior')
        else:
            objectives.append('Complete remaining features and prepare for deployment')
        task_keywords = set()
        for task in tasks:
            words = task.task_name.lower().split()
            task_keywords.update(words)
        if 'api' in task_keywords:
            objectives.append('Deliver functional API endpoints')
        if 'test' in task_keywords:
            objectives.append('Achieve comprehensive test coverage')
        if 'documentation' in task_keywords:
            objectives.append('Provide complete documentation')
        return objectives

    def _identify_phase_deliverables(self, tasks: List[TaskNode]) -> List[str]:
        """Identify deliverables for a phase."""
        deliverables = []
        for task in tasks:
            task_text = f'{task.task_name} {task.description}'.lower()
            if 'api' in task_text:
                deliverables.append('Functional API')
            if 'framework' in task_text:
                deliverables.append('Framework Implementation')
            if 'test' in task_text:
                deliverables.append('Test Suite')
            if 'documentation' in task_text:
                deliverables.append('Documentation')
            if 'example' in task_text:
                deliverables.append('Working Examples')
        return list(set(deliverables))

    def _define_success_criteria(self, tasks: List[TaskNode], deliverables: List[str]) -> List[str]:
        """Define success criteria for a phase."""
        criteria = []
        criteria.append(f'All {len(tasks)} tasks completed successfully')
        for deliverable in deliverables:
            criteria.append(f'{deliverable} is functional and tested')
        criteria.append('No critical bugs or issues')
        criteria.append('Code review and quality gates passed')
        return criteria

    def _calculate_phase_duration(self, parallel_groups: List[ParallelGroup]) -> int:
        """Calculate phase duration in weeks."""
        total_days = sum((group.estimated_duration for group in parallel_groups))
        return max(1, total_days // 5)

    def _get_phase_dependencies(self, tasks: List[TaskNode]) -> List[str]:
        """Get dependencies satisfied by completing this phase."""
        dependencies = []
        for task in tasks:
            dependencies.extend(task.requirements_traced)
        return list(set(dependencies))

    def _task_contributes_to_mvp(self, task: TaskNode, mvp_criteria: MVPCriteria) -> bool:
        """Check if task contributes to MVP deliverables."""
        task_text = f'{task.task_name} {task.description}'.lower()
        for deliverable in mvp_criteria.required_deliverables:
            if deliverable.lower() in task_text:
                return True
        return False

    def _add_minimal_dependencies(self, tasks: List[TaskNode], all_tasks: List[TaskNode]) -> List[TaskNode]:
        """Add only essential dependencies."""
        task_lookup = {task.task_id: task for task in all_tasks}
        result_tasks = set((task.task_id for task in tasks))
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in task_lookup:
                    result_tasks.add(dep_id)
        return [task_lookup[task_id] for task_id in result_tasks if task_id in task_lookup]

    def _estimate_timeline(self, tasks: List[TaskNode]) -> int:
        """Estimate timeline in weeks for tasks."""
        total_effort = sum((task.estimated_effort for task in tasks))
        return max(1, int(total_effort / self.working_hours_per_week))

    def _calculate_route_value_score(self, tasks: List[TaskNode]) -> float:
        """Calculate overall value score for a route."""
        if not tasks:
            return 0.0
        total_score = sum((self._calculate_task_value_score(task, MVPCriteria(required_deliverables=[], success_metrics={}, maximum_timeline=12, maximum_effort=1000, minimum_value_demonstration=[], quality_gates={}, risk_tolerance=RiskImpact.MEDIUM)) for task in tasks))
        return total_score / len(tasks)

    def _calculate_route_risk_score(self, tasks: List[TaskNode]) -> float:
        """Calculate overall risk score for a route."""
        if not tasks:
            return 0.0
        total_score = sum((self._calculate_task_risk_score(task) for task in tasks))
        return total_score / len(tasks)

    def _identify_route_deliverables(self, tasks: List[TaskNode]) -> List[str]:
        """Identify deliverables for a route."""
        deliverables = set()
        for task in tasks:
            task_deliverables = self._identify_phase_deliverables([task])
            deliverables.update(task_deliverables)
        return list(deliverables)

    def _check_dependencies_satisfied(self, selected_tasks: List[TaskNode], all_tasks: List[TaskNode]) -> bool:
        """Check if all dependencies are satisfied."""
        selected_ids = {task.task_id for task in selected_tasks}
        task_lookup = {task.task_id: task for task in all_tasks}
        for task in selected_tasks:
            for dep_id in task.dependencies:
                if dep_id not in selected_ids and dep_id in task_lookup:
                    dep_task = task_lookup[dep_id]
                    if dep_task.completion_status != TaskStatus.COMPLETED:
                        return False
        return True

    def _meets_minimum_deliverables(self, route: RouteOption, mvp_criteria: MVPCriteria) -> bool:
        """Check if route meets minimum deliverable requirements."""
        route_deliverables = set((d.lower() for d in route.deliverables))
        required_deliverables = set((d.lower() for d in mvp_criteria.required_deliverables))
        covered = len(route_deliverables.intersection(required_deliverables))
        required = len(required_deliverables)
        return required == 0 or covered / required >= 0.8

    def _identify_risk_factors(self, tasks: List[TaskNode], mvp_criteria: MVPCriteria) -> List[RiskFactor]:
        """Identify risk factors for the route."""
        risk_factors = []
        high_effort_tasks = [task for task in tasks if task.estimated_effort > 40]
        if high_effort_tasks:
            risk_factors.append(RiskFactor(risk_id='high_effort_tasks', risk_type=RiskType.TIMELINE_RISK, probability=0.6, impact=RiskImpact.MEDIUM, affected_tasks=[task.task_id for task in high_effort_tasks], mitigation_strategy='Break down large tasks into smaller components'))
        blocked_tasks = [task for task in tasks if task.completion_status == TaskStatus.BLOCKED]
        if blocked_tasks:
            risk_factors.append(RiskFactor(risk_id='blocked_tasks', risk_type=RiskType.DEPENDENCY_RISK, probability=0.8, impact=RiskImpact.HIGH, affected_tasks=[task.task_id for task in blocked_tasks], mitigation_strategy='Resolve blocking dependencies immediately'))
        total_effort = sum((task.estimated_effort for task in tasks))
        if total_effort > mvp_criteria.maximum_effort * 0.8:
            risk_factors.append(RiskFactor(risk_id='timeline_pressure', risk_type=RiskType.TIMELINE_RISK, probability=0.7, impact=RiskImpact.MEDIUM, affected_tasks=[task.task_id for task in tasks], mitigation_strategy='Consider scope reduction or additional resources'))
        return risk_factors

def __init__(self):
    self.working_hours_per_week = 40
    self.parallel_efficiency = 0.85
    self.phase_overhead = 0.1
    self.deliverable_weights = {'framework': 0.9, 'api': 0.8, 'integration': 0.7, 'documentation': 0.5, 'testing': 0.6, 'example': 0.4, 'prototype': 0.8}

def _generate_route_options(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[RouteOption]:
    """Generate multiple route options for evaluation."""
    route_options = []
    min_viable_tasks = self._find_minimum_viable_tasks(ecosystem_dag, mvp_criteria)
    if min_viable_tasks:
        route_options.append(self._create_route_option('minimum_viable', min_viable_tasks, ecosystem_dag))
    value_optimized_tasks = self._find_value_optimized_tasks(ecosystem_dag, mvp_criteria)
    if value_optimized_tasks:
        route_options.append(self._create_route_option('value_optimized', value_optimized_tasks, ecosystem_dag))
    risk_minimized_tasks = self._find_risk_minimized_tasks(ecosystem_dag, mvp_criteria)
    if risk_minimized_tasks:
        route_options.append(self._create_route_option('risk_minimized', risk_minimized_tasks, ecosystem_dag))
    balanced_tasks = self._find_balanced_tasks(ecosystem_dag, mvp_criteria)
    if balanced_tasks:
        route_options.append(self._create_route_option('balanced', balanced_tasks, ecosystem_dag))
    return route_options

def _find_minimum_viable_tasks(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[TaskNode]:
    """Find minimum set of tasks for viable MVP."""
    required_tasks = set()
    for deliverable in mvp_criteria.required_deliverables:
        tasks = self._find_tasks_for_deliverable(ecosystem_dag.tasks, deliverable)
        required_tasks.update(tasks)
    all_tasks = self._add_task_dependencies(list(required_tasks), ecosystem_dag.tasks)
    all_tasks.sort(key=lambda t: t.estimated_effort)
    return all_tasks

def _find_value_optimized_tasks(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[TaskNode]:
    """Find tasks that maximize value demonstration."""
    task_scores = {}
    for task in ecosystem_dag.tasks:
        score = self._calculate_task_value_score(task, mvp_criteria)
        task_scores[task.task_id] = score
    selected_tasks = []
    total_effort = 0
    sorted_tasks = sorted(ecosystem_dag.tasks, key=lambda t: task_scores.get(t.task_id, 0), reverse=True)
    for task in sorted_tasks:
        if total_effort + task.estimated_effort <= mvp_criteria.maximum_effort:
            selected_tasks.append(task)
            total_effort += task.estimated_effort
    return self._add_task_dependencies(selected_tasks, ecosystem_dag.tasks)

def _find_risk_minimized_tasks(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[TaskNode]:
    """Find tasks that minimize risk."""
    low_risk_tasks = []
    for task in ecosystem_dag.tasks:
        risk_score = self._calculate_task_risk_score(task)
        if risk_score < 0.5:
            if self._task_contributes_to_mvp(task, mvp_criteria):
                low_risk_tasks.append(task)
    return self._add_minimal_dependencies(low_risk_tasks, ecosystem_dag.tasks)

def _find_balanced_tasks(self, ecosystem_dag: EcosystemDAG, mvp_criteria: MVPCriteria) -> List[TaskNode]:
    """Find balanced set of tasks optimizing multiple factors."""
    task_scores = {}
    for task in ecosystem_dag.tasks:
        value_score = self._calculate_task_value_score(task, mvp_criteria)
        risk_score = self._calculate_task_risk_score(task)
        effort_score = 1.0 - task.estimated_effort / 40.0
        combined_score = 0.4 * value_score + 0.3 * (1.0 - risk_score) + 0.3 * effort_score
        task_scores[task.task_id] = combined_score
    selected_tasks = []
    total_effort = 0
    sorted_tasks = sorted(ecosystem_dag.tasks, key=lambda t: task_scores.get(t.task_id, 0), reverse=True)
    for task in sorted_tasks:
        if total_effort + task.estimated_effort <= mvp_criteria.maximum_effort:
            selected_tasks.append(task)
            total_effort += task.estimated_effort
    return self._add_task_dependencies(selected_tasks, ecosystem_dag.tasks)

def _create_route_option(self, route_id: str, tasks: List[TaskNode], ecosystem_dag: EcosystemDAG) -> RouteOption:
    """Create a route option from selected tasks."""
    total_effort = sum((task.estimated_effort for task in tasks))
    estimated_timeline = self._estimate_timeline(tasks)
    value_score = self._calculate_route_value_score(tasks)
    risk_score = self._calculate_route_risk_score(tasks)
    deliverables = self._identify_route_deliverables(tasks)
    dependencies_satisfied = self._check_dependencies_satisfied(tasks, ecosystem_dag.tasks)
    return RouteOption(route_id=route_id, tasks=tasks, estimated_effort=total_effort, estimated_timeline=estimated_timeline, value_score=value_score, risk_score=risk_score, deliverables=deliverables, dependencies_satisfied=dependencies_satisfied)

def _select_best_route(self, route_options: List[RouteOption], mvp_criteria: MVPCriteria) -> Optional[RouteOption]:
    """Select the best route option based on criteria."""
    viable_routes = []
    for route in route_options:
        if route.estimated_timeline <= mvp_criteria.maximum_timeline and route.estimated_effort <= mvp_criteria.maximum_effort and route.dependencies_satisfied and self._meets_minimum_deliverables(route, mvp_criteria):
            viable_routes.append(route)
    if not viable_routes:
        return None
    best_route = None
    best_score = -1
    for route in viable_routes:
        score = 0.4 * route.value_score + 0.3 * (1.0 - route.risk_score) + 0.2 * (1.0 - route.estimated_timeline / mvp_criteria.maximum_timeline) + 0.1 * (1.0 - route.estimated_effort / mvp_criteria.maximum_effort)
        if score > best_score:
            best_score = score
            best_route = route
    return best_route

def _find_tasks_for_deliverable(self, tasks: List[TaskNode], deliverable: str) -> List[TaskNode]:
    """Find tasks that contribute to a specific deliverable."""
    matching_tasks = []
    deliverable_lower = deliverable.lower()
    for task in tasks:
        task_desc_lower = task.description.lower()
        task_name_lower = task.task_name.lower()
        if deliverable_lower in task_desc_lower or deliverable_lower in task_name_lower or any((keyword in task_desc_lower for keyword in deliverable_lower.split())):
            matching_tasks.append(task)
    return matching_tasks

def _calculate_task_value_score(self, task: TaskNode, mvp_criteria: MVPCriteria) -> float:
    """Calculate value score for a task."""
    score = 0.0
    for deliverable in mvp_criteria.required_deliverables:
        if deliverable.lower() in task.description.lower():
            for deliverable_type, weight in self.deliverable_weights.items():
                if deliverable_type in deliverable.lower():
                    score += weight
                    break
            else:
                score += 0.5
    if task.completion_status == TaskStatus.COMPLETED:
        score += 0.2
    if task.estimated_effort > 20:
        score -= 0.1
    return min(1.0, max(0.0, score))

def _calculate_task_risk_score(self, task: TaskNode) -> float:
    """Calculate risk score for a task (0.0 = low risk, 1.0 = high risk)."""
    risk_score = 0.0
    if task.completion_status == TaskStatus.COMPLETED:
        risk_score += 0.0
    elif task.completion_status == TaskStatus.IN_PROGRESS:
        risk_score += 0.2
    elif task.completion_status == TaskStatus.BLOCKED:
        risk_score += 0.8
    elif task.completion_status == TaskStatus.FAILED:
        risk_score += 0.9
    else:
        risk_score += 0.4
    if task.estimated_effort > 40:
        risk_score += 0.3
    elif task.estimated_effort > 20:
        risk_score += 0.1
    complexity_keywords = ['complex', 'advanced', 'comprehensive', 'integrate', 'optimize']
    task_text = f'{task.task_name} {task.description}'.lower()
    for keyword in complexity_keywords:
        if keyword in task_text:
            risk_score += 0.1
    return min(1.0, risk_score)

def _add_task_dependencies(self, selected_tasks: List[TaskNode], all_tasks: List[TaskNode]) -> List[TaskNode]:
    """Add all dependencies for selected tasks."""
    task_lookup = {task.task_id: task for task in all_tasks}
    result_tasks = set((task.task_id for task in selected_tasks))

    def add_deps(task_id: str):
        if task_id not in task_lookup:
            return
        task = task_lookup[task_id]
        for dep_id in task.dependencies:
            if dep_id not in result_tasks and dep_id in task_lookup:
                result_tasks.add(dep_id)
                add_deps(dep_id)
    for task in selected_tasks:
        add_deps(task.task_id)
    return [task_lookup[task_id] for task_id in result_tasks if task_id in task_lookup]

def _group_tasks_into_phases(self, tasks: List[TaskNode]) -> List[Tuple[str, List[TaskNode]]]:
    """Group tasks into logical phases."""
    phases = []
    foundation_tasks = [task for task in tasks if any((keyword in task.task_name.lower() for keyword in ['setup', 'infrastructure', 'foundation', 'core', 'base']))]
    if foundation_tasks:
        phases.append(('Foundation Setup', foundation_tasks))
    core_tasks = [task for task in tasks if task not in foundation_tasks and any((keyword in task.task_name.lower() for keyword in ['implement', 'create', 'build', 'develop']))]
    if core_tasks:
        phases.append(('Core Implementation', core_tasks))
    integration_tasks = [task for task in tasks if task not in foundation_tasks and task not in core_tasks and any((keyword in task.task_name.lower() for keyword in ['integrate', 'test', 'validate', 'verify']))]
    if integration_tasks:
        phases.append(('Integration & Testing', integration_tasks))
    remaining_tasks = [task for task in tasks if task not in foundation_tasks and task not in core_tasks and (task not in integration_tasks)]
    if remaining_tasks:
        phases.append(('Finalization', remaining_tasks))
    return phases

def _create_parallel_groups(self, tasks: List[TaskNode]) -> List[ParallelGroup]:
    """Create parallel groups from tasks."""
    groups = []
    remaining_tasks = tasks.copy()
    group_id = 0
    while remaining_tasks:
        group_id += 1
        current_group = [remaining_tasks.pop(0)]
        current_effort = current_group[0].estimated_effort
        i = 0
        while i < len(remaining_tasks):
            task = remaining_tasks[i]
            if abs(task.estimated_effort - current_effort) <= 8:
                current_group.append(remaining_tasks.pop(i))
            else:
                i += 1
        max_effort = max((task.estimated_effort for task in current_group))
        estimated_duration = max_effort // 8
        groups.append(ParallelGroup(group_id=f'group_{group_id}', tasks=current_group, estimated_duration=estimated_duration, coordination_overhead=0.1 if len(current_group) > 1 else 0.0))
    return groups

def _define_phase_objectives(self, tasks: List[TaskNode], phase_number: int) -> List[str]:
    """Define objectives for a phase."""
    objectives = []
    if phase_number == 1:
        objectives.append('Establish foundational infrastructure and core interfaces')
    elif phase_number == 2:
        objectives.append('Implement core functionality and business logic')
    elif phase_number == 3:
        objectives.append('Integrate components and validate system behavior')
    else:
        objectives.append('Complete remaining features and prepare for deployment')
    task_keywords = set()
    for task in tasks:
        words = task.task_name.lower().split()
        task_keywords.update(words)
    if 'api' in task_keywords:
        objectives.append('Deliver functional API endpoints')
    if 'test' in task_keywords:
        objectives.append('Achieve comprehensive test coverage')
    if 'documentation' in task_keywords:
        objectives.append('Provide complete documentation')
    return objectives

def _identify_phase_deliverables(self, tasks: List[TaskNode]) -> List[str]:
    """Identify deliverables for a phase."""
    deliverables = []
    for task in tasks:
        task_text = f'{task.task_name} {task.description}'.lower()
        if 'api' in task_text:
            deliverables.append('Functional API')
        if 'framework' in task_text:
            deliverables.append('Framework Implementation')
        if 'test' in task_text:
            deliverables.append('Test Suite')
        if 'documentation' in task_text:
            deliverables.append('Documentation')
        if 'example' in task_text:
            deliverables.append('Working Examples')
    return list(set(deliverables))

def _define_success_criteria(self, tasks: List[TaskNode], deliverables: List[str]) -> List[str]:
    """Define success criteria for a phase."""
    criteria = []
    criteria.append(f'All {len(tasks)} tasks completed successfully')
    for deliverable in deliverables:
        criteria.append(f'{deliverable} is functional and tested')
    criteria.append('No critical bugs or issues')
    criteria.append('Code review and quality gates passed')
    return criteria

def _calculate_phase_duration(self, parallel_groups: List[ParallelGroup]) -> int:
    """Calculate phase duration in weeks."""
    total_days = sum((group.estimated_duration for group in parallel_groups))
    return max(1, total_days // 5)

def _get_phase_dependencies(self, tasks: List[TaskNode]) -> List[str]:
    """Get dependencies satisfied by completing this phase."""
    dependencies = []
    for task in tasks:
        dependencies.extend(task.requirements_traced)
    return list(set(dependencies))

def _task_contributes_to_mvp(self, task: TaskNode, mvp_criteria: MVPCriteria) -> bool:
    """Check if task contributes to MVP deliverables."""
    task_text = f'{task.task_name} {task.description}'.lower()
    for deliverable in mvp_criteria.required_deliverables:
        if deliverable.lower() in task_text:
            return True
    return False

def _add_minimal_dependencies(self, tasks: List[TaskNode], all_tasks: List[TaskNode]) -> List[TaskNode]:
    """Add only essential dependencies."""
    task_lookup = {task.task_id: task for task in all_tasks}
    result_tasks = set((task.task_id for task in tasks))
    for task in tasks:
        for dep_id in task.dependencies:
            if dep_id in task_lookup:
                result_tasks.add(dep_id)
    return [task_lookup[task_id] for task_id in result_tasks if task_id in task_lookup]

def _estimate_timeline(self, tasks: List[TaskNode]) -> int:
    """Estimate timeline in weeks for tasks."""
    total_effort = sum((task.estimated_effort for task in tasks))
    return max(1, int(total_effort / self.working_hours_per_week))

def _calculate_route_value_score(self, tasks: List[TaskNode]) -> float:
    """Calculate overall value score for a route."""
    if not tasks:
        return 0.0
    total_score = sum((self._calculate_task_value_score(task, MVPCriteria(required_deliverables=[], success_metrics={}, maximum_timeline=12, maximum_effort=1000, minimum_value_demonstration=[], quality_gates={}, risk_tolerance=RiskImpact.MEDIUM)) for task in tasks))
    return total_score / len(tasks)

def _calculate_route_risk_score(self, tasks: List[TaskNode]) -> float:
    """Calculate overall risk score for a route."""
    if not tasks:
        return 0.0
    total_score = sum((self._calculate_task_risk_score(task) for task in tasks))
    return total_score / len(tasks)

def _identify_route_deliverables(self, tasks: List[TaskNode]) -> List[str]:
    """Identify deliverables for a route."""
    deliverables = set()
    for task in tasks:
        task_deliverables = self._identify_phase_deliverables([task])
        deliverables.update(task_deliverables)
    return list(deliverables)

def _meets_minimum_deliverables(self, route: RouteOption, mvp_criteria: MVPCriteria) -> bool:
    """Check if route meets minimum deliverable requirements."""
    route_deliverables = set((d.lower() for d in route.deliverables))
    required_deliverables = set((d.lower() for d in mvp_criteria.required_deliverables))
    covered = len(route_deliverables.intersection(required_deliverables))
    required = len(required_deliverables)
    return required == 0 or covered / required >= 0.8

def _identify_risk_factors(self, tasks: List[TaskNode], mvp_criteria: MVPCriteria) -> List[RiskFactor]:
    """Identify risk factors for the route."""
    risk_factors = []
    high_effort_tasks = [task for task in tasks if task.estimated_effort > 40]
    if high_effort_tasks:
        risk_factors.append(RiskFactor(risk_id='high_effort_tasks', risk_type=RiskType.TIMELINE_RISK, probability=0.6, impact=RiskImpact.MEDIUM, affected_tasks=[task.task_id for task in high_effort_tasks], mitigation_strategy='Break down large tasks into smaller components'))
    blocked_tasks = [task for task in tasks if task.completion_status == TaskStatus.BLOCKED]
    if blocked_tasks:
        risk_factors.append(RiskFactor(risk_id='blocked_tasks', risk_type=RiskType.DEPENDENCY_RISK, probability=0.8, impact=RiskImpact.HIGH, affected_tasks=[task.task_id for task in blocked_tasks], mitigation_strategy='Resolve blocking dependencies immediately'))
    total_effort = sum((task.estimated_effort for task in tasks))
    if total_effort > mvp_criteria.maximum_effort * 0.8:
        risk_factors.append(RiskFactor(risk_id='timeline_pressure', risk_type=RiskType.TIMELINE_RISK, probability=0.7, impact=RiskImpact.MEDIUM, affected_tasks=[task.task_id for task in tasks], mitigation_strategy='Consider scope reduction or additional resources'))
    return risk_factors

def add_deps(task_id: str):
    if task_id not in task_lookup:
        return
    task = task_lookup[task_id]
    for dep_id in task.dependencies:
        if dep_id not in result_tasks and dep_id in task_lookup:
            result_tasks.add(dep_id)
            add_deps(dep_id)
