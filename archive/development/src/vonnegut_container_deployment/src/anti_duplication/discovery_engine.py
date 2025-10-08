"""
Capability Discovery Engine - Mandatory pre-development capability discovery.
"""

import hashlib
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .models import (
    CapabilityInventory, OverlapAnalysis, DiscoveryAttestation,
    ExistingSolution, CapabilityGap, EnhancementOpportunity,
    OverlappingCapability, OverlapRecommendation, DevelopmentRequest
)
from .capability_registry import CapabilityRegistry


class CapabilityDiscoveryEngine:
    """
    Mandatory pre-development capability discovery.
    
    Orchestrates the discovery process to identify existing solutions,
    analyze functional overlap, and generate discovery attestations.
    """
    
    def __init__(self, capability_registry: CapabilityRegistry):
        """Initialize the discovery engine."""
        self.registry = capability_registry
        self.logger = logging.getLogger(__name__)
        
        # Discovery configuration
        self.similarity_threshold = 0.7  # 70% similarity triggers overlap
        self.completeness_threshold = 0.8  # 80% completeness required for attestation
        
        self.logger.info("CapabilityDiscoveryEngine initialized")
    
    def discover_existing_solutions(self, problem_domain: str) -> CapabilityInventory:
        """
        Discover existing solutions for a problem domain.
        
        Args:
            problem_domain: Description of the problem domain or functionality needed
            
        Returns:
            CapabilityInventory containing discovered solutions and gaps
        """
        self.logger.info(f"Starting capability discovery for domain: {problem_domain}")
        
        # Ensure registry is fresh
        freshness = self.registry.validate_freshness()
        if not freshness["is_fresh"]:
            self.logger.warning("Registry is stale, triggering rescan")
            self.registry.scan_codebase()
        
        # Search for existing solutions
        existing_solutions = self.registry.semantic_search(problem_domain, limit=20)
        
        # Analyze capability gaps
        capability_gaps = self._identify_capability_gaps(problem_domain, existing_solutions)
        
        # Identify enhancement opportunities
        enhancement_opportunities = self._identify_enhancement_opportunities(
            problem_domain, existing_solutions
        )
        
        # Calculate discovery completeness score
        completeness_score = self._calculate_completeness_score(
            existing_solutions, capability_gaps, enhancement_opportunities
        )
        
        inventory = CapabilityInventory(
            domain=problem_domain,
            existing_solutions=existing_solutions,
            capability_gaps=capability_gaps,
            enhancement_opportunities=enhancement_opportunities,
            discovery_completeness_score=completeness_score,
            total_capabilities_found=len(existing_solutions)
        )
        
        self.logger.info(
            f"Discovery completed: {len(existing_solutions)} solutions found, "
            f"completeness score: {completeness_score:.2f}"
        )
        
        return inventory
    
    def assess_functional_overlap(
        self, 
        proposed_spec: str, 
        inventory: CapabilityInventory
    ) -> OverlapAnalysis:
        """
        Assess functional overlap between proposed development and existing capabilities.
        
        Args:
            proposed_spec: Specification or description of proposed development
            inventory: Capability inventory from discovery
            
        Returns:
            OverlapAnalysis with similarity scores and recommendations
        """
        self.logger.info("Analyzing functional overlap")
        
        overlapping_capabilities = []
        max_similarity = 0.0
        
        # Analyze each existing solution for overlap
        for solution in inventory.existing_solutions:
            similarity_score = self._calculate_similarity(proposed_spec, solution)
            
            if similarity_score > 0.3:  # Only include meaningful similarities
                overlap = OverlappingCapability(
                    existing_solution=solution,
                    similarity_score=similarity_score,
                    overlap_description=self._generate_overlap_description(
                        proposed_spec, solution, similarity_score
                    ),
                    functional_differences=self._identify_functional_differences(
                        proposed_spec, solution
                    ),
                    enhancement_potential=similarity_score > 0.5
                )
                overlapping_capabilities.append(overlap)
                max_similarity = max(max_similarity, similarity_score)
        
        # Sort by similarity score (highest first)
        overlapping_capabilities.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Generate recommendation
        recommendation = self._generate_overlap_recommendation(
            max_similarity, overlapping_capabilities, inventory
        )
        
        # Determine if justification is required
        justification_required = (
            max_similarity > self.similarity_threshold or
            len(overlapping_capabilities) > 3 or
            recommendation in [OverlapRecommendation.BLOCK, OverlapRecommendation.ENHANCE]
        )
        
        analysis = OverlapAnalysis(
            functional_similarity_score=max_similarity,
            overlapping_capabilities=overlapping_capabilities,
            unique_value_proposition=self._extract_unique_value_proposition(
                proposed_spec, overlapping_capabilities
            ),
            recommendation=recommendation,
            justification_required=justification_required
        )
        
        self.logger.info(
            f"Overlap analysis completed: max similarity {max_similarity:.2f}, "
            f"recommendation: {recommendation.value}"
        )
        
        return analysis
    
    def generate_discovery_attestation(
        self,
        request: DevelopmentRequest,
        inventory: CapabilityInventory,
        overlap_analysis: OverlapAnalysis,
        justification: str = ""
    ) -> DiscoveryAttestation:
        """
        Generate cryptographically signed discovery attestation.
        
        Args:
            request: Development request being processed
            inventory: Capability inventory from discovery
            overlap_analysis: Functional overlap analysis
            justification: Justification for new vs. enhance decision
            
        Returns:
            DiscoveryAttestation with cryptographic signature
        """
        self.logger.info(f"Generating discovery attestation for request: {request.request_id}")
        
        # Check if enhancement vs. new is justified
        enhancement_vs_new_justified = (
            not overlap_analysis.has_significant_overlap or
            (overlap_analysis.justification_required and justification.strip() != "") or
            overlap_analysis.recommendation == OverlapRecommendation.PROCEED
        )
        
        attestation = DiscoveryAttestation(
            problem_domain=inventory.domain,
            discovery_completeness_score=inventory.discovery_completeness_score,
            existing_solutions_found=len(inventory.existing_solutions),
            overlap_analysis_completed=True,
            enhancement_vs_new_justified=enhancement_vs_new_justified,
            justification_text=justification,
            attesting_agent="CapabilityDiscoveryEngine"
        )
        
        # Generate cryptographic signature
        attestation.attestation_signature = self._generate_attestation_signature(attestation)
        
        self.logger.info(
            f"Attestation generated: {attestation.attestation_id}, "
            f"valid: {attestation.is_valid}"
        )
        
        return attestation
    
    def _identify_capability_gaps(
        self, 
        problem_domain: str, 
        existing_solutions: List[ExistingSolution]
    ) -> List[CapabilityGap]:
        """Identify gaps in existing capabilities."""
        gaps = []
        
        # Simple heuristic: if few solutions found, there might be gaps
        if len(existing_solutions) < 3:
            gap = CapabilityGap(
                description=f"Limited existing solutions for {problem_domain}",
                required_functionality=problem_domain,
                priority="medium",
                estimated_effort="unknown",
                potential_solutions=["New development", "Enhancement of existing"]
            )
            gaps.append(gap)
        
        return gaps
    
    def _identify_enhancement_opportunities(
        self,
        problem_domain: str,
        existing_solutions: List[ExistingSolution]
    ) -> List[EnhancementOpportunity]:
        """Identify opportunities to enhance existing capabilities."""
        opportunities = []
        
        # Look for solutions that could be enhanced
        for solution in existing_solutions[:3]:  # Top 3 most relevant
            if self._has_enhancement_potential(solution, problem_domain):
                opportunity = EnhancementOpportunity(
                    existing_solution_id=solution.solution_id,
                    enhancement_description=f"Enhance {solution.name} to support {problem_domain}",
                    estimated_effort="medium",
                    value_proposition="Leverage existing code and patterns",
                    risk_assessment="Low risk - building on proven foundation"
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def _has_enhancement_potential(self, solution: ExistingSolution, problem_domain: str) -> bool:
        """Check if a solution has potential for enhancement."""
        # Simple heuristic: if solution name or description contains keywords from domain
        domain_keywords = problem_domain.lower().split()
        solution_text = f"{solution.name} {solution.description} {solution.functionality_summary}".lower()
        
        return any(keyword in solution_text for keyword in domain_keywords)
    
    def _calculate_completeness_score(
        self,
        existing_solutions: List[ExistingSolution],
        capability_gaps: List[CapabilityGap],
        enhancement_opportunities: List[EnhancementOpportunity]
    ) -> float:
        """Calculate discovery completeness score."""
        # Base score from number of solutions found
        base_score = min(len(existing_solutions) / 10.0, 0.8)  # Max 0.8 from solutions
        
        # Bonus for identifying gaps and opportunities
        gap_bonus = min(len(capability_gaps) * 0.05, 0.1)
        opportunity_bonus = min(len(enhancement_opportunities) * 0.05, 0.1)
        
        return min(base_score + gap_bonus + opportunity_bonus, 1.0)
    
    def _calculate_similarity(self, proposed_spec: str, solution: ExistingSolution) -> float:
        """Calculate similarity between proposed spec and existing solution."""
        # Simple text-based similarity (could be enhanced with ML)
        proposed_words = set(proposed_spec.lower().split())
        solution_words = set(
            f"{solution.name} {solution.description} {solution.functionality_summary}".lower().split()
        )
        
        if not proposed_words or not solution_words:
            return 0.0
        
        intersection = proposed_words.intersection(solution_words)
        union = proposed_words.union(solution_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _generate_overlap_description(
        self, 
        proposed_spec: str, 
        solution: ExistingSolution, 
        similarity_score: float
    ) -> str:
        """Generate description of functional overlap."""
        if similarity_score > 0.8:
            return f"High overlap with {solution.name} - very similar functionality"
        elif similarity_score > 0.6:
            return f"Significant overlap with {solution.name} - similar core functionality"
        elif similarity_score > 0.4:
            return f"Moderate overlap with {solution.name} - some shared functionality"
        else:
            return f"Minor overlap with {solution.name} - limited shared functionality"
    
    def _identify_functional_differences(
        self, 
        proposed_spec: str, 
        solution: ExistingSolution
    ) -> List[str]:
        """Identify functional differences between proposed and existing solution."""
        # Simplified implementation - could be enhanced with NLP
        differences = []
        
        proposed_words = set(proposed_spec.lower().split())
        solution_words = set(
            f"{solution.name} {solution.description} {solution.functionality_summary}".lower().split()
        )
        
        unique_to_proposed = proposed_words - solution_words
        if unique_to_proposed:
            differences.append(f"Proposed includes: {', '.join(list(unique_to_proposed)[:5])}")
        
        unique_to_existing = solution_words - proposed_words
        if unique_to_existing:
            differences.append(f"Existing includes: {', '.join(list(unique_to_existing)[:5])}")
        
        return differences
    
    def _generate_overlap_recommendation(
        self,
        max_similarity: float,
        overlapping_capabilities: List[OverlappingCapability],
        inventory: CapabilityInventory
    ) -> OverlapRecommendation:
        """Generate recommendation based on overlap analysis."""
        
        if max_similarity > 0.9:
            return OverlapRecommendation.BLOCK
        elif max_similarity > 0.7:
            if any(cap.enhancement_potential for cap in overlapping_capabilities):
                return OverlapRecommendation.ENHANCE
            else:
                return OverlapRecommendation.REVIEW
        elif max_similarity > 0.5:
            return OverlapRecommendation.REVIEW
        else:
            return OverlapRecommendation.PROCEED
    
    def _extract_unique_value_proposition(
        self,
        proposed_spec: str,
        overlapping_capabilities: List[OverlappingCapability]
    ) -> Optional[str]:
        """Extract unique value proposition of proposed development."""
        if not overlapping_capabilities:
            return "No existing similar capabilities found"
        
        # Find the most similar capability
        most_similar = overlapping_capabilities[0]
        
        if most_similar.similarity_score < 0.5:
            return "Addresses different problem domain than existing capabilities"
        elif most_similar.functional_differences:
            return f"Extends existing capabilities with: {most_similar.functional_differences[0]}"
        else:
            return "Unique value proposition requires manual analysis"
    
    def _generate_attestation_signature(self, attestation: DiscoveryAttestation) -> str:
        """Generate cryptographic signature for attestation."""
        # Create signature payload
        payload = {
            "attestation_id": attestation.attestation_id,
            "problem_domain": attestation.problem_domain,
            "discovery_completeness_score": attestation.discovery_completeness_score,
            "existing_solutions_found": attestation.existing_solutions_found,
            "overlap_analysis_completed": attestation.overlap_analysis_completed,
            "enhancement_vs_new_justified": attestation.enhancement_vs_new_justified,
            "justification_text": attestation.justification_text,
            "attestation_timestamp": attestation.attestation_timestamp.isoformat(),
            "attesting_agent": attestation.attesting_agent
        }
        
        # Generate hash-based signature (in production, use proper cryptographic signing)
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(payload_str.encode()).hexdigest()
        
        return f"sha256:{signature}"
    
    def validate_attestation_signature(self, attestation: DiscoveryAttestation) -> bool:
        """Validate the cryptographic signature of an attestation."""
        expected_signature = self._generate_attestation_signature(attestation)
        return attestation.attestation_signature == expected_signature