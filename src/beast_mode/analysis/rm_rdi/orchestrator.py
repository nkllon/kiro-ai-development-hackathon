"""
RM-RDI Analysis System - Analysis Orchestrator RM

OPERATOR SAFETY: This orchestrator provides READ-ONLY analysis coordination
with emergency shutdown capabilities and zero impact to existing systems.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .base import BaseOrchestrator, BaseAnalyzer, SafetyViolationError, AnalysisError
from .data_models import AnalysisResult, AnalysisStatus, AnalysisConfiguration
from .safety import get_safety_manager, is_safe_to_proceed, SafetyStatus
from .workflow import WorkflowCoordinator, AggregatedResult


@dataclass
class AnalysisWorkflow:
    """Configuration for analysis workflow execution"""
    workflow_id: str
    analyzer_names: List[str]
    parallel_execution: bool = True
    timeout_seconds: int = 300  # 5 minutes default
    retry_on_failure: bool = True
    max_retries: int = 2
    
    
@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    workflow_id: str
    status: AnalysisStatus
    results: Dict[str, AnalysisResult]
    execution_time: float
    errors: List[str]
    safety_validated: bool = True
    emergency_shutdown_available: bool = True


class AnalysisOrchestratorRM(BaseOrchestrator):
    """
    OPERATOR-SAFE Analysis Orchestrator RM
    
    Coordinates multiple analyzer components with full safety guarantees:
    - READ-ONLY operations only
    - Emergency shutdown for all analyzers
    - Resource monitoring and limits
    - Cannot impact existing systems
    - Graceful degradation on failures
    
    Implements ReflectiveModule interface for RM compliance.
    """
    
    def __init__(self):
        super().__init__("analysis_orchestrator")
        
        # Workflow management
        self.active_workflows: Dict[str, AnalysisWorkflow] = {}
        self.workflow_results: Dict[str, WorkflowResult] = {}
        self.workflow_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="analysis_")
        
        # Configuration and parameters
        self.default_config = AnalysisConfiguration()
        self.analysis_parameters: Dict[str, Any] = {}
        
        # Workflow coordination
        self.workflow_coordinator = WorkflowCoordinator()
        
        # Performance monitoring
        self.execution_metrics: Dict[str, List[float]] = {}
        self.last_cleanup_time = datetime.now()
        
        self.logger.info("AnalysisOrchestratorRM initialized with operator safety guarantees")
        
    def get_module_status(self) -> Dict[str, Any]:
        """Get orchestrator status with workflow and safety information"""
        base_status = super().get_module_status()
        
        # Add workflow-specific status
        workflow_status = {
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.workflow_results),
            "registered_analyzers": len(self.registered_analyzers),
            "executor_threads": {
                "max_workers": self.workflow_executor._max_workers,
                "active_threads": len([t for t in self.workflow_executor._threads if t.is_alive()]) if hasattr(self.workflow_executor, '_threads') else 0
            }
        }
        
        base_status.update({
            "workflow_status": workflow_status,
            "configuration": {
                "default_timeout": self.default_config.timeout_seconds,
                "max_parallel_analyses": self.default_config.max_parallel_analyses,
                "resource_limits": self.default_config.resource_limits
            }
        })
        
        return base_status
        
    def is_healthy(self) -> bool:
        """Health check including workflow executor and resource usage"""
        # Check base orchestrator health
        if not super().is_healthy():
            return False
            
        # Check workflow executor health
        if self.workflow_executor._shutdown:
            return False
            
        # Check resource usage
        safety_status = self.safety_manager.get_safety_status()
        if safety_status.resource_usage.get("memory_percent", 0) > 80:
            return False
            
        return True
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics including workflow performance"""
        base_health = super().get_health_indicators()
        
        # Add workflow-specific health indicators
        workflow_health = {
            "workflow_executor": {
                "is_shutdown": self.workflow_executor._shutdown,
                "max_workers": self.workflow_executor._max_workers,
                "active_workflows": len(self.active_workflows)
            },
            "performance_metrics": {
                "average_execution_times": {
                    analyzer: sum(times) / len(times) if times else 0
                    for analyzer, times in self.execution_metrics.items()
                },
                "total_workflows_executed": len(self.workflow_results)
            }
        }
        
        base_health["workflow_health"] = workflow_health
        return base_health
        
    def _get_primary_responsibility(self) -> str:
        """Primary responsibility of the analysis orchestrator"""
        return "safe_readonly_analysis_workflow_coordination"
        
    def configure_analysis_parameters(self, **parameters) -> None:
        """
        Configure analysis parameters with safety validation
        
        Args:
            **parameters: Analysis configuration parameters
            
        Raises:
            SafetyViolationError: If parameters violate safety constraints
        """
        # Validate parameters are safe
        unsafe_params = ['write', 'modify', 'delete', 'update', 'create', 'install', 'remove']
        
        for key, value in parameters.items():
            key_lower = key.lower()
            if any(unsafe in key_lower for unsafe in unsafe_params):
                raise SafetyViolationError(f"Unsafe parameter detected: {key}")
                
            if isinstance(value, str) and any(unsafe in value.lower() for unsafe in unsafe_params):
                raise SafetyViolationError(f"Unsafe value detected in parameter {key}: {value}")
                
        # Store safe parameters
        self.analysis_parameters.update(parameters)
        self.logger.info(f"Updated analysis parameters: {list(parameters.keys())}")
        
    def create_analysis_workflow(
        self,
        workflow_id: str,
        analyzer_names: List[str],
        parallel_execution: bool = True,
        timeout_seconds: int = 300,
        retry_on_failure: bool = True
    ) -> AnalysisWorkflow:
        """
        Create a new analysis workflow configuration
        
        Args:
            workflow_id: Unique identifier for the workflow
            analyzer_names: List of analyzer names to execute
            parallel_execution: Whether to run analyzers in parallel
            timeout_seconds: Maximum execution time
            retry_on_failure: Whether to retry failed analyzers
            
        Returns:
            AnalysisWorkflow: Configured workflow
            
        Raises:
            SafetyViolationError: If workflow configuration violates safety
            ValueError: If analyzers are not registered
        """
        # Safety check
        if not is_safe_to_proceed(f"workflow_creation_{workflow_id}"):
            raise SafetyViolationError("Workflow creation blocked by safety system")
            
        # Validate analyzers are registered
        missing_analyzers = [name for name in analyzer_names if name not in self.registered_analyzers]
        if missing_analyzers:
            raise ValueError(f"Analyzers not registered: {missing_analyzers}")
            
        # Validate timeout is reasonable
        if timeout_seconds > 1800:  # 30 minutes max
            raise SafetyViolationError("Timeout too long - maximum 30 minutes allowed")
            
        workflow = AnalysisWorkflow(
            workflow_id=workflow_id,
            analyzer_names=analyzer_names,
            parallel_execution=parallel_execution,
            timeout_seconds=timeout_seconds,
            retry_on_failure=retry_on_failure
        )
        
        self.active_workflows[workflow_id] = workflow
        self.logger.info(f"Created workflow: {workflow_id} with analyzers: {analyzer_names}")
        
        return workflow
        
    def execute_workflow(self, workflow_id: str, **analysis_kwargs) -> WorkflowResult:
        """
        Execute an analysis workflow with full safety monitoring
        
        Args:
            workflow_id: ID of workflow to execute
            **analysis_kwargs: Parameters to pass to analyzers
            
        Returns:
            WorkflowResult: Results of workflow execution
            
        Raises:
            SafetyViolationError: If execution violates safety constraints
            ValueError: If workflow not found
        """
        # Safety pre-check
        if not is_safe_to_proceed(f"workflow_execution_{workflow_id}"):
            raise SafetyViolationError("Workflow execution blocked by safety system")
            
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
            
        workflow = self.active_workflows[workflow_id]
        start_time = datetime.now()
        
        self.logger.info(f"Starting workflow execution: {workflow_id}")
        
        try:
            if workflow.parallel_execution:
                result = self._execute_parallel_workflow(workflow, analysis_kwargs)
            else:
                result = self._execute_sequential_workflow(workflow, analysis_kwargs)
                
            # Record execution metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            for analyzer_name in workflow.analyzer_names:
                if analyzer_name not in self.execution_metrics:
                    self.execution_metrics[analyzer_name] = []
                self.execution_metrics[analyzer_name].append(execution_time)
                
            # Store result
            self.workflow_results[workflow_id] = result
            
            # Clean up active workflow
            del self.active_workflows[workflow_id]
            
            self.logger.info(f"Completed workflow: {workflow_id} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {workflow_id} - {e}")
            
            # Create safe failure result
            execution_time = (datetime.now() - start_time).total_seconds()
            failure_result = WorkflowResult(
                workflow_id=workflow_id,
                status=AnalysisStatus.FAILED,
                results={},
                execution_time=execution_time,
                errors=[f"Workflow execution failed: {str(e)}"],
                safety_validated=True,
                emergency_shutdown_available=True
            )
            
            self.workflow_results[workflow_id] = failure_result
            del self.active_workflows[workflow_id]
            
            return failure_result
            
    def _execute_parallel_workflow(self, workflow: AnalysisWorkflow, analysis_kwargs: Dict[str, Any]) -> WorkflowResult:
        """Execute workflow with parallel analyzer execution"""
        results = {}
        errors = []
        
        # Submit all analyzer tasks
        future_to_analyzer = {}
        for analyzer_name in workflow.analyzer_names:
            analyzer = self.registered_analyzers[analyzer_name]
            future = self.workflow_executor.submit(
                self._safe_analyzer_execution,
                analyzer,
                analysis_kwargs
            )
            future_to_analyzer[future] = analyzer_name
            
        # Collect results with timeout
        try:
            for future in as_completed(future_to_analyzer, timeout=workflow.timeout_seconds):
                analyzer_name = future_to_analyzer[future]
                try:
                    result = future.result()
                    results[analyzer_name] = result
                except Exception as e:
                    error_msg = f"Analyzer {analyzer_name} failed: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
                    
        except TimeoutError:
            errors.append(f"Workflow timed out after {workflow.timeout_seconds} seconds")
            # Cancel remaining futures
            for future in future_to_analyzer:
                future.cancel()
                
        # Determine overall status
        if not results:
            status = AnalysisStatus.FAILED
        elif errors:
            status = AnalysisStatus.PARTIAL_SUCCESS
        else:
            status = AnalysisStatus.SUCCESS
            
        return WorkflowResult(
            workflow_id=workflow.workflow_id,
            status=status,
            results=results,
            execution_time=0,  # Will be set by caller
            errors=errors,
            safety_validated=True,
            emergency_shutdown_available=True
        )
        
    def _execute_sequential_workflow(self, workflow: AnalysisWorkflow, analysis_kwargs: Dict[str, Any]) -> WorkflowResult:
        """Execute workflow with sequential analyzer execution"""
        results = {}
        errors = []
        
        for analyzer_name in workflow.analyzer_names:
            try:
                analyzer = self.registered_analyzers[analyzer_name]
                result = self._safe_analyzer_execution(analyzer, analysis_kwargs)
                results[analyzer_name] = result
                
            except Exception as e:
                error_msg = f"Analyzer {analyzer_name} failed: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
                
                # Stop on first failure if not retrying
                if not workflow.retry_on_failure:
                    break
                    
        # Determine overall status
        if not results:
            status = AnalysisStatus.FAILED
        elif errors:
            status = AnalysisStatus.PARTIAL_SUCCESS
        else:
            status = AnalysisStatus.SUCCESS
            
        return WorkflowResult(
            workflow_id=workflow.workflow_id,
            status=status,
            results=results,
            execution_time=0,  # Will be set by caller
            errors=errors,
            safety_validated=True,
            emergency_shutdown_available=True
        )
        
    def _safe_analyzer_execution(self, analyzer: BaseAnalyzer, analysis_kwargs: Dict[str, Any]) -> AnalysisResult:
        """Execute analyzer with safety monitoring"""
        # Merge global parameters with call-specific parameters
        safe_kwargs = {**self.analysis_parameters, **analysis_kwargs}
        
        # Execute with safety monitoring
        return analyzer.execute_safe_analysis(**safe_kwargs)
        
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                "workflow_id": workflow_id,
                "status": "active",
                "analyzer_names": workflow.analyzer_names,
                "parallel_execution": workflow.parallel_execution,
                "timeout_seconds": workflow.timeout_seconds
            }
        elif workflow_id in self.workflow_results:
            result = self.workflow_results[workflow_id]
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "result_status": result.status.value,
                "execution_time": result.execution_time,
                "analyzer_count": len(result.results),
                "error_count": len(result.errors)
            }
        else:
            return {
                "workflow_id": workflow_id,
                "status": "not_found"
            }
            
    def list_workflows(self) -> Dict[str, Any]:
        """List all workflows (active and completed)"""
        return {
            "active_workflows": list(self.active_workflows.keys()),
            "completed_workflows": list(self.workflow_results.keys()),
            "total_workflows": len(self.active_workflows) + len(self.workflow_results)
        }
        
    def cleanup_old_results(self, max_age_hours: int = 24) -> int:
        """Clean up old workflow results to prevent memory leaks"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        old_workflows = []
        for workflow_id, result in self.workflow_results.items():
            # Estimate result age from workflow_id if it contains timestamp
            try:
                if "_" in workflow_id:
                    timestamp_str = workflow_id.split("_")[-1]
                    if timestamp_str.isdigit():
                        result_time = datetime.fromtimestamp(int(timestamp_str))
                        if result_time < cutoff_time:
                            old_workflows.append(workflow_id)
            except (ValueError, OSError):
                # If we can't parse timestamp, keep the result
                continue
                
        # Remove old results
        for workflow_id in old_workflows:
            del self.workflow_results[workflow_id]
            
        if old_workflows:
            self.logger.info(f"Cleaned up {len(old_workflows)} old workflow results")
            
        self.last_cleanup_time = datetime.now()
        return len(old_workflows)
        
    def create_coordinated_workflow(
        self,
        workflow_id: str,
        analyzer_configs: List[Dict[str, Any]],
        aggregation_strategy: str = "merge",
        error_strategy: str = "continue_on_error"
    ) -> Dict[str, Any]:
        """
        Create a coordinated workflow with result aggregation
        
        Args:
            workflow_id: Unique workflow identifier
            analyzer_configs: List of analyzer configurations with dependencies
            aggregation_strategy: How to aggregate results (merge, prioritize, consensus, weighted)
            error_strategy: How to handle errors (fail_fast, continue_on_error, retry_failed, graceful_degradation)
            
        Returns:
            Dict containing workflow plan
            
        Raises:
            SafetyViolationError: If workflow violates safety constraints
        """
        # Safety check
        if not is_safe_to_proceed(f"coordinated_workflow_{workflow_id}"):
            raise SafetyViolationError("Coordinated workflow creation blocked by safety system")
            
        # Validate all analyzers are registered
        for config in analyzer_configs:
            analyzer_name = config.get("analyzer_name")
            if not analyzer_name:
                raise ValueError("analyzer_name required in config")
            if analyzer_name not in self.registered_analyzers:
                raise ValueError(f"Analyzer not registered: {analyzer_name}")
                
        # Create workflow plan
        workflow_plan = self.workflow_coordinator.create_workflow_plan(
            workflow_id=workflow_id,
            analyzer_configs=analyzer_configs,
            aggregation_strategy=aggregation_strategy,
            error_strategy=error_strategy
        )
        
        self.logger.info(f"Created coordinated workflow: {workflow_id} with {len(analyzer_configs)} analyzers")
        return workflow_plan
        
    def execute_coordinated_workflow(self, workflow_id: str) -> AggregatedResult:
        """
        Execute a coordinated workflow with full result aggregation
        
        Args:
            workflow_id: ID of workflow to execute
            
        Returns:
            AggregatedResult: Aggregated results from all workflow steps
            
        Raises:
            SafetyViolationError: If execution violates safety constraints
        """
        # Safety check
        if not is_safe_to_proceed(f"coordinated_execution_{workflow_id}"):
            raise SafetyViolationError("Coordinated workflow execution blocked by safety system")
            
        self.logger.info(f"Starting coordinated workflow execution: {workflow_id}")
        
        try:
            # Execute workflow with coordination
            result = self.workflow_coordinator.execute_workflow_plan(workflow_id, self)
            
            self.logger.info(f"Completed coordinated workflow: {workflow_id} - Status: {result.overall_status.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Coordinated workflow execution failed: {workflow_id} - {e}")
            raise
            
    def get_coordinated_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of coordinated workflow"""
        return self.workflow_coordinator.get_workflow_progress(workflow_id)
        
    def list_coordinated_workflows(self) -> Dict[str, Any]:
        """List all coordinated workflows"""
        active = list(self.workflow_coordinator.active_workflows.keys())
        completed = list(self.workflow_coordinator.completed_workflows.keys())
        
        return {
            "active_coordinated_workflows": active,
            "completed_coordinated_workflows": completed,
            "total_coordinated_workflows": len(active) + len(completed)
        }
        
    def configure_analysis_thresholds(self, **thresholds) -> None:
        """
        Configure analysis thresholds and parameters
        
        Args:
            **thresholds: Threshold configurations
            
        Raises:
            SafetyViolationError: If thresholds violate safety constraints
        """
        # Validate thresholds are safe
        for key, value in thresholds.items():
            if not isinstance(value, (int, float, bool, str)):
                raise SafetyViolationError(f"Unsafe threshold type for {key}: {type(value)}")
                
            # Check for reasonable limits
            if isinstance(value, (int, float)):
                if value < 0 or value > 10000:  # Reasonable bounds
                    raise SafetyViolationError(f"Threshold value out of safe range for {key}: {value}")
                    
        # Update configuration
        self.default_config.analysis_thresholds.update(thresholds)
        self.logger.info(f"Updated analysis thresholds: {list(thresholds.keys())}")
        
    def get_analysis_configuration(self) -> Dict[str, Any]:
        """Get current analysis configuration"""
        return {
            "default_config": {
                "timeout_seconds": self.default_config.timeout_seconds,
                "max_parallel_analyses": self.default_config.max_parallel_analyses,
                "resource_limits": self.default_config.resource_limits,
                "analysis_thresholds": self.default_config.analysis_thresholds
            },
            "analysis_parameters": self.analysis_parameters,
            "registered_analyzers": list(self.registered_analyzers.keys()),
            "workflow_coordinator_active": True
        }
        
    def validate_analyzer_configuration(self, analyzer_name: str) -> Dict[str, Any]:
        """
        Validate configuration of a specific analyzer
        
        Args:
            analyzer_name: Name of analyzer to validate
            
        Returns:
            Dict containing validation results
        """
        if analyzer_name not in self.registered_analyzers:
            return {
                "analyzer_name": analyzer_name,
                "is_valid": False,
                "error": "Analyzer not registered"
            }
            
        analyzer = self.registered_analyzers[analyzer_name]
        
        try:
            # Check analyzer health
            is_healthy = analyzer.is_healthy()
            
            # Get analyzer status
            status = analyzer.get_module_status()
            
            # Validate safety systems
            safety_status = analyzer.safety_manager.get_safety_status()
            
            return {
                "analyzer_name": analyzer_name,
                "is_valid": True,
                "is_healthy": is_healthy,
                "status": status,
                "safety_validated": safety_status.is_safe,
                "configuration_valid": True
            }
            
        except Exception as e:
            return {
                "analyzer_name": analyzer_name,
                "is_valid": False,
                "error": f"Configuration validation failed: {str(e)}"
            }
        
    def emergency_shutdown_all(self) -> None:
        """Emergency shutdown of all workflows and analyzers"""
        self.logger.critical("Emergency shutdown of AnalysisOrchestratorRM initiated")
        
        # Cancel all active workflows
        for workflow_id in list(self.active_workflows.keys()):
            self.logger.warning(f"Cancelling active workflow: {workflow_id}")
            del self.active_workflows[workflow_id]
            
        # Shutdown workflow coordinator
        if hasattr(self, 'workflow_coordinator'):
            for workflow_id in list(self.workflow_coordinator.active_workflows.keys()):
                self.logger.warning(f"Cancelling coordinated workflow: {workflow_id}")
                del self.workflow_coordinator.active_workflows[workflow_id]
        
        # Shutdown thread pool executor
        self.workflow_executor.shutdown(wait=False)
        
        # Call parent emergency shutdown
        super().emergency_shutdown_all()
        
        self.logger.critical("AnalysisOrchestratorRM emergency shutdown completed")
        
    def __del__(self):
        """Cleanup on destruction"""
        try:
            if hasattr(self, 'workflow_executor') and not self.workflow_executor._shutdown:
                self.workflow_executor.shutdown(wait=True)
        except Exception:
            pass  # Ignore cleanup errors during destruction