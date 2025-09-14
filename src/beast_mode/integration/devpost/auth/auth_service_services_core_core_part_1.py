from src.rm_ddd.core.health import ModuleHealth

def __init__(self, client_id: Optional[str]=None, client_secret: Optional[str]=None):
    """
        Initialize the authentication service.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
        """
    self.client_id = client_id
    self.client_secret = client_secret
    self.credentials = AuthCredentials()
    self.credentials_file = Path.home() / '.devpost' / 'credentials.json'
    self._load_credentials()
