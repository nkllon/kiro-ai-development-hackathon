from src.rm_ddd.core.health import ModuleHealth

def get_authentication_status(self) -> Dict[str, Any]:
    """
        Get detailed authentication status.
        
        Returns:
            Dictionary with authentication status information
        """
    status = {'authenticated': self.is_authenticated(), 'method': None, 'expires_at': None, 'scope': None, 'credentials_file': str(self.credentials_file)}
    if self.credentials.access_token:
        status['method'] = 'oauth'
        status['expires_at'] = self.credentials.expires_at.isoformat() if self.credentials.expires_at else None
        status['scope'] = self.credentials.scope
    elif self.credentials.api_key:
        status['method'] = 'api_key'
    return status
