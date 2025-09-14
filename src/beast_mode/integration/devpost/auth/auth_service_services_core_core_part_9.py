from src.rm_ddd.core.health import ModuleHealth

def get_credentials(self) -> AuthCredentials:
    """
        Get current authentication credentials.
        
        Returns:
            AuthCredentials object
        """
    return self.credentials
