"""
Demo Script Generator for Hackathon Demo Framework.

Generates structured demo scripts with timing optimization, story arc development,
and technical demonstration sequences optimized for hackathon judging.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from ..models import (
    DemoScript,
    HackathonConfig,
    SystematicEvidence,
    TechnicalAssessment,
)


class StoryArcType(Enum):
    """Types of story arcs for demo presentations."""

    PROBLEM_SOLUTION = "problem_solution"
    HERO_JOURNEY = "hero_journey"
    BEFORE_AFTER = "before_after"
    FEATURE_SHOWCASE = "feature_showcase"
    TECHNICAL_DEEP_DIVE = "technical_deep_dive"


class DemoSection(Enum):
    """Demo script sections."""

    OPENING_HOOK = "opening_hook"
    PROBLEM_STATEMENT = "problem_statement"
    SOLUTION_OVERVIEW = "solution_overview"
    TECHNICAL_DEMONSTRATION = "technical_demonstration"
    SYSTEMATIC_EXCELLENCE = "systematic_excellence"
    BUSINESS_IMPACT = "business_impact"
    CLOSING_CALL_TO_ACTION = "closing_call_to_action"


@dataclass
class DemoTemplate:
    """Template for demo script generation."""

    name: str
    story_arc: StoryArcType
    target_duration: int  # seconds
    section_weights: Dict[DemoSection, float]  # Percentage of total time
    key_messages: List[str]
    backup_strategies: List[str]


@dataclass
class ContentGuidelines:
    """Guidelines for demo content generation."""

    max_technical_depth: float  # 0.0 = minimal, 1.0 = maximum
    judge_personas: List[str]  # Types of judges expected
    key_differentiators: List[str]
    must_include_elements: List[str]
    avoid_elements: List[str]


class DemoScriptGenerator:
    """
    Generates structured demo scripts optimized for hackathon presentations.

    Creates compelling narratives with proper timing, technical depth calibration,
    and systematic excellence showcase tailored to hackathon judging criteria.
    """

    def __init__(self, project_path: Path):
        """
        Initialize the demo script generator.

        Args:
            project_path: Path to the project being presented
        """
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)

        # Demo templates for different hackathon types
        self.templates = {
            "devpost_standard": DemoTemplate(
                name="DevPost Standard",
                story_arc=StoryArcType.PROBLEM_SOLUTION,
                target_duration=600,  # 10 minutes
                section_weights={
                    DemoSection.OPENING_HOOK: 0.05,
                    DemoSection.PROBLEM_STATEMENT: 0.15,
                    DemoSection.SOLUTION_OVERVIEW: 0.20,
                    DemoSection.TECHNICAL_DEMONSTRATION: 0.35,
                    DemoSection.SYSTEMATIC_EXCELLENCE: 0.10,
                    DemoSection.BUSINESS_IMPACT: 0.10,
                    DemoSection.CLOSING_CALL_TO_ACTION: 0.05,
                },
                key_messages=[
                    "Clear problem identification",
                    "Innovative technical solution",
                    "Systematic development approach",
                    "Real-world impact potential",
                ],
                backup_strategies=[
                    "Pre-recorded demo video",
                    "Screenshot walkthrough",
                    "Architecture diagram explanation",
                ],
            ),
            "mlh_quick": DemoTemplate(
                name="MLH Quick Pitch",
                story_arc=StoryArcType.FEATURE_SHOWCASE,
                target_duration=300,  # 5 minutes
                section_weights={
                    DemoSection.OPENING_HOOK: 0.10,
                    DemoSection.PROBLEM_STATEMENT: 0.15,
                    DemoSection.SOLUTION_OVERVIEW: 0.15,
                    DemoSection.TECHNICAL_DEMONSTRATION: 0.45,
                    DemoSection.SYSTEMATIC_EXCELLENCE: 0.05,
                    DemoSection.BUSINESS_IMPACT: 0.05,
                    DemoSection.CLOSING_CALL_TO_ACTION: 0.05,
                },
                key_messages=[
                    "Quick problem hook",
                    "Live demo focus",
                    "Technical innovation",
                    "Learning showcase",
                ],
                backup_strategies=[
                    "Quick screenshot sequence",
                    "Code walkthrough",
                    "Feature highlight reel",
                ],
            ),
            "technical_deep_dive": DemoTemplate(
                name="Technical Deep Dive",
                story_arc=StoryArcType.TECHNICAL_DEEP_DIVE,
                target_duration=900,  # 15 minutes
                section_weights={
                    DemoSection.OPENING_HOOK: 0.05,
                    DemoSection.PROBLEM_STATEMENT: 0.10,
                    DemoSection.SOLUTION_OVERVIEW: 0.15,
                    DemoSection.TECHNICAL_DEMONSTRATION: 0.40,
                    DemoSection.SYSTEMATIC_EXCELLENCE: 0.20,
                    DemoSection.BUSINESS_IMPACT: 0.05,
                    DemoSection.CLOSING_CALL_TO_ACTION: 0.05,
                },
                key_messages=[
                    "Technical complexity mastery",
                    "Systematic architecture",
                    "Development excellence",
                    "Scalable implementation",
                ],
                backup_strategies=[
                    "Architecture deep dive",
                    "Code quality showcase",
                    "Systematic process demonstration",
                ],
            ),
        }

        self.logger.info(f"Demo script generator initialized for {self.project_path}")

    def generate_demo_script(
        self,
        hackathon_config: HackathonConfig,
        systematic_evidence: SystematicEvidence,
        technical_assessment: TechnicalAssessment,
        template_name: str = "devpost_standard",
        content_guidelines: Optional[ContentGuidelines] = None,
    ) -> DemoScript:
        """
        Generate a complete demo script optimized for the hackathon.

        Args:
            hackathon_config: Hackathon configuration and judging criteria
            systematic_evidence: Evidence of systematic development
            technical_assessment: Technical implementation assessment
            template_name: Demo template to use
            content_guidelines: Content generation guidelines

        Returns:
            Complete demo script with timing and content
        """
        self.logger.info(f"Generating demo script using template: {template_name}")

        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")

        template = self.templates[template_name]

        # Apply hackathon-specific timing constraints
        target_duration = min(
            template.target_duration, hackathon_config.demo_time_limit * 60
        )

        # Generate content for each section
        script_content = self._generate_script_content(
            template,
            hackathon_config,
            systematic_evidence,
            technical_assessment,
            content_guidelines,
        )

        # Calculate timing breakdown
        timing_breakdown = self._calculate_timing_breakdown(template, target_duration)

        # Create demo script
        demo_script = DemoScript(
            opening_hook=script_content[DemoSection.OPENING_HOOK],
            problem_statement=script_content[DemoSection.PROBLEM_STATEMENT],
            solution_overview=script_content[DemoSection.SOLUTION_OVERVIEW],
            technical_demonstration=script_content[DemoSection.TECHNICAL_DEMONSTRATION],
            systematic_excellence=script_content[DemoSection.SYSTEMATIC_EXCELLENCE],
            business_impact=script_content[DemoSection.BUSINESS_IMPACT],
            closing_call_to_action=script_content[DemoSection.CLOSING_CALL_TO_ACTION],
            total_duration=target_duration,
            timing_breakdown=timing_breakdown,
            backup_plans=template.backup_strategies.copy(),
        )

        self.logger.info(f"Demo script generated. Duration: {target_duration}s")
        return demo_script

    def optimize_for_judges(
        self, demo_script: DemoScript, judging_criteria: List, judge_personas: List[str]
    ) -> DemoScript:
        """
        Optimize demo script for specific judges and criteria.

        Args:
            demo_script: Original demo script
            judging_criteria: Hackathon judging criteria
            judge_personas: Types of judges (technical, business, etc.)

        Returns:
            Optimized demo script
        """
        self.logger.info("Optimizing demo script for judge engagement")

        # Analyze judging criteria weights
        criteria_weights = self._analyze_judging_criteria(judging_criteria)

        # Adjust content emphasis based on criteria
        optimized_content = self._optimize_content_for_criteria(
            demo_script, criteria_weights, judge_personas
        )

        # Create optimized script
        optimized_script = DemoScript(
            opening_hook=optimized_content[DemoSection.OPENING_HOOK],
            problem_statement=optimized_content[DemoSection.PROBLEM_STATEMENT],
            solution_overview=optimized_content[DemoSection.SOLUTION_OVERVIEW],
            technical_demonstration=optimized_content[
                DemoSection.TECHNICAL_DEMONSTRATION
            ],
            systematic_excellence=optimized_content[DemoSection.SYSTEMATIC_EXCELLENCE],
            business_impact=optimized_content[DemoSection.BUSINESS_IMPACT],
            closing_call_to_action=optimized_content[
                DemoSection.CLOSING_CALL_TO_ACTION
            ],
            total_duration=demo_script.total_duration,
            timing_breakdown=demo_script.timing_breakdown.copy(),
            backup_plans=demo_script.backup_plans.copy(),
        )

        return optimized_script

    def create_story_arc(
        self, arc_type: StoryArcType, project_context: Dict[str, Any]
    ) -> Dict[DemoSection, str]:
        """
        Create a compelling story arc for the demo.

        Args:
            arc_type: Type of story arc to create
            project_context: Context about the project

        Returns:
            Story arc content for each demo section
        """
        if arc_type == StoryArcType.PROBLEM_SOLUTION:
            return self._create_problem_solution_arc(project_context)
        elif arc_type == StoryArcType.HERO_JOURNEY:
            return self._create_hero_journey_arc(project_context)
        elif arc_type == StoryArcType.BEFORE_AFTER:
            return self._create_before_after_arc(project_context)
        elif arc_type == StoryArcType.FEATURE_SHOWCASE:
            return self._create_feature_showcase_arc(project_context)
        elif arc_type == StoryArcType.TECHNICAL_DEEP_DIVE:
            return self._create_technical_deep_dive_arc(project_context)
        else:
            raise ValueError(f"Unknown story arc type: {arc_type}")

    def generate_backup_strategies(
        self, demo_script: DemoScript, technical_assessment: TechnicalAssessment
    ) -> List[str]:
        """
        Generate backup strategies for demo failures.

        Args:
            demo_script: Demo script to create backups for
            technical_assessment: Technical assessment of the project

        Returns:
            List of backup strategies
        """
        backup_strategies = []

        # Technical demo backups
        if technical_assessment.demo_stability_score < 90:
            backup_strategies.extend(
                [
                    "Pre-recorded demo video showing full functionality",
                    "Screenshot sequence with narrated walkthrough",
                    "Live code review highlighting key implementations",
                ]
            )

        # Network/connectivity backups
        backup_strategies.extend(
            [
                "Offline demo environment with local data",
                "Static presentation with architecture diagrams",
                "Code walkthrough focusing on systematic development",
            ]
        )

        # Time constraint backups
        backup_strategies.extend(
            [
                "Condensed 3-minute version focusing on core value",
                "Feature highlight reel with key differentiators",
                "Systematic excellence showcase with development maturity",
            ]
        )

        return backup_strategies

    # Private methods for implementation

    def _generate_script_content(
        self,
        template: DemoTemplate,
        hackathon_config: HackathonConfig,
        systematic_evidence: SystematicEvidence,
        technical_assessment: TechnicalAssessment,
        content_guidelines: Optional[ContentGuidelines],
    ) -> Dict[DemoSection, str]:
        """Generate content for each demo section."""

        project_context = {
            "hackathon_name": hackathon_config.hackathon_name,
            "judging_criteria": hackathon_config.judging_criteria,
            "systematic_evidence": systematic_evidence,
            "technical_assessment": technical_assessment,
            "project_path": self.project_path,
        }

        # Create story arc
        story_content = self.create_story_arc(template.story_arc, project_context)

        # Enhance with systematic evidence
        enhanced_content = self._enhance_with_systematic_evidence(
            story_content, systematic_evidence
        )

        # Apply content guidelines if provided
        if content_guidelines:
            enhanced_content = self._apply_content_guidelines(
                enhanced_content, content_guidelines
            )

        return enhanced_content

    def _calculate_timing_breakdown(
        self, template: DemoTemplate, target_duration: int
    ) -> Dict[str, int]:
        """Calculate timing for each demo section."""
        timing_breakdown = {}

        for section, weight in template.section_weights.items():
            section_duration = int(target_duration * weight)
            timing_breakdown[section.value] = section_duration

        return timing_breakdown

    def _create_problem_solution_arc(
        self, context: Dict[str, Any]
    ) -> Dict[DemoSection, str]:
        """Create problem-solution story arc."""
        return {
            DemoSection.OPENING_HOOK: self._generate_opening_hook(context),
            DemoSection.PROBLEM_STATEMENT: self._generate_problem_statement(context),
            DemoSection.SOLUTION_OVERVIEW: self._generate_solution_overview(context),
            DemoSection.TECHNICAL_DEMONSTRATION: self._generate_technical_demo(context),
            DemoSection.SYSTEMATIC_EXCELLENCE: self._generate_systematic_showcase(
                context
            ),
            DemoSection.BUSINESS_IMPACT: self._generate_business_impact(context),
            DemoSection.CLOSING_CALL_TO_ACTION: self._generate_closing_cta(context),
        }

    def _create_hero_journey_arc(
        self, context: Dict[str, Any]
    ) -> Dict[DemoSection, str]:
        """Create hero's journey story arc."""
        return {
            DemoSection.OPENING_HOOK: "The Challenge: [Describe the problem as a quest]",
            DemoSection.PROBLEM_STATEMENT: "The Obstacle: [Detail the specific challenges faced]",
            DemoSection.SOLUTION_OVERVIEW: "The Journey: [Outline the solution approach]",
            DemoSection.TECHNICAL_DEMONSTRATION: "The Victory: [Show the working solution]",
            DemoSection.SYSTEMATIC_EXCELLENCE: "The Wisdom: [Share systematic lessons learned]",
            DemoSection.BUSINESS_IMPACT: "The Treasure: [Present the value created]",
            DemoSection.CLOSING_CALL_TO_ACTION: "The Next Adventure: [Call for adoption/collaboration]",
        }

    def _create_before_after_arc(
        self, context: Dict[str, Any]
    ) -> Dict[DemoSection, str]:
        """Create before/after transformation story arc."""
        return {
            DemoSection.OPENING_HOOK: "Imagine a world where... [Paint the vision]",
            DemoSection.PROBLEM_STATEMENT: "But today's reality is... [Show current pain points]",
            DemoSection.SOLUTION_OVERVIEW: "What if we could... [Present the transformation]",
            DemoSection.TECHNICAL_DEMONSTRATION: "Here's how it works... [Show the solution in action]",
            DemoSection.SYSTEMATIC_EXCELLENCE: "Built systematically... [Highlight development quality]",
            DemoSection.BUSINESS_IMPACT: "The transformation delivers... [Quantify the benefits]",
            DemoSection.CLOSING_CALL_TO_ACTION: "Join the transformation... [Invite participation]",
        }

    def _create_feature_showcase_arc(
        self, context: Dict[str, Any]
    ) -> Dict[DemoSection, str]:
        """Create feature showcase story arc."""
        return {
            DemoSection.OPENING_HOOK: "Check this out... [Immediate feature hook]",
            DemoSection.PROBLEM_STATEMENT: "This solves... [Quick problem context]",
            DemoSection.SOLUTION_OVERVIEW: "Here's what we built... [Feature overview]",
            DemoSection.TECHNICAL_DEMONSTRATION: "Let me show you... [Live feature demo]",
            DemoSection.SYSTEMATIC_EXCELLENCE: "Built with quality... [Development highlights]",
            DemoSection.BUSINESS_IMPACT: "This means... [Impact summary]",
            DemoSection.CLOSING_CALL_TO_ACTION: "Try it yourself... [Engagement call]",
        }

    def _create_technical_deep_dive_arc(
        self, context: Dict[str, Any]
    ) -> Dict[DemoSection, str]:
        """Create technical deep dive story arc."""
        return {
            DemoSection.OPENING_HOOK: "The technical challenge... [Complex problem introduction]",
            DemoSection.PROBLEM_STATEMENT: "Existing solutions fail because... [Technical limitations]",
            DemoSection.SOLUTION_OVERVIEW: "Our architecture addresses... [Technical approach]",
            DemoSection.TECHNICAL_DEMONSTRATION: "Under the hood... [Deep technical demo]",
            DemoSection.SYSTEMATIC_EXCELLENCE: "Systematic development ensures... [Quality showcase]",
            DemoSection.BUSINESS_IMPACT: "Technical excellence delivers... [Business value]",
            DemoSection.CLOSING_CALL_TO_ACTION: "Collaborate with us... [Technical partnership]",
        }

    def _generate_opening_hook(self, context: Dict[str, Any]) -> str:
        """Generate compelling opening hook."""
        return f"""
🎯 **Opening Hook** (30 seconds)

"Imagine if [specific pain point] could be solved in [time/effort saved]. 
Today, I'll show you exactly how we made that possible with [project name].

[Compelling statistic or demo teaser that immediately grabs attention]

This isn't just another [category] solution - this is systematic excellence 
applied to [problem domain], and the results speak for themselves."

**Key Elements:**
- Immediate value proposition
- Specific, measurable benefit
- Systematic differentiation
- Confidence and credibility
"""

    def _generate_problem_statement(self, context: Dict[str, Any]) -> str:
        """Generate clear problem statement."""
        return f"""
🎯 **Problem Statement** (60 seconds)

"Here's the reality: [specific problem description with real-world context]

Current solutions fall short because:
• [Limitation 1 with specific example]
• [Limitation 2 with quantified impact]  
• [Limitation 3 with user pain point]

This affects [target audience] by [specific impact], costing [quantified cost] 
and preventing [missed opportunity].

We knew there had to be a systematic way to solve this."

**Key Elements:**
- Specific, relatable problem
- Clear limitations of existing solutions
- Quantified impact and cost
- Sets up systematic solution approach
"""

    def _generate_solution_overview(self, context: Dict[str, Any]) -> str:
        """Generate solution overview."""
        systematic_evidence = context.get("systematic_evidence")

        return f"""
🎯 **Solution Overview** (90 seconds)

"Meet [Project Name] - a systematic approach to [problem domain].

**Core Innovation:**
{systematic_evidence.competitive_advantages[0] if systematic_evidence.competitive_advantages else 'Systematic development approach'}

**Key Features:**
• [Feature 1]: [Specific benefit]
• [Feature 2]: [Measurable improvement]
• [Feature 3]: [Unique differentiator]

**Systematic Advantage:**
Unlike ad-hoc solutions, we built this using systematic development principles:
- Spec-driven development for predictable quality
- Comprehensive testing for reliability
- Systematic architecture for scalability

This isn't just working software - this is systematic excellence."

**Key Elements:**
- Clear solution positioning
- Specific feature benefits
- Systematic differentiation
- Quality and reliability emphasis
"""

    def _generate_technical_demo(self, context: Dict[str, Any]) -> str:
        """Generate technical demonstration script."""
        return f"""
🎯 **Technical Demonstration** (180 seconds)

"Let me show you how this works in practice.

**Demo Sequence:**
1. **Setup** (30s): [Show starting state/problem scenario]
2. **Core Functionality** (90s): [Demonstrate key features working]
3. **Systematic Quality** (30s): [Show testing, validation, reliability]
4. **Results** (30s): [Quantify the improvement/solution]

**Live Demo Script:**
'Starting with [scenario], watch what happens when we [action]...
[Step-by-step demonstration with clear narration]
Notice how [systematic element] ensures [quality/reliability]...
And here's the result: [quantified improvement]'

**Backup Plans:**
- Pre-recorded video if live demo fails
- Screenshot walkthrough with narration
- Code review highlighting systematic implementation

**Key Elements:**
- Clear demonstration sequence
- Systematic quality showcase
- Quantified results
- Professional backup strategies
"""

    def _generate_systematic_showcase(self, context: Dict[str, Any]) -> str:
        """Generate systematic excellence showcase."""
        systematic_evidence = context.get("systematic_evidence")

        return f"""
🎯 **Systematic Excellence** (60 seconds)

"What makes this special isn't just that it works - it's HOW we built it.

**Systematic Development Evidence:**
• Spec-driven: {len(systematic_evidence.spec_driven_evidence)} documented requirements → design → implementation
• Quality-first: {systematic_evidence.quality_metrics.get('test_coverage', 85)}% test coverage with systematic validation
• Beast Mode: {len(systematic_evidence.beast_mode_highlights)} systematic principles applied

**Development Maturity:**
{chr(10).join(f'• {indicator}' for indicator in systematic_evidence.development_maturity_indicators[:3])}

**Competitive Advantage:**
This systematic approach means predictable quality, reduced risk, and scalable excellence.
While others build ad-hoc solutions, we deliver systematic reliability."

**Key Elements:**
- Concrete systematic evidence
- Measurable quality metrics
- Development maturity demonstration
- Clear competitive differentiation
"""

    def _generate_business_impact(self, context: Dict[str, Any]) -> str:
        """Generate business impact statement."""
        return f"""
🎯 **Business Impact** (60 seconds)

"Here's what this means in the real world:

**Immediate Benefits:**
• [Quantified improvement 1]: [Specific metric/savings]
• [Quantified improvement 2]: [Time/cost reduction]
• [Quantified improvement 3]: [Quality/reliability gain]

**Market Opportunity:**
• Target market: [Size and characteristics]
• Competitive advantage: [Systematic differentiation]
• Scalability: [Growth potential with systematic foundation]

**Systematic Value:**
Because we built this systematically, we can:
- Guarantee consistent quality
- Scale reliably
- Maintain and enhance efficiently
- Deliver predictable results

This isn't just a hackathon project - it's a systematic solution ready for real-world impact."

**Key Elements:**
- Quantified benefits
- Market opportunity
- Systematic scalability
- Real-world readiness
"""

    def _generate_closing_cta(self, context: Dict[str, Any]) -> str:
        """Generate closing call-to-action."""
        return f"""
🎯 **Closing Call-to-Action** (30 seconds)

"We've shown you systematic excellence in action - a solution that doesn't just work, 
but works reliably, scales systematically, and delivers predictable results.

**Next Steps:**
• Try it: [Specific action for judges/audience]
• Collaborate: [Partnership/contribution opportunity]
• Learn: [Systematic approach knowledge sharing]

**The Ask:**
Join us in proving that systematic development isn't just better - it's the future.
Because when everyone wins through systematic excellence, we all succeed.

Thank you. Questions?"

**Key Elements:**
- Systematic excellence summary
- Clear next steps
- Specific ask/engagement
- Memorable closing
- Question invitation
"""

    def _enhance_with_systematic_evidence(
        self, content: Dict[DemoSection, str], systematic_evidence: SystematicEvidence
    ) -> Dict[DemoSection, str]:
        """Enhance content with systematic evidence."""
        # This would integrate actual systematic evidence into the content
        # For now, return the content as-is since it already includes placeholders
        return content

    def _apply_content_guidelines(
        self, content: Dict[DemoSection, str], guidelines: ContentGuidelines
    ) -> Dict[DemoSection, str]:
        """Apply content guidelines to adjust technical depth and focus."""
        # Adjust technical depth based on guidelines
        if guidelines.max_technical_depth < 0.5:
            # Reduce technical complexity in demonstrations
            content[DemoSection.TECHNICAL_DEMONSTRATION] = content[
                DemoSection.TECHNICAL_DEMONSTRATION
            ].replace("Deep technical demo", "High-level feature showcase")

        return content

    def _analyze_judging_criteria(self, judging_criteria: List) -> Dict[str, float]:
        """Analyze judging criteria to determine content emphasis."""
        criteria_weights = {}

        for criterion in judging_criteria:
            criteria_weights[criterion.criterion_name.lower()] = (
                criterion.weight_percentage / 100.0
            )

        return criteria_weights

    def _optimize_content_for_criteria(
        self,
        demo_script: DemoScript,
        criteria_weights: Dict[str, float],
        judge_personas: List[str],
    ) -> Dict[DemoSection, str]:
        """Optimize content based on judging criteria and judge personas."""
        # This would adjust content emphasis based on criteria weights
        # For now, return the original content
        return {
            DemoSection.OPENING_HOOK: demo_script.opening_hook,
            DemoSection.PROBLEM_STATEMENT: demo_script.problem_statement,
            DemoSection.SOLUTION_OVERVIEW: demo_script.solution_overview,
            DemoSection.TECHNICAL_DEMONSTRATION: demo_script.technical_demonstration,
            DemoSection.SYSTEMATIC_EXCELLENCE: demo_script.systematic_excellence,
            DemoSection.BUSINESS_IMPACT: demo_script.business_impact,
            DemoSection.CLOSING_CALL_TO_ACTION: demo_script.closing_call_to_action,
        }
