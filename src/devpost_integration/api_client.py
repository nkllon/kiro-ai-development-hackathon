"""
DevPost API Client - Production Implementation

Implements real DevPost API integration with proper HTTP handling,
authentication, rate limiting, and error recovery.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlencode

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class DevPostAPIError(Exception):
    """Base exception for DevPost API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class DevPostAuthenticationError(DevPostAPIError):
    """Authentication related errors"""
    pass


class DevPostRateLimitError(DevPostAPIError):
    """Rate limiting errors"""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class DevPostAPIClient:
    """
    Production-ready DevPost API client with comprehensive error handling,
    rate limiting, and authentication support.
    """
    
    BASE_URL = "https://devpost.com/api"
    API_VERSION = "v1"
    
    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        """
        Initialize the DevPost API client.
        
        Args:
            api_key: API key for authentication (if using API key auth)
            access_token: OAuth access token (if using OAuth auth)
        """
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = f"{self.BASE_URL}/{self.API_VERSION}"
        
        # Rate limiting
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = None
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # Session management
        self.session = self._create_session()
        
        # Request tracking
        self.request_count = 0
        self.error_count = 0
        
    def _create_session(self) -> requests.Session:
        """Create a configured requests session with retry logic"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'BeastMode-DevPost-Integration/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        return session
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on available credentials"""
        headers = {}
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        elif self.api_key:
            headers['X-API-Key'] = self.api_key
        else:
            raise DevPostAuthenticationError("No authentication credentials provided")
        
        return headers
    
    def _handle_rate_limiting(self) -> None:
        """Handle rate limiting by waiting if necessary"""
        current_time = time.time()
        
        # Enforce minimum request interval
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        # Check rate limit reset
        if self.rate_limit_reset and current_time < self.rate_limit_reset:
            wait_time = self.rate_limit_reset - current_time
            print(f"⏳ Rate limit reached, waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _update_rate_limit_headers(self, response: requests.Response) -> None:
        """Update rate limiting information from response headers"""
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in response.headers:
            reset_timestamp = int(response.headers['X-RateLimit-Reset'])
            self.rate_limit_reset = reset_timestamp
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an authenticated request to the DevPost API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base URL)
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response object
            
        Raises:
            DevPostAPIError: For API errors
            DevPostRateLimitError: For rate limiting
            DevPostAuthenticationError: For authentication errors
        """
        self._handle_rate_limiting()
        
        # Prepare request
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        headers = self._get_auth_headers()
        headers.update(kwargs.pop('headers', {}))
        
        # Add query parameters for API key if using API key auth
        if self.api_key and not self.access_token:
            params = kwargs.get('params', {})
            params['api_key'] = self.api_key
            kwargs['params'] = params
        
        try:
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=30,
                **kwargs
            )
            
            # Update rate limiting info
            self._update_rate_limit_headers(response)
            self.request_count += 1
            
            # Handle response
            if response.status_code == 401:
                raise DevPostAuthenticationError(
                    "Authentication failed. Please check your credentials.",
                    status_code=response.status_code
                )
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                raise DevPostRateLimitError(
                    "Rate limit exceeded. Please try again later.",
                    retry_after=retry_after
                )
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', f'API error: {response.status_code}')
                except json.JSONDecodeError:
                    error_message = f'API error: {response.status_code}'
                
                raise DevPostAPIError(
                    error_message,
                    status_code=response.status_code,
                    response_data=error_data if 'error_data' in locals() else None
                )
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            raise DevPostAPIError(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request to the API"""
        response = self._make_request('GET', endpoint, **kwargs)
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request to the API"""
        if data:
            kwargs['json'] = data
        response = self._make_request('POST', endpoint, **kwargs)
        return response.json()
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request to the API"""
        if data:
            kwargs['json'] = data
        response = self._make_request('PUT', endpoint, **kwargs)
        return response.json()
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request to the API"""
        response = self._make_request('DELETE', endpoint, **kwargs)
        return response.json()
    
    # Project Management Methods
    
    def get_projects(self, user_id: Optional[str] = None, **params) -> Dict[str, Any]:
        """
        Get projects for a user or all projects.
        
        Args:
            user_id: User ID to get projects for (optional)
            **params: Additional query parameters
            
        Returns:
            Dictionary containing projects data
        """
        endpoint = f"/projects"
        if user_id:
            endpoint = f"/users/{user_id}/projects"
        
        return self.get(endpoint, params=params)
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get a specific project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary containing project data
        """
        return self.get(f"/projects/{project_id}")
    
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            project_data: Project data dictionary
            
        Returns:
            Dictionary containing created project data
        """
        return self.post("/projects", data=project_data)
    
    def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing project.
        
        Args:
            project_id: Project ID
            project_data: Updated project data
            
        Returns:
            Dictionary containing updated project data
        """
        return self.put(f"/projects/{project_id}", data=project_data)
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary containing deletion confirmation
        """
        return self.delete(f"/projects/{project_id}")
    
    # Hackathon Management Methods
    
    def get_hackathons(self, **params) -> Dict[str, Any]:
        """
        Get hackathons.
        
        Args:
            **params: Query parameters (status, featured, etc.)
            
        Returns:
            Dictionary containing hackathons data
        """
        return self.get("/hackathons", params=params)
    
    def get_hackathon(self, hackathon_id: str) -> Dict[str, Any]:
        """
        Get a specific hackathon by ID.
        
        Args:
            hackathon_id: Hackathon ID
            
        Returns:
            Dictionary containing hackathon data
        """
        return self.get(f"/hackathons/{hackathon_id}")
    
    def get_hackathon_projects(self, hackathon_id: str, **params) -> Dict[str, Any]:
        """
        Get projects for a specific hackathon.
        
        Args:
            hackathon_id: Hackathon ID
            **params: Additional query parameters
            
        Returns:
            Dictionary containing projects data
        """
        return self.get(f"/hackathons/{hackathon_id}/projects", params=params)
    
    # User Management Methods
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing user data
        """
        return self.get(f"/users/{user_id}")
    
    def get_current_user(self) -> Dict[str, Any]:
        """
        Get current authenticated user information.
        
        Returns:
            Dictionary containing current user data
        """
        return self.get("/users/me")
    
    # Utility Methods
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limiting information"""
        return {
            "remaining": self.rate_limit_remaining,
            "reset_time": self.rate_limit_reset,
            "request_count": self.request_count,
            "error_count": self.error_count
        }
    
    def test_connection(self) -> bool:
        """
        Test the API connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.get_current_user()
            return True
        except DevPostAPIError:
            return False
    
    def close(self) -> None:
        """Close the session and cleanup resources"""
        if self.session:
            self.session.close()


# Async version for advanced usage
class AsyncDevPostAPIClient:
    """Async version of the DevPost API client"""
    
    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = f"{DevPostAPIClient.BASE_URL}/{DevPostAPIClient.API_VERSION}"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an async request to the API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_auth_headers()
        headers.update(kwargs.pop('headers', {}))
        
        async with self.session.request(method, url, headers=headers, **kwargs) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise DevPostAPIError(f"API error: {response.status} - {error_text}")
            
            return await response.json()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        headers = {}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        elif self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Async GET request"""
        return await self._make_request('GET', endpoint, **kwargs)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Async POST request"""
        if data:
            kwargs['json'] = data
        return await self._make_request('POST', endpoint, **kwargs)