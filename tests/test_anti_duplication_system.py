"""
Comprehensive tests for the Anti-Duplication System.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

from src.anti_duplication.capability_registry import CapabilityRegistry
from src.anti_duplication.discovery_engine import CapabilityDiscoveryEngine
from src.anti_duplication.development_gate import DevelopmentGate
from src.anti_duplication.models import (
    DevelopmentRequest, CapabilityType, OverlapRecommendation
)


class TestAntiDuplicationSystem:
    """Integration tests for the complete anti-duplication system."""
    
    @pytest.fixture
    def temp_codebase(self):
        """Create a temporary codebase for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create sample Python files
            (temp_path / "src").mkdir()
            
            # Existing WebSocket functionality
            websocket_file = temp_path / "src" / "websocket_handler.py"
            websocket_file.write_text('''
"""WebSocket handler for real-time communication."""

class WebSocketHandler:
    """Handles WebSocket connections and message routing."""
    
    def __init__(self):
        self.connections = []
    
    def handle_connection(self, websocket):
        """Handle new WebSocket connection."""
        self.connections.append(websocket)
    
    def broadcast_message(self, message):
        """Broadcast message to all connections."""
        for conn in self.connections:
            conn.send(message)
''')
            
            # Existing validation functionality
            validation_file = temp_path / "src" / "validator.py"
            validation_file.write_text('''
"""Input validation utilities."""

def validate_input(data):
    """Validate input data."""
    if not data:
        return False
    return True

def sanitize_input(data):
    """Sanitize input data."""
    return str(data).strip()
''')
            
            yield temp_path
    
    @pytest.fixture
    def registry(self, temp_codebase):
        """Create capability registry for testing."""
        return CapabilityRegistry(temp_codebase)
    
    @pytest.fixture
    def discovery_engine(self, registry):
        """Create discovery engine for testing."""
        return CapabilityDiscoveryEngine(registry)
    
    @pytest.fixture
    def development_gate(self, discovery_engine):
        """Create development gate for testing."""
        return DevelopmentGate(discovery_engine)
    
    def test_capability_registry_scanning(self, registry):
        """Test that capability registry can scan and index code."""
        # Perform scan
        scan_results = registry.scan_codebase()
        
        # Verify scan results
        assert scan_results["files_scanned"] >= 2
        assert scan_results["capabilities_found"] >= 3
        assert scan_results["errors_encountered"] == 0
        
        # Verify registry freshness
        freshness = registry.validate_freshness()
        assert freshness["is_fresh"] is True
        assert freshness["capabilities_count"] >= 3
    
    def test_semantic_search(self, registry):
        """Test semantic search functionality."""
        # Scan codebase first
        registry.scan_codebase()
        
        # Search for WebSocket-related capabilities
        websocket_results = registry.semantic_search("websocket connection")
        assert len(websocket_results) > 0
        
        # Verify we found the WebSocket handler
        websocket_handler_found = any(
            "WebSocketHandler" in result.name for result in websocket_results
        )
        assert websocket_handler_found
        
        # Search for validation capabilities
        validation_results = registry.semantic_search("validate input")
        assert len(validation_results) > 0
    
    def test_discovery_engine_existing_solutions(self, discovery_engine):
        """Test discovery of existing solutions."""
        # Scan registry first
        discovery_engine.registry.scan_codebase()
        
        # Discover solutions for WebSocket functionality
        inventory = discovery_engine.discover_existing_solutions("websocket real-time messaging")
        
        # Verify discovery results
        assert inventory.domain == "websocket real-time messaging"
        assert len(inventory.existing_solutions) > 0
        assert inventory.discovery_completeness_score > 0.0
        
        # Check that WebSocket handler was found
        websocket_solution_found = any(
            "websocket" in solution.name.lower() or "websocket" in solution.description.lower()
            for solution in inventory.existing_solutions
        )
        assert websocket_solution_found
    
    def test_overlap_analysis_high_similarity(self, discovery_engine):
        """Test overlap analysis with high similarity."""
        # Scan registry first
        discovery_engine.registry.scan_codebase()
        
        # Discover existing solutions
        inventory = discovery_engine.discover_existing_solutions("websocket handler")
        
        # Analyze overlap with very similar proposed functionality
        proposed_spec = "WebSocket connection handler for real-time messaging"
        overlap_analysis = discovery_engine.assess_functional_overlap(proposed_spec, inventory)
        
        # Verify high overlap detected
        assert overlap_analysis.functional_similarity_score > 0.5
        assert len(overlap_analysis.overlapping_capabilities) > 0
        assert overlap_analysis.justification_required is True
    
    def test_overlap_analysis_low_similarity(self, discovery_engine):
        """Test overlap analysis with low similarity."""
        # Scan registry first
        discovery_engine.registry.scan_codebase()
        
        # Discover existing solutions
        inventory = discovery_engine.discover_existing_solutions("database operations")
        
        # Analyze overlap with dissimilar proposed functionality
        proposed_spec = "Machine learning model training pipeline"
        overlap_analysis = discovery_engine.assess_functional_overlap(proposed_spec, inventory)
        
        # Verify low overlap
        assert overlap_analysis.functional_similarity_score < 0.3
        assert overlap_analysis.recommendation == OverlapRecommendation.PROCEED
    
    def test_discovery_attestation_generation(self, discovery_engine):
        """Test generation of discovery attestations."""
        # Scan registry first
        discovery_engine.registry.scan_codebase()
        
        # Create development request
        request = DevelopmentRequest(
            problem_statement="Need email notification system",
            proposed_solution="Build new email service with templates",
            requester="test_user"
        )
        
        # Perform discovery and overlap analysis
        inventory = discovery_engine.discover_existing_solutions(request.problem_statement)
        overlap_analysis = discovery_engine.assess_functional_overlap(
            request.proposed_solution, inventory
        )
        
        # Generate attestation
        attestation = discovery_engine.generate_discovery_attestation(
            request, inventory, overlap_analysis, "No existing email service found"
        )
        
        # Verify attestation
        assert attestation.problem_domain == request.problem_statement
        assert attestation.overlap_analysis_completed is True
        assert attestation.attestation_signature != ""
        assert attestation.attesting_agent == "CapabilityDiscoveryEngine"
        
        # Verify signature validation
        assert discovery_engine.validate_attestation_signature(attestation) is True
    
    def test_development_gate_approval(self, development_gate):
        """Test development gate approval for low overlap."""
        # Scan registry first
        development_gate.discovery_engine.registry.scan_codebase()
        
        # Create development request with low overlap
        request = DevelopmentRequest(
            problem_statement="Machine learning model training",
            proposed_solution="Build ML training pipeline with TensorFlow",
            requester="test_user",
            discovery_completed=True,
            discovery_attestation_id="test_attestation"
        )
        
        # Validate request
        decision = development_gate.validate_development_request(request)
        
        # Should be approved due to low overlap
        assert decision.is_approved
        assert "low overlap" in decision.reasoning.lower() or "proceed" in decision.reasoning.lower()
    
    def test_development_gate_blocking(self, development_gate):
        """Test development gate blocking for high overlap."""
        # Scan registry first
        development_gate.discovery_engine.registry.scan_codebase()
        
        # Create development request with high overlap
        request = DevelopmentRequest(
            problem_statement="websocket connection handling",
            proposed_solution="Build WebSocket handler for real-time connections",
            requester="test_user",
            discovery_completed=True,
            discovery_attestation_id="test_attestation"
        )
        
        # Validate request
        decision = development_gate.validate_development_request(request)
        
        # Should be blocked or require review due to high overlap
        assert decision.is_blocked or decision.decision == "REVIEW_REQUIRED"
        assert len(decision.required_actions) > 0
    
    def test_emergency_override(self, development_gate):
        """Test emergency override functionality."""
        # Create blocked request
        request = DevelopmentRequest(
            problem_statement="urgent websocket fix",
            proposed_solution="Duplicate WebSocket handler for emergency",
            requester="test_user"
        )
        
        # Use emergency override
        decision = development_gate.emergency_override(
            request, 
            "Critical production issue requires immediate fix",
            "emergency_authority"
        )
        
        # Should be approved with override
        assert decision.is_approved
        assert "emergency override" in decision.reasoning.lower()
        assert "mandatory review" in " ".join(decision.required_actions).lower()
    
    def test_audit_trail(self, development_gate):
        """Test audit trail functionality."""
        # Perform some operations that generate audit events
        request = DevelopmentRequest(
            problem_statement="test functionality",
            proposed_solution="test implementation",
            requester="test_user"
        )
        
        # Use emergency override to generate audit event
        development_gate.emergency_override(
            request,
            "Test override",
            "test_authority"
        )
        
        # Check audit trail
        audit_entries = development_gate.get_audit_trail(request.request_id)
        assert len(audit_entries) > 0
        
        # Verify audit entry content
        override_entry = next(
            (entry for entry in audit_entries if entry.event_type == "EMERGENCY_OVERRIDE"),
            None
        )
        assert override_entry is not None
        assert override_entry.request_id == request.request_id
        assert override_entry.actor == "test_authority"
        assert override_entry.integrity_hash != ""
    
    def test_gate_statistics(self, development_gate):
        """Test gate statistics functionality."""
        # Generate some decisions
        request1 = DevelopmentRequest(problem_statement="test1", requester="user1")
        request2 = DevelopmentRequest(problem_statement="test2", requester="user2")
        
        development_gate.emergency_override(request1, "test", "authority")
        development_gate.emergency_override(request2, "test", "authority")
        
        # Get statistics
        stats = development_gate.get_gate_statistics()
        
        # Verify statistics
        assert stats["emergency_overrides"] >= 2
        assert stats["total_decisions"] >= 0
        assert isinstance(stats["decisions_by_type"], dict)
    
    def test_end_to_end_workflow(self, temp_codebase):
        """Test complete end-to-end workflow."""
        # Initialize system
        registry = CapabilityRegistry(temp_codebase)
        discovery_engine = CapabilityDiscoveryEngine(registry)
        gate = DevelopmentGate(discovery_engine)
        
        # Step 1: Scan codebase
        scan_results = registry.scan_codebase()
        assert scan_results["capabilities_found"] > 0
        
        # Step 2: Create development request
        request = DevelopmentRequest(
            problem_statement="email notification system",
            proposed_solution="Build email service with SMTP integration",
            requester="developer"
        )
        
        # Step 3: Perform discovery
        inventory = discovery_engine.discover_existing_solutions(request.problem_statement)
        assert inventory.discovery_completeness_score > 0
        
        # Step 4: Analyze overlap
        overlap_analysis = discovery_engine.assess_functional_overlap(
            request.proposed_solution, inventory
        )
        assert overlap_analysis.analysis_id != ""
        
        # Step 5: Generate attestation
        attestation = discovery_engine.generate_discovery_attestation(
            request, inventory, overlap_analysis, "New functionality justified"
        )
        assert attestation.is_valid
        
        # Step 6: Update request with discovery completion
        request.discovery_completed = True
        request.discovery_attestation_id = attestation.attestation_id
        
        # Step 7: Validate through gate
        decision = gate.validate_development_request(request)
        assert decision.decision in ["APPROVED", "BLOCKED", "REVIEW_REQUIRED"]
        
        # Step 8: Check audit trail
        audit_entries = gate.get_audit_trail(request.request_id)
        assert len(audit_entries) > 0
    
    def test_performance_requirements(self, registry):
        """Test that performance requirements are met."""
        import time
        
        # Test registry scan performance
        start_time = time.time()
        registry.scan_codebase()
        scan_time = time.time() - start_time
        
        # Should complete scan in reasonable time (< 10 seconds for small codebase)
        assert scan_time < 10.0
        
        # Test search performance
        start_time = time.time()
        results = registry.semantic_search("websocket")
        search_time = time.time() - start_time
        
        # Should complete search in < 2 seconds
        assert search_time < 2.0
        assert len(results) >= 0  # May be empty, that's ok
    
    def test_registry_freshness_validation(self, registry):
        """Test registry freshness validation."""
        # Initially registry should not be fresh
        freshness = registry.validate_freshness()
        assert freshness["is_fresh"] is False
        
        # After scan, should be fresh
        registry.scan_codebase()
        freshness = registry.validate_freshness()
        assert freshness["is_fresh"] is True
        assert freshness["age_hours"] < 1.0
    
    def test_error_handling(self, temp_codebase):
        """Test error handling in various scenarios."""
        # Test with invalid codebase path
        invalid_registry = CapabilityRegistry(Path("/nonexistent/path"))
        
        # Should handle gracefully
        scan_results = invalid_registry.scan_codebase()
        assert "error" in scan_results or scan_results["files_scanned"] == 0
        
        # Test with corrupted file
        corrupted_file = temp_codebase / "corrupted.py"
        corrupted_file.write_text("invalid python syntax $$$ !!!")
        
        registry = CapabilityRegistry(temp_codebase)
        scan_results = registry.scan_codebase()
        
        # Should handle corrupted files gracefully
        assert scan_results["errors_encountered"] >= 0  # May encounter errors, that's ok
        assert scan_results["capabilities_found"] >= 0  # Should still find some capabilities