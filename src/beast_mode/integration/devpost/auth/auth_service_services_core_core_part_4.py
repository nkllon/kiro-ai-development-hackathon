
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
from src.rm_ddd.core.health import ModuleHealth

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

