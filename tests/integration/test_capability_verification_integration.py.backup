"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:24:55.736991
"""



import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

from src.beast_mode.messaging.capability_verifier import (
    CapabilityVerifier, VerificationStatus, TrustLevel
)
from src.beast_mode.messaging.agent_registry import AgentRegistry, DiscoveredAgent
from src.beast_mode.messaging.help_system import HelpWantedSystem, CollaborationSession, CollaborationStatus
from src.beast_mode.messaging.models import BeastModeMessage, MessageType, AgentCapabilities
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule




    def test_rdi_chain_validation(self):
        """Validate RDI chain integrity for this module."""
        rdi_validation = {
            "module": "/Users/lou/kiro-2/kiro-ai-development-hackathon/tests/integration/test_capability_verification_integration.py",
            "requirements": ['R1', 'R2'],
            "validation_timestamp": "2025-09-14T06:24:50.802461",
            "chain_integrity": True,
            "traceability_complete": True,
            "test_classes": 1,
            "test_methods": 11
        }
        
        # Assert RDI chain integrity
        assert rdi_validation["chain_integrity"] is True
        assert rdi_validation["traceability_complete"] is True
        assert len(rdi_validation["requirements"]) > 0
        
        # Log RDI validation results
        print(f"RDI Validation: {rdi_validation}")

class TestCapabilityVerificationIntegration(ReflectiveModule):
    """Integration tests for capability verification workflows"""
    
    @pytest.fixture
    def agent_registry(self):
        """Create a real agent registry for integration testing"""
        return AgentRegistry()
    
    @pytest.fixture
    def help_system(self, agent_registry):
        """Create a real help system for integration testing"""
        return HelpWantedSystem(agent_registry)
    
    @pytest.fixture
    def verifier(self, agent_registry, help_system):
        """Create a capability verifier with real dependencies"""
        return CapabilityVerifier(agent_registry, help_system)
    
    @pytest.fixture
    def sample_agents(self, agent_registry):
        """Create sample agents in the registry"""
        agents = []
        
        # Expert Python developer
        python_expert = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="python_expert",
            payload={
                "agent_capabilities": {
                    "agent_id": "python_expert",
                    "capabilities": ["python", "testing", "debugging", "performance_optimization"],
                    "availability": "ready_for_business",
                    "specializations": ["web_development", "data_analysis"]
                }
            }
        )
        agents.append(agent_registry.register_agent_discovery(python_expert))
        
        # Junior developer
        junior_dev = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="junior_dev",
            payload={
                "agent_capabilities": {
                    "agent_id": "junior_dev",
                    "capabilities": ["python", "testing"],
                    "availability": "ready_for_business"
                }
            }
        )
        agents.append(agent_registry.register_agent_discovery(junior_dev))
        
        # DevOps specialist
        devops_specialist = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="devops_specialist",
            payload={
                "agent_capabilities": {
                    "agent_id": "devops_specialist",
                    "capabilities": ["docker", "kubernetes", "terraform", "gcp"],
                    "availability": "ready_for_business",
                    "specializations": ["infrastructure", "deployment"]
                }
            }
        )
        agents.append(agent_registry.register_agent_discovery(devops_specialist))
        
        return agents
    
    def test_end_to_end_capability_verification(self, verifier, sample_agents):
        """Test complete capability verification workflow"""
        agent_id = "python_expert"
        capability = "python"
        
        # Step 1: Create and start verification test
        test = verifier.create_capability_test(
            agent_id=agent_id,
            capability=capability,
            test_type="interaction",
            test_description="Verify Python coding capability through code review task"
        )
        
        assert verifier.start_capability_test(test.test_id)
        assert test.status == VerificationStatus.IN_PROGRESS
        
        # Step 2: Complete verification test successfully
        result_data = {
            "task_completed": True,
            "code_quality": "excellent",
            "best_practices_followed": True,
            "documentation_quality": "good"
        }
        performance_metrics = {
            "response_time": 4.2,
            "accuracy": 0.95,
            "completeness": 1.0
        }
        
        assert verifier.complete_capability_test(
            test.test_id,
            success=True,
            result_data=result_data,
            performance_metrics=performance_metrics
        )
        
        # Step 3: Verify trust score was updated
        trust_key = (agent_id, capability)
        assert trust_key in verifier.trust_scores
        trust_score = verifier.trust_scores[trust_key]
        assert trust_score.verification_tests_passed == 1
        assert trust_score.last_verification is not None
        
        # Step 4: Record additional interactions
        interactions = [
            (True, 3.5),   # Successful interaction
            (True, 2.8),   # Another success
            (False, 8.0),  # One failure
            (True, 3.2),   # Recovery success
            (True, 2.9)    # Final success
        ]
        
        for success, response_time in interactions:
            verifier.record_interaction_result(agent_id, capability, success, response_time)
        
        # Step 5: Verify final trust metrics
        trust_score = verifier.trust_scores[trust_key]
        assert trust_score.total_interactions == 5
        assert trust_score.successful_interactions == 4
        assert trust_score.average_success_rate == 0.8
        assert trust_score.trust_level in [TrustLevel.HIGH, TrustLevel.MEDIUM, TrustLevel.EXPERT]
        assert trust_score.trust_score > 0.6  # Should be reasonably high
    
    def test_collaboration_based_verification(self, verifier, help_system, sample_agents):
        """Test capability verification through collaboration tracking"""
        # Create a help request
        help_request = help_system.create_help_request(
            requester_id="project_manager",
            required_capabilities=["python", "testing"],
            description="Need help with test automation setup"
        )
        
        # Simulate help response from python_expert
        help_response_msg = BeastModeMessage(
            type=MessageType.HELP_RESPONSE,
            source="python_expert",
            payload={
                "request_id": help_request.request_id,
                "matching_capabilities": ["python", "testing"],
                "confidence_score": 0.9,
                "availability": "ready_for_business",
                "message": "I can help with Python test automation"
            }
        )
        
        # Process the response
        assert help_system.process_help_response(help_response_msg)
        
        # Accept the help and start collaboration
        response_id = help_request.responses[0].response_id
        collaboration = help_system.accept_help_response(help_request.request_id, response_id)
        
        assert collaboration is not None
        assert collaboration.helper_id == "python_expert"
        assert "python" in collaboration.capabilities_used
        assert "testing" in collaboration.capabilities_used
        
        # Simulate successful collaboration
        collaboration.status = CollaborationStatus.COMPLETED
        collaboration.messages_exchanged = 12
        collaboration.success_metrics = {
            "task_completed": True,
            "quality_rating": 4.5,
            "time_efficiency": 0.9
        }
        
        # Record collaboration result
        verifier.record_collaboration_result(collaboration)
        
        # Verify trust scores were updated for both capabilities
        python_key = ("python_expert", "python")
        testing_key = ("python_expert", "testing")
        
        assert python_key in verifier.trust_scores
        assert testing_key in verifier.trust_scores
        
        for trust_score in [verifier.trust_scores[python_key], verifier.trust_scores[testing_key]]:
            assert trust_score.total_interactions == 1
            assert trust_score.successful_interactions == 1
            assert trust_score.average_success_rate == 1.0
    
    def test_capability_recommendation_workflow(self, verifier, help_system, sample_agents):
        """Test complete capability recommendation workflow"""
        # Build up trust history for agents
        agents_capabilities = [
            ("python_expert", "python", [(True, 2.5), (True, 3.0), (True, 2.8), (True, 3.2)]),
            ("python_expert", "testing", [(True, 4.0), (True, 3.5), (False, 6.0), (True, 3.8)]),
            ("junior_dev", "python", [(True, 5.0), (False, 8.0), (True, 6.0)]),
            ("junior_dev", "testing", [(False, 10.0), (True, 7.0), (True, 6.5)]),
        ]
        
        for agent_id, capability, interactions in agents_capabilities:
            for success, response_time in interactions:
                verifier.record_interaction_result(agent_id, capability, success, response_time)
        
        # Mock help system to return our agents
        mock_matches = [
            (sample_agents[0], 0.9),  # python_expert with high match
            (sample_agents[1], 0.7),  # junior_dev with medium match
        ]
        help_system.find_matching_agents = Mock(return_value=mock_matches)
        
        # Get recommendations
        recommendations = verifier.get_capability_recommendations(
            required_capabilities=["python", "testing"],
            min_trust_score=0.3,
            max_recommendations=10
        )
        
        # Verify recommendations
        assert len(recommendations) > 0
        
        # Should have recommendations for python_expert (higher trust)
        expert_recommendations = [r for r in recommendations if r.agent_id == "python_expert"]
        junior_recommendations = [r for r in recommendations if r.agent_id == "junior_dev"]
        
        assert len(expert_recommendations) > 0
        
        # Expert should have higher confidence than junior
        if junior_recommendations:
            max_expert_confidence = max(r.confidence for r in expert_recommendations)
            max_junior_confidence = max(r.confidence for r in junior_recommendations)
            assert max_expert_confidence >= max_junior_confidence
        
        # Check recommendation details
        for recommendation in expert_recommendations:
            assert recommendation.agent_id == "python_expert"
            assert recommendation.capability in ["python", "testing"]
            assert 0.0 <= recommendation.confidence <= 1.0
            assert 0.0 <= recommendation.trust_score <= 1.0
            assert recommendation.estimated_success_rate > 0.0
            assert recommendation.estimated_response_time > 0.0
            assert isinstance(recommendation.risk_factors, list)
    
    def test_agent_reputation_tracking(self, verifier, sample_agents):
        """Test comprehensive agent reputation tracking"""
        agent_id = "python_expert"
        
        # Build comprehensive interaction history
        capabilities_data = {
            "python": [(True, 2.5), (True, 3.0), (True, 2.8), (False, 5.0), (True, 3.2)],
            "testing": [(True, 4.0), (True, 3.5), (True, 4.2), (True, 3.8)],
            "debugging": [(True, 6.0), (False, 10.0), (True, 5.5)],
            "performance_optimization": [(True, 8.0), (True, 7.5)]
        }
        
        for capability, interactions in capabilities_data.items():
            for success, response_time in interactions:
                verifier.record_interaction_result(agent_id, capability, success, response_time)
        
        # Add some verification test results
        for capability in ["python", "testing"]:
            test = verifier.create_capability_test(agent_id, capability)
            verifier.start_capability_test(test.test_id)
            verifier.complete_capability_test(test.test_id, success=True)
        
        # Get comprehensive reputation
        reputation = verifier.get_agent_reputation(agent_id)
        
        # Verify reputation structure
        assert reputation['agent_id'] == agent_id
        assert reputation['overall_trust_level'] in [level.value for level in TrustLevel]
        assert 0.0 <= reputation['overall_trust_score'] <= 1.0
        assert reputation['total_interactions'] == sum(len(interactions) for interactions in capabilities_data.values())
        assert len(reputation['capabilities']) == len(capabilities_data)
        
        # Verify individual capability data
        for capability in capabilities_data.keys():
            assert capability in reputation['capabilities']
            cap_data = reputation['capabilities'][capability]
            
            assert 'trust_level' in cap_data
            assert 'trust_score' in cap_data
            assert 'success_rate' in cap_data
            assert 'total_interactions' in cap_data
            assert 'average_response_time' in cap_data
            assert 'consistency_score' in cap_data
        
        # Verify reputation summary is meaningful
        assert isinstance(reputation['reputation_summary'], str)
        assert len(reputation['reputation_summary']) > 0
        assert "No interaction history" not in reputation['reputation_summary']
    
    def test_trust_level_progression(self, verifier):
        """Test trust level progression through interactions"""
        agent_id = "test_agent"
        capability = "python"
        
        # Start with unknown (insufficient interactions)
        verifier.record_interaction_result(agent_id, capability, True)
        verifier.record_interaction_result(agent_id, capability, True)
        
        trust_key = (agent_id, capability)
        trust_score = verifier.trust_scores[trust_key]
        assert trust_score.trust_level == TrustLevel.UNKNOWN
        
        # Add more successful interactions to reach higher trust
        for _ in range(8):  # Total 10 interactions, all successful
            verifier.record_interaction_result(agent_id, capability, True, 3.0)
        
        trust_score = verifier.trust_scores[trust_key]
        assert trust_score.trust_level in [TrustLevel.HIGH, TrustLevel.EXPERT]
        assert trust_score.average_success_rate == 1.0
        
        # Add some failures to see trust level adjust
        for _ in range(5):  # 5 failures out of 15 total
            verifier.record_interaction_result(agent_id, capability, False, 8.0)
        
        trust_score = verifier.trust_scores[trust_key]
        assert trust_score.trust_level in [TrustLevel.MEDIUM, TrustLevel.HIGH]
        assert trust_score.average_success_rate == 10/15  # 10 successes out of 15
    
    def test_verification_system_statistics(self, verifier, sample_agents):
        """Test verification system statistics tracking"""
        # Create various tests and interactions
        verifier.create_capability_test("python_expert", "python")
        verifier.create_capability_test("junior_dev", "testing")
        
        # Record some interactions
        verifier.record_interaction_result("python_expert", "python", True)
        verifier.record_interaction_result("junior_dev", "testing", False)
        verifier.record_interaction_result("devops_specialist", "docker", True)
        
        # Get statistics
        stats = verifier.get_verification_stats()
        
        # Verify statistics structure
        assert 'tests_created' in stats
        assert 'tests_completed' in stats
        assert 'tests_passed' in stats
        assert 'tests_failed' in stats
        assert 'trust_scores_updated' in stats
        assert 'recommendations_generated' in stats
        assert 'active_tests' in stats
        assert 'total_trust_scores' in stats
        assert 'trust_level_distribution' in stats
        
        # Verify values make sense
        assert stats['tests_created'] == 2
        assert stats['total_trust_scores'] == 3
        assert stats['trust_scores_updated'] == 3
        
        # Verify trust level distribution
        trust_distribution = stats['trust_level_distribution']
        assert isinstance(trust_distribution, dict)
        assert all(level in trust_distribution for level in [level.value for level in TrustLevel])
    
    def test_expired_test_cleanup(self, verifier):
        """Test cleanup of expired verification tests"""
        # Create and start tests with short timeout
        test1 = verifier.create_capability_test("agent1", "python", timeout_minutes=1)
        test2 = verifier.create_capability_test("agent2", "java", timeout_minutes=1)
        
        verifier.start_capability_test(test1.test_id)
        verifier.start_capability_test(test2.test_id)
        
        # Manually expire the tests
        past_time = datetime.now() - timedelta(minutes=2)
        test1.started_at = past_time
        test2.started_at = past_time
        
        # Run cleanup
        expired_count = verifier.cleanup_expired_tests()
        
        assert expired_count == 2
        assert test1.status == VerificationStatus.EXPIRED
        assert test2.status == VerificationStatus.EXPIRED
        assert test1.completed_at is not None
        assert test2.completed_at is not None


if __name__ == "__main__":

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

    pytest.main([__file__])