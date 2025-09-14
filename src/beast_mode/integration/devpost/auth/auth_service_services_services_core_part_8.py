
def is_authenticated(self) -> bool:
    """
        Check if currently authenticated.
        
        Returns:
            True if authenticated and token is valid
        """
    if not self.credentials.access_token and (not self.credentials.api_key):
        return False
    if self.credentials.expires_at and datetime.now() >= self.credentials.expires_at:
        if self.credentials.refresh_token:
            try:
                return self.refresh_access_token()
            except DevPostAuthenticationError:
                return False
        return False
    return True
