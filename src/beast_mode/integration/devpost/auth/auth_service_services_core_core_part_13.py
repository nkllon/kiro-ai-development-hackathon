from src.rm_ddd.core.health import ModuleHealth

class SetupoauthcredentialsClass:
    """Auto-generated class for functions."""

    def setup_oauth_credentials(self, client_id: str, client_secret: str) -> None:
    """
    Setup OAuth credentials for the service.

    Args:
    client_id: OAuth client ID
    client_secret: OAuth client secret
    """
    self.client_id = client_id
    self.client_secret = client_secret
    config_data = {'client_id': client_id, 'client_secret': client_secret}
    config_file = Path.home() / '.devpost' / 'config.json'
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
    json.dump(config_file, f, indent=2)
    config_file.chmod(384)
    print('✅ OAuth credentials configured successfully')

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

