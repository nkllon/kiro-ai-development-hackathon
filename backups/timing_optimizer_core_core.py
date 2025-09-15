"""
Timing Optimizer Core Core

This module was extracted from timing_optimizer_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics
from ..models import DemoScript, HackathonConfig


class PacingStrategy(Enum):
    """Pacing strategies for presentations."""

    STEADY = "steady"
    FRONT_LOADED = "front_loaded"
    CRESCENDO = "crescendo"
    DEMO_FOCUSED = "demo_focused"
    SYSTEMATIC_EMPHASIS = "systematic_emphasis"


class TimingConstraint(Enum):
    """Types of timing constraints."""

    HARD_LIMIT = "hard_limit"
    SOFT_LIMIT = "soft_limit"
    MINIMUM_TIME = "minimum_time"
    BUFFER_TIME = "buffer_time"


@dataclass
class TimingAnalysis:
    """Analysis of presentation timing."""

    total_duration: int
    section_durations: Dict[str, int]
    pacing_score: float
    timing_issues: List[str]
    optimization_suggestions: List[str]
    buffer_time: int


@dataclass
class PacingRecommendation:
    """Recommendation for pacing optimization."""

    section: str
    current_duration: int
    recommended_duration: int
    adjustment_reason: str
    implementation_tips: List[str]


@dataclass
class TimingOptimization:
    """Complete timing optimization results."""

    optimized_script: DemoScript
    timing_analysis: TimingAnalysis
    pacing_recommendations: List[PacingRecommendation]
    rehearsal_schedule: List[str]
    contingency_plans: List[str]


class DemoTimingOptimizer:
    """
    Optimizes demo timing and pacing for maximum impact.

    Analyzes presentation flow, optimizes section timing, and provides
    recommendations for pacing that maximizes judge engagement within
    hackathon time constraints.
    """

    def __init__(self):
        """Initialize the timing optimizer."""
        self.logger = logging.getLogger(__name__)
        self.timing_templates = {
            "devpost_standard": {
                "opening_hook": 0.05,
                "problem_statement": 0.15,
                "solution_overview": 0.2,
                "technical_demonstration": 0.35,
                "systematic_excellence": 0.1,
                "business_impact": 0.1,
                "closing_call_to_action": 0.05,
            },
            "mlh_quick": {
                "opening_hook": 0.1,
                "problem_statement": 0.15,
                "solution_overview": 0.15,
                "technical_demonstration": 0.45,
                "systematic_excellence": 0.05,
                "business_impact": 0.05,
                "closing_call_to_action": 0.05,
            },
            "technical_deep_dive": {
                "opening_hook": 0.05,
                "problem_statement": 0.1,
                "solution_overview": 0.15,
                "technical_demonstration": 0.4,
                "systematic_excellence": 0.2,
                "business_impact": 0.05,
                "closing_call_to_action": 0.05,
            },
        }
        self.pacing_guidelines = {
            PacingStrategy.STEADY: "Maintain consistent energy and pace throughout",
            PacingStrategy.FRONT_LOADED: "Start strong with detailed setup, accelerate through later sections",
            PacingStrategy.CRESCENDO: "Build energy and excitement toward the demo climax",
            PacingStrategy.DEMO_FOCUSED: "Minimize setup time, maximize demonstration impact",
            PacingStrategy.SYSTEMATIC_EMPHASIS: "Ensure adequate time for systematic excellence showcase",
        }
        self.logger.info("Demo timing optimizer initialized")

    def optimize_demo_timing(
        self,
        demo_script: DemoScript,
        hackathon_config: HackathonConfig,
        pacing_strategy: PacingStrategy = PacingStrategy.DEMO_FOCUSED,
        template_name: str = "devpost_standard",
    ) -> TimingOptimization:
        """
        Optimize demo timing for maximum impact.

        Args:
            demo_script: Original demo script
            hackathon_config: Hackathon configuration with time limits
            pacing_strategy: Desired pacing strategy
            template_name: Timing template to use

        Returns:
            Complete timing optimization results
        """
        self.logger.info(
            f"Optimizing demo timing with {pacing_strategy.value} strategy"
        )
        current_analysis = self._analyze_current_timing(demo_script, hackathon_config)
        recommendations = self._generate_pacing_recommendations(
            demo_script, hackathon_config, pacing_strategy, template_name
        )
        optimized_script = self._apply_timing_optimizations(
            demo_script, recommendations, hackathon_config
        )
        optimized_analysis = self._analyze_current_timing(
            optimized_script, hackathon_config
        )
        rehearsal_schedule = self._create_rehearsal_schedule(optimized_script)
        contingency_plans = self._generate_contingency_plans(
            optimized_script, hackathon_config
        )
        optimization = TimingOptimization(
            optimized_script=optimized_script,
            timing_analysis=optimized_analysis,
            pacing_recommendations=recommendations,
            rehearsal_schedule=rehearsal_schedule,
            contingency_plans=contingency_plans,
        )
        self.logger.info(
            f"Timing optimization complete. Duration: {optimized_analysis.total_duration}s"
        )
        return optimization

    def analyze_pacing_effectiveness(
        self,
        demo_script: DemoScript,
        judge_attention_data: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze pacing effectiveness for judge engagement.

        Args:
            demo_script: Demo script to analyze
            judge_attention_data: Optional attention data from previous presentations

        Returns:
            Pacing effectiveness analysis
        """
        analysis = {
            "overall_pacing_score": 0.0,
            "section_pacing": {},
            "attention_curve": [],
            "engagement_peaks": [],
            "improvement_areas": [],
        }
        total_duration = demo_script.total_duration
        for section, duration in demo_script.timing_breakdown.items():
            section_ratio = duration / total_duration
            pacing_score = self._calculate_section_pacing_score(section, section_ratio)
            analysis["section_pacing"][section] = {
                "duration": duration,
                "ratio": section_ratio,
                "pacing_score": pacing_score,
            }
        section_scores = [
            data["pacing_score"] for data in analysis["section_pacing"].values()
        ]
        analysis["overall_pacing_score"] = statistics.mean(section_scores)
        for section, data in analysis["section_pacing"].items():
            if data["pacing_score"] > 80:
                analysis["engagement_peaks"].append(section)
        for section, data in analysis["section_pacing"].items():
            if data["pacing_score"] < 60:
                analysis["improvement_areas"].append(
                    {
                        "section": section,
                        "issue": "Suboptimal pacing",
                        "suggestion": self._get_pacing_suggestion(section, data),
                    }
                )
        return analysis

    def create_timing_rehearsal_plan(
        self, demo_script: DemoScript, rehearsal_sessions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Create systematic rehearsal plan for timing optimization.

        Args:
            demo_script: Demo script to rehearse
            rehearsal_sessions: Number of rehearsal sessions to plan

        Returns:
            Detailed rehearsal plan
        """
        rehearsal_plan = []
        for session in range(1, rehearsal_sessions + 1):
            session_plan = {
                "session_number": session,
                "focus_areas": [],
                "timing_goals": {},
                "success_criteria": [],
                "feedback_points": [],
            }
            if session == 1:
                session_plan["focus_areas"] = [
                    "Overall presentation flow",
                    "Major section transitions",
                    "Demo execution timing",
                ]
                session_plan["timing_goals"] = {
                    "total_duration": demo_script.total_duration,
                    "demo_section": demo_script.timing_breakdown.get(
                        "technical_demonstration", 180
                    ),
                }
                session_plan["success_criteria"] = [
                    "Complete presentation within time limit",
                    "Smooth transitions between sections",
                    "Demo executes without major issues",
                ]
            elif session == 2:
                session_plan["focus_areas"] = [
                    "Section pacing optimization",
                    "Systematic excellence emphasis",
                    "Judge engagement techniques",
                ]
                session_plan["timing_goals"] = {
                    section: duration
                    for section, duration in demo_script.timing_breakdown.items()
                }
                session_plan["success_criteria"] = [
                    "Each section within ±10% of target time",
                    "Systematic elements clearly highlighted",
                    "Engaging delivery throughout",
                ]
            else:
                session_plan["focus_areas"] = [
                    "Presentation polish and confidence",
                    "Backup plan execution",
                    "Q&A preparation",
                ]
                session_plan["timing_goals"] = {
                    "presentation": demo_script.total_duration - 60,
                    "qa_prep": 60,
                }
                session_plan["success_criteria"] = [
                    "Confident, polished delivery",
                    "Backup plans ready and tested",
                    "Q&A responses prepared",
                ]
            session_plan["feedback_points"] = [
                "Timing accuracy for each section",
                "Clarity of systematic excellence message",
                "Judge engagement and eye contact",
                "Technical demo reliability",
                "Overall presentation confidence",
            ]
            rehearsal_plan.append(session_plan)
        return rehearsal_plan

    def generate_real_time_timing_guide(
        self, demo_script: DemoScript
    ) -> Dict[str, Any]:
        """
        Generate real-time timing guide for presentation delivery.

        Args:
            demo_script: Demo script with timing information

        Returns:
            Real-time timing guide with checkpoints
        """
        timing_guide = {
            "checkpoints": [],
            "section_targets": {},
            "warning_thresholds": {},
            "recovery_strategies": {},
        }
        cumulative_time = 0
        for section, duration in demo_script.timing_breakdown.items():
            cumulative_time += duration
            checkpoint = {
                "section": section,
                "target_time": cumulative_time,
                "section_duration": duration,
                "key_message": self._get_section_key_message(section),
                "timing_cues": self._get_timing_cues(section, duration),
            }
            timing_guide["checkpoints"].append(checkpoint)
            timing_guide["section_targets"][section] = duration
            timing_guide["warning_thresholds"][section] = {
                "under_time": duration * 0.8,
                "over_time": duration * 1.2,
            }
            timing_guide["recovery_strategies"][section] = (
                self._get_recovery_strategies(section)
            )
        return timing_guide

    def _analyze_current_timing(
        self, demo_script: DemoScript, hackathon_config: HackathonConfig
    ) -> TimingAnalysis:
        """Analyze current timing against constraints."""
        total_duration = demo_script.total_duration
        time_limit = hackathon_config.demo_time_limit * 60
        timing_issues = []
        optimization_suggestions = []
        if total_duration > time_limit:
            timing_issues.append(
                f"Presentation too long: {total_duration}s > {time_limit}s"
            )
            optimization_suggestions.append("Reduce content or improve pacing")
        section_ratios = {}
        for section, duration in demo_script.timing_breakdown.items():
            ratio = duration / total_duration
            section_ratios[section] = ratio
            if section == "technical_demonstration" and ratio < 0.25:
                timing_issues.append("Technical demonstration may be too short")
                optimization_suggestions.append("Allocate more time to demo section")
            if section == "systematic_excellence" and ratio < 0.08:
                timing_issues.append("Systematic excellence showcase too brief")
                optimization_suggestions.append("Emphasize systematic development more")
        pacing_score = self._calculate_overall_pacing_score(section_ratios)
        buffer_time = max(0, time_limit - total_duration)
        return TimingAnalysis(
            total_duration=total_duration,
            section_durations=demo_script.timing_breakdown.copy(),
            pacing_score=pacing_score,
            timing_issues=timing_issues,
            optimization_suggestions=optimization_suggestions,
            buffer_time=buffer_time,
        )

    def _generate_pacing_recommendations(
        self,
        demo_script: DemoScript,
        hackathon_config: HackathonConfig,
        pacing_strategy: PacingStrategy,
        template_name: str,
    ) -> List[PacingRecommendation]:
        """Generate pacing recommendations."""
        recommendations = []
        if template_name not in self.timing_templates:
            template_name = "devpost_standard"
        optimal_ratios = self.timing_templates[template_name]
        time_limit = hackathon_config.demo_time_limit * 60
        adjusted_ratios = self._apply_pacing_strategy(optimal_ratios, pacing_strategy)
        for section, current_duration in demo_script.timing_breakdown.items():
            if section in adjusted_ratios:
                optimal_duration = int(time_limit * adjusted_ratios[section])
                if abs(current_duration - optimal_duration) > 10:
                    recommendation = PacingRecommendation(
                        section=section,
                        current_duration=current_duration,
                        recommended_duration=optimal_duration,
                        adjustment_reason=self._get_adjustment_reason(
                            section, current_duration, optimal_duration, pacing_strategy
                        ),
                        implementation_tips=self._get_implementation_tips(
                            section, optimal_duration
                        ),
                    )
                    recommendations.append(recommendation)
        return recommendations

    def _apply_timing_optimizations(
        self,
        demo_script: DemoScript,
        recommendations: List[PacingRecommendation],
        hackathon_config: HackathonConfig,
    ) -> DemoScript:
        """Apply timing optimizations to create optimized script."""
        optimized_timing = demo_script.timing_breakdown.copy()
        for recommendation in recommendations:
            optimized_timing[recommendation.section] = (
                recommendation.recommended_duration
            )
        total_optimized = sum(optimized_timing.values())
        time_limit = hackathon_config.demo_time_limit * 60
        if total_optimized > time_limit:
            reduction_factor = time_limit / total_optimized
            for section in optimized_timing:
                optimized_timing[section] = int(
                    optimized_timing[section] * reduction_factor
                )
        optimized_script = DemoScript(
            opening_hook=demo_script.opening_hook,
            problem_statement=demo_script.problem_statement,
            solution_overview=demo_script.solution_overview,
            technical_demonstration=demo_script.technical_demonstration,
            systematic_excellence=demo_script.systematic_excellence,
            business_impact=demo_script.business_impact,
            closing_call_to_action=demo_script.closing_call_to_action,
            total_duration=sum(optimized_timing.values()),
            timing_breakdown=optimized_timing,
            backup_plans=demo_script.backup_plans.copy(),
        )
        return optimized_script

    def _create_rehearsal_schedule(self, demo_script: DemoScript) -> List[str]:
        """Create rehearsal schedule."""
        return [
            f"Rehearsal 1: Full run-through focusing on overall flow ({demo_script.total_duration}s target)",
            f"Rehearsal 2: Section timing practice with {demo_script.timing_breakdown}",
            "Rehearsal 3: Demo reliability testing and backup plan practice",
            "Rehearsal 4: Final polish with Q&A preparation",
            "Rehearsal 5: Dress rehearsal with full setup and timing",
        ]

    def _generate_contingency_plans(
        self, demo_script: DemoScript, hackathon_config: HackathonConfig
    ) -> List[str]:
        """Generate contingency plans for timing issues."""
        return [
            f"If running long: Skip business impact section (saves {demo_script.timing_breakdown.get('business_impact', 60)}s)",
            f"If demo fails: Use backup screenshots (saves {demo_script.timing_breakdown.get('technical_demonstration', 180) - 60}s)",
            "If questions interrupt: Politely defer to end to maintain timing",
            "If technical issues: Have pre-recorded demo ready",
            f"Emergency 3-minute version: Opening + Demo + Systematic + Closing",
        ]

    def _calculate_section_pacing_score(self, section: str, ratio: float) -> float:
        """Calculate pacing score for a section."""
        optimal_ratios = {
            "opening_hook": 0.05,
            "problem_statement": 0.15,
            "solution_overview": 0.2,
            "technical_demonstration": 0.35,
            "systematic_excellence": 0.1,
            "business_impact": 0.1,
            "closing_call_to_action": 0.05,
        }
        if section not in optimal_ratios:
            return 50.0
        optimal = optimal_ratios[section]
        deviation = abs(ratio - optimal) / optimal
        score = max(0, 100 - deviation * 100)
        return score

    def _calculate_overall_pacing_score(
        self, section_ratios: Dict[str, float]
    ) -> float:
        """Calculate overall pacing score."""
        section_scores = []
        for section, ratio in section_ratios.items():
            score = self._calculate_section_pacing_score(section, ratio)
            section_scores.append(score)
        return statistics.mean(section_scores) if section_scores else 50.0

    def _apply_pacing_strategy(
        self, base_ratios: Dict[str, float], strategy: PacingStrategy
    ) -> Dict[str, float]:
        """Apply pacing strategy to base ratios."""
        adjusted_ratios = base_ratios.copy()
        if strategy == PacingStrategy.DEMO_FOCUSED:
            adjusted_ratios["technical_demonstration"] *= 1.2
            for section in adjusted_ratios:
                if section != "technical_demonstration":
                    adjusted_ratios[section] *= 0.9
        elif strategy == PacingStrategy.SYSTEMATIC_EMPHASIS:
            adjusted_ratios["systematic_excellence"] *= 1.5
            for section in adjusted_ratios:
                if section != "systematic_excellence":
                    adjusted_ratios[section] *= 0.95
        elif strategy == PacingStrategy.FRONT_LOADED:
            adjusted_ratios["problem_statement"] *= 1.2
            adjusted_ratios["solution_overview"] *= 1.1
            adjusted_ratios["business_impact"] *= 0.8
            adjusted_ratios["closing_call_to_action"] *= 0.8
        total = sum(adjusted_ratios.values())
        for section in adjusted_ratios:
            adjusted_ratios[section] /= total
        return adjusted_ratios

    def _get_adjustment_reason(
        self, section: str, current: int, optimal: int, strategy: PacingStrategy
    ) -> str:
        """Get reason for timing adjustment."""
        if current > optimal:
            return f"Reduce {section} by {current - optimal}s for better pacing with {strategy.value} strategy"
        else:
            return f"Increase {section} by {optimal - current}s to optimize for {strategy.value} strategy"

    def _get_implementation_tips(self, section: str, duration: int) -> List[str]:
        """Get implementation tips for section timing."""
        tips = {
            "opening_hook": [
                "Practice opening line for immediate impact",
                "Use compelling statistic or demo teaser",
                "Keep energy high and confident",
            ],
            "problem_statement": [
                "Use specific, relatable examples",
                "Quantify the problem impact",
                "Set up systematic solution approach",
            ],
            "technical_demonstration": [
                "Practice demo sequence multiple times",
                "Have backup screenshots ready",
                "Narrate clearly while demonstrating",
            ],
            "systematic_excellence": [
                "Emphasize development maturity",
                "Show concrete systematic evidence",
                "Differentiate from ad-hoc approaches",
            ],
        }
        return tips.get(
            section,
            ["Practice timing for this section", "Keep content focused and clear"],
        )

    def _get_pacing_suggestion(self, section: str, data: Dict[str, Any]) -> str:
        """Get pacing suggestion for improvement."""
        if data["pacing_score"] < 40:
            return (
                f"Consider major restructuring of {section} - timing significantly off"
            )
        elif data["pacing_score"] < 60:
            return f"Adjust {section} timing - currently {data['duration']}s, consider optimizing"
        else:
            return f"Minor timing adjustment needed for {section}"

    def _get_section_key_message(self, section: str) -> str:
        """Get key message for section."""
        messages = {
            "opening_hook": "Grab attention and establish credibility",
            "problem_statement": "Clear problem with quantified impact",
            "solution_overview": "Systematic solution approach",
            "technical_demonstration": "Working solution with systematic quality",
            "systematic_excellence": "Development maturity and competitive advantage",
            "business_impact": "Real-world value and market opportunity",
            "closing_call_to_action": "Strong finish with clear next steps",
        }
        return messages.get(section, "Key section message")

    def _get_timing_cues(self, section: str, duration: int) -> List[str]:
        """Get timing cues for section delivery."""
        return [
            f"Target duration: {duration} seconds",
            f"Halfway point: {duration // 2} seconds",
            f"Wrap-up cue: {duration - 15} seconds",
        ]

    def _get_recovery_strategies(self, section: str) -> List[str]:
        """Get recovery strategies for timing issues."""
        return [
            f"If running long in {section}: Skip detailed examples, focus on key points",
            f"If running short in {section}: Add systematic development details",
            "Use transition phrases to adjust pacing naturally",
        ]


def __init__(self):
    """Initialize the timing optimizer."""
    self.logger = logging.getLogger(__name__)
    self.timing_templates = {
        "devpost_standard": {
            "opening_hook": 0.05,
            "problem_statement": 0.15,
            "solution_overview": 0.2,
            "technical_demonstration": 0.35,
            "systematic_excellence": 0.1,
            "business_impact": 0.1,
            "closing_call_to_action": 0.05,
        },
        "mlh_quick": {
            "opening_hook": 0.1,
            "problem_statement": 0.15,
            "solution_overview": 0.15,
            "technical_demonstration": 0.45,
            "systematic_excellence": 0.05,
            "business_impact": 0.05,
            "closing_call_to_action": 0.05,
        },
        "technical_deep_dive": {
            "opening_hook": 0.05,
            "problem_statement": 0.1,
            "solution_overview": 0.15,
            "technical_demonstration": 0.4,
            "systematic_excellence": 0.2,
            "business_impact": 0.05,
            "closing_call_to_action": 0.05,
        },
    }
    self.pacing_guidelines = {
        PacingStrategy.STEADY: "Maintain consistent energy and pace throughout",
        PacingStrategy.FRONT_LOADED: "Start strong with detailed setup, accelerate through later sections",
        PacingStrategy.CRESCENDO: "Build energy and excitement toward the demo climax",
        PacingStrategy.DEMO_FOCUSED: "Minimize setup time, maximize demonstration impact",
        PacingStrategy.SYSTEMATIC_EMPHASIS: "Ensure adequate time for systematic excellence showcase",
    }
    self.logger.info("Demo timing optimizer initialized")


def optimize_demo_timing(
    self,
    demo_script: DemoScript,
    hackathon_config: HackathonConfig,
    pacing_strategy: PacingStrategy = PacingStrategy.DEMO_FOCUSED,
    template_name: str = "devpost_standard",
) -> TimingOptimization:
    """
    Optimize demo timing for maximum impact.

    Args:
        demo_script: Original demo script
        hackathon_config: Hackathon configuration with time limits
        pacing_strategy: Desired pacing strategy
        template_name: Timing template to use

    Returns:
        Complete timing optimization results
    """
    self.logger.info(f"Optimizing demo timing with {pacing_strategy.value} strategy")
    current_analysis = self._analyze_current_timing(demo_script, hackathon_config)
    recommendations = self._generate_pacing_recommendations(
        demo_script, hackathon_config, pacing_strategy, template_name
    )
    optimized_script = self._apply_timing_optimizations(
        demo_script, recommendations, hackathon_config
    )
    optimized_analysis = self._analyze_current_timing(
        optimized_script, hackathon_config
    )
    rehearsal_schedule = self._create_rehearsal_schedule(optimized_script)
    contingency_plans = self._generate_contingency_plans(
        optimized_script, hackathon_config
    )
    optimization = TimingOptimization(
        optimized_script=optimized_script,
        timing_analysis=optimized_analysis,
        pacing_recommendations=recommendations,
        rehearsal_schedule=rehearsal_schedule,
        contingency_plans=contingency_plans,
    )
    self.logger.info(
        f"Timing optimization complete. Duration: {optimized_analysis.total_duration}s"
    )
    return optimization


def analyze_pacing_effectiveness(
    self,
    demo_script: DemoScript,
    judge_attention_data: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Analyze pacing effectiveness for judge engagement.

    Args:
        demo_script: Demo script to analyze
        judge_attention_data: Optional attention data from previous presentations

    Returns:
        Pacing effectiveness analysis
    """
    analysis = {
        "overall_pacing_score": 0.0,
        "section_pacing": {},
        "attention_curve": [],
        "engagement_peaks": [],
        "improvement_areas": [],
    }
    total_duration = demo_script.total_duration
    for section, duration in demo_script.timing_breakdown.items():
        section_ratio = duration / total_duration
        pacing_score = self._calculate_section_pacing_score(section, section_ratio)
        analysis["section_pacing"][section] = {
            "duration": duration,
            "ratio": section_ratio,
            "pacing_score": pacing_score,
        }
    section_scores = [
        data["pacing_score"] for data in analysis["section_pacing"].values()
    ]
    analysis["overall_pacing_score"] = statistics.mean(section_scores)
    for section, data in analysis["section_pacing"].items():
        if data["pacing_score"] > 80:
            analysis["engagement_peaks"].append(section)
    for section, data in analysis["section_pacing"].items():
        if data["pacing_score"] < 60:
            analysis["improvement_areas"].append(
                {
                    "section": section,
                    "issue": "Suboptimal pacing",
                    "suggestion": self._get_pacing_suggestion(section, data),
                }
            )
    return analysis


def create_timing_rehearsal_plan(
    self, demo_script: DemoScript, rehearsal_sessions: int = 3
) -> List[Dict[str, Any]]:
    """
    Create systematic rehearsal plan for timing optimization.

    Args:
        demo_script: Demo script to rehearse
        rehearsal_sessions: Number of rehearsal sessions to plan

    Returns:
        Detailed rehearsal plan
    """
    rehearsal_plan = []
    for session in range(1, rehearsal_sessions + 1):
        session_plan = {
            "session_number": session,
            "focus_areas": [],
            "timing_goals": {},
            "success_criteria": [],
            "feedback_points": [],
        }
        if session == 1:
            session_plan["focus_areas"] = [
                "Overall presentation flow",
                "Major section transitions",
                "Demo execution timing",
            ]
            session_plan["timing_goals"] = {
                "total_duration": demo_script.total_duration,
                "demo_section": demo_script.timing_breakdown.get(
                    "technical_demonstration", 180
                ),
            }
            session_plan["success_criteria"] = [
                "Complete presentation within time limit",
                "Smooth transitions between sections",
                "Demo executes without major issues",
            ]
        elif session == 2:
            session_plan["focus_areas"] = [
                "Section pacing optimization",
                "Systematic excellence emphasis",
                "Judge engagement techniques",
            ]
            session_plan["timing_goals"] = {
                section: duration
                for section, duration in demo_script.timing_breakdown.items()
            }
            session_plan["success_criteria"] = [
                "Each section within ±10% of target time",
                "Systematic elements clearly highlighted",
                "Engaging delivery throughout",
            ]
        else:
            session_plan["focus_areas"] = [
                "Presentation polish and confidence",
                "Backup plan execution",
                "Q&A preparation",
            ]
            session_plan["timing_goals"] = {
                "presentation": demo_script.total_duration - 60,
                "qa_prep": 60,
            }
            session_plan["success_criteria"] = [
                "Confident, polished delivery",
                "Backup plans ready and tested",
                "Q&A responses prepared",
            ]
        session_plan["feedback_points"] = [
            "Timing accuracy for each section",
            "Clarity of systematic excellence message",
            "Judge engagement and eye contact",
            "Technical demo reliability",
            "Overall presentation confidence",
        ]
        rehearsal_plan.append(session_plan)
    return rehearsal_plan


def generate_real_time_timing_guide(self, demo_script: DemoScript) -> Dict[str, Any]:
    """
    Generate real-time timing guide for presentation delivery.

    Args:
        demo_script: Demo script with timing information

    Returns:
        Real-time timing guide with checkpoints
    """
    timing_guide = {
        "checkpoints": [],
        "section_targets": {},
        "warning_thresholds": {},
        "recovery_strategies": {},
    }
    cumulative_time = 0
    for section, duration in demo_script.timing_breakdown.items():
        cumulative_time += duration
        checkpoint = {
            "section": section,
            "target_time": cumulative_time,
            "section_duration": duration,
            "key_message": self._get_section_key_message(section),
            "timing_cues": self._get_timing_cues(section, duration),
        }
        timing_guide["checkpoints"].append(checkpoint)
        timing_guide["section_targets"][section] = duration
        timing_guide["warning_thresholds"][section] = {
            "under_time": duration * 0.8,
            "over_time": duration * 1.2,
        }
        timing_guide["recovery_strategies"][section] = self._get_recovery_strategies(
            section
        )
    return timing_guide


def _analyze_current_timing(
    self, demo_script: DemoScript, hackathon_config: HackathonConfig
) -> TimingAnalysis:
    """Analyze current timing against constraints."""
    total_duration = demo_script.total_duration
    time_limit = hackathon_config.demo_time_limit * 60
    timing_issues = []
    optimization_suggestions = []
    if total_duration > time_limit:
        timing_issues.append(
            f"Presentation too long: {total_duration}s > {time_limit}s"
        )
        optimization_suggestions.append("Reduce content or improve pacing")
    section_ratios = {}
    for section, duration in demo_script.timing_breakdown.items():
        ratio = duration / total_duration
        section_ratios[section] = ratio
        if section == "technical_demonstration" and ratio < 0.25:
            timing_issues.append("Technical demonstration may be too short")
            optimization_suggestions.append("Allocate more time to demo section")
        if section == "systematic_excellence" and ratio < 0.08:
            timing_issues.append("Systematic excellence showcase too brief")
            optimization_suggestions.append("Emphasize systematic development more")
    pacing_score = self._calculate_overall_pacing_score(section_ratios)
    buffer_time = max(0, time_limit - total_duration)
    return TimingAnalysis(
        total_duration=total_duration,
        section_durations=demo_script.timing_breakdown.copy(),
        pacing_score=pacing_score,
        timing_issues=timing_issues,
        optimization_suggestions=optimization_suggestions,
        buffer_time=buffer_time,
    )


def _generate_pacing_recommendations(
    self,
    demo_script: DemoScript,
    hackathon_config: HackathonConfig,
    pacing_strategy: PacingStrategy,
    template_name: str,
) -> List[PacingRecommendation]:
    """Generate pacing recommendations."""
    recommendations = []
    if template_name not in self.timing_templates:
        template_name = "devpost_standard"
    optimal_ratios = self.timing_templates[template_name]
    time_limit = hackathon_config.demo_time_limit * 60
    adjusted_ratios = self._apply_pacing_strategy(optimal_ratios, pacing_strategy)
    for section, current_duration in demo_script.timing_breakdown.items():
        if section in adjusted_ratios:
            optimal_duration = int(time_limit * adjusted_ratios[section])
            if abs(current_duration - optimal_duration) > 10:
                recommendation = PacingRecommendation(
                    section=section,
                    current_duration=current_duration,
                    recommended_duration=optimal_duration,
                    adjustment_reason=self._get_adjustment_reason(
                        section, current_duration, optimal_duration, pacing_strategy
                    ),
                    implementation_tips=self._get_implementation_tips(
                        section, optimal_duration
                    ),
                )
                recommendations.append(recommendation)
    return recommendations


def _apply_timing_optimizations(
    self,
    demo_script: DemoScript,
    recommendations: List[PacingRecommendation],
    hackathon_config: HackathonConfig,
) -> DemoScript:
    """Apply timing optimizations to create optimized script."""
    optimized_timing = demo_script.timing_breakdown.copy()
    for recommendation in recommendations:
        optimized_timing[recommendation.section] = recommendation.recommended_duration
    total_optimized = sum(optimized_timing.values())
    time_limit = hackathon_config.demo_time_limit * 60
    if total_optimized > time_limit:
        reduction_factor = time_limit / total_optimized
        for section in optimized_timing:
            optimized_timing[section] = int(
                optimized_timing[section] * reduction_factor
            )
    optimized_script = DemoScript(
        opening_hook=demo_script.opening_hook,
        problem_statement=demo_script.problem_statement,
        solution_overview=demo_script.solution_overview,
        technical_demonstration=demo_script.technical_demonstration,
        systematic_excellence=demo_script.systematic_excellence,
        business_impact=demo_script.business_impact,
        closing_call_to_action=demo_script.closing_call_to_action,
        total_duration=sum(optimized_timing.values()),
        timing_breakdown=optimized_timing,
        backup_plans=demo_script.backup_plans.copy(),
    )
    return optimized_script


def _create_rehearsal_schedule(self, demo_script: DemoScript) -> List[str]:
    """Create rehearsal schedule."""
    return [
        f"Rehearsal 1: Full run-through focusing on overall flow ({demo_script.total_duration}s target)",
        f"Rehearsal 2: Section timing practice with {demo_script.timing_breakdown}",
        "Rehearsal 3: Demo reliability testing and backup plan practice",
        "Rehearsal 4: Final polish with Q&A preparation",
        "Rehearsal 5: Dress rehearsal with full setup and timing",
    ]


def _generate_contingency_plans(
    self, demo_script: DemoScript, hackathon_config: HackathonConfig
) -> List[str]:
    """Generate contingency plans for timing issues."""
    return [
        f"If running long: Skip business impact section (saves {demo_script.timing_breakdown.get('business_impact', 60)}s)",
        f"If demo fails: Use backup screenshots (saves {demo_script.timing_breakdown.get('technical_demonstration', 180) - 60}s)",
        "If questions interrupt: Politely defer to end to maintain timing",
        "If technical issues: Have pre-recorded demo ready",
        f"Emergency 3-minute version: Opening + Demo + Systematic + Closing",
    ]


def _calculate_section_pacing_score(self, section: str, ratio: float) -> float:
    """Calculate pacing score for a section."""
    optimal_ratios = {
        "opening_hook": 0.05,
        "problem_statement": 0.15,
        "solution_overview": 0.2,
        "technical_demonstration": 0.35,
        "systematic_excellence": 0.1,
        "business_impact": 0.1,
        "closing_call_to_action": 0.05,
    }
    if section not in optimal_ratios:
        return 50.0
    optimal = optimal_ratios[section]
    deviation = abs(ratio - optimal) / optimal
    score = max(0, 100 - deviation * 100)
    return score


def _calculate_overall_pacing_score(self, section_ratios: Dict[str, float]) -> float:
    """Calculate overall pacing score."""
    section_scores = []
    for section, ratio in section_ratios.items():
        score = self._calculate_section_pacing_score(section, ratio)
        section_scores.append(score)
    return statistics.mean(section_scores) if section_scores else 50.0


def _apply_pacing_strategy(
    self, base_ratios: Dict[str, float], strategy: PacingStrategy
) -> Dict[str, float]:
    """Apply pacing strategy to base ratios."""
    adjusted_ratios = base_ratios.copy()
    if strategy == PacingStrategy.DEMO_FOCUSED:
        adjusted_ratios["technical_demonstration"] *= 1.2
        for section in adjusted_ratios:
            if section != "technical_demonstration":
                adjusted_ratios[section] *= 0.9
    elif strategy == PacingStrategy.SYSTEMATIC_EMPHASIS:
        adjusted_ratios["systematic_excellence"] *= 1.5
        for section in adjusted_ratios:
            if section != "systematic_excellence":
                adjusted_ratios[section] *= 0.95
    elif strategy == PacingStrategy.FRONT_LOADED:
        adjusted_ratios["problem_statement"] *= 1.2
        adjusted_ratios["solution_overview"] *= 1.1
        adjusted_ratios["business_impact"] *= 0.8
        adjusted_ratios["closing_call_to_action"] *= 0.8
    total = sum(adjusted_ratios.values())
    for section in adjusted_ratios:
        adjusted_ratios[section] /= total
    return adjusted_ratios


def _get_adjustment_reason(
    self, section: str, current: int, optimal: int, strategy: PacingStrategy
) -> str:
    """Get reason for timing adjustment."""
    if current > optimal:
        return f"Reduce {section} by {current - optimal}s for better pacing with {strategy.value} strategy"
    else:
        return f"Increase {section} by {optimal - current}s to optimize for {strategy.value} strategy"


def _get_implementation_tips(self, section: str, duration: int) -> List[str]:
    """Get implementation tips for section timing."""
    tips = {
        "opening_hook": [
            "Practice opening line for immediate impact",
            "Use compelling statistic or demo teaser",
            "Keep energy high and confident",
        ],
        "problem_statement": [
            "Use specific, relatable examples",
            "Quantify the problem impact",
            "Set up systematic solution approach",
        ],
        "technical_demonstration": [
            "Practice demo sequence multiple times",
            "Have backup screenshots ready",
            "Narrate clearly while demonstrating",
        ],
        "systematic_excellence": [
            "Emphasize development maturity",
            "Show concrete systematic evidence",
            "Differentiate from ad-hoc approaches",
        ],
    }
    return tips.get(
        section, ["Practice timing for this section", "Keep content focused and clear"]
    )


def _get_pacing_suggestion(self, section: str, data: Dict[str, Any]) -> str:
    """Get pacing suggestion for improvement."""
    if data["pacing_score"] < 40:
        return f"Consider major restructuring of {section} - timing significantly off"
    elif data["pacing_score"] < 60:
        return f"Adjust {section} timing - currently {data['duration']}s, consider optimizing"
    else:
        return f"Minor timing adjustment needed for {section}"


def _get_section_key_message(self, section: str) -> str:
    """Get key message for section."""
    messages = {
        "opening_hook": "Grab attention and establish credibility",
        "problem_statement": "Clear problem with quantified impact",
        "solution_overview": "Systematic solution approach",
        "technical_demonstration": "Working solution with systematic quality",
        "systematic_excellence": "Development maturity and competitive advantage",
        "business_impact": "Real-world value and market opportunity",
        "closing_call_to_action": "Strong finish with clear next steps",
    }
    return messages.get(section, "Key section message")


def _get_timing_cues(self, section: str, duration: int) -> List[str]:
    """Get timing cues for section delivery."""
    return [
        f"Target duration: {duration} seconds",
        f"Halfway point: {duration // 2} seconds",
        f"Wrap-up cue: {duration - 15} seconds",
    ]


def _get_recovery_strategies(self, section: str) -> List[str]:
    """Get recovery strategies for timing issues."""
    return [
        f"If running long in {section}: Skip detailed examples, focus on key points",
        f"If running short in {section}: Add systematic development details",
        "Use transition phrases to adjust pacing naturally",
    ]


def __init__(self):
    """Initialize the timing optimizer."""
    self.logger = logging.getLogger(__name__)
    self.timing_templates = {
        "devpost_standard": {
            "opening_hook": 0.05,
            "problem_statement": 0.15,
            "solution_overview": 0.2,
            "technical_demonstration": 0.35,
            "systematic_excellence": 0.1,
            "business_impact": 0.1,
            "closing_call_to_action": 0.05,
        },
        "mlh_quick": {
            "opening_hook": 0.1,
            "problem_statement": 0.15,
            "solution_overview": 0.15,
            "technical_demonstration": 0.45,
            "systematic_excellence": 0.05,
            "business_impact": 0.05,
            "closing_call_to_action": 0.05,
        },
        "technical_deep_dive": {
            "opening_hook": 0.05,
            "problem_statement": 0.1,
            "solution_overview": 0.15,
            "technical_demonstration": 0.4,
            "systematic_excellence": 0.2,
            "business_impact": 0.05,
            "closing_call_to_action": 0.05,
        },
    }
    self.pacing_guidelines = {
        PacingStrategy.STEADY: "Maintain consistent energy and pace throughout",
        PacingStrategy.FRONT_LOADED: "Start strong with detailed setup, accelerate through later sections",
        PacingStrategy.CRESCENDO: "Build energy and excitement toward the demo climax",
        PacingStrategy.DEMO_FOCUSED: "Minimize setup time, maximize demonstration impact",
        PacingStrategy.SYSTEMATIC_EMPHASIS: "Ensure adequate time for systematic excellence showcase",
    }
    self.logger.info("Demo timing optimizer initialized")


def optimize_demo_timing(
    self,
    demo_script: DemoScript,
    hackathon_config: HackathonConfig,
    pacing_strategy: PacingStrategy = PacingStrategy.DEMO_FOCUSED,
    template_name: str = "devpost_standard",
) -> TimingOptimization:
    """
    Optimize demo timing for maximum impact.

    Args:
        demo_script: Original demo script
        hackathon_config: Hackathon configuration with time limits
        pacing_strategy: Desired pacing strategy
        template_name: Timing template to use

    Returns:
        Complete timing optimization results
    """
    self.logger.info(f"Optimizing demo timing with {pacing_strategy.value} strategy")
    current_analysis = self._analyze_current_timing(demo_script, hackathon_config)
    recommendations = self._generate_pacing_recommendations(
        demo_script, hackathon_config, pacing_strategy, template_name
    )
    optimized_script = self._apply_timing_optimizations(
        demo_script, recommendations, hackathon_config
    )
    optimized_analysis = self._analyze_current_timing(
        optimized_script, hackathon_config
    )
    rehearsal_schedule = self._create_rehearsal_schedule(optimized_script)
    contingency_plans = self._generate_contingency_plans(
        optimized_script, hackathon_config
    )
    optimization = TimingOptimization(
        optimized_script=optimized_script,
        timing_analysis=optimized_analysis,
        pacing_recommendations=recommendations,
        rehearsal_schedule=rehearsal_schedule,
        contingency_plans=contingency_plans,
    )
    self.logger.info(
        f"Timing optimization complete. Duration: {optimized_analysis.total_duration}s"
    )
    return optimization


def analyze_pacing_effectiveness(
    self,
    demo_script: DemoScript,
    judge_attention_data: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Analyze pacing effectiveness for judge engagement.

    Args:
        demo_script: Demo script to analyze
        judge_attention_data: Optional attention data from previous presentations

    Returns:
        Pacing effectiveness analysis
    """
    analysis = {
        "overall_pacing_score": 0.0,
        "section_pacing": {},
        "attention_curve": [],
        "engagement_peaks": [],
        "improvement_areas": [],
    }
    total_duration = demo_script.total_duration
    for section, duration in demo_script.timing_breakdown.items():
        section_ratio = duration / total_duration
        pacing_score = self._calculate_section_pacing_score(section, section_ratio)
        analysis["section_pacing"][section] = {
            "duration": duration,
            "ratio": section_ratio,
            "pacing_score": pacing_score,
        }
    section_scores = [
        data["pacing_score"] for data in analysis["section_pacing"].values()
    ]
    analysis["overall_pacing_score"] = statistics.mean(section_scores)
    for section, data in analysis["section_pacing"].items():
        if data["pacing_score"] > 80:
            analysis["engagement_peaks"].append(section)
    for section, data in analysis["section_pacing"].items():
        if data["pacing_score"] < 60:
            analysis["improvement_areas"].append(
                {
                    "section": section,
                    "issue": "Suboptimal pacing",
                    "suggestion": self._get_pacing_suggestion(section, data),
                }
            )
    return analysis


def create_timing_rehearsal_plan(
    self, demo_script: DemoScript, rehearsal_sessions: int = 3
) -> List[Dict[str, Any]]:
    """
    Create systematic rehearsal plan for timing optimization.

    Args:
        demo_script: Demo script to rehearse
        rehearsal_sessions: Number of rehearsal sessions to plan

    Returns:
        Detailed rehearsal plan
    """
    rehearsal_plan = []
    for session in range(1, rehearsal_sessions + 1):
        session_plan = {
            "session_number": session,
            "focus_areas": [],
            "timing_goals": {},
            "success_criteria": [],
            "feedback_points": [],
        }
        if session == 1:
            session_plan["focus_areas"] = [
                "Overall presentation flow",
                "Major section transitions",
                "Demo execution timing",
            ]
            session_plan["timing_goals"] = {
                "total_duration": demo_script.total_duration,
                "demo_section": demo_script.timing_breakdown.get(
                    "technical_demonstration", 180
                ),
            }
            session_plan["success_criteria"] = [
                "Complete presentation within time limit",
                "Smooth transitions between sections",
                "Demo executes without major issues",
            ]
        elif session == 2:
            session_plan["focus_areas"] = [
                "Section pacing optimization",
                "Systematic excellence emphasis",
                "Judge engagement techniques",
            ]
            session_plan["timing_goals"] = {
                section: duration
                for section, duration in demo_script.timing_breakdown.items()
            }
            session_plan["success_criteria"] = [
                "Each section within ±10% of target time",
                "Systematic elements clearly highlighted",
                "Engaging delivery throughout",
            ]
        else:
            session_plan["focus_areas"] = [
                "Presentation polish and confidence",
                "Backup plan execution",
                "Q&A preparation",
            ]
            session_plan["timing_goals"] = {
                "presentation": demo_script.total_duration - 60,
                "qa_prep": 60,
            }
            session_plan["success_criteria"] = [
                "Confident, polished delivery",
                "Backup plans ready and tested",
                "Q&A responses prepared",
            ]
        session_plan["feedback_points"] = [
            "Timing accuracy for each section",
            "Clarity of systematic excellence message",
            "Judge engagement and eye contact",
            "Technical demo reliability",
            "Overall presentation confidence",
        ]
        rehearsal_plan.append(session_plan)
    return rehearsal_plan


def generate_real_time_timing_guide(self, demo_script: DemoScript) -> Dict[str, Any]:
    """
    Generate real-time timing guide for presentation delivery.

    Args:
        demo_script: Demo script with timing information

    Returns:
        Real-time timing guide with checkpoints
    """
    timing_guide = {
        "checkpoints": [],
        "section_targets": {},
        "warning_thresholds": {},
        "recovery_strategies": {},
    }
    cumulative_time = 0
    for section, duration in demo_script.timing_breakdown.items():
        cumulative_time += duration
        checkpoint = {
            "section": section,
            "target_time": cumulative_time,
            "section_duration": duration,
            "key_message": self._get_section_key_message(section),
            "timing_cues": self._get_timing_cues(section, duration),
        }
        timing_guide["checkpoints"].append(checkpoint)
        timing_guide["section_targets"][section] = duration
        timing_guide["warning_thresholds"][section] = {
            "under_time": duration * 0.8,
            "over_time": duration * 1.2,
        }
        timing_guide["recovery_strategies"][section] = self._get_recovery_strategies(
            section
        )
    return timing_guide


def _analyze_current_timing(
    self, demo_script: DemoScript, hackathon_config: HackathonConfig
) -> TimingAnalysis:
    """Analyze current timing against constraints."""
    total_duration = demo_script.total_duration
    time_limit = hackathon_config.demo_time_limit * 60
    timing_issues = []
    optimization_suggestions = []
    if total_duration > time_limit:
        timing_issues.append(
            f"Presentation too long: {total_duration}s > {time_limit}s"
        )
        optimization_suggestions.append("Reduce content or improve pacing")
    section_ratios = {}
    for section, duration in demo_script.timing_breakdown.items():
        ratio = duration / total_duration
        section_ratios[section] = ratio
        if section == "technical_demonstration" and ratio < 0.25:
            timing_issues.append("Technical demonstration may be too short")
            optimization_suggestions.append("Allocate more time to demo section")
        if section == "systematic_excellence" and ratio < 0.08:
            timing_issues.append("Systematic excellence showcase too brief")
            optimization_suggestions.append("Emphasize systematic development more")
    pacing_score = self._calculate_overall_pacing_score(section_ratios)
    buffer_time = max(0, time_limit - total_duration)
    return TimingAnalysis(
        total_duration=total_duration,
        section_durations=demo_script.timing_breakdown.copy(),
        pacing_score=pacing_score,
        timing_issues=timing_issues,
        optimization_suggestions=optimization_suggestions,
        buffer_time=buffer_time,
    )


def _generate_pacing_recommendations(
    self,
    demo_script: DemoScript,
    hackathon_config: HackathonConfig,
    pacing_strategy: PacingStrategy,
    template_name: str,
) -> List[PacingRecommendation]:
    """Generate pacing recommendations."""
    recommendations = []
    if template_name not in self.timing_templates:
        template_name = "devpost_standard"
    optimal_ratios = self.timing_templates[template_name]
    time_limit = hackathon_config.demo_time_limit * 60
    adjusted_ratios = self._apply_pacing_strategy(optimal_ratios, pacing_strategy)
    for section, current_duration in demo_script.timing_breakdown.items():
        if section in adjusted_ratios:
            optimal_duration = int(time_limit * adjusted_ratios[section])
            if abs(current_duration - optimal_duration) > 10:
                recommendation = PacingRecommendation(
                    section=section,
                    current_duration=current_duration,
                    recommended_duration=optimal_duration,
                    adjustment_reason=self._get_adjustment_reason(
                        section, current_duration, optimal_duration, pacing_strategy
                    ),
                    implementation_tips=self._get_implementation_tips(
                        section, optimal_duration
                    ),
                )
                recommendations.append(recommendation)
    return recommendations


def _apply_timing_optimizations(
    self,
    demo_script: DemoScript,
    recommendations: List[PacingRecommendation],
    hackathon_config: HackathonConfig,
) -> DemoScript:
    """Apply timing optimizations to create optimized script."""
    optimized_timing = demo_script.timing_breakdown.copy()
    for recommendation in recommendations:
        optimized_timing[recommendation.section] = recommendation.recommended_duration
    total_optimized = sum(optimized_timing.values())
    time_limit = hackathon_config.demo_time_limit * 60
    if total_optimized > time_limit:
        reduction_factor = time_limit / total_optimized
        for section in optimized_timing:
            optimized_timing[section] = int(
                optimized_timing[section] * reduction_factor
            )
    optimized_script = DemoScript(
        opening_hook=demo_script.opening_hook,
        problem_statement=demo_script.problem_statement,
        solution_overview=demo_script.solution_overview,
        technical_demonstration=demo_script.technical_demonstration,
        systematic_excellence=demo_script.systematic_excellence,
        business_impact=demo_script.business_impact,
        closing_call_to_action=demo_script.closing_call_to_action,
        total_duration=sum(optimized_timing.values()),
        timing_breakdown=optimized_timing,
        backup_plans=demo_script.backup_plans.copy(),
    )
    return optimized_script


def _create_rehearsal_schedule(self, demo_script: DemoScript) -> List[str]:
    """Create rehearsal schedule."""
    return [
        f"Rehearsal 1: Full run-through focusing on overall flow ({demo_script.total_duration}s target)",
        f"Rehearsal 2: Section timing practice with {demo_script.timing_breakdown}",
        "Rehearsal 3: Demo reliability testing and backup plan practice",
        "Rehearsal 4: Final polish with Q&A preparation",
        "Rehearsal 5: Dress rehearsal with full setup and timing",
    ]


def _generate_contingency_plans(
    self, demo_script: DemoScript, hackathon_config: HackathonConfig
) -> List[str]:
    """Generate contingency plans for timing issues."""
    return [
        f"If running long: Skip business impact section (saves {demo_script.timing_breakdown.get('business_impact', 60)}s)",
        f"If demo fails: Use backup screenshots (saves {demo_script.timing_breakdown.get('technical_demonstration', 180) - 60}s)",
        "If questions interrupt: Politely defer to end to maintain timing",
        "If technical issues: Have pre-recorded demo ready",
        f"Emergency 3-minute version: Opening + Demo + Systematic + Closing",
    ]


def _calculate_section_pacing_score(self, section: str, ratio: float) -> float:
    """Calculate pacing score for a section."""
    optimal_ratios = {
        "opening_hook": 0.05,
        "problem_statement": 0.15,
        "solution_overview": 0.2,
        "technical_demonstration": 0.35,
        "systematic_excellence": 0.1,
        "business_impact": 0.1,
        "closing_call_to_action": 0.05,
    }
    if section not in optimal_ratios:
        return 50.0
    optimal = optimal_ratios[section]
    deviation = abs(ratio - optimal) / optimal
    score = max(0, 100 - deviation * 100)
    return score


def _calculate_overall_pacing_score(self, section_ratios: Dict[str, float]) -> float:
    """Calculate overall pacing score."""
    section_scores = []
    for section, ratio in section_ratios.items():
        score = self._calculate_section_pacing_score(section, ratio)
        section_scores.append(score)
    return statistics.mean(section_scores) if section_scores else 50.0


def _apply_pacing_strategy(
    self, base_ratios: Dict[str, float], strategy: PacingStrategy
) -> Dict[str, float]:
    """Apply pacing strategy to base ratios."""
    adjusted_ratios = base_ratios.copy()
    if strategy == PacingStrategy.DEMO_FOCUSED:
        adjusted_ratios["technical_demonstration"] *= 1.2
        for section in adjusted_ratios:
            if section != "technical_demonstration":
                adjusted_ratios[section] *= 0.9
    elif strategy == PacingStrategy.SYSTEMATIC_EMPHASIS:
        adjusted_ratios["systematic_excellence"] *= 1.5
        for section in adjusted_ratios:
            if section != "systematic_excellence":
                adjusted_ratios[section] *= 0.95
    elif strategy == PacingStrategy.FRONT_LOADED:
        adjusted_ratios["problem_statement"] *= 1.2
        adjusted_ratios["solution_overview"] *= 1.1
        adjusted_ratios["business_impact"] *= 0.8
        adjusted_ratios["closing_call_to_action"] *= 0.8
    total = sum(adjusted_ratios.values())
    for section in adjusted_ratios:
        adjusted_ratios[section] /= total
    return adjusted_ratios


def _get_adjustment_reason(
    self, section: str, current: int, optimal: int, strategy: PacingStrategy
) -> str:
    """Get reason for timing adjustment."""
    if current > optimal:
        return f"Reduce {section} by {current - optimal}s for better pacing with {strategy.value} strategy"
    else:
        return f"Increase {section} by {optimal - current}s to optimize for {strategy.value} strategy"


def _get_implementation_tips(self, section: str, duration: int) -> List[str]:
    """Get implementation tips for section timing."""
    tips = {
        "opening_hook": [
            "Practice opening line for immediate impact",
            "Use compelling statistic or demo teaser",
            "Keep energy high and confident",
        ],
        "problem_statement": [
            "Use specific, relatable examples",
            "Quantify the problem impact",
            "Set up systematic solution approach",
        ],
        "technical_demonstration": [
            "Practice demo sequence multiple times",
            "Have backup screenshots ready",
            "Narrate clearly while demonstrating",
        ],
        "systematic_excellence": [
            "Emphasize development maturity",
            "Show concrete systematic evidence",
            "Differentiate from ad-hoc approaches",
        ],
    }
    return tips.get(
        section, ["Practice timing for this section", "Keep content focused and clear"]
    )


def _get_pacing_suggestion(self, section: str, data: Dict[str, Any]) -> str:
    """Get pacing suggestion for improvement."""
    if data["pacing_score"] < 40:
        return f"Consider major restructuring of {section} - timing significantly off"
    elif data["pacing_score"] < 60:
        return f"Adjust {section} timing - currently {data['duration']}s, consider optimizing"
    else:
        return f"Minor timing adjustment needed for {section}"


def _get_section_key_message(self, section: str) -> str:
    """Get key message for section."""
    messages = {
        "opening_hook": "Grab attention and establish credibility",
        "problem_statement": "Clear problem with quantified impact",
        "solution_overview": "Systematic solution approach",
        "technical_demonstration": "Working solution with systematic quality",
        "systematic_excellence": "Development maturity and competitive advantage",
        "business_impact": "Real-world value and market opportunity",
        "closing_call_to_action": "Strong finish with clear next steps",
    }
    return messages.get(section, "Key section message")


def _get_timing_cues(self, section: str, duration: int) -> List[str]:
    """Get timing cues for section delivery."""
    return [
        f"Target duration: {duration} seconds",
        f"Halfway point: {duration // 2} seconds",
        f"Wrap-up cue: {duration - 15} seconds",
    ]


def _get_recovery_strategies(self, section: str) -> List[str]:
    """Get recovery strategies for timing issues."""
    return [
        f"If running long in {section}: Skip detailed examples, focus on key points",
        f"If running short in {section}: Add systematic development details",
        "Use transition phrases to adjust pacing naturally",
    ]
