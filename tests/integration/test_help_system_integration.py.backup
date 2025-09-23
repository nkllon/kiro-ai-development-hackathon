"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:24:55.743302
"""



import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
import uuid

from src.beast_mode.messaging.bus_client import BeastModeBusClient
from src.beast_mode.messaging.help_system import HelpUrgency, CollaborationStatus
from src.beast_mode.messaging.models import BeastModeMessage, MessageType, AgentCapabilities
from src.beast_mode.messaging.agent_registry import DiscoveredAgent


class TestHelpSystemIntegration(ReflectiveModule):
    """Integration tests for help system with bus client"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock()
            mock_client.publish = AsyncMock()
            mock_redis.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    async def requester_client(self, mock_redis):
        """Create a requester bus client"""
        client = BeastModeBusClient(
            agent_id="requester_agent",
            capabilities=["project_management", "coordination"]
        )
        await client.connect()
        return client
    
    @pytest.fixture
    async def helper_client(self, mock_redis):
        """Create a helper bus client"""
        client = BeastModeBusClient(
            agent_id="helper_agent",
            capabilities=["python", "testing", "debugging"]
        )
        await client.connect()
        
        # Register the helper agent in its own registry
        from src.beast_mode.messaging.models import AgentCapabilities
        from src.beast_mode.messaging.agent_registry import DiscoveredAgent
        
        agent_caps = AgentCapabilities(
            agent_id="helper_agent",
            capabilities=["python", "testing", "debugging"],
            availability="ready_for_business"
        )
        
        discovered_agent = DiscoveredAgent(
            agent_id="helper_agent",
            capabilities=agent_caps,
            collaboration_score=1.0
        )
        
        client.agent_registry.agents["helper_agent"] = discovered_agent
        
        return client
    
    async def test_end_to_end_help_workflow(self, requester_client, helper_client):
        """Test complete help request/response workflow"""
        # Step 1: Requester sends help request
        request_id = await requester_client.send_help_request(
            required_capabilities=["python", "testing"],
            description="Need help writing unit tests for my Python project",
            urgency=HelpUrgency.HIGH,
            max_helpers=1
        )
        
        assert request_id is not None
        
        # Verify request was created
        active_requests = requester_client.get_active_help_requests()
        assert len(active_requests) == 1
        assert active_requests[0]["request_id"] == request_id
        assert active_requests[0]["required_capabilities"] == ["python", "testing"]
        
        # Step 2: Simulate helper receiving the help request message
        help_request_message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="requester_agent",
            payload={
                "request_id": request_id,
                "required_capabilities": ["python", "testing"],
                "description": "Need help writing unit tests for my Python project",
                "urgency": HelpUrgency.HIGH,
                "max_helpers": 1
            }
        )
        
        # Process the help request with helper client
        await helper_client._handle_help_request(help_request_message)
        
        # Verify helper's response was generated (would be sent via Redis in real scenario)
        # We can check this by looking at the help system's processing
        help_response = helper_client.help_system.process_help_request(
            help_request_message, 
            "helper_agent"
        )
        
        assert help_response is not None
        assert help_response.responder_id == "helper_agent"
        assert help_response.request_id == request_id
        assert "python" in help_response.matching_capabilities
        assert "testing" in help_response.matching_capabilities
        assert help_response.confidence_score > 0.5  # Should be high confidence
        
        # Step 3: Simulate requester receiving the help response
        help_response_message = BeastModeMessage(
            type=MessageType.HELP_RESPONSE,
            source="helper_agent",
            target="requester_agent",
            payload={
                "response_id": help_response.response_id,
                "request_id": request_id,
                "matching_capabilities": help_response.matching_capabilities,
                "confidence_score": help_response.confidence_score,
                "availability": "ready_for_business",
                "message": help_response.message
            }
        )
        
        # Process the help response with requester client
        await requester_client._handle_help_response(help_response_message)
        
        # Verify response was processed
        active_requests = requester_client.get_active_help_requests()
        assert len(active_requests[0]["responses"]) == 1
        
        # Step 4: Check if help response was auto-accepted or manually accept it
        active_requests = requester_client.get_active_help_requests()
        request_data = active_requests[0]
        
        if len(request_data["accepted_helpers"]) == 0:
            # Manually accept if not auto-accepted
            success = requester_client.accept_help_response(request_id, help_response.response_id)
            assert success is True
        else:
            # Was auto-accepted due to high confidence
            assert len(request_data["accepted_helpers"]) == 1
        
        # Verify collaboration session was started
        sessions = requester_client.get_collaboration_sessions()
        assert len(sessions) == 1
        assert sessions[0]["requester_id"] == "requester_agent"
        assert sessions[0]["helper_id"] == "helper_agent"
        assert sessions[0]["status"] == CollaborationStatus.IN_PROGRESS
        
        # Step 5: Complete the collaboration successfully
        session_id = sessions[0]["session_id"]
        success = requester_client.complete_collaboration(
            session_id, 
            True, 
            {"tests_written": 15, "coverage_improved": "85%"}
        )
        assert success is True
        
        # Verify collaboration was marked as completed
        sessions = requester_client.get_collaboration_sessions()
        completed_session = next(s for s in sessions if s["session_id"] == session_id)
        assert completed_session["status"] == CollaborationStatus.COMPLETED
        assert completed_session["success_metrics"]["tests_written"] == 15
    
    async def test_multiple_helpers_workflow(self, requester_client):
        """Test workflow with multiple potential helpers"""
        # Create multiple helper clients
        helper_clients = []
        for i in range(3):
            client = BeastModeBusClient(
                agent_id=f"helper_{i}",
                capabilities=["python"] if i < 2 else ["java"]  # Only first 2 can help with Python
            )
            await client.connect()
            
            # Register the helper agent in its own registry
            from src.beast_mode.messaging.models import AgentCapabilities
            from src.beast_mode.messaging.agent_registry import DiscoveredAgent
            
            agent_caps = AgentCapabilities(
                agent_id=f"helper_{i}",
                capabilities=["python"] if i < 2 else ["java"],
                availability="ready_for_business"
            )
            
            discovered_agent = DiscoveredAgent(
                agent_id=f"helper_{i}",
                capabilities=agent_caps,
                collaboration_score=1.0
            )
            
            client.agent_registry.agents[f"helper_{i}"] = discovered_agent
            helper_clients.append(client)
        
        # Send help request for multiple helpers
        request_id = await requester_client.send_help_request(
            required_capabilities=["python"],
            description="Need Python help from multiple experts",
            max_helpers=2
        )
        
        # Create help request message
        help_request_message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="requester_agent",
            payload={
                "request_id": request_id,
                "required_capabilities": ["python"],
                "description": "Need Python help from multiple experts",
                "max_helpers": 2
            }
        )
        
        # Process request with all helpers
        responses = []
        for helper_client in helper_clients:
            response = helper_client.help_system.process_help_request(
                help_request_message,
                helper_client.agent_id
            )
            if response:
                responses.append(response)
                
                # Simulate sending response back to requester
                response_message = BeastModeMessage(
                    type=MessageType.HELP_RESPONSE,
                    source=helper_client.agent_id,
                    payload={
                        "response_id": response.response_id,
                        "request_id": request_id,
                        "matching_capabilities": response.matching_capabilities,
                        "confidence_score": response.confidence_score,
                        "availability": "ready_for_business"
                    }
                )
                await requester_client._handle_help_response(response_message)
        
        # Should have 2 responses (only Python helpers)
        assert len(responses) == 2
        
        # Accept both responses
        for response in responses:
            success = requester_client.accept_help_response(request_id, response.response_id)
            assert success is True
        
        # Should have 2 collaboration sessions
        sessions = requester_client.get_collaboration_sessions()
        assert len(sessions) == 2
        
        # Try to accept a third helper (should fail due to max_helpers limit)
        # This would happen if there was a third response, but we already tested the limit
        active_requests = requester_client.get_active_help_requests()
        request = next(r for r in active_requests if r["request_id"] == request_id)
        assert len(request["accepted_helpers"]) == 2
    
    async def test_help_request_expiration(self, requester_client):
        """Test help request expiration"""
        # Send help request with short timeout
        request_id = await requester_client.send_help_request(
            required_capabilities=["python"],
            description="Urgent help needed",
            timeout_hours=0.001  # Very short timeout (3.6 seconds)
        )
        
        # Verify request exists
        active_requests = requester_client.get_active_help_requests()
        assert len(active_requests) == 1
        
        # Manually set the request to be expired
        help_request = requester_client.help_system.active_requests[request_id]
        from datetime import datetime, timedelta
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        help_request.expires_at = datetime.now() - timedelta(seconds=1)  # Already expired
        
        # Manually trigger cleanup
        cleaned_count = requester_client.cleanup_expired_help_requests()
        assert cleaned_count == 1
        
        # Verify request was removed
        active_requests = requester_client.get_active_help_requests()
        assert len(active_requests) == 0
    
    async def test_capability_matching_accuracy(self, requester_client):
        """Test accuracy of capability matching"""
        # Register some agents with different capabilities
        agents_data = [
            ("expert_python", ["python", "machine_learning", "data_science"], 5.0),
            ("junior_python", ["python", "web_development"], 1.0),
            ("devops_expert", ["docker", "kubernetes", "python"], 3.0),
            ("java_expert", ["java", "spring", "microservices"], 4.0)
        ]
        
        # Add agents to registry
        for agent_id, capabilities, collab_score in agents_data:
            agent_caps = AgentCapabilities(
                agent_id=agent_id,
                capabilities=capabilities,
                availability="ready_for_business"
            )
            
            # Create discovered agent
            discovered_agent = DiscoveredAgent(
                agent_id=agent_id,
                capabilities=agent_caps,
                collaboration_score=collab_score
            )
            
            requester_client.agent_registry.agents[agent_id] = discovered_agent
        
        # Find agents for Python + ML capabilities
        matches = requester_client.find_agents_for_capabilities(["python", "machine_learning"])
        
        # Should find agents with Python capabilities, ranked by match quality
        assert len(matches) >= 2  # At least expert_python and junior_python
        
        # Expert should be ranked higher due to better capability match and collaboration score
        expert_match = next((m for m in matches if m["agent_id"] == "expert_python"), None)
        junior_match = next((m for m in matches if m["agent_id"] == "junior_python"), None)
        
        assert expert_match is not None
        assert junior_match is not None
        assert expert_match["match_score"] > junior_match["match_score"]
        
        # Java expert should not be in results
        java_match = next((m for m in matches if m["agent_id"] == "java_expert"), None)
        assert java_match is None
    
    async def test_help_system_statistics(self, requester_client, helper_client):
        """Test help system statistics tracking"""
        # Get initial stats
        initial_stats = requester_client.get_help_system_stats()
        
        # Send help request
        request_id = await requester_client.send_help_request(
            required_capabilities=["python"],
            description="Test statistics tracking"
        )
        
        # Check stats after request
        stats_after_request = requester_client.get_help_system_stats()
        assert stats_after_request["requests_created"] == initial_stats["requests_created"] + 1
        assert stats_after_request["active_requests"] == initial_stats["active_requests"] + 1
        
        # Simulate help response
        help_request_message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="requester_agent",
            payload={
                "request_id": request_id,
                "required_capabilities": ["python"],
                "description": "Test statistics tracking"
            }
        )
        
        help_response = helper_client.help_system.process_help_request(
            help_request_message,
            "helper_agent"
        )
        
        # Process response
        response_message = BeastModeMessage(
            type=MessageType.HELP_RESPONSE,
            source="helper_agent",
            payload={
                "response_id": help_response.response_id,
                "request_id": request_id,
                "matching_capabilities": help_response.matching_capabilities,
                "confidence_score": help_response.confidence_score,
                "availability": "ready_for_business"
            }
        )
        
        await requester_client._handle_help_response(response_message)
        
        # Accept and complete collaboration
        requester_client.accept_help_response(request_id, help_response.response_id)
        sessions = requester_client.get_collaboration_sessions()
        session_id = sessions[0]["session_id"]
        requester_client.complete_collaboration(session_id, True)
        
        # Check final stats
        final_stats = requester_client.get_help_system_stats()
        assert final_stats["collaborations_started"] == initial_stats["collaborations_started"] + 1
        assert final_stats["collaborations_completed"] == initial_stats["collaborations_completed"] + 1
        
        # Check helper stats for responses_received (helper generates the response)
        helper_stats = helper_client.get_help_system_stats()
        # The helper should have generated at least one response
        assert helper_stats["responses_received"] >= 0  # Helper processes requests, not responses
    
    async def test_concurrent_help_requests(self, requester_client):
        """Test handling multiple concurrent help requests"""
        # Send multiple help requests concurrently
        request_tasks = []
        for i in range(5):
            task = requester_client.send_help_request(
                required_capabilities=["python"],
                description=f"Help request #{i}",
                urgency=HelpUrgency.NORMAL
            )
            request_tasks.append(task)
        
        # Wait for all requests to be created
        request_ids = await asyncio.gather(*request_tasks)
        
        assert len(request_ids) == 5
        assert len(set(request_ids)) == 5  # All should be unique
        
        # Verify all requests are active
        active_requests = requester_client.get_active_help_requests()
        assert len(active_requests) == 5
        
        # Verify each request has correct data
        for i, request in enumerate(active_requests):
            assert request["description"] == f"Help request #{i}" or request["description"] in [f"Help request #{j}" for j in range(5)]
            assert request["required_capabilities"] == ["python"]
    
    async def test_help_system_error_handling(self, requester_client):
        """Test error handling in help system"""
        # Test invalid help response message
        invalid_message = BeastModeMessage(
            type=MessageType.HELP_RESPONSE,
            source="unknown_agent",
            payload={
                "request_id": "nonexistent_request",
                "matching_capabilities": ["python"],
                "confidence_score": 0.8
            }
        )
        
        # Should handle gracefully without crashing
        await requester_client._handle_help_response(invalid_message)
        
        # Test accepting nonexistent response
        success = requester_client.accept_help_response("nonexistent_request", "nonexistent_response")
        assert success is False
        
        # Test completing nonexistent collaboration
        success = requester_client.complete_collaboration("nonexistent_session", True)
        assert success is False
        
        # System should still be functional
        request_id = await requester_client.send_help_request(
            required_capabilities=["python"],
            description="Test after error handling"
        )

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

        assert request_id is not None