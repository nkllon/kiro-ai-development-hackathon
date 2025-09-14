from datetime import datetime
from typing import Dict, List, Any
    def __init__(self, auth_service: DevpostAuthService, base_url: Optional[str]=None, timeout: Optional[float]=None, max_retry_attempts: Optional[int]=None, enable_logging: bool=True):
        Initialize Devpost API client.
        Args:
            auth_service: Authentication service instance
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            max_retry_attempts: Maximum retry attempts for failed requests
            enable_logging: Enable request/response logging
        self.auth_service = auth_service
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retry_attempts = max_retry_attempts or self.MAX_RETRY_ATTEMPTS
        self.enable_logging = enable_logging
        self._session: Optional[aiohttp.ClientSession] = None
        self._session_created_at: Optional[datetime] = None
        self._session_max_age = timedelta(hours=1)
        self._request_timestamps: List[float] = []
        self._burst_timestamps: List[float] = []
        self._request_count = 0
        self._error_count = 0
        self._retry_count = 0
        self._response_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthResult:
        Authenticate with Devpost API using provided credentials.
        Args:
            credentials: Authentication credentials (client_id, client_secret, or api_key)
        Returns:
            AuthResult with authentication status and token information
        try:
            if 'client_id' in credentials:
                self.auth_service.client_id = credentials['client_id']
            if 'client_secret' in credentials:
                self.auth_service.client_secret = credentials['client_secret']
            if 'api_key' in credentials:
                self.auth_service.api_key = credentials['api_key']
            result = await self.auth_service.authenticate()
            if result.success:
                logger.info('API client authenticated successfully')
            else:
                logger.error(f'API client authentication failed: {result.error_message}')
            return result
        except Exception as e:
            logger.error(f'Authentication error: {e}')
            return AuthResult(success=False, error_message=f'Authentication failed: {str(e)}')
    async def get_user_projects(self, hackathon_id: Optional[str]=None, status_filter: Optional[str]=None, limit: Optional[int]=None, offset: Optional[int]=None) -> List[DevpostProject]:
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
        endpoint = '/user/projects'
        params = {}
        if hackathon_id:
            params['hackathon_id'] = hackathon_id
        if status_filter:
            params['status'] = status_filter
        if limit:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        try:
            response_data = await self._make_request('GET', endpoint, params=params)
            projects = []
            project_list = response_data.get('projects', response_data.get('data', []))
            for project_data in project_list:
                try:
                    if not all((field in project_data for field in ['id', 'title'])):
                        logger.warning(f'Project data missing required fields: {project_data}')
                        continue
                    project = DevpostProject.from_dict(project_data)
                    projects.append(project)
                except Exception as e:
                    logger.warning(f'Failed to parse project data: {e}')
                    continue
            logger.info(f'Retrieved {len(projects)} user projects')
            return projects
        except Exception as e:
            logger.error(f'Failed to get user projects: {e}')
            raise
    async def get_project_details(self, project_id: str, include_media: bool=True, include_team: bool=True, include_links: bool=True) -> DevpostProject:
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
        if not project_id or not project_id.strip():
            raise ValidationError('Project ID cannot be empty')
        endpoint = f'/projects/{project_id}'
        params = {}
        if include_media:
            params['include'] = params.get('include', []) + ['media']
        if include_team:
            params['include'] = params.get('include', []) + ['team']
        if include_links:
            params['include'] = params.get('include', []) + ['links']
        if 'include' in params:
            params['include'] = ','.join(params['include'])
        try:
            response_data = await self._make_request('GET', endpoint, params=params)
            project_data = response_data.get('project', response_data)
            project = DevpostProject.from_dict(project_data)
            logger.info(f'Retrieved project details for {project_id}')
            return project
        except Exception as e:
            logger.error(f'Failed to get project details for {project_id}: {e}')
            raise
    async def update_project(self, project_id: str, updates: Dict[str, Any], partial_update: bool=True) -> Dict[str, Any]:
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
        if not project_id or not project_id.strip():
            raise ValidationError('Project ID cannot be empty')
        if not updates:
            raise ValidationError('Updates dictionary cannot be empty')
        endpoint = f'/projects/{project_id}'
        method = 'PATCH' if partial_update else 'PUT'
        try:
            self._validate_project_updates(updates)
            update_payload = {'project': updates, 'partial': partial_update}
            response_data = await self._make_request(method, endpoint, json_data=update_payload)
            success = response_data.get('success', True)
            updated_project = response_data.get('project', response_data.get('data'))
            result = {'success': success, 'project': updated_project, 'updated_fields': list(updates.keys()), 'timestamp': datetime.now().isoformat()}
            if success:
                logger.info(f'Successfully updated project {project_id} fields: {list(updates.keys())}')
            else:
                logger.warning(f'Project update returned success=False for {project_id}')
                result['error'] = response_data.get('error', 'Update failed')
            return result
        except Exception as e:
            logger.error(f'Failed to update project {project_id}: {e}')
            raise
    async def upload_media(self, project_id: str, media_path: Path, media_type: Optional[str]=None, description: Optional[str]=None, is_primary: bool=False, progress_callback: Optional[callable]=None) -> Dict[str, Any]:
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
        if not project_id or not project_id.strip():
            raise ValidationError('Project ID cannot be empty')
        if not media_path.exists():
            raise ValidationError(f'Media file does not exist: {media_path}')
        file_size = media_path.stat().st_size
        if file_size > self.MAX_REQUEST_SIZE:
            raise ValidationError(f'File too large: {file_size} bytes (max: {self.MAX_REQUEST_SIZE})')
        if not self._is_valid_media_file(media_path):
            raise ValidationError(f'Unsupported media file type: {media_path.suffix}')
        endpoint = f'/projects/{project_id}/media'
        try:
            metadata = {'filename': media_path.name, 'size': file_size, 'content_type': self._get_content_type(media_path)}
            if media_type:
                metadata['media_type'] = media_type
            if description:
                metadata['description'] = description
            if is_primary:
                metadata['is_primary'] = is_primary
            if file_size > 10 * 1024 * 1024:
                return await self._upload_large_media(project_id, media_path, metadata, progress_callback)
            with open(media_path, 'rb') as file:
                form_data = aiohttp.FormData()
                form_data.add_field('file', file, filename=media_path.name, content_type=metadata['content_type'])
                for key, value in metadata.items():
                    if key != 'content_type':
                        form_data.add_field(key, str(value))
                response_data = await self._make_request('POST', endpoint, form_data=form_data, timeout=120)
            result = {'success': response_data.get('success', True), 'media_id': response_data.get('media_id'), 'url': response_data.get('url'), 'thumbnail_url': response_data.get('thumbnail_url'), 'file_size': file_size, 'content_type': metadata['content_type'], 'uploaded_at': datetime.now().isoformat()}
            if progress_callback:
                progress_callback(100)
            logger.info(f'Successfully uploaded media {media_path.name} to project {project_id}')
            return result
    # ... (truncated for size compliance)