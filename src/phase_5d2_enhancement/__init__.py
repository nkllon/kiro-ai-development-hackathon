"""
Phase 5D2 Completion Enhancement System

A systematic framework for enhancing specification quality to meet Phase 5D2 completion criteria
and enable Phase 5D3 readiness. Focuses on the critical dimensions that prevent advancement.

Current State (Post-DAG):
- Overall Quality Score: 62.5 (target: 70+)
- Critical Gaps: 22.7% (target: <10%)
- Key Focus Areas: Problem Taxonomy (39.5), Cost Optimization (38.6), Scalability (43.8)

Target State:
- Overall Quality Score: 70+
- Critical Gaps: <10%
- Phase 5D3 Ready: True
"""

__version__ = "1.0.0"
__author__ = "Phase 5D2 Enhancement System"

# Core components
from .orchestration.enhancement_orchestrator import EnhancementOrchestrator
from .analysis.dimension_analyzer import DimensionAnalyzer
from .analysis.quality_validator import QualityValidator

# Enhancement engines
from .engines.problem_taxonomy_engine import ProblemTaxonomyEngine
from .engines.cost_optimization_engine import CostOptimizationEngine
from .engines.scalability_requirements_engine import ScalabilityRequirementsEngine
from .engines.generic_enhancement_engine import GenericEnhancementEngine

# Tracing and observability
from .tracing.jaeger_trace_manager import JaegerTraceManager

__all__ = [
    'EnhancementOrchestrator',
    'DimensionAnalyzer', 
    'QualityValidator',
    'ProblemTaxonomyEngine',
    'CostOptimizationEngine',
    'ScalabilityRequirementsEngine',
    'GenericEnhancementEngine',
    'JaegerTraceManager'
]