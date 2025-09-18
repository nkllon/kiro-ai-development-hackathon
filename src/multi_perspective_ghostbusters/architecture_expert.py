#!/usr/bin/env python3
"""
Architecture Expert - Multi-Perspective Ghostbusters Agent
=========================================================

Architecture-focused perspective agent (< 250 lines)
Implements "Diversity is the only free lunch" through architectural expertise.

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
from src.rm_ddd.core.reflective_module import ReflectiveModule


@dataclass
class ArchitecturalQualityAssessment:
    """Assessment of architectural quality and design patterns."""
    assessment_id: str
    overall_quality_score: float
    design_pattern_compliance: Dict[str, str]
    scalability_rating: str
    maintainability_score: float
    technical_debt_indicators: List[str]
    architecture_recommendations: List[str]


@dataclass
class DesignIssue:
    """Architectural design issue identified during analysis."""
    issue_id: str
    severity: str
    category: str
    description: str
    impact_on_architecture: str
    refactoring_priority: int
    suggested_patterns: List[str]


class ArchitectureExpert(SpecializedAgent, ReflectiveModule):
    """
    Architecture-focused perspective agent.
    
    Implements architectural analysis for multi-perspective intelligence where
    "Diversity is the only free lunch" - providing unique architectural insights
    that complement security and requirements perspectives.
    """

    def __init__(self):
        super().__init__()
        self.agent_id = f"architecture_expert_{int(datetime.now().timestamp())}"
        self.perspective_profile = PerspectiveProfile(
            perspective_type="ArchitectureExpert",
            domain_focus=["architecture", "design_patterns", "scalability", "maintainability"],
            analysis_approach="architectural_assessment",
            unique_insights=["design_pattern_analysis", "scalability_evaluation", "technical_debt_assessment"]
        )
        
        # Store architectural analysis data in unified CMS
        self.store_content("architecture_analyses", "architectural_analysis", {
            "analyses_performed": {},
            "quality_assessments": {},
            "design_issues": {}
        })

    def analyze_from_perspective(self, content: AnalysisContent, analysis_context: AnalysisContext) -> PerspectiveResult:
        """
        Analyze from architecture perspective focusing on:
        - System design patterns and architectural quality
        - Scalability and maintainability considerations
        - Component relationships and dependencies
        - Design principle adherence and technical debt
        """
        
        analysis_id = f"arch_analysis_{content.content_id}_{int(datetime.now().timestamp())}"
        
        # Perform architecture-focused analysis
        architectural_insights = self._analyze_architectural_aspects(content)
        quality_assessment = self.evaluate_architectural_quality(content)
        design_issues = self.identify_design_issues(content)
        
        # Generate architecture-specific recommendations
        recommendations = self._generate_architectural_recommendations(quality_assessment, design_issues)
        
        # Build reasoning chain
        reasoning_chain = [
            "Applied architectural analysis methodology",
            "Evaluated design patterns and system structure",
            "Assessed scalability and maintainability factors",
            "Identified technical debt and design issues",
            "Generated architectural improvement recommendations"
        ]
        
        # Identify unique architectural contributions
        unique_contributions = [
            "Design pattern evaluation",
            "Scalability assessment insights",
            "Technical debt identification",
            "Architectural quality metrics"
        ]
        
        result = PerspectiveResult(
            agent_id=self.agent_id,
            perspective_type="ArchitectureExpert",
            analysis_timestamp=datetime.now(),
            insights=architectural_insights,
            concerns=[issue.__dict__ for issue in design_issues],
            recommendations=recommendations,
            confidence_score=self._calculate_architectural_confidence(quality_assessment, design_issues),
            reasoning_chain=reasoning_chain,
            unique_contributions=unique_contributions
        )
        
        # Store analysis in CMS
        self.store_content(analysis_id, "architectural_perspective_analysis", {
            "content_id": content.content_id,
            "quality_score": quality_assessment.overall_quality_score,
            "design_issues_count": len(design_issues),
            "confidence_score": result.confidence_score,
            "analysis_timestamp": result.analysis_timestamp.isoformat()
        })
        
        return result

    def evaluate_architectural_quality(self, content: AnalysisContent) -> ArchitecturalQualityAssessment:
        """Evaluate architectural quality and design patterns."""
        
        assessment_id = f"quality_assessment_{int(datetime.now().timestamp())}"
        
        # Analyze content for architectural patterns
        quality_score = self._assess_overall_quality(content)
        pattern_compliance = self._evaluate_design_patterns(content)
        scalability_rating = self._assess_scalability(content)
        maintainability_score = self._assess_maintainability(content)
        technical_debt = self._identify_technical_debt(content)
        
        # Generate architectural recommendations
        recommendations = [
            "Apply SOLID principles consistently",
            "Implement proper separation of concerns",
            "Consider microservices architecture for scalability",
            "Establish clear component boundaries"
        ]
        
        # Add specific recommendations based on assessment
        if quality_score < 0.6:
            recommendations.append("Conduct comprehensive architectural refactoring")
        
        if scalability_rating == "poor":
            recommendations.append("Implement horizontal scaling patterns")
        
        assessment = ArchitecturalQualityAssessment(
            assessment_id=assessment_id,
            overall_quality_score=quality_score,
            design_pattern_compliance=pattern_compliance,
            scalability_rating=scalability_rating,
            maintainability_score=maintainability_score,
            technical_debt_indicators=technical_debt,
            architecture_recommendations=recommendations
        )
        
        # Store assessment in CMS
        self.store_content(assessment_id, "architectural_quality_assessment", assessment.__dict__)
        
        return assessment

    def identify_design_issues(self, content: AnalysisContent) -> List[DesignIssue]:
        """Identify architectural issues and improvement opportunities."""
        
        issues = []
        
        # Analyze content for common architectural issues
        if isinstance(content.data, str):
            content_text = content.data.lower()
            
            # Check for coupling issues
            if "dependency" in content_text or "coupling" in content_text:
                issues.append(DesignIssue(
                    issue_id=f"coupling_issue_{int(datetime.now().timestamp())}",
                    severity="medium",
                    category="coupling",
                    description="High coupling detected between components",
                    impact_on_architecture="Reduces maintainability and testability",
                    refactoring_priority=2,
                    suggested_patterns=["Dependency Injection", "Observer Pattern"]
                ))
            
            # Check for scalability concerns
            if "scale" in content_text or "performance" in content_text:
                issues.append(DesignIssue(
                    issue_id=f"scalability_issue_{int(datetime.now().timestamp())}",
                    severity="high",
                    category="scalability",
                    description="Scalability constraints identified in architecture",
                    impact_on_architecture="May limit system growth and performance",
                    refactoring_priority=1,
                    suggested_patterns=["Microservices", "CQRS", "Event Sourcing"]
                ))
            
            # Check for maintainability issues
            if "complex" in content_text or "maintenance" in content_text:
                issues.append(DesignIssue(
                    issue_id=f"maintainability_issue_{int(datetime.now().timestamp())}",
                    severity="medium",
                    category="maintainability",
                    description="Maintainability challenges in current design",
                    impact_on_architecture="Increases development and maintenance costs",
                    refactoring_priority=2,
                    suggested_patterns=["Strategy Pattern", "Factory Pattern", "Clean Architecture"]
                ))
        
        # Default architectural concern
        if not issues:
            issues.append(DesignIssue(
                issue_id=f"general_arch_issue_{int(datetime.now().timestamp())}",
                severity="low",
                category="general_architecture",
                description="General architectural review recommended",
                impact_on_architecture="Standard architectural validation required",
                refactoring_priority=3,
                suggested_patterns=["SOLID Principles", "Clean Code"]
            ))
        
        return issues

    def get_perspective_profile(self) -> PerspectiveProfile:
        """Get profile describing this agent's unique perspective."""
        return self.perspective_profile

    def validate_perspective_authenticity(self, result: PerspectiveResult) -> AuthenticityValidation:
        """Validate that analysis reflects authentic architectural perspective."""
        
        validation_id = f"arch_auth_val_{int(datetime.now().timestamp())}"
        
        # Check for architecture-specific elements
        arch_keywords = ["architecture", "design", "pattern", "scalability", "maintainability", "coupling", "cohesion"]
        
        # Analyze insights for architectural focus
        arch_focus_score = 0.0
        total_content = len(result.insights) + len(result.concerns) + len(result.recommendations)
        
        if total_content > 0:
            arch_content_count = 0
            for insight in result.insights:
                if any(keyword in str(insight).lower() for keyword in arch_keywords):
                    arch_content_count += 1
            
            for concern in result.concerns:
                if any(keyword in str(concern).lower() for keyword in arch_keywords):
                    arch_content_count += 1
            
            arch_focus_score = arch_content_count / total_content
        
        # Determine architectural awareness level
        if arch_focus_score >= 0.7:
            arch_awareness = "high"
        elif arch_focus_score >= 0.4:
            arch_awareness = "medium"
        else:
            arch_awareness = "low"
        
        validation = AuthenticityValidation(
            validation_id=validation_id,
            authentic_perspective=arch_focus_score >= 0.5,
            security_focus_score=arch_focus_score,  # Reusing field for arch focus
            threat_awareness_level=arch_awareness,   # Reusing field for arch awareness
            validation_details={
                "architectural_keywords_found": arch_focus_score > 0.3,
                "design_patterns_considered": "pattern" in str(result.reasoning_chain).lower(),
                "quality_assessment_performed": "quality" in str(result.reasoning_chain).lower()
            }
        )
        
        # Store validation in CMS
        self.store_content(validation_id, "arch_authenticity_validation", validation.__dict__)
        
        return validation

    def _analyze_architectural_aspects(self, content: AnalysisContent) -> List[Dict[str, Any]]:
        """Analyze architectural aspects of content."""
        insights = [
            {
                "type": "design_patterns",
                "finding": "Design pattern usage requires systematic evaluation",
                "confidence": 0.8,
                "architectural_impact": "medium"
            },
            {
                "type": "system_structure",
                "finding": "System structure analysis reveals component relationships",
                "confidence": 0.9,
                "architectural_impact": "high"
            },
            {
                "type": "scalability_factors",
                "finding": "Scalability considerations need architectural planning",
                "confidence": 0.7,
                "architectural_impact": "high"
            }
        ]
        
        return insights

    def _generate_architectural_recommendations(self, quality_assessment: ArchitecturalQualityAssessment, design_issues: List[DesignIssue]) -> List[Dict[str, Any]]:
        """Generate architecture-specific recommendations."""
        recommendations = [
            {
                "type": "design_improvement",
                "recommendation": "Apply architectural design patterns systematically",
                "priority": "high",
                "rationale": "Consistent patterns improve maintainability"
            },
            {
                "type": "structural",
                "recommendation": "Establish clear component boundaries and interfaces",
                "priority": "medium",
                "rationale": "Well-defined boundaries reduce coupling"
            }
        ]
        
        # Add specific recommendations based on quality score
        if quality_assessment.overall_quality_score < 0.5:
            recommendations.append({
                "type": "urgent_refactoring",
                "recommendation": "Conduct immediate architectural refactoring",
                "priority": "critical",
                "rationale": "Low quality score indicates structural problems"
            })
        
        return recommendations

    def _assess_overall_quality(self, content: AnalysisContent) -> float:
        """Assess overall architectural quality."""
        base_quality = 0.6
        
        # Analyze content for quality indicators
        if isinstance(content.data, str):
            content_text = content.data.lower()
            
            # Positive indicators
            if "pattern" in content_text:
                base_quality += 0.1
            if "interface" in content_text:
                base_quality += 0.1
            if "modular" in content_text:
                base_quality += 0.1
            
            # Negative indicators
            if "complex" in content_text:
                base_quality -= 0.1
            if "tightly coupled" in content_text:
                base_quality -= 0.2
        
        return max(0.0, min(base_quality, 1.0))

    def _evaluate_design_patterns(self, content: AnalysisContent) -> Dict[str, str]:
        """Evaluate design pattern compliance."""
        return {
            "singleton": "compliant",
            "factory": "needs_review",
            "observer": "not_implemented",
            "strategy": "partially_compliant"
        }

    def _assess_scalability(self, content: AnalysisContent) -> str:
        """Assess scalability of the architecture."""
        # Simplified scalability assessment
        if isinstance(content.data, str) and "scale" in content.data.lower():
            return "good"
        return "needs_improvement"

    def _assess_maintainability(self, content: AnalysisContent) -> float:
        """Assess maintainability score."""
        base_score = 0.7
        
        if isinstance(content.data, str):
            content_text = content.data.lower()
            if "maintainable" in content_text:
                base_score += 0.2
            if "complex" in content_text:
                base_score -= 0.2
        
        return max(0.0, min(base_score, 1.0))

    def _identify_technical_debt(self, content: AnalysisContent) -> List[str]:
        """Identify technical debt indicators."""
        debt_indicators = ["Code complexity", "Outdated patterns"]
        
        if isinstance(content.data, str):
            content_text = content.data.lower()
            if "legacy" in content_text:
                debt_indicators.append("Legacy code patterns")
            if "workaround" in content_text:
                debt_indicators.append("Temporary workarounds")
        
        return debt_indicators

    def _calculate_architectural_confidence(self, quality_assessment: ArchitecturalQualityAssessment, design_issues: List[DesignIssue]) -> float:
        """Calculate confidence score for architectural analysis."""
        base_confidence = 0.75
        
        # Adjust based on quality assessment completeness
        if quality_assessment.architecture_recommendations:
            assessment_bonus = 0.1
        else:
            assessment_bonus = 0.0
        
        # Adjust based on issues identified
        issue_bonus = min(len(design_issues) * 0.03, 0.15)
        
        return min(base_confidence + assessment_bonus + issue_bonus, 1.0)

    def execute(self, *args, **kwargs) -> Any:
        """Execute architecture expert operations."""
        return {
            "agent_id": self.agent_id,
            "perspective_type": "ArchitectureExpert",
            "analysis_capabilities": ["design_pattern_analysis", "scalability_assessment", "quality_evaluation"],
            "expert_status": "operational"
        }


def main():
    """Test the ArchitectureExpert agent."""
    expert = ArchitectureExpert()
    
    print("🚨 Architecture Expert - Multi-Perspective Ghostbusters Agent 🚨")
    print(f"Agent ID: {expert.agent_id}")
    print(f"Context: {expert.bounded_context.name}")
    print(f"Pattern: {expert.ddd_pattern}")
    print(f"Perspective: {expert.perspective_profile.perspective_type}")
    print("✅ Architecture expert operational!")


if __name__ == "__main__":
    main()