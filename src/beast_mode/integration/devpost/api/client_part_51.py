from datetime import datetime
from typing import Dict, List, Any

def __init__(self, auth_service: DevpostAuthService, base_url: Optional[str]=None, timeout: Optional[float]=None, max_retry_attempts: Optional[int]=None, enable_logging: bool=True):
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
