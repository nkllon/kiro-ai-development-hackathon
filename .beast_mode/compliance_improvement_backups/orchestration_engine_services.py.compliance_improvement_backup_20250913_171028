"""
Orchestration Engine Services

This module was extracted from orchestration_engine.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from ..models.dag_models import EcosystemDAG, MVPRoute, OptimizedExecution, OrchestrationPlan, ExecutionResult, ResourceRequirements, RiskFactor
from ..models.enums import ExecutionStatus, TaskStatus
from ..analysis.dependency_analyzer import DependencyAnalyzer, EcosystemAnalysisResult
from ..optimization.mvp_calculator import MVPRouteCalculator, MVPCriteria
from ..optimization.parallel_optimizer import ParallelOptimizer as ParallelExecutionOptimizer
from ..optimization.risk_assessor import RiskAssessor, RiskAssessmentResult
from ..optimization.phase_optimizer import PhaseOptimizer
from ..optimization.risk_assessor import RiskImpact

class OrchestrationEngine:
    """
    BEASTMASTER orchestration engine with EXTREME SYSTEMATIC PREJUDICE.
    
    Coordinates systematic dependency analysis, MVP route calculation,
    parallel execution optimization, and systematic quality monitoring
    to systematically annihilate ecosystem complexity.
    """

    def __init__(self, domain_context: str='beast_mode_dag_orchestration'):
        self.domain_context = domain_context
        self.dependency_analyzer = DependencyAnalyzer()
        self.mvp_calculator = MVPRouteCalculator()
        self.parallel_optimizer = ParallelExecutionOptimizer()
        self.risk_assessor = RiskAssessor()
        self.phase_optimizer = PhaseOptimizer()
        self.active_orchestrations: Dict[str, OrchestrationResult] = {}
        self.execution_history: List[OrchestrationResult] = []
        self.systematic_quality_threshold = 0.9
        self.performance_targets = {'analysis_time_seconds': 30, 'mvp_calculation_time_seconds': 10, 'optimization_time_seconds': 15}

    async def orchestrate_ecosystem_execution_with_extreme_prejudice(self, spec_directory: str, mvp_criteria: Optional[MVPCriteria]=None, resource_constraints: Optional[ResourceConstraints]=None) -> OrchestrationResult:
        """
        SYSTEMATICALLY ANNIHILATE ecosystem complexity with BEASTMASTER precision.
        
        Args:
            spec_directory: Directory containing specifications to orchestrate
            mvp_criteria: Optional MVP criteria (defaults will be used if not provided)
            resource_constraints: Optional resource constraints
            
        Returns:
            OrchestrationResult: Complete systematic orchestration with EXTREME quality
        """
        orchestration_id = f"beast_orchestration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if not Path(spec_directory).exists():
            raise ValueError(f'Specification directory not found: {spec_directory}')
        if mvp_criteria is None:
            mvp_criteria = self._create_default_mvp_criteria()
        if resource_constraints is None:
            resource_constraints = ResourceConstraints()
        try:
            print(f'🔍 PHASE 1: Systematic ecosystem analysis - {spec_directory}')
            ecosystem_analysis = await self.dependency_analyzer.analyze_complete_ecosystem(spec_directory)
            ecosystem_dag = ecosystem_analysis.ecosystem_dag
            print(f'🎯 PHASE 2: MVP route calculation with systematic optimization')
            mvp_route = await self.mvp_calculator.calculate_mvp_route(ecosystem_dag, mvp_criteria)
            print(f'⚡ PHASE 3: Parallel execution optimization with maximum efficiency')
            execution_plan = ExecutionPlan.from_mvp_route(mvp_route, ecosystem_analysis.constraint_graph)
            optimized_execution = await self.parallel_optimizer.optimize_parallel_execution_with_extreme_prejudice(execution_plan, resource_constraints)
            print(f'🛡️ PHASE 4: Risk assessment with systematic mitigation')
            risk_assessment = await self.risk_assessor.assess_systematic_risk_with_prejudice(mvp_route)
            systematic_quality_score = self._calculate_systematic_quality_score(ecosystem_analysis, mvp_route, optimized_execution, risk_assessment)
            recommendations = self._generate_systematic_recommendations(ecosystem_analysis, mvp_route, optimized_execution, risk_assessment)
            orchestration_result = OrchestrationResult(orchestration_id=orchestration_id, ecosystem_dag=ecosystem_dag, mvp_route=mvp_route, optimized_execution=optimized_execution, risk_assessment=risk_assessment, execution_plan=execution_plan, systematic_quality_score=systematic_quality_score, recommendations=recommendations, created_at=datetime.now())
            self.active_orchestrations[orchestration_id] = orchestration_result
            self.execution_history.append(orchestration_result)
            print(f'✅ ORCHESTRATION COMPLETE: {orchestration_id}')
            print(f'📊 Systematic Quality Score: {systematic_quality_score:.3f}')
            print(f'🎯 MVP Timeline: {mvp_route.estimated_timeline} weeks')
            print(f'⚡ Parallel Groups: {len(optimized_execution.parallel_groups)}')
            return orchestration_result
        except Exception as e:
            print(f'❌ ORCHESTRATION FAILED: {str(e)}')
            raise

    async def execute_orchestration_plan_with_monitoring(self, orchestration_id: str, execute_immediately: bool=False) -> ExecutionResult:
        """
        Execute orchestration plan with SYSTEMATIC monitoring and quality control.
        
        Args:
            orchestration_id: ID of orchestration to execute
            execute_immediately: Whether to start execution immediately
            
        Returns:
            ExecutionResult: Systematic execution results with quality metrics
        """
        if orchestration_id not in self.active_orchestrations:
            raise ValueError(f'Orchestration not found: {orchestration_id}')
        orchestration = self.active_orchestrations[orchestration_id]
        print(f'🚀 EXECUTING ORCHESTRATION: {orchestration_id}')
        execution_start = datetime.now()
        readiness_check = self._validate_execution_readiness(orchestration)
        if not readiness_check['ready']:
            raise ValueError(f"Execution not ready: {readiness_check['issues']}")
        completed_tasks = []
        failed_tasks = []
        for phase in orchestration.mvp_route.phases:
            print(f'📋 Executing Phase {phase.phase_number}: {phase.phase_name}')
            for task in phase.tasks:
                if task.completion_status == TaskStatus.COMPLETED:
                    completed_tasks.append(task.task_id)
                    print(f'  ✅ {task.task_name} (already completed)')
                elif execute_immediately:
                    completed_tasks.append(task.task_id)
                    print(f'  🔄 {task.task_name} (simulated execution)')
                else:
                    print(f'  📋 {task.task_name} (planned for execution)')
        execution_time = (datetime.now() - execution_start).total_seconds() / 60
        systematic_quality_score = orchestration.systematic_quality_score
        execution_result = ExecutionResult(execution_id=f'exec_{orchestration_id}', status=ExecutionStatus.COMPLETED if execute_immediately else ExecutionStatus.PLANNED, completed_tasks=completed_tasks, failed_tasks=failed_tasks, systematic_quality_score=systematic_quality_score, execution_time=int(execution_time), lessons_learned=self._extract_lessons_learned(orchestration))
        print(f'✅ EXECUTION RESULT: {execution_result.status.value}')
        print(f'📊 Tasks: {len(completed_tasks)} completed, {len(failed_tasks)} failed')
        return execution_result

    def get_orchestration_status(self, orchestration_id: str) -> Dict[str, Any]:
        """Get systematic status of orchestration."""
        if orchestration_id not in self.active_orchestrations:
            return {'error': f'Orchestration not found: {orchestration_id}'}
        orchestration = self.active_orchestrations[orchestration_id]
        total_tasks = len(orchestration.ecosystem_dag.tasks)
        completed_tasks = len([task for task in orchestration.ecosystem_dag.tasks if task.completion_status == TaskStatus.COMPLETED])
        progress_percentage = completed_tasks / total_tasks * 100 if total_tasks > 0 else 0
        return {'orchestration_id': orchestration_id, 'status': 'active', 'progress_percentage': progress_percentage, 'completed_tasks': completed_tasks, 'total_tasks': total_tasks, 'mvp_timeline_weeks': orchestration.mvp_route.estimated_timeline, 'success_probability': orchestration.mvp_route.success_probability, 'systematic_quality_score': orchestration.systematic_quality_score, 'risk_factors': len(orchestration.risk_assessment.risk_factors), 'parallel_groups': len(orchestration.optimized_execution.parallel_groups), 'created_at': orchestration.created_at.isoformat()}

    def list_active_orchestrations(self) -> List[Dict[str, Any]]:
        """List all active orchestrations with systematic summaries."""
        return [orchestration.get_summary() for orchestration in self.active_orchestrations.values()]

    def _create_default_mvp_criteria(self) -> MVPCriteria:
        """Create default MVP criteria with BEASTMASTER standards."""
        from ..optimization.risk_assessor import RiskImpact
        return MVPCriteria(required_deliverables=['Functional API', 'Core Framework', 'Basic Testing', 'Documentation', 'Working Examples'], success_metrics={'test_coverage': 0.8, 'performance_score': 0.7, 'quality_score': 0.9}, maximum_timeline=12, maximum_effort=1000, minimum_value_demonstration=['End-to-end workflow', 'Systematic quality validation', 'Performance benchmarks'], quality_gates={'systematic_score': 0.9, 'test_coverage': 0.8, 'performance': 0.7}, risk_tolerance=RiskImpact.MEDIUM)

    def _calculate_systematic_quality_score(self, ecosystem_analysis: EcosystemAnalysisResult, mvp_route: MVPRoute, optimized_execution: OptimizedExecution, risk_assessment: RiskAssessmentResult) -> float:
        """Calculate systematic quality score with BEASTMASTER precision."""
        analysis_score = min(1.0, ecosystem_analysis.ecosystem_dag.completion_percentage / 100.0 + 0.2)
        mvp_score = mvp_route.success_probability
        optimization_score = min(1.0, len(optimized_execution.parallel_groups) / 10.0 + 0.5)
        risk_score = max(0.1, 1.0 - risk_assessment.overall_risk_score)
        systematic_quality_score = 0.3 * analysis_score + 0.3 * mvp_score + 0.2 * optimization_score + 0.2 * risk_score
        return min(1.0, systematic_quality_score)

    def _generate_systematic_recommendations(self, ecosystem_analysis: EcosystemAnalysisResult, mvp_route: MVPRoute, optimized_execution: OptimizedExecution, risk_assessment: RiskAssessmentResult) -> List[str]:
        """Generate systematic recommendations with BEASTMASTER insights."""
        recommendations = []
        if ecosystem_analysis.ecosystem_dag.completion_percentage < 50:
            recommendations.append('🎯 Focus on completing foundation tasks before advanced features')
        if mvp_route.success_probability < 0.8:
            recommendations.append('⚠️ Consider scope reduction or timeline extension to improve success probability')
        if mvp_route.estimated_timeline > 10:
            recommendations.append('📅 Timeline is aggressive - consider parallel execution or additional resources')
        if len(optimized_execution.parallel_groups) < 3:
            recommendations.append('⚡ Limited parallelization opportunities - consider task restructuring')
        if optimized_execution.maximum_parallelism > 8:
            recommendations.append('👥 High parallelism requires strong coordination - ensure team communication')
        high_risk_factors = [r for r in risk_assessment.risk_factors if r.impact.value in ['high', 'critical']]
        if high_risk_factors:
            recommendations.append(f'🛡️ Address {len(high_risk_factors)} high-risk factors before execution')
        recommendations.extend(['🔍 Implement systematic progress monitoring throughout execution', '📊 Establish systematic quality gates at each phase boundary', '🔄 Plan systematic retrospectives for continuous improvement'])
        return recommendations

    def _validate_execution_readiness(self, orchestration: OrchestrationResult) -> Dict[str, Any]:
        """Validate systematic execution readiness."""
        issues = []
        if orchestration.systematic_quality_score < self.systematic_quality_threshold:
            issues.append(f'Systematic quality score {orchestration.systematic_quality_score:.3f} below threshold {self.systematic_quality_threshold}')
        critical_risks = [r for r in orchestration.risk_assessment.risk_factors if r.impact.value == 'critical']
        if critical_risks:
            issues.append(f'{len(critical_risks)} critical risk factors must be addressed')
        if orchestration.mvp_route.success_probability < 0.6:
            issues.append(f'MVP success probability {orchestration.mvp_route.success_probability:.3f} too low')
        return {'ready': len(issues) == 0, 'issues': issues, 'systematic_quality_score': orchestration.systematic_quality_score}

    def _extract_lessons_learned(self, orchestration: OrchestrationResult) -> List[str]:
        """Extract systematic lessons learned from orchestration."""
        lessons = []
        total_specs = len(orchestration.ecosystem_dag.specifications)
        total_tasks = len(orchestration.ecosystem_dag.tasks)
        if total_tasks > 100:
            lessons.append(f'Large ecosystem ({total_tasks} tasks) requires systematic coordination')
        if orchestration.mvp_route.estimated_timeline < 6:
            lessons.append('Aggressive timeline requires systematic risk mitigation')
        if len(orchestration.optimized_execution.parallel_groups) > 5:
            lessons.append('High parallelization achieved - coordination overhead managed systematically')
        if orchestration.risk_assessment.overall_risk_score > 0.7:
            lessons.append('High-risk scenario - systematic mitigation strategies essential')
        lessons.extend(['Systematic analysis enables informed decision-making', 'MVP optimization provides clear value delivery path', 'Risk assessment prevents systematic failures', 'Parallel optimization maximizes team efficiency'])
        return lessons

    async def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get systematic orchestration metrics and performance indicators."""
        total_orchestrations = len(self.active_orchestrations)
        active_count = sum((1 for o in self.active_orchestrations.values() if o.execution_status.value in ['PLANNED', 'RUNNING']))
        if total_orchestrations == 0:
            return {'total_orchestrations': 0, 'active_orchestrations': 0, 'average_systematic_quality': 0.0, 'average_mvp_timeline': 0.0, 'systematic_superiority_demonstrated': False}
        quality_scores = [o.systematic_quality_score for o in self.active_orchestrations.values()]
        mvp_timelines = [o.mvp_route.estimated_timeline for o in self.active_orchestrations.values() if o.mvp_route]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        avg_timeline = sum(mvp_timelines) / len(mvp_timelines) if mvp_timelines else 0.0
        return {'total_orchestrations': total_orchestrations, 'active_orchestrations': active_count, 'average_systematic_quality': avg_quality, 'average_mvp_timeline': avg_timeline, 'systematic_superiority_demonstrated': avg_quality > 0.8 and total_orchestrations > 0}
