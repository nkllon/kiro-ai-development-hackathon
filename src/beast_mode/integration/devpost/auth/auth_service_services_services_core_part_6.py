from src.rm_ddd.core.health import ModuleHealth

def complete_oauth_flow(self, authorization_code: str, state: str) -> bool:
    """
        Complete OAuth 2.0 flow with authorization code.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            state: State parameter for verification
            
        Returns:
            True if authentication successful
        """
    if not hasattr(self, '_oauth_state') or state != self._oauth_state:
        raise DevPostAuthenticationError('Invalid state parameter')
    if not self.client_secret:
        raise DevPostAuthenticationError('OAuth client secret not configured')
    try:
        token_data = {'grant_type': 'authorization_code', 'client_id': self.client_id, 'client_secret': self.client_secret, 'code': authorization_code, 'redirect_uri': self._redirect_uri}
        response = requests.post(self.TOKEN_URL, data=token_data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=30)
        if response.status_code != 200:
            raise DevPostAuthenticationError(f'Token exchange failed: {response.text}')
        token_response = response.json()
        self.credentials.access_token = token_response['access_token']
        self.credentials.refresh_token = token_response.get('refresh_token')
        self.credentials.token_type = token_response.get('token_type', 'Bearer')
        self.credentials.scope = token_response.get('scope')
        expires_in = token_response.get('expires_in', 3600)
        self.credentials.expires_at = datetime.now() + timedelta(seconds=expires_in)
        delattr(self, '_oauth_state')
        delattr(self, '_redirect_uri')
        self._save_credentials()
        return True
    except requests.RequestException as e:
        raise DevPostAuthenticationError(f'OAuth token exchange failed: {e}')

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

