"""
Core data models for the Hackathon Demo Framework.

These models define the structure for hackathon configurations, demo packages,
and all related components following systematic development principles.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path


class IsolationLevel(Enum):
    """Demo environment isolation levels"""
    CONTAINER = "container"
    VIRTUAL_ENV = "virtual_env"
    PROCESS = "process"
    NONE = "none"


class JudgePersonaType(Enum):
    """Types of hackathon judges"""
    TECHNICAL = "technical"
    BUSINESS = "business"
    DESIGN = "design"
    GENERAL = "general"
    ACADEMIC = "academic"


@dataclass
class JudgingCriterion:
    """Individual judging criterion with weight and optimization strategies"""
    criterion_name: str
    weight_percentage: float
    description: str
    optimization_strategies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not 0 <= self.weight_percentage <= 100:
            raise ValueError("Weight percentage must be between 0 and 100")


@dataclass
class HackathonConfig:
    """Complete hackathon configuration and requirements"""
    hackathon_name: str
    hackathon_id: str
    submission_deadline: datetime
    demo_time_limit: int  # minutes
    judging_criteria: List[JudgingCriterion]
    required_elements: List[str]
    theme_requirements: List[str] = field(default_factory=list)
    technical_requirements: List[str] = field(default_factory=list)
    platform_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.demo_time_limit <= 0:
            raise ValueError("Demo time limit must be positive")
        
        total_weight = sum(criterion.weight_percentage for criterion in self.judging_criteria)
        if abs(total_weight - 100.0) > 0.01:  # Allow small floating point errors
            raise ValueError(f"Judging criteria weights must sum to 100%, got {total_weight}%")


@dataclass
class JudgePersona:
    """Judge persona for engagement optimization"""
    persona_type: JudgePersonaType
    technical_depth_preference: float  # 0.0 = minimal, 1.0 = maximum
    engagement_preferences: List[str]
    attention_span_minutes: int
    key_interests: List[str] = field(default_factory=list)


@dataclass
class DemoScript:
    """Structured demo script with timing and content"""
    opening_hook: str  # 30 seconds - grab attention
    problem_statement: str  # 60 seconds - establish need
    solution_overview: str  # 90 seconds - present approach
    technical_demonstration: str  # 180 seconds - show it working
    systematic_excellence: str  # 60 seconds - highlight development maturity
    business_impact: str  # 60 seconds - show value proposition
    closing_call_to_action: str  # 30 seconds - memorable finish
    total_duration: int  # Target: 8-10 minutes with Q&A buffer
    backup_plans: List[str] = field(default_factory=list)
    timing_breakdown: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.timing_breakdown:
            self.timing_breakdown = {
                "opening_hook": 30,
                "problem_statement": 60,
                "solution_overview": 90,
                "technical_demonstration": 180,
                "systematic_excellence": 60,
                "business_impact": 60,
                "closing_call_to_action": 30
            }
        
        if self.total_duration == 0:
            self.total_duration = sum(self.timing_breakdown.values())


@dataclass
class SystematicEvidence:
    """Evidence of systematic development approach"""
    spec_driven_evidence: List[str]
    beast_mode_highlights: List[str]
    quality_metrics: Dict[str, float]
    development_maturity_indicators: List[str]
    competitive_advantages: List[str] = field(default_factory=list)


@dataclass
class TechnicalAssessment:
    """Technical implementation assessment results"""
    functionality_score: float
    code_quality_score: float
    documentation_score: float
    test_coverage_percentage: float
    installation_reliability: float
    demo_stability_score: float
    overall_technical_score: float
    critical_issues: List[str] = field(default_factory=list)
    improvement_recommendations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        scores = [
            self.functionality_score,
            self.code_quality_score,
            self.documentation_score,
            self.installation_reliability,
            self.demo_stability_score
        ]
        
        if self.overall_technical_score == 0:
            self.overall_technical_score = sum(scores) / len(scores)


@dataclass
class ComplianceAssessment:
    """Hackathon compliance validation results"""
    mandatory_requirements: Dict[str, bool]
    hackathon_specific_criteria: Dict[str, float]
    submission_format_compliance: bool
    deadline_compliance: bool
    team_eligibility: bool
    overall_compliance_score: float
    blocking_issues: List[str] = field(default_factory=list)
    warning_issues: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.overall_compliance_score == 0:
            # Calculate based on mandatory requirements
            passed_requirements = sum(1 for passed in self.mandatory_requirements.values() if passed)
            total_requirements = len(self.mandatory_requirements)
            
            if total_requirements > 0:
                base_score = (passed_requirements / total_requirements) * 100
                
                # Apply penalties for non-compliance
                if not self.submission_format_compliance:
                    base_score *= 0.8
                if not self.deadline_compliance:
                    base_score *= 0.5  # Major penalty for deadline issues
                if not self.team_eligibility:
                    base_score = 0  # Disqualifying
                
                self.overall_compliance_score = base_score


@dataclass
class DemoEnvironment:
    """Demo environment configuration and status"""
    environment_id: str
    isolation_level: IsolationLevel
    dependency_status: Dict[str, bool]
    backup_strategies: List[str]
    failure_scenarios: List[str]
    monitoring_config: Dict[str, Any]
    reliability_score: float = 0.0
    
    def __post_init__(self):
        if self.reliability_score == 0:
            # Calculate reliability based on dependency status
            if self.dependency_status:
                working_deps = sum(1 for status in self.dependency_status.values() if status)
                total_deps = len(self.dependency_status)
                self.reliability_score = (working_deps / total_deps) * 100 if total_deps > 0 else 100


@dataclass
class JudgeMaterials:
    """Materials prepared specifically for judge evaluation"""
    executive_summary: str
    technical_overview: str
    systematic_development_evidence: str
    competitive_analysis: str
    business_impact_summary: str
    demo_instructions: str
    quick_start_guide: str = ""
    troubleshooting_guide: str = ""


@dataclass
class PresentationMetrics:
    """Metrics for presentation effectiveness measurement"""
    timing_analysis: Dict[str, float]
    content_coverage: Dict[str, bool]
    engagement_indicators: Dict[str, float]
    technical_demonstration_effectiveness: float
    systematic_excellence_showcase: float
    overall_impact_score: float
    improvement_opportunities: List[str] = field(default_factory=list)


@dataclass
class DemoPackage:
    """Complete demo package ready for hackathon submission"""
    demo_script: DemoScript
    judge_materials: JudgeMaterials
    demo_environment: DemoEnvironment
    systematic_evidence: SystematicEvidence
    technical_assessment: TechnicalAssessment
    compliance_assessment: ComplianceAssessment
    presentation_metrics: Optional[PresentationMetrics] = None
    backup_plans: List[str] = field(default_factory=list)
    
    def is_submission_ready(self) -> bool:
        """Check if demo package is ready for hackathon submission"""
        return (
            self.technical_assessment.overall_technical_score >= 80.0 and
            self.compliance_assessment.overall_compliance_score >= 95.0 and
            self.demo_environment.reliability_score >= 90.0 and
            len(self.compliance_assessment.blocking_issues) == 0
        )
    
    def get_readiness_score(self) -> float:
        """Calculate overall submission readiness score"""
        scores = [
            self.technical_assessment.overall_technical_score,
            self.compliance_assessment.overall_compliance_score,
            self.demo_environment.reliability_score
        ]
        
        if self.presentation_metrics:
            scores.append(self.presentation_metrics.overall_impact_score)
        
        return sum(scores) / len(scores)


@dataclass
class ValidationResult:
    """Result of systematic validation process"""
    is_valid: bool
    score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)


# Template configurations for common hackathons
DEVPOST_HACKATHON_TEMPLATE = HackathonConfig(
    hackathon_name="DevPost Hackathon",
    hackathon_id="devpost-template",
    submission_deadline=datetime.now(),  # To be customized
    demo_time_limit=10,
    judging_criteria=[
        JudgingCriterion("Technical Implementation", 30.0, "Quality and innovation of technical solution"),
        JudgingCriterion("Business Impact", 25.0, "Potential real-world impact and market viability"),
        JudgingCriterion("Presentation Quality", 20.0, "Clarity and effectiveness of demo presentation"),
        JudgingCriterion("Innovation", 15.0, "Novelty and creativity of approach"),
        JudgingCriterion("Completeness", 10.0, "Completeness of implementation and documentation")
    ],
    required_elements=[
        "README.md with clear setup instructions",
        ".kiro directory with project structure",
        "Working demo or prototype",
        "Clear problem statement and solution description"
    ],
    platform_requirements={
        "repository": "public GitHub repository",
        "demo_video": "optional but recommended",
        "live_demo": "preferred for final judging"
    }
)

MLH_HACKATHON_TEMPLATE = HackathonConfig(
    hackathon_name="MLH Hackathon",
    hackathon_id="mlh-template", 
    submission_deadline=datetime.now(),  # To be customized
    demo_time_limit=5,  # MLH typically has shorter demo times
    judging_criteria=[
        JudgingCriterion("Technical Difficulty", 25.0, "Complexity and technical challenge overcome"),
        JudgingCriterion("Design", 25.0, "User experience and interface design quality"),
        JudgingCriterion("Usefulness", 25.0, "Practical value and problem-solving capability"),
        JudgingCriterion("Learning", 25.0, "New technologies learned and applied")
    ],
    required_elements=[
        "DevPost submission with all required fields",
        "Public GitHub repository",
        "Demo video (2-3 minutes)",
        "Team member contributions documented"
    ],
    theme_requirements=["Must align with hackathon theme"],
    technical_requirements=["Must use at least one sponsor technology"]
)