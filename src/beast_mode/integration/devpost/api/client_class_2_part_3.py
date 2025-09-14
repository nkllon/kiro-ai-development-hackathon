from src.rm_ddd.core.registry import register_module

    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """
    HTTP client for Devpost API with comprehensive error handling and retry logic.
    
    Provides session management, rate limiting, request/response logging,
    and automatic retry mechanisms with exponential backoff for robust
    API interactions.
    """
    BASE_URL = 'https://devpost.com/api/v2'
    API_VERSION = 'v2'
    DEFAULT_TIMEOUT = 30
    MAX_REQUEST_SIZE = 50 * 1024 * 1024
    MAX_RETRY_ATTEMPTS = 3
    BASE_RETRY_DELAY = 1.0
    MAX_RETRY_DELAY = 60.0
    RETRY_MULTIPLIER = 2.0
    JITTER_RANGE = 0.1
    RATE_LIMIT_WINDOW = 60
    MAX_REQUESTS_PER_WINDOW = 100
    BURST_LIMIT = 10
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
    AUTH_ERROR_STATUS_CODES = {401, 403}
