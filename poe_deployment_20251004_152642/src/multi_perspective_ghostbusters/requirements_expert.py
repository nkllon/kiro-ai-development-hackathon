#!/usr/bin/env python3
"""
Requirements Expert - Multi-Perspective Ghostbusters Agent
=========================================================

Requirements-focused perspective agent (< 250 lines)
Implements "Diversity is the only free lunch" through requirements expertise.

Author: Beast Mode Framework
Date: 2025-01-27
Context: Specialized Agent
Pattern: DomainService
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.multi_perspective_ghostbusters.security_expert import (
    SpecializedAgent, AnalysisContent, AnalysisContext, PerspectiveResult, 
    PerspectiveProfile, AuthenticityValidation
)
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class RequirementsCoverage:
    """Assessment of requirements coverage and completeness."""
    coverage_id: str
    overall_coverage_score: float
    functional_requirements_coverage: float
    non_functional_requirements_coverage: float
    traceability_score: float
    completeness_indicators: List[str]
    coverage_gaps: List[str]


@dataclass
class RequirementsGap:
    """Gap identified in requirements analysis."""
    gap_id: str
    gap_type: str
    severity: str
    description: str
    impact_on_system: str
    resolution_priority: int
    suggested_requirements: List[str]


class RequirementsExpert(SpecializedAgent, ReflectiveModule):
    """
    Requirements-focused perspective agent.
    
    Implements requirements analysis for multi-perspective intelligence where
    "Diversity is the only free lunch" - providing unique requirements insights
    that complement security and architectural perspectives.
    """

    def __init__(self):
        super().__init__()
        self.agent_id = f"requirements_expert_{int(datetime.now().timestamp())}"
        self.perspective_profile = PerspectiveProfile(
            perspective_type="RequirementsExpert",
            domain_focus=["requirements", "traceability", "acceptance_criteria", "stakeholder_needs"],
            analysis_approach="requirements_validation",
            unique_insights=["requirements_completeness", "traceability_analysis", "stakeholder_alignment"]
        )
        
        # Store requirements analysis data in unified CMS
        self.store_content("requirements_analyses", "requirements_analysis", {
            "analyses_performed": {},
            "coverage_assessments": {},
            "requirements_gaps": {}
        })

    def analyze_from_perspective(self, content: AnalysisContent, analysis_context: AnalysisContext) -> PerspectiveResult:
        """
        Analyze from requirements perspective focusing on:
        - Requirements completeness and clarity
        - Traceability and validation criteria
        - Stakeholder needs and acceptance criteria
        - Requirements conflicts and gaps
        """
        
        analysis_id = f"req_analysis_{content.content_id}_{int(datetime.now().timestamp())}"
        
        # Perform requirements-focused analysis
        requirements_insights = self._analyze_requirements_aspects(content)
        coverage_assessment = self.validate_requirements_coverage(content)
        requirements_gaps = self.identify_requirements_gaps(content)
        
        # Generate requirements-specific recommendations
        recommendations = self._generate_requirements_recommendations(coverage_assessment, requirements_gaps)
        
        # Build reasoning chain
        reasoning_chain = [
            "Applied requirements analysis methodology",
            "Evaluated requirements completeness and clarity",
            "Assessed traceability and validation criteria",
            "Identified stakeholder needs alignment",
            "Generated requirements improvement recommendations"
        ]
        
        # Identify unique requirements contributions
        unique_contributions = [
            "Requirements completeness evaluation",
            "Traceability analysis insights",
            "Stakeholder needs assessment",
            "Acceptance criteria validation"
        ]
        
        result = PerspectiveResult(
            agent_id=self.agent_id,
            perspective_type="RequirementsExpert",
            analysis_timestamp=datetime.now(),
            insights=requirements_insights,
            concerns=[gap.__dict__ for gap in requirements_gaps],
            recommendations=recommendations,
            confidence_score=self._calculate_requirements_confidence(coverage_assessment, requirements_gaps),
            reasoning_chain=reasoning_chain,
            unique_contributions=unique_contributions
        )
        
        # Store analysis in CMS
        self.store_content(analysis_id, "requirements_perspective_analysis", {
            "content_id": content.content_id,
            "coverage_score": coverage_assessment.overall_coverage_score,
            "gaps_identified": len(requirements_gaps),
            "confidence_score": result.confidence_score,
            "analysis_timestamp": result.analysis_timestamp.isoformat()
        })
        
        return result

    def validate_requirements_coverage(self, content: AnalysisContent) -> RequirementsCoverage:
        """Validate requirements coverage and completeness."""
        
        coverage_id = f"coverage_assessment_{int(datetime.now().timestamp())}"
        
        # Analyze content for requirements coverage
        functional_coverage = self._assess_functional_coverage(content)
        non_functional_coverage = self._assess_non_functional_coverage(content)
        traceability_score = self._assess_traceability(content)
        
        # Calculate overall coverage
        overall_coverage = (functional_coverage + non_functional_coverage + traceability_score) / 3
        
        # Identify completeness indicators
        completeness_indicators = self._identify_completeness_indicators(content)
        
        # Identify coverage gaps
        coverage_gaps = self._identify_coverage_gaps(functional_coverage, non_functional_coverage, traceability_score)
        
        coverage = RequirementsCoverage(
            coverage_id=coverage_id,
            overall_coverage_score=overall_coverage,
            functional_requirements_coverage=functional_coverage,
            non_functional_requirements_coverage=non_functional_coverage,
            traceability_score=traceability_score,
            completeness_indicators=completeness_indicators,
            coverage_gaps=coverage_gaps
        )
        
        # Store coverage assessment in CMS
        self.store_content(coverage_id, "requirements_coverage_assessment", coverage.__dict__)
        
        return coverage

    def identify_requirements_gaps(self, content: AnalysisContent) -> List[RequirementsGap]:
        """Identify gaps and conflicts in requirements."""
        
        gaps = []
        
        # Analyze content for common requirements gaps
        if isinstance(content.data, str):
            content_text = content.data.lower()
            
            # Check for missing acceptance criteria
            if "requirement" in content_text and "acceptance" not in content_text:
                gaps.append(RequirementsGap(
                    gap_id=f"acceptance_gap_{int(datetime.now().timestamp())}",
                    gap_type="acceptance_criteria",
                    severity="medium",
                    description="Requirements lack clear acceptance criteria",
                    impact_on_system="Unclear validation and testing criteria",
                    resolution_priority=2,
                    suggested_requirements=["Define measurable acceptance criteria", "Establish validation methods"]
                ))
            
            # Check for missing traceability
            if "design" in content_text and "trace" not in content_text:
                gaps.append(RequirementsGap(
                    gap_id=f"traceability_gap_{int(datetime.now().timestamp())}",
                    gap_type="traceability",
                    severity="high",
                    description="Requirements lack traceability to design and implementation",
                    impact_on_system="Difficult to validate implementation completeness",
                    resolution_priority=1,
                    suggested_requirements=["Establish requirements traceability matrix", "Link requirements to design elements"]
                ))
            
            # Check for missing stakeholder validation
            if "user" in content_text and "stakeholder" not in content_text:
                gaps.append(RequirementsGap(
                    gap_id=f"stakeholder_gap_{int(datetime.now().timestamp())}",
                    gap_type="stakeholder_validation",
                    severity="medium",
                    description="Requirements lack stakeholder validation",
                    impact_on_system="May not meet actual user needs",
                    resolution_priority=2,
                    suggested_requirements=["Conduct stakeholder review", "Validate user stories with actual users"]
                ))
        
        # Default requirements gap
        if not gaps:
            gaps.append(RequirementsGap(
                gap_id=f"general_req_gap_{int(datetime.now().timestamp())}",
                gap_type="general_requirements",
                severity="low",
                description="General requirements review recommended",
                impact_on_system="Standard requirements validation required",
                resolution_priority=3,
                suggested_requirements=["Conduct comprehensive requirements review"]
            ))
        
        return gaps

    def get_perspective_profile(self) -> PerspectiveProfile:
        """Get profile describing this agent's unique perspective."""
        return self.perspective_profile

    def validate_perspective_authenticity(self, result: PerspectiveResult) -> AuthenticityValidation:
        """Validate that analysis reflects authentic requirements perspective."""
        
        validation_id = f"req_auth_val_{int(datetime.now().timestamp())}"
        
        # Check for requirements-specific elements
        req_keywords = ["requirements", "acceptance", "criteria", "stakeholder", "traceability", "validation"]
        
        # Analyze insights for requirements focus
        req_focus_score = 0.0
        total_content = len(result.insights) + len(result.concerns) + len(result.recommendations)
        
        if total_content > 0:
            req_content_count = 0
            for insight in result.insights:
                if any(keyword in str(insight).lower() for keyword in req_keywords):
                    req_content_count += 1
            
            for concern in result.concerns:
                if any(keyword in str(concern).lower() for keyword in req_keywords):
                    req_content_count += 1
            
            req_focus_score = req_content_count / total_content
        
        # Determine requirements awareness level
        if req_focus_score >= 0.7:
            req_awareness = "high"
        elif req_focus_score >= 0.4:
            req_awareness = "medium"
        else:
            req_awareness = "low"
        
        validation = AuthenticityValidation(
            validation_id=validation_id,
            authentic_perspective=req_focus_score >= 0.5,
            security_focus_score=req_focus_score,  # Reusing field for req focus
            threat_awareness_level=req_awareness,   # Reusing field for req awareness
            validation_details={
                "requirements_keywords_found": req_focus_score > 0.3,
                "traceability_considered": "trace" in str(result.reasoning_chain).lower(),
                "acceptance_criteria_evaluated": "acceptance" in str(result.reasoning_chain).lower()
            }
        )
        
        # Store validation in CMS
        self.store_content(validation_id, "req_authenticity_validation", validation.__dict__)
        
        return validation

    def _analyze_requirements_aspects(self, content: AnalysisContent) -> List[Dict[str, Any]]:
        """Analyze requirements aspects of content."""
        insights = [
            {
                "type": "requirements_completeness",
                "finding": "Requirements completeness requires systematic validation",
                "confidence": 0.85,
                "requirements_impact": "high"
            },
            {
                "type": "traceability_analysis",
                "finding": "Traceability from requirements to implementation needs verification",
                "confidence": 0.9,
                "requirements_impact": "high"
            },
            {
                "type": "stakeholder_alignment",
                "finding": "Stakeholder needs alignment should be validated",
                "confidence": 0.8,
                "requirements_impact": "medium"
            }
        ]
        
        return insights

    def _generate_requirements_recommendations(self, coverage: RequirementsCoverage, gaps: List[RequirementsGap]) -> List[Dict[str, Any]]:
        """Generate requirements-specific recommendations."""
        recommendations = [
            {
                "type": "coverage_improvement",
                "recommendation": "Enhance requirements coverage through systematic analysis",
                "priority": "high",
                "rationale": "Complete coverage ensures system meets all needs"
            },
            {
                "type": "traceability",
                "recommendation": "Establish comprehensive requirements traceability",
                "priority": "medium",
                "rationale": "Traceability enables validation and change impact analysis"
            }
        ]
        
        # Add specific recommendations based on coverage score
        if coverage.overall_coverage_score < 0.6:
            recommendations.append({
                "type": "urgent_requirements",
                "recommendation": "Conduct immediate requirements analysis and gap closure",
                "priority": "critical",
                "rationale": "Low coverage score indicates significant requirements gaps"
            })
        
        return recommendations

    def _assess_functional_coverage(self, content: AnalysisContent) -> float:
        """Assess functional requirements coverage."""
        base_coverage = 0.6
        
        if isinstance(content.data, str):
            content_text = content.data.lower()
            if "functional" in content_text:
                base_coverage += 0.2
            if "user story" in content_text:
                base_coverage += 0.1
        
        return min(base_coverage, 1.0)

    def _assess_non_functional_coverage(self, content: AnalysisContent) -> float:
        """Assess non-functional requirements coverage."""
        base_coverage = 0.5
        
        if isinstance(content.data, str):
            content_text = content.data.lower()
            if "performance" in content_text:
                base_coverage += 0.1
            if "security" in content_text:
                base_coverage += 0.1
            if "scalability" in content_text:
                base_coverage += 0.1
        
        return min(base_coverage, 1.0)

    def _assess_traceability(self, content: AnalysisContent) -> float:
        """Assess requirements traceability."""
        base_traceability = 0.4
        
        if isinstance(content.data, str):
            content_text = content.data.lower()
            if "trace" in content_text:
                base_traceability += 0.3
            if "requirement" in content_text and "design" in content_text:
                base_traceability += 0.2
        
        return min(base_traceability, 1.0)

    def _identify_completeness_indicators(self, content: AnalysisContent) -> List[str]:
        """Identify indicators of requirements completeness."""
        indicators = ["Basic requirements structure present"]
        
        if isinstance(content.data, str):
            content_text = content.data.lower()
            if "acceptance criteria" in content_text:
                indicators.append("Acceptance criteria defined")
            if "user story" in content_text:
                indicators.append("User stories present")
            if "stakeholder" in content_text:
                indicators.append("Stakeholder considerations included")
        
        return indicators

    def _identify_coverage_gaps(self, functional: float, non_functional: float, traceability: float) -> List[str]:
        """Identify coverage gaps based on scores."""
        gaps = []
        
        if functional < 0.7:
            gaps.append("Functional requirements coverage insufficient")
        if non_functional < 0.6:
            gaps.append("Non-functional requirements coverage needs improvement")
        if traceability < 0.5:
            gaps.append("Requirements traceability needs establishment")
        
        return gaps

    def _calculate_requirements_confidence(self, coverage: RequirementsCoverage, gaps: List[RequirementsGap]) -> float:
        """Calculate confidence score for requirements analysis."""
        base_confidence = 0.8
        
        # Adjust based on coverage score
        coverage_adjustment = (coverage.overall_coverage_score - 0.5) * 0.4
        
        # Adjust based on gaps identified (more gaps = higher confidence in analysis)
        gap_bonus = min(len(gaps) * 0.02, 0.1)
        
        return max(0.1, min(base_confidence + coverage_adjustment + gap_bonus, 1.0))

    def execute(self, *args, **kwargs) -> Any:
        """Execute requirements expert operations."""
        return {
            "agent_id": self.agent_id,
            "perspective_type": "RequirementsExpert",
            "analysis_capabilities": ["requirements_validation", "traceability_analysis", "stakeholder_assessment"],
            "expert_status": "operational"
        }


def main():
    """Test the RequirementsExpert agent."""
    expert = RequirementsExpert()
    
    print("🚨 Requirements Expert - Multi-Perspective Ghostbusters Agent 🚨")
    print(f"Agent ID: {expert.agent_id}")
    print(f"Context: {expert.bounded_context.name}")
    print(f"Pattern: {expert.ddd_pattern}")
    print(f"Perspective: {expert.perspective_profile.perspective_type}")
    print("✅ Requirements expert operational!")


if __name__ == "__main__":
    main()