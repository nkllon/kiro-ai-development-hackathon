from src.rm_ddd.core.health import ModuleHealth

class GetauthheadersClass:
    """Auto-generated class for functions."""

    def get_auth_headers(self) -> Dict[str, str]:
    """
    Get authentication headers for API requests.

    Returns:
    Dictionary of authentication headers
    """
    if not self.is_authenticated():
    raise DevPostAuthenticationError('Not authenticated')
    if self.credentials.access_token:
    return {'Authorization': f'{self.credentials.token_type} {self.credentials.access_token}'}
    elif self.credentials.api_key:
    return {'X-API-Key': self.credentials.api_key}
    else:
    raise DevPostAuthenticationError('No valid credentials available')

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

