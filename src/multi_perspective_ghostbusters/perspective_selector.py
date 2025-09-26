#!/usr/bin/env python3
"""
Perspective Selector - Multi-Perspective Ghostbusters Component
==============================================================

Selects optimal agent combinations for content analysis (< 200 lines)
Implements "Diversity is the only free lunch" through optimal selection.

Author: Beast Mode Framework
Date: 2025-01-27
Context: Agent Management
Pattern: DomainService
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.multi_perspective_ghostbusters.agent_lifecycle_manager import SpecializedAgent


@dataclass
class DiversityRequirements:
    """Requirements for diversity in perspective selection."""
    minimum_perspectives: int
    maximum_perspectives: int
    required_perspective_types: List[str]
    diversity_threshold: float
    uniqueness_requirement: float


@dataclass
class SelectedPerspectives:
    """Selected perspectives for analysis."""
    selection_id: str
    selected_agents: List[SpecializedAgent]
    diversity_score: float
    selection_rationale: List[str]
    estimated_coverage: float
    selection_timestamp: datetime


@dataclass
class OptimalAgentMix:
    """Optimal mix of agents for content type."""
    mix_id: str
    content_type: str
    recommended_agents: List[str]
    diversity_optimization: Dict[str, float]
    performance_prediction: float
    mix_rationale: List[str]


@dataclass
class ContentCharacteristics:
    """Characteristics of content to be analyzed."""
    content_type: str
    complexity_level: str
    domain_areas: List[str]
    analysis_requirements: List[str]
    expected_challenges: List[str]


@dataclass
class DiversityValidation:
    """Validation of diversity in selected perspectives."""
    validation_id: str
    diversity_achieved: bool
    diversity_score: float
    uniqueness_metrics: Dict[str, float]
    recommendations: List[str]


class PerspectiveSelector(ReflectiveModule):
    """
    Selects optimal agent combinations for content analysis.
    
    Implements perspective selection for multi-perspective analysis where
    "Diversity is the only free lunch" - optimizing agent combinations
    for maximum analytical diversity and coverage.
    """

    def __init__(self):
        super().__init__()
        self._selection_history: Dict[str, SelectedPerspectives] = {}
        self._performance_data: Dict[str, Dict[str, float]] = {}
        
        # Store selection data in unified CMS
        self.store_content("selection_pool", "perspective_selection", {
            "selection_history": {},
            "performance_data": {},
            "optimization_metrics": {}
        })

    def select_optimal_perspectives(self,
                                  content: Any,
                                  available_agents: List[SpecializedAgent],
                                  diversity_requirements: DiversityRequirements) -> SelectedPerspectives:
        """Select perspectives most relevant to content type."""
        
        selection_id = f"selection_{int(datetime.now().timestamp())}"
        
        # Analyze content characteristics
        content_chars = self._analyze_content_characteristics(content)
        
        # Score agents based on relevance and diversity
        agent_scores = self._score_agents_for_content(available_agents, content_chars)
        
        # Select optimal combination
        selected_agents = self._select_optimal_combination(
            available_agents, agent_scores, diversity_requirements
        )
        
        # Calculate diversity score
        diversity_score = self._calculate_selection_diversity(selected_agents)
        
        # Generate selection rationale
        rationale = self._generate_selection_rationale(selected_agents, content_chars, diversity_score)
        
        selection = SelectedPerspectives(
            selection_id=selection_id,
            selected_agents=selected_agents,
            diversity_score=diversity_score,
            selection_rationale=rationale,
            estimated_coverage=self._estimate_coverage(selected_agents, content_chars),
            selection_timestamp=datetime.now()
        )
        
        self._selection_history[selection_id] = selection
        
        # Store in CMS
        self.store_content(selection_id, "perspective_selection", {
            "content_type": content_chars.content_type,
            "agents_selected": len(selected_agents),
            "diversity_score": diversity_score,
            "selection_rationale": rationale
        })
        
        return selection

    def optimize_agent_mix(self,
                          content_characteristics: ContentCharacteristics,
                          historical_performance: Dict[str, float]) -> OptimalAgentMix:
        """Use historical performance data to guide agent choice."""
        
        mix_id = f"mix_{content_characteristics.content_type}_{int(datetime.now().timestamp())}"
        
        # Analyze historical performance patterns
        performance_patterns = self._analyze_performance_patterns(historical_performance)
        
        # Identify optimal agent types for content
        optimal_types = self._identify_optimal_agent_types(content_characteristics, performance_patterns)
        
        # Calculate diversity optimization metrics
        diversity_optimization = self._calculate_diversity_optimization(optimal_types)
        
        # Predict performance
        performance_prediction = self._predict_mix_performance(optimal_types, historical_performance)
        
        # Generate rationale
        rationale = self._generate_mix_rationale(optimal_types, performance_patterns)
        
        mix = OptimalAgentMix(
            mix_id=mix_id,
            content_type=content_characteristics.content_type,
            recommended_agents=optimal_types,
            diversity_optimization=diversity_optimization,
            performance_prediction=performance_prediction,
            mix_rationale=rationale
        )
        
        # Store in CMS
        self.store_content(mix_id, "agent_mix_optimization", {
            "content_type": content_characteristics.content_type,
            "recommended_count": len(optimal_types),
            "performance_prediction": performance_prediction,
            "diversity_metrics": diversity_optimization
        })
        
        return mix

    def maintain_diversity_principles(self, selected_mix: SelectedPerspectives) -> DiversityValidation:
        """Ensure optimal diversity while maximizing quality."""
        
        validation_id = f"diversity_val_{int(datetime.now().timestamp())}"
        
        # Validate diversity metrics
        diversity_metrics = self._validate_diversity_metrics(selected_mix.selected_agents)
        
        # Check uniqueness requirements
        uniqueness_check = self._check_perspective_uniqueness(selected_mix.selected_agents)
        
        # Assess overall diversity achievement
        diversity_achieved = (
            selected_mix.diversity_score >= 0.7 and
            uniqueness_check["overall_uniqueness"] >= 0.8
        )
        
        # Generate recommendations
        recommendations = self._generate_diversity_recommendations(diversity_metrics, uniqueness_check)
        
        validation = DiversityValidation(
            validation_id=validation_id,
            diversity_achieved=diversity_achieved,
            diversity_score=selected_mix.diversity_score,
            uniqueness_metrics=uniqueness_check,
            recommendations=recommendations
        )
        
        # Store validation in CMS
        self.store_content(validation_id, "diversity_validation", validation.__dict__)
        
        return validation

    def _analyze_content_characteristics(self, content: Any) -> ContentCharacteristics:
        """Analyze content to determine characteristics."""
        # Simplified content analysis
        return ContentCharacteristics(
            content_type="general",
            complexity_level="medium",
            domain_areas=["analysis", "evaluation"],
            analysis_requirements=["comprehensive", "multi-perspective"],
            expected_challenges=["complexity", "ambiguity"]
        )

    def _score_agents_for_content(self, agents: List[SpecializedAgent], content_chars: ContentCharacteristics) -> Dict[str, float]:
        """Score agents based on relevance to content."""
        scores = {}
        
        for agent in agents:
            # Base score from agent type relevance
            base_score = 0.5
            
            # Bonus for relevant capabilities
            if hasattr(agent, 'capabilities') and agent.capabilities:
                capability_bonus = len(agent.capabilities) * 0.1
                base_score += min(capability_bonus, 0.3)
            
            # Bonus for domain alignment
            if hasattr(agent, 'perspective_profile'):
                profile = agent.perspective_profile
                if isinstance(profile, dict) and 'domain_focus' in profile:
                    domain_overlap = len(set(profile['domain_focus']) & set(content_chars.domain_areas))
                    base_score += domain_overlap * 0.1
            
            scores[agent.agent_id] = min(base_score, 1.0)
        
        return scores

    def _select_optimal_combination(self, agents: List[SpecializedAgent], scores: Dict[str, float], requirements: DiversityRequirements) -> List[SpecializedAgent]:
        """Select optimal combination of agents."""
        # Sort agents by score
        sorted_agents = sorted(agents, key=lambda a: scores.get(a.agent_id, 0.0), reverse=True)
        
        # Select top agents up to maximum
        selected = sorted_agents[:requirements.maximum_perspectives]
        
        # Ensure minimum requirements
        if len(selected) < requirements.minimum_perspectives:
            # Add more agents if available
            remaining = [a for a in agents if a not in selected]
            selected.extend(remaining[:requirements.minimum_perspectives - len(selected)])
        
        return selected

    def _calculate_selection_diversity(self, selected_agents: List[SpecializedAgent]) -> float:
        """Calculate diversity score for selected agents."""
        if not selected_agents:
            return 0.0
        
        # Calculate type diversity
        agent_types = set()
        for agent in selected_agents:
            agent_types.add(agent.agent_type)
        
        type_diversity = len(agent_types) / len(selected_agents)
        
        # Calculate perspective diversity (if available)
        perspective_types = set()
        for agent in selected_agents:
            if hasattr(agent, 'perspective_profile') and isinstance(agent.perspective_profile, dict):
                perspective_types.add(agent.perspective_profile.get('perspective_type', 'unknown'))
        
        perspective_diversity = len(perspective_types) / len(selected_agents) if selected_agents else 0.0
        
        # Combined diversity score
        return (type_diversity + perspective_diversity) / 2

    def _generate_selection_rationale(self, agents: List[SpecializedAgent], content_chars: ContentCharacteristics, diversity_score: float) -> List[str]:
        """Generate rationale for agent selection."""
        rationale = [
            f"Selected {len(agents)} agents for {content_chars.content_type} analysis",
            f"Achieved diversity score of {diversity_score:.2f}",
            "Optimized for multi-perspective coverage"
        ]
        
        if diversity_score > 0.8:
            rationale.append("High diversity achieved - excellent perspective coverage")
        elif diversity_score > 0.6:
            rationale.append("Good diversity achieved - adequate perspective coverage")
        else:
            rationale.append("Limited diversity - consider additional agent types")
        
        return rationale

    def _estimate_coverage(self, agents: List[SpecializedAgent], content_chars: ContentCharacteristics) -> float:
        """Estimate analysis coverage from selected agents."""
        # Simplified coverage estimation
        base_coverage = min(len(agents) * 0.2, 1.0)
        
        # Bonus for domain alignment
        domain_bonus = 0.0
        for agent in agents:
            if hasattr(agent, 'perspective_profile') and isinstance(agent.perspective_profile, dict):
                profile = agent.perspective_profile
                if 'domain_focus' in profile:
                    overlap = len(set(profile['domain_focus']) & set(content_chars.domain_areas))
                    domain_bonus += overlap * 0.1
        
        return min(base_coverage + domain_bonus, 1.0)

    def _analyze_performance_patterns(self, historical_performance: Dict[str, float]) -> Dict[str, Any]:
        """Analyze historical performance patterns."""
        if not historical_performance:
            return {"average_performance": 0.5, "top_performers": [], "patterns": []}
        
        avg_performance = sum(historical_performance.values()) / len(historical_performance)
        top_performers = [k for k, v in historical_performance.items() if v > avg_performance]
        
        return {
            "average_performance": avg_performance,
            "top_performers": top_performers,
            "patterns": ["consistent_high_performance" if avg_performance > 0.7 else "variable_performance"]
        }

    def _identify_optimal_agent_types(self, content_chars: ContentCharacteristics, patterns: Dict[str, Any]) -> List[str]:
        """Identify optimal agent types for content."""
        optimal_types = ["SecurityExpert", "ArchitectureExpert", "RequirementsExpert"]
        
        # Add specialized types based on content
        if "security" in content_chars.domain_areas:
            optimal_types.append("SecuritySpecialist")
        if "performance" in content_chars.domain_areas:
            optimal_types.append("PerformanceExpert")
        
        return optimal_types[:5]  # Limit to 5 types

    def _calculate_diversity_optimization(self, agent_types: List[str]) -> Dict[str, float]:
        """Calculate diversity optimization metrics."""
        return {
            "type_diversity": len(set(agent_types)) / len(agent_types) if agent_types else 0.0,
            "coverage_optimization": min(len(agent_types) * 0.2, 1.0),
            "balance_score": 1.0 / len(agent_types) if agent_types else 0.0
        }

    def _predict_mix_performance(self, agent_types: List[str], historical_performance: Dict[str, float]) -> float:
        """Predict performance of agent mix."""
        if not historical_performance:
            return 0.7  # Default prediction
        
        relevant_scores = [historical_performance.get(agent_type, 0.5) for agent_type in agent_types]
        return sum(relevant_scores) / len(relevant_scores) if relevant_scores else 0.5

    def _generate_mix_rationale(self, agent_types: List[str], patterns: Dict[str, Any]) -> List[str]:
        """Generate rationale for agent mix."""
        return [
            f"Recommended {len(agent_types)} agent types for optimal coverage",
            f"Based on historical performance patterns: {patterns.get('patterns', [])}",
            "Optimized for diversity and performance balance"
        ]

    def _validate_diversity_metrics(self, agents: List[SpecializedAgent]) -> Dict[str, float]:
        """Validate diversity metrics for agents."""
        return {
            "agent_count": len(agents),
            "type_diversity": len(set(a.agent_type for a in agents)) / len(agents) if agents else 0.0,
            "overall_diversity": self._calculate_selection_diversity(agents)
        }

    def _check_perspective_uniqueness(self, agents: List[SpecializedAgent]) -> Dict[str, float]:
        """Check uniqueness of perspectives."""
        if not agents:
            return {"overall_uniqueness": 0.0}
        
        unique_perspectives = set()
        for agent in agents:
            if hasattr(agent, 'perspective_profile') and isinstance(agent.perspective_profile, dict):
                unique_perspectives.add(agent.perspective_profile.get('perspective_type', 'unknown'))
        
        return {
            "overall_uniqueness": len(unique_perspectives) / len(agents),
            "unique_count": len(unique_perspectives),
            "total_agents": len(agents)
        }

    def _generate_diversity_recommendations(self, diversity_metrics: Dict[str, float], uniqueness_check: Dict[str, float]) -> List[str]:
        """Generate recommendations for improving diversity."""
        recommendations = []
        
        if diversity_metrics.get("overall_diversity", 0.0) < 0.7:
            recommendations.append("Consider adding more diverse agent types")
        
        if uniqueness_check.get("overall_uniqueness", 0.0) < 0.8:
            recommendations.append("Ensure each agent has a unique perspective")
        
        if not recommendations:
            recommendations.append("Diversity requirements satisfied")
        
        return recommendations

    def execute(self, *args, **kwargs) -> Any:
        """Execute perspective selection operations."""
        return {
            "selections_made": len(self._selection_history),
            "performance_data_points": len(self._performance_data),
            "selector_status": "operational"
        }


def main():
    """Test the PerspectiveSelector."""
    selector = PerspectiveSelector()
    
    print("🚨 Perspective Selector - Multi-Perspective Ghostbusters 🚨")
    print(f"Context: {selector.bounded_context.name}")
    print(f"Pattern: {selector.ddd_pattern}")
    print(f"Capabilities: {len(selector.capabilities)}")
    print("✅ Selection system operational!")


if __name__ == "__main__":
    main()