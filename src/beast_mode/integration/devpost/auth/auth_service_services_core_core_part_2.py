from src.rm_ddd.core.health import ModuleHealth

def _load_credentials(self) -> None:
    """Load stored credentials from file"""
    if self.credentials_file.exists():
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
            self.credentials.access_token = data.get('access_token')
            self.credentials.refresh_token = data.get('refresh_token')
            self.credentials.api_key = data.get('api_key')
            self.credentials.token_type = data.get('token_type', 'Bearer')
            self.credentials.scope = data.get('scope')
            if data.get('expires_at'):
                self.credentials.expires_at = datetime.fromisoformat(data['expires_at'])
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f'⚠️ Could not load credentials: {e}')
            self.credentials = AuthCredentials()

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

