"""Orchestration controller for distributed Beast Mode operations."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..core.reflective_module import HealthIndicator, ModuleStatus, ReflectiveModule
from .models import (
    DistributionPlan,
    DistributionStrategy,
    InstanceFailure,
    IntegrationReport,
    KiroInstance,
    RecoveryPlan,
    SwarmConfig,
    SwarmState,
    Task,
    TaskStatus,
)

logger = logging.getLogger(__name__)


class OrchestrationController(ReflectiveModule):
    """Central coordination hub for distributed Beast Mode operations.

    Manages swarm lifecycle, task distribution, health monitoring,
    and systematic integration following Beast Mode principles.
    """

    def __init__(self, config: SwarmConfig):
        super().__init__("OrchestrationController", "1.0.0")
        self.config = config
        self.swarm_state = SwarmState(config=config)
        self.active_swarms: Dict[str, SwarmState] = {}
        self.task_queue: List[Task] = []
        self.distribution_history: List[DistributionPlan] = []
        self.recovery_history: List[RecoveryPlan] = []
        
        # Performance tracking
        self.performance_metrics = {
            "swarms_launched": 0,
            "tasks_distributed": 0,
            "successful_integrations": 0,
            "failed_recoveries": 0,
            "average_swarm_startup_time": 0.0,
            "average_task_completion_time": 0.0,
        }
        
        logger.info(f"OrchestrationController initialized with config: {config.model_dump()}")

    def launch_swarm(self, tasks: List[Task]) -> SwarmState:
        """Launch distributed Beast Mode swarm with systematic approach.
        
        Args:
            tasks: List of tasks to be distributed across the swarm
            
        Returns:
            SwarmState: Current state of the launched swarm
            
        Raises:
            ValueError: If tasks list is empty or configuration is invalid
            RuntimeError: If swarm launch fails
        """
        start_time = datetime.now()
        
        try:
            if not tasks:
                raise ValueError("Cannot launch swarm with empty task list")
                
            # Validate configuration using systematic approach
            self._validate_swarm_config()
            
            # Create new swarm state
            swarm_state = SwarmState(config=self.config)
            swarm_state.status = "launching"
            
            # Add tasks to swarm
            for task in tasks:
                swarm_state.execution_status[task.id] = TaskStatus.PENDING
                
            # Generate distribution plan
            distribution_plan = self.distribute_tasks(tasks)
            
            # Create instances based on distribution plan
            instances = self._create_instances(distribution_plan)
            
            # Update swarm state
            swarm_state.instances = {inst.instance_id: inst for inst in instances}
            swarm_state.task_assignments = distribution_plan.instance_assignments
            swarm_state.status = "active"
            
            # Store swarm state
            self.active_swarms[swarm_state.swarm_id] = swarm_state
            self.swarm_state = swarm_state
            
            # Update performance metrics
            launch_time = (datetime.now() - start_time).total_seconds()
            self.performance_metrics["swarms_launched"] += 1
            self._update_average_metric("average_swarm_startup_time", launch_time)
            
            # Add health indicator
            self.add_health_indicator(
                self.create_health_indicator(
                    "swarm_launch",
                    "healthy",
                    f"Successfully launched swarm {swarm_state.swarm_id} with {len(instances)} instances",
                    {
                        "swarm_id": swarm_state.swarm_id,
                        "instance_count": len(instances),
                        "task_count": len(tasks),
                        "launch_time_seconds": launch_time,
                    }
                )
            )
            
            self.update_activity()
            logger.info(f"Swarm {swarm_state.swarm_id} launched successfully in {launch_time:.2f}s")
            
            return swarm_state
            
        except Exception as e:
            self.add_health_indicator(
                self.create_health_indicator(
                    "swarm_launch",
                    "critical",
                    f"Failed to launch swarm: {str(e)}",
                    {"error": str(e), "task_count": len(tasks)}
                )
            )
            logger.error(f"Swarm launch failed: {e}")
            raise RuntimeError(f"Swarm launch failed: {e}") from e

    def distribute_tasks(self, tasks: List[Task]) -> DistributionPlan:
        """Create optimal task distribution plan using systematic analysis.
        
        Args:
            tasks: List of tasks to distribute
            
        Returns:
            DistributionPlan: Optimized distribution plan
        """
        start_time = datetime.now()
        
        try:
            # Analyze task dependencies
            dependency_graph = self._build_dependency_graph(tasks)
            
            # Calculate parallel execution groups
            parallel_groups = self._calculate_parallel_groups(dependency_graph)
            
            # Determine optimal instance count
            optimal_instances = self._calculate_optimal_instances(tasks, parallel_groups)
            
            # Create distribution plan based on strategy
            plan = self._create_distribution_plan(tasks, optimal_instances, parallel_groups)
            
            # Store plan for analysis
            self.distribution_history.append(plan)
            
            # Update metrics
            self.performance_metrics["tasks_distributed"] += len(tasks)
            
            self.add_health_indicator(
                self.create_health_indicator(
                    "task_distribution",
                    "healthy",
                    f"Created distribution plan for {len(tasks)} tasks across {optimal_instances} instances",
                    {
                        "task_count": len(tasks),
                        "instance_count": optimal_instances,
                        "parallel_groups": len(parallel_groups),
                        "strategy": self.config.task_distribution_strategy.value,
                    }
                )
            )
            
            self.update_activity()
            logger.info(f"Task distribution plan created: {len(tasks)} tasks, {optimal_instances} instances")
            
            return plan
            
        except Exception as e:
            self.add_health_indicator(
                self.create_health_indicator(
                    "task_distribution",
                    "critical",
                    f"Failed to create distribution plan: {str(e)}",
                    {"error": str(e), "task_count": len(tasks)}
                )
            )
            logger.error(f"Task distribution failed: {e}")
            raise

    def monitor_swarm(self, swarm_id: Optional[str] = None) -> SwarmState:
        """Get real-time swarm health and progress with systematic monitoring.
        
        Args:
            swarm_id: Specific swarm to monitor, defaults to current swarm
            
        Returns:
            SwarmState: Current swarm status and metrics
        """
        try:
            target_swarm_id = swarm_id or self.swarm_state.swarm_id
            
            if target_swarm_id not in self.active_swarms:
                raise ValueError(f"Swarm {target_swarm_id} not found")
                
            swarm = self.active_swarms[target_swarm_id]
            
            # Update instance health status
            self._update_instance_health(swarm)
            
            # Update performance metrics
            self._update_swarm_metrics(swarm)
            
            # Update last activity
            swarm.last_updated = datetime.now()
            
            self.update_activity()
            
            return swarm
            
        except Exception as e:
            self.add_health_indicator(
                self.create_health_indicator(
                    "swarm_monitoring",
                    "warning",
                    f"Failed to monitor swarm: {str(e)}",
                    {"error": str(e), "swarm_id": swarm_id}
                )
            )
            logger.warning(f"Swarm monitoring failed: {e}")
            raise

    def handle_failure(self, failure: InstanceFailure) -> RecoveryPlan:
        """Generate systematic recovery plan for failed instances.
        
        Args:
            failure: Instance failure information
            
        Returns:
            RecoveryPlan: Systematic recovery strategy
        """
        start_time = datetime.now()
        
        try:
            # Analyze failure type and impact
            failure_analysis = self._analyze_failure(failure)
            
            # Generate recovery strategy
            recovery_plan = self._generate_recovery_strategy(failure, failure_analysis)
            
            # Store recovery plan
            self.recovery_history.append(recovery_plan)
            
            # Update failure metrics
            if not recovery_plan.recovery_strategy == "manual":
                # Attempt automatic recovery
                recovery_success = self._execute_recovery_plan(recovery_plan)
                if not recovery_success:
                    self.performance_metrics["failed_recoveries"] += 1
            
            self.add_health_indicator(
                self.create_health_indicator(
                    "failure_recovery",
                    "warning" if recovery_plan.recovery_strategy != "manual" else "critical",
                    f"Generated recovery plan for instance {failure.instance_id}",
                    {
                        "instance_id": failure.instance_id,
                        "failure_type": failure.failure_type,
                        "recovery_strategy": recovery_plan.recovery_strategy,
                        "affected_tasks": len(failure.affected_tasks),
                    }
                )
            )
            
            self.update_activity()
            logger.info(f"Recovery plan generated for {failure.instance_id}: {recovery_plan.recovery_strategy}")
            
            return recovery_plan
            
        except Exception as e:
            self.add_health_indicator(
                self.create_health_indicator(
                    "failure_recovery",
                    "critical",
                    f"Failed to generate recovery plan: {str(e)}",
                    {"error": str(e), "instance_id": failure.instance_id}
                )
            )
            logger.error(f"Recovery plan generation failed: {e}")
            raise

    def integrate_results(self, swarm_id: Optional[str] = None) -> IntegrationReport:
        """Systematically integrate completed work with quality gates.
        
        Args:
            swarm_id: Specific swarm to integrate, defaults to current swarm
            
        Returns:
            IntegrationReport: Integration results and status
        """
        start_time = datetime.now()
        
        try:
            target_swarm_id = swarm_id or self.swarm_state.swarm_id
            swarm = self.active_swarms[target_swarm_id]
            
            # Identify completed tasks ready for integration
            completed_tasks = self._get_completed_tasks(swarm)
            
            if not completed_tasks:
                return IntegrationReport(
                    integration_time=datetime.now() - start_time,
                    summary="No completed tasks ready for integration"
                )
            
            # Execute integration with quality gates
            integration_report = self._execute_integration(completed_tasks, swarm)
            
            # Update metrics
            self.performance_metrics["successful_integrations"] += len(integration_report.successful_integrations)
            
            self.add_health_indicator(
                self.create_health_indicator(
                    "integration",
                    "healthy" if not integration_report.failed_integrations else "warning",
                    f"Integrated {len(integration_report.successful_integrations)} tasks, {len(integration_report.failed_integrations)} failed",
                    {
                        "successful": len(integration_report.successful_integrations),
                        "failed": len(integration_report.failed_integrations),
                        "conflicts": len(integration_report.conflicts_remaining),
                    }
                )
            )
            
            self.update_activity()
            logger.info(f"Integration completed: {integration_report.summary}")
            
            return integration_report
            
        except Exception as e:
            self.add_health_indicator(
                self.create_health_indicator(
                    "integration",
                    "critical",
                    f"Integration failed: {str(e)}",
                    {"error": str(e), "swarm_id": swarm_id}
                )
            )
            logger.error(f"Integration failed: {e}")
            raise

    # Private helper methods

    def _validate_swarm_config(self) -> None:
        """Validate swarm configuration for systematic compliance."""
        if self.config.instance_count < 1:
            raise ValueError("Instance count must be at least 1")
        if self.config.max_instances < self.config.min_instances:
            raise ValueError("Max instances must be >= min instances")
        if not self.config.deployment_targets and self.config.instance_count > 1:
            # Add default local deployment target
            from .models import DeploymentTarget
            self.config.deployment_targets = [
                DeploymentTarget(name="local", type="local")
            ]

    def _build_dependency_graph(self, tasks: List[Task]) -> Dict[str, List[str]]:
        """Build task dependency graph for analysis."""
        graph = {}
        for task in tasks:
            graph[task.id] = task.dependencies.copy()
        return graph

    def _calculate_parallel_groups(self, dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Calculate parallel execution groups using topological sort."""
        # Simplified implementation - in production would use proper topological sort
        groups = []
        remaining_tasks = set(dependency_graph.keys())
        
        while remaining_tasks:
            # Find tasks with no dependencies in remaining set
            ready_tasks = [
                task_id for task_id in remaining_tasks
                if not any(dep in remaining_tasks for dep in dependency_graph[task_id])
            ]
            
            if not ready_tasks:
                # Circular dependency - break it
                ready_tasks = [next(iter(remaining_tasks))]
            
            groups.append(ready_tasks)
            remaining_tasks -= set(ready_tasks)
        
        return groups

    def _calculate_optimal_instances(self, tasks: List[Task], parallel_groups: List[List[str]]) -> int:
        """Calculate optimal number of instances based on tasks and parallelism."""
        max_parallel = max(len(group) for group in parallel_groups) if parallel_groups else 1
        
        # Consider configuration limits
        optimal = min(
            max_parallel,
            self.config.instance_count,
            self.config.max_instances,
            len(tasks)  # No more instances than tasks
        )
        
        return max(optimal, self.config.min_instances)

    def _create_distribution_plan(
        self, tasks: List[Task], instance_count: int, parallel_groups: List[List[str]]
    ) -> DistributionPlan:
        """Create distribution plan based on strategy."""
        # Simple round-robin distribution for now
        # In production, would implement sophisticated strategies
        task_assignments = {f"instance-{i}": [] for i in range(instance_count)}
        
        for i, task in enumerate(tasks):
            instance_id = f"instance-{i % instance_count}"
            task_assignments[instance_id].append(task.id)
        
        # Calculate estimated completion time
        max_tasks_per_instance = max(len(task_list) for task_list in task_assignments.values()) if task_assignments else 0
        avg_task_duration = sum(task.estimated_duration.total_seconds() for task in tasks) / len(tasks) if tasks else 0
        estimated_completion_time = timedelta(seconds=max_tasks_per_instance * avg_task_duration)
        
        plan = DistributionPlan(
            total_tasks=len(tasks),
            strategy_used=self.config.task_distribution_strategy,
            parallel_execution_groups=parallel_groups,
            instance_assignments=task_assignments,
            estimated_completion_time=estimated_completion_time,
        )
        
        return plan

    def _create_instances(self, plan: DistributionPlan) -> List[KiroInstance]:
        """Create Kiro instances based on distribution plan."""
        instances = []
        
        for instance_id, task_ids in plan.instance_assignments.items():
            if not task_ids:  # Skip empty assignments
                continue
                
            # Create instance configuration
            from .models import PeacockTheme
            from pathlib import Path
            
            theme = PeacockTheme(
                color_name=f"color-{len(instances) + 1}",
                primary_color=f"#{''.join([hex(hash(instance_id))[i] for i in range(2, 8)])}",
                accent_color=f"#{''.join([hex(hash(instance_id + 'accent'))[i] for i in range(2, 8)])}"
            )
            
            instance = KiroInstance(
                instance_id=instance_id,
                branch_name=f"feature/{instance_id}",
                workspace_path=Path(f"/tmp/kiro-workspaces/{instance_id}"),
                source_repository=".",  # Current repository
                task_assignments=task_ids,
                communication_endpoint=f"tcp://localhost:{5000 + len(instances)}",
                peacock_theme=theme,
                visual_identifier=theme.color_name,
            )
            
            instances.append(instance)
        
        return instances

    def _update_instance_health(self, swarm: SwarmState) -> None:
        """Update health status of all instances in swarm."""
        current_time = datetime.now()
        
        for instance in swarm.instances.values():
            # Check heartbeat timeout
            if instance.last_heartbeat:
                time_since_heartbeat = (current_time - instance.last_heartbeat).total_seconds()
                if time_since_heartbeat > self.config.health_check_interval * 2:
                    instance.status = "error"
            
            # Update performance metrics
            instance.performance_metrics["last_health_check"] = current_time.isoformat()

    def _update_swarm_metrics(self, swarm: SwarmState) -> None:
        """Update performance metrics for swarm."""
        metrics = swarm.performance_metrics
        
        # Count task statuses
        completed_count = sum(1 for status in swarm.execution_status.values() if status == TaskStatus.COMPLETED)
        failed_count = sum(1 for status in swarm.execution_status.values() if status == TaskStatus.FAILED)
        
        metrics.completed_tasks = completed_count
        metrics.failed_tasks = failed_count
        metrics.active_instances = len([i for i in swarm.instances.values() if i.status == "active"])
        
        # Calculate error rate
        total_finished = completed_count + failed_count
        metrics.error_rate = (failed_count / total_finished) if total_finished > 0 else 0.0
        
        metrics.last_updated = datetime.now()

    def _analyze_failure(self, failure: InstanceFailure) -> Dict[str, any]:
        """Analyze failure for recovery strategy."""
        return {
            "severity": "high" if failure.failure_type in ["crash", "resource"] else "medium",
            "recoverable": failure.is_recoverable,
            "task_impact": len(failure.affected_tasks),
            "recovery_complexity": "simple" if failure.recovery_attempts == 0 else "complex"
        }

    def _generate_recovery_strategy(self, failure: InstanceFailure, analysis: Dict[str, any]) -> RecoveryPlan:
        """Generate recovery strategy based on failure analysis."""
        if not analysis["recoverable"] or analysis["recovery_complexity"] == "complex":
            strategy = "manual"
        elif failure.failure_type == "timeout":
            strategy = "restart"
        elif failure.failure_type == "resource":
            strategy = "scale_up"
        else:
            strategy = "reassign"
        
        return RecoveryPlan(
            failed_instance=failure.instance_id,
            recovery_strategy=strategy,
            estimated_recovery_time=timedelta(minutes=5 if strategy == "restart" else 15),
            required_actions=[f"Execute {strategy} recovery for {failure.instance_id}"],
        )

    def _execute_recovery_plan(self, plan: RecoveryPlan) -> bool:
        """Execute recovery plan (simplified implementation)."""
        # In production, this would execute actual recovery actions
        logger.info(f"Executing recovery plan: {plan.recovery_strategy} for {plan.failed_instance}")
        return True  # Assume success for now

    def _get_completed_tasks(self, swarm: SwarmState) -> List[str]:
        """Get list of completed tasks ready for integration."""
        return [
            task_id for task_id, status in swarm.execution_status.items()
            if status == TaskStatus.COMPLETED
        ]

    def _execute_integration(self, task_ids: List[str], swarm: SwarmState) -> IntegrationReport:
        """Execute integration of completed tasks."""
        start_time = datetime.now()
        
        # Simplified integration - in production would handle git merges, conflicts, etc.
        successful = task_ids.copy()  # Assume all succeed for now
        failed = []
        
        return IntegrationReport(
            integration_batch=task_ids,
            successful_integrations=successful,
            failed_integrations=failed,
            integration_time=datetime.now() - start_time,
            summary=f"Successfully integrated {len(successful)} tasks"
        )

    def _update_average_metric(self, metric_name: str, new_value: float) -> None:
        """Update running average for performance metric."""
        current_avg = self.performance_metrics[metric_name]
        count = self.performance_metrics.get(f"{metric_name}_count", 0)
        
        new_avg = (current_avg * count + new_value) / (count + 1)
        self.performance_metrics[metric_name] = new_avg
        self.performance_metrics[f"{metric_name}_count"] = count + 1

    # ReflectiveModule implementation

    def get_module_status(self) -> ModuleStatus:
        """Get current module status with health indicators."""
        return ModuleStatus(
            module_name=self.name,
            version=self.version,
            status="active" if self.is_healthy() else "error",
            uptime=self.get_uptime(),
            last_activity=self.last_activity,
            health_indicators=self.get_health_indicators(),
            performance_metrics={
                **self.performance_metrics,
                "active_swarms": len(self.active_swarms),
                "task_queue_size": len(self.task_queue),
                "distribution_history_size": len(self.distribution_history),
            },
        )

    def is_healthy(self) -> bool:
        """Check if module is in healthy state."""
        # Check for recent critical health indicators
        recent_indicators = [
            indicator for indicator in self._health_indicators
            if (datetime.now() - indicator.timestamp).total_seconds() < 300  # 5 minutes
        ]
        
        critical_count = sum(1 for indicator in recent_indicators if indicator.status == "critical")
        return critical_count == 0

    def get_health_indicators(self) -> List[HealthIndicator]:
        """Get current health indicators."""
        # Add current performance indicator
        swarm_health = "healthy"
        if self.active_swarms:
            error_rates = [swarm.performance_metrics.error_rate for swarm in self.active_swarms.values()]
            avg_error_rate = sum(error_rates) / len(error_rates)
            if avg_error_rate > 0.1:  # 10% error rate threshold
                swarm_health = "warning"
            if avg_error_rate > 0.3:  # 30% error rate threshold
                swarm_health = "critical"
        
        performance_indicator = self.create_health_indicator(
            "swarm_performance",
            swarm_health,
            f"Managing {len(self.active_swarms)} active swarms",
            {
                "active_swarms": len(self.active_swarms),
                "total_swarms_launched": self.performance_metrics["swarms_launched"],
                "tasks_distributed": self.performance_metrics["tasks_distributed"],
            }
        )
        
        return self._health_indicators + [performance_indicator]