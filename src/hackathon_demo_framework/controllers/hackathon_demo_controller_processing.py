"""
Hackathon Demo Controller Processing

This module was extracted from hackathon_demo_controller.py
as part of RM-DDD compliance refactoring.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..models import SpecToCodeModel, SystematicSuperiorityModel, MultiAgentCollaborationModel, ProductionInfrastructureModel, Task, HumanInput, GKEConfig
from ..views import HackathonDemoView, DemoPhase, DemoContent

def create_spec_transformation(self, session_id: str, spec: str) -> TransformationResult:
    """Create a new spec-to-code transformation"""
    if session_id not in self.active_sessions:
        raise ValueError(f'Session {session_id} not found')
    model_result = self.spec_model.transform_spec_to_code(spec)
    transformation = TransformationResult(transformation_id=f"TRANS-{datetime.now().strftime('%Y%m%d%H%M%S')}", spec=spec, generated_code=model_result.generated_code, systematic_score=model_result.systematic_score, quality_metrics={'quality_level': model_result.quality_level.value, 'test_coverage': model_result.test_coverage, 'security_validation': model_result.security_validation, 'performance_metrics': model_result.performance_metrics}, learning_patterns=[{'pattern_id': pattern.pattern_id, 'pattern_type': pattern.pattern_type, 'confidence_score': pattern.confidence_score, 'improvement_factor': pattern.improvement_factor} for pattern in model_result.learning_patterns], created_at=datetime.now())
    self.transformation_history.append(transformation)
    self._update_session_progress(session_id, 0.1)
    self._log_interaction(session_id, 'transformation_created', {'transformation_id': transformation.transformation_id, 'spec': spec, 'systematic_score': model_result.systematic_score})
    return transformation
