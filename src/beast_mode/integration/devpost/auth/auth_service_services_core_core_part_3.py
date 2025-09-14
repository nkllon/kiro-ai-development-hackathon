from src.rm_ddd.core.health import ModuleHealth

class SavecredentialsClass:
    """Auto-generated class for functions."""

    def _save_credentials(self) -> None:
    """Save credentials to file"""
    self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
    data = {'access_token': self.credentials.access_token, 'refresh_token': self.credentials.refresh_token, 'api_key': self.credentials.api_key, 'token_type': self.credentials.token_type, 'scope': self.credentials.scope, 'expires_at': self.credentials.expires_at.isoformat() if self.credentials.expires_at else None}
    with open(self.credentials_file, 'w') as f:
    json.dump(data, f, indent=2)
    self.credentials_file.chmod(384)

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

