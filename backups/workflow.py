"""
RM-RDI Analysis System - Workflow Coordination

OPERATOR SAFETY: Workflow coordination with result aggregation and error handling
All operations are READ-ONLY with emergency shutdown capabilities.
"""

from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from .data_models import AnalysisResult, AnalysisStatus
from .safety import get_safety_manager


class SafetyViolationError(Exception):
    """Raised when safety constraints are violated"""
    pass


class WorkflowStage(Enum):
    """Stages of workflow execution"""
    INITIALIZATION = "initialization"
    PRE_ANALYSIS = "pre_analysis"
    ANALYSIS_EXECUTION = "analysis_execution"
    RESULT_AGGREGATION = "result_aggregation"
    POST_PROCESSING = "post_processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    step_id: str
    analyzer_name: str
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 2
    
    
@dataclass
class StepResult:
    """Result of a workflow step execution"""
    step_id: str
    analyzer_name: str
    status: AnalysisStatus
    result: Optional[AnalysisResult] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    

@dataclass
class AggregatedResult:
    """Aggregated results from multiple analyzers"""
    workflow_id: str
    timestamp: datetime
    overall_status: AnalysisStatus
    step_results: Dict[str, StepResult]
    summary: Dict[str, Any]
    recommendations: List[str]
    safety_validated: bool = True
    emergency_shutdown_available: bool = True
    

class WorkflowCoordinator:
    """
    Coordinates workflow execution with result aggregation and error handling
    
    SAFETY GUARANTEES:
    - All operations are READ-ONLY
    - Graceful error handling without system impact
    - Emergency shutdown capability
    - Result validation and safety checks
    """
    
    def __init__(self):
        self.safety_manager = get_safety_manager()
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.completed_workflows: Dict[str, AggregatedResult] = {}
        
        # Result aggregation strategies
        self.aggregation_strategies: Dict[str, Callable] = {
            "merge": self._merge_results,
            "prioritize": self._prioritize_results,
            "consensus": self._consensus_results,
            "weighted": self._weighted_results
        }
        
        # Error handling strategies
        self.error_strategies: Dict[str, Callable] = {
            "fail_fast": self._fail_fast_strategy,
            "continue_on_error": self._continue_on_error_strategy,
            "retry_failed": self._retry_failed_strategy,
            "graceful_degradation": self._graceful_degradation_strategy
        }
        
    def create_workflow_plan(
        self,
        workflow_id: str,
        analyzer_configs: List[Dict[str, Any]],
        aggregation_strategy: str = "merge",
        error_strategy: str = "continue_on_error"
    ) -> Dict[str, Any]:
        """
        Create a workflow execution plan
        
        Args:
            workflow_id: Unique workflow identifier
            analyzer_configs: List of analyzer configurations
            aggregation_strategy: How to aggregate results
            error_strategy: How to handle errors
            
        Returns:
            Dict containing workflow plan
            
        Raises:
            SafetyViolationError: If workflow plan violates safety
        """
        # Safety validation
        if not self.safety_manager.validate_workflow_safety(workflow_id):
            raise SafetyViolationError(f"Workflow plan violates safety constraints: {workflow_id}")
            
        # Create workflow steps
        steps = []
        for i, config in enumerate(analyzer_configs):
            step = WorkflowStep(
                step_id=f"{workflow_id}_step_{i}",
                analyzer_name=config["analyzer_name"],
                dependencies=config.get("dependencies", []),
                parameters=config.get("parameters", {}),
                timeout_seconds=config.get("timeout_seconds", 300),
                max_retries=config.get("max_retries", 2)
            )
            steps.append(step)
            
        # Validate dependencies
        self._validate_dependencies(steps)
        
        # Create execution plan
        execution_plan = {
            "workflow_id": workflow_id,
            "steps": steps,
            "aggregation_strategy": aggregation_strategy,
            "error_strategy": error_strategy,
            "created_at": datetime.now(),
            "stage": WorkflowStage.INITIALIZATION,
            "safety_validated": True
        }
        
        self.active_workflows[workflow_id] = execution_plan
        return execution_plan
        
    def execute_workflow_plan(
        self,
        workflow_id: str,
        orchestrator_instance
    ) -> AggregatedResult:
        """
        Execute a workflow plan with full coordination
        
        Args:
            workflow_id: ID of workflow to execute
            orchestrator_instance: AnalysisOrchestratorRM instance
            
        Returns:
            AggregatedResult: Aggregated results from all steps
            
        Raises:
            SafetyViolationError: If execution violates safety
        """
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow plan not found: {workflow_id}")
            
        plan = self.active_workflows[workflow_id]
        steps = plan["steps"]
        
        # Update stage
        plan["stage"] = WorkflowStage.PRE_ANALYSIS
        
        try:
            # Execute steps based on dependencies
            step_results = self._execute_steps_with_dependencies(
                steps, 
                orchestrator_instance,
                plan["error_strategy"]
            )
            
            # Update stage
            plan["stage"] = WorkflowStage.RESULT_AGGREGATION
            
            # Aggregate results
            aggregated_result = self._aggregate_step_results(
                workflow_id,
                step_results,
                plan["aggregation_strategy"]
            )
            
            # Update stage
            plan["stage"] = WorkflowStage.POST_PROCESSING
            
            # Post-process results
            self._post_process_results(aggregated_result)
            
            # Mark as completed
            plan["stage"] = WorkflowStage.COMPLETED
            self.completed_workflows[workflow_id] = aggregated_result
            
            # Clean up active workflow
            del self.active_workflows[workflow_id]
            
            return aggregated_result
            
        except Exception as e:
            plan["stage"] = WorkflowStage.FAILED
            plan["error"] = str(e)
            
            # Create failure result
            failure_result = AggregatedResult(
                workflow_id=workflow_id,
                timestamp=datetime.now(),
                overall_status=AnalysisStatus.FAILED,
                step_results={},
                summary={"error": str(e)},
                recommendations=[
                    "Review workflow configuration",
                    "Check analyzer availability",
                    "Verify safety constraints"
                ],
                safety_validated=True,
                emergency_shutdown_available=True
            )
            
            self.completed_workflows[workflow_id] = failure_result
            del self.active_workflows[workflow_id]
            
            return failure_result
            
    def _validate_dependencies(self, steps: List[WorkflowStep]) -> None:
        """Validate step dependencies are valid"""
        step_ids = {step.step_id for step in steps}
        
        for step in steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise ValueError(f"Invalid dependency {dep} for step {step.step_id}")
                    
        # Check for circular dependencies
        self._check_circular_dependencies(steps)
        
    def _check_circular_dependencies(self, steps: List[WorkflowStep]) -> None:
        """Check for circular dependencies in workflow steps"""
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id: str, step_map: Dict[str, WorkflowStep]) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            step = step_map[step_id]
            for dep in step.dependencies:
                if dep not in visited:
                    if has_cycle(dep, step_map):
                        return True
                elif dep in rec_stack:
                    return True
                    
            rec_stack.remove(step_id)
            return False
            
        step_map = {step.step_id: step for step in steps}
        
        for step in steps:
            if step.step_id not in visited:
                if has_cycle(step.step_id, step_map):
                    raise ValueError(f"Circular dependency detected involving step {step.step_id}")
                    
    def _execute_steps_with_dependencies(
        self,
        steps: List[WorkflowStep],
        orchestrator_instance,
        error_strategy: str
    ) -> Dict[str, StepResult]:
        """Execute steps respecting dependencies"""
        step_map = {step.step_id: step for step in steps}
        results = {}
        completed = set()
        
        # Execute steps in dependency order
        while len(completed) < len(steps):
            ready_steps = [
                step for step in steps
                if step.step_id not in completed and
                all(dep in completed for dep in step.dependencies)
            ]
            
            if not ready_steps:
                # Check if we're stuck due to failed dependencies
                remaining_steps = [step for step in steps if step.step_id not in completed]
                raise RuntimeError(f"Cannot proceed - remaining steps have unmet dependencies: {[s.step_id for s in remaining_steps]}")
                
            # Execute ready steps
            for step in ready_steps:
                try:
                    result = self._execute_single_step(step, orchestrator_instance)
                    results[step.step_id] = result
                    completed.add(step.step_id)
                    
                except Exception as e:
                    # Handle error based on strategy
                    error_result = StepResult(
                        step_id=step.step_id,
                        analyzer_name=step.analyzer_name,
                        status=AnalysisStatus.FAILED,
                        error=str(e),
                        retry_count=step.retry_count
                    )
                    
                    if self._should_continue_on_error(error_strategy, step, e):
                        results[step.step_id] = error_result
                        completed.add(step.step_id)
                    else:
                        results[step.step_id] = error_result
                        raise
                        
        return results
        
    def _execute_single_step(
        self,
        step: WorkflowStep,
        orchestrator_instance
    ) -> StepResult:
        """Execute a single workflow step"""
        start_time = datetime.now()
        
        try:
            # Get analyzer
            if step.analyzer_name not in orchestrator_instance.registered_analyzers:
                raise ValueError(f"Analyzer not registered: {step.analyzer_name}")
                
            analyzer = orchestrator_instance.registered_analyzers[step.analyzer_name]
            
            # Execute analysis
            result = analyzer.execute_safe_analysis(**step.parameters)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return StepResult(
                step_id=step.step_id,
                analyzer_name=step.analyzer_name,
                status=result.status,
                result=result,
                execution_time=execution_time,
                retry_count=step.retry_count
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Retry if configured
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                return self._execute_single_step(step, orchestrator_instance)
                
            return StepResult(
                step_id=step.step_id,
                analyzer_name=step.analyzer_name,
                status=AnalysisStatus.FAILED,
                error=str(e),
                execution_time=execution_time,
                retry_count=step.retry_count
            )
            
    def _should_continue_on_error(
        self,
        error_strategy: str,
        step: WorkflowStep,
        error: Exception
    ) -> bool:
        """Determine if workflow should continue after step error"""
        if error_strategy == "fail_fast":
            return False
        elif error_strategy == "continue_on_error":
            return True
        elif error_strategy == "retry_failed":
            return step.retry_count >= step.max_retries
        elif error_strategy == "graceful_degradation":
            # Continue unless it's a safety violation
            return not isinstance(error, SafetyViolationError)
        else:
            return False
            
    def _aggregate_step_results(
        self,
        workflow_id: str,
        step_results: Dict[str, StepResult],
        aggregation_strategy: str
    ) -> AggregatedResult:
        """Aggregate results from all workflow steps"""
        # Determine overall status
        statuses = [result.status for result in step_results.values()]
        
        if all(status == AnalysisStatus.SUCCESS for status in statuses):
            overall_status = AnalysisStatus.SUCCESS
        elif any(status == AnalysisStatus.SUCCESS for status in statuses):
            overall_status = AnalysisStatus.PARTIAL_SUCCESS
        else:
            overall_status = AnalysisStatus.FAILED
            
        # Apply aggregation strategy
        aggregation_func = self.aggregation_strategies.get(aggregation_strategy, self._merge_results)
        
        # Extract analysis results
        analysis_results = [
            result.result for result in step_results.values()
            if result.result is not None
        ]
        
        summary = aggregation_func(analysis_results)
        
        # Generate recommendations
        recommendations = self._generate_workflow_recommendations(step_results, summary)
        
        return AggregatedResult(
            workflow_id=workflow_id,
            timestamp=datetime.now(),
            overall_status=overall_status,
            step_results=step_results,
            summary=summary,
            recommendations=recommendations,
            safety_validated=True,
            emergency_shutdown_available=True
        )
        
    def _merge_results(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Merge strategy: combine all results"""
        merged = {
            "total_analyses": len(results),
            "successful_analyses": len([r for r in results if r.status == AnalysisStatus.SUCCESS]),
            "findings": [],
            "metrics": {},
            "recommendations": []
        }
        
        for result in results:
            merged["findings"].extend(result.findings)
            merged["metrics"].update(result.metrics)
            merged["recommendations"].extend(result.recommendations)
            
        return merged
        
    def _prioritize_results(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Prioritize strategy: use highest priority results"""
        if not results:
            return {}
            
        # Sort by priority (assuming higher priority values are more important)
        sorted_results = sorted(results, key=lambda r: r.priority, reverse=True)
        primary_result = sorted_results[0]
        
        return {
            "primary_analysis": primary_result.analysis_types[0] if primary_result.analysis_types else "unknown",
            "findings": primary_result.findings,
            "metrics": primary_result.metrics,
            "recommendations": primary_result.recommendations,
            "secondary_analyses": len(sorted_results) - 1
        }
        
    def _consensus_results(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Consensus strategy: find common findings"""
        if not results:
            return {}
            
        # Find common findings
        all_findings = [set(r.findings) for r in results]
        common_findings = set.intersection(*all_findings) if all_findings else set()
        
        # Average metrics where possible
        all_metrics = {}
        for result in results:
            for key, value in result.metrics.items():
                if isinstance(value, (int, float)):
                    if key not in all_metrics:
                        all_metrics[key] = []
                    all_metrics[key].append(value)
                    
        averaged_metrics = {
            key: sum(values) / len(values)
            for key, values in all_metrics.items()
        }
        
        return {
            "consensus_findings": list(common_findings),
            "averaged_metrics": averaged_metrics,
            "analysis_count": len(results),
            "agreement_level": len(common_findings) / max(1, len(set().union(*all_findings)))
        }
        
    def _weighted_results(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Weighted strategy: weight results by confidence"""
        if not results:
            return {}
            
        total_weight = sum(r.confidence for r in results)
        if total_weight == 0:
            return self._merge_results(results)
            
        weighted_findings = []
        weighted_metrics = {}
        
        for result in results:
            weight = result.confidence / total_weight
            
            # Weight findings by confidence
            for finding in result.findings:
                weighted_findings.append(f"{finding} (confidence: {result.confidence:.2f})")
                
            # Weight metrics
            for key, value in result.metrics.items():
                if isinstance(value, (int, float)):
                    if key not in weighted_metrics:
                        weighted_metrics[key] = 0
                    weighted_metrics[key] += value * weight
                    
        return {
            "weighted_findings": weighted_findings,
            "weighted_metrics": weighted_metrics,
            "total_confidence": total_weight,
            "analysis_count": len(results)
        }
        
    def _generate_workflow_recommendations(
        self,
        step_results: Dict[str, StepResult],
        summary: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on workflow results"""
        recommendations = []
        
        # Check for failed steps
        failed_steps = [
            result for result in step_results.values()
            if result.status == AnalysisStatus.FAILED
        ]
        
        if failed_steps:
            recommendations.append(f"Review {len(failed_steps)} failed analysis steps")
            for failed in failed_steps:
                if failed.error:
                    recommendations.append(f"Address error in {failed.analyzer_name}: {failed.error}")
                    
        # Check execution times
        slow_steps = [
            result for result in step_results.values()
            if result.execution_time > 60  # More than 1 minute
        ]
        
        if slow_steps:
            recommendations.append(f"Optimize {len(slow_steps)} slow-running analyzers")
            
        # Add summary-based recommendations
        if "total_analyses" in summary and summary["total_analyses"] > 0:
            success_rate = summary.get("successful_analyses", 0) / summary["total_analyses"]
            if success_rate < 0.8:
                recommendations.append("Consider reviewing analyzer configurations - low success rate")
                
        return recommendations
        
    def _fail_fast_strategy(self, step: WorkflowStep, error: Exception) -> bool:
        """Fail fast strategy: stop on first error"""
        return False
        
    def _continue_on_error_strategy(self, step: WorkflowStep, error: Exception) -> bool:
        """Continue on error strategy: keep going despite errors"""
        return True
        
    def _retry_failed_strategy(self, step: WorkflowStep, error: Exception) -> bool:
        """Retry failed strategy: retry up to max retries"""
        return step.retry_count >= step.max_retries
        
    def _graceful_degradation_strategy(self, step: WorkflowStep, error: Exception) -> bool:
        """Graceful degradation strategy: continue unless safety violation"""
        return not isinstance(error, SafetyViolationError)
        
    def _post_process_results(self, aggregated_result: AggregatedResult) -> None:
        """Post-process aggregated results"""
        # Add metadata
        aggregated_result.summary["post_processing"] = {
            "processed_at": datetime.now().isoformat(),
            "total_execution_time": sum(
                result.execution_time for result in aggregated_result.step_results.values()
            ),
            "step_count": len(aggregated_result.step_results)
        }
        
        # Validate safety
        if not self._validate_result_safety(aggregated_result):
            raise SafetyViolationError("Aggregated result failed safety validation")
            
    def _validate_result_safety(self, result: AggregatedResult) -> bool:
        """Validate that aggregated result is safe"""
        # Check safety flags
        if not result.safety_validated or not result.emergency_shutdown_available:
            return False
            
        # Validate all step results
        for step_result in result.step_results.values():
            if step_result.result and not step_result.result.safety_validated:
                return False
                
        return True
        
    def get_workflow_progress(self, workflow_id: str) -> Dict[str, Any]:
        """Get progress information for active workflow"""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
            
        plan = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "stage": plan["stage"].value,
            "total_steps": len(plan["steps"]),
            "created_at": plan["created_at"].isoformat(),
            "safety_validated": plan.get("safety_validated", False)
        }