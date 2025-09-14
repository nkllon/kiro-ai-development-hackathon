"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.559026
"""




import pytest
import asyncio
from datetime import datetime, time, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.beast_mode.messaging.bus_client import BeastModeBusClient
from src.beast_mode.messaging.collaboration_scheduler import (
    CollaborationType,
    OfficeHoursPattern,
    CollaborationStatus
)
from src.beast_mode.messaging.models import BeastModeMessage, MessageType


class TestCollaborationSchedulerIntegration(ReflectiveModule):
    """Test collaboration scheduler integration with bus client"""
    
    @pytest.fixture
    async def bus_client(self):
        """Create a test bus client with mocked Redis"""
        client = BeastModeBusClient(
            redis_url="redis://localhost:6379",
            agent_id="test_agent",
            capabilities=["python", "testing", "collaboration"]
        )
        
        # Mock Redis connection
        client.client = AsyncMock()
        client.client.ping = AsyncMock(return_value=True)
        client.client.publish = AsyncMock()
        client.is_connected = True
        
        return client
    
    @pytest.mark.asyncio
    async def test_announce_office_hours(self, bus_client):
        """Test announcing office hours to the network"""
        await bus_client.announce_office_hours(
            pattern=OfficeHoursPattern.DAILY,
            start_time=time(9, 0),
            end_time=time(17, 0),
            description="Daily collaboration hours",
            capabilities_focus=["python", "testing"]
        )
        
        # Check office hours were set locally
        office_hours = bus_client.collaboration_scheduler.get_office_hours()
        assert office_hours is not None
        assert office_hours.pattern == OfficeHoursPattern.DAILY
        assert office_hours.start_time == time(9, 0)
        assert office_hours.end_time == time(17, 0)
        assert office_hours.description == "Daily collaboration hours"
        assert office_hours.capabilities_focus == ["python", "testing"]
        
        # Check message was published
        bus_client.client.publish.assert_called_once()
        call_args = bus_client.client.publish.call_args
        assert call_args[0][0] == "beast_mode_network"  # channel
        
        # Parse the published message
        import json
        message_data = json.loads(call_args[0][1])
        assert message_data['type'] == MessageType.OFFICE_HOURS_ANNOUNCEMENT
        assert message_data['source'] == "test_agent"
        assert message_data['target'] is None  # Broadcast
        
        office_hours_data = message_data['payload']['office_hours']
        assert office_hours_data['pattern'] == "daily"
        assert office_hours_data['start_time'] == "09:00:00"
        assert office_hours_data['end_time'] == "17:00:00"
        assert office_hours_data['description'] == "Daily collaboration hours"
        assert office_hours_data['capabilities_focus'] == ["python", "testing"]
    
    @pytest.mark.asyncio
    async def test_request_collaboration(self, bus_client):
        """Test requesting collaboration with other agents"""
        # Set up office hours for the requesting agent
        bus_client.collaboration_scheduler.set_office_hours(
            pattern=OfficeHoursPattern.DAILY,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        target_agents = ["agent1", "agent2"]
        topic = "Code review session"
        scheduled_start = datetime(2024, 1, 1, 10, 0)
        
        request_id = await bus_client.request_collaboration(
            target_agents=target_agents,
            topic=topic,
            collaboration_type=CollaborationType.SCHEDULED_SESSION,
            scheduled_start=scheduled_start,
            duration_minutes=60,
            description="Review recent changes",
            required_capabilities=["python", "code_review"]
        )
        
        assert request_id is not None
        
        # Check session was created locally
        sessions = bus_client.collaboration_scheduler.sessions
        assert len(sessions) == 1
        
        session = list(sessions.values())[0]
        assert session.organizer_id == "test_agent"
        assert session.participants == ["test_agent", "agent1", "agent2"]
        assert session.topic == topic
        assert session.session_type == CollaborationType.SCHEDULED_SESSION
        assert session.scheduled_start == scheduled_start
        assert session.description == "Review recent changes"
        assert session.required_capabilities == ["python", "code_review"]
        assert session.status == CollaborationStatus.SCHEDULED
        
        # Check messages were sent to target agents
        assert bus_client.client.publish.call_count == 2  # One message per target agent
        
        # Parse the published messages
        import json
        calls = bus_client.client.publish.call_args_list
        
        for i, call in enumerate(calls):
            message_data = json.loads(call[0][1])
            assert message_data['type'] == MessageType.COLLABORATION_REQUEST
            assert message_data['source'] == "test_agent"
            assert message_data['target'] == target_agents[i]
            
            payload = message_data['payload']
            assert payload['request_id'] == request_id
            assert payload['session_id'] == session.session_id
            assert payload['topic'] == topic
            assert payload['collaboration_type'] == CollaborationType.SCHEDULED_SESSION.value
            assert payload['scheduled_start'] == scheduled_start.isoformat()
            assert payload['duration_minutes'] == 60
            assert payload['description'] == "Review recent changes"
            assert payload['required_capabilities'] == ["python", "code_review"]
            assert payload['organizer_capabilities'] == ["python", "testing", "collaboration"]
    
    @pytest.mark.asyncio
    async def test_handle_office_hours_announcement(self, bus_client):
        """Test handling office hours announcement from another agent"""
        message = BeastModeMessage(
            type=MessageType.OFFICE_HOURS_ANNOUNCEMENT,
            source="other_agent",
            payload={
                "office_hours": {
                    "pattern": "weekdays",
                    "start_time": "08:00:00",
                    "end_time": "16:00:00",
                    "timezone": "EST",
                    "days_of_week": [0, 1, 2, 3, 4],
                    "description": "Weekday office hours",
                    "capabilities_focus": ["python", "ai"],
                    "max_concurrent_sessions": 3,
                    "session_duration_minutes": 30
                },
                "announcement": "Agent other_agent office hours: weekdays 08:00:00-16:00:00"
            }
        )
        
        await bus_client._handle_office_hours_announcement(message)
        
        # Check office hours were stored
        office_hours = bus_client.collaboration_scheduler.get_office_hours("other_agent")
        assert office_hours is not None
        assert office_hours.agent_id == "other_agent"
        assert office_hours.pattern == OfficeHoursPattern.WEEKDAYS
        assert office_hours.start_time == time(8, 0)
        assert office_hours.end_time == time(16, 0)
        assert office_hours.timezone == "EST"
        assert office_hours.days_of_week == {0, 1, 2, 3, 4}
        assert office_hours.description == "Weekday office hours"
        assert office_hours.capabilities_focus == ["python", "ai"]
        assert office_hours.max_concurrent_sessions == 3
        assert office_hours.session_duration_minutes == 30
    
    @pytest.mark.asyncio
    async def test_handle_collaboration_request(self, bus_client):
        """Test handling collaboration request from another agent"""
        # Set up office hours to be available
        bus_client.collaboration_scheduler.set_office_hours(
            pattern=OfficeHoursPattern.DAILY,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        # Use a time within office hours for the request
        message = BeastModeMessage(
            type=MessageType.COLLABORATION_REQUEST,
            source="requesting_agent",
            payload={
                "request_id": "req123",
                "session_id": "session123",
                "topic": "Help with testing",
                "collaboration_type": "ad_hoc",
                "scheduled_start": None,  # Immediate collaboration
                "duration_minutes": 30,
                "description": "Need help with unit tests",
                "required_capabilities": ["python", "testing"],
                "organizer_capabilities": ["python", "debugging"]
            }
        )
        
        # Mock the availability check to return True
        with patch.object(bus_client.collaboration_scheduler, 'is_agent_available', return_value=True):
            await bus_client._handle_collaboration_request(message)
        
        # Check response was sent
        bus_client.client.publish.assert_called_once()
        call_args = bus_client.client.publish.call_args
        
        import json
        response_data = json.loads(call_args[0][1])
        assert response_data['type'] == MessageType.COLLABORATION_RESPONSE
        assert response_data['source'] == "test_agent"
        assert response_data['target'] == "requesting_agent"
        assert response_data['correlation_id'] == message.id
        
        payload = response_data['payload']
        assert payload['request_id'] == "req123"
        assert payload['available'] is True
        
        agent_capabilities = payload['agent_capabilities']
        assert agent_capabilities['agent_id'] == "test_agent"
        assert agent_capabilities['capabilities'] == ["python", "testing", "collaboration"]
        assert agent_capabilities['availability'] == "ready_for_business"
    
    @pytest.mark.asyncio
    async def test_handle_collaboration_request_unavailable(self, bus_client):
        """Test handling collaboration request when unavailable"""
        # Don't set office hours, so agent is unavailable
        
        message = BeastModeMessage(
            type=MessageType.COLLABORATION_REQUEST,
            source="requesting_agent",
            payload={
                "request_id": "req123",
                "session_id": "session123",
                "topic": "Help with testing",
                "collaboration_type": "ad_hoc",
                "scheduled_start": "2024-01-01T10:30:00",
                "duration_minutes": 30,
                "description": "Need help with unit tests",
                "required_capabilities": ["python", "testing"],
                "organizer_capabilities": ["python", "debugging"]
            }
        )
        
        await bus_client._handle_collaboration_request(message)
        
        # Check response was sent
        bus_client.client.publish.assert_called_once()
        call_args = bus_client.client.publish.call_args
        
        import json
        response_data = json.loads(call_args[0][1])
        
        payload = response_data['payload']
        assert payload['request_id'] == "req123"
        assert payload['available'] is False
        
        agent_capabilities = payload['agent_capabilities']
        assert agent_capabilities['availability'] == "busy"
    
    @pytest.mark.asyncio
    async def test_handle_collaboration_response(self, bus_client):
        """Test handling collaboration response from another agent"""
        message = BeastModeMessage(
            type=MessageType.COLLABORATION_RESPONSE,
            source="responding_agent",
            payload={
                "request_id": "req123",
                "available": True,
                "agent_capabilities": {
                    "agent_id": "responding_agent",
                    "capabilities": ["python", "testing"],
                    "availability": "ready_for_business"
                }
            }
        )
        
        # Set up callback to capture the event
        callback_called = False
        callback_args = None
        
        def response_callback(agent_id, payload):
            nonlocal callback_called, callback_args
            callback_called = True
            callback_args = (agent_id, payload)
        
        bus_client.collaboration_scheduler.set_collaboration_callback(
            'on_collaboration_response', 
            response_callback
        )
        
        await bus_client._handle_collaboration_response(message)
        
        # Check callback was triggered
        assert callback_called is True
        assert callback_args[0] == "responding_agent"
        assert callback_args[1]['request_id'] == "req123"
        assert callback_args[1]['available'] is True
    
    @pytest.mark.asyncio
    async def test_start_collaboration_session_integration(self, bus_client):
        """Test starting collaboration session with network notification"""
        # Set up office hours for the requesting agent
        bus_client.collaboration_scheduler.set_office_hours(
            pattern=OfficeHoursPattern.DAILY,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        # Create a session
        session = bus_client.collaboration_scheduler.schedule_collaboration(
            participants=["test_agent", "other_agent"],
            topic="Integration test session",
            scheduled_start=datetime(2024, 1, 1, 10, 0),
            duration_minutes=30
        )
        
        assert session is not None
        
        # Reset mock to clear previous calls
        bus_client.client.publish.reset_mock()
        
        # Start the session
        success = await bus_client.start_collaboration_session(session.session_id)
        assert success is True
        
        # Check session status
        updated_session = bus_client.collaboration_scheduler.get_session(session.session_id)
        assert updated_session.status == CollaborationStatus.ACTIVE
        assert updated_session.actual_start is not None
        
        # Check notification was sent to participant
        bus_client.client.publish.assert_called_once()
        call_args = bus_client.client.publish.call_args
        
        import json
        message_data = json.loads(call_args[0][1])
        assert message_data['type'] == MessageType.COLLABORATION_START
        assert message_data['source'] == "test_agent"
        assert message_data['target'] == "other_agent"
        
        payload = message_data['payload']
        assert payload['session_id'] == session.session_id
        assert payload['topic'] == "Integration test session"
        assert payload['organizer'] == "test_agent"
        assert payload['participants'] == ["test_agent", "other_agent"]
        assert 'started_at' in payload
    
    @pytest.mark.asyncio
    async def test_end_collaboration_session_integration(self, bus_client):
        """Test ending collaboration session with network notification"""
        # Set up office hours for the requesting agent
        bus_client.collaboration_scheduler.set_office_hours(
            pattern=OfficeHoursPattern.DAILY,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        # Create and start a session
        session = bus_client.collaboration_scheduler.schedule_collaboration(
            participants=["test_agent", "other_agent"],
            topic="Integration test session",
            scheduled_start=datetime(2024, 1, 1, 10, 0),
            duration_minutes=30
        )
        
        bus_client.collaboration_scheduler.start_collaboration_session(session.session_id)
        
        # Reset mock to clear previous calls
        bus_client.client.publish.reset_mock()
        
        # End the session
        success_metrics = {"outcome": "successful", "knowledge_shared": True}
        success = await bus_client.end_collaboration_session(
            session.session_id,
            success=True,
            success_metrics=success_metrics
        )
        assert success is True
        
        # Check session status
        updated_session = bus_client.collaboration_scheduler.get_session(session.session_id)
        assert updated_session.status == CollaborationStatus.COMPLETED
        assert updated_session.actual_end is not None
        assert updated_session.success_metrics == success_metrics
        
        # Check notification was sent to participant
        bus_client.client.publish.assert_called_once()
        call_args = bus_client.client.publish.call_args
        
        import json
        message_data = json.loads(call_args[0][1])
        assert message_data['type'] == MessageType.COLLABORATION_END
        assert message_data['source'] == "test_agent"
        assert message_data['target'] == "other_agent"
        
        payload = message_data['payload']
        assert payload['session_id'] == session.session_id
        assert payload['success'] is True
        assert payload['success_metrics'] == success_metrics
        assert payload['organizer'] == "test_agent"
        assert 'ended_at' in payload
    
    @pytest.mark.asyncio
    async def test_handle_collaboration_start(self, bus_client):
        """Test handling collaboration start message"""
        message = BeastModeMessage(
            type=MessageType.COLLABORATION_START,
            source="organizer_agent",
            payload={
                "session_id": "session123",
                "topic": "Test collaboration",
                "organizer": "organizer_agent",
                "participants": ["organizer_agent", "test_agent"],
                "started_at": "2024-01-01T10:00:00"
            }
        )
        
        # Set up callback to capture the event
        callback_called = False
        callback_args = None
        
        def start_callback(session_id, payload):
            nonlocal callback_called, callback_args
            callback_called = True
            callback_args = (session_id, payload)
        
        bus_client.collaboration_scheduler.set_collaboration_callback(
            'on_collaboration_start', 
            start_callback
        )
        
        # Create the session first (normally would be created by collaboration request)
        from src.beast_mode.messaging.collaboration_scheduler import CollaborationSession
        session = CollaborationSession(
            session_id="session123",
            organizer_id="organizer_agent",
            participants=["organizer_agent", "test_agent"],
            topic="Test collaboration",
            status=CollaborationStatus.SCHEDULED
        )
        bus_client.collaboration_scheduler.sessions["session123"] = session
        
        await bus_client._handle_collaboration_start(message)
        
        # Check session was started
        updated_session = bus_client.collaboration_scheduler.get_session("session123")
        assert updated_session.status == CollaborationStatus.ACTIVE
        
        # Check callback was triggered
        assert callback_called is True
        assert callback_args[0] == "session123"
        assert callback_args[1]['topic'] == "Test collaboration"
    
    @pytest.mark.asyncio
    async def test_handle_collaboration_end(self, bus_client):
        """Test handling collaboration end message"""
        message = BeastModeMessage(
            type=MessageType.COLLABORATION_END,
            source="organizer_agent",
            payload={
                "session_id": "session123",
                "success": True,
                "success_metrics": {"outcome": "successful"},
                "ended_at": "2024-01-01T11:00:00",
                "organizer": "organizer_agent"
            }
        )
        
        # Set up callback to capture the event
        callback_called = False
        callback_args = None
        
        def end_callback(session_id, success, success_metrics):
            nonlocal callback_called, callback_args
            callback_called = True
            callback_args = (session_id, success, success_metrics)
        
        bus_client.collaboration_scheduler.set_collaboration_callback(
            'on_collaboration_end', 
            end_callback
        )
        
        # Create an active session first
        from src.beast_mode.messaging.collaboration_scheduler import CollaborationSession
        session = CollaborationSession(
            session_id="session123",
            organizer_id="organizer_agent",
            participants=["organizer_agent", "test_agent"],
            topic="Test collaboration",
            status=CollaborationStatus.ACTIVE,
            actual_start=datetime.now()
        )
        bus_client.collaboration_scheduler.sessions["session123"] = session
        bus_client.collaboration_scheduler.active_sessions.add("session123")
        
        await bus_client._handle_collaboration_end(message)
        
        # Check session was ended
        updated_session = bus_client.collaboration_scheduler.get_session("session123")
        assert updated_session.status == CollaborationStatus.COMPLETED
        assert updated_session.success_metrics == {"outcome": "successful"}
        
        # Check callback was triggered
        assert callback_called is True
        assert callback_args[0] == "session123"
        assert callback_args[1] is True
        assert callback_args[2] == {"outcome": "successful"}
    
    @pytest.mark.asyncio
    async def test_collaboration_workflow_end_to_end(self, bus_client):
        """Test complete collaboration workflow"""
        # Agent 1 announces office hours
        await bus_client.announce_office_hours(
            pattern=OfficeHoursPattern.DAILY,
            start_time=time(9, 0),
            end_time=time(17, 0),
            description="Available for collaboration"
        )
        
        # Agent 1 requests collaboration with Agent 2
        request_id = await bus_client.request_collaboration(
            target_agents=["agent2"],
            topic="Code review",
            collaboration_type=CollaborationType.AD_HOC,
            duration_minutes=30,
            description="Review pull request",
            required_capabilities=["python", "code_review"]
        )
        
        # Simulate Agent 2 responding positively
        response_message = BeastModeMessage(
            type=MessageType.COLLABORATION_RESPONSE,
            source="agent2",
            payload={
                "request_id": request_id,
                "available": True,
                "agent_capabilities": {
                    "agent_id": "agent2",
                    "capabilities": ["python", "code_review"],
                    "availability": "ready_for_business"
                }
            }
        )
        
        await bus_client._handle_collaboration_response(response_message)
        
        # Get the created session
        sessions = list(bus_client.collaboration_scheduler.sessions.values())
        assert len(sessions) == 1
        session = sessions[0]
        
        # Start the collaboration session
        success = await bus_client.start_collaboration_session(session.session_id)
        assert success is True
        
        # Simulate some collaboration activity (update session)
        session.collaboration_data['progress'] = 'reviewing code'
        
        # End the collaboration session
        success_metrics = {
            "outcome": "successful",
            "issues_found": 3,
            "improvements_suggested": 5
        }
        success = await bus_client.end_collaboration_session(
            session.session_id,
            success=True,
            success_metrics=success_metrics
        )
        assert success is True
        
        # Verify final session state
        final_session = bus_client.collaboration_scheduler.get_session(session.session_id)
        assert final_session.status == CollaborationStatus.COMPLETED
        assert final_session.success_metrics == success_metrics
        assert final_session.actual_start is not None
        assert final_session.actual_end is not None
        
        # Verify statistics were updated
        stats = bus_client.get_collaboration_stats()
        assert stats['total_sessions'] == 1
        assert stats['successful_sessions'] == 1
        assert stats['average_duration'] > 0
    
    def test_collaboration_availability_checking(self, bus_client):
        """Test collaboration availability checking"""
        # Set office hours
        bus_client.collaboration_scheduler.set_office_hours(
            pattern=OfficeHoursPattern.WEEKDAYS,
            start_time=time(9, 0),
            end_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}  # Monday to Friday
        )
        
        # Test availability during office hours (Wednesday 10 AM)
        wednesday_10am = datetime(2024, 1, 3, 10, 0)  # Wednesday
        available = bus_client.is_agent_available_for_collaboration("test_agent", wednesday_10am)
        assert available is True
        
        # Test availability outside office hours (Wednesday 6 PM)
        wednesday_6pm = datetime(2024, 1, 3, 18, 0)  # Wednesday 6 PM
        available = bus_client.is_agent_available_for_collaboration("test_agent", wednesday_6pm)
        assert available is False
        
        # Test availability on weekend (Saturday 10 AM)
        saturday_10am = datetime(2024, 1, 6, 10, 0)  # Saturday
        available = bus_client.is_agent_available_for_collaboration("test_agent", saturday_10am)
        assert available is False
        
        # Test finding next available slot
        next_slot = bus_client.get_next_available_collaboration_slot("test_agent", 30)
        assert next_slot is not None
    
    def test_collaboration_recommendations(self, bus_client):
        """Test collaboration recommendations"""
        # Create some completed sessions to generate patterns
        from src.beast_mode.messaging.collaboration_scheduler import CollaborationSession
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        
        # Create multiple successful sessions with the same participant
        for i in range(3):
            session = CollaborationSession(
                organizer_id="test_agent",
                participants=["test_agent", "frequent_collaborator"],
                topic=f"Session {i+1}",
                status=CollaborationStatus.COMPLETED,
                actual_start=datetime.now() - timedelta(days=i*7),
                actual_end=datetime.now() - timedelta(days=i*7) + timedelta(minutes=45),
                required_capabilities=["python", "testing"]
            )
            session.success_metrics = {"success": True}
            bus_client.collaboration_scheduler.sessions[session.session_id] = session
        
        # Trigger pattern analysis
        bus_client.collaboration_scheduler._analyze_collaboration_patterns()
        
        # Get recommendations
        recommendations = bus_client.get_collaboration_recommendations()
        
        # Should have recommendations based on the pattern
        assert len(recommendations) > 0
        
        recommendation = recommendations[0]
        assert recommendation['type'] == 'pattern_based'
        assert 'frequent_collaborator' in recommendation['participants']
        assert recommendation['success_probability'] > 0
        assert 'python' in recommendation['capabilities']
        assert 'testing' in recommendation['capabilities']
    
    def test_collaboration_stats_integration(self, bus_client):
        """Test collaboration statistics integration"""
        # Set up office hours for the requesting agent
        bus_client.collaboration_scheduler.set_office_hours(
            pattern=OfficeHoursPattern.DAILY,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        # Initial stats
        stats = bus_client.get_collaboration_stats()
        assert stats['total_sessions'] == 0
        assert stats['successful_sessions'] == 0
        assert stats['active_sessions'] == 0
        
        # Create and complete a session
        session = bus_client.collaboration_scheduler.schedule_collaboration(
            participants=["test_agent", "other_agent"],
            topic="Test session",
            duration_minutes=30
        )
        
        bus_client.collaboration_scheduler.start_collaboration_session(session.session_id)
        bus_client.collaboration_scheduler.end_collaboration_session(
            session.session_id, 
            success=True,
            success_metrics={"outcome": "successful"}
        )
        
        # Check updated stats
        stats = bus_client.get_collaboration_stats()
        assert stats['total_sessions'] == 1
        assert stats['successful_sessions'] == 1
        assert stats['active_sessions'] == 0
        assert stats['average_duration'] > 0
    
    def test_active_collaboration_sessions_display(self, bus_client):
        """Test active collaboration sessions display"""
        # Set up office hours for the requesting agent
        bus_client.collaboration_scheduler.set_office_hours(
            pattern=OfficeHoursPattern.DAILY,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        # Create multiple sessions with different statuses
        session1 = bus_client.collaboration_scheduler.schedule_collaboration(
            participants=["test_agent", "agent1"],
            topic="Active session 1",
            duration_minutes=30
        )
        
        session2 = bus_client.collaboration_scheduler.schedule_collaboration(
            participants=["test_agent", "agent2"],
            topic="Active session 2",
            duration_minutes=45
        )
        
        session3 = bus_client.collaboration_scheduler.schedule_collaboration(
            participants=["test_agent", "agent3"],
            topic="Completed session",
            duration_minutes=60
        )
        
        # Start first two sessions
        bus_client.collaboration_scheduler.start_collaboration_session(session1.session_id)
        bus_client.collaboration_scheduler.start_collaboration_session(session2.session_id)
        
        # Complete third session
        bus_client.collaboration_scheduler.start_collaboration_session(session3.session_id)
        bus_client.collaboration_scheduler.end_collaboration_session(session3.session_id)
        
        # Get active sessions
        active_sessions = bus_client.get_active_collaboration_sessions()
        
        assert len(active_sessions) == 2
        
        # Check session data format
        session_data = active_sessions[0]
        assert 'session_id' in session_data
        assert 'type' in session_data
        assert 'organizer' in session_data
        assert 'participants' in session_data
        assert 'topic' in session_data
        assert 'status' in session_data
        
        # Verify only active sessions are returned
        active_session_ids = {s['session_id'] for s in active_sessions}
        assert session1.session_id in active_session_ids
        assert session2.session_id in active_session_ids

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

        assert session3.session_id not in active_session_ids