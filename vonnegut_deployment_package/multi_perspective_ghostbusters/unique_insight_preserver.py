#!/usr/bin/env python3
"""
Unique Insight Preserver - Multi-Perspective Ghostbusters Component
=================================================================

Synthesis component for preserving unique insights (< 200 lines)
Implements "Diversity is the only free lunch" through insight preservation.

Author: Beast Mode Framework
Date: 2025-01-27
Context: Synthesis Context
Pattern: DomainService
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.multi_perspective_ghostbusters.security_expert import PerspectiveResult
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class UniqueInsight:
    """Insight unique to a specific perspective."""
    insight_id: str
    originating_perspective: str
    insight_content: str
    uniqueness_score: float
    original_context: Dict[str, Any]
    reasoning_chain: List[str]
    value_assessment: float


@dataclass
class InsightValue:
    """Assessment of insight value and relevance."""
    value_id: str
    insight_id: str
    relevance_score: float
    novelty_score: float
    actionability_score: float
    overall_value: float


class UniqueInsightPreserver(ReflectiveModule):
    """
    Unique insight preservation component for multi-perspective analysis.
    
    Implements insight preservation where "Diversity is the only free lunch" -
    ensuring that valuable unique contributions from individual perspectives
    are not lost during synthesis, maintaining the diversity benefit.
    """

    def __init__(self):
        super().__init__()
        self.preserver_id = f"unique_insight_preserver_{int(datetime.now().timestamp())}"
        
        # Store unique insight data in unified CMS
        self.store_content("unique_insights", "unique_insight_analysis", {
            "preserved_insights": {},
            "value_assessments": {},
            "traceability_records": {}
        })

    def identify_unique_insights(self, perspectives: List[PerspectiveResult]) -> List[UniqueInsight]:
        """Identify insights unique to individual perspectives."""
        
        if len(perspectives) < 2:
            return []
        
        unique_insights = []
        
        # Analyze each perspective for unique contributions
        for perspective in perspectives:
            perspective_unique_insights = self._find_perspective_unique_insights(
                perspective, perspectives
            )
            unique_insights.extend(perspective_unique_insights)
        
        # Store unique insights in CMS
        for insight in unique_insights:
            self.store_content(insight.insight_id, "unique_insight", insight.__dict__)
        
        return unique_insights

    def preserve_original_context(self, unique_insights: List[UniqueInsight]) -> Dict[str, Dict[str, Any]]:
        """Preserve original context and reasoning chains."""
        
        context_preservation = {}
        
        for insight in unique_insights:
            preserved_context = {
                "original_perspective": insight.originating_perspective,
                "reasoning_chain": insight.reasoning_chain,
                "context_metadata": insight.original_context,
                "preservation_timestamp": datetime.now().isoformat(),
                "traceability_id": f"trace_{insight.insight_id}"
            }
            
            context_preservation[insight.insight_id] = preserved_context
        
        # Store context preservation in CMS
        self.store_content("context_preservation", "preserved_contexts", context_preservation)
        
        return context_preservation

    def assess_insight_value(self, unique_insights: List[UniqueInsight]) -> List[InsightValue]:
        """Assess potential value and relevance of unique insights."""
        
        value_assessments = []
        
        for insight in unique_insights:
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(insight)
            
            # Calculate novelty score
            novelty_score = self._calculate_novelty_score(insight)
            
            # Calculate actionability score
            actionability_score = self._calculate_actionability_score(insight)
            
            # Calculate overall value
            overall_value = (relevance_score + novelty_score + actionability_score) / 3
            
            value_assessment = InsightValue(
                value_id=f"value_assessment_{int(datetime.now().timestamp())}",
                insight_id=insight.insight_id,
                relevance_score=relevance_score,
                novelty_score=novelty_score,
                actionability_score=actionability_score,
                overall_value=overall_value
            )
            
            value_assessments.append(value_assessment)
        
        # Store value assessments in CMS
        for assessment in value_assessments:
            self.store_content(assessment.value_id, "insight_value_assessment", assessment.__dict__)
        
        return value_assessments

    def maintain_traceability(self, unique_insights: List[UniqueInsight]) -> Dict[str, str]:
        """Maintain traceability to originating perspectives."""
        
        traceability_map = {}
        
        for insight in unique_insights:
            traceability_record = {
                "insight_id": insight.insight_id,
                "originating_perspective": insight.originating_perspective,
                "traceability_chain": [
                    f"Generated by {insight.originating_perspective}",
                    f"Preserved at {datetime.now().isoformat()}",
                    f"Uniqueness score: {insight.uniqueness_score}"
                ],
                "preservation_metadata": {
                    "preserver_id": self.preserver_id,
                    "preservation_method": "unique_insight_identification",
                    "context_preserved": True
                }
            }
            
            traceability_map[insight.insight_id] = insight.originating_perspective
        
        # Store traceability records in CMS
        self.store_content("traceability_records", "insight_traceability", traceability_map)
        
        return traceability_map

    def ensure_synthesis_preservation(self, unique_insights: List[UniqueInsight]) -> Dict[str, Any]:
        """Ensure unique insights are not lost during synthesis."""
        
        preservation_strategy = {
            "preservation_method": "explicit_unique_insight_tracking",
            "insights_to_preserve": [],
            "preservation_rules": [
                "High-value unique insights must be explicitly included in synthesis",
                "Original context and reasoning must be maintained",
                "Traceability to originating perspective must be preserved",
                "Unique insights should be clearly marked in final output"
            ],
            "quality_gates": {
                "minimum_uniqueness_score": 0.6,
                "minimum_value_score": 0.5,
                "required_context_preservation": True
            }
        }
        
        # Identify insights that meet preservation criteria
        for insight in unique_insights:
            if (insight.uniqueness_score >= 0.6 and 
                insight.value_assessment >= 0.5):
                preservation_strategy["insights_to_preserve"].append({
                    "insight_id": insight.insight_id,
                    "preservation_priority": "high",
                    "originating_perspective": insight.originating_perspective,
                    "preservation_reason": "Meets quality gates for unique value"
                })
        
        # Store preservation strategy in CMS
        self.store_content("preservation_strategy", "synthesis_preservation", preservation_strategy)
        
        return preservation_strategy

    def _find_perspective_unique_insights(self, target_perspective: PerspectiveResult, 
                                        all_perspectives: List[PerspectiveResult]) -> List[UniqueInsight]:
        """Find insights unique to a specific perspective."""
        
        unique_insights = []
        other_perspectives = [p for p in all_perspectives if p.agent_id != target_perspective.agent_id]
        
        # Analyze insights for uniqueness
        for insight in target_perspective.insights:
            uniqueness_score = self._calculate_uniqueness_score(insight, other_perspectives)
            
            if uniqueness_score >= 0.5:  # Threshold for considering insight unique
                unique_insight = UniqueInsight(
                    insight_id=f"unique_{target_perspective.agent_id}_{int(datetime.now().timestamp())}",
                    originating_perspective=target_perspective.perspective_type,
                    insight_content=str(insight),
                    uniqueness_score=uniqueness_score,
                    original_context={
                        "agent_id": target_perspective.agent_id,
                        "analysis_timestamp": target_perspective.analysis_timestamp.isoformat(),
                        "confidence_score": target_perspective.confidence_score
                    },
                    reasoning_chain=target_perspective.reasoning_chain,
                    value_assessment=0.0  # Will be calculated separately
                )
                unique_insights.append(unique_insight)
        
        # Analyze unique contributions
        for contribution in target_perspective.unique_contributions:
            unique_insight = UniqueInsight(
                insight_id=f"contribution_{target_perspective.agent_id}_{int(datetime.now().timestamp())}",
                originating_perspective=target_perspective.perspective_type,
                insight_content=str(contribution),
                uniqueness_score=0.9,  # Unique contributions are inherently unique
                original_context={
                    "agent_id": target_perspective.agent_id,
                    "contribution_type": "unique_contribution"
                },
                reasoning_chain=target_perspective.reasoning_chain,
                value_assessment=0.0
            )
            unique_insights.append(unique_insight)
        
        return unique_insights

    def _calculate_uniqueness_score(self, insight: Any, other_perspectives: List[PerspectiveResult]) -> float:
        """Calculate how unique an insight is compared to other perspectives."""
        
        insight_text = str(insight).lower()
        similarity_scores = []
        
        for other_perspective in other_perspectives:
            max_similarity = 0.0
            
            # Check similarity with other insights
            for other_insight in other_perspective.insights:
                other_text = str(other_insight).lower()
                similarity = self._calculate_text_similarity(insight_text, other_text)
                max_similarity = max(max_similarity, similarity)
            
            similarity_scores.append(max_similarity)
        
        # Uniqueness is inverse of maximum similarity
        if similarity_scores:
            max_similarity = max(similarity_scores)
            uniqueness_score = 1.0 - max_similarity
        else:
            uniqueness_score = 1.0
        
        return uniqueness_score

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity calculation."""
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    def _calculate_relevance_score(self, insight: UniqueInsight) -> float:
        """Calculate relevance score for an insight."""
        
        # Simple relevance scoring based on content keywords
        relevant_keywords = ["critical", "important", "significant", "risk", "opportunity", "improvement"]
        insight_text = insight.insight_content.lower()
        
        relevance_count = sum(1 for keyword in relevant_keywords if keyword in insight_text)
        return min(relevance_count * 0.2, 1.0)

    def _calculate_novelty_score(self, insight: UniqueInsight) -> float:
        """Calculate novelty score for an insight."""
        
        # Novelty is closely related to uniqueness
        return insight.uniqueness_score

    def _calculate_actionability_score(self, insight: UniqueInsight) -> float:
        """Calculate actionability score for an insight."""
        
        # Simple actionability scoring based on action keywords
        action_keywords = ["should", "must", "recommend", "implement", "improve", "fix", "address"]
        insight_text = insight.insight_content.lower()
        
        action_count = sum(1 for keyword in action_keywords if keyword in insight_text)
        return min(action_count * 0.25, 1.0)

    def execute(self, *args, **kwargs) -> Any:
        """Execute unique insight preservation operations."""
        return {
            "preserver_id": self.preserver_id,
            "component_type": "UniqueInsightPreserver",
            "capabilities": ["unique_insight_identification", "context_preservation", "value_assessment", "traceability"],
            "status": "operational"
        }


def main():
    """Test the UniqueInsightPreserver component."""
    preserver = UniqueInsightPreserver()
    
    print("🚨 Unique Insight Preserver - Multi-Perspective Ghostbusters Component 🚨")
    print(f"Preserver ID: {preserver.preserver_id}")
    print(f"Context: {preserver.bounded_context.name}")
    print(f"Pattern: {preserver.ddd_pattern}")
    print("✅ Unique insight preserver operational!")


if __name__ == "__main__":
    main()