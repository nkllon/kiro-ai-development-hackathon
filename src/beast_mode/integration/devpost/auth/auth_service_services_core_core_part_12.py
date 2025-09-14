from src.rm_ddd.core.health import ModuleHealth

class InteractiveoauthflowClass:
    """Auto-generated class for functions."""

    def interactive_oauth_flow(self) -> bool:
    """
    Perform interactive OAuth flow with automatic browser opening.

    Returns:
    True if authentication successful
    """
    try:
    auth_url = self.authenticate_with_oauth()
    print(f'🌐 Opening browser for OAuth authentication...')
    print(f"🔗 If browser doesn't open, visit: {auth_url}")
    webbrowser.open(auth_url)
    print("\n📋 After authorizing, you'll be redirected to a page with an error.")
    print("🔍 Look for the 'code' parameter in the URL and paste it here:")
    authorization_code = input('Authorization code: ').strip()
    print("🔍 Also look for the 'state' parameter in the URL:")
    state = input('State: ').strip()
    return self.complete_oauth_flow(authorization_code, state)
    except KeyboardInterrupt:
    print('\n❌ OAuth flow cancelled by user')
    return False
    except Exception as e:
    print(f'❌ OAuth flow failed: {e}')
    return False

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

