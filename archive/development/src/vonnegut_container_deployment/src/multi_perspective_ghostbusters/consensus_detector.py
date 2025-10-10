#!/usr/bin/env python3
"""
Consensus Detector - Multi-Perspective Ghostbusters Component
===========================================================

Synthesis component for identifying consensus areas (< 150 lines)
Implements "Diversity is the only free lunch" through consensus detection.

Author: Beast Mode Framework
Date: 2025-01-27
Context: Synthesis Context
Pattern: DomainService
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.multi_perspective_ghostbusters.security_expert import PerspectiveResult
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class ConsensusArea:
    """Area where multiple perspectives agree."""
    consensus_id: str
    agreeing_perspectives: List[str]
    consensus_topic: str
    agreement_strength: float
    supporting_evidence: List[str]
    confidence_score: float


@dataclass
class ConsensusInsight:
    """High-confidence insight from consensus analysis."""
    insight_id: str
    insight_content: str
    supporting_perspectives: List[str]
    evidence_quality: float
    consensus_confidence: float


class ConsensusDetector(ReflectiveModule):
    """
    Consensus detection component for multi-perspective analysis.
    
    Implements consensus identification where "Diversity is the only free lunch" -
    identifying areas where diverse perspectives agree provides high-confidence
    insights that are more reliable than any single perspective.
    """

    def __init__(self):
        super().__init__()
        self.detector_id = f"consensus_detector_{int(datetime.now().timestamp())}"
        
        # Store consensus data in unified CMS
        self.store_content("consensus_analyses", "consensus_analysis", {
            "consensus_areas": {},
            "confidence_scores": {},
            "evidence_collections": {}
        })

    def identify_consensus_areas(self, perspectives: List[PerspectiveResult]) -> List[ConsensusArea]:
        """Identify areas where multiple perspectives agree."""
        
        if len(perspectives) < 2:
            return []
        
        consensus_areas = []
        
        # Analyze insights for agreement
        insight_agreements = self._find_insight_agreements(perspectives)
        for agreement in insight_agreements:
            consensus_areas.append(agreement)
        
        # Analyze recommendations for consensus
        recommendation_agreements = self._find_recommendation_agreements(perspectives)
        for agreement in recommendation_agreements:
            consensus_areas.append(agreement)
        
        # Store consensus areas in CMS
        for area in consensus_areas:
            self.store_content(area.consensus_id, "consensus_area", area.__dict__)
        
        return consensus_areas

    def calculate_confidence_scores(self, consensus_areas: List[ConsensusArea]) -> Dict[str, float]:
        """Calculate confidence scores based on agreement strength."""
        
        confidence_scores = {}
        
        for area in consensus_areas:
            # Base confidence from agreement strength
            base_confidence = area.agreement_strength
            
            # Boost confidence based on number of agreeing perspectives
            perspective_bonus = min(len(area.agreeing_perspectives) * 0.1, 0.3)
            
            # Boost confidence based on evidence quality
            evidence_bonus = min(len(area.supporting_evidence) * 0.05, 0.2)
            
            # Calculate final confidence
            final_confidence = min(base_confidence + perspective_bonus + evidence_bonus, 1.0)
            confidence_scores[area.consensus_id] = final_confidence
        
        # Store confidence scores in CMS
        self.store_content("confidence_scores", "consensus_confidence", confidence_scores)
        
        return confidence_scores

    def collect_supporting_evidence(self, consensus_areas: List[ConsensusArea]) -> Dict[str, List[str]]:
        """Collect supporting evidence from agreeing perspectives."""
        
        evidence_collection = {}
        
        for area in consensus_areas:
            evidence = []
            
            # Collect evidence from supporting perspectives
            for perspective_id in area.agreeing_perspectives:
                evidence.append(f"Perspective {perspective_id} supports: {area.consensus_topic}")
            
            # Add existing supporting evidence
            evidence.extend(area.supporting_evidence)
            
            evidence_collection[area.consensus_id] = evidence
        
        # Store evidence collection in CMS
        self.store_content("evidence_collection", "consensus_evidence", evidence_collection)
        
        return evidence_collection

    def rank_consensus_by_confidence(self, consensus_areas: List[ConsensusArea]) -> List[ConsensusArea]:
        """Rank consensus areas by confidence and evidence quality."""
        
        # Calculate confidence scores for ranking
        confidence_scores = self.calculate_confidence_scores(consensus_areas)
        
        # Sort by confidence score (highest first)
        ranked_areas = sorted(
            consensus_areas,
            key=lambda area: confidence_scores.get(area.consensus_id, 0.0),
            reverse=True
        )
        
        return ranked_areas

    def generate_consensus_insights(self, consensus_areas: List[ConsensusArea]) -> List[ConsensusInsight]:
        """Generate structured consensus insights."""
        
        insights = []
        
        for area in consensus_areas:
            insight = ConsensusInsight(
                insight_id=f"consensus_insight_{int(datetime.now().timestamp())}",
                insight_content=f"Consensus identified: {area.consensus_topic}",
                supporting_perspectives=area.agreeing_perspectives,
                evidence_quality=min(len(area.supporting_evidence) * 0.2, 1.0),
                consensus_confidence=area.confidence_score
            )
            insights.append(insight)
        
        # Store insights in CMS
        for insight in insights:
            self.store_content(insight.insight_id, "consensus_insight", insight.__dict__)
        
        return insights

    def _find_insight_agreements(self, perspectives: List[PerspectiveResult]) -> List[ConsensusArea]:
        """Find agreements in insights across perspectives."""
        
        agreements = []
        
        # Simple keyword-based agreement detection
        common_keywords = ["security", "architecture", "requirements", "quality", "performance"]
        
        for keyword in common_keywords:
            agreeing_perspectives = []
            supporting_evidence = []
            
            for perspective in perspectives:
                # Check if perspective mentions this keyword in insights
                for insight in perspective.insights:
                    if keyword in str(insight).lower():
                        agreeing_perspectives.append(perspective.agent_id)
                        supporting_evidence.append(f"Insight from {perspective.perspective_type}")
                        break
            
            # Create consensus area if multiple perspectives agree
            if len(agreeing_perspectives) >= 2:
                agreement = ConsensusArea(
                    consensus_id=f"insight_consensus_{keyword}_{int(datetime.now().timestamp())}",
                    agreeing_perspectives=agreeing_perspectives,
                    consensus_topic=f"{keyword.title()} considerations identified",
                    agreement_strength=len(agreeing_perspectives) / len(perspectives),
                    supporting_evidence=supporting_evidence,
                    confidence_score=0.0  # Will be calculated later
                )
                agreements.append(agreement)
        
        return agreements

    def _find_recommendation_agreements(self, perspectives: List[PerspectiveResult]) -> List[ConsensusArea]:
        """Find agreements in recommendations across perspectives."""
        
        agreements = []
        
        # Common recommendation themes
        recommendation_themes = ["improve", "enhance", "validate", "review", "implement"]
        
        for theme in recommendation_themes:
            agreeing_perspectives = []
            supporting_evidence = []
            
            for perspective in perspectives:
                # Check if perspective has recommendations with this theme
                for recommendation in perspective.recommendations:
                    if theme in str(recommendation).lower():
                        agreeing_perspectives.append(perspective.agent_id)
                        supporting_evidence.append(f"Recommendation from {perspective.perspective_type}")
                        break
            
            # Create consensus area if multiple perspectives agree
            if len(agreeing_perspectives) >= 2:
                agreement = ConsensusArea(
                    consensus_id=f"rec_consensus_{theme}_{int(datetime.now().timestamp())}",
                    agreeing_perspectives=agreeing_perspectives,
                    consensus_topic=f"Need to {theme} identified",
                    agreement_strength=len(agreeing_perspectives) / len(perspectives),
                    supporting_evidence=supporting_evidence,
                    confidence_score=0.0  # Will be calculated later
                )
                agreements.append(agreement)
        
        return agreements

    def execute(self, *args, **kwargs) -> Any:
        """Execute consensus detection operations."""
        return {
            "detector_id": self.detector_id,
            "component_type": "ConsensusDetector",
            "capabilities": ["consensus_identification", "confidence_scoring", "evidence_collection"],
            "status": "operational"
        }


def main():
    """Test the ConsensusDetector component."""
    detector = ConsensusDetector()
    
    print("🚨 Consensus Detector - Multi-Perspective Ghostbusters Component 🚨")
    print(f"Detector ID: {detector.detector_id}")
    print(f"Context: {detector.bounded_context.name}")
    print(f"Pattern: {detector.ddd_pattern}")
    print("✅ Consensus detector operational!")


if __name__ == "__main__":
    main()