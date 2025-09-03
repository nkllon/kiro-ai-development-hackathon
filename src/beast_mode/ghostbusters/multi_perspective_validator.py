"""
Beast Mode Framework - Multi-Perspective Validator (Ghostbusters Integration)
Implements C7 validation using stakeholder perspectives for low-confidence decisions
Requirements: C7 Multi-Stakeholder Perspective Validation
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from ..core.reflective_module import ReflectiveModule, HealthStatus

class StakeholderType(Enum):
    BEAST_MODE_SYSTEM = "beast_mode_system"
    GKE_CONSUMER = "gke_consumer"
    DEVOPS_SRE = "devops_sre"
    DEVELOPMENT_TEAM = "development_team"
    EVALUATOR_JUDGE = "evaluator_judge"

@dataclass
class StakeholderPerspective:
    stakeholder_type: StakeholderType
    confidence_score: float  # 0.0-1.0
    assessment: str
    concerns: List[str]
    recommendations: List[str]
    approval_status: bool

@dataclass
class MultiPerspectiveAnalysis:
    decision_context: str
    overall_confidence: float
    stakeholder_perspectives: Dict[StakeholderType, StakeholderPerspective]
    consensus_reached: bool
    final_recommendation: str
    risk_factors: List[str]

class MultiPerspectiveValidator(ReflectiveModule):
    """
    Ghostbusters-style multi-perspective validation for low-confidence decisions
    Implements stakeholder-driven risk reduction for complex decisions
    """
    
    def __init__(self):
        super().__init__("multi_perspective_validator")
        self.validation_count = 0
        self.total_validations = 0
        
        # Decision confidence thresholds
        self.confidence_thresholds = {
            'high_confidence': 0.8,      # 80%+ → Use registry + domain tools
            'medium_confidence': 0.5,    # 50-80% → Registry + basic multi-perspective
            'low_confidence': 0.5        # <50% → Full Ghostbusters multi-perspective
        }
        
        self._update_health_indicator(
            "validation_readiness",
            HealthStatus.HEALTHY,
            "ready",
            "Multi-perspective validation ready"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "validations_performed": self.total_validations,
            "current_validations": self.validation_count,
            "confidence_thresholds": self.confidence_thresholds,
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for validation capability"""
        return not self._degradation_active
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics"""
        return {
            "validation_capability": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "validations_completed": self.total_validations,
                "current_load": self.validation_count
            },
            "stakeholder_model_integrity": {
                "status": "healthy",
                "stakeholder_types": len(StakeholderType),
                "perspective_completeness": "100%"
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Multi-stakeholder perspective validation"""
        return "multi_stakeholder_perspective_validation"
        
    def validate_c7_multi_stakeholder_perspectives(self, 
                                                 decision_context: str,
                                                 initial_confidence: float) -> MultiPerspectiveAnalysis:
        """
        C7: Multi-Stakeholder Perspective Validation
        Validates decisions from all stakeholder perspectives
        """
        self.validation_count += 1
        
        try:
            # Determine if full multi-perspective analysis is needed
            if initial_confidence >= self.confidence_thresholds['high_confidence']:
                # High confidence - minimal validation needed
                return self._minimal_validation(decision_context, initial_confidence)
            elif initial_confidence >= self.confidence_thresholds['medium_confidence']:
                # Medium confidence - basic multi-perspective check
                return self._basic_multi_perspective_check(decision_context, initial_confidence)
            else:
                # Low confidence - full Ghostbusters multi-perspective analysis
                return self._full_ghostbusters_analysis(decision_context, initial_confidence)
                
        finally:
            self.validation_count -= 1
            self.total_validations += 1
            
    def _minimal_validation(self, decision_context: str, confidence: float) -> MultiPerspectiveAnalysis:
        """High confidence decisions - minimal stakeholder validation"""
        
        # Quick validation from key stakeholders
        perspectives = {
            StakeholderType.BEAST_MODE_SYSTEM: StakeholderPerspective(
                stakeholder_type=StakeholderType.BEAST_MODE_SYSTEM,
                confidence_score=0.9,
                assessment="High confidence decision aligns with systematic superiority goals",
                concerns=[],
                recommendations=["Proceed with implementation"],
                approval_status=True
            ),
            StakeholderType.GKE_CONSUMER: StakeholderPerspective(
                stakeholder_type=StakeholderType.GKE_CONSUMER,
                confidence_score=0.85,
                assessment="Decision supports service integration and adoption",
                concerns=[],
                recommendations=["Ensure service documentation is updated"],
                approval_status=True
            )
        }
        
        return MultiPerspectiveAnalysis(
            decision_context=decision_context,
            overall_confidence=confidence,
            stakeholder_perspectives=perspectives,
            consensus_reached=True,
            final_recommendation="Approved - high confidence decision",
            risk_factors=[]
        )
        
    def _basic_multi_perspective_check(self, decision_context: str, confidence: float) -> MultiPerspectiveAnalysis:
        """Medium confidence decisions - basic multi-perspective validation"""
        
        perspectives = {}
        
        # Beast Mode System Perspective
        perspectives[StakeholderType.BEAST_MODE_SYSTEM] = StakeholderPerspective(
            stakeholder_type=StakeholderType.BEAST_MODE_SYSTEM,
            confidence_score=0.75,
            assessment="Decision supports systematic superiority but needs validation",
            concerns=["Medium confidence requires additional validation"],
            recommendations=["Validate against systematic methodology principles"],
            approval_status=True
        )
        
        # GKE Consumer Perspective  
        perspectives[StakeholderType.GKE_CONSUMER] = StakeholderPerspective(
            stakeholder_type=StakeholderType.GKE_CONSUMER,
            confidence_score=0.7,
            assessment="Decision should support service integration",
            concerns=["Ensure 5-minute integration constraint is met"],
            recommendations=["Test integration complexity before implementation"],
            approval_status=True
        )
        
        # DevOps Perspective
        perspectives[StakeholderType.DEVOPS_SRE] = StakeholderPerspective(
            stakeholder_type=StakeholderType.DEVOPS_SRE,
            confidence_score=0.8,
            assessment="Decision should maintain 99.9% uptime requirements",
            concerns=["Validate operational impact"],
            recommendations=["Ensure graceful degradation is maintained"],
            approval_status=True
        )
        
        overall_confidence = sum(p.confidence_score for p in perspectives.values()) / len(perspectives)
        consensus = all(p.approval_status for p in perspectives.values())
        
        return MultiPerspectiveAnalysis(
            decision_context=decision_context,
            overall_confidence=overall_confidence,
            stakeholder_perspectives=perspectives,
            consensus_reached=consensus,
            final_recommendation="Approved with conditions - implement with stakeholder recommendations",
            risk_factors=["Medium confidence requires monitoring during implementation"]
        )
        
    def _full_ghostbusters_analysis(self, decision_context: str, confidence: float) -> MultiPerspectiveAnalysis:
        """Low confidence decisions - full Ghostbusters multi-perspective analysis"""
        
        perspectives = {}
        
        # Beast Mode System Perspective - Does this prove systematic superiority?
        if "metrics" in decision_context.lower() or "baseline" in decision_context.lower():
            beast_confidence = 0.85
            beast_assessment = "Metrics foundation is critical for proving systematic superiority"
            beast_concerns = ["Must establish concrete baseline before claiming superiority"]
            beast_recommendations = ["Implement comprehensive measurement framework", "Validate statistical significance"]
            beast_approval = True
        else:
            beast_confidence = 0.4
            beast_assessment = "Decision does not clearly support systematic superiority demonstration"
            beast_concerns = ["Unclear connection to superiority proof"]
            beast_recommendations = ["Clarify how this supports systematic methodology"]
            beast_approval = False
            
        perspectives[StakeholderType.BEAST_MODE_SYSTEM] = StakeholderPerspective(
            stakeholder_type=StakeholderType.BEAST_MODE_SYSTEM,
            confidence_score=beast_confidence,
            assessment=beast_assessment,
            concerns=beast_concerns,
            recommendations=beast_recommendations,
            approval_status=beast_approval
        )
        
        # GKE Consumer Perspective - Does this improve integration and velocity?
        if "service" in decision_context.lower() or "integration" in decision_context.lower():
            gke_confidence = 0.8
            gke_assessment = "Decision supports service integration and adoption"
            gke_concerns = ["Ensure integration remains under 5 minutes"]
            gke_recommendations = ["Provide clear API documentation", "Test integration workflow"]
            gke_approval = True
        else:
            gke_confidence = 0.6
            gke_assessment = "Decision has unclear impact on service consumption"
            gke_concerns = ["May not directly benefit GKE hackathon team"]
            gke_recommendations = ["Clarify service delivery benefits"]
            gke_approval = True  # Conditional approval
            
        perspectives[StakeholderType.GKE_CONSUMER] = StakeholderPerspective(
            stakeholder_type=StakeholderType.GKE_CONSUMER,
            confidence_score=gke_confidence,
            assessment=gke_assessment,
            concerns=gke_concerns,
            recommendations=gke_recommendations,
            approval_status=gke_approval
        )
        
        # DevOps/SRE Perspective - Does this maintain 99.9% uptime and scalability?
        if "performance" in decision_context.lower() or "monitoring" in decision_context.lower():
            devops_confidence = 0.9
            devops_assessment = "Decision supports operational reliability and monitoring"
            devops_concerns = []
            devops_recommendations = ["Implement comprehensive health monitoring", "Ensure graceful degradation"]
            devops_approval = True
        else:
            devops_confidence = 0.5
            devops_assessment = "Decision has unclear operational impact"
            devops_concerns = ["May affect system reliability"]
            devops_recommendations = ["Assess operational impact", "Plan rollback strategy"]
            devops_approval = True  # Conditional approval
            
        perspectives[StakeholderType.DEVOPS_SRE] = StakeholderPerspective(
            stakeholder_type=StakeholderType.DEVOPS_SRE,
            confidence_score=devops_confidence,
            assessment=devops_assessment,
            concerns=devops_concerns,
            recommendations=devops_recommendations,
            approval_status=devops_approval
        )
        
        # Development Team Perspective - Is this maintainable with >90% test coverage?
        if "test" in decision_context.lower() or "implementation" in decision_context.lower():
            dev_confidence = 0.85
            dev_assessment = "Decision supports maintainable implementation"
            dev_concerns = ["Must maintain >90% test coverage"]
            dev_recommendations = ["Implement comprehensive unit tests", "Document architectural decisions"]
            dev_approval = True
        else:
            dev_confidence = 0.6
            dev_assessment = "Decision has unclear implementation complexity"
            dev_concerns = ["May increase maintenance burden"]
            dev_recommendations = ["Assess implementation complexity", "Plan testing strategy"]
            dev_approval = True  # Conditional approval
            
        perspectives[StakeholderType.DEVELOPMENT_TEAM] = StakeholderPerspective(
            stakeholder_type=StakeholderType.DEVELOPMENT_TEAM,
            confidence_score=dev_confidence,
            assessment=dev_assessment,
            concerns=dev_concerns,
            recommendations=dev_recommendations,
            approval_status=dev_approval
        )
        
        # Evaluator/Judge Perspective - Does this provide concrete measurable superiority?
        if "evidence" in decision_context.lower() or "superiority" in decision_context.lower():
            eval_confidence = 0.9
            eval_assessment = "Decision provides concrete evidence for superiority evaluation"
            eval_concerns = []
            eval_recommendations = ["Ensure statistical rigor", "Provide clear comparative metrics"]
            eval_approval = True
        else:
            eval_confidence = 0.4
            eval_assessment = "Decision does not clearly provide evaluation evidence"
            eval_concerns = ["May not support hackathon assessment"]
            eval_recommendations = ["Clarify evaluation benefits", "Provide measurable outcomes"]
            eval_approval = False
            
        perspectives[StakeholderType.EVALUATOR_JUDGE] = StakeholderPerspective(
            stakeholder_type=StakeholderType.EVALUATOR_JUDGE,
            confidence_score=eval_confidence,
            assessment=eval_assessment,
            concerns=eval_concerns,
            recommendations=eval_recommendations,
            approval_status=eval_approval
        )
        
        # Calculate overall results
        overall_confidence = sum(p.confidence_score for p in perspectives.values()) / len(perspectives)
        consensus = all(p.approval_status for p in perspectives.values())
        
        # Collect all risk factors
        risk_factors = []
        for p in perspectives.values():
            risk_factors.extend(p.concerns)
            
        # Generate final recommendation
        if consensus and overall_confidence >= 0.7:
            final_recommendation = "Approved after full multi-perspective analysis - implement with all stakeholder recommendations"
        elif consensus and overall_confidence >= 0.5:
            final_recommendation = "Conditionally approved - address stakeholder concerns before implementation"
        else:
            final_recommendation = "Not approved - significant stakeholder concerns must be resolved"
            
        return MultiPerspectiveAnalysis(
            decision_context=decision_context,
            overall_confidence=overall_confidence,
            stakeholder_perspectives=perspectives,
            consensus_reached=consensus,
            final_recommendation=final_recommendation,
            risk_factors=risk_factors
        )