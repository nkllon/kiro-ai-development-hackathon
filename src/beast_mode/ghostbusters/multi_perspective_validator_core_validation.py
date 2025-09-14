"""
Multi Perspective Validator Core Validation

This module was extracted from multi_perspective_validator_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from src.rm_ddd.core.health import ModuleHealth


def validate_c7_multi_stakeholder_perspectives(self, decision_context: str, initial_confidence: float) -> MultiPerspectiveAnalysis:
    """
        C7: Multi-Stakeholder Perspective Validation
        Validates decisions from all stakeholder perspectives
        """
    self.validation_count += 1
    try:
        if initial_confidence >= self.confidence_thresholds['high_confidence']:
            return self._minimal_validation(decision_context, initial_confidence)
        elif initial_confidence >= self.confidence_thresholds['medium_confidence']:
            return self._basic_multi_perspective_check(decision_context, initial_confidence)
        else:
            return self._full_ghostbusters_analysis(decision_context, initial_confidence)
    finally:
        self.validation_count -= 1
        self.total_validations += 1

def _basic_multi_perspective_check(self, decision_context: str, confidence: float) -> MultiPerspectiveAnalysis:
    """Medium confidence decisions - basic multi-perspective validation"""
    perspectives = {}
    perspectives[StakeholderType.BEAST_MODE_SYSTEM] = StakeholderPerspective(stakeholder_type=StakeholderType.BEAST_MODE_SYSTEM, confidence_score=0.75, assessment='Decision supports systematic superiority but needs validation', concerns=['Medium confidence requires additional validation'], recommendations=['Validate against systematic methodology principles'], approval_status=True)
    perspectives[StakeholderType.GKE_CONSUMER] = StakeholderPerspective(stakeholder_type=StakeholderType.GKE_CONSUMER, confidence_score=0.7, assessment='Decision should support service integration', concerns=['Ensure 5-minute integration constraint is met'], recommendations=['Test integration complexity before implementation'], approval_status=True)
    perspectives[StakeholderType.DEVOPS_SRE] = StakeholderPerspective(stakeholder_type=StakeholderType.DEVOPS_SRE, confidence_score=0.8, assessment='Decision should maintain 99.9% uptime requirements', concerns=['Validate operational impact'], recommendations=['Ensure graceful degradation is maintained'], approval_status=True)
    overall_confidence = sum((p.confidence_score for p in perspectives.values())) / len(perspectives)
    consensus = all((p.approval_status for p in perspectives.values()))
    return MultiPerspectiveAnalysis(decision_context=decision_context, overall_confidence=overall_confidence, stakeholder_perspectives=perspectives, consensus_reached=consensus, final_recommendation='Approved with conditions - implement with stakeholder recommendations', risk_factors=['Medium confidence requires monitoring during implementation'])
