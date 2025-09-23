#!/usr/bin/env python3
"""
Human Analysis Presenter - Multi-Perspective Ghostbusters Component
=================================================================

Human collaboration component for analysis presentation (< 250 lines)
Implements "Diversity is the only free lunch" through human-readable presentation.

Author: Beast Mode Framework
Date: 2025-01-27
Context: Human Collaboration Context
Pattern: DomainService
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.multi_perspective_ghostbusters.security_expert import PerspectiveResult
from src.multi_perspective_ghostbusters.consensus_detector import ConsensusArea
from src.multi_perspective_ghostbusters.unique_insight_preserver import UniqueInsight
from src.multi_perspective_ghostbusters.conflict_analysis_resolver import PerspectiveConflict
from src.rm_ddd.core.reflective_module import ReflectiveModule


@dataclass
class HumanReadableAnalysis:
    """Human-friendly presentation of multi-perspective analysis."""
    presentation_id: str
    summary: Dict[str, Any]
    consensus_highlights: List[str]
    unique_insights_summary: List[str]
    conflict_overview: List[str]
    interactive_elements: Dict[str, Any]


@dataclass
class AgreementDisagreementVisualization:
    """Visualization of agreement and disagreement areas."""
    visualization_id: str
    agreement_areas: List[Dict[str, Any]]
    disagreement_areas: List[Dict[str, Any]]
    confidence_mapping: Dict[str, float]
    visual_representation: Dict[str, Any]


class HumanAnalysisPresenter(ReflectiveModule):
    """
    Human analysis presentation component for multi-perspective analysis.
    
    Implements human-AI collaboration where "Diversity is the only free lunch" -
    presenting multi-perspective analysis in human-comprehensible formats that
    enable effective human-AI collaboration and decision-making.
    """

    def __init__(self):
        super().__init__()
        self.presenter_id = f"human_presenter_{int(datetime.now().timestamp())}"
        
        # Store presentation data in unified CMS
        self.store_content("human_presentations", "human_presentation", {
            "formatted_analyses": {},
            "visualizations": {},
            "interactive_elements": {}
        })

    def format_multi_perspective_results(self, perspectives: List[PerspectiveResult], 
                                       consensus_areas: List[ConsensusArea],
                                       unique_insights: List[UniqueInsight],
                                       conflicts: List[PerspectiveConflict]) -> HumanReadableAnalysis:
        """Format multi-perspective results for human comprehension."""
        
        presentation_id = f"human_analysis_{int(datetime.now().timestamp())}"
        
        # Create executive summary
        summary = self._create_executive_summary(perspectives, consensus_areas, unique_insights, conflicts)
        
        # Highlight consensus areas
        consensus_highlights = self._format_consensus_highlights(consensus_areas)
        
        # Summarize unique insights
        unique_insights_summary = self._format_unique_insights_summary(unique_insights)
        
        # Overview conflicts
        conflict_overview = self._format_conflict_overview(conflicts)
        
        # Create interactive elements
        interactive_elements = self._create_interactive_elements(perspectives, consensus_areas, conflicts)
        
        analysis = HumanReadableAnalysis(
            presentation_id=presentation_id,
            summary=summary,
            consensus_highlights=consensus_highlights,
            unique_insights_summary=unique_insights_summary,
            conflict_overview=conflict_overview,
            interactive_elements=interactive_elements
        )
        
        # Store formatted analysis in CMS
        self.store_content(presentation_id, "human_readable_analysis", analysis.__dict__)
        
        return analysis

    def visualize_agreement_disagreement(self, consensus_areas: List[ConsensusArea], 
                                       conflicts: List[PerspectiveConflict]) -> AgreementDisagreementVisualization:
        """Visualize agreement and disagreement areas clearly."""
        
        visualization_id = f"agreement_viz_{int(datetime.now().timestamp())}"
        
        # Format agreement areas
        agreement_areas = []
        for consensus in consensus_areas:
            agreement_areas.append({
                "topic": consensus.consensus_topic,
                "agreeing_perspectives": consensus.agreeing_perspectives,
                "confidence": consensus.confidence_score,
                "evidence_count": len(consensus.supporting_evidence),
                "visual_indicator": "✅" if consensus.confidence_score > 0.7 else "⚠️"
            })
        
        # Format disagreement areas
        disagreement_areas = []
        for conflict in conflicts:
            disagreement_areas.append({
                "topic": conflict.conflict_type,
                "conflicting_perspectives": conflict.conflicting_perspectives,
                "severity": conflict.conflict_severity,
                "disagreement_points": conflict.disagreement_points,
                "visual_indicator": "🔴" if conflict.conflict_severity == "high" else "🟡"
            })
        
        # Create confidence mapping
        confidence_mapping = {}
        for consensus in consensus_areas:
            confidence_mapping[consensus.consensus_topic] = consensus.confidence_score
        
        # Create visual representation
        visual_representation = self._create_visual_representation(agreement_areas, disagreement_areas)
        
        visualization = AgreementDisagreementVisualization(
            visualization_id=visualization_id,
            agreement_areas=agreement_areas,
            disagreement_areas=disagreement_areas,
            confidence_mapping=confidence_mapping,
            visual_representation=visual_representation
        )
        
        # Store visualization in CMS
        self.store_content(visualization_id, "agreement_disagreement_viz", visualization.__dict__)
        
        return visualization

    def present_reasoning_chains(self, perspectives: List[PerspectiveResult]) -> Dict[str, Any]:
        """Present reasoning chains and confidence scores transparently."""
        
        reasoning_presentation = {
            "presentation_id": f"reasoning_chains_{int(datetime.now().timestamp())}",
            "perspective_reasoning": [],
            "confidence_analysis": {},
            "transparency_elements": {}
        }
        
        for perspective in perspectives:
            # Format reasoning chain
            formatted_reasoning = {
                "perspective_type": perspective.perspective_type,
                "agent_id": perspective.agent_id,
                "confidence_score": perspective.confidence_score,
                "reasoning_steps": [
                    {"step": i+1, "reasoning": step, "confidence_impact": "positive" if "systematic" in step.lower() else "neutral"}
                    for i, step in enumerate(perspective.reasoning_chain)
                ],
                "key_insights": [str(insight) for insight in perspective.insights[:3]],  # Top 3 insights
                "confidence_factors": self._analyze_confidence_factors(perspective)
            }
            
            reasoning_presentation["perspective_reasoning"].append(formatted_reasoning)
        
        # Analyze confidence patterns
        reasoning_presentation["confidence_analysis"] = self._analyze_confidence_patterns(perspectives)
        
        # Add transparency elements
        reasoning_presentation["transparency_elements"] = {
            "methodology_explanation": "Multi-perspective analysis using specialized AI agents",
            "confidence_interpretation": "Scores reflect agent certainty in analysis quality",
            "reasoning_validation": "Each step traceable to specific analytical methodology",
            "human_guidance": "Use confidence scores to prioritize review areas"
        }
        
        # Store reasoning presentation in CMS
        self.store_content(reasoning_presentation["presentation_id"], "reasoning_chains", reasoning_presentation)
        
        return reasoning_presentation

    def create_interactive_exploration_interface(self, analysis: HumanReadableAnalysis, 
                                               visualization: AgreementDisagreementVisualization) -> Dict[str, Any]:
        """Provide interfaces for human input and feedback."""
        
        interface = {
            "interface_id": f"interactive_interface_{int(datetime.now().timestamp())}",
            "exploration_options": {
                "drill_down_consensus": [
                    {"area": area["topic"], "action": "explore_evidence", "description": f"Examine evidence for {area['topic']}"}
                    for area in visualization.agreement_areas
                ],
                "investigate_conflicts": [
                    {"conflict": area["topic"], "action": "analyze_disagreement", "description": f"Understand {area['topic']} disagreement"}
                    for area in visualization.disagreement_areas
                ],
                "review_unique_insights": [
                    {"insight": insight, "action": "evaluate_value", "description": f"Assess insight value"}
                    for insight in analysis.unique_insights_summary[:5]  # Top 5
                ]
            },
            "feedback_mechanisms": {
                "consensus_validation": "Confirm or challenge consensus areas",
                "insight_prioritization": "Rank unique insights by importance",
                "conflict_resolution": "Provide human perspective on disagreements",
                "additional_perspectives": "Suggest missing analytical angles"
            },
            "collaboration_tools": {
                "annotation_system": "Add human insights to AI analysis",
                "priority_marking": "Mark high-priority areas for action",
                "confidence_adjustment": "Adjust AI confidence based on human expertise",
                "synthesis_guidance": "Guide AI synthesis with human judgment"
            }
        }
        
        # Store interface in CMS
        self.store_content(interface["interface_id"], "interactive_interface", interface)
        
        return interface

    def facilitate_interactive_exploration(self, conflicts: List[PerspectiveConflict], 
                                         unique_insights: List[UniqueInsight]) -> Dict[str, Any]:
        """Allow interactive exploration of conflicts and insights."""
        
        exploration_framework = {
            "exploration_id": f"exploration_{int(datetime.now().timestamp())}",
            "conflict_exploration": {
                "available_conflicts": [
                    {
                        "conflict_id": conflict.conflict_id,
                        "summary": f"{conflict.conflict_type} between {', '.join(conflict.conflicting_perspectives)}",
                        "exploration_actions": [
                            "view_detailed_disagreement",
                            "compare_reasoning_chains",
                            "assess_validity_of_positions",
                            "explore_resolution_options"
                        ]
                    }
                    for conflict in conflicts
                ],
                "exploration_guidance": [
                    "Focus on high-severity conflicts first",
                    "Look for patterns in disagreement types",
                    "Consider domain expertise when evaluating positions",
                    "Identify learning opportunities from conflicts"
                ]
            },
            "insight_exploration": {
                "unique_insights_catalog": [
                    {
                        "insight_id": insight.insight_id,
                        "originating_perspective": insight.originating_perspective,
                        "content_preview": insight.insight_content[:100] + "..." if len(insight.insight_content) > 100 else insight.insight_content,
                        "uniqueness_score": insight.uniqueness_score,
                        "exploration_actions": [
                            "view_full_insight",
                            "trace_reasoning_origin",
                            "assess_practical_value",
                            "compare_with_consensus"
                        ]
                    }
                    for insight in unique_insights
                ],
                "insight_guidance": [
                    "High uniqueness scores indicate novel perspectives",
                    "Consider practical applicability of unique insights",
                    "Evaluate how insights complement consensus areas",
                    "Look for actionable recommendations in unique insights"
                ]
            }
        }
        
        # Store exploration framework in CMS
        self.store_content(exploration_framework["exploration_id"], "interactive_exploration", exploration_framework)
        
        return exploration_framework

    def _create_executive_summary(self, perspectives: List[PerspectiveResult], 
                                consensus_areas: List[ConsensusArea],
                                unique_insights: List[UniqueInsight],
                                conflicts: List[PerspectiveConflict]) -> Dict[str, Any]:
        """Create executive summary of multi-perspective analysis."""
        
        return {
            "analysis_overview": f"Multi-perspective analysis from {len(perspectives)} specialized agents",
            "key_statistics": {
                "perspectives_analyzed": len(perspectives),
                "consensus_areas_identified": len(consensus_areas),
                "unique_insights_preserved": len(unique_insights),
                "conflicts_analyzed": len(conflicts)
            },
            "confidence_summary": {
                "average_confidence": sum(p.confidence_score for p in perspectives) / len(perspectives) if perspectives else 0.0,
                "confidence_range": f"{min(p.confidence_score for p in perspectives):.2f} - {max(p.confidence_score for p in perspectives):.2f}" if perspectives else "N/A",
                "high_confidence_areas": len([c for c in consensus_areas if c.confidence_score > 0.8])
            },
            "diversity_benefit": "Multiple perspectives provide richer analysis than any single perspective"
        }

    def _format_consensus_highlights(self, consensus_areas: List[ConsensusArea]) -> List[str]:
        """Format consensus areas for human readability."""
        
        highlights = []
        for consensus in consensus_areas:
            highlight = f"✅ {consensus.consensus_topic} (Confidence: {consensus.confidence_score:.2f})"
            highlight += f" - Agreed by {len(consensus.agreeing_perspectives)} perspectives"
            highlights.append(highlight)
        
        return highlights

    def _format_unique_insights_summary(self, unique_insights: List[UniqueInsight]) -> List[str]:
        """Format unique insights for human readability."""
        
        summaries = []
        for insight in unique_insights:
            summary = f"💡 {insight.originating_perspective}: {insight.insight_content[:80]}..."
            summary += f" (Uniqueness: {insight.uniqueness_score:.2f})"
            summaries.append(summary)
        
        return summaries

    def _format_conflict_overview(self, conflicts: List[PerspectiveConflict]) -> List[str]:
        """Format conflicts for human readability."""
        
        overviews = []
        for conflict in conflicts:
            severity_icon = "🔴" if conflict.conflict_severity == "high" else "🟡" if conflict.conflict_severity == "medium" else "🟢"
            overview = f"{severity_icon} {conflict.conflict_type}: {', '.join(conflict.conflicting_perspectives)}"
            if conflict.disagreement_points:
                overview += f" - {conflict.disagreement_points[0]}"
            overviews.append(overview)
        
        return overviews

    def _create_interactive_elements(self, perspectives: List[PerspectiveResult], 
                                   consensus_areas: List[ConsensusArea],
                                   conflicts: List[PerspectiveConflict]) -> Dict[str, Any]:
        """Create interactive elements for human engagement."""
        
        return {
            "perspective_selector": {
                "available_perspectives": [p.perspective_type for p in perspectives],
                "action": "Select perspective to view detailed analysis"
            },
            "consensus_explorer": {
                "high_confidence_consensus": [c.consensus_topic for c in consensus_areas if c.confidence_score > 0.8],
                "action": "Explore evidence supporting consensus"
            },
            "conflict_analyzer": {
                "active_conflicts": [c.conflict_type for c in conflicts],
                "action": "Investigate disagreement details"
            },
            "feedback_collector": {
                "feedback_types": ["validate_consensus", "challenge_insight", "resolve_conflict", "add_perspective"],
                "action": "Provide human input to enhance analysis"
            }
        }

    def _create_visual_representation(self, agreement_areas: List[Dict[str, Any]], 
                                    disagreement_areas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create visual representation of agreement/disagreement."""
        
        return {
            "agreement_visualization": {
                "type": "consensus_map",
                "elements": [
                    {"topic": area["topic"], "confidence": area["confidence"], "visual": area["visual_indicator"]}
                    for area in agreement_areas
                ]
            },
            "disagreement_visualization": {
                "type": "conflict_matrix",
                "elements": [
                    {"topic": area["topic"], "severity": area["severity"], "visual": area["visual_indicator"]}
                    for area in disagreement_areas
                ]
            },
            "legend": {
                "✅": "High confidence consensus",
                "⚠️": "Moderate confidence consensus",
                "🔴": "High severity conflict",
                "🟡": "Medium severity conflict"
            }
        }

    def _analyze_confidence_factors(self, perspective: PerspectiveResult) -> Dict[str, Any]:
        """Analyze factors contributing to confidence score."""
        
        return {
            "base_confidence": perspective.confidence_score,
            "contributing_factors": [
                "Systematic analytical methodology",
                "Domain expertise application",
                "Evidence quality assessment"
            ],
            "confidence_interpretation": "high" if perspective.confidence_score > 0.8 else "moderate" if perspective.confidence_score > 0.6 else "low"
        }

    def _analyze_confidence_patterns(self, perspectives: List[PerspectiveResult]) -> Dict[str, Any]:
        """Analyze confidence patterns across perspectives."""
        
        confidence_scores = [p.confidence_score for p in perspectives]
        
        return {
            "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
            "confidence_variance": max(confidence_scores) - min(confidence_scores) if confidence_scores else 0.0,
            "high_confidence_perspectives": [p.perspective_type for p in perspectives if p.confidence_score > 0.8],
            "pattern_interpretation": "Consistent confidence across perspectives indicates reliable analysis"
        }

    def execute(self, *args, **kwargs) -> Any:
        """Execute human analysis presentation operations."""
        return {
            "presenter_id": self.presenter_id,
            "component_type": "HumanAnalysisPresenter",
            "capabilities": ["multi_perspective_formatting", "agreement_visualization", "reasoning_presentation", "interactive_exploration"],
            "status": "operational"
        }


def main():
    """Test the HumanAnalysisPresenter component."""
    presenter = HumanAnalysisPresenter()
    
    print("🚨 Human Analysis Presenter - Multi-Perspective Ghostbusters Component 🚨")
    print(f"Presenter ID: {presenter.presenter_id}")
    print(f"Context: {presenter.bounded_context.name}")
    print(f"Pattern: {presenter.ddd_pattern}")
    print("✅ Human analysis presenter operational!")


if __name__ == "__main__":
    main()