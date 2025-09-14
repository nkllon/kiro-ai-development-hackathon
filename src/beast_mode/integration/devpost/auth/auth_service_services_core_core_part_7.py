from src.rm_ddd.core.health import ModuleHealth

class RefreshaccesstokenClass:
    """Auto-generated class for functions."""

    def refresh_access_token(self) -> bool:
    """
    Refresh the access token using refresh token.

    Returns:
    True if refresh successful
    """
    if not self.credentials.refresh_token:
    raise DevPostAuthenticationError('No refresh token available')
    if not self.client_secret:
    raise DevPostAuthenticationError('OAuth client secret not configured')
    try:
    refresh_data = {'grant_type': 'refresh_token', 'client_id': self.client_id, 'client_secret': self.client_secret, 'refresh_token': self.credentials.refresh_token}
    response = requests.post(self.TOKEN_URL, data=refresh_data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=30)
    if response.status_code != 200:
    raise DevPostAuthenticationError(f'Token refresh failed: {response.text}')
    token_response = response.json()
    self.credentials.access_token = token_response['access_token']
    self.credentials.refresh_token = token_response.get('refresh_token', self.credentials.refresh_token)
    expires_in = token_response.get('expires_in', 3600)
    self.credentials.expires_at = datetime.now() + timedelta(seconds=expires_in)
    self._save_credentials()
    return True
    except requests.RequestException as e:
    raise DevPostAuthenticationError(f'Token refresh failed: {e}')

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

