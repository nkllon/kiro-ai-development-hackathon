#!/usr/bin/env python3
"""
DAG Orchestrator - Main Coordination Component
=============================================

The main DAG orchestrator that coordinates all existing components to provide
unified DAG-based parallel execution with comprehensive validation and monitoring.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)
from src.rm_ddd.core.dag_registry import DAGRegistry
from src.dag_orchestration.execution.parallel_execution_engine import (
    ParallelExecutionEngine,
    TaskDefinition,
    TaskExecutionResult,
    ExecutionStrategy
)
from src.dag_orchestration.execution.dependency_aware_scheduler import (
    DependencyAwareScheduler,
    SchedulingStrategy,
    SchedulingDecision
)
from src.dag_orchestration.core.infrastructure_validator import (
    InfrastructureValidator,
    ValidationPolicy
)
from src.dag_orchestration.integration.ace_reporter_integration import ACEReporterIntegration
from src.dag_orchestration.integration.ai_memory_palace_integration import AIMemoryPalaceIntegration


class OrchestrationStatus(Enum):
    """DAG orchestration status enumeration."""
    IDLE = "idle"
    VALIDATING = "validating"
    SCHEDULING = "scheduling"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OrchestrationConfig:
    """Configuration for DAG orchestration."""
    max_workers: int = 10
    execution_strategy: ExecutionStrategy = ExecutionStrategy.CONSERVATIVE
    scheduling_strategy: SchedulingStrategy = SchedulingStrategy.ADAPTIVE
    validation_policy: Optional[ValidationPolicy] = None
    enable_prefire_testing: bool = True
    enable_continuous_monitoring: bool = True
    timeout_seconds: Optional[float] = None


@dataclass
class OrchestrationResult:
    """Result of DAG orchestration execution."""
    orchestration_id: str
    status: OrchestrationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    skipped_tasks: int = 0
    task_results: Dict[str, TaskExecutionResult] = field(default_factory=dict)
    validation_report: Optional[Any] = None
    scheduling_decisions: List[SchedulingDecision] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    error_summary: Optional[str] = None


class DAGOrchestrator(ReflectiveModule):
    """
    Main DAG orchestrator that coordinates all components for unified
    DAG-based parallel execution with comprehensive validation and monitoring.
    
    Integrates:
    - DAG Registry for dependency validation
    - Parallel Execution Engine for task execution
    - Dependency Aware Scheduler for intelligent scheduling
    - Infrastructure Validator for prefire testing
    - ReflectiveModule for complete observability
    """
    
    def __init__(self, config: Optional[OrchestrationConfig] = None):
        super().__init__()
        self.module_id = "DAGOrchestrator"
        self._config = config or OrchestrationConfig()
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Initialize core components
        self._dag_registry = DAGRegistry()
        self._parallel_engine = ParallelExecutionEngine(
            max_workers=self._config.max_workers,
            execution_strategy=self._config.execution_strategy
        )
        self._scheduler = DependencyAwareScheduler(
            strategy=self._config.scheduling_strategy
        )
        self._infrastructure_validator = InfrastructureValidator(
            validation_policy=self._config.validation_policy
        )
        
        # Initialize integration components
        self._ace_reporter = ACEReporterIntegration()
        self._ai_memory_palace = AIMemoryPalaceIntegration()
        
        # Orchestration state
        self._current_orchestration: Optional[OrchestrationResult] = None
        self._orchestration_history: List[OrchestrationResult] = []
        self._orchestration_lock = asyncio.Lock()
        
        # Statistics
        self._total_orchestrations = 0
        self._successful_orchestrations = 0
        self._failed_orchestrations = 0
        
        self._logger.info(f"DAGOrchestrator initialized with config: {self._config}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "DAGOrchestrator",
            "version": "1.0.0",
            "description": "Main DAG orchestrator coordinating parallel execution",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "configuration": {
                "max_workers": self._config.max_workers,
                "execution_strategy": self._config.execution_strategy.value,
                "scheduling_strategy": self._config.scheduling_strategy.value,
                "prefire_testing_enabled": self._config.enable_prefire_testing,
                "continuous_monitoring_enabled": self._config.enable_continuous_monitoring
            },
            "component_status": {
                "dag_registry": self._dag_registry.validate_dag(),
                "parallel_engine": self._parallel_engine.get_health_status().status.value,
                "scheduler": self._scheduler.get_health_status().status.value,
                "infrastructure_validator": self._infrastructure_validator.get_health_status().status.value
            },
            "statistics": {
                "total_orchestrations": self._total_orchestrations,
                "successful_orchestrations": self._successful_orchestrations,
                "failed_orchestrations": self._failed_orchestrations,
                "success_rate": self._successful_orchestrations / max(self._total_orchestrations, 1),
                "current_orchestration_active": self._current_orchestration is not None
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            issues = []
            health_score = 1.0
            
            # Check component health
            components = {
                "DAG Registry": self._dag_registry.validate_dag(),
                "Parallel Engine": self._parallel_engine.get_health_status(),
                "Scheduler": self._scheduler.get_health_status(),
                "Infrastructure Validator": self._infrastructure_validator.get_health_status()
            }
            
            for component_name, component_health in components.items():
                if isinstance(component_health, bool):
                    if not component_health:
                        issues.append(f"{component_name} validation failed")
                        health_score *= 0.7
                elif hasattr(component_health, 'status'):
                    if component_health.status != ModuleStatus.HEALTHY:
                        issues.append(f"{component_name} unhealthy: {component_health.status.value}")
                        health_score *= 0.8
            
            # Check orchestration statistics
            if self._total_orchestrations > 0:
                success_rate = self._successful_orchestrations / self._total_orchestrations
                if success_rate < 0.8:  # Less than 80% success rate
                    issues.append(f"Low orchestration success rate: {success_rate:.1%}")
                    health_score *= 0.6
            
            # Determine overall status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.WARNING
            else:
                status = ModuleStatus.ERROR
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, fall back to simpler execution strategies
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.API_INTEGRATION,
                ModuleCapability.MONITORING
            ]
            
            # Switch to conservative strategies
            self._config.execution_strategy = ExecutionStrategy.SEQUENTIAL
            self._config.scheduling_strategy = SchedulingStrategy.FIFO
            self._config.enable_continuous_monitoring = False
            
            # Apply degradation to components
            self._parallel_engine.graceful_degradation()
            self._scheduler.graceful_degradation()
            self._infrastructure_validator.graceful_degradation()
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics and performance metrics."""
        try:
            # Get component statistics
            engine_stats = self._parallel_engine.get_execution_statistics()
            scheduler_stats = self._scheduler.get_scheduling_statistics()
            
            # Calculate orchestration statistics
            orchestration_success_rate = (
                self._successful_orchestrations / max(self._total_orchestrations, 1)
            )
            
            return {
                "orchestration_statistics": {
                    "total_orchestrations": self._total_orchestrations,
                    "successful_orchestrations": self._successful_orchestrations,
                    "failed_orchestrations": self._failed_orchestrations,
                    "success_rate": orchestration_success_rate,
                    "current_orchestration": self._current_orchestration.orchestration_id if self._current_orchestration else None,
                    "orchestration_history_count": len(self._orchestration_history)
                },
                "execution_statistics": engine_stats,
                "scheduling_statistics": scheduler_stats,
                "component_health": {
                    "orchestrator": self.get_health_status().status.value,
                    "execution_engine": self._parallel_engine.get_health_status().status.value,
                    "scheduler": self._scheduler.get_health_status().status.value,
                    "infrastructure_validator": self._infrastructure_validator.get_health_status().status.value
                },
                "configuration": {
                    "max_workers": self._config.max_workers,
                    "execution_strategy": self._config.execution_strategy.value,
                    "scheduling_strategy": self._config.scheduling_strategy.value,
                    "prefire_testing_enabled": self._config.enable_prefire_testing,
                    "continuous_monitoring_enabled": self._config.enable_continuous_monitoring
                }
            }
        except Exception as e:
            self._logger.error(f"Failed to get execution statistics: {e}")
            return {
                "error": f"Statistics collection failed: {str(e)}",
                "orchestration_statistics": {
                    "total_orchestrations": self._total_orchestrations,
                    "successful_orchestrations": self._successful_orchestrations,
                    "failed_orchestrations": self._failed_orchestrations
                }
            }

    async def execute_dag(self, tasks: List[TaskDefinition], 
                         execution_requirements: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """
        Execute DAG with comprehensive orchestration including validation,
        scheduling, and parallel execution.
        
        Args:
            tasks: List of task definitions to execute
            execution_requirements: Optional execution requirements
            
        Returns:
            OrchestrationResult with complete execution details
        """
        with self.trace_operation("execute_dag", 
                                task_count=len(tasks),
                                execution_requirements=execution_requirements) as trace:
            
            async with self._orchestration_lock:
                # Create orchestration result
                orchestration_id = str(uuid.uuid4())
                result = OrchestrationResult(
                    orchestration_id=orchestration_id,
                    status=OrchestrationStatus.VALIDATING,
                    start_time=datetime.now(),
                    total_tasks=len(tasks)
                )
                
                self._current_orchestration = result
                self._total_orchestrations += 1
                
                try:
                    # Phase 1: Infrastructure Validation (Prefire Testing)
                    if self._config.enable_prefire_testing:
                        self._logger.info(f"Starting prefire validation for orchestration {orchestration_id}")
                        validation_passed, validation_report = await self._infrastructure_validator.validate_for_execution(
                            execution_requirements or {}
                        )
                        
                        result.validation_report = validation_report
                        
                        if not validation_passed:
                            result.status = OrchestrationStatus.FAILED
                            result.error_summary = f"Infrastructure validation failed: {validation_report.recommendations}"
                            self._failed_orchestrations += 1
                            
                            # Broadcast validation failure
                            await self._ace_reporter.broadcast_execution_start(
                                orchestration_id, len(tasks), {"status": "validation_failed"}
                            )
                            
                            trace.output_result = {
                                'orchestration_id': orchestration_id,
                                'status': 'failed',
                                'failure_reason': 'infrastructure_validation'
                            }
                            
                            return result
                    
                    # Phase 2: DAG Validation and Registration
                    self._logger.info(f"Validating DAG structure for orchestration {orchestration_id}")
                    self._validate_and_register_tasks(tasks)
                    
                    # Phase 3: Task Scheduling
                    result.status = OrchestrationStatus.SCHEDULING
                    self._logger.info(f"Scheduling tasks for orchestration {orchestration_id}")
                    
                    self._scheduler.register_tasks(tasks)
                    
                    # Phase 4: Parallel Execution
                    result.status = OrchestrationStatus.EXECUTING
                    self._logger.info(f"Starting parallel execution for orchestration {orchestration_id}")
                    
                    # Broadcast execution start
                    execution_plan = {
                        "max_workers": self._config.max_workers,
                        "execution_strategy": self._config.execution_strategy.value,
                        "scheduling_strategy": self._config.scheduling_strategy.value,
                        "estimated_duration": len(tasks) * 2.0  # Simple estimation
                    }
                    await self._ace_reporter.broadcast_execution_start(
                        orchestration_id, len(tasks), execution_plan
                    )
                    
                    # Start continuous monitoring if enabled
                    if self._config.enable_continuous_monitoring:
                        await self._infrastructure_validator.start_continuous_monitoring()
                    
                    # Execute tasks with parallel engine and track progress
                    task_results = await self._execute_with_lifecycle_tracking(
                        orchestration_id, tasks, execution_requirements
                    )
                    
                    # Phase 5: Results Processing
                    result.task_results = task_results
                    result.completed_tasks = sum(1 for r in task_results.values() 
                                               if r.status.value == "completed")
                    result.failed_tasks = sum(1 for r in task_results.values() 
                                            if r.status.value == "failed")
                    result.skipped_tasks = sum(1 for r in task_results.values() 
                                             if r.status.value == "skipped")
                    
                    # Determine final status
                    if result.failed_tasks == 0:
                        result.status = OrchestrationStatus.COMPLETED
                        self._successful_orchestrations += 1
                    else:
                        result.status = OrchestrationStatus.FAILED
                        result.error_summary = f"{result.failed_tasks} tasks failed"
                        self._failed_orchestrations += 1
                    
                    # Finalize result
                    result.end_time = datetime.now()
                    result.duration_seconds = (result.end_time - result.start_time).total_seconds()
                    
                    # Collect performance metrics
                    result.performance_metrics = {
                        'execution_engine_stats': self._parallel_engine.get_execution_statistics(),
                        'scheduling_stats': self._scheduler.get_scheduling_statistics(),
                        'validation_stats': self._infrastructure_validator.get_validation_statistics(),
                        'ace_reporter_stats': self._ace_reporter.get_broadcast_statistics(),
                        'ai_memory_palace_stats': self._ai_memory_palace.get_learning_statistics()
                    }
                    
                    # Store execution pattern for learning
                    pattern_data = {
                        "task_count": len(tasks),
                        "execution_strategy": self._config.execution_strategy.value,
                        "scheduling_strategy": self._config.scheduling_strategy.value,
                        "max_workers": self._config.max_workers
                    }
                    await self._ai_memory_palace.store_execution_pattern(
                        orchestration_id, pattern_data, result.performance_metrics
                    )
                    
                    # Learn from execution for future optimization
                    learning_insights = await self._ai_memory_palace.learn_from_execution(
                        orchestration_id, result.performance_metrics
                    )
                    result.performance_metrics['learning_insights'] = learning_insights
                    
                    # Broadcast execution summary
                    execution_summary = {
                        "orchestration_id": orchestration_id,
                        "task_count": result.total_tasks,
                        "completed_tasks": result.completed_tasks,
                        "failed_tasks": result.failed_tasks,
                        "success_rate": result.completed_tasks / max(result.total_tasks, 1),
                        "actual_duration": result.duration_seconds,
                        "performance_metrics": result.performance_metrics
                    }
                    await self._ace_reporter.broadcast_execution_summary(
                        orchestration_id, execution_summary
                    )
                    
                    trace.output_result = {
                        'orchestration_id': orchestration_id,
                        'status': result.status.value,
                        'total_tasks': result.total_tasks,
                        'completed_tasks': result.completed_tasks,
                        'failed_tasks': result.failed_tasks,
                        'duration_seconds': result.duration_seconds
                    }
                    
                    self._logger.info(f"Orchestration {orchestration_id} completed with status: {result.status.value}")
                    
                    return result
                    
                except Exception as e:
                    # Handle orchestration failure
                    result.status = OrchestrationStatus.FAILED
                    result.end_time = datetime.now()
                    result.duration_seconds = (result.end_time - result.start_time).total_seconds()
                    result.error_summary = f"Orchestration failed: {str(e)}"
                    
                    self._failed_orchestrations += 1
                    self._logger.error(f"Orchestration {orchestration_id} failed: {e}")
                    
                    trace.output_result = {
                        'orchestration_id': orchestration_id,
                        'status': 'failed',
                        'error': str(e)
                    }
                    
                    return result
                    
                finally:
                    # Cleanup
                    self._current_orchestration = None
                    self._orchestration_history.append(result)
                    
                    # Keep only last 100 orchestrations in history
                    if len(self._orchestration_history) > 100:
                        self._orchestration_history = self._orchestration_history[-100:]
                    
                    # Stop continuous monitoring
                    if self._config.enable_continuous_monitoring:
                        await self._infrastructure_validator.stop_continuous_monitoring()
    
    def _validate_and_register_tasks(self, tasks: List[TaskDefinition]) -> None:
        """Validate and register tasks with DAG registry."""
        # Clear existing registrations
        self._dag_registry = DAGRegistry()
        
        # Register each task
        for task in tasks:
            success = self._dag_registry.register_module(task.task_id, task.dependencies)
            if not success:
                raise ValueError(f"Task {task.task_id} creates circular dependency")
        
        # Validate overall DAG structure
        if not self._dag_registry.validate_dag():
            raise ValueError("Task dependencies do not form a valid DAG")
        
        self._logger.info(f"Successfully validated and registered {len(tasks)} tasks")
    
    async def _execute_with_lifecycle_tracking(self, orchestration_id: str, 
                                             tasks: List[TaskDefinition],
                                             execution_requirements: Optional[Dict[str, Any]] = None) -> Dict[str, TaskExecutionResult]:
        """
        Execute tasks with comprehensive lifecycle tracking and progress broadcasting.
        
        Args:
            orchestration_id: Unique orchestration identifier
            tasks: List of task definitions to execute
            execution_requirements: Optional execution requirements
            
        Returns:
            Dictionary mapping task_id to TaskExecutionResult
        """
        # Create enhanced task definitions with lifecycle callbacks
        enhanced_tasks = []
        for task in tasks:
            enhanced_task = TaskDefinition(
                task_id=task.task_id,
                name=task.name,
                dependencies=task.dependencies,
                execution_function=self._create_lifecycle_wrapper(
                    orchestration_id, task.task_id, task.execution_function
                ),
                execution_args=task.execution_args,
                execution_kwargs=task.execution_kwargs,
                resource_requirements=task.resource_requirements,
                timeout_seconds=task.timeout_seconds,
                retry_count=task.retry_count,
                max_retries=task.max_retries,
                priority=task.priority
            )
            enhanced_tasks.append(enhanced_task)
        
        # Execute with parallel engine
        return await self._parallel_engine.execute_dag_parallel(
            enhanced_tasks, execution_requirements
        )
    
    def _create_lifecycle_wrapper(self, orchestration_id: str, task_id: str, 
                                original_function: Optional[callable]) -> callable:
        """
        Create a wrapper function that adds lifecycle tracking to task execution.
        
        Args:
            orchestration_id: Orchestration identifier
            task_id: Task identifier
            original_function: Original task function to wrap
            
        Returns:
            Wrapped function with lifecycle tracking
        """
        async def lifecycle_wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                # Execute original function
                if original_function:
                    if asyncio.iscoroutinefunction(original_function):
                        result = await original_function(*args, **kwargs)
                    else:
                        result = original_function(*args, **kwargs)
                else:
                    result = f"Task {task_id} executed successfully"
                
                # Calculate duration
                duration = (datetime.now() - start_time).total_seconds()
                
                # Broadcast task completion
                await self._ace_reporter.broadcast_task_completion(
                    orchestration_id, task_id, "completed", duration, {"result": str(result)}
                )
                
                return result
                
            except Exception as e:
                # Calculate duration
                duration = (datetime.now() - start_time).total_seconds()
                
                # Broadcast task failure
                await self._ace_reporter.broadcast_task_completion(
                    orchestration_id, task_id, "failed", duration, {"error": str(e)}
                )
                
                raise e
        
        return lifecycle_wrapper
    
    def get_current_orchestration_status(self) -> Optional[Dict[str, Any]]:
        """Get status of current orchestration if active."""
        if self._current_orchestration is None:
            return None
        
        return {
            'orchestration_id': self._current_orchestration.orchestration_id,
            'status': self._current_orchestration.status.value,
            'start_time': self._current_orchestration.start_time.isoformat(),
            'total_tasks': self._current_orchestration.total_tasks,
            'completed_tasks': self._current_orchestration.completed_tasks,
            'failed_tasks': self._current_orchestration.failed_tasks,
            'duration_seconds': (datetime.now() - self._current_orchestration.start_time).total_seconds()
        }
    
    def get_orchestration_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get history of recent orchestrations."""
        history = []
        for result in self._orchestration_history[-limit:]:
            history.append({
                'orchestration_id': result.orchestration_id,
                'status': result.status.value,
                'start_time': result.start_time.isoformat(),
                'end_time': result.end_time.isoformat() if result.end_time else None,
                'duration_seconds': result.duration_seconds,
                'total_tasks': result.total_tasks,
                'completed_tasks': result.completed_tasks,
                'failed_tasks': result.failed_tasks,
                'error_summary': result.error_summary
            })
        
        return history
    
    def get_orchestration_statistics(self) -> Dict[str, Any]:
        """Get comprehensive orchestration statistics."""
        success_rate = self._successful_orchestrations / max(self._total_orchestrations, 1)
        
        # Calculate average orchestration duration
        completed_orchestrations = [r for r in self._orchestration_history if r.duration_seconds is not None]
        avg_duration = (
            sum(r.duration_seconds for r in completed_orchestrations) / len(completed_orchestrations)
            if completed_orchestrations else 0.0
        )
        
        return {
            'total_orchestrations': self._total_orchestrations,
            'successful_orchestrations': self._successful_orchestrations,
            'failed_orchestrations': self._failed_orchestrations,
            'success_rate': success_rate,
            'average_duration_seconds': avg_duration,
            'current_orchestration_active': self._current_orchestration is not None,
            'component_statistics': {
                'parallel_engine': self._parallel_engine.get_execution_statistics(),
                'scheduler': self._scheduler.get_scheduling_statistics(),
                'infrastructure_validator': self._infrastructure_validator.get_validation_statistics(),
                'ace_reporter': self._ace_reporter.get_broadcast_statistics(),
                'ai_memory_palace': self._ai_memory_palace.get_learning_statistics()
            }
        }
    
    def validate_execution_plan(self, tasks: List[TaskDefinition], 
                              execution_requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate execution plan without executing tasks.
        
        Args:
            tasks: List of task definitions to validate
            execution_requirements: Optional execution requirements
            
        Returns:
            Validation report with readiness assessment
        """
        with self.trace_operation("validate_execution_plan", 
                                task_count=len(tasks),
                                execution_requirements=execution_requirements) as trace:
            
            validation_report = {
                "plan_valid": True,
                "validation_time": datetime.now().isoformat(),
                "task_count": len(tasks),
                "validation_results": [],
                "readiness_score": 1.0,
                "recommendations": []
            }
            
            try:
                # Validate DAG structure
                try:
                    self._validate_and_register_tasks(tasks)
                    validation_report["validation_results"].append({
                        "check": "DAG Structure",
                        "passed": True,
                        "details": "All task dependencies form a valid DAG"
                    })
                except Exception as e:
                    validation_report["plan_valid"] = False
                    validation_report["readiness_score"] *= 0.0
                    validation_report["validation_results"].append({
                        "check": "DAG Structure",
                        "passed": False,
                        "details": str(e)
                    })
                    validation_report["recommendations"].append("Fix circular dependencies in task definitions")
                
                # Check component health
                components = {
                    "Parallel Engine": self._parallel_engine.get_health_status(),
                    "Scheduler": self._scheduler.get_health_status(),
                    "Infrastructure Validator": self._infrastructure_validator.get_health_status(),
                    "ACE Reporter": self._ace_reporter.get_health_status(),
                    "AI Memory Palace": self._ai_memory_palace.get_health_status()
                }
                
                for component_name, health in components.items():
                    if health.status == ModuleStatus.HEALTHY:
                        validation_report["validation_results"].append({
                            "check": f"{component_name} Health",
                            "passed": True,
                            "details": f"Health score: {health.health_score:.2f}"
                        })
                    else:
                        validation_report["readiness_score"] *= 0.8
                        validation_report["validation_results"].append({
                            "check": f"{component_name} Health",
                            "passed": False,
                            "details": f"Status: {health.status.value}, Issues: {health.issues}"
                        })
                        validation_report["recommendations"].append(f"Address {component_name} health issues")
                
                # Validate resource requirements
                total_resource_weight = sum(
                    task.resource_requirements.get('weight', 1.0) for task in tasks
                )
                if total_resource_weight > self._config.max_workers * 2:
                    validation_report["readiness_score"] *= 0.9
                    validation_report["recommendations"].append(
                        "Consider increasing max_workers or reducing task resource requirements"
                    )
                
                # Check for potential optimization opportunities
                similar_patterns = []
                if len(tasks) > 5:  # Only check for larger executions
                    pattern_data = {
                        "task_count": len(tasks),
                        "execution_strategy": self._config.execution_strategy.value,
                        "max_workers": self._config.max_workers
                    }
                    # Note: In real implementation, this would be async
                    # similar_patterns = await self._ai_memory_palace.retrieve_similar_patterns(pattern_data)
                
                if similar_patterns:
                    validation_report["recommendations"].append(
                        f"Found {len(similar_patterns)} similar execution patterns for optimization"
                    )
                
                # Final readiness assessment
                if validation_report["readiness_score"] >= 0.9:
                    validation_report["readiness_assessment"] = "READY"
                elif validation_report["readiness_score"] >= 0.7:
                    validation_report["readiness_assessment"] = "READY_WITH_WARNINGS"
                else:
                    validation_report["readiness_assessment"] = "NOT_READY"
                    validation_report["plan_valid"] = False
                
                trace.output_result = {
                    'plan_valid': validation_report["plan_valid"],
                    'readiness_score': validation_report["readiness_score"],
                    'readiness_assessment': validation_report["readiness_assessment"]
                }
                
                return validation_report
                
            except Exception as e:
                validation_report["plan_valid"] = False
                validation_report["readiness_score"] = 0.0
                validation_report["readiness_assessment"] = "VALIDATION_ERROR"
                validation_report["validation_results"].append({
                    "check": "Validation Process",
                    "passed": False,
                    "details": f"Validation error: {str(e)}"
                })
                
                trace.output_result = {
                    'plan_valid': False,
                    'error': str(e)
                }
                
                return validation_report
    
    async def shutdown(self) -> None:
        """Shutdown the DAG orchestrator and all components."""
        with self.trace_operation("shutdown") as trace:
            self._logger.info("Shutting down DAG orchestrator")
            
            # Stop any active orchestration
            if self._current_orchestration:
                self._current_orchestration.status = OrchestrationStatus.CANCELLED
            
            # Shutdown components
            self._parallel_engine.shutdown()
            await self._infrastructure_validator.stop_continuous_monitoring()
            
            trace.output_result = {'shutdown_completed': True}
            self._logger.info("DAG orchestrator shutdown completed")


# Convenience functions for integration
def create_dag_orchestrator(config: Optional[OrchestrationConfig] = None) -> DAGOrchestrator:
    """
    Factory function to create DAG orchestrator.
    
    Args:
        config: Optional orchestration configuration
        
    Returns:
        DAGOrchestrator instance
    """
    return DAGOrchestrator(config)


def create_orchestration_config(
    max_workers: int = 10,
    execution_strategy: ExecutionStrategy = ExecutionStrategy.CONSERVATIVE,
    scheduling_strategy: SchedulingStrategy = SchedulingStrategy.ADAPTIVE,
    enable_prefire_testing: bool = True,
    enable_continuous_monitoring: bool = True
) -> OrchestrationConfig:
    """
    Convenience function to create orchestration configuration.
    
    Args:
        max_workers: Maximum number of worker threads
        execution_strategy: Execution strategy to use
        scheduling_strategy: Scheduling strategy to use
        enable_prefire_testing: Whether to enable prefire testing
        enable_continuous_monitoring: Whether to enable continuous monitoring
        
    Returns:
        OrchestrationConfig instance
    """
    return OrchestrationConfig(
        max_workers=max_workers,
        execution_strategy=execution_strategy,
        scheduling_strategy=scheduling_strategy,
        enable_prefire_testing=enable_prefire_testing,
        enable_continuous_monitoring=enable_continuous_monitoring
    )


def create_dag_orchestrator(config: Optional[OrchestrationConfig] = None, 
                           max_workers: Optional[int] = None) -> DAGOrchestrator:
    """
    Factory function to create DAG orchestrator with flexible configuration.
    
    Args:
        config: Optional orchestration configuration
        max_workers: Optional max workers (for backward compatibility)
        
    Returns:
        DAGOrchestrator instance
    """
    if config is None:
        # Create default config, using max_workers if provided
        workers = max_workers if max_workers is not None else 10
        config = OrchestrationConfig(max_workers=workers)
    
    return DAGOrchestrator(config)


def create_orchestration_result(orchestration_id: str, 
                              status: OrchestrationStatus = OrchestrationStatus.IDLE) -> OrchestrationResult:
    """
    Factory function to create orchestration result.
    
    Args:
        orchestration_id: Unique orchestration identifier
        status: Initial orchestration status
        
    Returns:
        OrchestrationResult instance
    """
    return OrchestrationResult(
        orchestration_id=orchestration_id,
        status=status,
        start_time=datetime.now()
    )