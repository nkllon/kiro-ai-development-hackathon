#!/usr/bin/env python3
"""
Agent Control Governance DAG Validator
=====================================

Validates the Agent Control Governance DAG structure for mathematical
correctness, dependency compliance, and execution readiness.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Set
from dataclasses import dataclass

# Import validation components
try:
    from src.rm_ddd.core.dag_registry import DAGRegistry
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
    from src.dag_orchestration.core.infrastructure_validator import InfrastructureValidator
except ImportError as e:
    print(f"❌ Failed to import validation components: {e}")
    print("Please ensure the Beast Mode framework is properly installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Validation result for DAG structure."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


class AgentControlGovernanceDAGValidator(ReflectiveModule):
    """
    Validator for Agent Control Governance DAG structure.
    
    Ensures mathematical correctness, dependency compliance,
    and execution readiness before launching parallel execution.
    """
    
    def __init__(self):
        super().__init__()
        self.dag_registry = DAGRegistry()
        self.infrastructure_validator = InfrastructureValidator()
        self.dag_data = None
        
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": "agent_control_governance_dag_validator",
            "name": "Agent Control Governance DAG Validator",
            "version": "1.0.0",
            "description": "Validates Agent Control Governance DAG structure",
            "author": "Beast Mode Framework"
        }
    
    def get_capabilities(self):
        """Get module capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.VALIDATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self):
        """Get module health status."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        return ModuleHealth(
            module_id=self.get_module_info()["module_id"],
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
    
    def load_dag_definition(self, dag_file_path: str) -> bool:
        """
        Load DAG definition from JSON file.
        
        Args:
            dag_file_path: Path to the DAG definition JSON file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with self.trace_operation("load_dag_definition", dag_file_path=dag_file_path):
                dag_file = Path(dag_file_path)
                if not dag_file.exists():
                    logger.error(f"DAG definition file not found: {dag_file_path}")
                    return False
                
                with open(dag_file, 'r') as f:
                    self.dag_data = json.load(f)
                
                logger.info(f"✅ Loaded DAG definition from {dag_file_path}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to load DAG definition: {e}")
            return False
    
    def validate_dag_structure(self) -> ValidationResult:
        """
        Validate the complete DAG structure.
        
        Returns:
            ValidationResult with validation status and details
        """
        try:
            with self.trace_operation("validate_dag_structure") as trace:
                if not self.dag_data:
                    return ValidationResult(
                        is_valid=False,
                        errors=["No DAG data loaded"],
                        warnings=[],
                        metrics={}
                    )
                
                errors = []
                warnings = []
                metrics = {}
                
                logger.info("🔍 VALIDATING AGENT CONTROL GOVERNANCE DAG")
                logger.info("=" * 50)
                
                # 1. Validate basic structure
                structure_result = self._validate_basic_structure()
                errors.extend(structure_result.errors)
                warnings.extend(structure_result.warnings)
                metrics.update(structure_result.metrics)
                
                # 2. Validate mathematical constraints (DAG compliance)
                dag_result = self._validate_dag_compliance()
                errors.extend(dag_result.errors)
                warnings.extend(dag_result.warnings)
                metrics.update(dag_result.metrics)
                
                # 3. Validate dependency consistency
                dependency_result = self._validate_dependency_consistency()
                errors.extend(dependency_result.errors)
                warnings.extend(dependency_result.warnings)
                metrics.update(dependency_result.metrics)
                
                # 4. Validate resource requirements
                resource_result = self._validate_resource_requirements()
                errors.extend(resource_result.errors)
                warnings.extend(resource_result.warnings)
                metrics.update(resource_result.metrics)
                
                # 5. Validate parallelization potential
                parallel_result = self._validate_parallelization_potential()
                errors.extend(parallel_result.errors)
                warnings.extend(parallel_result.warnings)
                metrics.update(parallel_result.metrics)
                
                # 6. Validate infrastructure readiness
                infra_result = self._validate_infrastructure_readiness()
                errors.extend(infra_result.errors)
                warnings.extend(infra_result.warnings)
                metrics.update(infra_result.metrics)
                
                is_valid = len(errors) == 0
                
                result = ValidationResult(
                    is_valid=is_valid,
                    errors=errors,
                    warnings=warnings,
                    metrics=metrics
                )
                
                trace.output_result = {
                    "is_valid": is_valid,
                    "error_count": len(errors),
                    "warning_count": len(warnings),
                    "metrics": metrics
                }
                
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to validate DAG structure: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                metrics={}
            )
    
    def _validate_basic_structure(self) -> ValidationResult:
        """Validate basic DAG structure."""
        errors = []
        warnings = []
        metrics = {}
        
        logger.info("📋 Validating basic structure...")
        
        # Check required top-level keys
        required_keys = ['execution_plan', 'task_definitions', 'dag_validation']
        for key in required_keys:
            if key not in self.dag_data:
                errors.append(f"Missing required key: {key}")
        
        # Validate execution plan
        execution_plan = self.dag_data.get('execution_plan', {})
        plan_required_keys = ['plan_id', 'total_tasks', 'parallelization_strategy']
        for key in plan_required_keys:
            if key not in execution_plan:
                errors.append(f"Missing execution plan key: {key}")
        
        # Validate task definitions
        task_definitions = self.dag_data.get('task_definitions', [])
        if not task_definitions:
            errors.append("No task definitions found")
        else:
            metrics['total_tasks'] = len(task_definitions)
            
            # Validate each task definition
            for i, task in enumerate(task_definitions):
                task_required_keys = ['id', 'name', 'description', 'dependencies']
                for key in task_required_keys:
                    if key not in task:
                        errors.append(f"Task {i}: Missing required key: {key}")
        
        logger.info(f"  ✅ Found {metrics.get('total_tasks', 0)} task definitions")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def _validate_dag_compliance(self) -> ValidationResult:
        """Validate DAG compliance (no circular dependencies)."""
        errors = []
        warnings = []
        metrics = {}
        
        logger.info("🔄 Validating DAG compliance...")
        
        task_definitions = self.dag_data.get('task_definitions', [])
        
        # Build dependency graph
        dependency_graph = {}
        task_ids = set()
        
        for task in task_definitions:
            task_id = task.get('id')
            dependencies = task.get('dependencies', [])
            
            if task_id:
                task_ids.add(task_id)
                dependency_graph[task_id] = set(dependencies)
        
        # Register with DAG registry for validation
        try:
            for task_id, deps in dependency_graph.items():
                success = self.dag_registry.register_module(task_id, deps)
                if not success:
                    errors.append(f"Task {task_id} creates circular dependency")
        except Exception as e:
            errors.append(f"DAG validation error: {str(e)}")
        
        # Validate that all dependencies exist
        for task_id, deps in dependency_graph.items():
            for dep in deps:
                if dep not in task_ids:
                    errors.append(f"Task {task_id} depends on non-existent task: {dep}")
        
        # Calculate metrics
        metrics['total_dependencies'] = sum(len(deps) for deps in dependency_graph.values())
        metrics['tasks_with_dependencies'] = sum(1 for deps in dependency_graph.values() if deps)
        metrics['tasks_without_dependencies'] = len(task_ids) - metrics['tasks_with_dependencies']
        
        logger.info(f"  ✅ Validated {len(task_ids)} tasks with {metrics['total_dependencies']} dependencies")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def _validate_dependency_consistency(self) -> ValidationResult:
        """Validate dependency consistency across phases."""
        errors = []
        warnings = []
        metrics = {}
        
        logger.info("🔗 Validating dependency consistency...")
        
        task_definitions = self.dag_data.get('task_definitions', [])
        
        # Group tasks by phase
        phases = {}
        for task in task_definitions:
            phase = task.get('phase', 1)
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(task)
        
        # Validate phase dependencies
        for phase_num, tasks in phases.items():
            for task in tasks:
                task_id = task.get('id')
                dependencies = task.get('dependencies', [])
                
                # Check that dependencies are from earlier phases
                for dep in dependencies:
                    dep_phase = None
                    for p, p_tasks in phases.items():
                        for p_task in p_tasks:
                            if p_task.get('id') == dep:
                                dep_phase = p
                                break
                        if dep_phase:
                            break
                    
                    if dep_phase and dep_phase >= phase_num:
                        errors.append(f"Task {task_id} in phase {phase_num} depends on task {dep} in phase {dep_phase} (should be earlier)")
        
        metrics['total_phases'] = len(phases)
        metrics['phase_distribution'] = {f"phase_{p}": len(tasks) for p, tasks in phases.items()}
        
        logger.info(f"  ✅ Validated {len(phases)} phases with consistent dependencies")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def _validate_resource_requirements(self) -> ValidationResult:
        """Validate resource requirements."""
        errors = []
        warnings = []
        metrics = {}
        
        logger.info("💾 Validating resource requirements...")
        
        task_definitions = self.dag_data.get('task_definitions', [])
        
        total_cpu_cores = 0
        total_memory_mb = 0
        total_disk_mb = 0
        total_duration_minutes = 0
        
        for task in task_definitions:
            task_id = task.get('id')
            resources = task.get('resource_requirements', {})
            
            # Validate required resource fields
            required_resource_fields = ['cpu_cores', 'memory_mb', 'disk_mb', 'estimated_duration_minutes']
            for field in required_resource_fields:
                if field not in resources:
                    warnings.append(f"Task {task_id}: Missing resource requirement: {field}")
                else:
                    value = resources[field]
                    if not isinstance(value, (int, float)) or value <= 0:
                        errors.append(f"Task {task_id}: Invalid {field} value: {value}")
            
            # Accumulate totals
            total_cpu_cores += resources.get('cpu_cores', 0)
            total_memory_mb += resources.get('memory_mb', 0)
            total_disk_mb += resources.get('disk_mb', 0)
            total_duration_minutes += resources.get('estimated_duration_minutes', 0)
        
        metrics['total_cpu_cores'] = total_cpu_cores
        metrics['total_memory_mb'] = total_memory_mb
        metrics['total_disk_mb'] = total_disk_mb
        metrics['total_duration_minutes'] = total_duration_minutes
        metrics['estimated_sequential_hours'] = total_duration_minutes / 60
        
        logger.info(f"  ✅ Total resources: {total_cpu_cores} CPU cores, {total_memory_mb} MB RAM, {total_disk_mb} MB disk")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def _validate_parallelization_potential(self) -> ValidationResult:
        """Validate parallelization potential."""
        errors = []
        warnings = []
        metrics = {}
        
        logger.info("⚡ Validating parallelization potential...")
        
        task_definitions = self.dag_data.get('task_definitions', [])
        
        # Group tasks by phase
        phases = {}
        for task in task_definitions:
            phase = task.get('phase', 1)
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(task)
        
        # Calculate parallelization metrics
        max_parallel_tasks = max(len(tasks) for tasks in phases.values()) if phases else 0
        total_phases = len(phases)
        
        # Calculate potential time savings
        sequential_time = sum(
            task.get('resource_requirements', {}).get('estimated_duration_minutes', 0)
            for task in task_definitions
        )
        
        # Estimate parallel time (longest phase duration)
        parallel_time = 0
        for phase_tasks in phases.values():
            phase_duration = max(
                task.get('resource_requirements', {}).get('estimated_duration_minutes', 0)
                for task in phase_tasks
            ) if phase_tasks else 0
            parallel_time += phase_duration
        
        parallelization_efficiency = (
            (sequential_time - parallel_time) / sequential_time * 100
            if sequential_time > 0 else 0
        )
        
        metrics['max_parallel_tasks_per_phase'] = max_parallel_tasks
        metrics['total_phases'] = total_phases
        metrics['sequential_time_minutes'] = sequential_time
        metrics['parallel_time_minutes'] = parallel_time
        metrics['parallelization_efficiency_percent'] = parallelization_efficiency
        metrics['time_savings_minutes'] = sequential_time - parallel_time
        
        logger.info(f"  ✅ Max parallel tasks: {max_parallel_tasks}, Efficiency: {parallelization_efficiency:.1f}%")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def _validate_infrastructure_readiness(self) -> ValidationResult:
        """Validate infrastructure readiness."""
        errors = []
        warnings = []
        metrics = {}
        
        logger.info("🏗️  Validating infrastructure readiness...")
        
        try:
            # Use infrastructure validator to check readiness
            validation_result = self.infrastructure_validator.validate_all_preconditions()
            
            if not validation_result.get('overall_status', False):
                errors.append("Infrastructure validation failed")
                
                # Add specific infrastructure errors
                precondition_results = validation_result.get('precondition_results', [])
                for result in precondition_results:
                    if not result.get('passed', True):
                        error_msg = result.get('error_message', 'Unknown infrastructure error')
                        errors.append(f"Infrastructure: {error_msg}")
            
            metrics['infrastructure_ready'] = validation_result.get('overall_status', False)
            metrics['infrastructure_checks'] = len(validation_result.get('precondition_results', []))
            
        except Exception as e:
            warnings.append(f"Could not validate infrastructure: {str(e)}")
            metrics['infrastructure_ready'] = False
        
        logger.info(f"  ✅ Infrastructure readiness: {metrics.get('infrastructure_ready', False)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def generate_validation_report(self, validation_result: ValidationResult) -> str:
        """Generate comprehensive validation report."""
        report = []
        report.append("🔍 AGENT CONTROL GOVERNANCE DAG VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Overall status
        status_emoji = "✅" if validation_result.is_valid else "❌"
        report.append(f"{status_emoji} Overall Status: {'VALID' if validation_result.is_valid else 'INVALID'}")
        report.append("")
        
        # Metrics summary
        metrics = validation_result.metrics
        report.append("📊 Validation Metrics:")
        report.append(f"  • Total Tasks: {metrics.get('total_tasks', 0)}")
        report.append(f"  • Total Phases: {metrics.get('total_phases', 0)}")
        report.append(f"  • Max Parallel Tasks: {metrics.get('max_parallel_tasks_per_phase', 0)}")
        report.append(f"  • Total Dependencies: {metrics.get('total_dependencies', 0)}")
        report.append(f"  • Parallelization Efficiency: {metrics.get('parallelization_efficiency_percent', 0):.1f}%")
        report.append(f"  • Sequential Time: {metrics.get('sequential_time_minutes', 0)/60:.1f} hours")
        report.append(f"  • Parallel Time: {metrics.get('parallel_time_minutes', 0)/60:.1f} hours")
        report.append(f"  • Time Savings: {metrics.get('time_savings_minutes', 0)/60:.1f} hours")
        report.append(f"  • Infrastructure Ready: {metrics.get('infrastructure_ready', False)}")
        report.append("")
        
        # Errors
        if validation_result.errors:
            report.append("❌ Validation Errors:")
            for error in validation_result.errors:
                report.append(f"  • {error}")
            report.append("")
        
        # Warnings
        if validation_result.warnings:
            report.append("⚠️  Validation Warnings:")
            for warning in validation_result.warnings:
                report.append(f"  • {warning}")
            report.append("")
        
        # Recommendations
        report.append("💡 Recommendations:")
        if validation_result.is_valid:
            report.append("  • DAG structure is valid and ready for execution")
            report.append("  • Consider running infrastructure validation before execution")
            report.append("  • Monitor resource usage during parallel execution")
        else:
            report.append("  • Fix all validation errors before attempting execution")
            report.append("  • Review dependency structure for circular references")
            report.append("  • Ensure all required infrastructure is available")
        
        return "\n".join(report)


def main():
    """Main validation function."""
    logger.info("🔍 AGENT CONTROL GOVERNANCE DAG VALIDATOR")
    logger.info("=" * 50)
    
    # Initialize validator
    validator = AgentControlGovernanceDAGValidator()
    
    # Load DAG definition
    dag_file = "agent_control_governance_dag_tasks.json"
    if not validator.load_dag_definition(dag_file):
        logger.error(f"❌ Failed to load DAG definition from {dag_file}")
        sys.exit(1)
    
    # Validate DAG structure
    validation_result = validator.validate_dag_structure()
    
    # Generate and display report
    report = validator.generate_validation_report(validation_result)
    print("\n" + report)
    
    # Save validation report
    report_file = "agent_control_governance_dag_validation_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"📄 Validation report saved to {report_file}")
    
    # Exit with appropriate code
    if validation_result.is_valid:
        logger.info("🎉 DAG validation completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 DAG validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()