from src.rm_ddd.core.health import ModuleHealth

def authenticate_with_oauth(self, scopes: Optional[list]=None, redirect_uri: str='http://localhost:8080/callback') -> str:
    """
        Start OAuth 2.0 authentication flow.
        
        Args:
            scopes: List of OAuth scopes to request
            redirect_uri: OAuth redirect URI
            
        Returns:
            Authorization URL for user to visit
        """
    if not self.client_id:
        raise DevPostAuthenticationError('OAuth client ID not configured')
    scopes = scopes or self.DEFAULT_SCOPES
    state = secrets.token_urlsafe(32)
    self._oauth_state = state
    self._redirect_uri = redirect_uri
    params = {'client_id': self.client_id, 'response_type': 'code', 'redirect_uri': redirect_uri, 'scope': ' '.join(scopes), 'state': state}
    auth_url = f'{self.AUTHORIZATION_URL}?{urlencode(params)}'
    return auth_url
