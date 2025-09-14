from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

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
from src.rm_ddd.core.health import ModuleHealth


    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

