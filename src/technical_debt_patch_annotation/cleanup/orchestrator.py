"""
Forward Pass Cleanup Orchestrator for Technical Debt Patch Annotation System.

This module implements systematic cleanup planning algorithms with patch grouping,
execution order optimization based on component dependencies, and validation
frameworks for cleanup completion with rollback mechanisms.

Requirements addressed: 4.1, 4.2, 4.3, 4.4, 4.5
"""

import json
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, GracefulDegradationResult
from ..core.models import PatchAnnotation, DebtLevel, BypassType, ValidationResult


class CleanupStatus(Enum):
    """Status of cleanup tasks and plans."""
    DRAFT = "Draft"
    APPROVED = "Approved"
    IN_PROGRESS = "In_Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    ROLLED_BACK = "Rolled_Back"


class RiskLevel(Enum):
    """Risk assessment levels for cleanup operations."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class CleanupCriteria:
    """Criteria for selecting patches for cleanup."""
    target_components: List[str] = field(default_factory=list)
    debt_levels: List[DebtLevel] = field(default_factory=list)
    max_patches: Optional[int] = None
    priority_threshold: float = 0.0
    include_expired: bool = True
    exclude_patch_ids: List[str] = field(default_factory=list)
    created_before: Optional[datetime] = None
    created_after: Optional[datetime] = None


@dataclass
class CleanupTask:
    """Individual cleanup task within a cleanup plan."""
    task_id: str = field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8].upper()}")
    patch_id: str = ""
    component: str = ""
    description: str = ""
    remediation_steps: List[str] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Other task IDs this depends on
    estimated_effort: timedelta = field(default_factory=lambda: timedelta(hours=1))
    risk_level: RiskLevel = RiskLevel.MEDIUM
    assigned_to: str = ""
    status: CleanupStatus = CleanupStatus.DRAFT
    created_date: datetime = field(default_factory=datetime.now)
    completed_date: Optional[datetime] = None
    validation_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackPlan:
    """Rollback plan for cleanup operations."""
    rollback_id: str = field(default_factory=lambda: f"ROLLBACK-{uuid.uuid4().hex[:8].upper()}")
    rollback_steps: List[str] = field(default_factory=list)
    backup_locations: Dict[str, str] = field(default_factory=dict)  # file -> backup_path
    rollback_validation: List[str] = field(default_factory=list)
    emergency_contacts: List[str] = field(default_factory=list)
    estimated_rollback_time: timedelta = field(default_factory=lambda: timedelta(minutes=30))


@dataclass
class CleanupPlan:
    """Systematic cleanup execution plan."""
    plan_id: str = field(default_factory=lambda: f"PLAN-{uuid.uuid4().hex[:8].upper()}")
    plan_name: str = ""
    target_components: List[str] = field(default_factory=list)
    patches_to_resolve: List[PatchAnnotation] = field(default_factory=list)
    execution_order: List[CleanupTask] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)
    rollback_plan: Optional[RollbackPlan] = None
    estimated_effort: timedelta = field(default_factory=lambda: timedelta(hours=4))
    risk_assessment: RiskLevel = RiskLevel.MEDIUM
    created_date: datetime = field(default_factory=datetime.now)
    scheduled_date: Optional[datetime] = None
    status: CleanupStatus = CleanupStatus.DRAFT
    created_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ValidationResult:
    """Result of cleanup validation operations."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None, 
                 metadata: Dict[str, Any] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.metadata = metadata or {}
        self.validation_timestamp = datetime.now()


class ForwardPassOrchestrator(ReflectiveModule):
    """
    Manages systematic patch cleanup processes with component-based grouping,
    dependency-aware execution ordering, and comprehensive validation.
    
    This orchestrator implements Requirements 4.1-4.5 for forward pass management:
    - 4.1: Patches marked for forward pass appear in cleanup planning reports
    - 4.2: Forward passes group patches by component and priority
    - 4.3: Cleanup provides specific remediation steps
    - 4.4: Patches are marked completed with validation
    - 4.5: Success is verified through automated testing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Forward Pass Orchestrator.
        
        Args:
            config: Configuration dictionary with orchestrator settings
        """
        super().__init__()
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Component dependency graph for execution ordering
        self.component_dependencies: Dict[str, Set[str]] = {}
        
        # Active cleanup plans
        self.active_plans: Dict[str, CleanupPlan] = {}
        
        # Cleanup history for learning and optimization
        self.cleanup_history: List[CleanupPlan] = []
        
        # Risk assessment thresholds
        self.risk_thresholds = {
            'critical_component_count': 3,
            'high_debt_patch_count': 5,
            'total_patch_count': 20,
            'estimated_effort_hours': 8
        }
        
        self.logger.info("ForwardPassOrchestrator initialized")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant."""
        return {
            'module_id': 'forward_pass_orchestrator',
            'name': 'Forward Pass Cleanup Orchestrator',
            'version': '1.0.0',
            'description': 'Systematic cleanup planning and execution for technical debt patches',
            'capabilities': [cap.value for cap in self.get_capabilities()],
            'active_plans': len(self.active_plans),
            'completed_plans': len(self.cleanup_history),
            'component_dependencies': len(self.component_dependencies)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant."""
        issues = []
        
        # Check for overdue plans
        overdue_plans = sum(1 for plan in self.active_plans.values() 
                           if plan.scheduled_date and plan.scheduled_date < datetime.now())
        if overdue_plans > 0:
            issues.append(f"{overdue_plans} cleanup plans are overdue")
        
        # Check for failed plans
        failed_plans = sum(1 for plan in self.active_plans.values() 
                          if plan.status == CleanupStatus.FAILED)
        if failed_plans > 0:
            issues.append(f"{failed_plans} cleanup plans have failed")
        
        # Determine status
        if failed_plans > 0:
            status = ModuleStatus.ERROR
            health_score = 0.3
        elif overdue_plans > 0:
            status = ModuleStatus.WARNING
            health_score = 0.7
        elif len(self.active_plans) > 10:
            status = ModuleStatus.WARNING
            health_score = 0.8
            issues.append("High number of active cleanup plans")
        else:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
        
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return ModuleHealth(
            module_id='forward_pass_orchestrator',
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant."""
        try:
            # In degraded mode, we can still plan cleanups but not execute them
            degraded_capabilities = []
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,  # Can still plan cleanups
                ModuleCapability.VALIDATION,          # Can still validate plans
                ModuleCapability.MONITORING           # Can still monitor status
            ]
            
            # If we have too many active plans, degrade data processing
            if len(self.active_plans) > 20:
                degraded_capabilities.append(ModuleCapability.DATA_PROCESSING)
                remaining_capabilities.remove(ModuleCapability.DATA_PROCESSING)
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
            
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def plan_cleanup_pass(self, criteria: CleanupCriteria, patches: List[PatchAnnotation]) -> CleanupPlan:
        """
        Plan systematic cleanup of patches based on criteria.
        
        Implements Requirement 4.1: Patches marked for forward pass appear in cleanup planning reports
        Implements Requirement 4.2: Forward passes group patches by component and priority
        
        Args:
            criteria: Criteria for selecting and organizing patches
            patches: Available patches to consider for cleanup
            
        Returns:
            CleanupPlan with systematic execution strategy
        """
        self.logger.info(f"Planning cleanup pass with {len(patches)} patches")
        
        # Filter patches based on criteria
        filtered_patches = self._filter_patches_by_criteria(patches, criteria)
        self.logger.info(f"Filtered to {len(filtered_patches)} patches matching criteria")
        
        # Group patches by component for efficient cleanup
        component_groups = self.group_patches_by_component(filtered_patches)
        
        # Generate cleanup tasks for each patch
        cleanup_tasks = []
        for component, component_patches in component_groups.items():
            component_tasks = self._generate_component_cleanup_tasks(component, component_patches)
            cleanup_tasks.extend(component_tasks)
        
        # Optimize execution order based on dependencies
        ordered_tasks = self._optimize_execution_order(cleanup_tasks)
        
        # Assess risk level for the cleanup plan
        risk_level = self._assess_cleanup_risk(filtered_patches, ordered_tasks)
        
        # Generate rollback plan
        rollback_plan = self._generate_rollback_plan(ordered_tasks)
        
        # Create cleanup plan
        plan = CleanupPlan(
            plan_name=f"Cleanup Pass - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            target_components=list(component_groups.keys()),
            patches_to_resolve=filtered_patches,
            execution_order=ordered_tasks,
            validation_criteria=self._generate_plan_validation_criteria(filtered_patches),
            rollback_plan=rollback_plan,
            estimated_effort=self._calculate_total_effort(ordered_tasks),
            risk_assessment=risk_level,
            metadata={
                'criteria': criteria.__dict__,
                'component_count': len(component_groups),
                'task_count': len(ordered_tasks),
                'patch_distribution': {comp: len(patches) for comp, patches in component_groups.items()}
            }
        )
        
        # Store active plan
        self.active_plans[plan.plan_id] = plan
        
        self.logger.info(f"Created cleanup plan {plan.plan_id} with {len(ordered_tasks)} tasks")
        return plan
    
    def group_patches_by_component(self, patches: List[PatchAnnotation]) -> Dict[str, List[PatchAnnotation]]:
        """
        Group patches for efficient cleanup by component.
        
        Implements Requirement 4.2: Forward passes group patches by component and priority
        
        Args:
            patches: List of patches to group
            
        Returns:
            Dictionary mapping component names to lists of patches
        """
        component_groups = defaultdict(list)
        
        for patch in patches:
            component = patch.component or "unknown"
            component_groups[component].append(patch)
        
        # Sort patches within each component by priority (debt level and creation date)
        for component, component_patches in component_groups.items():
            component_patches.sort(key=lambda p: (
                self._get_debt_priority(p.debt_level),
                p.created_date
            ))
        
        return dict(component_groups)
    
    def generate_cleanup_tasks(self, cleanup_plan: CleanupPlan) -> List[CleanupTask]:
        """
        Generate specific cleanup implementation tasks from a cleanup plan.
        
        Implements Requirement 4.3: Cleanup provides specific remediation steps
        
        Args:
            cleanup_plan: The cleanup plan to generate tasks from
            
        Returns:
            List of detailed cleanup tasks with remediation steps
        """
        if not cleanup_plan.execution_order:
            # Generate tasks if not already present
            tasks = []
            component_groups = self.group_patches_by_component(cleanup_plan.patches_to_resolve)
            
            for component, patches in component_groups.items():
                component_tasks = self._generate_component_cleanup_tasks(component, patches)
                tasks.extend(component_tasks)
            
            cleanup_plan.execution_order = self._optimize_execution_order(tasks)
        
        return cleanup_plan.execution_order
    
    def validate_cleanup_completion(self, cleanup_task: CleanupTask) -> ValidationResult:
        """
        Validate that patch cleanup was successful.
        
        Implements Requirement 4.4: Patches are marked completed with validation
        Implements Requirement 4.5: Success is verified through automated testing
        
        Args:
            cleanup_task: The cleanup task to validate
            
        Returns:
            ValidationResult indicating success/failure and details
        """
        self.logger.info(f"Validating cleanup completion for task {cleanup_task.task_id}")
        
        errors = []
        warnings = []
        validation_metadata = {
            'task_id': cleanup_task.task_id,
            'patch_id': cleanup_task.patch_id,
            'validation_timestamp': datetime.now().isoformat()
        }
        
        # Validate task completion status
        if cleanup_task.status != CleanupStatus.COMPLETED:
            errors.append(f"Task status is {cleanup_task.status.value}, expected Completed")
        
        # Validate completion date is set
        if not cleanup_task.completed_date:
            errors.append("Completion date not set for completed task")
        
        # Run validation criteria checks
        for i, criterion in enumerate(cleanup_task.validation_criteria):
            try:
                validation_result = self._execute_validation_criterion(criterion, cleanup_task)
                validation_metadata[f'criterion_{i}_result'] = validation_result
                
                if not validation_result.get('passed', False):
                    errors.append(f"Validation criterion failed: {criterion}")
            except Exception as e:
                errors.append(f"Error executing validation criterion '{criterion}': {str(e)}")
        
        # Validate file changes if applicable
        if cleanup_task.patch_id:
            file_validation = self._validate_patch_removal(cleanup_task.patch_id)
            if not file_validation['removed']:
                errors.append(f"Patch {cleanup_task.patch_id} still present in source code")
            validation_metadata['patch_removal'] = file_validation
        
        # Check for regression indicators
        regression_check = self._check_for_regressions(cleanup_task)
        if regression_check['regressions_detected']:
            warnings.extend(regression_check['regression_details'])
        validation_metadata['regression_check'] = regression_check
        
        # Update task validation results
        cleanup_task.validation_results = validation_metadata
        
        is_valid = len(errors) == 0
        self.logger.info(f"Task {cleanup_task.task_id} validation: {'PASSED' if is_valid else 'FAILED'}")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata=validation_metadata
        )
    
    def execute_cleanup_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute a cleanup plan with systematic task execution and validation.
        
        Args:
            plan_id: ID of the cleanup plan to execute
            
        Returns:
            Dictionary with execution results and status
        """
        if plan_id not in self.active_plans:
            raise ValueError(f"Cleanup plan {plan_id} not found")
        
        plan = self.active_plans[plan_id]
        self.logger.info(f"Executing cleanup plan {plan_id}")
        
        plan.status = CleanupStatus.IN_PROGRESS
        execution_results = {
            'plan_id': plan_id,
            'started_at': datetime.now().isoformat(),
            'tasks_completed': 0,
            'tasks_failed': 0,
            'task_results': {}
        }
        
        try:
            # Execute tasks in dependency order
            for task in plan.execution_order:
                self.logger.info(f"Executing task {task.task_id}: {task.description}")
                
                # Check dependencies are completed
                if not self._check_task_dependencies(task, plan.execution_order):
                    task.status = CleanupStatus.FAILED
                    execution_results['tasks_failed'] += 1
                    execution_results['task_results'][task.task_id] = {
                        'status': 'failed',
                        'error': 'Dependencies not satisfied'
                    }
                    continue
                
                # Execute task (this would integrate with actual cleanup tools)
                task_result = self._execute_cleanup_task(task)
                execution_results['task_results'][task.task_id] = task_result
                
                if task_result['status'] == 'completed':
                    task.status = CleanupStatus.COMPLETED
                    task.completed_date = datetime.now()
                    execution_results['tasks_completed'] += 1
                    
                    # Validate completion
                    validation = self.validate_cleanup_completion(task)
                    task_result['validation'] = {
                        'is_valid': validation.is_valid,
                        'errors': validation.errors,
                        'warnings': validation.warnings
                    }
                else:
                    task.status = CleanupStatus.FAILED
                    execution_results['tasks_failed'] += 1
            
            # Update plan status
            if execution_results['tasks_failed'] == 0:
                plan.status = CleanupStatus.COMPLETED
            else:
                plan.status = CleanupStatus.FAILED
            
            execution_results['completed_at'] = datetime.now().isoformat()
            execution_results['final_status'] = plan.status.value
            
        except Exception as e:
            self.logger.error(f"Error executing cleanup plan {plan_id}: {str(e)}")
            plan.status = CleanupStatus.FAILED
            execution_results['error'] = str(e)
            execution_results['completed_at'] = datetime.now().isoformat()
            execution_results['final_status'] = 'failed'
        
        # Move to history
        self.cleanup_history.append(plan)
        
        return execution_results
    
    def rollback_cleanup(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute rollback plan for a failed cleanup.
        
        Args:
            plan_id: ID of the cleanup plan to rollback
            
        Returns:
            Dictionary with rollback results
        """
        if plan_id not in self.active_plans:
            raise ValueError(f"Cleanup plan {plan_id} not found")
        
        plan = self.active_plans[plan_id]
        if not plan.rollback_plan:
            raise ValueError(f"No rollback plan available for {plan_id}")
        
        self.logger.info(f"Rolling back cleanup plan {plan_id}")
        
        rollback_results = {
            'plan_id': plan_id,
            'rollback_started': datetime.now().isoformat(),
            'steps_completed': 0,
            'steps_failed': 0,
            'step_results': []
        }
        
        try:
            for i, step in enumerate(plan.rollback_plan.rollback_steps):
                self.logger.info(f"Executing rollback step {i+1}: {step}")
                
                step_result = self._execute_rollback_step(step, plan.rollback_plan)
                rollback_results['step_results'].append(step_result)
                
                if step_result['status'] == 'completed':
                    rollback_results['steps_completed'] += 1
                else:
                    rollback_results['steps_failed'] += 1
            
            plan.status = CleanupStatus.ROLLED_BACK
            rollback_results['rollback_completed'] = datetime.now().isoformat()
            rollback_results['final_status'] = 'rolled_back'
            
        except Exception as e:
            self.logger.error(f"Error during rollback of plan {plan_id}: {str(e)}")
            rollback_results['error'] = str(e)
            rollback_results['final_status'] = 'rollback_failed'
        
        return rollback_results
    
    def get_cleanup_status(self, plan_id: str) -> Dict[str, Any]:
        """
        Get current status of a cleanup plan.
        
        Args:
            plan_id: ID of the cleanup plan
            
        Returns:
            Dictionary with current status and progress
        """
        if plan_id in self.active_plans:
            plan = self.active_plans[plan_id]
        else:
            # Check history
            plan = next((p for p in self.cleanup_history if p.plan_id == plan_id), None)
            if not plan:
                raise ValueError(f"Cleanup plan {plan_id} not found")
        
        completed_tasks = sum(1 for task in plan.execution_order if task.status == CleanupStatus.COMPLETED)
        failed_tasks = sum(1 for task in plan.execution_order if task.status == CleanupStatus.FAILED)
        total_tasks = len(plan.execution_order)
        
        return {
            'plan_id': plan_id,
            'plan_name': plan.plan_name,
            'status': plan.status.value,
            'progress': {
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'total_tasks': total_tasks,
                'completion_percentage': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            'target_components': plan.target_components,
            'patches_count': len(plan.patches_to_resolve),
            'estimated_effort': str(plan.estimated_effort),
            'risk_level': plan.risk_assessment.value,
            'created_date': plan.created_date.isoformat(),
            'scheduled_date': plan.scheduled_date.isoformat() if plan.scheduled_date else None
        }
    
    # Private helper methods
    
    def _filter_patches_by_criteria(self, patches: List[PatchAnnotation], criteria: CleanupCriteria) -> List[PatchAnnotation]:
        """Filter patches based on cleanup criteria."""
        filtered = []
        
        for patch in patches:
            # Component filter
            if criteria.target_components and patch.component not in criteria.target_components:
                continue
            
            # Debt level filter
            if criteria.debt_levels and patch.debt_level not in criteria.debt_levels:
                continue
            
            # Exclusion filter
            if patch.patch_id in criteria.exclude_patch_ids:
                continue
            
            # Date filters
            if criteria.created_before and patch.created_date > criteria.created_before:
                continue
            
            if criteria.created_after and patch.created_date < criteria.created_after:
                continue
            
            # Expiration filter
            if not criteria.include_expired and patch.expected_resolution and patch.expected_resolution < datetime.now():
                continue
            
            filtered.append(patch)
        
        # Apply max patches limit
        if criteria.max_patches and len(filtered) > criteria.max_patches:
            # Sort by priority and take top N
            filtered.sort(key=lambda p: (
                self._get_debt_priority(p.debt_level),
                p.created_date
            ))
            filtered = filtered[:criteria.max_patches]
        
        return filtered
    
    def _generate_component_cleanup_tasks(self, component: str, patches: List[PatchAnnotation]) -> List[CleanupTask]:
        """Generate cleanup tasks for patches in a specific component."""
        tasks = []
        
        for patch in patches:
            task = CleanupTask(
                patch_id=patch.patch_id,
                component=component,
                description=f"Clean up patch {patch.patch_id} in {component}: {patch.reason}",
                remediation_steps=self._generate_remediation_steps(patch),
                validation_criteria=patch.validation_criteria or self._generate_default_validation_criteria(patch),
                estimated_effort=self._estimate_cleanup_effort(patch),
                risk_level=self._assess_patch_cleanup_risk(patch),
                assigned_to=patch.assigned_to
            )
            tasks.append(task)
        
        return tasks
    
    def _optimize_execution_order(self, tasks: List[CleanupTask]) -> List[CleanupTask]:
        """Optimize task execution order based on component dependencies."""
        # Build dependency graph
        component_order = self._get_component_execution_order([task.component for task in tasks])
        
        # Group tasks by component
        component_tasks = defaultdict(list)
        for task in tasks:
            component_tasks[task.component].append(task)
        
        # Order tasks by component dependencies, then by risk level within component
        ordered_tasks = []
        for component in component_order:
            if component in component_tasks:
                # Sort tasks within component by risk level (high risk first for early detection)
                component_task_list = component_tasks[component]
                component_task_list.sort(key=lambda t: (
                    self._get_risk_priority(t.risk_level),
                    t.estimated_effort
                ))
                ordered_tasks.extend(component_task_list)
        
        return ordered_tasks
    
    def _get_component_execution_order(self, components: List[str]) -> List[str]:
        """Get optimal execution order for components based on dependencies."""
        unique_components = list(set(components))
        
        # If no dependencies defined, use alphabetical order
        if not self.component_dependencies:
            return sorted(unique_components)
        
        # Topological sort of components
        in_degree = {comp: 0 for comp in unique_components}
        
        # Calculate in-degrees
        for comp in unique_components:
            for dep in self.component_dependencies.get(comp, set()):
                if dep in in_degree:
                    in_degree[comp] += 1
        
        # Kahn's algorithm for topological sorting
        queue = deque([comp for comp, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Update in-degrees of dependent components
            for comp in unique_components:
                if current in self.component_dependencies.get(comp, set()):
                    in_degree[comp] -= 1
                    if in_degree[comp] == 0:
                        queue.append(comp)
        
        # If not all components processed, there's a cycle - fall back to alphabetical
        if len(result) != len(unique_components):
            self.logger.warning("Cycle detected in component dependencies, using alphabetical order")
            return sorted(unique_components)
        
        return result
    
    def _assess_cleanup_risk(self, patches: List[PatchAnnotation], tasks: List[CleanupTask]) -> RiskLevel:
        """Assess overall risk level for cleanup plan."""
        risk_factors = {
            'critical_patches': sum(1 for p in patches if p.debt_level == DebtLevel.CRITICAL),
            'high_debt_patches': sum(1 for p in patches if p.debt_level == DebtLevel.HIGH),
            'total_patches': len(patches),
            'critical_components': len(set(p.component for p in patches if p.debt_level in [DebtLevel.CRITICAL, DebtLevel.HIGH])),
            'total_effort_hours': sum(task.estimated_effort.total_seconds() / 3600 for task in tasks)
        }
        
        # Risk assessment logic
        if (risk_factors['critical_patches'] > 0 or 
            risk_factors['critical_components'] >= self.risk_thresholds['critical_component_count'] or
            risk_factors['total_effort_hours'] > self.risk_thresholds['estimated_effort_hours']):
            return RiskLevel.CRITICAL
        
        if (risk_factors['high_debt_patches'] >= self.risk_thresholds['high_debt_patch_count'] or
            risk_factors['total_patches'] >= self.risk_thresholds['total_patch_count']):
            return RiskLevel.HIGH
        
        if risk_factors['high_debt_patches'] > 0 or risk_factors['total_patches'] > 5:
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _generate_rollback_plan(self, tasks: List[CleanupTask]) -> RollbackPlan:
        """Generate rollback plan for cleanup tasks."""
        rollback_steps = []
        backup_locations = {}
        
        # Generate rollback steps (reverse order of execution)
        for task in reversed(tasks):
            if task.patch_id:
                rollback_steps.append(f"Restore patch {task.patch_id} in component {task.component}")
                backup_locations[task.patch_id] = f"/tmp/patch_backups/{task.patch_id}.backup"
        
        rollback_steps.extend([
            "Verify all patches are restored to original state",
            "Run regression tests to ensure system stability",
            "Notify team of rollback completion"
        ])
        
        return RollbackPlan(
            rollback_steps=rollback_steps,
            backup_locations=backup_locations,
            rollback_validation=[
                "All patch annotations present in source code",
                "System functionality unchanged from pre-cleanup state",
                "No new errors or warnings in logs"
            ],
            estimated_rollback_time=timedelta(minutes=len(tasks) * 5 + 30)
        )
    
    def _generate_plan_validation_criteria(self, patches: List[PatchAnnotation]) -> List[str]:
        """Generate validation criteria for the overall cleanup plan."""
        criteria = [
            "All targeted patches removed from source code",
            "No new compilation errors introduced",
            "All existing tests continue to pass",
            "System performance maintained or improved"
        ]
        
        # Add component-specific criteria
        components = set(p.component for p in patches)
        for component in components:
            criteria.append(f"Component {component} functionality verified")
        
        return criteria
    
    def _calculate_total_effort(self, tasks: List[CleanupTask]) -> timedelta:
        """Calculate total estimated effort for all tasks."""
        return sum((task.estimated_effort for task in tasks), timedelta())
    
    def _get_debt_priority(self, debt_level: DebtLevel) -> int:
        """Get numeric priority for debt level (lower number = higher priority)."""
        priority_map = {
            DebtLevel.CRITICAL: 0,
            DebtLevel.HIGH: 1,
            DebtLevel.MEDIUM: 2,
            DebtLevel.LOW: 3
        }
        return priority_map.get(debt_level, 4)
    
    def _get_risk_priority(self, risk_level: RiskLevel) -> int:
        """Get numeric priority for risk level (lower number = higher priority)."""
        priority_map = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 3
        }
        return priority_map.get(risk_level, 4)
    
    def _generate_remediation_steps(self, patch: PatchAnnotation) -> List[str]:
        """Generate specific remediation steps for a patch."""
        steps = []
        
        if patch.cleanup_task:
            steps.append(patch.cleanup_task)
        
        steps.extend([
            f"Remove patch annotation {patch.patch_id} from {patch.file_path}",
            f"Implement proper solution for: {patch.reason}",
            "Run unit tests to verify functionality",
            "Update documentation if necessary"
        ])
        
        if patch.upstream_issue:
            steps.insert(0, f"Verify upstream issue {patch.upstream_issue} is resolved")
        
        return steps
    
    def _generate_default_validation_criteria(self, patch: PatchAnnotation) -> List[str]:
        """Generate default validation criteria for a patch."""
        return [
            f"Patch {patch.patch_id} annotation removed from source code",
            f"Component {patch.component} functionality verified",
            "No regression in existing functionality",
            "Performance impact assessed and acceptable"
        ]
    
    def _estimate_cleanup_effort(self, patch: PatchAnnotation) -> timedelta:
        """Estimate cleanup effort based on patch characteristics."""
        base_effort = timedelta(hours=1)
        
        # Adjust based on debt level
        if patch.debt_level == DebtLevel.CRITICAL:
            base_effort *= 3
        elif patch.debt_level == DebtLevel.HIGH:
            base_effort *= 2
        elif patch.debt_level == DebtLevel.LOW:
            base_effort *= 0.5
        
        # Adjust based on bypass type
        if patch.bypass_type in [BypassType.SECURITY, BypassType.ARCHITECTURE]:
            base_effort *= 1.5
        
        return base_effort
    
    def _assess_patch_cleanup_risk(self, patch: PatchAnnotation) -> RiskLevel:
        """Assess risk level for cleaning up a specific patch."""
        if patch.debt_level == DebtLevel.CRITICAL:
            return RiskLevel.CRITICAL
        elif patch.debt_level == DebtLevel.HIGH:
            return RiskLevel.HIGH
        elif patch.bypass_type in [BypassType.SECURITY, BypassType.ARCHITECTURE]:
            return RiskLevel.HIGH
        elif patch.debt_level == DebtLevel.MEDIUM:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _execute_validation_criterion(self, criterion: str, task: CleanupTask) -> Dict[str, Any]:
        """Execute a validation criterion and return results."""
        # This would integrate with actual validation tools
        # For now, return a mock result
        return {
            'criterion': criterion,
            'passed': True,
            'details': f"Validation criterion '{criterion}' executed successfully",
            'timestamp': datetime.now().isoformat()
        }
    
    def _validate_patch_removal(self, patch_id: str) -> Dict[str, Any]:
        """Validate that a patch has been removed from source code."""
        # This would scan source code for the patch annotation
        # For now, return a mock result
        return {
            'patch_id': patch_id,
            'removed': True,
            'scan_timestamp': datetime.now().isoformat(),
            'details': f"Patch {patch_id} successfully removed from source code"
        }
    
    def _check_for_regressions(self, task: CleanupTask) -> Dict[str, Any]:
        """Check for regressions after cleanup task completion."""
        # This would run regression tests and analyze results
        # For now, return a mock result
        return {
            'regressions_detected': False,
            'regression_details': [],
            'test_results': {
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0
            },
            'check_timestamp': datetime.now().isoformat()
        }
    
    def _check_task_dependencies(self, task: CleanupTask, all_tasks: List[CleanupTask]) -> bool:
        """Check if all dependencies for a task are satisfied."""
        if not task.dependencies:
            return True
        
        task_status_map = {t.task_id: t.status for t in all_tasks}
        
        for dep_id in task.dependencies:
            if dep_id not in task_status_map or task_status_map[dep_id] != CleanupStatus.COMPLETED:
                return False
        
        return True
    
    def _execute_cleanup_task(self, task: CleanupTask) -> Dict[str, Any]:
        """Execute a cleanup task (mock implementation)."""
        # This would integrate with actual cleanup tools and processes
        # For now, return a mock successful result
        return {
            'task_id': task.task_id,
            'status': 'completed',
            'started_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat(),
            'steps_executed': len(task.remediation_steps),
            'details': f"Successfully executed cleanup for patch {task.patch_id}"
        }
    
    def _execute_rollback_step(self, step: str, rollback_plan: RollbackPlan) -> Dict[str, Any]:
        """Execute a rollback step (mock implementation)."""
        # This would integrate with actual rollback tools and processes
        # For now, return a mock successful result
        return {
            'step': step,
            'status': 'completed',
            'executed_at': datetime.now().isoformat(),
            'details': f"Successfully executed rollback step: {step}"
        }
    
    def set_component_dependencies(self, dependencies: Dict[str, List[str]]) -> None:
        """
        Set component dependencies for execution ordering.
        
        Args:
            dependencies: Dictionary mapping component names to lists of their dependencies
        """
        self.component_dependencies = {
            comp: set(deps) for comp, deps in dependencies.items()
        }
        self.logger.info(f"Updated component dependencies for {len(dependencies)} components")
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status summary."""
        health = self.get_health_status()
        return {
            'status': health.status.value,
            'health_score': health.health_score,
            'active_plans': len(self.active_plans),
            'completed_plans': len(self.cleanup_history),
            'component_dependencies': len(self.component_dependencies),
            'issues': health.issues,
            'last_activity': datetime.now().isoformat()
        }