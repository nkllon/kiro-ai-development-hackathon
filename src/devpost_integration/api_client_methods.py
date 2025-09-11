class DevPostAPIError(Exception):
    """Base exception for DevPost API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(module_id="api_client", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
