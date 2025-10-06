"""
Development Gate - Enforcement mechanism for discovery requirements.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .models import (
    DiscoveryAttestation, GateDecision, DevelopmentRequest,
    OverlapAnalysis, CapabilityInventory, AuditLogEntry
)
from .discovery_engine import CapabilityDiscoveryEngine


class DevelopmentGate:
    """
    Enforcement mechanism for discovery requirements.
    
    Validates discovery attestations, blocks duplicate development,
    and maintains audit trails for compliance.
    """
    
    def __init__(self, discovery_engine: CapabilityDiscoveryEngine, audit_log_path: Optional[Path] = None):
        """Initialize the development gate."""
        self.discovery_engine = discovery_engine
        self.logger = logging.getLogger(__name__)
        
        # Audit log setup
        self.audit_log_path = audit_log_path or Path(".anti_duplication/audit.jsonl")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Gate configuration
        self.emergency_override_enabled = True
        self.require_manual_review_threshold = 0.8  # High similarity requires manual review
        
        self.logger.info("DevelopmentGate initialized")
    
    def validate_development_request(self, request: DevelopmentRequest) -> GateDecision:
        """
        Validate a development request through the complete gate process.
        
        Args:
            request: Development request to validate
            
        Returns:
            GateDecision indicating whether development can proceed
        """
        self.logger.info(f"Validating development request: {request.request_id}")
        
        try:
            # Step 1: Check if discovery is completed
            if not request.discovery_completed or not request.discovery_attestation_id:
                return self._create_gate_decision(
                    request.request_id,
                    "BLOCKED",
                    "Discovery not completed",
                    ["Complete capability discovery", "Provide discovery attestation"],
                    "DevelopmentGate"
                )
            
            # Step 2: Validate discovery attestation (this would load from storage in real implementation)
            # For now, we'll simulate this step
            attestation_valid = True  # Would validate actual attestation
            
            if not attestation_valid:
                return self._create_gate_decision(
                    request.request_id,
                    "BLOCKED",
                    "Invalid discovery attestation",
                    ["Regenerate valid discovery attestation"],
                    "DevelopmentGate"
                )
            
            # Step 3: Perform fresh overlap analysis
            inventory = self.discovery_engine.discover_existing_solutions(request.problem_statement)
            overlap_analysis = self.discovery_engine.assess_functional_overlap(
                request.proposed_solution, inventory
            )
            
            # Step 4: Make gate decision based on overlap
            decision = self._make_overlap_decision(request, inventory, overlap_analysis)
            
            # Step 5: Log decision for audit
            self._log_audit_event("GATE_DECISION", request.request_id, {
                "decision": decision.decision,
                "reasoning": decision.reasoning,
                "overlap_score": overlap_analysis.functional_similarity_score,
                "existing_solutions_count": len(inventory.existing_solutions)
            }, "DevelopmentGate")
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error validating request {request.request_id}: {e}")
            return self._create_gate_decision(
                request.request_id,
                "BLOCKED",
                f"Validation error: {str(e)}",
                ["Contact system administrator", "Retry validation"],
                "DevelopmentGate"
            )
    
    def validate_discovery_attestation(self, attestation: DiscoveryAttestation) -> GateDecision:
        """
        Validate a discovery attestation for authenticity and completeness.
        
        Args:
            attestation: Discovery attestation to validate
            
        Returns:
            GateDecision indicating validation result
        """
        self.logger.info(f"Validating discovery attestation: {attestation.attestation_id}")
        
        # Check attestation validity
        if not attestation.is_valid:
            return self._create_gate_decision(
                attestation.attestation_id,
                "BLOCKED",
                "Attestation is not valid",
                [
                    f"Discovery completeness score too low: {attestation.discovery_completeness_score}",
                    "Overlap analysis not completed" if not attestation.overlap_analysis_completed else "",
                    "Enhancement vs new decision not justified" if not attestation.enhancement_vs_new_justified else ""
                ],
                "DevelopmentGate"
            )
        
        # Validate cryptographic signature
        if not self.discovery_engine.validate_attestation_signature(attestation):
            return self._create_gate_decision(
                attestation.attestation_id,
                "BLOCKED",
                "Invalid attestation signature",
                ["Regenerate attestation with valid signature"],
                "DevelopmentGate"
            )
        
        # Check attestation age (should be recent)
        age_hours = (datetime.utcnow() - attestation.attestation_timestamp).total_seconds() / 3600
        if age_hours > 24:  # Attestation older than 24 hours
            return self._create_gate_decision(
                attestation.attestation_id,
                "REVIEW_REQUIRED",
                f"Attestation is {age_hours:.1f} hours old",
                ["Consider regenerating attestation", "Manual review recommended"],
                "DevelopmentGate"
            )
        
        return self._create_gate_decision(
            attestation.attestation_id,
            "APPROVED",
            "Attestation is valid and current",
            [],
            "DevelopmentGate"
        )
    
    def block_duplicate_development(self, overlap_analysis: OverlapAnalysis) -> GateDecision:
        """
        Block development based on overlap analysis.
        
        Args:
            overlap_analysis: Analysis of functional overlap
            
        Returns:
            GateDecision indicating whether to block development
        """
        if overlap_analysis.should_block_development:
            overlapping_solutions = [
                f"{cap.existing_solution.name} ({cap.similarity_score:.2f} similarity)"
                for cap in overlap_analysis.overlapping_capabilities[:3]
            ]
            
            return self._create_gate_decision(
                overlap_analysis.analysis_id,
                "BLOCKED",
                f"High functional overlap detected ({overlap_analysis.functional_similarity_score:.2f})",
                [
                    "Consider enhancing existing solutions instead:",
                    *overlapping_solutions,
                    "Provide strong justification for new development if proceeding"
                ],
                "DevelopmentGate"
            )
        
        elif overlap_analysis.functional_similarity_score > self.require_manual_review_threshold:
            return self._create_gate_decision(
                overlap_analysis.analysis_id,
                "REVIEW_REQUIRED",
                f"Significant overlap requires manual review ({overlap_analysis.functional_similarity_score:.2f})",
                [
                    "Manual review required due to high similarity",
                    "Consider enhancement vs new development",
                    "Provide detailed justification for approach"
                ],
                "DevelopmentGate"
            )
        
        else:
            return self._create_gate_decision(
                overlap_analysis.analysis_id,
                "APPROVED",
                f"Acceptable overlap level ({overlap_analysis.functional_similarity_score:.2f})",
                [],
                "DevelopmentGate"
            )
    
    def require_enhancement_justification(
        self, 
        request: DevelopmentRequest,
        existing_capabilities: List[Any]
    ) -> GateDecision:
        """
        Require justification for new development vs enhancement.
        
        Args:
            request: Development request
            existing_capabilities: List of existing capabilities that could be enhanced
            
        Returns:
            GateDecision indicating justification requirements
        """
        if not existing_capabilities:
            return self._create_gate_decision(
                request.request_id,
                "APPROVED",
                "No existing capabilities found - new development justified",
                [],
                "DevelopmentGate"
            )
        
        # Check if justification was provided
        if not hasattr(request, 'enhancement_justification') or not request.enhancement_justification:
            return self._create_gate_decision(
                request.request_id,
                "BLOCKED",
                "Enhancement vs new development justification required",
                [
                    f"Found {len(existing_capabilities)} existing capabilities that could be enhanced",
                    "Provide detailed justification for new development approach",
                    "Consider enhancement benefits: lower risk, faster delivery, consistency"
                ],
                "DevelopmentGate"
            )
        
        return self._create_gate_decision(
            request.request_id,
            "APPROVED",
            "Enhancement vs new development justification provided",
            [],
            "DevelopmentGate"
        )
    
    def emergency_override(
        self, 
        request: DevelopmentRequest, 
        override_reason: str,
        override_authority: str
    ) -> GateDecision:
        """
        Provide emergency override for blocked development.
        
        Args:
            request: Development request to override
            override_reason: Reason for emergency override
            override_authority: Authority authorizing override
            
        Returns:
            GateDecision with emergency approval
        """
        if not self.emergency_override_enabled:
            return self._create_gate_decision(
                request.request_id,
                "BLOCKED",
                "Emergency override is disabled",
                ["Contact system administrator"],
                "DevelopmentGate"
            )
        
        self.logger.warning(
            f"Emergency override used for request {request.request_id} "
            f"by {override_authority}: {override_reason}"
        )
        
        # Log emergency override for audit
        self._log_audit_event("EMERGENCY_OVERRIDE", request.request_id, {
            "override_reason": override_reason,
            "override_authority": override_authority,
            "original_request": {
                "problem_statement": request.problem_statement,
                "proposed_solution": request.proposed_solution
            }
        }, override_authority)
        
        return self._create_gate_decision(
            request.request_id,
            "APPROVED",
            f"Emergency override approved: {override_reason}",
            [
                "EMERGENCY OVERRIDE - Mandatory review required within 48 hours",
                "Document lessons learned from this override",
                "Update discovery process to prevent future overrides"
            ],
            override_authority
        )
    
    def _make_overlap_decision(
        self,
        request: DevelopmentRequest,
        inventory: CapabilityInventory,
        overlap_analysis: OverlapAnalysis
    ) -> GateDecision:
        """Make gate decision based on overlap analysis."""
        
        # High overlap - block development
        if overlap_analysis.functional_similarity_score > 0.9:
            return self._create_gate_decision(
                request.request_id,
                "BLOCKED",
                f"Extremely high overlap ({overlap_analysis.functional_similarity_score:.2f}) - duplicate development",
                [
                    "Use existing solution instead of new development",
                    f"Found {len(overlap_analysis.overlapping_capabilities)} highly similar capabilities",
                    "Contact capability owners for enhancement requests"
                ],
                "DevelopmentGate"
            )
        
        # Significant overlap - require review
        elif overlap_analysis.functional_similarity_score > 0.7:
            return self._create_gate_decision(
                request.request_id,
                "REVIEW_REQUIRED",
                f"Significant overlap ({overlap_analysis.functional_similarity_score:.2f}) requires review",
                [
                    "Manual review required before proceeding",
                    "Consider enhancement of existing capabilities",
                    "Provide strong justification for new development",
                    f"Review {len(overlap_analysis.overlapping_capabilities)} similar capabilities"
                ],
                "DevelopmentGate"
            )
        
        # Moderate overlap - proceed with caution
        elif overlap_analysis.functional_similarity_score > 0.5:
            return self._create_gate_decision(
                request.request_id,
                "APPROVED",
                f"Moderate overlap ({overlap_analysis.functional_similarity_score:.2f}) - proceed with awareness",
                [
                    "Consider reusing components from existing solutions",
                    "Document unique value proposition",
                    "Coordinate with existing capability owners"
                ],
                "DevelopmentGate"
            )
        
        # Low overlap - approve
        else:
            return self._create_gate_decision(
                request.request_id,
                "APPROVED",
                f"Low overlap ({overlap_analysis.functional_similarity_score:.2f}) - new development justified",
                [],
                "DevelopmentGate"
            )
    
    def _create_gate_decision(
        self,
        request_id: str,
        decision: str,
        reasoning: str,
        required_actions: List[str],
        decision_maker: str
    ) -> GateDecision:
        """Create a gate decision with proper logging."""
        gate_decision = GateDecision(
            request_id=request_id,
            decision=decision,
            reasoning=reasoning,
            required_actions=[action for action in required_actions if action.strip()],
            decision_maker=decision_maker
        )
        
        self.logger.info(
            f"Gate decision for {request_id}: {decision} - {reasoning}"
        )
        
        return gate_decision
    
    def _log_audit_event(
        self,
        event_type: str,
        request_id: str,
        details: Dict[str, Any],
        actor: str
    ) -> None:
        """Log an event to the audit trail."""
        audit_entry = AuditLogEntry(
            event_type=event_type,
            request_id=request_id,
            details=details,
            actor=actor
        )
        
        # Write to audit log file
        try:
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps({
                    "entry_id": audit_entry.entry_id,
                    "timestamp": audit_entry.timestamp.isoformat(),
                    "event_type": audit_entry.event_type,
                    "request_id": audit_entry.request_id,
                    "details": audit_entry.details,
                    "actor": audit_entry.actor,
                    "integrity_hash": audit_entry.integrity_hash
                }) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")
    
    def get_audit_trail(self, request_id: Optional[str] = None) -> List[AuditLogEntry]:
        """Get audit trail entries, optionally filtered by request ID."""
        entries = []
        
        try:
            if self.audit_log_path.exists():
                with open(self.audit_log_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            if not request_id or data.get("request_id") == request_id:
                                entry = AuditLogEntry(
                                    entry_id=data["entry_id"],
                                    timestamp=datetime.fromisoformat(data["timestamp"]),
                                    event_type=data["event_type"],
                                    request_id=data["request_id"],
                                    details=data["details"],
                                    actor=data["actor"],
                                    integrity_hash=data["integrity_hash"]
                                )
                                entries.append(entry)
        except Exception as e:
            self.logger.error(f"Failed to read audit log: {e}")
        
        return entries
    
    def get_gate_statistics(self) -> Dict[str, Any]:
        """Get statistics about gate decisions."""
        audit_entries = self.get_audit_trail()
        
        gate_decisions = [e for e in audit_entries if e.event_type == "GATE_DECISION"]
        
        if not gate_decisions:
            return {
                "total_decisions": 0,
                "approved": 0,
                "blocked": 0,
                "review_required": 0,
                "emergency_overrides": 0
            }
        
        decisions_by_type = {}
        for entry in gate_decisions:
            decision = entry.details.get("decision", "unknown")
            decisions_by_type[decision] = decisions_by_type.get(decision, 0) + 1
        
        emergency_overrides = len([e for e in audit_entries if e.event_type == "EMERGENCY_OVERRIDE"])
        
        return {
            "total_decisions": len(gate_decisions),
            "approved": decisions_by_type.get("APPROVED", 0),
            "blocked": decisions_by_type.get("BLOCKED", 0),
            "review_required": decisions_by_type.get("REVIEW_REQUIRED", 0),
            "emergency_overrides": emergency_overrides,
            "decisions_by_type": decisions_by_type
        }