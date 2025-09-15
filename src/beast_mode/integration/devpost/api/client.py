"""
Devpost API client implementation.

This module provides the core HTTP client for interacting with the Devpost API,
including session management, request/response handling, rate limiting, and
comprehensive error handling with retry mechanisms.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime, timedelta
import random

import aiohttp
from aiohttp import ClientTimeout, ClientError, ClientResponseError

from ..interfaces import DevpostAPIClientInterface
from ..models import DevpostProject, AuthResult
from ..auth.auth_service import DevpostAuthService
from ....core.exceptions import NetworkError, AuthenticationError, ValidationError


logger = logging.getLogger(__name__)


class DevpostAPIClient(DevpostAPIClientInterface):
    """
    HTTP client for Devpost API with comprehensive error handling and retry logic.
    
    Provides session management, rate limiting, request/response logging,
    and automatic retry mechanisms with exponential backoff for robust
    API interactions.
    """
    
    # API configuration
    BASE_URL = "https://devpost.com/api/v2"
    API_VERSION = "v2"
    
    # Request configuration
    DEFAULT_TIMEOUT = 30  # seconds
    MAX_REQUEST_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Retry configuration
    MAX_RETRY_ATTEMPTS = 3
    BASE_RETRY_DELAY = 1.0  # seconds
    MAX_RETRY_DELAY = 60.0  # seconds
    RETRY_MULTIPLIER = 2.0
    JITTER_RANGE = 0.1  # 10% jitter
    
    # Rate limiting configuration
    RATE_LIMIT_WINDOW = 60  # seconds
    MAX_REQUESTS_PER_WINDOW = 100  # Conservative limit
    BURST_LIMIT = 10  # Maximum burst requests
    
    # HTTP status codes that should trigger retries
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
    
    # HTTP status codes that indicate authentication issues
    AUTH_ERROR_STATUS_CODES = {401, 403}
    
    def __init__(
        self,
        auth_service: DevpostAuthService,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retry_attempts: Optional[int] = None,
        enable_logging: bool = True
    ):
        """
        Initialize Devpost API client.
        
        Args:
            auth_service: Authentication service instance
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            max_retry_attempts: Maximum retry attempts for failed requests
            enable_logging: Enable request/response logging
        """
        self.auth_service = auth_service
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retry_attempts = max_retry_attempts or self.MAX_RETRY_ATTEMPTS
        self.enable_logging = enable_logging
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._session_created_at: Optional[datetime] = None
        self._session_max_age = timedelta(hours=1)  # Recreate session every hour
        
        # Rate limiting
        self._request_timestamps: List[float] = []
        self._burst_timestamps: List[float] = []
        
        # Request tracking
        self._request_count = 0
        self._error_count = 0
        self._retry_count = 0
        
        # Response caching (simple in-memory cache)
        self._response_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate with Devpost API using provided credentials.
        
        Args:
            credentials: Authentication credentials (client_id, client_secret, or api_key)
            
        Returns:
            AuthResult with authentication status and token information
        """
        try:
            # Update auth service with new credentials
            if "client_id" in credentials:
                self.auth_service.client_id = credentials["client_id"]
            if "client_secret" in credentials:
                self.auth_service.client_secret = credentials["client_secret"]
            if "api_key" in credentials:
                self.auth_service.api_key = credentials["api_key"]
            
            # Perform authentication
            result = await self.auth_service.authenticate()
            
            if result.success:
                logger.info("API client authenticated successfully")
            else:
                logger.error(f"API client authentication failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return AuthResult(
                success=False,
                error_message=f"Authentication failed: {str(e)}"
            )
    
    async def get_user_projects(
        self, 
        hackathon_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[DevpostProject]:
        """
        Retrieve user's hackathon projects from Devpost.
        
        Args:
            hackathon_id: Filter projects by specific hackathon
            status_filter: Filter by submission status (draft, submitted, published)
            limit: Maximum number of projects to return
            offset: Number of projects to skip (for pagination)
        
        Returns:
            List of DevpostProject objects
            
        Raises:
            AuthenticationError: If not authenticated
            NetworkError: If request fails
        """
        endpoint = "/user/projects"
        
        # Build query parameters
        params = {}
        if hackathon_id:
            params["hackathon_id"] = hackathon_id
        if status_filter:
            params["status"] = status_filter
        if limit:
            params["limit"] = limit
        if offset is not None:  # Allow 0 as valid offset
            params["offset"] = offset
        
        try:
            response_data = await self._make_request("GET", endpoint, params=params)
            
            projects = []
            project_list = response_data.get("projects", response_data.get("data", []))
            
            for project_data in project_list:
                try:
                    # Ensure required fields are present
                    if not all(field in project_data for field in ["id", "title"]):
                        logger.warning(f"Project data missing required fields: {project_data}")
                        continue
                    
                    project = DevpostProject.from_dict(project_data)
                    projects.append(project)
                except Exception as e:
                    logger.warning(f"Failed to parse project data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(projects)} user projects")
            return projects
            
        except Exception as e:
            logger.error(f"Failed to get user projects: {e}")
            raise
    
    async def get_project_details(
        self, 
        project_id: str,
        include_media: bool = True,
        include_team: bool = True,
        include_links: bool = True
    ) -> DevpostProject:
        """
        Get detailed information for a specific project.
        
        Args:
            project_id: Unique project identifier
            include_media: Include media files in response
            include_team: Include team member details
            include_links: Include project links
            
        Returns:
            DevpostProject with detailed information
            
        Raises:
            ValidationError: If project_id is invalid
            NetworkError: If request fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        endpoint = f"/projects/{project_id}"
        
        # Build query parameters for detailed data
        params = {}
        if include_media:
            params["include"] = params.get("include", []) + ["media"]
        if include_team:
            params["include"] = params.get("include", []) + ["team"]
        if include_links:
            params["include"] = params.get("include", []) + ["links"]
        
        if "include" in params:
            params["include"] = ",".join(params["include"])
        
        try:
            response_data = await self._make_request("GET", endpoint, params=params)
            
            # Handle different response formats
            project_data = response_data.get("project", response_data)
            
            project = DevpostProject.from_dict(project_data)
            
            logger.info(f"Retrieved project details for {project_id}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to get project details for {project_id}: {e}")
            raise
    
    async def update_project(
        self, 
        project_id: str, 
        updates: Dict[str, Any],
        partial_update: bool = True
    ) -> Dict[str, Any]:
        """
        Update project information on Devpost.
        
        Args:
            project_id: Unique project identifier
            updates: Dictionary of fields to update
            partial_update: If True, only update provided fields; if False, replace entire project
            
        Returns:
            Dictionary with update result and updated project data
            
        Raises:
            ValidationError: If project_id or updates are invalid
            NetworkError: If request fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        if not updates:
            raise ValidationError("Updates dictionary cannot be empty")
        
        endpoint = f"/projects/{project_id}"
        method = "PATCH" if partial_update else "PUT"
        
        try:
            # Validate update data
            self._validate_project_updates(updates)
            
            # Prepare update payload
            update_payload = {
                "project": updates,
                "partial": partial_update
            }
            
            response_data = await self._make_request(method, endpoint, json_data=update_payload)
            
            # Extract success status and updated project
            success = response_data.get("success", True)  # Default to True if not specified
            updated_project = response_data.get("project", response_data.get("data"))
            
            result = {
                "success": success,
                "project": updated_project,
                "updated_fields": list(updates.keys()),
                "timestamp": datetime.now().isoformat()
            }
            
            if success:
                logger.info(f"Successfully updated project {project_id} fields: {list(updates.keys())}")
            else:
                logger.warning(f"Project update returned success=False for {project_id}")
                result["error"] = response_data.get("error", "Update failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            raise
    
    async def upload_media(
        self, 
        project_id: str, 
        media_path: Path,
        media_type: Optional[str] = None,
        description: Optional[str] = None,
        is_primary: bool = False,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Upload media file to project with progress tracking.
        
        Args:
            project_id: Unique project identifier
            media_path: Path to media file
            media_type: Type of media (image, video, document)
            description: Optional description for the media
            is_primary: Whether this should be the primary project image
            progress_callback: Optional callback for upload progress
            
        Returns:
            Dictionary with upload result information
            
        Raises:
            ValidationError: If inputs are invalid
            NetworkError: If upload fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        if not media_path.exists():
            raise ValidationError(f"Media file does not exist: {media_path}")
        
        file_size = media_path.stat().st_size
        if file_size > self.MAX_REQUEST_SIZE:
            raise ValidationError(f"File too large: {file_size} bytes (max: {self.MAX_REQUEST_SIZE})")
        
        # Validate file type
        if not self._is_valid_media_file(media_path):
            raise ValidationError(f"Unsupported media file type: {media_path.suffix}")
        
        endpoint = f"/projects/{project_id}/media"
        
        try:
            # Prepare metadata
            metadata = {
                "filename": media_path.name,
                "size": file_size,
                "content_type": self._get_content_type(media_path)
            }
            
            if media_type:
                metadata["media_type"] = media_type
            if description:
                metadata["description"] = description
            if is_primary:
                metadata["is_primary"] = is_primary
            
            # For large files, use chunked upload
            if file_size > 10 * 1024 * 1024:  # 10MB threshold
                return await self._upload_large_media(
                    project_id, media_path, metadata, progress_callback
                )
            
            # Standard upload for smaller files
            with open(media_path, 'rb') as file:
                form_data = aiohttp.FormData()
                form_data.add_field(
                    'file',
                    file,
                    filename=media_path.name,
                    content_type=metadata["content_type"]
                )
                
                # Add metadata fields
                for key, value in metadata.items():
                    if key != "content_type":  # Already set in file field
                        form_data.add_field(key, str(value))
                
                response_data = await self._make_request(
                    "POST", 
                    endpoint, 
                    form_data=form_data,
                    timeout=120  # Longer timeout for uploads
                )
            
            # Process response
            result = {
                "success": response_data.get("success", True),
                "media_id": response_data.get("media_id"),
                "url": response_data.get("url"),
                "thumbnail_url": response_data.get("thumbnail_url"),
                "file_size": file_size,
                "content_type": metadata["content_type"],
                "uploaded_at": datetime.now().isoformat()
            }
            
            if progress_callback:
                progress_callback(100)  # Complete
            
            logger.info(f"Successfully uploaded media {media_path.name} to project {project_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload media {media_path} to project {project_id}: {e}")
            raise
    
    async def create_project(
        self, 
        hackathon_id: str, 
        project_data: Dict[str, Any],
        auto_submit: bool = False
    ) -> DevpostProject:
        """
        Create a new project submission.
        
        Args:
            hackathon_id: Hackathon identifier
            project_data: Project information
            auto_submit: Automatically submit project after creation
            
        Returns:
            Created DevpostProject
            
        Raises:
            ValidationError: If inputs are invalid
            NetworkError: If creation fails
        """
        if not hackathon_id or not hackathon_id.strip():
            raise ValidationError("Hackathon ID cannot be empty")
        
        if not project_data:
            raise ValidationError("Project data cannot be empty")
        
        endpoint = f"/hackathons/{hackathon_id}/projects"
        
        try:
            # Validate project data
            self._validate_project_data(project_data)
            
            # Prepare creation payload
            creation_payload = {
                "project": project_data,
                "auto_submit": auto_submit
            }
            
            response_data = await self._make_request("POST", endpoint, json_data=creation_payload)
            
            # Handle different response formats
            project_data_response = response_data.get("project", response_data.get("data", response_data))
            project = DevpostProject.from_dict(project_data_response)
            
            logger.info(f"Successfully created project {project.id} for hackathon {hackathon_id}")
            
            if auto_submit:
                logger.info(f"Project {project.id} was automatically submitted")
            
            return project
            
        except Exception as e:
            logger.error(f"Failed to create project for hackathon {hackathon_id}: {e}")
            raise
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete a project submission.
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            True if deletion was successful
            
        Raises:
            ValidationError: If project_id is invalid
            NetworkError: If deletion fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        endpoint = f"/projects/{project_id}"
        
        try:
            response_data = await self._make_request("DELETE", endpoint)
            
            success = response_data.get("success", True)
            if success:
                logger.info(f"Successfully deleted project {project_id}")
            else:
                logger.warning(f"Project deletion returned success=False for {project_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            raise
    
    async def submit_project(self, project_id: str) -> Dict[str, Any]:
        """
        Submit a project for hackathon judging.
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            Dictionary with submission result
            
        Raises:
            ValidationError: If project_id is invalid
            NetworkError: If submission fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        endpoint = f"/projects/{project_id}/submit"
        
        try:
            response_data = await self._make_request("POST", endpoint)
            
            result = {
                "success": response_data.get("success", True),
                "submission_id": response_data.get("submission_id"),
                "submitted_at": response_data.get("submitted_at"),
                "status": response_data.get("status", "submitted")
            }
            
            if result["success"]:
                logger.info(f"Successfully submitted project {project_id}")
            else:
                logger.warning(f"Project submission failed for {project_id}")
                result["error"] = response_data.get("error", "Submission failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to submit project {project_id}: {e}")
            raise
    
    async def withdraw_project(self, project_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Withdraw a submitted project.
        
        Args:
            project_id: Unique project identifier
            reason: Optional reason for withdrawal
            
        Returns:
            Dictionary with withdrawal result
            
        Raises:
            ValidationError: If project_id is invalid
            NetworkError: If withdrawal fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        endpoint = f"/projects/{project_id}/withdraw"
        
        payload = {}
        if reason:
            payload["reason"] = reason
        
        try:
            response_data = await self._make_request("POST", endpoint, json_data=payload)
            
            result = {
                "success": response_data.get("success", True),
                "withdrawn_at": response_data.get("withdrawn_at"),
                "status": response_data.get("status", "withdrawn"),
                "reason": reason
            }
            
            if result["success"]:
                logger.info(f"Successfully withdrew project {project_id}")
            else:
                logger.warning(f"Project withdrawal failed for {project_id}")
                result["error"] = response_data.get("error", "Withdrawal failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to withdraw project {project_id}: {e}")
            raise
    
    async def get_hackathon_details(self, hackathon_id: str) -> Dict[str, Any]:
        """
        Get details about a specific hackathon.
        
        Args:
            hackathon_id: Hackathon identifier
            
        Returns:
            Dictionary with hackathon information
            
        Raises:
            ValidationError: If hackathon_id is invalid
            NetworkError: If request fails
        """
        if not hackathon_id or not hackathon_id.strip():
            raise ValidationError("Hackathon ID cannot be empty")
        
        endpoint = f"/hackathons/{hackathon_id}"
        
        try:
            response_data = await self._make_request("GET", endpoint)
            
            hackathon_data = response_data.get("hackathon", response_data)
            
            logger.info(f"Retrieved hackathon details for {hackathon_id}")
            return hackathon_data
            
        except Exception as e:
            logger.error(f"Failed to get hackathon details for {hackathon_id}: {e}")
            raise
    
    async def get_user_hackathons(
        self, 
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get hackathons the user is participating in or eligible for.
        
        Args:
            status: Filter by hackathon status (active, upcoming, past)
            limit: Maximum number of hackathons to return
            offset: Number of hackathons to skip (for pagination)
            
        Returns:
            List of hackathon dictionaries
            
        Raises:
            NetworkError: If request fails
        """
        endpoint = "/user/hackathons"
        
        params = {}
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        
        try:
            response_data = await self._make_request("GET", endpoint, params=params)
            
            hackathons = response_data.get("hackathons", response_data.get("data", []))
            
            logger.info(f"Retrieved {len(hackathons)} user hackathons")
            return hackathons
            
        except Exception as e:
            logger.error(f"Failed to get user hackathons: {e}")
            raise
    
    async def add_team_member(
        self, 
        project_id: str, 
        username: str,
        role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a team member to a project.
        
        Args:
            project_id: Unique project identifier
            username: Username of team member to add
            role: Optional role for the team member
            
        Returns:
            Dictionary with operation result
            
        Raises:
            ValidationError: If inputs are invalid
            NetworkError: If request fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")
        
        endpoint = f"/projects/{project_id}/team"
        
        payload = {
            "username": username.strip()
        }
        if role:
            payload["role"] = role
        
        try:
            response_data = await self._make_request("POST", endpoint, json_data=payload)
            
            result = {
                "success": response_data.get("success", True),
                "member": response_data.get("member"),
                "team_size": response_data.get("team_size")
            }
            
            if result["success"]:
                logger.info(f"Successfully added team member {username} to project {project_id}")
            else:
                logger.warning(f"Failed to add team member {username} to project {project_id}")
                result["error"] = response_data.get("error", "Failed to add team member")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to add team member {username} to project {project_id}: {e}")
            raise
    
    async def remove_team_member(self, project_id: str, username: str) -> Dict[str, Any]:
        """
        Remove a team member from a project.
        
        Args:
            project_id: Unique project identifier
            username: Username of team member to remove
            
        Returns:
            Dictionary with operation result
            
        Raises:
            ValidationError: If inputs are invalid
            NetworkError: If request fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")
        
        endpoint = f"/projects/{project_id}/team/{username}"
        
        try:
            response_data = await self._make_request("DELETE", endpoint)
            
            result = {
                "success": response_data.get("success", True),
                "removed_member": username,
                "team_size": response_data.get("team_size")
            }
            
            if result["success"]:
                logger.info(f"Successfully removed team member {username} from project {project_id}")
            else:
                logger.warning(f"Failed to remove team member {username} from project {project_id}")
                result["error"] = response_data.get("error", "Failed to remove team member")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to remove team member {username} from project {project_id}: {e}")
            raise
    
    async def _upload_large_media(
        self,
        project_id: str,
        media_path: Path,
        metadata: Dict[str, Any],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Upload large media files using chunked upload.
        
        Args:
            project_id: Unique project identifier
            media_path: Path to media file
            metadata: File metadata
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary with upload result
        """
        chunk_size = 5 * 1024 * 1024  # 5MB chunks
        file_size = metadata["size"]
        
        # Initialize chunked upload
        init_endpoint = f"/projects/{project_id}/media/upload/init"
        init_response = await self._make_request("POST", init_endpoint, json_data=metadata)
        
        upload_id = init_response.get("upload_id")
        if not upload_id:
            raise NetworkError("Failed to initialize chunked upload")
        
        # Upload chunks
        uploaded_chunks = []
        bytes_uploaded = 0
        
        try:
            with open(media_path, 'rb') as file:
                chunk_number = 1
                
                while True:
                    chunk_data = file.read(chunk_size)
                    if not chunk_data:
                        break
                    
                    # Upload chunk
                    chunk_endpoint = f"/projects/{project_id}/media/upload/{upload_id}/chunk/{chunk_number}"
                    
                    form_data = aiohttp.FormData()
                    form_data.add_field(
                        'chunk',
                        chunk_data,
                        filename=f"chunk_{chunk_number}",
                        content_type="application/octet-stream"
                    )
                    
                    chunk_response = await self._make_request(
                        "POST",
                        chunk_endpoint,
                        form_data=form_data,
                        timeout=300  # 5 minute timeout for chunks
                    )
                    
                    uploaded_chunks.append({
                        "chunk_number": chunk_number,
                        "etag": chunk_response.get("etag"),
                        "size": len(chunk_data)
                    })
                    
                    bytes_uploaded += len(chunk_data)
                    
                    # Report progress
                    if progress_callback:
                        progress = int((bytes_uploaded / file_size) * 100)
                        progress_callback(progress)
                    
                    chunk_number += 1
            
            # Complete upload
            complete_endpoint = f"/projects/{project_id}/media/upload/{upload_id}/complete"
            complete_payload = {
                "chunks": uploaded_chunks,
                "total_size": file_size
            }
            
            complete_response = await self._make_request(
                "POST",
                complete_endpoint,
                json_data=complete_payload
            )
            
            return {
                "success": True,
                "media_id": complete_response.get("media_id"),
                "url": complete_response.get("url"),
                "thumbnail_url": complete_response.get("thumbnail_url"),
                "file_size": file_size,
                "content_type": metadata["content_type"],
                "upload_method": "chunked",
                "chunks_uploaded": len(uploaded_chunks),
                "uploaded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Abort upload on error
            try:
                abort_endpoint = f"/projects/{project_id}/media/upload/{upload_id}/abort"
                await self._make_request("POST", abort_endpoint)
            except Exception as abort_error:
                logger.warning(f"Failed to abort upload {upload_id}: {abort_error}")
            
            raise e
    
    async def delete_media(self, project_id: str, media_id: str) -> bool:
        """
        Delete a media file from a project.
        
        Args:
            project_id: Unique project identifier
            media_id: Media file identifier
            
        Returns:
            True if deletion was successful
            
        Raises:
            ValidationError: If inputs are invalid
            NetworkError: If deletion fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        if not media_id or not media_id.strip():
            raise ValidationError("Media ID cannot be empty")
        
        endpoint = f"/projects/{project_id}/media/{media_id}"
        
        try:
            response_data = await self._make_request("DELETE", endpoint)
            
            success = response_data.get("success", True)
            if success:
                logger.info(f"Successfully deleted media {media_id} from project {project_id}")
            else:
                logger.warning(f"Media deletion returned success=False for {media_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete media {media_id} from project {project_id}: {e}")
            raise
    
    async def get_project_media(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all media files for a project.
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            List of media file dictionaries
            
        Raises:
            ValidationError: If project_id is invalid
            NetworkError: If request fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        endpoint = f"/projects/{project_id}/media"
        
        try:
            response_data = await self._make_request("GET", endpoint)
            
            media_files = response_data.get("media", response_data.get("data", []))
            
            logger.info(f"Retrieved {len(media_files)} media files for project {project_id}")
            return media_files
            
        except Exception as e:
            logger.error(f"Failed to get media for project {project_id}: {e}")
            raise
    
    async def update_media_metadata(
        self,
        project_id: str,
        media_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update metadata for a media file.
        
        Args:
            project_id: Unique project identifier
            media_id: Media file identifier
            updates: Dictionary of metadata updates
            
        Returns:
            Dictionary with update result
            
        Raises:
            ValidationError: If inputs are invalid
            NetworkError: If update fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        if not media_id or not media_id.strip():
            raise ValidationError("Media ID cannot be empty")
        
        if not updates:
            raise ValidationError("Updates dictionary cannot be empty")
        
        endpoint = f"/projects/{project_id}/media/{media_id}"
        
        # Validate allowed update fields
        allowed_fields = {"description", "is_primary", "alt_text", "caption"}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValidationError(f"Invalid update fields: {invalid_fields}")
        
        try:
            response_data = await self._make_request("PATCH", endpoint, json_data=updates)
            
            result = {
                "success": response_data.get("success", True),
                "media": response_data.get("media"),
                "updated_fields": list(updates.keys())
            }
            
            if result["success"]:
                logger.info(f"Successfully updated media {media_id} metadata")
            else:
                logger.warning(f"Media metadata update failed for {media_id}")
                result["error"] = response_data.get("error", "Update failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to update media {media_id} metadata: {e}")
            raise
    
    async def batch_upload_media(
        self,
        project_id: str,
        media_files: List[Path],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Upload multiple media files in batch.
        
        Args:
            project_id: Unique project identifier
            media_files: List of media file paths
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary with batch upload results
            
        Raises:
            ValidationError: If inputs are invalid
            NetworkError: If batch upload fails
        """
        if not project_id or not project_id.strip():
            raise ValidationError("Project ID cannot be empty")
        
        if not media_files:
            raise ValidationError("Media files list cannot be empty")
        
        # Validate all files exist
        for media_path in media_files:
            if not media_path.exists():
                raise ValidationError(f"Media file does not exist: {media_path}")
        
        results = {
            "total_files": len(media_files),
            "successful_uploads": [],
            "failed_uploads": [],
            "total_size": 0
        }
        
        try:
            for i, media_path in enumerate(media_files):
                try:
                    # Individual progress callback
                    def file_progress(percent):
                        if progress_callback:
                            overall_progress = ((i * 100) + percent) / len(media_files)
                            progress_callback(int(overall_progress))
                    
                    upload_result = await self.upload_media(
                        project_id,
                        media_path,
                        progress_callback=file_progress
                    )
                    
                    results["successful_uploads"].append({
                        "file": str(media_path),
                        "result": upload_result
                    })
                    results["total_size"] += media_path.stat().st_size
                    
                except Exception as e:
                    logger.warning(f"Failed to upload {media_path}: {e}")
                    results["failed_uploads"].append({
                        "file": str(media_path),
                        "error": str(e)
                    })
            
            results["success_rate"] = len(results["successful_uploads"]) / len(media_files)
            
            logger.info(
                f"Batch upload completed: {len(results['successful_uploads'])}/{len(media_files)} successful"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Batch upload failed: {e}")
            raise
    
    def _is_valid_media_file(self, file_path: Path) -> bool:
        """
        Check if file is a valid media file type.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file type is supported
        """
        valid_extensions = {
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
            # Videos
            '.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv',
            # Documents
            '.pdf', '.doc', '.docx', '.txt', '.md', '.rtf',
            # Archives
            '.zip', '.tar', '.gz', '.rar'
        }
        
        return file_path.suffix.lower() in valid_extensions
    
    def _validate_media_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate media file and extract metadata.
        
        Args:
            file_path: Path to media file
            
        Returns:
            Dictionary with validation result and metadata
        """
        if not file_path.exists():
            return {"valid": False, "error": "File does not exist"}
        
        if not self._is_valid_media_file(file_path):
            return {"valid": False, "error": f"Unsupported file type: {file_path.suffix}"}
        
        file_size = file_path.stat().st_size
        if file_size > self.MAX_REQUEST_SIZE:
            return {
                "valid": False, 
                "error": f"File too large: {file_size} bytes (max: {self.MAX_REQUEST_SIZE})"
            }
        
        if file_size == 0:
            return {"valid": False, "error": "File is empty"}
        
        # Extract basic metadata
        metadata = {
            "valid": True,
            "filename": file_path.name,
            "size": file_size,
            "content_type": self._get_content_type(file_path),
            "extension": file_path.suffix.lower(),
            "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        # Determine media type
        if metadata["extension"] in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}:
            metadata["media_type"] = "image"
        elif metadata["extension"] in {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'}:
            metadata["media_type"] = "video"
        else:
            metadata["media_type"] = "document"
        
        return metadata
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[aiohttp.FormData] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            json_data: JSON data for request body
            form_data: Form data for multipart requests
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout override
            
        Returns:
            Response data as dictionary
            
        Raises:
            AuthenticationError: If authentication fails
            NetworkError: If request fails after retries
            ValidationError: If response validation fails
        """
        url = f"{self.base_url}{endpoint}"
        request_timeout = timeout or self.timeout
        
        # Check authentication
        if not self.auth_service.is_authenticated():
            raise AuthenticationError("Not authenticated with Devpost API")
        
        # Check rate limiting
        if not self._check_rate_limit():
            raise NetworkError("Rate limit exceeded. Please wait before making more requests.")
        
        # Prepare headers
        request_headers = self._get_request_headers()
        if headers:
            request_headers.update(headers)
        
        # Check cache for GET requests
        cache_key = None
        if method == "GET" and not form_data:
            cache_key = self._get_cache_key(url, params)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.debug(f"Returning cached response for {method} {url}")
                return cached_response
        
        # Execute request with retry logic
        last_exception = None
        
        for attempt in range(self.max_retry_attempts):
            try:
                if self.enable_logging:
                    logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                session = await self._get_session()
                
                async with session.request(
                    method=method,
                    url=url,
                    json=json_data,
                    data=form_data,
                    params=params,
                    headers=request_headers,
                    timeout=ClientTimeout(total=request_timeout)
                ) as response:
                    
                    # Track request
                    self._request_count += 1
                    
                    # Handle response
                    response_data = await self._handle_response(response, url, method)
                    
                    # Cache successful GET responses
                    if method == "GET" and cache_key and response.status == 200:
                        self._cache_response(cache_key, response_data)
                    
                    if self.enable_logging:
                        logger.debug(f"Request successful: {method} {url}")
                    
                    return response_data
                    
            except ClientResponseError as e:
                last_exception = e
                
                # Track error
                self._error_count += 1
                
                # Check if we should retry
                if e.status in self.AUTH_ERROR_STATUS_CODES:
                    # Try to refresh token
                    try:
                        await self.auth_service.refresh_token()
                        request_headers = self._get_request_headers()
                        logger.info("Refreshed authentication token, retrying request")
                        continue
                    except Exception as refresh_error:
                        logger.error(f"Token refresh failed: {refresh_error}")
                        raise AuthenticationError(f"Authentication failed: {str(e)}")
                
                elif e.status in self.RETRYABLE_STATUS_CODES:
                    if attempt < self.max_retry_attempts - 1:
                        delay = self._calculate_backoff_delay(attempt)
                        logger.warning(f"Request failed with status {e.status}, retrying in {delay:.2f}s")
                        await asyncio.sleep(delay)
                        self._retry_count += 1
                        continue
                    else:
                        logger.error(f"Request failed after {self.max_retry_attempts} attempts: {e}")
                        raise NetworkError(f"Request failed: {str(e)}")
                
                else:
                    # Non-retryable error
                    logger.error(f"Request failed with non-retryable status {e.status}: {e}")
                    raise NetworkError(f"Request failed: {str(e)}")
                    
            except (ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                self._error_count += 1
                
                if attempt < self.max_retry_attempts - 1:
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(f"Network error, retrying in {delay:.2f}s: {e}")
                    await asyncio.sleep(delay)
                    self._retry_count += 1
                    continue
                else:
                    logger.error(f"Network error after {self.max_retry_attempts} attempts: {e}")
                    raise NetworkError(f"Network error: {str(e)}")
                    
            except Exception as e:
                # Unexpected error, don't retry
                logger.error(f"Unexpected error during request: {e}")
                raise NetworkError(f"Unexpected error: {str(e)}")
        
        # All retries exhausted
        error_msg = f"Request failed after {self.max_retry_attempts} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"
        
        logger.error(error_msg)
        raise NetworkError(error_msg)
    
    async def _handle_response(
        self, 
        response: aiohttp.ClientResponse, 
        url: str, 
        method: str
    ) -> Dict[str, Any]:
        """
        Handle HTTP response and extract data.
        
        Args:
            response: aiohttp response object
            url: Request URL for logging
            method: HTTP method for logging
            
        Returns:
            Response data as dictionary
            
        Raises:
            ClientResponseError: If response indicates error
            ValidationError: If response format is invalid
        """
        # Check status code
        if response.status >= 400:
            error_text = await response.text()
            logger.error(f"{method} {url} failed with status {response.status}: {error_text}")
            raise ClientResponseError(
                request_info=response.request_info,
                history=response.history,
                status=response.status,
                message=error_text
            )
        
        # Parse response
        try:
            if response.content_type == 'application/json':
                response_data = await response.json()
            else:
                # Handle non-JSON responses
                text_data = await response.text()
                response_data = {"data": text_data, "content_type": response.content_type}
            
            if self.enable_logging:
                logger.debug(f"Response received: {method} {url} -> {response.status}")
            
            return response_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from {url}: {e}")
            raise ValidationError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to process response from {url}: {e}")
            raise ValidationError(f"Response processing failed: {str(e)}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create HTTP session with automatic renewal.
        
        Returns:
            aiohttp.ClientSession instance
        """
        now = datetime.now()
        
        # Check if session needs renewal
        if (
            not self._session or 
            self._session.closed or
            (self._session_created_at and now - self._session_created_at > self._session_max_age)
        ):
            # Close existing session
            if self._session and not self._session.closed:
                await self._session.close()
            
            # Create new session
            connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=30,  # Per-host connection limit
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=ClientTimeout(total=self.timeout),
                headers={"User-Agent": f"DevpostIntegration/{self.API_VERSION}"}
            )
            
            self._session_created_at = now
            logger.debug("Created new HTTP session")
        
        return self._session
    
    def _get_request_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests including authentication.
        
        Returns:
            Dictionary with request headers
        """
        headers = {
            "Accept": "application/json",
            "User-Agent": f"DevpostIntegration/{self.API_VERSION}"
        }
        
        # Add authentication headers
        token = self.auth_service.get_current_token()
        if token:
            if token.token_type == "ApiKey":
                headers["Authorization"] = f"ApiKey {token.access_token}"
            else:
                headers["Authorization"] = f"{token.token_type} {token.access_token}"
        
        return headers
    
    def _check_rate_limit(self) -> bool:
        """
        Check if request is within rate limits.
        
        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        
        # Clean old timestamps
        cutoff = now - self.RATE_LIMIT_WINDOW
        self._request_timestamps = [ts for ts in self._request_timestamps if ts > cutoff]
        self._burst_timestamps = [ts for ts in self._burst_timestamps if ts > now - 10]  # 10 second burst window
        
        # Check burst limit
        if len(self._burst_timestamps) >= self.BURST_LIMIT:
            logger.warning("Burst rate limit exceeded")
            return False
        
        # Check window limit
        if len(self._request_timestamps) >= self.MAX_REQUESTS_PER_WINDOW:
            logger.warning("Rate limit exceeded")
            return False
        
        # Add timestamps
        self._request_timestamps.append(now)
        self._burst_timestamps.append(now)
        
        return True
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate delay for exponential backoff with jitter.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = self.BASE_RETRY_DELAY * (self.RETRY_MULTIPLIER ** attempt)
        delay = min(delay, self.MAX_RETRY_DELAY)
        
        # Add jitter
        jitter = delay * self.JITTER_RANGE * (2 * random.random() - 1)
        delay += jitter
        
        return max(0, delay)
    
    def _get_cache_key(self, url: str, params: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for request."""
        key_parts = [url]
        if params:
            sorted_params = sorted(params.items())
            key_parts.append(str(sorted_params))
        return "|".join(key_parts)
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if still valid."""
        if cache_key not in self._response_cache:
            return None
        
        cached_data = self._response_cache[cache_key]
        if time.time() - cached_data["timestamp"] > self._cache_ttl:
            del self._response_cache[cache_key]
            return None
        
        return cached_data["data"]
    
    def _cache_response(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Cache response data."""
        self._response_cache[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }
        
        # Simple cache cleanup - remove oldest entries if cache gets too large
        if len(self._response_cache) > 100:
            oldest_key = min(
                self._response_cache.keys(),
                key=lambda k: self._response_cache[k]["timestamp"]
            )
            del self._response_cache[oldest_key]
    
    def _validate_project_updates(self, updates: Dict[str, Any]) -> None:
        """Validate project update data."""
        allowed_fields = {
            "title", "tagline", "description", "tags", "links", 
            "team_members", "submission_status"
        }
        
        for field in updates.keys():
            if field not in allowed_fields:
                raise ValidationError(f"Invalid update field: {field}")
        
        # Validate specific fields
        if "title" in updates and not updates["title"].strip():
            raise ValidationError("Title cannot be empty")
        
        if "tagline" in updates and len(updates["tagline"]) > 120:
            raise ValidationError("Tagline must be 120 characters or less")
        
        if "description" in updates and len(updates["description"]) > 5000:
            raise ValidationError("Description must be 5000 characters or less")
        
        if "tags" in updates and len(updates["tags"]) > 10:
            raise ValidationError("Maximum 10 tags allowed")
    
    def _validate_project_data(self, project_data: Dict[str, Any]) -> None:
        """Validate project creation data."""
        required_fields = {"title", "description"}
        
        for field in required_fields:
            if field not in project_data:
                raise ValidationError(f"Required field missing: {field}")
            if not project_data[field].strip():
                raise ValidationError(f"Required field cannot be empty: {field}")
        
        # Use the same validation as updates
        self._validate_project_updates(project_data)
    
    def _get_content_type(self, file_path: Path) -> str:
        """Get content type for file upload."""
        suffix = file_path.suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown'
        }
        return content_types.get(suffix, 'application/octet-stream')
    
    def get_client_stats(self) -> Dict[str, Any]:
        """
        Get client statistics for monitoring.
        
        Returns:
            Dictionary with client statistics
        """
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "retry_count": self._retry_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "cache_size": len(self._response_cache),
            "session_age": (
                (datetime.now() - self._session_created_at).total_seconds()
                if self._session_created_at else 0
            ),
            "rate_limit_remaining": max(
                0, 
                self.MAX_REQUESTS_PER_WINDOW - len(self._request_timestamps)
            )
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of API client.
        
        Returns:
            Dictionary with health status
        """
        health_status = {
            "status": "unknown",
            "authenticated": False,
            "api_reachable": False,
            "response_time_ms": None,
            "error": None
        }
        
        try:
            # Check authentication
            health_status["authenticated"] = self.auth_service.is_authenticated()
            
            if not health_status["authenticated"]:
                health_status["status"] = "unhealthy"
                health_status["error"] = "Not authenticated"
                return health_status
            
            # Test API connectivity
            start_time = time.time()
            
            try:
                await self._make_request("GET", "/user/profile")
                response_time = (time.time() - start_time) * 1000
                
                health_status["api_reachable"] = True
                health_status["response_time_ms"] = round(response_time, 2)
                health_status["status"] = "healthy"
                
            except Exception as e:
                health_status["error"] = str(e)
                health_status["status"] = "unhealthy"
            
        except Exception as e:
            health_status["error"] = str(e)
            health_status["status"] = "error"
        
        return health_status
    
    async def close(self) -> None:
        """Close HTTP session and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("HTTP session closed")
        
        # Clear cache
        self._response_cache.clear()
        
        # Reset counters
        self._request_timestamps.clear()
        self._burst_timestamps.clear()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    # Basic HTTP method wrappers for direct API access
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the specified endpoint.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout override
            
        Returns:
            Response data as dictionary
        """
        return await self._make_request("GET", endpoint, params=params, headers=headers, timeout=timeout)
    
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[aiohttp.FormData] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request to the specified endpoint.
        
        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON data for request body
            form_data: Form data for multipart requests
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout override
            
        Returns:
            Response data as dictionary
        """
        return await self._make_request(
            "POST", endpoint, json_data=json_data, form_data=form_data, 
            params=params, headers=headers, timeout=timeout
        )
    
    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[aiohttp.FormData] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Make a PUT request to the specified endpoint.
        
        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON data for request body
            form_data: Form data for multipart requests
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout override
            
        Returns:
            Response data as dictionary
        """
        return await self._make_request(
            "PUT", endpoint, json_data=json_data, form_data=form_data,
            params=params, headers=headers, timeout=timeout
        )
    
    async def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[aiohttp.FormData] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Make a PATCH request to the specified endpoint.
        
        Args:
            endpoint: API endpoint (without base URL)
            json_data: JSON data for request body
            form_data: Form data for multipart requests
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout override
            
        Returns:
            Response data as dictionary
        """
        return await self._make_request(
            "PATCH", endpoint, json_data=json_data, form_data=form_data,
            params=params, headers=headers, timeout=timeout
        )
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Make a DELETE request to the specified endpoint.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout override
            
        Returns:
            Response data as dictionary
        """
        return await self._make_request("DELETE", endpoint, params=params, headers=headers, timeout=timeout)