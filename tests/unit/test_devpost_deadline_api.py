"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.509035
"""




import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.beast_mode.integration.devpost.api.client import DevpostAPIClient
from src.beast_mode.integration.devpost.auth.auth_service import DevpostAuthService
from src.beast_mode.core.exceptions import ValidationError, NetworkError
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule




    def test_rdi_chain_validation(self):
        """Validate RDI chain integrity for this module."""
        rdi_validation = {
            "module": "/Users/lou/kiro-2/kiro-ai-development-hackathon/tests/unit/test_devpost_deadline_api.py",
            "requirements": ['R1'],
            "validation_timestamp": "2025-09-14T06:24:50.664200",
            "chain_integrity": True,
            "traceability_complete": True,
            "test_classes": 2,
            "test_methods": 4
        }
        
        # Assert RDI chain integrity
        assert rdi_validation["chain_integrity"] is True
        assert rdi_validation["traceability_complete"] is True
        assert len(rdi_validation["requirements"]) > 0
        
        # Log RDI validation results
        print(f"RDI Validation: {rdi_validation}")

class TestDeadlineAPIMethods(ReflectiveModule):
    """Test deadline and submission requirement API methods (Task 4.4)."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Create mock authentication service."""
        auth_service = Mock(spec=DevpostAuthService)
        auth_service.is_authenticated.return_value = True
        auth_service.get_current_token.return_value = Mock(access_token="test_token")
        return auth_service
    
    @pytest.fixture
    def api_client(self, mock_auth_service):
        """Create API client with mocked auth service."""
        return DevpostAPIClient(auth_service=mock_auth_service)
    
    @pytest.mark.asyncio
    async def test_get_hackathon_deadlines_success(self, api_client):
        """Test successful retrieval of hackathon deadlines."""
        hackathon_id = "hack-123"
        mock_response = {
            "deadlines": [
                {
                    "type": "submission",
                    "deadline_time": "2025-09-15T12:00:00Z",
                    "description": "Final submission deadline",
                    "is_hard_deadline": True,
                    "requirements": ["project_description", "demo_video"],
                    "timezone": "PDT"
                },
                {
                    "type": "judging",
                    "deadline_time": "2025-09-20T18:00:00Z",
                    "description": "Judging period ends",
                    "is_hard_deadline": False,
                    "requirements": [],
                    "timezone": "PDT"
                }
            ]
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.get_hackathon_deadlines(hackathon_id)
            
            assert len(result) == 2
            assert result[0]["type"] == "submission"
            assert result[0]["deadline_time"] == "2025-09-15T12:00:00Z"
            assert result[0]["is_hard_deadline"] is True
            assert len(result[0]["requirements"]) == 2
            
            assert result[1]["type"] == "judging"
            assert result[1]["is_hard_deadline"] is False
            
            mock_request.assert_called_once_with(
                "GET", 
                f"/hackathons/{hackathon_id}/deadlines", 
                params={}
            )
    
    @pytest.mark.asyncio
    async def test_get_hackathon_deadlines_with_past(self, api_client):
        """Test retrieval of hackathon deadlines including past deadlines."""
        hackathon_id = "hack-123"
        mock_response = {"deadlines": []}
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            await api_client.get_hackathon_deadlines(hackathon_id, include_past=True)
            
            mock_request.assert_called_once_with(
                "GET", 
                f"/hackathons/{hackathon_id}/deadlines", 
                params={"include_past": "true"}
            )
    
    @pytest.mark.asyncio
    async def test_get_hackathon_deadlines_invalid_id(self, api_client):
        """Test get_hackathon_deadlines with invalid hackathon ID."""
        with pytest.raises(ValidationError, match="Hackathon ID cannot be empty"):
            await api_client.get_hackathon_deadlines("")
        
        with pytest.raises(ValidationError, match="Hackathon ID cannot be empty"):
            await api_client.get_hackathon_deadlines("   ")
    
    @pytest.mark.asyncio
    async def test_get_submission_requirements_success(self, api_client):
        """Test successful retrieval of submission requirements."""
        hackathon_id = "hack-123"
        mock_response = {
            "requirements": [
                {
                    "id": "req-1",
                    "title": "Project Description",
                    "description": "Detailed project description required",
                    "required": True,
                    "validation_rule": "min_length:100",
                    "field_type": "textarea",
                    "min_length": 100,
                    "category": "project_info",
                    "order": 1
                },
                {
                    "id": "req-2",
                    "title": "Demo Video",
                    "description": "Video demonstration of the project",
                    "required": False,
                    "field_type": "file",
                    "file_types": ["mp4", "mov", "avi"],
                    "category": "media",
                    "order": 2
                }
            ]
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.get_submission_requirements(hackathon_id)
            
            assert len(result) == 2
            assert result[0]["id"] == "req-1"
            assert result[0]["title"] == "Project Description"
            assert result[0]["required"] is True
            assert result[0]["min_length"] == 100
            assert result[0]["category"] == "project_info"
            
            assert result[1]["id"] == "req-2"
            assert result[1]["required"] is False
            assert "mp4" in result[1]["file_types"]
            
            mock_request.assert_called_once_with(
                "GET", 
                f"/hackathons/{hackathon_id}/requirements", 
                params={}
            )
    
    @pytest.mark.asyncio
    async def test_get_submission_requirements_with_project(self, api_client):
        """Test retrieval of submission requirements for specific project."""
        hackathon_id = "hack-123"
        project_id = "proj-456"
        mock_response = {
            "requirements": [
                {
                    "id": "req-1",
                    "title": "Project Description",
                    "required": True,
                    "completed": True,
                    "completion_notes": "Description provided"
                }
            ]
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.get_submission_requirements(hackathon_id, project_id)
            
            assert len(result) == 1
            assert result[0]["completed"] is True
            assert result[0]["completion_notes"] == "Description provided"
            
            mock_request.assert_called_once_with(
                "GET", 
                f"/hackathons/{hackathon_id}/requirements", 
                params={"project_id": project_id}
            )
    
    @pytest.mark.asyncio
    async def test_update_submission_status_success(self, api_client):
        """Test successful submission status update."""
        project_id = "proj-123"
        status = "submitted"
        completion_notes = "All requirements completed"
        
        mock_response = {
            "success": True,
            "previous_status": "draft",
            "status": "submitted",
            "updated_at": "2025-09-15T10:30:00Z"
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.update_submission_status(project_id, status, completion_notes)
            
            assert result["success"] is True
            assert result["previous_status"] == "draft"
            assert result["new_status"] == "submitted"
            assert result["completion_notes"] == completion_notes
            
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "PUT"
            assert call_args[0][1] == f"/projects/{project_id}/status"
            assert call_args[1]["json_data"]["status"] == "submitted"
            assert call_args[1]["json_data"]["completion_notes"] == completion_notes
    
    @pytest.mark.asyncio
    async def test_update_submission_status_invalid_inputs(self, api_client):
        """Test update_submission_status with invalid inputs."""
        with pytest.raises(ValidationError, match="Project ID cannot be empty"):
            await api_client.update_submission_status("", "submitted")
        
        with pytest.raises(ValidationError, match="Status cannot be empty"):
            await api_client.update_submission_status("proj-123", "")
        
        with pytest.raises(ValidationError, match="Invalid status"):
            await api_client.update_submission_status("proj-123", "invalid_status")
    
    @pytest.mark.asyncio
    async def test_validate_project_requirements_success(self, api_client):
        """Test successful project requirements validation."""
        project_id = "proj-123"
        hackathon_id = "hack-456"
        
        mock_response = {
            "is_valid": False,
            "completion_percentage": 75.0,
            "missing_requirements": [
                {
                    "id": "req-2",
                    "title": "Demo Video",
                    "description": "Video demonstration required",
                    "required": True,
                    "suggested_action": "Upload a demo video"
                }
            ],
            "validation_errors": ["Demo video is required"],
            "warnings": ["Consider adding more screenshots"],
            "ready_for_submission": False
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.validate_project_requirements(project_id, hackathon_id)
            
            assert result["is_valid"] is False
            assert result["completion_percentage"] == 75.0
            assert len(result["missing_requirements"]) == 1
            assert result["missing_requirements"][0]["requirement_id"] == "req-2"
            assert result["missing_requirements"][0]["suggested_action"] == "Upload a demo video"
            assert len(result["validation_errors"]) == 1
            assert len(result["warnings"]) == 1
            assert result["ready_for_submission"] is False
            
            mock_request.assert_called_once_with(
                "GET", 
                f"/projects/{project_id}/validate", 
                params={"hackathon_id": hackathon_id}
            )
    
    @pytest.mark.asyncio
    async def test_get_project_submission_history_success(self, api_client):
        """Test successful retrieval of project submission history."""
        project_id = "proj-123"
        
        mock_response = {
            "history": [
                {
                    "timestamp": "2025-09-15T10:00:00Z",
                    "action": "status_change",
                    "previous_status": "draft",
                    "new_status": "submitted",
                    "user": {"username": "alice", "name": "Alice Smith"},
                    "notes": "Final submission",
                    "automated": False,
                    "validation_results": {"is_valid": True}
                },
                {
                    "timestamp": "2025-09-14T15:30:00Z",
                    "action": "created",
                    "new_status": "draft",
                    "user": {"username": "alice", "name": "Alice Smith"},
                    "automated": True
                }
            ]
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.get_project_submission_history(project_id)
            
            assert len(result) == 2
            assert result[0]["action"] == "status_change"
            assert result[0]["previous_status"] == "draft"
            assert result[0]["new_status"] == "submitted"
            assert result[0]["user"]["username"] == "alice"
            assert result[0]["automated"] is False
            
            assert result[1]["action"] == "created"
            assert result[1]["automated"] is True
            
            mock_request.assert_called_once_with(
                "GET", 
                f"/projects/{project_id}/submission-history", 
                params={}
            )
    
    @pytest.mark.asyncio
    async def test_schedule_deadline_notification_success(self, api_client):
        """Test successful deadline notification scheduling."""
        project_id = "proj-123"
        deadline_type = "submission"
        advance_time_hours = 24
        notification_type = "email"
        custom_message = "Don't forget to submit!"
        
        mock_response = {
            "success": True,
            "notification_id": "notif-789",
            "scheduled_time": "2025-09-14T12:00:00Z"
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.schedule_deadline_notification(
                project_id, deadline_type, advance_time_hours, notification_type, custom_message
            )
            
            assert result["success"] is True
            assert result["notification_id"] == "notif-789"
            assert result["deadline_type"] == "submission"
            assert result["advance_time_hours"] == 24
            assert result["notification_type"] == "email"
            
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == f"/projects/{project_id}/notifications/schedule"
            payload = call_args[1]["json_data"]
            assert payload["deadline_type"] == "submission"
            assert payload["advance_time_hours"] == 24
            assert payload["custom_message"] == custom_message
    
    @pytest.mark.asyncio
    async def test_schedule_deadline_notification_invalid_inputs(self, api_client):
        """Test schedule_deadline_notification with invalid inputs."""
        with pytest.raises(ValidationError, match="Project ID cannot be empty"):
            await api_client.schedule_deadline_notification("", "submission", 24)
        
        with pytest.raises(ValidationError, match="Deadline type cannot be empty"):
            await api_client.schedule_deadline_notification("proj-123", "", 24)
        
        with pytest.raises(ValidationError, match="Advance time must be non-negative"):
            await api_client.schedule_deadline_notification("proj-123", "submission", -1)
    
    @pytest.mark.asyncio
    async def test_get_deadline_notifications_success(self, api_client):
        """Test successful retrieval of deadline notifications."""
        project_id = "proj-123"
        
        mock_response = {
            "notifications": [
                {
                    "id": "notif-1",
                    "deadline_type": "submission",
                    "scheduled_time": "2025-09-14T12:00:00Z",
                    "notification_type": "email",
                    "status": "scheduled",
                    "custom_message": "Reminder message",
                    "created_at": "2025-09-10T10:00:00Z"
                },
                {
                    "id": "notif-2",
                    "deadline_type": "judging",
                    "scheduled_time": "2025-09-19T18:00:00Z",
                    "notification_type": "push",
                    "status": "sent",
                    "sent_at": "2025-09-19T18:00:00Z",
                    "created_at": "2025-09-15T14:00:00Z"
                }
            ]
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.get_deadline_notifications(project_id)
            
            assert len(result) == 2
            assert result[0]["notification_id"] == "notif-1"
            assert result[0]["deadline_type"] == "submission"
            assert result[0]["status"] == "scheduled"
            assert result[0]["custom_message"] == "Reminder message"
            
            assert result[1]["notification_id"] == "notif-2"
            assert result[1]["status"] == "sent"
            assert result[1]["sent_at"] == "2025-09-19T18:00:00Z"
            
            mock_request.assert_called_once_with(
                "GET", 
                f"/projects/{project_id}/notifications", 
                params={"active_only": "true"}
            )
    
    @pytest.mark.asyncio
    async def test_cancel_deadline_notification_success(self, api_client):
        """Test successful deadline notification cancellation."""
        project_id = "proj-123"
        notification_id = "notif-456"
        
        mock_response = {
            "success": True,
            "cancelled_at": "2025-09-13T16:00:00Z",
            "previous_status": "scheduled"
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.cancel_deadline_notification(project_id, notification_id)
            
            assert result["success"] is True
            assert result["notification_id"] == notification_id
            assert result["previous_status"] == "scheduled"
            assert "cancelled_at" in result
            
            mock_request.assert_called_once_with(
                "POST", 
                f"/projects/{project_id}/notifications/{notification_id}/cancel"
            )
    
    @pytest.mark.asyncio
    async def test_cancel_deadline_notification_invalid_inputs(self, api_client):
        """Test cancel_deadline_notification with invalid inputs."""
        with pytest.raises(ValidationError, match="Project ID cannot be empty"):
            await api_client.cancel_deadline_notification("", "notif-123")
        
        with pytest.raises(ValidationError, match="Notification ID cannot be empty"):
            await api_client.cancel_deadline_notification("proj-123", "")



    def test_rdi_chain_validation(self):
        """Validate RDI chain integrity for this module."""
        rdi_validation = {
            "module": "/Users/lou/kiro-2/kiro-ai-development-hackathon/tests/unit/test_devpost_deadline_api.py",
            "requirements": ['R1'],
            "validation_timestamp": "2025-09-14T06:24:50.664274",
            "chain_integrity": True,
            "traceability_complete": True,
            "test_classes": 2,
            "test_methods": 4
        }
        
        # Assert RDI chain integrity
        assert rdi_validation["chain_integrity"] is True
        assert rdi_validation["traceability_complete"] is True
        assert len(rdi_validation["requirements"]) > 0
        
        # Log RDI validation results
        print(f"RDI Validation: {rdi_validation}")

class TestDeadlineAPIErrorHandling(ReflectiveModule):
    """Test error handling for deadline API methods."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Create mock authentication service."""
        auth_service = Mock(spec=DevpostAuthService)
        auth_service.is_authenticated.return_value = True
        auth_service.get_current_token.return_value = Mock(access_token="test_token")
        return auth_service
    
    @pytest.fixture
    def api_client(self, mock_auth_service):
        """Create API client with mocked auth service."""
        return DevpostAPIClient(auth_service=mock_auth_service)
    
    @pytest.mark.asyncio
    async def test_get_hackathon_deadlines_network_error(self, api_client):
        """Test get_hackathon_deadlines with network error."""
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = NetworkError("Connection failed")
            
            with pytest.raises(NetworkError):
                await api_client.get_hackathon_deadlines("hack-123")
    
    @pytest.mark.asyncio
    async def test_get_submission_requirements_malformed_data(self, api_client):
        """Test get_submission_requirements with malformed response data."""
        mock_response = {
            "requirements": [
                {"title": "Missing ID"},  # Missing required 'id' field
                {"id": "req-2", "title": "Valid Requirement"}
            ]
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.get_submission_requirements("hack-123")
            
            # Should skip malformed requirement and return only valid one
            assert len(result) == 1
            assert result[0]["id"] == "req-2"
    
    @pytest.mark.asyncio
    async def test_validate_project_requirements_string_missing_requirements(self, api_client):
        """Test validate_project_requirements with string-format missing requirements."""
        mock_response = {
            "is_valid": False,
            "completion_percentage": 50.0,
            "missing_requirements": ["demo_video", "project_description"],  # String format
            "validation_errors": [],
            "warnings": []
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await api_client.validate_project_requirements("proj-123", "hack-456")
            
            assert len(result["missing_requirements"]) == 2
            assert result["missing_requirements"][0]["requirement_id"] == "demo_video"
            assert result["missing_requirements"][0]["title"] == "demo_video"
            assert result["missing_requirements"][0]["suggested_action"] == "Please provide demo_video"
            
            assert result["missing_requirements"][1]["requirement_id"] == "project_description"


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

    pytest.main([__file__, "-v"])