from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _validate_media_file(self, file_path: Path) -> Dict[str, Any]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """
        Validate media file and extract metadata.
        
        Args:
            file_path: Path to media file
            
        Returns:
            Dictionary with validation result and metadata
        """
        if not file_path.exists():
            return {'valid': False, 'error': 'File does not exist'}
        if not self._is_valid_media_file(file_path):
            return {'valid': False, 'error': f'Unsupported file type: {file_path.suffix}'}
        file_size = file_path.stat().st_size
        if file_size > self.MAX_REQUEST_SIZE:
            return {'valid': False, 'error': f'File too large: {file_size} bytes (max: {self.MAX_REQUEST_SIZE})'}
        if file_size == 0:
            return {'valid': False, 'error': 'File is empty'}
        metadata = {'valid': True, 'filename': file_path.name, 'size': file_size, 'content_type': self._get_content_type(file_path), 'extension': file_path.suffix.lower(), 'modified_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()}
        if metadata['extension'] in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}:
            metadata['media_type'] = 'image'
        elif metadata['extension'] in {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'}:
            metadata['media_type'] = 'video'
        else:
            metadata['media_type'] = 'document'
        return metadata

    async def _make_request(self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]]=None, form_data: Optional[aiohttp.FormData]=None, params: Optional[Dict[str, Any]]=None, headers: Optional[Dict[str, str]]=None, timeout: Optional[float]=None) -> Dict[str, Any]:
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
        url = f'{self.base_url}{endpoint}'
        request_timeout = timeout or self.timeout
        if not self.auth_service.is_authenticated():
            raise AuthenticationError('Not authenticated with Devpost API')
        if not self._check_rate_limit():
            raise NetworkError('Rate limit exceeded. Please wait before making more requests.')
        request_headers = self._get_request_headers()
        if headers:
            request_headers.update(headers)
        cache_key = None
        if method == 'GET' and (not form_data):
            cache_key = self._get_cache_key(url, params)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.debug(f'Returning cached response for {method} {url}')
                return cached_response
        last_exception = None
        for attempt in range(self.max_retry_attempts):
            try:
                if self.enable_logging:
                    logger.debug(f'Making {method} request to {url} (attempt {attempt + 1})')
                session = await self._get_session()
                async with session.request(method=method, url=url, json=json_data, data=form_data, params=params, headers=request_headers, timeout=ClientTimeout(total=request_timeout)) as response:
                    self._request_count += 1
                    response_data = await self._handle_response(response, url, method)
                    if method == 'GET' and cache_key and (response.status == 200):
                        self._cache_response(cache_key, response_data)
                    if self.enable_logging:
                        logger.debug(f'Request successful: {method} {url}')
                    return response_data
            except ClientResponseError as e:
                last_exception = e
                self._error_count += 1
                if e.status in self.AUTH_ERROR_STATUS_CODES:
                    try:
                        await self.auth_service.refresh_token()
                        request_headers = self._get_request_headers()
                        logger.info('Refreshed authentication token, retrying request')
                        continue
                    except Exception as refresh_error:
                        logger.error(f'Token refresh failed: {refresh_error}')
                        raise AuthenticationError(f'Authentication failed: {str(e)}')
                elif e.status in self.RETRYABLE_STATUS_CODES:
                    if attempt < self.max_retry_attempts - 1:
                        delay = self._calculate_backoff_delay(attempt)
                        logger.warning(f'Request failed with status {e.status}, retrying in {delay:.2f}s')
                        await asyncio.sleep(delay)
                        self._retry_count += 1
                        continue
                    else:
                        logger.error(f'Request failed after {self.max_retry_attempts} attempts: {e}')
                        raise NetworkError(f'Request failed: {str(e)}')
                else:
                    logger.error(f'Request failed with non-retryable status {e.status}: {e}')
                    raise NetworkError(f'Request failed: {str(e)}')
            except (ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                self._error_count += 1
                if attempt < self.max_retry_attempts - 1:
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(f'Network error, retrying in {delay:.2f}s: {e}')
                    await asyncio.sleep(delay)
                    self._retry_count += 1
                    continue
                else:
                    logger.error(f'Network error after {self.max_retry_attempts} attempts: {e}')
                    raise NetworkError(f'Network error: {str(e)}')
            except Exception as e:
                logger.error(f'Unexpected error during request: {e}')
                raise NetworkError(f'Unexpected error: {str(e)}')
        error_msg = f'Request failed after {self.max_retry_attempts} attempts'
        if last_exception:
            error_msg += f': {str(last_exception)}'
        logger.error(error_msg)
        raise NetworkError(error_msg)

    async def _handle_response(self, response: aiohttp.ClientResponse, url: str, method: str) -> Dict[str, Any]:
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
        if response.status >= 400:
            error_text = await response.text()
            logger.error(f'{method} {url} failed with status {response.status}: {error_text}')
            raise ClientResponseError(request_info=response.request_info, history=response.history, status=response.status, message=error_text)
        try:
            if response.content_type == 'application/json':
                response_data = await response.json()
            else:
                text_data = await response.text()
                response_data = {'data': text_data, 'content_type': response.content_type}
            if self.enable_logging:
                logger.debug(f'Response received: {method} {url} -> {response.status}')
            return response_data
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse JSON response from {url}: {e}')
            raise ValidationError(f'Invalid JSON response: {str(e)}')
        except Exception as e:
            logger.error(f'Failed to process response from {url}: {e}')
            raise ValidationError(f'Response processing failed: {str(e)}')

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create HTTP session with automatic renewal.
        
        Returns:
            aiohttp.ClientSession instance
        """
        now = datetime.now()
        if not self._session or self._session.closed or (self._session_created_at and now - self._session_created_at > self._session_max_age):
            if self._session and (not self._session.closed):
                await self._session.close()
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30, ttl_dns_cache=300, use_dns_cache=True, keepalive_timeout=30, enable_cleanup_closed=True)
            self._session = aiohttp.ClientSession(connector=connector, timeout=ClientTimeout(total=self.timeout), headers={'User-Agent': f'DevpostIntegration/{self.API_VERSION}'})
            self._session_created_at = now
            logger.debug('Created new HTTP session')
        return self._session

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

