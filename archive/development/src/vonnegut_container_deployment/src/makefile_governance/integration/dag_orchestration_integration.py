"""
DAG Orchestration Integration for Makefile Governance

Integrates makefile governance components with the DAG orchestration system
for parallel execution of validation and governance tasks.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleStatus, ModuleCapability, ModuleHealth
from src.dag_orchestration.core.dag_orchestrator import DAGOrchestrator, OrchestrationConfig
from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition, ExecutionStrategy
from src.dag_orchestration.execution.dependency_aware_scheduler import SchedulingStrategy
from src.makefile_governance.core.syntax_validator import MakefileSyntaxValidator
from src.makefile_governance.core.governance_engine import MakefileGovernanceEngine
from src.makefile_governance.core.health_monitor import MakefileHealthMonitor


@dataclass
class MakefileValidationTask:
    """Definition of a makefile validation task for DAG execution."""
    makefile_path: Path
    validation_type: str  # 'syntax', 'governance', 'health'
    dependencies: Set[str]
    priority: int = 0


class MakefileDAGOrchestrator(ReflectiveModule):
    """
    DAG orchestrator specifically designed for makefile governance tasks.
    
    Coordinates parallel execution of makefile validation, governance checking,
    and health monitoring using the Beast Mode DAG orchestration framework.
    """
    
    def __init__(self, max_workers: int = 4):
        super().__init__()
        self.module_id = "makefile_dag_orchestrator"
        self._logger = logging.getLogger(__name__)
        
        # Initialize components
        self._syntax_validator = MakefileSyntaxValidator()
        self._governance_engine = MakefileGovernanceEngine()
        self._health_monitor = MakefileHealthMonitor()
        
        # Initialize DAG orchestrator
        config = OrchestrationConfig(
            max_workers=max_workers,
            execution_strategy=ExecutionStrategy.CONSERVATIVE,
            scheduling_strategy=SchedulingStrategy.ADAPTIVE,
            enable_prefire_testing=True,
            enable_continuous_monitoring=True
        )
        self._dag_orchestrator = DAGOrchestrator(config)
        
        # Statistics
        self._total_orchestrations = 0
        self._successful_orchestrations = 0
        self._failed_orchestrations = 0
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Makefile DAG Orchestrator",
            "version": "1.0.0",
            "description": "DAG orchestrator for makefile governance tasks",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "components": {
                "syntax_validator": self._syntax_validator.get_module_info(),
                "governance_engine": self._governance_engine.get_module_info(),
                "health_monitor": self._health_monitor.get_module_info(),
                "dag_orchestrator": self._dag_orchestrator.get_module_info()
            },
            "statistics": {
                "total_orchestrations": self._total_orchestrations,
                "successful_orchestrations": self._successful_orchestrations,
                "failed_orchestrations": self._failed_orchestrations,
                "success_rate": self._successful_orchestrations / max(self._total_orchestrations, 1)
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        # Aggregate health from all components
        component_healths = [
            self._syntax_validator.get_health_status(),
            self._governance_engine.get_health_status(),
            self._health_monitor.get_health_status(),
            self._dag_orchestrator.get_health_status()
        ]
        
        # Calculate overall health
        health_scores = [h.health_score for h in component_healths]
        overall_score = sum(health_scores) / len(health_scores)
        
        # Collect issues
        issues = []
        for health in component_healths:
            issues.extend(health.issues)
        
        # Determine status
        if overall_score >= 0.9:
            status = ModuleStatus.HEALTHY
        elif overall_score >= 0.7:
            status = ModuleStatus.WARNING
        else:
            status = ModuleStatus.ERROR
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=overall_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=sum(h.error_count for h in component_healths),
            warning_count=sum(h.warning_count for h in component_healths)
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        # Apply degradation to all components
        results = [
            self._syntax_validator.graceful_degradation(),
            self._governance_engine.graceful_degradation(),
            self._health_monitor.graceful_degradation(),
            self._dag_orchestrator.graceful_degradation()
        ]
        
        # Aggregate results
        success = all(r.success for r in results)
        
        remaining_capabilities = [ModuleCapability.CORE_FUNCTIONALITY]
        degraded_capabilities = [
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
        
        return GracefulDegradationResult(
            success=success,
            degraded_capabilities=degraded_capabilities,
            remaining_capabilities=remaining_capabilities
        )
    
    async def validate_makefiles_parallel(self, makefile_paths: List[Path], 
                                        validation_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate multiple makefiles in parallel using DAG orchestration.
        
        Args:
            makefile_paths: List of makefile paths to validate
            validation_options: Optional validation configuration
            
        Returns:
            Comprehensive validation results
        """
        with self.trace_operation("validate_makefiles_parallel", 
                                makefile_count=len(makefile_paths),
                                validation_options=validation_options) as trace:
            
            self._total_orchestrations += 1
            
            try:
                # Create validation tasks
                tasks = self._create_validation_tasks(makefile_paths, validation_options or {})
                
                # Execute tasks using DAG orchestrator
                orchestration_result = await self._dag_orchestrator.execute_dag(
                    tasks, 
                    execution_requirements={
                        "makefile_validation": True,
                        "parallel_execution": True,
                        "resource_requirements": {"cpu": len(makefile_paths) * 0.1}
                    }
                )
                
                # Process results
                validation_results = self._process_orchestration_results(orchestration_result)
                
                # Update statistics
                if orchestration_result.status.value == "completed":
                    self._successful_orchestrations += 1
                else:
                    self._failed_orchestrations += 1
                
                # Record health metrics
                for makefile_path in makefile_paths:
                    success = str(makefile_path) in validation_results.get("successful_validations", [])
                    duration = validation_results.get("task_durations", {}).get(str(makefile_path), 0.0)
                    
                    self._health_monitor.record_validation_result(success, duration)
                    if validation_results.get("governance_results", {}).get(str(makefile_path)):
                        compliant = validation_results["governance_results"][str(makefile_path)].get("is_compliant", False)
                        self._health_monitor.record_governance_result(compliant, duration)
                
                trace.output_result = {
                    "orchestration_id": orchestration_result.orchestration_id,
                    "status": orchestration_result.status.value,
                    "total_tasks": orchestration_result.total_tasks,
                    "completed_tasks": orchestration_result.completed_tasks,
                    "failed_tasks": orchestration_result.failed_tasks,
                    "duration_seconds": orchestration_result.duration_seconds
                }
                
                return validation_results
                
            except Exception as e:
                self._failed_orchestrations += 1
                self._logger.error(f"Parallel validation failed: {e}")
                raise
    
    def _create_validation_tasks(self, makefile_paths: List[Path], 
                               validation_options: Dict[str, Any]) -> List[TaskDefinition]:
        """Create DAG tasks for makefile validation."""
        tasks = []
        
        for i, makefile_path in enumerate(makefile_paths):
            # Syntax validation task
            syntax_task = TaskDefinition(
                task_id=f"syntax_validation_{i}_{makefile_path.name}",
                name=f"Syntax Validation: {makefile_path.name}",
                dependencies=set(),
                execution_function=self._create_syntax_validation_function(makefile_path),
                priority=validation_options.get("syntax_priority", 10)
            )
            tasks.append(syntax_task)
            
            # Governance validation task (depends on syntax validation)
            governance_task = TaskDefinition(
                task_id=f"governance_validation_{i}_{makefile_path.name}",
                name=f"Governance Validation: {makefile_path.name}",
                dependencies={syntax_task.task_id},
                execution_function=self._create_governance_validation_function(makefile_path),
                priority=validation_options.get("governance_priority", 5)
            )
            tasks.append(governance_task)
            
            # Health monitoring task (depends on both validations)
            health_task = TaskDefinition(
                task_id=f"health_monitoring_{i}_{makefile_path.name}",
                name=f"Health Monitoring: {makefile_path.name}",
                dependencies={syntax_task.task_id, governance_task.task_id},
                execution_function=self._create_health_monitoring_function(makefile_path),
                priority=validation_options.get("health_priority", 1)
            )
            tasks.append(health_task)
        
        return tasks
    
    def _create_syntax_validation_function(self, makefile_path: Path):
        """Create syntax validation function for a specific makefile."""
        async def validate_syntax():
            try:
                result = self._syntax_validator.validate_makefile(makefile_path)
                return {
                    "task_type": "syntax_validation",
                    "makefile_path": str(makefile_path),
                    "result": {
                        "is_valid": result.is_valid,
                        "error_count": len(result.errors),
                        "warning_count": len(result.warnings),
                        "errors": [{"type": e.error_type.value, "line": e.line_number, "message": e.message} 
                                 for e in result.errors],
                        "warnings": [{"type": w.error_type.value, "line": w.line_number, "message": w.message} 
                                   for w in result.warnings]
                    }
                }
            except Exception as e:
                return {
                    "task_type": "syntax_validation",
                    "makefile_path": str(makefile_path),
                    "error": str(e),
                    "result": {"is_valid": False, "error_count": 1, "warning_count": 0}
                }
        
        return validate_syntax
    
    def _create_governance_validation_function(self, makefile_path: Path):
        """Create governance validation function for a specific makefile."""
        async def validate_governance():
            try:
                result = self._governance_engine.validate_governance(makefile_path)
                return {
                    "task_type": "governance_validation",
                    "makefile_path": str(makefile_path),
                    "result": {
                        "is_compliant": result.is_compliant,
                        "violation_count": len(result.violations),
                        "complexity_score": result.complexity_score,
                        "quality_score": result.quality_score,
                        "violations": [{"rule": v.rule.name, "line": v.line_number, "message": v.message} 
                                     for v in result.violations],
                        "recommendations": result.recommendations
                    }
                }
            except Exception as e:
                return {
                    "task_type": "governance_validation",
                    "makefile_path": str(makefile_path),
                    "error": str(e),
                    "result": {"is_compliant": False, "violation_count": 1}
                }
        
        return validate_governance
    
    def _create_health_monitoring_function(self, makefile_path: Path):
        """Create health monitoring function for a specific makefile."""
        async def monitor_health():
            try:
                # Get current system health
                system_health = self._health_monitor.get_system_health()
                
                return {
                    "task_type": "health_monitoring",
                    "makefile_path": str(makefile_path),
                    "result": {
                        "system_status": system_health.status.value,
                        "health_score": system_health.health_score,
                        "active_alerts": len(system_health.alerts),
                        "recommendations": system_health.recommendations
                    }
                }
            except Exception as e:
                return {
                    "task_type": "health_monitoring",
                    "makefile_path": str(makefile_path),
                    "error": str(e),
                    "result": {"system_status": "error", "health_score": 0.0}
                }
        
        return monitor_health
    
    def _process_orchestration_results(self, orchestration_result) -> Dict[str, Any]:
        """Process DAG orchestration results into structured validation results."""
        results = {
            "orchestration_summary": {
                "orchestration_id": orchestration_result.orchestration_id,
                "status": orchestration_result.status.value,
                "total_tasks": orchestration_result.total_tasks,
                "completed_tasks": orchestration_result.completed_tasks,
                "failed_tasks": orchestration_result.failed_tasks,
                "duration_seconds": orchestration_result.duration_seconds
            },
            "syntax_results": {},
            "governance_results": {},
            "health_results": {},
            "successful_validations": [],
            "failed_validations": [],
            "task_durations": {}
        }
        
        # Process individual task results
        for task_id, task_result in orchestration_result.task_results.items():
            if task_result.result and isinstance(task_result.result, dict):
                task_data = task_result.result
                makefile_path = task_data.get("makefile_path")
                task_type = task_data.get("task_type")
                
                # Record task duration
                if makefile_path and task_result.duration_seconds:
                    results["task_durations"][makefile_path] = task_result.duration_seconds
                
                # Process by task type
                if task_type == "syntax_validation":
                    results["syntax_results"][makefile_path] = task_data.get("result", {})
                    if task_data.get("result", {}).get("is_valid", False):
                        if makefile_path not in results["failed_validations"]:
                            results["successful_validations"].append(makefile_path)
                    else:
                        results["failed_validations"].append(makefile_path)
                        if makefile_path in results["successful_validations"]:
                            results["successful_validations"].remove(makefile_path)
                
                elif task_type == "governance_validation":
                    results["governance_results"][makefile_path] = task_data.get("result", {})
                
                elif task_type == "health_monitoring":
                    results["health_results"][makefile_path] = task_data.get("result", {})
        
        return results
    
    async def repair_makefiles_parallel(self, makefile_paths: List[Path], 
                                      repair_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Repair multiple makefiles in parallel using DAG orchestration.
        
        Args:
            makefile_paths: List of makefile paths to repair
            repair_options: Optional repair configuration
            
        Returns:
            Comprehensive repair results
        """
        with self.trace_operation("repair_makefiles_parallel", 
                                makefile_count=len(makefile_paths),
                                repair_options=repair_options) as trace:
            
            try:
                # Create repair tasks
                tasks = self._create_repair_tasks(makefile_paths, repair_options or {})
                
                # Execute tasks using DAG orchestrator
                orchestration_result = await self._dag_orchestrator.execute_dag(
                    tasks,
                    execution_requirements={
                        "makefile_repair": True,
                        "parallel_execution": True,
                        "backup_creation": True,
                        "resource_requirements": {"cpu": len(makefile_paths) * 0.2}
                    }
                )
                
                # Process results
                repair_results = self._process_repair_results(orchestration_result)
                
                # Record health metrics
                for makefile_path in makefile_paths:
                    success = str(makefile_path) in repair_results.get("successful_repairs", [])
                    duration = repair_results.get("task_durations", {}).get(str(makefile_path), 0.0)
                    self._health_monitor.record_repair_result(success, duration)
                
                trace.output_result = {
                    "orchestration_id": orchestration_result.orchestration_id,
                    "status": orchestration_result.status.value,
                    "successful_repairs": len(repair_results.get("successful_repairs", [])),
                    "failed_repairs": len(repair_results.get("failed_repairs", []))
                }
                
                return repair_results
                
            except Exception as e:
                self._logger.error(f"Parallel repair failed: {e}")
                raise
    
    def _create_repair_tasks(self, makefile_paths: List[Path], 
                           repair_options: Dict[str, Any]) -> List[TaskDefinition]:
        """Create DAG tasks for makefile repair."""
        tasks = []
        
        for i, makefile_path in enumerate(makefile_paths):
            # Repair task
            repair_task = TaskDefinition(
                task_id=f"repair_{i}_{makefile_path.name}",
                name=f"Repair: {makefile_path.name}",
                dependencies=set(),
                execution_function=self._create_repair_function(makefile_path, repair_options),
                priority=repair_options.get("repair_priority", 10)
            )
            tasks.append(repair_task)
            
            # Validation task (depends on repair)
            validation_task = TaskDefinition(
                task_id=f"post_repair_validation_{i}_{makefile_path.name}",
                name=f"Post-Repair Validation: {makefile_path.name}",
                dependencies={repair_task.task_id},
                execution_function=self._create_syntax_validation_function(makefile_path),
                priority=repair_options.get("validation_priority", 5)
            )
            tasks.append(validation_task)
        
        return tasks
    
    def _create_repair_function(self, makefile_path: Path, repair_options: Dict[str, Any]):
        """Create repair function for a specific makefile."""
        async def repair_makefile():
            try:
                create_backup = repair_options.get("create_backup", True)
                result = self._syntax_validator.repair_makefile(makefile_path, create_backup)
                
                return {
                    "task_type": "makefile_repair",
                    "makefile_path": str(makefile_path),
                    "result": {
                        "repair_successful": result.is_valid,
                        "backup_path": result.backup_path,
                        "errors_remaining": len(result.errors),
                        "warnings_remaining": len(result.warnings)
                    }
                }
            except Exception as e:
                return {
                    "task_type": "makefile_repair",
                    "makefile_path": str(makefile_path),
                    "error": str(e),
                    "result": {"repair_successful": False}
                }
        
        return repair_makefile
    
    def _process_repair_results(self, orchestration_result) -> Dict[str, Any]:
        """Process repair orchestration results."""
        results = {
            "orchestration_summary": {
                "orchestration_id": orchestration_result.orchestration_id,
                "status": orchestration_result.status.value,
                "total_tasks": orchestration_result.total_tasks,
                "completed_tasks": orchestration_result.completed_tasks,
                "failed_tasks": orchestration_result.failed_tasks,
                "duration_seconds": orchestration_result.duration_seconds
            },
            "repair_results": {},
            "validation_results": {},
            "successful_repairs": [],
            "failed_repairs": [],
            "task_durations": {}
        }
        
        # Process individual task results
        for task_id, task_result in orchestration_result.task_results.items():
            if task_result.result and isinstance(task_result.result, dict):
                task_data = task_result.result
                makefile_path = task_data.get("makefile_path")
                task_type = task_data.get("task_type")
                
                # Record task duration
                if makefile_path and task_result.duration_seconds:
                    results["task_durations"][makefile_path] = task_result.duration_seconds
                
                # Process by task type
                if task_type == "makefile_repair":
                    results["repair_results"][makefile_path] = task_data.get("result", {})
                    if task_data.get("result", {}).get("repair_successful", False):
                        results["successful_repairs"].append(makefile_path)
                    else:
                        results["failed_repairs"].append(makefile_path)
                
                elif task_type == "syntax_validation":
                    results["validation_results"][makefile_path] = task_data.get("result", {})
        
        return results
    
    def get_orchestration_statistics(self) -> Dict[str, Any]:
        """Get comprehensive orchestration statistics."""
        dag_stats = self._dag_orchestrator.get_orchestration_statistics()
        health_stats = self._health_monitor.get_system_health()
        
        return {
            "makefile_orchestrator": {
                "total_orchestrations": self._total_orchestrations,
                "successful_orchestrations": self._successful_orchestrations,
                "failed_orchestrations": self._failed_orchestrations,
                "success_rate": self._successful_orchestrations / max(self._total_orchestrations, 1)
            },
            "dag_orchestrator": dag_stats,
            "system_health": {
                "status": health_stats.status.value,
                "health_score": health_stats.health_score,
                "active_alerts": len(health_stats.alerts),
                "recommendations": health_stats.recommendations
            }
        }


# Convenience functions
def create_makefile_dag_orchestrator(max_workers: int = 4) -> MakefileDAGOrchestrator:
    """
    Factory function to create makefile DAG orchestrator.
    
    Args:
        max_workers: Maximum number of worker threads
        
    Returns:
        MakefileDAGOrchestrator instance
    """
    return MakefileDAGOrchestrator(max_workers=max_workers)