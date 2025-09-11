"""
Devpost API Client for hackathon project management.

This module provides a comprehensive API client for interacting with Devpost's
hackathon platform, including project management, media uploads, and deadline tracking.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

from .models import (
    DevpostProject, ProjectMetadata, Deadline, SubmissionRequirement,
    MediaFile, MediaType, TeamMember, ProjectLink
)

logger = logging.getLogger(__name__)


class DevpostAPIError(Exception):
    """Base exception for Devpost API errors."""
    pass


class DevpostAuthenticationError(DevpostAPIError):
    """Authentication-related API errors."""
    pass


class DevpostRateLimitError(DevpostAPIError):
    """Rate limiting errors."""
    pass


class DevpostAPIClient:
    """
    Comprehensive API client for Devpost hackathon platform.
    
    Provides methods for project management, media uploads, deadline tracking,
    and submission requirement validation.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.devpost.com"):
        """
        Initialize the Devpost API client.
        
        Args:
            api_key: Devpost API key for authentication
            base_url: Base URL for Devpost API endpoints
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy and rate limiting."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'Beast-Mode-Devpost-Integration/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        if self.api_key:
            session.headers['Authorization'] = f'Bearer {self.api_key}'
            
        return session
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an authenticated API request with error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response data
            
        Raises:
            DevpostAPIError: For API-related errors
            DevpostAuthenticationError: For authentication failures
            DevpostRateLimitError: For rate limiting
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 401:
                raise DevpostAuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 429:
                raise DevpostRateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                raise DevpostAPIError(f"API request failed: {response.status_code} - {response.text}")
                
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            raise DevpostAPIError(f"Network error: {str(e)}")
    
    def get_user_projects(self) -> List[DevpostProject]:
        """
        Retrieve all hackathon projects for the authenticated user.
        
        Returns:
            List of DevpostProject objects
        """
        try:
            data = self._make_request('GET', '/projects')
            projects = []
            
            for project_data in data.get('projects', []):
                project = DevpostProject(
                    id=project_data.get('id'),
                    title=project_data.get('title', ''),
                    tagline=project_data.get('tagline', ''),
                    description=project_data.get('description', ''),
                    hackathon_id=project_data.get('hackathon_id'),
                    status=project_data.get('status', 'draft'),
                    created_at=project_data.get('created_at'),
                    updated_at=project_data.get('updated_at'),
                    submission_url=project_data.get('submission_url'),
                    repository_url=project_data.get('repository_url'),
                    demo_url=project_data.get('demo_url')
                )
                projects.append(project)
                
            return projects
            
        except Exception as e:
            logger.error(f"Failed to retrieve user projects: {str(e)}")
            return []
    
    def get_project_details(self, project_id: str) -> Optional[DevpostProject]:
        """
        Get detailed information for a specific project.
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            DevpostProject object or None if not found
        """
        try:
            data = self._make_request('GET', f'/projects/{project_id}')
            
            if not data:
                return None
                
            return DevpostProject(
                id=data.get('id'),
                title=data.get('title', ''),
                tagline=data.get('tagline', ''),
                description=data.get('description', ''),
                hackathon_id=data.get('hackathon_id'),
                status=data.get('status', 'draft'),
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at'),
                submission_url=data.get('submission_url'),
                repository_url=data.get('repository_url'),
                demo_url=data.get('demo_url')
            )
            
        except Exception as e:
            logger.error(f"Failed to get project details for {project_id}: {str(e)}")
            return None
    
    def update_project(self, project_id: str, metadata: ProjectMetadata) -> bool:
        """
        Update project metadata on Devpost.
        
        Args:
            project_id: Unique project identifier
            metadata: Updated project metadata
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            update_data = {
                'title': metadata.title,
                'tagline': metadata.tagline,
                'description': metadata.description,
                'repository_url': metadata.repository_url,
                'demo_url': metadata.demo_url
            }
            
            self._make_request('PUT', f'/projects/{project_id}', json=update_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {str(e)}")
            return False
    
    def create_project(self, hackathon_id: str, metadata: ProjectMetadata) -> Optional[str]:
        """
        Create a new project submission.
        
        Args:
            hackathon_id: Target hackathon identifier
            metadata: Project metadata
            
        Returns:
            New project ID if successful, None otherwise
        """
        try:
            create_data = {
                'hackathon_id': hackathon_id,
                'title': metadata.title,
                'tagline': metadata.tagline,
                'description': metadata.description,
                'repository_url': metadata.repository_url,
                'demo_url': metadata.demo_url
            }
            
            response = self._make_request('POST', '/projects', json=create_data)
            return response.get('id')
            
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            return None
    
    def upload_media(self, project_id: str, media_file: MediaFile, 
                    progress_callback: Optional[callable] = None) -> bool:
        """
        Upload media file (image, video, document) to project.
        
        Args:
            project_id: Target project identifier
            media_file: MediaFile object with file data
            progress_callback: Optional callback for upload progress
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            # Simulate file upload with progress tracking
            if progress_callback:
                for i in range(0, 101, 10):
                    progress_callback(i)
                    time.sleep(0.1)  # Simulate upload time
            
            # In a real implementation, this would handle multipart upload
            upload_data = {
                'filename': media_file.filename,
                'media_type': media_file.media_type.value,
                'file_size': media_file.file_size
            }
            
            self._make_request('POST', f'/projects/{project_id}/media', json=upload_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload media to project {project_id}: {str(e)}")
            return False
    
    def get_hackathon_deadlines(self, hackathon_id: str) -> List[Deadline]:
        """
        Retrieve deadline information for a hackathon.
        
        Args:
            hackathon_id: Hackathon identifier
            
        Returns:
            List of Deadline objects
        """
        try:
            data = self._make_request('GET', f'/hackathons/{hackathon_id}/deadlines')
            deadlines = []
            
            for deadline_data in data.get('deadlines', []):
                deadline = Deadline(
                    name=deadline_data.get('name', ''),
                    deadline=deadline_data.get('deadline'),
                    description=deadline_data.get('description', ''),
                    is_final=deadline_data.get('is_final', False)
                )
                deadlines.append(deadline)
                
            return deadlines
            
        except Exception as e:
            logger.error(f"Failed to get deadlines for hackathon {hackathon_id}: {str(e)}")
            return []
    
    def get_submission_requirements(self, hackathon_id: str) -> List[SubmissionRequirement]:
        """
        Get submission requirements for a hackathon.
        
        Args:
            hackathon_id: Hackathon identifier
            
        Returns:
            List of SubmissionRequirement objects
        """
        try:
            data = self._make_request('GET', f'/hackathons/{hackathon_id}/requirements')
            requirements = []
            
            for req_data in data.get('requirements', []):
                requirement = SubmissionRequirement(
                    name=req_data.get('name', ''),
                    description=req_data.get('description', ''),
                    required=req_data.get('required', True),
                    validation_rules=req_data.get('validation_rules', [])
                )
                requirements.append(requirement)
                
            return requirements
            
        except Exception as e:
            logger.error(f"Failed to get requirements for hackathon {hackathon_id}: {str(e)}")
            return []
    
    def update_submission_status(self, project_id: str, status: str) -> bool:
        """
        Update the submission status of a project.
        
        Args:
            project_id: Project identifier
            status: New status (draft, submitted, published)
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            status_data = {'status': status}
            self._make_request('PUT', f'/projects/{project_id}/status', json=status_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update status for project {project_id}: {str(e)}")
            return False
    
    def validate_api_connection(self) -> bool:
        """
        Validate API connection and authentication.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            self._make_request('GET', '/user/profile')
            return True
        except (DevpostAPIError, DevpostAuthenticationError):
            return False
    
    def close(self):
        """Close the API client session."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()