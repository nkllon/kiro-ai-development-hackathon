"""
Orchestration Engine Validation

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
