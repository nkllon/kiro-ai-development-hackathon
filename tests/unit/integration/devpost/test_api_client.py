"""
Unit tests for Devpost API client.

This module contains comprehensive tests for the DevpostAPIClient class,
including HTTP handling, authentication, project management, and media upload
functionality with mocked responses.
"""

import asyncio
import json
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import aiohttp
from aiohttp import ClientResponseError, ClientError

from src.beast_mode.integration.devpost.api.client import DevpostAPIClient
from src.beast_mode.integration.devpost.auth.auth_service import DevpostAuthService
from src.beast_mode.integration.devpost.models import DevpostProject, AuthToken, AuthResult
from src.beast_mode.core.exceptions import NetworkError, AuthenticationError, ValidationError


class TestDevpostAPIClient:
    """Test suite for DevpostAPIClient."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Create mock authentication service."""
        auth_service = Mock(spec=DevpostAuthService)
        auth_service.is_authenticated.return_value = True
        auth_service.get_current_token.return_value = AuthToken(
            access_token="test_token",
            token_type="Bearer",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        return auth_service
    
    @pytest.fixture
    def api_client(self, mock_auth_service):
        """Create API client with mocked auth service."""
        return DevpostAPIClient(
            auth_service=mock_auth_service,
            enable_logging=False  # Disable logging for tests
        )
    
    @pytest.fixture
    def sample_project_data(self):
        """Sample project data for testing."""
        return {
            "id": "test-project-123",
            "title": "Test Project",
            "tagline": "A test project for unit testing",
            "description": "This is a comprehensive test project for validating API functionality",
            "hackathon_id": "hackathon-456",
            "hackathon_name": "Test Hackathon 2025",
            "team_members": [],
            "tags": ["python", "testing", "api"],
            "links": [],
            "media": [],
            "submission_status": "draft",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
    
    @pytest.fixture
    def temp_media_file(self):
        """Create temporary media file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake image data")
            temp_path = Path(f.name)
        
        yield temp_path
        
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    class TestInitialization:
        """Test client initialization."""
        
        def test_client_initialization_default_params(self, mock_auth_service):
            """Test client initialization with default parameters."""
            client = DevpostAPIClient(auth_service=mock_auth_service)
            
            assert client.auth_service == mock_auth_service
            assert client.base_url == DevpostAPIClient.BASE_URL
            assert client.timeout == DevpostAPIClient.DEFAULT_TIMEOUT
            assert client.max_retry_attempts == DevpostAPIClient.MAX_RETRY_ATTEMPTS
            assert client.enable_logging is True
        
        def test_client_initialization_custom_params(self, mock_auth_service):
            """Test client initialization with custom parameters."""
            custom_url = "https://custom.devpost.com/api/v2"
            custom_timeout = 60
            custom_retries = 5
            
            client = DevpostAPIClient(
                auth_service=mock_auth_service,
                base_url=custom_url,
                timeout=custom_timeout,
                max_retry_attempts=custom_retries,
                enable_logging=False
            )
            
            assert client.base_url == custom_url
            assert client.timeout == custom_timeout
            assert client.max_retry_attempts == custom_retries
            assert client.enable_logging is False
    
    class TestAuthentication:
        """Test authentication functionality."""
        
        @pytest.mark.asyncio
        async def test_authenticate_success(self, api_client, mock_auth_service):
            """Test successful authentication."""
            # Setup mock
            auth_result = AuthResult(
                success=True,
                token=AuthToken(access_token="new_token", token_type="Bearer")
            )
            mock_auth_service.authenticate.return_value = auth_result
            
            # Test
            credentials = {"client_id": "test_id", "client_secret": "test_secret"}
            result = await api_client.authenticate(credentials)
            
            # Verify
            assert result.success is True
            assert result.token.access_token == "new_token"
            mock_auth_service.authenticate.assert_called_once()
        
        @pytest.mark.asyncio
        async def test_authenticate_failure(self, api_client, mock_auth_service):
            """Test authentication failure."""
            # Setup mock
            auth_result = AuthResult(
                success=False,
                error_message="Invalid credentials"
            )
            mock_auth_service.authenticate.return_value = auth_result
            
            # Test
            credentials = {"api_key": "invalid_key"}
            result = await api_client.authenticate(credentials)
            
            # Verify
            assert result.success is False
            assert "Invalid credentials" in result.error_message
        
        @pytest.mark.asyncio
        async def test_authenticate_exception(self, api_client, mock_auth_service):
            """Test authentication with exception."""
            # Setup mock
            mock_auth_service.authenticate.side_effect = Exception("Network error")
            
            # Test
            credentials = {"api_key": "test_key"}
            result = await api_client.authenticate(credentials)
            
            # Verify
            assert result.success is False
            assert "Network error" in result.error_message
    
    class TestProjectManagement:
        """Test project management API methods."""
        
        @pytest.mark.asyncio
        async def test_get_user_projects_success(self, api_client, sample_project_data):
            """Test successful retrieval of user projects."""
            # Setup mock response
            mock_response_data = {
                "projects": [sample_project_data]
            }
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response_data
                
                # Test
                projects = await api_client.get_user_projects()
                
                # Verify
                assert len(projects) == 1
                assert projects[0].id == "test-project-123"
                assert projects[0].title == "Test Project"
                mock_request.assert_called_once_with("GET", "/user/projects", params={})
        
        @pytest.mark.asyncio
        async def test_get_user_projects_with_filters(self, api_client, sample_project_data):
            """Test user projects retrieval with filters."""
            mock_response_data = {"projects": [sample_project_data]}
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response_data
                
                # Test with filters
                await api_client.get_user_projects(
                    hackathon_id="hackathon-456",
                    status_filter="draft",
                    limit=10,
                    offset=0
                )
                
                # Verify parameters were passed
                expected_params = {
                    "hackathon_id": "hackathon-456",
                    "status": "draft",
                    "limit": 10,
                    "offset": 0
                }
                mock_request.assert_called_once_with("GET", "/user/projects", params=expected_params)
        
        @pytest.mark.asyncio
        async def test_get_project_details_success(self, api_client, sample_project_data):
            """Test successful project details retrieval."""
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = sample_project_data
                
                # Test
                project = await api_client.get_project_details("test-project-123")
                
                # Verify
                assert project.id == "test-project-123"
                assert project.title == "Test Project"
                mock_request.assert_called_once()
        
        @pytest.mark.asyncio
        async def test_get_project_details_invalid_id(self, api_client):
            """Test project details with invalid ID."""
            with pytest.raises(ValidationError, match="Project ID cannot be empty"):
                await api_client.get_project_details("")
        
        @pytest.mark.asyncio
        async def test_update_project_success(self, api_client):
            """Test successful project update."""
            updates = {"title": "Updated Title", "description": "Updated description"}
            mock_response = {
                "success": True,
                "project": {"id": "test-project-123", **updates}
            }
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                # Test
                result = await api_client.update_project("test-project-123", updates)
                
                # Verify
                assert result["success"] is True
                assert result["updated_fields"] == ["title", "description"]
                mock_request.assert_called_once()
        
        @pytest.mark.asyncio
        async def test_update_project_validation_error(self, api_client):
            """Test project update with validation error."""
            with pytest.raises(ValidationError, match="Project ID cannot be empty"):
                await api_client.update_project("", {"title": "New Title"})
            
            with pytest.raises(ValidationError, match="Updates dictionary cannot be empty"):
                await api_client.update_project("test-project-123", {})
        
        @pytest.mark.asyncio
        async def test_create_project_success(self, api_client, sample_project_data):
            """Test successful project creation."""
            project_data = {
                "title": "New Project",
                "description": "A new test project"
            }
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {"project": sample_project_data}
                
                # Test
                project = await api_client.create_project("hackathon-456", project_data)
                
                # Verify
                assert project.id == "test-project-123"
                assert project.title == "Test Project"
                mock_request.assert_called_once()
        
        @pytest.mark.asyncio
        async def test_delete_project_success(self, api_client):
            """Test successful project deletion."""
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {"success": True}
                
                # Test
                result = await api_client.delete_project("test-project-123")
                
                # Verify
                assert result is True
                mock_request.assert_called_once_with("DELETE", "/projects/test-project-123")
        
        @pytest.mark.asyncio
        async def test_submit_project_success(self, api_client):
            """Test successful project submission."""
            mock_response = {
                "success": True,
                "submission_id": "sub-123",
                "submitted_at": "2025-01-01T12:00:00",
                "status": "submitted"
            }
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                # Test
                result = await api_client.submit_project("test-project-123")
                
                # Verify
                assert result["success"] is True
                assert result["submission_id"] == "sub-123"
                assert result["status"] == "submitted"
                mock_request.assert_called_once_with("POST", "/projects/test-project-123/submit")
    
    class TestMediaHandling:
        """Test media upload and handling functionality."""
        
        @pytest.mark.asyncio
        async def test_upload_media_success(self, api_client, temp_media_file):
            """Test successful media upload."""
            mock_response = {
                "success": True,
                "media_id": "media-123",
                "url": "https://example.com/media.jpg",
                "thumbnail_url": "https://example.com/thumb.jpg"
            }
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                # Test
                result = await api_client.upload_media("test-project-123", temp_media_file)
                
                # Verify
                assert result["success"] is True
                assert result["media_id"] == "media-123"
                assert result["url"] == "https://example.com/media.jpg"
                mock_request.assert_called_once()
        
        @pytest.mark.asyncio
        async def test_upload_media_file_not_exists(self, api_client):
            """Test media upload with non-existent file."""
            non_existent_file = Path("/non/existent/file.jpg")
            
            with pytest.raises(ValidationError, match="Media file does not exist"):
                await api_client.upload_media("test-project-123", non_existent_file)
        
        @pytest.mark.asyncio
        async def test_upload_media_file_too_large(self, api_client):
            """Test media upload with file too large."""
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                # Create a file larger than MAX_REQUEST_SIZE
                large_data = b"x" * (DevpostAPIClient.MAX_REQUEST_SIZE + 1)
                f.write(large_data)
                large_file = Path(f.name)
            
            try:
                with pytest.raises(ValidationError, match="File too large"):
                    await api_client.upload_media("test-project-123", large_file)
            finally:
                large_file.unlink()
        
        @pytest.mark.asyncio
        async def test_delete_media_success(self, api_client):
            """Test successful media deletion."""
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {"success": True}
                
                # Test
                result = await api_client.delete_media("test-project-123", "media-123")
                
                # Verify
                assert result is True
                mock_request.assert_called_once_with("DELETE", "/projects/test-project-123/media/media-123")
        
        @pytest.mark.asyncio
        async def test_get_project_media_success(self, api_client):
            """Test successful project media retrieval."""
            mock_media = [
                {"id": "media-1", "filename": "image1.jpg", "url": "https://example.com/1.jpg"},
                {"id": "media-2", "filename": "image2.png", "url": "https://example.com/2.png"}
            ]
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {"media": mock_media}
                
                # Test
                media_files = await api_client.get_project_media("test-project-123")
                
                # Verify
                assert len(media_files) == 2
                assert media_files[0]["id"] == "media-1"
                assert media_files[1]["filename"] == "image2.png"
                mock_request.assert_called_once_with("GET", "/projects/test-project-123/media")
        
        @pytest.mark.asyncio
        async def test_get_project_media_empty_response(self, api_client):
            """Test project media retrieval with empty response."""
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {"media": []}
                
                # Test
                media_files = await api_client.get_project_media("test-project-123")
                
                # Verify
                assert len(media_files) == 0
        
        @pytest.mark.asyncio
        async def test_get_project_media_alternative_response_format(self, api_client):
            """Test project media retrieval with alternative response format."""
            mock_media = [{"id": "media-1", "filename": "test.jpg"}]
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                # Response with 'data' key instead of 'media'
                mock_request.return_value = {"data": mock_media}
                
                # Test
                media_files = await api_client.get_project_media("test-project-123")
                
                # Verify
                assert len(media_files) == 1
                assert media_files[0]["id"] == "media-1"
        
        @pytest.mark.asyncio
        async def test_get_project_media_invalid_project_id(self, api_client):
            """Test project media retrieval with invalid project ID."""
            with pytest.raises(ValidationError, match="Project ID cannot be empty"):
                await api_client.get_project_media("")
        
        @pytest.mark.asyncio
        async def test_delete_media_success(self, api_client):
            """Test successful media deletion."""
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {"success": True}
                
                # Test
                result = await api_client.delete_media("test-project-123", "media-123")
                
                # Verify
                assert result is True
                mock_request.assert_called_once_with("DELETE", "/projects/test-project-123/media/media-123")
        
        @pytest.mark.asyncio
        async def test_delete_media_failure(self, api_client):
            """Test media deletion failure."""
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {"success": False}
                
                # Test
                result = await api_client.delete_media("test-project-123", "media-123")
                
                # Verify
                assert result is False
        
        @pytest.mark.asyncio
        async def test_delete_media_invalid_ids(self, api_client):
            """Test media deletion with invalid IDs."""
            # Test empty project ID
            with pytest.raises(ValidationError, match="Project ID cannot be empty"):
                await api_client.delete_media("", "media-123")
            
            # Test empty media ID
            with pytest.raises(ValidationError, match="Media ID cannot be empty"):
                await api_client.delete_media("test-project-123", "")
        
        @pytest.mark.asyncio
        async def test_delete_media_network_error(self, api_client):
            """Test media deletion with network error."""
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.side_effect = NetworkError("Connection failed")
                
                # Test
                with pytest.raises(NetworkError, match="Connection failed"):
                    await api_client.delete_media("test-project-123", "media-123")
        
        @pytest.mark.asyncio
        async def test_batch_upload_media_success(self, api_client):
            """Test successful batch media upload."""
            # Create multiple temp files
            temp_files = []
            for i in range(3):
                with tempfile.NamedTemporaryFile(suffix=f".jpg", delete=False) as f:
                    f.write(f"fake image data {i}".encode())
                    temp_files.append(Path(f.name))
            
            try:
                # Mock individual upload calls
                with patch.object(api_client, 'upload_media', new_callable=AsyncMock) as mock_upload:
                    mock_upload.return_value = {
                        "success": True,
                        "media_id": "media-123",
                        "url": "https://example.com/media.jpg"
                    }
                    
                    # Test
                    result = await api_client.batch_upload_media("test-project-123", temp_files)
                    
                    # Verify
                    assert result["total_files"] == 3
                    assert len(result["successful_uploads"]) == 3
                    assert len(result["failed_uploads"]) == 0
                    assert result["success_rate"] == 1.0
                    assert mock_upload.call_count == 3
            
            finally:
                # Cleanup
                for temp_file in temp_files:
                    if temp_file.exists():
                        temp_file.unlink()
        
        @pytest.mark.asyncio
        async def test_batch_upload_media_partial_failure(self, api_client):
            """Test batch media upload with some failures."""
            # Create multiple temp files
            temp_files = []
            for i in range(3):
                with tempfile.NamedTemporaryFile(suffix=f".jpg", delete=False) as f:
                    f.write(f"fake image data {i}".encode())
                    temp_files.append(Path(f.name))
            
            try:
                # Mock upload calls - first succeeds, second fails, third succeeds
                with patch.object(api_client, 'upload_media', new_callable=AsyncMock) as mock_upload:
                    mock_upload.side_effect = [
                        {"success": True, "media_id": "media-1", "url": "https://example.com/1.jpg"},
                        ValidationError("Upload failed"),
                        {"success": True, "media_id": "media-3", "url": "https://example.com/3.jpg"}
                    ]
                    
                    # Test
                    result = await api_client.batch_upload_media("test-project-123", temp_files)
                    
                    # Verify
                    assert result["total_files"] == 3
                    assert len(result["successful_uploads"]) == 2
                    assert len(result["failed_uploads"]) == 1
                    assert result["success_rate"] == 2/3
                    assert mock_upload.call_count == 3
            
            finally:
                # Cleanup
                for temp_file in temp_files:
                    if temp_file.exists():
                        temp_file.unlink()
        
        @pytest.mark.asyncio
        async def test_batch_upload_media_empty_list(self, api_client):
            """Test batch upload with empty file list."""
            with pytest.raises(ValidationError, match="Media files list cannot be empty"):
                await api_client.batch_upload_media("test-project-123", [])
        
        @pytest.mark.asyncio
        async def test_upload_media_with_progress_callback(self, api_client, temp_media_file):
            """Test media upload with progress callback."""
            progress_values = []
            
            def progress_callback(percent):
                progress_values.append(percent)
            
            mock_response = {
                "success": True,
                "media_id": "media-123",
                "url": "https://example.com/media.jpg"
            }
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                # Test
                result = await api_client.upload_media(
                    "test-project-123", 
                    temp_media_file,
                    progress_callback=progress_callback
                )
                
                # Verify
                assert result["success"] is True
                assert 100 in progress_values  # Should report 100% completion
        
        @pytest.mark.asyncio
        async def test_upload_media_large_file_chunked(self, api_client):
            """Test large file upload using chunked upload."""
            # Create a large temp file (>10MB to trigger chunked upload)
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                # Write 11MB of data
                chunk_data = b"x" * (1024 * 1024)  # 1MB chunk
                for _ in range(11):
                    f.write(chunk_data)
                large_file = Path(f.name)
            
            try:
                # Mock the chunked upload method
                with patch.object(api_client, '_upload_large_media', new_callable=AsyncMock) as mock_chunked:
                    mock_chunked.return_value = {
                        "success": True,
                        "media_id": "media-large",
                        "url": "https://example.com/large.mp4",
                        "upload_method": "chunked"
                    }
                    
                    # Test
                    result = await api_client.upload_media("test-project-123", large_file)
                    
                    # Verify chunked upload was used
                    mock_chunked.assert_called_once()
                    assert result["upload_method"] == "chunked"
            
            finally:
                large_file.unlink()
        
        @pytest.mark.asyncio
        async def test_upload_media_invalid_project_id(self, api_client, temp_media_file):
            """Test media upload with invalid project ID."""
            with pytest.raises(ValidationError, match="Project ID cannot be empty"):
                await api_client.upload_media("", temp_media_file)
        
        @pytest.mark.asyncio
        async def test_upload_media_unsupported_file_type(self, api_client):
            """Test media upload with unsupported file type."""
            with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
                f.write(b"fake executable")
                unsupported_file = Path(f.name)
            
            try:
                with pytest.raises(ValidationError, match="Unsupported media file type"):
                    await api_client.upload_media("test-project-123", unsupported_file)
            finally:
                unsupported_file.unlink()
        
        @pytest.mark.asyncio
        async def test_upload_media_with_metadata(self, api_client, temp_media_file):
            """Test media upload with additional metadata."""
            mock_response = {
                "success": True,
                "media_id": "media-123",
                "url": "https://example.com/media.jpg"
            }
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                # Test with metadata
                result = await api_client.upload_media(
                    "test-project-123",
                    temp_media_file,
                    media_type="image",
                    description="Test image description",
                    is_primary=True
                )
                
                # Verify metadata was included in request
                call_args = mock_request.call_args
                form_data = call_args[1]['form_data']
                
                # Check that metadata fields were added to form data
                assert result["success"] is True
                mock_request.assert_called_once()
        
        @pytest.mark.asyncio
        async def test_update_media_metadata_success(self, api_client):
            """Test successful media metadata update."""
            updates = {
                "description": "Updated description",
                "is_primary": True,
                "alt_text": "Updated alt text"
            }
            
            mock_response = {
                "success": True,
                "media": {"id": "media-123", **updates}
            }
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                # Test
                result = await api_client.update_media_metadata("test-project-123", "media-123", updates)
                
                # Verify
                assert result["success"] is True
                assert result["updated_fields"] == list(updates.keys())
                mock_request.assert_called_once_with(
                    "PATCH", 
                    "/projects/test-project-123/media/media-123", 
                    json_data=updates
                )
        
        @pytest.mark.asyncio
        async def test_update_media_metadata_invalid_fields(self, api_client):
            """Test media metadata update with invalid fields."""
            invalid_updates = {
                "filename": "new_name.jpg",  # Not allowed
                "invalid_field": "value"
            }
            
            with pytest.raises(ValidationError, match="Invalid update fields"):
                await api_client.update_media_metadata("test-project-123", "media-123", invalid_updates)
        
        @pytest.mark.asyncio
        async def test_update_media_metadata_empty_updates(self, api_client):
            """Test media metadata update with empty updates."""
            with pytest.raises(ValidationError, match="Updates dictionary cannot be empty"):
                await api_client.update_media_metadata("test-project-123", "media-123", {})
        
        @pytest.mark.asyncio
        async def test_chunked_upload_initialization_failure(self, api_client):
            """Test chunked upload when initialization fails."""
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(b"x" * (15 * 1024 * 1024))  # 15MB file
                large_file = Path(f.name)
            
            try:
                # Mock failed initialization
                with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                    mock_request.return_value = {}  # No upload_id returned
                    
                    with pytest.raises(NetworkError, match="Failed to initialize chunked upload"):
                        await api_client._upload_large_media(
                            "test-project-123",
                            large_file,
                            {"size": large_file.stat().st_size, "content_type": "video/mp4"}
                        )
            finally:
                large_file.unlink()
        
        @pytest.mark.asyncio
        async def test_chunked_upload_with_progress(self, api_client):
            """Test chunked upload with progress tracking."""
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(b"x" * (12 * 1024 * 1024))  # 12MB file
                large_file = Path(f.name)
            
            progress_values = []
            
            def progress_callback(percent):
                progress_values.append(percent)
            
            try:
                # Mock successful chunked upload
                with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                    # Mock responses for init, chunks, and complete
                    mock_request.side_effect = [
                        {"upload_id": "upload-123"},  # Init response
                        {"etag": "chunk1"},  # Chunk 1
                        {"etag": "chunk2"},  # Chunk 2  
                        {"etag": "chunk3"},  # Chunk 3
                        {  # Complete response
                            "media_id": "media-large",
                            "url": "https://example.com/large.mp4"
                        }
                    ]
                    
                    metadata = {
                        "size": large_file.stat().st_size,
                        "content_type": "video/mp4"
                    }
                    
                    result = await api_client._upload_large_media(
                        "test-project-123",
                        large_file,
                        metadata,
                        progress_callback
                    )
                    
                    # Verify
                    assert result["success"] is True
                    assert result["upload_method"] == "chunked"
                    assert len(progress_values) > 0  # Progress was reported
                    assert max(progress_values) <= 100  # Progress doesn't exceed 100%
            
            finally:
                large_file.unlink()
        
        @pytest.mark.asyncio
        async def test_chunked_upload_abort_on_error(self, api_client):
            """Test chunked upload abort when chunk upload fails."""
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(b"x" * (12 * 1024 * 1024))  # 12MB file
                large_file = Path(f.name)
            
            try:
                with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                    # Mock init success, then chunk failure
                    mock_request.side_effect = [
                        {"upload_id": "upload-123"},  # Init success
                        NetworkError("Chunk upload failed"),  # First chunk fails
                        {"success": True}  # Abort call
                    ]
                    
                    metadata = {
                        "size": large_file.stat().st_size,
                        "content_type": "video/mp4"
                    }
                    
                    with pytest.raises(NetworkError, match="Chunk upload failed"):
                        await api_client._upload_large_media(
                            "test-project-123",
                            large_file,
                            metadata
                        )
                    
                    # Verify abort was called
                    assert mock_request.call_count == 3  # init, chunk, abort
                    abort_call = mock_request.call_args_list[2]
                    assert "abort" in abort_call[0][1]  # abort endpoint called
            
            finally:
                large_file.unlink()
        
        def test_is_valid_media_file(self, api_client):
            """Test media file validation."""
            # Valid files
            assert api_client._is_valid_media_file(Path("test.jpg")) is True
            assert api_client._is_valid_media_file(Path("test.png")) is True
            assert api_client._is_valid_media_file(Path("test.mp4")) is True
            assert api_client._is_valid_media_file(Path("test.pdf")) is True
            
            # Invalid files
            assert api_client._is_valid_media_file(Path("test.exe")) is False
            assert api_client._is_valid_media_file(Path("test.bat")) is False
        
        def test_validate_media_file(self, api_client, temp_media_file):
            """Test comprehensive media file validation."""
            result = api_client._validate_media_file(temp_media_file)
            
            assert result["valid"] is True
            assert result["filename"] == temp_media_file.name
            assert result["size"] > 0
            assert result["content_type"] == "image/jpeg"
            assert result["media_type"] == "image"
        
        def test_validate_media_file_not_exists(self, api_client):
            """Test media file validation for non-existent file."""
            result = api_client._validate_media_file(Path("/non/existent/file.jpg"))
            
            assert result["valid"] is False
            assert "does not exist" in result["error"]
        
        def test_validate_media_file_unsupported_type(self, api_client):
            """Test media file validation for unsupported file type."""
            with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
                f.write(b"fake executable")
                unsupported_file = Path(f.name)
            
            try:
                result = api_client._validate_media_file(unsupported_file)
                
                assert result["valid"] is False
                assert "Unsupported file type" in result["error"]
            finally:
                unsupported_file.unlink()
        
        def test_validate_media_file_too_large(self, api_client):
            """Test media file validation for file too large."""
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                # Create file larger than MAX_REQUEST_SIZE
                large_data = b"x" * (DevpostAPIClient.MAX_REQUEST_SIZE + 1)
                f.write(large_data)
                large_file = Path(f.name)
            
            try:
                result = api_client._validate_media_file(large_file)
                
                assert result["valid"] is False
                assert "File too large" in result["error"]
            finally:
                large_file.unlink()
        
        def test_validate_media_file_empty_file(self, api_client):
            """Test media file validation for empty file."""
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                # Don't write anything - file will be empty
                empty_file = Path(f.name)
            
            try:
                result = api_client._validate_media_file(empty_file)
                
                assert result["valid"] is False
                assert "File is empty" in result["error"]
            finally:
                empty_file.unlink()
        
        def test_validate_media_file_with_metadata_extraction(self, api_client, temp_media_file):
            """Test media file validation with metadata extraction."""
            result = api_client._validate_media_file(temp_media_file)
            
            assert result["valid"] is True
            assert result["filename"] == temp_media_file.name
            assert result["size"] > 0
            assert result["content_type"] == "image/jpeg"
            assert result["media_type"] == "image"
            assert result["extension"] == ".jpg"
            assert "modified_at" in result
        
        def test_validate_media_file_video_type(self, api_client):
            """Test media file validation for video files."""
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(b"fake video data")
                video_file = Path(f.name)
            
            try:
                result = api_client._validate_media_file(video_file)
                
                assert result["valid"] is True
                assert result["media_type"] == "video"
                assert result["content_type"] == "video/mp4"
            finally:
                video_file.unlink()
        
        def test_validate_media_file_document_type(self, api_client):
            """Test media file validation for document files."""
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(b"fake pdf data")
                doc_file = Path(f.name)
            
            try:
                result = api_client._validate_media_file(doc_file)
                
                assert result["valid"] is True
                assert result["media_type"] == "document"
                assert result["content_type"] == "application/pdf"
            finally:
                doc_file.unlink()
        
        def test_is_valid_media_file_comprehensive(self, api_client):
            """Test comprehensive media file type validation."""
            # Test valid image types
            valid_images = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"]
            for ext in valid_images:
                assert api_client._is_valid_media_file(Path(f"test{ext}")) is True
            
            # Test valid video types
            valid_videos = [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"]
            for ext in valid_videos:
                assert api_client._is_valid_media_file(Path(f"test{ext}")) is True
            
            # Test valid document types
            valid_docs = [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"]
            for ext in valid_docs:
                assert api_client._is_valid_media_file(Path(f"test{ext}")) is True
            
            # Test valid archive types
            valid_archives = [".zip", ".tar", ".gz", ".rar"]
            for ext in valid_archives:
                assert api_client._is_valid_media_file(Path(f"test{ext}")) is True
            
            # Test invalid types
            invalid_types = [".exe", ".bat", ".sh", ".py", ".js", ".unknown"]
            for ext in invalid_types:
                assert api_client._is_valid_media_file(Path(f"test{ext}")) is False
        
        def test_get_content_type_comprehensive(self, api_client):
            """Test comprehensive content type detection."""
            content_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg", 
                ".png": "image/png",
                ".gif": "image/gif",
                ".mp4": "video/mp4",
                ".mov": "video/quicktime",
                ".avi": "video/x-msvideo",
                ".pdf": "application/pdf",
                ".txt": "text/plain",
                ".md": "text/markdown"
            }
            
            for ext, expected_type in content_type_map.items():
                assert api_client._get_content_type(Path(f"test{ext}")) == expected_type
            
            # Test unknown extension
            assert api_client._get_content_type(Path("test.unknown")) == "application/octet-stream"
    
    class TestErrorHandling:
        """Test error handling and retry logic."""
        
        @pytest.mark.asyncio
        async def test_make_request_not_authenticated(self, api_client, mock_auth_service):
            """Test request when not authenticated."""
            mock_auth_service.is_authenticated.return_value = False
            
            with pytest.raises(AuthenticationError, match="Not authenticated"):
                await api_client._make_request("GET", "/test")
        
        @pytest.mark.asyncio
        async def test_make_request_rate_limited(self, api_client):
            """Test request when rate limited."""
            # Fill up rate limit
            api_client._request_timestamps = [time.time()] * api_client.MAX_REQUESTS_PER_WINDOW
            
            with pytest.raises(NetworkError, match="Rate limit exceeded"):
                await api_client._make_request("GET", "/test")
        
        @pytest.mark.asyncio
        async def test_make_request_retry_on_500(self, api_client):
            """Test retry logic on server error."""
            with patch.object(api_client, '_get_session') as mock_get_session:
                # Create mock session
                mock_session = AsyncMock()
                
                # Create mock context manager for successful response
                mock_success_response = AsyncMock()
                mock_success_response.status = 200
                mock_success_response.json = AsyncMock(return_value={"success": True})
                mock_success_response.content_type = 'application/json'
                
                # Create mock context manager that returns the response
                mock_context = AsyncMock()
                mock_context.__aenter__ = AsyncMock(return_value=mock_success_response)
                mock_context.__aexit__ = AsyncMock(return_value=None)
                
                # First two calls fail with 500, third succeeds
                error_response = ClientResponseError(
                    request_info=Mock(),
                    history=[],
                    status=500,
                    message="Internal Server Error"
                )
                
                mock_session.request.side_effect = [
                    error_response,  # First call fails
                    error_response,  # Second call fails
                    mock_context     # Third succeeds
                ]
                
                mock_get_session.return_value = mock_session
                
                # This should eventually succeed after retries
                with patch('asyncio.sleep'):  # Speed up test by mocking sleep
                    result = await api_client._make_request("GET", "/test")
                    assert result == {"success": True}
        
        @pytest.mark.asyncio
        async def test_make_request_auth_error_refresh_token(self, api_client, mock_auth_service):
            """Test token refresh on authentication error."""
            with patch.object(api_client, '_get_session') as mock_get_session:
                mock_session = AsyncMock()
                
                # Create mock context manager for successful response
                mock_success_response = AsyncMock()
                mock_success_response.status = 200
                mock_success_response.json = AsyncMock(return_value={"success": True})
                mock_success_response.content_type = 'application/json'
                
                mock_context = AsyncMock()
                mock_context.__aenter__ = AsyncMock(return_value=mock_success_response)
                mock_context.__aexit__ = AsyncMock(return_value=None)
                
                # First call returns 401, second call succeeds
                auth_error = ClientResponseError(
                    request_info=Mock(),
                    history=[],
                    status=401,
                    message="Unauthorized"
                )
                
                mock_session.request.side_effect = [
                    auth_error,
                    mock_context
                ]
                
                mock_get_session.return_value = mock_session
                
                # Mock token refresh
                mock_auth_service.refresh_token.return_value = AuthToken(
                    access_token="new_token",
                    token_type="Bearer"
                )
                
                # Test
                result = await api_client._make_request("GET", "/test")
                
                # Verify token refresh was called
                mock_auth_service.refresh_token.assert_called_once()
                assert result == {"success": True}
    
    class TestUtilityMethods:
        """Test utility and helper methods."""
        
        def test_get_content_type(self, api_client):
            """Test content type detection."""
            assert api_client._get_content_type(Path("test.jpg")) == "image/jpeg"
            assert api_client._get_content_type(Path("test.png")) == "image/png"
            assert api_client._get_content_type(Path("test.mp4")) == "video/mp4"
            assert api_client._get_content_type(Path("test.pdf")) == "application/pdf"
            assert api_client._get_content_type(Path("test.unknown")) == "application/octet-stream"
        
        def test_calculate_backoff_delay(self, api_client):
            """Test exponential backoff calculation."""
            delay_0 = api_client._calculate_backoff_delay(0)
            delay_1 = api_client._calculate_backoff_delay(1)
            delay_2 = api_client._calculate_backoff_delay(2)
            
            # Delays should increase exponentially (with jitter)
            assert 0 < delay_0 < delay_1 < delay_2
            assert delay_2 <= api_client.MAX_RETRY_DELAY
        
        def test_get_client_stats(self, api_client):
            """Test client statistics."""
            # Simulate some activity
            api_client._request_count = 10
            api_client._error_count = 2
            api_client._retry_count = 1
            
            stats = api_client.get_client_stats()
            
            assert stats["request_count"] == 10
            assert stats["error_count"] == 2
            assert stats["retry_count"] == 1
            assert stats["error_rate"] == 0.2
            assert "cache_size" in stats
            assert "rate_limit_remaining" in stats
        
        @pytest.mark.asyncio
        async def test_health_check_healthy(self, api_client, mock_auth_service):
            """Test health check when system is healthy."""
            mock_auth_service.is_authenticated.return_value = True
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {"status": "ok"}
                
                health = await api_client.health_check()
                
                assert health["status"] == "healthy"
                assert health["authenticated"] is True
                assert health["api_reachable"] is True
                assert health["response_time_ms"] is not None
        
        @pytest.mark.asyncio
        async def test_health_check_not_authenticated(self, api_client, mock_auth_service):
            """Test health check when not authenticated."""
            mock_auth_service.is_authenticated.return_value = False
            
            health = await api_client.health_check()
            
            assert health["status"] == "unhealthy"
            assert health["authenticated"] is False
            assert "Not authenticated" in health["error"]
        
        @pytest.mark.asyncio
        async def test_close_cleanup(self, api_client):
            """Test client cleanup on close."""
            # Add some data to clean up
            api_client._response_cache["test"] = {"data": "test"}
            api_client._request_timestamps = [time.time()]
            
            # Mock session
            mock_session = AsyncMock()
            mock_session.closed = False
            api_client._session = mock_session
            
            await api_client.close()
            
            # Verify cleanup
            mock_session.close.assert_called_once()
            assert len(api_client._response_cache) == 0
            assert len(api_client._request_timestamps) == 0
        
        @pytest.mark.asyncio
        async def test_context_manager(self, api_client):
            """Test async context manager functionality."""
            with patch.object(api_client, 'close', new_callable=AsyncMock) as mock_close:
                async with api_client as client:
                    assert client == api_client
                
                mock_close.assert_called_once()
    
    class TestHTTPMethodWrappers:
        """Test basic HTTP method wrapper functions."""
        
        @pytest.mark.asyncio
        async def test_get_method(self, api_client):
            """Test GET method wrapper."""
            mock_response = {"data": "test"}
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                result = await api_client.get("/test", params={"key": "value"})
                
                assert result == mock_response
                mock_request.assert_called_once_with(
                    "GET", "/test", params={"key": "value"}, headers=None, timeout=None
                )
        
        @pytest.mark.asyncio
        async def test_post_method(self, api_client):
            """Test POST method wrapper."""
            mock_response = {"success": True}
            json_data = {"title": "Test"}
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                result = await api_client.post("/test", json_data=json_data)
                
                assert result == mock_response
                mock_request.assert_called_once_with(
                    "POST", "/test", json_data=json_data, form_data=None,
                    params=None, headers=None, timeout=None
                )
        
        @pytest.mark.asyncio
        async def test_put_method(self, api_client):
            """Test PUT method wrapper."""
            mock_response = {"updated": True}
            json_data = {"title": "Updated"}
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                result = await api_client.put("/test", json_data=json_data)
                
                assert result == mock_response
                mock_request.assert_called_once_with(
                    "PUT", "/test", json_data=json_data, form_data=None,
                    params=None, headers=None, timeout=None
                )
        
        @pytest.mark.asyncio
        async def test_patch_method(self, api_client):
            """Test PATCH method wrapper."""
            mock_response = {"patched": True}
            json_data = {"description": "Updated description"}
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                result = await api_client.patch("/test", json_data=json_data)
                
                assert result == mock_response
                mock_request.assert_called_once_with(
                    "PATCH", "/test", json_data=json_data, form_data=None,
                    params=None, headers=None, timeout=None
                )
        
        @pytest.mark.asyncio
        async def test_delete_method(self, api_client):
            """Test DELETE method wrapper."""
            mock_response = {"deleted": True}
            
            with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                result = await api_client.delete("/test")
                
                assert result == mock_response
                mock_request.assert_called_once_with(
                    "DELETE", "/test", params=None, headers=None, timeout=None
                )


# Integration test helpers
class TestAPIClientIntegration:
    """Integration tests with real-like scenarios."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Create mock authentication service."""
        auth_service = Mock(spec=DevpostAuthService)
        auth_service.is_authenticated.return_value = True
        auth_service.get_current_token.return_value = AuthToken(
            access_token="test_token",
            token_type="Bearer",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        return auth_service
    
    @pytest.fixture
    def api_client(self, mock_auth_service):
        """Create API client with mocked auth service."""
        return DevpostAPIClient(
            auth_service=mock_auth_service,
            enable_logging=False  # Disable logging for tests
        )
    
    @pytest.fixture
    def sample_project_data(self):
        """Sample project data for testing."""
        return {
            "id": "test-project-123",
            "title": "Test Project",
            "tagline": "A test project for unit testing",
            "description": "This is a comprehensive test project for validating API functionality",
            "hackathon_id": "hackathon-456",
            "hackathon_name": "Test Hackathon 2025",
            "team_members": [],
            "tags": ["python", "testing", "api"],
            "links": [],
            "media": [],
            "submission_status": "draft",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
    
    @pytest.mark.asyncio
    async def test_full_project_workflow(self, api_client, sample_project_data):
        """Test complete project workflow from creation to submission."""
        project_data = {
            "title": "Integration Test Project",
            "description": "A project for integration testing"
        }
        
        with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
            # Mock responses for different endpoints
            def mock_request_side_effect(method, endpoint, **kwargs):
                if method == "POST" and "projects" in endpoint:
                    return {"project": sample_project_data}
                elif method == "PUT" and "projects" in endpoint:
                    return {"success": True, "project": sample_project_data}
                elif method == "POST" and "submit" in endpoint:
                    return {"success": True, "submission_id": "sub-123"}
                else:
                    return {"success": True}
            
            mock_request.side_effect = mock_request_side_effect
            
            # Create project
            project = await api_client.create_project("hackathon-456", project_data)
            assert project.id == "test-project-123"
            
            # Update project
            updates = {"description": "Updated description"}
            result = await api_client.update_project(project.id, updates)
            assert result["success"] is True
            
            # Submit project
            submission = await api_client.submit_project(project.id)
            assert submission["success"] is True
            assert submission["submission_id"] == "sub-123"
            
            # Verify all calls were made
            assert mock_request.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__])