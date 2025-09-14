from src.rm_ddd.core.health import ModuleHealth

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
