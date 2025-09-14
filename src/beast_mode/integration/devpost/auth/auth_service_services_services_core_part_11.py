
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
