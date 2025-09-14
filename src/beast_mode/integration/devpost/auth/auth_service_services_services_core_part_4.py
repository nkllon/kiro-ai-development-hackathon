
def authenticate_with_api_key(self, api_key: str) -> bool:
    """
        Authenticate using API key.
        
        Args:
            api_key: DevPost API key
            
        Returns:
            True if authentication successful
        """
    try:
        from ..api.client import DevPostAPIClient
        client = DevPostAPIClient(api_key=api_key)
        if client.test_connection():
            self.credentials.api_key = api_key
            self.credentials.access_token = None
            self.credentials.refresh_token = None
            self._save_credentials()
            return True
        else:
            return False
    except Exception as e:
        raise DevPostAuthenticationError(f'API key authentication failed: {e}')
